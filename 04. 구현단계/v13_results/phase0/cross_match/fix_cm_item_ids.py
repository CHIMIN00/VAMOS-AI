#!/usr/bin/env python
"""
Fix item_id reference mismatches in CM JSON files.
EA files were re-extracted on 2026-03-21, causing item_id shifts.
CM files were generated on 2026-03-17 with old item_ids.
"""

import json
import glob
import os
import re
import sys
import io
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

EA_DIR = r"D:\VAMOS\04. 구현단계\v13_results\phase0\extraction"
CM_DIR = r"D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match"

CM_FILES = [
    "v13_CM03_taxonomy.json",
    "v13_CM04_names.json",
    "v13_CM06_versions.json",
]


def load_ea_data():
    """Load all EA items and build multiple lookup indices."""
    all_items = {}          # item_id -> item
    agent_items = defaultdict(list)  # ea_agent -> [items]

    # Index: (ea_agent, source_file, source_line) -> [item_ids]
    by_agent_file_line = defaultdict(list)
    # Index: (ea_agent, key) -> [item_ids]
    by_agent_key = defaultdict(list)
    # Index: (ea_agent, source_file) -> [items]
    by_agent_file = defaultdict(list)

    for fpath in sorted(glob.glob(os.path.join(EA_DIR, "v13_EA*.json"))):
        with open(fpath, encoding="utf-8") as f:
            ea = json.load(f)
        agent = ea["metadata"]["agent"]  # e.g. "EA-1"
        for item in ea["items"]:
            iid = item["item_id"]
            all_items[iid] = item
            agent_items[agent].append(item)

            sf = item.get("source_file", "")
            sl = item.get("source_line", 0)
            key = item.get("key", "")

            by_agent_file_line[(agent, sf, sl)].append(item)
            if key:
                by_agent_key[(agent, key)].append(item)
            by_agent_file[(agent, sf)].append(item)

    return all_items, agent_items, by_agent_file_line, by_agent_key, by_agent_file


def normalize_agent(ea_agent_str):
    """Normalize ea_agent strings: 'EA-1', 'EA-01' etc."""
    m = re.match(r'EA-?(\d+)', ea_agent_str)
    if m:
        return f"EA-{int(m.group(1))}"
    return ea_agent_str


def find_best_match(src, comp_key, all_items, by_agent_file_line, by_agent_key, by_agent_file, agent_items):
    """Try to find the correct item_id for a source with invalid item_id."""
    ea_agent = normalize_agent(src.get("ea_agent", ""))
    sf = src.get("source_file", "")
    sl = src.get("source_line", 0)
    src_text = src.get("source_text", "")
    old_id = src.get("item_id", "")

    # Strategy 1: exact match on (agent, file, line)
    candidates = by_agent_file_line.get((ea_agent, sf, sl), [])
    if len(candidates) == 1:
        return candidates[0]["item_id"], "exact_file_line"
    if len(candidates) > 1:
        # Multiple items on same line - try to disambiguate by key or source_text
        for c in candidates:
            if c.get("key", "") == comp_key:
                return c["item_id"], "file_line+key"
        # Try source_text substring match
        for c in candidates:
            c_text = c.get("source_text", "")
            if c_text and src_text and (c_text in src_text or src_text in c_text):
                return c["item_id"], "file_line+text"
        # Just take first
        return candidates[0]["item_id"], "file_line_first"

    # Strategy 2: match by (agent, source_file) + nearby line
    file_items = by_agent_file.get((ea_agent, sf), [])
    if file_items:
        # Find closest line
        closest = None
        min_dist = float('inf')
        for item in file_items:
            dist = abs(item.get("source_line", 0) - sl)
            if dist < min_dist:
                min_dist = dist
                closest = item
            elif dist == min_dist and closest:
                # Prefer matching key
                if item.get("key", "") == comp_key:
                    closest = item

        if closest and min_dist <= 20:
            return closest["item_id"], f"nearby_line(dist={min_dist})"

    # Strategy 3: match by (agent, key)
    key_items = by_agent_key.get((ea_agent, comp_key), [])
    if len(key_items) == 1:
        return key_items[0]["item_id"], "agent+key"
    if len(key_items) > 1:
        # Multiple - prefer same file
        for item in key_items:
            if item.get("source_file", "") == sf:
                return item["item_id"], "agent+key+file"
        return key_items[0]["item_id"], "agent+key_first"

    # Strategy 4: source_text substring match within agent
    if src_text and len(src_text) > 10:
        # Use first 40 chars as search key
        search = src_text[:min(60, len(src_text))]
        for item in agent_items.get(ea_agent, []):
            item_text = item.get("source_text", "")
            if item_text and search in item_text:
                return item["item_id"], "text_substr"
            if item_text and item_text in src_text:
                return item["item_id"], "text_substr_rev"

    # Strategy 5: Try to translate old ID format to new
    # Old: EA08-0294 -> New: EA-08_294, or EA-03_313 -> shifted
    m = re.match(r'EA(\d+)-(\d+)', old_id)
    if m:
        agent_num = int(m.group(1))
        item_num = int(m.group(2))
        new_id = f"EA-{agent_num:02d}_{item_num:03d}"
        if new_id in all_items:
            return new_id, "format_convert"

    # Strategy 6: For same agent, try file + text match more loosely
    if sf and src_text:
        for item in agent_items.get(ea_agent, []):
            if item.get("source_file", "") == sf:
                item_text = item.get("source_text", "")
                if item_text and src_text:
                    # Check for significant overlap
                    words_src = set(src_text.split())
                    words_item = set(item_text.split())
                    if len(words_src) > 2 and len(words_item) > 2:
                        overlap = len(words_src & words_item)
                        if overlap >= min(len(words_src), len(words_item)) * 0.6:
                            return item["item_id"], "word_overlap"

    return None, "no_match"


def fix_cm_file(cm_path, all_items, agent_items, by_agent_file_line, by_agent_key, by_agent_file):
    """Fix item_id references in a CM file."""
    with open(cm_path, encoding="utf-8") as f:
        cm = json.load(f)

    fixed_count = 0
    removed_sources = 0
    removed_comparisons = 0
    match_methods = defaultdict(int)
    unfixed = []

    new_comparisons = []
    for comp in cm["comparisons"]:
        new_sources = []
        for src in comp["sources"]:
            iid = src.get("item_id", "")
            ea_agent = normalize_agent(src.get("ea_agent", ""))

            # Fix ea_agent format if needed (e.g., "EA-3" should stay "EA-3")
            # But source might say "EA-8" while item_id says "EA08-..."

            if iid and iid in all_items:
                # Already valid
                new_sources.append(src)
                continue

            if not iid:
                # Empty item_id - try to find match
                new_id, method = find_best_match(
                    src, comp.get("key", ""),
                    all_items, by_agent_file_line, by_agent_key, by_agent_file, agent_items
                )
                if new_id:
                    src["item_id"] = new_id
                    new_sources.append(src)
                    fixed_count += 1
                    match_methods[method] += 1
                else:
                    removed_sources += 1
                    unfixed.append(f"  {comp['comparison_id']}: empty item_id for {ea_agent}")
                continue

            # Invalid item_id - try to find correct one
            new_id, method = find_best_match(
                src, comp.get("key", ""),
                all_items, by_agent_file_line, by_agent_key, by_agent_file, agent_items
            )

            if new_id:
                src["item_id"] = new_id
                new_sources.append(src)
                fixed_count += 1
                match_methods[method] += 1
            else:
                # Cannot fix - remove this source
                removed_sources += 1
                unfixed.append(f"  {comp['comparison_id']}: {iid} ({ea_agent}, {src.get('source_file','')}:{src.get('source_line',0)})")

        if new_sources:
            comp["sources"] = new_sources
            new_comparisons.append(comp)
        else:
            removed_comparisons += 1

    cm["comparisons"] = new_comparisons

    # Update metadata counts
    result_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    for comp in cm["comparisons"]:
        result_counts[comp["result"]] += 1
        severity_counts[comp["severity"]] += 1

    cm["metadata"]["total_comparisons"] = len(cm["comparisons"])
    cm["metadata"]["results"] = {
        "CONSISTENT": result_counts.get("CONSISTENT", 0),
        "INCONSISTENT": result_counts.get("INCONSISTENT", 0),
        "SOURCE_CONFLICT": result_counts.get("SOURCE_CONFLICT", 0),
        "SINGLE_SOURCE": result_counts.get("SINGLE_SOURCE", 0),
    }
    cm["metadata"]["severity"] = {
        "CRITICAL": severity_counts.get("CRITICAL", 0),
        "WARNING": severity_counts.get("WARNING", 0),
        "INFO": severity_counts.get("INFO", 0),
    }

    # Save
    with open(cm_path, "w", encoding="utf-8") as f:
        json.dump(cm, f, ensure_ascii=False, indent=2)

    basename = os.path.basename(cm_path)
    print(f"\n{'='*60}")
    print(f"File: {basename}")
    print(f"  Fixed: {fixed_count}")
    print(f"  Removed sources: {removed_sources}")
    print(f"  Removed comparisons: {removed_comparisons}")
    print(f"  Match methods: {dict(match_methods)}")
    if unfixed:
        print(f"  Unfixed ({len(unfixed)}):")
        for u in unfixed[:10]:
            print(u)
        if len(unfixed) > 10:
            print(f"  ... and {len(unfixed)-10} more")
    print(f"  Total comparisons: {cm['metadata']['total_comparisons']}")


def main():
    print("Loading EA data...")
    all_items, agent_items, by_agent_file_line, by_agent_key, by_agent_file = load_ea_data()
    print(f"  Loaded {len(all_items)} EA items across {len(agent_items)} agents")

    for cm_file in CM_FILES:
        cm_path = os.path.join(CM_DIR, cm_file)
        if not os.path.exists(cm_path):
            print(f"SKIP: {cm_file} not found")
            continue
        fix_cm_file(cm_path, all_items, agent_items, by_agent_file_line, by_agent_key, by_agent_file)

    print("\nDone!")


if __name__ == "__main__":
    main()
