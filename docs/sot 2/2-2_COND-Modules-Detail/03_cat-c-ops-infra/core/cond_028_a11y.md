# COND-028: 접근성 (a11y) — L3 상세 명세

> **모듈 ID**: COND-028
> **카테고리**: CAT-C (Ops/Infra) — Core
> **이름**: 접근성 (a11y)
> **우선순위**: HIGH
> **Phase**: Phase 1
> **L3 수준**: L3
> **LOCK 준수**: LOCK-CD-03/04/05/06/08/10
> **인프라 패턴**: Pipeline (rule-set → checks → fixes), Result Aggregation

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class UIComponent(BaseModel):
    component_id: str
    html: str = Field(..., max_length=2_000_000, description="평가 대상 HTML 마크업")
    css: Optional[str] = None
    aria_attributes: dict[str, str] = Field(default_factory=dict)
    viewport: Literal["desktop", "tablet", "mobile"] = "desktop"

class A11yRequest(BaseModel):
    """COND-028 입력 스키마"""
    ui_component: UIComponent
    check_level: Literal["A", "AA", "AAA"] = "AA"
    rules: Optional[list[str]] = Field(default=None, description="실행할 axe 규칙 ID 화이트리스트")
    auto_fix: bool = Field(default=False, description="자동 수정 패치 생성 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "ui_component": {"component_id": "btn-submit",
                                 "html": "<button>OK</button>", "viewport": "desktop"},
                "check_level": "AA", "auto_fix": True
            }
        }
```

---

## E2. Output Schema

```python
class A11yViolation(BaseModel):
    rule_id: str
    severity: Literal["critical", "serious", "moderate", "minor"]
    wcag_criterion: str   # ex) "1.4.3"
    description: str
    selector: str         # CSS selector
    snippet: str

class A11yFix(BaseModel):
    violation_rule_id: str
    fix_type: Literal["aria_label", "contrast", "keyboard", "alt_text", "role", "lang"]
    patch: str            # HTML diff
    confidence: float = Field(ge=0, le=1)

class AccessibilityReport(BaseModel):
    score: float = Field(ge=0, le=100)
    violations: list[A11yViolation]
    warnings: list[A11yViolation]
    passes: int
    incomplete: int

class A11yResponse(BaseModel):
    """COND-028 출력 스키마"""
    a11y_report: AccessibilityReport
    fixes: list[A11yFix]
    check_level: Literal["A", "AA", "AAA"]
    execution_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "a11y_report": {"score": 78.5, "violations": [
                    {"rule_id": "button-name", "severity": "critical",
                     "wcag_criterion": "4.1.2", "description": "Buttons must have discernible text",
                     "selector": "button", "snippet": "<button>OK</button>"}
                ], "warnings": [], "passes": 14, "incomplete": 0},
                "fixes": [{"violation_rule_id": "button-name", "fix_type": "aria_label",
                           "patch": "<button aria-label=\"확인\">OK</button>", "confidence": 0.92}],
                "check_level": "AA", "execution_time_ms": 145
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION audit(request: A11yRequest) -> Result[A11yResponse, VamosError]:
    # 1. DOM 파싱
    dom = parse_html(request.ui_component.html)
    IF dom is invalid:
        RETURN Err(VamosError("COND_028_HTML_PARSE_ERROR", ...))

    # 2. axe-core 룰셋 로드 (check_level에 따라)
    rules = axe_core.load_rules(level=request.check_level, whitelist=request.rules)

    # 3. 각 규칙 실행 (Pipeline)
    violations, warnings, passes, incomplete = [], [], 0, 0
    FOR rule IN rules:
        result = rule.run(dom, css=request.ui_component.css)
        SWITCH result.outcome:
            CASE "violation": violations.append(map_violation(rule, result))
            CASE "warning":   warnings.append(map_violation(rule, result))
            CASE "pass":      passes += 1
            CASE "incomplete":incomplete += 1

    # 4. 점수 산출 (가중치: critical=10, serious=5, moderate=2, minor=1)
    score = compute_score(violations, passes)

    # 5. 자동 수정 생성 (auto_fix=true)
    fixes = []
    IF request.auto_fix:
        FOR v IN violations:
            patch = fix_generator.generate(v, dom)
            IF patch: fixes.append(A11yFix(...))

    # 6. WCAG 매핑 검증 (incomplete가 너무 많으면 경고)
    IF incomplete > len(rules) * 0.3:
        emit_warning("audit_coverage_low")

    RETURN Ok(A11yResponse(a11y_report=AccessibilityReport(score, violations, warnings, passes, incomplete),
                           fixes=fixes, check_level=request.check_level, ...))
```

---

## E4. Error Handling

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|-------------|--------------|
| `COND_028_HTML_PARSE_ERROR` | HTML 파싱 실패(잘못된 마크업) | `FB_COND_028_RAW_HTML` | "HTML 구문이 유효하지 않습니다." |
| `COND_028_RULESET_LOAD_FAIL` | axe-core 룰셋 로드 실패 | `FB_COND_028_BUILTIN_RULES` | "기본 규칙으로 대체합니다." |
| `COND_028_FIX_GENERATION_FAIL` | 자동 수정 생성 실패 | `FB_COND_028_NO_FIX` | "자동 수정을 생성할 수 없습니다." |
| `COND_028_HTML_TOO_LARGE` | html > 2 MB | `FB_COND_028_PARTIAL_AUDIT` | "마크업이 너무 큽니다. 일부만 검사합니다." |
| `COND_028_EXECUTE_TIMEOUT` | timeout_ms 초과 | `FB_COND_SKIP` | "검사 시간이 초과되었습니다." |

```python
return Err(VamosError(
    failure_code="COND_028_HTML_PARSE_ERROR",
    message="Invalid HTML markup at offset 142",
    fallback_id="FB_COND_028_RAW_HTML",
    trace_id=ctx.trace_id,
))
```

---

## E5. Dependency Map

| 관계 | 항목 | 비고 |
|------|------|------|
| 소비 | — | CAT-C 인프라 계층, COND 내부 의존 0건 |
| 제공 | 모든 CAT (UI 컴포넌트 검사) | |

| I-Module | 용도 |
|----------|------|
| I-1, I-5, I-6, I-9 | 공통 4종 |

| 라이브러리 / 인프라 | 사양 |
|--------------------|------|
| `axe-core` (npm) | ≥4.8 |
| `lxml` / `beautifulsoup4` | HTML 파싱 |
| Headless Chromium (선택) | DOM 렌더링 기반 검사 |
| PostgreSQL | 검사 이력 영속화 |

---

## E6. Performance Benchmark (I-04)

| 메트릭 | SLA 목표 | 임계값 | 측정 |
|--------|---------|--------|------|
| **p50 단일 컴포넌트 검사** | ≤ 80 ms | > 250 ms | histogram |
| **p99 페이지 단위 검사 (≤ 200 KB HTML)** | ≤ 1.2 s | > 3 s | histogram |
| **처리량** | ≥ 200 req/s/instance | < 50 | load test |
| **자동 수정 정확도(confidence ≥ 0.9 비율)** | ≥ 70 % | < 50 % | 회귀 셋 |
| **가용성** | 99.9 % | < 99.5 % | uptime |

---

## E7. Integration Test Spec

```yaml
- name: "a11y_button_missing_label"
  input: { ui_component: {component_id: "b1", html: "<button>OK</button>"}, check_level: "AA", auto_fix: true }
  expected:
    - a11y_report.violations[0].rule_id == "button-name"
    - fixes.length >= 1
    - "aria-label" in fixes[0].patch

- name: "a11y_contrast_violation"
  input: { ui_component: {component_id: "t1", html: "<p style='color:#aaa;background:#bbb'>x</p>"}, check_level: "AAA" }
  expected: [a11y_report.violations | any(v: v.rule_id == "color-contrast")]

- name: "a11y_html_too_large"
  input: { ui_component: {html: "x" * 3_000_000} }
  expected: [error.failure_code == "COND_028_HTML_TOO_LARGE"]
```

---

## E8. Blue Node Integration

| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Content Node, Creative Node (UI 산출물 검사) |
| **Permission Level** | P0 (시스템 레벨) |
| **게이트 요구** | policy |
| **호출 패턴** | UI 렌더링 후 OpsInfraMixin.audit_a11y() 호출 |

| 이벤트 | event_type |
|--------|------------|
| 초기화 | `cond.c.028.initialized` |
| 실행 시작/완료/실패 | `cond.c.028.execute_start` / `execute_done` / `execute_fail` |
| 헬스체크 | `cond.c.028.health` |
| 종료 | `cond.c.028.shutdown` |

Decision: `optional_signals ← {cond_module_id: "COND-028", score, violations_count, level}`

---

## E9. BaseModule ABC 적합성

```python
class Cond028A11y(BaseModule):
    async def initialize(self) -> Result[None, VamosError]:
        self._axe = await AxeCoreRuntime.start()
        self._fix_gen = FixGenerator(self.config)
        self._emit_event("cond.c.028.initialized")
        return Ok(None)

    async def execute(self, request: A11yRequest) -> Result[A11yResponse, VamosError]:
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        return Ok(HealthStatus(healthy=self._axe.is_alive(), latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        await self._axe.stop()
        self._emit_event("cond.c.028.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(id="COND-028", version="1.0.0",
                              capabilities=["audit_wcag", "auto_fix", "aria_check"])
```

---

## E10. Configuration

```python
class Cond028Config(ModuleConfig):
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 30
    timeout_ms: int = 5000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=1, backoff_ms=500)

    default_check_level: Literal["A", "AA", "AAA"] = "AA"
    enable_auto_fix: bool = True
    max_html_bytes: int = 2_000_000
    headless_renderer: bool = False
    rule_pack_version: str = "axe-core@4.8"
```
