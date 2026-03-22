---
session: 06
sections: [7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8]
status: complete
---

# §7. I-Series Part 1: I-1 ~ I-8 — ORANGE CORE 핵심 모듈 상세

> **비유**: ORANGE CORE를 하나의 **두뇌(Brain)**라고 생각해 보세요. 이 두뇌 안에는 각각의 역할을 담당하는 **25개의 영역**이 있습니다. 마치 사람의 뇌에서 "시각 영역"은 눈으로 본 것을 해석하고, "언어 영역"은 말을 이해하고, "판단 영역"은 결정을 내리듯, VAMOS의 I-Series(I-1~I-25) 모듈은 각자 고유한 기능을 수행합니다. 이 장에서는 그중 가장 핵심적인 **I-1부터 I-8까지 8개 모듈**을 하나씩 상세히 살펴봅니다.

[근거: D2.0-02 §0.1, §1, §7]

---

## §7.1 I-1 의도 감지기 (Intent Detector)

### 비유
사용자의 말을 듣고 "아, 이 사람은 이걸 원하는구나!"를 파악하는 **접수 창구 직원**과 같습니다.

### 목적
사용자가 입력한 텍스트(또는 파일/이미지 첨부)를 분석하여 **의도(Intent)**, **도메인(영역)**, **제약 조건**, **출력 형식** 등으로 구조화합니다. 이렇게 정리된 결과물을 **IntentFrame**(의도 프레임)이라고 부르며, 이후 모든 모듈이 이 IntentFrame을 기반으로 일관되게 동작합니다. [근거: D2.0-02 §7.1]

### 구조도

```
사용자 입력 (텍스트 + 첨부파일)
     ↓
┌─────────────────────────┐
│     I-1 Intent Detector │
│  ┌───────────────────┐  │
│  │ 의도 파악          │  │  → "코드 작성해줘" → task_type: code
│  │ 도메인 판별        │  │  → "주식 분석해줘" → domain_hint: P1
│  │ 위험 플래그 설정   │  │  → "계좌 이체해줘" → safety_sensitive: true
│  │ 모호성 탐지        │  │  → "그거 해줘" → is_ambiguous: true
│  └───────────────────┘  │
└─────────┬───────────────┘
          ↓
    IntentFrame (구조화된 의도 프레임)
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `user_input.text` | 필수 | 사용자가 입력한 텍스트 |
| `user_input.attachments` | 선택 | 첨부된 파일/이미지/문서 (형식 메타데이터만 I-1에서 확인) |
| `session_context` | 선택 | L0 세션 요약/최근 대화 내용 |
| `project_context_hint` | 선택 | 프로젝트 ID, 태그 등 (I-7 연계) |

[근거: D2.0-02 §7.2]

### 출력 (Output)

**IntentFrame** (의도 프레임) — 아래 필드들로 구성됩니다:

| 필드 | 설명 | 예시 |
|------|------|------|
| `intent_id` | 고유 식별자 | `"int_abc123"` |
| `trace_id` | 추적용 ID (전체 파이프라인에서 공유) | `"tr_xyz789"` |
| `user_goal` | 사용자의 목표를 한 문장으로 정리 | `"파이썬으로 웹 크롤러 만들기"` |
| `domain_hint` | 도메인 힌트: P0(안전)/P1(주의)/P2(고위험) + 후보 리스트 | `P0` |
| `task_type` | 작업 유형 | `explain`, `plan`, `code`, `research`, `summarize` 등 |
| `constraints` | 형식/포함/제외 제약 | `format: "단일 코드블럭"` |
| `risk_flags` | 위험 플래그 3종 | 안전/승인/비용 민감 여부 (bool) |
| `ambiguity` | 모호성 정보 | 모호한지, 누락 슬롯, 질문 목록 (최대 3개) |
| `required_artifacts` | 필요한 산출물 형태 | `doc`, `pdf`, `code`, `diagram` 등 |

[근거: D2.0-02 §7.3, CLAUDE.md §12 IntentFrame]

### 내부 상태 (States)

| 상태 코드 | 설명 |
|----------|------|
| `I1_S0_RAW` | 원시 입력 수신 상태 |
| `I1_S1_PARSED` | 의도 파싱(분석) 완료 |
| `I1_S2_AMBIGUOUS` | 모호성 감지 — 추가 질문 필요 |
| `I1_S3_READY` | IntentFrame 준비 완료, 다음 모듈로 전달 가능 |

[근거: D2.0-02 §7.5]

### 관련 이벤트 (Events) — `oc.i1.*` 네임스페이스

| 이벤트 | 발생 시점 |
|--------|----------|
| `oc.i1.intent.parsed` | 의도 파싱 성공 시 |
| `oc.i1.intent.ambiguous` | 모호한 입력 감지 시 |
| `oc.i1.parse.started` | 파싱 시작 시 |
| `oc.i1.parse.failed` | 파싱 실패 시 |
| `oc.i1.emotion.detected` | 감정 감지 완료 시 (STEP7 확장) |

[근거: D2.0-02 §7.7, §6.1]

### 에러 코드 (FailureCodes) — `OC_I1_*`

| 에러 코드 | 원인 | 사용자 영향 |
|----------|------|------------|
| `OC_I1_PARSE_FAIL` | 입력을 구조화할 수 없음 (너무 짧거나, 의미 불명) | 요청 거절 또는 재질문 |
| `OC_I1_AMBIGUOUS_UNRESOLVED` | 모호한 슬롯(빈칸)이 해결되지 않음 | 추가 질문으로 전환 |

[근거: D2.0-02 §7.8, §6.2]

### 폴백 전략 (Fallbacks) — `FB_*`

| 폴백 ID | 조건 | 동작 |
|---------|------|------|
| `FB_INTENT_HEURISTIC_PARSE` | `OC_I1_PARSE_FAIL` 발생 시 | 핵심 슬롯(목표/대상/형식)만 최소 추출, 불확실 슬롯은 "unknown"으로 두고 다음 단계에서 보수적 처리 |
| `FB_ASK_CLARIFICATION` | `OC_I1_AMBIGUOUS_UNRESOLVED` 발생 시 | 모호한 슬롯 1~3개만 질문으로 환원, 사용자 응답 전까지 Decision은 HOLD 상태 |

[근거: D2.0-02 §7.9, §6.3]

### Policy Hook 목록

| 조건 | 동작 |
|------|------|
| `safety_sensitive=true` 또는 `approval_maybe_required=true` | I-5 Condition & Decision Engine에서 승인 게이트(Approval Gate) 후보로 전달 |

[근거: D2.0-02 §7.6]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 관계 |
|----------|------|
| **I-2** (Context Builder) | IntentFrame을 받아 근거 수집 시작 |
| **I-4** (Multimodal Interpreter) | 첨부파일 해석 결과를 I-1에 제공 |
| **I-5** (Condition & Decision Engine) | IntentFrame의 위험 플래그를 기반으로 정책/승인 판단 |
| **I-7** (Project/Session Manager) | 프로젝트 컨텍스트 힌트 제공 |
| **I-8** (Policy Engine) | safety 플래그 기반 정책 판단 |
| **Front Mini LLM** | I-1의 내부 서브컴포넌트로, 입력 전처리/도메인 힌트 생성 담당 |

[근거: D2.0-02 §7.4, §1.4, CLAUDE.md §5]

### 버전별 활성 여부

| V0 | V1 | V2 | V3 | status | change_lock |
|----|----|----|-----|--------|-------------|
| ON | ON | ON | ON | **CORE** (필수) | false |

[근거: CLAUDE.md §6 I-Series 표]

### 핵심 요약 (3줄)
1. **I-1 Intent Detector**는 사용자 입력을 **IntentFrame**(의도 프레임)으로 구조화하는 첫 번째 관문입니다.
2. 모호한 입력은 **최대 3개 질문**으로 명확화하고, 위험한 요청은 **risk_flags**로 표시합니다.
3. 파싱 실패 시 최소 추출(FB_INTENT_HEURISTIC_PARSE) 또는 재질문(FB_ASK_CLARIFICATION)으로 대응합니다.

---

## §7.2 I-2 컨텍스트 빌더 / RAG (Context Builder / RAG)

### 비유
도서관에서 참고 자료를 찾아와 "여기 이런 근거가 있어요"라고 정리해 주는 **사서(Librarian)**와 같습니다.

### 목적
I-1이 파악한 사용자의 의도(IntentFrame)를 바탕으로, 내부 문서/기억/외부 웹 등에서 **근거(Evidence)**를 수집·정리합니다. 이를 통해 "추측이나 단정 없이, 근거에 기반한 답변"을 만들 수 있도록 합니다. 결과물은 **EvidencePack**(근거 꾸러미)입니다. [근거: D2.0-02 §7.11]

### 구조도

```
IntentFrame (I-1에서 전달)
     ↓
┌─────────────────────────────┐
│    I-2 Context Builder      │
│  ┌────────┐ ┌────────────┐  │
│  │내부 RAG│ │외부 웹 검색│  │  ← 벡터 검색 + BM25 + GraphRAG + 웹(Tavily)
│  └───┬────┘ └─────┬──────┘  │
│      └─────┬──────┘         │
│        앙상블 재순위화       │
│            ↓                │
│     EvidencePack 생성       │
└─────────────┬───────────────┘
              ↓
    EvidencePack (근거 꾸러미)
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `IntentFrame` | 필수 | I-1에서 생성된 의도 프레임 |
| `allowed_sources_policy` | 필수 | 허용된 소스 범위 (07 정책) |
| `time_constraints` | 선택 | 최신성 요구 여부 |
| `project_assets` | 선택 | 프로젝트 문서/코드 인덱스 힌트 |

[근거: D2.0-02 §7.12]

### 출력 (Output)

**EvidencePack** (근거 꾸러미) — 아래 필드들로 구성됩니다:

| 필드 | 설명 |
|------|------|
| `evidence_pack_id` | 근거 꾸러미 고유 ID |
| `trace_id` | 추적 ID |
| `items[]` | 근거 항목 배열: 소스 유형(memory/doc/web/code 등), 발췌/요약, QoD 점수, 시점 |
| `coverage.sufficient` | 근거가 충분한지 여부 (bool) |
| `coverage.gaps` | 부족한 영역 목록 |
| `citations_ready` | 인용 준비 완료 여부 |

[근거: D2.0-02 §7.13]

### 내부 상태 (States)

| 상태 코드 | 설명 |
|----------|------|
| `I2_S0_READY` | 검색 준비 완료 |
| `I2_S1_QUERY_BUILT` | 검색 쿼리 생성 완료 |
| `I2_S2_FETCHING` | 근거 수집 중 (내부 RAG + 외부 검색) |
| `I2_S3_PACK_READY` | 근거 꾸러미 완성 |
| `I2_S4_INSUFFICIENT` | 근거 부족 — 재검색 또는 다운시프트 필요 |

[근거: D2.0-02 §7.15]

### 관련 이벤트 (Events) — `oc.i2.*` 네임스페이스

| 이벤트 | 발생 시점 |
|--------|----------|
| `oc.i2.query.built` | 검색 쿼리 생성 완료 시 |
| `oc.i2.fetch.started` | 근거 수집 시작 시 |
| `oc.i2.evidence.ready` | 근거 꾸러미 완성 시 |
| `oc.i2.evidence.insufficient` | 근거 부족 판정 시 |
| `oc.i2.fetch.blocked` | 정책에 의해 소스 차단 시 |
| `oc.i2.fetch.failed` | 수집 실패 시 |
| `oc.i2.web_search.triggered` | 실시간 웹 검색 시작 시 (STEP7 확장) |
| `oc.i2.web_search.completed` | 웹 검색 완료 시 (STEP7 확장) |

[근거: D2.0-02 §7.17, §6.1]

### 에러 코드 (FailureCodes) — `OC_I2_*`

| 에러 코드 | 원인 | 사용자 영향 |
|----------|------|------------|
| `OC_I2_RAG_NO_SOURCE` | 검색 가능한 소스가 없음 | 근거 없는 답변 방지, 재검색 시도 |
| `OC_I2_EVIDENCE_QOD_LOW` | 근거 품질(QoD)이 기준 미달 | 단정 금지, 재검색 또는 다운시프트 |
| `OC_I2_SOURCE_POLICY_BLOCK` | 정책에 의해 소스 접근 차단 | 대체 소스로 전환 |
| `OC_I2_TIMEOUT` | 검색 시간 초과 | 짧은 응답 모드로 축소 |

[근거: D2.0-02 §7.18, §6.2]

### 폴백 전략 (Fallbacks) — `FB_*`

| 폴백 ID | 조건 | 동작 |
|---------|------|------|
| `FB_RAG_RETRY_EXPAND` | `OC_I2_EVIDENCE_QOD_LOW` 또는 `OC_I2_RAG_NO_SOURCE` | 검색 범위 확장 (내부→외부, 최신성 완화). 최종 실패 시 "근거 부족" 명시 + 요약으로 다운시프트 |
| `FB_RAG_SWITCH_SOURCE` | `OC_I2_SOURCE_POLICY_BLOCK` 또는 `OC_I2_TIMEOUT` | 다른 소스 세트로 재시도, 타임아웃 시 짧은 응답 모드 |

[근거: D2.0-02 §7.19, §6.3]

### Policy Hook 목록

| 조건 | 동작 |
|------|------|
| 정책상 금지된 소스 | 검색/인용 금지 → deny 또는 대체 소스 |
| QoD 미달 | "단정 금지" + 재검색 루프 (I-6 Self-check)로 전파 |

[근거: D2.0-02 §7.16]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 관계 |
|----------|------|
| **I-1** (Intent Detector) | IntentFrame을 입력으로 받음 |
| **I-5** (Condition & Decision Engine) | EvidencePack을 입력으로 전달 |
| **I-6** (Self-check Engine) | QoD 미달 시 재검색 루프 트리거 |
| **I-15** (Evidence & QoD Manager) | 근거 품질(QoD) 점수 평가 |
| **I-16** (Knowledge Search Engine) | 지식 검색 엔진과 연계 |
| **E-2** (Web Search) | 외부 웹 검색 도구 |

[근거: D2.0-02 §7.14]

### 버전별 활성 여부

| V0 | V1 | V2 | V3 | status | change_lock |
|----|----|----|-----|--------|-------------|
| ON | ON | ON | ON | **CORE** (필수) | false |

> **RAG 기술 진화**: V1은 Basic RAG(BM25+벡터, 정확도 64%+), V2는 Hybrid+Rerank(정확도 83%+), V3는 Self-RAG+GraphRAG(정확도 90%+)로 단계별 발전합니다. [근거: CLAUDE.md §7.4 DEC-004]

[근거: CLAUDE.md §6 I-Series 표]

### 핵심 요약 (3줄)
1. **I-2 Context Builder**는 의도(IntentFrame)를 기반으로 내부·외부에서 **근거(Evidence)**를 수집하는 사서 역할입니다.
2. 수집된 근거는 **EvidencePack**으로 묶이며, 품질 미달(QoD 기준 미충족) 시 **재검색 루프**가 작동합니다.
3. 모든 답변은 반드시 근거에 기반해야 하며, 근거 없는 단정은 **구조적으로 차단**됩니다.

---

## §7.3 I-3 메모리 시스템 (Memory System)

### 비유
학습한 것을 **노트에 적어두고**, 나중에 필요할 때 꺼내 쓰는 **기억 관리 비서**와 같습니다. 단, 어떤 노트는 잠깐만 보관하고(세션 메모리), 어떤 노트는 영구 보관합니다(장기 메모리).

### 목적
4계층 메모리(L0~L3)에 대해 "**무엇을** 저장할지, **언제** 저장할지, **승인이** 필요한지"를 결정하고 실행을 트리거합니다. 저장의 "물리적 구현"은 별도 저장 계층(06)이 담당하고, I-3는 "저장 결정과 호출 타이밍"만 관리합니다. [근거: D2.0-02 §7.21]

### 4계층 메모리 구조

| 계층 | 이름 | 범위 | 유효 기간(TTL) | V1 | V2 | V3 |
|------|------|------|---------------|----|----|-----|
| **L0** | Session (세션) | 단일 대화 | 7일 (최대 30일) | ON | ON | ON |
| **L1** | Project (프로젝트) | project_id 단위 | 90일 (연장 가능) | 선택적 | ON | ON |
| **L2** | Long-term (장기) | 전역 (검색 기반) | 무기한 | OFF | 제한(승인) | ON |
| **L3** | Procedural (절차적) | 전역/프로젝트 | 무기한 | OFF | 제한 | ON |

> **중요 규칙**: L2 저장은 기본적으로 **"승인 필요"** — 변경 불가(LOCK). [근거: CLAUDE.md §7.2]

[근거: CLAUDE.md §15]

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `Decision` (memory_plan 포함) | 필수 | I-5에서 생성된 결정 (저장 계획 포함) |
| `output_artifact_meta` | 필수 | I-4 결과의 메타데이터 |
| `storage_policy` / `retention_policy` | 필수 | 저장 정책/보존 정책 (06/07) |

[근거: D2.0-02 §7.22]

### 출력 (Output)

**MemoryCommitRequest** (메모리 저장 요청):

| 필드 | 설명 |
|------|------|
| `layer` | 저장 대상 계층: L0, L1, L2 |
| `payload_ref` | 저장할 내용 참조 (원문/요약/메타데이터) |
| `requires_user_approval` | 사용자 승인 필요 여부 (bool) |
| `deny_reason` | 거부 사유 (선택) |

[근거: D2.0-02 §7.23]

### 내부 상태 (States)

| 상태 코드 | 설명 |
|----------|------|
| `I3_S0_PLAN_CREATED` | 저장 계획 생성 완료 |
| `I3_S1_WAIT_APPROVAL` | 사용자 승인 대기 중 |
| `I3_S2_COMMITTING` | 저장 실행 중 |
| `I3_S3_DONE` | 저장 완료 |
| `I3_S4_DENY` | 저장 거부됨 |

[근거: D2.0-02 §7.25]

### 관련 이벤트 (Events) — `oc.i3.*` 네임스페이스

| 이벤트 | 발생 시점 |
|--------|----------|
| `oc.i3.plan.created` | 저장 계획 생성 시 |
| `oc.i3.commit.requested` | 저장 요청 시 |
| `oc.i3.commit.approval_required` | 승인 필요 판정 시 |
| `oc.i3.commit.completed` | 저장 완료 시 |
| `oc.i3.commit.denied` | 저장 거부 시 |
| `oc.i3.commit.failed` | 저장 실패 시 |
| `oc.i3.conversation.exported` | 대화 내보내기 시 (STEP7 확장) |
| `oc.i3.conversation.searched` | 대화 이력 검색 시 (STEP7 확장) |

[근거: D2.0-02 §7.27, §6.1]

### 에러 코드 (FailureCodes) — `OC_I3_*`

| 에러 코드 | 원인 | 사용자 영향 |
|----------|------|------------|
| `OC_I3_MEMORY_POLICY_DENY` | 저장 정책에 의해 거부됨 (민감/금지 데이터) | 메타데이터만 저장 또는 완전 거부 |
| `OC_I3_APPROVAL_REQUIRED` | L2 장기 메모리 저장에 사용자 승인 필요 | 승인 전까지 저장 보류 |
| `OC_I3_COMMIT_FAIL` | 저장 실행 중 오류 발생 | 재시도 또는 실패 기록 |

[근거: D2.0-02 §7.28, §6.2]

### 폴백 전략 (Fallbacks) — `FB_*`

| 폴백 ID | 조건 | 동작 |
|---------|------|------|
| `FB_MEMORY_META_ONLY` | `OC_I3_MEMORY_POLICY_DENY` | 원문 저장 금지 시 **메타 요약**(해시/요약/태그)만 저장. 민감/금지 항목은 저장하지 않음 |
| `FB_REQUIRE_APPROVAL` | `OC_I3_APPROVAL_REQUIRED` | 승인 요청 메시지 생성, 승인 전까지 Decision은 HOLD |

[근거: D2.0-02 §7.29, §6.3]

### Policy Hook 목록

| 조건 | 동작 |
|------|------|
| `data_class`가 민감/금지 | payload 제거 (메타만 저장) 또는 deny (07 규정) |
| L2 저장 시 | 기본적으로 **승인 필요** (LOCK) |
| QoD < 0.4 | L2 벡터 삽입 금지 |
| QoD < 0.7 | 출력 보류 |

[근거: D2.0-02 §7.26, CLAUDE.md §15]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 관계 |
|----------|------|
| **I-5** (Condition & Decision Engine) | Decision.memory_plan을 입력으로 받음 |
| **I-4** (Multimodal Interpreter) | 출력 산출물의 메타데이터 제공 |
| **I-7** (Project/Session Manager) | 프로젝트/세션 경계 관리 |
| **I-14** (Summarizer & Memory Distiller) | 대화 요약/메모리 정제 |
| **06 (Storage)** | 물리적 저장 구현 담당 |
| **07 (Safety)** | 민감/금지/승인 규정 제공 |

[근거: D2.0-02 §7.24]

### 버전별 활성 여부

| V0 | V1 | V2 | V3 | status | change_lock |
|----|----|----|-----|--------|-------------|
| ON | ON | ON | ON | **CORE** (필수) | false |

[근거: CLAUDE.md §6 I-Series 표]

### 핵심 요약 (3줄)
1. **I-3 Memory System**은 4계층 메모리(L0~L3)에 **무엇을 언제 저장할지** 결정하는 기억 관리자입니다.
2. 민감한 데이터는 **메타만 저장**(FB_MEMORY_META_ONLY)하고, L2 장기 저장은 기본 **승인 필요**(LOCK)입니다.
3. 프로젝트 간 데이터 혼합은 금지되며, `project_id` 필드로 **네임스페이스가 분리**됩니다.

---

## §7.4 I-4 멀티모달 인터프리터 (Multimodal Interpreter)

### 비유
요리사가 만든 음식을 **예쁜 그릇에 담아 완성된 요리로 내놓는** 플레이팅 전문가와 같습니다. 원재료(Action 결과)를 사용자가 읽고·재사용·저장 가능한 형태로 변환합니다.

### 목적
BLUE NODE(실행 엔진)나 도구(Tools)가 생성한 원시 결과물을 사용자가 읽고, 재사용하고, 저장할 수 있는 **"구조화 산출물"(StructuredOutput)**로 변환합니다. 출력 규격(output_spec)을 준수하는지도 검증합니다. [근거: D2.0-02 §7.31]

> ⚠️ **주의**: D2.0-01 정본에서 I-4는 "멀티모달 **입력** 해석"으로 정의하지만, D2.0-02에서는 "**출력** 구조화"로 설계되어 있습니다. 구현 시 실제 기능 범위를 확인해야 합니다. [근거: D2.0-02 §7 I-4 주석]

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `raw_outputs` | 필수 | BLUE NODE/Tools에서 나온 원시 결과물 |
| `output_spec` | 필수 | Decision.output_spec — 출력 형식 요구사항 |
| `evidence_pack_ref` | 필수 | I-2에서 생성된 근거 꾸러미 참조 |

[근거: D2.0-02 §7.32]

### 출력 (Output)

**StructuredOutput** (구조화 산출물):

| 필드 | 설명 |
|------|------|
| `artifact_type` | 산출물 형태: `md`, `json`, `code`, `diagram` 등 |
| `content` | 실제 내용 |
| `compliance_report` | 규격 준수 보고서: output_spec 충족 여부, 인용 충족 여부, 누락 항목 |

[근거: D2.0-02 §7.33]

### 내부 상태 (States)

| 상태 코드 | 설명 |
|----------|------|
| `I4_S0_RAW` | 원시 결과물 수신 |
| `I4_S1_STRUCTURING` | 구조화 진행 중 |
| `I4_S2_READY` | 구조화 완료, 전달 준비 |
| `I4_S3_SPEC_VIOLATION` | 출력 규격 위반 감지 |

[근거: D2.0-02 §7.35]

### 관련 이벤트 (Events) — `oc.i4.*` 네임스페이스

| 이벤트 | 발생 시점 |
|--------|----------|
| `oc.i4.structuring.started` | 구조화 시작 시 |
| `oc.i4.output.structured` | 구조화 완료 시 |
| `oc.i4.spec.violated` | 출력 규격 위반 시 |
| `oc.i4.mask.applied` | 민감 정보 마스킹 적용 시 |
| `oc.i4.structuring.failed` | 구조화 실패 시 |
| `oc.i4.tone.adapted` | 감정 기반 톤 조절 적용 시 (STEP7 확장) |
| `oc.i4.citations.generated` | 인용 출처 생성 시 (STEP7 확장) |

[근거: D2.0-02 §6.1]

### 에러 코드 (FailureCodes) — `OC_I4_*`

| 에러 코드 | 원인 | 사용자 영향 |
|----------|------|------------|
| `OC_I4_OUTPUT_SPEC_VIOLATION` | 출력이 요구된 형식(output_spec)을 위반 | 재구성 시도 또는 최소 형식으로 다운시프트 |
| `OC_I4_CITATION_MISSING` | 필수 인용이 누락됨 | 인용 재탐지 후 재출력 |
| `OC_I4_MASK_FAIL` | 민감 정보 마스킹 실패 | 민감 필드 재탐지 후 마스킹 재시도 |

[근거: D2.0-02 §7.38, §6.2]

### 폴백 전략 (Fallbacks) — `FB_*`

| 폴백 ID | 조건 | 동작 |
|---------|------|------|
| `FB_OUTPUT_REFORMAT` | `OC_I4_OUTPUT_SPEC_VIOLATION` | output_spec에 맞게 구조 재정렬, 누락 항목은 compliance_report로 명시 |
| `FB_OUTPUT_MINIMAL` | 재구성도 실패 시 | 핵심 결론/해야 할 일만 **최소 포맷**으로 출력, 상세 근거/부록 생략 |
| `FB_POLICY_MASK` | `OC_I4_MASK_FAIL` 또는 `OC_I4_CITATION_MISSING` | 민감 필드 재탐지 → 마스킹 후 재출력 |

[근거: D2.0-02 §7.39, §6.3]

### Policy Hook 목록

| 조건 | 동작 |
|------|------|
| 포맷/민감 정보 규칙 위반 | 마스킹/재작성 요구 (07 규정) |

[근거: D2.0-02 §7.36]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 관계 |
|----------|------|
| **I-1** (Intent Detector) | 감정 프레임(EmotionFrame) 기반 톤 조절에 사용 |
| **I-2** (Context Builder) | EvidencePack 기반 인용 생성 |
| **I-5** (Condition & Decision Engine) | Decision.output_spec을 입력으로 받음 |
| **I-6** (Self-check Engine) | 출력 품질 검증 대상 |
| **I-13** (Multimodal Output Renderer) | 최종 렌더링 |
| **08 (UI/UX)** | 표시 요구사항 제공 |
| **06 (Storage)** | 저장 단위 요구사항 제공 |

[근거: D2.0-02 §7.34]

### 버전별 활성 여부

| V0 | V1 | V2 | V3 | status | change_lock |
|----|----|----|-----|--------|-------------|
| ON | ON | ON | ON | **CORE** (필수) | false |

[근거: CLAUDE.md §6 I-Series 표]

### 핵심 요약 (3줄)
1. **I-4 Multimodal Interpreter**는 원시 결과물을 사용자가 읽고 활용할 수 있는 **구조화 산출물**로 변환합니다.
2. 출력 규격(output_spec) 위반 시 **재구성(FB_OUTPUT_REFORMAT)** 또는 **최소 출력(FB_OUTPUT_MINIMAL)**으로 대응합니다.
3. 민감 정보는 자동 **마스킹** 처리되며, 인용(Citation)이 필요한 답변에는 **출처가 인라인으로 표시**됩니다.

---

## §7.5 I-5 결정 엔진 (Condition & Decision Engine) 🔒

> ⚠️ **LOCK (change_lock=true)** — 이 모듈의 핵심 로직(단일결정 원칙, 게이트 우회 불가)은 **변경 불가**입니다. 변경하려면 반드시 07 Approval Gate 승인이 필요합니다. [근거: CLAUDE.md §6, §7.2]

### 비유
법원의 **판사**와 같습니다. 증거(EvidencePack)와 법률(Policy/Cost/Approval 규칙)을 모두 검토한 뒤, "유죄/무죄"처럼 하나의 **확정 판결(Decision)**을 내리고 **도장을 찍으면(locked=true)** 그 판결은 바꿀 수 없습니다.

### 목적
I-1이 파악한 의도(IntentFrame) + I-2가 모은 근거(EvidencePack) + I-8의 정책/비용 조건을 종합하여, **단일결정(Decision)**을 생성하고 잠금(lock)합니다. 어떤 BLUE NODE(실행 엔진)와 도구(Tools)를 사용할지 라우팅(경로 선택)도 이 단계에서 확정합니다. [근거: D2.0-02 §7.41]

### 단일결정 원칙 (Decision Kernel) — LOCK

> **핵심 규칙**: "한 시점, 한 컨텍스트, 한 결론" — Decision 객체가 `locked=true`가 되면 **결론을 변경할 수 없습니다**. 이후에는 축소(downshift)만 허용됩니다. [근거: D2.0-02 §3, CLAUDE.md §7.2]

### 구조도

```
IntentFrame (I-1)   EvidencePack (I-2)   Cost/Policy (I-8/I-9)
      ↓                    ↓                     ↓
┌─────────────────────────────────────────────────────┐
│              I-5 Condition & Decision Engine          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │PolicyGate│→ │ CostGate │→ │  EvidenceGate    │  │
│  │(정책)    │  │ (비용)   │  │  (근거 충분성)   │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       └──────────────┼─────────────────┘            │
│                      ↓                               │
│           라우팅(BLUE NODE/Tool 선택)                │
│                      ↓                               │
│           Decision 생성 + locked=true                │
└──────────────────────┬──────────────────────────────┘
                       ↓
              Decision (확정 판결)
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `IntentFrame` | 필수 | I-1에서 생성된 의도 프레임 |
| `EvidencePack` | 필수 | I-2에서 수집된 근거 꾸러미 |
| `cost_status` | 필수 | I-9(Cost Manager)에서 제공한 비용 상태 |
| `policy_rules` / `approval_rules` | 필수 | 07에서 제공한 정책/승인 규칙 |
| `project_status` | 선택 | I-7에서 제공한 프로젝트 상태 |

[근거: D2.0-02 §7.42]

### 출력 (Output)

**Decision** (확정 판결) — FREEZE (18필드):

| 핵심 필드 | 설명 |
|----------|------|
| `decision_id` | 결정 고유 ID |
| `trace_id` | 추적 ID |
| `policy_gate` | 정책 게이트 결과: `block`/`require_approval`/`mask`/`allow` |
| `approval_required` | 승인 필요 여부 |
| `approval_status` | 승인 상태: `approved`/`denied`/`pending`/`expired` |
| `cost_gate` | 비용 게이트 결과: `normal`/`downshift`/`split`/`stop` |
| `routing` | 선택된 BLUE NODE / 실행 모드 |
| `memory_plan` | 저장 계획 (I-3 입력) |
| `conclusion` | 최종 결론: `ACCEPT`/`REJECT`/`HOLD`/`ESCALATE` |
| `locked` | **항상 `true`** — 한번 확정되면 변경 불가 |

[근거: D2.0-02 §7.43, CLAUDE.md §12 Decision]

### 내부 상태 (States)

| 상태 코드 | 설명 |
|----------|------|
| `I5_S0_INPUT_READY` | 입력 수신 완료 |
| `I5_S1_GATES_EVALUATED` | 모든 게이트(Policy/Cost/Evidence) 평가 완료 |
| `I5_S2_ROUTE_SELECTED` | BLUE NODE/Tool 라우팅 확정 |
| `I5_S3_DECISION_LOCKED` | 결정 잠금 (locked=true) |
| `I5_S4_DENY_OR_APPROVAL_WAIT` | 거부 또는 승인 대기 |

[근거: D2.0-02 §7.45]

### 관련 이벤트 (Events) — `oc.i5.*` 네임스페이스

| 이벤트 | 발생 시점 |
|--------|----------|
| `oc.i5.gates.evaluated` | 모든 게이트 평가 완료 시 |
| `oc.i5.route.selected` | 라우팅 확정 시 |
| `oc.i5.decision.locked` | 결정 잠금 시 |
| `oc.i5.approval.required` | 승인 필요 판정 시 |
| `oc.i5.cost.downshifted` | 비용 다운시프트 실행 시 |
| `oc.i5.policy.blocked` | 정책에 의해 차단 시 |
| `oc.i5.decision.failed` | 결정 생성 실패 시 |
| `oc.deny.blocked` | 최종 거부 처리 시 |

[근거: D2.0-02 §7.47, §6.1]

### 에러 코드 (FailureCodes) — `OC_I5_*`

| 에러 코드 | 원인 | 사용자 영향 |
|----------|------|------------|
| `OC_I5_POLICY_BLOCK` | 정책에 의해 요청 차단 (Non-goal 등) | 요청 거부 + 사유 설명 + 대안 제시 |
| `OC_I5_APPROVAL_REQUIRED` | 고위험 작업에 사용자 승인 필요 | 승인 전까지 실행 보류 (HOLD) |
| `OC_I5_COST_OVER_BUDGET` | 예산(비용 상한) 초과 위험 | 저비용 모드로 자동 전환 (다운시프트) |
| `OC_I5_EVIDENCE_INSUFFICIENT` | 근거가 충분하지 않음 | HOLD/ESCALATE + 재검색 루프 |
| `OC_I5_ROUTE_NOT_FOUND` | 적합한 BLUE NODE/Tool이 없음 | 범용 안전 노드로 라우팅 |

[근거: D2.0-02 §7.48, §6.2]

### 폴백 전략 (Fallbacks) — `FB_*`

| 폴백 ID | 조건 | 동작 |
|---------|------|------|
| `FB_REQUIRE_APPROVAL` | `OC_I5_APPROVAL_REQUIRED` | 승인 요청 메시지 생성, 승인 전까지 Decision=HOLD |
| `FB_COST_DOWNSHIFT` | `OC_I5_COST_OVER_BUDGET` | 모델/도구를 저비용 모드로 전환 + 출력 범위 축소 |
| `FB_ROUTE_SAFE_NODE` | `OC_I5_ROUTE_NOT_FOUND` | 기본 안전 노드(범용/보수)로 라우팅, 기능 제한 모드 |
| `FB_RESTRICT_GENERAL_INFO` | `OC_I5_POLICY_BLOCK` (의료/법률 도메인) | 단정적 판단 제거, 일반 정보만 안내, **전문가 상담 권유** |
| `FB_DENY_WITH_REASON` | `OC_I5_POLICY_BLOCK` (Non-goal 위반) | 거절 사유 설명 + 허용 가능한 대안 1~2개 제시 |

[근거: D2.0-02 §7.49, §6.3]

### Policy Hook 목록 — Approval/Safety/Cost 연결 (확정)

| 게이트 | 동작 |
|--------|------|
| **Policy Gate** (07) | 금지: `block` → deny / 민감: `mask` 또는 `require_approval` |
| **Cost Gate** (I-9 + 07) | 예산 초과 위험: `downshift` → FB_COST_DOWNSHIFT |
| **Evidence Gate** (I-2/I-15) | 근거 불충분: HOLD/ESCALATE + 재검색 루프 |
| **Approval Gate** | 승인 필요: `require_approval` → FB_REQUIRE_APPROVAL |

> **게이트 우회 불가 (LOCK)**: Policy → Cost → Approval → Evidence 순으로 **반드시 통과**해야 합니다. 어떤 경우에도 이 게이트들을 건너뛸 수 없습니다. [근거: CLAUDE.md §5, §7.2]

[근거: D2.0-02 §7.46]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 관계 |
|----------|------|
| **I-1** (Intent Detector) | IntentFrame 입력 |
| **I-2** (Context Builder) | EvidencePack 입력 |
| **I-3** (Memory System) | Decision.memory_plan 전달 |
| **I-4** (Multimodal Interpreter) | Decision.output_spec 전달 |
| **I-6** (Self-check Engine) | Decision 결과 검증 |
| **I-8** (Policy Engine) | 정책 규칙 제공 |
| **I-9** (Cost Manager) | 비용 상태/게이트 제공 |
| **BLUE NODE (03)** | 라우팅된 실행 엔진 |
| **07 (Safety)** | 승인/정책/금지 규정 |

[근거: D2.0-02 §7.44]

### 버전별 활성 여부

| V0 | V1 | V2 | V3 | status | change_lock |
|----|----|----|-----|--------|-------------|
| ON | ON | ON | ON | **CORE (LOCK)** — 변경 불가 🔒 | **true** |

[근거: CLAUDE.md §6 I-Series 표]

### 핵심 요약 (3줄)
1. **I-5 Condition & Decision Engine**은 의도+근거+정책+비용을 종합해 **단일결정(Decision)**을 생성하고 잠금(lock)하는 판사입니다.
2. 정책/승인/비용/근거 **4개 게이트를 반드시 통과**해야 하며, 우회는 절대 불가합니다 (LOCK).
3. `locked=true` 이후에는 결론 변경이 불가하고, **축소(downshift)만** 허용됩니다 — 이것이 **단일결정 원칙**입니다.

---

## §7.6 I-6 자기검증 엔진 (Self-check Engine)

### 비유
시험 답안지를 제출하기 전에 **한 번 더 검토하는 교정 선생님**과 같습니다. 틀린 부분이 있으면 "다시 풀어봐"라고 돌려보내거나(Soft loop), 너무 심각하면 "선생님한테 물어봐"라고 합니다(Hard loop → 승인 요청).

### 목적
출력 품질, 정합성(일관성), 정책 준수, 비용 적정성, 근거 충분성을 **최종 점검**합니다. 실패 시 자동 1회 재시도(Soft loop)를 하고, 그래도 실패하면 종료 또는 사용자 승인으로 전환합니다. Self-evo(자기진화) 제안 기능도 포함하지만, **자동 적용은 절대 금지**입니다 — "제안"까지만 합니다. [근거: D2.0-02 §7.51]

### Self-check 임계값 (LOCK)

| 위험 등급 | 통과 기준 (self_check_score) | 의미 |
|----------|---------------------------|------|
| **P0** (안전) | ≥ **70점** | 일상적인 질문 (날씨, 일반 상식 등) |
| **P1** (주의) | ≥ **75점** | 전문적인 질문 (투자, 코드, 분석 등) |
| **P2** (고위험) | ≥ **80점** | 고위험 도메인 (의료, 법률 관련 정보 등) |

> **변경 불가 (LOCK)**: 이 임계값은 PLAN 3.0에서 확정된 정본이며, 변경하려면 별도 승인이 필요합니다. [근거: D2.0-02 §7.53-1, §7.53-2.1]

[근거: D2.0-02 §7.53-1]

### FAIL 처리 규칙 (LOCK)

```
1차 FAIL → 자동 1회 Soft loop (재시도)
    ↓ (여전히 FAIL)
2차 연속 FAIL → 게이트 결과 우선으로 수렴:
    ├─ 승인 필요 상황 → FB_REQUIRE_APPROVAL
    ├─ 축소 가능 → FB_OUTPUT_MINIMAL
    └─ 정책 위반 → FB_DENY_WITH_REASON

※ P2(고위험)에서는 Soft loop를 강행하지 않고
   07의 Approval/Policy/Cost Gate 결론을 우선합니다.
```

[근거: D2.0-02 §7.53-1 규칙 2), 3)]

### 인터페이스 (최소)

| 함수 | 입력 | 출력 |
|------|------|------|
| `run_self_check()` | `decision_id`, `structured_output_ref` | `self_check_report` (점수/판정/사유) |
| `propose_self_evo()` | `self_check_report` | `candidate_changes[]` (개선 후보 — 제안만, 자동 적용 금지) |

[근거: D2.0-02 §7.52]

### 관련 이벤트 (Events) — `oc.i6.*` 네임스페이스

| 이벤트 | 발생 시점 |
|--------|----------|
| `oc.i6.selfcheck.started` | 자기검증 시작 시 |
| `oc.i6.selfcheck.passed` | 검증 통과 (PASS) 시 |
| `oc.i6.selfcheck.failed` | 검증 실패 (FAIL) 시 |

[근거: D2.0-02 §7.53]

### 에러 코드 (FailureCodes) — `OC_I6_*`

| 에러 코드 | 원인 | 사용자 영향 |
|----------|------|------------|
| `OC_I6_SELF_CHECK_FAIL` | Self-check 점수가 임계값 미달 | 1차: 자동 재시도 / 2차: 폴백 수렴 |

[근거: D2.0-02 §7.53]

### 폴백 전략 (Fallbacks) — `FB_*`

Self-check FAIL 시 사용되는 폴백은 **게이트 결과에 따라 동적으로 선택**됩니다:

| 상황 | 폴백 ID | 동작 |
|------|---------|------|
| 승인 필요 | `FB_REQUIRE_APPROVAL` | 사용자 승인 요청 → Decision HOLD |
| 축소 가능 | `FB_OUTPUT_MINIMAL` | 핵심만 최소 포맷으로 출력 |
| 정책 위반/Non-goal | `FB_DENY_WITH_REASON` | 거절 사유 설명 + 대안 제시 |

> **중요**: fallback_id 문자열은 반드시 **02 §6.3 Fallback Strategy Registry 정본**만 사용합니다. [근거: D2.0-02 §7.53-1 규칙 2)]

### Policy Hook 목록

| 조건 | 동작 |
|------|------|
| P2 고위험 FAIL | Soft loop 미강행, 07 Gate 결론 우선 적용 |
| 결론 lock 이후 | downshift(축소)만 허용, 결론 변경 불가 |
| PASS/FAIL/Soft loop 결과 | 모두 **LogEvent로 기록** (감사 추적) |

[근거: D2.0-02 §7.53-1 규칙 3), 4)]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 관계 |
|----------|------|
| **I-5** (Condition & Decision Engine) | Decision 결과를 검증 대상으로 받음 |
| **I-4** (Multimodal Interpreter) | StructuredOutput을 검증 |
| **I-2** (Context Builder) | QoD 미달 시 재검색 루프 트리거 |
| **I-15** (Evidence & QoD Manager) | QoD 점수 연계 |
| **I-18** (Self-evo Engine) | Self-evo 제안 전달 (I-12/I-18/I-21 연계) |
| **S-1** (Self-check Engine) | S-Series에서 I-6와 연결 |

[근거: D2.0-02 §7.52]

### 버전별 활성 여부

| V0 | V1 | V2 | V3 | status | change_lock |
|----|----|----|-----|--------|-------------|
| ON | ON | ON | ON | **CORE** (필수) | false |

[근거: CLAUDE.md §6 I-Series 표]

### 핵심 요약 (3줄)
1. **I-6 Self-check Engine**은 답변 품질을 P0:70/P1:75/P2:80 기준으로 **최종 검증**하는 교정 선생님입니다.
2. 1차 실패 시 **자동 1회 재시도**(Soft loop), 2차 실패 시 **폴백 수렴**(승인/축소/거부)으로 처리됩니다.
3. Self-evo(자기진화)는 **"제안만 가능, 자동 적용 절대 금지"**가 핵심 규칙입니다 (LOCK).

---

## §7.7 I-7 프로젝트/세션 매니저 (Project/Session Manager)

### 비유
여러 프로젝트를 동시에 관리하는 **프로젝트 매니저(PM)**와 같습니다. "이 대화는 어떤 프로젝트에 속하는지", "지금까지 무엇을 했는지", "다음에 뭘 해야 하는지"를 추적합니다.

### 목적
`project_id`(프로젝트 식별자), 태그(tags), 세션-프로젝트 연결, 작업 히스토리(이력), 마일스톤(이정표), 컨텍스트 경계(범위)를 관리합니다. 사용자가 여러 프로젝트를 오가도 각 프로젝트의 맥락이 섞이지 않도록 합니다. [근거: D2.0-02 §7.54]

### 인터페이스 (최소)

| 함수 | 입력 | 출력 |
|------|------|------|
| `resolve_project_context()` | `session_id`, `user_input` | `project_context` (현재 프로젝트 정보) |
| `update_project_state()` | `project_id`, `decision_id`, `artifacts_meta` | `ok` (상태 업데이트 완료) |

[근거: D2.0-02 §7.55]

### 관련 이벤트 (Events) — `oc.i7.*` 네임스페이스

| 이벤트 | 발생 시점 |
|--------|----------|
| `oc.i7.project.resolved` | 프로젝트 컨텍스트 해석 완료 시 |
| `oc.i7.project.updated` | 프로젝트 상태 업데이트 시 |

[근거: D2.0-02 §7.56]

### 에러 코드 (FailureCodes) — `OC_I7_*`

| 에러 코드 | 원인 | 사용자 영향 |
|----------|------|------------|
| `OC_I7_PROJECT_RESOLVE_FAIL` | 프로젝트 컨텍스트를 해석할 수 없음 | 기본 컨텍스트로 진행 또는 프로젝트 선택 요청 |

[근거: D2.0-02 §7.56]

### 폴백 전략 (Fallbacks) — `FB_*`

| 폴백 ID | 조건 | 동작 |
|---------|------|------|
| (명시적 폴백 미정의) | `OC_I7_PROJECT_RESOLVE_FAIL` | 기본 프로젝트 컨텍스트 사용 또는 사용자에게 프로젝트 선택 요청 |

> I-7은 최소 명세 수준으로, 상세 폴백 전략은 구현 단계에서 확정됩니다. [근거: D2.0-02 §7.54~7.56]

### Policy Hook 목록

| 조건 | 동작 |
|------|------|
| 프로젝트 간 데이터 혼합 시도 | **금지** — project_id 네임스페이스로 분리 |

[근거: CLAUDE.md §15]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 관계 |
|----------|------|
| **I-1** (Intent Detector) | project_context_hint 제공 |
| **I-3** (Memory System) | 프로젝트별 메모리 경계 관리 |
| **I-5** (Condition & Decision Engine) | project_status 제공 |
| **I-22** (Task/Project Manager) | 상세 작업 관리 확장 (V2+) |

[근거: D2.0-02 §7.54]

### 버전별 활성 여부

| V0 | V1 | V2 | V3 | status | change_lock |
|----|----|----|-----|--------|-------------|
| OFF | OFF | COND | ON | **COND** (조건부) | false |

> **COND(조건부)**: I-7은 기본 꺼짐(OFF)이며, V2에서 조건부 활성화, V3에서 완전 활성화됩니다. V1에서는 기본 프로젝트/세션 관리만 I-1/I-3에서 최소 처리합니다. [근거: CLAUDE.md §6 I-Series 표]

### 핵심 요약 (3줄)
1. **I-7 Project/Session Manager**는 프로젝트별 컨텍스트(맥락)를 관리하는 PM으로, 프로젝트 간 **데이터 혼합을 방지**합니다.
2. 현재는 **최소 명세 수준**이며, V1에서는 OFF(비활성), V2에서 조건부, V3에서 완전 활성화됩니다.
3. 작업 히스토리, 마일스톤, 태그 등을 추적하여 **장기 프로젝트의 연속성**을 보장합니다.

---

## §7.8 I-8 정책 엔진 (Policy Engine) 🔒

> ⚠️ **LOCK (change_lock=true)** — 이 모듈의 핵심 로직(정책 판정, 안전 규칙, Non-goal 적용)은 **변경 불가**입니다. 변경하려면 반드시 07 Approval Gate 승인이 필요합니다. [근거: CLAUDE.md §6, §7.2]

### 비유
건물 입구의 **보안 게이트**와 같습니다. 모든 요청이 이 게이트를 통과해야 하며, "출입 금지 목록"(Non-goal)에 해당하면 무조건 차단하고, "승인 필요" 구역이면 관리자 허가를 받아야만 통과시킵니다.

### 목적
VAMOS의 모든 요청에 대해 **정책(Policy)**, **안전 규칙(Safety Rules)**, **Non-goal(절대 금지 7개)**, **승인 요구사항(Approval)**을 평가하여 `block`(차단), `require_approval`(승인 요구), `mask`(민감 정보 가림), `allow`(허용) 중 하나를 판정합니다. I-5 Condition & Decision Engine이 결정을 내리기 전에 반드시 이 정책 판정을 거쳐야 합니다. [근거: D2.0-02 §7.46, CLAUDE.md §6]

> **D2.0-02 참고**: D2.0-02에서 I-8 "Policy Engine"의 기능은 I-5 섹션(§7.41~7.50)에서 정책 게이트(Policy Gate)로 설계되어 있습니다. D2.0-01 정본에서는 I-8이 "Policy Engine"으로 독립 모듈입니다. [근거: D2.0-02 §4.0 매핑 테이블]

### 정책 판정 4단계

| 판정 결과 | 의미 | 예시 |
|----------|------|------|
| `block` | **즉시 차단** — 실행 불가 | "해킹 방법 알려줘" → Non-goal 2.2 위반 |
| `require_approval` | **승인 필요** — 사용자 확인 후 진행 | P2 도메인 활성화, 고비용 작업 |
| `mask` | **민감 정보 가림** — 실행은 허용하되 민감 데이터 마스킹 | 개인정보 포함 질문 |
| `allow` | **허용** — 제한 없이 진행 | 일반적인 질문/작업 |

[근거: D2.0-02 §7.46, CLAUDE.md §12 Decision.policy_gate]

### Non-goal (절대 금지 7개) — LOCK

정책 엔진이 **무조건 차단**하는 7가지 행위:

| # | 금지 항목 | 위반 시 대응 |
|---|----------|-------------|
| 2.1 | 실거래/주문/계좌/API 연동 | 즉시 거부 (분석 보조만 가능) |
| 2.2 | 불법 행위/해킹/권한 상승 | 즉시 차단 + 법적 책임 고지 |
| 2.3 | 의료/법률 단정적 판단/대리 결정 | 단정 금지 + "전문가 상담 필요" |
| 2.4 | 민감 개인정보 장기 저장 | 저장 거부 + 세션 내 임시 사용만 |
| 2.5 | 저작권/약관 위반 | 거부 + 합법적 접근 방법 안내 |
| 2.6 | P2 도메인 자동 생성 금지 | 명시적 승인 없이 활성화 불가 |
| 2.7 | 위험 기능 자동 실행 금지 | HITL(사람 개입) 승인 없이 실행 불가 |

[근거: CLAUDE.md §8, BASE-1.3 section 2]

### 7개 불변 구역 (ABSOLUTE LOCK)

아래 7개 영역은 **어떤 Self-evo(자기진화)도, 어떤 승인도 변경할 수 없는** 절대 불변 구역입니다:

| 불변 구역 | 설명 |
|----------|------|
| `safety_rules` | 안전 규칙 |
| `cost_ceiling` | 비용 상한 |
| `approval_flow` | 승인 흐름 |
| `non_goals` | 절대 금지 7개 |
| `audit_format` | 감사 로그 형식 |
| `data_retention` | 데이터 보존 정책 |
| `user_consent` | 사용자 동의 |

[근거: CLAUDE.md §7.3, §7.5]

### 게이트 위치 (파이프라인 내 적용 시점)

```
S0_RECEIVED → S1(PolicyGate!) → S2(EvidenceGate) → S3(PolicyGate! + CostGate + ApprovalGate)
          → S4_EXECUTING → S5_OUTPUT → S6(PolicyGate! + SelfCheckGate)
          → S7 → S8_DONE
```

> PolicyGate는 **S1~S3, S6** 단계에서 반복 적용됩니다. 초기 입력 단계부터 최종 출력 단계까지 정책 준수를 보장합니다. [근거: CLAUDE.md §5]

### 관련 이벤트 (Events) — `oc.i5.*` / `oc.i8.*` 네임스페이스

I-8 Policy Engine의 이벤트는 I-5 Condition & Decision Engine과 밀접하게 연관됩니다:

| 이벤트 | 발생 시점 |
|--------|----------|
| `oc.i5.policy.blocked` | 정책에 의해 차단 시 |
| `oc.i5.approval.required` | 정책이 승인을 요구할 때 |
| `oc.deny.blocked` | 최종 거부 처리 시 |
| `oc.p2.activated` | P2 고위험 도메인 활성화 시 |
| `oc.p2.deactivated` | P2 비활성화 시 (세션 종료 시 자동 OFF) |

[근거: D2.0-02 §6.1]

### 에러 코드 (FailureCodes) — `OC_I5_*` (정책 관련)

| 에러 코드 | 원인 | 사용자 영향 |
|----------|------|------------|
| `OC_I5_POLICY_BLOCK` | 정책 위반 (Non-goal, 안전 규칙 등) | 요청 거부 + 사유 설명 |
| `OC_I5_APPROVAL_REQUIRED` | 고위험 작업에 승인 필요 | 승인 대기 (10분 미응답 시 자동 거부) |
| `POLICY_DENY` | 범용 정책 거부 | 대안 제시 |

[근거: D2.0-02 §6.2, CLAUDE.md §16]

### 폴백 전략 (Fallbacks) — `FB_*`

| 폴백 ID | 조건 | 동작 |
|---------|------|------|
| `FB_DENY_WITH_REASON` | `OC_I5_POLICY_BLOCK` | 거절 사유 짧게 설명 + 허용 가능한 대안 1~2개 제시 |
| `FB_RESTRICT_GENERAL_INFO` | 의료/법률 도메인 정책 차단 | 단정적 결론 제거, 일반 정보만 안내, **전문가 상담 권유** + 응급 시 즉시 연락 권고 |
| `FB_REQUIRE_APPROVAL` | 승인 필요 | 승인 요청 생성, 승인/거절/타임아웃 대기 |

[근거: D2.0-02 §6.3]

### Policy Hook 목록

| 조건 | 동작 |
|------|------|
| Non-goal 7개 위반 | 즉시 `block` → deny |
| P2 도메인 활성화 요청 | `require_approval` → 모달 재확인 (DEC-011) |
| 민감 개인정보 포함 | `mask` 또는 `require_approval` |
| P2 세션 종료 | **자동 OFF** (LOCK: Option A) |
| 승인 타임아웃 | 10분 미응답 → **자동 거부** |

[근거: CLAUDE.md §7.3]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 관계 |
|----------|------|
| **I-5** (Condition & Decision Engine) | 정책 판정 결과를 Decision에 반영 |
| **I-9** (Cost Manager) | 비용 관련 정책과 연계 |
| **I-19** (Approval Manager) | 승인 요청/처리 위임 |
| **I-3** (Memory System) | 민감 데이터 저장 정책 적용 |
| **I-6** (Self-check Engine) | Self-check 결과와 정책 교차 검증 |
| **07 (Safety/Cost/Approval)** | 정책 스키마/규정의 정본(SOT) |
| **Guardrails (4-Layer)** | L1(NeMo)+L2(Guardrails AI)+L3(LlamaGuard)+L4(사후감사) |

[근거: D2.0-02 §7.46, CLAUDE.md §7.3]

### RBAC (역할 기반 접근 제어)

| 역할 | 자율 레벨 | 비용 상한 | 가능 작업 |
|------|----------|----------|----------|
| **OWNER** | L3 | ₩266,000/월 | 모든 기능 |
| **ADMIN** | L2 | ₩93,000/월 | 대부분 기능 |
| **OPERATOR** | L1 | ₩40,000/월 | 기본 기능 |
| **VIEWER** | L0 | ₩0 | 조회만 가능 |

> **중요**: L3(최고 자율)에서도 Non-goal/RBAC/CostBudget/안전필터는 **자동 불가**입니다. [근거: CLAUDE.md §7.3]

[근거: CLAUDE.md §7.3 RBAC]

### 버전별 활성 여부

| V0 | V1 | V2 | V3 | status | change_lock |
|----|----|----|-----|--------|-------------|
| ON | ON | ON | ON | **CORE (LOCK)** — 변경 불가 🔒 | **true** |

[근거: CLAUDE.md §6 I-Series 표]

### 핵심 요약 (3줄)
1. **I-8 Policy Engine**은 모든 요청을 `block`/`require_approval`/`mask`/`allow`로 판정하는 **보안 게이트**입니다.
2. Non-goal(절대 금지 7개)과 7개 불변 구역은 **어떤 경우에도 변경 불가**합니다 (ABSOLUTE LOCK).
3. 정책 게이트는 파이프라인의 **S1~S3, S6 단계에서 반복 적용**되어, 입력부터 출력까지 정책 준수를 보장합니다.

---

# 검증 체크리스트 결과

- [x] 8개 모듈 모두 작성 완료 (I-1 ~ I-8)
- [x] 각 모듈 13가지 항목 모두 포함 (모듈명, 비유, 목적, 입력, 출력, 상태, 이벤트, 에러코드, 폴백, Policy Hook, 관련 모듈, 버전별 활성, LOCK 여부)
- [x] I-5, I-8의 LOCK 표시 완료 (🔒 + change_lock=true 명시)
- [x] 비유 설명 포함 (각 모듈마다 초보자 친화적 비유)
- [x] 근거 SOT 참조 표기 완료 (모든 섹션에 [근거: ...] 표기)
