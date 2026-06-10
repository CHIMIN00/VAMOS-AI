# H7: Step-Back Prompting — 구현 명세

> **도메인**: 5-2_File-Context (DEFINED-HERE)  
> **파이프라인 위치**: Phase E — E-4 (검색)  
> **버전**: V1 (CORE)  
> **난이도**: Easy  
> **핵심 도구**: LangChain step-back 프롬프트 템플릿 (AUTHORITY_CHAIN §3.3)  
> **대안 도구**: LlamaIndex step-back workflow (SOT §8 H7)  
> **상위 문서**: `../FILE_CONTEXT_구조화_종합계획서.md` §6.4 H 상세표

---

## 1. 개요

### 1.1 문제 정의

매우 구체적인 질문("D2.0-06 L776의 alpha 값은?")은 너무 좁은 범위만 검색하여 맥락이 부족하다. 직접 검색으로는 해당 라인만 반환되고, 그 값이 왜 그렇게 설정되었는지, 어떤 맥락에서 사용되는지 등의 배경 정보가 누락된다.

### 1.2 해결 전략

원래 질문의 **"한 단계 추상화" 버전**을 LLM으로 생성 → **원본 질문 + 추상화 질문** 모두 검색 → 결과를 결합하여 구체적 답변과 맥락 정보를 동시에 제공한다.

| 단계 | 설명 | 예시 |
|------|------|------|
| 1. 추상화 | 구체 질문 → 상위 개념 질문 | "alpha 값은?" → "Hybrid Search 가중치 설계 원칙은?" |
| 2. 병렬 검색 | 원본 + 추상화 각각 검색 | 원본: L776 청크 / 추상화: Hybrid Search 전체 설계 청크 |
| 3. 결합 | 양쪽 결과 RRF 융합 | 구체적 값 + 설계 맥락 동시 제공 |

### 1.3 기대 효과

- **기존 오류의 39.9% 수정** (SOT §8 H7 — Zheng et al., 2023 근거)
- **RAG 단독 오류의 21.6% 추가 수정** (SOT §8 H7)
- H2 Query Decomposition과 병행 시 양방향 검색 효과

---

## 2. 파이프라인 배치

```
Phase E: 분할 처리 (200K+)
  E-1~E-3: 청킹, 임베딩 준비
  ──────────────────────────────────────
  E-4:   검색 ([H1]HyDE+[H4]RAG-Fusion
         +[H7]StepBack ◀── 본 기술
         +[H15]Metadata+4-Index Fusion+ColBERT)
  ──────────────────────────────────────
  E-5:   2단 Reranking+[H6]CoN+[H14]Compression
```

### 2.1 실행 조건

| 조건 | 설명 |
|------|------|
| 활성화 트리거 | 구체적 질문(특정 파일/라인/값 지칭)에 선택적 활성화 |
| 비활성화 | 이미 추상적/광범위한 질문은 스킵 (추상화 불필요) |
| 선행 단계 | E-1~E-3 완료, A-10 H2 Query Decomposition(해당 시) |
| 후속 단계 | 검색 결과 → E-5 Reranking으로 전달 |
| 병행 기술 | H1 HyDE, H4 RAG-Fusion과 E-4 내에서 병행 실행 |

---

## 3. 구현 상세

### 3.1 핵심 도구: LangChain Step-Back 프롬프트 템플릿

```python
# R1: Python 3.11+ 필수
# R2: Pydantic v2 스키마 검증

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

class StepBackResult(BaseModel):
    """Step-Back 결과 (R2 Pydantic v2)"""
    original_query: str
    step_back_query: str
    abstraction_level: str = Field(description="concept | principle | category | overview")
    original_results: list[dict]
    step_back_results: list[dict]
    fused_results: list[dict]  # RRF 융합 후
```

### 3.2 추상화 프롬프트

```python
from langchain_community.chat_models import ChatOllama  # [A8] 로컬 모델 (비용 0)

STEP_BACK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at abstracting specific questions into broader concepts.
Given a specific question, generate a more general "step-back" question that captures 
the underlying concept or principle.

Rules:
- Preserve the domain context (VAMOS AI, file context, RAG, etc.)
- The step-back question should be one abstraction level higher
- Output only the step-back question, nothing else
- Keep the same language as the input (Korean/English)

Examples:
- "D2.0-06 L776의 alpha 값은?" → "Hybrid Search 가중치 설계 원칙은?"
- "Mecab-ko의 복합 명사 분석 방법은?" → "한국어 형태소 분석의 청킹 적용 전략은?"
- "RRF k=60 선택 근거는?" → "검색 결과 융합 알고리즘 비교 및 파라미터 선택 기준은?"
"""),
    ("human", "{question}")
])

def create_step_back_chain(llm=None):
    """
    Step-Back 추상화 체인 생성.
    
    2단계 로직:
    1. LLM이 원본 질문을 추상화 (Step-Back)
    2. 원본 + 추상화 질문 모두 검색 → RRF 융합
    """
    if llm is None:
        llm = ChatOllama(model="llama3.1:8b")  # [A8] 로컬 모델 (비용 0)
    
    return STEP_BACK_PROMPT | llm
```

### 3.3 2단계 검색 및 결합

```python
async def step_back_search(
    query: str,
    retriever,
    step_back_chain,
    rrf_k: int = 60,  # L2 LOCK: RRF k=60
):
    """
    Step-Back 2단계 검색.
    
    1단계: 원본 질문 추상화
    2단계: 원본 + 추상화 병렬 검색 → RRF 융합
    """
    # 1단계: 추상화
    step_back_query = (await step_back_chain.ainvoke({"question": query})).content
    
    # 2단계: 병렬 검색
    import asyncio
    original_results, step_back_results = await asyncio.gather(
        retriever.ainvoke(query),
        retriever.ainvoke(step_back_query),
    )
    
    # RRF 융합 (L2 LOCK k=60)
    # reciprocal_rank_fusion(): h04_rag_fusion.md §3.3 정의 공유
    fused = reciprocal_rank_fusion(
        [original_results, step_back_results],
        k=rrf_k,
    )
    
    return StepBackResult(
        original_query=query,
        step_back_query=step_back_query,
        abstraction_level="concept",
        original_results=original_results,
        step_back_results=step_back_results,
        fused_results=fused,
    )
```

---

## 4. LOCK 참조

본 기술은 DEFINED-HERE 항목(5-2 도메인 소유)이며 별도 LOCK 값은 없다. 검색 결과 융합 시 아래 LOCK을 준수한다:

| LOCK | 값 (SOT 원문) | 연동 |
|------|--------------|------|
| **L2** | `alpha * bm25_score + (1-alpha) * vector_score`, alpha=0.3, RRF k=60, top-10→reranker→top-3~5 | 원본+추상화 결과 RRF 융합 시 k=60 적용. 최종 top-10 → E-5 reranker |

---

## 5. 거버넌스 준수

| 규칙 | 준수 내용 |
|------|----------|
| R1 | Python 3.11+ — asyncio 기반 병렬 검색 (원본+추상화 동시) |
| R2 | `StepBackResult` Pydantic v2 BaseModel |
| R6 | 모든 파라미터(추상화 레벨, RRF k=60)는 본 명세 또는 SOT 원본에 근거 |
| R7 | V1 범위 — 파이프라인 배치도 내 V2 항목(L14 ColBERT 등)은 위치 맥락 표시용이며, 본 기술이 V2에 의존하지 않음 |
| R9 | 추상화 질문 및 내부 검색 과정은 사용자 응답에 미노출 |
| R10 | [A8] 로컬 모델 기본 사용 (비용 0) |

---

## 6. 벤치마크 연동 (§12)

| 메트릭 | 기준선 | H7 기여 |
|--------|--------|---------|
| Faithfulness | ≥ 0.85 | 추상화 검색으로 맥락 보강 → 기존 오류 39.9% 수정 |
| Answer Relevancy | ≥ 0.80 | 구체적 답변 + 맥락 정보 → 응답 완성도 향상 |
| Context Recall | ≥ 0.75 | 추상화 질문으로 관련 청크 추가 회수 → 회수율 향상 |

---

## 7. 시너지 관계

| 대상 | 관계 | 설명 |
|------|------|------|
| H1 (HyDE) | 병행 | HyDE 가상 문서(구체적) + Step-Back 추상화 → 양방향 검색 커버리지 |
| H4 (RAG-Fusion) | 병행 | Fusion 용어 다양화 + Step-Back 개념 추상화 → 다차원 검색 |
| H2 (Query Decomposition) | 병행 | H2 구체적 분해 + H7 추상화 → SOT §8 H7 "H2와 병행" 권고 |
| H15 (Metadata Filtering) | 연동 | 검색 시 H15 메타데이터 필터 적용 |

---

## 8. 성능 기대치

| 항목 | 값 |
|------|-----|
| 추상화 생성 지연 | < 500ms (로컬 LLM 기준) |
| 병렬 검색 지연 | < 2초 (원본+추상화 비동기) |
| 기존 오류 수정률 | 39.9% (SOT §8 H7 — Zheng et al., 2023) |
| RAG 단독 오류 추가 수정 | 21.6% (SOT §8 H7) |
| 추가 비용 | 0 ([A8] 로컬 모델) |
