#!/usr/bin/env python3
"""
Phase 0-C Agent C-4: Feature extraction from D2.0-06 and D2.0-07
Generates v10_src_C04.json
"""
import json
from datetime import datetime

features = []

def add(fid, src, line, section, name, ver, cat, impl, deps=None, extractable=True, conf="명시적", notes=""):
    features.append({
        "feature_id": fid,
        "source_file": src,
        "source_line": line,
        "source_section": section,
        "feature_name": name,
        "version_scope": ver,
        "category": cat,
        "implementation_type": impl,
        "dependencies": deps or [],
        "extractable": extractable,
        "confidence": conf,
        "notes": notes
    })

# ============================================================
# D2.0-06 STORAGE/MEMORY FEATURES
# ============================================================

# §1.1 RAG Pipeline
add("D206-001", "D2.0-06", "64-78", "§1.1 RAG 파이프라인 6단계", "RAG 6단계 파이프라인 구현 (Collect→Chunk→Embed→Store→Retrieve→Generate)", "V1,V2,V3", "FT-FUNC", "신규구현", notes="LOCK. 각 단계 독립 모듈 구현")
add("D206-002", "D2.0-06", 77, "§1.1 RAG 파이프라인", "RAG 운영 한계 설정 (문서 15개/청크 30개)", "V1,V2", "FT-CFG", "설정")
add("D206-003", "D2.0-06", 78, "§1.1 RAG 파이프라인", "RAG 파이프라인 실패 시 레지스트리 failure_code 기록", "V1,V2,V3", "FT-FUNC", "신규구현")

# §2 Memory Hierarchy
add("D206-004", "D2.0-06", "80-116", "§2 메모리 계층(L0~L3)", "L0 Session Memory 구현 (인메모리, 세션 단기)", "V1", "FT-MOD", "신규구현", notes="LOCK. B-4 Working 연결")
add("D206-005", "D2.0-06", "90-93", "§2 메모리 계층", "L1 Project Memory 구현 (project_id 단위)", "V1", "FT-MOD", "신규구현", notes="LOCK. B-1 Episodic 연결")
add("D206-006", "D2.0-06", "94-97", "§2 메모리 계층", "L2 Long-term Knowledge 구현 (전역 검색 기반)", "V2", "FT-MOD", "신규구현", notes="LOCK. B-3 Semantic 연결")
add("D206-007", "D2.0-06", "98-101", "§2 메모리 계층", "L3 Procedural Memory 구현 (절차/플레이북)", "V2,V3", "FT-MOD", "신규구현", notes="LOCK. B-2 Procedural 연결. D7 게이트 필수")
add("D206-008", "D2.0-06", "109-116", "§2 메모리 계층", "(Lx, By) 매핑 규칙 구현", "V1,V2,V3", "FT-CFG", "설정", notes="LOCK")

# §2.2 Storage Stack
add("D206-009", "D2.0-06", "142-148", "§2.2 P1-STORAGE", "V1 저장 스택: SQLite + JSONL + Chroma", "V1", "FT-INFRA", "인프라", notes="LOCK")
add("D206-010", "D2.0-06", "149-153", "§2.2 P1-STORAGE", "V2 저장 스택: Postgres + Qdrant", "V2", "FT-INFRA", "인프라", notes="LOCK")
add("D206-011", "D2.0-06", "155-158", "§2.2 P1-STORAGE", "V3 저장 스택: 매니지드 Postgres/Qdrant Cloud", "V3", "FT-INFRA", "인프라", notes="LOCK")
add("D206-012", "D2.0-06", 146, "§2.2 P1-STORAGE", "BGE-M3 임베딩 모델 통합 (1024dim/Matryoshka 256dim)", "V1,V2,V3", "FT-MOD", "신규구현", notes="DEC-005 UPDATED")

# §2.2-A VectorStore Adapter
add("D206-013", "D2.0-06", "172-184", "§2.2-A VectorStore 어댑터", "VectorStore 추상 인터페이스 구현 (upsert/search/delete/get_by_id)", "V1,V2,V3", "FT-API", "신규구현", notes="LOCK")
add("D206-014", "D2.0-06", 181, "§2.2-A VectorStore 어댑터", "ChromaAdapter 구현 (V1 로컬)", "V1", "FT-MOD", "신규구현")
add("D206-015", "D2.0-06", 182, "§2.2-A VectorStore 어댑터", "QdrantAdapter 구현 (V2 서버)", "V2", "FT-MOD", "신규구현")
add("D206-016", "D2.0-06", 183, "§2.2-A VectorStore 어댑터", "매니지드 Vector DB 어댑터 (V3)", "V3", "FT-MOD", "신규구현")

# §2.3 Memory Activation by Version
add("D206-017", "D2.0-06", "186-204", "§2.3 Memory Activation", "V1 메모리 활성화 정책 (L0 활성, L1 선택, L2/L3 비활성)", "V1", "FT-CFG", "설정", notes="P1-SCOPE: MUST")
add("D206-018", "D2.0-06", "196-200", "§2.3 Memory Activation", "V2 메모리 활성화 정책 (L0/L1 활성, L2/L3 제한적)", "V2", "FT-CFG", "설정")
add("D206-019", "D2.0-06", "201-204", "§2.3 Memory Activation", "V3 메모리 활성화 정책 (L0~L3 전체 활성)", "V3", "FT-CFG", "설정")

# §2.4 B-2 Procedural Memory
add("D206-020", "D2.0-06", "206-248", "§2.4 B-2 Procedural Memory", "L3 Procedural Memory 상세 스키마 (procedure_id, version, steps 등)", "V2,V3", "FT-SCHEMA", "신규구현")
add("D206-021", "D2.0-06", "238-244", "§2.4.3 생성/승격 파이프라인", "L3 Procedural 생성/승격 파이프라인 (Candidate→PolicyCheck→Approval→저장→활성)", "V2,V3", "FT-FUNC", "신규구현")
add("D206-022", "D2.0-06", "245-248", "§2.4.4 폐기/롤백", "L3 Procedural 폐기/롤백 메커니즘", "V2,V3", "FT-FUNC", "신규구현")

# §2.5 Memory Redesign
add("D206-023", "D2.0-06", "253-278", "§2.5 메모리 재설계", "통합 메모리 모델 전환 (계층+B-Series+QoD+TTL)", "V1,V2,V3", "FT-FUNC", "신규구현", notes="ADD-053~056")
add("D206-024", "D2.0-06", "259-262", "§2.5.2 SourceQoD 연동", "SourceQoD 스코어 산출/기록 모듈 (0~1)", "V1,V2,V3", "FT-MOD", "신규구현")
add("D206-025", "D2.0-06", "264-272", "§2.5.3 TTL 정책", "계층별 TTL 정책 구현 (L0 세션종료/L1 90일/L2 무기한/L3 정책기반)", "V1,V2,V3", "FT-CFG", "설정")
add("D206-026", "D2.0-06", "274-277", "§2.5.4 KB 연동", "L2↔외부 KB 동기화 모듈", "V2,V3", "FT-FUNC", "신규구현")

# STEP7-D items in §2
add("D206-027", "D2.0-06", "283-288", "§2 STEP7 S7D-001", "자동 사실 추출 (GPT Memory 패턴)", "V1", "FT-FUNC", "신규구현")
add("D206-028", "D2.0-06", "290-295", "§2 STEP7 S7D-002", "기억해줘/잊어줘 명시 명령 처리", "V1", "FT-FUNC", "신규구현")
add("D206-029", "D2.0-06", "297-301", "§2 STEP7 S7D-035~037", "L0/L1/L2 메모리 구현 (3건 통합)", "V1", "FT-MOD", "신규구현")
add("D206-030", "D2.0-06", "303-307", "§2 STEP7 S7D-042", "메모리 검색 우선순위 구현 (L0→L1→L2→L3)", "V1", "FT-FUNC", "신규구현")
add("D206-031", "D2.0-06", "309-315", "§2 STEP7 S7D-007", "메모리 사용 로그 (감사 로그)", "V1", "FT-FUNC", "신규구현")
add("D206-032", "D2.0-06", "317-323", "§2 STEP7 S7D-008", "메모리 내보내기/가져오기 (JSON/SQLite)", "V1", "FT-FUNC", "신규구현")
add("D206-033", "D2.0-06", "325-333", "§2 STEP7 S7D-038", "L3 절차/템플릿 메모리 구현", "V1", "FT-MOD", "신규구현")
add("D206-034", "D2.0-06", "335-341", "§2 STEP7 S7D-040", "메모리 승격 알고리즘 (L0→L1→L2→L3)", "V1", "FT-FUNC", "신규구현")
add("D206-035", "D2.0-06", "343-347", "§2 STEP7 S7-A-030", "Claude Projects 동등 기능 (project_id 격리)", "V1", "FT-FUNC", "신규구현")
add("D206-036", "D2.0-06", "349-353", "§2 STEP7 S7-A-031", "Claude Memory 동등 기능 (크로스 대화 메모리)", "V1", "FT-FUNC", "신규구현")
add("D206-037", "D2.0-06", "355-359", "§2 STEP7 S7-F-022", "커뮤니케이션 스타일 학습", "V1", "FT-FUNC", "신규구현")
add("D206-038", "D2.0-06", "361-365", "§2 STEP7 S7-F-023", "작업 패턴 프로파일", "V2", "FT-FUNC", "신규구현")
add("D206-039", "D2.0-06", "367-371", "§2 STEP7 S7-F-026", "작업 중단 복원 (task_checkpoint)", "V1", "FT-FUNC", "신규구현")
add("D206-040", "D2.0-06", "373-379", "§2 STEP7 S7-F-061", "오프라인 지식 정리 (Dream Mode)", "V2", "FT-FUNC", "신규구현")
add("D206-041", "D2.0-06", "381-385", "§2 STEP7 S7-F-096", "컨텍스트 윈도우 관리 (<10K/10K~200K/200K+)", "V1", "FT-FUNC", "신규구현")
add("D206-042", "D2.0-06", "387-393", "§2 STEP7 S7D-003", "메모리 충돌 해소 (contradiction_resolver)", "V2", "FT-MOD", "신규구현")
add("D206-043", "D2.0-06", "395-400", "§2 STEP7 S7D-004", "메모리 적중률 추적 (hits/misses per layer)", "V2", "FT-FUNC", "신규구현")
add("D206-044", "D2.0-06", "402-407", "§2 STEP7 S7D-005", "메모리 신선도 관리 (freshness_score)", "V2", "FT-FUNC", "신규구현")
add("D206-045", "D2.0-06", "409-416", "§2 STEP7 S7D-041", "메모리 강등/삭제 알고리즘", "V2", "FT-FUNC", "신규구현")
add("D206-046", "D2.0-06", "418-423", "§2 STEP7 S7D-044", "메모리 중복 제거 (cosine >0.95)", "V2", "FT-FUNC", "신규구현")
add("D206-047", "D2.0-06", "425-430", "§2 STEP7 S7D-006", "크로스 프로젝트 메모리 검색", "V2", "FT-FUNC", "신규구현")
add("D206-048", "D2.0-06", "432-437", "§2 STEP7 S7D-039", "아카이브 메모리 구현 (V2+ 확장)", "V3", "FT-MOD", "신규구현")
add("D206-049", "D2.0-06", "439-444", "§2 STEP7 S7D-045", "메모리 사용 통계 대시보드", "V3", "FT-UI", "신규구현")
add("D206-050", "D2.0-06", "447-452", "§2 STEP7 S7D-046", "사용자 확인 후 저장 UX", "V1,V3", "FT-UI", "신규구현")
add("D206-051", "D2.0-06", "454-457", "§2 STEP7 INNOV-09", "AI Personality Evolution 메커니즘", "V1", "FT-FUNC", "신규구현", conf="추론", notes="V1 + MEDIUM 우선순위")

# §3 Storage Policies
add("D206-052", "D2.0-06", "535-571", "§3 저장 정책", "Allow/Restrict/Deny 저장 정책 구현 (계층별)", "V1,V2,V3", "FT-SEC", "신규구현", notes="LOCK")
add("D206-053", "D2.0-06", "573-580", "§3.3 로그/트레이스", "로그/트레이스 원문 저장 금지 + 마스킹 구현", "V1,V2,V3", "FT-SEC", "신규구현")
add("D206-054", "D2.0-06", "586-600", "§3 STEP7 S7D-066", "PII 자동 감지 + 마스킹 (정규식+NER)", "V1", "FT-SEC", "신규구현")
add("D206-055", "D2.0-06", "592-600", "§3 STEP7 S7D-065", "데이터 분류 체계 (4등급 민감도)", "V1", "FT-SEC", "신규구현")
add("D206-056", "D2.0-06", "602-606", "§3 STEP7 S7D-054", "캐시 프라이버시 (민감 데이터 캐시 제외)", "V1,V3", "FT-SEC", "설정")
add("D206-057", "D2.0-06", "608-612", "§3 STEP7 S7D-068", "완전 삭제 보장 (GDPR 잊힐 권리)", "V2", "FT-SEC", "신규구현")
add("D206-058", "D2.0-06", "614-618", "§3 STEP7 S7D-069", "암호화 저장 (AES-256, PBKDF2)", "V1,V2", "FT-SEC", "신규구현")
add("D206-059", "D2.0-06", "620-624", "§3 STEP7 S7D-070", "데이터 보존 정책 (법적 요건 대응)", "V2", "FT-CFG", "설정")
add("D206-060", "D2.0-06", "626-631", "§3 STEP7 S7D-071", "감사 로그 저장 (해시체인 무결성)", "V2", "FT-SEC", "신규구현")

# §4 RAG Indexing
add("D206-061", "D2.0-06", "641-657", "§4.1 운영 한계", "인덱싱 운영 한계 설정 (doc≤15, chunk≤30) + 예산 기반 가변", "V1,V2,V3", "FT-CFG", "설정", notes="LOCK")
add("D206-062", "D2.0-06", "646-649", "§4.1 RAG 재시도", "RAG 재시도 정책 (max_retry=3, BM25 폴백→캐시→단독)", "V1,V2,V3", "FT-FUNC", "신규구현")

# §4.3 Korean RAG
add("D206-063", "D2.0-06", "661-681", "§4.3 한국어 RAG", "형태소 분석 기반 토큰화 (Mecab-ko V1/Kiwi V2)", "V1,V2", "FT-MOD", "신규구현")
add("D206-064", "D2.0-06", "670-672", "§4.3.2 불용어", "한국어 불용어 처리", "V1", "FT-CFG", "설정")
add("D206-065", "D2.0-06", "674-677", "§4.3.3 한-영 혼용", "한-영 혼용 문서 처리 (language 메타, 교차 언어 검색)", "V1,V2", "FT-FUNC", "신규구현")
add("D206-066", "D2.0-06", "694-695", "§4.3 Contextual Retrieval", "Contextual Retrieval 벤치마크 적용 (67% 향상)", "V1", "FT-FUNC", "신규구현")

# §4.x~4.z
add("D206-067", "D2.0-06", "697-701", "§4.x GraphRAG", "GraphRAG 연동 (벡터+그래프 hybrid)", "V2", "FT-FUNC", "신규구현")
add("D206-068", "D2.0-06", "706-709", "§4.y.1 RAGAS", "RAGAS 평가 파이프라인 구현", "V2", "FT-TEST", "신규구현")
add("D206-069", "D2.0-06", "711-713", "§4.y.2 Multi-Retriever", "다중 검색기 (BM25+Graph+메타필터, RRF 통합)", "V2", "FT-FUNC", "신규구현")
add("D206-070", "D2.0-06", "715-717", "§4.y.3 임베딩 벤치마크", "임베딩 모델 벤치마크 (Recall@K, MRR)", "V2", "FT-TEST", "신규구현")
add("D206-071", "D2.0-06", "719-723", "§4.y.4 Codebase Indexing", "소스코드 Codebase Indexing (함수/클래스 단위)", "V2", "FT-FUNC", "신규구현")
add("D206-072", "D2.0-06", "725-736", "§4.z CLib QoD", "Cloud Library 출처별 QoD 가중치 설정", "V1,V2,V3", "FT-CFG", "설정")

# §4.7 Semantic Cache
add("D206-073", "D2.0-06", "738-757", "§4.7 Semantic Cache", "Semantic Cache 구현 (cosine ≥0.95, TTL 24h)", "V1,V2", "FT-MOD", "신규구현", notes="ADD-012/MOD-017")
add("D206-074", "D2.0-06", "748-753", "§4.7.2 캐시 무효화", "캐시 무효화 정책 (TTL+소스변경+QoD변동+수동)", "V1,V2", "FT-FUNC", "신규구현")
add("D206-075", "D2.0-06", "755-757", "§4.7.3 캐시 모니터링", "캐시 모니터링 (히트율, 응답시간 절감)", "V2", "FT-UI", "신규구현")

# §4 STEP7 items
add("D206-076", "D2.0-06", "763-768", "§4 STEP7 S7D-009", "V1 Chroma 임베디드 설정 (3 컬렉션)", "V1", "FT-INFRA", "인프라")
add("D206-077", "D2.0-06", "770-774", "§4 STEP7 S7D-027", "V1 BGE-M3 로컬 임베딩 (256dim Matryoshka)", "V1", "FT-MOD", "신규구현")
add("D206-078", "D2.0-06", "776-780", "§4 STEP7 S7D-012", "하이브리드 검색 구현 (BM25+Vector, alpha=0.3)", "V1", "FT-FUNC", "신규구현")
add("D206-079", "D2.0-06", "782-787", "§4 STEP7 S7D-055", "문서 수집 파이프라인 (PDF/DOCX/HTML 등)", "V1", "FT-FUNC", "신규구현")
add("D206-080", "D2.0-06", "789-792", "§4 STEP7 S7D-058", "임베딩 + 인덱싱 자동화 (증분)", "V1", "FT-FUNC", "신규구현")
add("D206-081", "D2.0-06", "794-798", "§4 STEP7 S7D-019", "V1 경량 KG: NetworkX + JSON", "V1", "FT-MOD", "신규구현")
add("D206-082", "D2.0-06", "800-805", "§4 STEP7 S7D-020", "KG 스키마 설계 (Node/Edge)", "V1", "FT-SCHEMA", "신규구현")
add("D206-083", "D2.0-06", "807-809", "§4 STEP7 S7-F-001", "KG 자동 구축 (엔티티/관계 추출)", "V1,V2", "FT-FUNC", "신규구현")
add("D206-084", "D2.0-06", "811-813", "§4 STEP7 S7-F-005", "Digital Twin 기본 (사용자 프로필 모델)", "V2", "FT-FUNC", "신규구현")
add("D206-085", "D2.0-06", "815-817", "§4 STEP7 S7-P-001", "GraphRAG 핵심 구현", "V2", "FT-FUNC", "신규구현")
add("D206-086", "D2.0-06", "819-821", "§4 STEP7 S7-P-002", "CRAG (Corrective RAG) 구현", "V2", "FT-FUNC", "신규구현")
add("D206-087", "D2.0-06", "823-825", "§4 STEP7 S7-P-003", "Self-RAG 자기 평가 루프", "V2", "FT-FUNC", "신규구현")
add("D206-088", "D2.0-06", "827-829", "§4 STEP7 S7-P-004", "Contextual Retrieval (청킹+문맥)", "V1", "FT-FUNC", "신규구현")
add("D206-089", "D2.0-06", "831-833", "§4 STEP7 S7-P-005", "ColPali 멀티모달 RAG", "V3", "FT-FUNC", "신규구현")
add("D206-090", "D2.0-06", "835-841", "§4 STEP7 S7D-011", "벡터 인덱스 컬렉션 전략 (도메인별 분리)", "V1,V2", "FT-CFG", "설정")
add("D206-091", "D2.0-06", "843-848", "§4 STEP7 S7D-014", "벡터 차원 선택 전략 (256 vs 1024)", "V1,V2", "FT-CFG", "설정")
add("D206-092", "D2.0-06", "851-857", "§4 STEP7 S7D-018", "Cross-Encoder 재순위화", "V1", "FT-MOD", "신규구현")
add("D206-093", "D2.0-06", "859-865", "§4 STEP7 S7D-028", "임베딩 캐싱 (sha256 key, LRU)", "V1", "FT-FUNC", "신규구현")
add("D206-094", "D2.0-06", "867-872", "§4 STEP7 S7D-029", "다국어 임베딩 전략 (교차 언어 검색)", "V1", "FT-FUNC", "신규구현")
add("D206-095", "D2.0-06", "874-881", "§4 STEP7 S7D-048", "Semantic Cache 구현 상세 (GPTCache 참조)", "V1", "FT-MOD", "신규구현")
add("D206-096", "D2.0-06", "883-888", "§4 STEP7 S7D-050", "결과 캐시 (외부 API/MCP 결과)", "V1", "FT-FUNC", "신규구현")
add("D206-097", "D2.0-06", "890-896", "§4 STEP7 S7D-051", "캐시 무효화 정책 (TTL+이벤트+수동)", "V1", "FT-FUNC", "신규구현")
add("D206-098", "D2.0-06", "898-903", "§4 STEP7 S7D-053", "캐시 크기 제한 (V1:500MB, LRU)", "V1,V2,V3", "FT-CFG", "설정")
add("D206-099", "D2.0-06", "905-913", "§4 STEP7 S7D-056", "동적 청킹 전략 (문서유형별)", "V1", "FT-FUNC", "신규구현")
add("D206-100", "D2.0-06", "915-920", "§4 STEP7 S7D-057", "Contextual Retrieval 구현 (프리픽스 자동 삽입)", "V1", "FT-FUNC", "신규구현")
add("D206-101", "D2.0-06", "922-931", "§4 STEP7 S7D-059", "메타데이터 태깅 (자동, 6필드)", "V1", "FT-FUNC", "신규구현")
add("D206-102", "D2.0-06", "933-937", "§4 STEP7 S7-A-034", "Prompt Caching (입력, 90% 비용 절감)", "V1", "FT-FUNC", "신규구현")
add("D206-103", "D2.0-06", "939-943", "§4 STEP7 S7-B-016", "Prompt Cache 최적화 (50%+ 비용 절감)", "V1", "FT-FUNC", "신규구현")
add("D206-104", "D2.0-06", "945-948", "§4 STEP7 S7-I-006", "오픈소스 임베딩 활용 (BGE-M3, E5)", "V1", "FT-CFG", "설정")
add("D206-105", "D2.0-06", "951-955", "§4 STEP7 S7-J-005", "Fragment Injection (관련 조각만 컨텍스트 주입)", "V1", "FT-FUNC", "신규구현")
add("D206-106", "D2.0-06", "957-960", "§4 STEP7 S7-K-002", "Semantic Index (로컬 파일 시맨틱 인덱싱)", "V1", "FT-FUNC", "신규구현")
add("D206-107", "D2.0-06", "962-965", "§4 STEP7 S7-P-009", "동적 청크 크기 최적화", "V1", "FT-FUNC", "신규구현")

# R2 J 멀티모달
add("D206-108", "D2.0-06", "969-973", "§4 R2 J-007", "멀티모달 임베딩 통합검색 (CLIP)", "V2", "FT-FUNC", "신규구현")
add("D206-109", "D2.0-06", "975-978", "§4 R2 J-031", "오디오 인덱싱/검색 (Whisper 전사)", "V1", "FT-FUNC", "신규구현")
add("D206-110", "D2.0-06", "980-984", "§4 R2 J-051", "멀티모달 문서 청킹", "V2", "FT-FUNC", "신규구현")
add("D206-111", "D2.0-06", "986-988", "§4 R2 J-052", "이미지-텍스트 크로스검색", "V2", "FT-FUNC", "신규구현")
add("D206-112", "D2.0-06", "990-993", "§4 R2 J-053", "테이블/스프레드시트 RAG (Text-to-SQL)", "V2", "FT-FUNC", "신규구현")
add("D206-113", "D2.0-06", "995-999", "§4 R2 J-054", "코드 RAG (tree-sitter)", "V1", "FT-FUNC", "신규구현")
add("D206-114", "D2.0-06", "1001-1004", "§4 R2 J-064", "멀티모달 메모리 통합", "V2", "FT-FUNC", "신규구현")
add("D206-115", "D2.0-06", "1006-1009", "§4 R2 J-068", "개인 멀티미디어 라이브러리", "V2", "FT-FUNC", "신규구현")

# R2 B+보강
add("D206-116", "D2.0-06", "1013-1017", "§4 R2 S7B-025", "대화 히스토리 검색", "V1", "FT-FUNC", "신규구현")
add("D206-117", "D2.0-06", "1019-1023", "§4 D-ADD-01", "MemGPT/Letta 패턴 통합", "V2", "FT-FUNC", "신규구현")
add("D206-118", "D2.0-06", "1025-1029", "§4 D-ADD-02", "LightRAG 경량 RAG", "V1", "FT-FUNC", "신규구현")
add("D206-119", "D2.0-06", "1031-1034", "§4 D-ADD-03", "RadixAttention KV 캐시 패턴", "V1", "FT-FUNC", "신규구현", conf="추론", notes="V1 + MEDIUM")

# V2 items
add("D206-120", "D2.0-06", "1036-1045", "§4 S7D-010", "V2 Qdrant 서버 전환 + Chroma→Qdrant 마이그레이션", "V2", "FT-MIG", "마이그레이션")
add("D206-121", "D2.0-06", "1047-1053", "§4 S7D-021", "자동 엔티티/관계 추출 (NER+RE)", "V2", "FT-MOD", "신규구현")
add("D206-122", "D2.0-06", "1055-1063", "§4 S7D-022", "V2 Neo4j 마이그레이션 (NetworkX→Neo4j)", "V2", "FT-MIG", "마이그레이션")
add("D206-123", "D2.0-06", "1065-1071", "§4 S7D-023", "GraphRAG 쿼리 파이프라인 (로컬+글로벌+Multi-hop)", "V2", "FT-FUNC", "신규구현")
add("D206-124", "D2.0-06", "1073-1078", "§4 S7D-024", "KG 충돌 감지 + 해소", "V2", "FT-FUNC", "신규구현")
add("D206-125", "D2.0-06", "1080-1085", "§4 S7D-026", "Cognee 통합 (AI KG 자동 구축)", "V2", "FT-MOD", "신규구현")
add("D206-126", "D2.0-06", "1087-1092", "§4 S7D-031", "V2 하이브리드 임베딩 (Dense+Sparse)", "V2", "FT-MOD", "신규구현")
add("D206-127", "D2.0-06", "1094-1099", "§4 S7D-034", "Sparse+Dense 하이브리드 임베딩 (SPLADE)", "V2", "FT-MOD", "신규구현")
add("D206-128", "D2.0-06", "1101-1107", "§4 S7D-060", "Self-RAG 루프 구현", "V2", "FT-FUNC", "신규구현")
add("D206-129", "D2.0-06", "1109-1115", "§4 S7D-061", "CRAG 보정 경로 (Fallback Chain)", "V2", "FT-FUNC", "신규구현")
add("D206-130", "D2.0-06", "1117-1122", "§4 S7D-062", "4중 인덱스 융합 (BM25+Vector+Graph+Summary)", "V2", "FT-FUNC", "신규구현")
add("D206-131", "D2.0-06", "1124-1129", "§4 S7D-013", "벡터 인덱스 최적화 (HNSW 자동 튜닝)", "V2", "FT-FUNC", "보강")
add("D206-132", "D2.0-06", "1131-1136", "§4 S7D-015", "Multi-tenancy 설계", "V2", "FT-INFRA", "신규구현")
add("D206-133", "D2.0-06", "1138-1142", "§4 S7D-017", "벡터 DB 모니터링 대시보드", "V2", "FT-UI", "신규구현")
add("D206-134", "D2.0-06", "1144-1149", "§4 S7D-025", "KG 시간적 관계 (temporal_edge)", "V2", "FT-FUNC", "신규구현")
add("D206-135", "D2.0-06", "1151-1155", "§4 S7D-030", "임베딩 차원 축소 (Matryoshka/PCA)", "V2", "FT-FUNC", "보강")
add("D206-136", "D2.0-06", "1157-1162", "§4 S7D-032", "임베딩 품질 벤치마크 (MTEB 기반)", "V2", "FT-TEST", "테스트")
add("D206-137", "D2.0-06", "1164-1168", "§4 S7D-033", "임베딩 모델 자동 업데이트 (재임베딩 파이프라인)", "V2", "FT-FUNC", "신규구현")
add("D206-138", "D2.0-06", "1170-1175", "§4 S7D-063", "인덱스 자동 업데이트 (4중 인덱스 증분)", "V2", "FT-FUNC", "신규구현")
add("D206-139", "D2.0-06", "1177-1182", "§4 S7D-064", "RAG 품질 자동 평가 (RAGAS, 주간)", "V3", "FT-TEST", "테스트")

# §5 Log Storage
add("D206-140", "D2.0-06", "1243-1249", "§5 로그 저장소", "로그 저장소 분리 원칙 + PII 마스킹", "V1,V2,V3", "FT-CFG", "설정")

# §6 Retention/TTL/Backup
add("D206-141", "D2.0-06", "1255-1267", "§6 TTL/백업", "TTL 기본값 구현 + 버전별 백업 정책", "V1,V2,V3", "FT-CFG", "설정")
add("D206-142", "D2.0-06", "1274-1280", "§6 S7D-016", "벡터 DB 백업/복원", "V1,V2", "FT-FUNC", "신규구현")
add("D206-143", "D2.0-06", "1282-1287", "§6 S7D-077", "압축 전략 (ZSTD, 양자화)", "V1", "FT-FUNC", "신규구현")
add("D206-144", "D2.0-06", "1289-1294", "§6 S7D-072", "백업 자동화 (일간증분/주간전체)", "V1,V2", "FT-FUNC", "신규구현")
add("D206-145", "D2.0-06", "1296-1300", "§6 S7D-074", "데이터 사용량 모니터링", "V1,V2", "FT-FUNC", "신규구현")
add("D206-146", "D2.0-06", "1302-1305", "§6 S7D-081", "불필요 데이터 자동 정리", "V1", "FT-FUNC", "신규구현")

# §7 Schema
add("D206-147", "D2.0-06", "1318-1320", "§7.2 MemoryRecord", "MemoryRecord 스키마 구현 (설계 레벨)", "V1,V2,V3", "FT-SCHEMA", "신규구현")
add("D206-148", "D2.0-06", "1322-1333", "§7.3 SourceQoD", "SourceQoD 스키마 구현 (QoD 가중치 공식 포함)", "V1,V2,V3", "FT-SCHEMA", "신규구현", notes="DEC-010/014 확정")
add("D206-149", "D2.0-06", "1339-1355", "§7 S7D-043", "MemoryEntry 스키마 설계 (상세)", "V1,V2,V3", "FT-SCHEMA", "신규구현")

# §8 Registry
add("D206-150", "D2.0-06", "1359-1417", "§8 레지스트리", "저장 관련 event_type/failure_code/fallback 레지스트리 연동", "V1,V2,V3", "FT-CFG", "설정")

# §10 Extended Features
add("D206-151", "D2.0-06", "1506-1512", "§10.1 Memory Analytics", "Memory Usage Analytics (계층별 저장량, 검색빈도)", "V2", "FT-FUNC", "신규구현")
add("D206-152", "D2.0-06", "1516-1529", "§10.2 임베딩 최적화", "Batch Embedding + File Search + 동적 차원 선택", "V1,V2", "FT-FUNC", "보강")
add("D206-153", "D2.0-06", "1531-1547", "§10.3 벡터 인덱싱", "인덱스 구조 + 데이터 품질 필터 + 재구성 트리거", "V1,V2", "FT-FUNC", "보강")
add("D206-154", "D2.0-06", "1549-1565", "§10.4 Memory 접근 패턴", "4계층 접근 패턴 + Router 쿼리 라우팅", "V1,V2", "FT-FUNC", "신규구현")
add("D206-155", "D2.0-06", "1567-1580", "§10.5 RAG API", "RAG 통합 API (retrieve/index/delete/status)", "V2,V3", "FT-API", "신규구현")
add("D206-156", "D2.0-06", "1582-1621", "§10.6 EmbeddingConfig", "EmbeddingConfig 스키마 + Memory.type 4종 + rag_framework 3단계", "V1,V2,V3", "FT-SCHEMA", "신규구현")
add("D206-157", "D2.0-06", "1625-1651", "§10.7 고급 RAG", "Self-RAG + GraphRAG 고급 + DSPy/Reflexion + 멀티모달 RAG", "V2,V3", "FT-FUNC", "신규구현")
add("D206-158", "D2.0-06", "1652-1666", "§10.8 엔터프라이즈", "멀티테넌시 + SOC-2/GDPR + HA", "V3", "FT-INFRA", "인프라")

# §10 STEP7 items
add("D206-159", "D2.0-06", "1672-1678", "§10 S7D-080", "저장소 추상화 레이어 (StorageAdapter)", "V1,V2,V3", "FT-MOD", "신규구현")
add("D206-160", "D2.0-06", "1680-1685", "§10 S7D-047", "Prompt Cache 구현 (시스템 프롬프트 90% 절감)", "V1", "FT-FUNC", "신규구현")
add("D206-161", "D2.0-06", "1687-1691", "§10 S7D-049", "KV Cache 전략 (vLLM PagedAttention)", "V3", "FT-FUNC", "신규구현")
add("D206-162", "D2.0-06", "1693-1700", "§10 S7D-052", "캐시 적중률 모니터링", "V3", "FT-UI", "신규구현")
add("D206-163", "D2.0-06", "1702-1706", "§10 S7D-067", "로컬↔클라우드 동기화", "V2", "FT-FUNC", "신규구현")
add("D206-164", "D2.0-06", "1708-1712", "§10 S7D-073", "멀티디바이스 메모리 동기화 (E2EE)", "V3", "FT-FUNC", "신규구현")
add("D206-165", "D2.0-06", "1714-1718", "§10 S7D-075", "V1 저장소 비용 = 0원 확인", "V1", "FT-CFG", "설정")
add("D206-166", "D2.0-06", "1720-1723", "§10 S7D-076", "V2 저장소 비용 예산 (~$40/월)", "V2", "FT-CFG", "설정")
add("D206-167", "D2.0-06", "1726-1731", "§10 S7D-078", "V1→V2 마이그레이션 스크립트", "V2", "FT-MIG", "마이그레이션")
add("D206-168", "D2.0-06", "1733-1737", "§10 S7D-079", "V2→V3 마이그레이션 (분산 클러스터)", "V3", "FT-MIG", "마이그레이션")
add("D206-169", "D2.0-06", "1739-1745", "§10 S7D-082", "저장소 건강도 대시보드", "V3", "FT-UI", "신규구현")

# Ideas PART 6
add("D206-170", "D2.0-06", "1758-1760", "아이디어 IDEA-H04", "GraphRAG (Neo4j+Chroma 이중 구조)", "V2", "FT-FUNC", "신규구현", conf="추론")
add("D206-171", "D2.0-06", "1762-1764", "아이디어 IDEA-C08", "256K Long Context 활용 (stuff all)", "V2", "FT-FUNC", "신규구현", conf="추론")
add("D206-172", "D2.0-06", "1766-1768", "아이디어 IDEA-H08", "Agentic RAG (retrieve→evaluate→refine)", "V2", "FT-FUNC", "신규구현", conf="추론")
add("D206-173", "D2.0-06", "1769-1771", "아이디어 IDEA-C09", "3D ViT 비디오 압축 RAG", "V3", "FT-FUNC", "신규구현", conf="추론")
add("D206-174", "D2.0-06", "1772-1774", "아이디어 IDEA-M07", "멀티모달 RAG (ColPali/ColQwen)", "V3", "FT-FUNC", "신규구현", conf="추론")
add("D206-175", "D2.0-06", "1776-1778", "아이디어 IDEA-M10", "실시간 지식 업데이트 (RSS/WebSocket)", "V2", "FT-FUNC", "신규구현", conf="추론")

# Ideas PART 6 Knowledge
add("D206-176", "D2.0-06", "1783-1788", "아이디어 P6-KNW-01", "실시간 웹 검색 + 출처 인용", "V2", "FT-FUNC", "신규구현")
add("D206-177", "D2.0-06", "1790-1796", "아이디어 P6-KNW-02", "멀티소스 교차 검증", "V2", "FT-FUNC", "신규구현")
add("D206-178", "D2.0-06", "1797-1802", "아이디어 P6-KNW-03", "파일 업로드 즉시 분석", "V1,V2", "FT-FUNC", "신규구현")
add("D206-179", "D2.0-06", "1804-1809", "아이디어 P6-KNW-04", "지식 신선도 관리", "V2", "FT-FUNC", "신규구현")
add("D206-180", "D2.0-06", "1811-1816", "아이디어 P6-KNW-05", "지식 충돌 자동 감지", "V2", "FT-FUNC", "신규구현")
add("D206-181", "D2.0-06", "1818-1822", "아이디어 P6-INV-02", "대안 데이터 소스 관리", "V2", "FT-DOMAIN", "신규구현")
add("D206-182", "D2.0-06", "1824-1829", "아이디어 P6-MUL-03", "초대형 문서 처리 (1M+ 컨텍스트)", "V3", "FT-FUNC", "신규구현")
add("D206-183", "D2.0-06", "1831-1836", "아이디어 P6-DAT-05", "데이터 카탈로그", "V2", "FT-FUNC", "신규구현")
add("D206-184", "D2.0-06", "1838-1843", "아이디어 P6-DAT-07", "데이터 버전 관리 (DVC 패턴)", "V2", "FT-FUNC", "신규구현")

# PART 7 HOW
add("D206-185", "D2.0-06", "1849-1858", "아이디어 P7-MEM", "메모리 시스템 상세 설계 (4건 통합)", "V1,V2,V3", "FT-FUNC", "신규구현")
add("D206-186", "D2.0-06", "1860-1865", "아이디어 P7-NSP", "프로젝트별 메모리 격리 (Namespace)", "V1", "FT-SEC", "신규구현")

# §11 PKM/Knowledge (M items - selecting key ones)
for i, (mid, name, ver, cat) in enumerate([
    ("M-001", "자동 지식 캡처", "V1", "FT-FUNC"),
    ("M-003", "문서 인제스트 + Obsidian 양방향 통합", "V1,V2", "FT-FUNC"),
    ("M-007", "자동 태깅/분류 (LLM 기반)", "V1", "FT-FUNC"),
    ("M-009", "시맨틱 노트 검색 (하이브리드)", "V1", "FT-FUNC"),
    ("M-011", "노트 연결 자동 발견", "V1", "FT-FUNC"),
    ("M-013", "지식 요약/통합", "V1", "FT-FUNC"),
    ("M-015", "일일/주간 지식 리뷰", "V1", "FT-FUNC"),
    ("M-017", "웹 클리핑 + 북마크", "V1", "FT-FUNC"),
    ("M-019", "프로젝트 지식 공간", "V1", "FT-FUNC"),
    ("M-023", "문서 템플릿 (회의록/리서치 등)", "V1", "FT-FUNC"),
    ("M-025", "지식 내보내기/백업", "V1,V2", "FT-FUNC"),
    ("M-027", "연구 노트 관리 (논문/인용)", "V1", "FT-FUNC"),
    ("M-029", "코드 스니펫 라이브러리", "V1", "FT-FUNC"),
    ("M-031", "아이디어 캡처 (성숙도 추적)", "V1", "FT-FUNC"),
    ("M-033", "학습 경로 연동", "V1", "FT-FUNC"),
    ("M-035", "투자 리서치 노트", "V1", "FT-DOMAIN"),
    ("M-037", "컨텍스트 노트 제안", "V1,V2", "FT-FUNC"),
    ("M-039", "다국어 노트 (한/영 혼합)", "V1", "FT-FUNC"),
    ("M-041", "지식 갭 분석 (KG 기반)", "V2", "FT-FUNC"),
    ("M-043", "지식 진화 추적 (타임라인)", "V1", "FT-FUNC"),
    ("M-012", "지식그래프 자동 구축 (V2 Neo4j)", "V2", "FT-FUNC"),
    ("M-014", "Zettelkasten 방법론 심화", "V2", "FT-FUNC"),
    ("M-020", "지식 임포트/익스포트 확장 (Notion/Obsidian)", "V2", "FT-FUNC"),
    ("M-028", "지식 공유 및 협업", "V2,V3", "FT-FUNC"),
    ("M-032", "그래프 추론 (경로/패턴)", "V2", "FT-FUNC"),
    ("M-034", "그래프 시각화 인터랙션 (Cytoscape.js)", "V2", "FT-UI"),
    ("M-036", "그래프 자동 정리 (중복 병합)", "V2", "FT-FUNC"),
    ("M-038", "그래프 기반 추천", "V2", "FT-FUNC"),
    ("M-042", "지식의 Dream Mode 처리", "V2", "FT-FUNC"),
    ("M-048", "지식관리 벤치마크 (VBS-14)", "V2", "FT-TEST"),
    ("M-045", "지식 기반 의사결정 지원 (SWOT)", "V1", "FT-FUNC"),
    ("M-046", "지식 기반 글쓰기 지원", "V1", "FT-FUNC"),
    ("M-047", "2차 뇌 (Second Brain) 대시보드", "V1,V2", "FT-UI"),
    ("M-044", "지식 기반 개인 어시스턴트 (V3 심화)", "V1,V3", "FT-FUNC"),
], start=187):
    add(f"D206-{i:03d}", "D2.0-06", f"§11 {mid}", f"§11 PKM {mid}", f"{mid} {name}", ver, cat, "신규구현")

# §11 R5 상세 구현 — M PKM/지식관리 V2 MED/LOW (12건)
r5_start = 221
for i, (mid, name, ver, cat) in enumerate([
    ("M-002", "웹 클리핑 + AI 요약 (YouTube/PDF 특화 파서)", "V2", "FT-FUNC"),
    ("M-004", "스크린 캡처 지식화 (Microsoft Recall 로컬 버전)", "V2", "FT-FUNC"),
    ("M-006", "이메일/메시지 지식 추출 (Gmail/Outlook/Slack)", "V2", "FT-FUNC"),
    ("M-008", "투자 지식 자동 축적 (분석결과+매매근거 기록)", "V2", "FT-DOMAIN"),
    ("M-010", "RSS/뉴스피드 지식화 (자동수집+일일다이제스트)", "V2", "FT-FUNC"),
    ("M-016", "시간 기반 지식 관리 (타임라인뷰+주월간리뷰)", "V2", "FT-FUNC"),
    ("M-018", "멀티 계층 카테고리 (MECE 4계층+AI 자동분류)", "V2", "FT-FUNC"),
    ("M-022", "컨텍스트 인식 지식 추천 (프로액티브 관련지식 표면)", "V2", "FT-FUNC"),
    ("M-024", "질의응답 QA over Knowledge (멀티홉+시간인식)", "V2", "FT-FUNC"),
    ("M-026", "지식 연결 탐색 (갭분석+지식지도 시각화)", "V2", "FT-FUNC"),
    ("M-030", "지식 통계/분석 (대시보드+연결밀도+활용률)", "V2", "FT-FUNC"),
    ("M-043", "예측적 지식 서핑 (행동예측→관련지식 미리 로드)", "V2", "FT-FUNC"),
], start=0):
    add(f"D206-{r5_start+i:03d}", "D2.0-06", f"2085-2147", f"§11 R5 {mid}", f"{mid} {name}", ver, cat, "신규구현")

# §11 R6 상세 구현 — M PKM/지식관리 V3 (10건, 단 M-045~047은 기추출 → 5건만 추가)
r6_start = r5_start + 12
for i, (mid, name, ver, cat) in enumerate([
    ("M-037", "개인 위키 V3 (지식그래프 기반 위키+정적사이트 발행)", "V3", "FT-FUNC"),
    ("M-039", "Notion AI 대비 VAMOS 완전 차별화 (대화형+KG+L0~L3+로컬)", "V3", "FT-FUNC"),
    ("M-040", "Obsidian+AI 대비 VAMOS 차별화 (네이티브AI+에이전트+vault호환)", "V3", "FT-FUNC"),
    ("M-044", "지식 기반 개인 어시스턴트 V3 심화 (축적형 AI 차별화)", "V3", "FT-FUNC"),
    ("M-049~054", "PKM 참고자료+로드맵 (V1즉시/V2 3개월/V3 6개월+ 구현계획)", "V1,V2,V3", "FT-CFG"),
], start=0):
    add(f"D206-{r6_start+i:03d}", "D2.0-06", f"2149-2196", f"§11 R6 {mid}", f"{mid} {name}", ver, cat, "신규구현")

# ============================================================
# D2.0-07 SAFETY/COST/APPROVAL FEATURES
# ============================================================
n = 1

def d207(line, section, name, ver, cat, impl, deps=None, extractable=True, conf="명시적", notes=""):
    global n
    add(f"D207-{n:03d}", "D2.0-07", line, section, name, ver, cat, impl, deps, extractable, conf, notes)
    n += 1

# §1 Non-goal
d207("73-81", "§1 Non-goal", "Non-goal 절대 금지 7항목 정책 구현 (실거래/해킹/의료법률/PII/저작권/P2자동/위험자동)", "V1,V2,V3", "FT-CFG", "설정", notes="LOCK. RULE 1.3 §2")

# §1.1 3-Layer Guardrails
d207("86-91", "§1.1 3층 Guardrails", "Layer 1 입력 방어: NeMo Guardrails 구현", "V1", "FT-SEC", "신규구현", notes="ADD-013")
d207("88", "§1.1 3층 Guardrails", "Layer 2 처리 방어: Guardrails AI 구현", "V1", "FT-SEC", "신규구현", notes="ADD-013")
d207("89", "§1.1 3층 Guardrails", "Layer 3 출력 방어: LlamaGuard 구현", "V1", "FT-SEC", "신규구현", notes="ADD-015")

# §2 Risk Classification
d207("93-100", "§2.1 도메인 등급", "P0/P1/P2 도메인 등급 분류 구현 (P2 승인/세션 재확인/5분 타임아웃)", "V1,V2,V3", "FT-CFG", "설정")
d207("102-108", "§2.2 외부 API 위험", "외부 API 사용 전 체크리스트 구현", "V1,V2,V3", "FT-SEC", "설정")

# §2.2A Threat Modeling S7E-001~010
d207("126-136", "§2.2A S7E-001", "STRIDE 기반 위협 모델링 (6대 공격표면)", "V1", "FT-SEC", "신규구현")
d207("138-158", "§2.2A S7E-002", "AI 특화 공격 트리 작성", "V1", "FT-SEC", "신규구현")
d207("160-172", "§2.2A S7E-003", "OWASP Top 10 for LLM 전 항목 대응 매핑", "V1", "FT-SEC", "신규구현")
d207("174-179", "§2.2A S7E-004", "Supply Chain 보안 (npm audit/pip-audit/SBOM)", "V1,V2", "FT-SEC", "신규구현")
d207("181-186", "§2.2A S7E-005", "API Key 관리 (저장/순환/폐기/gitleaks)", "V1,V2", "FT-SEC", "신규구현")
d207("188-196", "§2.2A S7E-006", "Input Validation (모든 입력 검증)", "V1,V2", "FT-SEC", "신규구현")
d207("198-203", "§2.2A S7E-007", "Output Sanitization (LLM 출력 안전성)", "V1", "FT-SEC", "신규구현")
d207("205-211", "§2.2A S7E-008", "Rate Limiting / Cost Protection", "V1,V2", "FT-SEC", "신규구현")
d207("213-217", "§2.2A S7E-009", "Penetration Testing 계획", "V2", "FT-TEST", "테스트")
d207("219-221", "§2.2A S7E-010", "Security Champions 프로그램", "V2", "FT-CFG", "설정")

# §2.3 Prompt Injection
d207("225-231", "§2.3 Prompt Injection", "프롬프트 주입 방어 시스템 (직접/간접)", "V1", "FT-SEC", "신규구현", notes="ADD-014")
d207("239-241", "§2.3.1 입력 검증", "PolicyCheck Gate 전 스키마 유효성 검사", "V1", "FT-SEC", "신규구현")
d207("243-246", "§2.3.2 민감 데이터", "민감 데이터 처리 규칙 (마스킹+SENSITIVE_DATA_FLAG)", "V1", "FT-SEC", "신규구현")
d207("256-269", "§2.3 커뮤니티 스킬", "커뮤니티 스킬 보안 검증 체계 (4단계)", "V1,V2,V3", "FT-SEC", "신규구현")

# §2.4 Prompt Injection Deep S7E-011~020
d207("286-299", "§2.4 S7E-011", "Instruction Hierarchy (5레벨 프롬프트 우선순위)", "V1", "FT-SEC", "신규구현")
d207("301-313", "§2.4 S7E-012", "Input/Output Tagging (신뢰 경계 마킹)", "V1", "FT-SEC", "신규구현")
d207("315-326", "§2.4 S7E-013", "Canary Token / Tripwire (프롬프트 추출 감지)", "V1", "FT-SEC", "신규구현")
d207("328-334", "§2.4 S7E-014", "Indirect Injection 방어 (외부 콘텐츠 격리)", "V1,V2", "FT-SEC", "신규구현")
d207("336-348", "§2.4 S7E-015", "Tool Call 검증 (MCP Poisoning 방어)", "V1,V2", "FT-SEC", "신규구현")
d207("351-361", "§2.4 S7E-016", "Multi-layer Defense 아키텍처 (6레이어)", "V1", "FT-SEC", "신규구현")
d207("363-369", "§2.4 S7E-017", "Jailbreak 방어 (패턴 DB + CAI)", "V1,V2", "FT-SEC", "신규구현")
d207("371-377", "§2.4 S7E-018", "Prompt Injection 탐지 모델 (규칙→ML)", "V1,V2,V3", "FT-SEC", "신규구현")
d207("379-384", "§2.4 S7E-019", "Agent Sandboxing (프로세스→컨테이너→마이크로VM)", "V1,V2,V3", "FT-SEC", "신규구현")
d207("386-392", "§2.4 S7E-020", "Red Team 자동화 (garak/PyRIT)", "V2", "FT-TEST", "테스트")

# §3 Approval
d207("397-410", "§3.1 승인 필수", "2단계 승인 구조 (계획+실행) 구현", "V1,V2,V3", "FT-FUNC", "신규구현")
d207("416-430", "§3.2.1 자율 운영 수준", "자율 운영 수준 4단계 (L0 FULL_MANUAL~L3 FULL_AUTO)", "V1,V2,V3", "FT-CFG", "설정", notes="LOCK. 기본값 L1")
d207("432-451", "§3.3 S/E-Module 승인", "S-Module/E-Module 승인 규칙 표 (allow/restrict/deny)", "V1,V2,V3", "FT-CFG", "설정", notes="LOCK")
d207("456-467", "§3.4 Self-evo 롤백", "자기진화 롤백 메커니즘 (스냅샷+트리거+복원)", "V1,V2", "FT-FUNC", "신규구현", notes="ADD-074")
d207("469-477", "§3.4 S7E-071", "보안 인시던트 시 상태 롤백 (자동/수동)", "V2", "FT-FUNC", "신규구현")
d207("480-484", "§3.5.1 RLHF/DPO", "RLHF/DPO 피드백 파이프라인", "V1,V2", "FT-FUNC", "신규구현", notes="ADD-042")
d207("486-493", "§3.5.2 Constitutional AI", "Constitutional AI 원칙 시스템 (4원칙+Critique 루프)", "V1,V2", "FT-FUNC", "신규구현", notes="ADD-043")

# §3.6 RBAC
d207("497-518", "§3.6 RBAC", "RBAC 4역할 구현 (OWNER/ADMIN/OPERATOR/VIEWER + AGENT 시스템주체)", "V1,V2", "FT-SEC", "신규구현", notes="LOCK. MOD-023")

# §3.7 Auth S7E-021~030
d207("552-557", "§3.7 S7E-021", "로컬 인증 (PIN/생체인증/세션타임아웃)", "V1", "FT-SEC", "신규구현")
d207("559-564", "§3.7 S7E-022", "OAuth2 + MFA (TOTP/WebAuthn)", "V2", "FT-SEC", "신규구현")
d207("566-577", "§3.7 S7E-023", "RBAC 상세 접근제어 매트릭스", "V1", "FT-SEC", "신규구현")
d207("578-583", "§3.7 S7E-024", "API Key Scoping (최소 권한)", "V2", "FT-SEC", "신규구현")
d207("585-593", "§3.7 S7E-025", "Tool 실행 권한 (AUTO/CONFIRM/RESTRICTED/BLOCKED)", "V1", "FT-SEC", "신규구현")
d207("595-601", "§3.7 S7E-026", "Session 관리 (세션 라이프사이클)", "V1", "FT-SEC", "신규구현")
d207("603-608", "§3.7 S7E-027", "Zero-Trust Architecture", "V2", "FT-SEC", "신규구현")
d207("610-615", "§3.7 S7E-028", "감사 추적 (Audit Trail)", "V2", "FT-SEC", "신규구현")
d207("617-621", "§3.7 S7E-029", "Data Access Layer (데이터 접근 권한 세분화)", "V2", "FT-SEC", "신규구현")
d207("623-626", "§3.7 S7E-030", "SSO 통합 (SAML/OIDC/Keycloak)", "V3", "FT-SEC", "신규구현")

# §4 Cost
d207("632-639", "§4.1 비용 상한", "비용 상한 구현 (V1:40K/V2:93K/V3:266K KRW 월)", "V1,V2,V3", "FT-CFG", "설정", notes="LOCK")
d207("661-674", "§4.2 다운시프트", "다운시프트 정책 (80% 경고 force_mini / 100% 차단 deny)", "V1,V2,V3", "FT-FUNC", "신규구현", notes="LOCK")
d207("677-691", "§4.2.1 비용 절감", "비용 절감 전략 3가지 (캐싱/경량모델/불필요호출제거)", "V1,V2,V3", "FT-FUNC", "신규구현", notes="ADD-010")
d207("693-703", "§4.3 월 예산 초과", "월 예산 초과 처리 (차단→알림→예산상향승인)", "V1,V2,V3", "FT-FUNC", "신규구현")
d207("736-749", "§4.3.2 COST_APPROVAL", "COST_APPROVAL 워크플로우 (4 트리거, 10/5분 타임아웃)", "V1,V2,V3", "FT-FUNC", "신규구현", notes="ADD-060")
d207("757-768", "§4.5 Logging Stack", "버전별 Logging Stack (V1:JSONL/V2:Postgres/V3:Loki)", "V1,V2,V3", "FT-INFRA", "인프라", notes="LOCK")

# §5 PolicyCheck
d207("927-943", "§5 PolicyCheck", "PolicyCheck 게이트 구현 (4호출위치 + 5검사항목)", "V1,V2,V3", "FT-FUNC", "신규구현")
d207("945-963", "§5.2.1 SelfCheckGate", "SelfCheckGate 구현 (P0≥70/P1≥75/P2≥80)", "V1,V2,V3", "FT-FUNC", "신규구현", notes="LOCK. 5-Gate 5th gate")

# §5.3 Data Privacy S7E-031~040
d207("978-993", "§5.3 S7E-031", "PII 탐지 및 마스킹 (8패턴 정규식→Presidio)", "V1,V2", "FT-SEC", "신규구현")
d207("995-1000", "§5.3 S7E-032", "로컬 데이터 암호화 (SQLCipher AES-256)", "V1", "FT-SEC", "신규구현")
d207("1002-1008", "§5.3 S7E-033", "데이터 주권 (100% 사용자 소유, vamos purge)", "V1", "FT-SEC", "신규구현")
d207("1010-1015", "§5.3 S7E-034", "데이터 최소화 (LLM 전송 최소화)", "V1", "FT-SEC", "설정")
d207("1017-1024", "§5.3 S7E-035", "Opt-in/Opt-out (학습 데이터 사용 거부)", "V1", "FT-SEC", "설정")
d207("1026-1031", "§5.3 S7E-036", "E2E 암호화 (Signal/Noise Protocol)", "V2", "FT-SEC", "신규구현")
d207("1033-1040", "§5.3 S7E-037", "GDPR / 개인정보보호법 준수", "V2", "FT-SEC", "신규구현")
d207("1042-1052", "§5.3 S7E-038", "데이터 보존 정책 (유형별 보존기간)", "V2", "FT-CFG", "설정")
d207("1054-1058", "§5.3 S7E-039", "익명화/가명화 (k-익명성/DP)", "V2", "FT-SEC", "신규구현")
d207("1060-1066", "§5.3 S7E-040", "프라이버시 대시보드 (데이터 투명성 UI)", "V2", "FT-UI", "신규구현")
d207("1068-1074", "§5.3 S7E-068", "Crypto-shredding 기반 완전 삭제", "V2", "FT-SEC", "신규구현")

# §6 Schema
d207("1078-1106", "§6 스키마", "PolicyCheck/Approval/CostBudget/Downshift/Block 스키마 구현", "V1,V2,V3", "FT-SCHEMA", "신규구현", notes="SOT=D7")

# §10 Guardrails Deep
d207("1736-1750", "§15.8 4-Layer Guardrails", "Layer 4 사후 감사 (Post-delivery Audit) 구현", "V2", "FT-SEC", "신규구현")

# §12 Cost Dashboard
d207("1613-1658", "§15.6 비용 관리", "실시간 비용 모니터링 + 예산 알림 + 분석 대시보드 + 예측 엔진", "V1,V2,V3", "FT-FUNC", "신규구현", notes="S05-B17")

# §13 RBAC extension already covered

# §14 Autonomy already covered

# §15 Extended Features
d207("1224-1263", "§15.1 TCO", "TCO 프레임워크 (비용분석+GPU비교+숨겨진비용)", "V1,V2,V3", "FT-FUNC", "신규구현")
d207("1267-1310", "§15.2 ASL", "ASL 안전성 계층 (ASL-1~4→VAMOS 매핑+필터파이프라인+테스트)", "V1,V2", "FT-SEC", "신규구현")
d207("1314-1382", "§15.3 AI 윤리", "AI 윤리/Safety/Alignment/거버넌스 프레임워크", "V1,V2", "FT-CFG", "설정")
d207("1386-1392", "§15.3 S7E-046", "Harm Assessment 자동화 (위해성 점수 0~1)", "V2", "FT-SEC", "신규구현")
d207("1394-1400", "§15.3 S7E-052", "투명성 의무 이행 (EU AI Act 보고서)", "V2", "FT-FUNC", "신규구현")
d207("1402-1407", "§15.3 S7E-048", "Ethical Guardrails 실시간 감시", "V2", "FT-SEC", "신규구현")
d207("1409-1414", "§15.3 S7E-059", "AI 영향평가 (의사결정 영향 분석)", "V2", "FT-FUNC", "신규구현")
d207("1418-1470", "§15.4 컴플라이언스", "SOC-2/GDPR 대응 + 감사 로그 무결성 + 자동 검증", "V1,V2", "FT-SEC", "신규구현")
d207("1474-1479", "§15.4 E-ADD-03", "EU AI Act 최신 반영", "V1", "FT-CFG", "설정")
d207("1481-1487", "§15.4 S7E-054", "NIST AI RMF 매핑", "V2", "FT-CFG", "설정")
d207("1489-1494", "§15.4 S7E-055", "ISO 42001 준비", "V2,V3", "FT-CFG", "설정")
d207("1496-1501", "§15.4 S7E-058", "컴플라이언스 자동 체크 (주간)", "V2", "FT-TEST", "테스트")
d207("1503-1508", "§15.4 S7E-067", "감사 보고서 자동 생성 (월간)", "V2", "FT-FUNC", "신규구현")
d207("1510-1516", "§15.4 S7E-060", "국가별 규제 적응", "V3", "FT-CFG", "설정")

# §15.5 Red Team
d207("1520-1570", "§15.5 Red Team", "Red Team 테스트 + Bias 탐지 파이프라인 + AI 워터마킹", "V2,V3", "FT-TEST", "테스트")
d207("1585-1591", "§15.5 S7E-065", "이상 탐지 (비정상 사용 패턴)", "V2", "FT-SEC", "신규구현")
d207("1593-1598", "§15.5 S7E-088", "보안 등급 점수 자동 산출 (0~100)", "V2", "FT-FUNC", "신규구현")
d207("1600-1605", "§15.5 S7E-084", "Multi-Agent 보안 테스트", "V3", "FT-TEST", "테스트")

# §15.7 Graceful Degradation
d207("1662-1692", "§15.7 Graceful Degradation", "안전 필터 에러 복구 + Graceful Degradation 4단계 + Safe Defaults", "V1,V2", "FT-FUNC", "신규구현")
d207("1695-1700", "§15.7 S7E-073", "긴급 연락 체계", "V1", "FT-FUNC", "신규구현")
d207("1702-1707", "§15.7 S7E-074", "안전 모드 (최소 기능 동작)", "V1", "FT-FUNC", "신규구현")
d207("1709-1714", "§15.7 S7E-066", "보안 알림 시스템 (INFO/WARN/CRITICAL)", "V2", "FT-FUNC", "신규구현")
d207("1716-1721", "§15.7 S7E-072", "Root Cause Analysis (인시던트 근본원인)", "V2", "FT-FUNC", "신규구현")
d207("1723-1728", "§15.7 S7E-075", "인시던트 대응 훈련 (분기 1회)", "V2", "FT-TEST", "테스트")

# §15.8 4-Layer Guardrails / C2PA
d207("1769-1781", "§15.8 C2PA", "C2PA 콘텐츠 인증 (디지털 서명)", "V3", "FT-SEC", "신규구현")

# §15.9 NLI Hallucination
d207("1791-1841", "§15.9 NLI Hallucination", "NLI 기반 환각 탐지 시스템 (사실추출→NLI→판정→임계값)", "V1,V2", "FT-SEC", "신규구현", notes="CRITICAL")

# §15.10 PolicyCheck Self-check
d207("1844-1868", "§15.10 PolicyCheck Self-check", "PolicyCheck Self-check 모듈 (일관성검증+정책드리프트감지)", "V1,V2", "FT-FUNC", "신규구현")

# §15.11 RSP
d207("1872-1903", "§15.11 RSP/Catastrophic Risk", "RSP 프레임워크 + Catastrophic Risk 4분류 + 안전 벤치마크", "V1,V2", "FT-SEC", "신규구현")
d207("1907-1913", "§15.11 S7E-049", "Safety Benchmark 정기 실행 (500건 세트)", "V2", "FT-TEST", "테스트")
d207("1915-1929", "§15.11 S7E-050", "Human-in-the-Loop (고위험 결정 사람 확인)", "V2", "FT-FUNC", "신규구현")

# §15.12 Control Inversion
d207("1933-1974", "§15.12 Control Inversion", "Control Inversion 방지 (패턴탐지+AGENT자율권한계+킬스위치)", "V1,V2", "FT-SEC", "신규구현")
d207("1967-1974", "§15.12 S7E-082", "Agent 행동 모니터링 (실시간 감시+제한)", "V2", "FT-SEC", "신규구현")

# §15.13 Risk/Regulatory
d207("1978-2004", "§15.13 리스크 관리", "AI 리스크 레지스터 + Regulatory Change Alert 시스템", "V1,V2,V3", "FT-FUNC", "신규구현")

# §15.14 Self-evo Safety
d207("2007-2060", "§15.14 Self-evo 안전장치", "Self-evo 안전 게이트 + Conflict Resolution + 임계값 관리", "V1,V2,V3", "FT-SEC", "신규구현")

# §15.15 Ideas
d207("2068-2070", "§15.15 IDEA-C06", "병렬 에이전트 보상 함수 (PARL)", "V2", "FT-FUNC", "신규구현", conf="추론")
d207("2072-2074", "§15.15 IDEA-C10", "단순 RL 프레임워크 (Kimi k1.5)", "V2", "FT-FUNC", "신규구현", conf="추론")
d207("2076-2078", "§15.15 IDEA-H09", "투자 특화 Red-teaming (100+ 패턴 DB)", "V2", "FT-TEST", "신규구현", conf="추론")
d207("2080-2082", "§15.15 IDEA-M03", "XAI 설명 가능한 AI (SHAP/LIME)", "V2", "FT-FUNC", "신규구현", conf="추론")
d207("2084-2086", "§15.15 IDEA-M11", "규제 준수 자동 검증 (금융위/SEC)", "V2", "FT-SEC", "신규구현", conf="추론")
d207("2088-2090", "§15.15 IDEA-M12", "감사 추적 강화 (구조화 로그+해시체인)", "V2", "FT-SEC", "신규구현", conf="추론")
d207("2092-2094", "§15.15 IDEA-M16", "예측적 비용 최적화 (Predictive Cost)", "V2", "FT-FUNC", "신규구현", conf="추론")

# §15.16 Health/Wellness
d207("2105-2111", "§15.16 P-009", "감정 지능 개발 도구", "V1", "FT-FUNC", "신규구현")
d207("2113-2117", "§15.16 P-032", "AI 성격 진화 (적응 범위 제한)", "V1", "FT-FUNC", "신규구현")
d207("2139-2144", "§15.16 P-006", "개인 감정 패턴 학습 (예측적 지원)", "V2", "FT-FUNC", "신규구현")
d207("2146-2150", "§15.16 P-031", "Dream Mode 웰니스 분석", "V2", "FT-FUNC", "신규구현")
d207("2154-2159", "§15.16 P-033", "웰니스 커뮤니티 (V3 익명 참여)", "V3", "FT-FUNC", "신규구현")

# §16 Ideas PART 6
d207("2173-2179", "§16.1 P6-SAF-01", "Constitutional AI 벤치마크 (200건+ 테스트)", "V3", "FT-TEST", "테스트")
d207("2181-2186", "§16.2 P6-SAF-02", "프라이버시 보존 학습 (Federated/DP)", "V3", "FT-SEC", "신규구현")
d207("2188-2193", "§16.3 P6-SAF-03", "보안 아키텍처 인증 대비 (SOC2/ISO27001)", "V3", "FT-SEC", "신규구현")
d207("2195-2201", "§16.4 P6-SAF-04", "투자 면책/경고 자동 삽입", "V2", "FT-CFG", "설정")
d207("2202-2207", "§16.5 P6-SAF-05", "편향성 탐지/완화 (Bias Detection Module)", "V2", "FT-SEC", "신규구현")
d207("2209-2214", "§16.6 P6-SAF-06", "할루시네이션 탐지 특화 (Financial)", "V2", "FT-SEC", "신규구현")
d207("2216-2221", "§16.7 P6-INV-05", "VaR 기반 위험 한도 규칙", "V2", "FT-DOMAIN", "신규구현")
d207("2223-2228", "§16.8 P6-DAT-03", "데이터 리니지 감사 (Data Provenance)", "V2", "FT-SEC", "신규구현")
d207("2230-2235", "§16.9 P6-AGT-05", "에이전트 신뢰도 기반 승인 연동", "V2", "FT-FUNC", "신규구현")
d207("2237-2242", "§16.10 P6-INF-02", "모델 배포 안전 규칙 (A/B 테스트+롤백)", "V2", "FT-CFG", "설정")

# §17 Ideas PART 7 HOW
d207("2263-2266", "§17.1 P7-SEC", "탈옥 차단 엔진 (CAI+투자특화 DB)", "V2", "FT-SEC", "신규구현")
d207("2268-2271", "§17.2 P7-EVO", "진화 보호 메커니즘 (10개 NEVER_AUTO 항목: safety_rules/cost_ceiling/approval_flow/non_goals/audit_format/data_retention/user_consent/escalate_own_privilege/disable_guardrails/bypass_gate)", "V1,V2", "FT-SEC", "신규구현", notes="CLAUDE.md §17 NEVER_AUTO 10항목")
d207("2273-2276", "§17.3 P7-QOD", "편향 감사 엔진 (확증/최신/생존/섹터)", "V2", "FT-FUNC", "신규구현")
d207("2278-2281", "§17.4 P7-LOG", "규제 보고서 자동 생성 (월간/분기별)", "V2", "FT-FUNC", "신규구현")
d207("2283-2286", "§17.5 P7-SEC", "이상 행동 탐지 (베이스라인→이상→격리)", "V2", "FT-SEC", "신규구현")
d207("2288-2291", "§17.6 P7-CST", "비용 경고 자동 조치 (80%force_mini/100%차단)", "V1,V2", "FT-FUNC", "신규구현")

# R1/R2 Additional STEP7 items
d207("2384-2387", "R1 S7E-041", "Personal Constitution (사용자 정의 가치관/규칙)", "V1", "FT-FUNC", "신규구현")
d207("2389-2391", "R1 S7E-042", "Confidence & Uncertainty 투명 표시 (0-100%)", "V1", "FT-FUNC", "신규구현")
d207("2393-2396", "R1 S7E-051", "EU AI Act 위험등급 자체 평가", "V1", "FT-CFG", "설정")
d207("2398-2400", "R1 S7E-053", "금융 규제 검토 (면책 자동 삽입)", "V1", "FT-CFG", "설정")
d207("2404-2407", "R1 S7E-061", "보안 이벤트 로깅 (전수 기록)", "V1", "FT-SEC", "신규구현")
d207("2409-2413", "R1 S7E-062", "비용 모니터링 (실시간 API 비용 추적)", "V1", "FT-FUNC", "신규구현")
d207("2417-2418", "R1 S7E-077", "Agent 최소 권한 원칙", "V1", "FT-SEC", "신규구현")
d207("2420-2421", "R1 S7E-078", "Agent 통신 보안 (HMAC 무결성)", "V1", "FT-SEC", "신규구현")
d207("2423-2426", "R1 S7E-079", "Tool 실행 게이트 (5-Gate 통합)", "V1", "FT-SEC", "신규구현")
d207("2428-2429", "R1 S7E-080", "Delegation Attack 방어 (3단계 깊이 제한)", "V1", "FT-SEC", "신규구현")

# R1 Wellness
d207("2433-2435", "R1 P-001", "감정 인식 시스템 (KoBERT 6감정)", "V1", "FT-MOD", "신규구현")
d207("2437-2439", "R1 P-002", "감정 적응형 응답", "V1", "FT-FUNC", "신규구현")
d207("2442-2443", "R1 P-018", "건강 데이터 프라이버시", "V1", "FT-SEC", "신규구현")

# R1 Cross
d207("2447-2449", "R1 S7-F-003", "Constitutional AI 핵심 구현", "V1", "FT-FUNC", "신규구현")
d207("2451-2453", "R1 S7-F-007", "Confidence Score 산출 알고리즘", "V1", "FT-FUNC", "신규구현")
d207("2455-2457", "R1 S7-F-010", "Privacy-First 데이터 파이프라인", "V1", "FT-SEC", "신규구현")
d207("2459-2461", "R1 S7-F-011", "Rollback 메커니즘 (설정/메모리/KG)", "V1", "FT-FUNC", "신규구현")
d207("2463-2464", "R1 S7-N-001", "Tool Poisoning 방어 강화", "V1", "FT-SEC", "신규구현")
d207("2466-2467", "R1 S7-N-002", "Delegation Attack 방어 강화", "V1", "FT-SEC", "신규구현")
d207("2469-2470", "R1 S7-N-003", "최소 권한 원칙 세분화", "V1", "FT-SEC", "신규구현")
d207("2472-2473", "R1 S7-N-004", "Agent 통신 보안 상세", "V1", "FT-SEC", "신규구현")

# R2 Additional items (key ones)
d207("2509", "R2 S7E-043", "Refusal Protocol (위험 요청 거부+대안)", "V1", "FT-FUNC", "신규구현")
d207("2510", "R2 S7E-044", "Hallucination 방지 (사실검증+불확실성명시)", "V1", "FT-FUNC", "신규구현")
d207("2511", "R2 S7E-045", "Bias 감지/완화 (자가테스트+경고)", "V1", "FT-SEC", "신규구현")
d207("2512", "R2 S7E-047", "투명성 보고서 (월간 자동 생성)", "V1", "FT-FUNC", "신규구현")
d207("2513", "R2 S7E-056", "면책 고지 시스템 (투자/의료/법률)", "V1", "FT-CFG", "설정")
d207("2516", "R2 S7E-063", "Agent 활동 추적 (에이전트별 로그)", "V1", "FT-FUNC", "신규구현")
d207("2518", "R2 S7E-069", "인시던트 분류 (P1~P4 4단계+절차)", "V1", "FT-SEC", "신규구현")
d207("2519", "R2 S7E-070", "자동 격리 (보안 이벤트 시 Agent 격리)", "V1", "FT-SEC", "신규구현")
d207("2520", "R2 S7E-081", "데이터 경계 격리 (Agent간)", "V1", "FT-SEC", "신규구현")
d207("2521", "R2 S7E-085", "5-Gate Security 통합", "V1", "FT-SEC", "신규구현")
d207("2522", "R2 S7E-086", "Privacy-by-Design (설계단계 내장)", "V1", "FT-SEC", "설정")
d207("2523", "R2 S7E-089", "DLP 전송 차단 (API 전송 전 PII/키)", "V1", "FT-SEC", "신규구현")

# R2 Cross
d207("2529", "R2 S7-A-013", "에이전트 비용 모델 분리 (Lead→Opus, Sub→Haiku)", "V1", "FT-CFG", "설정")
d207("2530", "R2 S7-D-019", "자율 등급 4단계 Gate 통합", "V1", "FT-FUNC", "신규구현")
d207("2531", "R2 S7-E-010", "비용 시뮬레이션 모드 (dry_run)", "V1", "FT-FUNC", "신규구현")
d207("2532", "R2 S7-F-029", "프라이버시 우선 모드", "V1", "FT-SEC", "설정")
d207("2533", "R2 S7-F-055", "민감도 자동 분류 (4단계)", "V1", "FT-SEC", "신규구현")
d207("2534", "R2 S7-H-008", "Guardrailing API (Mistral 안전 필터)", "V1", "FT-SEC", "신규구현")
d207("2535", "R2 S7-H-010", "Mistral Moderation (유해 콘텐츠 검증)", "V1", "FT-SEC", "신규구현")
d207("2536", "R2 S7-I-005", "Llama Guard 3 (오픈소스 안전 분류기)", "V1", "FT-SEC", "신규구현")

# R2 Wellness
d207("2541", "R2 P-003", "감정 기록/트렌드 (대화별 태깅)", "V1", "FT-FUNC", "신규구현")
d207("2542", "R2 P-004", "스트레스 관리 (호흡/그라운딩/명상)", "V1", "FT-FUNC", "신규구현")
d207("2543", "R2 P-007", "공감 대화 엔진 (Carl Rogers)", "V1", "FT-MOD", "신규구현")
d207("2544", "R2 P-016", "의료 정보 관리 (복약+검진, AES-256)", "V1", "FT-SEC", "신규구현")
d207("2545", "R2 P-020", "CBT 셀프케어 (사고기록+인지왜곡)", "V1", "FT-FUNC", "신규구현")
d207("2546", "R2 P-023", "번아웃 예방 (과도업무감지→중단)", "V1", "FT-FUNC", "신규구현")
d207("2547", "R2 P-028", "웰니스-투자 연동 (수면부족→결정연기)", "V1", "FT-DOMAIN", "신규구현")

# R2 D+J+보강
d207("2557", "R2 J-017", "이미지 안전성 필터 (NSFW+워터마크)", "V1", "FT-SEC", "신규구현")
d207("2558", "R2 J-067", "프라이버시 멀티모달 (로컬우선)", "V1", "FT-SEC", "설정")
d207("2559", "R2 S7-O-009", "Guardrails 프레임워크 (NeMo 선언적 규칙)", "V1", "FT-SEC", "신규구현")
d207("2560", "R2 E-ADD-01", "A2A 보안 프로토콜 (에이전트간 인증/암호화)", "V1", "FT-SEC", "신규구현")

# ── 누락분 보완 (Phase 0-C 검증 결과) ──

# §2.3.3 인증/인가 검사
d207("248-250", "§2.3.3 인증/인가 검사", "PolicyCheck Gate에서 세션 유효성+RBAC 권한 검증 (Tool/외부API 호출 시)", "V1,V2,V3", "FT-SEC", "신규구현")

# §2.3.4 외부 통신 보안
d207("252-254", "§2.3.4 외부 통신 보안", "외부 API HTTPS(TLS 1.2+) 강제 + 응답 스키마 대조 검증", "V1,V2,V3", "FT-SEC", "신규구현")

# §4.3.2 멀티 에이전트 비용 경고
d207("751-755", "§4.3.2 멀티 에이전트 비용 경고", "멀티에이전트 비용 15x 모니터링 + 싱글 대비 3배 초과 시 자동 경고", "V1,V2,V3", "FT-FUNC", "신규구현", notes="REF:영상1")

# §4.7 P1 Stack Combos (V1/V2/V3)
d207("789-833", "§4.7.1 COMBO-V1-LOCAL", "V1 로컬 스택 조합 (Ollama+Chroma+SQLite+JSONL, 월비용≈0)", "V1", "FT-INFRA", "인프라", notes="LOCK")
d207("835-879", "§4.7.1 COMBO-V2-SERVER", "V2 서버 스택 조합 (GPT-4o mini+Qdrant+Postgres+Docker, 월≈65K~95K KRW)", "V2", "FT-INFRA", "인프라", notes="LOCK")
d207("882-923", "§4.7.1 COMBO-V3-OPS", "V3 운영형 스택 조합 (vLLM+K8s+매니지드DB+Loki/ELK, 월≈725K~1.3M KRW)", "V3", "FT-INFRA", "인프라", notes="LOCK")

# §7 레지스트리
d207("1110-1149", "§7 레지스트리", "Safety/Cost 레지스트리 네이밍 규칙 (event_type:lower.dot/failure_code:UPPER_SNAKE/fallback_id:FB_UPPER_SNAKE)", "V1,V2,V3", "FT-CFG", "설정", notes="정본=02 §6.2/6.3")

# §8 시나리오 기반 감사 체크포인트
d207("1152-1168", "§8 감사 체크포인트", "5대 시나리오 감사 체크포인트 (Trading deny/의료법률 restrict/비용초과/PII저장/P2무단활성화)", "V1,V2,V3", "FT-TEST", "테스트")

# §15.8.2 Layer 간 데이터 흐름
d207("1752-1767", "§15.8.2 Layer 데이터 흐름", "4-Layer Guardrails 간 gate_trace_id 연동 아키텍처", "V1,V2", "FT-FUNC", "신규구현")

# §15.8.4 C2PA 비용 연동
d207("1783-1787", "§15.8.4 C2PA 비용", "C2PA 서명 비용 CostBudget 연동 (c2pa_signing_cost)", "V3", "FT-CFG", "설정")

# R2 누락 항목
d207("2514", "R2 S7E-057", "이용약관/개인정보 법적 문서 표시 + 동의 관리", "V1", "FT-CFG", "설정")
d207("2517", "R2 S7E-064", "사용 통계 수집 (익명화 패턴, 로컬 전용)", "V1", "FT-FUNC", "신규구현")
d207("2549", "R2 P-038", "V1 즉시 구현 웰니스 필수 체크리스트", "V1", "FT-CFG", "설정")
d207("2550", "R2 P-042", "웰니스 성공 KPI (성과 측정 지표)", "V1", "FT-TEST", "테스트")

# §15.16 추가 웰니스
d207("2119-2123", "§15.16 P-035", "웰니스 참고 서비스 정리 (Calm/Headspace/Woebot 등)", "V1", "FT-CFG", "설정")
d207("2131-2135", "§15.16 P-041", "웰니스 크로스 레퍼런스 (카테고리간 연결 매핑)", "V1", "FT-CFG", "설정")
d207("2161-2167", "§15.16 P-040", "V3 웰니스 로드맵 (웨어러블/IoT/멀티모달)", "V3", "FT-FUNC", "신규구현")

# ============================================================
# STATISTICS
# ============================================================
d206_count = sum(1 for f in features if f["source_file"] == "D2.0-06")
d207_count = sum(1 for f in features if f["source_file"] == "D2.0-07")
total = len(features)
extractable_true = sum(1 for f in features if f["extractable"])
extractable_false = sum(1 for f in features if not f["extractable"])
inference_count = sum(1 for f in features if f["confidence"] == "추론")

cats = {}
vers = {}
for f in features:
    c = f["category"]
    cats[c] = cats.get(c, 0) + 1
    for v in f["version_scope"].split(","):
        vers[v.strip()] = vers.get(v.strip(), 0) + 1

output = {
    "meta": {
        "agent": "C-4",
        "phase": "0-C",
        "source_files": ["D2.0-06_STORAGE_MEMORY", "D2.0-07_SAFETY_COST_APPROVAL"],
        "generated_at": datetime.now().isoformat(),
        "template_ref": "v10_feature_definition.md §2.1"
    },
    "features": features,
    "statistics": {
        "total_features": total,
        "d206_count": d206_count,
        "d207_count": d207_count,
        "extractable_true": extractable_true,
        "extractable_false": extractable_false,
        "confidence_inference": inference_count,
        "by_category": dict(sorted(cats.items())),
        "by_version": dict(sorted(vers.items())),
        "judgment_needed": 0
    },
    "reading_report": {
        "D2.0-06": {
            "total_lines": 2428,
            "lines_read": 2428,
            "read_ratio": "100%",
            "unread_areas": "없음",
            "last_line_quote": "STEP7 AI기술보강 통합 완료: 2026-02-23"
        },
        "D2.0-07": {
            "total_lines": 2655,
            "lines_read": 2655,
            "read_ratio": "100%",
            "unread_areas": "없음",
            "last_line_quote": "---"
        }
    }
}

with open(r"D:\VAMOS\04. 구현단계\v10_results\phase0-c\v10_src_C04.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ v10_src_C04.json 생성 완료")
print(f"   총 피처: {total}건 (D206: {d206_count}, D207: {d207_count})")
print(f"   extractable=true: {extractable_true}, false: {extractable_false}")
print(f"   confidence=추론: {inference_count}")
print(f"   카테고리별: {dict(sorted(cats.items()))}")
print(f"   버전별: {dict(sorted(vers.items()))}")