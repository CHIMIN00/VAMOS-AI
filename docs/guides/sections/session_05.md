---
session: 05
sections: [6.1, 6.2, 6.3, 6.4, 6.5]
status: complete
---

# §6. 모듈 시스템 개요

> **비유**: VAMOS를 거대한 레고 성(城)이라고 상상해 보세요. 이 성은 **81개의 레고 블록 (I25+E16+S8+A7+B6+C7+D6+EVX6)**으로 이루어져 있습니다. 어떤 블록은 성의 기둥처럼 **반드시 있어야 하는 것**이고, 어떤 블록은 장식탑처럼 **필요할 때만 끼워 넣는 것**이며, 어떤 블록은 아직 실험 중인 **시제품**입니다. 이 장에서는 VAMOS를 구성하는 81개 블록(모듈)의 전체 체계를 한눈에 살펴봅니다.

---

## §6.1 모듈이란? — 레고 블록 비유와 Runnable 인터페이스

### 비유

레고 블록 하나하나가 각자의 **모양과 역할**을 가지듯, VAMOS의 **모듈(Module)**은 하나의 독립된 기능 단위입니다. 예를 들어:

- **I-1 (의도 감지기)** = "사용자가 무슨 말을 했는지 파악하는" 블록
- **E-2 (웹 검색)** = "인터넷에서 정보를 찾아오는" 블록
- **C-1 (논리 검증기)** = "답변이 논리적으로 맞는지 확인하는" 블록

### 정의

**모듈(Module)**이란, VAMOS 시스템 안에서 **하나의 명확한 책임**을 가진 독립 실행 단위입니다. 모든 모듈은 **Runnable 인터페이스**(실행 가능한 표준 규격)를 따릅니다. [근거: D2.0-01 §5.5]

### Runnable 인터페이스란?

**Runnable 인터페이스**(실행 규격)란, 모든 모듈이 반드시 갖춰야 하는 **표준 약속**입니다. 쉽게 말해, 모든 레고 블록의 **연결 돌기 모양이 동일**하여 어디든 끼울 수 있는 것과 같습니다.

| 표준 항목 | 설명 | 비유 |
|----------|------|------|
| **입력 (Input)** | 모듈이 받아들이는 데이터 | 레고 블록의 아래쪽 구멍 |
| **출력 (Output)** | 모듈이 내보내는 결과 | 레고 블록의 위쪽 돌기 |
| **상태 (State)** | 현재 동작 중인지, 대기 중인지 | 블록에 붙은 LED 표시등 |
| **이벤트 (Event)** | "작업 완료!" 같은 알림 | 블록이 보내는 신호음 |
| **에러코드 (Failure Code)** | 문제 발생 시 원인 코드 | 블록의 오류 표시등 색상 |
| **폴백 (Fallback)** | 실패 시 대안 행동 | 예비 블록으로 자동 교체 |

[근거: D2.0-01 §5.5.1, D2.0-02 §6.*]

### 핵심 요약 (3줄)
1. **모듈**은 VAMOS를 구성하는 독립 기능 단위로, 레고 블록과 같습니다.
2. 모든 모듈은 **Runnable 인터페이스**(표준 규격)를 따라 입력·출력·상태·이벤트·에러·폴백을 갖습니다.
3. 이 표준 덕분에 모듈을 **자유롭게 조합**하고, 버전에 따라 켜고 끌 수 있습니다.

---

## §6.2 분류 체계: CORE / COND / EXP — 세 가지 등급

모든 81개 모듈은 **세 가지 등급(status)** 중 하나로 분류됩니다. (일부는 RE-ADD(재도입 대기)도 있습니다.) [근거: D2.0-01 §5.5.1 LOCK]

### 비유

| 등급 | 비유 | 의미 |
|------|------|------|
| **CORE** (코어, 필수) | 성의 **기둥과 벽** — 없으면 성이 무너짐 | 항상 켜져 있는 핵심 모듈. 시스템 작동에 반드시 필요 |
| **COND** (조건부) | 성의 **다리와 문** — 필요할 때 연결 | 기본 꺼짐(OFF). 승인·정책·비용 조건을 만족하면 켜짐 |
| **EXP** (실험적) | 성의 **전망탑** — 아직 시제품 단계 | 실험/고비용 기능. 기본적으로 V3에서만 활성화 |
| **RE-ADD** (재도입) | 한번 치워뒀다가 **다시 꺼내온 블록** | Design 2.0에서 재도입 대기 중인 모듈 |

### 상세 설명

- **CORE**: 기본 활성(ON). 별도 경고나 제한 없이 항상 동작합니다. 예: I-1(의도 감지기), I-5(결정 엔진), I-8(정책 엔진)
- **COND**: 기본 비활성(OFF 또는 COND). **승인(Approval) + 정책(Policy) + 비용(Cost) 게이트**를 모두 통과해야 "세션 단위 ON"이 가능합니다. 예: I-7(프로젝트 매니저), A-4(토론 모드) [근거: D2.0-01 §5.14.4 LOCK]
- **EXP**: 실험 기능. UI에서 🧪 LAB 배지가 표시되며 "불안정/고비용 가능" 경고가 나타납니다. 예: I-18(자기진화 엔진), D-3(장기 계획기) [근거: D2.0-01 §5.8.2 LOCK]
- **RE-ADD**: Design 2.0에서 재도입된 기능. UI에서 ✨ NEW 배지로 강조됩니다. 예: EVX-1(Code-as-Policy), E-13(캘린더 동기화)

> **중요**: `change_lock=true`(변경 잠금)인 모듈은 정책·스키마·정본 필드 변경 시 반드시 **07 Approval Gate 승인**이 필요합니다. **변경 불가** 표시에 해당합니다. [근거: D2.0-01 §5.5.1 LOCK]

### 핵심 요약 (3줄)
1. 모듈은 **CORE**(필수)·**COND**(조건부)·**EXP**(실험)·**RE-ADD**(재도입) 네 등급으로 분류됩니다.
2. CORE는 항상 켜져 있고, COND는 조건 충족 시에만, EXP는 V3에서만 기본 활성화됩니다.
3. 이 분류 체계는 **LOCK(변경 불가)**이며, 모든 버전에서 동일하게 적용됩니다.

---

## §6.3 버전별 활성 모듈 수

VAMOS는 버전이 올라갈수록 더 많은 모듈이 활성화됩니다. 마치 레고 성을 **점점 더 크게 확장**하는 것과 같습니다. [근거: D2.0-01 §5.6~§5.13, CLAUDE.md §6]

### 전체 요약 표

| 버전 | 활성 모듈 수 | 단계 설명 | 비유 |
|------|------------|----------|------|
| **V0** | **5개** | 최소 구현 ("돌아가는 코어") | 레고 성의 기둥 5개만 세운 상태 |
| **V1** | **32개** | 초기 제품화 (₩40K/월 MVP) | 기본 구조 완성 + 필수 기능 장착 |
| **V2** | **42개** | 프로 확장 (₩93K/월) | 조건부 기능 10개 추가 활성 |
| **V3** | **81개** | 전체 가동 (₩266K/월 Enterprise) | 모든 블록이 완성된 풀 스케일 성 |

### 시리즈별 상세 수량 표

| 시리즈 | 전체 | V0 | V1 | V2 (ON+COND) | V3 |
|--------|------|----|----|-------------|-----|
| **I-Series** (내부 기능) | 25 | 5 | 17 | 22 (17 ON + 5 COND) | 25 |
| **E-Series** (외부 기능) | 16 | 0 | 6 | 10 (6 ON + 4 COND) | 16 |
| **S-Series** (자기진화) | 8 | 0 | 1 | 1 | 8 |
| **A-Series** (아키텍처 확장) | 7 | 0 | 2 | 3 (2 ON + 1 COND) | 7 |
| **B-Series** (메모리/스킬) | 6 | 0 | 1 | 1 | 6 |
| **C-Series** (검증/추론) | 7 | 0 | 3 | 3 | 7 |
| **D-Series** (Brain/RAG) | 6 | 0 | 2 | 2 | 6 |
| **EVX-Series** (검증 확장) | 6 | 0 | 0 | 0 | 6 |
| **합계** | **81 (I25+E16+S8+A7+B6+C7+D6+EVX6)** | **5** | **32** | **42** | **81** |

> **V0의 5개 모듈**: I-1(의도 감지기), I-2(컨텍스트 구성기), I-3(메모리 시스템), I-4(멀티모달 해석기), I-5(결정 엔진) — ORANGE CORE의 핵심 흐름 모듈만으로 최소 동작을 확인합니다. [근거: D2.0-01 §3.2]

### 핵심 요약 (3줄)
1. V0(5개) → V1(32개) → V2(42개) → V3(81개)로 **점진적 확장**됩니다.
2. V1에서는 I-Series 17개 + E-Series 6개가 핵심이고, V3에서 비로소 **전체 81개**가 가동됩니다.
3. 각 버전의 활성 모듈 수는 **비용 상한(LOCK)**과 연동되어 설계되었습니다.

---

## §6.4 네이밍 규칙 — 모듈 ID 읽는 법

모듈 ID는 **접두어(알파벳) + 번호**로 구성됩니다. 접두어만 보면 해당 모듈이 어떤 역할군에 속하는지 바로 알 수 있습니다. [근거: D2.0-01 §5.14.2 LOCK]

### 8개 시리즈 네이밍 규칙

| 접두어 | 형식 | 의미 | 예시 | 개수 |
|--------|------|------|------|------|
| **I-#** | I-1 ~ I-25 | **Internal** (내부 기능) — ORANGE CORE의 판단·제어 모듈 | I-1 의도 감지기, I-5 결정 엔진 | 25개 |
| **E-#** | E-1 ~ E-16 | **External** (외부 기능) — 사용자 환경과 상호작용하는 도구 | E-2 웹 검색, E-4 코드 실행기 | 16개 |
| **S-#** | S-1 ~ S-8 | **Self-evo** (자기진화) — 스스로 개선하는 진화 모듈 | S-1 자기검증, S-6 검색 진화 | 8개 |
| **A-#** | A-1 ~ A-7 | **Advanced** (아키텍처 확장) — 고급 인프라 확장 | A-1 멀티브레인, A-4 토론 모드 | 7개 |
| **B-#** | B-1 ~ B-6 | **Memory/Skill** (메모리·스킬 자산) — 기억과 학습 자산 | B-1 스킬 라이브러리, B-3 망각/감쇠 | 6개 |
| **C-#** | C-1 ~ C-7 | **Reasoning** (검증·추론 확장) — 논리·수학·코드 검증 | C-1 논리 검증기, C-2 수학 검증기 | 7개 |
| **D-#** | D-1 ~ D-6 | **Generation** (Brain/Planner/RAG) — 생성·계획·검색 확장 | D-1 Think 엔진, D-6 GraphRAG | 6개 |
| **EVX-#** | EVX-1 ~ EVX-6 | **Verify Extension** (검증 확장) — 고급 검증 체인 | EVX-1 Code-as-Policy, EVX-2 적대적 검증 | 6개 |

### 주의: S-# vs S#_ 구분 (LOCK, 변경 불가)

VAMOS에서 **S**로 시작하는 표기가 두 가지 있어 혼동하기 쉽습니다:

| 표기 | 의미 | 예시 |
|------|------|------|
| **S-#** (하이픈) | **모듈 ID** (Self-evo 시리즈) | S-1(자기검증), S-5(라우터 진화) |
| **S#_** (언더스코어) | **상태명** (State Machine) | S0_RECEIVED(수신됨), S3_DECISION_LOCKED(결정 잠금) |

> 이 구분은 **LOCK(변경 불가)**이며, 모든 문서와 코드에서 반드시 준수해야 합니다. [근거: D2.0-01 §0.5, §5.14.2 LOCK]

### 핵심 요약 (3줄)
1. 모듈 ID는 **접두어(I/E/S/A/B/C/D/EVX) + 번호**로 구성됩니다.
2. 접두어만 보면 Internal(내부), External(외부), Self-evo(진화) 등 **역할군을 즉시 파악**할 수 있습니다.
3. **S-#**(모듈)과 **S#_**(상태)의 구분은 LOCK이며, 하이픈과 언더스코어로 충돌을 방지합니다.

---

## §6.5 모듈 간 의존성 규칙 — CORE→COND 단방향 원칙

### 비유

건물의 **기둥(CORE)**은 스스로 서 있어야 합니다. 기둥이 장식탑(COND/EXP)에 기대서 서면 안 되겠죠? 반대로, 장식탑은 기둥에 연결되어 지탱받을 수 있습니다. VAMOS의 모듈 의존성도 같은 원칙을 따릅니다.

### 의존성 규칙 (R7)

```
┌──────────┐          ┌──────────┐          ┌──────────┐
│   CORE   │ ───────► │   COND   │ ───────► │   EXP    │
│  (필수)   │  허용     │ (조건부)  │  허용     │ (실험)   │
└──────────┘          └──────────┘          └──────────┘
     ▲                      │                      │
     │         ✖ 금지        │        ✖ 금지         │
     └──────────────────────┘──────────────────────┘
```

| 규칙 | 설명 | 이유 |
|------|------|------|
| **CORE → COND 허용** | 필수 모듈이 조건부 모듈을 호출할 수 있음 | CORE는 항상 켜져 있으므로 안전하게 호출 가능 |
| **CORE → EXP 허용** | 필수 모듈이 실험 모듈을 호출할 수 있음 | 단, 해당 버전에서 EXP가 활성화된 경우에만 |
| **COND → CORE 금지** ✖ | 조건부 모듈이 필수 모듈에 **역방향 의존 금지** | COND가 꺼져 있을 때 CORE 동작이 깨질 위험 |
| **EXP → CORE 금지** ✖ | 실험 모듈이 필수 모듈에 역방향 의존 금지 | 동일한 이유 — 시스템 안정성 보호 |

> **핵심 원칙**: 의존성은 반드시 **CORE → COND → EXP 방향(단방향)**으로만 흘러야 합니다. 역방향 의존은 시스템 안정성을 위협하므로 **절대 금지**합니다. [근거: D2.0-01 §5.5.1, §5.14.4 LOCK]

### 실제 예시

```
I-5 (결정 엔진, CORE) ──호출──► I-7 (프로젝트 매니저, COND)  ✅ 허용
I-6 (자기검증, CORE)   ──연동──► S-1 (자기검증 엔진, CORE)   ✅ 허용 (CORE↔CORE)
I-7 (프로젝트 매니저, COND) ──의존──► I-5 (결정 엔진, CORE)  ✖ 역방향 금지
S-4 (에러패턴, EXP)  ──의존──► I-20 (폴백 관리자, CORE)     ✖ 역방향 금지
```

> **참고**: CORE↔CORE 간의 의존은 허용됩니다. 같은 등급 내에서는 양방향 연동이 가능합니다.

### 핵심 요약 (3줄)
1. 모듈 의존성은 **CORE → COND → EXP 단방향**으로만 허용됩니다.
2. **역방향 의존(COND→CORE, EXP→CORE)은 절대 금지** — 시스템 안정성 보호를 위한 핵심 규칙입니다.
3. 같은 등급 내(CORE↔CORE 등)의 양방향 연동은 허용됩니다.

---

## 81개 모듈 전체 목록

> 아래 표는 VAMOS의 **전체 81개 모듈**을 한눈에 보여줍니다. [근거: D2.0-01 §5.6~§5.13 LOCK]

### I-Series — 내부 기능 (I-1 ~ I-25, 총 25개)

| ID | 이름 | 분류 | LOCK | V1 | V2 | V3 |
|----|------|------|------|----|----|-----|
| I-1 | 의도 감지기 (Intent Detector) | CORE | - | ON | ON | ON |
| I-2 | 컨텍스트 구성기 (Context Builder) | CORE | - | ON | ON | ON |
| I-3 | 메모리 시스템 (Memory System) | CORE | - | ON | ON | ON |
| I-4 | 멀티모달 해석기 (Multimodal Interpreter) | CORE | - | ON | ON | ON |
| I-5 | 결정 엔진 (Condition & Decision Engine) | CORE | **변경 불가** | ON | ON | ON |
| I-6 | 자기검증 엔진 (Self-check Engine) | CORE | - | ON | ON | ON |
| I-7 | 프로젝트/세션 매니저 (Project/Session Manager) | COND | - | OFF | COND | ON |
| I-8 | 정책 엔진 (Policy Engine) | CORE | **변경 불가** | ON | ON | ON |
| I-9 | 비용 관리자 (Cost Manager) | CORE | **변경 불가** | ON | ON | ON |
| I-10 | 툴 레지스트리/라우터 (Tool Registry/Router) | CORE | - | ON | ON | ON |
| I-11 | 출력 생성기 (Output Composer) | CORE | - | ON | ON | ON |
| I-12 | 워크플로우 빌더 (Workflow Builder) | COND | - | OFF | COND | ON |
| I-13 | 멀티모달 출력 렌더러 (Multimodal Output Renderer) | CORE | - | ON | ON | ON |
| I-14 | 요약·증류기 (Summarizer & Memory Distiller) | CORE | - | ON | ON | ON |
| I-15 | 근거·QoD 관리자 (Evidence & QoD Manager) | CORE | - | ON | ON | ON |
| I-16 | 지식 검색 엔진 (Knowledge Search Engine) | CORE | - | ON | ON | ON |
| I-17 | 블루 노드 매니저 (Blue Node Manager) | CORE | - | ON | ON | ON |
| I-18 | 자기진화 엔진 (Self-evo Engine) | EXP | - | OFF | OFF | ON |
| I-19 | 승인 관리자 (Approval Manager) | CORE | **변경 불가** | ON | ON | ON |
| I-20 | 실패·폴백 관리자 (Failure/Fallback Manager) | CORE | - | ON | ON | ON |
| I-21 | 지식 소스 진화 (Source Evolution) | EXP | - | OFF | OFF | ON |
| I-22 | 태스크/프로젝트 관리자 (Task/Project Manager) | COND | - | OFF | COND | ON |
| I-23 | 문서/코드 구조화 (Doc/Code Structuring) | COND | - | OFF | COND | ON |
| I-24 | 지식 그래프 엔진 (Knowledge Graph Engine) | EXP | - | OFF | OFF | ON |
| I-25 | SDAR 엔진 (Self-Directed Adaptive Reasoning) | COND | - | OFF | COND | ON |

### E-Series — 외부 기능 (E-1 ~ E-16, 총 16개)

| ID | 이름 | 분류 | LOCK | V1 | V2 | V3 |
|----|------|------|------|----|----|-----|
| E-1 | 코딩·시스템 설계 도우미 (Coding & System Design Helper) | CORE | - | ON | ON | ON |
| E-2 | 웹 검색 (Web Search) | CORE | - | ON | ON | ON |
| E-3 | 문서 파서 (Document Parser) | CORE | - | ON | ON | ON |
| E-4 | 코드 실행기 (Code Executor) | CORE | - | ON | ON | ON |
| E-5 | 이미지 분석기 (Image Analyzer) | CORE | - | ON | ON | ON |
| E-6 | Z3 솔버 (Z3 Solver) | CORE | - | ON | ON | ON |
| E-7 | 음성→텍스트 (Speech-to-Text) | EXP | - | OFF | OFF | ON |
| E-8 | 텍스트→음성 (Text-to-Speech) | EXP | - | OFF | OFF | ON |
| E-9 | 영상 분석기 (Video Analyzer) | EXP | - | OFF | OFF | ON |
| E-10 | 외부 API 게이트웨이 (External API Gateway) | EXP | - | OFF | OFF | ON |
| E-11 | 브라우저 자동화 (Browser Automation) | EXP | - | OFF | OFF | ON |
| E-12 | DB 커넥터 (DB Connector) | EXP | - | OFF | OFF | ON |
| E-13 | 캘린더/태스크 동기화 (Calendar/Task Sync) | RE-ADD | - | OFF | COND | ON |
| E-14 | 이메일 핸들러 (Email Handler) | RE-ADD | - | OFF | COND | ON |
| E-15 | 파일 시스템/클라우드 수집기 (File System / Cloud Collector) | RE-ADD | - | OFF | COND | ON |
| E-16 | 클라우드 스토리지 동기화 (Cloud Storage Sync) | RE-ADD | - | OFF | COND | ON |

### S-Series — 자기진화 (S-1 ~ S-8, 총 8개)

| ID | 이름 | 분류 | LOCK | V1 | V2 | V3 | I-모듈 연결 |
|----|------|------|------|----|----|-----|------------|
| S-1 | 자기검증 엔진 (Self-check Engine) | CORE | - | ON | ON | ON | I-6, I-15 |
| S-2 | 벤치마크 QA 스위트 (Benchmark QA Suite) | EXP | - | OFF | OFF | ON | I-24 |
| S-3 | 템플릿 진화 (Template Evolution) | EXP | - | OFF | OFF | ON | I-12, I-18 |
| S-4 | 에러 패턴 마이너 (Error Pattern Miner) | EXP | - | OFF | OFF | ON | I-20, I-18 |
| S-5 | 라우터 진화 (Router Evolution) | EXP | - | OFF | OFF | ON | I-10, I-18 |
| S-6 | 검색 진화 (Search Evolution) | EXP | - | OFF | OFF | ON | I-16, I-18 |
| S-7 | 사용자 협업 디자이너 (User-Coop Designer) | EXP | - | OFF | OFF | ON | I-19, I-18 |
| S-8 | 자기진화 거버넌스 (Self-evo Governance) | COND | **변경 불가** | OFF | OFF | ON | I-19, I-8, I-9, I-24 |

### A-Series — 아키텍처 확장 (A-1 ~ A-7, 총 7개)

| ID | 이름 | 분류 | LOCK | V1 | V2 | V3 |
|----|------|------|------|----|----|-----|
| A-1 | 멀티브레인 어댑터 (MultiBrain Adapter) | CORE | - | ON | ON | ON |
| A-2 | 프리셋 모듈화 (Preset Modularization) | CORE | - | ON | ON | ON |
| A-3 | 메타 AI (Meta AI) | EXP | - | OFF | OFF | ON |
| A-4 | 토론 모드 (Debate Mode) | COND | - | OFF | COND | ON |
| A-5 | 지연 생성 (Lazy Generation) | EXP | - | OFF | OFF | ON |
| A-6 | 연합 모듈 네트워크 (Federated Module Network) | EXP | - | OFF | OFF | ON |
| A-7 | 원격 실행기 (Remote Executor) | EXP | - | OFF | OFF | ON |

> **A-6, A-7 구분 (LOCK, 변경 불가)**: A-6은 Federated(연합) 전용, A-7은 Remote Executor(원격 실행) 전용으로 고정되었습니다. [근거: D2.0-01 §0.5 LOCK]

### B-Series — 메모리/스킬/자기진화 자산 (B-1 ~ B-6, 총 6개)

| ID | 이름 | 분류 | LOCK | V1 | V2 | V3 |
|----|------|------|------|----|----|-----|
| B-1 | 스킬 라이브러리 (Skill Library) | EXP | - | OFF | OFF | ON |
| B-2 | 방법론 메모리 (Procedural Memory) | EXP | - | OFF | OFF | ON |
| B-3 | 망각/감쇠 (Memory Decay) | CORE | - | ON | ON | ON |
| B-4 | 자동 커리큘럼 생성기 (Auto Curriculum Generator) | EXP | - | OFF | OFF | ON |
| B-5 | RL 자기 훈련기 (RL-like Self Trainer) | EXP | - | OFF | OFF | ON |
| B-6 | DSPy 프롬프트 최적화기 (DSPy Prompt Optimizer) | EXP | - | OFF | OFF | ON |

> **주의**: B-Series는 "메모리/스킬 **자산 모듈**"의 ID입니다. 메모리 **유형**(L0 세션/L1 프로젝트/L2 장기/L3 절차적)과는 별개의 네임스페이스입니다. [근거: D2.0-01 §5.10]

### C-Series — 검증/추론 확장 (C-1 ~ C-7, 총 7개)

| ID | 이름 | 분류 | LOCK | V1 | V2 | V3 |
|----|------|------|------|----|----|-----|
| C-1 | 논리 검증기 (Logic Verifier) | CORE | - | ON | ON | ON |
| C-2 | 수학 검증기 (Math Verifier) | CORE | - | ON | ON | ON |
| C-3 | 코드 검증기 (Code Verifier) | CORE | - | ON | ON | ON |
| C-4 | 도메인 시뮬레이터 (Domain Simulator) | EXP | - | OFF | OFF | ON |
| C-5 | 베이지안 신념 엔진 (Bayesian Belief Engine) | EXP | - | OFF | OFF | ON |
| C-6 | RL 어드바이저 (RL Advisor) | EXP | - | OFF | OFF | ON |
| C-7 | GNN 스코어 모델 (GNN Score Model) | EXP | - | OFF | OFF | ON |

### D-Series — Brain/Planner/RAG 확장 (D-1 ~ D-6, 총 6개)

| ID | 이름 | 분류 | LOCK | V1 | V2 | V3 |
|----|------|------|------|----|----|-----|
| D-1 | Think 엔진 (Think Engine) | CORE | - | ON | ON | ON |
| D-2 | 멀티모달 엔진 (Multimodal Engine) | CORE | - | ON | ON | ON |
| D-3 | 장기 계획기 (Long Horizon Planner) | EXP | - | OFF | OFF | ON |
| D-4 | 성격/톤 엔진 (Personality/Tone Engine) | EXP | - | OFF | OFF | ON |
| D-5 | 범용 Brain 병렬 (General Brain Parallel) | EXP | - | OFF | OFF | ON |
| D-6 | GraphRAG / 하이브리드 RAG | EXP | - | OFF | OFF | ON |

### EVX-Series — 검증 확장군 (EVX-1 ~ EVX-6, 총 6개)

| ID | 이름 | 분류 | LOCK | V1 | V2 | V3 |
|----|------|------|------|----|----|-----|
| EVX-1 | Code-as-Policy (코드 기반 정책) | RE-ADD | - | OFF | OFF | ON |
| EVX-2 | 적대적 검증기 (Adversarial Verifier) | RE-ADD | **변경 불가** | OFF | OFF | ON |
| EVX-3 | 로그확률 신뢰도 (Log-prob Confidence) | RE-ADD | - | OFF | OFF | ON |
| EVX-4 | 사고 버퍼 (Thought Buffer) | RE-ADD | - | OFF | OFF | ON |
| EVX-5 | 생성-검증-학습 (Gen-Verify-Learn) | RE-ADD | - | OFF | OFF | ON |
| EVX-6 | Z3 솔버 라우팅 (Z3 Solver Routing) | RE-ADD | - | OFF | OFF | ON |

> **E-* vs EVX-* 구분 (LOCK, 변경 불가)**: E-*는 "외부 기능(External Features)" 전용, EVX-*는 "검증 확장(Verify Extensions)" 전용 네임스페이스입니다. E 변형 표기(E\`-*, E/-* 등)는 **전면 금지**됩니다. [근거: D2.0-01 §0.5 LOCK]

---

### 전체 모듈 통계 요약

| 분류 | 개수 | 비율 | 대표 모듈 |
|------|------|------|----------|
| **CORE** (필수) | 32개 | 40% | I-1, I-5, I-8, E-1~E-6, C-1~C-3 등 |

> **참고: CORE 범위 구분** — MASTER_SPEC §2.3에서 정의하는 **CORE 모듈 범위는 26개**입니다: I/E/S/A 시리즈에서 status="CORE"인 모듈 — I(17)+E(6)+S(1)+A(2)=26. 위 표의 32개는 B/C/D 시리즈의 CORE급 모듈(B-3, C-1~C-3, D-1~D-2)까지 포함한 전체 모듈 카탈로그 기준입니다. CORE 26개와 **P0 도메인 16개**(§13 참조, BLUE NODES)는 **서로 다른 분류 축**이므로 혼동하지 않도록 주의하세요. [근거: MASTER_SPEC §2.3, v13 DELTA-019]
| **COND** (조건부) | 7개 | 9% | I-7, I-12, I-22, I-23, I-25, A-4, S-8 |
| **EXP** (실험) | 32개 | 39% | I-18, I-24, E-7~E-12, S-2~S-7, A-3, B-1 |
| **RE-ADD** (재도입) | 10개 | 12% | EVX-1~EVX-6, E-13~E-16 |
| **합계** | **81개** | 100% | — |

### 핵심 요약 (3줄)
1. VAMOS는 **8개 시리즈, 81개 모듈 (I25+E16+S8+A7+B6+C7+D6+EVX6)**로 구성되며, 각 모듈은 CORE/COND/EXP/RE-ADD로 분류됩니다.
2. **LOCK(변경 불가)** 모듈은 I-5, I-8, I-9, I-19, S-8, EVX-2로, 정책·비용·승인의 핵심 모듈입니다.
3. 모든 모듈 정보는 **D2.0-01 §5.6~§5.13의 모듈 카탈로그가 단일 정본(SOT)**입니다.
