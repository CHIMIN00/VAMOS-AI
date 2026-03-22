FN AUDIT RESULTS
================
Total MATCHED samples: 30

FN FOUND (MATCHED but actually MISSING):
# | feature_id | feature_name | cited_line | problem | reason
1 | v12_C01b_122 | API RBAC Authorization Matrix | L1009 | different_feature | PART2 L1009 says "ApprovalGate: P2 감지 → hold" — this is about I-5 Decision Engine's ApprovalGate, NOT about an API RBAC Authorization Matrix. The SOT feature is a complete RBAC authorization matrix (§13), while the cited text describes a gate rule within the pipeline. L601 has "RBACRole" schema (6 fields) but L1009 does not cover an authorization matrix.
2 | v12_C02_003 | INFRA-CORE Architecture | L994 | different_feature | PART2 L994 is "V0-STEP-4: ORANGE CORE 최소 파이프라인 (Day 5-8)" — this is the ORANGE CORE pipeline section header, NOT INFRA-CORE Architecture. INFRA-CORE is a separate infrastructure layer (A-Series). The cited location describes I-Series (Intent) modules, not the infrastructure/common layer.
3 | v12_C02_091 | Module C-4 File Store | L1208 | different_feature | PART2 L1208 says "L0 Session Memory (SQLite)" — this is about V0-STEP-5 memory storage, NOT Module C-4 File Store. C-4 is a distinct verification/file-store module. L0 Session Memory is part of the I-3/memory subsystem, not C-4.
4 | v12_C10_050 | 5계층 통신 프로토콜 스택 | L196 | different_feature | PART2 L196 says "monorepo 초기화 (PHASE_B2 정본 기준)" — this is about project scaffolding/directory structure, NOT a 5-layer communication protocol stack. The SOT describes "통신 계층: React UI ↔ Tauri IPC ↔ Rust Backend ↔ JSON-RPC ↔ Python" which is a specific protocol stack architecture. The monorepo init section only shows directory layout.
5 | v12_C02_130 | EvidenceItem Schema | L579 | different_feature | PART2 L579 says "EvidencePack | 6 | D2.0-02 §7.2" — this is EvidencePack, NOT EvidenceItem. The SOT feature is specifically "EvidenceItem schema" which is a sub-schema within/different from EvidencePack. PART2 lists EvidencePack as a top-level schema but never mentions EvidenceItem as a distinct schema.
6 | v12_C05_001 | i18n 다국어 지원 시스템 | L2288 | too_generic | PART2 L2288 is an AI prompt summary listing "~44개 React 컴포넌트, 8개 Custom Hook, 7개 Zustand Store, i18n, 디자인 시스템" — i18n is mentioned only as a comma-separated list item in a prompt summary. No implementation guidance for the i18n system itself (locale management, key structure, fallback logic, etc.). The SOT describes "i18n 키로 관리하며 하드코딩 금지, 기본 ko-KR" which is specific guidance not found at the cited line.
7 | v12_C02_043 | Module I-18 Health Monitor | L2288 | different_feature | PART2 L2288 is "~44개 React 컴포넌트, 8개 Custom Hook, 7개 Zustand Store, i18n" — this is the Phase 4 UI/UX section. Module I-18 Health Monitor is an ORANGE CORE backend module, not a UI component. I-18 is never mentioned at or near L2288. The entire Phase 4 section is about frontend UI.
8 | v12_C01a_142 | Soft/Hard Loop Strategy | L2073 | too_generic | PART2 L2073 is an AI prompt summary for Phase 3: "V1-Phase 3 Workflow/Agent를 구현하세요..." — Soft/Hard Loop IS mentioned in the prompt text ("Soft/Hard Loop"), but only as a list item in the AI prompt summary. The actual implementation detail is at L2082 ("R1~R11 + ... Circuit Breaker recovery=60s LOCK + Agent max 2 Sub LOCK") and L1685-1686 has the specific guidance. L2073 itself is just a section-level prompt summary, not implementation guidance.
9 | v12_C09b_507 | CI/CD 파이프라인 | L2411 | too_generic | PART2 L2411 is an AI prompt summary: "V1-Phase 5 통합 테스트를 수행하세요. §6.3 테스트 ~85개..." — mentions CI/CD only as part of a broader Phase 5 summary. No specific CI/CD pipeline implementation guidance at this line. The SOT is "[S7F-001] CI/CD 파이프라인 | CRITICAL V1" which requires detailed pipeline design.
10 | v12_C06_014 | IntentType Literal 정의 (other 포함) | L578 | parent_module_only | PART2 L578 says "IntentFrame | 10 | D2.0-02 §7.1" — this is about the IntentFrame schema (parent model), NOT the specific IntentType Literal definition. IntentType is a field/sub-type within IntentFrame. The SOT specifically requires 'IntentType = Literal["query","action","creative","other"]' — PART2 never defines IntentType as a Literal with specific values including "other".
11 | v12_C02_027 | Module I-2 RAG Retriever | L1003 | different_feature | PART2 L1003 says "I-2 Context Builder (스텁)" — the SOT feature is "I-2 — RAG Retriever" but PART2 calls it "I-2 Context Builder" and only implements it as a stub (empty EvidencePack). While the module ID matches (I-2), the SOT names it as a RAG Retriever which implies full retrieval-augmented generation, whereas PART2 only provides a stub that returns empty results. The module name difference (Context Builder vs RAG Retriever) suggests different scope/functionality.
12 | v12_C09b_557 | PagedAttention / vLLM 최적화 | L3287 | different_feature | PART2 L3287 says "LlamaGuard (L3) | 4-Layer 중 3개 활성" — this is about LlamaGuard security layers, NOT PagedAttention/vLLM optimization. These are completely different features. PagedAttention is a memory-efficient attention mechanism for LLM inference, while LlamaGuard is a safety/guardrail system.
13 | v12_C06_074 | 금융 감성 분석 모델 | L2872 | different_feature | PART2 L2872 says "SHAP/LIME Explainability 모듈 (explainer.py)" — this is about model explainability (SHAP/LIME), NOT financial sentiment analysis. The SOT is "SentimentAnalysis: FinBERT 감성 분석 모델 (S13 AINV)" which is a specific FinBERT-based sentiment analysis model. SHAP/LIME and FinBERT sentiment are fundamentally different features.
14 | v12_C08_021 | HandoffPacket 인계 프로토콜 스키마 | L3284 | parent_module_only | PART2 L3284 says "6가지 협업 패턴 | Sequential/Parallel/Debate/Supervisor/Handoff/Hybrid" — this mentions "Handoff" as one of 6 collaboration patterns, NOT the HandoffPacket schema specifically. The SOT requires "class HandoffPacket(BaseModel): 에이전트 간 인계 패킷" — a specific Pydantic schema definition. The PART2 line only lists pattern names without defining the HandoffPacket schema.
15 | v12_C12_199 | 그래프 시각화 인터랙션 | L2309 | different_feature | PART2 L2309 says "WorkflowPage.tsx: Builder View 그래프 시각화" — this is about the Workflow page's graph visualization (pipeline DAG view), NOT PKM knowledge graph visualization interaction. The SOT is "M-034. 그래프 시각화 인터랙션" from the PKM/Knowledge Management guide, which is about interactive knowledge graph exploration, not workflow pipeline visualization.
16 | v12_C02_106 | Module EVX-6 Quality Dashboard | L3806 | different_feature | PART2 L3806 says "EVX-6 Multi-Objective Optimizer — 다목적 최적화 (품질/비용/속도 동시)" — the module ID matches (EVX-6), but PART2 names it "Multi-Objective Optimizer" while SOT names it "Quality Dashboard". These describe fundamentally different features: an optimization algorithm vs a monitoring/visualization dashboard. The notes field even acknowledges this discrepancy.

NOT FN (confirmed MATCHED):
# | feature_id | feature_name | cited_line | verification
1 | v12_C01b_169 | V0 Package Dependency List | L241 | Text at L241 directly lists package dependencies: "Python: poetry init → core dependencies", "Rust: cargo init → tauri, serde, tokio", "Node: pnpm init → react, @tauri-apps/api, zustand". This IS the V0 package dependency list.
2 | v12_C02_129 | ResponseEnvelope Schema | L582 | Text at L582 says "ResponseEnvelope | 5 (LOCK) | CLAUDE.md §12" — directly names the ResponseEnvelope schema with 5 locked fields. This is specific implementation guidance for the schema.
3 | v12_C02_167 | EvidenceGate Implementation | L1010 | Text at L1010 says "EvidenceGate: 스텁 (항상 sufficient)" — directly describes the EvidenceGate implementation (stub that always returns sufficient). This is specific implementation guidance.
4 | v12_C08_051 | contracts.py Pydantic 모델 정렬 | L574 | Text at L574 says "25개 Pydantic v2 핵심 모델 → backend/vamos_core/schemas/contracts.py" — directly references the contracts.py file with 25 Pydantic models. This covers the Pydantic model alignment feature.
5 | v12_C06_041 | WorkflowStageSchema 모델 | L597 | Text at L597 says "WorkflowStage | 4 (LOCK) | D2.1-D5" — directly names WorkflowStage with 4 locked fields. Matches the SOT feature.
6 | v12_C01b_103 | Autonomy Level Controller | L1811 | Text at L1811 says "I-1: autonomy_level V1 기본값 L2_COPILOT (PHASE_B4 §3.1 LOCK)" — directly describes autonomy level configuration, matching the SOT "§9 Autonomy L0-L3".
7 | v12_C12_261 | 인지행동 기반 셀프케어 (CBT) | L2200 | Text at L2200 says "CBT 셀프케어 (사고기록+인지왜곡)" — directly matches the SOT feature name "인지행동 기반 셀프케어". Specific feature with implementation guidance reference.
8 | v12_C09a_050 | MCP Tool Call 6단계 검증 파이프라인 | L2589 | Text at L2589 says "MCPClient.call_tool(server_url, tool_name, params) -> ToolResult" — this describes MCP tool call interface. While not explicitly a "6-step verification pipeline", it provides direct implementation guidance for MCP tool calls.
9 | v12_C12_083 | Multimodal Router (ORANGE CORE 확장) | L1678 | Text at L1678 says "I-4 Multimodal Interpreter → orange_core/i04_multimodal_interpreter.py" with details "텍스트/이미지/음성 입력 해석". This covers multimodal routing/interpretation in ORANGE CORE.
10 | v12_C03_039 | Search Engine Integration | L1801 | Text at L1801 says "I-16 | Knowledge Search Engine (지식 검색, RAG 통합)" — directly describes the search engine module matching the SOT "Search Engine Integration: Brave/Google/Tavily/Per...".
11 | v12_C09b_555 | MemGPT/Letta 패턴 적용 | L2878 | Text at L2878 says "MemGPT/Letta 패턴 통합" — exact name match with the SOT feature. Listed as a v23 expansion item in V2-Phase 2.
12 | v12_C01a_024 | Knowledge Graph Engine | L3724 | Text at L3724 says "그룹 3: I-24 Knowledge Graph Engine — Neo4j 기반 지식 그래프" with detailed I/O specs, function signatures, and dependencies. Excellent match.
13 | v12_C12_147 | 에이전트 마켓플레이스 | L3975 | Text at L3975 says "Agent Marketplace — 에이전트 탐색/설치/검증". Direct feature match.
14 | v12_C01b_088 | Agent Marketplace | L3975 | Text at L3975 says "Agent Marketplace — 에이전트 탐색/설치/검증". Direct feature match (same line as above, different SOT source).

FN COUNT: 16/30
FN RATE: 53.3%

================
DETAILED ANALYSIS NOTES
================

HIGH-CONFIDENCE FN (clearly wrong MATCHED judgment):
- v12_C02_043 (I-18 Health Monitor mapped to UI section) — completely wrong section
- v12_C09b_557 (PagedAttention mapped to LlamaGuard) — completely different feature
- v12_C06_074 (금융 감성분석 mapped to SHAP/LIME) — completely different feature
- v12_C02_003 (INFRA-CORE mapped to ORANGE CORE) — different architecture layer
- v12_C02_091 (C-4 File Store mapped to L0 Session Memory) — different module entirely
- v12_C10_050 (5-layer protocol stack mapped to monorepo init) — different feature entirely
- v12_C12_199 (PKM graph visualization mapped to workflow graph viz) — different domain

MEDIUM-CONFIDENCE FN (debatable but likely wrong):
- v12_C01b_122 (RBAC Matrix mapped to ApprovalGate) — related security area but wrong feature
- v12_C02_130 (EvidenceItem mapped to EvidencePack) — related but different schema
- v12_C06_014 (IntentType Literal mapped to IntentFrame) — sub-type vs parent model
- v12_C08_021 (HandoffPacket schema mapped to collaboration patterns list) — related but no schema detail
- v12_C02_027 (RAG Retriever mapped to Context Builder stub) — same module ID but different implementation scope/name
- v12_C02_106 (Quality Dashboard mapped to Multi-Objective Optimizer) — same EVX-6 ID but different feature name/function

BORDERLINE FN (might be acceptable as weak match):
- v12_C05_001 (i18n mapped to prompt summary mention) — i18n IS mentioned but zero implementation detail
- v12_C01a_142 (Soft/Hard Loop mapped to prompt summary) — feature IS referenced but at summary level
- v12_C09b_507 (CI/CD mapped to Phase 5 summary) — CI/CD IS referenced but at summary level
