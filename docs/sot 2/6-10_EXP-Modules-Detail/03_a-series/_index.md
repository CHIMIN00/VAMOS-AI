# 03. A-Series — 고급 AI 모듈 (Advanced AI)

> **도메인**: 6-10_EXP-Modules-Detail
> **서브폴더**: 03_a-series
> **정본 출처**: D2.0-01 (산재: §0.5, §0.6, §5.10 등 — A-Series 관련 정의 분산)
> **모듈 수**: 4 (A-3, A-5, A-6, A-7)
> **상태**: Phase 0 — 인터페이스 정의

---

## 1. 개요

A-시리즈는 VAMOS의 고급 AI 역량을 담당하는 모듈 그룹이다. 메타 AI(A-3), 지연 생성(A-5), 연합 학습(A-6), 원격 실행(A-7)으로 구성된다.

> **참고**: A-1(Multi-Brain Adapter)은 6-9_Brain-Adapter-HAL에서, A-2(MCTS)는 1-1_Verifier-Reasoning에서, A-4(기타)는 기타 도메인에서 관리. 본 서브폴더는 A-3, A-5, A-6, A-7만 수록.

---

## 2. 모듈 요약

| ID | 모듈명 | Input 타입 | Output 타입 | 핵심 알고리즘 | 패키지 |
|----|--------|-----------|-----------|-------------|--------|
| A-3 | Meta AI | MetaAnalysisRequest | MetaReport | 모듈 성능 통계 분석 + 자동 튜닝 권고 | — |
| A-5 | Lazy Generation | LazyRequest | LazyResult | 지연 생성 + 배치 판단 + 불필요 호출 차단 | — |
| A-6 | Federated | FederatedRequest | FederatedResult | FedAvg 연합 학습 (그래디언트만 교환) | — |
| A-7 | Remote Executor | RemoteTask | RemoteResult | SSH/K8s Job 원격 실행 + 재시도 | paramiko, kubernetes |

---

## 3. 의존성 관계

```
I-18 (Self-evo Engine, 6-6) ──→ A-3 (Meta AI)
                                   │
                                   ├──→ A-5 (Lazy Generation) ──→ Brain Adapter (6-9)
                                   └──→ A-7 (Remote Executor) ←── A-6 (Federated)
                                                                      │
                                                                      └──→ 07 Approval Gate
```

---

## 4. DEFER 항목

| DEFER ID | 항목 | 차단 이유 | 해제 조건 |
|----------|------|----------|----------|
| DEFER-AT-004 | A-6 Federated 인증/승인 프로토콜 | 연합 에이전트 인증 프로토콜 미정의 | mTLS + JWT 인증 스펙 확정 + 07 승인 워크플로우 문서화 |

---

## 5. L3 상태 요약

| 모듈 | L3 시트 | Input/Output | 알고리즘 | 에러 처리 | 테스트 기준 | 비고 |
|------|---------|:----------:|:-------:|:--------:|:---------:|------|
| A-3 | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| A-5 | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| A-6 | ✅ | ✅ | ✅ | DEFER | DEFER | DEFER-AT-004 |
| A-7 | ✅ | ✅ | ✅ | ✅ | ✅ | — |

> 상세 L3 시트는 상위 카탈로그 문서 §2 참조
