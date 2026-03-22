---
session: 33
sections: [45, 45.1, 45.2, 45.3, 45.4, 45.5, 45.6, 45.7, 46, 46.1, 46.2, 46.3, 47, 47.1, 47.2, 47.3, 47.4, 47.5, 47.6, 48, 49]
status: complete
---

# 부록 (Appendix)

> 이 부록은 VAMOS AI 시스템의 전체 스키마 정의, 의존성 패키지, 정본 문서 맵, 용어집, 자주 묻는 질문을 한데 모은 참고 자료입니다. 본문에서 다룬 개념들을 빠르게 찾아볼 수 있도록 정리했습니다.

---

# §45. 스키마 정의 전체 목록 (D2.1-D1~D8)

## 비유

> 스키마(Schema)는 "택배 상자의 규격"과 같습니다. 모든 택배는 정해진 크기·양식으로 포장해야 배송 시스템이 처리할 수 있듯, VAMOS 내부에서 오가는 모든 데이터도 정해진 스키마(구조 규칙)를 따라야 합니다.

## 정의

**스키마 (Schema)**: 데이터가 어떤 필드(항목)를 갖고, 각 필드가 어떤 타입(문자열/숫자/참거짓 등)이며, 필수인지 선택인지를 정의하는 "데이터 설계도"입니다. VAMOS는 Pydantic v2 (파이썬 데이터 검증 라이브러리)를 사용하여 모든 스키마를 자동 검증합니다. [근거: D2.1-D1 §3, D2.0-02 ADD-036b]

## 구조도

```
D2.1 스키마 문서 체계 (7개 그룹 + 1개 용어집)
┌───────────────────────────────────────────────────┐
│ D1: SCHEMA_GLOSSARY (용어집/규칙 정본)             │
├───────────────────────────────────────────────────┤
│ D2: ORANGE_CORE ─── DecisionSchema, LogEventSchema │
│ D3: BLUE_NODES ──── NodeCapabilityProfile + 12개   │
│ D4: INFRA_CORE ──── ToolRegistryEntry + 6개        │
│ D5: AGENT_WORKFLOW ─ WorkflowOutputEnvelope + 9개  │
│ D6: STORAGE_MEMORY ─ MemoryRecord + 5개            │
│ D7: SAFETY_COST ──── PolicyCheck + 7개             │
│ D8: UI_UX ────────── SOT 스키마 없음 (문서형 계약) │
└───────────────────────────────────────────────────┘
```

> 모든 스키마는 `_meta` 블록(메타데이터 헤더)을 필수 포함하며, 버전은 v3.0.0으로 통일되어 있습니다. [근거: D2.1-D1 §3.1 LOCK]

---

## §45.1 D2.1-D2: ORANGE CORE 스키마

### 비유
ORANGE CORE 스키마는 "법원 판결문 양식"과 같습니다. 판사가 판결을 내릴 때 반드시 사건번호, 당사자, 판결 이유, 결론을 정해진 양식에 적듯, ORANGE CORE의 판단 결과도 DecisionSchema라는 정해진 양식을 따릅니다.

### 주요 Pydantic 모델 목록

| 스키마명 | 역할 | SOT 상태 |
|---------|------|---------|
| **DecisionSchema** | ORANGE CORE의 단일 판단 결과 (의도/근거/게이트/라우팅/메모리/결론) | SOT (정본) |
| **LogEventSchema** | 모든 이벤트 기록의 최소 단위 (이벤트 타입/생산자/심각도/페이로드) | SOT (정본) |
| **EventTypeRegistry** | 이벤트 타입 코드값 목록 (123개, lower.dot 형식) | SOT (레지스트리) |
| **FailureCodeRegistry** | 실패 코드 목록 (36개, UPPER_SNAKE 형식) | SOT (레지스트리) |
| **FallbackRegistry** | 폴백(대체 전략) 코드 목록 (23개, FB_UPPER_SNAKE 형식) | SOT (레지스트리) |

### DecisionSchema 주요 필드 (5개)

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `decision_id` | string | ✅ | 판단 레코드 고유 식별자 (예: `dec_01HZX9R1ABCDE`) |
| `policy_gate` | enum | ✅ | 정책 게이트 결과: `block` / `require_approval` / `mask` / `allow` |
| `cost_gate` | enum | ✅ | 비용 게이트 결과: `normal` / `downshift` / `split` / `stop` |
| `conclusion` | enum | ✅ | 최종 결론: `ACCEPT` / `REJECT` / `HOLD` / `ESCALATE` |
| `locked` | boolean | ✅ | 결정 잠금 여부 — 한번 잠기면 변경 불가 (🔒 변경 불가) |

### LogEventSchema 주요 필드 (5개)

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `event_type` | enum | ✅ | 이벤트 타입 (EventTypeRegistry 코드값만 허용) |
| `producer` | string | ✅ | 생산자 모듈 (예: `I-1`, `I-5`) |
| `payload` | object | ✅ | 이벤트 핵심 데이터 (trace_id, decision_id 등) |
| `severity` | enum | ✅ | 심각도: `info` / `warn` / `error` / `critical` |
| `sinks` | array | ❌ | 이벤트 전달 대상 목록 (`file`, `db`, `audit`) |

[근거: D2.1-D2 §4.1, §4.2, §5.1~5.3]

### 핵심 요약 (3줄)
1. ORANGE CORE는 DecisionSchema(판단)와 LogEventSchema(로그) 2개의 SOT 스키마를 소유합니다.
2. 3개 레지스트리(EventType 123개, FailureCode 36개, Fallback 23개)가 모든 코드값의 정본입니다.
3. Decision은 한번 `locked=true`가 되면 절대 변경할 수 없는 불변 객체입니다 (🔒 변경 불가).

---

## §45.2 D2.1-D3: BLUE NODES 스키마

### 비유
BLUE NODES 스키마는 "직원 이력서 + 업무 요청서 + 결과 보고서" 양식입니다. 각 노드(실행 모듈)가 어떤 능력을 가졌는지(이력서), 어떤 작업을 요청받았는지(요청서), 어떤 결과를 냈는지(보고서)를 표준 양식으로 관리합니다.

### 주요 스키마 목록

| 스키마명 | 역할 | 스키마 수 |
|---------|------|----------|
| NodeCapabilityProfileSchema | 노드 능력 프로필 (필수 도구/위험등급/게이트 목록) | 1 |
| NodeRequestEnvelopeSchema | CORE→NODE 요청 봉투 (의도 요약/제약/trace_id) | 1 |
| NodeResponseEnvelopeSchema | NODE→CORE 응답 봉투 (결과/상태/근거) | 1 |
| ToolCallRegistrySchema | MCP 도구 관리 (도구 ID/인증/호출 제한) | 1 |
| MCPBridgeLayerSchema | MCP 연결 계층 (Streamable HTTP 🔒 변경 불가) | 1 |
| CloudLibrary 시리즈 | 클라우드 라이브러리 관련 7개 스키마 | 7 |

### NodeCapabilityProfileSchema 주요 필드 (5개)

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `node_id` | string | ✅ | 노드 고유 ID (예: `bn_web_research`) |
| `required_tools` | array | ✅ | 필수 도구 ID 목록 (D4 ToolRegistry 참조) |
| `risk_class` | enum | ✅ | 위험도: `low` / `med` / `high` |
| `cost_class` | enum | ✅ | 비용 등급: `v0` / `v1` / `v2` / `v3` |
| `required_gates` | array | ✅ | 필수 게이트: `policy` / `cost` / `approval` / `evidence` / `self_check` |

[근거: D2.1-D3 §5.1~5.12, §4.1]

### 핵심 요약 (3줄)
1. BLUE NODES는 능력 프로필/요청 봉투/응답 봉투 3개 핵심 스키마 + MCP/Cloud Library 9개 스키마를 소유합니다.
2. MCPBridgeLayer의 transport는 `streamable_http`만 허용됩니다 (DEC-017 🔒 변경 불가).
3. 모든 노드 실행은 반드시 trace_id로 Decision에 연결 가능해야 합니다.

---

## §45.3 D2.1-D4: INFRA CORE 스키마

### 비유
INFRA CORE 스키마는 "공장 설비 등록대장"과 같습니다. 어떤 기계(도구)가 있는지, 각 기계의 사용 비용과 위험도는 얼마인지, 사용하려면 어떤 허가(게이트)가 필요한지를 등록 관리합니다.

### 주요 스키마 목록

| 스키마명 | 역할 |
|---------|------|
| ToolRegistryEntrySchema | 도구 레지스트리 항목 (도구 ID/카테고리/위험등급/게이트) |
| BrainAdapterResponseSchema | Brain 어댑터 표준 응답 (출력/근거/비용/경고) |
| InfraInvokeResultSchema | 인프라 호출 결과 (모델 ID/정책 결과/비용 요약) |
| PromptCacheManagerSchema | 프롬프트 캐시 관리 (해시/히트 수/TTL/절감 비용) |
| RateLimitConfigSchema | API 호출 제한 설정 (RPM/RPD/TPM/초과 시 동작) |
| BackupConfigSchema | 데이터 백업 설정 (주기/보존/암호화) |

### ToolRegistryEntrySchema 주요 필드 (5개)

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `tool_id` | string | ✅ | 도구 고유 ID (예: `tool_playwright`) |
| `category` | string | ✅ | 카테고리 (예: `llm.text`, `browser.render`, `mcp.tool`) |
| `risk_class` | enum | ✅ | 위험도: `low` / `med` / `high` |
| `cost_class` | enum | ✅ | 비용 등급: `v0` / `v1` / `v2` / `v3` |
| `required_gates` | array | ✅ | 필수 게이트 목록 (🔒 07 Gate와 정합 필수) |

[근거: D2.1-D4 §4.1~4.6, §5.1]

### 핵심 요약 (3줄)
1. 모든 도구/Brain 실행은 반드시 ToolRegistry를 경유해야 합니다 — 직접 HTTP/SDK 호출 금지 (🔒 변경 불가).
2. PromptCache, RateLimit, Backup 3개 운영 스키마로 비용 절감과 안정성을 관리합니다.
3. BrainAdapterResponse에는 항상 `trace_id`를 포함하여 추적/감사가 가능하도록 합니다.

---

## §45.4 D2.1-D5: AGENT WORKFLOW 스키마

### 비유
AGENT WORKFLOW 스키마는 "공연 대본과 무대 진행표"입니다. 어떤 순서(Intake→Plan→Execute→Verify→Deliver)로 작업이 진행되는지, 각 단계에서 어떤 검증이 필요한지, 실패하면 어떻게 처리하는지를 정의합니다.

### 주요 스키마 목록

| 스키마명 | 역할 |
|---------|------|
| WorkflowOutputEnvelopeSchema | 워크플로우 최종 출력 — 3단 출력 필수 (🔒 변경 불가) |
| FailureReportSchema | 실패 보고서 (원인/근거부족/위험/개선 4항목 필수) |
| VerifyChainEntrySchema | 검증 체인 항목 (EVX-1~EVX-6) |
| WorkflowStageSchema | 표준 5단계 파이프라인 정의 (🔒 변경 불가) |
| AgentMarketplaceSchema | 에이전트 마켓플레이스 항목 |
| CircuitBreakerSchema | 서킷 브레이커 (연속 실패 시 자동 차단) |
| GatePipelineMappingSchema | 게이트-파이프라인 매핑 |
| HITLRequestSchema | Human-in-the-Loop 개입 요청 |
| ResponseEnvelopeSchema | 최종 응답 봉투 |

### WorkflowOutputEnvelopeSchema 주요 필드

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `user_response` | string | ✅ | 사용자에게 전달되는 최종 응답 |
| `evidence_summary` | string | ✅ | 근거/출처 요약 (QoD 포함) |
| `log_report` | object | ✅ | 로그/리포트 (trace_id, 이벤트, 승인 기록) |

> **🔒 변경 불가**: 워크플로우 종료 시 이 3개 필드를 반드시 산출해야 합니다. [근거: D2.1-D5 §4.1, 05 §7.2 LOCK]

### 핵심 요약 (3줄)
1. 워크플로우는 반드시 user_response / evidence_summary / log_report 3단 출력을 산출합니다 (🔒 변경 불가).
2. 실패 시 FailureReport(원인/근거부족/위험/개선)를 의무적으로 생성합니다.
3. 검증 체인(EVX-1~6)과 Circuit Breaker로 품질과 안정성을 보장합니다.

---

## §45.5 D2.1-D6: STORAGE & MEMORY 스키마

### 비유
STORAGE & MEMORY 스키마는 "도서관 카드 카탈로그"입니다. 어떤 기억(책)이 어느 선반(계층 L0~L3)에 있는지, 어떤 종류(B-1~B-4)인지, 언제까지 보관하는지를 기록합니다.

### 주요 스키마 목록

| 스키마명 | 역할 |
|---------|------|
| MemoryRecordSchema | 메모리 레코드 (계층/유형/요약/정책판정/TTL) |
| SourceQoDSchema | 소스 품질 점수 (QoD 종합/신선도/신뢰도/완전성) |
| VectorStoreAdapterSchema | 벡터 DB 어댑터 (Chroma↔Qdrant 투명 전환) |
| GraphRAGConfigSchema | GraphRAG 설정 (Knowledge Graph + RAG 결합) |
| SemanticCacheSchema | 의미 캐시 (유사 질문 재활용, cosine ≥ 0.95 🔒) |

### MemoryRecordSchema 주요 필드 (5개)

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `scope` | enum | ✅ | 저장 계층: `L0`(세션) / `L1`(프로젝트) / `L2`(장기지식) / `L3`(절차) (🔒 변경 불가) |
| `memory_type` | enum | ✅ | 기억 유형: `B-1`(에피소드) / `B-2`(절차) / `B-3`(지식) / `B-4`(감정) (🔒 변경 불가) |
| `content_summary` | string | ✅ | 원문이 아닌 요약/메타 중심 저장 |
| `policy_decision` | enum | ✅ | 저장 정책: `allow` / `restrict` / `deny` |
| `ttl` | string | ❌ | 보존 기한: L0=session_end, L1=90d, L2=indefinite (🔒 변경 불가) |

[근거: D2.1-D6 §4.1~4.5, 06 §2.1 LOCK]

### 핵심 요약 (3줄)
1. 메모리는 4계층(L0~L3) × 4유형(B-1~B-4) 매트릭스로 분류됩니다 (🔒 변경 불가).
2. Semantic Cache는 cosine 유사도 0.95 이상일 때만 캐시 히트로 판정합니다 (🔒 변경 불가).
3. 벡터 DB는 V1=Chroma, V2+=Qdrant로 어댑터 교체만으로 투명 전환됩니다.

---

## §45.6 D2.1-D7: SAFETY/COST/APPROVAL 스키마

### 비유
SAFETY/COST/APPROVAL 스키마는 "건물 출입 보안 시스템"입니다. 방문자(요청)의 신원을 확인하고(PolicyCheck), 출입 허가를 발급하며(Approval), 사용 비용을 관리하고(CostBudget), 위험 수준에 따라 접근 권한을 조절합니다(RBAC/Autonomy).

### 주요 스키마 목록

| 스키마명 | 역할 |
|---------|------|
| PolicyCheckSchema | 정책 검사 결과 (deny/restrict/allow + 사유) |
| ApprovalSchema | 승인 객체 (2단계: plan/execute) |
| CostBudgetSchema | 비용 예산 (일/월 상한 + 사용량 추적) |
| DownshiftSchema | 다운시프트 정책 (80% 경고, 100% 차단 🔒 변경 불가) |
| GuardrailsCheckSchema | 4-Layer Guardrails 검사 결과 |
| RBACRoleSchema | 역할 기반 접근 제어 (OWNER/ADMIN/OPERATOR/VIEWER 🔒 변경 불가) |
| AutonomyLevelSchema | 자율 운영 수준 (L0~L3 🔒 변경 불가) |

### CostBudgetSchema 주요 필드 (5개)

| 필드명 | 타입 | 필수 | 설명 |
|--------|------|------|------|
| `mode` | enum | ✅ | 비용 모드: `V1` / `V2` / `V3` |
| `daily_limit` | integer | ✅ | 일일 상한(원): V1=1,300 / V2=3,100 / V3=8,900 (🔒 변경 불가) |
| `monthly_limit` | integer | ✅ | 월 상한(원): V1=40,000 / V2=93,000 / V3=266,000 (🔒 변경 불가) |
| `used_today` | integer | ✅ | 금일 누적 사용액(원) |
| `used_month` | integer | ✅ | 당월 누적 사용액(원) |

[근거: D2.1-D7 §4.1~4.7, 07 §4.1 LOCK]

### 핵심 요약 (3줄)
1. 비용 상한은 V1=₩40,000/월, V2=₩93,000/월, V3=₩266,000/월로 고정됩니다 (🔒 변경 불가).
2. 다운시프트는 80% 경고 → Mini 모델 강제, 100% 초과 → 자동 차단입니다 (🔒 변경 불가).
3. RBAC 4역할과 Autonomy Level L0~L3으로 세밀한 접근 제어가 가능합니다.

---

## §45.7 D2.1-D8: UI/UX 스키마

### 비유
D8은 "인테리어 디자인 가이드북"입니다. 건물(시스템)의 구조(스키마)를 직접 정의하지 않고, 벽지 색상이나 가구 배치(UI 표현 규칙)만 정의합니다.

### SOT 스키마 없음 (문서형 계약)

D8은 SOT 스키마를 소유하지 않습니다 (DN-005 결정). 대신 아래 문서형 계약을 정의합니다:

| 계약 항목 | 내용 | 연결 |
|----------|------|------|
| UI 프레임워크 | **Tauri 2.0 + React** (🔒 변경 불가) | STEP7 S7C-053 |
| 이벤트 매핑 | `event_type` → UI 표시 (코드값은 D2 정본 참조) | D2 EventTypeRegistry |
| 에러 메시지 매핑 | `failure_code` → UI 문구/우선순위 | D2 FailureCodeRegistry |
| Pipeline 상태 매핑 | S0~S8 → UI_S4_RUNNING 등 | 08 §4.6 |
| 산출물 유형 | Canvas / Artifacts / 알림 / 자율 수준 UI | 08 §7 |

[근거: D2.1-D8 §2, §6-A, DN-005]

### 핵심 요약 (3줄)
1. D8은 SOT 스키마가 없으며, UI 표현 규칙만 "문서형 계약"으로 정의합니다.
2. V1 데스크톱은 Tauri 2.0 + React로 구현합니다 (🔒 변경 불가).
3. 모든 UI 이벤트/에러/폴백 코드값은 D2 정본 레지스트리를 참조합니다 (REF-only).

---

# §46. 의존성 & 패키지 목록 (PHASE_B3)

## 비유

> 의존성 패키지는 "레고 블록 부품 목록"과 같습니다. VAMOS라는 완성품을 만들려면 어떤 블록(패키지)이 필요한지, 각 블록의 규격(버전)은 무엇인지를 정리한 것입니다.

## 정의

**의존성 (Dependency)**: 소프트웨어가 동작하기 위해 필요한 외부 라이브러리/패키지입니다. VAMOS는 Frontend(React), Backend(Rust/Tauri), AI/ML(Python) 3개 영역의 패키지를 관리합니다. [근거: PHASE_B3 §1]

### 의존성 관리 원칙

| 원칙 | 내용 |
|------|------|
| 최소 의존 | V1에 필요한 패키지만 포함, V2+ 패키지는 `[V2+]` 표시 |
| 버전 고정 | 메이저 버전 호환 범위 지정 (`>=`, `<` 사용) |
| LOCK 준수 | A1 Tech Stack LOCK 결정에 부합하는 패키지만 |
| 라이선스 검토 | 상용/오픈소스 충돌 방지 |
| 보안 감사 | `npm audit`, `cargo audit`, `pip-audit` 정기 실행 |

[근거: PHASE_B3 §1.1]

---

## §46.1 Python 패키지 (pyproject.toml)

> **필수 조건**: `requires-python = ">=3.11"` — BGE-M3, Pydantic v2 등이 Python 3.11+ 전용 기능에 의존합니다.

### 핵심 패키지 (core)

| 패키지 | 버전 | 용도 | 비고 |
|--------|------|------|------|
| `pydantic` | `>=2.10,<3.0` | 스키마 검증 (Pydantic v2) | 🔒 전수 검증 의무 |
| `langgraph` | `>=0.2.60,<1.0` | StateGraph 워크플로우 | 🔒 Agent 프레임워크 |
| `langchain-core` | `>=0.3.25,<1.0` | Runnable 인터페이스 | 🔒 패턴 참조만 |
| `langchain-openai` | `>=0.2.14,<1.0` | OpenAI GPT-4o mini/GPT-4o | V1 기본 LLM |
| `langchain-community` | `>=0.3.15,<1.0` | Ollama 로컬 LLM | V1 로컬 Brain |

### 임베딩 / 벡터 / 저장소

| 패키지 | 버전 | 용도 | 버전별 |
|--------|------|------|--------|
| `FlagEmbedding` | `>=1.3.0,<2.0` | BGE-M3 임베딩 (1024차원, 무료) | V1 |
| `torch` | `>=2.5.0,<3.0` | PyTorch (로컬 모델 추론) | V1 |
| `chromadb` | `>=0.5.23,<1.0` | Chroma 벡터 DB | V1 |
| `qdrant-client` | `>=1.12.0,<2.0` | Qdrant 벡터 DB | [V2+] |
| `aiosqlite` | `>=0.20.0,<1.0` | 비동기 SQLite | V1 |
| `sqlalchemy` | `>=2.0.36,<3.0` | SQL ORM | V1/V2+ |

### 가드레일 / MCP / 유틸리티

| 패키지 | 버전 | 용도 | 버전별 |
|--------|------|------|--------|
| `nemoguardrails` | `>=0.11.0,<1.0` | Layer 1 입력 레일 | V1 |
| `guardrails-ai` | `>=0.5.15,<1.0` | Layer 2 출력 검증 | V1 |
| `transformers` | `>=4.47.0,<5.0` | LlamaGuard (Layer 3) | [V2+] |
| `httpx` | `>=0.28.0,<1.0` | MCP Streamable HTTP 클라이언트 | V1 |
| `tiktoken` | `>=0.8.0,<1.0` | 토큰 카운팅 (🔒 cl100k_base) | V1 |
| `structlog` | `>=24.4.0,<25.0` | 구조화 로깅 | V1 |
| `orjson` | `>=3.10.0,<4.0` | 고속 JSON 직렬화 | V1 |
| `tenacity` | `>=9.0.0,<10.0` | API 호출 재시도 | V1 |

[근거: PHASE_B3 §4.1~4.8]

---

## §46.2 Rust 크레이트 (Cargo.toml)

| 크레이트 | 버전 | 용도 |
|---------|------|------|
| `tauri` | `^2.2` | Tauri 2.0 코어 프레임워크 (🔒 UI LOCK) |
| `serde` / `serde_json` | `^1.0` | JSON 직렬화/역직렬화 |
| `tokio` | `^1.42` (features: full) | 비동기 런타임 |
| `reqwest` | `^0.12` (features: json, rustls-tls) | MCP HTTP 통신 (DEC-017) |
| `uuid` | `^1.11` (features: v4) | 고유 ID 생성 (decision_id, trace_id) |
| `chrono` | `^0.4` | ISO8601 타임스탬프 |
| `thiserror` | `^2.0` | VamosError Rust 구현 |
| `tracing` | `^0.1` | 구조화 로깅/트레이싱 |
| `toml` | `^0.8` | 설정 파일 파싱 |

[근거: PHASE_B3 §3.1~3.4]

---

## §46.3 Node 패키지 (package.json)

### dependencies (주요 14개)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `react` / `react-dom` | `^18.3.0` | React UI 라이브러리 |
| `@tauri-apps/api` | `^2.2.0` | Tauri IPC 통신 |
| `zustand` | `^5.0.0` | 경량 상태 관리 (Flux 패턴) |
| `@tanstack/react-query` | `^5.62.0` | 서버 상태/비동기 데이터 |
| `@xyflow/react` | `^12.4.0` | 노드 기반 플로우 에디터 (LangGraph 시각화) |
| `recharts` | `^2.14.0` | 차트/시각화 (비용 차트) |
| `zod` | `^3.24.0` | 프론트 스키마 검증 |
| `sonner` | `^1.7.0` | 토스트 알림 |

### devDependencies (주요)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| `typescript` | `^5.7.0` | TypeScript 컴파일러 |
| `vite` | `^6.0.0` | 번들러/개발 서버 |
| `vitest` | `^2.1.0` | 테스트 프레임워크 |
| `tailwindcss` | `^3.4.0` | 유틸리티 CSS |
| `eslint` | `^9.16.0` | 린터 |
| `prettier` | `^3.4.0` | 코드 포매터 |

[근거: PHASE_B3 §2.1~2.2]

### 버전별 차이 요약

| 구성 요소 | V1 | V2 | V3 |
|----------|-----|-----|-----|
| **LLM** | Ollama + GPT-4o mini | + Claude | + vLLM |
| **Embedding** | BGE-M3 (로컬) | + text-embedding-3-small | + large |
| **Vector DB** | Chroma | Qdrant | Qdrant Cloud |
| **Storage** | SQLite | + PostgreSQL | 매니지드 Postgres |
| **Guardrails** | 2-Layer | + LlamaGuard (4-Layer) | = V2 |
| **모니터링** | structlog (JSONL) | + Postgres 로그 | + OpenTelemetry + Prometheus |
| **비용 상한** | ₩40K/월 | ₩93K/월 | ₩266K/월 |

[근거: PHASE_B3 §5.1~5.4]

### 핵심 요약 (3줄)
1. Python(30+ 패키지), Rust(13 크레이트), Node(28 패키지) 3개 영역으로 구성됩니다.
2. V1→V2→V3로 진화하며 LLM/Vector/Storage/Guardrails 패키지가 점진 확장됩니다.
3. 모든 패키지는 MIT/Apache-2.0 호환 라이선스이며, 보안 감사를 정기 실행합니다.

---

# §47. 정본 문서 맵 & 우선순위

## 비유

> 정본 문서 맵은 "법률 체계의 위계"와 같습니다. 헌법(RULE) > 법률(PLAN) > 시행령(DESIGN) > 세부 규칙(스키마) 순으로, 상위 문서가 하위 문서보다 항상 우선합니다.

---

## §47.1 SOT 문서 전체 인덱스

> VAMOS 프로젝트의 전체 산출물 문서(68개)를 분류별로 정리합니다.

### RULE (절대 규칙) — 1개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 1 | BASE-1.3_VAMOS_RULE_1.3_BASE.md | 절대 상위 규칙 (Identity/Safety/Policy) | 필수 |

### PLAN (로드맵) — 2개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 2 | PLAN-2.0_VAMOS_PLAN_2.0_.md | (SUPERSEDED) 이전 로드맵 | - |
| 3 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | 로드맵/비용/버전 정본 (SOT) | 필수 |

### DESIGN (아키텍처 설계) — 8개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 4 | D2.0-01: OVERVIEW | 통합 개요/연결 허브 | 필수 |
| 5 | D2.0-02: ORANGE_CORE | 판단/제어 엔진 (I-1~I-21) | 필수 |
| 6 | D2.0-03: BLUE_NODES | 도메인 실행 모듈 | 필수 |
| 7 | D2.0-04: INFRA_CORE | 인프라 계층 | 필수 |
| 8 | D2.0-05: AGENT_WORKFLOW | 워크플로우 파이프라인 | 필수 |
| 9 | D2.0-06: STORAGE_MEMORY | 저장/메모리 계층 | 필수 |
| 10 | D2.0-07: SAFETY_COST_APPROVAL | 안전/비용/승인 | 필수 |
| 11 | D2.0-08: UI_UX | UI/UX 설계 | 필수 |

### SCHEMA (스키마 정의) — 10개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 12 | D2.1-A1: TECH_STACK | 기술 스택 정본 | 필수 |
| 13 | D2.1-D1: SCHEMA_GLOSSARY | 용어집/규칙 정본 | 필수 |
| 14~20 | D2.1-D2~D8 | 스키마 정의 (7개 그룹) | 필수 |
| 21 | D2.1-Q1: AUDIT_REPORT | 감사 보고서 | 필수 |

### PHASE (구현 가이드) — 7개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 22 | PHASE_B1: API_CONTRACT | API 계약 (88개 엔드포인트) | 필수 |
| 23 | PHASE_B2: PROJECT_STRUCTURE | 프로젝트 구조 (Monorepo) | 필수 |
| 24 | PHASE_B3: DEPENDENCIES | 의존성 관리 | 필수 |
| 25 | PHASE_B4: CONFIG_SPEC | 설정 명세 | 필수 |
| 26 | PHASE_B5: TEST_STRATEGY | 테스트 전략 | 필수 |
| 27 | PHASE_B6: CICD_PIPELINE | CI/CD 파이프라인 | 필수 |
| 28 | PHASE_B7: MIGRATION_STRATEGY | 마이그레이션 전략 | 필수 |

### SPEC (통합 명세) — 5개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 29 | VAMOS_MASTER_SPECIFICATION | 통합 요약 (단일 참조점) | 필수 |
| 30 | VAMOS_AI_INVESTING_SPEC | AI 투자 도메인 | V2 필수 |
| 31 | VAMOS_CLOUD_LIBRARY_SPEC | Cloud Library 시스템 | V2 필수 |
| 32 | VAMOS_AGENT_TEAMS_SPEC | Agent Teams 설계 | V2 필수 |
| 33 | VAMOS_SDAR_DESIGN_SPECIFICATION | SDAR 자율추론 | V3 필수 |

### STEP7 상세명세서 — 5개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 34~37 | STEP7_A-E / F-I / J-M / N-P 상세명세서 | 16개 카테고리 상세 | 참고 |
| 38 | STEP7_보강_통합명세서 | TITLE_ONLY 448건 확장 | 참고 |

### STEP7 작업가이드 — 15개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 39 | STEP7-B_대화프로세스_작업가이드 | 대화 프로세스 강화 가이드 | 참고 |
| 40 | STEP7-C_UI_UX_전수비교_작업가이드 | UI/UX 전수 비교 가이드 | 참고 |
| 41 | STEP7-D_메모리_저장소_아키텍처_작업가이드 | 메모리/저장소 강화 가이드 | 참고 |
| 42 | STEP7-E_보안_안전_거버넌스_작업가이드 | 보안/거버넌스 강화 가이드 | 참고 |
| 43 | STEP7-F_인프라_배포_MLOps_작업가이드 | 인프라/MLOps 강화 가이드 | 참고 |
| 44 | STEP7-G_벤치마크_평가_품질보증_작업가이드 | 벤치마크/품질 강화 가이드 | 참고 |
| 45 | STEP7-H_비즈니스모델_시장전략_작업가이드 | 비즈니스/시장 전략 가이드 | 참고 |
| 46 | STEP7-I_AI_Investing_보강_작업가이드 | AI 투자 보강 가이드 | 참고 |
| 47 | STEP7-J_멀티모달_생성처리_작업가이드 | 멀티모달 처리 강화 가이드 | 참고 |
| 48 | STEP7-K_에이전트프로토콜_상호운용성_작업가이드 | 에이전트 프로토콜 강화 가이드 | 참고 |
| 49 | STEP7-L_개발자도구_API_SDK_작업가이드 | 개발자도구/SDK 강화 가이드 | 참고 |
| 50 | STEP7-M_PKM_지식관리_작업가이드 | PKM/지식관리 강화 가이드 | 참고 |
| 51 | STEP7-N_워크플로우자동화_RPA_작업가이드 | 워크플로우/RPA 강화 가이드 | 참고 |
| 52 | STEP7-O_교육_학습_자기개발_작업가이드 | 교육/학습 강화 가이드 | 참고 |
| 53 | STEP7-P_건강_웰니스_감성AI_작업가이드 | 건강/감성AI 강화 가이드 | 참고 |

### STEP7 보조 문서 — 4개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 54 | STEP7_A-I_보강_추가항목_통합 | A~I 카테고리 보강 추가항목 통합 | 참고 |
| 55 | STEP7_STEP6통합_마스터인덱스 | STEP6/7 통합 마스터 인덱스 (1,545항목) | 참고 |
| 56 | STEP7_작업가이드 | STEP7 전체 작업 가이드라인 | 참고 |
| 57 | STEP7_PHASE7_최종검증보고서 | STEP7 최종 검증 결과 보고서 | 참고 |

### STEP7 구현 우선순위 — 6개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 58 | STEP7_R1_V1_CRITICAL | V1 CRITICAL 우선순위 항목 | 필수 |
| 59 | STEP7_R2_V1_HIGH | V1 HIGH 우선순위 항목 | 필수 |
| 60 | STEP7_R3_V1_MEDIUM_LOW | V1 MEDIUM/LOW 우선순위 항목 | 참고 |
| 61 | STEP7_R4_V2_CRITICAL_HIGH | V2 CRITICAL/HIGH 우선순위 항목 | V2 필수 |
| 62 | STEP7_R5_V2_MEDIUM_LOW | V2 MEDIUM/LOW 우선순위 항목 | 참고 |
| 63 | STEP7_R6_V3_ALL | V3 전체 우선순위 항목 | V3 필수 |

### READINESS (구현 준비) — 3개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 64 | VAMOS_IMPLEMENTATION_READINESS_GUIDE | 구현 준비 가이드 | 필수 |
| 65 | VAMOS_IMPLEMENTATION_READINESS_REVIEW | 구현 준비 검토 보고서 | 필수 |
| 66 | VAMOS_V0_READINESS_FINAL_REVIEW | V0 준비 최종 검토 | 필수 |

### GUIDE (사용자 가이드) — 2개

| # | 파일명 | 역할 | V1 |
|---|--------|------|-----|
| 67 | VAMOS_BEGINNER_GUIDE | 초보자 온보딩 가이드 | 참고 |
| 68 | CLAUDE.md | AI 에이전트 운영 규칙/SOT 참조 가이드 | 필수 |

**총 68개 파일** [근거: docs/sot/ 디렉토리 전수 확인]

---

## §47.2 문서 권위 체계

```
[1등급] RULE 1.3 ────── 절대 상위 (위반 시 무효)
   ↓
[2등급] PLAN 3.0 ────── 로드맵/비용/버전 정본
   ↓
[3등급] DESIGN 2.0 LOCK ── 설계 문서의 LOCK 블록
   ↓
[4등급] DESIGN 2.0 본문 ── 설계 문서 일반 내용
   ↓
[5등급] 스키마 문서 (D1~D8), TECH_STACK (A1)
```

> **충돌 해결 규칙**: 상위 문서가 항상 우선합니다. 예를 들어 D7 스키마와 RULE 1.3이 충돌하면 RULE 1.3을 따릅니다. [근거: D2.0-01 §0.3 LOCK, D2.1-D1 §0 정본 우선순위]

### 변경관리 규칙 (🔒 변경 불가)

| 규칙 | 내용 |
|------|------|
| 삭제 금지 | `[DEPRECATE]` + 대체 경로로만 처리 |
| 창작 금지 | SOT에 없는 내용 생성 불가 |
| Major 변경 | 07 Approval (승인) 필요 |

[근거: D2.0-01 §0.5 LOCK]

---

## §47.3 SOURCE_CONFLICT 해결 규칙

문서 간 충돌이 발견되면 아래 규칙으로 해결합니다:

| 충돌 유형 | 해결 방법 | 근거 |
|----------|----------|------|
| RULE vs DESIGN | RULE 우선 (하위 문서 수정) | §0.3 |
| DESIGN LOCK vs DESIGN 본문 | LOCK 블록 우선 | §0.3 |
| D# 스키마 vs DESIGN 서술 | D# 스키마 기준 (충돌 시 D# 수정) | D1 §3.3, AC-D1-005 |
| Registry 값 vs 타문서 | Registry SOT 소유 문서 우선 | D1 §4.1 |
| 네임스페이스 충돌 | EVX-*=Verify 전용, E-*=외부 전용, S-#=모듈 ID | D2.0-01 §0.6 LOCK |

[근거: D2.1-D1 §2.5, D2.0-01 §0.6 LOCK]

---

## §47.4 LOCK / FREEZE 값 전체 레지스트리

> LOCK(잠금)은 변경이 절대 불가능한 값이며, FREEZE(동결)은 특정 조건 없이 변경이 금지된 값입니다.

### 아키텍처 LOCK

| 항목 | LOCK 값 | 근거 |
|------|---------|------|
| 문서 우선순위 | RULE > PLAN > DESIGN LOCK > DESIGN > 스키마 | DEC-001 |
| LangChain import | 금지 (패턴만 참조) | DEC-002 |
| LangGraph | Agent Workflow 프레임워크 | MASTER_SPEC §17.1 |
| Monorepo 구조 | 확정 | MASTER_SPEC §17.1 |

### 핵심 엔진 LOCK

| 항목 | LOCK 값 | 근거 |
|------|---------|------|
| Decision Lock | locked=true 후 변경 불가 | 02 §3.2 |
| Gate 우회 | 불가능 (Policy→Cost→Approval→Evidence→SelfCheck 필수) | MASTER_SPEC §17.2 |
| Self-check 임계값 | P0:70, P1:75, P2:80 | MASTER_SPEC §17.2 |
| MCP 전송 | Streamable HTTP | DEC-017 |
| 코드 실행 격리 | Docker 샌드박스 필수 (30초) | 02 §1.3-A |

### 비용/안전 LOCK

| 항목 | LOCK 값 | 근거 |
|------|---------|------|
| V1 월 상한 | ₩40,000 ($30) | 07 §4.1 |
| V2 월 상한 | ₩93,000 ($70) | 07 §4.1 |
| V3 월 상한 | ₩266,000 ($200) | 07 §4.1 |
| Downshift 경고 | 80% | 07 §4.2 |
| Downshift 차단 | 100% | 07 §4.2 |
| RBAC 역할 | OWNER/ADMIN/OPERATOR/VIEWER | 07 §3.6 |
| Autonomy 기본 | L1 (SUPERVISED) | 07 §3.2.1 |
| Non-goal | 7개 절대 금지 | RULE 1.3 §2 |
| 불변 구역 | safety/cost/approval/non_goals/audit/retention/consent | RULE 1.3 |

### 데이터/인프라 LOCK

| 항목 | LOCK 값 | 근거 |
|------|---------|------|
| QoD 스케일 | 0.0~1.0 | DEC-010 |
| QoD 가중치 | relevance 0.30 + accuracy 0.25 + freshness 0.25 + completeness 0.20 | DEC-014 |
| Semantic Cache | cosine ≥ 0.95 | 06 §4.7 ADD-012 |
| Embedding V1 | BGE-M3 (로컬) / text-embedding-3-small (클라우드) | DEC-005 |
| Vector V1 | Chroma | A1 LOCK |
| tiktoken | cl100k_base 인코딩 | 02 §2.3-A |

### Self-evo / UI LOCK

| 항목 | LOCK 값 | 근거 |
|------|---------|------|
| Self-evo 원칙 | 제안만, 자동 적용 절대 금지 | MASTER_SPEC §17.5 |
| Self-evo 롤백 | 동일 제안 14일 재적용 금지 | MASTER_SPEC §17.5 |
| UI 프레임워크 | Tauri 2.0 + React | DEC-053, MASTER_SPEC §17.6 |
| 비용 경고 색상 | 80%=#FBBF24(노란), 100%=#EF4444(빨간) | DEC-015 |

[근거: MASTER_SPEC §17.1~17.6]

---

## §47.5 ★DEC 결정사항 통합 인덱스 (GAP-14)

> DEC(Decision) 결정사항은 VAMOS 아키텍처의 핵심 설계 결정으로, 모두 LOCK 상태입니다.

| DEC ID | 제목 | 결정 내용 | 상태 |
|--------|------|----------|------|
| DEC-001 | 문서 우선순위 | RULE > PLAN > DESIGN LOCK > DESIGN > 스키마 | 🔒 FREEZE |
| DEC-002 | LangChain 의존 방식 | import 금지, 패턴만 참조. Allowlist: langchain-core/community/openai만 | 🔒 FREEZE |
| DEC-003 | 도구 승인 Allowlist | 읽기전용=자동, 외부API/쓰기/실행=확인 필요 | 🔒 LOCK |
| DEC-004 | GraphRAG 아키텍처 | 하이브리드 RAG: V1=Basic 64%+, V2=Hybrid 83%+, V3=Self-RAG 90%+ | 🔒 LOCK |
| DEC-005 | Embedding 모델 | V1=BGE-M3(로컬,1024dim) / text-embedding-3-small(클라우드) | 🔒 UPDATED |
| DEC-006 | D4 Infra Catalog | 별도 카탈로그 삭제, D2.0-04 §4로 통합 | ✅ 구현 |
| DEC-010 | QoD 스케일 | 0.0~1.0 범위 확정 | 🔒 LOCK |
| DEC-011 | P2 재확인 UI | 모달 방식 확정 | 🔒 LOCK |
| DEC-014 | QoD 가중치 | relevance 0.30 + accuracy 0.25 + freshness 0.25 + completeness 0.20 | 🔒 LOCK |
| DEC-015 | 비용 경고 색상 | 80%=#FBBF24(노란), 100%=#EF4444(빨간) | 🔒 LOCK |
| DEC-016 | I-10 UI 오케스트레이션 | D2.0-08 §4.4 정본 | ✅ 구현 |
| DEC-017 | MCP 전송 계층 | Streamable HTTP 기본값. SSE deprecated | 🔒 LOCK |
| DEC-019 | HW 선택 기준 및 TCO | D2.0-04 §4.3.6 정본 | ✅ 구현 |

[근거: MASTER_SPEC §17, CLAUDE.md DEC 목록]

---

## §47.6 ★ADD-xxx 항목 전수 인덱스 & 매핑 (GAP-17)

> ADD 항목은 DESIGN 문서(D2.0-01~08)에 산재한 구현 추가사항입니다.

### D2.0-02 ORANGE CORE ADD 항목 (주요)

| ADD ID | 제목 | 버전 | 상태 |
|--------|------|------|------|
| ADD-001 | Runnable 프로토콜 | V1 | 미구현 |
| ADD-010 | 비용 절감 전략 | V1+ | 미구현 |
| ADD-012 | Semantic Cache (cosine ≥ 0.95) | V1 | 미구현 |
| ADD-013~015 | 4-Layer Guardrails 방어 설계 | V1+ | 미구현 |
| ADD-014 | 프롬프트 주입 방어 | V1 | 미구현 |
| ADD-028 | MCP 우선 전략 | V1 | 미구현 |
| ADD-036b | Pydantic 스키마 전수 검증 | V1 | 미구현 |
| ADD-037b | Function Call 에러 처리 | V1 | 미구현 |
| ADD-038 | tiktoken 연동 | V1 | 미구현 |
| ADD-052 | Chat Engine 재설계 | V1+ | 미구현 |
| ADD-069 | LangChain 제거 후 경량 대안 | V1 | ✅ 구현 |
| A-ADD-08 | Structured Outputs 강화 | V1 | 미구현 |
| S03-ADD-001 | Decision Audit Trail API | V1 | 미구현 |
| S03-ADD-006 | Multi-Brain Failover | V1 | 미구현 |

### D2.0-04 INFRA CORE ADD 항목

| ADD ID | 제목 | 버전 | 상태 |
|--------|------|------|------|
| ADD-039 | 동적 모델 라우팅 | V1 | 미구현 |
| ADD-041 | Batch API 스케줄러 | V1 | 미구현 |
| ADD-059 | 비용/로그 통합 스키마 | V1 | 미구현 |

### D2.0-05 AGENT WORKFLOW ADD 항목

| ADD ID | 제목 | 버전 | 상태 |
|--------|------|------|------|
| ADD-009 | Agent Mode 열거형 | V1 | 미구현 |
| ADD-024~027 | Agent 3요소/통신/코딩/프로파일링 | V1 | 미구현 |
| ADD-044 | Walk-Forward Validation | V1+ | 미구현 |
| ADD-061~064 | 프롬프트 라이브러리/최적화/버전관리/A-B 테스트 | V1 | 미구현 |
| ADD-072 | Circuit Breaker 패턴 | V1 | 미구현 |
| ADD-075~077 | V2 Autonomous Agent / GroupChat / Crew | V2 | 미구현 |

### D2.0-06 STORAGE MEMORY ADD 항목

| ADD ID | 제목 | 버전 | 상태 |
|--------|------|------|------|
| ADD-006 | 한국어 RAG 최적화 | V1+ | 미구현 |
| ADD-053~056 | 메모리 시스템 전면 재설계 | V1 | 미구현 |

### D2.0-07 SAFETY ADD 항목

| ADD ID | 제목 | 버전 | 상태 |
|--------|------|------|------|
| ADD-060 | COST_APPROVAL 워크플로우 | V1 | 미구현 |
| ADD-074 | Self-evo 롤백 메커니즘 | V1 | 미구현 |

### D2.0-08 UI/UX ADD 항목

| ADD ID | 제목 | 버전 | 상태 |
|--------|------|------|------|
| ADD-016 | CLI Layer | V1 | 미구현 |
| ADD-050 | Hologram 이벤트 네임스페이스 | V1 | 미구현 |
| ADD-081 | V1=Streamlit / V2=Loki-lite / V3=Grafana | V1~V3 | 미구현 |

### 통계 요약

| 분류 | V1 | V2 | V3 | 합계 |
|------|-----|-----|-----|------|
| 총 ADD 항목 | ~52 | ~15 | ~5 | ~74 |
| 구현 완료 | 1 | 0 | 0 | 1 |
| 미구현 | ~51 | ~15 | ~5 | ~73 |

[근거: D2.0-01~08 전수 검색, MASTER_SPEC §17]

### 핵심 요약 (3줄)
1. VAMOS는 68개 정본 문서 체계로, RULE > PLAN > DESIGN > 스키마 위계를 따릅니다.
2. 13개 DEC 결정사항과 74+ ADD 구현항목이 전 문서에 걸쳐 관리됩니다.
3. LOCK/FREEZE 값은 비용 상한, Self-check 임계값, MCP 전송 등 핵심 설계를 보호합니다.

---

# §48. 용어집 (Glossary)

> VAMOS에서 사용하는 핵심 용어를 영문 알파벳 순으로 정리합니다. 각 용어의 정의는 D2.1-D1 Glossary(정본)와 MASTER_SPEC에 근거합니다.

| # | 영문 용어 | 한글 설명 | 관련 섹션 |
|---|----------|----------|----------|
| 1 | A2A (Agent-to-Agent) | 에이전트 간 통신 프로토콜 (Google 주도 표준) | §26, §44 |
| 2 | Acceptance Criteria | 검증 기준 — 각 문서/스키마가 충족해야 할 최소 요건 | §45 |
| 3 | ADD (Implementation Item) | 설계 문서에 명시된 구현 추가 사항 | §47.6 |
| 4 | Approval | 승인 객체 — 계획/실행 2단계 승인 (plan / execute) | §20, §45.6 |
| 5 | Artifact | 실행 단계 산출물 (코드/문서/데이터/차트 등) | §10, §45.7 |
| 6 | Autonomy Level | 자율 운영 수준 — L0(수동)~L3(완전자율) | §20, §45.6 |
| 7 | BGE-M3 | V1 기본 임베딩 모델 (다국어, 1024차원, 무료) | §24, §46.1 |
| 8 | BLUE NODE | 도메인 실행 모듈 — CORE 규칙을 상속하며 독립 실행 불가 | §5~§8, §45.2 |
| 9 | Brain Adapter | LLM/도구를 표준 인터페이스로 감싸는 어댑터 | §12, §45.3 |
| 10 | Circuit Breaker | 연속 실패 시 자동 차단/복구 패턴 | §10, §45.4 |
| 11 | CostBudget | 비용 예산 객체 — 일/월 상한 + 사용량 추적 | §20, §45.6 |
| 12 | CRAG | Corrective RAG — 검색 결과 보정 (웹 검색 폴백 포함) | §24 |
| 13 | DEC (Decision Item) | 아키텍처 핵심 설계 결정 (LOCK/FREEZE 상태) | §47.5 |
| 14 | Decision | 한 시점·한 컨텍스트·한 결론을 불변 객체로 고정한 판단 결과 | §3, §45.1 |
| 15 | Docker Sandbox | 코드 실행 격리 환경 (신뢰 불가 코드 안전 실행) | §12 |
| 16 | Downshift | 비용 상한 근접 시 저비용 모델로 전환 (80% 경고 / 100% 차단) | §20, §45.6 |
| 17 | Evidence | 근거 — 내부/외부 소스에서 수집한 데이터 | §3, §45.1 |
| 18 | EvidencePack | Evidence 집합 + QoD 메타 (검색/근거 번들) | §3 |
| 19 | EVX (Verify Extension) | 검증 확장 모듈 (EVX-1~EVX-6) | §10, §45.4 |
| 20 | Failure | 실패 — 코드화되어 FailureCodeRegistry에 등록 | §45.1 |
| 21 | Fallback | 실패 시 대체 경로 (FallbackRegistry 코드로 관리) | §45.1 |
| 22 | Front Mini | CORE 최전방 게이트 모듈 — 빠른 의도 분류 (경량 LLM) | §3 |
| 23 | Gate | 정책/승인/비용 검문 지점 (Policy / Approval / Cost Gate) | §10, §45.4 |
| 24 | GraphRAG | Knowledge Graph + RAG 결합 검색 | §24, §45.5 |
| 25 | Guardrails (4-Layer) | NeMo + Guardrails AI + LlamaGuard + Post-Delivery Audit 4층 방어 체계 | §20, §45.6 |
| 26 | HITL | Human-in-the-Loop — 자동화 중 사람 개입 메커니즘 | §10, §45.4 |
| 27 | IntentFrame | 의도 해석 결과 객체 (I-1 산출물) | §3 |
| 28 | LOCK | 변경 불가 값/규칙 — 설계 결정으로 확정된 불변 항목 | §47.4 |
| 29 | LogEvent | 모든 이벤트 기록 단위 (event_type으로 분류) | §45.1 |
| 30 | MCP | Model Context Protocol — 단일 도구 연결 표준 | §8, §45.2 |
| 31 | Memory (L0~L3) | L0=세션 / L1=프로젝트 / L2=장기지식 / L3=절차 메모리 | §15, §45.5 |
| 32 | Neo4j | V2+ Knowledge Graph 데이터베이스 | §24 |
| 33 | Non-goal | 절대 금지 항목 (7개) — 위반 시 즉시 차단 | §1 |
| 34 | ORANGE CORE | 중앙 사령탑 — 모든 판단·정책·비용·승인 총괄 | §3~§4, §45.1 |
| 35 | P0/P1/P2 | P0=핵심(안전) / P1=확장(일반) / P2=위험(승인 필수) 도메인 | §5 |
| 36 | PolicyCheck | 정책 검사 결과 (deny / restrict / allow + 근거) | §20, §45.6 |
| 37 | Pydantic v2 | 스키마 검증 표준 (BaseModel 기반, 전수 검증 의무) | §45 |
| 38 | Qdrant | V2+ 기본 벡터 데이터베이스 (서버 모드) | §24, §46.1 |
| 39 | QoD | Quality of Data — 관련성+정확성+최신성+완전성 가중 평균 | §15, §45.5 |
| 40 | RBAC | Role-Based Access Control — 역할 기반 접근 제어 | §20, §45.6 |
| 41 | REF-only | 타 문서에서 참조만 가능 (재정의 금지) | §47.2 |
| 42 | Registry | 코드값 목록의 정본 — SOT 소유 문서에서만 확정 | §45.1 |
| 43 | Run | 단일 실행 단위 (session_id 범위) | §10 |
| 44 | Runnable | 모듈 간 통신 프로토콜 (invoke/ainvoke/stream/batch) | §3 |
| 45 | SDAR | Self-Diagnosis & Auto-Repair — 자가진단 및 자동복구 | §37 |
| 46 | Self-evo | 자기 진화 모듈 (S-1~S-8) — 제안만 가능, 자동 적용 금지 | §29~§30 |
| 47 | Self-RAG | 자기 평가 루프 RAG — 생성 결과를 자체 검증 | §24 |
| 48 | Semantic Cache | 의미 기반 캐시 — 유사 질문 재활용 (cosine ≥ 0.95) | §24, §45.5 |
| 49 | SOT | Source of Truth — 정본 (해당 항목의 유일한 권위 문서) | §47 |
| 50 | Streamable HTTP | MCP 전송 계층 표준 (stdio → Streamable HTTP 전환) | §8, §45.2 |
| 51 | Tauri | V1 데스크톱 앱 프레임워크 (Rust + React, ~30MB) | §22, §46 |
| 52 | tiktoken | 토큰 카운팅 표준 라이브러리 (cl100k_base 인코딩) | §12, §46.1 |
| 53 | ToolCall | 도구 호출 단위 — ToolRegistry 경유 실행 | §12, §45.3 |
| 54 | Trace | 모든 요청에 trace_id를 부여하여 디버깅/감사 가능 | §3 |
| 55 | VamosError | 표준 에러 처리 인터페이스 (error_code + message + context) | §3 |
| 56 | Workflow | Agent 실행 흐름 — 표준 5단계 (Intake→Plan→Execute→Verify→Deliver) | §10, §45.4 |

[근거: D2.1-D1 §1.2 Glossary, MASTER_SPEC §1~§17]

### 핵심 요약 (3줄)
1. VAMOS 용어집은 56개 핵심 용어를 영문 알파벳 순으로 정리합니다.
2. 용어 정의의 정본은 D2.1-D1(SCHEMA_GLOSSARY)이며, 타 문서는 사용만 허용됩니다.
3. 새 용어가 필요하면 반드시 D1에 먼저 추가한 후 타 문서에서 REF-only로 참조합니다.

---

# §49. 자주 묻는 질문 (FAQ)

## Q1. VAMOS AI를 사용하려면 GPU가 필요한가요?

**A**: V1(로컬 MVP)에서는 **CPU만으로도 사용 가능**합니다. 기본 임베딩 모델(BGE-M3)은 CPU에서도 동작하며, LLM은 외부 API(GPT-4o mini)를 호출합니다. 다만, LlamaGuard(Layer 3 안전 분류)를 로컬에서 실행하려면 GPU가 필요하며, 이는 V2+에서 선택사항입니다. [근거: PHASE_B3 §4.2 NOTE, §5.1]

## Q2. V1부터 시작해도 되나요?

**A**: 네, **V1부터 시작하는 것이 권장됩니다**. V1은 최소 기능 제품(MVP)으로, 월 ₩40,000 이내 비용으로 핵심 기능을 체험할 수 있습니다. V0(기본 구조만 구축) → V1(MVP) → V2(서버) → V3(엔터프라이즈) 순서로 진화합니다. [근거: MASTER_SPEC §16]

## Q3. VAMOS는 실제 주식 거래를 할 수 있나요?

**A**: **절대 불가능합니다.** VAMOS의 7개 Non-goal 중 첫 번째가 "실거래/주문/계좌/API 연동 금지"입니다. 분석 보조만 가능하며, 실거래 요청 시 즉시 거부됩니다. Paper Trading(모의 투자)만 허용됩니다. [근거: RULE 1.3 §2.1, MASTER_SPEC §1.4]

## Q4. 비용이 얼마나 드나요?

**A**: 버전별 월 비용 상한이 LOCK되어 있습니다:
- **V1**: ₩40,000/월 ($30) — 로컬 MVP
- **V2**: ₩93,000/월 ($70) — 서버 환경
- **V3**: ₩266,000/월 ($200) — 엔터프라이즈

80% 도달 시 경고 + Mini 모델 강제, 100% 도달 시 자동 차단됩니다. [근거: D2.1-D7 §4.3, §4.4, 07 §4.1~4.2 LOCK]

## Q5. ORANGE CORE와 BLUE NODE의 차이는 무엇인가요?

**A**: **ORANGE CORE**는 "본부장"으로, 모든 판단·정책·비용·승인을 총괄합니다. **BLUE NODE**는 "현장 팀원"으로, 코딩/리서치/투자분석 등 특정 도메인 작업을 실행합니다. BLUE NODE는 CORE의 지시 없이 독립 실행할 수 없습니다. [근거: RULE 1.3 §4.1~4.2, MASTER_SPEC §2.2]

## Q6. 스키마 문서가 8개(D1~D8)나 되는데, 꼭 다 알아야 하나요?

**A**: 일반 사용자는 알 필요 없습니다. 스키마는 개발자가 구현할 때 참조하는 "데이터 설계도"입니다. 초보자는 D1(용어집)과 D2(ORANGE CORE — Decision/LogEvent)만 이해하면 충분합니다. [근거: D2.1-D1 §0]

## Q7. MCP가 뭔가요?

**A**: **MCP(Model Context Protocol)**는 AI 모델이 외부 도구를 호출하는 "표준 통신 규격"입니다. USB가 다양한 기기를 하나의 포트로 연결하듯, MCP는 웹 검색·문서 파싱·코드 실행 등 다양한 도구를 하나의 프로토콜로 연결합니다. VAMOS는 Streamable HTTP 방식을 사용합니다. [근거: D2.0-03 §6.4.1, DEC-017 LOCK]

## Q8. Self-check과 Self-evo의 차이는?

**A**: **Self-check**(자기검증)은 매번 답변을 내놓기 전에 "이 답이 맞는지" 확인하는 것입니다. **Self-evo**(자기진화)는 시스템 자체가 "이 프롬프트를 개선하자" 같은 개선 제안을 하는 것입니다. Self-evo는 제안만 가능하며 자동 적용은 절대 금지됩니다. [근거: MASTER_SPEC §11, §17.5 LOCK]

## Q9. V1에서 사용할 수 있는 LLM은 무엇인가요?

**A**: V1에서는 **Ollama(로컬 LLM)** + **GPT-4o mini(OpenAI API)**를 기본으로 사용합니다. Claude(Anthropic)는 V2+에서 추가됩니다. 비용 절감을 위해 간단한 작업은 Mini 모델, 복잡한 작업만 Main 모델을 사용합니다. [근거: PHASE_B3 §5.1, MASTER_SPEC §15]

## Q10. Pydantic v2란 무엇이고 왜 중요한가요?

**A**: **Pydantic v2**는 파이썬에서 데이터의 타입과 형식을 자동으로 검증해주는 라이브러리입니다. VAMOS에서는 모든 내부 데이터(Decision, LogEvent 등)가 Pydantic 모델로 정의되어 있어서, 잘못된 데이터가 시스템에 들어오는 것을 원천 차단합니다. [근거: D2.0-02 ADD-036b, PHASE_B3 §4.1]

## Q11. 비용이 100%를 초과하면 어떻게 되나요?

**A**: **자동으로 차단됩니다.** 승인 없이는 어떤 LLM 호출도 실행되지 않습니다. 80% 도달 시에는 경고와 함께 Mini 모델(저비용)로 강제 전환되고, 100% 초과 시에는 완전 차단됩니다. 계속 사용하려면 사용자가 직접 승인(Approval)을 해야 합니다. [근거: D2.1-D7 §4.4, 07 §4.2 LOCK]

## Q12. RBAC에서 VIEWER 역할은 무엇을 할 수 있나요?

**A**: **VIEWER**는 읽기 전용 역할입니다. 시스템 상태, 로그, 비용 현황을 조회할 수 있지만, 실행·설정 변경·승인은 불가합니다. OWNER > ADMIN > OPERATOR > VIEWER 순서로 권한이 줄어듭니다. [근거: D2.1-D7 §4.6, 07 §3.6 LOCK]

## Q13. 메모리 L0~L3의 차이는 무엇인가요?

**A**:
- **L0 (세션 메모리)**: 현재 대화 중에만 유지, 대화 종료 시 삭제
- **L1 (프로젝트 메모리)**: 프로젝트 단위 기억, 기본 90일 보관
- **L2 (장기 지식)**: 학습된 지식, 무기한 보관
- **L3 (절차 메모리)**: "이런 상황에서는 이렇게 하라"는 절차 기억

[근거: D2.1-D6 §4.1, 06 §2.1 LOCK]

## Q14. 39개 문서를 다 읽어야 하나요?

**A**: **아닙니다.** 초보자는 이 가이드(BEGINNER_GUIDE)만 읽으면 됩니다. 개발자는 MASTER_SPEC(통합 요약) 한 문서를 먼저 읽고, 구현할 부분의 DESIGN/SCHEMA/PHASE 문서를 참조하면 됩니다. [근거: MASTER_SPEC §0]

## Q15. Non-goal이 7개라는데, 전부 알려주세요.

**A**: ①실거래/주문 금지 ②불법행위/해킹 금지 ③의료/법률 단정 금지 ④민감 개인정보 장기 저장 금지 ⑤저작권/약관 위반 금지 ⑥P2 도메인 자동 생성 금지 ⑦위험 기능 자동 실행 금지. 이 7가지는 절대 변경할 수 없는 불변 구역입니다. [근거: RULE 1.3 §2, MASTER_SPEC §1.4]

## Q16. Tauri가 Electron보다 나은 이유는?

**A**: **번들 크기가 ~30MB로 Electron(~150MB)의 1/5 수준**이며, Rust 백엔드 덕분에 메모리 사용량과 성능이 훨씬 우수합니다. 보안 면에서도 Tauri 2.0의 capabilities 기반 권한 관리가 더 세밀합니다. [근거: D2.1-D8 §6-A.1, STEP7 S7C-053]

## Q17. GraphRAG는 V1에서도 사용되나요?

**A**: V1에서는 **간이 버전(P1-SCOPE)**으로 JSON 파일 기반 Graph를 사용합니다. V2+에서 Neo4j 기반 본격 GraphRAG가 도입됩니다. V1에서도 기본 RAG(64%+ 정확도 목표)는 지원됩니다. [근거: D2.1-D6 §4.4, DEC-004]

## Q18. Circuit Breaker가 왜 필요한가요?

**A**: 특정 도구/API가 연속으로 실패하면 계속 재시도하는 대신 **자동으로 차단**(Open 상태)하여 시스템 전체 장애를 방지합니다. 일정 시간(recovery_time) 후 시험 호출(Half-Open)을 하여 복구 여부를 확인합니다. [근거: D2.1-D5 §4.6, 05 §4.x]

## Q19. SOT(Source of Truth)가 무엇인가요?

**A**: **SOT(정본)**는 "이 항목에 대해 유일하게 권위 있는 문서"를 뜻합니다. 예를 들어 EventTypeRegistry의 SOT는 D2이므로, 이벤트 타입 코드값은 D2에서만 추가/변경할 수 있고, 다른 문서는 참조만(REF-only) 가능합니다. [근거: D2.1-D1 §1.1, §4.1]

## Q20. VAMOS를 처음 시작하려면 어떤 순서로 설치하나요?

**A**: ①Node.js + npm 설치 → ②Rust + Cargo 설치 → ③Python 3.11+ 설치 → ④`git clone` 후 `npm install` (프론트) → ⑤`cargo build` (Rust 백엔드) → ⑥`pip install` (Python AI/ML) → ⑦`.env` 환경변수 설정 (API 키) → ⑧`tauri dev`로 개발 서버 실행. 자세한 내용은 PHASE_B2(프로젝트 구조)와 PHASE_B3(의존성)을 참조하세요. [근거: PHASE_B3 §1.2, PHASE_B2]

---

### 핵심 요약 (3줄)
1. GPU 없이도 V1 사용 가능, 비용은 V1 기준 월 ₩40,000 이내입니다.
2. 실거래 절대 금지, Self-evo 자동 적용 금지 등 7개 Non-goal은 불변입니다.
3. 초보자는 이 가이드만 읽으면 되며, 개발자는 MASTER_SPEC부터 시작하세요.
