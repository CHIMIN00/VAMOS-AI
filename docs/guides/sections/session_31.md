---
session: 31
sections: [43]
status: complete
---

# §43. V2 COND 확장 모듈 (106개)

> **비유**: VAMOS의 COND(조건부) 확장 모듈은 스마트폰의 **앱스토어에서 설치하는 앱**과 비슷합니다. 스마트폰(CORE 모듈)은 기본 기능만 가지고 있지만, 필요한 앱(COND 모듈)을 설치하면 카메라, 건강관리, 교육 등 다양한 기능을 추가할 수 있습니다. 안 쓰는 앱은 삭제하면 공간도 차지하지 않듯이, COND 모듈도 꺼두면 메모리/CPU를 전혀 사용하지 않습니다.

**COND 모듈 (Conditional Module, 조건부 모듈)** 이란 기본적으로 꺼져 있다가(OFF), 사용자가 설정 파일(config.toml)에서 `enabled = true`로 바꿔야만 작동하는 선택적 모듈입니다. V2 버전에서는 기존 원본 10개에 더해 **106개의 확장 COND 모듈**이 7개 카테고리로 그룹화되어 추가됩니다.

[근거: D2.0-01 §5.6, D2.0-01 §5.14.4, PART2 §4 V2-Phase 2]

---

## COND 모듈의 핵심 원리

```
┌──────────────────────────────────────────────────────────────┐
│                     config.v2.toml                           │
│                                                              │
│  [modules.cond.cat_a_ai_ml]                                  │
│  group_enabled = false  ← 기본 OFF (꺼져 있음)               │
│                    ↓ 사용자가 true로 변경                     │
│  group_enabled = true   ← ON (켜짐, 작동 시작!)              │
│                                                              │
│  ※ 비활성 시: 메모리 0, CPU 0 — 자원 낭비 없음               │
│  ※ 활성 시: BaseModule 인터페이스로 통일된 방식으로 동작      │
└──────────────────────────────────────────────────────────────┘
```

### 공통 규칙 (모든 106개 모듈에 적용)

| 규칙 | 설명 |
|------|------|
| **기본 OFF** | 모든 COND 모듈은 초기 상태가 `enabled = false` (D2.0-01 §5.14.4) |
| **BaseModule 상속** | 모든 모듈은 `BaseModule(ABC)` 클래스를 상속받아 동일한 인터페이스 제공 |
| **카테고리별 Mixin** | 7개 카테고리마다 공통 기능을 묶은 Mixin 클래스 적용 |
| **Runnable 인터페이스** | 모든 모듈이 같은 방식으로 실행/중지/상태 확인 가능 |
| **Module Catalog 표준** | id, name, version, category(COND), enabled, dependencies 필드 필수 (D2.0-01 §5.5 LOCK 🔒) |
| **비활성 = 자원 제로** | 꺼진 모듈은 메모리/CPU를 전혀 사용하지 않음 |

[근거: D2.0-01 §5.5 LOCK, D2.0-01 §5.14.4, PART2 V2-Phase 2 규칙]

---

### 버전별 COND 모듈 활성 현황

| 항목 | V0 | V1 | V2 | V3 |
|------|:---:|:---:|:---:|:---:|
| **COND 모듈 수** | 0개 | 0개 | 116개 (원본 10 + 확장 106) | 116개 + EXP 추가 |
| **활성화 방식** | — | — | config.toml `enabled=true` | config + 자동 활성화 |
| **카테고리 그룹** | — | — | 7개 카테고리 | 7개 + EXP 카테고리 |
| **우선순위** | — | — | HIGH 94 / MEDIUM 8 / LOW 4 | 전체 활성 |

[근거: PART2 §1.1, PART2 §4 V2-Phase 2]

---

### 7개 카테고리 전체 구조도

```
V2 COND 확장 모듈 (106개)
│
├── CAT-A: AI/ML 엔진 ──────────── 13개  (모델 추론, 설명가능성, 편향 감사)
├── CAT-B: 지식관리 ─────────────── 13개  (지식 그래프, 벡터 검색, 지식 신선도)
├── CAT-C: 운영/인프라 ──────────── 53개  (헬스체크, 서킷브레이커, 분산 트레이싱)
├── CAT-D: 미디어/생성 ──────────── 8개   (멀티미디어, 스타일 변환, 코드 변환)
├── CAT-E: 교육/학습 ────────────── 7개   (적응형 학습, 퀴즈, 튜토리얼)
├── CAT-F: 웰빙/건강 ────────────── 8개   (수면, 운동, 영양, 감정 분석)
└── CAT-G: 외부통합 확장 ────────── 4개   (Notion, Zapier, JIRA 연동)
                                 ─────
                                 106개
```

---

## §43.1 CAT-A: AI/ML 엔진 (13개)

> **비유**: CAT-A는 VAMOS의 **두뇌 강화 장치**입니다. 기본 두뇌(CORE)가 생각하는 것에 더해, 왜 그렇게 판단했는지 설명하고(SHAP/LIME), 편향이 없는지 감사하고(편향 감사), 더 나은 모델을 자동으로 테스트하는(A/B 테스팅) 고급 인지 기능을 제공합니다.

### 디렉토리 및 설정

- **디렉토리**: `backend/vamos_core/modules/cond_ai_ml/`
- **Mixin**: `AiMlModuleMixin` — 모델 추론 래퍼, 배치 스케줄링, 결과 캐싱
- **공통 의존성**: I-5(Condition & Decision Engine), M-11(PromptManager)
- **config 그룹**: `[modules.cond.cat_a_ai_ml]`

```toml
[modules.cond.cat_a_ai_ml]
group_enabled = false       # 카테고리 일괄 ON/OFF
batch_size = 32             # 배치 처리 기본 크기
model_timeout_s = 60        # 모델 추론 타임아웃 (60초)
cache_ttl_s = 3600          # 결과 캐시 유효 시간 (1시간)
```

### 모듈 목록 (13개)

| # | 모듈명 | 한줄 설명 | 우선순위 | 활성 조건 | 산출물 참조 |
|---|--------|----------|:---:|----------|-----------|
| #11 | **SHAP/LIME 설명가능성** (Explainability) | AI가 왜 그런 판단을 했는지 시각적으로 설명하는 모듈 | HIGH | `cat_a_ai_ml.group_enabled = true` | AINV-056 |
| #12 | **배치 처리** (Batch Processing) | 여러 작업을 한꺼번에 묶어서 효율적으로 처리 | HIGH | `cat_a_ai_ml.group_enabled = true` | D202-059 |
| #13 | **시간 여행 디버깅** (Time-Travel Debugging) | 과거 시점으로 돌아가 AI의 판단 과정을 재현/분석 | HIGH | `cat_a_ai_ml.group_enabled = true` | D203-111 |
| #14 | **모델 A/B 테스팅 고급** | 1000건/7일 동안 두 모델을 비교하여 자동 승격/롤백 | HIGH | `cat_a_ai_ml.group_enabled = true` | D204-162 |
| #15 | **작업 패턴 프로파일** (Task Pattern Profile) | 사용자의 작업 습관을 분석하여 최적화 제안 | HIGH | `cat_a_ai_ml.group_enabled = true` | D206-038 |
| #25 | **감정 패턴 학습** (Emotion Pattern Learning) | 개인의 감정 변화 패턴을 학습하여 예측적 지원 | HIGH | `cat_a_ai_ml.group_enabled = true` | D207-114 |
| #26 | **편향 감사 엔진** (Bias Audit Engine) | 확증/최신/생존/섹터 편향을 자동으로 감지하고 보고 | HIGH | `cat_a_ai_ml.group_enabled = true` | D207-129 |
| #85 | **CrewAI 역할 패턴 참조** | CrewAI 프레임워크의 역할 기반 에이전트 패턴 적용 | HIGH | `cat_a_ai_ml.group_enabled = true` | S7JM-123 |
| #102 | **Qwen 3 한중일 특화** | 한국어/중국어/일본어에 특화된 Qwen 3 모델 활용 | HIGH | `cat_a_ai_ml.group_enabled = true` | S7NP-128 |
| #103 | **FinGPT 활용** | 금융 특화 언어 모델(FinGPT) 통합 | HIGH | `cat_a_ai_ml.group_enabled = true` | S7NP-190 |
| #104 | **Ambient Intelligence** (앰비언트 인텔리전스) | 주변 환경을 인식하여 맥락에 맞는 지능형 서비스 제공 | HIGH | `cat_a_ai_ml.group_enabled = true` | S7NP-198 |
| #105 | **S5 피드백 학습** | 성과 측정, 롤백, 패턴 강화를 통한 자기 개선 | MEDIUM | `cat_a_ai_ml.group_enabled = true` | CLIB-057 |
| #106 | **C3 규칙 제안** | 반복 패턴을 분석하여 새 규칙 제안 (인간 승인 필수) | MEDIUM | `cat_a_ai_ml.group_enabled = true` | CLIB-077 |

[근거: PART2 V2-Phase 2 #11~#15, #25, #26, #85, #102~#106]

**핵심 요약 (3줄)**
1. CAT-A는 AI/ML 엔진 카테고리로, 모델 설명가능성·편향 감사·A/B 테스팅 등 13개 고급 인지 모듈을 포함합니다.
2. 모든 모듈은 `AiMlModuleMixin`을 공유하며, `group_enabled = true`로 카테고리 전체를 한 번에 활성화합니다.
3. HIGH 우선순위 11개 + MEDIUM 2개로 구성되며, 배치 크기(32)와 모델 타임아웃(60초)이 기본 설정됩니다.

---

## §43.2 CAT-B: 지식관리 (13개)

> **비유**: CAT-B는 VAMOS의 **개인 도서관 사서**입니다. 책(지식)을 분류하고, 오래된 책의 내용이 아직 정확한지 확인하고(지식 신선도), 서로 모순되는 내용을 발견하면 알려주고(지식 충돌 감지), 다른 도서관(Notion, Obsidian)에서 책을 가져오기도 합니다.

### 디렉토리 및 설정

- **디렉토리**: `backend/vamos_core/modules/cond_knowledge/`
- **Mixin**: `KnowledgeModuleMixin` — KG(Knowledge Graph, 지식 그래프) 연동, 벡터 검색, 지식 그래프 CRUD
- **공통 의존성**: I-3(ContextAggregator), M-05(L1MemoryProvider), I-7(ProjectSessionManager)
- **config 그룹**: `[modules.cond.cat_b_knowledge]`

```toml
[modules.cond.cat_b_knowledge]
group_enabled = false
kg_backend = "neo4j"              # 지식 그래프 백엔드 (Neo4j 그래프 데이터베이스)
vector_dim = 1536                 # 임베딩 벡터 차원 (OpenAI text-embedding-3-small 기준)
freshness_check_interval_h = 24   # 지식 신선도 점검 주기 (24시간마다)
```

### 모듈 목록 (13개)

| # | 모듈명 | 한줄 설명 | 우선순위 | 활성 조건 | 산출물 참조 |
|---|--------|----------|:---:|----------|-----------|
| #17 | **MemGPT/Letta 패턴 통합** | 장기 메모리를 효율적으로 관리하는 MemGPT 방식 적용 | HIGH | `cat_b_knowledge.group_enabled = true` | D206-117 |
| #18 | **Cognee AI KG 자동 구축** | AI가 자동으로 지식 그래프(Knowledge Graph)를 만들어주는 도구 | HIGH | `cat_b_knowledge.group_enabled = true` | D206-125 |
| #19 | **지식 신선도 관리** (Knowledge Freshness) | 저장된 지식이 최신인지 주기적으로 확인하고 갱신 | HIGH | `cat_b_knowledge.group_enabled = true` | D206-179 |
| #20 | **지식 충돌 자동 감지** | 서로 모순되는 지식을 자동으로 찾아내어 알림 | HIGH | `cat_b_knowledge.group_enabled = true` | D206-180 |
| #21 | **M-020 Notion/Obsidian 임포트** | Notion, Obsidian의 노트를 VAMOS 지식 체계로 가져오기 | HIGH | `cat_b_knowledge.group_enabled = true` | D206-209 |
| #22 | **M-004 스크린 캡처 지식화** | 화면 캡처 내용을 자동으로 분석하여 지식으로 저장 (Microsoft Recall 로컬 버전) | HIGH | `cat_b_knowledge.group_enabled = true` | D206-222 |
| #23 | **M-016 시간 기반 지식 관리** | 타임라인 뷰 + 주간/월간 리뷰로 지식을 시간순 관리 | HIGH | `cat_b_knowledge.group_enabled = true` | D206-226 |
| #24 | **M-043 예측적 지식 서핑** | 사용자 행동을 예측하여 관련 지식을 미리 불러오기 | HIGH | `cat_b_knowledge.group_enabled = true` | D206-232 |
| #87 | **개인 위키** (Personal Wiki) | 개인 지식을 위키 형태로 구조화하여 관리 | HIGH | `cat_b_knowledge.group_enabled = true` | S7JM-267 |
| #88 | **예측적 지식 서핑** (S7JM) | 지식 검색을 미리 예측하여 로딩 속도 향상 | HIGH | `cat_b_knowledge.group_enabled = true` | S7JM-273 |
| #89 | **지식 기반 개인 어시스턴트** | 축적된 지식을 활용한 맞춤형 AI 비서 | HIGH | `cat_b_knowledge.group_enabled = true` | S7JM-274 |
| #107 | **형태소 분석 토큰화** | 한국어 형태소 분석 기반 토큰화 (Mecab-ko V1 / Kiwi V2) | MEDIUM | `cat_b_knowledge.group_enabled = true` | D206-063 |
| #108 | **Zettelkasten 심화** | Zettelkasten(메모 상자) 방법론을 적용한 지식 연결 심화 | MEDIUM | `cat_b_knowledge.group_enabled = true` | D206-208 |

[근거: PART2 V2-Phase 2 #17~#24, #87~#89, #107, #108]

**핵심 요약 (3줄)**
1. CAT-B는 지식관리 카테고리로, 지식 그래프 자동 구축·신선도 관리·충돌 감지 등 13개 모듈을 포함합니다.
2. Neo4j 그래프 DB와 1536차원 벡터 검색을 기반으로, 24시간마다 지식 신선도를 자동 점검합니다.
3. Notion/Obsidian 임포트, 스크린 캡처 지식화 등 외부 지식을 VAMOS 체계로 통합하는 기능이 핵심입니다.

---

## §43.3 CAT-C: 운영/인프라 (53개)

> **비유**: CAT-C는 VAMOS의 **건물 관리팀**입니다. 건물(시스템)의 전기, 수도, 엘리베이터가 정상 작동하는지 점검하고(헬스체크), 문제가 생기면 자동으로 차단하고(서킷브레이커), 건물의 모든 상태를 대시보드에 표시합니다(메트릭 수집). 53개로 가장 많은 모듈을 가진 카테고리입니다.

### 디렉토리 및 설정

- **디렉토리**: `backend/vamos_core/modules/cond_ops/`
  - E-0xx 운영 모듈: `cond_ops/external/` 하위에 배치
- **Mixin**: `OpsModuleMixin` — 헬스체크, 메트릭 수집, 서킷브레이커
- **공통 의존성**: 인프라 레이어 (Redis, PostgreSQL, Prometheus)
- **config 그룹**: `[modules.cond.cat_c_ops]`

```toml
[modules.cond.cat_c_ops]
group_enabled = false
health_check_interval_s = 30     # 헬스체크 주기 (30초마다)
circuit_breaker_threshold = 5    # 서킷브레이커 실패 임계 (5회 실패 시 차단)
metrics_export_interval_s = 15   # 메트릭 내보내기 주기 (15초마다)
```

### 주요 모듈 상세 (10개)

| # | 모듈명 | 한줄 설명 | 왜 중요한가? |
|---|--------|----------|------------|
| #27 | **국제화** (B-026 Internationalization) | 다국어 지원 — 한국어, 영어, 일본어 등 메시지/UI 번역 | 글로벌 사용자 대응 |
| #28 | **접근성** (B-030 Accessibility) | 장애인 사용자를 위한 접근성 표준 준수 (스크린 리더, 키보드 네비게이션) | 포용적 설계 |
| #29 | **버전 관리** (B-032 Version Control) | 시스템 구성 요소의 버전 추적 및 호환성 관리 | 안정적 업데이트 |
| #30 | **분산 트레이싱** (Distributed Tracing) | 여러 서비스를 거치는 요청의 전체 경로를 추적 | 성능 병목 진단 |
| #31 | **백프레셔** (Backpressure) | 과부하 시 요청 속도를 자동으로 조절하여 시스템 보호 | 시스템 안정성 |
| #32 | **CQRS 패턴** (Command Query Responsibility Segregation) | 데이터 읽기와 쓰기를 분리하여 성능 최적화 | 대규모 처리 |
| #33 | **사가 패턴** (Saga Pattern) | 여러 서비스에 걸친 트랜잭션을 안전하게 관리 | 분산 트랜잭션 |
| #34 | **읽기 복제본** (Read Replica) | 읽기 전용 DB 복제본으로 조회 성능 향상 | DB 부하 분산 |
| #74 | **작업 큐 서버** (Task Queue Server) | 비동기 작업을 대기열에 넣고 순서대로 처리 | 안정적 작업 처리 |
| #75 | **검색 엔진 서버** (Search Engine Server) | 전문 검색(Full-text Search) 기능 제공 | 빠른 데이터 검색 |

### 전체 모듈 목록 (53개)

| # 범위 | 모듈 그룹 | 개수 | 설명 | 우선순위 |
|--------|----------|:---:|------|:---:|
| #27~#29 | 국제화, 접근성, 버전 관리 | 3 | 시스템 기본 운영 품질 | HIGH |
| #30~#34 | 분산 트레이싱, 백프레셔, CQRS, 사가, 읽기 복제본 | 5 | 분산 시스템 아키텍처 패턴 | HIGH |
| #35~#73 | E-024~E-092 운영 모듈 | 39 | 외부 연동 운영 모듈 (모니터링, 로깅, 알림 등) | HIGH |
| #74~#79 | 작업 큐, 검색 엔진, 알림, 피처 스토어, CDN, 다중 리전 | 6 | 인프라 서버 컴포넌트 | HIGH |

#### E-0xx 운영 모듈 상세 (39개)

| # | 모듈 ID | 한줄 설명 | 산출물 참조 |
|---|---------|----------|-----------|
| #35 | E-024 운영 | 운영 관리 모듈 | S7AE-561 |
| #36 | E-025 운영 | 운영 관리 모듈 | S7AE-562 |
| #37 | E-026 운영 | 운영 관리 모듈 | S7AE-563 |
| #38 | E-027 운영 | 운영 관리 모듈 | S7AE-564 |
| #39 | E-028 운영 | 운영 관리 모듈 | S7AE-565 |
| #40 | E-029 운영 | 운영 관리 모듈 | S7AE-566 |
| #41 | E-030 운영 | 운영 관리 모듈 | S7AE-567 |
| #42 | E-034 운영 | 운영 관리 모듈 | S7AE-571 |
| #43 | E-035 운영 | 운영 관리 모듈 | S7AE-572 |
| #44 | E-036 운영 | 운영 관리 모듈 | S7AE-573 |
| #45 | E-037 운영 | 운영 관리 모듈 | S7AE-574 |
| #46 | E-038 운영 | 운영 관리 모듈 | S7AE-575 |
| #47 | E-039 운영 | 운영 관리 모듈 | S7AE-576 |
| #48 | E-040 운영 | 운영 관리 모듈 | S7AE-577 |
| #49 | E-043 운영 | 운영 관리 모듈 | S7AE-580 |
| #50 | E-044 운영 | 운영 관리 모듈 | S7AE-581 |
| #51 | E-045 운영 | 운영 관리 모듈 | S7AE-582 |
| #52 | E-046 운영 | 운영 관리 모듈 | S7AE-583 |
| #53 | E-047 운영 | 운영 관리 모듈 | S7AE-584 |
| #54 | E-048 운영 | 운영 관리 모듈 | S7AE-585 |
| #55 | E-049 운영 | 운영 관리 모듈 | S7AE-586 |
| #56 | E-050 운영 | 운영 관리 모듈 | S7AE-587 |
| #57 | E-069 운영 | 운영 관리 모듈 | S7AE-606 |
| #58 | E-070 운영 | 운영 관리 모듈 | S7AE-607 |
| #59 | E-071 운영 | 운영 관리 모듈 | S7AE-608 |
| #60 | E-072 운영 | 운영 관리 모듈 | S7AE-609 |
| #61 | E-075 운영 | 운영 관리 모듈 | S7AE-612 |
| #62 | E-076 운영 | 운영 관리 모듈 | S7AE-613 |
| #63 | E-081 운영 | 운영 관리 모듈 | S7AE-618 |
| #64 | E-082 운영 | 운영 관리 모듈 | S7AE-619 |
| #65 | E-083 운영 | 운영 관리 모듈 | S7AE-620 |
| #66 | E-084 운영 | 운영 관리 모듈 | S7AE-621 |
| #67 | E-086 운영 | 운영 관리 모듈 | S7AE-623 |
| #68 | E-087 운영 | 운영 관리 모듈 | S7AE-624 |
| #69 | E-088 운영 | 운영 관리 모듈 | S7AE-625 |
| #70 | E-089 운영 | 운영 관리 모듈 | S7AE-626 |
| #71 | E-090 운영 | 운영 관리 모듈 | S7AE-627 |
| #72 | E-091 운영 | 운영 관리 모듈 | S7AE-628 |
| #73 | E-092 운영 | 운영 관리 모듈 | S7AE-629 |

#### 인프라 서버 모듈 (6개)

| # | 모듈명 | 한줄 설명 | 산출물 참조 |
|---|--------|----------|-----------|
| #74 | **작업 큐 서버** (Task Queue) | 비동기 작업을 대기열에 넣고 순서대로 처리하는 서버 | S7FI-024 |
| #75 | **검색 엔진 서버** (Search Engine) | 전문 검색(Full-text Search) 기능을 제공하는 서버 | S7FI-026 |
| #76 | **알림 서버** (Notification Server) | 사용자에게 푸시 알림/이메일/SMS 발송 서버 | S7FI-030 |
| #77 | **피처 스토어** (Feature Store) | ML 모델이 사용하는 특성(Feature) 데이터를 저장/서빙 | S7FI-072 |
| #78 | **CDN 구성** (Content Delivery Network) | 정적 파일을 사용자 가까운 서버에서 빠르게 전달 | S7FI-080 |
| #79 | **다중 리전 복제** (Multi-Region Replication) | 여러 지역의 서버에 데이터를 복제하여 가용성 확보 | S7FI-087 |

[근거: PART2 V2-Phase 2 #27~#79, S7AE/S7FI 시리즈]

**핵심 요약 (3줄)**
1. CAT-C는 53개로 가장 많은 모듈을 가진 카테고리로, 시스템의 안정적 운영을 담당합니다.
2. 헬스체크(30초), 서킷브레이커(5회 실패 차단), 메트릭 수집(15초)으로 시스템 상태를 실시간 관리합니다.
3. 분산 트레이싱, CQRS, 사가 패턴 등 엔터프라이즈급 아키텍처 패턴과 39개의 E-0xx 외부 운영 모듈을 포함합니다.

---

## §43.4 CAT-D: 미디어/생성 (8개)

> **비유**: CAT-D는 VAMOS의 **멀티미디어 제작 스튜디오**입니다. 사진 편집(스타일 트랜스퍼), 로고 디자인(로고/아이콘 생성), 음성 편집(화자 분리), 문서 디자인(인포그래픽) 등 다양한 미디어를 만들고 변환하는 도구가 모여 있습니다.

### 디렉토리 및 설정

- **디렉토리**: `backend/vamos_core/modules/cond_media/`
- **Mixin**: `MediaModuleMixin` — 멀티미디어 파이프라인, 포맷 변환, 스토리지 연동
- **공통 의존성**: E-15(CloudCollector), M-07(OutputFormatter)
- **config 그룹**: `[modules.cond.cat_d_media]`

```toml
[modules.cond.cat_d_media]
group_enabled = false
max_file_size_mb = 100           # 처리 가능 최대 파일 크기 (100MB)
transcode_timeout_s = 300        # 변환 작업 타임아웃 (5분)
```

### 모듈 목록 (8개)

| # | 모듈명 | 한줄 설명 | 우선순위 | 활성 조건 | 산출물 참조 |
|---|--------|----------|:---:|----------|-----------|
| #16 | **개인 멀티미디어 라이브러리** | 사진/영상/음성 파일을 AI로 분류·태깅하여 관리 | HIGH | `cat_d_media.group_enabled = true` | D206-115 |
| #80 | **스타일 트랜스퍼** (Style Transfer) | 이미지에 특정 화풍/스타일을 적용하여 변환 | HIGH | `cat_d_media.group_enabled = true` | S7JM-014 |
| #81 | **로고/아이콘 생성** | AI로 로고와 아이콘을 자동 디자인 | HIGH | `cat_d_media.group_enabled = true` | S7JM-016 |
| #82 | **화자 분리** (Speaker Diarization) | 여러 사람이 말하는 오디오에서 누가 언제 말했는지 분리 | HIGH | `cat_d_media.group_enabled = true` | S7JM-023 |
| #83 | **양식/폼 자동 생성** | 설문지, 신청서 등 양식을 AI로 자동 생성 | HIGH | `cat_d_media.group_enabled = true` | S7JM-047 |
| #84 | **크로스모달 검색** (Cross-modal Search) | 텍스트로 이미지를 검색하거나, 이미지로 텍스트를 검색 | HIGH | `cat_d_media.group_enabled = true` | S7JM-062 |
| #86 | **코드 변환** (Code Translation) | 한 프로그래밍 언어의 코드를 다른 언어로 자동 변환 | HIGH | `cat_d_media.group_enabled = true` | S7JM-181 |
| #109 | **인포그래픽 자동 생성** | 데이터를 시각적 인포그래픽으로 자동 변환 | MEDIUM | `cat_d_media.group_enabled = true` | S7JM-057 |

[근거: PART2 V2-Phase 2 #16, #80~#84, #86, #109]

**핵심 요약 (3줄)**
1. CAT-D는 멀티미디어 생성/변환 카테고리로, 이미지·오디오·코드·문서 등 8개 모듈을 포함합니다.
2. 최대 100MB 파일을 처리할 수 있으며, 변환 작업은 5분 타임아웃이 기본 설정됩니다.
3. 크로스모달 검색(텍스트↔이미지)과 코드 변환(언어 간) 등 서로 다른 형식 간 변환이 핵심 기능입니다.

---

## §43.5 CAT-E: 교육/학습 (7개)

> **비유**: CAT-E는 VAMOS의 **개인 과외 선생님**입니다. 학생(사용자)의 실력에 맞게 난이도를 조절하고(적응형 난이도), 시험 준비를 도와주고(시험 도우미), 학습 교재를 만들어주고(교육 컨텐츠 생성), 퀴즈를 내서 이해도를 확인합니다(교육 평가 도구).

### 디렉토리 및 설정

- **디렉토리**: `backend/vamos_core/modules/cond_education/`
- **Mixin**: `EducationModuleMixin` — 학습 진도 추적, 퀴즈 생성, 적응형 난이도
- **공통 의존성**: I-1(IntentDetector), M-11(PromptManager), A-4(DebateMode)
- **config 그룹**: `[modules.cond.cat_e_education]`

```toml
[modules.cond.cat_e_education]
group_enabled = false
adaptive_difficulty = true       # 적응형 난이도 활성화 (사용자 수준에 맞춤)
quiz_max_questions = 20          # 퀴즈 최대 문항 수
```

### 모듈 목록 (7개)

| # | 모듈명 | 한줄 설명 | 우선순위 | 활성 조건 | 산출물 참조 |
|---|--------|----------|:---:|----------|-----------|
| #91 | **개인화 학습 경로** (Personalized Learning Path) | 사용자의 수준과 목표에 맞는 최적 학습 경로 설계 | HIGH | `cat_e_education.group_enabled = true` | S7NP-045 |
| #92 | **시험 준비 도우미** (Exam Prep Assistant) | 시험 일정, 범위, 핵심 요약, 예상 문제 등 시험 대비 지원 | HIGH | `cat_e_education.group_enabled = true` | S7NP-059 |
| #93 | **교육 컨텐츠 생성** (Educational Content Generator) | 학습 주제에 맞는 교재, 설명 자료, 연습 문제 자동 생성 | HIGH | `cat_e_education.group_enabled = true` | S7NP-072 |
| #94 | **교육 평가 도구** (Educational Assessment Tool) | 학습 성취도를 측정하는 시험/퀴즈 자동 생성 및 채점 | HIGH | `cat_e_education.group_enabled = true` | S7NP-073 |
| #113 | **대화형 튜토리얼** (Interactive Tutorial) | AI와 대화하며 단계별로 배우는 튜토리얼 | LOW | `cat_e_education.group_enabled = true` | S7JM-219 |
| #114 | **학습 분석 대시보드** (Learning Analytics Dashboard) | 학습 시간, 진도율, 강/약점을 시각적으로 보여주는 대시보드 | LOW | `cat_e_education.group_enabled = true` | S7NP-051 |
| #115 | **언어 학습 특화** (Language Learning Specialist) | 외국어 학습에 특화된 발음, 문법, 어휘 학습 도구 | LOW | `cat_e_education.group_enabled = true` | S7NP-056 |

[근거: PART2 V2-Phase 2 #91~#94, #113~#115]

**핵심 요약 (3줄)**
1. CAT-E는 교육/학습 카테고리로, 개인화 학습·시험 준비·컨텐츠 생성 등 7개 모듈을 포함합니다.
2. 적응형 난이도 기능이 기본 활성화되어 사용자 수준에 맞게 자동 조절됩니다.
3. HIGH 4개(핵심 교육 기능) + LOW 3개(부가 기능)로 구성되며, A-4(DebateMode)과 연동하여 토론식 학습도 가능합니다.

---

## §43.6 CAT-F: 웰빙/건강 (8개)

> **비유**: CAT-F는 VAMOS의 **개인 건강 코치**입니다. 수면 패턴을 분석하고(수면 개선), 운동 기록을 추적하고(피트니스 트래커), 식단을 관리하고(영양 관리), 감정 변화를 기록하고(감정 일지), 이 모든 데이터를 종합하여 맞춤형 건강 조언을 제공합니다(개인화 건강 인사이트).

### 디렉토리 및 설정

- **디렉토리**: `backend/vamos_core/modules/cond_wellbeing/`
- **Mixin**: `WellbeingModuleMixin` — 건강 데이터 수집, 트렌드 분석, 알림 스케줄링
- **공통 의존성**: I-7(ProjectSessionManager), E-13(CalendarSync)
- **config 그룹**: `[modules.cond.cat_f_wellbeing]`

```toml
[modules.cond.cat_f_wellbeing]
group_enabled = false
data_retention_days = 365        # 건강 데이터 보관 기간 (1년)
reminder_interval_h = 4          # 알림 주기 (4시간마다)
```

### 모듈 목록 (8개)

| # | 모듈명 | 한줄 설명 | 우선순위 | 활성 조건 | 산출물 참조 |
|---|--------|----------|:---:|----------|-----------|
| #95 | **수면 개선 도우미** (Sleep Improvement Assistant) | 수면 시간/패턴을 분석하여 수면 품질 개선 제안 | HIGH | `cat_f_wellbeing.group_enabled = true` | S7NP-085 |
| #96 | **운동/피트니스 트래커** (Fitness Tracker) | 운동 종류, 시간, 칼로리 소비 등을 기록하고 분석 | HIGH | `cat_f_wellbeing.group_enabled = true` | S7NP-086 |
| #97 | **식단/영양 관리** (Diet/Nutrition Manager) | 식사 기록, 영양소 분석, 식단 추천 | HIGH | `cat_f_wellbeing.group_enabled = true` | S7NP-087 |
| #98 | **감정 일지 분석** (Emotion Journal Analyzer) | 감정 변화를 기록하고 패턴을 분석하여 인사이트 제공 | HIGH | `cat_f_wellbeing.group_enabled = true` | S7NP-090 |
| #99 | **사회적 관계 관리** (Social Relationship Manager) | 인간관계 네트워크를 관리하고 소통 패턴 분석 | HIGH | `cat_f_wellbeing.group_enabled = true` | S7NP-098 |
| #100 | **개인화 건강 인사이트** (Personalized Health Insights) | 수면+운동+식단+감정 데이터를 종합한 맞춤형 건강 조언 | HIGH | `cat_f_wellbeing.group_enabled = true` | S7NP-104 |
| #101 | **감정 기반 음악 추천** (Emotion-based Music Recommendation) | 현재 감정 상태에 맞는 음악을 자동 추천 | HIGH | `cat_f_wellbeing.group_enabled = true` | S7NP-106 |
| #116 | **웰빙 대시보드** (Wellbeing Dashboard) | 모든 건강/웰빙 데이터를 한눈에 보여주는 종합 대시보드 | LOW | `cat_f_wellbeing.group_enabled = true` | S7NP-091 |

[근거: PART2 V2-Phase 2 #95~#101, #116]

**핵심 요약 (3줄)**
1. CAT-F는 웰빙/건강 카테고리로, 수면·운동·식단·감정 등 전인적 건강 관리 8개 모듈을 포함합니다.
2. 건강 데이터는 365일(1년) 보관되며, 4시간마다 리마인더 알림을 보내 꾸준한 기록을 유도합니다.
3. #100(개인화 건강 인사이트)이 다른 웰빙 모듈의 데이터를 종합하여 전체적인 건강 조언을 제공하는 허브 역할을 합니다.

---

## §43.7 CAT-G: 외부통합 확장 (4개)

> **비유**: CAT-G는 VAMOS의 **만능 어댑터(변환 플러그)**입니다. 서로 다른 콘센트(외부 서비스)에 맞는 변환 플러그를 제공하여, Notion, Zapier, JIRA 등 다양한 서비스를 VAMOS와 연결할 수 있게 합니다.

### 디렉토리 및 설정

- **디렉토리**: `backend/vamos_core/modules/cond_integration/`
- **Mixin**: `IntegrationModuleMixin` — OAuth 플로우, 웹훅 수신, API 어댑터 패턴
- **공통 의존성**: E-13~E-16(기존 외부통합 모듈), I-22(TaskProjectManager)
- **config 그룹**: `[modules.cond.cat_g_integration]`

```toml
[modules.cond.cat_g_integration]
group_enabled = false
oauth_token_refresh_min = 55     # OAuth 토큰 갱신 주기 (55분 — 만료 전 갱신)
webhook_timeout_s = 30           # 웹훅 응답 타임아웃 (30초)
```

### 모듈 목록 (4개)

| # | 모듈명 | 한줄 설명 | 우선순위 | 활성 조건 | 산출물 참조 |
|---|--------|----------|:---:|----------|-----------|
| #90 | **Notion/Obsidian 통합** | Notion과 Obsidian 앱과 양방향 동기화 | HIGH | `cat_g_integration.group_enabled = true` | S7NP-031 |
| #110 | **ETL 도구** (Extract-Transform-Load) | 외부 데이터를 추출→변환→적재하는 데이터 파이프라인 | MEDIUM | `cat_g_integration.group_enabled = true` | S7NP-016 |
| #111 | **Zapier/Make 호환 패턴** | Zapier, Make(Integromat) 자동화 플랫폼과 연동 | MEDIUM | `cat_g_integration.group_enabled = true` | S7NP-027 |
| #112 | **JIRA/Linear 통합** | JIRA, Linear 프로젝트 관리 도구와 태스크 동기화 | MEDIUM | `cat_g_integration.group_enabled = true` | S7NP-033 |

[근거: PART2 V2-Phase 2 #90, #110~#112]

**핵심 요약 (3줄)**
1. CAT-G는 외부통합 확장 카테고리로, 외부 서비스와의 연동을 담당하는 4개 모듈을 포함합니다.
2. OAuth 토큰을 55분마다 자동 갱신하고, 웹훅은 30초 타임아웃으로 안정적 연동을 보장합니다.
3. 기존 E-13~E-16 외부통합 모듈을 브릿지로 활용하여, Notion·Zapier·JIRA 등 외부 서비스로 확장합니다.

---

## §43 전체 요약 — 106개 모듈 카테고리별 집계

| 카테고리 | 모듈 수 | HIGH | MEDIUM | LOW | config 키 | 핵심 Mixin |
|----------|:------:|:----:|:------:|:---:|-----------|-----------|
| **CAT-A** AI/ML 엔진 | 13 | 11 | 2 | 0 | `cat_a_ai_ml` | `AiMlModuleMixin` |
| **CAT-B** 지식관리 | 13 | 11 | 2 | 0 | `cat_b_knowledge` | `KnowledgeModuleMixin` |
| **CAT-C** 운영/인프라 | 53 | 53 | 0 | 0 | `cat_c_ops` | `OpsModuleMixin` |
| **CAT-D** 미디어/생성 | 8 | 7 | 1 | 0 | `cat_d_media` | `MediaModuleMixin` |
| **CAT-E** 교육/학습 | 7 | 4 | 0 | 3 | `cat_e_education` | `EducationModuleMixin` |
| **CAT-F** 웰빙/건강 | 8 | 7 | 0 | 1 | `cat_f_wellbeing` | `WellbeingModuleMixin` |
| **CAT-G** 외부통합 확장 | 4 | 1 | 3 | 0 | `cat_g_integration` | `IntegrationModuleMixin` |
| **합계** | **106** | **94** | **8** | **4** | — | — |

### 공통 에러코드 및 폴백

| 에러코드 | 발생 조건 | 버전 | 폴백 동작 |
|---------|----------|:---:|----------|
| `COND_MODULE_INIT_FAIL` | COND 모듈 초기화 실패 (의존성 미충족) | V2 | `FB_SKIP_COND` — CORE만으로 계속 동작 |
| `COND_BATCH_TIMEOUT` | CAT-A~G 배치 처리 타임아웃 | V2 | `FB_REDUCE_BATCH` — batch_size를 절반으로 줄여 재시도 |
| `COND_DEPENDENCY_CONFLICT` | COND 모듈 간 순환 의존 감지 | V2 | `FB_ISOLATE_MODULE` — 충돌 모듈 비활성화 |

[근거: PART2 §6.12 에러코드/폴백 테이블]

### 파일 구조

```
backend/vamos_core/modules/
├── cond_ai_ml/                 # CAT-A: AI/ML 엔진 (13개)
│   ├── __init__.py
│   ├── _mixin.py               # AiMlModuleMixin
│   ├── _config.py              # 카테고리 설정
│   └── ai_ml_011_shap_explainer.py  # 파일명 규칙 예시
│
├── cond_knowledge/             # CAT-B: 지식관리 (13개)
│   ├── __init__.py
│   ├── _mixin.py               # KnowledgeModuleMixin
│   └── _config.py
│
├── cond_ops/                   # CAT-C: 운영/인프라 (53개)
│   ├── __init__.py
│   ├── _mixin.py               # OpsModuleMixin
│   ├── _config.py
│   └── external/               # E-0xx 운영 모듈 하위 배치
│
├── cond_media/                 # CAT-D: 미디어/생성 (8개)
│   ├── __init__.py
│   ├── _mixin.py               # MediaModuleMixin
│   └── _config.py
│
├── cond_education/             # CAT-E: 교육/학습 (7개)
│   ├── __init__.py
│   ├── _mixin.py               # EducationModuleMixin
│   └── _config.py
│
├── cond_wellbeing/             # CAT-F: 웰빙/건강 (8개)
│   ├── __init__.py
│   ├── _mixin.py               # WellbeingModuleMixin
│   └── _config.py
│
└── cond_integration/           # CAT-G: 외부통합 확장 (4개)
    ├── __init__.py
    ├── _mixin.py               # IntegrationModuleMixin
    └── _config.py
```

파일명 규칙: `{category_prefix}_{module_number}_{snake_name}.py`
- 예: `ai_ml_011_shap_explainer.py`, `knowledge_017_memgpt_letta.py`

[근거: PART2 V2-Phase 2 v10 공통 규칙]

---

**§43 전체 핵심 요약 (3줄)**
1. V2 COND 확장 모듈 106개는 7개 카테고리(AI/ML, 지식, 운영, 미디어, 교육, 웰빙, 외부통합)로 그룹화되어 배치 구현됩니다.
2. 모든 모듈은 기본 OFF이며, `config.v2.toml`에서 `group_enabled = true`로 카테고리 단위 일괄 활성화하거나 개별 모듈 단위로 제어합니다.
3. 비활성 모듈은 메모리/CPU 사용 제로이며, BaseModule + 카테고리별 Mixin 패턴으로 통일된 인터페이스를 제공합니다.
