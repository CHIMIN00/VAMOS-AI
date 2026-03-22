#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""5차 재검토: 3-2 SUB_FEATURE 전수 검토 결과 적용
- 97건 중 52건 오분류 → Step 2 이동
- 45건 SUB_FEATURE 유지
"""

import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

PHASE2 = r"D:\VAMOS\04. 구현단계\v10_results\phase2"

# ============================================================
# 이동 대상 52건
# ============================================================
MOVE_IDS = {
    # A. 벤치마크 30건 (STEP7-G 독립 스펙 존재)
    "S7BG-071", "S7FI-091", "S7FI-097", "S7FI-098", "S7FI-100",
    "S7FI-101", "S7FI-102", "S7FI-107", "S7FI-108", "S7FI-109",
    "S7FI-110", "S7FI-111", "S7FI-112", "S7FI-115", "S7FI-116",
    "S7FI-117", "S7FI-118", "S7FI-119", "S7FI-123", "S7FI-124",
    "S7FI-125", "S7FI-126", "S7FI-132", "S7FI-133", "S7FI-141",
    "S7FI-142", "S7FI-143", "S7FI-144", "S7FI-145", "S7NP-180",
    # B. STEP7-F 독립 스펙 5건
    "D204-080", "S7NP-138", "S7NP-169", "S7FI-061", "S7AE-622",
    # B. STEP7-E 독립 스펙 3건
    "D207-195", "SDAR-055", "SDAR-057",
    # B. STEP7-H/I 독립 스펙 2건
    "S7FI-211", "S7FI-295",
    # C. PART2 참조 불일치 6건
    "CLAUDE-188", "D204-143", "P30-049", "S7FI-172", "S7JM-096", "S7BG-027",
    # D. 키워드 오매칭 6건
    "TEAM-012", "TEAM-074", "D207-169", "S7NP-051", "S7NP-091", "S7NP-139",
}

# 이동 사유 매핑
MOVE_REASONS = {
    # A. 벤치마크 - STEP7-G 독립 스펙
    "S7BG-071": ("STEP7-G 독립 스펙", "S7G-027 (BFCL v3) — 벤치마크별 독립 구현 스펙 존재"),
    "S7FI-091": ("STEP7-G 독립 스펙", "STEP7-G 벤치마크 가이드에 독립 평가 항목 존재"),
    "S7FI-097": ("STEP7-G 독립 스펙", "S7G-001 (MMLU) — 목표점수/커스텀 확장 독립 정의"),
    "S7FI-098": ("STEP7-G 독립 스펙", "STEP7-G 벤치마크 가이드에 독립 평가 항목 존재"),
    "S7FI-100": ("STEP7-G 독립 스펙", "STEP7-G 벤치마크 가이드에 독립 평가 항목 존재"),
    "S7FI-101": ("STEP7-G 독립 스펙", "S7G-006 (GSM8K) — 수학 추론 벤치마크 독립 스펙"),
    "S7FI-102": ("STEP7-G 독립 스펙", "STEP7-G 벤치마크 가이드에 독립 평가 항목 존재"),
    "S7FI-107": ("STEP7-G 독립 스펙", "STEP7-G 한국어 벤치마크 독립 평가 항목 존재"),
    "S7FI-108": ("STEP7-G 독립 스펙", "STEP7-G 한국어 벤치마크 독립 평가 항목 존재"),
    "S7FI-109": ("STEP7-G 독립 스펙", "STEP7-G 한국어 벤치마크 독립 평가 항목 존재"),
    "S7FI-110": ("STEP7-G 독립 스펙", "STEP7-G 한국어 벤치마크 독립 평가 항목 존재"),
    "S7FI-111": ("STEP7-G 독립 스펙", "STEP7-G 한국어 벤치마크 독립 평가 항목 존재"),
    "S7FI-112": ("STEP7-G 독립 스펙", "STEP7-G 한국어 벤치마크 독립 평가 항목 존재"),
    "S7FI-115": ("STEP7-G 독립 스펙", "S7G-002 (HumanEval) — 코딩 벤치마크 독립 스펙"),
    "S7FI-116": ("STEP7-G 독립 스펙", "S7G-002 (MBPP) — 코딩 벤치마크 독립 스펙"),
    "S7FI-117": ("STEP7-G 독립 스펙", "STEP7-G 코딩 벤치마크 독립 평가 항목 존재"),
    "S7FI-118": ("STEP7-G 독립 스펙", "STEP7-G 코딩 벤치마크 독립 평가 항목 존재"),
    "S7FI-119": ("STEP7-G 독립 스펙", "STEP7-G 코딩 벤치마크 독립 평가 항목 존재"),
    "S7FI-123": ("STEP7-G 독립 스펙", "STEP7-G 에이전트 벤치마크 독립 평가 항목 존재"),
    "S7FI-124": ("STEP7-G 독립 스펙", "STEP7-G 에이전트 벤치마크 독립 평가 항목 존재"),
    "S7FI-125": ("STEP7-G 독립 스펙", "STEP7-G 에이전트 벤치마크 독립 평가 항목 존재"),
    "S7FI-126": ("STEP7-G 독립 스펙", "STEP7-G 에이전트 벤치마크 독립 평가 항목 존재"),
    "S7FI-132": ("STEP7-G 독립 스펙", "S7G-035 (RAGAS) — RAG 벤치마크 독립 스펙"),
    "S7FI-133": ("STEP7-G 독립 스펙", "S7G-035 (RAGAS) — RAG 벤치마크 독립 스펙"),
    "S7FI-141": ("STEP7-G 독립 스펙", "STEP7-G 안전성 벤치마크 독립 평가 항목 존재"),
    "S7FI-142": ("STEP7-G 독립 스펙", "STEP7-G 안전성 벤치마크 독립 평가 항목 존재"),
    "S7FI-143": ("STEP7-G 독립 스펙", "STEP7-G 안전성 벤치마크 독립 평가 항목 존재"),
    "S7FI-144": ("STEP7-G 독립 스펙", "STEP7-G 안전성 벤치마크 독립 평가 항목 존재"),
    "S7FI-145": ("STEP7-G 독립 스펙", "STEP7-G 안전성 벤치마크 독립 평가 항목 존재"),
    "S7NP-180": ("STEP7-G 독립 스펙", "S7G-001 (MMLU-Pro) — 벤치마크 독립 스펙"),
    # B. STEP7 독립 스펙
    "D204-080": ("STEP7-F 독립 스펙", "S7F-054 (LLM 메트릭 수집) — 독립 풀스펙 존재"),
    "S7NP-138": ("STEP7-F 독립 스펙", "S7F-004 (모델 Fallback 체인) — 독립 풀스펙 존재"),
    "S7NP-169": ("STEP7-F 독립 스펙", "S7F-024 (Qdrant 프로덕션 벡터DB) — V1→V2 마이그레이션 포함"),
    "S7FI-061": ("STEP7-F 독립 스펙", "S7F-063 (비용 대시보드) — Grafana 독립 스펙 존재"),
    "S7AE-622": ("STEP7-F 독립 스펙", "S7F-063 (비용 대시보드) — 동일 대상, 독립 스펙 존재"),
    "D207-195": ("STEP7-E 독립 스펙", "S7E-057 (이용약관/개인정보처리방침) — 법적 문서 독립 스펙"),
    "SDAR-055": ("STEP7-E 독립 스펙", "S7E-085 (3-Gate 보안 통합) — CostGate 보안 독립 스펙"),
    "SDAR-057": ("STEP7-E 독립 스펙", "S7E-085 (3-Gate 보안 통합) — EvidenceGate 보안 독립 스펙"),
    "S7FI-211": ("STEP7-H 독립 스펙", "S7H-027~031 (5개 페르소나) — 독립 페르소나 스펙 존재"),
    "S7FI-295": ("STEP7-I 독립 스펙", "S7I-031~040 (10건 한국시장 특화) — 독립 파생상품 스펙"),
    # C. PART2 참조 불일치
    "CLAUDE-188": ("PART2 참조 불일치", "L454 SourceQoD 스키마 정의 ≠ V2→V3 전환 검증 게이트"),
    "D204-143": ("PART2 참조 불일치", "L2505 Cloud Library SDK 의존성 ≠ OpenAPI→다국어 SDK 코드 생성"),
    "P30-049": ("PART2 참조 불일치", "L1439 S3_DECISION_LOCKED 상태 머신 ≠ RAG 가변 청크 크기"),
    "S7FI-172": ("PART2 참조 불일치", "L2474 GO/NO-GO 체크리스트 1줄 ≠ 평가 데이터셋 관리 시스템"),
    "S7JM-096": ("PART2 참조 불일치", "L2474 평가용 데이터셋 ≠ 참고 데이터셋(J), 목적 다름"),
    "S7BG-027": ("PART2 참조 불일치", "L454 SourceQoD 스키마 정의 ≠ 응답 품질 자동 평가 시스템"),
    # D. 키워드 오매칭
    "TEAM-012": ("키워드 오매칭", "L2019 '에이전트 찬반 논증' ≠ 작업-에이전트 매칭 알고리즘"),
    "TEAM-074": ("키워드 오매칭", "L2505 Cloud Library SDK ≠ @vamos.agent 데코레이터 SDK"),
    "D207-169": ("키워드 오매칭", "L2555 연합학습 그래디언트 교환 ≠ 사용자 프라이버시 우선 모드"),
    "S7NP-051": ("키워드 오매칭", "L2109 비용 모니터링 대시보드 ≠ 학습 분석 대시보드"),
    "S7NP-091": ("키워드 오매칭", "L2109 비용 모니터링 대시보드 ≠ 웰빙 대시보드"),
    "S7NP-139": ("키워드 오매칭", "L211 AI 작업 프롬프트 템플릿 ≠ 한국어 프롬프트 최적화"),
}

assert len(MOVE_IDS) == 52, f"Expected 52, got {len(MOVE_IDS)}"

# ============================================================
# 1) 3-2 파일에서 52건 제거
# ============================================================
sf_path = f"{PHASE2}\\step1\\3-2_SUB_FEATURE_OF_EXISTING.md"
with open(sf_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 각 항목 섹션 파악
sections = []
i = 0
while i < len(lines):
    m = re.match(r'^### ([A-Z0-9][\w-]+)', lines[i].strip())
    if m:
        item_id = m.group(1)
        start = i
        end = i + 1
        while end < len(lines):
            if lines[end].strip() == "---":
                end += 1
                break
            end += 1
        sections.append((start, end, item_id))
        i = end
    else:
        i += 1

print(f"3-2에서 발견된 전체 항목: {len(sections)}건")

# 이동 대상 블록 수집 + 제거
moved_items = {}  # id → {내용, severity, ...}
remove_ranges = []
for start, end, item_id in sections:
    if item_id in MOVE_IDS:
        remove_ranges.append((start, end))
        block = lines[start:end]
        content = severity = category = evidence = version = source = ""
        for line in block:
            s = line.strip()
            if s.startswith("- **내용**:"):
                content = s.replace("- **내용**: ", "")
            if s.startswith("- **Severity**:"):
                severity = s.split("|")[0].replace("- **Severity**: ", "").strip()
            if s.startswith("- **Category**:"):
                category = s.replace("- **Category**: ", "")
            if s.startswith("- **Evidence**:"):
                evidence = s.replace("- **Evidence**: ", "")
            if "**Version**:" in s:
                vm = re.search(r'\*\*Version\*\*:\s*(\S+)', s)
                if vm:
                    version = vm.group(1)
            if s.startswith("- **출처**:"):
                source = s.replace("- **출처**: ", "")
        moved_items[item_id] = {
            "내용": content, "severity": severity, "category": category,
            "evidence": evidence, "version": version, "출처": source,
        }

print(f"이동 대상 확인: {len(moved_items)}건")

# 누락 체크
not_found = MOVE_IDS - set(moved_items.keys())
if not_found:
    print(f"⚠️ 파일에서 찾지 못한 ID: {not_found}")

# 역순 제거
remove_ranges.sort(reverse=True)
for start, end in remove_ranges:
    # 시작 전 빈 줄도 제거
    while start > 0 and lines[start-1].strip() == "":
        start -= 1
    del lines[start:end]

# 건수 업데이트
remaining = 97 - len(moved_items)
high_remaining = 27
medium_remaining = 18
low_remaining = 0

# 헤더 및 요약 업데이트
new_lines = []
for line in lines:
    # 제목 건수
    if "# Step 1 확정: 3-2 SUB_FEATURE_OF_EXISTING (97건)" in line:
        line = line.replace("97건", f"{remaining}건")
    # 요약 건수
    if "최종 97건" in line:
        line = line.replace("최종 97건", f"최종 {remaining}건")
    # 전수 목록 건수
    if "## 전수 목록 (97건)" in line:
        line = line.replace("97건", f"{remaining}건")
    # Severity 분포 테이블 (기존 값이 잘못됨)
    if "| HIGH | 39 |" in line:
        line = line.replace("| HIGH | 39 |", f"| HIGH | {high_remaining} |")
    if "| MEDIUM | 26 |" in line:
        line = line.replace("| MEDIUM | 26 |", f"| MEDIUM | {medium_remaining} |")
    if "| LOW | 37 |" in line:
        line = line.replace("| LOW | 37 |", f"| LOW | {low_remaining} |")
    if "| **합계** | **102** |" in line:
        line = line.replace("**102**", f"**{remaining}**")
    # 섹션 헤더 건수
    if "## HIGH Severity (34건)" in line:
        line = line.replace("34건", f"{high_remaining}건")
    if "## MEDIUM Severity (26건)" in line:
        line = line.replace("26건", f"{medium_remaining}건")
    if "## LOW Severity (37건)" in line:
        line = line.replace("37건", f"{low_remaining}건")
    new_lines.append(line)

# LOW Severity 섹션이 비어있으면 빈 섹션 표시
# (이미 모든 LOW 항목이 제거되었으므로)

# 5차 재검토 이력 추가 (요약 뒤에)
insert_idx = None
for i, line in enumerate(new_lines):
    if "---" in line and i > 5:
        insert_idx = i
        break

if insert_idx:
    history = [
        f"> **5차 재검토**: 2026-03-10 STEP7 카테고리별 가이드 + PART2 원본 대조, 52건 오분류 → Step 2 이동\n",
    ]
    new_lines[insert_idx:insert_idx] = history

with open(sf_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"3-2 SUB_FEATURE: {len(moved_items)}건 제거 → {remaining}건")

# ============================================================
# 2) Step 2 보고서에 이동 항목 추가
# ============================================================
step2_path = f"{PHASE2}\\step2_unclassified_report.md"

additions = []
additions.append("\n\n---\n\n")
additions.append("## 5차 재검토 이동분 (3-2 SUB_FEATURE 전수 검토)\n\n")
additions.append("> **재검토일**: 2026-03-10\n")
additions.append("> **사유**: 3-2 SUB_FEATURE 97건 전수 검토 — 키워드 매칭만으로 판정된 항목을\n")
additions.append(">  STEP7 카테고리별 가이드(B~P) + PART2 원본 대조하여 오분류 52건 이동\n\n")

# Part A: 벤치마크 30건
bench_ids = sorted([sid for sid in moved_items if MOVE_REASONS[sid][0] == "STEP7-G 독립 스펙"])
additions.append(f"### A. 벤치마크 → Step 2 이동: {len(bench_ids)}건\n\n")
additions.append("**근거**: STEP7-G_벤치마크_평가_품질보증_작업가이드.md에 S7G-001~088 (88건) 독립 구현 스펙 존재\n")
additions.append("PART2 L1799 '성능 벤치마크 V1 대비 ±10%'는 마이그레이션 검증 체크리스트일 뿐, 개별 벤치마크와 무관\n\n")
additions.append("| ID | 내용 | Severity | STEP7-G 스펙 |\n")
additions.append("|-----|------|----------|-------------|\n")
for sid in bench_ids:
    info = moved_items[sid]
    reason = MOVE_REASONS[sid][1]
    additions.append(f"| {sid} | {info['내용']} | {info['severity']} | {reason} |\n")

# Part B: STEP7 독립 스펙 10건
spec_ids = sorted([sid for sid in moved_items if "독립 스펙" in MOVE_REASONS[sid][0] and "STEP7-G" not in MOVE_REASONS[sid][0]])
additions.append(f"\n### B. STEP7 독립 스펙 존재 → Step 2 이동: {len(spec_ids)}건\n\n")
additions.append("**근거**: STEP7 카테고리별 작업가이드(F/E/H/I)에 독립 구현 스펙이 존재하나 키워드 매칭으로 SUB_FEATURE 오분류\n\n")
additions.append("| ID | 내용 | Severity | 가이드 | 이동 사유 |\n")
additions.append("|-----|------|----------|--------|----------|\n")
for sid in spec_ids:
    info = moved_items[sid]
    cat, reason = MOVE_REASONS[sid]
    additions.append(f"| {sid} | {info['내용']} | {info['severity']} | {cat} | {reason} |\n")

# Part C: PART2 참조 불일치 6건
mismatch_ids = sorted([sid for sid in moved_items if MOVE_REASONS[sid][0] == "PART2 참조 불일치"])
additions.append(f"\n### C. PART2 참조 불일치 → Step 2 이동: {len(mismatch_ids)}건\n\n")
additions.append("**근거**: PART2 키워드 매칭 지점의 실제 내용이 해당 항목과 무관 (스키마≠검증, 상태명≠기능 등)\n\n")
additions.append("| ID | 내용 | Severity | 불일치 상세 |\n")
additions.append("|-----|------|----------|------------|\n")
for sid in mismatch_ids:
    info = moved_items[sid]
    reason = MOVE_REASONS[sid][1]
    additions.append(f"| {sid} | {info['내용']} | {info['severity']} | {reason} |\n")

# Part D: 키워드 오매칭 6건
wrong_ids = sorted([sid for sid in moved_items if MOVE_REASONS[sid][0] == "키워드 오매칭"])
additions.append(f"\n### D. 키워드 오매칭 → Step 2 이동: {len(wrong_ids)}건\n\n")
additions.append("**근거**: 동일 키워드가 PART2에서 완전히 다른 기능을 지칭 (대시보드≠대시보드, SDK≠SDK 등)\n\n")
additions.append("| ID | 내용 | Severity | 오매칭 상세 |\n")
additions.append("|-----|------|----------|------------|\n")
for sid in wrong_ids:
    info = moved_items[sid]
    reason = MOVE_REASONS[sid][1]
    additions.append(f"| {sid} | {info['내용']} | {info['severity']} | {reason} |\n")

with open(step2_path, "a", encoding="utf-8") as f:
    f.writelines(additions)

print(f"\nStep 2 보고서: {len(moved_items)}건 추가 완료")

# ============================================================
# 3) 수치 요약
# ============================================================
print(f"\n=== 최종 수치 ===")
print(f"Step 1 NOT_APPLICABLE: 0건 (변동 없음)")
print(f"Step 1 SUB_FEATURE: 97 → {remaining}건 (-{len(moved_items)})")
print(f"  - HIGH: 34 → {high_remaining}건 (-7)")
print(f"  - MEDIUM: 26 → {medium_remaining}건 (-8)")
print(f"  - LOW: 37 → {low_remaining}건 (-37)")
print(f"Step 1 SKIP_CONFIRMED: 10건 (변동 없음)")
print(f"Step 1 RESOLVED: 10건 (변동 없음)")
print(f"Step 1 SECTION6: 1건 (변동 없음)")
print(f"Step 1 DUPLICATE: 1건 (변동 없음)")
step1_total = 0 + remaining + 10 + 10 + 1 + 1
print(f"Step 1 합계: {step1_total}건")
step2_total = 949 + len(moved_items)
print(f"Step 2 합계: 949 + {len(moved_items)} = {step2_total}건")
print(f"전체: {step1_total + step2_total}건 (1,068건 확인)")
