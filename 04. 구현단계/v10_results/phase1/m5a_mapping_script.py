#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M-5a Agent: §6.1~§6.7 Feature → PART2 매핑 검증
- Feature Registry 전체 3940건 vs PART2 §6.1~§6.7 (lines 2848~3165)
- M-1~M-4 MISSING 항목 재확인
"""

import json
import re
import sys
import os
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ============================================================
# 1. PART2 §6.1~§6.7 로드 및 키워드 인덱스 구축
# ============================================================

PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
REGISTRY_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json"
LAYER1_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase0-b\v10_layer1_claude_features.json"
OUTPUT_DIR = r"D:\VAMOS\04. 구현단계\v10_results\phase1"

# §6.1~§6.7 범위
S6_START = 2848  # "# 6. 시스템별 상세 구현 가이드"
S6_END = 3165    # §6.7 끝 (§6.8 직전)

# 서브섹션 정의
SUBSECTIONS = {
    "§6.1": {"name": "UI/UX 상세", "start": 2854, "end": 2957},
    "§6.1.1": {"name": "핵심 레이아웃", "start": 2856, "end": 2864},
    "§6.1.2": {"name": "React 컴포넌트", "start": 2865, "end": 2880},
    "§6.1.3": {"name": "Custom Hooks + Stores", "start": 2881, "end": 2889},
    "§6.1.4": {"name": "구현 중 결정 항목", "start": 2890, "end": 2900},
    "§6.1.5": {"name": "멀티모달 UI", "start": 2901, "end": 2914},
    "§6.1.6": {"name": "UI State Machine", "start": 2915, "end": 2936},
    "§6.1.7": {"name": "Failure/Fallback UI", "start": 2937, "end": 2947},
    "§6.1.8": {"name": "UI 접근 제어 RBAC", "start": 2948, "end": 2957},
    "§6.2": {"name": "Rust/Tauri 인프라", "start": 2959, "end": 2992},
    "§6.2.1": {"name": "Tauri IPC 커맨드 핸들러", "start": 2961, "end": 2970},
    "§6.2.2": {"name": "Python-Rust JSON-RPC", "start": 2971, "end": 2981},
    "§6.2.3": {"name": "Rust 핵심 모듈", "start": 2983, "end": 2992},
    "§6.3": {"name": "테스트", "start": 2994, "end": 3023},
    "§6.4": {"name": "CI/CD", "start": 3026, "end": 3046},
    "§6.5": {"name": "보안", "start": 3049, "end": 3068},
    "§6.6": {"name": "MCP 서버/클라이언트", "start": 3071, "end": 3101},
    "§6.7": {"name": "Agent Teams 상세 구현", "start": 3103, "end": 3165},
}

def load_part2_section():
    """§6.1~§6.7 전문 로드 (행번호 보존)"""
    with open(PART2_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    section_lines = {}  # line_num -> content
    for i in range(S6_START - 1, min(S6_END, len(lines))):
        section_lines[i + 1] = lines[i].rstrip()
    return section_lines

def build_keyword_index(section_lines):
    """§6 내 키워드 → 행번호 역인덱스"""
    index = defaultdict(list)  # keyword -> [(line_num, subsection)]

    for line_num, content in section_lines.items():
        subsec = find_subsection(line_num)
        # 각 행에서 의미 있는 토큰 추출
        tokens = extract_tokens(content)
        for token in tokens:
            index[token.lower()].append((line_num, subsec))
    return index

def find_subsection(line_num):
    """행번호로 서브섹션 판별"""
    best = "§6"
    best_start = 0
    for sec_id, info in SUBSECTIONS.items():
        if info["start"] <= line_num <= info["end"] and info["start"] > best_start:
            best = sec_id
            best_start = info["start"]
    return best

def extract_tokens(text):
    """텍스트에서 검색 가능한 토큰 추출"""
    # 한글 + 영문 + 숫자 + 하이픈 조합
    tokens = set()
    # 영문/숫자/하이픈 토큰
    for m in re.finditer(r'[A-Za-z0-9_\-\.]+', text):
        t = m.group()
        if len(t) >= 2:
            tokens.add(t)
    # 한글 토큰 (2글자 이상)
    for m in re.finditer(r'[가-힣]+', text):
        t = m.group()
        if len(t) >= 2:
            tokens.add(t)
    # 모듈 ID 패턴 (I-1, E-7, D-3 등)
    for m in re.finditer(r'[A-Z]-\d+', text):
        tokens.add(m.group())
    # LOCK ID 패턴
    for m in re.finditer(r'LOCK-[A-Z]+-\d+', text):
        tokens.add(m.group())
    # D2.0-XX 참조
    for m in re.finditer(r'D2\.\d+-\d+', text):
        tokens.add(m.group())
    return tokens

# ============================================================
# 2. Feature Registry 로드
# ============================================================

def load_registry():
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['features']

# ============================================================
# 3. M-1~M-4 MISSING 항목 로드
# ============================================================

def load_missing_items():
    """M-1~M-4의 MISSING 항목 수집"""
    missing = []

    # M-1
    try:
        with open(os.path.join(OUTPUT_DIR, 'm1_v0_mapping_result.json'), 'r', encoding='utf-8') as f:
            m1 = json.load(f)
        for sev in ['BLOCKER','HIGH','MEDIUM','LOW']:
            for item in m1.get('missing_by_severity',{}).get(sev,[]):
                missing.append({
                    'feature_id': item['feature_id'],
                    'feature_name': item.get('feature_name',''),
                    'severity': sev,
                    'source_agent': 'M-1'
                })
    except: pass

    # M-2
    try:
        with open(os.path.join(OUTPUT_DIR, 'v10_m2_missing_items.json'), 'r', encoding='utf-8') as f:
            m2m = json.load(f)
        if isinstance(m2m, dict):
            for item in m2m.get('items', []):
                missing.append({
                    'feature_id': item.get('feature_id',''),
                    'feature_name': item.get('feature_name',''),
                    'severity': item.get('severity','MEDIUM'),
                    'source_agent': 'M-2'
                })
    except: pass

    # M-3
    try:
        with open(os.path.join(OUTPUT_DIR, 'v10_m3_missing_final.json'), 'r', encoding='utf-8') as f:
            m3m = json.load(f)
        if isinstance(m3m, dict):
            for item in m3m.get('items', []):
                missing.append({
                    'feature_id': item.get('feature_id',''),
                    'feature_name': item.get('feature_name',''),
                    'severity': item.get('severity','MEDIUM'),
                    'source_agent': 'M-3'
                })
        elif isinstance(m3m, list):
            for item in m3m:
                missing.append({
                    'feature_id': item.get('feature_id',''),
                    'feature_name': item.get('feature_name',''),
                    'severity': item.get('severity','MEDIUM'),
                    'source_agent': 'M-3'
                })
    except: pass

    # M-4
    try:
        with open(os.path.join(OUTPUT_DIR, 'v10_m4_missing_items.json'), 'r', encoding='utf-8') as f:
            m4m = json.load(f)
        if isinstance(m4m, dict):
            for item in m4m.get('items', []):
                missing.append({
                    'feature_id': item.get('feature_id',''),
                    'feature_name': item.get('feature_name',''),
                    'severity': item.get('severity','MEDIUM'),
                    'source_agent': 'M-4'
                })
    except: pass

    return missing

# ============================================================
# 4. 매핑 엔진
# ============================================================

# §6 핵심 키워드 → 섹션 매핑 (수동 정의: 확실한 매핑)
S6_DOMAIN_KEYWORDS = {
    # §6.1 UI/UX
    "§6.1": [
        "3-column", "layout", "builder view", "cockpit", "hologram",
        "react", "컴포넌트", "component", "decisioncard", "chatpanel",
        "userbubble", "aibubble", "thinkingblock", "artifactembed",
        "approvaldialog", "costdashboard", "budgetgauge", "tokencounter",
        "verificationbadge", "memorycandidatelist", "nodestatusbadge",
        "guardrailsalert", "modelselector", "keyboard shortcuts",
        "hooks", "stores", "usetauriipc", "usedecision", "useworkflow",
        "usememory", "usecost", "usenotification", "useautonomy", "uselog",
        "appstore", "decisionstore", "coststore", "notificationstore",
        "authstore", "memorystore", "workflowstore",
        "멀티모달", "multimodal", "clip", "ocr", "stt", "tts", "whisper",
        "tesseract", "pymupdf", "mermaid", "plotly", "edge tts",
        "ui state machine", "ui_s0", "ui_s1", "ui_s2", "ui_s3",
        "ui_s4", "ui_s5", "ui_s6", "ui_s7", "ui_s8",
        "failure", "fallback", "fm_err", "tl_err", "mc_err",
        "rbac", "owner", "admin", "operator", "viewer",
        "다크모드", "dark mode", "framer motion", "css",
        "이미지 입력", "음성 입력", "차트", "문서",
        "3d 생성", "비디오 스트리밍", "아바타", "디지털 휴먼",
        "음성 클로닝", "ar", "수어", "ppt",
        "computer use", "imagegengateway",
    ],
    # §6.2 Rust/Tauri
    "§6.2": [
        "tauri", "ipc", "커맨드 핸들러", "command handler",
        "json-rpc", "python-rust", "python_manager",
        "ipc_protocol", "config.rs", "serde",
        "vamos:decision", "vamos:workflow", "vamos:node",
        "vamos:pipeline", "vamos:memory", "vamos:vector",
        "vamos:policy", "vamos:cost", "vamos:ui",
        "langgraph.workflow", "langgraph.stage", "langgraph.decision",
        "langgraph.node", "langgraph.verify", "embedding.encode",
        "embedding.store", "llm.generate", "llm.record_invoke",
        "mcp.bridge", "mcp.tools.discover",
        "cargo", "clippy", "tarpaulin", "rust",
    ],
    # §6.3 테스트
    "§6.3": [
        "pytest", "cargo test", "vitest", "playwright",
        "unit test", "integration test", "e2e",
        "val-001", "val-002", "val-003", "val-004", "val-005",
        "val-006", "val-007", "val-008", "val-009", "val-010",
        "acceptance criteria", "커버리지", "coverage",
        "테스트 전략", "test strategy",
    ],
    # §6.4 CI/CD
    "§6.4": [
        "ci/cd", "ci.yml", "workflow", "github actions",
        "quality-python", "quality-rust", "quality-react",
        "quality-schema", "test-python", "test-rust", "test-react",
        "coverage-report", "build-tauri", "release",
        "security.yml", "build-docker", "deploy",
        "ruff", "mypy", "eslint", "tsc",
        "pip-audit", "cargo-audit", "npm audit",
        "helm", "blue-green", "docker compose",
    ],
    # §6.5 보안
    "§6.5": [
        "nemo guardrails", "guardrails ai", "llamaguard",
        "pii", "마스킹", "masking", "주민번호", "전화번호",
        "rbac 시스템", "autonomy", "자율성",
        "p2 세션 승인", "docker 샌드박스", "코드 샌드박스",
        "승인 타임아웃", "auto-deny", "sqlcipher", "aes-256",
        "api key", "dotenv", "gitignore",
        "입력 검증", "zod", "hmac", "hmac-sha256",
        "gdpr", "데이터 권리",
        "dec-003", "도구 승인", "allowlist",
    ],
    # §6.6 MCP
    "§6.6": [
        "mcp bridge", "mcp server", "mcp client",
        "streamable http", "mcp 서버", "mcp 클라이언트",
        "pyodide", "pymupdf mcp", "clip mcp", "playwright mcp",
        "tavily", "serpapi", "e2b", "unstructured",
        "mcp.search", "mcp.code", "mcp.doc", "mcp.vision",
        "mcp.speech", "mcp.browser", "mcp.db", "mcp.realtime",
    ],
    # §6.7 Agent Teams
    "§6.7": [
        "agent team", "에이전트 팀", "lead agent", "sub-agent",
        "sequential", "parallel", "messagebus",
        "in-memory queue", "위임 깊이", "delegation",
        "research agent", "coding agent", "quant agent",
        "content agent", "trading agent", "productivity agent",
        "critic agent", "sdar agent",
        "lock-at-001", "lock-at-002", "lock-at-003", "lock-at-004",
        "lock-at-005", "lock-at-006", "lock-at-007", "lock-at-008",
        "lock-at-009", "lock-at-010", "lock-at-011", "lock-at-012",
        "lock-at-013", "lock-at-014", "lock-at-015", "lock-at-016",
        "lock-at-017",
        "agent marketplace", "노코드 빌더", "n8n", "flowise",
        "langchain", "에이전트 수", "agent swarm",
        "checkpoint", "replay", "fork", "trace_id",
    ],
}

def search_feature_in_s6(feature, section_lines, keyword_index):
    """
    Feature를 §6.1~§6.7에서 검색.
    반환: (found, matches)
      found: bool
      matches: [{"line": int, "subsection": str, "match_type": str, "evidence": str}]
    """
    matches = []
    search_terms = []

    # 1. feature_name 키워드
    name = feature.get('feature_name', '') or feature.get('name', '')
    name_tokens = extract_tokens(name)
    search_terms.extend(name_tokens)

    # 2. module_id
    mod_id = feature.get('module_id', '') or feature.get('mod', '')
    if mod_id:
        search_terms.append(mod_id)

    # 3. tech_keywords
    tech = feature.get('tech_keywords', []) or feature.get('tech', [])
    if isinstance(tech, list):
        search_terms.extend(tech)

    # 4. source_section SRC 참조
    src_sec = feature.get('source_section', '') or feature.get('src_sec', '')
    if src_sec:
        for m in re.finditer(r'D2\.\d+-\d+', src_sec):
            search_terms.append(m.group())

    # 도메인 키워드 매칭 (§6 서브섹션과 직접 매칭)
    matched_sections = set()
    for sec_id, keywords in S6_DOMAIN_KEYWORDS.items():
        name_lower = name.lower()
        for kw in keywords:
            if kw.lower() in name_lower:
                matched_sections.add(sec_id)
                # 해당 섹션의 행번호 추가
                sec_info = SUBSECTIONS.get(sec_id, {})
                matches.append({
                    "line": sec_info.get("start", 0),
                    "subsection": sec_id,
                    "match_type": "domain_keyword",
                    "evidence": f"feature_name contains '{kw}' → {sec_id}"
                })
                break  # 섹션당 하나만

    # tech_keywords 매칭
    for t in tech:
        if not t: continue
        t_lower = t.lower()
        for sec_id, keywords in S6_DOMAIN_KEYWORDS.items():
            if sec_id in matched_sections:
                continue
            for kw in keywords:
                if kw.lower() == t_lower or t_lower in kw.lower() or kw.lower() in t_lower:
                    matched_sections.add(sec_id)
                    sec_info = SUBSECTIONS.get(sec_id, {})
                    matches.append({
                        "line": sec_info.get("start", 0),
                        "subsection": sec_id,
                        "match_type": "tech_keyword",
                        "evidence": f"tech_keyword '{t}' matches '{kw}' → {sec_id}"
                    })
                    break

    # 키워드 인덱스 검색 (행 수준)
    for term in search_terms:
        term_lower = term.lower()
        if term_lower in keyword_index:
            for (line_num, subsec) in keyword_index[term_lower]:
                if not any(m['line'] == line_num for m in matches):
                    matches.append({
                        "line": line_num,
                        "subsection": subsec,
                        "match_type": "keyword_index",
                        "evidence": f"'{term}' found at line {line_num}"
                    })

    # module_id 직접 검색
    if mod_id:
        for line_num, content in section_lines.items():
            if mod_id in content:
                subsec = find_subsection(line_num)
                if not any(m['line'] == line_num for m in matches):
                    matches.append({
                        "line": line_num,
                        "subsection": subsec,
                        "match_type": "module_id",
                        "evidence": f"module_id '{mod_id}' found at line {line_num}"
                    })

    return len(matches) > 0, matches

def check_in_phase_sections(feature, features_by_id=None):
    """
    §2~§5에 배정되었는지 확인 (part2_mapping_status 기준)
    """
    status = feature.get('part2_mapping_status', '') or feature.get('p2_status', '')
    phase = feature.get('part2_phase', '') or feature.get('p2_phase', '')

    if status in ['PRE_MATCHED', 'PRE_GAP']:
        return True, phase
    if phase and phase not in ['', 'null', 'None']:
        return True, phase
    return False, ''

# ============================================================
# 5. 메인 실행
# ============================================================

def main():
    print("=" * 60)
    print("M-5a Agent: §6.1~§6.7 Feature → PART2 매핑 검증")
    print("=" * 60)

    # 로드
    print("\n[1/5] PART2 §6.1~§6.7 로드...")
    section_lines = load_part2_section()
    print(f"  → {len(section_lines)} lines loaded (L{S6_START}~L{S6_END})")

    print("\n[2/5] 키워드 인덱스 구축...")
    keyword_index = build_keyword_index(section_lines)
    print(f"  → {len(keyword_index)} unique keywords indexed")

    print("\n[3/5] Feature Registry 로드...")
    features = load_registry()
    print(f"  → {len(features)} features loaded")

    print("\n[4/5] M-1~M-4 MISSING 항목 로드...")
    prev_missing = load_missing_items()
    prev_missing_ids = {m['feature_id'] for m in prev_missing}
    print(f"  → {len(prev_missing)} MISSING items from M-1~M-4")

    # 매핑 수행
    print("\n[5/5] 매핑 수행 중...")

    results = []
    stats = {
        "s6_only_no_phase": [],   # §6에 있지만 §2-§5에 없는 항목
        "s6_matched": [],          # §6에서 매칭된 항목
        "s6_not_found": [],        # §6에서 못 찾은 항목
        "prev_missing_found_in_s6": [],  # M-1~M-4 MISSING이었으나 §6에서 발견
        "prev_missing_still_missing": [], # M-1~M-4 MISSING이고 §6에서도 없음
    }

    section_counts = defaultdict(int)  # 서브섹션별 매핑 수

    for i, feat in enumerate(features):
        fid = feat['feature_id']
        fname = feat['feature_name']

        found, matches = search_feature_in_s6(feat, section_lines, keyword_index)
        in_phase, phase = check_in_phase_sections(feat)

        entry = {
            "feature_id": fid,
            "feature_name": fname,
            "version_scope": feat.get('version_scope', ''),
            "category": feat.get('category', ''),
            "in_s6": found,
            "s6_matches": matches[:5] if matches else [],  # 최대 5개
            "s6_subsections": list(set(m['subsection'] for m in matches)) if matches else [],
            "in_phase_s2_s5": in_phase,
            "phase_assignment": phase,
        }

        # 판정
        if found and not in_phase:
            entry["verdict"] = "PARTIAL"
            entry["verdict_detail"] = "§6 only, Phase 미배정"
            stats["s6_only_no_phase"].append(entry)
        elif found and in_phase:
            entry["verdict"] = "SPREAD"
            entry["verdict_detail"] = f"§6 + {phase}"
        elif not found and in_phase:
            entry["verdict"] = "MATCHED_PHASE_ONLY"
            entry["verdict_detail"] = f"§2-§5만 ({phase}), §6 해당 없음"
        else:
            entry["verdict"] = "NOT_IN_S6"
            entry["verdict_detail"] = "§6.1~§6.7에 없음 (§2-§5 또는 §6.8+ 확인 필요)"

        if found:
            stats["s6_matched"].append(fid)
            for subsec in entry["s6_subsections"]:
                section_counts[subsec] += 1
        else:
            stats["s6_not_found"].append(fid)

        # M-1~M-4 MISSING 재확인
        if fid in prev_missing_ids:
            if found:
                stats["prev_missing_found_in_s6"].append(entry)
            else:
                stats["prev_missing_still_missing"].append(fid)

        results.append(entry)

        if (i + 1) % 500 == 0:
            print(f"  → {i + 1}/{len(features)} processed...")

    print(f"  → {len(features)} features processed")

    # ============================================================
    # 6. 결과 출력
    # ============================================================

    # 통계 요약
    summary = {
        "_meta": {
            "agent": "M-5a",
            "phase": "Phase 1",
            "scope": "§6.1~§6.7 시스템별 상세 (전반부)",
            "total_features_scanned": len(features),
            "part2_lines_scanned": f"L{S6_START}~L{S6_END}",
            "generated_date": "2026-03-09"
        },
        "statistics": {
            "s6_matched_count": len(stats["s6_matched"]),
            "s6_not_found_count": len(stats["s6_not_found"]),
            "s6_only_no_phase_count": len(stats["s6_only_no_phase"]),
            "prev_missing_found_in_s6": len(stats["prev_missing_found_in_s6"]),
            "prev_missing_still_missing": len(stats["prev_missing_still_missing"]),
        },
        "subsection_coverage": {k: v for k, v in sorted(section_counts.items())},
        "s6_only_no_phase_items": [
            {
                "feature_id": e["feature_id"],
                "feature_name": e["feature_name"],
                "version_scope": e["version_scope"],
                "s6_subsections": e["s6_subsections"],
                "s6_evidence": e["s6_matches"][0]["evidence"] if e["s6_matches"] else "",
            }
            for e in stats["s6_only_no_phase"]
        ],
        "prev_missing_found_in_s6_items": [
            {
                "feature_id": e["feature_id"],
                "feature_name": e["feature_name"],
                "version_scope": e["version_scope"],
                "s6_subsections": e["s6_subsections"],
                "source_agent": next((m['source_agent'] for m in prev_missing if m['feature_id'] == e['feature_id']), ''),
                "original_severity": next((m['severity'] for m in prev_missing if m['feature_id'] == e['feature_id']), ''),
            }
            for e in stats["prev_missing_found_in_s6"]
        ],
    }

    # JSON 출력
    result_path = os.path.join(OUTPUT_DIR, 'v10_m5a_mapping_result.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump({
            "_meta": summary["_meta"],
            "statistics": summary["statistics"],
            "subsection_coverage": summary["subsection_coverage"],
            "mappings": results
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Full mapping result: {result_path}")

    # 요약 보고서
    report_path = os.path.join(OUTPUT_DIR, 'v10_m5a_summary.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"✓ Summary report: {report_path}")

    # 콘솔 요약
    print("\n" + "=" * 60)
    print("M-5a 매핑 결과 요약")
    print("=" * 60)
    print(f"  전체 스캔 Feature: {len(features)}")
    print(f"  §6.1~§6.7 매칭: {len(stats['s6_matched'])}")
    print(f"  §6.1~§6.7 미발견: {len(stats['s6_not_found'])}")
    print(f"  §6 only (Phase 미배정): {len(stats['s6_only_no_phase'])}")
    print(f"  M-1~M-4 MISSING → §6 발견: {len(stats['prev_missing_found_in_s6'])}")
    print(f"  M-1~M-4 MISSING → §6에서도 미발견: {len(stats['prev_missing_still_missing'])}")

    print(f"\n서브섹션별 매핑 건수:")
    for sec, cnt in sorted(section_counts.items()):
        sec_name = SUBSECTIONS.get(sec, {}).get("name", "")
        print(f"  {sec} ({sec_name}): {cnt}건")

    if stats["s6_only_no_phase"]:
        print(f"\n§6 only, Phase 미배정 항목 (상위 20건):")
        for e in stats["s6_only_no_phase"][:20]:
            print(f"  [{e['version_scope']}] {e['feature_id']}: {e['feature_name'][:60]}")
            print(f"    → {', '.join(e['s6_subsections'])}")

    if stats["prev_missing_found_in_s6"]:
        print(f"\nM-1~M-4 MISSING → §6에서 발견된 항목:")
        for e in stats["prev_missing_found_in_s6"]:
            orig = next((m for m in prev_missing if m['feature_id'] == e['feature_id']), {})
            print(f"  [{orig.get('source_agent','')}][{orig.get('severity','')}] {e['feature_id']}: {e['feature_name'][:60]}")
            print(f"    → §6 위치: {', '.join(e['s6_subsections'])}")

if __name__ == "__main__":
    main()