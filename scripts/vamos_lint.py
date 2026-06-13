"""VAMOS 커스텀 린터 — Layer 1(VL-001~005) + Layer 2(VL-006~008).

PART2 §1.3 R1~R11 + CLAUDE.md §7 LOCK 결정사항 중 ruff로 검사 불가능한 규칙 검증.

Layer 1 (VL-001~005, STRATEGY_09 §8.2 Phase 2-5 — 의미 동결, 변경 금지):
  VL-001: class Config: 사용 금지 (R2 — Pydantic v2는 model_config = ConfigDict(...))
  VL-002: S-#(모듈 ID, 하이픈) vs S#_(상태, 언더스코어) 네이밍 혼동 검사
  VL-003: CORE→COND 역방향 import 금지 (R7 — orange_core가 COND 모듈 import 불가)
  VL-004: LOCK/FREEZE 상수 재할당 검사 (R5 — LOCK config 키 런타임 덮어쓰기 금지)
  VL-005: 파일명/상수 네이밍 규칙 (event=lower.dot, failure=UPPER_SNAKE, fallback=FB_UPPER_SNAKE)

Layer 2 (VL-006~008, STRATEGY_09 §8.2 "V1 진입 시 — 187 모듈 명명·15 교차용어·SOT 2 연동",
세션 P6-1a 2026-06-13 신설 — 187 = 81 base + COND 106):
  VL-006: 모듈 ID 형식·범위 (base 시리즈 I≤25/E≤16/S≤8/A≤7/B≤6/C≤7/D≤6/EVX≤6 — 범위 초과=오류)
  VL-007: 15 교차용어 접두사 강제 (GLOSSARY_CROSS_DOMAIN) — *COND/도메인 모듈 파일 한정*
          (CORE/스키마는 단일 의미라 비대상 — V0 CORE 회귀 0)
  VL-008: COND-### 모듈 참조 무결성 — SOT 2 정본(COND_MODULES_종합명세) 등재 ID(COND-011~116)만 허용

SOT 2 연동: Layer 2는 docs/sot 2/{2-2_COND-Modules-Detail, 0-0_Governance-Rules-Meta}에서
COND 정본 ID 집합·15 교차용어를 *런타임 로드*한다(스크립트 위치 기준 해석). SOT 2 부재 환경에서는
해당 검사를 안전 생략(경고)하고 Layer 1은 정상 동작.

⚠️ CI 3-job 강제 승격(잠긴 배선)은 PHASE4-DEC-014 절차 선행 — 본 도구는 규칙 추가 + 로컬/advisory
실행까지(P6-1a 범위). VL-001~005 의미·CI 배선 무수정.

사용: python scripts/vamos_lint.py <검사 루트 디렉토리> [--mode warn|error]
  - 기본 mode=error. 오탐 발생 시(A1, 리스크 R05) --mode warn으로 시작 → 안정화 후 error 전환.
종료 코드: 0=위반 없음(또는 warn 모드), 1=위반 존재(error 모드)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Windows cp949 콘솔 — 출력 UnicodeEncodeError 방지 (P4-0 도구 점검 수리)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------- 규칙 정의

# VL-001: Pydantic v1 스타일 class Config (모델 내부 들여쓰기 1단 이상)
RE_CLASS_CONFIG = re.compile(r"^\s+class\s+Config\s*[:(]", re.M)
RE_PYDANTIC_HINT = re.compile(r"\bpydantic\b|\bBaseModel\b", re.I)

# VL-002: 상태 표기는 S#_ (S0_RECEIVED), 모듈 ID는 S-# (S-1)
RE_STATE_AS_MODULE = re.compile(r"""["']S-\d+_[A-Z]""")          # S-1_RECEIVED 같은 혼동
RE_MODULE_AS_STATE = re.compile(r"""["']S\d+-[A-Za-z]""")        # S1-... 같은 혼동

# VL-003: orange_core(CORE) → COND 모듈 import 금지 (R7)
RE_COND_IMPORT = re.compile(r"^\s*(?:from|import)\s+(?:\S*\.)?(cond_modules|cond)\b", re.M)

# VL-004: LOCK config 키 재할당 (semantic_cache.similarity_threshold = ... 등 코드 내 덮어쓰기)
LOCK_KEY_TAILS = [
    "single_decision_lock", "daily_limit", "monthly_limit", "warn_threshold",
    "block_threshold", "similarity_threshold", "trace_id_required",
    "threshold_p0", "threshold_p1", "threshold_p2", "soft_loop_max",
    "timeout_s", "p2_timeout_s", "active_node_cap", "min_width",
]
RE_LOCK_ASSIGN = re.compile(
    r"^\s*(?:config|cfg|settings)\s*(?:\.|\[)[^=\n]*(?:" + "|".join(LOCK_KEY_TAILS) + r")[^=\n]*=\s*[^=]",
    re.M,
)

# VL-005: 네이밍 상수 규칙
RE_EVENT_BAD = re.compile(r"""(?:EVENT|event_type)\s*=\s*["']([A-Z][A-Z0-9_.]*)["']""")     # event는 lower.dot
RE_FAILURE_BAD = re.compile(r"""(?:FAILURE|failure_code)\s*=\s*["']([a-z][a-z0-9_.]*)["']""")  # failure는 UPPER_SNAKE
RE_FALLBACK_BAD = re.compile(r"""(?:FALLBACK|fallback_id)\s*=\s*["'](?!FB_)([A-Za-z0-9_.]+)["']""")  # FB_ 접두 필수

# ---------------------------------------------------------------- Layer 2 (VL-006~008)

#: base 81 모듈 시리즈별 최대 번호 (I25+E16+S8+A7+B6+C7+D6+EVX6 = 81 — STRATEGY_09 §9.1 / CLAUDE 보강전략)
_BASE_SERIES_MAX: dict[str, int] = {
    "I": 25, "E": 16, "S": 8, "A": 7, "B": 6, "C": 7, "D": 6, "EVX": 6,
}
# VL-006: 따옴표로 감싼 base 모듈 ID 리터럴 ("I-3" 등). EVX를 E보다 먼저(alternation 우선).
RE_BASE_ID = re.compile(r"""["'](EVX|I|E|S|A|B|C|D)-(\d+)["']""")
# VL-008: COND-### 참조 (주석/문자열 포함 — 깨진 모듈 참조 탐지)
RE_COND_REF = re.compile(r"\bCOND-(\d+)\b")
# VL-007: COND/도메인 모듈 파일 식별 — MODULE_ID = "COND-..." 선언 또는 경로에 cond_modules
RE_MODULE_ID_DECL = re.compile(r"""MODULE_ID\s*[:=]\s*["']COND-\d+["']""")

#: SOT 2 정본 위치 (스크립트 = repo_root/scripts → repo_root/docs/sot 2)
_SOT2_DIR = Path(__file__).resolve().parent.parent / "docs" / "sot 2"
_COND_MASTER = _SOT2_DIR / "2-2_COND-Modules-Detail" / "COND_MODULES_종합명세.md"
_GLOSSARY = _SOT2_DIR / "0-0_Governance-Rules-Meta" / "GLOSSARY_CROSS_DOMAIN.md"

# 교차용어 → 허용 접두사(prefix_term 코드형, GLOSSARY 규칙 3 "prefix_term"). 정본은 런타임 로드로 갱신.
_CROSS_TERM_PREFIXES: dict[str, tuple[str, ...]] = {
    "qod": ("aux_qod", "ml_qod"),
    "gate": ("qa_gate", "eval_gate", "phase_gate", "sdar_gate", "cl_gate", "vamos_5_gate"),
    "pipeline": ("cicd_pipeline", "io_pipeline", "model_pipeline"),
    "agent": ("agent_team", "agent_service"),
    "discovery": ("service_discovery", "anomaly_detection"),
    "score": ("alpha_score", "div_score", "task_quality", "response_quality"),
    "breaking": ("breaking_change", "breaking_news"),
}


def _load_cond_ids() -> frozenset[str] | None:
    """COND 정본 ID 집합 로드 (SOT 2 연동). 부재 시 None(검사 생략)."""
    if not _COND_MASTER.exists():
        return None
    try:
        text = _COND_MASTER.read_text(encoding="utf-8")
    except OSError:
        return None
    return frozenset(re.findall(r"COND-\d{3}", text))


def _load_cross_terms() -> dict[str, tuple[str, ...]]:
    """GLOSSARY에서 교차용어 표제 로드 → _CROSS_TERM_PREFIXES와 교차(정본 우선)."""
    terms = dict(_CROSS_TERM_PREFIXES)
    if _GLOSSARY.exists():
        try:
            text = _GLOSSARY.read_text(encoding="utf-8")
            # "### N. <Term>" 표제에서 용어 추출 — 등재 여부 확인용(접두사 맵은 위 정본 유지)
            for m in re.finditer(r"^###\s+\d+\.\s+([A-Za-z][\w/ -]*)", text, re.M):
                key = m.group(1).strip().split()[0].lower()
                terms.setdefault(key, ())
        except OSError:
            pass
    return terms


#: 런타임 1회 로드 캐시 (None = 미시도)
_COND_IDS: frozenset[str] | None = None
_CROSS_TERMS: dict[str, tuple[str, ...]] | None = None
_SOT2_AVAILABLE = _COND_MASTER.exists()


def _is_domain_module(path: Path, text: str) -> bool:
    """VL-007 적용 대상 = COND/도메인 모듈 파일(MODULE_ID 선언 또는 cond_modules 경로).

    V0 CORE(orange_core/schemas/infra/safety/rpc/storage)는 단일 의미 영역이라 비대상.
    """
    parts = {p.lower() for p in path.parts}
    if "cond_modules" in parts:
        return True
    return bool(RE_MODULE_ID_DECL.search(text))


def lint_file(path: Path, text: str) -> list[tuple[str, int, str]]:
    """단일 파일 검사 → [(rule_id, line_no, message)]."""
    findings: list[tuple[str, int, str]] = []

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    # VL-001 — Pydantic 맥락 파일에서만
    if RE_PYDANTIC_HINT.search(text):
        for m in RE_CLASS_CONFIG.finditer(text):
            findings.append(("VL-001", line_of(m.start()),
                             "class Config: 금지 — Pydantic v2 model_config = ConfigDict(...) 사용 (R2)"))

    # VL-002
    for m in RE_STATE_AS_MODULE.finditer(text):
        findings.append(("VL-002", line_of(m.start()),
                         "S-#는 모듈 ID(하이픈) — 상태는 S#_(언더스코어) 사용 (CLAUDE.md §7.1)"))
    for m in RE_MODULE_AS_STATE.finditer(text):
        findings.append(("VL-002", line_of(m.start()),
                         "S#-는 잘못된 표기 — 모듈 ID는 S-#, 상태는 S#_ (CLAUDE.md §7.1)"))

    # VL-003 — orange_core 하위 파일에서만
    parts = {p.lower() for p in path.parts}
    if "orange_core" in parts:
        for m in RE_COND_IMPORT.finditer(text):
            findings.append(("VL-003", line_of(m.start()),
                             "CORE→COND 역방향 import 금지 (R7) — COND는 CORE 소비만 가능"))

    # VL-004 — 프로덕션 코드 한정 (PHASE4-DEC-012). test 코드는 LOCK 재할당이 ValidationError로
    # *거부됨을 검증*하므로 면제(R5 의도 = 런타임 덮어쓰기 금지이지, 거부 테스트 금지가 아님).
    is_test = path.name.startswith("test_") or "tests" in parts
    if not is_test:
        for m in RE_LOCK_ASSIGN.finditer(text):
            findings.append(("VL-004", line_of(m.start()),
                             "LOCK config 키 런타임 재할당 금지 (R5/D13) — config.v1.toml LOCK 값은 불변"))

    # VL-005
    for m in RE_EVENT_BAD.finditer(text):
        findings.append(("VL-005", line_of(m.start()),
                         f"event 이름 '{m.group(1)}'은 lower.dot 형식이어야 함 (예: oc.intent.parsed)"))
    for m in RE_FAILURE_BAD.finditer(text):
        findings.append(("VL-005", line_of(m.start()),
                         f"failure 코드 '{m.group(1)}'은 UPPER_SNAKE 형식이어야 함 (예: INTENT_PARSE_FAILED)"))
    for m in RE_FALLBACK_BAD.finditer(text):
        findings.append(("VL-005", line_of(m.start()),
                         f"fallback ID '{m.group(1)}'은 FB_ 접두 UPPER_SNAKE 형식이어야 함 (예: FB_COST_DOWNSHIFT)"))

    # ── Layer 2 (VL-006~008) ────────────────────────────────────────────────
    global _COND_IDS, _CROSS_TERMS
    if _COND_IDS is None and _SOT2_AVAILABLE:
        _COND_IDS = _load_cond_ids()
    if _CROSS_TERMS is None:
        _CROSS_TERMS = _load_cross_terms()

    # VL-006 — base 모듈 ID 형식·범위 (범위 초과 = 잘못된 모듈 ID)
    for m in RE_BASE_ID.finditer(text):
        series, num = m.group(1), int(m.group(2))
        cap = _BASE_SERIES_MAX[series]
        if num < 1 or num > cap:
            findings.append(("VL-006", line_of(m.start()),
                             f"모듈 ID '{series}-{num}' 범위 초과 — {series} 시리즈는 "
                             f"{series}-1~{series}-{cap} (STRATEGY_09 §9.1 187=81+106)"))

    # VL-008 — COND 모듈 참조 무결성 (SOT 2 정본 등재 ID만 허용)
    if _COND_IDS is not None:
        for m in RE_COND_REF.finditer(text):
            cond_id = f"COND-{m.group(1)}"
            # 3자리 정규형 + 정본 집합 등재
            if len(m.group(1)) != 3 or cond_id not in _COND_IDS:
                findings.append(("VL-008", line_of(m.start()),
                                 f"'{cond_id}' 미등재 모듈 참조 — SOT 2 정본(COND_MODULES_종합명세, "
                                 f"COND-011~116 {len(_COND_IDS)}개)에 없음 (깨진 참조)"))

    # VL-007 — 15 교차용어 접두사 강제 (COND/도메인 모듈 파일 한정)
    if _is_domain_module(path, text):
        for term, prefixes in _CROSS_TERMS.items():
            if not prefixes:
                continue  # GLOSSARY 등재만 되고 코드 접두사 맵 미정의 용어는 강제 보류
            # 따옴표 식별자/키로 쓰인 bare 교차용어 (event/key/const 값)
            bare = re.compile(rf"""["']({term})["']""", re.I)
            for mm in bare.finditer(text):
                findings.append(("VL-007", line_of(mm.start()),
                                 f"교차용어 '{term}'은 도메인 접두사 필요 "
                                 f"(예: {', '.join(prefixes[:2])}) — GLOSSARY_CROSS_DOMAIN 규칙 3"))

    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="VAMOS custom linter (VL-001~005)")
    ap.add_argument("root", nargs="?", default="backend", help="검사 루트 디렉토리")
    ap.add_argument("--mode", choices=["warn", "error"], default="error",
                    help="warn: 위반을 경고만 (exit 0) / error: 위반 시 exit 1")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"[vamos_lint] 루트 '{root}' 부재 — 검사 대상 없음 (OK)")
        return 0

    total: list[tuple[Path, str, int, str]] = []
    n_files = 0
    for py in sorted(root.rglob("*.py")):
        # 가상환경/캐시 제외
        sparts = {p.lower() for p in py.parts}
        if sparts & {".venv", "venv", "__pycache__", "node_modules", ".git"}:
            continue
        n_files += 1
        try:
            text = py.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            print(f"[vamos_lint] 읽기 실패 {py}: {e}")
            continue
        for rule, line, msg in lint_file(py, text):
            total.append((py, rule, line, msg))

    for py, rule, line, msg in total:
        print(f"{py}:{line}: {rule} {msg}")
    print(f"[vamos_lint] 파일 {n_files}개 검사 — 위반 {len(total)}건 (mode={args.mode})")
    if total and args.mode == "error":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
