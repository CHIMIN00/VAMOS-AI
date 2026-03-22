---
session: 02
sections: [2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8]
status: complete
---

# 2. 전체 아키텍처 — 4계층 구조

> 이 섹션에서는 VAMOS의 전체 구조를 4개 계층으로 나누어 설명합니다. 사용자의 요청이 어떤 경로를 거쳐 최종 답변이 되는지, 각 계층이 어떤 역할을 하는지를 이해할 수 있습니다.
> [근거: D2.0-01 §2.1~§2.3 / PLAN-3.0 §1.3(A)~(D) / BEGINNER_GUIDE §2장]

---

## 2.1 아키텍처 개요도

### 비유로 이해하기

VAMOS의 구조를 **병원**에 비유하면 이렇습니다:

| 병원 비유 | VAMOS 계층 | 하는 일 |
|-----------|------------|---------|
| **접수처** | Front Mini LLM | "무슨 증상이세요?" — 요청을 처음 받고 분류 |
| **원장실** | ORANGE CORE | "이 환자는 내과로, 이 검사부터" — 판단/지시/관리 |
| **진료과** | BLUE NODES | "내과", "외과", "정형외과" — 분야별 전문 진료 |
| **검사실/약국** | OTHER BRAINS | "혈액검사", "MRI", "처방" — 실제 도구 실행 |
| **진료 결과지** | Main/Hologram LLM | 최종 결과를 정리하여 환자에게 전달 |

> [근거: BEGINNER_GUIDE §2.1]

### 전체 구조도 (ASCII 다이어그램)

```
┌─────────────────────────────────────────────────────────────────┐
│                       사용자 입력 (User Request)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  [1계층] Front Mini LLM ─── 의도 파악, 도메인 판별, 안전 필터링     │
│          (입구 경비원 — 빠르고 가벼운 AI 모델)                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  [2계층] ORANGE CORE ──── 정책 확인, 비용 계산, 라우팅 결정,        │
│          승인 관리 (두뇌/지휘관 — I-1~I-25 모듈 관장)               │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│   │ I-1      │ │ I-2      │ │ I-5      │ │ I-6      │          │
│   │ Intent   │→│ Evidence │→│ Decision │→│ Self-chk │          │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│          ↓                                                      │
│   ┌─────────────────────────────────────────────┐              │
│   │  Policy / Cost / Approval Gates (안전 게이트)  │              │
│   └─────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
          │                                │
          ▼                                ▼
┌────────────────────┐          ┌────────────────────┐
│ [3계층] BLUE NODES │          │ [4계층] OTHER      │
│  (실행팀)           │          │  BRAINS / INFRA    │
│ P0: Dev/Research   │◄────────►│ Multi-Brain Adapter│
│ P1: Content/Quant  │          │ Tool Runtime       │
│ P2: Trading(승인)  │          │ Solver/Sandbox     │
└────────────────────┘          └────────────────────┘
          │                                │
          └──────────────┬─────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Main/Hologram LLM ── 최종 출력 생성 (3-Part Output)              │
│  (사용자 응답 + 근거/요약 + 로그/리포트)                             │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    사용자에게 전달 (Final Output)                   │
└─────────────────────────────────────────────────────────────────┘
```

> 이 구조는 **"LLM + 중앙 제어 + 실행 계층 + LLM"**이라는 양방향 흐름입니다.
> CORE는 **결정 구조**, NODE는 **행동 엔진**, OTHER BRAINS는 **실행 자원**입니다.
> [근거: D2.0-01 §2.1 / PLAN-3.0 §1.3(A)]

---

## 2.2 1계층: Front Mini LLM — 입구 경비원

### 비유

**건물 입구의 경비원**을 상상해보세요. 경비원은 방문자가 오면:
1. "누구세요? 무슨 용건이세요?" (의도 파악)
2. "이 건물에 출입 가능한 분인가요?" (안전 확인)
3. "그러면 3층 회의실로 가세요" (적절한 곳으로 안내)

Front Mini LLM이 바로 이 역할입니다.

### 정의

**Front Mini LLM**(프론트 미니 LLM)은 사용자의 입력을 **가장 먼저** 받는 작고 빠른 AI 모델입니다. 비용이 저렴한 경량 모델(예: GPT-4o mini)을 사용하여, 모든 요청을 빠르게 1차 처리합니다. [근거: PLAN-3.0 §1.3(A)]

### Front Mini LLM이 하는 일 3가지

| # | 하는 일 | 설명 | 비유 |
|---|---------|------|------|
| 1 | **의도 파악 (Intent Detection)** | 사용자가 무엇을 원하는지 분석. "코딩인지, 리서치인지, 분석인지" 판별 | "무슨 용건이세요?" |
| 2 | **도메인 판별 (Domain Classification)** | 어떤 분야(P0/P1/P2)에 해당하는지 분류 | "어느 부서로 안내할까요?" |
| 3 | **안전 필터링 (Safety Filtering)** | 위험하거나 금지된 요청을 즉시 차단 | "출입 금지 구역입니다" |

### 작동 예시

```
사용자: "삼성전자 최근 실적 분석해줘"

Front Mini LLM 판단:
├── 의도: "데이터 분석/리서치" ✅
├── 도메인: P1_Data&Quant (1회 승인 필요)
├── 안전: 위험 요소 없음 ✅
└── → ORANGE CORE로 전달
```

### 버전별 Front Mini LLM 모델

| 버전 | 사용 모델 | 특징 |
|------|----------|------|
| **V1** | Ollama(로컬) + GPT-4o mini | 저비용, 경량 멀티모달 |
| **V2** | GPT-4o mini + Sonnet | 범용 멀티모달 |
| **V3** | vLLM + 외부 조합 | 최고 성능 멀티모달 (사용자 승인 필요) |

> **LOCK (변경 불가)**: 멀티모달 모델 선택은 비용 모드와 연동됩니다. V1은 저비용 모드, V2는 표준 모드, V3는 고성능 모드입니다. [근거: PLAN-3.0 §1.3(A)]

### 핵심 요약 (3줄)

1. **Front Mini LLM은 모든 사용자 요청을 가장 먼저 받는 "입구 경비원" 역할의 경량 AI 모델입니다.**
2. **의도 파악, 도메인 판별, 안전 필터링의 3가지 일을 수행하여 ORANGE CORE에 전달합니다.**
3. **비용이 저렴한 미니 모델을 사용하여, 모든 요청에 대해 빠르게 1차 처리합니다.** [근거: PLAN-3.0 §1.3(A) / BEGINNER_GUIDE §2.2]

---

## 2.3 2계층: ORANGE CORE — 두뇌/지휘관

### 비유

**오케스트라의 지휘자**를 떠올려보세요. 지휘자는 직접 악기를 연주하지 않지만, 어떤 악기가 언제 어떻게 연주할지 **모든 판단을 내립니다**. ORANGE CORE가 바로 VAMOS의 지휘자입니다.

### 정의

**ORANGE CORE**(오렌지 코어)는 VAMOS 전체의 **중앙 판단/제어 시스템**입니다. 직접 "내용을 생성"하지는 않지만, **누가, 무엇을, 어떻게 처리할지를 결정**합니다. [근거: D2.0-01 §2.1.1 / PLAN-3.0 §1.3(B)]

### ORANGE CORE의 역할

| 역할 | 설명 | 비유 |
|------|------|------|
| **입력 해석 표준화** | I-1 Intent Detector로 사용자 의도를 구조화 | 접수 서류를 양식에 맞춰 정리 |
| **근거 수집** | I-2 Context Builder(RAG)로 관련 정보 수집 | 관련 자료실에서 참고 문서를 가져옴 |
| **판단 생성/잠금** | I-5 Condition & Decision Engine으로 단일결정(Decision) 생성 | 최종 판결문 작성 |
| **정책/비용/승인 게이트** | I-8/I-9/I-19로 안전·비용·승인 확인 | 보안 검사대 통과 |
| **자기 검증** | I-6 Self-check Engine으로 결과 검증 | 교정쇄 교열 |
| **로그/감사** | 모든 판단 과정을 기록 | 회의록 작성 |

> **비책임**: 도메인 실행 로직의 "내용 생성"은 BLUE NODE가 담당합니다. ORANGE CORE는 판단만 합니다. [근거: D2.0-01 §2.1.1]

### I-Series 모듈 25개 — ORANGE CORE가 관장하는 내부 기능

ORANGE CORE 안에는 **I-1부터 I-25까지 25개의 내부 모듈**이 있습니다. 이것을 **I-Series(내부 기능 시리즈)**라고 부릅니다.

#### 핵심 모듈 (I-1 ~ I-6) — 모든 버전에서 항상 활성

| 모듈 ID | 이름 | 하는 일 | 비유 | 버전별 활성 |
|---------|------|---------|------|-----------|
| **I-1** | Intent Detector (의도 감지기) | 사용자 말의 의도 파악 | "뭘 원하시는 거죠?" | V1:ON / V2:ON / V3:ON |
| **I-2** | Context Builder (컨텍스트 구성기) | 관련 지식/정보를 검색하여 수집 (RAG) | "관련 자료 찾아볼게요" | V1:ON / V2:ON / V3:ON |
| **I-3** | Memory System (메모리 시스템) | 기억 저장/관리 (4계층: L0~L3) | "이전 대화 기억나요" | V1:ON / V2:ON / V3:ON |
| **I-4** | Multimodal Interpreter (멀티모달 해석기) | 텍스트뿐 아니라 이미지/파일도 이해 | "사진도 볼 수 있어요" | V1:ON / V2:ON / V3:ON |
| **I-5** | Condition & Decision Engine (조건 판단 및 의사결정 엔진) | 최종 판단 (어떤 팀이, 어떤 도구로 처리할지) | "최종 결정합니다" | V1:ON / V2:ON / V3:ON |
| **I-6** | Self-check Engine (자기검증 엔진) | 결과가 맞는지 스스로 검증 | "다시 한번 확인할게요" | V1:ON / V2:ON / V3:ON |

> **LOCK (변경 불가)**: I-5 Condition & Decision Engine의 change_lock은 true입니다. 이 모듈의 핵심 로직은 변경할 수 없습니다. [근거: D2.0-01 §5.6]

나머지 19개 모듈(I-7~I-25)은 정책 관리(I-8), 비용 관리(I-9), 승인 관리(I-19) 등 관리/검증 역할부터, 워크플로우 설계(I-12), 자기진화(I-18), 자가진단/자동복구(I-25) 등 고급 기능까지 포함합니다.

> **I-7~I-25 각 모듈의 상세 설명은 §7(I-Series 전체 해설)에서 다룹니다.**

> [근거: D2.0-01 §5.6 (LOCK) I-Series 정본 인덱스 / BEGINNER_GUIDE §2.3]

### 버전별 I-Series 활성 현황 요약

| 구분 | V1 | V2 | V3 |
|------|----|----|-----|
| **항상 활성 (CORE)** | 17개 | 17개 | 25개 (전체) |
| **조건부 활성 (COND)** | 0개 | 5개 | 0개 |
| **비활성 (OFF)** | 8개 | 3개 | 0개 |

### 핵심 요약 (3줄)

1. **ORANGE CORE는 VAMOS의 "두뇌/지휘관"으로, 직접 내용을 생성하지 않고 누가 무엇을 어떻게 처리할지를 판단합니다.** [근거: D2.0-01 §2.1.1]
2. **I-1~I-25까지 25개의 내부 모듈을 관장하며, V1에서는 17개, V3에서는 전체 25개가 활성화됩니다.** [근거: D2.0-01 §5.6]
3. **정책/비용/승인 게이트를 통해 모든 판단의 안전성을 보장하며, I-5(단일결정 엔진)은 change_lock=true로 핵심 로직 변경이 불가능합니다.** [근거: D2.0-01 §2.1.1 / PLAN-3.0 §1.3(B)]

---

## 2.4 3계층: BLUE NODES — 실행팀

### 비유

**병원의 진료과**를 생각해보세요. 내과, 외과, 정형외과 등 각 진료과에는 해당 분야의 **전문의**가 있습니다. BLUE NODES는 이렇게 분야별로 전문화된 실행팀입니다.

### 정의

**BLUE NODES**(블루 노드)는 **도메인(분야)별 실행 엔진**입니다. ORANGE CORE가 "이 작업은 코딩팀이 처리해"라고 판단하면, 해당 BLUE NODE가 실제로 작업을 수행합니다. [근거: D2.0-01 §2.1.2 / PLAN-3.0 §1.3(C)]

### P0/P1/P2 도메인 분류

BLUE NODES는 **위험도와 중요도**에 따라 3개 등급으로 나뉩니다:

| 등급 | 이름 | 특징 | 승인 필요? | 포함 도메인 |
|------|------|------|-----------|------------|
| **P0** | 핵심 도메인 | 기본 활성, 항상 사용 가능 | 승인 불필요 | Dev/System, Research, Productivity |
| **P1** | 확장 도메인 | 1회 승인 후 세션 내 사용 가능 | **1회 승인 필요** | Content, Data & Quant |
| **P2** | 승인 기반 도메인 | 매 세션 승인 필요, 높은 위험 | **세션별 승인 필요** | Trading Strategy 등 (실거래 금지!) |

### 각 도메인의 역할

| 도메인 | 분야 | 하는 일 예시 |
|--------|------|-------------|
| **Dev/System** (P0) | 개발/시스템 | 코드 작성, 디버깅, 리팩토링, 프로젝트 구조 이해 |
| **Research** (P0) | 리서치 | 논문 검색, 문서 분석, 비교표 작성, 요약 |
| **Productivity** (P0) | 생산성 | TODO 관리, 일정 계획, 리마인더, 보고서 작성 |
| **Content** (P1) | 콘텐츠 | 블로그, 유튜브 스크립트, SNS 글, 카피라이팅 |
| **Data & Quant** (P1) | 데이터/분석 | 데이터 분석, 차트 생성, 실적 분석, 통계 |
| **Trading Strategy** (P2) | 트레이딩 전략 | 투자 전략 분석 (실거래 연동은 **절대 금지**) |

### BLUE NODE의 제약 사항

1. **ORANGE CORE의 Decision에 종속**: CORE가 판단하고, NODE가 실행합니다. NODE가 스스로 판단하지 않습니다.
2. **P2 노드는 세션별 승인 + 자동 OFF**: P2 도메인은 세션이 끝나면 자동으로 비활성화됩니다. [근거: D2.0-01 §2.1.2 (RULE 1.3 §3.3)]
3. **템플릿 기반 실행**: 각 노드는 정해진 템플릿(TemplateSet)을 따라 작업합니다.

### 핵심 요약 (3줄)

1. **BLUE NODES는 분야별 전문 실행팀으로, P0(핵심)/P1(확장)/P2(승인 기반) 3개 등급으로 나뉩니다.** [근거: D2.0-01 §2.1.2]
2. **P0(Dev, Research, Productivity)는 승인 없이 즉시 사용 가능하고, P2(Trading)는 매 세션마다 승인이 필요합니다.** [근거: PLAN-3.0 §1.3(C)]
3. **BLUE NODE는 ORANGE CORE의 판단에 종속되어 실행만 담당하며, 스스로 판단하지 않습니다.** [근거: D2.0-01 §2.1.2]

---

## 2.5 4계층: OTHER BRAINS / INFRA-CORE — 도구/자원

### 비유

**병원의 검사실, 약국, MRI실**을 떠올려보세요. 의사(BLUE NODE)가 "이 환자 혈액검사 해주세요"라고 요청하면, 검사실(OTHER BRAINS)이 실제로 검사를 수행합니다. OTHER BRAINS는 이런 **실제 도구와 자원**의 모음입니다.

### 정의

**OTHER BRAINS**(아더 브레인즈), 또는 **INFRA-CORE**(인프라 코어)는 **실행 자원 계층**입니다. 여러 AI 모델, 웹 검색, 코드 실행기, 데이터베이스 등 실제 도구들이 여기에 속합니다. [근거: D2.0-01 §2.1.3 / PLAN-3.0 §1.3(D)]

### OTHER BRAINS의 구성 요소

| 구성 요소 | 하는 일 | 포함되는 것들 |
|-----------|---------|-------------|
| **Multi-Brain Adapter (A-1)** | 여러 AI 모델을 하나로 연결하는 어댑터 | GPT-4o, Sonnet, Ollama 등 모델 라우팅 |
| **Tool Runtime** | 외부 도구 실행 환경 | 웹 검색(E-2), 파일 시스템(E-15), API 연결 |
| **Solver/Sandbox** | 수학/논리 검증, 코드 실행 격리 환경 | Z3 Solver(E-6), Code Executor(E-4) |
| **Cache/Store** | 캐시 및 저장소 연결 | 메모리(L0~L3), 벡터 DB, 로그 저장 |

### Brain Adapter (A-1) — 여러 AI 모델의 연결고리

**Brain Adapter란?** 여러 AI 모델(뇌, Brain)을 하나의 통일된 인터페이스로 연결하는 **어댑터(변환기)**입니다.

비유하면, **만능 리모컨**과 같습니다. TV, 에어컨, 조명 등 서로 다른 기기를 하나의 리모컨으로 제어하듯, Brain Adapter는 GPT-4o, Sonnet, Ollama 등 서로 다른 AI 모델을 하나의 방식으로 호출합니다.

| 버전 | 사용 가능한 Brain (AI 모델) |
|------|--------------------------|
| **V1** | Ollama(로컬) + GPT-4o mini (2~3개 brain) |
| **V2** | + Sonnet, 다중 모델 조합 |
| **V3** | vLLM + 외부 조합, GPU Brain 포함 |

### E-Series (외부 기능) — OTHER BRAINS가 실행하는 도구들

OTHER BRAINS 계층에서 실제로 실행되는 도구를 **E-Series(외부 기능 시리즈)**라고 합니다. 총 **16개 모듈**(E-1~E-16)이 있으며, 대표적인 예시는 다음과 같습니다:

| 대표 모듈 | 하는 일 | V1 활성 여부 |
|-----------|---------|-------------|
| **E-1** Coding Helper | 코드 작성/디버깅/설계 도우미 | ON |
| **E-2** Web Search | 인터넷 검색 | ON |
| **E-3** Document Parser | 문서(PDF/Word 등) 읽기 | ON |
| **E-4** Code Executor | 코드 실제 실행 (샌드박스) | ON |
| **E-7** Speech-to-Text | 음성 → 텍스트 변환 | OFF (V3에서 ON) |
| **E-12** DB Connector | 데이터베이스 연결 | OFF (V3에서 ON) |

버전별로 V1에서 6개, V2에서 10개, V3에서 전체 16개가 활성화됩니다.

> **E-1~E-16 각 모듈의 상세 설명은 §8(E-Series 전체 해설)에서 다룹니다.**
> [근거: D2.0-01 §5.8]

### 핵심 원칙: CORE는 제어, Brain은 실행

```
ORANGE CORE ──(판단/지시)──→ OTHER BRAINS ──(실행/결과)──→ ORANGE CORE
   [지휘관]                    [도구/자원]                  [결과 확인]
```

> **분리 원칙**: CORE가 제어하고, Brain이 실행합니다. 이 둘은 절대 섞이지 않습니다. [근거: D2.0-01 §2.1.3]

### 핵심 요약 (3줄)

1. **OTHER BRAINS(INFRA-CORE)는 웹 검색, 코드 실행, DB 조회 등 실제 도구들의 모음인 "실행 자원 계층"입니다.** [근거: D2.0-01 §2.1.3]
2. **Brain Adapter(A-1)가 여러 AI 모델을 하나의 인터페이스로 연결하며, V1에서 2~3개, V3에서 GPU Brain까지 확장됩니다.** [근거: PLAN-3.0 §1.3(D)]
3. **E-Series(E-1~E-16) 16개의 외부 도구가 있으며, V1에서 6개 활성, V3에서 전체 활성됩니다.** [근거: D2.0-01 §5.8]

---

## 2.6 Main/Hologram LLM — 최종 출력 생성

### 비유

**병원의 진료 결과지 작성**을 생각해보세요. 접수(Front Mini), 원장 판단(CORE), 진료과 진료(BLUE NODE), 검사(OTHER BRAINS)가 모두 끝난 후, 환자에게 전달할 **최종 결과 문서**를 만드는 단계입니다.

### 정의

**Main/Hologram LLM**(메인/홀로그램 LLM)은 VAMOS의 **최종 출력을 생성**하는 고성능 AI 모델입니다. Front Mini LLM이 "입구"라면, Main LLM은 "출구"입니다. 수집된 모든 정보와 분석 결과를 종합하여, 사용자에게 전달할 최종 응답을 만듭니다. [근거: PLAN-3.0 §1.3(A) / BEGINNER_GUIDE §2.1]

### 3-Part Output (3단 출력) — VAMOS의 표준 출력 형식

Main LLM이 생성하는 모든 출력은 반드시 **3개 파트**로 구성됩니다:

```
┌─────────────────────────────────────────────┐
│ Part 1: 사용자 응답 (Answer)                  │
│   → 최종 결과물 (보고서/코드/분석/요약 등)       │
│   → Markdown, 표, 차트 등으로 보기 좋게 정리     │
├─────────────────────────────────────────────┤
│ Part 2: 근거/요약 (Evidence Summary)           │
│   → 참고한 소스, 출처 링크                      │
│   → QoD(품질 점수), 인용 정보                   │
│   → VERIFIED / PARTIAL / UNVERIFIED 배지        │
├─────────────────────────────────────────────┤
│ Part 3: 로그/리포트 (Trace Report)             │
│   → 판단 과정 기록 (trace_id 포함)              │
│   → 비용 사용량, 승인 이벤트, 검증 결과          │
└─────────────────────────────────────────────┘
```

> **왜 3-Part인가?** 정확성·근거 기반 출력이 VAMOS의 핵심 철학이기 때문입니다. 답변만 주는 것이 아니라, **"왜 이 답변이 맞는지"(근거)**와 **"어떻게 이 답변에 도달했는지"(로그)**를 함께 제공합니다. [근거: D2.0-01 §2.3.2]

### 검증 배지 (Verification Badge)

Main LLM의 출력에는 **근거 품질에 따른 배지**가 붙습니다:

| 배지 | 조건 | 의미 |
|------|------|------|
| ✅ **VERIFIED** | QoD ≥ 0.8 | 교차 검증/근거 충분 (신뢰 높음) |
| ⚠️ **PARTIAL** | 0.5 ≤ QoD < 0.8 | 일부 검증/근거 제한 (주의) |
| 🚫 **UNVERIFIED** | QoD < 0.5 | 근거 부족/환각 가능 (경고) |

> **LOCK (변경 불가)**: 이 배지 체계는 변경 불가능합니다. QoD(Quality of Data)는 근거/데이터의 품질을 0~1 사이의 점수로 나타낸 것입니다. [근거: D2.0-01 §5.15]

### Front Mini LLM vs Main LLM 비교

| 비교 항목 | Front Mini LLM (앞단) | Main/Hologram LLM (뒷단) |
|-----------|----------------------|------------------------|
| **역할** | 입력 수신, 의도 파악, 안전 필터링 | 최종 출력 생성 |
| **모델 크기** | 작고 가벼움 (저비용) | 크고 강력함 (고비용) |
| **처리 시점** | 요청 **시작** 시 | 요청 **마지막** 에 |
| **비유** | 입구 경비원 | 최종 보고서 작성자 |
| **V1 모델** | GPT-4o mini | GPT-4o mini (동일, 비용 절약) |
| **V3 모델** | 경량 멀티모달 | 플래그십 모델 적극 활용 |

### 핵심 요약 (3줄)

1. **Main/Hologram LLM은 모든 처리 결과를 종합하여 최종 출력을 생성하는 "보고서 작성자"입니다.** [근거: PLAN-3.0 §1.3(A)]
2. **모든 출력은 3-Part(응답 + 근거/요약 + 로그/리포트) 형식을 따르며, 근거 없이는 답변을 출력하지 않습니다.** [근거: D2.0-01 §2.3.2]
3. **출력에는 검증 배지(VERIFIED/PARTIAL/UNVERIFIED)가 붙어, 사용자가 답변의 신뢰도를 한눈에 알 수 있습니다.** [근거: D2.0-01 §5.15]

---

## 2.7 계층 간 데이터 흐름 전체도

### 전체 흐름 (ASCII 흐름도)

사용자가 "최근 논문 요약해줘"라고 입력했을 때, VAMOS 내부에서 일어나는 **전체 데이터 흐름**입니다:

```
사용자: "최근 LLM 효율화 논문 요약해줘"
  │
  ▼
[1계층] Front Mini LLM
  │  ├── 의도 파악: "리서치/논문 분석"
  │  ├── 도메인 판별: P0_Research (승인 불필요)
  │  └── 안전 확인: OK ✅
  │
  ▼  IntentFrame 생성 → ORANGE CORE로 전달
[2계층] ORANGE CORE
  │  ├── I-1: IntentFrame 확인 및 구조화
  │  ├── I-2: RAG로 관련 논문 데이터 검색
  │  ├── I-8: Policy Engine — 정책 확인 OK
  │  ├── I-9: Cost Manager — 비용 확인 OK (₩15 예상)
  │  ├── I-5: Condition & Decision Engine — "P0_Research 노드 활성화" 결정
  │  └── I-17: Blue Node Manager — Research 노드 호출
  │
  ▼  Decision(판단 결과) → BLUE NODE로 전달
[3계층] BLUE NODE (Research)
  │  ├── 검색 쿼리 설계: "LLM efficiency 2024-2025"
  │  ├── 논문 필터링 기준 설정
  │  └── OTHER BRAINS에 실행 요청
  │
  ▼  실행 요청 → OTHER BRAINS로 전달
[4계층] OTHER BRAINS
  │  ├── E-2 (Web Search): 논문 검색 실행
  │  ├── E-3 (Document Parser): PDF 논문 파싱
  │  ├── A-1 (Brain Adapter): AI 모델로 분석
  │  └── 결과 반환 → BLUE NODE → ORANGE CORE
  │
  ▼  결과 종합 → ORANGE CORE에서 검증
[2계층] ORANGE CORE (검증)
  │  ├── I-6: Self-check — 결과 검증 (QoD: 0.85 → VERIFIED ✅)
  │  ├── I-15: Evidence 품질 확인
  │  ├── I-14: 요약 생성 → 메모리 저장
  │  └── I-11: Output Composer → 3-Part Output 조립
  │
  ▼  3-Part Output → Main LLM으로 전달
Main/Hologram LLM
  │  ├── Part 1: 논문 5편 요약표 + 핵심 비교
  │  ├── Part 2: 각 논문 출처 (arXiv 링크 등), QoD: 0.85
  │  └── Part 3: 비용 ₩15, trace_id, 검증 결과
  │
  ▼
사용자에게 전달 ✅
```

### Agent 관점 5단계 (데이터 흐름 요약)

위의 흐름을 **Agent 관점 5단계**로 요약하면 다음과 같습니다:

| 단계 | 명칭 | 담당 | 핵심 산출물 | 상태 코드 |
|------|------|------|-----------|----------|
| 1 | **Perception** (인식) | Front Mini + I-1 | IntentFrame | S0 → S1 |
| 2 | **Reasoning** (추론) | I-2 + I-5 + Gates | EvidencePack + Decision | S2 → S3 |
| 3 | **Action** (실행) | BLUE NODE + OTHER BRAINS | Artifacts / Results | S4 → S5 |
| 4 | **Reflection** (성찰) | I-6 + Verify | Self-check 결과 | S6 |
| 5 | **Memory** (기억) | I-3 + Storage | L0/L1/L2 저장 | S7 → S8 |

> **참고**: 이 "Agent 관점 5단계"는 데이터 흐름을 개념적으로 요약한 것입니다. §3.2에서 다루는 **Standard 5-Phase 파이프라인**(Intake → Plan → Execute → Verify → Deliver)은 처리 절차를 정의하는 별개의 프레임워크이므로 혼동하지 마세요.
> [근거: D2.0-01 §2.3.1 / D2.0-01 §2.3.3 파이프라인 명칭 매핑표]

### 핵심 요약 (3줄)

1. **데이터는 Front Mini LLM → ORANGE CORE → BLUE NODE → OTHER BRAINS → ORANGE CORE(검증) → Main LLM 순서로 흐릅니다.** [근거: D2.0-01 §2.3]
2. **이 흐름은 Agent 관점 5단계(Perception → Reasoning → Action → Reflection → Memory)로 요약되며, §3.2의 Standard 5-Phase와는 별개입니다.** [근거: D2.0-01 §2.3.1]
3. **상태 코드(S0~S8)로 현재 진행 상황을 추적할 수 있어, 마치 택배 추적처럼 요청의 처리 상태를 알 수 있습니다.** [근거: D2.0-01 §2.3.3]

---

## 2.8 개발 환경 셋업 — V1/V2/V3 각각의 절차 ★GAP-2

### 비유

집을 짓는 것에 비유하면:
- **V1**은 "원룸 자취방" — 혼자 쓰기에 충분하고, 설치가 간단
- **V2**은 "팀 사무실" — 여러 사람이 쓸 수 있고, 서버가 필요
- **V3**은 "기업 데이터센터" — 대규모 운영, 자동 확장

### 기술 스택 전체 비교

| 항목 | V1 (로컬/개인) | V2 (단일 서버) | V3 (운영형) |
|------|---------------|---------------|-------------|
| **AI 모델** | Ollama + GPT-4o mini | + Sonnet | vLLM + 외부 조합 |
| **LLM 프레임워크** | **LangGraph** (LOCK) | 동일 | 동일 |
| **저장소** | SQLite + JSONL | Postgres 단일 | Managed Postgres |
| **Vector DB** | Chroma (로컬) | Qdrant (서버) | Qdrant Cloud |
| **로깅** | JSONL + SQLite | Postgres + JSONL 압축 | Loki/ELK + Object |
| **배포** | Windows/WSL 단일 | VPS + Docker Compose (Hetzner 권장) | Hetzner Lite(권장) / K8s(선택) |
| **UI** | Tauri 2.0 + React | + PWA | + 모바일 |
| **안전** | NeMo + Guardrails AI | + LlamaGuard (4-Layer) | + 사후 감사 (4층) |
| **MCP 전송** | Streamable HTTP (LOCK) | 동일 | 동일 |
| **Embedding** | BGE-M3 (무료) | + text-embedding-3-small | + large 모델 |

> **LOCK (변경 불가)**: LangGraph 프레임워크와 Streamable HTTP(MCP 전송)는 모든 버전에서 동일하며 변경 불가능합니다. [근거: D2.0-01 §3.3 / BEGINNER_GUIDE §11.1]

### V1 환경 셋업 — 로컬/개인 ("원룸 자취방")

**대상**: 개인 사용자, 가벼운 작업, Windows/WSL 환경

```
필요한 것:
├── OS: Windows 10/11 또는 WSL2
├── Python 3.11+
├── Node.js 18+
├── Rust (Tauri 빌드용)
├── Ollama (로컬 LLM 실행)
├── OpenAI API 키 (GPT-4o mini용)
└── 저장공간: 약 10GB 이상 권장

셋업 순서:
1. Python / Node.js / Rust 설치
2. Ollama 설치 → 로컬 LLM 모델 다운로드
3. 프로젝트 클론: git clone vamos.git
4. 의존성 설치: pip install -r requirements.txt / npm install
5. 환경변수 설정: .env 파일에 API 키 등록
6. SQLite 초기화 (자동)
7. Chroma 벡터 DB 초기화 (자동)
8. 실행: vamos start (또는 npm run tauri dev)
```

**비용 모드**: 저비용 (Mini 모델 90%+ 사용)
**비용 상한**: 일 1,300원 ($1) / 월 40,000원 ($30)

### V2 환경 셋업 — Docker Compose ("팀 사무실")

**대상**: 팀 사용, 전문가 사용, Docker 지원 서버 환경

```
필요한 것:
├── OS: Linux 서버 또는 Docker 지원 환경
├── Docker + Docker Compose
├── Postgres DB
├── Qdrant (벡터 검색 서버)
├── OpenAI API 키 + Anthropic API 키
└── 서버 사양: RAM 16GB+, SSD 50GB+ 권장

셋업 순서:
1. Docker + Docker Compose 설치
2. docker-compose.yml 작성 (서비스 정의)
   ├── vamos-backend (Python)
   ├── vamos-frontend (React)
   ├── postgres (DB)
   ├── qdrant (Vector DB)
   └── ollama (로컬 LLM, 선택)
3. 환경변수 설정: .env 파일에 API 키, DB 접속 정보 등록
4. 실행: docker-compose up -d
5. Postgres 마이그레이션 실행
6. Qdrant 컬렉션 초기화
7. 접속: http://localhost:3000
```

**비용 모드**: 표준 (Mini 60~70% / Main 30~40%)
**비용 상한**: 일 3,100원 ($2.3) / 월 93,000원 ($70)

### V3 환경 셋업 — Kubernetes ("기업 데이터센터")

**대상**: 기업/파워 유저, 대규모 운영, 자동 확장 필요

```
필요한 것:
├── Kubernetes 클러스터 (K8s)
├── Managed Postgres (AWS RDS / GCP Cloud SQL 등)
├── Qdrant Cloud (벡터 검색)
├── GPU 서버 (vLLM 실행용)
├── Loki + Grafana (관측 스택)
├── 다중 API 키 (OpenAI, Anthropic, 기타)
└── 서버 사양: GPU 포함, RAM 32GB+, SSD 200GB+

셋업 순서:
1. K8s 클러스터 구성 (EKS/GKE/AKS 등)
2. Helm Chart 배포
   ├── vamos-core (백엔드 파드)
   ├── vamos-ui (프론트엔드 파드)
   ├── postgres (매니지드 DB)
   ├── qdrant (벡터 DB 클러스터)
   ├── vllm (GPU Brain 파드)
   ├── loki (로그 집계)
   └── grafana (모니터링 대시보드)
3. 시크릿 관리: K8s Secrets 또는 Vault
4. 네트워크 정책 설정 (파드 간 통신 규칙)
5. HPA(Horizontal Pod Autoscaler) 설정 — 자동 확장
6. Grafana 대시보드 구성 (비용/성능/안전 모니터링)
7. 관측 스택 연동: ORANGE CORE 판단 로그, BLUE NODE 실행 로그
```

**비용 모드**: 고성능 (Main 모델 중심, 플래그십 적극 활용)
**비용 상한**: 일 8,900원 ($6.7) / 월 266,000원 ($200)

> **V3 관측성(Observability) 스택**: Loki + Grafana로 확정되었습니다. 선택 근거는 ELK 대비 경량 구조, 비용 효율적, K8s 환경 친화적이기 때문입니다. [근거: PLAN-3.0 §1.3(D)]

> **v26 업데이트**: V2부터 VPS가 필요합니다. Hetzner CX31($8/월)을 권장하며, V3에서는 동일 서버에 RunPod Serverless GPU를 추가하는 경로 B(~$123-142/월)가 비용 효율적입니다. 상세는 §39 배포 전략 참조. [근거: v26 메이커에반 개선안 7]

### 프로젝트 구조 (Monorepo)

**Monorepo**(모노레포)란? 하나의 코드 저장소에 프론트엔드, 백엔드, 설정 등 모든 것을 함께 관리하는 방식입니다.

```
vamos/
├── src/                  ← React 프론트엔드 (사용자 화면)
│   ├── components/       ← 화면 구성 요소
│   ├── pages/            ← 페이지 (Dashboard, Chat, Settings 등)
│   └── stores/           ← 상태 관리 (Zustand)
│
├── src-tauri/            ← Rust 백엔드 (Tauri, 데스크톱 앱 로직)
│   └── src/
│       ├── commands/     ← IPC 커맨드 (프론트↔백 통신)
│       └── bridge/       ← Python 연결 브릿지
│
├── backend/              ← Python AI/ML 핵심 로직
│   └── vamos_core/
│       ├── orange_core/  ← 판단 엔진 (I-1~I-5)
│       ├── blue_nodes/   ← 도메인별 노드
│       ├── infra/        ← 인프라 (모델 라우팅, 도구 등)
│       ├── storage/      ← 메모리/벡터/캐시
│       ├── safety/       ← 안전/비용/승인
│       └── schemas/      ← 데이터 스키마 (Pydantic v2)
│
├── shared/types/         ← JSON Schema (공유 타입 정의)
├── config/               ← 설정 파일
└── tests/                ← 테스트 (unit, integration, e2e)
```

> **3개 언어의 역할**:
> - **React/TypeScript**: 사용자가 보는 화면 (UI)
> - **Rust**: 데스크톱 앱 + 프론트↔백 통신 (IPC) + 성능 중심 로직
> - **Python**: AI/ML 핵심 로직 (모델 호출, RAG, 메모리 등)
> [근거: BEGINNER_GUIDE §11.2]

### 핵심 요약 (3줄)

1. **V1(로컬)은 Windows/WSL에서 SQLite+Chroma로 간단히 시작하고, V2(서버)는 Docker Compose+Postgres+Qdrant로 확장합니다.** [근거: D2.0-01 §3.3]
2. **V3(운영)은 K8s+Managed Postgres+Qdrant Cloud+GPU Brain으로 대규모 운영하며, Loki+Grafana 관측 스택을 사용합니다.** [근거: PLAN-3.0 §1.3(D)]
3. **모든 버전에서 LangGraph 프레임워크와 Streamable HTTP(MCP 전송)는 LOCK(변경 불가)이며, Monorepo 구조(React+Rust+Python)로 구성됩니다.** [근거: D2.0-01 §3.3 / BEGINNER_GUIDE §11.1]

---

## 전체 핵심 요약 (3줄)

1. **VAMOS는 Front Mini LLM(입구) → ORANGE CORE(판단) → BLUE NODES(실행) → OTHER BRAINS(도구) → Main LLM(출력)의 4계층+α 구조로, "LLM + 중앙 제어 + 실행 계층 + LLM"의 양방향 흐름을 따릅니다.** [근거: D2.0-01 §2.1 / PLAN-3.0 §1.3(A)]
2. **ORANGE CORE가 I-Series 25개 모듈로 모든 판단을 내리고, BLUE NODES(P0/P1/P2)가 도메인별 실행을, OTHER BRAINS가 실제 도구 실행을 담당하며, 이 분리 원칙은 VAMOS 아키텍처의 핵심입니다.** [근거: D2.0-01 §2.1.1~§2.1.3]
3. **개발 환경은 V1(로컬/SQLite/Chroma) → V2(Docker/Postgres/Qdrant) → V3(K8s/GPU/Loki+Grafana)로 확장되며, LangGraph 프레임워크는 모든 버전에서 LOCK입니다.** [근거: D2.0-01 §3.3 / BEGINNER_GUIDE §11.1]
