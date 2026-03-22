#!/usr/bin/env python3
"""VAMOS v10 Phase 0-B: CLAUDE.md Feature Index Extraction (Layer 1)"""
import json

features = []
idx = [0]  # mutable counter

def add(src_line, section, name, version, cat, impl_type="신규구현",
        deps=None, extractable=True, confidence="명시적", notes=""):
    idx[0] += 1
    f = {
        "feature_id": f"CLAUDE-{idx[0]:03d}",
        "source_file": "CLAUDE",
        "source_line": src_line,
        "source_section": section,
        "feature_name": name,
        "version_scope": version,
        "category": cat,
        "implementation_type": impl_type,
        "dependencies": deps or [],
        "extractable": extractable,
        "confidence": confidence,
        "notes": notes
    }
    features.append(f)

# ============================================================
# §1 프로젝트 개요 (lines 8-16)
# ============================================================
add(11, "§1 프로젝트 개요", "4계층 아키텍처 프레임워크 구현 (Front Mini LLM → ORANGE CORE → BLUE NODES → OTHER BRAINS → Main LLM)", "V0,V1,V2,V3", "FT-FUNC")
add(13, "§1 프로젝트 개요", "통신 계층 구현 (React UI ↔ Tauri IPC ↔ Rust Backend ↔ JSON-RPC stdin/stdout ↔ Python AI/ML ↔ MCP Streamable HTTP)", "V0,V1", "FT-INFRA")
add(14, "§1 프로젝트 개요", "V0→V1→V2→V3 버전 전환 메커니즘 구현", "V0,V1,V2,V3", "FT-FUNC", notes="버전별 모듈 ON/OFF, 기술스택 전환, 비용상한 전환 포함")

# ============================================================
# §5 4계층 아키텍처 (lines 60-89)
# ============================================================
# 5-Phase Pipeline
add(72, "§5 5-Phase 파이프라인", "Phase 1: Perception/Intake 구현 (Front Mini + I-1 → IntentFrame, S0→S1)", "V0,V1", "FT-FUNC", deps=["CLAUDE-009"])
add(73, "§5 5-Phase 파이프라인", "Phase 2: Reasoning/Plan 구현 (I-2 + I-5 + Gates → EvidencePack + Decision, S2→S3)", "V1", "FT-FUNC", deps=["CLAUDE-010","CLAUDE-013"])
add(74, "§5 5-Phase 파이프라인", "Phase 3: Action/Execute 구현 (BLUE NODE + D4 → Artifacts/Results, S4→S5)", "V1", "FT-FUNC")
add(75, "§5 5-Phase 파이프라인", "Phase 4: Reflection/Verify 구현 (I-6 + EVX → Self-check 결과, S6)", "V1", "FT-FUNC", deps=["CLAUDE-014"])
add(76, "§5 5-Phase 파이프라인", "Phase 5: Memory/Store 구현 (I-3 + D6 → L0/L1/L2/L3 저장, S7→S8)", "V1", "FT-FUNC", deps=["CLAUDE-011"])

# 5 Gates
add(82, "§5 Gate 시스템", "PolicyGate 구현 (block/require_approval/mask/allow, S1~S3,S6)", "V1", "FT-FUNC", deps=["CLAUDE-016"])
add(83, "§5 Gate 시스템", "CostGate 구현 (normal/downshift/split/stop, S2~S4)", "V1", "FT-FUNC", deps=["CLAUDE-017"])
add(84, "§5 Gate 시스템", "ApprovalGate 구현 (approved/denied/pending/expired, S1~S3)", "V1", "FT-FUNC", deps=["CLAUDE-027"])
add(85, "§5 Gate 시스템", "EvidenceGate 구현 (sufficient/insufficient → HOLD/ESCALATE + 재검색, S2)", "V1", "FT-FUNC", deps=["CLAUDE-023"])
add(86, "§5 Gate 시스템", "SelfCheckGate 구현 (PASS/WARN/FAIL → Soft loop 1회, S5→S6)", "V1", "FT-FUNC", deps=["CLAUDE-014"])

# ============================================================
# §6 모듈 시스템 81개 (lines 92-206)
# ============================================================

# I-Series (I-1 ~ I-25)
i_modules = [
    (98,  "I-1",  "Intent Detector (대화 이해/추론)", "V1,V2,V3", "CORE"),
    (99,  "I-2",  "Context Builder (RAG/지식 검색)", "V1,V2,V3", "CORE"),
    (100, "I-3",  "Memory System (4계층: L0~L3)", "V1,V2,V3", "CORE"),
    (101, "I-4",  "Multimodal Interpreter", "V1,V2,V3", "CORE"),
    (102, "I-5",  "Condition & Decision Engine", "V1,V2,V3", "CORE(LOCK)"),
    (103, "I-6",  "Self-check Engine", "V1,V2,V3", "CORE"),
    (104, "I-7",  "Project/Session Manager", "V2,V3", "COND"),
    (105, "I-8",  "Policy Engine", "V1,V2,V3", "CORE(LOCK)"),
    (106, "I-9",  "Cost Manager", "V1,V2,V3", "CORE(LOCK)"),
    (107, "I-10", "Tool Registry/Router", "V1,V2,V3", "CORE"),
    (108, "I-11", "Output Composer", "V1,V2,V3", "CORE"),
    (109, "I-12", "Workflow Builder", "V2,V3", "COND"),
    (110, "I-13", "Multimodal Output Renderer", "V1,V2,V3", "CORE"),
    (111, "I-14", "Summarizer & Memory Distiller", "V1,V2,V3", "CORE"),
    (112, "I-15", "Evidence & QoD Manager", "V1,V2,V3", "CORE"),
    (113, "I-16", "Knowledge Search Engine", "V1,V2,V3", "CORE"),
    (114, "I-17", "Blue Node Manager", "V1,V2,V3", "CORE"),
    (115, "I-18", "Self-evo Engine", "V3", "EXP"),
    (116, "I-19", "Approval Manager", "V1,V2,V3", "CORE(LOCK)"),
    (117, "I-20", "Failure/Fallback Manager", "V1,V2,V3", "CORE"),
    (118, "I-21", "Source Evolution", "V3", "EXP"),
    (119, "I-22", "Task/Project Manager", "V2,V3", "COND"),
    (120, "I-23", "Doc/Code Structuring", "V2,V3", "COND"),
    (121, "I-24", "Knowledge Graph Engine", "V3", "EXP"),
    (122, "I-25", "SDAR Engine (자가진단/수리)", "V2,V3", "COND"),
]
for line, mid, name, ver, status in i_modules:
    add(line, "§6 I-Series", f"{mid} {name} 모듈 구현", ver, "FT-MOD",
        notes=f"status={status}")

# E-Series (E-1 ~ E-16)
e_modules = [
    (128, "E-1",  "Coding & System Design Helper", "V1,V2,V3"),
    (129, "E-2",  "Web Search", "V1,V2,V3"),
    (130, "E-3",  "Document Parser", "V1,V2,V3"),
    (131, "E-4",  "Code Executor", "V1,V2,V3"),
    (132, "E-5",  "Image Analyzer", "V1,V2,V3"),
    (133, "E-6",  "Z3 Solver", "V1,V2,V3"),
    (134, "E-7",  "Speech-to-Text", "V3"),
    (135, "E-8",  "Text-to-Speech", "V3"),
    (136, "E-9",  "Video Analyzer", "V3"),
    (137, "E-10", "External API Gateway", "V3"),
    (138, "E-11", "Browser Automation", "V3"),
    (139, "E-12", "DB Connector", "V3"),
    (140, "E-13", "Calendar/Task Sync", "V2,V3"),
    (141, "E-14", "Email Handler", "V2,V3"),
    (142, "E-15", "File System (V1) → Cloud Collector (V2+)", "V2,V3"),
    (143, "E-16", "Cloud Storage Sync", "V2,V3"),
]
for line, mid, name, ver in e_modules:
    add(line, "§6 E-Series", f"{mid} {name} 모듈 구현", ver, "FT-MOD")

# S-Series (S-1 ~ S-8)
s_modules = [
    (149, "S-1", "Self-check Engine", "V1,V2,V3", "I-6, I-15"),
    (150, "S-2", "Benchmark QA Suite", "V3", "I-24"),
    (151, "S-3", "Template Evolution", "V3", "I-12, I-18"),
    (152, "S-4", "Error Pattern Miner", "V3", "I-20, I-18"),
    (153, "S-5", "Router Evolution → Cloud Evolver", "V3", "I-10, I-18"),
    (154, "S-6", "Search Evolution", "V3", "I-16, I-18"),
    (155, "S-7", "User-Coop Designer", "V3", "I-19, I-18"),
    (156, "S-8", "Self-evo Governance", "V3", "I-19, I-8, I-9, I-24"),
]
for line, mid, name, ver, i_conn in s_modules:
    add(line, "§6 S-Series", f"{mid} {name} 모듈 구현", ver, "FT-MOD",
        notes=f"I-연결: {i_conn}")

# A-Series (A-1 ~ A-7)
a_modules = [
    (162, "A-1", "MultiBrain Adapter", "V1,V2,V3"),
    (163, "A-2", "Preset Modularization", "V1,V2,V3"),
    (164, "A-3", "Meta AI", "V3"),
    (165, "A-4", "Debate Mode", "V2,V3"),
    (166, "A-5", "Lazy Generation", "V3"),
    (167, "A-6", "Federated Module Network (LOCK)", "V3"),
    (168, "A-7", "Remote Executor (LOCK)", "V3"),
]
for line, mid, name, ver in a_modules:
    add(line, "§6 A-Series", f"{mid} {name} 모듈 구현", ver, "FT-MOD")

# B-Series (B-1 ~ B-6)
b_modules = [
    (174, "B-1", "Skill Library (스킬 라이브러리)", "V3", "EXP"),
    (175, "B-2", "Procedural Memory (방법론 메모리)", "V3", "EXP"),
    (176, "B-3", "Memory Decay (망각/감쇠)", "V1,V2,V3", "CORE"),
    (177, "B-4", "Auto Curriculum Generator", "V3", "EXP"),
    (178, "B-5", "RL-like Self Trainer", "V3", "EXP"),
    (179, "B-6", "DSPy Prompt Optimizer", "V3", "EXP"),
]
for line, mid, name, ver, status in b_modules:
    add(line, "§6 B-Series", f"{mid} {name} 모듈 구현", ver, "FT-MOD",
        notes=f"status={status}")

# C-Series (C-1 ~ C-7)
c_modules = [
    (185, "C-1", "Logic Verifier", "V1,V2,V3", "CORE"),
    (186, "C-2", "Math Verifier", "V1,V2,V3", "CORE"),
    (187, "C-3", "Code Verifier", "V1,V2,V3", "CORE"),
    (188, "C-4", "Domain Simulator", "V3", "EXP"),
    (189, "C-5", "Bayesian Belief Engine", "V3", "EXP"),
    (190, "C-6", "RL Advisor", "V3", "EXP"),
    (191, "C-7", "GNN Score Model", "V3", "EXP"),
]
for line, mid, name, ver, status in c_modules:
    add(line, "§6 C-Series", f"{mid} {name} 모듈 구현", ver, "FT-MOD",
        notes=f"status={status}")

# D-Series (D-1 ~ D-6)
d_modules = [
    (197, "D-1", "Think Engine", "V1,V2,V3", "CORE"),
    (198, "D-2", "Multimodal Engine", "V1,V2,V3", "CORE"),
    (199, "D-3", "Long Horizon Planner", "V3", "EXP"),
    (200, "D-4", "Personality/Tone Engine", "V3", "EXP"),
    (201, "D-5", "General Brain (Parallel)", "V3", "EXP"),
    (202, "D-6", "GraphRAG / Hybrid RAG", "V3", "EXP"),
]
for line, mid, name, ver, status in d_modules:
    add(line, "§6 D-Series", f"{mid} {name} 모듈 구현", ver, "FT-MOD",
        notes=f"status={status}")

# EVX-1 ~ EVX-6
evx_items = [
    ("EVX-1", "Code-as-Policy 검증"),
    ("EVX-2", "Adversarial 검증"),
    ("EVX-3", "Log-prob Confidence 검증"),
    ("EVX-4", "Thought Buffer 검증"),
    ("EVX-5", "Gen-Verify-Learn 검증"),
    ("EVX-6", "Z3 Solver Routing 검증"),
]
for evx_id, evx_name in evx_items:
    add(204, "§6 EVX", f"{evx_id} {evx_name} 구현", "V1,V2,V3", "FT-FUNC",
        confidence="추론", notes="CLAUDE.md §6에 한 줄 언급. 상세는 D2.0-02 참조. 버전은 추론(V1 기본 포함 가정)")

# STEP7 참조
add(205, "§6 STEP7", "STEP7 16개 카테고리(A~P) 3,101건 AI기술보강 반영", "V1,V2,V3", "FT-DOMAIN",
    extractable=False, confidence="추론", notes="STEP7 상세는 개별 SRC 파일에서 추출. CLAUDE.md에서는 메타 참조만")

# ============================================================
# §7 LOCK 결정사항 (lines 209-293)
# ============================================================

# 7.1 아키텍처 LOCK
add(216, "§7.1 아키텍처 LOCK", "LangChain Allowlist 적용 (langchain-core/community/openai adapter만 허용, 본체 import 금지)", "V1", "FT-CFG", impl_type="설정")
add(217, "§7.1 아키텍처 LOCK", "도구 승인 Allowlist 구현 (읽기전용=자동, 외부API/쓰기/코드실행=확인 필요)", "V1", "FT-SEC")
add(218, "§7.1 아키텍처 LOCK", "MCP Streamable HTTP 전송 구현", "V1", "FT-INFRA")
add(224, "§7.1 아키텍처 LOCK", "LangGraph Agent Workflow 프레임워크 통합", "V1", "FT-INFRA")
add(225, "§7.1 아키텍처 LOCK", "config.toml 설정 포맷 구현", "V0", "FT-CFG", impl_type="설정")

# 7.2 핵심 엔진 LOCK
add(231, "§7.2 핵심 엔진 LOCK", "Decision Lock 구현 (한 시점/한 컨텍스트/한 결론 → locked=true, S3 이후 변경불가)", "V1", "FT-FUNC")
add(233, "§7.2 핵심 엔진 LOCK", "Self-check 임계값 적용 (P0:70, P1:75, P2:80)", "V1", "FT-CFG", impl_type="설정")
add(234, "§7.2 핵심 엔진 LOCK", "Self-check 루프 구현 (Soft loop 자동 1회만, 이후 승인 필요)", "V1", "FT-FUNC")
add(235, "§7.2 핵심 엔진 LOCK", "L2 저장 정책 구현 (기본 승인 필요)", "V2", "FT-FUNC")
add(236, "§7.2 핵심 엔진 LOCK", "코드 실행 Docker 샌드박스 구현 (네트워크 차단, 30초 제한)", "V1", "FT-INFRA")
add(237, "§7.2 핵심 엔진 LOCK", "동시성 제한 구현 (MAX_CONCURRENT_BLUE_NODES=3, TOOLS=5)", "V1", "FT-CFG", impl_type="설정")
add(238, "§7.2 핵심 엔진 LOCK", "Multi-Brain Failover 구현 (GPT-4o→Claude→Ollama, 3회 타임아웃 시 전환)", "V1", "FT-FUNC")
add(239, "§7.2 핵심 엔진 LOCK", "대화 턴 상한 구현 (P0=5, P1=10, P2=20)", "V1", "FT-FUNC")
add(240, "§7.2 핵심 엔진 LOCK", "TEE 최대 반복 구현 (P0=3회, P1=5회, P2=10회)", "V1", "FT-FUNC")

# 7.3 비용/안전 LOCK
add(246, "§7.3 비용/안전 LOCK", "V1 비용 엔진 구현 (₩40,000/월, ₩1,300/일, Mini 90%+)", "V1", "FT-FUNC")
add(249, "§7.3 비용/안전 LOCK", "Downshift 로직 구현 (80% warn/force_mini, 100% block 자동차단)", "V1", "FT-FUNC")
add(250, "§7.3 비용/안전 LOCK", "RBAC 4역할 구현 (OWNER/ADMIN/OPERATOR/VIEWER + 권한 매트릭스)", "V1", "FT-SEC")
add(251, "§7.3 비용/안전 LOCK", "Autonomy 기본값 L1(SUPERVISED) 구현", "V1", "FT-CFG", impl_type="설정")
add(252, "§7.3 비용/안전 LOCK", "Guardrails 4-Layer 안전 필터 구현 (L1:NeMo + L2:Guardrails AI + L3:LlamaGuard + L4:사후감사V2+)", "V1,V2", "FT-SEC")
add(253, "§7.3 비용/안전 LOCK", "P2 자동 OFF 구현 (세션 종료 시 즉시 OFF)", "V1", "FT-FUNC")
add(254, "§7.3 비용/안전 LOCK", "Non-goal 7개 항목 거부/차단 로직 구현", "V1", "FT-SEC")
add(255, "§7.3 비용/안전 LOCK", "7개 불변 구역 보호 구현 (safety_rules/cost_ceiling/approval_flow/non_goals/audit_format/data_retention/user_consent)", "V1", "FT-SEC")
add(256, "§7.3 비용/안전 LOCK", "승인 타임아웃 구현 (10분 미응답 → 자동 거부)", "V1", "FT-FUNC")

# 7.4 데이터/인프라 LOCK
add(262, "§7.4 데이터/인프라 LOCK", "GraphRAG 하이브리드 RAG 구현 (V1=Basic 64%+, V2=Hybrid+Rerank 83%+, V3=Self-RAG+Graph 90%+)", "V1,V2,V3", "FT-FUNC")
add(263, "§7.4 데이터/인프라 LOCK", "Embedding BGE-M3 로컬 구현 (1024dim) + text-embedding-3-small 클라우드", "V1", "FT-INFRA")
add(264, "§7.4 데이터/인프라 LOCK", "QoD 0.0~1.0 스케일 구현 (DEC-010)", "V1", "FT-FUNC")
add(265, "§7.4 데이터/인프라 LOCK", "QoD 가중치 적용 (RAG: relevance 0.30 + accuracy 0.25 + freshness 0.25 + completeness 0.20)", "V1", "FT-CFG", impl_type="설정")
add(267, "§7.4 데이터/인프라 LOCK", "Semantic Cache 구현 (cosine ≥ 0.95)", "V1", "FT-FUNC")
add(268, "§7.4 데이터/인프라 LOCK", "Vector DB V1=Chroma 로컬 구현", "V1", "FT-INFRA")
add(269, "§7.4 데이터/인프라 LOCK", "RAG 6단계 파이프라인 구현 (Collect→Chunk 300~500tok→Embed→Store→Retrieve→Generate)", "V1", "FT-FUNC")
add(271, "§7.4 데이터/인프라 LOCK", "설정 우선순위 구현 (ENV > config.toml > default)", "V0", "FT-CFG", impl_type="설정")
add(272, "§7.4 데이터/인프라 LOCK", "JSON Structured 로깅 구현 (평문 금지, trace_id 필수)", "V0", "FT-INFRA")
add(273, "§7.4 데이터/인프라 LOCK", "네이밍 컨벤션 적용 (event:lower.dot / failure:UPPER_SNAKE / fallback:FB_ / state:S#_ / module:S-#)", "V0", "FT-CFG", impl_type="설정")

# 7.5 Self-evo LOCK
add(279, "§7.5 Self-evo LOCK", "Self-evo 제안-승인 워크플로우 구현 (자동 적용 절대 금지)", "V3", "FT-FUNC")
add(280, "§7.5 Self-evo LOCK", "Self-evo 허용 6개 영역 제한 구현 (프롬프트/도구조합/메모리관리/출력포맷/워크플로우순서/모델선택)", "V3", "FT-CFG", impl_type="설정")
add(282, "§7.5 Self-evo LOCK", "Self-evo 롤백 잠금 구현 (동일 제안 롤백 후 14일 재적용 금지)", "V3", "FT-FUNC")

# 7.6 UI/UX LOCK
add(288, "§7.6 UI/UX LOCK", "Tauri 2.0 + React 18 UI 프레임워크 구현", "V1", "FT-UI")
add(289, "§7.6 UI/UX LOCK", "2-View 구현 (Builder:개발/관리 + Hologram:사용자 대화)", "V1", "FT-UI")
add(290, "§7.6 UI/UX LOCK", "3-Panel 레이아웃 구현 (Left:Navigation/Timeline + Center:Canvas/Stream + Right:Control/HUD)", "V1", "FT-UI")
add(291, "§7.6 UI/UX LOCK", "P2 재확인 모달 구현 (DEC-011)", "V1", "FT-UI")
add(292, "§7.6 UI/UX LOCK", "비용 경고 색상 표시 구현 (80%=#FBBF24노란, 100%=#EF4444빨간, DEC-015)", "V1", "FT-UI")
add(293, "§7.6 UI/UX LOCK", "ORANGE/BLUE 브랜드 색상 적용 (#F97316, #00F6FF)", "V1", "FT-UI", impl_type="설정")

# ============================================================
# §9 미해소 이슈 45건 (lines 311-377)
# ============================================================
# HIGH
add(317, "§9 HIGH 이슈", "IMPLEMENTATION 계층 = PHASE_B 명시 (V0-002)", "V0", "FT-CFG", impl_type="설정")
add(318, "§9 HIGH 이슈", "Python 백엔드 통신 계층 확정 (V0-004)", "V0", "FT-INFRA")
add(319, "§9 HIGH 이슈", "I-Series 25개 모듈 카운트 통일 확정 (V1-001)", "V1", "FT-CFG", impl_type="설정")
add(320, "§9 HIGH 이슈", "E-15 명칭 충돌 처리: File System / Cloud Collector 겸용 (V1-002)", "V1", "FT-CFG", impl_type="설정")
add(321, "§9 HIGH 이슈", "S-5 명칭 충돌 처리: Router Evolution / Cloud Evolver 겸용 (V1-003)", "V1", "FT-CFG", impl_type="설정")
add(323, "§9 HIGH 이슈", "Python 백엔드 진입점 정의 (V1-015)", "V0", "FT-INFRA")
add(324, "§9 HIGH 이슈", "I-21~I-25 모듈 정의 추가 (V1-016)", "V1", "FT-MOD", notes="Source Evolution/Task/Doc/KG/SDAR")
add(325, "§9 HIGH 이슈", "Agent Teams vs FREEZE 충돌 해결 (V2-003): Lead Agent 단방향만 V1, MessageBus는 V2", "V1,V2", "FT-FUNC")
add(326, "§9 HIGH 이슈", "STEP7 TITLE_ONLY V2 CRITICAL ~190건 상세 스펙 보강 (V2-008)", "V2", "FT-DOMAIN", extractable=False, notes="TITLE_ONLY_UNVERIFIABLE — 상세 스펙 미존재")

# MEDIUM
add(332, "§9 MEDIUM 이슈", "V0 비용 상한 = V1 동일 적용 ₩40,000/월 (V0-001)", "V0", "FT-CFG", impl_type="설정")
add(333, "§9 MEDIUM 이슈", "디렉토리 구조 PHASE_B2 정본 적용 (V0-003)", "V0", "FT-INFRA")
add(334, "§9 MEDIUM 이슈", "approval_status enum 4값 통일: approved/denied/pending/expired (V1-004)", "V1", "FT-SCHEMA")
add(335, "§9 MEDIUM 이슈", "datetime.utcnow() → datetime.now(timezone.utc) 전수 교체 (V1-005)", "V1", "FT-FUNC")
add(336, "§9 MEDIUM 이슈", "QoD 5요소 가중치 통일: Accuracy 0.30 + Relevance 0.25 + Completeness 0.20 + Safety 0.15 + Efficiency 0.10 (V1-006)", "V1", "FT-CFG", impl_type="설정")
add(337, "§9 MEDIUM 이슈", "Front Mini LLM = I-1 내부 서브컴포넌트 명시 (V1-007)", "V1", "FT-CFG", impl_type="설정")
add(338, "§9 MEDIUM 이슈", "Guardrails 4-Layer 명시 (L4=V2+ 활성) (V1-010)", "V1", "FT-CFG", impl_type="설정")
add(340, "§9 MEDIUM 이슈", "10-Layer 명칭 충돌 해결: Cloud Library CL-Layer 접두어 (V2-001)", "V2", "FT-CFG", impl_type="설정")
add(341, "§9 MEDIUM 이슈", "SDAR V2 COND 활성화 조건 정의 (AR-L2→AR-L3, LOW성공률≥95%) (V2-002)", "V2", "FT-CFG", impl_type="설정")
add(342, "§9 MEDIUM 이슈", "JSONL→PostgreSQL+Loki 로그 마이그레이션 (V2-004)", "V2", "FT-MIG", impl_type="마이그레이션")
add(343, "§9 MEDIUM 이슈", "Chroma→Qdrant 벡터 재임베딩 (4-Phase, needs_reembedding 플래그) (V2-005)", "V2", "FT-MIG", impl_type="마이그레이션")
add(344, "§9 MEDIUM 이슈", "NetworkX JSON→Neo4j Community 변환 (V2-006)", "V2", "FT-MIG", impl_type="마이그레이션")
add(346, "§9 MEDIUM 이슈", "K8s 배포 명세 보강 (Helm Chart, ArgoCD, 멀티리전) (V3-001)", "V3", "FT-INFRA")
add(347, "§9 MEDIUM 이슈", "S-8 Self-evo 거버넌스 상세화 (V3-002)", "V3", "FT-MOD")
add(348, "§9 MEDIUM 이슈", "스키마 버전 v3.0.0 통일 승격 (CC-001)", "V0", "FT-SCHEMA", impl_type="설정")
add(349, "§9 MEDIUM 이슈", "QoD 가중치 이중 체계 구분 명시: RAG 소스 vs Cloud Library 수집 (CC-003)", "V2", "FT-CFG", impl_type="설정")
add(350, "§9 MEDIUM 이슈", "EventTypeRegistry 완성: agent.* + sdar.* 이벤트 통합 등록 (CC-006)", "V1", "FT-CFG", impl_type="설정")
add(351, "§9 MEDIUM 이슈", "Python/TypeScript 스키마 동기화 메커니즘 (Pydantic→Zod 자동변환) (CC-007)", "V1", "FT-INFRA")
add(352, "§9 MEDIUM 이슈", "HMAC-SHA256 키관리/검증 상세화 (Agent Teams MessageBus) (CC-012)", "V2", "FT-SEC")

# LOW
add(361, "§9 LOW 이슈", "React 18.3 통일 (V1-014)", "V1", "FT-CFG", impl_type="설정")
add(362, "§9 LOW 이슈", "V3 비용 상한 재산정 (V2 운영 데이터 기반) (V3-003)", "V3", "FT-CFG", impl_type="설정")
add(363, "§9 LOW 이슈", "GraphRAG 90% 목표 벤치마크 기준/측정 방법 정의 (V3-004)", "V3", "FT-TEST", impl_type="테스트")

# INFO
add(373, "§9 INFO 이슈", "테스트 케이스 AC 기반 자동 도출 (CC-008)", "V1", "FT-TEST", impl_type="테스트", confidence="추론")

# ============================================================
# §10 GO/NO-GO (lines 380-476) — 비중복 항목만
# ============================================================
# V0 진입 전
add(392, "§10 V0 GO/NO-GO", "BASE-1.3 전 24개 규칙 코드 매핑", "V0", "FT-CFG", impl_type="설정")
add(393, "§10 V0 GO/NO-GO", "스캐폴딩 + 의존성 설치 (pip/npm/cargo)", "V0", "FT-INFRA", impl_type="인프라")
add(395, "§10 V0 GO/NO-GO", "24개 스키마 코드 생성 (Pydantic v2/Zod/serde)", "V0", "FT-SCHEMA")
add(396, "§10 V0 GO/NO-GO", "I-1~I-5 + I-19 스켈레톤 생성", "V0", "FT-MOD")
add(397, "§10 V0 GO/NO-GO", "L0 세션 메모리 최소 구현", "V0", "FT-FUNC")
add(398, "§10 V0 GO/NO-GO", "비용 엔진 ₩40,000/월 하드코딩", "V0", "FT-FUNC")
add(399, "§10 V0 GO/NO-GO", "Guardrails L1+L2 초기 설정", "V0", "FT-SEC", impl_type="설정")
add(400, "§10 V0 GO/NO-GO", "Ollama + Chroma + SQLite 초기화", "V0", "FT-INFRA", impl_type="인프라")

# V1 진입 전 (비중복)
add(417, "§10 V1 GO/NO-GO", "15개 보안 항목 (S7E + DEC-003 Allowlist) 구현", "V1", "FT-SEC")
add(418, "§10 V1 GO/NO-GO", "테스트 인프라 구축 (80%+ 커버리지)", "V1", "FT-TEST", impl_type="테스트")
add(419, "§10 V1 GO/NO-GO", "CI/CD 설정 완료 (GitHub Actions 8-stage)", "V1", "FT-INFRA", impl_type="인프라")
add(420, "§10 V1 GO/NO-GO", "스토리지 스택 구축 (SQLite+Chroma+JSONL+Graph)", "V1", "FT-INFRA", impl_type="인프라")

# V1→V2 전환 조건
add(432, "§10 V1→V2 전환", "QoD ≥ 0.85 (30일) 달성 검증", "V2", "FT-TEST", impl_type="테스트", confidence="추론")
add(432, "§10 V1→V2 전환", "RAG 정확도 ≥ 60% 달성 검증", "V2", "FT-TEST", impl_type="테스트", confidence="추론")
add(433, "§10 V1→V2 전환", "메모리 승격/강등 오류율 < 1% 달성", "V2", "FT-TEST", impl_type="테스트", confidence="추론")

# V2 진입 전 (비중복)
add(447, "§10 V2 GO/NO-GO", "MessageBus 구현 결정 (Redis vs In-Memory)", "V2", "FT-INFRA")
add(451, "§10 V2 GO/NO-GO", "V2 인프라 10개 컴포넌트 구축", "V2", "FT-INFRA", impl_type="인프라")
add(452, "§10 V2 GO/NO-GO", "V2 비용 모니터링 대시보드 구현 (₩93,000 이내)", "V2", "FT-UI")

# V2→V3 전환 조건
add(458, "§10 V2→V3 전환", "QoD ≥ 0.90 (60일) 달성 검증", "V3", "FT-TEST", impl_type="테스트", confidence="추론")
add(459, "§10 V2→V3 전환", "Loki+Grafana 배포", "V3", "FT-INFRA", impl_type="인프라")

# V3 진입 전 (비중복)
add(472, "§10 V3 GO/NO-GO", "에이전트 50+ 병렬 인프라 구축", "V3", "FT-INFRA", impl_type="인프라")
add(473, "§10 V3 GO/NO-GO", "A2A 프로토콜 설계 구현", "V3", "FT-FUNC")
add(474, "§10 V3 GO/NO-GO", "Federated Agent 승인 체계 구현", "V3", "FT-SEC")
add(475, "§10 V3 GO/NO-GO", "Agent Marketplace 기준 확정 구현", "V3", "FT-FUNC")

# ============================================================
# §11 기술 스택 (lines 480-494)
# ============================================================
add(484, "§11 기술 스택", "V1 LLM 통합: Ollama + GPT-4o mini", "V1", "FT-INFRA", impl_type="인프라")
add(484, "§11 기술 스택", "V2 LLM 확장: GPT-4o mini + Sonnet 추가", "V2", "FT-INFRA", impl_type="인프라")
add(484, "§11 기술 스택", "V3 LLM 확장: vLLM + 외부 조합", "V3", "FT-INFRA", impl_type="인프라")
add(486, "§11 기술 스택", "V2+ Embedding 확장: text-embedding-3-small 추가", "V2", "FT-INFRA", impl_type="인프라")
add(487, "§11 기술 스택", "V2 Vector DB: Chroma→Qdrant 서버 전환", "V2", "FT-MIG", impl_type="마이그레이션")
add(488, "§11 기술 스택", "V2 Graph DB: NetworkX JSON→Neo4j Community 전환", "V2", "FT-MIG", impl_type="마이그레이션")
add(489, "§11 기술 스택", "V2 Storage: SQLite+JSONL→PostgreSQL 전환", "V2", "FT-MIG", impl_type="마이그레이션")
add(490, "§11 기술 스택", "V2 Deploy: Docker Compose 구성", "V2", "FT-INFRA", impl_type="인프라")
add(490, "§11 기술 스택", "V3 Deploy: K8s 전환", "V3", "FT-INFRA", impl_type="인프라")
add(491, "§11 기술 스택", "V2 UI: PWA (Next.js) 추가", "V2", "FT-UI")
add(491, "§11 기술 스택", "V3 UI: 모바일 네이티브 추가", "V3", "FT-UI")

# ============================================================
# §12 핵심 스키마 (lines 498-537)
# ============================================================
add(500, "§12 핵심 스키마", "Decision 스키마 구현 (18필드, FREEZE)", "V0,V1", "FT-SCHEMA")
add(511, "§12 핵심 스키마", "IntentFrame 스키마 구현", "V0,V1", "FT-SCHEMA")
add(521, "§12 핵심 스키마", "ResponseEnvelope 스키마 구현 (LOCK)", "V0,V1", "FT-SCHEMA")
add(531, "§12 핵심 스키마", "상태 머신 S0~S8 구현 (8단계 전이 + 타임아웃)", "V0,V1", "FT-FUNC")

# ============================================================
# §13 API 계약 (lines 541-551)
# ============================================================
add(543, "§13 API 계약", "Tauri IPC Core Commands 구현 (decision/workflow/session 15개)", "V1", "FT-API")
add(545, "§13 API 계약", "Tauri IPC Agent Commands 구현 (node/pipeline/marketplace 15개)", "V1", "FT-API")
add(546, "§13 API 계약", "Tauri IPC Storage Commands 구현 (memory/vector/cache/graphrag/qod 18개)", "V1", "FT-API")
add(547, "§13 API 계약", "Tauri IPC Safety Commands 구현 (policy/cost/approval/guardrails/rbac/autonomy 19개)", "V1", "FT-API")
add(548, "§13 API 계약", "Tauri IPC UI Commands 구현 (log/config/theme/notification 5개)", "V1", "FT-API")
add(549, "§13 API 계약", "Python-Rust JSON-RPC 구현 (langgraph.*/embedding.*/llm.*/mcp.* 13개)", "V1", "FT-API")
add(550, "§13 API 계약", "MCP Tool Protocol 구현 (tools/call, tool_registry.get/list 3개)", "V1", "FT-API")
add(551, "§13 API 계약", "API 응답 규격 구현 ({success, data/error, trace_id})", "V1", "FT-API")

# ============================================================
# §14 프로젝트 구조 (lines 555-587)
# ============================================================
add(558, "§14 프로젝트 구조", "Monorepo 디렉토리 스캐폴딩 (vamos/ 루트)", "V0", "FT-INFRA", impl_type="인프라")
add(559, "§14 프로젝트 구조", "GitHub Actions CI/CD 워크플로우 (8-stage)", "V1", "FT-INFRA", impl_type="인프라")
add(560, "§14 프로젝트 구조", "React 프론트엔드 구조 (components/pages/hooks/stores/types)", "V0,V1", "FT-UI")
add(566, "§14 프로젝트 구조", "Rust Tauri 백엔드 구조 (commands/bridge/models)", "V0,V1", "FT-INFRA")
add(571, "§14 프로젝트 구조", "Python AI/ML 백엔드 구조 (orange_core/blue_nodes/infra/agent/storage/safety/schemas/mcp)", "V0,V1", "FT-INFRA")
add(581, "§14 프로젝트 구조", "shared/types JSON Schema Golden Source 구현", "V0", "FT-SCHEMA")
add(582, "§14 프로젝트 구조", "config 디렉토리 구성 (default.toml + llm/embedding/storage/safety/mcp)", "V0", "FT-CFG", impl_type="설정")
add(583, "§14 프로젝트 구조", "data 디렉토리 구성 (sqlite/chroma/logs/graph/backups)", "V0", "FT-INFRA", impl_type="인프라")
add(587, "§14 프로젝트 구조", "타입 동기화: Python contracts.py SOT → TypeScript Zod / Rust serde 생성", "V0,V1", "FT-SCHEMA")

# ============================================================
# §15 메모리/저장 계층 (lines 591-603)
# ============================================================
add(595, "§15 메모리/저장", "L0 Session 메모리 구현 (단일 세션, TTL 7일/최대30일, B-4)", "V1", "FT-FUNC")
add(596, "§15 메모리/저장", "L1 Project 메모리 구현 (project_id 단위, TTL 90일, B-1)", "V1", "FT-FUNC", notes="V1에서 선택적")
add(597, "§15 메모리/저장", "L2 Long-term 메모리 구현 (전역, 무기한, B-3, 승인 필요)", "V2", "FT-FUNC")
add(598, "§15 메모리/저장", "L3 Procedural 메모리 구현 (전역/프로젝트, 무기한, B-2)", "V3", "FT-FUNC")
add(600, "§15 메모리/저장", "프로젝트 네임스페이스 구현 (project_id 필수, 혼합 금지)", "V1", "FT-FUNC")
add(601, "§15 메모리/저장", "QoD 임계값 적용 (< 0.4 → L2 벡터삽입 금지, < 0.7 → 출력 보류)", "V1", "FT-FUNC")
add(602, "§15 메모리/저장", "PII 마스킹 구현 (V1=정규식, V2+=NER 모델+문맥 분류기)", "V1,V2", "FT-SEC")
add(603, "§15 메모리/저장", "메모리 검색 순서 구현 (현재 프로젝트 → 글로벌 → 아카이브)", "V1", "FT-FUNC")

# ============================================================
# §16 레지스트리 요약 (lines 607-614)
# ============================================================
add(609, "§16 레지스트리", "EventTypeRegistry 구현 (53+ 이벤트: oc.i1.*/oc.i2.*/wf.*/ui.*/mem.*/agent.*/sdar.*)", "V1", "FT-CFG")
add(610, "§16 레지스트리", "FailureCodeRegistry 구현 (20개: OC_I1_*/OC_I2_*/POLICY_DENY/GT_ERR_*/TOOL_*)", "V1", "FT-CFG")
add(611, "§16 레지스트리", "FallbackRegistry 구현 (13개: FB_ASK_CLARIFICATION/FB_RAG_*/FB_COST_*/FB_REQUIRE_*/FB_OUTPUT_*)", "V1", "FT-CFG")
add(612, "§16 레지스트리", "ToolRegistry 구현 (tool_id, category 8종, adapter_id, risk_class, cost_class, required_gates)", "V1", "FT-CFG")
add(613, "§16 레지스트리", "NodeRegistry 구현 (domain_name 기반)", "V1", "FT-CFG")
add(614, "§16 레지스트리", "VerifyChainRegistry 구현 (EVX-1~EVX-6)", "V1", "FT-CFG")

# ============================================================
# §17 주요 특화 시스템 (lines 618-638)
# ============================================================
add(622, "§17 AI Investing", "AI Investing 83개 데이터 소스 통합", "V1", "FT-DOMAIN")
add(622, "§17 AI Investing", "AI Investing 96개 전략 카탈로그 구현", "V1", "FT-DOMAIN")
add(623, "§17 AI Investing", "51% Gate 구현 (Win Rate≥51%, Sharpe≥1.0, Decay<30%)", "V1", "FT-DOMAIN")
add(624, "§17 AI Investing", "5-Agent 구조 구현 (Perplexity→Gemini→ChatGPT→Claude→Copilot)", "V1", "FT-DOMAIN")
add(625, "§17 AI Investing", "법적 준수 자동 감지 (Wash Sale/PDT/Uptick Rule)", "V1", "FT-DOMAIN")
add(629, "§17 SDAR", "SDAR 5-Layer 구현 (Detection→Diagnosis→Prescription→Repair→Verification)", "V2,V3", "FT-DOMAIN")
add(630, "§17 SDAR", "AR-Level 구현 (AR-L0 수동~AR-L4 고위험자동, 기본 AR-L2)", "V2,V3", "FT-DOMAIN")
add(631, "§17 SDAR", "NEVER_AUTO 10개 영역 보호 구현", "V2,V3", "FT-SEC")
add(635, "§17 Agent Teams", "Lead Agent + Sub-Agents 위임 구현 (최대 깊이 3단계)", "V1,V2,V3", "FT-FUNC")
add(636, "§17 Agent Teams", "5가지 협업 패턴 구현 (Sequential/Parallel/Debate/Supervisor/Handoff)", "V1,V2,V3", "FT-FUNC")
add(637, "§17 Agent Teams", "에이전트 수 확장 구현 (V1=3, V2=10, V3=50+)", "V1,V2,V3", "FT-FUNC")

# ============================================================
# §18 작업 시 주의사항 (lines 641-667) — 코딩 컨벤션 = 구현 행위
# ============================================================
add(651, "§18 코딩 컨벤션", "Python PEP 8 + 타입 힌트 필수 + Pydantic v2 + async/await 적용", "V0", "FT-CFG", impl_type="설정")
add(652, "§18 코딩 컨벤션", "TypeScript strict mode + Zod 검증 + React 18 + zustand 적용", "V0", "FT-CFG", impl_type="설정")
add(653, "§18 코딩 컨벤션", "Rust stable + serde derive + thiserror/anyhow 적용", "V0", "FT-CFG", impl_type="설정")

# ============================================================
# §19 V1 구현 순서 (lines 670-678) — 주차별 구현 → 구현 행위
# ============================================================
add(674, "§19 V1 구현 순서", "주 1~2: ORANGE CORE 기본 파이프라인 구현 (I-1→I-2→I-5→I-8)", "V1", "FT-FUNC", confidence="추론", notes="구현 순서이나 파이프라인 조합이 구현 항목")
add(675, "§19 V1 구현 순서", "주 3~4: Storage/Memory + RAG 구현 (L0/L1, Chroma, BM25+Vector)", "V1", "FT-FUNC", confidence="추론")
add(676, "§19 V1 구현 순서", "주 5~6: Workflow Engine 구현 (LangGraph StateGraph, 5-Pipeline, TEE)", "V1", "FT-FUNC", confidence="추론")
add(677, "§19 V1 구현 순서", "주 7~9: UI/UX 구현 (Tauri+React, Builder/Hologram View, 3-Panel)", "V1", "FT-UI", confidence="추론")
add(678, "§19 V1 구현 순서", "주 10~12: 통합 + AI Investing Paper Trading MVP + E2E 테스트", "V1", "FT-TEST", impl_type="테스트", confidence="추론")

# ============================================================
# §20 Config LOCK 값 (lines 682-697)
# ============================================================
add(686, "§20 Config LOCK", "config.v1.toml core.single_decision_lock=true 적용", "V1", "FT-CFG", impl_type="설정")
add(687, "§20 Config LOCK", "config.v1.toml embedding.model=bge-m3 적용", "V1", "FT-CFG", impl_type="설정")
add(688, "§20 Config LOCK", "config.v1.toml embedding.dimension=1024 적용", "V1", "FT-CFG", impl_type="설정")
add(689, "§20 Config LOCK", "config.v1.toml vector_db.backend=chroma 적용", "V1", "FT-CFG", impl_type="설정")
add(690, "§20 Config LOCK", "config.v1.toml graph_db.backend=json_file 적용", "V1", "FT-CFG", impl_type="설정")
add(691, "§20 Config LOCK", "config.v1.toml cost.daily_limit=1300 적용 (ABSOLUTE LOCK)", "V1", "FT-CFG", impl_type="설정")
add(692, "§20 Config LOCK", "config.v1.toml cost.monthly_limit=40000 적용 (ABSOLUTE LOCK)", "V1", "FT-CFG", impl_type="설정")
add(693, "§20 Config LOCK", "config.v1.toml cost.warn_threshold=80 적용", "V1", "FT-CFG", impl_type="설정")
add(694, "§20 Config LOCK", "config.v1.toml cost.block_threshold=100 적용", "V1", "FT-CFG", impl_type="설정")
add(695, "§20 Config LOCK", "config.v1.toml semantic_cache.similarity_threshold=0.95 적용", "V1", "FT-CFG", impl_type="설정")
add(696, "§20 Config LOCK", "config.v1.toml logging.trace_id_required=true 적용", "V1", "FT-CFG", impl_type="설정")
add(697, "§20 Config LOCK", "config.v1.toml mcp.transport=streamable_http 적용", "V1", "FT-CFG", impl_type="설정")

# ============================================================
# 통계 계산
# ============================================================
total = len(features)
extractable_true = sum(1 for f in features if f["extractable"])
extractable_false = sum(1 for f in features if not f["extractable"])

cat_dist = {}
for f in features:
    c = f["category"]
    cat_dist[c] = cat_dist.get(c, 0) + 1

ver_dist = {"V0": 0, "V1": 0, "V2": 0, "V3": 0}
for f in features:
    for v in ["V0", "V1", "V2", "V3"]:
        if v in f["version_scope"]:
            ver_dist[v] += 1

inference_count = sum(1 for f in features if f["confidence"] == "추론")
unknown_count = sum(1 for f in features if "V_UNKNOWN" in f["version_scope"])

# 판단필요 항목 — 이번 추출에서는 없음 (CLAUDE.md는 구조가 명확)
judgment_needed = 0

# ============================================================
# 용어 매핑 테이블
# ============================================================
terminology_mapping = [
    {"claude_md_term": "IntentDetector / I-1", "part2_term": "의도 분석기 / 의도 탐지기", "notes": "I-1 모듈"},
    {"claude_md_term": "Context Builder / I-2", "part2_term": "컨텍스트 빌더 / 맥락 구축기", "notes": "I-2 모듈"},
    {"claude_md_term": "Memory System / I-3", "part2_term": "메모리 시스템", "notes": "I-3 모듈"},
    {"claude_md_term": "Multimodal Interpreter / I-4", "part2_term": "멀티모달 해석기", "notes": "I-4 모듈"},
    {"claude_md_term": "Condition & Decision Engine / I-5", "part2_term": "조건 판단 엔진 / 의사결정 엔진", "notes": "I-5 모듈"},
    {"claude_md_term": "Self-check Engine / I-6", "part2_term": "자기점검 엔진 / 셀프체크", "notes": "I-6 모듈"},
    {"claude_md_term": "Policy Engine / I-8", "part2_term": "정책 엔진", "notes": "I-8 모듈"},
    {"claude_md_term": "Cost Manager / I-9", "part2_term": "비용 관리자 / 비용 엔진", "notes": "I-9 모듈"},
    {"claude_md_term": "Tool Registry/Router / I-10", "part2_term": "도구 레지스트리 / 도구 라우터", "notes": "I-10 모듈"},
    {"claude_md_term": "Output Composer / I-11", "part2_term": "출력 작성기 / 출력 합성기", "notes": "I-11 모듈"},
    {"claude_md_term": "Workflow Builder / I-12", "part2_term": "워크플로우 빌더", "notes": "I-12 모듈"},
    {"claude_md_term": "Summarizer & Memory Distiller / I-14", "part2_term": "요약기 / 메모리 증류기", "notes": "I-14 모듈"},
    {"claude_md_term": "Evidence & QoD Manager / I-15", "part2_term": "근거 관리자 / QoD 관리자", "notes": "I-15 모듈"},
    {"claude_md_term": "Knowledge Search Engine / I-16", "part2_term": "지식 검색 엔진", "notes": "I-16 모듈"},
    {"claude_md_term": "Blue Node Manager / I-17", "part2_term": "블루노드 관리자", "notes": "I-17 모듈"},
    {"claude_md_term": "Self-evo Engine / I-18", "part2_term": "자기진화 엔진", "notes": "I-18 모듈"},
    {"claude_md_term": "Approval Manager / I-19", "part2_term": "승인 관리자", "notes": "I-19 모듈"},
    {"claude_md_term": "Failure/Fallback Manager / I-20", "part2_term": "장애/대체 관리자 / 폴백 관리자", "notes": "I-20 모듈"},
    {"claude_md_term": "SDAR Engine / I-25", "part2_term": "자가진단/수리 엔진", "notes": "I-25 모듈"},
    {"claude_md_term": "IntentFrame", "part2_term": "의도 프레임 / IntentFrame", "notes": "스키마"},
    {"claude_md_term": "EvidencePack", "part2_term": "증거 패킷 / EvidencePack", "notes": "스키마"},
    {"claude_md_term": "ResponseEnvelope", "part2_term": "응답 봉투 / ResponseEnvelope", "notes": "스키마"},
    {"claude_md_term": "Decision", "part2_term": "결정 / Decision", "notes": "스키마"},
    {"claude_md_term": "PolicyGate", "part2_term": "정책 게이트", "notes": "Gate"},
    {"claude_md_term": "CostGate", "part2_term": "비용 게이트", "notes": "Gate"},
    {"claude_md_term": "ApprovalGate", "part2_term": "승인 게이트", "notes": "Gate"},
    {"claude_md_term": "EvidenceGate", "part2_term": "근거 게이트", "notes": "Gate"},
    {"claude_md_term": "SelfCheckGate", "part2_term": "자기점검 게이트", "notes": "Gate"},
    {"claude_md_term": "Front Mini LLM", "part2_term": "프론트 미니 LLM / 소형 LLM", "notes": "I-1 서브컴포넌트"},
    {"claude_md_term": "ORANGE CORE", "part2_term": "오렌지 코어", "notes": "핵심 계층"},
    {"claude_md_term": "BLUE NODE", "part2_term": "블루 노드", "notes": "도메인 실행 계층"},
    {"claude_md_term": "OTHER BRAINS", "part2_term": "기타 브레인 / 외부 브레인", "notes": "외부 도구 계층"},
    {"claude_md_term": "Hologram LLM", "part2_term": "홀로그램 LLM / 메인 LLM", "notes": "최종 출력 LLM"},
    {"claude_md_term": "Builder View", "part2_term": "빌더 뷰 / 개발 뷰", "notes": "UI"},
    {"claude_md_term": "Hologram View", "part2_term": "홀로그램 뷰 / 대화 뷰", "notes": "UI"},
    {"claude_md_term": "Downshift", "part2_term": "다운시프트 / 비용 절감 전환", "notes": "비용 정책"},
    {"claude_md_term": "TEE (Try-Execute-Evaluate)", "part2_term": "TEE 루프 / 시도-실행-평가", "notes": "워크플로우"},
    {"claude_md_term": "QoD (Quality of Decision)", "part2_term": "결정 품질 / QoD", "notes": "품질 지표"},
    {"claude_md_term": "HITL (Human-In-The-Loop)", "part2_term": "사람 개입 / HITL", "notes": "승인 방식"},
    {"claude_md_term": "Semantic Cache", "part2_term": "의미 캐시 / 시맨틱 캐시", "notes": "캐시"},
    {"claude_md_term": "RBAC", "part2_term": "역할 기반 접근 제어 / RBAC", "notes": "보안"},
]

# ============================================================
# 최종 산출물 조립
# ============================================================
output = {
    "meta": {
        "phase": "0-B",
        "source_file": "CLAUDE.md",
        "source_path": "D:\\VAMOS\\docs\\sot\\CLAUDE.md",
        "source_lines_total": 697,
        "source_lines_read": 697,
        "read_completion": "100%",
        "last_line_content": "| mcp.transport | streamable_http | LOCK |",
        "generated_date": "2026-03-08",
        "generator": "v10 Phase 0-B Agent"
    },
    "features": features,
    "statistics": {
        "total_features": total,
        "extractable_true": extractable_true,
        "extractable_false": extractable_false,
        "category_distribution": dict(sorted(cat_dist.items())),
        "version_distribution": ver_dist,
        "confidence_inference_count": inference_count,
        "confidence_explicit_count": total - inference_count,
        "version_unknown_count": unknown_count,
        "judgment_needed_count": judgment_needed
    },
    "terminology_mapping": terminology_mapping
}

# JSON 저장
out_path = r"D:\VAMOS\04. 구현단계\v10_results\phase0-b\v10_layer1_claude_features.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"[OK] Saved: {out_path}")
print(f"총 추출 건수: {total}")
print(f"  extractable=true: {extractable_true}")
print(f"  extractable=false: {extractable_false}")
print(f"카테고리별 분포:")
for k, v in sorted(cat_dist.items()):
    print(f"  {k}: {v}")
print(f"버전별 분포:")
for k, v in ver_dist.items():
    print(f"  {v:>3d}건에서 {k} 포함")
print(f"confidence='추론': {inference_count}건")
print(f"version_scope='V_UNKNOWN': {unknown_count}건")
print(f"판단필요: {judgment_needed}건")
