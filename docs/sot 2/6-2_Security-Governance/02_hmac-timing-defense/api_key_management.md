# API Key 관리 상세 명세

> **Phase**: 1 (V1)
> **§7.3 항목**: #10 "API Key 관리"
> **세션**: P1-1
> **작성일**: 2026-04-12
> **상태**: DRAFT

---

## 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| Part2 구현가이드 | §6.5 #11 | API Key 관리 지침 |
| STEP7-E | S7E-005 (API Key 관리, HIGH, V1) | API Key 보안 요구사항 |
| AUTHORITY_CHAIN.md | §5 L5 | 키 순환 90일 LOCK |
| AUTHORITY_CHAIN.md | §5 L17 | Cost Gate 일일 한도 LOCK |
| AUTHORITY_CHAIN.md | §5 L18 | trace_id 서버 측 UUID v4 LOCK |
| 02_hmac-timing-defense/_index.md | §D | 암호화 인프라 |
| ai_code_checklist_7items.md | CK-05 | API 키 노출 방지 체크리스트 |

---

## 1. 키 저장 아키텍처

### 1.1 .env 파일 구성

```bash
# .env — API Key 저장 (V1)
# 파일 권한: 0600 (소유자만 읽기/쓰기)
# .gitignore 필수 등록

ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# 키 메타데이터
API_KEY_VERSION=v2026041201
API_KEY_ROTATED_AT=2026-04-12T00:00:00Z
API_KEY_EXPIRES_AT=2026-07-11T00:00:00Z  # 90일 (L5)
```

### 1.2 dotenv 로딩 패턴

```typescript
// 정본 패턴 — 프로세스 환경 변수로만 참조
import 'dotenv/config';

// COMPLIANT: 환경 변수 참조
const apiKey = process.env.ANTHROPIC_API_KEY;
if (!apiKey) throw new ConfigError('ANTHROPIC_API_KEY not set');

// VIOLATION: 하드코딩 금지 (CK-05)
// const apiKey = "sk-ant-abc123...";

// VIOLATION: 로그 출력 금지 (CK-05)
// console.log(`Using key: ${apiKey}`);
```

### 1.3 소스 코드 노출 방지

```yaml
# .gitignore — 필수 등록
.env
.env.local
.env.*.local
*.key
*.pem
credentials.json
```

```yaml
# .pre-commit-config.yaml — detect-secrets hook
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

**gitleaks 설정**:
```toml
# .gitleaks.toml
[allowlist]
description = "VAMOS API Key Allowlist"

[[rules]]
id = "anthropic-api-key"
description = "Anthropic API Key"
regex = '''sk-ant-[a-zA-Z0-9-_]{20,}'''
tags = ["api-key", "anthropic"]

[[rules]]
id = "openai-api-key"
description = "OpenAI API Key"
regex = '''sk-[a-zA-Z0-9]{48,}'''
tags = ["api-key", "openai"]

[[rules]]
id = "generic-secret"
description = "Generic Secret"
regex = '''(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['"][^'"]{10,}['"]'''
tags = ["secret"]
```

---

## 2. 키 로테이션 정책

### 2.1 90일 주기 (L5)

> LOCK (Part2 §6.5.2): 90일 주기 자동 키 순환. 이전 키는 grace period(24h) 후 폐기. `key_version` 필드로 다중 키 지원

| 항목 | 값 | 근거 |
|------|-----|------|
| **순환 주기** | 90일 | L5 |
| **Grace Period** | 24시간 (이전 키 병행 유효) | L5, 부록 §D |
| **자동화** | 매일 실행 잡 + `last_rotated_at` 경과일 비교 (≥90일 시 순환; cron DOM */90은 발화 불가하여 금지) | 운영 자동화 |
| **알림** | 순환 7일 전 사전 알림 | DevOps 통보 |

### 2.2 로테이션 자동화 스크립트

```python
import os
import json
from datetime import datetime, timedelta

def rotate_api_key(provider: str) -> dict:
    """API Key 자동 순환
    시간복잡도: O(1) — API 호출 + 파일 갱신
    LOCK 참조: L5 (90일 순환)
    """
    # 1. 신규 키 발급 (Provider API)
    new_key = provider_api.create_key(provider)
    
    # 2. Grace Period: 이전 키 보존 (24시간)
    old_key = os.environ.get(f'{provider.upper()}_API_KEY')
    grace_expires = datetime.utcnow() + timedelta(hours=24)
    
    # 3. .env 파일 갱신
    update_env_file({
        f'{provider.upper()}_API_KEY': new_key,
        f'{provider.upper()}_API_KEY_OLD': old_key,  # Grace Period
        'API_KEY_VERSION': f'v{datetime.now().strftime("%Y%m%d%H")}',
        'API_KEY_ROTATED_AT': datetime.utcnow().isoformat() + 'Z',
        'API_KEY_EXPIRES_AT': (datetime.utcnow() + timedelta(days=90)).isoformat() + 'Z',
        'API_KEY_GRACE_EXPIRES': grace_expires.isoformat() + 'Z',
    })
    
    # 4. 감사 로그
    log_security_event("api_key_rotation", {
        "provider": provider,
        "new_key_hash": hashlib.sha256(new_key.encode()).hexdigest()[:16],
        "grace_expires": grace_expires.isoformat(),
        "next_rotation": (datetime.utcnow() + timedelta(days=90)).isoformat()
    })
    
    return {"status": "rotated", "grace_expires": grace_expires.isoformat()}
```

### 2.3 Grace Period 듀얼 키 검증

```python
def verify_api_key(request_key: str) -> bool:
    """API Key 검증 (Grace Period 듀얼 키 지원)"""
    current_key = os.environ.get('ANTHROPIC_API_KEY')
    old_key = os.environ.get('ANTHROPIC_API_KEY_OLD')
    grace_expires = os.environ.get('API_KEY_GRACE_EXPIRES')
    
    # 현재 키 확인
    if hmac.compare_digest(request_key, current_key):  # L3: 상수 시간 비교
        return True
    
    # Grace Period 내 이전 키 확인
    if old_key and grace_expires:
        if datetime.now(timezone.utc) < datetime.fromisoformat(grace_expires.replace('Z', '+00:00')):
            if hmac.compare_digest(request_key, old_key):
                return True
    
    return False
```

---

## 3. 비상 폐기 절차

```
[키 유출 감지]
  → 1. 즉시 폐기: Provider API로 이전 키 비활성화 (0분)
  → 2. 새 키 발급: Provider API로 신규 키 생성 (1분)
  → 3. .env 교체: 새 키 등록 + 이전 키 제거 (2분)
  → 4. 서비스 재시작: 환경 변수 리로드 (3분)
  → 5. 감사 로그: 유출 경위 + 대응 조치 기록 (5분)
  → 6. 에스컬레이션: P0 oncall 통보 + 보안 팀 리뷰 (10분)
```

**비상 폐기 SLA**: 유출 감지 후 10분 이내 전체 절차 완료

---

## 4. 접근 로깅

```json
{
  "event": "security.api_key.usage",
  "trace_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "timestamp": "2026-04-12T13:00:00Z",
  "error": {
    "code": "AK-LOG",
    "message": "API key access logged",
    "severity": "INFO"
  },
  "context": {
    "provider": "anthropic",
    "endpoint": "/v1/messages",
    "key_version": "v2026041201",
    "key_hash": "a1b2c3d4...",
    "user_role": "OPERATOR",
    "cost_estimate_krw": 50
  },
  "recovery": {
    "action": "logged",
    "cost_remaining_daily_krw": 92950
  }
}
```

---

## 5. 비용 제어 연동 (L17)

> LOCK (D2.0-07 §4 / Part2 §6.5.3): Cost Gate 일일 한도 V2 = ₩93,000/일 ($70/일). (월 환산 참고치이며, 자동 차단 임계값은 일일 ₩93,000 기준)
>
> LOCK (Part2 §6.5.3): Cost Gate 일일 한도 (V2: ₩93,000), rate limiting (10 req/min 기본)

```python
def check_cost_gate(api_call_cost: float, trace_id: str) -> bool:
    """Cost Gate 일일 한도 초과 시 API Key 자동 비활성화
    LOCK 참조: L17 (V2: ₩93,000)
    """
    daily_total = get_daily_cost_total()
    
    if daily_total + api_call_cost > DAILY_COST_LIMIT:  # L17
        # API Key 자동 비활성화 트리거
        disable_api_key_temporarily()
        log_security_event("cost_gate_triggered", {
            "trace_id": trace_id,
            "daily_total": daily_total,
            "attempted_cost": api_call_cost,
            "limit": DAILY_COST_LIMIT,
            "action": "api_key_disabled"
        })
        return False
    
    return True
```

---

## 6. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| AK-001 | API Key 미설정 | NO | 서비스 시작 차단, 설정 안내 |
| AK-002 | API Key 만료 (90일 초과) | YES | 자동 순환 트리거, Grace Period |
| AK-003 | API Key 유출 감지 | NO | 비상 폐기 절차 즉시 발동 |
| AK-004 | Grace Period 만료 + 이전 키 사용 시도 | NO | 인증 거부, 최신 키 사용 안내 |
| AK-005 | Cost Gate 한도 초과 | YES | API Key 일시 비활성, 다음 날 자동 복원 |
| AK-006 | detect-secrets pre-commit 차단 | YES | 커밋 거부, 키 제거 후 재커밋 |
| AK-007 | Provider API 키 발급 실패 | YES | 재시도 (최대 3회), 수동 발급 안내 |

---

## 7. S7E-005 요구사항 대조

| S7E-005 요구사항 | 본 문서 반영 | 상태 |
|----------------|------------|:----:|
| API Key 안전한 저장 | §1.1 .env + 0600 권한 | OK |
| 키 순환 | §2 90일 로테이션 (L5) | OK |
| 키 폐기 | §3 비상 폐기 절차 | OK |
| 키 노출 방지 | §1.3 detect-secrets + gitleaks | OK |
| 접근 로깅 | §4 trace_id 포함 로깅 | OK |

---

## 8. Phase 2 통합 테스트 시나리오

| # | 시나리오 | 예상 결과 |
|---|---------|----------|
| T-01 | .env에 API Key 설정 후 정상 API 호출 | 200 OK |
| T-02 | API Key 미설정 시 서비스 시작 | 시작 차단 + 에러 메시지 |
| T-03 | API Key 하드코딩 커밋 시도 | pre-commit hook 차단 |
| T-04 | 90일 경과 후 자동 순환 트리거 | 신규 키 발급 + Grace Period 시작 |
| T-05 | Grace Period(24h) 내 이전 키 사용 | 인증 성공 |
| T-06 | Grace Period 만료 후 이전 키 사용 | 인증 실패 |
| T-07 | 키 유출 감지 → 비상 폐기 | 10분 이내 전체 절차 완료 |
| T-08 | Cost Gate 한도 초과 시 | API Key 일시 비활성화 (L17) |
| T-09 | gitleaks 스캔에서 키 패턴 탐지 | 커밋 차단 + 경고 |
| T-10 | 키 사용 로그에 trace_id 포함 확인 | UUID v4 형식 (L18) |
