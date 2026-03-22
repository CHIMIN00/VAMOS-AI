#!/usr/bin/env python3
"""
validate_links.py — Prototype link validator for sot 2/Ai-investing-detail/

Based on: AI_INVESTING_구조화_종합계획서.md §10 검증 체크리스트 spec.

Actions:
  1. Extract all paths containing "Ai-investing-detail/" from PART2/SPEC via regex
  2. Check if each extracted path actually exists on the filesystem (os.path.exists)
  3. Check all files in sot2/ are listed in INDEX.md (if INDEX.md exists)
  4. Compare _index.md file lists with actual folder contents (if subfolders exist)

Output: JSON { broken_links: [], orphan_files: [], missing_index: [] }

Usage:
  python _validate_links_prototype.py [--part2 PATH] [--spec PATH] [--sot2 PATH] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    broken_links: list[dict[str, str]] = field(default_factory=list)
    orphan_files: list[str] = field(default_factory=list)
    missing_index: list[str] = field(default_factory=list)

    # Extra diagnostic fields (not in the minimal spec, but useful)
    referenced_paths: list[dict[str, str]] = field(default_factory=list)
    index_md_exists: bool = False
    subfolders_found: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def summary(self) -> str:
        lines = [
            "=" * 70,
            "  VALIDATE_LINKS — Result Summary",
            "=" * 70,
            "",
            f"  Referenced Ai-investing-detail/ paths found : {len(self.referenced_paths)}",
            f"  Broken links (path not on disk)             : {len(self.broken_links)}",
            f"  Orphan files (not in INDEX.md)              : {len(self.orphan_files)}",
            f"  Missing from _index.md                      : {len(self.missing_index)}",
            f"  INDEX.md exists                             : {self.index_md_exists}",
            f"  Subfolders found                            : {len(self.subfolders_found)}",
            "",
        ]

        if self.referenced_paths:
            lines.append("--- Referenced paths ---")
            for rp in self.referenced_paths:
                lines.append(f"  [{rp['source']}] {rp['path']}")
            lines.append("")

        if self.broken_links:
            lines.append("--- Broken links ---")
            for bl in self.broken_links:
                lines.append(f"  [{bl['source']}] {bl['path']}")
            lines.append("")

        if self.orphan_files:
            lines.append("--- Orphan files (not in INDEX.md) ---")
            for of_ in self.orphan_files:
                lines.append(f"  {of_}")
            lines.append("")

        if self.missing_index:
            lines.append("--- Missing from _index.md ---")
            for mi in self.missing_index:
                lines.append(f"  {mi}")
            lines.append("")

        if not (self.broken_links or self.orphan_files or self.missing_index):
            lines.append("  ALL CHECKS PASSED (or not applicable in current state)")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Action 1: Extract Ai-investing-detail/ paths from PART2 / SPEC
# ---------------------------------------------------------------------------

# Regex: match any path-like string containing Ai-investing-detail/
# Captures things like:
#   sot 2/Ai-investing-detail/01_realtime-adaptive/_index.md
#   Ai-investing-detail/INDEX.md
#   docs/sot 2/Ai-investing-detail/foo/bar.md
PATH_RE = re.compile(
    r'(?:[^\s"\'()\[\]]*?)'           # optional prefix (no whitespace/brackets)
    r'((?:[^\s"\'()\[\]]*?)'          # capture group start — optional prefix
    r'Ai-investing-detail/'            # anchor
    r'[^\s"\'()\[\]>]*)',              # rest of path (no whitespace/brackets/angle)
    re.IGNORECASE,
)

# Simpler fallback: grab anything after "Ai-investing-detail/" up to whitespace
SIMPLE_PATH_RE = re.compile(
    r'((?:\S*?)Ai-investing-detail/\S*)',
    re.IGNORECASE,
)


def extract_paths_from_file(filepath: str | Path) -> list[dict[str, str]]:
    """Return list of {source: filename, path: extracted_path}."""
    filepath = Path(filepath)
    if not filepath.is_file():
        print(f"  WARN: Source file not found: {filepath}", file=sys.stderr)
        return []

    results: list[dict[str, str]] = []
    seen: set[str] = set()
    text = filepath.read_text(encoding="utf-8", errors="replace")

    for match in SIMPLE_PATH_RE.finditer(text):
        raw = match.group(1).strip().rstrip(")")  # clean trailing parens
        # Normalise: strip markdown link artifacts
        raw = raw.lstrip("[").rstrip("]").rstrip(")")
        if raw not in seen:
            seen.add(raw)
            results.append({"source": filepath.name, "path": raw})

    return results


# ---------------------------------------------------------------------------
# Action 2: Check if each extracted path exists on disk
# ---------------------------------------------------------------------------

def resolve_path(raw_path: str, sot2_dir: Path, repo_root: Path) -> Path | None:
    """Try to resolve a raw path string to an actual filesystem path."""
    # Strategy 1: treat as relative to repo root (D:\VAMOS)
    candidates = [
        repo_root / raw_path,
        sot2_dir.parent / raw_path,  # relative to sot 2/
    ]

    # Strategy 2: extract the part after Ai-investing-detail/ and join with sot2_dir's Ai-investing-detail
    ai_detail_dir = sot2_dir / "Ai-investing-detail"
    idx = raw_path.lower().find("ai-investing-detail/")
    if idx >= 0:
        relative = raw_path[idx + len("Ai-investing-detail/"):]
        candidates.append(ai_detail_dir / relative)
        # Also try with the actual sot2 parent
        candidates.append(sot2_dir / "Ai-investing-detail" / relative)

    # Strategy 3: maybe it's an absolute-ish path (docs/sot 2/...)
    if "docs/" in raw_path.lower():
        docs_idx = raw_path.lower().find("docs/")
        candidates.append(repo_root / raw_path[docs_idx:])

    for c in candidates:
        try:
            if c.exists():
                return c
        except OSError:
            pass
    return None


def check_broken_links(
    refs: list[dict[str, str]], sot2_dir: Path, repo_root: Path
) -> list[dict[str, str]]:
    broken: list[dict[str, str]] = []
    for ref in refs:
        resolved = resolve_path(ref["path"], sot2_dir, repo_root)
        if resolved is None:
            broken.append(ref)
    return broken


# ---------------------------------------------------------------------------
# Action 3: Check all files in sot2/ are listed in INDEX.md
# ---------------------------------------------------------------------------

def check_orphan_files(sot2_ai_detail_dir: Path) -> tuple[bool, list[str]]:
    """Return (index_exists, orphan_files)."""
    index_path = sot2_ai_detail_dir / "INDEX.md"
    if not index_path.is_file():
        # INDEX.md doesn't exist yet — list all non-meta files as potential orphans
        all_files: list[str] = []
        for f in sorted(sot2_ai_detail_dir.rglob("*")):
            if f.is_file() and f.name not in ("INDEX.md", "_validate_links_prototype.py"):
                rel = f.relative_to(sot2_ai_detail_dir)
                all_files.append(str(rel).replace("\\", "/"))
        return False, all_files

    # INDEX.md exists — parse it for file references
    index_text = index_path.read_text(encoding="utf-8", errors="replace")
    # Collect all .md references from INDEX.md
    index_refs: set[str] = set()
    for m in re.finditer(r'[\w/\-_.]+\.md', index_text):
        index_refs.add(m.group(0).strip("/"))

    orphans: list[str] = []
    for f in sorted(sot2_ai_detail_dir.rglob("*.md")):
        if f.name in ("INDEX.md", "_index.md"):
            continue
        rel = str(f.relative_to(sot2_ai_detail_dir)).replace("\\", "/")
        # Check if any INDEX.md entry matches this file (partial match OK)
        found = any(rel.endswith(ref) or ref.endswith(rel) or ref in rel for ref in index_refs)
        if not found:
            orphans.append(rel)

    return True, orphans


# ---------------------------------------------------------------------------
# Action 4: Compare _index.md with actual folder contents
# ---------------------------------------------------------------------------

def check_index_vs_folder(sot2_ai_detail_dir: Path) -> tuple[list[str], list[str]]:
    """Return (subfolders_found, missing_from_index)."""
    subfolders: list[str] = []
    missing: list[str] = []

    for d in sorted(sot2_ai_detail_dir.iterdir()):
        if not d.is_dir():
            continue
        if d.name.startswith("_") or d.name.startswith("."):
            continue
        subfolders.append(d.name)

        index_file = d / "_index.md"
        if not index_file.is_file():
            # No _index.md in this subfolder — all files are "missing" from index
            for f in sorted(d.rglob("*.md")):
                rel = str(f.relative_to(sot2_ai_detail_dir)).replace("\\", "/")
                missing.append(f"[no _index.md] {rel}")
            continue

        # Parse _index.md for file references
        idx_text = index_file.read_text(encoding="utf-8", errors="replace")
        idx_refs: set[str] = set()
        for m in re.finditer(r'[\w/\-_.]+\.md', idx_text):
            idx_refs.add(m.group(0).strip("/"))

        # Check each .md file in this folder tree
        for f in sorted(d.rglob("*.md")):
            if f.name == "_index.md":
                continue
            rel = str(f.relative_to(d)).replace("\\", "/")
            fname = f.name
            found = any(
                fname in ref or ref in rel or rel.endswith(ref)
                for ref in idx_refs
            )
            if not found:
                full_rel = str(f.relative_to(sot2_ai_detail_dir)).replace("\\", "/")
                missing.append(full_rel)

    return subfolders, missing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Ensure stdout handles Unicode properly on Windows
    import io
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Validate Ai-investing-detail links")
    parser.add_argument(
        "--part2",
        default=r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md",
        help="Path to PART2 file",
    )
    parser.add_argument(
        "--spec",
        default=r"D:\VAMOS\docs\sot\VAMOS_AI_INVESTING_SPEC.md",
        help="Path to SPEC file",
    )
    parser.add_argument(
        "--sot2",
        default=r"D:\VAMOS\docs\sot 2",
        help="Path to sot 2 directory",
    )
    parser.add_argument(
        "--repo-root",
        default=r"D:\VAMOS",
        help="Repository root directory",
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true",
        help="Output as JSON only",
    )
    args = parser.parse_args()

    sot2_dir = Path(args.sot2)
    ai_detail_dir = sot2_dir / "Ai-investing-detail"
    repo_root = Path(args.repo_root)

    result = ValidationResult()

    # --- Action 1: Extract paths ---
    print("[ Action 1 ] Extracting Ai-investing-detail/ paths from PART2 and SPEC ...")
    for src in [args.part2, args.spec]:
        refs = extract_paths_from_file(src)
        result.referenced_paths.extend(refs)
    print(f"  Found {len(result.referenced_paths)} path references")

    # --- Action 2: Check broken links ---
    print("[ Action 2 ] Checking if referenced paths exist on disk ...")
    result.broken_links = check_broken_links(result.referenced_paths, sot2_dir, repo_root)
    print(f"  Broken links: {len(result.broken_links)}")

    # --- Action 3: Check orphan files ---
    print("[ Action 3 ] Checking orphan files (not in INDEX.md) ...")
    if ai_detail_dir.is_dir():
        result.index_md_exists, result.orphan_files = check_orphan_files(ai_detail_dir)
        if not result.index_md_exists:
            print("  INDEX.md does not exist yet — listing all files as potential orphans")
        print(f"  Orphan/unlisted files: {len(result.orphan_files)}")
    else:
        print(f"  WARN: Ai-investing-detail directory not found: {ai_detail_dir}")

    # --- Action 4: Compare _index.md with folder contents ---
    print("[ Action 4 ] Comparing _index.md files with actual folder contents ...")
    if ai_detail_dir.is_dir():
        result.subfolders_found, result.missing_index = check_index_vs_folder(ai_detail_dir)
        print(f"  Subfolders: {len(result.subfolders_found)}")
        print(f"  Missing from _index.md: {len(result.missing_index)}")
    else:
        print("  WARN: No subfolders to check")

    # --- Output ---
    if args.json_output:
        print(result.to_json())
    else:
        print()
        print(result.summary())

        # Also dump the canonical JSON output
        print("\n--- JSON Output ---")
        # Minimal spec-compliant JSON (3 fields only)
        minimal = {
            "broken_links": result.broken_links,
            "orphan_files": result.orphan_files,
            "missing_index": result.missing_index,
        }
        print(json.dumps(minimal, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()