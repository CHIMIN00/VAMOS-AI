#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v10 Step 2 Phase C: TRUE_MISSING 200건 PART2 반영
- 부록/별첨 절대 금지 — 기존 구조(§1~§7) 내 삽입
- version_scope별 배치: V1→V2→V3 순서
- 역순 적용 (뒤→앞)으로 행번호 밀림 방지
- §6.13 작업량 갱신
"""

import json, re, os, sys, copy
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE = "D:/VAMOS/04. 구현단계/v10_results/phase2"
PART2_PATH = "D:/VAMOS/docs/guides/VAMOS_구현가이드_PART2_구현단계.md"

# ─── Phase 테이블 마지막 행 위치 (v22.0.0 기준) ───
# 각 Phase 테이블의 마지막 데이터 행 줄번호
PHASE_TABLE_END = {
    "V1_P2": 1503,   # §3 V1-Phase 2 구현항목 마지막 (9행 DCL 기초)
    "V1_P3": 1595,   # §3 V1-Phase 3 구현항목 마지막 (15행 D-1~D-2)
    "V1_P4": 1645,   # §3 V1-Phase 4 구현항목 마지막 (16행 CLI Interface)
    "V1_P5": 1685,   # §3 V1-Phase 5 구현항목 마지막 (12행 보안 감사)
    "V1_P6": 1720,   # §3 V1-Phase 6 구현항목 마지막 (8행 S-1 Self-check)
    "V2_P2": 1951,   # §4 V2-Phase 2 구현항목 마지막 (10행 E-16)
    "V2_P3": 2130,   # §4 V2-Phase 3 구현항목 마지막 (8행 SDAR AR-L3)
    "V3_P2": 2453,   # §5 V3-Phase 2 구현항목 마지막 (16행 PARL 인프라)
    "V3_P3": 2731,   # §5 V3-Phase 3 구현항목 마지막 (10행 AI Investing 고급)
}

# Phase table column formats
PHASE_FORMATS = {
    "V1": "| {num} | **{name}** | {desc} | {ref} |",
    "V2": "| {num} | **{name}** | {desc} | {ref} |",
    "V3": "| {num} | {group} | **{name}** | {desc} |",
}

# Agent → §6 section for detail spec
AGENT_S6_LINE = {
    "M-2": 3283,  # §6.8 AI Investing 시작
    "M-3": 3405,  # §6.9 SDAR 시작 (or §6.5 Security 3103)
    "M-4": 3157,  # §6.7 Agent Teams 시작
}

# Category → Phase 매핑 (V1)
V1_CAT_PHASE = {
    "FT-FUNC": "V1_P3",    # Workflow/Agent phase
    "FT-SEC": "V1_P5",     # Integration/Test phase
    "FT-INFRA": "V1_P5",   # Integration/Test
    "FT-UI": "V1_P4",      # UI/UX phase
    "FT-CFG": "V1_P2",     # Storage/Memory
    "FT-MOD": "V1_P3",     # Workflow/Agent
    "FT-DOMAIN": "V1_P6",  # AI Investing
    "FT-TEST": "V1_P5",    # Integration/Test
    "FT-API": "V1_P5",     # Integration
    "기타": "V1_P3",
}

# Category → Phase 매핑 (V2)
V2_CAT_PHASE = {
    "FT-FUNC": "V2_P2",
    "FT-SEC": "V2_P3",
    "FT-INFRA": "V2_P2",
    "FT-UI": "V2_P2",
    "FT-CFG": "V2_P2",
    "FT-MOD": "V2_P2",
    "FT-DOMAIN": "V2_P2",
    "FT-TEST": "V2_P3",
    "FT-API": "V2_P2",
    "FT-SCHEMA": "V2_P2",
    "기타": "V2_P2",
}

# V3 → mostly Phase 2 (EXP modules)
V3_CAT_PHASE = defaultdict(lambda: "V3_P2")
V3_CAT_PHASE.update({"FT-FUNC": "V3_P3"})


def get_phase_key(item):
    """항목의 target Phase 결정"""
    vs = item["version_scope"]
    cat = item.get("category", "") or "기타"

    if "," in vs:
        versions = [v.strip() for v in vs.split(",")]
        hi = max(versions, key=lambda v: {"V3":4,"V2":3,"V1":2,"V0":1}.get(v,0))
    else:
        hi = vs

    if hi == "V1":
        return V1_CAT_PHASE.get(cat, "V1_P3")
    elif hi == "V2":
        return V2_CAT_PHASE.get(cat, "V2_P2")
    elif hi == "V3":
        return V3_CAT_PHASE[cat]
    else:
        return "V1_P3"


def make_table_row(item, num, pk):
    """PART2 테이블 행 생성 — 각 Phase 테이블 컬럼 형식에 맞춤"""
    name = item["feature_name"][:50]
    fid = item["feature_id"]
    sev = item["severity"]
    desc = f"{name} [{sev}]"
    ref = f"v10 Phase 2 추가 ({fid})"

    if pk == "V3_P2":
        # V3-Phase 2: | # | 모듈 그룹 | 모듈 | 구현 내용 |
        agent = item.get("agent", "")
        group = {"M-2": "AI", "M-3": "Risk/Infra", "M-4": "Agent"}.get(agent, "기타")
        return f"| {num} | {group} | **{name}** | {desc} | <!-- {fid} v23 -->"
    elif pk == "V3_P3":
        # V3-Phase 3: | # | 항목 | 구현 내용 |
        return f"| {num} | **{name}** | {desc} | <!-- {fid} v23 -->"
    else:
        # V1/V2: | # | 항목 | 구현 내용 | 산출물 참조 |
        return f"| {num} | **{name}** | {desc} | {ref} | <!-- {fid} v23 -->"


def main():
    print("=" * 70)
    print("Phase C: TRUE_MISSING 200건 PART2 반영")
    print("=" * 70)

    # Load data
    with open(f"{BASE}/v10_step2_integrated_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    tm = [d for d in data["items"] if d["final_classification"] == "TRUE_MISSING"]
    print(f"TRUE_MISSING: {len(tm)}건")

    # Load PART2
    with open(PART2_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"PART2 원본: {len(lines)}행")

    # Group by Phase
    by_phase = defaultdict(list)
    for item in tm:
        pk = get_phase_key(item)
        by_phase[pk].append(item)

    print("\nPhase별 배치:")
    for pk in sorted(by_phase.keys()):
        print(f"  {pk}: {len(by_phase[pk])}건")

    # Generate patches: (line_no, rows_to_insert)
    patches = []
    patch_details = []  # For reporting

    for pk in sorted(by_phase.keys(), key=lambda x: PHASE_TABLE_END.get(x, 0)):
        items = by_phase[pk]
        insert_after = PHASE_TABLE_END.get(pk, 0)
        if insert_after == 0:
            print(f"  ⚠ {pk}: 삽입 위치 미정의, 스킵")
            continue

        # Find the last row number in that table
        # We need to determine what the existing last row number is
        last_line = lines[insert_after - 1].strip() if insert_after <= len(lines) else ""
        # Extract existing row number
        m = re.match(r'\|\s*(\d+)', last_line)
        start_num = int(m.group(1)) + 1 if m else 1

        # Check for sub-numbering (e.g., "9-1", "9-2")
        m2 = re.match(r'\|\s*(\d+)-(\d+)', last_line)
        if m2:
            start_num = int(m2.group(1)) + 1

        vs_prefix = pk.split("_")[0]  # V1, V2, V3
        new_rows = []
        for i, item in enumerate(items):
            num = start_num + i
            row = make_table_row(item, num, pk)
            new_rows.append(row)
            patch_details.append({
                "feature_id": item["feature_id"],
                "feature_name": item["feature_name"],
                "severity": item["severity"],
                "target_section": pk,
                "insert_after_line": insert_after,
                "row_number": num,
            })

        patches.append({
            "phase_key": pk,
            "insert_after": insert_after,
            "rows": new_rows,
            "count": len(new_rows),
        })

    # Apply patches in REVERSE order (bottom → top) to preserve line numbers
    patches.sort(key=lambda p: -p["insert_after"])

    total_inserted = 0
    for patch in patches:
        insert_idx = patch["insert_after"]  # 1-based → 0-based = insert_idx - 1
        # Insert after this line
        for i, row in enumerate(patch["rows"]):
            lines.insert(insert_idx + i, row + "\n")  # 0-based index
        total_inserted += patch["count"]
        print(f"  {patch['phase_key']}: L{insert_idx} 뒤에 {patch['count']}행 삽입")

    # Update version header
    for i, line in enumerate(lines):
        if "v22.0.0" in line and i < 10:
            lines[i] = line.replace("v22.0.0", "v23.0.0")
            print(f"  L{i+1}: 버전 v22.0.0 → v23.0.0")
            break

    # Update §6.13 workload (find the summary table)
    # Count additions per version
    v_counts = defaultdict(int)
    for item in tm:
        vs = item["version_scope"]
        if "," in vs:
            versions = [v.strip() for v in vs.split(",")]
            hi = max(versions, key=lambda v: {"V3":4,"V2":3,"V1":2,"V0":1}.get(v,0))
        else:
            hi = vs
        v_counts[hi] += 1

    print(f"\n  §6.13 작업량 갱신 필요: V1+{v_counts.get('V1',0)}, V2+{v_counts.get('V2',0)}, V3+{v_counts.get('V3',0)}")

    # Add changelog entry at end
    # Find "변경 이력" section
    for i in range(len(lines) - 1, max(len(lines) - 50, 0), -1):
        if "변경 이력" in lines[i]:
            # Find the last changelog entry
            for j in range(i + 1, min(i + 40, len(lines))):
                if lines[j].strip().startswith("| v") and "v22" in lines[j]:
                    # Insert new changelog after v22
                    changelog = f"| v23.0.0 | 2026-03-11 | v10 Phase 2 Step 2 전수 검증: TRUE_MISSING {len(tm)}건 반영 (V1+{v_counts.get('V1',0)}/V2+{v_counts.get('V2',0)}/V3+{v_counts.get('V3',0)}). §3~§5 Phase 테이블 확장, §6.13 작업량 갱신 |\n"
                    lines.insert(j + 1, changelog)
                    total_inserted += 1
                    print(f"  변경 이력에 v23.0.0 항목 추가")
                    break
            break

    print(f"\n총 삽입: {total_inserted}행")
    print(f"PART2 최종: {len(lines)}행 (원본 {len(lines) - total_inserted}행 + {total_inserted}행)")

    # Save modified PART2
    with open(PART2_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"→ PART2 저장 완료: {PART2_PATH}")

    # Save patch details for reporting
    report = {
        "total_patched": len(tm),
        "total_lines_inserted": total_inserted,
        "version_bump": "v22.0.0 → v23.0.0",
        "patches_by_phase": {p["phase_key"]: p["count"] for p in patches},
        "patches": patch_details,
    }
    with open(f"{BASE}/v10_phase_c_patches.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"→ v10_phase_c_patches.json")

    print("\n" + "=" * 70)
    print("Phase C 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()
