#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""3-2 SUB_FEATURE 45건 판정 사유 업데이트
키워드 매칭 → 실제 아키텍처 관계 분석 기반 사유로 교체
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

sf_path = r"D:\VAMOS\04. 구현단계\v10_results\phase2\step1\3-2_SUB_FEATURE_OF_EXISTING.md"

# 항목별 개선된 판정 사유 매핑
UPDATED_REASONS = {
    # === HIGH: module_id_exact (이미 양호하지만 통일) ===
    "CLAUDE-089": "PART2 L2584에 EVX-1 (evx01_code_as_policy.py) 파일명+기능 '코드 생성→정책 자동 적용' 완전 정의. MASTER_SPEC §7.3에서 Verify-phase 하위 컴포넌트로 아키텍처 확정. 독립 구현 항목이 아닌 G3 Quality Gate 검증 체인의 일부",
    "CLAUDE-090": "PART2 L2585에 EVX-2 (evx02_adversarial.py) 파일명+기능 '적대적 입력 자동 생성+견고성 테스트' 완전 정의. MASTER_SPEC §7.3에서 Verify-phase 하위 컴포넌트로 확정",
    "CLAUDE-091": "PART2 L2586에 EVX-3 (evx03_logprob.py) 파일명+기능 'LLM 로그 확률 분석→불확실성 측정' 완전 정의. Verify-phase 하위 컴포넌트",
    "CLAUDE-092": "PART2 L2587에 EVX-4 (evx04_thought_debug.py) 파일명+기능 '추론 체인 시각화/디버깅' 완전 정의. Verify-phase 하위 컴포넌트",
    "CLAUDE-093": "PART2 L2588에 EVX-5 (evx05_synthetic_data.py) 파일명+기능 '합성 학습 데이터 생성' 완전 정의. Verify-phase 하위 컴포넌트",
    "D202-073": "PART2 L2438에 모듈 ID 'I-18' 직접 등재. V2 그룹5 (I-13~I-19 고급 인텔리전스)의 하위 모듈로, 상위 모듈 아키텍처 내에서 구현 범위가 명확히 지정됨",
    "TEAM-103": "PART2 L2438에 모듈 ID 'I-18' 직접 등재. TEAM-103은 팀 실행 패턴을 I-18에 연동하는 것으로, I-18 모듈 구현(D202-073)에 종속. 별도 모듈이 아닌 연동 작업",

    # === HIGH: 키워드 매칭 → 아키텍처 분석 ===
    "D202-085": "PART2 L823-828 I-5 Condition & Decision Engine 내 4개 Gate 중 하나로 'EvidenceGate: 스텁 (항상 sufficient)' 명시. V0에서 스텁, V1에서 I-6 Self-check 연동 예정. I-5 모듈 구현 시 함께 구현되는 하위 컴포넌트",
    "D202-087": "PART2 L910에 'SelfCheckGate (M-14) V0 스텁' 명시. I-5 Gate 시스템의 자체 품질 검증 컴포넌트로, V0 스텁 → V1 활성화 로드맵이 PART2 내 정의. 독립 모듈이 아닌 Gate 아키텍처 일부",
    "D202-094": "PART2 L475-481 레지스트리 테이블에 ToolRegistry(2 seed entries, D2.1-D4 정본) 명시. 5개 레지스트리(Event/Failure/Fallback/Tool/Node) 통합 시스템의 일부로, registries.py에서 일괄 관리되는 구조",
    "D204-021": "PART2 L1410에 'Multimodal Interpreter 텍스트/이미지/음성' 모듈 정의, L2728에 V3 '멀티모달 고급 (3D 생성, 비디오)' 로드맵 명시. GPT-4o/Gemini 네이티브 활용은 이 모듈의 V2 확장 구현",
    "D204-026": "PART2 L2292에 'vLLM 셀프호스팅 A10G GPU' 인프라 명시, L2632에 EVX 의존성으로 torch 등 GPU 패키지 정의. vLLM/PagedAttention은 V2 GPU 서빙 인프라의 핵심 구현이며 PART2 V2-Phase 2에 포함",
    "D204-042": "PART2 L480 ToolRegistry + L823-828 I-5 Gate 시스템 양쪽에 정의. '04→07 Gate 연결'은 두 PART2 컴포넌트(ToolRegistry, 3-Gate) 사이의 내부 연동 규칙이며 독립 기능이 아닌 아키텍처 통합 작업",
    "D206-087": "STEP7-D S7D-060 (Self-RAG 루프)의 하위 구현. PART2 L1400-1417 RAG 파이프라인(BGE-M3 임베딩 → I-16 Knowledge Search) 내에서 Self-RAG는 품질 자기 평가 루프로 통합. S7D-060이 상위 스펙",
    "D206-128": "STEP7-D S7D-060과 동일 대상 (Self-RAG 루프 구현). D206-087과 같은 기능의 다른 출처 항목으로, PART2 RAG 파이프라인(L1400-1417) + S7D-060에 종속",
    "D207-056": "PART2 L910 SelfCheckGate (M-14)의 구체적 구현 임곗값 정의. P0≥70/P1≥75/P2≥80은 이 Gate의 파라미터 설정이며, Gate 모듈 구현 시 포함되는 설정값",
    "S7AE-376": "PART2 L2554에 '인증 프로토콜: mTLS + JWT (DEFER-AT-004 해결 후)' 명시. JWT 토큰 관리는 A-6 Federated 모듈 인증 프로토콜의 하위 구현으로, 독립 인증 시스템이 아닌 mTLS+JWT 통합 인증의 일부",
    "S7BG-014": "PART2 L2452에 'PARL Agent Swarm 오케스트레이션' 명시 — 최대 100 동시 서브에이전트, 1500 협업 스텝. Swarm 패턴은 이 PARL Agent 아키텍처의 구현 방식으로 이미 상위 모듈에 포함",
    "S7BG-024": "PART2 L2429에 'HPA CPU 70% 자동 스케일링' 명시. V2 인프라 스케일링 정책으로 PART2 V2-Phase 2 인프라 항목에 포함. STEP7-F에서는 키워드 수준 언급만 있고 독립 스펙 없음",
    "S7FI-069": "PART2 L473-481 레지스트리 테이블에 5개 레지스트리 정의 (registries.py 파일). '모델 레지스트리'는 이 통합 레지스트리 시스템의 확장이며, STEP7-F에서도 독립 스펙 미존재",
    "S7FI-081": "PART2 L2317에 '도메인/SSL/DNS 설정' 인프라 항목으로 포함. DNS 관리는 V2 도메인 설정 작업의 일부이며, STEP7-F에서도 L627/L1326에 키워드 수준 언급만 존재 (독립 스펙 없음)",
    "S7FI-357": "PART2 L916에 '개인정보 수집 PolicyGate' 명시. 개인정보 보호는 I-5 Gate 시스템의 PolicyGate가 담당하며, PII 탐지/마스킹은 STEP7-E S7E-031에서 별도 관리하되 PART2 Gate 아키텍처에 종속",
    "S7JM-253": "PART2 L1400-1417에 RAG 파이프라인 아키텍처 정의 (BGE-M3 임베딩 → I-16 Knowledge Search → 검색 결과 통합). 'RAG 최적화'는 이 파이프라인의 성능 튜닝으로 독립 모듈이 아님",
    "S7NP-008": "STEP7-N 작업가이드 N-003 (Workflow Trigger System)에서 'cron 스케줄 (매일/매주/매월)' 포함 확인. 스케줄러는 워크플로우 트리거 시스템의 시간 기반 트리거 유형이며 독립 모듈이 아님",
    "S7NP-204": "PART2 전체 아키텍처가 로컬 우선 설계 (Ollama 로컬 배포, L2555 원본 데이터 전송 금지, L2554 mTLS). '로컬 우선 프라이버시'는 독립 기능이 아닌 아키텍처 설계 원칙으로, PART2 전반에 내재",
    "SDAR-051": "PART2 L2007에 'SDAR 자가진단/자동수리 엔진 AR-L3' 명시. NEVER_AUTO 차단 규칙은 이 SDAR 엔진의 안전 제약조건으로, 엔진 구현 시 포함되는 보호 로직 (L739 '하드코딩' 매칭은 우연 — 실제 근거는 SDAR 모듈 종속)",
    "SDAR-083": "PART2 L2007 SDAR 엔진의 안전 규칙 구현. NEVER_AUTO_TARGETS frozenset은 수리 대상 검증 로직으로 SDAR 모듈 내부 구현. 판정 근거는 SDAR 모듈 종속 (기존 '하드코딩' 키워드 매칭은 우연적 일치였음)",

    # === MEDIUM: module_id_exact ===
    "CLAUDE-239": "PART2 L2584-2589에 EVX-1~6 모듈 전체가 파일명+기능과 함께 등재. VerifyChainRegistry는 이 6개 모듈을 레지스트리로 관리하는 구조체로, EVX 모듈 시스템의 부속 정의",
    "DD5-010": "CLAUDE-239와 동일 대상 (VerifyChainRegistry). PART2 L2584 EVX 모듈 + MASTER_SPEC L614 'VerifyChainRegistry: EVX-1~EVX-6' 정의. JSON 형식 명세는 이 레지스트리의 직렬화 포맷 결정",

    # === MEDIUM: 키워드 매칭 → 아키텍처 분석 ===
    "CLAUDE-238": "PART2 L481에 'NodeRegistry 1 seed entry (D2.1-D3 정본)' 명시. 5개 레지스트리(Event/Failure/Fallback/Tool/Node) 통합 시스템의 일부로 registries.py에서 관리. domain_name 기반 구현은 이 시스템의 세부 구현",
    "D203-025": "PART2 L94에 'mcp/' 디렉토리로 MCP 브릿지 서브시스템 정의. Inspector/Playground/로그뷰어는 이 MCP 서브시스템의 개발 도구로, STEP7-K에서도 독립 스펙 미확인. MCP 브릿지 구현에 부속",
    "D206-006": "STEP7-D S7D-038 (L3 장기 메모리)에 포함. PART2 메모리 계층 아키텍처 (L1→L2→L3→L4)에서 L2 Long-term Knowledge는 이 계층 구조의 한 레이어로 독립 모듈이 아닌 메모리 시스템 하위 구현",
    "D206-022": "STEP7-D S7D-041 (메모리 강등/삭제 알고리즘)에 포함. L3 Procedural 폐기/롤백은 메모리 라이프사이클 관리의 일부로, S7D-041 메모리 정리 알고리즘 구현 시 함께 처리",
    "D206-139": "STEP7-D S7D-064 (RAG 품질 자동 평가 — RAGAS 메트릭)와 동일 대상. S7D-064가 상위 스펙이며, PART2 RAG 파이프라인(L1400)의 품질 보증 컴포넌트로 파이프라인에 종속",
    "D207-049": "PART2에 버전별 비용 상한 광범위 명시: V1 ₩40K/월(L1388,L1755), V2 ₩93K/월(L1763,L1905,L2110), V3 ₩266K/월(L2282,L2319). 비용 관리는 PART2 CostGate(L825) + 비용 모니터링(L2110) 시스템에 통합",
    "PB4-003": "PART2 L1018에 'config.v1.toml → Pydantic ConfigModel' 통합 config 로더 정의. [core] 섹션은 이 통합 ConfigModel의 하위 섹션으로, config.v1.toml 파일 구조에 종속되는 구현 단위",
    "PB4-004": "PB4-003과 동일 근거. [llm] 섹션은 config.v1.toml 통합 ConfigModel의 하위 섹션. PART2 L1029에서 'LOCK 값이 ConfigModel로 정확히 로드되는지 확인' 검증 포함",
    "PB4-006": "PB4-003과 동일 근거. [vector_db]+[graph_db] 섹션은 config.v1.toml 통합 ConfigModel의 하위 섹션. 단일 Pydantic 모델 내 DB 연결 설정",
    "PB4-009": "PB4-003과 동일 근거. [mcp] 섹션은 config.v1.toml 통합 ConfigModel의 하위 섹션. streamable_http LOCK 값은 PART2 설정 체계 내 MCP 전송 프로토콜 고정값",
    "PB6-013": "PART2 L1193에 'GitHub Actions 시크릿 설정' 명시. 14개 시크릿 등록은 CI/CD 파이프라인 구축(PART2 V1-Phase 1)의 환경 설정 작업으로, 독립 기능이 아닌 배포 파이프라인 세팅의 일부",
    "S7AE-359": "PART2 L2813-2819에 A2A Protocol 정의, L2817에 '디스커버리: mDNS/DNS-SD 기반 에이전트 발견' 명시. 서비스 디스커버리는 V3 A2A 프로토콜의 하위 컴포넌트로 프로토콜 구현에 종속",
    "S7AE-558": "PART2 L1343에 Docker Compose 기반 services 정의, V2에서 K8s 전환 예정. 컨테이너 오케스트레이션은 PART2 인프라 스택(Docker→K8s)의 운영 계층으로, STEP7-F S7F-031(K8s)/S7F-037-043(Docker) 범위에 포함",
    "S7AE-569": "PART2 L2312에 'GPU 노드 프로비저닝 A10G' 명시. 환경 프로비저닝은 V2 인프라 확장 작업의 일부로, GPU 노드 + 클라우드 환경 셋업이 PART2 배포 계획에 포함",
    "TEAM-022": "PART2 L2007에 'SDAR 자가진단/자동수리 엔진 AR-L3' 모듈 명시. SDARAgent는 이 SDAR 엔진을 에이전트로 래핑한 것으로, SDAR 모듈 구현의 인터페이스 계층",
    "TEAM-024": "PART2 L2027에 '알림/리마인더 설정' 기능 명시. ProductivityAgent(일정관리/리마인더/노트)는 이 알림 시스템과 Sub-Agent↔BLUE NODE 매핑 테이블의 구현체로, 에이전트 프레임워크 내 역할 배정",
}

with open(sf_path, "r", encoding="utf-8") as f:
    content = f.read()

update_count = 0
for item_id, new_reason in UPDATED_REASONS.items():
    # 패턴: "- **판정 사유**: ..." 뒤에 빈 줄 또는 ---까지
    pattern = rf'(### {re.escape(item_id)}\n.*?- \*\*판정 사유\*\*: )(.+?)(\n)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        old_reason = match.group(2)
        if old_reason.strip() != new_reason.strip():
            content = content[:match.start(2)] + new_reason + content[match.end(2):]
            update_count += 1
            print(f"✅ {item_id}: 판정 사유 업데이트")
        else:
            print(f"⏭️ {item_id}: 이미 동일")
    else:
        print(f"⚠️ {item_id}: 패턴 미발견")

with open(sf_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n=== 완료: {update_count}건 판정 사유 업데이트 ===")
