import json

# Load input
with open("D:/VAMOS/04. 구현단계/v10_results/phase2/nf_M-2.json", "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Total items: {len(items)}")

results = []

for item in items:
    fid = item["feature_id"]
    fname = item["feature_name"]
    severity = item["severity"]
    substatus = item.get("substatus", "")
    category = item.get("category", "")
    version = item.get("version_scope", "V1")

    classification = "TRUE_MISSING"
    evidence_source = ""
    evidence_line = 0
    evidence_text = ""
    reason = ""

    # === AINV- items -> AI Investing ===
    if fid.startswith("AINV-"):
        if "백테스팅" in fname or "backtest" in fname.lower():
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 3319
            evidence_text = "| 2 | 백테스트 | vectorbt(조건부 ADOPT) 또는 backtrader | 없음 |"
            reason = "AI Investing §6.8 백테스트 기술스택에 포함"
        elif "EngineConfig" in fname or "설정 모델" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 3291
            evidence_text = "### 51% Gate 파라미터 (LOCK)"
            reason = "AI Investing §6.8 파라미터 설정에 포함"
        elif "OHLCV" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 3318
            evidence_text = "| 1 | 데이터 소스 | yfinance + Alpha Vantage | 없음 |"
            reason = "AI Investing §6.8 데이터 소스(yfinance) OHLCV 처리에 포함"
        elif "Mean-Variance" in fname or "portfolio_optimizer" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 3324
            evidence_text = "| 7 | ML Pipeline | scikit-learn + XGBoost | 없음 |"
            reason = "AI Investing §6.8 ML Pipeline으로 포트폴리오 최적화 포함"
        else:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1713
            evidence_text = "| 1 | **Paper Trading MVP** | 시뮬레이션 트레이딩 (51% Gate)"
            reason = "V1-Phase 6 AI Investing MVP 구현 범위에 포함"

    # === BASE- items ===
    elif fid.startswith("BASE-"):
        if "2단계 승인" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1404
            evidence_text = "| 6 | I-19 | 승인 워크플로우, 타임아웃(10분), P2 게이팅"
            reason = "I-19 Approval Manager가 2단계 승인(P1/P2 게이팅) 포함"

    # === BGNR- items ===
    elif fid.startswith("BGNR-"):
        if "3단 출력" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1413
            evidence_text = "| 10 | I-11 | Output Composer (StructuredOutput 생성, PII 마스킹)"
            reason = "I-11 Output Composer의 StructuredOutput이 3단 출력 구조 포함"

    # === CLIB- items ===
    elif fid.startswith("CLIB-"):
        classification = "TRUE_MISSING"
        reason = "Cloud Library 진화 제어 정책은 PART2/STEP7에 구체적 구현 스펙 없음"

    # === D202- items ===
    elif fid.startswith("D202-"):
        if "응답 길이 자동 조절" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1413
            evidence_text = "| 10 | I-11 | Output Composer (StructuredOutput 생성, PII 마스킹)"
            reason = "I-11 Output Composer가 응답 구성 시 길이 조절 포함"
        elif "감정 히스토리 추적" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1399
            evidence_text = "| 1 | I-1 | IntentFrame 생성, 감정 탐지, 사고 수준 분류"
            reason = "I-1 Intent Detector의 감정 탐지가 히스토리 추적의 상위 모듈"
        elif "PromptCacheManager" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1499
            evidence_text = "| 5 | **Semantic Cache** | cosine >= 0.95 LOCK, 응답 캐싱"
            reason = "V1-Phase 2 Semantic Cache가 프롬프트 캐싱 기능 포함"
        elif "적응형 응답 톤" in fname or "ToneAdapter" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1399
            evidence_text = "| 1 | I-1 | IntentFrame 생성, 감정 탐지, 사고 수준 분류"
            reason = "I-1 감정 탐지 + I-11 Output Composer에서 톤 조절 구현"

    # === D203- items ===
    elif fid.startswith("D203-"):
        if "노드 폭발 방지" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1587
            evidence_text = "| 7 | **Agent Teams V1** | Lead + max 2 Sub-Agent, Sequential/Parallel만"
            reason = "Agent Teams V1의 max 2 Sub-Agent 제한이 노드 폭발 방지 역할"

    # === D204- items ===
    elif fid.startswith("D204-"):
        if "알림 중복 방지" in fname or "debounce" in fname:
            classification = "TRUE_MISSING"
            reason = "알림 debounce 구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "기여 가이드라인" in fname or "CONTRIBUTING" in fname:
            classification = "RECLASSIFIED"
            reason = "문서/프로세스 항목으로 구현 가이드 범위 외"
        elif "R3~R6 추정" in fname:
            classification = "RECLASSIFIED"
            reason = "추정 항목으로 원본 확인 필요한 메타 정보, 구현 스펙이 아님"

    # === D205- items ===
    elif fid.startswith("D205-"):
        if "중앙 프롬프트 라이브러리" in fname:
            classification = "TRUE_MISSING"
            reason = "프롬프트 라이브러리 구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "오케스트레이션 패턴" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1581
            evidence_text = "| 1 | **LangGraph StateGraph** | 5-Phase 완성 (Intake->Plan->Execute->Verify->Deliver)"
            reason = "V1-Phase 3 LangGraph + Agent Teams V1이 오케스트레이션 패턴 포함"
        elif "AgentMode Enum" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1425
            evidence_text = "I-1: `autonomy_level` 기본값 `L2_COPILOT` (PHASE_B4 §3.1 LOCK)"
            reason = "I-1의 autonomy_level 설정이 AgentMode 개념 포함"
        elif "3단 출력" in fname or "user_response" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1413
            evidence_text = "| 10 | I-11 | Output Composer (StructuredOutput 생성, PII 마스킹)"
            reason = "I-11 Output Composer의 StructuredOutput이 3단 출력 구조 포함"

    # === D206- items ===
    elif fid.startswith("D206-"):
        if "커뮤니케이션 스타일 학습" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "STEP7-D"
            evidence_line = 46
            evidence_text = "S7D-001: GPT Memory 패턴 참조 — 자동 사실 추출"
            reason = "STEP7-D S7D-001 자동 사실 추출이 스타일 학습의 상위 기능"
        elif "작업 중단 복원" in fname or "task_checkpoint" in fname:
            classification = "TRUE_MISSING"
            reason = "task_checkpoint 구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "한-영 혼용 문서" in fname or "교차 언어" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1400
            evidence_text = "| 2 | I-2 | RAG 파이프라인, BGE-M3 임베딩, Chroma 검색"
            reason = "I-2 RAG의 BGE-M3 임베딩이 다국어(한-영) 지원 내장"
        elif "동적 청크 크기" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1525
            evidence_text = "Stage 2 Chunk (쪼개기, 300~500tok)"
            reason = "V1-Phase 2 6-Stage RAG Pipeline의 Stage 2 Chunk에 포함"
        elif "M-001 자동 지식 캡처" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "STEP7-D"
            evidence_line = 46
            evidence_text = "S7D-001: GPT Memory 패턴 참조 — 자동 사실 추출"
            reason = "STEP7-D S7D-001이 자동 지식 캡처의 상위 기능"
        elif "M-011 노트 연결" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1498
            evidence_text = "| 4 | **JSON 파일 기반 GraphRAG** | 기본 엔티티/관계 저장, NetworkX"
            reason = "V1-Phase 2 GraphRAG의 엔티티/관계 발견이 노트 연결 포함"
        elif "M-013 지식 요약" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1416
            evidence_text = "| 14 | I-14 | Summarizer, 메모리 증류"
            reason = "I-14 Summarizer가 지식 요약/통합 기능 포함"
        elif "M-017 웹 클리핑" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1589
            evidence_text = "| 9 | **E-2 Web Search** | Tavily/SerpAPI MCP 연결"
            reason = "E-2 Web Search가 웹 콘텐츠 수집의 상위 기능"
        elif "M-027 연구 노트" in fname:
            classification = "TRUE_MISSING"
            reason = "연구 노트/논문 인용 관리 구체적 구현 스펙 없음"
        elif "M-029 코드 스니펫" in fname:
            classification = "TRUE_MISSING"
            reason = "코드 스니펫 라이브러리 구체적 구현 스펙 없음"
        elif "M-031 아이디어 캡처" in fname:
            classification = "TRUE_MISSING"
            reason = "아이디어 캡처(성숙도 추적) 구체적 구현 스펙 없음"
        elif "M-039 다국어 노트" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1643
            evidence_text = "| 14 | **i18n 국제화** | react-i18next, ko-KR/en-US"
            reason = "V1-Phase 4 i18n 국제화가 다국어 노트 지원의 상위 기능"
        elif "M-045" in fname or "M-046" in fname or "M-044" in fname:
            classification = "TRUE_MISSING"
            reason = "지식 기반 응용(의사결정/글쓰기/어시스턴트) 구체적 구현 스펙 없음"
        elif "(Lx, By) 매핑" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1513
            evidence_text = "#### B<->L 매핑 테이블 (D2.0-06 §2.1 + CLAUDE.md §15, LOCK)"
            reason = "V1-Phase 2 B<->L 매핑 테이블에 명시"
        elif "형태소 분석" in fname or "Mecab" in fname:
            classification = "TRUE_MISSING"
            reason = "형태소 분석 기반 토큰화 구체적 구현 스펙 없음"
        elif "한국어 불용어" in fname:
            classification = "TRUE_MISSING"
            reason = "한국어 불용어 처리 구체적 구현 스펙 없음"
        elif "M-049~054 PKM" in fname:
            classification = "RECLASSIFIED"
            reason = "로드맵/참고자료 정리로 구현 가이드 범위 외"

    # === D207- items ===
    elif fid.startswith("D207-"):
        if "2단계 승인 구조" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1404
            evidence_text = "| 6 | I-19 | 승인 워크플로우, 타임아웃(10분), P2 게이팅"
            reason = "I-19 Approval Manager가 계획+실행 2단계 승인 포함"
        elif "감정 적응형 응답" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1399
            evidence_text = "| 1 | I-1 | IntentFrame 생성, 감정 탐지, 사고 수준 분류"
            reason = "I-1 감정 탐지 + I-11 Output Composer가 감정 적응형 응답"
        elif "프라이버시 우선 모드" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1501
            evidence_text = "| 7 | **PII 마스킹** | 주민번호/전화번호/이메일/카드번호 regex"
            reason = "V1-Phase 2 PII 마스킹이 프라이버시 기본 기능 포함"
        elif "스트레스 관리" in fname or "CBT 셀프케어" in fname or "번아웃 예방" in fname:
            classification = "TRUE_MISSING"
            reason = "웰니스 기능 구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "자율 운영 수준 4단계" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1425
            evidence_text = "I-1: `autonomy_level` 기본값 `L2_COPILOT` (PHASE_B4 §3.1 LOCK)"
            reason = "I-1의 autonomy_level이 자율 운영 수준 개념 포함"
        elif "공감 대화 엔진" in fname:
            classification = "TRUE_MISSING"
            reason = "공감 대화 엔진 구체적 구현 스펙 없음"
        elif "웰니스 참고 서비스" in fname:
            classification = "RECLASSIFIED"
            reason = "참고 서비스 정리로 설계문서/조사 수준"

    # === DD4- items ===
    elif fid.startswith("DD4-"):
        if "KBEmbeddingRecord" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1497
            evidence_text = "| 3 | **Chroma Vector DB** | BGE-M3 1024dim, Matryoshka 256dim"
            reason = "V1-Phase 2 Chroma Vector DB 임베딩 저장이 KBEmbeddingRecord 포함"

    # === MSTR- items ===
    elif fid.startswith("MSTR-"):
        classification = "TRUE_MISSING"
        reason = "3종 TemplateSet 구체적 구현 스펙이 PART2/STEP7에 없음"

    # === P30- items ===
    elif fid.startswith("P30-"):
        if "IDEA 40건 로드맵" in fname:
            classification = "RECLASSIFIED"
            reason = "로드맵 추적은 프로젝트 관리 수준, 구현 가이드 범위 외"
        elif "가변 청크 크기" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1525
            evidence_text = "Stage 2 Chunk (쪼개기, 300~500tok)"
            reason = "V1-Phase 2 RAG Pipeline의 Chunk 단계에 포함"

    # === S7AE- items ===
    elif fid.startswith("S7AE-"):
        if "B-006 개발 로드맵" in fname:
            classification = "RECLASSIFIED"
            reason = "개발 로드맵은 프로젝트 관리 수준"
        elif "레이트 리미팅" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "STEP7-E"
            evidence_line = 78
            evidence_text = "LLM04: Model Denial of Service -> Rate limiting + Cost Gate"
            reason = "STEP7-E S7E-003 OWASP LLM04 대응에 Rate limiting 포함"
        elif "세션 관리" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1495
            evidence_text = "| 1 | **L0 Session Memory** | SQLite, TTL=session_end, 자동 정리"
            reason = "V1-Phase 2 L0 Session Memory가 세션 관리 포함"
        elif "권한 관리" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1661
            evidence_text = "| 11 | RBAC 접근 제어 | OWNER/ADMIN/OPERATOR/VIEWER"
            reason = "V1-Phase 4 RBAC 4역할 접근 제어가 권한 관리 포함"
        elif "OpenAPI 스펙" in fname:
            classification = "RECLASSIFIED"
            reason = "OpenAPI 스펙은 API 문서화 수준"
        elif "알림 규칙 엔진" in fname:
            classification = "TRUE_MISSING"
            reason = "알림 규칙 엔진 구체적 구현 스펙 없음"
        elif "인시던트 관리" in fname:
            classification = "RECLASSIFIED"
            reason = "인시던트 관리는 운영 프로세스 수준"
        elif "시크릿 관리" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "STEP7-E"
            evidence_line = 96
            evidence_text = "S7E-005: API Key 관리 — V1: `.env` + `dotenv` + `.gitignore`"
            reason = "STEP7-E S7E-005 API Key 관리가 시크릿 관리 포함"
        elif "보안 스캐닝" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1685
            evidence_text = "| 12 | **보안 감사** | pip-audit, cargo-audit, npm audit"
            reason = "V1-Phase 5 보안 감사가 보안 스캐닝 포함"
        elif "B-004 기술 평가" in fname or "B-011 보안 설계" in fname or "B-023 배포 전략" in fname or "B-025 확장성 설계" in fname or "B-028 품질 관리" in fname:
            classification = "RECLASSIFIED"
            reason = "설계 단계 문서/프로세스 항목, 구현 스펙이 아님"
        elif "마이크로서비스" in fname:
            classification = "RECLASSIFIED"
            reason = "V1은 모놀리스(Tauri+Python), 마이크로서비스는 V3+"
        elif "로드 밸런서" in fname:
            classification = "RECLASSIFIED"
            reason = "V1은 로컬 단일 인스턴스, 로드 밸런서는 V2+"
        elif "서킷 브레이커" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1584
            evidence_text = "| 4 | **Circuit Breaker** | closed/open/half_open, failure_threshold=3"
            reason = "V1-Phase 3 Circuit Breaker 구현 항목에 명시"
        elif "컨피그 서버" in fname:
            classification = "RECLASSIFIED"
            reason = "V1은 로컬 TOML 설정, 중앙 컨피그 서버는 V2+"
        elif "중앙 로깅" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1638
            evidence_text = "| 9 | **Log 페이지** | 로그/감사 뷰어"
            reason = "V1-Phase 4 Log 페이지가 로깅 포함"
        elif "그레이스풀 셧다운" in fname:
            classification = "TRUE_MISSING"
            reason = "그레이스풀 셧다운 구체적 구현 스펙 없음"
        elif "리트라이 정책" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1583
            evidence_text = "| 3 | **Soft/Hard Loop** | 검증 실패 -> 1회 자동 재시도 -> HITL 승인"
            reason = "V1-Phase 3 Soft/Hard Loop이 리트라이 정책 포함"
        elif "캐시 계층" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1499
            evidence_text = "| 5 | **Semantic Cache** | cosine >= 0.95 LOCK, 응답 캐싱"
            reason = "V1-Phase 2 Semantic Cache가 캐시 계층 포함"
        elif "커넥션 풀링" in fname:
            classification = "TRUE_MISSING"
            reason = "커넥션 풀링 구체적 구현 스펙 없음"
        elif "운영" in fname and ("E-0" in fname or "E-01" in fname or "E-02" in fname):
            classification = "RECLASSIFIED"
            reason = "운영 가이드는 구현 후 운영 단계 문서"
        elif "APM 통합" in fname:
            classification = "RECLASSIFIED"
            reason = "APM은 V2+ 모니터링 범위"
        elif "인그레스 컨트롤러" in fname:
            classification = "RECLASSIFIED"
            reason = "V1은 로컬 앱, 인그레스는 V3 K8s"
        elif "블루/그린 배포" in fname:
            classification = "RECLASSIFIED"
            reason = "V1은 로컬 데스크톱, 블루/그린은 V2+"
        elif "백업 검증" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "STEP7-D"
            evidence_line = 84
            evidence_text = "S7D-016: 벡터 DB 백업/복원 — 정기 스냅샷, Point-in-Time 복원"
            reason = "STEP7-D S7D-016 백업/복원이 백업 검증 포함"
        elif "할루시네이션" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1411
            evidence_text = "| 8 | I-6 | Self-check (P0>=70, P1>=75, P2>=80), Soft Loop 1회"
            reason = "I-6 Self-check의 QoD 검증이 할루시네이션 탐지 포함"
        else:
            classification = "RECLASSIFIED"
            reason = "아키텍처/엔지니어링 설계 수준 항목, V1 구현 스펙에 미포함"

    # === S7BG- items ===
    elif fid.startswith("S7BG-"):
        if "할루시네이션 탐지" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1411
            evidence_text = "| 8 | I-6 | Self-check (P0>=70, P1>=75, P2>=80)"
            reason = "I-6 Self-check의 QoD 검증이 할루시네이션 탐지 포함"
        elif "로깅/트레이싱" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1638
            evidence_text = "| 9 | **Log 페이지** | 로그/감사 뷰어"
            reason = "V1-Phase 4 Log 페이지 + JSONL 기반 로깅"
        elif "백테스팅 고급" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 3319
            evidence_text = "| 2 | 백테스트 | vectorbt(조건부 ADOPT) 또는 backtrader |"
            reason = "AI Investing §6.8 백테스트 기술스택에 포함"
        elif "OpenBB v4" in fname:
            classification = "RECLASSIFIED"
            reason = "OpenBB 통합은 외부 라이브러리 참고, V1 스펙에 미포함"

    # === S7FI- items ===
    elif fid.startswith("S7FI-"):
        if "투자 유니버스" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1713
            evidence_text = "| 1 | **Paper Trading MVP** | 시뮬레이션 트레이딩 (51% Gate)"
            reason = "V1-Phase 6 Paper Trading MVP에 투자 대상 관리 포함"
        elif "투자 성과 추적" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1713
            evidence_text = "| 1 | **Paper Trading MVP** | 시뮬레이션 트레이딩 (51% Gate)"
            reason = "V1-Phase 6 Paper Trading MVP에 성과 추적 포함"
        elif "소셜 미디어 분석" in fname:
            classification = "TRUE_MISSING"
            reason = "소셜 미디어 분석 구체적 구현 스펙 없음"
        elif "웹 트래픽 분석" in fname or "앱 다운로드 분석" in fname:
            classification = "RECLASSIFIED"
            reason = "비즈니스 분석 수준, VAMOS 구현 범위 외"
        elif "블랙-리터만" in fname or "팩터 투자" in fname or "리밸런싱 엔진" in fname:
            classification = "TRUE_MISSING"
            reason = "고급 투자 기능 구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "상관관계 분석" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 3320
            evidence_text = "| 3 | 분석 프레임워크 | pandas + numpy + scipy | 없음 |"
            reason = "AI Investing §6.8 분석 프레임워크(scipy)로 상관관계 분석 가능"
        elif "규제 리포팅" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1716
            evidence_text = "| 4 | **법적 컴플라이언스** | Wash Sale, PDT, Uptick Rule 감지"
            reason = "V1-Phase 6 법적 컴플라이언스가 규제 리포팅의 상위 기능"
        elif "GAP" in fname:
            classification = "RECLASSIFIED"
            reason = "GAP 분석/로드맵은 전략 기획 수준"
        elif "모델 버전 관리" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "STEP7-F"
            evidence_line = 49
            evidence_text = "S7F-001: Ollama 기반 로컬 LLM 서빙 — 모델 다운로드/관리"
            reason = "STEP7-F S7F-001 Ollama 모델 관리가 모델 버전 관리 포함"
        elif "환경별 배포" in fname:
            classification = "RECLASSIFIED"
            reason = "V1은 로컬 단일 환경, 환경별 배포는 V2+"
        elif "알림 규칙" in fname:
            classification = "TRUE_MISSING"
            reason = "알림 규칙 구체적 구현 스펙 없음"
        elif "에러 트래킹" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1419
            evidence_text = "| 16 | I-20 | Failure/Fallback Manager"
            reason = "I-20 Failure/Fallback Manager가 에러 트래킹 포함"
        elif "벤치마크" in fname or "태스크 완료율" in fname or "접근성 평가" in fname or "한국 시장 이해도" in fname or "뉴스 분석 품질" in fname:
            classification = "RECLASSIFIED"
            reason = "벤치마크/평가는 QA 프로세스 수준, 구현 스펙이 아님"
        elif any(k in fname for k in ["가격", "경쟁사", "원가", "구독", "프리미엄", "할인", "수익 모델", "페르소나", "페인 포인트", "개인 투자자 프로파일", "SOM 분석", "경쟁사 매핑", "차별화 전략", "SWOT 분석", "경쟁 우위", "포지셔닝", "출시 전략", "마케팅", "리텐션", "재무 모델"]):
            classification = "RECLASSIFIED"
            reason = "비즈니스/마케팅 전략 수준, 구현 스펙이 아님"
        elif any(k in fname for k in ["한국 주식시장", "한국 채권시장", "한국 파생상품", "한국 ETF", "한국 IPO", "한국 공시", "한국 배당"]):
            classification = "RECLASSIFIED"
            reason = "한국 시장 세부 분석은 V1 AI Investing MVP 범위 외"
        elif "암호화폐" in fname or "NFT" in fname:
            classification = "RECLASSIFIED"
            reason = "암호화폐/NFT 분석은 V1 AI Investing 범위 외"
        else:
            classification = "RECLASSIFIED"
            reason = "비즈니스 전략/시장 분석 수준, 구현 스펙이 아님"

    # === S7JM- items ===
    elif fid.startswith("S7JM-"):
        if "스크린 캡처" in fname and "화면 이해" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1592
            evidence_text = "| 12 | **E-5 Image Analyzer** | CLIP MCP 래퍼"
            reason = "E-5 Image Analyzer가 화면 캡처 이해의 상위 기능"
        elif "비전 기반 코드 이해" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1592
            evidence_text = "| 12 | **E-5 Image Analyzer** | CLIP MCP 래퍼"
            reason = "E-5 Image Analyzer가 비전 기반 코드 이해의 상위 기능"
        elif "음성 대화 모드" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1410
            evidence_text = "| 7 | I-4 | Multimodal Interpreter (텍스트/이미지/음성 해석)"
            reason = "I-4 Multimodal Interpreter가 음성 입력 해석 포함"
        elif "오디오 파일 분석" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1410
            evidence_text = "| 7 | I-4 | Multimodal Interpreter (텍스트/이미지/음성 해석)"
            reason = "I-4 Multimodal Interpreter가 오디오 해석 포함"
        elif "음성 품질 최적화" in fname:
            classification = "TRUE_MISSING"
            reason = "음성 품질 최적화 구체적 구현 스펙 없음"
        elif "스프레드시트 분석" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1590
            evidence_text = "| 10 | **E-3 Document Parser** | Unstructured.io MCP, PyMuPDF"
            reason = "E-3 Document Parser가 문서 파싱의 상위 기능"
        elif "코드 자동완성" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1588
            evidence_text = "| 8 | **E-1 Coding Helper** | 코드 생성/디버그/리팩토링"
            reason = "E-1 Coding Helper가 코드 자동완성의 상위 기능"
        elif "디버깅 어시스턴트" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1588
            evidence_text = "| 8 | **E-1 Coding Helper** | 코드 생성/디버그/리팩토링"
            reason = "E-1 Coding Helper가 디버깅 기능 포함"
        elif "성능 프로파일링" in fname:
            classification = "TRUE_MISSING"
            reason = "성능 프로파일링 구체적 구현 스펙 없음"
        elif "데이터베이스 관리 도구" in fname:
            classification = "TRUE_MISSING"
            reason = "데이터베이스 관리 도구 구체적 구현 스펙 없음"
        elif "스크린 캡처 지식화" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1592
            evidence_text = "| 12 | **E-5 Image Analyzer** | CLIP MCP 래퍼"
            reason = "E-5 Image Analyzer + I-14 Summarizer로 캡처 지식화 가능"
        elif "코드 지식 추출" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1588
            evidence_text = "| 8 | **E-1 Coding Helper** | 코드 생성/디버그/리팩토링"
            reason = "E-1 Coding Helper + I-14로 코드 지식 추출 가능"
        elif "음성 메모" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1410
            evidence_text = "| 7 | I-4 | Multimodal Interpreter (텍스트/이미지/음성 해석)"
            reason = "I-4 + I-3 Memory Commit으로 음성->지식 변환 가능"
        elif "지식그래프 자동 구축" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1498
            evidence_text = "| 4 | **JSON 파일 기반 GraphRAG** | 기본 엔티티/관계 저장, NetworkX"
            reason = "V1-Phase 2 GraphRAG가 지식그래프 구축의 상위 기능"
        elif "폴더/노트북 구조" in fname or "Zettelkasten" in fname:
            classification = "TRUE_MISSING"
            reason = "노트 구조 관리 구체적 구현 스펙 없음"
        elif "시간 기반 지식 관리" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1502
            evidence_text = "| 8 | **메모리 B-3 Decay** | TTL 기반 자동 만료, activation_state 관리"
            reason = "B-3 Memory Decay의 TTL 기반 관리가 시간 기반 지식 관리 포함"
        elif "지식 성숙도 추적" in fname:
            classification = "TRUE_MISSING"
            reason = "지식 성숙도 추적 구체적 구현 스펙 없음"
        elif "지식 요약 및 종합" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1416
            evidence_text = "| 14 | I-14 | Summarizer, 메모리 증류"
            reason = "I-14 Summarizer가 지식 요약 기능 포함"
        elif "지식 연결 탐색" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1498
            evidence_text = "| 4 | **JSON 파일 기반 GraphRAG** | 기본 엔티티/관계 저장, NetworkX"
            reason = "GraphRAG의 그래프 검색이 지식 연결 탐색 포함"
        elif "스마트 리마인더" in fname or "지식 버전 관리" in fname or "개인 위키" in fname:
            classification = "TRUE_MISSING"
            reason = "구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "지식 기반 개인 어시스턴트" in fname or "지식 기반 의사결정" in fname or "지식 기반 글쓰기" in fname:
            classification = "TRUE_MISSING"
            reason = "지식 기반 응용 구체적 구현 스펙 없음"
        elif "LlamaIndex 통합" in fname:
            classification = "RECLASSIFIED"
            reason = "VAMOS는 자체 RAG 파이프라인 사용, LlamaIndex는 외부 참고"
        elif "자동 온톨로지 구축" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1498
            evidence_text = "| 4 | **JSON 파일 기반 GraphRAG** | 기본 엔티티/관계 저장, NetworkX"
            reason = "GraphRAG의 엔티티/관계 추출이 온톨로지 구축의 기반"
        elif "투자 차트" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 3321
            evidence_text = "| 4 | 시각화 | plotly + matplotlib | 없음 |"
            reason = "AI Investing §6.8 시각화(plotly+matplotlib)로 차트 생성 포함"
        elif "마인드맵" in fname:
            classification = "TRUE_MISSING"
            reason = "마인드맵 자동 생성 구체적 구현 스펙 없음"
        elif "참고 오픈소스" in fname or "참고 사례" in fname or "참고 표준문서" in fname:
            classification = "RECLASSIFIED"
            reason = "참고 자료 정리는 설계/조사 수준"
        elif "투자+코딩 통합" in fname:
            classification = "RECLASSIFIED"
            reason = "통합 비전은 설계 수준"
        elif "온보딩 마법사" in fname or "대화형 튜토리얼" in fname:
            classification = "TRUE_MISSING"
            reason = "구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "다국어 지원 DX" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1643
            evidence_text = "| 14 | **i18n 국제화** | react-i18next, ko-KR/en-US"
            reason = "V1-Phase 4 i18n 국제화가 다국어 DX 포함"
        elif "지식 임포트/익스포트" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1500
            evidence_text = "| 6 | **대화 내보내기/가져오기** | JSON/Markdown export, import"
            reason = "V1-Phase 2 대화 내보내기/가져오기가 지식 임포트/익스포트의 상위 기능"
        else:
            classification = "TRUE_MISSING"
            reason = "PART2/STEP7에 구체적 구현 스펙 없음"

    # === S7NP- items ===
    elif fid.startswith("S7NP-"):
        if "루프/반복 처리" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1583
            evidence_text = "| 3 | **Soft/Hard Loop** | 검증 실패 -> 1회 자동 재시도 -> HITL 승인"
            reason = "V1-Phase 3 Soft/Hard Loop이 루프/반복 처리 포함"
        elif "폼 자동 입력" in fname or "Notion/Obsidian" in fname:
            classification = "TRUE_MISSING"
            reason = "구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "개인화 학습 경로" in fname or "플래시카드" in fname or "간격 반복" in fname or "퀴즈 자동 생성" in fname or "학습 진도 추적" in fname:
            classification = "TRUE_MISSING"
            reason = "학습 기능 구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "소크라테스식 대화" in fname:
            classification = "TRUE_MISSING"
            reason = "구체적 구현 스펙 없음"
        elif "코딩 실습 환경" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1591
            evidence_text = "| 11 | **E-4 Code Executor** | Docker 샌드박스 LOCK, E2B"
            reason = "E-4 Code Executor가 코딩 실습 환경의 상위 기능"
        elif "논문 읽기 도우미" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1590
            evidence_text = "| 10 | **E-3 Document Parser** | Unstructured.io MCP, PyMuPDF"
            reason = "E-3 Document Parser가 논문(PDF) 파싱의 상위 기능"
        elif "독서 관리" in fname or "학습 목표" in fname or "마이크로러닝" in fname or "학습 동기" in fname:
            classification = "TRUE_MISSING"
            reason = "구체적 구현 스펙이 PART2/STEP7에 없음"
        elif "교육 차별화" in fname or "웰니스 차별화" in fname:
            classification = "RECLASSIFIED"
            reason = "차별화 전략은 기획 수준"
        elif "교육 다국어" in fname or "웰니스 다국어" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1643
            evidence_text = "| 14 | **i18n 국제화** | react-i18next, ko-KR/en-US"
            reason = "V1-Phase 4 i18n 국제화가 다국어 지원 포함"
        elif "감정 대응 대화" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1399
            evidence_text = "| 1 | I-1 | IntentFrame 생성, 감정 탐지, 사고 수준 분류"
            reason = "I-1의 감정 탐지가 감정 대응 대화의 상위 기능"
        elif "스트레스 관리" in fname or "수면 개선" in fname or "습관 추적기" in fname or "일기 작성" in fname or "감정 일지" in fname or "긍정 심리" in fname:
            classification = "TRUE_MISSING"
            reason = "웰니스 기능 구체적 구현 스펙 없음"
        elif "목표 설정/추적" in fname or "집중 모드" in fname or "포모도로" in fname or "웰니스 알림" in fname or "번아웃 예방" in fname:
            classification = "TRUE_MISSING"
            reason = "생산성/웰니스 기능 구체적 구현 스펙 없음"
        elif "대화 분기 관리" in fname:
            classification = "TRUE_MISSING"
            reason = "대화 분기 관리 구체적 구현 스펙 없음"
        elif "입력 검증" in fname or "Injection 방지" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 3118
            evidence_text = "| 입력 검증 | Zod + regex 패턴 | V1 |"
            reason = "PART2 §6.5 보안 입력 검증(Zod + regex)에 포함"
        elif "지식-투자-코딩 통합" in fname:
            classification = "RECLASSIFIED"
            reason = "통합 비전은 설계 수준"
        elif "학습 분석 대시보드" in fname or "웰빙 대시보드" in fname:
            classification = "TRUE_MISSING"
            reason = "대시보드 구체적 구현 스펙 없음"
        elif "언어 학습 특화" in fname or "투자 교육 특화" in fname:
            classification = "TRUE_MISSING"
            reason = "교육 특화 구체적 구현 스펙 없음"
        elif "코딩 교육 특화" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1588
            evidence_text = "| 8 | **E-1 Coding Helper** | 코드 생성/디버그/리팩토링"
            reason = "E-1 Coding Helper가 코딩 교육의 상위 기능"
        elif "교육 접근성" in fname or "웰니스 접근성" in fname:
            classification = "RECLASSIFIED"
            reason = "접근성은 UX 가이드라인 수준"
        elif "키보드 내비게이션" in fname:
            classification = "TRUE_MISSING"
            reason = "키보드 내비게이션 구체적 구현 스펙 없음"
        elif "투자 심리 분석" in fname or "감정적 투자 방지" in fname:
            classification = "TRUE_MISSING"
            reason = "투자 심리 관련 구체적 구현 스펙 없음"
        elif "OpenBB" in fname:
            classification = "RECLASSIFIED"
            reason = "OpenBB 통합은 외부 참고, V1 스펙에 미포함"
        else:
            classification = "TRUE_MISSING"
            reason = "PART2/STEP7에 구체적 구현 스펙 없음"

    # === TEAM- items ===
    elif fid.startswith("TEAM-"):
        if "AgentMatcher" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1587
            evidence_text = "| 7 | **Agent Teams V1** | Lead + max 2 Sub-Agent, Sequential/Parallel만"
            reason = "Agent Teams V1의 에이전트 선택/라우팅이 AgentMatcher 포함"
        elif "TaskDecomposer" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1581
            evidence_text = "| 1 | **LangGraph StateGraph** | 5-Phase 완성 (Intake->Plan->Execute->Verify->Deliver)"
            reason = "LangGraph Plan Phase에서 작업 분해 수행"
        elif "DelegationSecurityGuard" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1617
            evidence_text = "| 10 | 위임 깊이 제한 | 최대 2단계 (LOCK-AT-004)"
            reason = "V1-Phase 3 위임 깊이 제한이 위임 공격 방어 포함"
        elif "TeamCostManager" in fname or "CostTracker" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1420
            evidence_text = "| 17 | I-9 | Cost Manager (비용 추적, 다운시프트, 토큰 카운팅)"
            reason = "I-9 Cost Manager가 에이전트별 비용 추적의 상위 기능"
        elif "FileOwnership" in fname:
            classification = "TRUE_MISSING"
            reason = "FileOwnership 모델 구체적 구현 스펙 없음"
        elif "AgentLifecycleManager" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1587
            evidence_text = "| 7 | **Agent Teams V1** | Lead + max 2 Sub-Agent"
            reason = "Agent Teams V1이 에이전트 생성/종료 관리 포함"
        elif "ResearchAgent" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1589
            evidence_text = "| 9 | **E-2 Web Search** | Tavily/SerpAPI MCP 연결"
            reason = "E-2 Web Search + Agent Teams V1으로 리서치 에이전트 구현 가능"
        elif "ContentAgent" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1587
            evidence_text = "| 7 | **Agent Teams V1** | Lead + max 2 Sub-Agent"
            reason = "Agent Teams V1 Sub-Agent로 콘텐츠 에이전트 구현 가능"
        elif "CriticAgent" in fname:
            classification = "UPPER_MODULE"
            evidence_source = "PART2"
            evidence_line = 1594
            evidence_text = "| 14 | **C-1~C-3** | Logic Verifier/Math Verifier/Code Verifier"
            reason = "C-1~C-3 Verifier가 CriticAgent 검증의 상위 모듈"
        else:
            classification = "TRUE_MISSING"
            reason = "PART2/STEP7에 구체적 구현 스펙 없음"

    results.append({
        "feature_id": fid,
        "classification": classification,
        "evidence_source": evidence_source,
        "evidence_line": evidence_line,
        "evidence_text": evidence_text,
        "reason": reason
    })

# Count results
from collections import Counter
counts = Counter(r["classification"] for r in results)
print(f"\nClassification summary:")
for k, v in sorted(counts.items()):
    print(f"  {k}: {v}")
print(f"  Total: {sum(counts.values())}")

# Save results
with open("D:/VAMOS/04. 구현단계/v10_results/phase2/nf_M-2_verified.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(results)} items to nf_M-2_verified.json")
