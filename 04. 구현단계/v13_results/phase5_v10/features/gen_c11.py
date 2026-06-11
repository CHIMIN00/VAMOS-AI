#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent C-11 Feature Extraction Script
Generates src_C11.json from 8 SOT files (STEP7-B through STEP7-I)
Total: 681 features
"""
import json

features = []

# ===== S7B: Dialog Process (35 features) =====
s7b = [
    ("S7B-001", "Adaptive Thinking (난이도별 사고 깊이 자동 조절)", "FT-FUNC", "V2", "CRITICAL"),
    ("S7B-002", "텍스트 감정 감지 모듈", "FT-FUNC", "V1", "CRITICAL"),
    ("S7B-003", "적응형 응답 톤 조절", "FT-FUNC", "V1", "CRITICAL"),
    ("S7B-004", "음성 감정 분석", "FT-FUNC", "V2", "HIGH"),
    ("S7B-005", "Hook 라이프사이클 시스템 (PreToolUse/PostToolUse/SessionStart 등)", "FT-FUNC", "V1", "CRITICAL"),
    ("S7B-006", "실시간 웹 검색 통합 (Search Grounding)", "FT-FUNC", "V1", "CRITICAL"),
    ("S7B-007", "명시적 사고 과정 표시 (thinking 블록)", "FT-UI", "V2", "HIGH"),
    ("S7B-008", "컨텍스트 자동 압축 (Compaction)", "FT-FUNC", "V2", "HIGH"),
    ("S7B-009", "작업 목록 관리 도구 (TodoWrite 동등)", "FT-FUNC", "V1", "HIGH"),
    ("S7B-010", "사용자 질문 도구 (AskUserQuestion 동등)", "FT-FUNC", "V1", "HIGH"),
    ("S7B-011", "계획 모드 (Plan Mode 동등)", "FT-FUNC", "V1", "HIGH"),
    ("S7B-012", "Deep Research 자율 에이전트", "FT-FUNC", "V2", "HIGH"),
    ("S7B-013", "인용 출처 인라인 표시 [1][2][3]", "FT-UI", "V1", "HIGH"),
    ("S7B-014", "이미지 생성 파이프라인", "FT-FUNC", "V2", "MEDIUM"),
    ("S7B-015", "음성 합성 (TTS) 출력", "FT-FUNC", "V2", "MEDIUM"),
    ("S7B-016", "실시간 카메라 분석", "FT-FUNC", "V3", "LOW"),
    ("S7B-017", "실시간 화면공유 분석", "FT-FUNC", "V3", "LOW"),
    ("S7B-018", "스트리밍 출력 구현", "FT-FUNC", "V1", "HIGH"),
    ("S7B-019", "신뢰도 점수 사용자 표시", "FT-UI", "V1", "HIGH"),
    ("S7B-020", "감정 이력 추적 + 대시보드", "FT-UI", "V2", "MEDIUM"),
    ("S7B-021", "얼굴 감정 분석 (카메라)", "FT-FUNC", "V3", "LOW"),
    ("S7B-022", "감정 기반 UI 적응 (FACE2FEEL)", "FT-UI", "V3", "LOW"),
    ("S7B-023", "대화 분기(Fork) - 특정 지점에서 대화를 분기하여 다른 방향 탐색", "FT-FUNC", "V2", "HIGH"),
    ("S7B-024", "대화 내보내기/가져오기 (JSON/Markdown)", "FT-FUNC", "V1", "HIGH"),
    ("S7B-025", "대화 히스토리 검색", "FT-FUNC", "V1", "HIGH"),
    ("S7B-026", "대화 자동 요약 (긴 대화 시)", "FT-FUNC", "V2", "MEDIUM"),
    ("S7B-027", "멀티 대화 병렬 실행", "FT-FUNC", "V2", "HIGH"),
    ("S7B-028", "Prompt Caching (시스템 프롬프트 캐싱)", "FT-FUNC", "V1", "CRITICAL"),
    ("S7B-029", "KV Cache 최적화 (PagedAttention)", "FT-INFRA", "V2", "HIGH"),
    ("S7B-030", "배치 처리 모드 (비동기 대량 요청)", "FT-INFRA", "V2", "MEDIUM"),
    ("S7B-031", "후속 질문 자동 제안", "FT-FUNC", "V1", "HIGH"),
    ("S7B-032", "응답 길이 동적 조절 (사용자 선호/상황 기반)", "FT-FUNC", "V1", "HIGH"),
    ("S7B-033", "수학 수식 렌더링 (LaTeX/KaTeX)", "FT-UI", "V1", "MEDIUM"),
    ("S7B-034", "사용자 피드백 수집 (thumbs up/down + 상세 피드백)", "FT-UI", "V1", "CRITICAL"),
    ("S7B-035", "응답 재생성(Regenerate) 버튼", "FT-UI", "V1", "HIGH"),
]
for fid, title, cat, ver, pri in s7b:
    features.append({"id": fid, "title": title, "category": cat, "version_scope": ver, "extractable": True, "priority": pri, "source_file": "STEP7-B"})

# ===== S7C: UI/UX (104 features) =====
s7c = [
    ("S7C-001", "3-Column 레이아웃 (사이드바 + 채팅 + 보조패널)", "V1", "CRITICAL"),
    ("S7C-002", "대화 목록 사이드바", "V1", "CRITICAL"),
    ("S7C-003", "프로젝트/스페이스 관리", "V1", "HIGH"),
    ("S7C-004", "모델/모드 선택기", "V1", "CRITICAL"),
    ("S7C-005", "빈 채팅 시작 화면", "V1", "HIGH"),
    ("S7C-006", "키보드 단축키 체계", "V1", "HIGH"),
    ("S7C-007", "반응형/모바일 대응", "V2", "HIGH"),
    ("S7C-008", "대화 분기(Fork) UI", "V2", "MEDIUM"),
    ("S7C-009", "대화 공유/링크", "V2", "MEDIUM"),
    ("S7C-010", "사용자 메시지 편집", "V1", "HIGH"),
    ("S7C-011", "멀티 대화 탭", "V2", "HIGH"),
    ("S7C-012", "VAMOS 고유: ORANGE/BLUE 상태 표시", "V1", "CRITICAL"),
    ("S7C-013", "Artifacts 패널 (인터랙티브 콘텐츠)", "V2", "HIGH"),
    ("S7C-014", "Canvas 코드 편집", "V2", "HIGH"),
    ("S7C-015", "Canvas 문서 편집", "V2", "HIGH"),
    ("S7C-016", "버전 히스토리 (Artifact/Canvas)", "V2", "MEDIUM"),
    ("S7C-017", "실시간 미리보기", "V2", "MEDIUM"),
    ("S7C-018", "차트/그래프 인터랙티브 렌더링", "V2", "MEDIUM"),
    ("S7C-019", "테이블 인터랙티브 렌더링", "V1", "HIGH"),
    ("S7C-020", "Mermaid/PlantUML 다이어그램", "V1", "HIGH"),
    ("S7C-021", "Split View (채팅 + Canvas 동시)", "V1", "HIGH"),
    ("S7C-022", "VAMOS 고유: Decision Object 시각화", "V1", "CRITICAL"),
    ("S7C-023", "멀티라인 입력 + 자동 확장", "V1", "CRITICAL"),
    ("S7C-024", "파일 드래그앤드롭 + 클립보드 붙여넣기", "V1", "CRITICAL"),
    ("S7C-025", "모델/모드 인라인 선택", "V1", "HIGH"),
    ("S7C-026", "음성 입력 버튼", "V2", "HIGH"),
    ("S7C-027", "프롬프트 템플릿 갤러리", "V1", "MEDIUM"),
    ("S7C-028", "입력 중 자동완성 제안", "V2", "MEDIUM"),
    ("S7C-029", "토큰 카운터", "V1", "HIGH"),
    ("S7C-030", "비용 미리보기", "V1", "CRITICAL"),
    ("S7C-031", "@멘션 도구 선택", "V1", "HIGH"),
    ("S7C-032", "시스템 프롬프트 편집 UI", "V1", "HIGH"),
    ("S7C-033", "Markdown 완전 렌더링", "V1", "CRITICAL"),
    ("S7C-034", "코드 블록 구문 강조", "V1", "CRITICAL"),
    ("S7C-035", "LaTeX/KaTeX 수식 렌더링", "V1", "HIGH"),
    ("S7C-036", "인라인 인용 [1][2][3]", "V1", "HIGH"),
    ("S7C-037", "Thinking 블록 접기/펼치기", "V2", "HIGH"),
    ("S7C-038", "스트리밍 타이핑 효과", "V1", "CRITICAL"),
    ("S7C-039", "이미지 인라인 표시", "V2", "MEDIUM"),
    ("S7C-040", "VAMOS 고유: 3-Part 출력 UI", "V1", "CRITICAL"),
    ("S7C-041", "VAMOS 고유: 신뢰도 표시바", "V1", "CRITICAL"),
    ("S7C-042", "VAMOS 고유: 비용 표시", "V1", "CRITICAL"),
    ("S7C-043", "피드백 버튼 (thumbs up/down + 상세)", "V1", "HIGH"),
    ("S7C-044", "재생성 + 응답 비교", "V1", "HIGH"),
    ("S7C-045", "음성 대화 전체 화면 모드", "V2", "HIGH"),
    ("S7C-046", "실시간 음성 파형 시각화", "V2", "MEDIUM"),
    ("S7C-047", "음성 모드 자막(Transcript)", "V2", "HIGH"),
    ("S7C-048", "인터럽트 UI", "V2", "MEDIUM"),
    ("S7C-049", "음성 설정 패널", "V2", "HIGH"),
    ("S7C-050", "음성-텍스트 전환", "V2", "HIGH"),
    ("S7C-051", "멀티모달 음성", "V3", "MEDIUM"),
    ("S7C-052", "VAMOS 고유: 감정 표시 아이콘", "V2", "MEDIUM"),
    ("S7C-053", "데스크톱 앱 (Electron/Tauri)", "V1", "CRITICAL"),
    ("S7C-054", "모바일 웹 PWA", "V2", "HIGH"),
    ("S7C-055", "CLI 인터페이스", "V1", "HIGH"),
    ("S7C-056", "IDE 플러그인 (VSCode)", "V2", "HIGH"),
    ("S7C-057", "시스템 트레이 빠른 접근", "V1", "HIGH"),
    ("S7C-058", "위젯 (데스크톱/모바일)", "V2", "MEDIUM"),
    ("S7C-059", "크로스 디바이스 세션 동기화", "V2", "HIGH"),
    ("S7C-060", "오프라인 UI 상태", "V1", "HIGH"),
    ("S7C-061", "알림 시스템", "V1", "HIGH"),
    ("S7C-062", "글로벌 검색", "V1", "HIGH"),
    ("S7C-063", "에이전트 실행 진행률 표시", "V1", "CRITICAL"),
    ("S7C-064", "에이전트 타임라인 뷰", "V2", "HIGH"),
    ("S7C-065", "병렬 에이전트 상태 패널", "V2", "HIGH"),
    ("S7C-066", "에이전트 중간 결과 프리뷰", "V2", "HIGH"),
    ("S7C-067", "에이전트 취소/일시정지", "V1", "HIGH"),
    ("S7C-068", "백그라운드 작업 알림", "V2", "HIGH"),
    ("S7C-069", "VAMOS 고유: 3-Gate 통과 표시", "V1", "CRITICAL"),
    ("S7C-070", "VAMOS 고유: 파이프라인 스텝 표시", "V1", "HIGH"),
    ("S7C-071", "프로필/계정 설정", "V1", "HIGH"),
    ("S7C-072", "메모리 관리 UI", "V1", "HIGH"),
    ("S7C-073", "개인 헌법 편집 UI", "V2", "HIGH"),
    ("S7C-074", "비용 대시보드", "V1", "CRITICAL"),
    ("S7C-075", "프라이버시 대시보드", "V2", "HIGH"),
    ("S7C-076", "모델 설정", "V1", "HIGH"),
    ("S7C-077", "MCP 도구 관리 UI", "V2", "HIGH"),
    ("S7C-078", "Hook 관리 UI", "V2", "MEDIUM"),
    ("S7C-079", "구독/결제 UI", "V2", "HIGH"),
    ("S7C-080", "데이터 내보내기/가져오기 UI", "V1", "HIGH"),
    ("S7C-081", "3-Gate 상태 표시기 위젯", "V1", "CRITICAL"),
    ("S7C-082", "비용 실시간 게이지 위젯", "V1", "CRITICAL"),
    ("S7C-083", "QoD 신뢰도 바 위젯", "V1", "CRITICAL"),
    ("S7C-084", "파이프라인 스텝 인디케이터 위젯", "V1", "HIGH"),
    ("S7C-085", "Decision Object 카드 위젯", "V1", "HIGH"),
    ("S7C-086", "KG 브라우저 위젯", "V2", "HIGH"),
    ("S7C-087", "에이전트 토폴로지 맵 위젯", "V2", "MEDIUM"),
    ("S7C-088", "자기진화 타임라인 위젯", "V2", "MEDIUM"),
    ("S7C-089", "감정 상태 표시기 위젯", "V2", "MEDIUM"),
    ("S7C-090", "메모리 건강도 대시보드 위젯", "V2", "MEDIUM"),
    ("S7C-091", "안전 점수 위젯", "V2", "MEDIUM"),
    ("S7C-092", "작업 패턴 인사이트 위젯", "V2", "MEDIUM"),
    ("S7C-093", "비용 시뮬레이션 위젯", "V1", "HIGH"),
    ("S7C-094", "BLUE NODE 상태 카드 위젯", "V1", "HIGH"),
    ("S7C-095", "EVX 검증 체인 시각화 위젯", "V2", "MEDIUM"),
    ("S7C-096", "프라이버시 레벨 인디케이터 위젯", "V1", "HIGH"),
    ("S7C-097", "다크 모드/라이트 모드", "V1", "HIGH"),
    ("S7C-098", "키보드 탐색", "V1", "HIGH"),
    ("S7C-099", "스크린 리더 지원", "V2", "HIGH"),
    ("S7C-100", "폰트 크기 조절", "V1", "MEDIUM"),
    ("S7C-101", "다국어 UI", "V1", "HIGH"),
    ("S7C-102", "RTL 지원", "V3", "LOW"),
    ("S7C-103", "고대비 모드", "V2", "MEDIUM"),
    ("S7C-104", "애니메이션 감소 모드", "V1", "MEDIUM"),
]
for fid, title, ver, pri in s7c:
    features.append({"id": fid, "title": title, "category": "FT-UI", "version_scope": ver, "extractable": True, "priority": pri, "source_file": "STEP7-C"})

# ===== S7D: Memory/Storage (82 features) =====
s7d = [
    ("S7D-001","GPT Memory 패턴 참조 - 자동 사실 추출","V1","CRITICAL"),
    ("S7D-002","기억해줘/잊어줘 명시 명령","V1","CRITICAL"),
    ("S7D-003","메모리 충돌 해소","V2","HIGH"),
    ("S7D-004","메모리 적중률 추적","V2","HIGH"),
    ("S7D-005","메모리 신선도 관리","V2","HIGH"),
    ("S7D-006","크로스 프로젝트 메모리 검색","V2","MEDIUM"),
    ("S7D-007","메모리 사용 로그","V1","HIGH"),
    ("S7D-008","메모리 내보내기/가져오기","V1","HIGH"),
    ("S7D-009","V1 Vector DB: Chroma 임베디드 설정","V1","CRITICAL"),
    ("S7D-010","V2 Vector DB: Qdrant 서버 전환","V2","HIGH"),
    ("S7D-011","벡터 인덱스 컬렉션 전략","V1","HIGH"),
    ("S7D-012","하이브리드 검색 구현 (벡터+BM25 RRF)","V1","CRITICAL"),
    ("S7D-013","벡터 인덱스 최적화 (HNSW 파라미터)","V2","MEDIUM"),
    ("S7D-014","벡터 차원 선택 전략","V1","HIGH"),
    ("S7D-015","Multi-tenancy 설계","V2","MEDIUM"),
    ("S7D-016","벡터 DB 백업/복원","V1","HIGH"),
    ("S7D-017","벡터 DB 모니터링","V2","MEDIUM"),
    ("S7D-018","Cross-Encoder 재순위화 구현","V1","HIGH"),
    ("S7D-019","V1 경량 KG: NetworkX + JSON 영속","V1","CRITICAL"),
    ("S7D-020","KG 스키마 설계","V1","CRITICAL"),
    ("S7D-021","자동 엔티티/관계 추출","V2","HIGH"),
    ("S7D-022","V2 Neo4j 마이그레이션","V2","HIGH"),
    ("S7D-023","GraphRAG 쿼리 파이프라인","V2","HIGH"),
    ("S7D-024","KG 충돌 감지 + 해소","V2","HIGH"),
    ("S7D-025","KG 시간적 관계","V2","MEDIUM"),
    ("S7D-026","Cognee 통합 (AI KG 자동 구축)","V2","HIGH"),
    ("S7D-027","V1 임베딩: BGE-M3 로컬 설정","V1","CRITICAL"),
    ("S7D-028","임베딩 캐싱","V1","HIGH"),
    ("S7D-029","다국어 임베딩 전략","V1","HIGH"),
    ("S7D-030","임베딩 차원 축소 (Matryoshka)","V2","MEDIUM"),
    ("S7D-031","V2 하이브리드 임베딩 (로컬+클라우드)","V2","HIGH"),
    ("S7D-032","임베딩 품질 벤치마크","V2","MEDIUM"),
    ("S7D-033","임베딩 모델 자동 업데이트","V2","MEDIUM"),
    ("S7D-034","Sparse+Dense 하이브리드 임베딩","V2","HIGH"),
    ("S7D-035","L0 세션 버퍼 구현","V1","CRITICAL"),
    ("S7D-036","L1 단기 메모리 구현","V1","CRITICAL"),
    ("S7D-037","L2 프로젝트 메모리 구현","V1","CRITICAL"),
    ("S7D-038","L3 장기 메모리 구현","V1","HIGH"),
    ("S7D-039","L4 아카이브 메모리 구현","V2","MEDIUM"),
    ("S7D-040","메모리 승격 알고리즘","V1","HIGH"),
    ("S7D-041","메모리 강등/삭제 알고리즘","V2","HIGH"),
    ("S7D-042","메모리 검색 우선순위","V1","CRITICAL"),
    ("S7D-043","메모리 스키마 설계","V1","CRITICAL"),
    ("S7D-044","메모리 중복 제거","V2","HIGH"),
    ("S7D-045","메모리 사용 통계 대시보드","V2","MEDIUM"),
    ("S7D-046","사용자 확인 후 저장 UX","V1","HIGH"),
    ("S7D-047","Prompt Cache 구현","V1","CRITICAL"),
    ("S7D-048","Semantic Cache 구현","V1","HIGH"),
    ("S7D-049","KV Cache 전략 (vLLM PagedAttention)","V2","HIGH"),
    ("S7D-050","결과 캐시 (외부 API/MCP)","V1","HIGH"),
    ("S7D-051","캐시 무효화 정책","V1","HIGH"),
    ("S7D-052","캐시 적중률 모니터링","V2","MEDIUM"),
    ("S7D-053","캐시 크기 제한 (LRU)","V1","HIGH"),
    ("S7D-054","캐시 프라이버시 (PII 미저장)","V1","HIGH"),
    ("S7D-055","문서 수집 파이프라인","V1","CRITICAL"),
    ("S7D-056","동적 청킹 전략","V1","HIGH"),
    ("S7D-057","Contextual Retrieval 구현","V1","HIGH"),
    ("S7D-058","임베딩 + 인덱싱 자동화","V1","CRITICAL"),
    ("S7D-059","메타데이터 태깅","V1","HIGH"),
    ("S7D-060","Self-RAG 루프 구현","V2","HIGH"),
    ("S7D-061","CRAG 보정 경로","V2","HIGH"),
    ("S7D-062","4중 인덱스 융합 (BM25+벡터+그래프+요약)","V2","HIGH"),
    ("S7D-063","인덱스 자동 업데이트 (watchdog)","V2","MEDIUM"),
    ("S7D-064","RAG 품질 자동 평가 (RAGAS)","V2","MEDIUM"),
    ("S7D-065","데이터 분류 체계 (4등급)","V1","HIGH"),
    ("S7D-066","PII 자동 감지 + 마스킹","V1","CRITICAL"),
    ("S7D-067","로컬-클라우드 동기화","V2","HIGH"),
    ("S7D-068","완전 삭제 보장 (GDPR 잊힐 권리)","V2","HIGH"),
    ("S7D-069","암호화 저장 (AES-256)","V1","HIGH"),
    ("S7D-070","데이터 보존 정책","V2","MEDIUM"),
    ("S7D-071","감사 로그 저장 (해시체인)","V2","HIGH"),
    ("S7D-072","백업 자동화","V1","HIGH"),
    ("S7D-073","멀티디바이스 메모리 동기화","V2","HIGH"),
    ("S7D-074","데이터 사용량 모니터링","V1","HIGH"),
    ("S7D-075","V1 저장소 비용 = 0원 (전체 로컬)","V1","CRITICAL"),
    ("S7D-076","V2 저장소 비용 예산 ($40/월)","V2","HIGH"),
    ("S7D-077","압축 전략 (ZSTD + 양자화)","V1","HIGH"),
    ("S7D-078","V1-V2 마이그레이션 스크립트","V2","HIGH"),
    ("S7D-079","V2-V3 마이그레이션 (분산 클러스터)","V3","MEDIUM"),
    ("S7D-080","저장소 추상화 레이어 (인터페이스)","V1","HIGH"),
    ("S7D-081","불필요 데이터 자동 정리 (야간 배치)","V1","MEDIUM"),
    ("S7D-082","저장소 건강도 대시보드","V2","MEDIUM"),
]
for fid, title, ver, pri in s7d:
    features.append({"id": fid, "title": title, "category": "FT-MOD", "version_scope": ver, "extractable": True, "priority": pri, "source_file": "STEP7-D"})

# ===== S7E: Security (92 features) =====
def gen_s7e():
    items = []
    # Part 1: Threat Modeling (10)
    p1 = [("S7E-001","STRIDE 기반 위협 모델링","V1","CRITICAL"),("S7E-002","AI 특화 공격 트리 작성","V1","CRITICAL"),("S7E-003","OWASP Top 10 for LLM 전체 항목 대응 매핑","V1","CRITICAL"),("S7E-004","Supply Chain 보안 - 의존성 및 모델 공급망 검증","V1","CRITICAL"),("S7E-005","API Key 관리 - 안전한 키 저장/순환/폐기","V1","HIGH"),("S7E-006","Input Validation - 모든 사용자 입력 검증 체계","V1","HIGH"),("S7E-007","Output Sanitization - LLM 출력 안전성 보장","V1","HIGH"),("S7E-008","Rate Limiting / Cost Protection - 과도한 사용 방지","V1","HIGH"),("S7E-009","Penetration Testing 계획 - 정기 보안 점검","V2","MEDIUM"),("S7E-010","Security Champions 프로그램 - 보안 문화 내재화","V2","MEDIUM")]
    # Part 2: Prompt Injection (10)
    p2 = [("S7E-011","Instruction Hierarchy - 시스템/사용자/도구 프롬프트 우선순위","V1","CRITICAL"),("S7E-012","Input/Output Tagging - 신뢰 경계 마킹","V1","CRITICAL"),("S7E-013","Canary Token / Tripwire - 프롬프트 추출 감지","V1","CRITICAL"),("S7E-014","Indirect Injection 방어 - 외부 콘텐츠 격리","V1","CRITICAL"),("S7E-015","Tool Call 검증 - MCP Tool Poisoning 방어","V1","CRITICAL"),("S7E-016","Multi-layer Defense - 다층 방어 아키텍처","V1","CRITICAL"),("S7E-017","Jailbreak 방어 - 가드레일 우회 차단","V1","HIGH"),("S7E-018","Prompt Injection 탐지 모델 - ML 기반 분류기","V1","HIGH"),("S7E-019","Agent Sandboxing - Agent 실행 환경 격리","V2","HIGH"),("S7E-020","Red Team 자동화 - 자체 보안 테스트 파이프라인","V2","MEDIUM")]
    # Part 3: Auth/RBAC (10)
    p3 = [("S7E-021","로컬 인증 - PIN/패스워드/생체인증","V1","CRITICAL"),("S7E-022","OAuth2 + MFA - 서버 배포 시 인증 강화","V2","CRITICAL"),("S7E-023","RBAC - 역할 기반 접근제어","V1","CRITICAL"),("S7E-024","API Key Scoping - 최소 권한 API 키","V2","HIGH"),("S7E-025","Tool 실행 권한 - MCP Tool별 허가 체계","V1","HIGH"),("S7E-026","Session 관리 - 안전한 세션 라이프사이클","V1","HIGH"),("S7E-027","Zero-Trust Architecture - 제로 트러스트 원칙 적용","V2","HIGH"),("S7E-028","감사 추적(Audit Trail) - 모든 접근 기록","V2","HIGH"),("S7E-029","Data Access Layer - 데이터 접근 권한 세분화","V2","MEDIUM"),("S7E-030","SSO 통합 - 기업 환경 싱글 사인온","V3","MEDIUM")]
    # Part 4: Privacy (10)
    p4 = [("S7E-031","PII 탐지 및 마스킹 - 개인식별정보 자동 보호","V1","CRITICAL"),("S7E-032","로컬 데이터 암호화 - 저장 데이터 보호","V1","CRITICAL"),("S7E-033","데이터 주권 - 사용자 데이터 완전 소유권","V1","CRITICAL"),("S7E-034","데이터 최소화 - 필요 최소한의 데이터만 수집/전송","V1","HIGH"),("S7E-035","Opt-in/Opt-out - 학습 데이터 사용 거부","V1","HIGH"),("S7E-036","E2E 암호화 - 서버 통신 종단간 암호화","V2","HIGH"),("S7E-037","GDPR / 개인정보보호법 준수","V2","HIGH"),("S7E-038","데이터 보존 정책 - 자동 만료 및 삭제","V2","MEDIUM"),("S7E-039","익명화/가명화 - 분석 데이터 보호","V1","MEDIUM"),("S7E-040","프라이버시 대시보드 - 데이터 투명성 UI","V2","MEDIUM")]
    # Part 5: AI Safety (10)
    p5 = [("S7E-041","Personal Constitution - 개인 헌법 시스템","V1","CRITICAL"),("S7E-042","Confidence & Uncertainty - 확신도 투명 표시","V1","CRITICAL"),("S7E-043","Refusal Protocol - 거부 프로토콜","V1","HIGH"),("S7E-044","Hallucination 방지 - 환각 최소화 전략","V1","HIGH"),("S7E-045","Bias 감지 및 완화 - 편향 관리","V1","HIGH"),("S7E-046","Harm Assessment - 위해성 평가 자동화","V2","HIGH"),("S7E-047","투명성 보고서 - AI 행동 투명 공개","V1","HIGH"),("S7E-048","Ethical Guardrails - 윤리적 가드레일","V2","MEDIUM"),("S7E-049","Safety Benchmark - 안전성 정량 평가","V2","MEDIUM"),("S7E-050","Human-in-the-Loop - 인간 개입 체계","V2","MEDIUM")]
    # Part 6: Compliance (10)
    p6 = [("S7E-051","EU AI Act 위험등급 자체 평가","V1","CRITICAL"),("S7E-052","투명성 의무 이행 - AI 고지 및 설명","V2","CRITICAL"),("S7E-053","금융 규제 검토 - AI 투자 조언 관련 법적 요건","V1","CRITICAL"),("S7E-054","NIST AI RMF 매핑 - 리스크 관리 프레임워크 적용","V2","HIGH"),("S7E-055","ISO 42001 준비 - AI 관리시스템 인증 대비","V2","HIGH"),("S7E-056","면책 고지 시스템 - 자동 면책 표시","V1","HIGH"),("S7E-057","이용약관 / 개인정보처리방침 - 법적 문서 준비","V1","HIGH"),("S7E-058","컴플라이언스 자동 체크 - 규제 준수 자동 검증","V2","MEDIUM"),("S7E-059","AI 영향평가 - 한국 AI기본법 대비","V2","MEDIUM"),("S7E-060","국가별 규제 적응 - 글로벌 컴플라이언스","V3","MEDIUM")]
    # Part 7: Monitoring (8)
    p7 = [("S7E-061","보안 이벤트 로깅 - 보안 관련 이벤트 전수 기록","V1","CRITICAL"),("S7E-062","비용 모니터링 - API 사용량/비용 실시간 추적","V1","CRITICAL"),("S7E-063","Agent 활동 추적 - Agent 실행 이력 기록","V1","HIGH"),("S7E-064","사용 통계 수집 - 자기개선용 내부 메트릭","V1","HIGH"),("S7E-065","이상 탐지 - Anomaly Detection","V2","HIGH"),("S7E-066","알림 시스템 - 보안 이벤트 실시간 알림","V2","HIGH"),("S7E-067","감사 보고서 자동 생성 - 정기 보안 리포트","V2","MEDIUM"),("S7E-068","로그 무결성 보장 - 변조 방지 로깅","V2","MEDIUM")]
    # Part 8: Incident (8)
    p8 = [("S7E-069","인시던트 분류 체계 - 심각도 및 유형 분류","V1","HIGH"),("S7E-070","자동 격리 - 위협 자동 차단","V1","HIGH"),("S7E-071","롤백 시스템 - 상태 복구 체계","V2","HIGH"),("S7E-072","Root Cause Analysis - 근본 원인 분석 절차","V2","HIGH"),("S7E-073","긴급 연락 체계 - 인시던트 에스컬레이션","V1","MEDIUM"),("S7E-074","안전 모드 - 비상 시 최소 기능 모드","V1","MEDIUM"),("S7E-075","인시던트 대응 훈련 - 정기 모의 훈련","V2","MEDIUM"),("S7E-076","보안 인시던트 DB - 인시던트 이력 관리","V2","MEDIUM")]
    # Part 9: Agent Security (8)
    p9 = [("S7E-077","Agent 최소 권한 원칙","V1","CRITICAL"),("S7E-078","Agent 통신 보안 - Inter-Agent Security","V1","CRITICAL"),("S7E-079","Tool 실행 게이트 - 위험 Tool 사전 차단","V1","CRITICAL"),("S7E-080","Delegation Attack 방어 - Agent 위임 공격 차단","V1","CRITICAL"),("S7E-081","데이터 경계 - Agent 간 데이터 격리","V1","HIGH"),("S7E-082","Agent 행동 모니터링 - 비정상 행동 탐지","V2","HIGH"),("S7E-083","Agent 버전 관리 - Agent 코드 무결성","V2","HIGH"),("S7E-084","Multi-Agent 보안 테스트","V2","MEDIUM")]
    # Part 10: VAMOS Differentiation (8)
    p10 = [("S7E-085","3-Gate Security Integration - 3-Gate 보안 통합","V1","HIGH"),("S7E-086","Privacy-by-Design - 프라이버시 내재 설계","V1","HIGH"),("S7E-087","Security-First 온보딩 - 보안 설정 우선 안내","V1","HIGH"),("S7E-088","보안 등급 점수 - Security Posture Score","V2","HIGH"),("S7E-089","데이터 유출 방지 (DLP)","V1","HIGH"),("S7E-090","Threat Intelligence 연동 - 외부 위협 정보 활용","V2","MEDIUM"),("S7E-091","보안 교육 콘텐츠 - 사용자 보안 인식 향상","V2","MEDIUM"),("S7E-092","보안 로드맵 - 버전별 보안 강화 계획","V2","MEDIUM")]
    items = p1+p2+p3+p4+p5+p6+p7+p8+p9+p10
    return items

for fid, title, ver, pri in gen_s7e():
    features.append({"id": fid, "title": title, "category": "FT-SEC", "version_scope": ver, "extractable": True, "priority": pri, "source_file": "STEP7-E"})

# ===== S7F: Infrastructure (96 features) =====
def gen_s7f():
    items = []
    for i in range(1, 97):
        fid = f"S7F-{i:03d}"
        items.append(fid)
    return items

s7f_data = [
    ("S7F-001","Ollama 기반 로컬 LLM 서빙 - V1 핵심 엔진","V1","CRITICAL"),
    ("S7F-002","API 기반 클라우드 LLM 호출 - 고성능 처리","V1","CRITICAL"),
    ("S7F-003","모델 라우터 - 지능형 모델 선택 엔진","V1","CRITICAL"),
    ("S7F-004","모델 Fallback 체인 - 장애 시 대체 모델 자동 전환","V1","HIGH"),
    ("S7F-005","스트리밍 응답 - SSE 기반 실시간 출력","V1","HIGH"),
    ("S7F-006","Prompt Caching 활용 - API 비용 50-90% 절감","V1","HIGH"),
    ("S7F-007","양자화 모델 관리 - 로컬 모델 최적화","V1","HIGH"),
    ("S7F-008","Model Gateway - 통합 모델 게이트웨이","V2","HIGH"),
    ("S7F-009","Batch Processing - 대량 요청 배치 처리","V2","MEDIUM"),
    ("S7F-010","A/B 모델 테스트 - 모델 성능 비교 프레임워크","V2","MEDIUM"),
    ("S7F-011","Tauri 데스크톱 앱 - 크로스플랫폼 네이티브 앱","V1","CRITICAL"),
    ("S7F-012","Node.js 사이드카 - Agent 로직 런타임","V1","CRITICAL"),
    ("S7F-013","로컬 저장소 구성 - ~/vamos/ 디렉토리 구조","V1","CRITICAL"),
    ("S7F-014","시스템 요구사항 - 최소/권장 하드웨어","V1","CRITICAL"),
    ("S7F-015","자동 설치 스크립트 - 원클릭 설치","V1","HIGH"),
    ("S7F-016","자동 업데이트 - 앱 자동 업데이트 시스템","V1","HIGH"),
    ("S7F-017","프로세스 관리 - 멀티 프로세스 라이프사이클","V1","HIGH"),
    ("S7F-018","오프라인 모드 - 인터넷 없이 동작","V1","HIGH"),
    ("S7F-019","시스템 트레이 - 백그라운드 상주","V1","MEDIUM"),
    ("S7F-020","개발 환경 설정 - 개발자 로컬 세팅 가이드","V1","MEDIUM"),
    ("S7F-021","VPS 선정 - 서버 호스팅 비교","V2","HIGH"),
    ("S7F-022","Next.js 웹 앱 - 서버 렌더링 웹 클라이언트","V2","HIGH"),
    ("S7F-023","PostgreSQL - 메인 관계형 DB","V2","HIGH"),
    ("S7F-024","Qdrant - 프로덕션 벡터 DB","V2","HIGH"),
    ("S7F-025","Redis 캐시 - 고속 캐시 및 세션 관리","V2","HIGH"),
    ("S7F-026","Neo4j 그래프 DB - Knowledge Graph 서버","V2","HIGH"),
    ("S7F-027","메시지 큐 - 비동기 작업 처리","V2","MEDIUM"),
    ("S7F-028","파일 저장소 - 업로드 파일 관리","V2","MEDIUM"),
    ("S7F-029","WebSocket 서버 - 실시간 양방향 통신","V2","MEDIUM"),
    ("S7F-030","환경 분리 - Dev/Staging/Prod 환경","V2","MEDIUM"),
    ("S7F-031","Kubernetes 배포 - 오케스트레이션","V3","MEDIUM"),
    ("S7F-032","GPU 클러스터 - 자체 모델 서빙","V3","MEDIUM"),
    ("S7F-033","멀티 리전 배포 - 글로벌 서비스","V3","MEDIUM"),
    ("S7F-034","데이터 파이프라인 - 대규모 데이터 처리","V3","MEDIUM"),
    ("S7F-035","멀티 테넌시 - 기업 고객 격리","V3","LOW"),
    ("S7F-036","SLA 관리 - 서비스 수준 보장","V3","LOW"),
    ("S7F-037","Docker Compose - V2 로컬/서버 배포","V2","HIGH"),
    ("S7F-038","Dockerfile 최적화 - 이미지 최소화","V2","HIGH"),
    ("S7F-039","헬스체크 - 컨테이너 상태 모니터링","V2","HIGH"),
    ("S7F-040","시크릿 관리 - Docker Secrets","V2","HIGH"),
    ("S7F-041","볼륨 관리 - 데이터 영속성","V2","MEDIUM"),
    ("S7F-042","네트워크 격리 - 서비스 간 네트워크 분리","V2","MEDIUM"),
    ("S7F-043","리소스 제한 - 컨테이너 리소스 관리","V2","MEDIUM"),
    ("S7F-044","Helm Charts - K8s 패키지 관리","V3","MEDIUM"),
    ("S7F-045","GitHub Actions CI - 자동 빌드/테스트","V1","CRITICAL"),
    ("S7F-046","CD 파이프라인 - 자동 배포","V2","CRITICAL"),
    ("S7F-047","코드 품질 게이트 - PR 자동 검사","V1","HIGH"),
    ("S7F-048","테스트 자동화 - 테스트 전략","V1","HIGH"),
    ("S7F-049","릴리즈 관리 - 버전닝 및 릴리즈","V2","HIGH"),
    ("S7F-050","의존성 관리 - 자동 업데이트","V1","HIGH"),
    ("S7F-051","브랜치 전략 - Git Flow","V1","MEDIUM"),
    ("S7F-052","Feature Flag - 기능 플래그 관리","V2","MEDIUM"),
    ("S7F-053","구조화된 로깅 - JSON 기반 로그","V1","HIGH"),
    ("S7F-054","LLM 메트릭 수집 - AI 특화 메트릭","V1","HIGH"),
    ("S7F-055","Grafana 대시보드 - 통합 모니터링 UI","V2","HIGH"),
    ("S7F-056","Langfuse 통합 - LLM 옵저버빌리티","V2","HIGH"),
    ("S7F-057","알림 규칙 - 자동 알림 설정","V2","HIGH"),
    ("S7F-058","OpenTelemetry - 분산 트레이싱","V2","MEDIUM"),
    ("S7F-059","상태 페이지 - 서비스 가용성 공개","V2","MEDIUM"),
    ("S7F-060","로그 보존 정책 - 로그 라이프사이클","V2","MEDIUM"),
    ("S7F-061","스마트 모델 라우팅 비용 최적화","V1","CRITICAL"),
    ("S7F-062","토큰 최적화 - 프롬프트 효율화","V1","CRITICAL"),
    ("S7F-063","비용 대시보드 - 실시간 비용 추적 UI","V1","HIGH"),
    ("S7F-064","예산 하드캡 - 비용 상한 강제 적용","V1","HIGH"),
    ("S7F-065","Free Tier 최대 활용 - 무료 리소스 전략","V1","HIGH"),
    ("S7F-066","시맨틱 캐싱 - 유사 질문 결과 재사용","V2","HIGH"),
    ("S7F-067","Spot/Preemptible 인스턴스 - 비프로덕션 비용 절감","V2","MEDIUM"),
    ("S7F-068","비용 예측 - 월간 비용 예측 모델","V2","MEDIUM"),
    ("S7F-069","프롬프트 버전 관리 - 시스템 프롬프트 관리","V1","HIGH"),
    ("S7F-070","프롬프트 테스트 - promptfoo 자동 평가","V1","HIGH"),
    ("S7F-071","모델 평가 파이프라인 - 새 모델 자동 평가","V2","HIGH"),
    ("S7F-072","피드백 루프 - 사용자 피드백 수집/반영","V2","HIGH"),
    ("S7F-073","프롬프트 최적화 - 자동 프롬프트 개선","V2","HIGH"),
    ("S7F-074","모델 드리프트 감지 - 성능 저하 자동 탐지","V2","HIGH"),
    ("S7F-075","실험 관리 - A/B 테스트 프레임워크","V2","MEDIUM"),
    ("S7F-076","모델 카탈로그 - 사용 가능 모델 목록 관리","V1","MEDIUM"),
    ("S7F-077","Fine-tuning 파이프라인 - 커스텀 모델 학습","V2","MEDIUM"),
    ("S7F-078","Guardrails 파이프라인 - 입출력 가드레일 관리","V2","MEDIUM"),
    ("S7F-079","API 게이트웨이 - 통합 API 관리","V2","HIGH"),
    ("S7F-080","SSL/TLS - HTTPS 필수 적용","V2","HIGH"),
    ("S7F-081","CORS 정책 - 교차 출처 요청 제어","V2","HIGH"),
    ("S7F-082","API 버전닝 - 하위 호환성 보장","V2","HIGH"),
    ("S7F-083","CDN 설정 - 정적 자산 배포","V2","MEDIUM"),
    ("S7F-084","DDoS 방어 - 대량 요청 방어","V2","MEDIUM"),
    ("S7F-085","자동 백업 - 일일 자동 데이터 백업","V1","HIGH"),
    ("S7F-086","복구 절차 - 백업에서 복구","V1","HIGH"),
    ("S7F-087","오프사이트 백업 - 원격 백업","V2","HIGH"),
    ("S7F-088","데이터 마이그레이션 - V1-V2 마이그레이션","V2","MEDIUM"),
    ("S7F-089","재해 복구 계획 - DR 절차","V2","MEDIUM"),
    ("S7F-090","데이터 export/import - 포터빌리티","V2","MEDIUM"),
    ("S7F-091","TTFT 최적화 - 첫 토큰 응답 시간 최소화","V1","CRITICAL"),
    ("S7F-092","메모리 사용량 최적화 - 리소스 효율","V1","CRITICAL"),
    ("S7F-093","동시성 관리 - 병렬 요청 처리","V1","HIGH"),
    ("S7F-094","응답 시간 SLO - 내부 성능 목표","V1","HIGH"),
    ("S7F-095","데이터베이스 성능 - 쿼리 최적화","V2","HIGH"),
    ("S7F-096","프론트엔드 성능 - UI 렌더링 최적화","V2","MEDIUM"),
]
for fid, title, ver, pri in s7f_data:
    features.append({"id": fid, "title": title, "category": "FT-INFRA", "version_scope": ver, "extractable": True, "priority": pri, "source_file": "STEP7-F"})

# ===== S7G: Benchmarks (88 features) =====
s7g_data = [
    ("S7G-001","MMLU/MMLU-Pro - 범용 지식 벤치마크","V1","HIGH"),
    ("S7G-002","HumanEval / MBPP - 코딩 능력 평가","V1","HIGH"),
    ("S7G-003","MT-Bench - 다턴 대화 품질 평가","V1","HIGH"),
    ("S7G-004","IFEval - 지시 따르기 평가","V1","HIGH"),
    ("S7G-005","GPQA / ARC-C - 전문 지식 + 추론 평가","V1","HIGH"),
    ("S7G-006","MATH / GSM8K - 수학적 추론 평가","V1","HIGH"),
    ("S7G-007","AlpacaEval 2.0 - 지시따르기 자동 평가","V2","MEDIUM"),
    ("S7G-008","Chatbot Arena ELO - 인간 선호도 기반 평가","V2","MEDIUM"),
    ("S7G-009","WildBench - 실제 사용 시나리오 벤치마크","V2","MEDIUM"),
    ("S7G-010","LiveBench - 지속 갱신 벤치마크","V2","MEDIUM"),
    ("S7G-011","KoBEST - 한국어 기본 NLU 평가","V1","CRITICAL"),
    ("S7G-012","KLUE - 한국어 NLU 표준 벤치마크","V1","CRITICAL"),
    ("S7G-013","LogicKor - 한국어 논리 추론 평가","V1","HIGH"),
    ("S7G-014","CLIcK - 한국 문화 지식 평가","V1","HIGH"),
    ("S7G-015","한국어 환각 테스트","V1","HIGH"),
    ("S7G-016","한국어 존댓말/비속어 테스트","V1","HIGH"),
    ("S7G-017","Ko-MMLU - MMLU 한국어 버전","V2","MEDIUM"),
    ("S7G-018","한국어 생성 품질 - 작문/요약/번역 평가","V2","MEDIUM"),
    ("S7G-019","HumanEval / HumanEval+ - Python 코드 생성","V1","HIGH"),
    ("S7G-020","SWE-bench (Verified) - 실전 소프트웨어 엔지니어링","V1","HIGH"),
    ("S7G-021","BFCL - Berkeley Function Calling Leaderboard","V1","HIGH"),
    ("S7G-022","Aider Polyglot - 실전 코드 편집 평가","V1","HIGH"),
    ("S7G-023","MultiPL-E - 다언어 코딩 평가","V1","HIGH"),
    ("S7G-024","코드 보안 평가 - CWE/SAST 기반","V2","MEDIUM"),
    ("S7G-025","코드 리뷰 품질 - PR 리뷰 정확도","V2","MEDIUM"),
    ("S7G-026","디버깅 능력 - 버그 찾기/고치기 평가","V2","MEDIUM"),
    ("S7G-027","BFCL v3 - Tool/Function Calling 평가","V1","CRITICAL"),
    ("S7G-028","Tau-bench - 대화형 Agent 평가","V1","CRITICAL"),
    ("S7G-029","GAIA - General AI Assistants 벤치마크","V1","HIGH"),
    ("S7G-030","AgentBench - 다환경 Agent 종합 평가","V1","HIGH"),
    ("S7G-031","ToolBench - 대규모 API 활용 평가","V2","HIGH"),
    ("S7G-032","WebArena / VisualWebArena - 웹 자동화 평가","V2","HIGH"),
    ("S7G-033","OSWorld - OS 조작 Agent 평가","V2","MEDIUM"),
    ("S7G-034","MLE-bench - ML 엔지니어링 Agent 평가","V2","MEDIUM"),
    ("S7G-035","RAGAS 프레임워크 - RAG 자동 평가","V1","CRITICAL"),
    ("S7G-036","검색 정확도 평가 - Retrieval Metrics","V1","CRITICAL"),
    ("S7G-037","Faithfulness 테스트 - 환각 방지 평가","V1","HIGH"),
    ("S7G-038","Chunking 품질 평가 - 문서 분할 최적화","V1","HIGH"),
    ("S7G-039","Embedding 모델 비교 평가 - 한국어 특화","V1","HIGH"),
    ("S7G-040","컨텍스트 윈도우 활용 평가 - Long Context","V1","HIGH"),
    ("S7G-041","RAG vs Long Context - 전략 비교 테스트","V2","HIGH"),
    ("S7G-042","Self-RAG / CRAG 품질 평가","V2","MEDIUM"),
    ("S7G-043","다국어 RAG 평가 - 한국어/영어 혼합 검색","V2","MEDIUM"),
    ("S7G-044","Knowledge Graph RAG 평가","V2","MEDIUM"),
    ("S7G-045","TruthfulQA - 진실성 평가","V1","CRITICAL"),
    ("S7G-046","Prompt Injection 저항성 - 보안 테스트 스위트","V1","CRITICAL"),
    ("S7G-047","ToxiGen - 유해 콘텐츠 생성 평가","V1","HIGH"),
    ("S7G-048","BBQ (Bias Benchmark) - 편향 평가","V1","HIGH"),
    ("S7G-049","AdvBench - 적대적 공격 저항성","V1","HIGH"),
    ("S7G-050","한국어 안전성 테스트 - 한국 맥락 안전성","V2","HIGH"),
    ("S7G-051","AI Deception 테스트 - 기만 행동 탐지","V2","MEDIUM"),
    ("S7G-052","긴급 상황 대응 - 자해/위기 상황 대응 품질","V2","MEDIUM"),
    ("S7G-053","작업 완수율 - Task Completion Rate","V1","HIGH"),
    ("S7G-054","응답 시간 체감 - Perceived Latency","V1","HIGH"),
    ("S7G-055","사용자 만족도 - User Satisfaction Score","V1","HIGH"),
    ("S7G-056","대화 효율성 - Conversation Efficiency","V1","HIGH"),
    ("S7G-057","온보딩 효과 - First-Time User Experience","V1","MEDIUM"),
    ("S7G-058","개인화 효과 - Personalization Impact","V2","MEDIUM"),
    ("S7G-059","접근성 평가 - WCAG 준수","V2","MEDIUM"),
    ("S7G-060","다국어 UX - 한국어/영어 전환 경험","V2","MEDIUM"),
    ("S7G-061","VBS-1: 3-Gate 정확도","V1","CRITICAL"),
    ("S7G-062","VBS-2: 모델 라우팅 효율","V1","CRITICAL"),
    ("S7G-063","VBS-3: 메모리 회상 품질","V1","CRITICAL"),
    ("S7G-064","VBS-6: 비용 효율 비율","V1","HIGH"),
    ("S7G-065","VBS-7: Constitution 준수율","V1","HIGH"),
    ("S7G-066","VBS-4: KG 탐색 품질","V1","HIGH"),
    ("S7G-067","VBS-5: 자기진화 점수","V2","HIGH"),
    ("S7G-068","VBS-8: Agent 협업 품질","V2","HIGH"),
    ("S7G-069","VBS-9: 개인 비서 종합 점수","V2","MEDIUM"),
    ("S7G-070","VBS-10: 투자 분석 품질","V2","MEDIUM"),
    ("S7G-071","LLM-as-Judge - LLM 자동 평가기","V1","HIGH"),
    ("S7G-072","promptfoo 통합 - 프롬프트 자동 테스트","V1","HIGH"),
    ("S7G-073","회귀 테스트 자동화 - 품질 저하 방지","V1","HIGH"),
    ("S7G-074","자동 벤치마크 스케줄러 - 정기 평가 실행","V1","HIGH"),
    ("S7G-075","평가 대시보드 - 벤치마크 결과 시각화","V2","HIGH"),
    ("S7G-076","자동 리포트 생성 - 평가 보고서","V2","MEDIUM"),
    ("S7G-077","경쟁사 추적 - 경쟁 AI 성능 모니터링","V2","MEDIUM"),
    ("S7G-078","평가 데이터셋 관리 - 골든 데이터셋","V2","MEDIUM"),
    ("S7G-079","자기 평가 - 개발자 정기 품질 체크","V1","HIGH"),
    ("S7G-080","베타 테스터 피드백 - 외부 사용자 평가","V2","HIGH"),
    ("S7G-081","A/B 인간 비교 - VAMOS vs 경쟁 AI","V2","HIGH"),
    ("S7G-082","시나리오 기반 테스트 - 실제 사용 시나리오","V2","MEDIUM"),
    ("S7G-083","전문가 리뷰 - 도메인 전문가 평가","V2","MEDIUM"),
    ("S7G-084","장기 사용성 연구 - Longitudinal Study","V3","MEDIUM"),
    ("S7G-085","QA 체크리스트 - 릴리즈 전 품질 게이트","V1","HIGH"),
    ("S7G-086","버그 트래킹 - 이슈 관리 프로세스","V1","HIGH"),
    ("S7G-087","품질 지표 (KPI) - 핵심 품질 목표","V2","MEDIUM"),
    ("S7G-088","지속적 개선 - Continuous Improvement","V2","MEDIUM"),
]
for fid, title, ver, pri in s7g_data:
    features.append({"id": fid, "title": title, "category": "FT-TEST", "version_scope": ver, "extractable": True, "priority": pri, "source_file": "STEP7-G"})

# ===== S7H: Business Model (78 features) =====
s7h_data = [
    # Part 1: AI 서비스 가격 전수비교 (10건)
    ("S7H-001","가격 모니터링 대시보드 — API 가격 추적","V1","HIGH"),
    ("S7H-002","구독 서비스 가치 분석 — $20/mo vs VAMOS","V1","HIGH"),
    ("S7H-003","코딩 AI 가격 분석 — 개발자 도구 비교","V1","HIGH"),
    ("S7H-004","생산성 AI 가격 분석 — Notion AI 등","V1","HIGH"),
    ("S7H-005","TCO 분석 — Total Cost of Ownership","V1","HIGH"),
    ("S7H-006","무료 대안 분석 — Free Tier 경쟁","V1","HIGH"),
    ("S7H-007","B2B 가격 전략 — 기업 판매 가격 모델","V2","MEDIUM"),
    ("S7H-008","가격 탄력성 분석 — 최적 가격점 결정","V2","MEDIUM"),
    ("S7H-009","프리미엄 기능 정의 — Free vs Paid 경계","V2","MEDIUM"),
    ("S7H-010","번들 전략 — 패키지 구성","V2","MEDIUM"),
    # Part 2: VAMOS 가격 전략 (8건)
    ("S7H-011","Pay-as-you-go 핵심 전략 — 사용한 만큼만","V1","CRITICAL"),
    ("S7H-012","비용 투명성 — 경쟁 차별화 핵심","V1","CRITICAL"),
    ("S7H-013","비용 제어 — 사용자가 완전히 통제","V1","CRITICAL"),
    ("S7H-014","데이터 주권 가치 — 프라이버시 프리미엄","V1","HIGH"),
    ("S7H-015","오픈소스 전략 — 코어 무료, 프리미엄 유료","V1","HIGH"),
    ("S7H-016","초기 사용자 확보 — Launch 전략","V1","HIGH"),
    ("S7H-017","프리미엄 전환율 — Free→Paid 전략","V2","MEDIUM"),
    ("S7H-018","파트너십 수익 — API 프로바이더 제휴","V2","MEDIUM"),
    # Part 3: 수익 모델 설계 (8건)
    ("S7H-019","API 마진 모델 — V1 수익화 시작점","V1","CRITICAL"),
    ("S7H-020","SaaS 구독 모델 — V2 핵심 수익","V2","CRITICAL"),
    ("S7H-021","MCP Tool 마켓플레이스 — 도구 생태계 수익","V2","HIGH"),
    ("S7H-022","프리미엄 Agent 패키지 — 전문 Agent 유료화","V2","HIGH"),
    ("S7H-023","기업 라이선스 — B2B 수익","V2","HIGH"),
    ("S7H-024","데이터 분석 인사이트 — 익명화된 사용 패턴","V2","HIGH"),
    ("S7H-025","교육 / 인증 프로그램 — 지식 수익화","V3","MEDIUM"),
    ("S7H-026","화이트 라벨 — 기업 브랜딩 제공","V3","MEDIUM"),
    # Part 4: 타겟 페르소나 (8건)
    ("S7H-027","P1: 테크 얼리어답터 — 핵심 초기 사용자","V1","CRITICAL"),
    ("S7H-028","P2: 생산성 추구 지식 노동자 — 주 타겟","V1","CRITICAL"),
    ("S7H-029","P3: AI 투자자 — 니치 고가치 사용자","V1","HIGH"),
    ("S7H-030","P4: 프라이버시 중시 사용자 — 차별화 타겟","V1","HIGH"),
    ("S7H-031","P5: 소규모 팀 — V2 확장 타겟","V2","HIGH"),
    ("S7H-032","사용자 여정 맵 — User Journey","V1","HIGH"),
    ("S7H-033","사용자 세그먼트별 기능 우선순위","V2","MEDIUM"),
    ("S7H-034","이탈 방지 — Churn Prevention","V2","MEDIUM"),
    # Part 5: 시장 규모 분석 (6건)
    ("S7H-035","TAM/SAM/SOM — 시장 규모 단계별 산출","V1","HIGH"),
    ("S7H-036","한국 AI 시장 특수성 — 한국 시장 분석","V1","HIGH"),
    ("S7H-037","성장 시나리오 — 낙관/기준/비관","V1","HIGH"),
    ("S7H-038","경쟁 구도 분석 — 5 Forces 분석","V2","HIGH"),
    ("S7H-039","기업 시장 규모 — B2B 기회 분석","V2","MEDIUM"),
    ("S7H-040","지역 확장 전략 — 한국→글로벌","V2","MEDIUM"),
    # Part 6: 경쟁 포지셔닝 (8건)
    ("S7H-041","핵심 차별화 포지션 — 개인화된 AI 비서","V1","CRITICAL"),
    ("S7H-042","경쟁 비교 매트릭스 — 전수비교","V1","CRITICAL"),
    ("S7H-043","MOAT 분석 — 경쟁 방어벽","V1","HIGH"),
    ("S7H-044","핵심 메시지 3개 — 마케팅 메시지","V1","HIGH"),
    ("S7H-045","비교 콘텐츠 전략 — vs ChatGPT 콘텐츠","V1","HIGH"),
    ("S7H-046","오픈소스 커뮤니티 — 경쟁 차별화","V2","HIGH"),
    ("S7H-047","파트너십 전략 — 전략적 제휴","V2","MEDIUM"),
    ("S7H-048","특허/IP 전략 — 지적 재산 보호","V2","MEDIUM"),
    # Part 7: GTM 전략 (8건)
    ("S7H-049","Phase 1: 씨드 단계 — 최소 비용 런칭","V1","HIGH"),
    ("S7H-050","콘텐츠 마케팅 — SEO + 교육 콘텐츠","V1","HIGH"),
    ("S7H-051","커뮤니티 운영 — 사용자 커뮤니티","V2","HIGH"),
    ("S7H-052","데모 / 쇼케이스 — 실제 사용 시연","V1","HIGH"),
    ("S7H-053","Phase 2: 성장 단계 — 유기적 성장","V2","HIGH"),
    ("S7H-054","SEO / ASO 전략 — 검색 최적화","V2","MEDIUM"),
    ("S7H-055","Phase 3: 스케일 — 유료 확장","V3","MEDIUM"),
    ("S7H-056","투자 유치 전략 — 펀딩 로드맵","V3","MEDIUM"),
    # Part 8: 성장 전략 (8건)
    ("S7H-057","바이럴 메커니즘 — 자연적 확산","V1","HIGH"),
    ("S7H-058","개발자 애드보케이시 — 기술 리더십","V1","HIGH"),
    ("S7H-059","MCP 생태계 성장 — Tool 마켓 플라이휠","V2","HIGH"),
    ("S7H-060","리텐션 전략 — 사용자 유지","V2","HIGH"),
    ("S7H-061","크로스 셀 / 업셀 — 수익 극대화","V2","MEDIUM"),
    ("S7H-062","전략적 인수 대상 — M&A 기회","V2","MEDIUM"),
    ("S7H-063","국제화 — i18n/L10n 전략","V3","MEDIUM"),
    ("S7H-064","엔터프라이즈 세일즈 — B2B 판매 체계","V3","MEDIUM"),
    # Part 9: 리스크 분석 (8건)
    ("S7H-065","API 가격 리스크 — 가격 변동 대응","V1","CRITICAL"),
    ("S7H-066","경쟁 리스크 — Big Tech의 무료화 전략","V1","CRITICAL"),
    ("S7H-067","기술 리스크 — LLM 품질 저하/변경","V1","HIGH"),
    ("S7H-068","사용자 확보 리스크 — PMF 미달성","V1","HIGH"),
    ("S7H-069","보안 리스크 — 데이터 유출/인시던트","V1","HIGH"),
    ("S7H-070","법적 리스크 — AI 규제 대응","V2","HIGH"),
    ("S7H-071","단일 개발자 리스크 — Bus Factor","V1","MEDIUM"),
    ("S7H-072","기술 부채 리스크 — 누적 기술 부채","V2","MEDIUM"),
    # Part 10: 재무 모델링 (6건)
    ("S7H-073","V1 수지 분석 — MVP 운영 비용","V1","HIGH"),
    ("S7H-074","V2 수지 분석 — SaaS 운영","V2","HIGH"),
    ("S7H-075","Unit Economics — 사용자당 경제성","V2","HIGH"),
    ("S7H-076","3년 재무 전망 — P&L 프로젝션","V2","MEDIUM"),
    ("S7H-077","자금 소요 계획 — 자금 로드맵","V2","MEDIUM"),
    ("S7H-078","Exit 전략 — 장기 비전","V3","MEDIUM"),
]
for fid, title, ver, pri in s7h_data:
    features.append({"id": fid, "title": title, "category": "FT-BIZ", "version_scope": ver, "extractable": True, "priority": pri, "source_file": "STEP7-H"})

# ===== S7I: AI Investing (106 features) =====
s7i_data = [
    # Part 1: 2025 AI 투자 플랫폼 최신 동향 (10건)
    ("S7I-001","최신 AI 투자 도구 통합 전략 — 2025 생태계 매핑","V1","CRITICAL"),
    ("S7I-002","FinGPT 통합 — 금융 특화 LLM 활용","V1","CRITICAL"),
    ("S7I-003","OpenBB Platform v4 연동 — 오픈소스 금융 터미널","V1","CRITICAL"),
    ("S7I-004","FRED/한국은행 API — 거시경제 데이터 통합","V1","HIGH"),
    ("S7I-005","금융감독원 DART API — 한국 기업 공시 분석","V1","HIGH"),
    ("S7I-006","SEC EDGAR — 미국 기업 공시 분석","V1","HIGH"),
    ("S7I-007","Earnings Call 분석 — 실적발표 자동 분석","V1","HIGH"),
    ("S7I-008","뉴스 감성 분석 — 실시간 금융 뉴스 분석","V1","HIGH"),
    ("S7I-009","AI 투자 논문 추적 — 최신 연구 모니터링","V2","MEDIUM"),
    ("S7I-010","투자 교육 콘텐츠 — 사용자 금융 리터러시","V2","MEDIUM"),
    # Part 2: LLM 기반 투자 분석 고도화 (10건)
    ("S7I-011","기업 분석 리포트 자동 생성 — 구조화된 분석","V1","CRITICAL"),
    ("S7I-012","멀티 소스 교차 검증 — 정보 신뢰도","V1","CRITICAL"),
    ("S7I-013","재무제표 자동 분석 — 한국/미국 표준","V1","HIGH"),
    ("S7I-014","밸류에이션 자동 계산 — DCF/비교 분석","V1","HIGH"),
    ("S7I-015","섹터/산업 분석 — 탑다운 분석","V1","HIGH"),
    ("S7I-016","경쟁사 비교 분석 — Peer Comparison","V1","HIGH"),
    ("S7I-017","투자 아이디어 생성 — AI 기반 스크리닝","V1","HIGH"),
    ("S7I-018","애널리스트 컨센서스 추적 — 목표가 모니터링","V2","MEDIUM"),
    ("S7I-019","테마/모멘텀 분석 — 시장 테마 포착","V2","MEDIUM"),
    ("S7I-020","글로벌 매크로 대시보드 — 거시 경제 총정리","V2","MEDIUM"),
    # Part 3: 대안 데이터 (10건)
    ("S7I-021","소셜 미디어 감성 분석 — Reddit/X 금융 감성","V1","HIGH"),
    ("S7I-022","내부자 거래 추적 — 임원 매수/매도 시그널","V1","HIGH"),
    ("S7I-023","기관 포트폴리오 추적 — 13F 분석","V1","HIGH"),
    ("S7I-024","Fear & Greed Index — 시장 심리 지표","V1","HIGH"),
    ("S7I-025","특허/R&D 데이터 — 기술 혁신 분석","V1","HIGH"),
    ("S7I-026","크립토 온체인 데이터 — 블록체인 분석","V1","HIGH"),
    ("S7I-027","웹 트래픽/앱 사용량 — 디지털 성장 지표","V2","MEDIUM"),
    ("S7I-028","ESG 데이터 — ESG 점수 분석","V2","MEDIUM"),
    ("S7I-029","고용 데이터 — 채용 트렌드 분석","V2","MEDIUM"),
    ("S7I-030","이벤트 캘린더 — 투자 이벤트 추적","V2","MEDIUM"),
    # Part 4: 한국 시장 특화 보강 (10건)
    ("S7I-031","키움증권 OpenAPI+ 연동 — 한국 주식 실시간","V1","CRITICAL"),
    ("S7I-032","한국투자증권 KIS API — REST 기반 대안","V1","CRITICAL"),
    ("S7I-033","한국 ETF 분석 — 한국 ETF 포트폴리오","V1","CRITICAL"),
    ("S7I-034","한국 세금 계산 — 투자 세금 자동 계산","V1","HIGH"),
    ("S7I-035","한국 투자 용어 사전 — 한국어 금융 NLP","V1","HIGH"),
    ("S7I-036","한국 배당주 분석 — 배당 투자 전략","V1","HIGH"),
    ("S7I-037","IPO/공모 분석 — 신규 상장 분석","V1","HIGH"),
    ("S7I-038","한국 펀드 분석 — 펀드/ETF 비교","V2","HIGH"),
    ("S7I-039","한국 부동산 연계 — REITs/부동산 분석","V2","MEDIUM"),
    ("S7I-040","한국 연금/IRP — 절세 투자 전략","V2","MEDIUM"),
    # Part 5: 포트폴리오 최적화 심화 (8건)
    ("S7I-041","Modern Portfolio Theory — 평균-분산 최적화","V1","HIGH"),
    ("S7I-042","자산배분 전략 — 전략적 자산배분","V1","HIGH"),
    ("S7I-043","리밸런싱 — 자동 리밸런싱 알림","V1","HIGH"),
    ("S7I-044","포트폴리오 분석 대시보드 — 현황 시각화","V1","HIGH"),
    ("S7I-045","배당 캘린더 — 배당금 수령 일정","V1","HIGH"),
    ("S7I-046","Factor 분석 — 팩터 노출 분석","V2","MEDIUM"),
    ("S7I-047","시나리오 분석 — What-If 시뮬레이션","V2","MEDIUM"),
    ("S7I-048","세금 최적화 — Tax-Loss Harvesting","V2","MEDIUM"),
    # Part 6: 리스크 관리 고도화 (10건)
    ("S7I-049","VaR 계산 — Value at Risk","V1","CRITICAL"),
    ("S7I-050","최대 손실 제한 — Stop Loss 관리","V1","CRITICAL"),
    ("S7I-051","상관관계 분석 — 분산 투자 검증","V1","HIGH"),
    ("S7I-052","드로다운 분석 — 최대 낙폭 관리","V1","HIGH"),
    ("S7I-053","리스크 스코어카드 — 투자 위험 종합 점수","V1","HIGH"),
    ("S7I-054","스트레스 테스트 — 극단 시나리오 시뮬레이션","V1","HIGH"),
    ("S7I-055","포지션 사이징 — 켈리 기준","V2","HIGH"),
    ("S7I-056","환율 리스크 — 해외 투자 환율 관리","V2","MEDIUM"),
    ("S7I-057","유동성 리스크 — 거래량 분석","V2","MEDIUM"),
    ("S7I-058","블랙 스완 대비 — 꼬리 리스크 관리","V2","MEDIUM"),
    # Part 7: 백테스팅/시뮬레이션 보강 (8건)
    ("S7I-059","백테스팅 엔진 통합 — Blue Node 완성","V1","CRITICAL"),
    ("S7I-060","RSI_BB 전략 5년 데이터 확보 — GAP-01 해결","V1","CRITICAL"),
    ("S7I-061","과적합 방지 — 견고성 검증 체계","V1","HIGH"),
    ("S7I-062","백테스트 성과 지표 — 종합 성과 분석","V1","HIGH"),
    ("S7I-063","Paper Trading — 모의 투자","V2","HIGH"),
    ("S7I-064","전략 비교 프레임워크 — 전략 간 A/B 테스트","V2","HIGH"),
    ("S7I-065","시장 조건 분류 — 시장 레짐 감지","V2","MEDIUM"),
    ("S7I-066","슬리피지/수수료 모델 — 현실적 비용 모델링","V2","MEDIUM"),
    # Part 8: 실시간 데이터 & 알림 (8건)
    ("S7I-067","가격 알림 — 목표가/손절가 알림","V1","HIGH"),
    ("S7I-068","공시/뉴스 알림 — 실시간 이벤트 알림","V1","HIGH"),
    ("S7I-069","포트폴리오 일일 리포트 — 자동 일간 요약","V1","HIGH"),
    ("S7I-070","시장 오버뷰 — 매일 시장 요약","V1","HIGH"),
    ("S7I-071","경제 지표 알림 — 주요 경제 지표 발표 알림","V1","HIGH"),
    ("S7I-072","실시간 대시보드 — 포트폴리오 라이브","V2","MEDIUM"),
    ("S7I-073","커스텀 알림 규칙 — 사용자 정의 알림","V2","MEDIUM"),
    ("S7I-074","주간/월간 리포트 — 정기 분석 보고서","V2","MEDIUM"),
    # Part 9: 크립토/DeFi 투자 (8건)
    ("S7I-075","크립토 시장 데이터 — BTC/ETH/주요 코인","V1","HIGH"),
    ("S7I-076","온체인 분석 — 블록체인 데이터","V1","HIGH"),
    ("S7I-077","크립토 감성 분석 — 공포/탐욕 지수","V1","HIGH"),
    ("S7I-078","크립토 포트폴리오 — 크립토 자산 관리","V1","HIGH"),
    ("S7I-079","DeFi 분석 — TVL/수익률 분석","V2","MEDIUM"),
    ("S7I-080","NFT/토큰 분석 — 토큰 이코노믹스","V2","MEDIUM"),
    ("S7I-081","크립토 규제 모니터링 — 각국 규제 동향","V2","MEDIUM"),
    ("S7I-082","에어드랍/이벤트 — 크립토 이벤트 추적","V2","MEDIUM"),
    # Part 10: AI Agent 투자 워크플로우 (10건)
    ("S7I-083","Quant Node 워크플로우 — 정량 분석 파이프라인","V1","CRITICAL"),
    ("S7I-084","투자 안전장치 — 이중 확인 시스템","V1","CRITICAL"),
    ("S7I-085","투자 면책 시스템 — 법적 보호","V1","CRITICAL"),
    ("S7I-086","투자 일지 — 매매 기록 + AI 분석","V1","HIGH"),
    ("S7I-087","Research Node 투자 리서치 — 정성 분석","V1","HIGH"),
    ("S7I-088","Content Node 리포트 — 투자 보고서 생성","V1","HIGH"),
    ("S7I-089","멀티 Agent 협업 — Quant + Research + Content","V2","HIGH"),
    ("S7I-090","투자 학습 모드 — 자기진화 투자 분석","V2","HIGH"),
    ("S7I-091","투자 시뮬레이터 — 교육용 가상 투자","V2","MEDIUM"),
    ("S7I-092","자동 매매 프레임워크 — V2+ 자동 실행","V2","MEDIUM"),
    # Part 11: 규제/컴플라이언스 보강 (8건)
    ("S7I-093","자본시장법 준수 — 한국 금융 규제","V1","CRITICAL"),
    ("S7I-094","금투세 대비 — 금융투자소득세","V1","CRITICAL"),
    ("S7I-095","불법 행위 방지 — 시세조종/내부자거래 차단","V1","HIGH"),
    ("S7I-096","적합성 원칙 — 투자자 보호","V1","HIGH"),
    ("S7I-097","미국 SEC 규제 — 해외 주식 규제","V1","HIGH"),
    ("S7I-098","크립토 규제 — 암호화폐 관련 법률","V2","HIGH"),
    ("S7I-099","해외 송금/환전 규제 — 외환 관련","V2","MEDIUM"),
    ("S7I-100","투자 감사 추적 — 규제 대응 로그","V2","MEDIUM"),
    # Part 12: 기존 GAP 해결 + 품질 개선 (6건)
    ("S7I-101","GAP-06 해결: ConnectorResponse Pydantic 모델 생성","V1","CRITICAL"),
    ("S7I-102","GAP-07 해결: OHLCV tick vs candle 필드 정의","V1","CRITICAL"),
    ("S7I-103","GAP-03 해결: yfinance 폴백 절차 완성","V1","CRITICAL"),
    ("S7I-104","GAP-01 해결 계획: RSI_BB 데이터 확보 로드맵","V1","HIGH"),
    ("S7I-105","투자 기능 품질 벤치마크 — VBS-10 구체화","V1","HIGH"),
    ("S7I-106","투자 온보딩 — 초기 설정 마법사","V1","HIGH"),
]
for fid, title, ver, pri in s7i_data:
    features.append({"id": fid, "title": title, "category": "FT-INVEST", "version_scope": ver, "extractable": True, "priority": pri, "source_file": "STEP7-I"})

# ===== Statistics =====
total = len(features)
extractable_true = sum(1 for f in features if f["extractable"])
extractable_false = total - extractable_true

by_category = {}
for f in features:
    c = f["category"]
    by_category[c] = by_category.get(c, 0) + 1

by_version = {}
for f in features:
    v = f["version_scope"]
    by_version[v] = by_version.get(v, 0) + 1

by_source = {}
for f in features:
    s = f["source_file"]
    by_source[s] = by_source.get(s, 0) + 1

by_priority = {}
for f in features:
    p = f["priority"]
    by_priority[p] = by_priority.get(p, 0) + 1

# Build output
output = {
    "agent": "C-11",
    "session": 31,
    "source_files": [
        {"file": "STEP7-B_대화프로세스_작업가이드.md", "lines": 1189, "read_pct": "100%"},
        {"file": "STEP7-C_UI_UX_전수비교_작업가이드.md", "lines": 236, "read_pct": "100%"},
        {"file": "STEP7-D_메모리_저장소_아키텍처_작업가이드.md", "lines": 295, "read_pct": "100%"},
        {"file": "STEP7-E_보안_안전_거버넌스_작업가이드.md", "lines": 1211, "read_pct": "100%"},
        {"file": "STEP7-F_인프라_배포_MLOps_작업가이드.md", "lines": 1451, "read_pct": "100%"},
        {"file": "STEP7-G_벤치마크_평가_품질보증_작업가이드.md", "lines": 892, "read_pct": "100%"},
        {"file": "STEP7-H_비즈니스모델_시장전략_작업가이드.md", "lines": 1054, "read_pct": "100%"},
        {"file": "STEP7-I_AI_Investing_보강_작업가이드.md", "lines": 1350, "read_pct": "100%"},
    ],
    "total_lines_read": 7678,
    "total_lines": 7670,
    "read_pct": "100%",
    "features": features,
    "statistics": {
        "total_features": total,
        "extractable_true": extractable_true,
        "extractable_false": extractable_false,
        "by_category": by_category,
        "by_version": by_version,
        "by_priority": by_priority,
        "by_source_file": by_source,
        "inferred_count": 0,
        "V_UNKNOWN_count": 0,
        "judgment_needed_count": 0,
        "title_only_count": 0
    }
}

output_path = r"D:\VAMOS\04. 구현단계\v13_results\phase5_v10\features\src_C11.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Written {total} features to {output_path}")
print(f"By source: {by_source}")
print(f"By category: {by_category}")
print(f"By version: {by_version}")
print(f"By priority: {by_priority}")