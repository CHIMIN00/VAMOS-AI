#!/usr/bin/env python3
"""
Task 0-I-E: Find all bare §6 references and map to §6.X sub-sections.
"""
import json
import re
from pathlib import Path
from datetime import date

INPUT = Path(r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md")
OUTPUT = Path(r"D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_s6_mapping.json")

lines = INPUT.read_text(encoding="utf-8").splitlines()

# ── Step 1: Build §6.X section map ──────────────────────────────────────────
s6_subsections = []
s6_section_re = re.compile(r"^#{1,3}\s+(6\.(\d+)(?:\.\d+)?)\s+(.*)")
for i, line in enumerate(lines, 1):
    m = s6_section_re.match(line)
    if m:
        sec_num = m.group(1)          # e.g. "6.1", "6.1.1", "6.10.2"
        title = m.group(3).strip()
        # Only top-level §6.X (not §6.X.Y)
        if "." not in sec_num.split(".", 1)[1]:  # no second dot after 6.
            s6_subsections.append({
                "id": f"§{sec_num}",
                "line": i,
                "title": title
            })

print(f"Found {len(s6_subsections)} §6.X sub-sections:")
for s in s6_subsections:
    print(f"  {s['id']} (L{s['line']}): {s['title']}")

# ── Step 2: Build keyword map for matching ───────────────────────────────────
# Each §6.X gets keywords derived from its title + known content
keyword_map = {
    "§6.1": {
        "title": "UI/UX 상세",
        "keywords": ["ui", "ux", "레이아웃", "컴포넌트", "react", "hook", "store",
                     "멀티모달 ui", "페이지", "dashboard", "chat", "workflow",
                     "memory 페이지", "settings", "마인드맵", "온보딩", "키보드",
                     "폼 자동", "대화 분기", "state machine"],
    },
    "§6.2": {
        "title": "Rust/Tauri 인프라",
        "keywords": ["rust", "tauri", "ipc", "json-rpc", "커맨드", "핸들러",
                     "그레이스풀 셧다운", "커넥션 풀링", "bridge"],
    },
    "§6.3": {
        "title": "테스트",
        "keywords": ["테스트", "test", "pytest", "검증", "단위", "통합", "e2e"],
    },
    "§6.4": {
        "title": "CI/CD",
        "keywords": ["ci", "cd", "ci/cd", "pipeline", "github actions", "워크플로우",
                     "배포", "deploy"],
    },
    "§6.5": {
        "title": "보안",
        "keywords": ["보안", "security", "hmac", "rbac", "oauth", "mfa", "totp",
                     "webauthn", "방화벽", "stride", "owasp", "llm top 10",
                     "gdpr", "llamaguard", "fileownership"],
    },
    "§6.6": {
        "title": "MCP 서버/클라이언트",
        "keywords": ["mcp", "model context protocol", "도구 프로토콜", "mcp bridge"],
    },
    "§6.7": {
        "title": "Agent Teams 상세 구현",
        "keywords": ["agent", "team", "에이전트", "parl", "협업", "패턴",
                     "swarm", "specialization", "marketplace"],
    },
    "§6.8": {
        "title": "AI Investing 상세 구현",
        "keywords": ["invest", "투자", "trading", "거래", "블랙-리터만", "팩터",
                     "리밸런싱", "포트폴리오", "소셜 미디어 분석", "투자 교육",
                     "투자 심리", "감정적 투자", "real trading", "lstm"],
    },
    "§6.9": {
        "title": "SDAR 상세 구현",
        "keywords": ["sdar", "자가진단", "자동수리", "auto-repair", "ar-l"],
    },
    "§6.10": {
        "title": "Cloud Library 상세 구현",
        "keywords": ["cloud library", "클라우드 라이브러리", "rt-bnp", "breaking news",
                     "dcl", "domain context", "진화 제어", "수집", "gate",
                     "cl-g", "페일오버"],
    },
    "§6.11": {
        "title": "이벤트/로깅 시스템",
        "keywords": ["이벤트", "event", "로깅", "logging", "log", "알림 규칙",
                     "알림", "notification", "eventtype"],
    },
    "§6.12": {
        "title": "운영 (버전별 전략)",
        "keywords": ["운영", "모니터링", "백업", "복구", "인시던트", "롤백",
                     "헬스체크", "비용 초과", "vpn", "crm", "관리자 콘솔",
                     "성능 프로파일링", "데이터베이스 관리"],
    },
    "§6.13": {
        "title": "전체 코딩 작업량 요약",
        "keywords": ["작업량", "코딩량", "요약", "합계", "sp"],
    },
}

# Additional domain-specific keyword sets for v23 items
item_to_section = {
    # Cloud Library related
    "CLIB": "§6.10",
    "진화 제어": "§6.10",
    # Prompt / Template
    "TemplateSet": "§6.7",  # Agent Teams context
    "MSTR": "§6.7",
    "프롬프트 라이브러리": "§6.7",
    "D205": "§6.7",  # D2.0-05 is Agent Teams
    # Memory / Knowledge Management
    "D206": "§6.10",  # D2.0-06 is Cloud Library / Memory
    "한국어 불용어": "§6.10",
    "연구 노트": "§6.10",
    "코드 스니펫": "§6.10",
    "아이디어 캡처": "§6.10",
    "Zettelkasten": "§6.10",
    "지식 성숙도": "§6.10",
    "폴더/노트북": "§6.10",
    "지식 기반 의사결정": "§6.10",
    "지식 기반 글쓰기": "§6.10",
    # Wellness / Psychology -> UI features (§6.1) or new module areas
    "D207": "§6.1",  # D2.0-07 wellness/psychology features
    "스트레스 관리": "§6.1",
    "CBT 셀프케어": "§6.1",
    "번아웃 예방": "§6.1",
    "공감 대화": "§6.1",
    "습관 추적": "§6.1",
    "일기 작성": "§6.1",
    "긍정 심리": "§6.1",
    "목표 설정": "§6.1",
    "집중 모드": "§6.1",
    "포모도로": "§6.1",
    "웰니스 알림": "§6.1",
    "스트레스 관리 도우미": "§6.1",
    # Education / Learning -> UI features
    "플래시카드": "§6.1",
    "간격 반복": "§6.1",
    "퀴즈 자동": "§6.1",
    "학습 진도": "§6.1",
    "소크라테스": "§6.1",
    "독서 관리": "§6.1",
    "학습 목표": "§6.1",
    "마이크로러닝": "§6.1",
    "학습 동기": "§6.1",
    # Finance / Investing
    "S7FI": "§6.8",
    "블랙-리터만": "§6.8",
    "팩터 투자": "§6.8",
    "리밸런싱": "§6.8",
    "소셜 미디어 분석": "§6.8",
    "투자 교육": "§6.8",
    "투자 심리": "§6.8",
    "감정적 투자": "§6.8",
    "S7NP-057": "§6.8",   # 투자 교육 특화
    "S7NP-108": "§6.8",   # 투자 심리 분석
    "S7NP-110": "§6.8",   # 감정적 투자 방지
    # Alert / Notification
    "알림 규칙": "§6.11",
    "S7FI-056": "§6.11",
    "S7AE-549": "§6.11",
    "스마트 리마인더": "§6.11",
    # Infra / Operations
    "S7AE-366": "§6.2",  # graceful shutdown = Rust infra
    "S7AE-389": "§6.2",  # connection pooling = Rust infra
    "S7JM-189": "§6.12",  # 성능 프로파일링 = operations
    "S7JM-201": "§6.12",  # DB 관리 도구 = operations
    "TEAM-091": "§6.5",  # FileOwnership = security
    # UI-specific
    "S7JM-058": "§6.1",
    "S7JM-217": "§6.1",
    "S7NP-151": "§6.1",
    "S7NP-017": "§6.1",
    "S7NP-142": "§6.1",
    # Audio
    "S7JM-030": "§6.2",  # 음성 품질 최적화 = infra
    "음성 품질": "§6.2",
    # Task management
    "작업 중단 복원": "§6.7",  # Agent Teams checkpoint
    "task_checkpoint": "§6.7",
    "D206-039": "§6.7",
    # Note/Knowledge S7JM
    "S7JM-243": "§6.10",
    "S7JM-244": "§6.10",
    "S7JM-247": "§6.10",
    "S7JM-257": "§6.11",  # 스마트 리마인더 -> alerting
    "S7JM-275": "§6.10",
    "S7JM-276": "§6.10",
    # S7NP education/wellness items -> §6.1 UI features
    "S7NP-047": "§6.1",
    "S7NP-048": "§6.1",
    "S7NP-049": "§6.1",
    "S7NP-050": "§6.1",
    "S7NP-052": "§6.1",
    "S7NP-061": "§6.1",
    "S7NP-062": "§6.1",
    "S7NP-063": "§6.1",
    "S7NP-064": "§6.1",
    "S7NP-083": "§6.1",
    "S7NP-088": "§6.1",
    "S7NP-089": "§6.1",
    "S7NP-093": "§6.1",
    "S7NP-094": "§6.1",
    "S7NP-096": "§6.1",
    "S7NP-105": "§6.1",
    "S7NP-109": "§6.1",
}


def match_section(line_text: str, context_lines: list[str]) -> tuple[str, str, str]:
    """Return (mapped_to, confidence, reason)."""
    full_context = " ".join(context_lines).lower()
    original_context = " ".join(context_lines)

    # Strategy 0 (FIRST): Check for external document references (D2.0-XX §6 etc.)
    # These refer to §6 of ANOTHER document, not our §6
    # Patterns: "D2.0-07 §3/§6", "D2.0-03 §6", "PHASE_B7 §6", "D2.1-D2 §6"
    ext_doc_re = re.compile(r"(D2\.\d+-\d+|PHASE_B\d+|D2\.1-D\d+)\s*(§\d+/)?§6")
    if ext_doc_re.search(line_text):
        # Check if line also has our document's bare §6 ref (like "§6 참조" or "§6 상세")
        has_our_ref = ("§6 참조" in line_text or "§6 상세" in line_text
                       or "§6에서" in line_text or "§6 항목" in line_text
                       or "— §6" in line_text)
        if not has_our_ref:
            return "EXTERNAL_REF", "high", "외부 문서의 §6 참조 (본 문서의 §6이 아님)"

    # Strategy 1: Check for specific item IDs in the line (v23 ref IDs)
    for key, section in item_to_section.items():
        if key in line_text:
            title = keyword_map[section]["title"]
            return section, "high", f"항목 '{key}' → {section} ({title})"

    # Strategy 2: Check item description keywords in the line itself
    for section_id, info in keyword_map.items():
        for kw in info["keywords"]:
            if kw.lower() in line_text.lower():
                return section_id, "high", f"키워드 '{kw}' 매칭 → {section_id} ({info['title']})"

    # Strategy 3: Check broader context
    for section_id, info in keyword_map.items():
        for kw in info["keywords"]:
            if kw.lower() in full_context:
                return section_id, "medium", f"컨텍스트 키워드 '{kw}' → {section_id} ({info['title']})"

    return "NO_MATCH", "low", "키워드 매칭 실패 — 수동 검토 필요"


# ── Step 3: Scan for all bare §6 references ──────────────────────────────────
# Match §6 NOT followed by .digit (bare §6 reference)
# Also match "§6 " patterns but exclude "§6.X" sub-section references
bare_s6_re = re.compile(r"§6(?!\.\d)")

mappings = []
for i, line in enumerate(lines):
    line_num = i + 1
    if bare_s6_re.search(line):
        # Get context ±3 lines
        ctx_start = max(0, i - 3)
        ctx_end = min(len(lines), i + 4)
        context_lines = lines[ctx_start:ctx_end]
        context_str = "\n".join(f"L{ctx_start + j + 1}: {context_lines[j]}"
                                for j in range(len(context_lines)))

        mapped_to, confidence, reason = match_section(line, context_lines)

        mappings.append({
            "source_line": line_num,
            "reference_text": line.strip()[:200],  # truncate long lines
            "context": context_str[:800],  # truncate long contexts
            "mapped_to": mapped_to,
            "confidence": confidence,
            "reason": reason,
        })

# ── Separate external refs vs real §6 mappings ──────────────────────────────
real_mappings = [m for m in mappings if m["mapped_to"] != "EXTERNAL_REF"]
ext_mappings = [m for m in mappings if m["mapped_to"] == "EXTERNAL_REF"]
no_match = [m for m in real_mappings if m["mapped_to"] == "NO_MATCH"]
mapped = [m for m in real_mappings if m["mapped_to"] != "NO_MATCH"]

print(f"\nTotal bare §6 references found: {len(mappings)}")
print(f"  External document refs (not our §6): {len(ext_mappings)}")
print(f"  Real §6 refs (our document): {len(real_mappings)}")
print(f"    Mapped: {len(mapped)}")
print(f"    NO_MATCH: {len(no_match)}")

# ── Step 4: Output JSON ─────────────────────────────────────────────────────
result = {
    "metadata": {
        "task": "0-I-E",
        "source": "VAMOS_구현가이드_PART2_구현단계.md",
        "created": "2026-03-15",
        "total_bare_s6_refs": len(mappings),
        "external_doc_refs": len(ext_mappings),
        "real_s6_refs": len(real_mappings),
        "mapped": len(mapped),
        "no_match": len(no_match),
        "note": "bare §6 = §6 without sub-section number. External refs (D2.0-XX §6, PHASE_BX §6) reference §6 of other documents."
    },
    "s6_subsections": s6_subsections,
    "mappings": real_mappings,
    "external_refs": ext_mappings,
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nOutput written to: {OUTPUT}")

# Summary by target section
print("\n── Mapping Summary ──")
from collections import Counter
section_counts = Counter(m["mapped_to"] for m in real_mappings)
for sec, count in sorted(section_counts.items()):
    print(f"  {sec}: {count} refs")
