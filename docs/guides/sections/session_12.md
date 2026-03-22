---
session: 12
sections: [13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6]
status: complete
---

# §13. D-Series — 두뇌/플래너/RAG 확장 모듈 (D-1 ~ D-6, 총 6개)

> **비유**: S-Series가 VAMOS의 **자기 성장 시스템**, B-Series가 **학습 자산 도서관**이라면, D-Series는 VAMOS의 **두뇌 업그레이드 키트**입니다. 기본 두뇌(ORANGE CORE)로도 생각할 수 있지만, D-Series를 장착하면 **더 깊이 생각하고(Think Engine)**, **그림과 소리도 이해하고(Multimodal)**, **장기 계획을 세우고(Planner)**, **개성 있게 말하고(Personality)**, **동시에 여러 생각을 하고(Parallel Brain)**, **지식 그래프로 더 똑똑하게 검색(GraphRAG)**할 수 있습니다.

[근거: D2.0-01 §5.12, CLAUDE.md §6 D-Series]

---

## D-Series 버전별 활성 여부 총괄표

| 모듈 ID | 모듈 이름 | 분류 | V0 | V1 | V2 | V3 | LOCK |
|---------|----------|------|----|----|----|----|------|
| D-1 | Think Engine (사고 엔진) | CORE | OFF | ON | ON | ON | false |
| D-2 | Multimodal Engine (멀티모달 엔진) | CORE | OFF | ON | ON | ON | false |
| D-3 | Long Horizon Planner (장기 계획 수립기) | EXP | OFF | OFF | OFF | ON | false |
| D-4 | Personality/Tone Engine (성격/톤 엔진) | EXP | OFF | OFF | OFF | ON | false |
| D-5 | Parallel General Brain (병렬 범용 두뇌) | EXP | OFF | OFF | OFF | ON | false |
| D-6 | GraphRAG / Hybrid RAG (그래프 기반 RAG) | EXP | OFF | OFF | OFF | ON | false |

> **분류 설명**: CORE = 핵심 모듈 (V1부터 항상 활성), EXP = 실험적 모듈 (V3 전용, 승인 없이 자동 ON 금지)
>
> **비용 참고**: V1에서는 D-1, D-2만 활성 → ₩40,000/월 수준. V3에서 전체 활성 시 ₩266,000/월 수준으로 증가.

[근거: D2.0-01 §5.12, §8.5.3~§8.5.5]

---

## §13.1 D-1 Think Engine (사고 엔진)

### 비유
> 사람이 어려운 문제를 풀 때 **"한 단계씩 차근차근 생각해보자"**라고 하는 것처럼, VAMOS가 복잡한 질문에 대해 **단계별로 논리적 사고**를 수행하는 엔진입니다.

### 목적
LLM(대규모 언어 모델)이 단순히 답을 "찍는" 것이 아니라, Chain-of-Thought(사고의 연쇄, 한 단계씩 논리를 이어가는 방식)나 Tree-of-Thought(사고의 나무, 여러 가능성을 동시에 탐색하는 방식)를 활용해 **깊이 있는 추론**을 수행합니다. ORANGE CORE(02)의 핵심 의사결정 과정에서 사고의 질을 높이는 역할을 합니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 사용자 질의(query), L0/L1 메모리 컨텍스트, 추론 전략(CoT/ToT 선택) |
| 출력 | 추론 결과(reasoning decisions), 단계별 사고 과정(thought trace), 행동 계획(action plan) |

### 상세 설명
- **Chain-of-Thought (CoT)**: "1단계 → 2단계 → 3단계"처럼 **직선형**으로 논리를 전개하는 방식
- **Tree-of-Thought (ToT)**: "여러 가능성을 나무처럼 분기시켜 탐색"하는 방식. 복잡한 문제에서 최적 경로를 찾을 때 유용
- TEE(Think-Execute-Evaluate) 루프의 **Think 단계**에서 핵심 역할 수행
- 02(ORANGE CORE)와 직접 연결되어 의사결정 품질을 향상시킴

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | CORE |
| V0 | OFF |
| V1 | ON |
| V2 | ON |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-02 (ORANGE CORE) |
| UI 노출 | false (내부 전용) |

### 관련 모듈
- 02 (ORANGE CORE): 의사결정 엔진과 직접 연결
- EVX-4 (Thought Buffer): 사고 과정 저장/재활용
- EVX-3 (Log-prob Confidence): 사고 결과의 신뢰도 평가

### 에러코드 / 폴백
- TEE 루프에서 Think 단계 실패 시: Soft Loop 1회 자동 재시도 → 실패 시 승인 요청 또는 중단(deny)
- P0 시나리오: TEE 최대 3회, P1: 5회, P2: 10회 반복 허용

[근거: D2.0-01 §5.12 D-1, D2.0-05 §12.5.1 TEE Loop, D2.0-02]

### 핵심 요약 (3줄)
1. D-1은 VAMOS가 **단계별 논리적 사고**(CoT/ToT)를 수행하는 핵심 엔진입니다.
2. V1부터 활성화되는 **CORE 모듈**로, ORANGE CORE(02)의 의사결정 품질을 높입니다.
3. TEE 루프의 Think 단계에서 핵심 역할을 하며, 실패 시 Soft Loop 재시도를 지원합니다.

---

## §13.2 D-2 Multimodal Engine (멀티모달 엔진)

### 비유
> 사람이 **눈으로 보고, 귀로 듣고, 손으로 만지며** 세상을 이해하듯, VAMOS가 텍스트뿐 아니라 **이미지, 음성, 영상** 등 다양한 형태의 정보를 함께 처리하는 엔진입니다.

### 목적
텍스트만 처리하던 AI를 넘어, 이미지/음성/영상 등 **다양한 입력 형태(modality)**를 통합 처리합니다. 사용자가 사진을 보내거나 음성으로 질문하더라도 VAMOS가 이해하고 적절히 응답할 수 있게 합니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 텍스트(text), 이미지(image), 음성(audio), 영상(video) — 복합 입력 가능 |
| 출력 | 통합된 멀티모달 표현(unified multimodal representation), 분석 결과 |

### 상세 설명
- 텍스트 + 이미지, 텍스트 + 음성 등 **여러 형태를 동시에 입력**받아 하나의 통합된 이해로 변환
- 02(ORANGE CORE)와 직접 연결되어 멀티모달 컨텍스트를 의사결정에 반영
- 내부 전용 모듈로, UI에 직접 노출되지 않음 (결과만 사용자에게 전달)

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | CORE |
| V0 | OFF |
| V1 | ON |
| V2 | ON |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-02 (ORANGE CORE) |
| UI 노출 | false (내부 전용) |

### 관련 모듈
- 02 (ORANGE CORE): 멀티모달 분석 결과를 의사결정에 반영
- D-1 (Think Engine): 멀티모달 컨텍스트 기반 사고 수행

### 에러코드 / 폴백
- 지원하지 않는 파일 형태 입력 시: 텍스트 전용 모드로 폴백 (fallback)
- 처리 실패 시: 02 Fallback Strategy Registry(§6.3) 참조

[근거: D2.0-01 §5.12 D-2, D2.0-02]

### 핵심 요약 (3줄)
1. D-2는 텍스트, 이미지, 음성, 영상 등 **다양한 입력을 통합 처리**하는 엔진입니다.
2. V1부터 활성화되는 **CORE 모듈**로, VAMOS의 멀티모달 이해 능력을 담당합니다.
3. 지원하지 않는 형태의 입력은 텍스트 전용 모드로 자동 폴백됩니다.

---

## §13.3 D-3 Long Horizon Planner (장기 계획 수립기)

### 비유
> 여행 계획을 세울 때 "1일차에 이동 → 2일차에 관광 → 3일차에 복귀"처럼 **여러 단계에 걸친 장기 계획**을 세우는 여행 플래너와 같습니다.

### 목적
단순한 한 번의 질의응답이 아니라, **여러 단계에 걸친 복잡한 작업**을 계획하고 실행 순서를 결정합니다. 예를 들어, "주식 분석 → 리포트 작성 → 이메일 발송"처럼 다단계 목표를 달성하기 위한 실행 계획을 수립합니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 목표 명세(goal specification), 제약 조건(constraints), 사용 가능한 도구/자원 목록 |
| 출력 | 다단계 실행 계획(multi-step plan), 단계별 의존성 관계, 예상 비용/시간 |

### 상세 설명
- **V3 전용 모듈**: V1/V2에서는 단순 Plan 단계(§7.1)로 처리하지만, V3에서는 D-3이 장기 계획을 전담
- 5단계 파이프라인(Intake → Plan → Execute → Verify → Deliver)의 **Plan 단계를 확장**하는 역할
- 02(ORANGE CORE)와 연결되어 각 단계의 의사결정을 지원
- P2(위험/확장) 도메인에서는 특히 중요 — 복잡한 작업일수록 계획의 질이 결과에 큰 영향

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | EXP (실험적) |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-02 (ORANGE CORE) |
| UI 노출 | false (내부 전용) |

### 관련 모듈
- 02 (ORANGE CORE): 계획 결과를 의사결정에 반영
- D-1 (Think Engine): 각 계획 단계의 추론 수행
- EVX-5 (Gen-Verify-Learn): 계획 실행 결과를 학습에 반영

### 에러코드 / 폴백
- 계획 수립 실패 시: 단순 단일 단계 실행으로 폴백
- 비용 예산 초과 시: G2(CostBudget) 게이트에서 차단 → 다운시프트(downshift) 또는 거부(deny)
- "검증 축소 모드"에서 D-3 깊이(depth) 축소 가능 (비용 절감)

[근거: D2.0-01 §5.12 D-3, D2.0-05 §7.1 Plan Stage]

### 핵심 요약 (3줄)
1. D-3은 여러 단계에 걸친 **복잡한 장기 작업 계획**을 수립하는 V3 전용 모듈입니다.
2. 5단계 파이프라인의 Plan 단계를 확장하여 **다단계 실행 계획과 의존성 관계**를 생성합니다.
3. 비용 예산 초과 시 G2 게이트에서 차단되며, 검증 축소 모드로 깊이 조절이 가능합니다.

---

## §13.4 D-4 Personality/Tone Engine (성격/톤 엔진)

### 비유
> 같은 내용이라도 **친구에게 말할 때**와 **교수님에게 보고할 때** 말투가 다르듯, VAMOS의 응답 스타일을 사용자 맞춤으로 조절하는 **말투 코디네이터**입니다.

### 목적
사용자의 선호도나 상황에 따라 VAMOS의 **응답 톤, 스타일, 성격**을 조절합니다. 친근한 대화체, 비즈니스 격식체, 전문가 분석체 등 다양한 톤으로 동일한 정보를 전달할 수 있게 합니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 응답할 콘텐츠, 스타일 가이드라인(사용자 설정), 톤 프리셋 |
| 출력 | 성격/톤이 적용된 최종 응답(personality-adjusted response) |

### 상세 설명
- **V3 전용 모듈**: V1/V2에서는 기본 톤(default tone)으로 응답
- 05(Agent Workflow)와 연동하여 파이프라인의 Deliver 단계에서 최종 출력 톤을 조정
- 08(UI/UX)와 연결되어 사용자 인터페이스에서 톤 설정 가능
- 톤 프리셋 예시: 친근한(casual), 격식체(formal), 분석적(analytical), 교육적(educational)

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | EXP (실험적) |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-05 (Agent Workflow) |
| UI 노출 | false (내부 전용, 08 UI에서 설정 연동) |

### 관련 모듈
- 05 (Agent Workflow): 파이프라인 Deliver 단계에서 톤 적용
- 08 (UI/UX): 사용자 톤 설정 인터페이스
- D-1 (Think Engine): 톤 적용 전 사고 결과 생성

### 에러코드 / 폴백
- 톤 적용 실패 시: 기본 톤(default)으로 폴백하여 응답 생성
- 부적절한 톤 요청 시: 07(Policy/Approval) 게이트에서 차단

[근거: D2.0-01 §5.12 D-4, D2.0-05 §7.2, D2.0-08]

### 핵심 요약 (3줄)
1. D-4는 VAMOS 응답의 **톤과 스타일을 사용자 맞춤으로 조절**하는 V3 전용 모듈입니다.
2. Agent Workflow의 Deliver 단계에서 최종 출력 톤을 적용하며, UI(08)에서 설정 가능합니다.
3. 톤 적용 실패 시 기본 톤으로 자동 폴백되며, 부적절한 요청은 Policy 게이트에서 차단됩니다.

---

## §13.5 D-5 Parallel General Brain (병렬 범용 두뇌)

### 비유
> 시험 문제를 풀 때 **혼자서 순서대로 푸는 것**이 아니라, **여러 명이 동시에 나눠 풀고 답을 합치는** 방식입니다. 여러 두뇌가 동시에 생각하여 더 빠르고 정확한 결과를 만듭니다.

### 목적
하나의 LLM이 순차적으로 처리하는 것이 아니라, **여러 LLM 인스턴스를 병렬로 실행**하여 복잡한 작업을 분산 처리합니다. Multi-Brain(다중 두뇌) 시스템의 핵심으로, A-1(MultiBrain Adapter) 및 A-4(Debate Mode)과 연동됩니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 분산 처리할 작업 목록(task distributions), 병렬 실행 설정 |
| 출력 | 병렬 처리 결과(parallel processing results), 통합된 최종 결과 |

### 상세 설명
- **V3 전용 모듈**: V1/V2에서는 단일 LLM 순차 처리
- 최대 동시 활성 에이전트 수: **3개** (LOCK — 변경 불가)
- A-1(MultiBrain Adapter)이 작업 분배를 관리하고, D-5가 실제 병렬 실행을 담당
- A-4(Debate Mode)과 연동하여 여러 두뇌가 **서로 다른 관점에서 토론**하는 방식도 지원
- 에이전트 간 직접 통신 금지 — 모든 통신은 CORE를 통해 수행 (LOCK)

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | EXP (실험적) |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-02 (ORANGE CORE) |
| UI 노출 | false (내부 전용) |

### 관련 모듈 및 제약사항
- A-1 (MultiBrain Adapter): 작업 분배/조율
- A-4 (Debate Mode): 다관점 토론 실행
- 02 (ORANGE CORE): 최종 의사결정 통합
- **병렬 에이전트 상한: 3개** (LOCK — D2.0-01 §5.12, 변경 불가)
- **에이전트 간 직접 통신 금지** (LOCK — 모든 통신은 CORE 경유)

### 에러코드 / 폴백
- 병렬 실행 실패 시: 단일 순차 실행 모드로 폴백
- Circuit Breaker(회로 차단기) 적용: 3회 연속 실패 시 OPEN 상태로 전환, 60초 후 HALF-OPEN 시도
- P2 도메인에서는 HALF-OPEN 전환에 **사용자 승인 필수** (LOCK)

[근거: D2.0-01 §5.12 D-5, D2.0-05 §4.4 Circuit Breaker, §5 Cooperative Agent]

### 핵심 요약 (3줄)
1. D-5는 **여러 LLM을 동시에 병렬 실행**하여 복잡한 작업을 분산 처리하는 V3 전용 모듈입니다.
2. 최대 동시 활성 에이전트 수는 **3개로 LOCK**(변경 불가)되어 있으며, 에이전트 간 직접 통신은 금지됩니다.
3. A-1(MultiBrain Adapter), A-4(Debate Mode)과 연동하며, 실패 시 Circuit Breaker 패턴이 적용됩니다.

---

## §13.6 D-6 GraphRAG / Hybrid RAG (그래프 기반 RAG)

### 비유
> 도서관에서 책을 찾을 때 **키워드 검색(벡터 검색)**만 하는 것이 아니라, 책들 사이의 **참고문헌 관계(지식 그래프)**까지 따라가며 연관된 자료를 함께 찾아주는 **초지능형 사서**입니다.

### 목적
기존 벡터 검색(Vector Search, 유사한 의미의 텍스트를 수학적으로 찾는 방식)에 **지식 그래프(Knowledge Graph, 정보 간의 관계를 그래프 형태로 저장한 구조)**를 결합하여 더 정확하고 깊이 있는 검색 결과를 제공합니다. RAG(Retrieval-Augmented Generation, 검색 기반 생성)의 확장 버전입니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 검색 쿼리(query), 지식 그래프 데이터, 벡터 저장소(vector store) |
| 출력 | 그래프 강화 검색 결과(graph-augmented retrieval results), 관계 경로(relation path), 근거 출처(evidence source) |

### 상세 설명
- **V3 전용 모듈**: V1/V2에서는 기본 벡터 검색만 사용
- 06(Storage/Memory)의 지식 그래프 저장소와 직접 연동
- 02(ORANGE CORE)의 I-24(Knowledge Graph Engine)와 연결
- **Hybrid 방식**: 벡터 검색(의미 기반) + 그래프 검색(관계 기반)을 동시에 수행하여 결과를 통합
- 검색 결과에 **근거 출처(evidence source)**를 함께 제공하여 검증 가능성 향상

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | EXP (실험적) |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-06 (Storage/Memory) |
| UI 노출 | false (내부 전용) |

### 관련 모듈
- 06 (Storage/Memory): 지식 그래프 및 벡터 저장소
- 02 (ORANGE CORE): I-24 Knowledge Graph Engine과 연결
- D-1 (Think Engine): 검색 결과를 기반으로 추론 수행
- EVX-3 (Log-prob Confidence): 검색 결과의 신뢰도 평가

### 에러코드 / 폴백
- 그래프 검색 실패 시: 벡터 검색 전용 모드로 폴백 (기존 RAG 방식)
- 지식 그래프 데이터 없음 시: 벡터 검색만으로 결과 생성
- 비용 예산 초과 시: G2(CostBudget) 게이트에서 차단

[근거: D2.0-01 §5.12 D-6, D2.0-06 §2, D2.0-02 I-2]

### 핵심 요약 (3줄)
1. D-6은 **벡터 검색 + 지식 그래프**를 결합하여 더 정확한 검색 결과를 제공하는 V3 전용 모듈입니다.
2. 06(Storage/Memory)의 지식 그래프와 02(ORANGE CORE)의 I-24 Knowledge Graph Engine에 연결됩니다.
3. 그래프 검색 실패 시 기존 벡터 검색 방식으로 자동 폴백되어 서비스 연속성을 보장합니다.

---

# §14. EVX-Series — 검증 확장 모듈 (EVX-1 ~ EVX-6, 총 6개)

> **비유**: VAMOS가 결과를 만들어내는 과정에서 **여러 종류의 검사관**이 순서대로 확인하는 시스템입니다. 병원에 비유하면, 혈액 검사(EVX-1), 엑스레이(EVX-2), 혈압 측정(EVX-3), 진료 기록 보관(EVX-4), 치료 후 경과 추적(EVX-5), 정밀 검사 의뢰(EVX-6)처럼 **각각 전문 분야가 다른 검증 모듈**들입니다.
>
> **중요**: EVX-Series는 VAMOS 2.0에서 **재도입(RE-ADD)**된 모듈군으로, 모두 **V3 전용**입니다.

[근거: D2.0-01 §5.13, D2.0-05 §7.4]

---

## EVX-Series 버전별 활성 여부 총괄표

| 모듈 ID | 모듈 이름 | 분류 | V0 | V1 | V2 | V3 | LOCK |
|---------|----------|------|----|----|----|----|------|
| EVX-1 | Code-as-Policy (코드 기반 정책) | RE-ADD | OFF | OFF | OFF | ON | false |
| EVX-2 | Adversarial Verifier (적대적 검증기) | RE-ADD | OFF | OFF | OFF | ON | **true** 🔒 변경 불가 |
| EVX-3 | Log-prob Confidence (확률 기반 신뢰도) | RE-ADD | OFF | OFF | OFF | ON | false |
| EVX-4 | Thought Buffer (사고 버퍼) | RE-ADD | OFF | OFF | OFF | ON | false |
| EVX-5 | Gen-Verify-Learn (생성-검증-학습 루프) | RE-ADD | OFF | OFF | OFF | ON | false |
| EVX-6 | Z3 Solver Routing (Z3 라우팅) | RE-ADD | OFF | OFF | OFF | ON | false |

> **분류 설명**: RE-ADD = 2.0에서 재도입된 모듈 (이전 버전에서 제거되었다가 V3에서 복귀)
>
> **LOCK 주의**: EVX-2(Adversarial Verifier)는 Policy/Approval(07)과의 연동 중요성 때문에 **LOCK = true** (변경 불가)

[근거: D2.0-01 §5.13]

---

## EVX-Series 공통 규칙 (LOCK)

EVX 모듈은 아래 공통 규칙을 따릅니다. 이 규칙은 **LOCK(변경 불가)**입니다.

### 배치 원칙 (Deployment Principle)
EVX 모듈은 5단계 파이프라인의 **다음 5개 실행 구간** 중 하나에 명시적으로 배치되어야 합니다:

| 구간 | 설명 | 해당 EVX |
|------|------|---------|
| Plan | 실행 전 제약/정책/불확실성 사전 생성 | EVX-1, EVX-3, EVX-6 |
| Execute | (선택) 실행 중 결과 검증/재검증 | EVX-4 |
| Verify | 최종 검증 (자기 확인/적대적/제약 검증) | EVX-1, EVX-2, EVX-3, EVX-4, EVX-5, EVX-6 |
| Memory | 저장 전 검증 (저장 정책/민감도/증거 품질) | — |
| Reflection | 사후 평가/학습 신호 생성 (즉시 적용 금지 → 신호만) | EVX-5 |

### 기록 원칙 (Recording Principle)
- 실행된 EVX 모듈은 반드시 `Decision.verify.chain_used`에 EVX-ID로 기록
- 게이트 결과는 `Decision.gates.result.*`에 기록 (Policy/Approval/Cost/Evidence)

### 공통 차단 조건 (Blocking Conditions)
- **PolicyCheck = deny** → 실행/재시도 없이 즉시 중단
- **비용 한도 초과/차단** → 승인 없이 EVX 확장 실행 금지
- **P2 도메인 관련 EVX** → 승인 없이 실행 불가
- **Self-check 임계값 미달** → Soft Loop 최대 1회 허용

[근거: D2.0-05 §7.4.1, LOCK]

---

## §14.1 EVX-1 Code-as-Policy (코드 기반 정책)

### 비유
> 회사의 규칙을 "말로 적은 규정집" 대신 **"자동 실행되는 프로그램 코드"**로 만드는 것입니다. 코드로 작성된 정책은 사람의 해석 차이 없이 **항상 동일하게 적용**됩니다.

### 목적
보안 정책, 비용 규칙, 접근 제한 등 VAMOS의 **정책(Policy)을 코드로 표현하고 자동 실행**합니다. 자연어로 작성된 정책은 해석이 모호할 수 있지만, 코드 정책은 정확하고 일관성 있게 검증됩니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 정책 명세(policy specifications), 검증 대상 코드/데이터 |
| 출력 | 정책 검증 결과(policy-verified decisions), 위반 사항 목록 |

### 상세 설명
- **배치 구간**: Plan/Verify — 실행 전 사전 정책 확인 + 최종 정책 검증
- 기록: `Decision.verify.chain_used += [EVX-1]`, `gates.result.policy` 참조
- 07(Policy/Approval)과 연동하여 정책 준수 여부를 코드 레벨에서 자동 검증
- UI: **Builder 패널**에서 정책 코드 확인 가능

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | RE-ADD |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-02 (ORANGE CORE) |
| UI 노출 | true — Builder 패널 |

### 차단 조건
- Policy deny → 즉시 중단
- P2 도메인에서 승인 없이 실행 불가

### 관련 모듈
- 05 (Agent Workflow): 파이프라인 Plan/Verify 단계 연동
- 07 (Policy/Approval): 정책 규칙 원본 관리

[근거: D2.0-01 §5.13 EVX-1, D2.0-05 §7.4, D2.0-02 §10.2]

### 핵심 요약 (3줄)
1. EVX-1은 **정책을 코드로 표현하여 자동 검증**하는 V3 전용 재도입 모듈입니다.
2. Plan/Verify 두 구간에 배치되어 사전/사후 정책 검증을 수행합니다.
3. Builder 패널에서 UI 확인이 가능하며, Policy deny 시 즉시 중단됩니다.

---

## §14.2 EVX-2 Adversarial Verifier (적대적 검증기)

### 비유
> 변호사가 자기 주장을 발표한 후, **상대편 변호사(Devil's Advocate)**가 일부러 반박을 시도하여 약점을 찾아내는 **법정 공방**과 같습니다. 의도적으로 공격해봐야 진짜 강한지 알 수 있습니다.

### 목적
VAMOS의 의사결정 결과를 **의도적으로 반박하고 공격(adversarial attack)**하여, 숨겨진 약점이나 논리적 허점을 발견합니다. 자기 검증(self-check)만으로는 놓칠 수 있는 문제를 적대적 시뮬레이션을 통해 찾아냅니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 검증 대상(claims), 관련 증거(evidence) |
| 출력 | 적대적 검증 결과(adversarial verification results), 발견된 취약점 목록 |

### 상세 설명
- **배치 구간**: Verify — 최종 검증 단계에서만 실행
- 기록: `Decision.verify.chain_used += [EVX-2]`, `evidence_ref` (존재 시)
- 07(Policy/Approval)과 연동하여 정책/승인 관련 검증 수행
- UI: **Builder + Hologram 패널** 모두에서 결과 확인 가능
- **LOCK = true** 🔒 — Policy/Approval(07) 연동의 중요성 때문에 변경 불가

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | RE-ADD |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| **LOCK** | **true 🔒 변경 불가** |
| 소유 문서 | D2.0-02 (ORANGE CORE) |
| UI 노출 | true — Builder + Hologram 패널 |

### 차단 조건
- 비용 차단 시 → 실행 금지
- 승인 필요하지만 미승인 시 → 실행 금지

### 관련 모듈
- 05 (Agent Workflow): Verify 단계 연동
- 07 (Policy/Approval): 정책 준수 검증 (LOCK 연동)
- 08 (UI/UX): Hologram 패널에서 적대적 검증 결과 시각화

[근거: D2.0-01 §5.13 EVX-2, D2.0-05 §7.4, D2.0-07 §5]

### 핵심 요약 (3줄)
1. EVX-2는 **의도적 반박을 통해 의사결정의 약점을 발견**하는 V3 전용 검증 모듈입니다.
2. **LOCK = true (변경 불가)** — Policy/Approval(07)과의 연동 중요성 때문에 잠겨 있습니다.
3. Builder + Hologram 양쪽 패널에서 결과를 확인할 수 있으며, 비용/승인 차단 시 실행이 금지됩니다.

---

## §14.3 EVX-3 Log-prob Confidence (확률 기반 신뢰도)

### 비유
> 시험에서 "정답에 대해 얼마나 확신하는지" **자신감 점수**를 매기는 것과 같습니다. LLM이 "90% 확신"이라고 하면 믿을 만하지만, "30% 확신"이라면 추가 확인이 필요하다는 신호입니다.

### 목적
LLM이 답변을 생성할 때 내부적으로 계산하는 **Log-probability(로그 확률, 각 단어/토큰의 선택 확률을 로그 스케일로 표현한 값)**를 분석하여, 응답의 **신뢰도(confidence)**를 수치화합니다. 신뢰도가 낮으면 추가 검증이나 사용자 확인을 요청합니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 모델 출력(model outputs with log-probabilities) |
| 출력 | 신뢰도 점수(confidence scores), 불확실성 신호(uncertainty signal) |

### 상세 설명
- **배치 구간**: Plan/Verify — 사전 불확실성 신호 생성 + 최종 신뢰도 검증
- 기록: `Decision.verify.chain_used += [EVX-3]`, `optional_signals(uncertainty)`
- 신뢰도가 임계값 미만일 경우 → 추가 검증 트리거 또는 사용자 확인 요청
- UI: **Builder 패널**에서 신뢰도 점수 확인 가능

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | RE-ADD |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-02 (ORANGE CORE) |
| UI 노출 | true — Builder 패널 |

### 차단 조건
- 비용 차단 시 → 확장 실행 금지

### 관련 모듈
- 02 (ORANGE CORE): 의사결정 신뢰도 평가
- 05 (Agent Workflow): Plan/Verify 단계 연동
- D-1 (Think Engine): 사고 결과의 신뢰도 평가
- D-6 (GraphRAG): 검색 결과의 신뢰도 평가

[근거: D2.0-01 §5.13 EVX-3, D2.0-05 §7.4]

### 핵심 요약 (3줄)
1. EVX-3은 LLM 출력의 **Log-probability를 분석하여 신뢰도를 수치화**하는 V3 전용 모듈입니다.
2. Plan/Verify 구간에서 불확실성 신호를 생성하며, 신뢰도가 낮으면 추가 검증을 트리거합니다.
3. Builder 패널에서 신뢰도 점수를 확인할 수 있으며, 비용 차단 시 확장 실행이 금지됩니다.

---

## §14.4 EVX-4 Thought Buffer (사고 버퍼)

### 비유
> 수학 문제를 풀 때 **연습장에 중간 계산 과정을 적어두는 것**과 같습니다. 나중에 비슷한 문제를 풀 때 연습장을 다시 보면 시간을 절약할 수 있고, 어디서 틀렸는지도 확인할 수 있습니다.

### 목적
VAMOS가 문제를 해결하는 과정에서 발생하는 **중간 사고 과정(intermediate reasoning steps)**을 임시 저장하고, 필요할 때 재활용합니다. 같은 문제를 다시 풀 때 처음부터 시작하지 않아도 되고, 디버깅(오류 추적) 시에도 유용합니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 중간 추론 단계(intermediate reasoning steps) |
| 출력 | 버퍼링된 사고 표현(buffered thought representations), 추적 참조(trace_ref) |

### 상세 설명
- **배치 구간**: Execute/Verify — 실행 중 사고 과정 저장 + 검증 시 참조
- 기록: `Decision.verify.chain_used += [EVX-4]`, `trace_ref`
- UI: **Builder + Hologram 패널** 모두에서 사고 과정 시각화 가능
- 08(UI/UX)에서 사고 버퍼 표면(surface) 정의가 필요한 상태
- 민감 데이터(sensitive data) 감지 시 → 저장 금지 (차단)

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | RE-ADD |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-02 (ORANGE CORE) |
| UI 노출 | true — Builder + Hologram 패널 |

### 차단 조건
- Policy deny → 즉시 중단
- 민감 데이터 감지 → 저장 금지

### 관련 모듈
- 05 (Agent Workflow): Execute/Verify 단계 연동
- 08 (UI/UX): Hologram 패널에서 사고 과정 시각화
- D-1 (Think Engine): 사고 과정의 원본 생성

[근거: D2.0-01 §5.13 EVX-4, D2.0-05 §7.4, D2.0-08 §2]

### 핵심 요약 (3줄)
1. EVX-4는 **중간 사고 과정을 저장하고 재활용**하는 V3 전용 버퍼 모듈입니다.
2. Execute/Verify 구간에서 작동하며, Builder + Hologram 양쪽 패널에서 시각화됩니다.
3. 민감 데이터가 감지되면 저장이 차단되며, Policy deny 시 즉시 중단됩니다.

---

## §14.5 EVX-5 Gen-Verify-Learn (생성-검증-학습 루프)

### 비유
> 요리사가 음식을 만들고(생성) → 맛을 보고(검증) → 레시피를 수정하는(학습) **반복 개선 과정**과 같습니다. 매번 더 나은 결과를 만들어내는 자동 개선 루프입니다.

### 목적
VAMOS의 출력 결과를 **자동으로 생성(Generate) → 검증(Verify) → 학습(Learn)**하는 순환 루프를 실행합니다. 다만, 학습 결과는 **즉시 적용되지 않고 "학습 신호(learn_hint)"로만 기록**되며, 실제 적용에는 별도 승인이 필요합니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 생성된 출력(generation outputs) |
| 출력 | 검증된 결과(verified results), 학습 힌트 신호(learn_hint signal) |

### 상세 설명
- **배치 구간**: Verify/Reflection — 최종 검증 + 사후 학습 신호 생성
- 기록: `Decision.verify.chain_used += [EVX-5]`, `optional_signals(learn_hint)`
- **중요 제약**: 학습 결과의 **자동 적용(auto-apply) 금지** — 신호만 기록하며, 실제 적용은 별도 승인 후에만 가능
- 05(Agent Workflow)와 연동하여 워크플로우 개선 신호를 전달
- UI: **Builder 패널**에서 학습 신호 확인 가능

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | RE-ADD |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-02 (ORANGE CORE) |
| UI 노출 | true — Builder 패널 |

### 차단 조건
- 자동 적용(auto-apply) 금지 — 신호만 기록 (승인 전까지)

### 관련 모듈
- 05 (Agent Workflow): 워크플로우 개선 연동
- D-3 (Long Horizon Planner): 계획 결과의 학습 루프

[근거: D2.0-01 §5.13 EVX-5, D2.0-05 §7.4]

### 핵심 요약 (3줄)
1. EVX-5는 **생성→검증→학습의 자동 개선 루프**를 실행하는 V3 전용 모듈입니다.
2. 학습 결과는 **즉시 적용 금지** — 학습 힌트 신호(learn_hint)로만 기록되며 별도 승인이 필요합니다.
3. Verify/Reflection 구간에서 작동하며, Builder 패널에서 학습 신호를 확인할 수 있습니다.

---

## §14.6 EVX-6 Z3 Solver Routing (Z3 라우팅)

### 비유
> 복잡한 수학 문제를 사람이 직접 풀지 않고 **전문 계산기(Z3 Solver)**에게 넘겨서 정확한 답을 구하는 **문제 배분 담당자**입니다. 모든 문제를 Z3에 보내는 것이 아니라, **Z3가 필요한 문제인지 판단**하고 라우팅합니다.

### 목적
수학적 제약 조건(constraint)을 만족하는지 확인해야 할 때, **Z3 SMT Solver(Satisfiability Modulo Theories Solver, 수학적 만족 가능성을 검증하는 자동 증명 도구)**가 필요한지 판단하고, 필요한 경우 Z3로 라우팅하여 정확한 검증 결과를 받습니다.

### 입력 / 출력

| 구분 | 내용 |
|------|------|
| 입력 | 제약 만족 문제(constraint satisfaction problems) |
| 출력 | 해결된 제약 결과(solved constraints), 제약 참조(constraint_ref) |

### 상세 설명
- **배치 구간**: Plan/Verify — 사전 제약 확인 + 최종 제약 검증
- 기록: `Decision.verify.chain_used += [EVX-6]`, `gates.result.evidence/constraint_ref`
- 04(Infrastructure)와 연결되어 솔버(solver) 인프라에 접근
- 모든 문제를 Z3에 보내는 것이 아니라, **Z3 검증이 필요한지 먼저 판단(routing)** → 필요한 경우에만 실행
- UI: **Builder 패널**에서 제약 검증 결과 확인 가능

### 분류 / 버전 / LOCK

| 항목 | 값 |
|------|-----|
| 분류 | RE-ADD |
| V0 | OFF |
| V1 | OFF |
| V2 | OFF |
| V3 | ON |
| LOCK | false |
| 소유 문서 | D2.0-04 (Infrastructure) |
| UI 노출 | true — Builder 패널 |

### 차단 조건
- Policy deny → 즉시 중단
- 솔버 실행에 승인 필요하지만 미승인 시 → 실행 금지

### 관련 모듈
- 04 (Infrastructure): Z3 솔버 인프라 제공
- 02 (ORANGE CORE): 제약 검증 결과를 의사결정에 반영
- EVX-1 (Code-as-Policy): 코드 정책의 제약 조건 검증

[근거: D2.0-01 §5.13 EVX-6, D2.0-05 §7.4, D2.0-04 §7]

### 핵심 요약 (3줄)
1. EVX-6은 **Z3 SMT Solver가 필요한 문제를 판단하고 라우팅**하는 V3 전용 검증 모듈입니다.
2. Plan/Verify 구간에서 작동하며, 04(Infrastructure)의 솔버 인프라에 접근합니다.
3. 모든 문제에 Z3를 적용하는 것이 아니라, **필요 여부를 먼저 판단**하여 효율적으로 실행합니다.

---

# D-Series + EVX-Series 통합 비교표

## 전체 12개 모듈 한눈에 보기

| # | 모듈 ID | 모듈 이름 | 비유 (한 줄) | 분류 | V1 | V2 | V3 | LOCK |
|---|---------|----------|-------------|------|----|----|----|----|
| 1 | D-1 | Think Engine | 단계별 논리 사고 엔진 | CORE | ON | ON | ON | false |
| 2 | D-2 | Multimodal Engine | 눈/귀/손으로 세상 이해 | CORE | ON | ON | ON | false |
| 3 | D-3 | Long Horizon Planner | 여행 계획 플래너 | EXP | OFF | OFF | ON | false |
| 4 | D-4 | Personality/Tone Engine | 말투 코디네이터 | EXP | OFF | OFF | ON | false |
| 5 | D-5 | Parallel General Brain | 여러 명이 동시에 문제 풀기 | EXP | OFF | OFF | ON | false |
| 6 | D-6 | GraphRAG / Hybrid RAG | 초지능형 사서 | EXP | OFF | OFF | ON | false |
| 7 | EVX-1 | Code-as-Policy | 자동 실행 규정집 | RE-ADD | OFF | OFF | ON | false |
| 8 | EVX-2 | Adversarial Verifier | 상대편 변호사 반박 | RE-ADD | OFF | OFF | ON | **true 🔒** |
| 9 | EVX-3 | Log-prob Confidence | 자신감 점수 매기기 | RE-ADD | OFF | OFF | ON | false |
| 10 | EVX-4 | Thought Buffer | 연습장 중간 계산 | RE-ADD | OFF | OFF | ON | false |
| 11 | EVX-5 | Gen-Verify-Learn | 요리-맛보기-레시피수정 | RE-ADD | OFF | OFF | ON | false |
| 12 | EVX-6 | Z3 Solver Routing | 전문 계산기 배분 담당 | RE-ADD | OFF | OFF | ON | false |

## EVX-Series 배치 구간 매핑

```
파이프라인:  Plan ──→ Execute ──→ Verify ──→ Memory ──→ Reflection
             │          │          │                      │
EVX 배치:   EVX-1     EVX-4     EVX-1                   EVX-5
            EVX-3                EVX-2
            EVX-6                EVX-3
                                 EVX-4
                                 EVX-5
                                 EVX-6
```

[근거: D2.0-01 §5.12~§5.13, D2.0-05 §7.4.1]

---

### 핵심 요약 — §13 D-Series (3줄)
1. D-Series는 VAMOS의 **두뇌 확장 모듈 6개**로, D-1/D-2는 CORE(V1~), D-3~D-6은 EXP(V3 전용)입니다.
2. 사고(Think) → 멀티모달 → 장기계획 → 성격/톤 → 병렬두뇌 → 그래프RAG 순으로 **인지 능력을 단계적 확장**합니다.
3. 병렬 에이전트 상한 3개(LOCK), 에이전트 간 직접 통신 금지(LOCK) 등 핵심 제약이 존재합니다.

### 핵심 요약 — §14 EVX-Series (3줄)
1. EVX-Series는 **검증 확장 모듈 6개**로, 모두 RE-ADD 분류의 V3 전용 모듈입니다.
2. 5단계 파이프라인의 **Plan/Execute/Verify/Reflection 구간에 선택적으로 배치**되며, 실행 기록은 Decision에 필수 기록됩니다.
3. EVX-2(Adversarial Verifier)만 **LOCK = true**(변경 불가)이며, 전체 EVX는 Policy/Cost/Approval 차단 조건을 공유합니다.
