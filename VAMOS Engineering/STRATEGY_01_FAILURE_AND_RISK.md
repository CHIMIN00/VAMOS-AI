# STRATEGY 01: 실패 대비 및 리스크 관리

> **상위 전략**: PMBOK 리스크 관리 + SRE 사이트 신뢰성 엔지니어링
> **포함 관점**: A1(Phase 실패 복구) + A2(데이터 백업) + A15(리스크 레지스터)
> **적용 Phase**: 전 Phase 공통
> **관련 문서**: 로드맵 전 Phase "실패 시" 항목, 하네스 계획서 §13 위험 8건

---

## 1. 전략 개요

```
핵심 원칙:
  "실패는 일어난다 — 문제는 실패 자체가 아니라 대응 방법의 부재"
  
3가지 층위:
  예방: A15 리스크 레지스터로 위험을 미리 식별하고 대비
  복구: A1 실패 시 복구 방법으로 Phase가 막히지 않게
  보호: A2 데이터 백업으로 작업물 소실 방지
```

---

## 2. A1: Phase 실패 시 복구 방법

### 2.1 문제 정의

```
현재: Phase 완료 조건만 있고, 충족 못하면 어떻게 하라는 지시가 없음
위험: Phase에서 막히면 → 전체 프로젝트가 멈춤
```

### 2.2 전략: 단계적 축소 (Graceful Degradation)

```
원칙: 100% 달성 못하면 → 핵심만 남기고 나머지 연기
      완전히 멈추는 것보다 범위 줄여서라도 진행하는 것이 낫다
```

### 2.3 Phase별 실패 복구 방법

**Phase 0 실패:**
```
실패 조건: 매트릭스 갱신 불가 (구조적 모순 발견)
복구 방법:
  1. 모순 항목을 "PENDING" 표시하고 Phase 1 진입
  2. Phase 1 D1 결과로 모순 해소
  3. Phase 2에서 매트릭스 재갱신
```

**Phase 1 실패:**
```
실패 조건 A: CONFLICT 해소 불가 (SOT 간 근본적 모순)
복구 방법:
  1. 정본 우선순위(RULE > PLAN > DESIGN LOCK)에 따라 상위 문서가 정답
  2. 그래도 해소 불가 → 해당 도메인을 Phase 1 범위에서 제외
  3. V1 D1'에서 재검증

실패 조건 B: SOT 2 완성 불가 (2,654개 중 일부 미완)
복구 방법:
  1. 핵심 5개 도메인(T0~T2) 완성 여부 확인
  2. 12개 완성 → D1 부분 실행 가능
  3. 나머지는 Phase 2와 병행 완성
```

**Phase 2 실패:**
```
실패 조건: CLAUDE.md 보강 후 REJECT 판정
복구 방법:
  1. REJECT 원인 분석 (8스킬 결과에서 FAIL 항목 확인)
  2. FAIL 항목만 수정 후 재검증
  3. 3회 시도 후에도 REJECT → 보강 범위 축소 (§21~§24만 적용, §25~§28 연기)
  4. BRONZE 이상이면 Phase 3 진입 허용 (SILVER 목표 유지하되 차선 허용)
```

**Phase 3 실패:**
```
실패 조건: R1 결정이 SOT와 충돌
복구 방법:
  1. /sot-check로 충돌 지점 정확히 식별
  2. SOT가 정본이므로 R1 결정을 SOT에 맞춤
  3. SOT 자체가 모순이면 → DF 역류 → D1 부분 재실행
```

**Phase 4 실패:**
```
실패 조건: V0 체크리스트 16항목 중 Must 미통과
복구 방법:
  1. 실패 항목의 원인 분석 (설계 문제? 코드 문제? 환경 문제?)
  2. 설계 문제 → DF 역류 → Phase 3 R1 수정
  3. 코드 문제 → 해당 STEP 재실행
  4. 환경 문제 → Phase 2 린터/CI 재확인
```

**Phase 5 실패:**
```
실패 조건: DRIFT 발견 (설계↔코드 불일치)
복구 방법:
  1. DRIFT 목록에서 CRITICAL 항목 식별
  2. 설계가 정본 → 코드 수정
  3. 코드가 맞고 설계가 낡음 → DF 역류 → D2 전파
  4. Phase 4 해당 STEP 재실행
```

---

## 3. A2: 데이터 백업 전략

### 3.1 문제 정의

```
현재: 396,000줄 문서 + 작업 산출물이 로컬에만 존재
위험: 하드디스크 고장, 실수로 파일 삭제
```

### 3.2 전략: Git 태그 기반 체크포인트

```
도구: Git (이미 사용 중)
추가 비용: ₩0

규칙:
  ① Git remote(GitHub) 연결 유지 — Phase 0에서 확인
  ② 주요 마일스톤마다 git tag 생성:
     git tag phase0-complete
     git tag phase1-d1-pass
     git tag phase2-b1-complete
     git tag v0-release
     git tag v1-release
  ③ Phase 완료 시 git push --tags
  ④ 복구 필요 시: git checkout phase1-d1-pass 로 해당 시점 복원
```

### 3.3 백업 범위

```
Git으로 백업되는 것:
  ✓ SOT 68개 + SOT 2 2,654개
  ✓ CLAUDE.md + 보강전략
  ✓ VAMOS Engineering 문서들
  ✓ VAMOS HOME 노트
  ✓ .claude/skills + hooks + settings
  ✓ 코드 (Phase 4+)

Git으로 백업 안 되는 것:
  ✗ .env (API Key) → .env.example만 저장 (보안)
  ✗ node_modules, __pycache__ → .gitignore로 제외 (재생성 가능)
  ✗ 대용량 모델 파일 → 다운로드 가능 (BGE-M3 등)
```

---

## 4. A15: 리스크 레지스터

### 4.1 문제 정의

```
현재: 하네스 계획서 §13에 위험 8건 있으나 로드맵에 미반영
      Phase별 위험이 한눈에 안 보임
```

### 4.2 전략: 확률×영향 매트릭스

```
각 위험에 3가지 평가:
  발생 확률: HIGH / MEDIUM / LOW
  영향도: HIGH / MEDIUM / LOW
  대응 우선순위: 확률×영향 조합

  HIGH×HIGH = 즉시 대응 (로드맵에 대응 작업 포함)
  HIGH×MEDIUM 또는 MEDIUM×HIGH = 대응책 준비 (실패 시 실행)
  나머지 = 인지만 (발생 시 대응)
```

### 4.3 리스크 레지스터

| # | 위험 | 확률 | 영향 | Phase | 대응책 |
|---|------|------|------|-------|--------|
| R01 | SOT 내부 불일치 다수 발견 | MEDIUM | HIGH | Phase 1 | 정본 우선순위로 해소 + 범위 축소 |
| R02 | SOT 2 ↔ SOT 불일치 다수 | HIGH | HIGH | Phase 1 | 핵심 5개 도메인 우선 해소 |
| R03 | PART2 참조 SOT가 구버전 | MEDIUM | MEDIUM | Phase 1 | /sot-check method-c로 탐지 + 갱신 |
| R04 | CLAUDE.md 보강 후 REJECT | LOW | MEDIUM | Phase 2 | 범위 축소 → BRONZE 허용 |
| R05 | 린터 오탐(false positive) | MEDIUM | LOW | Phase 2 | 초기 warn 모드 → 안정화 후 error |
| R06 | R1 결정이 SOT와 충돌 | MEDIUM | HIGH | Phase 3 | /sot-check 대조 → SOT 기준 수정 |
| R07 | 3개 언어 타입 불일치 | MEDIUM | HIGH | Phase 4 | Pydantic 정본 + 자동 생성 규칙 |
| R08 | V0 16항목 중 일부 미통과 | MEDIUM | MEDIUM | Phase 4 | Must/Should/Could 축소 |
| R09 | CI 환경 과엄격으로 속도 저하 | MEDIUM | LOW | Phase 4 | V0에서는 ruff+pytest만 필수 |
| R10 | CLAUDE.md 보강이 D1 정합 깨뜨림 | LOW | HIGH | Phase 2 | 보강 후 /sot-check 재실행 |
| R11 | SOT 2 작업 중 기존 SOT 변경 필요 | HIGH | MEDIUM | Phase 1 | D2 변경 추적 + /integrity 감시 |
| R12 | Obsidian 노트와 SOT 2 불일치 | MEDIUM | MEDIUM | Phase 2 | 샘플 10% 수동 대조 |
| R13 | 외부 의존성 변경 (Python/Rust 버전) | LOW | MEDIUM | Phase 2 | LOCK으로 버전 고정 |
| R14 | 스킬/Hook 코드 변경으로 깨짐 | MEDIUM | MEDIUM | Phase 4 | Phase 착수 전 스킬 건강 검진 |
| R15 | V1이 V0 코드 깨뜨림 | MEDIUM | HIGH | Phase 6 | 회귀 테스트 + expand/contract 패턴 |

### 4.4 관점 간 연결

```
A15(리스크) → 위험이 현실이 되면 → A1(복구) 방법 실행
A15(리스크) → 데이터 손실 위험 → A2(백업) 으로 보호
A15(R08) → V0 축소 필요 → A9(스코프 축소 규칙)으로 처리
```

---

> **참조**: STRATEGY_08 (매트릭스), STRATEGY_09 (하네스 계획서 §13), STRATEGY_10 (검증 체계)
