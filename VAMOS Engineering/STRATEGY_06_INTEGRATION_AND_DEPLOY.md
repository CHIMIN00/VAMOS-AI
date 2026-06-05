# STRATEGY 06: 통합 관리 및 배포

> **상위 전략**: Stripe API 거버넌스 + DORA DevOps 메트릭
> **포함 관점**: A20(인터페이스 계약 거버넌스) + A23(마이그레이션 경로) + A24(배포 무결성)
> **적용 Phase**: Phase 3 (R1), Phase 4 (B2c, R2c), Phase 6 (V1)
> **관련 문서**: 매트릭스 B2c, R2c, R3, 하네스 계획서

---

## 1. 전략 개요

```
핵심 원칙:
  "3개 언어(Python/Rust/TS)가 하나의 제품처럼 동작하려면 계약이 필수"

3가지 기법:
  Single Source of Truth: 타입의 정본은 하나만 (A20)
  Expand/Contract: 버전 전환 시 깨뜨리지 않기 (A23)
  Post-Deploy Verification: 배포 후 확인 (A24)
```

---

## 2. A20: 인터페이스 계약 거버넌스

### 2.1 VAMOS 통신 구조

```
React 18 (TypeScript)
  ↕ Tauri IPC (invoke/listen)
Rust Backend (serde)
  ↕ JSON-RPC stdin/stdout
Python AI/ML (Pydantic v2)
  ↕ MCP Streamable HTTP
외부 도구 (MCP Server)
```

### 2.2 정본 규칙

```
정본(Single Source of Truth): Python Pydantic v2 모델
  → 유일하게 수동 편집하는 곳
  → 모든 타입 변경은 여기서 시작

파생(자동 생성):
  Pydantic → JSON Schema 추출 (pydantic model_json_schema)
  JSON Schema → serde 구조체 (Rust) — 자동 생성 스크립트
  JSON Schema → TypeScript interface — 자동 생성 스크립트

금지:
  ✗ Rust serde 구조체를 직접 수정
  ✗ TypeScript interface를 직접 수정
  ✗ JSON Schema를 직접 수정
  → 이것들은 항상 Pydantic에서 생성
```

### 2.3 계약 변경 절차

```
Step 1: Pydantic 모델 수정 (Python)
  → 예: Decision에 confidence_score 필드 추가

Step 2: JSON Schema 재생성
  → python -c "from schemas import Decision; print(Decision.model_json_schema())"

Step 3: Rust serde 재생성
  → 자동 생성 스크립트 실행 (Phase 4에서 구축)

Step 4: TypeScript interface 재생성
  → 자동 생성 스크립트 실행

Step 5: 왕복 테스트 (Round-trip Test)
  → Python 객체 → JSON → Rust 파싱 → JSON → Python 파싱
  → 원본과 결과 동일 = PASS
  → 불일치 = FAIL → Step 1 재확인

Step 6: 커밋
  → Pydantic + JSON Schema + serde + TS interface 4개 파일 동시 커밋
  → 하나만 커밋하는 것 금지 (불일치 방지)
```

### 2.4 검증 방법

```
Phase 4 B2c에서:
  매 스키마 변경 시 → Step 5 왕복 테스트 자동 실행
  CI에서: JSON Schema ↔ 실제 Pydantic 모델 일치 확인

Phase 5 D3에서:
  D2.1 SOT 스키마 정의 ↔ 실제 Pydantic 모델 필드 대조
```

---

## 3. A23: 마이그레이션 경로 설계

### 3.1 문제: 버전 전환 시 깨짐

```
V0 → V1 전환 시:
  스키마 필드 추가/변경 가능
  config LOCK 값 추가 가능
  모듈 활성화 변경 (V0 스켈레톤 → V1 활성)
  → 한 번에 바꾸면 V0 코드가 깨질 수 있음
```

### 3.2 전략: Expand/Contract 패턴

```
스키마 변경 시 3단계:

Step 1 — Expand (확장):
  새 필드 추가 (기존 필드 유지, optional로 추가)
  예: Decision에 confidence_score: float | None = None 추가
  → 기존 코드는 이 필드를 무시 → 안 깨짐

Step 2 — Migrate (전환):
  코드를 새 필드 사용으로 점진적 전환
  예: SelfCheckGate가 confidence_score를 채우기 시작
  예: UI가 confidence_score 표시 시작

Step 3 — Contract (축소):
  기존 필드 제거 (모든 코드가 새 필드 사용 확인 후)
  → 이 단계는 V1 안정화 후에만 수행
  → 급하지 않으면 V2까지 유지해도 됨
```

### 3.3 config 변경 시

```
config.v1.toml → config.v1.1.toml 전환:

규칙:
  기존 키 삭제 금지 (하위 호환)
  새 키 추가 시 기본값 필수
  LOCK 키 변경 시 Approval Gate 필수

예:
  V0: cost_monthly_limit = 40000 (LOCK)
  V1: cost_monthly_limit = 40000 (LOCK)  ← 유지
      confidence_refuse_threshold = 0.30 (LOCK)  ← 추가 (신규)
```

### 3.4 Phase 6에서 적용

```
V0→V1 마이그레이션 체크리스트:
  □ 스키마 변경: Expand 단계만 적용 (Contract는 V2까지 미룸)
  □ config: 기존 키 전부 유지 + 새 키에 기본값
  □ 모듈 활성화: OFF→ON 변경은 config 수준 (코드 변경 없이)
  □ 데이터: SQLite V0 데이터 → V1에서 읽기 가능 (스키마 호환)
  □ 왕복 테스트: V0 테스트 케이스가 V1에서도 PASS
```

---

## 4. A24: 배포 무결성 검증

### 4.1 문제: 배포 ≠ 올바른 배포

```
Knight Capital 교훈:
  8개 서버 중 7개만 새 코드 배포
  1개 서버에 5년 전 코드 잔존
  → 45분간 $440M 손실
```

### 4.2 전략: Post-Deployment Verification

```
Phase 6 (V1 배포 시) 검증 3단계:

Step 1: Health Check
  → /health 엔드포인트 호출 → 200 OK 확인
  → 응답에 version 필드 → 의도한 버전인지 확인

Step 2: Config Verification
  → /config/locks 엔드포인트 호출
  → 런타임 로드된 LOCK 값 vs config.v1.toml 파일 대조
  → 불일치 0건 = PASS

Step 3: Smoke Test
  → 핵심 E2E 테스트 1개 실행
  → "안녕하세요" 입력 → IntentFrame 생성 → Decision → Response 반환
  → 정상 반환 = PASS

3개 전부 PASS → 배포 성공
1개라도 FAIL → 이전 버전으로 롤백 (git checkout v0-release)
```

### 4.3 V0에서의 적용 (Phase 4~5)

```
V0는 로컬 실행이므로 "배포"가 아니라 "실행 확인":
  Step 1: 앱 기동 확인 (Tauri 윈도우 열림)
  Step 2: config.v1.toml 로드 확인 (로그에서 LOCK 값 출력)
  Step 3: 기본 입력→출력 테스트 통과
```

---

## 5. 관점 간 연결

```
A20(계약 거버넌스) → 스키마 변경 시 → A23(마이그레이션) Expand/Contract 적용
A20(왕복 테스트) → 배포 전 확인 → A24(배포 무결성) Smoke Test 포함
A23(마이그레이션) → V0→V1 전환 → STRATEGY_01 A15(R15: V1이 V0 깨뜨림) 리스크 대응
A24(배포 검증) → FAIL 시 → STRATEGY_01 A1(실패 복구: 롤백)
```

---

> **참조**: STRATEGY_08 (매트릭스 B2c, R2c), STRATEGY_05 (스키마에 confidence/reasoning 추가)
