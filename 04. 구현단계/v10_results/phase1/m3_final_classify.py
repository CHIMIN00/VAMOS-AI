"""
M-3 최종 분류: MISSING 항목의 심각도 재판정
- 상위 모듈이 PART2에 있으면 → MEDIUM (세부 기능 누락, 상위 기능은 존재)
- 상위 모듈도 PART2에 없으면 → HIGH/BLOCKER
- 도메인 세부 기능(S7AE 등)은 §6 검색도 수행
"""
import json
import re
from collections import Counter

RESULT_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase1\v10_m3_mapping_result_v2.json"
PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
OUTPUT_DIR = r"D:\VAMOS\04. 구현단계\v10_results\phase1"

# PART2 §4에 명시된 V2 구현 항목 (상위 모듈/기능 키워드)
V2_PART2_MODULES = {
    # V2-Phase 1
    "infra_migration": ["SQLite", "PostgreSQL", "JSONL", "Chroma", "Qdrant", "Neo4j", "NetworkX",
                        "Docker", "config.v2", "마이그레이션", "migration", "VPS", "Alembic",
                        "Blue-Green", "rollback", "TimescaleDB", "배포", "deploy", "Helm",
                        "컨테이너", "스키마", "DDL", "DML", "인덱스", "무결성", "백업",
                        "Backup", "Canary", "헬스체크", "healthcheck", "SSH"],
    # V2-Phase 2
    "i07_project_session": ["I-7", "i07", "Project/Session", "프로젝트", "세션", "session",
                            "idle_timeout", "max_turns"],
    "i12_workflow": ["I-12", "i12", "Workflow", "워크플로우", "스케줄러", "scheduler",
                     "StateGraph", "서브 워크플로우", "subflow"],
    "i22_task_project": ["I-22", "i22", "Task/Project", "태스크", "task", "프로젝트 관리"],
    "i23_doc_code": ["I-23", "i23", "Doc/Code", "문서 구조화", "코드 구조화", "AST"],
    "i25_sdar": ["I-25", "i25", "SDAR", "자가진단", "자동수리", "AR-L2", "AR-L3",
                 "repair", "self-diagnosis", "자가 수리", "5-Gate"],
    "a04_debate": ["A-4", "a04", "Debate", "Bull", "Bear", "토론", "찬반"],
    "e13_calendar": ["E-13", "e13", "Calendar", "캘린더", "일정", "Google Calendar"],
    "e14_email": ["E-14", "e14", "Email", "이메일", "Gmail"],
    "e15_cloud_collector": ["E-15", "e15", "Cloud Collector", "Cloud Library", "RT-BNP",
                            "DCL-GEO", "RSS", "Breaking", "뉴스", "수집", "Crawl",
                            "Discovery", "7-Stage"],
    "e16_cloud_storage": ["E-16", "e16", "Cloud Storage", "클라우드 스토리지", "Google Drive",
                          "OneDrive", "S3"],
    # V2-Phase 3
    "agent_teams_v2": ["Agent Teams", "에이전트 팀", "MessageBus", "Redis",
                       "협업 패턴", "Sequential", "Parallel", "Supervisor", "Handoff", "Hybrid",
                       "Lead Agent", "Sub-Agent", "Quant Agent", "Content Agent",
                       "Trading Agent", "Productivity Agent", "Critic Agent", "SDAR Agent",
                       "max_agents", "AgentPool", "에이전트 풀"],
    "hmac_security": ["HMAC", "SHA-256", "인증", "서명", "signature", "hmac_secret"],
    "llamaguard": ["LlamaGuard", "Guardrails", "NeMo", "GuardrailsAI", "L1", "L2", "L3",
                   "safe/unsafe", "4-Layer"],
    "gdpr": ["GDPR", "열람", "이동", "제한", "삭제", "Access", "Portability",
             "Restriction", "Erasure", "개인정보"],
    "cloud_library_v2": ["Cloud Library V2", "7-Stage", "LLM 분석"],
    "rt_bnp_v2": ["RT-BNP V2", "REST API", "30초", "Kafka", "breaking_news",
                  "Trading Agent", "시그널"],
    "sdar_ar_l3": ["AR-L3", "MEDIUM risk", "5개 액션", "수리 성공률"],
}

# §6 시스템별 상세에서 V2 관련 키워드 (PARTIAL 후보)
S6_V2_KEYWORDS = {
    "§6.1-UI": ["멀티모달 UI", "UI State Machine", "Failure/Fallback UI", "접근 제어"],
    "§6.2-Rust": ["IPC", "Tauri", "JSON-RPC"],
    "§6.3-Test": ["테스트", "VAL", "검증", "AC"],
    "§6.5-Security": ["보안", "인증", "암호화"],
    "§6.7-AgentTeams": ["V2 추가 에이전트", "LOCK-AT"],
    "§6.8-AIInvesting": ["AI Investing", "포트폴리오", "매매", "차트", "백테스트",
                         "시뮬레이션", "Circuit Breaker", "51% Gate"],
    "§6.9-SDAR": ["5-Layer", "State Machine", "수리 액션", "Kill Switch"],
    "§6.10-CloudLib": ["10-Layer", "평가 점수", "신뢰도", "5-Gate", "RT-BNP", "DCL"],
    "§6.11-EventLog": ["EventType", "FailureCode", "Fallback"],
}


def find_parent_module(feature):
    """Check if feature's parent module exists in PART2 §4."""
    fname = feature.get("feature_name", "").lower()
    notes = str(feature.get("notes", "") or "").lower()
    src = str(feature.get("source_section", "") or "").lower()
    fid = feature.get("feature_id", "")

    for module_key, keywords in V2_PART2_MODULES.items():
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in fname or kw_lower in notes or kw_lower in src:
                return module_key
    return None


def find_s6_match(feature):
    """Check if feature has a match in §6 system details."""
    fname = feature.get("feature_name", "").lower()
    notes = str(feature.get("notes", "") or "").lower()

    for section, keywords in S6_V2_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in fname or kw.lower() in notes:
                return section
    return None


def final_classify(results):
    """Final classification of all results."""
    stats = {
        "reclassified_to_medium": 0,
        "reclassified_to_partial": 0,
        "reclassified_to_na": 0,
        "remaining_high": 0,
    }

    for r in results:
        if r["verdict"] != "MISSING":
            continue

        parent = find_parent_module(r)
        s6_match = find_s6_match(r)

        if parent:
            # Parent module exists → downgrade to MEDIUM
            r["severity"] = "MEDIUM"
            r["notes"] = (r.get("notes", "") or "") + f" [M-3: 상위 모듈 '{parent}' PART2 존재, 세부 항목 미명시]"
            stats["reclassified_to_medium"] += 1
        elif s6_match:
            # Found in §6 → PARTIAL
            r["verdict"] = "PARTIAL"
            r["part2_phase"] = f"{s6_match} (Phase 미배정)"
            r["severity"] = None
            r["notes"] = (r.get("notes", "") or "") + f" [M-3: §6에서 발견, V2 Phase 미배정]"
            stats["reclassified_to_partial"] += 1
        else:
            # Truly missing
            vs = r.get("version_scope", "")
            cat = r.get("category", "")
            if vs == "V2" and cat in ("FT-FUNC", "FT-MOD", "FT-INFRA", "FT-SEC", "FT-API"):
                r["severity"] = "HIGH"
                stats["remaining_high"] += 1
            elif vs == "V2":
                r["severity"] = "MEDIUM"
            else:
                r["severity"] = "LOW"

    return results, stats


def main():
    with open(RESULT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data["results"]
    print(f"Total: {len(results)}")

    missing_before = sum(1 for r in results if r["verdict"] == "MISSING")
    print(f"MISSING before final classify: {missing_before}")

    results, stats = final_classify(results)
    print(f"\nReclassification stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Final stats
    verdicts = Counter(r["verdict"] for r in results)
    print(f"\n=== FINAL Verdicts ===")
    for v, c in verdicts.most_common():
        print(f"  {v}: {c}")

    primary = [r for r in results if r["m3_role"] == "PRIMARY"]
    pv = Counter(r["verdict"] for r in primary)
    print(f"\n=== PRIMARY Final Verdicts ({len(primary)}) ===")
    for v, c in pv.most_common():
        print(f"  {v}: {c}")

    cc = [r for r in results if r["m3_role"] == "CROSS_CHECK"]
    cv = Counter(r["verdict"] for r in cc)
    print(f"\n=== CROSS_CHECK Final Verdicts ({len(cc)}) ===")
    for v, c in cv.most_common():
        print(f"  {v}: {c}")

    # MISSING severity
    still_missing = [r for r in results if r["verdict"] == "MISSING"]
    if still_missing:
        sev = Counter(r["severity"] for r in still_missing)
        print(f"\n=== FINAL MISSING Severity ({len(still_missing)}) ===")
        for s, c in sev.most_common():
            print(f"  {s}: {c}")

        # Primary HIGH
        p_high = [r for r in still_missing if r["m3_role"] == "PRIMARY" and r["severity"] == "HIGH"]
        print(f"\n=== PRIMARY MISSING HIGH ({len(p_high)}) - TOP 30 ===")
        for r in p_high[:30]:
            print(f"  {r['feature_id']}: {r['feature_name'][:55]}")
            print(f"    cat={r['category']}, src={str(r.get('source_section',''))[:40]}")

    # Save final
    data["results"] = results
    data["statistics"] = {
        "overall": dict(verdicts),
        "primary": dict(pv),
        "cross_check": dict(cv),
        "missing_severity": dict(Counter(r["severity"] for r in still_missing if r.get("severity"))) if still_missing else {},
        "reclassification": stats,
    }

    out_path = f"{OUTPUT_DIR}/v10_m3_mapping_result_final.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_path}")

    # Save remaining missing
    out_missing = f"{OUTPUT_DIR}/v10_m3_missing_final.json"
    with open(out_missing, "w", encoding="utf-8") as f:
        json.dump(still_missing, f, ensure_ascii=False, indent=2)
    print(f"Saved: {out_missing}")


if __name__ == "__main__":
    main()