# VAMOS 5개 엔지니어링 계획서 — 범위/목차 (Phase 0-4 산출물)

> **작성일**: 2026-04-04
> **목적**: 하네스 계획서(STRATEGY_09, ①) 이외 5개 엔지니어링 계획서의 범위와 목차를 사전 정의
> **근거**: STRATEGY_08 매트릭스 v1.1 셀 I/O 계약
> **우선순위**: Could (Phase 0 시간 여유 시 수행)
> **상태**: 초안 (Phase 해당 시점에 상세화 예정)

---

## 계획서 전체 맵

| # | 계획서 | 매트릭스 셀 | 주요 Phase | STRATEGY_08 근거 |
|---|--------|------------|-----------|-----------------|
| ① | 하네스 엔지니어링 | B1, B2a, B3, BF | Phase 2~5 | **STRATEGY_09** (기작성) |
| ② | 설계 정합 엔지니어링 | D2, D3, DF | Phase 1~5 | §4.1 D행 |
| ③ | 런타임 엔지니어링 | R1, R2a, R2b, RF | Phase 3~5 | §4.3 R행 |
| ④ | 다중 스택 통합 엔지니어링 | B2c, R2c | Phase 3~4 | §4.2 B2c + §4.3 R2c |
| ⑤ | 횡단 엔지니어링 | X1~X3, XF | Phase 2~5 | §4.4 X행 |
| ⑥ | 운영 엔지니어링 | R3 | Phase 5~6 | §4.3 R3 |

---

## ② 설계 정합 엔지니어링 계획서

**매트릭스 셀**: D2 (설계 변경 추적/전파) + D3 (설계↔코드 정합 검증) + DF (설계 역류 프로토콜)
**실행 시점**: Phase 1 (D1 후 상시), Phase 4~5 (D3 집중)
**선행 조건**: D1 PASS

### 목차 (예정)

```
1. 배경 및 목적
   1.1 D1 이후 설계 무결성 유지의 필요성
   1.2 변경 전파 실패 시 리스크 (SOT↔코드 DRIFT)

2. D2: 설계 변경 추적/전파
   2.1 변경 감지 메커니즘 — integrity_snapshot diff
   2.2 영향 범위 분석 — /sot-graph 참조/피참조 맵
   2.3 연쇄 갱신 절차 — SOT → SOT 2 → CLAUDE.md → PART2
   2.4 갱신 후 재검증 — D1 부분 재실행

3. D3: 설계↔코드 정합 검증
   3.1 스키마 대조 — Pydantic 25개 모델 vs 실제 코드
   3.2 API 계약 대조 — 88개 엔드포인트 vs 실제 라우트
   3.3 모듈 구현 대조 — 187개 모듈 vs 디렉토리/파일
   3.4 LOCK 값 대조 — config.v1.toml vs SOT LOCK 정의
   3.5 레지스트리 대조 — EventType/Failure/Fallback vs 코드 실사용

4. DF: 설계 역류 프로토콜
   4.1 트리거 조건 (B2/R2에서 SOT 모순 발견)
   4.2 severity 판정 (CRITICAL/HIGH/MEDIUM)
   4.3 연쇄 영향 맵
   4.4 최대 반복 규칙 (2회 → ESCALATE)

5. 도구 및 자동화
   5.1 /integrity snapshot, /sot-graph, /sot-check method-c
   5.2 Hook 기반 반자동 감지

6. 완료 기준 및 KPI
```

---

## ③ 런타임 엔지니어링 계획서

**매트릭스 셀**: R1 (런타임 설계 확정) + R2a (코어 런타임 구현) + R2b (도메인 실행 구현) + RF (런타임 역류)
**실행 시점**: Phase 3 (R1), Phase 4 (R2a/R2b), Phase 5 (검증)
**선행 조건**: D1 PASS + Phase 2 완료

### 목차 (예정)

```
1. 배경 및 목적
   1.1 VAMOS 런타임 아키텍처 개요
   1.2 SOT 설계 → 실제 런타임 변환 전략

2. R1: 런타임 설계 확정
   2.1 5-Gate 체인 실행 순서 확정
   2.2 메모리 L0~L3 승격/강등 알고리즘
   2.3 Multi-Brain Failover 전략 (GPT→Claude→Ollama)
   2.4 LangGraph DAG 상태 전이 맵
   2.5 CostGate 임계값 (80%/100%)
   2.6 IPC 통신 프로토콜 (JSON-RPC) 사양
   2.7 MCP Streamable HTTP 계약

3. R2a: 코어 런타임 구현
   3.1 ORANGE CORE I-1~I-25 모듈 (V0: 스켈레톤)
   3.2 5-Phase Pipeline (Perception→Reasoning→Action→Reflection→Memory)
   3.3 5-Gate 체인 구현
   3.4 메모리 L0~L3 구현
   3.5 EventType/Failure/Fallback Registry
   3.6 config.v1.toml LOCK 런타임 강제
   3.7 Defense Layer 3계층 (A21)
   3.8 reasoning_trace 필드 (A22)
   3.9 confidence_score (A25) — 임계값 0.85/0.60/0.30

4. R2b: 도메인 실행 구현
   4.1 BLUE NODE 구현 (V0: Dev/Research/Productivity)
   4.2 LangGraph DAG 에이전트 워크플로우
   4.3 RAG 파이프라인 (BGE-M3 → Chroma)
   4.4 Multi-Brain Adapter (A-1)
   4.5 COND 조건부 활성화 로직
   4.6 A2A 에이전트 간 통신

5. RF: 런타임 역류 프로토콜
   5.1 트리거 조건 (R3 운영 중 아키텍처 문제)
   5.2 연쇄 영향 맵 (R1→R2a→R2b→R2c→B2c)

6. 버전별 구현 범위
   6.1 V0: 스캐폴드 13항목
   6.2 V1: 26개 CORE + E2E 파이프라인

7. 완료 기준 및 KPI
```

---

## ④ 다중 스택 통합 엔지니어링 계획서

**매트릭스 셀**: B2c (Python↔Rust↔TypeScript 동기화) + R2c (프론트엔드 구현)
**실행 시점**: Phase 3 (설계), Phase 4 (구현)
**선행 조건**: R1 IPC 확정 + B1 환경

### 목차 (예정)

```
1. 배경 및 목적
   1.1 3개 언어 스택 (Python/Rust/TypeScript) 존재 이유
   1.2 타입 불일치 리스크와 정본 원칙 (Pydantic 기준)

2. B2c: 다중 언어 타입 동기화
   2.1 Pydantic v2 → JSON Schema 추출
   2.2 JSON Schema → serde 구조체 (Rust)
   2.3 JSON Schema → TypeScript interface
   2.4 JSON-RPC 메시지 포맷 3개 언어 일치 검증
   2.5 Tauri IPC 커맨드 인터페이스 일치 확인
   2.6 타입 불일치 시 해소 절차

3. R2c: 프론트엔드 구현
   3.1 Tauri 2.0 윈도우 + 앱 셸
   3.2 React 18 컴포넌트 구현
   3.3 Rust IPC 바인딩 (invoke 커맨드)
   3.4 Hologram 렌더링 시스템 (V2+)

4. B2c↔R2c 연동 포인트
   4.1 shared_schemas/ 공유 저장소
   4.2 IPC 왕복 테스트 전략
   4.3 프론트↔백엔드 계약 검증 자동화

5. 버전별 구현 범위
   5.1 V0: Tauri 기동 + 기본 입출력
   5.2 V1: E2E 사용자 입력→응답 표시

6. 완료 기준 및 KPI
```

---

## ⑤ 횡단 엔지니어링 계획서

**매트릭스 셀**: X1 (횡단 전략 수립) + X2 (횡단 실행) + X3 (횡단 운영) + XF (횡단 역류)
**실행 시점**: Phase 2~3 (X1), Phase 4 (X2), Phase 5~6 (X3)
**선행 조건**: D1 PASS

### 목차 (예정)

```
1. 배경 및 목적
   1.1 횡단 관심사의 정의 — D/B/R 3행 이상 관통
   1.2 X행 경계 판별 기준 (STRATEGY_08 §8)

2. X1: 횡단 전략 수립
   2.1 보안 전략
       - 7개 불변 구역 강제 방법
       - Permission Matrix
       - 감사 로그 무결성
   2.2 테스트 전략
       - 테스트 피라미드 (단위→통합→E2E→멱등성→회귀)
       - 커버리지 목표 (V1: 80%+)
   2.3 버전/릴리스 전략
       - Git 브랜치 전략 (main/develop/feature/*)
       - V0→V1→V2→V3 릴리스 기준
       - Semantic Versioning
   2.4 책임 AI 전략 (A16)
       - 7개 불변 관련 자산 태깅
       - 면책 조항, 투명성 고지 기준
       - STRATEGY_05 §6 연동
   2.5 문서화 전략
       - 코드 문서 vs 설계 문서 유지 주체
       - VAMOS HOME 지식 그래프 갱신 규칙

3. X2: 횡단 실행
   3.1 보안 실행 — OWASP Top 10 스캔 + PII 필터링 + consent 관리
   3.2 테스트 실행 — 단위/통합/E2E 작성
   3.3 버전 관리 실행 — 브랜치 관리 + commitlint
   3.4 문서화 실행 — VAMOS HOME 갱신

4. X3: 횡단 운영
   4.1 정기 보안 감사
   4.2 회귀 테스트 자동 스케줄
   4.3 릴리스 관리 + 핫픽스
   4.4 지식 그래프 최신성 유지

5. XF: 횡단 역류 프로토콜
   5.1 트리거 조건 (X3 운영 중 전략 수정 필요)
   5.2 연쇄 영향 맵 (X1→X2→B2a/R2a)

6. 완료 기준 및 KPI
```

---

## ⑥ 운영 엔지니어링 계획서

**매트릭스 셀**: R3 (운영/모니터링/유지보수)
**실행 시점**: Phase 5~6
**선행 조건**: R2 전체 + B3 PASS + D3 ALIGNED

### 목차 (예정)

```
1. 배경 및 목적
   1.1 VAMOS 운영 환경 정의
   1.2 V1~V3 운영 비용 구조 (V1:₩40K, V2:₩93K, V3:₩266K)

2. Agent Dog 모니터링
   2.1 V1: SQLite 메트릭 + JSONL 로그
   2.2 V2: Langfuse + Phoenix + Grafana
   2.3 메트릭 수집 항목 정의

3. 비용 추적
   3.1 월 예산 대비 소진율 모니터링
   3.2 CostGate Alert (80% 경고, 100% 차단)

4. SLO 모니터링
   4.1 P99 latency 목표 및 임계값
   4.2 error rate 목표 및 임계값
   4.3 Alert 라우팅 (비용 80%, SelfCheck FAIL 3연속)

5. 모델 성능 Drift 감지
   5.1 Drift 정의 및 감지 기준
   5.2 Drift 대응 절차

6. 보안 감사 로그
   6.1 감사 로그 무결성 검증
   6.2 정기 검토 주기

7. 정기 회귀 테스트
   7.1 스케줄 (야간/주간)
   7.2 회귀 탐지 시 에스컬레이션

8. 운영 대시보드
   8.1 메트릭 시각화
   8.2 월간 운영 리포트 포맷

9. 완료 기준 및 KPI
```

---

> **다음 단계**: 각 계획서는 해당 Phase 진입 시 상세화한다.
> - ②설계정합: Phase 1 D1 완료 직후
> - ③런타임: Phase 3 진입 시
> - ④다중스택: Phase 3 R1 IPC 확정 직후
> - ⑤횡단: Phase 2~3 병렬
> - ⑥운영: Phase 5 진입 시
