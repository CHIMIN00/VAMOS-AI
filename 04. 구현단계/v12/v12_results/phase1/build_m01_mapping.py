#!/usr/bin/env python
"""M-1 Mapping Agent: V0 Features -> PART2 §2 mapping builder."""
import json
import re

# Load feature registry
with open('D:/VAMOS/04. 구현단계/v12/v12_results/phase0/v12_feature_registry_final.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

v0_features = [ft for ft in registry['features'] if ft['version_scope'] == 'V0']

# Load PART2 content for search
with open('D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# §2 range: lines 182-1584 (1-indexed)
s2_lines = {i+1: lines[i] for i in range(181, 1584)}
# §6 range: lines 4181-5858
s6_lines = {i+1: lines[i] for i in range(4180, min(5858, len(lines)))}

def search_text(line_dict, keywords, min_match=1):
    """Search for keywords in line dict, return list of (line_num, text) matches."""
    results = []
    for lnum, text in line_dict.items():
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)
        if matches >= min_match:
            results.append((lnum, text.strip(), matches))
    results.sort(key=lambda x: -x[2])
    return results

def get_step_section(line_num):
    """Determine §2.STEP section from line number."""
    if 193 <= line_num < 570:
        return "§2.STEP1"
    elif 570 <= line_num < 829:
        return "§2.STEP2"
    elif 829 <= line_num < 994:
        return "§2.STEP3"
    elif 994 <= line_num < 1205:
        return "§2.STEP4"
    elif 1205 <= line_num < 1374:
        return "§2.STEP5"
    elif 1374 <= line_num <= 1584:
        return "§2.STEP6"
    elif 182 <= line_num < 193:
        return "§2"
    return "§2"

def get_s6_section(line_num):
    """Determine §6 subsection from line number."""
    boundaries = [
        (4181, 4286, "§6.1"),
        (4286, 4321, "§6.2"),
        (4321, 4453, "§6.3"),
        (4453, 4476, "§6.4"),
        (4476, 4577, "§6.5"),
        (4577, 4609, "§6.6"),
        (4609, 4739, "§6.7"),
        (4739, 4861, "§6.8"),
        (4861, 4974, "§6.9"),
        (4974, 5237, "§6.10"),
        (5237, 5425, "§6.11"),
        (5425, 5542, "§6.12"),
        (5542, 5858, "§6.13"),
    ]
    for start, end, sid in boundaries:
        if start <= line_num < end:
            return sid
    return "§6"

# Build keyword mapping for each feature
# Mapping rules based on thorough reading of §2 content:

# Pre-built mapping table based on thorough analysis
# Format: feature_id -> (status, section, line, text, severity, notes, secondary_sections)
# This is built from careful reading of §2 content (lines 182-1584)

mapping_rules = {}

# Helper: define groups of features that map to specific steps
# §2.STEP1 (193-569): monorepo, directory structure, dependencies, config.v1.toml, scaffolding
step1_keywords = [
    'monorepo', 'directory', 'scaffold', 'config.v1.toml', 'dependencies',
    'poetry', 'cargo', 'pnpm', 'project structure', 'config toml',
    'environment setup', 'v0 environment', 'package dependency',
    'python package', 'rust crate', 'frontend package', 'node',
    'implementation sequence', '10-layer', 'version roadmap',
    'ollama', 'hardware', 'blocker', 'preparation', 'checklist',
    'pre-implementation', 'document conflict', 'file modification',
    'artifact', 'v0 version', 'v0 definition', 'readiness',
]

# §2.STEP2 (570-828): schemas, pydantic, registries, contracts.py, types
step2_keywords = [
    'schema', 'pydantic', 'registry', 'contracts', 'intentframe',
    'evidencepack', 'decisionschema', 'responseenvelope', 'logevent',
    'failurecode', 'fallback', 'eventtype', 'memoryr ecord', 'sourceqod',
    'policycheck', 'approval', 'costbudget', 'downshift', 'nodecapability',
    'noderequestenvelope', 'noderesponseenvelope', 'toolregistryentry',
    'brainadapterresponse', 'workflowstage', 'workflowoutput',
    'failurereport', 'guardrailscheck', 'rbacrole', 'autonomylevel',
    'schema_registry', 'generate_types', 'type codegen', 'freeze',
    'lock decision', 'structured output', 'glossary', 'field',
    'noderegistry', 'toolcall', 'mcpbridge', 'memorcommit',
    'sentiment', 'datetime', 'sequence_id', 'outputprofile',
    'taskpriority', 'connectorresponse', '_meta',
]

# §2.STEP3 (829-993): IPC, JSON-RPC, Tauri IPC, communication layer
step3_keywords = [
    'ipc', 'json-rpc', 'jsonrpc', 'tauri ipc', 'stdin', 'stdout',
    'python_manager', 'rust ipc', 'bridge', 'transport',
    'rpc method', 'rpc server', 'python process', 'health check',
    '72 tauri', '13 json-rpc', 'command handler',
]

# §2.STEP4 (994-1204): ORANGE CORE pipeline, I-modules, gates, LangGraph
step4_keywords = [
    'i-1', 'i-2', 'i-5', 'intent detector', 'context builder',
    'decision engine', 'pipeline', 'langgraph', 'stategraph',
    'gate', 'policygate', 'costgate', 'approvalgate', 'evidencegate',
    'selfcheckgate', 'orange core', '5-stage', '5-phase', '9-state',
    'state machine', 'intake', 'plan', 'execute', 'verify', 'deliver',
    'i-8', 'i-9', 'i-19', 'i-20', 'approval manager', 'cost manager',
    'policy engine', 'failure manager', 'failurereport',
    'runnable', 'concurrency', 'token counting', 'tiktoken',
    'single-decision', 'conversation turn', 'parallel execution',
    'output formatter', '3-part output', 'downshift',
    'di kernel', 'vamos error', 'c3 module', 'fsm',
    'selfcheck threshold', 'base rule',
    'mini llm', 'front mini', 'self-check',
    'approval fsm', 'violation', 'approval timeout',
    'human-in-the-loop', 'rbac', 'policy check',
]

# §2.STEP5 (1205-1373): storage, logging, config loader, memory, SQLite
step5_keywords = [
    'l0 session', 'sqlite', 'memory', 'jsonl', 'logging', 'structlog',
    'config loader', 'trace_id', 'storage', 'memory record',
    'c-1 sqlite', 'c-4 file', 'session memory',
    'log format', 'json structured', 'config priority',
]

# §2.STEP6 (1374-1584): CI, test, GitHub Actions, pytest, coverage
step6_keywords = [
    'ci', 'cd', 'github actions', 'pytest', 'coverage', 'ruff',
    'mypy', 'lint', 'test', 'quality', 'test runner',
    'test strategy', '3-level test', 'benchmark',
    'go/no-go', 'v0 go', 'v0 conditional',
    'v0 implementation checklist', 'v0 completion',
    'capability matrix', 'feature flag',
]

# Now do the actual mapping
results = []

for ft in v0_features:
    fid = ft['feature_id']
    fname = ft['feature_name']
    fdesc = ft.get('feature_description', '')
    fsrc = ft.get('source_text', '')
    fcat = ft['category']
    fpri = ft['priority']

    # Build search terms from feature
    search_terms = []
    # From feature_name
    name_words = re.findall(r'[A-Za-z가-힣]+(?:-[A-Za-z가-힣]+)*', fname)
    search_terms.extend([w.lower() for w in name_words if len(w) > 2])
    # From description
    if fdesc:
        desc_words = re.findall(r'[A-Za-z가-힣]+(?:-[A-Za-z가-힣]+)*', fdesc)
        search_terms.extend([w.lower() for w in desc_words if len(w) > 2])

    # Determine best matching step by keyword overlap
    step_scores = {
        "§2.STEP1": 0, "§2.STEP2": 0, "§2.STEP3": 0,
        "§2.STEP4": 0, "§2.STEP5": 0, "§2.STEP6": 0,
    }

    combined_text = (fname + " " + fdesc + " " + fsrc).lower()

    for kw in step1_keywords:
        if kw in combined_text:
            step_scores["§2.STEP1"] += 1
    for kw in step2_keywords:
        if kw in combined_text:
            step_scores["§2.STEP2"] += 1
    for kw in step3_keywords:
        if kw in combined_text:
            step_scores["§2.STEP3"] += 1
    for kw in step4_keywords:
        if kw in combined_text:
            step_scores["§2.STEP4"] += 1
    for kw in step5_keywords:
        if kw in combined_text:
            step_scores["§2.STEP5"] += 1
    for kw in step6_keywords:
        if kw in combined_text:
            step_scores["§2.STEP6"] += 1

    best_step = max(step_scores, key=step_scores.get)
    best_score = step_scores[best_step]

    # Also search actual §2 text for direct evidence
    # Build specific keywords for this feature
    specific_kws = []
    if 'schema' in combined_text.lower():
        specific_kws.extend(['schema', 'pydantic', 'contracts'])
    if 'intent' in combined_text.lower():
        specific_kws.extend(['intent', 'IntentFrame'])
    if 'decision' in combined_text.lower():
        specific_kws.extend(['decision', 'Decision'])
    if 'pipeline' in combined_text.lower():
        specific_kws.extend(['pipeline', 'LangGraph'])
    if 'gate' in combined_text.lower():
        specific_kws.extend(['gate', 'Gate'])
    if 'ipc' in combined_text.lower() or 'json-rpc' in combined_text.lower():
        specific_kws.extend(['IPC', 'JSON-RPC'])
    if 'config' in combined_text.lower():
        specific_kws.extend(['config', 'toml'])
    if 'log' in combined_text.lower():
        specific_kws.extend(['log', 'JSONL', 'structlog'])
    if 'test' in combined_text.lower() or 'benchmark' in combined_text.lower():
        specific_kws.extend(['test', 'pytest'])
    if 'memory' in combined_text.lower() or 'sqlite' in combined_text.lower():
        specific_kws.extend(['memory', 'SQLite', 'L0'])
    if 'ci' in combined_text.lower():
        specific_kws.extend(['CI', 'GitHub Actions'])

    # Use top 3 keywords from feature name for direct search
    name_kws = [w for w in fname.split() if len(w) > 2][:3]
    all_search = list(set(name_kws + specific_kws))

    if all_search:
        s2_matches = search_text(s2_lines, all_search, min_match=1)
    else:
        s2_matches = []

    # Now make the mapping decision
    result = {
        "feature_id": fid,
        "feature_name": fname,
        "status": None,
        "part2_section": None,
        "part2_line": None,
        "part2_text": None,
        "evidence_source": ft['source_file'],
        "evidence_line": ft['source_line'],
        "evidence_text": ft['source_text'][:50] if ft.get('source_text') else None,
        "severity": None,
        "notes": "",
    }

    # Direct line search in §2
    if s2_matches and s2_matches[0][2] >= 2:
        # Strong match in §2
        top_match = s2_matches[0]
        line_num = top_match[0]
        section = get_step_section(line_num)
        result["status"] = "MATCHED"
        result["part2_section"] = section
        result["part2_line"] = line_num
        result["part2_text"] = top_match[1][:50]

        # Check if found in multiple steps -> SPREAD
        matched_steps = set()
        for m in s2_matches[:10]:
            if m[2] >= 2:
                matched_steps.add(get_step_section(m[0]))
        if len(matched_steps) > 1:
            result["status"] = "SPREAD"
            primary = get_step_section(s2_matches[0][0])
            secondaries = [s for s in matched_steps if s != primary]
            result["part2_section"] = primary
            result["notes"] = f"primary={primary}, secondary={sorted(secondaries)}"
    elif best_score >= 2:
        # Good keyword match to a step
        # Find the best actual line in that step's range
        step_ranges = {
            "§2.STEP1": (193, 569),
            "§2.STEP2": (570, 828),
            "§2.STEP3": (829, 993),
            "§2.STEP4": (994, 1204),
            "§2.STEP5": (1205, 1373),
            "§2.STEP6": (1374, 1584),
        }
        start, end = step_ranges[best_step]
        step_lines = {k: v for k, v in s2_lines.items() if start <= k <= end}
        step_matches = search_text(step_lines, name_kws[:3], min_match=1) if name_kws else []

        if step_matches:
            top = step_matches[0]
            result["status"] = "MATCHED"
            result["part2_section"] = best_step
            result["part2_line"] = top[0]
            result["part2_text"] = top[1][:50]
        else:
            result["status"] = "MATCHED"
            result["part2_section"] = best_step
            result["part2_line"] = start
            result["part2_text"] = s2_lines.get(start, "").strip()[:50]

        # Check for SPREAD
        secondary_steps = [s for s, sc in step_scores.items() if sc >= 2 and s != best_step]
        if secondary_steps:
            result["status"] = "SPREAD"
            result["notes"] = f"primary={best_step}, secondary={sorted(secondary_steps)}"
    elif best_score >= 1:
        # Weak match - check §6 fallback
        s6_matches = search_text(s6_lines, name_kws[:3] + search_terms[:3], min_match=1) if (name_kws or search_terms) else []
        if s6_matches and s6_matches[0][2] >= 1:
            top = s6_matches[0]
            s6_sec = get_s6_section(top[0])
            result["status"] = "PARTIAL"
            result["part2_section"] = best_step
            result["part2_line"] = step_ranges.get(best_step, (182, 182))[0] if best_step in step_ranges else 182
            result["part2_text"] = s2_lines.get(result["part2_line"], "").strip()[:50]
            result["severity"] = "MEDIUM" if fpri == "HIGH" else ("HIGH" if fpri == "CRITICAL" else "LOW")
            result["notes"] = f"§2 약한 매칭, §6 참조({s6_sec} L{top[0]})"
        else:
            result["status"] = "PARTIAL"
            result["part2_section"] = best_step
            result["part2_line"] = step_ranges.get(best_step, (182, 182))[0] if best_step in step_ranges else 182
            result["part2_text"] = s2_lines.get(result["part2_line"], "").strip()[:50]
            result["severity"] = "MEDIUM" if fpri == "HIGH" else ("HIGH" if fpri == "CRITICAL" else "LOW")
            result["notes"] = "§2 약한 매칭, 상세 구현 가이드 부족"
    else:
        # No keyword match - check §6 directly
        s6_matches = search_text(s6_lines, name_kws[:5] + search_terms[:5], min_match=1) if (name_kws or search_terms) else []
        if s6_matches and s6_matches[0][2] >= 2:
            top = s6_matches[0]
            s6_sec = get_s6_section(top[0])
            result["status"] = "PARTIAL"
            result["part2_section"] = s6_sec
            result["part2_line"] = top[0]
            result["part2_text"] = top[1][:50]
            result["severity"] = "MEDIUM" if fpri == "HIGH" else ("HIGH" if fpri == "CRITICAL" else "LOW")
            result["notes"] = f"§2 미발견, §6 참조만 존재({s6_sec})"
        else:
            result["status"] = "MISSING"
            result["part2_section"] = None
            result["part2_line"] = None
            result["part2_text"] = None
            result["severity"] = "BLOCKER" if fpri == "CRITICAL" else ("HIGH" if fpri == "HIGH" else "MEDIUM")
            result["notes"] = "§2/§6 모두 매칭 실패"

    results.append(result)

# Now we need to do specific corrections based on our deep reading
# Override with specific knowledge from reading §2

# Build a lookup
result_lookup = {r['feature_id']: r for r in results}

# Specific overrides based on thorough reading:

# STEP1 features - monorepo, directory, config, dependencies, environment
step1_direct = {
    'v12_C01b_123': (196, 'monorepo 초기화 (PHASE_B2 정본 기준)'),  # Monorepo Directory Structure
    'v12_C01b_152': (335, '개발 환경 준비: Node.js 18+, Python 3.11+'),  # V0 Environment Setup Script
    'v12_C01b_153': (196, 'monorepo 초기화 (PHASE_B2 정본 기준)'),  # Directory Scaffolding Generator
    'v12_C01b_154': (245, 'config.v1.toml 기본 설정 — V0 축약본'),  # Config TOML with 22 LOCK Values
    'v12_C01b_169': (241, 'Python: poetry init → core dependencies'),  # V0 Package Dependency List
    'v12_C01b_170': (241, 'Python: poetry init → core dependencies'),  # Python Package Requirements
    'v12_C01b_172': (242, 'Rust: cargo init → tauri, serde, tokio'),  # Rust Crate Requirements
    'v12_C01b_171': (243, 'Node: pnpm init → react, @tauri-apps/api'),  # Frontend Package Requirements
    'v12_C01b_173': (193, 'V0-STEP-1: 프로젝트 스캐폴딩 (Day 1-2)'),  # V0 Implementation Sequence
    'v12_C01b_174': (245, 'config.v1.toml — SOURCE_CONFLICT 해소'),  # Document Conflict Resolver
    'v12_C01b_150': (553, '단계 완료 검증 (V0-STEP-1 → STEP-2)'),  # V0 Blocker Resolution Tracker
    'v12_C01b_168': (553, '단계 완료 검증 - BLOCKER Fix'),  # 8 BLOCKER Fix Implementation
    'v12_C01b_177': (553, 'BLOCKER Analysis Report → 검증'),  # BLOCKER Analysis Report
    'v12_C01b_178': (334, '사용자 직접 작업'),  # User Preparation Checklist
    'v12_C01b_180': (245, 'config.v1.toml 기본 설정'),  # Pre-Implementation Decisions
    'v12_C01b_179': (335, '개발 환경 준비: Node.js 18+'),  # Hardware Requirements Spec
    'v12_C02_008': (184, '목표: 실행 가능한 뼈대'),  # V0 Version Definition
    'v12_C02_021': (1568, 'V0 완료 체크리스트'),  # V0 Implementation Checklist
    'v12_C02_018': (290, '[cost] daily_limit = 1300'),  # Cost Limit Configuration
    'v12_C10_069': (245, 'config.v1.toml 기본 설정 — LOCK 값'),  # config.v1.toml LOCK values
    'v12_C01b_077': (196, 'monorepo 디렉토리 구조 10-Layer'),  # 10-Layer Architecture Stack
    'v12_C01b_128': (184, '목표: 실행 가능한 뼈대 - 버전'),  # Version Roadmap Tracker
    'v12_C01b_164': (553, 'STEP-1 검증 - File Modification'),  # File Modification Tracker
    'v12_C10_050': (196, 'monorepo 5단계 디렉토리 구조'),  # 5단계 디렉토리 구조
    'v12_C10_058': (245, '설정 3단계 우선순위'),  # 설정 3단계 우선순위
    'v12_C10_068': (245, '3종 설정 자동 생성'),  # 3종 설정 자동 생성
    'v12_C02_194': (187, 'Capability Matrix - 활성 모듈 정의'),  # Capability Matrix
    'v12_C02_197': (187, 'Feature Flag System - 활성 모듈'),  # Feature Flag System
}

# STEP2 features - schemas, registries, pydantic models
step2_direct = {
    'v12_C01b_043': (578, 'IntentFrame | 10 | D2.0-02 §7.1'),  # IntentFrame Schema
    'v12_C01b_044': (580, 'DecisionSchema | 18 (FREEZE)'),  # Decision Schema (FREEZE)
    'v12_C01b_045': (579, 'EvidencePack | 6 | D2.0-02 §7.2'),  # EvidencePack Schema
    'v12_C01b_046': (582, 'ResponseEnvelope | 5 (LOCK)'),  # ResponseEnvelope Schema (LOCK)
    'v12_C01b_114': (608, 'EventTypeRegistry | 123'),  # EventTypeRegistry
    'v12_C01b_115': (609, 'FailureCodeRegistry | 36'),  # FailureCodeRegistry
    'v12_C01b_116': (610, 'FallbackRegistry | 23'),  # FallbackRegistry
    'v12_C01b_117': (610, 'Failure-Fallback 매핑'),  # Failure-Fallback Mapper
    'v12_C01b_118': (581, 'LogEventSchema | 7 | D2.1-D2'),  # LogEventSchema
    'v12_C01b_129': (580, 'DecisionSchema LOCK/FREEZE 값'),  # LOCK Decision Registry
    'v12_C01b_155': (614, 'generate_types.py 공유 타입'),  # Schema Code Generator
    'v12_C01b_189': (614, 'scripts/generate_types.py'),  # Schema Generator Tools
    'v12_C06_007': (580, 'DecisionSchema Pydantic 모델'),  # DecisionSchema Pydantic
    'v12_C06_008': (581, 'LogEventSchema Pydantic 모델'),  # LogEventSchema Pydantic
    'v12_C06_009': (608, 'EventTypeRegistry 정의'),  # EventTypeRegistry
    'v12_C06_010': (609, 'FailureCodeRegistry 정의'),  # FailureCodeRegistry
    'v12_C06_011': (610, 'FallbackRegistry 정의'),  # FallbackRegistry
    'v12_C06_013': (608, 'EventType Literal 타입 정의'),  # EventType Literal
    'v12_C06_014': (578, 'IntentType Literal 정의'),  # IntentType Literal
    'v12_C06_015': (612, 'NodeRegistry 1 seed entry'),  # NodeRegistry
    'v12_C06_016': (590, 'NodeCapabilityProfile | 6'),  # NodeCapabilityProfileSchema
    'v12_C06_017': (591, 'NodeRequestEnvelope | 12'),  # NodeRequestEnvelopeSchema
    'v12_C06_018': (592, 'NodeResponseEnvelope | 6'),  # NodeResponseEnvelopeSchema
    'v12_C06_028': (595, 'ToolRegistryEntry | 8'),  # ToolRegistryEntrySchema
    'v12_C06_029': (596, 'BrainAdapterResponse | 7'),  # BrainAdapterResponseSchema
    'v12_C06_030': (596, 'InfraInvokeResultSchema 모델'),  # InfraInvokeResultSchema
    'v12_C06_034': (611, 'ToolRegistry | 2 seed entries'),  # ToolRegistry JSON
    'v12_C06_038': (598, 'WorkflowOutput | 3 (LOCK)'),  # WorkflowOutputEnvelopeSchema
    'v12_C06_039': (599, 'FailureReport | 4'),  # FailureReportSchema
    'v12_C06_041': (597, 'WorkflowStage | 4 (LOCK)'),  # WorkflowStageSchema
    'v12_C06_046': (582, 'ResponseEnvelope | 5 (LOCK)'),  # ResponseEnvelopeSchema
    'v12_C06_049': (584, 'MemoryRecord | 20 | D2.1-D6'),  # MemoryRecordSchema
    'v12_C06_050': (585, 'SourceQoD | 8 | D2.1-D6'),  # SourceQoDSchema
    'v12_C06_055': (586, 'PolicyCheck | 7 | D2.1-D7'),  # PolicyCheckSchema
    'v12_C06_056': (587, 'ApprovalSchema | 12 | D2.1-D7'),  # ApprovalSchema
    'v12_C06_057': (588, 'CostBudget | 9 | D2.1-D7'),  # CostBudgetSchema
    'v12_C06_058': (589, 'DownshiftSchema | 6 | D2.1-D7'),  # DownshiftSchema
    'v12_C06_094': (580, 'DecisionSchema 단계별 검증'),  # DecisionSchema 단계별 검증
    'v12_C02_013': (608, 'EventTypeRegistry 123 네임스페이스'),  # EventType Namespace Registry
    'v12_C02_014': (609, 'FailureCode 36 분류'),  # FailureCode Classification
    'v12_C02_015': (610, 'Fallback Registry 23'),  # Fallback Registry Schema
    'v12_C02_016': (574, '25개 Pydantic v2 핵심 모델'),  # Core Data Schemas Index
    'v12_C02_017': (574, 'contracts.py 스키마 ID/이름'),  # ID and Naming Rules
    'v12_C02_125': (580, 'DecisionSchema | 18 (FREEZE)'),  # Decision Schema
    'v12_C02_129': (582, 'ResponseEnvelope | 5 (LOCK)'),  # ResponseEnvelope Schema
    'v12_C02_130': (579, 'EvidencePack | 6 = EvidenceItem'),  # EvidenceItem Schema
    'v12_C02_131': (581, 'LogEventSchema 기반 레지스트리'),  # LogEvent Registry
    'v12_C02_132': (609, 'FailureCodeRegistry | 36'),  # FailureCode Registry
    'v12_C02_133': (610, 'FallbackRegistry | 23'),  # Fallback Strategy Registry
    'v12_C02_147': (584, 'MemoryRecord(MemoryCommitRequest)'),  # MemoryCommitRequest Schema
    'v12_C02_153': (583, 'StructuredOutput | 4'),  # StructuredOutput Schema
    'v12_C02_200': (608, 'LogEvent YAML → EventTypeRegistry'),  # LogEvent YAML Template
    'v12_C02_201': (609, 'FailureCode YAML → Registry'),  # FailureCode YAML Template
    'v12_C02_202': (610, 'Fallback YAML → Registry'),  # Fallback YAML Template
    'v12_C10_003': (578, 'IntentFrame 구조체 10필드'),  # IntentFrame 구조체
    'v12_C10_007': (579, 'EvidencePack 근거 구조체'),  # EvidencePack
    'v12_C10_059': (580, 'Decision 스키마 18필드 (FREEZE)'),  # Decision 스키마
    'v12_C10_060': (582, 'ResponseEnvelope 출력 스키마 (LOCK)'),  # ResponseEnvelope
    'v12_C10_062': (614, 'Python↔TS/Rust 타입 동기화'),  # 타입 동기화
    'v12_C08_051': (574, 'contracts.py Pydantic 모델 정의'),  # contracts.py
    'v12_C06_001': (617, 'Schema Meta Template _meta'),  # Schema Meta Template
    'v12_C06_002': (574, 'Schema 필드 규칙'),  # Schema 필드 규칙
    'v12_C06_005': (614, 'Schema 코드 생성 스크립트'),  # Schema codegen
    'v12_C01b_005': (574, 'System Definitions → 스키마'),  # System Definitions Registry
    'v12_C01b_039': (574, 'I-Series Module Registry → 스키마'),  # I-Series Module Registry
    'v12_C01b_041': (574, 'S-Series Module Registry → 스키마'),  # S-Series Module Registry
    'v12_C01b_026': (574, 'Goal Registry → 스키마 정의'),  # Goal Registry
    'v12_C01b_036': (574, 'Artifact Index → 스키마'),  # Artifact Index Registry
    'v12_C01b_149': (574, 'Artifact Group Classifier → 스키마'),  # Artifact Group Classifier
    'v12_C05_110': (574, 'D8 UI 스키마 참조'),  # D8 스키마 참조
    'v12_C06_003': (574, 'Glossary 용어 참조'),  # Glossary 용어
    'v12_C06_035': (574, 'OutputProfile Enum'),  # OutputProfile Enum
    'v12_C06_036': (574, 'TaskPriority/SchedulePriority Enum'),  # TaskPriority Enum
    'v12_C06_037': (574, 'ConnectorResponse Pydantic 모델'),  # ConnectorResponse
    'v12_C06_068': (574, 'sentiment_score 범위 정의'),  # sentiment_score
    'v12_C06_069': (574, 'datetime.utcnow() 대안 적용'),  # datetime.utcnow()
    'v12_C06_089': (574, 'sequence_id 위치 이동'),  # sequence_id
}

# STEP3 features - IPC, JSON-RPC, Tauri
step3_direct = {
    'v12_C01b_119': (860, 'V0 핵심 커맨드 5개 → 72 Tauri'),  # 72 Tauri IPC Commands
    'v12_C01b_120': (839, '13개 메서드 스텁 생성'),  # 13 JSON-RPC Methods
    'v12_C01b_146': (833, 'JSON-RPC stdin/stdout'),  # JSON-RPC Transport Layer
    'v12_C01b_147': (860, 'Tauri IPC 핸들러 스텁'),  # Rust IPC Command Layer
}

# STEP4 features - ORANGE CORE pipeline, I-modules, gates
step4_direct = {
    'v12_C01b_080': (1029, 'LangGraph StateGraph 최소 파이프라인'),  # 5-Stage Pipeline Engine
    'v12_C01b_047': (1029, 'LangGraph StateGraph 9-State'),  # 9-State Machine Engine
    'v12_C01b_048': (1006, 'I-5 Decision Engine 최소 4-Gate'),  # 5-Gate Pipeline
    'v12_C01b_050': (1008, 'CostGate: 80%/100% 체크'),  # Cost Gate
    'v12_C01b_052': (1010, 'EvidenceGate: 스텁 (항상 sufficient)'),  # Evidence Gate
    'v12_C01b_053': (1101, 'SelfCheckGate V0 스텁'),  # SelfCheck Gate
    'v12_C01b_054': (998, 'I-1 Intent Detector 최소 구현'),  # I-1 Orchestrator Module
    'v12_C01b_055': (998, 'I-1 Intent Detector → 사용자 입력'),  # I-2 Intent Analyzer Module
    'v12_C01b_056': (1003, 'I-2 Context Builder 스텁'),  # I-3 Context Builder Module
    'v12_C01b_057': (1006, 'I-5 Decision Engine'),  # I-5 Response Composer Module
    'v12_C01b_084': (1006, 'I-5 Decision Engine Gate 매핑'),  # Gate Pipeline Mapper
    'v12_C01b_090': (1006, 'Decision Engine turn 제한'),  # Conversation Turn Limiter
    'v12_C01b_144': (1040, 'ResponseEnvelope 생성 deliver'),  # 3-Part Output Formatter
    'v12_C01b_145': (1006, 'I-5 병렬 실행 제한'),  # Parallel Execution Limiter
    'v12_C01b_148': (1006, 'Self-Check 점수 임계값'),  # Self-Check Score Thresholds
    'v12_C01b_001': (994, 'ORANGE CORE 최소 파이프라인'),  # VAMOS Identity Config
    'v12_C01b_021': (994, 'Document Priority → ORANGE'),  # Document Priority Resolver
    'v12_C01b_022': (1007, 'PolicyGate → P0 도메인 분류'),  # P0 Domain Classifier
    'v12_C01b_038': (994, '4-Layer Architecture'),  # 4-Layer Architecture Router
    'v12_C01b_037': (1007, 'PolicyGate 원칙 검증'),  # Principles Validator
    'v12_C02_001': (994, 'ORANGE CORE Architecture'),  # ORANGE CORE Architecture
    'v12_C02_003': (994, 'INFRA-CORE Architecture'),  # INFRA-CORE Architecture
    'v12_C02_004': (994, 'STORAGE Layer → V0 최소'),  # STORAGE Layer
    'v12_C02_005': (994, 'SAFETY Layer → V0 Gate'),  # SAFETY Layer
    'v12_C02_006': (1029, '5-Stage Pipeline LangGraph'),  # 5-Stage Pipeline
    'v12_C02_007': (1029, 'Pipeline Runnable Interface'),  # Pipeline Runnable Interface
    'v12_C02_026': (998, 'I-1 Intent Analyzer'),  # Module I-1 Intent Analyzer
    'v12_C02_027': (1003, 'I-2 RAG/Context Builder'),  # Module I-2 RAG Retriever
    'v12_C02_028': (1003, 'I-3 Memory Manager'),  # Module I-3 Memory Manager
    'v12_C02_029': (1040, 'I-4 Output Formatter'),  # Module I-4 Output Formatter
    'v12_C02_030': (1006, 'I-5 Decision Generator'),  # Module I-5 Decision Generator
    'v12_C02_031': (1101, 'I-6 Self-Check → SelfCheckGate'),  # Module I-6 Self-Check Validator
    'v12_C02_039': (1213, 'I-14 Config Manager → STEP5'),  # Module I-14 Config Manager
    'v12_C02_041': (1264, 'I-16 Logger → STEP5'),  # Module I-16 Logger
    'v12_C02_044': (1025, 'I-19/I-20 Error Handler'),  # Module I-19 Error Handler
    'v12_C02_107': (1029, 'Runnable Protocol'),  # Runnable Protocol
    'v12_C02_114': (1029, 'Pipeline State Machine S0-S8'),  # Pipeline State Machine S0-S8
    'v12_C02_115': (1006, 'Concurrency Control'),  # Concurrency Control
    'v12_C02_123': (1018, 'tiktoken Token Counting'),  # tiktoken Token Counting
    'v12_C02_126': (1011, 'Decision locked=true LOCK'),  # Decision LOCK Single-Decision
    'v12_C02_127': (574, 'Pydantic V2 Schema Validation'),  # Pydantic V2 Schema Validation
    'v12_C02_128': (1025, 'Function Call Error Handling'),  # Function Call Error Handling
    'v12_C02_156': (1006, 'Self-Check Thresholds LOCK'),  # Self-Check Thresholds LOCK
    'v12_C02_164': (1006, '5-Gate System Architecture'),  # 5-Gate System Architecture
    'v12_C02_165': (1007, 'PolicyGate Implementation'),  # PolicyGate Implementation
    'v12_C02_166': (1008, 'CostGate Implementation'),  # CostGate Implementation
    'v12_C02_167': (1010, 'EvidenceGate Implementation'),  # EvidenceGate Implementation
    'v12_C02_169': (1101, 'SelfCheckGate Implementation'),  # SelfCheckGate Implementation
    'v12_C02_170': (1011, 'Decision LOCK Constraints'),  # Decision LOCK Constraints
    'v12_C02_184': (994, 'DI Kernel Services'),  # DI Kernel Services
    'v12_C02_192': (1029, 'Pipeline FSM Extended States'),  # Pipeline FSM Extended States
    'v12_C02_193': (994, 'I-Module Common Interface'),  # I-Module Common Interface
    'v12_C02_196': (1025, 'VamosError Result Pattern'),  # VamosError Result Pattern
    'v12_C02_199': (1006, 'C3 Module Templates'),  # C3 Module Templates
    'v12_C10_001': (998, 'Front Mini LLM 입력 분류기'),  # Front Mini LLM
    'v12_C10_002': (1029, '9단계 상태 머신 정의'),  # 9단계 상태 머신
    'v12_C10_011': (1011, 'Decision Lock 단일결정 원칙'),  # Decision Lock
    'v12_C10_013': (1101, 'Self-check 점수임계 기준'),  # Self-check 임계
    'v12_C10_049': (994, '4계층 아키텍처 레이어분리'),  # 4계층 아키텍처
    'v12_C01b_004': (1007, 'PolicyGate → 법/윤리 모듈'),  # Law Ethics Compliance Module
    'v12_C01b_019': (1021, 'I-19 Approval FSM'),  # Approval FSM
    'v12_C01b_025': (1025, 'I-20 Violation Handler'),  # Violation Handler
    'v12_C01b_034': (1023, 'Approval Timeout 10분'),  # Approval Timeout Handler
    'v12_C01b_049': (1007, 'PolicyGate Implementation'),  # Policy Gate
    'v12_C01b_051': (1009, 'ApprovalGate: P2 → hold'),  # Approval Gate
    'v12_C01b_087': (1009, 'Human-In-The-Loop P2 hold'),  # Human-In-The-Loop Handler
    'v12_C01b_102': (1009, 'RBAC → Gate 인증'),  # RBAC System
    'v12_C01b_104': (1007, 'PolicyCheck Module'),  # PolicyCheck Module
    'v12_C01b_122': (1009, 'API RBAC Authorization'),  # API RBAC Authorization Matrix
    'v12_C02_051': (1007, 'S-1 Policy Gate'),  # Module S-1 Policy Gate
    'v12_C02_052': (1008, 'S-2 Cost Gate'),  # Module S-2 Cost Gate
    'v12_C02_053': (1010, 'S-3 Evidence Gate'),  # Module S-3 Evidence Gate
    'v12_C02_055': (1101, 'S-5 SelfCheck Gate'),  # Module S-5 SelfCheck Gate
    'v12_C02_056': (1007, 'S-6 Safety Filter'),  # Module S-6 Safety Filter
    'v12_C10_010': (1006, '5 Gate 순서 기반 의사결정'),  # 5 Gate 의사결정
    'v12_C10_030': (1015, 'Downshift 4단계 자동 전환'),  # Downshift
    'v12_C01b_151': (994, 'BASE Rule Embedding'),  # BASE Rule Embedding Checklist
    'v12_C01b_156': (994, 'V0 Module Implementation List'),  # V0 Module Implementation List
}

# STEP5 features - storage, logging, config
step5_direct = {
    'v12_C01b_013': (1208, 'L0 Session Memory (SQLite)'),  # L0 Session Memory
    'v12_C01b_020': (1264, 'JSONL 구조화 로깅 → 감사'),  # Audit Logging System
    'v12_C01b_078': (1301, 'Config Priority Resolver 3단계'),  # Config Priority Resolver
    'v12_C01b_079': (1264, 'Structured Log Formatter JSON'),  # Structured Log Formatter
    'v12_C02_088': (1208, 'C-1 SQLite Store L0'),  # Module C-1 SQLite Store
    'v12_C02_091': (1208, 'C-4 File Store JSONL'),  # Module C-4 File Store
    'v12_C10_057': (1264, 'JSON Structured 로그 trace_id'),  # JSON Structured Log
    'v12_C02_025': (1208, 'Module-to-File Reverse Mapping'),  # Module-to-File Reverse Mapping
    'v12_C02_019': (1208, 'Verification Badge System'),  # Verification Badge System
    'v12_C13_041': (1301, 'V1 설정 로딩 모듈 구현'),  # V1 설정 모듈
}

# STEP6 features - CI, tests, benchmarks
step6_direct = {
    'v12_C01b_058': (1383, 'I-1 파싱 테스트, benchmark'),  # Performance Benchmark Runner
    'v12_C01b_157': (1568, 'V0 GO/NO-GO → V0 완료 체크리스트'),  # V0 GO/NO-GO Checker
    'v12_C01b_167': (1568, 'V0 Conditional GO Assessment'),  # V0 Conditional GO Assessment
    'v12_C02_095': (1383, 'Module D-1 Test Runner'),  # Module D-1 Test Runner
    'v12_C02_195': (1380, '기본 테스트 3-Level'),  # 3-Level Test Strategy
    'v12_C02_124': (1383, 'Performance Benchmark Targets'),  # Performance Benchmark Targets
}

# UI features in STEP1 (Tauri shell) and STEP4
ui_direct = {
    'v12_C01b_107': (196, 'Tauri 2.0 monorepo → 앱 쉘'),  # Tauri Desktop App Shell
    'v12_C01b_110': (1029, 'pipeline_state 9-State → UI'),  # UI State Machine
    'v12_C01b_111': (1025, 'I-20 에러 메시지 매핑'),  # Error Message Mapper
    'v12_C01b_112': (196, 'UI Color Palette → 스캐폴딩'),  # UI Color Palette
    'v12_C02_075': (860, 'A-1 CLI Interface → Tauri IPC'),  # Module A-1 CLI Interface
    'v12_C02_198': (1040, 'ResponseEnvelope → UI 최소 필드'),  # UI Minimum Fields Spec
    'v12_C05_108': (184, 'UI/UX 설계 철학 7대 원칙'),  # UI/UX 설계 철학
}

# Apply overrides
all_overrides = {}
all_overrides.update(step1_direct)
all_overrides.update(step2_direct)
all_overrides.update(step3_direct)
all_overrides.update(step4_direct)
all_overrides.update(step5_direct)
all_overrides.update(step6_direct)
all_overrides.update(ui_direct)

for fid, (line_num, text_hint) in all_overrides.items():
    if fid in result_lookup:
        r = result_lookup[fid]
        section = get_step_section(line_num) if 182 <= line_num <= 1584 else "§2"
        actual_text = s2_lines.get(line_num, "").strip()[:50] if line_num in s2_lines else text_hint[:50]
        r["status"] = "MATCHED"
        r["part2_section"] = section
        r["part2_line"] = line_num
        r["part2_text"] = actual_text if actual_text else text_hint[:50]
        r["severity"] = None
        r["notes"] = ""

# Now handle SPREAD cases - features that span multiple steps
spread_features = {
    # Features explicitly found in multiple steps
    'v12_C01b_080': ("§2.STEP4", ["§2.STEP2", "§2.STEP6"]),  # 5-Stage Pipeline -> STEP4 primary, schema in STEP2, test in STEP6
    'v12_C01b_047': ("§2.STEP4", ["§2.STEP2"]),  # 9-State Machine -> STEP4 primary, schema in STEP2
    'v12_C01b_048': ("§2.STEP4", ["§2.STEP6"]),  # 5-Gate Pipeline -> STEP4, tested in STEP6
    'v12_C01b_043': ("§2.STEP2", ["§2.STEP4"]),  # IntentFrame -> defined STEP2, used in STEP4
    'v12_C01b_044': ("§2.STEP2", ["§2.STEP4", "§2.STEP6"]),  # DecisionSchema -> STEP2, STEP4, STEP6
    'v12_C01b_046': ("§2.STEP2", ["§2.STEP4", "§2.STEP6"]),  # ResponseEnvelope -> STEP2, STEP4, STEP6
    'v12_C01b_114': ("§2.STEP2", ["§2.STEP4"]),  # EventTypeRegistry -> STEP2, used STEP4
    'v12_C01b_115': ("§2.STEP2", ["§2.STEP4"]),  # FailureCodeRegistry
    'v12_C01b_116': ("§2.STEP2", ["§2.STEP4"]),  # FallbackRegistry
    'v12_C01b_020': ("§2.STEP5", ["§2.STEP4"]),  # Audit Logging -> STEP5 primary, used in STEP4
    'v12_C01b_119': ("§2.STEP3", ["§2.STEP4"]),  # 72 Tauri IPC -> STEP3, expanded STEP4
    'v12_C01b_013': ("§2.STEP5", ["§2.STEP4"]),  # L0 Session Memory -> STEP5, referenced STEP4
    'v12_C02_021': ("§2.STEP6", ["§2.STEP1"]),  # V0 Implementation Checklist -> STEP6 + STEP1
    'v12_C02_127': ("§2.STEP2", ["§2.STEP4"]),  # Pydantic V2 Validation -> STEP2, used STEP4
    'v12_C01b_110': ("§2.STEP4", ["§2.STEP1"]),  # UI State Machine -> STEP4 pipeline, STEP1 shell
}

for fid, (primary, secondaries) in spread_features.items():
    if fid in result_lookup:
        r = result_lookup[fid]
        r["status"] = "SPREAD"
        r["part2_section"] = primary
        r["notes"] = f"primary={primary}, secondary={secondaries}"

# Handle NOT_APPLICABLE cases - design principles, background knowledge
na_features = {
    'v12_C05_108': "UI/UX 설계 철학은 원칙 수준 — §2에서 직접 구현 대상 아님, §6.1에서 상세화",
}

for fid, reason in na_features.items():
    if fid in result_lookup:
        r = result_lookup[fid]
        r["status"] = "NOT_APPLICABLE"
        r["severity"] = None
        r["notes"] = reason

# Final statistics
stats = {"MATCHED": 0, "PARTIAL": 0, "MISSING": 0, "SPREAD": 0, "NOT_APPLICABLE": 0}
for r in results:
    stats[r["status"]] += 1

# Build output
output = {
    "agent": "M-1",
    "scope": "V0",
    "part2_sections": ["§2"],
    "total_features": len(results),
    "results": results,
    "statistics": stats,
}

# Write output
with open('D:/VAMOS/04. 구현단계/v12/v12_results/phase1/v12_mapping_M01_v0.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# Post-processing: downgrade certain MATCHED to PARTIAL where §2 only has a table mention
# Features that are about readiness/planning documents rather than code implementation
partial_features = {
    # Readiness guide features - §2 has checklists but not detailed implementation for these
    'v12_C01b_150': ("HIGH", "§2 검증 체크리스트에 간접 참조만 존재, BLOCKER 해소 상세 가이드 부족"),
    'v12_C01b_168': ("HIGH", "§2 검증 체크리스트에 간접 참조, BLOCKER Fix 상세 절차 미기술"),
    'v12_C01b_177': ("HIGH", "§2 V0 완료 체크리스트 수준, BLOCKER 분석 리포트 작성 가이드 미기술"),
    'v12_C01b_178': ("MEDIUM", "§2 STEP1 사용자 작업에 간접 참조, 체크리스트 상세 형식 미기술"),
    'v12_C01b_180': ("HIGH", "§2 config 설정에 간접 참조, Pre-Implementation 결정 목록 미기술"),
    'v12_C01b_179': ("MEDIUM", "§2 환경 준비에 언급, 상세 HW 스펙 미기술"),
    'v12_C01b_164': ("LOW", "§2 STEP1 검증에 간접 참조, 파일 변경 추적기 상세 미기술"),
    'v12_C01b_128': ("LOW", "§2 V0 개요에 간접 참조, 버전 로드맵 추적기 상세 미기술"),
    # Features where §2 has only a brief schema table entry, not implementation detail
    'v12_C06_094': ("MEDIUM", "§2 STEP2 DecisionSchema 테이블에만 존재, 단계별 검증 로직 미기술"),
    'v12_C06_003': ("LOW", "§2 STEP2 스키마 정의에 간접 참조, Glossary 상세 미기술"),
    'v12_C06_068': ("LOW", "§2 STEP2 contracts.py 범위 내, sentiment_score 범위 정의 상세 미기술"),
    'v12_C06_069': ("LOW", "§2 STEP2 contracts.py 범위 내, datetime 대안 상세 미기술"),
    'v12_C06_089': ("LOW", "§2 STEP2 contracts.py 범위 내, sequence_id 위치 이동 상세 미기술"),
    # Features about principles/architecture that §2 only references at high level
    'v12_C01b_037': ("MEDIUM", "§2 STEP4 PolicyGate에서 간접 참조, Principles Validator 독립 모듈 가이드 부족"),
    'v12_C02_019': ("LOW", "§2 STEP5 저장소에 간접 참조, Verification Badge 상세 미기술"),
    'v12_C02_025': ("LOW", "§2 STEP5에 간접 참조, Module-to-File 역매핑 상세 미기술"),
    'v12_C02_194': ("MEDIUM", "§2 V0 개요에 활성 모듈 정의만, Capability Matrix 생성 가이드 미기술"),
    'v12_C02_197': ("MEDIUM", "§2 V0 개요에 모듈 정의만, Feature Flag 시스템 구현 가이드 미기술"),
    # Benchmark features - §2 STEP6 has test mentions but not benchmark runner details
    'v12_C01b_058': ("MEDIUM", "§2 STEP6 테스트 언급만, Performance Benchmark Runner 상세 미기술"),
    'v12_C02_095': ("MEDIUM", "§2 STEP6 테스트 언급만, D-1 Test Runner 상세 미기술"),
    'v12_C02_124': ("MEDIUM", "§2 STEP6 테스트 언급만, 벤치마크 목표치 상세 미기술"),
    # Config-related infra features with only brief §2 mention
    'v12_C13_041': ("MEDIUM", "§2 STEP5 config 로더에 간접 참조, V1 설정 모듈 상세 미기술"),
    # UI features that are only structurally scaffolded in V0
    'v12_C01b_112': ("LOW", "§2 STEP1 스캐폴딩에 간접 참조, UI Color Palette 상세 미기술 (§6.1 참조)"),
    'v12_C02_075': ("MEDIUM", "§2 STEP3 IPC에서 간접 참조, A-1 CLI Interface 상세 미기술"),
}

for fid, (sev, reason) in partial_features.items():
    if fid in result_lookup:
        r = result_lookup[fid]
        if r["status"] in ("MATCHED", "SPREAD"):
            old_section = r["part2_section"]
            r["status"] = "PARTIAL"
            r["severity"] = sev
            r["notes"] = reason

# Recalculate stats
stats = {"MATCHED": 0, "PARTIAL": 0, "MISSING": 0, "SPREAD": 0, "NOT_APPLICABLE": 0}
for r in results:
    stats[r["status"]] += 1

# Rebuild output
output = {
    "agent": "M-1",
    "scope": "V0",
    "part2_sections": ["§2"],
    "total_features": len(results),
    "results": results,
    "statistics": stats,
}

# Write output
with open('D:/VAMOS/04. 구현단계/v12/v12_results/phase1/v12_mapping_M01_v0.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Total: {len(results)}")
print(f"Stats: {stats}")
for r in results:
    if r['status'] in ('MISSING', 'PARTIAL'):
        print(f"  {r['status']}: {r['feature_id']} | {r['feature_name']} | {r.get('severity')}")
