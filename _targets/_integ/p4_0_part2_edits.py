# P4-0 PART2 연쇄 수정 스크립트 (PHASE4-DEC-002/003/004/005/009 집행)
# CRLF 보존: newline='' 로 읽고 그대로 기록 (UTF-8 no-BOM). 각 치환 기대 횟수 assert.
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"

with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    text = f.read()

orig_cr = text.count("\r")

# (old, new, expected_count)
EDITS = [
    # ── DEC-002: CostGate 키 재설계 (템플릿 2곳 동일 문자열) ──
    ("warn_threshold = 70              # % 1단계 경고 (P30-058: 70/85/95 3단계 경보)",
     "warn_threshold = 80              # % force_mini 다운시프트 시작 (LOCK 게이트 — DEC-005·D13, OWNER 승인 조정 가능)", 2),
    ("escalate_threshold = 85          # % 2단계 심화 경고",
     "block_threshold = 100            # % deny 차단 (LOCK — 변경 불가, DEC-005)", 2),
    ("block_threshold = 95             # % 3단계 차단",
     "alert_thresholds = [70, 85, 95]  # P30-058 3단계 경보 (비-LOCK, 통지 전용 — PHASE4-DEC-002 병존 확정)", 2),
    # DEC-002: STEP-4 AI 프롬프트 CostGate 행
    ("- CostGate: I-9 stub 호출 → 70% warn, 85% escalate, 95% block (config.v1.toml cost 섹션, P30-058 3단계)",
     "- CostGate: I-9 stub 호출 → 게이트 80% warn(force_mini)/100% block(deny — LOCK, DEC-005) + 경보 70/85/95는 통지 전용(alert_thresholds, P30-058 — PHASE4-DEC-002 병존)", 1),
    # DEC-002: §6.12.8 관계 주석
    ("### 6.12.8 비용 초과 대응\r\n\r\n```",
     "### 6.12.8 비용 초과 대응\r\n\r\n> ※ 아래 70/85/95는 **경보·완화 체계**(P30-058, alert_thresholds — 통지 전용)이며, 차단 집행은 게이트 80(force_mini)/100(deny) LOCK(DEC-005)이 수행한다. 95 단계의 \"일시 정지 대기\"는 예고이지 차단이 아니다 (PHASE4-DEC-002 병존 확정).\r\n\r\n```", 1),
    # DEC-002: §7.5.1 한정 표기
    ("| 비용 임계값 단일화 | config.toml warn=80%, block=100% 유일 SOT (BLOCKER-11) |",
     "| 비용 임계값 단일화 | config.toml warn=80%, block=100% — **게이트 집행 SOT** (BLOCKER-11; 경보 alert_thresholds=[70,85,95]는 P30-058 별도 체계 — PHASE4-DEC-002) |", 1),
    # ── DEC-003: DecisionSchema 18→20 연쇄 ──
    ("| 3 | DecisionSchema | 18 (FREEZE) | D2.1-D2 §4.1 — 14 required + 4 optional |",
     "| 3 | DecisionSchema | 20 (FREEZE+DEC-010 확장) | D2.1-D2 §4.1 18(14+4) + confidence_score/confidence_level 2필드(PHASE3-DEC-010) = 16 required + 4 optional |", 2),
    ("2. **FREEZE/LOCK 확인**: DecisionSchema 18필드(FREEZE), ResponseEnvelope 5필드(LOCK), WorkflowStage 4필드(LOCK), WorkflowOutput 3필드(LOCK)",
     "2. **FREEZE/LOCK 확인**: DecisionSchema 20필드(FREEZE 18+DEC-010 confidence 2), ResponseEnvelope 5필드(LOCK), WorkflowStage 4필드(LOCK), WorkflowOutput 3필드(LOCK)", 1),
    ("- DecisionSchema: 18필드 (14 required + 4 optional) — FREEZE",
     "- DecisionSchema: 20필드 (16 required + 4 optional) — FREEZE 18 + DEC-010 confidence_score/confidence_level (PHASE4-DEC-003)", 1),
    ("<!-- FREEZE_SNAPSHOT: D2.1-D2:DecisionSchema:v3.0.0:18fields:2026-03-03 -->",
     "<!-- FREEZE_SNAPSHOT: D2.1-D2:DecisionSchema:v3.0.0:18fields:2026-03-03 + PHASE3-DEC-010:confidence2:20fields:2026-06-12 -->", 1),
    ("### DecisionSchema (18필드, FREEZE — D2.1-D2 §4.1)",
     "### DecisionSchema (20필드 = FREEZE 18 + DEC-010 confidence 2 — D2.1-D2 §4.1 + PHASE3-DEC-010)", 1),
    ("- **14 required + 4 optional** (총 18필드)",
     "- **16 required + 4 optional** (총 20필드 — D2.1-D2 §4.1 18 + confidence_score/confidence_level required 2, PHASE4-DEC-003)", 1),
    ("| 2 | DecisionSchema 18필드 (FREEZE) | `len(DecisionSchema.model_fields) == 18` (14 required + 4 optional) | ✅ |",
     "| 2 | DecisionSchema 20필드 (FREEZE+DEC-010) | `len(DecisionSchema.model_fields) == 20` (16 required + 4 optional — PHASE4-DEC-003) | ✅ |", 1),
    ('    """DecisionSchema는 정확히 18필드 (FREEZE)"""',
     '    """DecisionSchema는 정확히 20필드 (FREEZE 18 + DEC-010 confidence 2)"""', 1),
    ("    assert len(fields) == 18",
     "    assert len(fields) == 20", 1),
    # DEC-003: 약기 테이블 Decision 행을 SOT 실필드로 교체
    ("| 3 | DecisionSchema | decision_id(str), intent_frame_id(str), chosen_action(str), priority(P0-P3), risk_level(Enum), gate_results(list[GateResult]), evidence_ids(list), cost_estimate(float), approval_status(Enum), execution_plan(dict), created_at(datetime), updated_at(datetime), locked(bool), lock_reason(str?), **+4 optional** |",
     "| 3 | DecisionSchema | decision_id(str), trace_id(str), timestamp(datetime), intent_frame_ref(str), evidence_pack_ref(str), policy_gate(Enum), approval_required(bool), approval_status(Enum 2값), cost_gate(Enum), routing(dict), memory_plan(dict), output_spec(dict), conclusion(Enum), locked(bool), confidence_score(float), confidence_level(Enum) — **D2.1-D2 §4.1 정본 + DEC-010**, +4 optional(optional_signals/verify/gates/s_module_hints) |", 1),
    # DEC-009 ※: 약기 테이블 경고 보강
    ("### 25개 모델 핵심 필드 참조 (SOT 문서 기반)",
     "### 25개 모델 핵심 필드 참조 (SOT 문서 기반) <!-- ⚠️ P4-0 실측: 본 약기는 일부 행이 D2.1 SOT와 다름(예: #11/#12) — 필드 정본은 항상 D2.1 원문+seed (Method B/C 규칙). 불일치 시 SOT 채택 (PHASE4-DEC-009 ※) -->", 1),
    # ── DEC-003: [confidence] 섹션 추가 (템플릿 2곳) + 13→14섹션 연쇄 ──
    ("max_entries = 1000\r\n```",
     "max_entries = 1000\r\n\r\n[confidence]                     # PHASE3-DEC-010 신규 LOCK 3키 (Registry §8 R1-A25) — PHASE4-DEC-003\r\nconfidence_high_threshold = 0.85     # LOCK\r\nconfidence_medium_threshold = 0.60   # LOCK\r\nconfidence_refuse_threshold = 0.30   # LOCK\r\n```", 2),
    ("3. **config.v1.toml 기본 설정** — ⚠️ **V0 축약본 (참조용, 13섹션)** (PHASE_B4 §3 기준) <!-- B4 정본은 17섹션. V0에서 [blue_nodes],[ui],[rate_limit],[guardrails] 생략. 정본은 아래 §2 STEP-3의 V1 확장판(17섹션). 구현 시 B4 §3 전체를 참조하세요 -->",
     "3. **config.v1.toml 기본 설정** — ⚠️ **V0 축약본 (참조용, 14섹션 = B4 13 + [confidence])** (PHASE_B4 §3 기준 + PHASE3-DEC-010) <!-- B4 정본은 17섹션. V0에서 [blue_nodes],[ui],[rate_limit],[guardrails] 생략 + [confidence] 신규(DEC-010, B4 §3.17 신설 지시 등재). V1+ 확장 17(+1)섹션은 PHASE_B4 §3 정본 참조 (PHASE4-DEC-009 라벨 정정) -->", 1),
    ("## 3. config/config.v1.toml 생성 — ✅ **V1 확장판 (정본, 17섹션)** (PHASE_B4 §3 정본 LOCK 값)",
     "## 3. config/config.v1.toml 생성 — ✅ **V0 14섹션 (정본 LOCK 값 — B4 13 + [confidence] DEC-010)** (PHASE_B4 §3; V1+ 확장 17(+1)섹션은 B4 §3 전체 참조 — PHASE4-DEC-009 라벨 정정) ", 1),
    ("| 5 | config.v1.toml 생성 | `config/config.v1.toml` 존재 + 13섹션 구조 + LOCK 값 정확성 (PHASE_B4 §3 대조) | ✅ |",
     "| 5 | config.v1.toml 생성 | `config/config.v1.toml` 존재 + 14섹션 구조(B4 13 + [confidence] — PHASE4-DEC-003) + LOCK 값 정확성 (PHASE_B4 §3 대조) | ✅ |", 1),
    ("각 서브 Config 클래스는 config.v1.toml의 섹션과 1:1 매핑합니다 (V0=13개 섹션, V1+=17개 섹션, B4 §3 정본 기준).",
     "각 서브 Config 클래스는 config.v1.toml의 섹션과 1:1 매핑합니다 (V0=14개 섹션[B4 13 + confidence], V1+=17(+1)개 섹션, B4 §3 정본 + PHASE3-DEC-010 기준).", 1),
    ("    semantic_cache: SemanticCacheConfig  # PHASE_B4 §3.15",
     "    semantic_cache: SemanticCacheConfig  # PHASE_B4 §3.15\r\n    confidence: ConfidenceConfig   # PHASE3-DEC-010 신규 3키 (LOCK) — PHASE4-DEC-003", 1),
    ("| 8 | config 로드 | `get_config()` → VamosConfig 13개 서브모델 정상 로드 | ✅ |",
     "| 8 | config 로드 | `get_config()` → VamosConfig 14개 서브모델 정상 로드 (+confidence — PHASE4-DEC-003) | ✅ |", 1),
    # ── DEC-004: §7.1 #15 충족 수단 ──
    ("| 15 | Guardrails L1+L2 설정 | PHASE_B4 | [ ] |",
     "| 15 | Guardrails L1+L2 설정 | PHASE_B4 | [ ] | <!-- V0 충족 수단 = 코드 수준 등가(L1 입력: extra=forbid+model_validate+non-goal deny / L2 출력: ResponseEnvelope 검증+verify 노드) — [guardrails] 섹션은 V1+ 유지 (PHASE4-DEC-004) -->", 1),
    # ── DEC-005: STEP-1 리포 신설·STEP-6 yml 2종 reconcile ──
    ("2. **GitHub 리포지토리 생성**: `vamos` 리포 생성 + clone",
     "2. **GitHub 리포지토리 생성**: `vamos` 리포 생성 + clone <!-- P4-0 reconcile: 불집행 — D:\\VAMOS 단일 repo 기존재(PART1 E.5 PASS)·Phase 2 자산(backend/pyproject·tests·ci.yml·Hook 18) 승계 (PHASE4-DEC-005) -->", 1),
    ("1. **GitHub Actions 기본 워크플로우**\r\n   - `quality-python.yml`: ruff lint + mypy\r\n   - `test-python.yml`: pytest + coverage",
     "1. **GitHub Actions 기본 워크플로우** <!-- P4-0 reconcile: Phase 2 확정 ci.yml 단일 통합(quality/test/vamos-lint 3 job, PHASE_B6 §2 중재)이 정본 — 아래 yml 2종 분리는 대체됨. Stage Gate #1/#2는 ci.yml 해당 job PASS로 판정 (PHASE4-DEC-005, §6.4 XREF-V0-19 동계열) -->\r\n   - `quality-python.yml`: ruff lint + mypy\r\n   - `test-python.yml`: pytest + coverage", 1),
    # ── DEC-009: 디렉토리 트리에 schemas/seed 추가 (2곳, 패딩 상이) ──
    ("├── scripts/           # 유틸리티 스크립트",
     "├── schemas/seed/      # SOT 추출 seed JSON (Method B — PHASE4-DEC-009: 루트 경로 확정)\r\n├── scripts/           # 유틸리티 스크립트", 1),
    ("├── scripts/                # 유틸리티 스크립트",
     "├── schemas/seed/           # SOT 추출 seed JSON (Method B — PHASE4-DEC-009: 루트 경로 확정)\r\n├── scripts/                # 유틸리티 스크립트", 1),
]

failures = []
for old, new, expected in EDITS:
    n = text.count(old)
    if n != expected:
        failures.append((old[:60], expected, n))
        continue
    text = text.replace(old, new)

if failures:
    print("❌ 치환 횟수 불일치 — 집행 중단(파일 미기록):")
    for o, e, n in failures:
        print(f"  기대 {e} != 실제 {n} :: {o}...")
    sys.exit(1)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(text)

new_cr = text.count("\r")
new_lf = text.count("\n")
print(f"✅ {len(EDITS)}건 전건 치환 완료. CR {orig_cr} → {new_cr} / LF {new_lf} (CR==LF: {new_cr == new_lf})")
