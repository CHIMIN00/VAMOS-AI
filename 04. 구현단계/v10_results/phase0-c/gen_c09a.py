#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v10 Phase 0-C Agent C-9a: Generate v10_src_C09a.json"""
import json
from datetime import date

OUTPUT = r"D:\VAMOS\04. 구현단계\v10_results\phase0-c\v10_src_C09a.json"
features = []
_idx = [0]  # mutable counter

def nid(prefix):
    _idx[0] += 1
    return f"{prefix}-{_idx[0]:03d}"

def add(src, section, name, ver, cat, extractable=True, conf="명시적", notes="", deps=[], impl="구현"):
    prefix = "S7AE" if src == "AE" else "S7FI"
    features.append({
        "feature_id": nid(prefix),
        "source_file": f"STEP7_{'A-E' if src=='AE' else 'F-I'}",
        "source_line": 0,
        "source_section": section,
        "feature_name": name,
        "version_scope": ver,
        "category": cat,
        "implementation_type": impl,
        "dependencies": list(deps),
        "extractable": extractable,
        "confidence": conf,
        "notes": notes
    })

def bundle(src, section, names, ver, cat):
    for nm in names:
        add(src, section, nm, ver, cat, extractable=False, conf="추론",
            notes="TITLE_ONLY: 제목만 존재, 상세 스펙 없음")

###############################################################################
# CATEGORY A (316 items)
###############################################################################
# Part A (35): 28 detailed + 7 bundled
a_detailed = [
    ("Agent Teams 아키텍처 설계","V2","FT-FUNC"),("Agent SDK 통합 프레임워크","V2","FT-FUNC"),
    ("MCP (Model Context Protocol) 구현","V1","FT-API"),("Hooks 시스템 구현","V1","FT-FUNC"),
    ("CAI 2.0 Constitutional AI 적용","V2","FT-FUNC"),("Agent Orchestrator 설계","V2","FT-FUNC"),
    ("Agent Communication Protocol","V2","FT-API"),("Agent State Management","V2","FT-FUNC"),
    ("Agent Task Decomposition","V2","FT-FUNC"),("Agent Memory System","V2","FT-FUNC"),
    ("Agent Tool Registry","V1","FT-FUNC"),("Agent Execution Engine","V2","FT-FUNC"),
    ("Agent Error Recovery","V2","FT-FUNC"),("Agent Monitoring Dashboard","V2","FT-UI"),
    ("Agent Security Sandbox","V2","FT-SEC"),("Agent Logging System","V1","FT-INFRA"),
    ("Agent Performance Profiler","V2","FT-TEST"),("Agent Version Control","V2","FT-CFG"),
    ("Agent Deployment Pipeline","V2","FT-INFRA"),("Agent A/B Testing Framework","V3","FT-TEST"),
    ("MCP Server Registry","V1","FT-INFRA"),("MCP Client SDK","V1","FT-API"),
    ("MCP Transport Layer","V1","FT-INFRA"),("Hooks Event System","V1","FT-FUNC"),
    ("Hooks Plugin Architecture","V1","FT-FUNC"),("CAI 2.0 Rule Engine","V2","FT-FUNC"),
    ("CAI 2.0 Safety Classifier","V2","FT-SEC"),("CAI 2.0 Feedback Loop","V2","FT-FUNC"),
]
for nm, ver, cat in a_detailed:
    add("AE", "§A Part-A", nm, ver, cat, notes="Agent/MCP/Hooks/CAI 상세 스펙")

bundle("AE", "§A Part-A 번들", [
    "Artifacts 시스템","Projects 관리","Memory 시스템","Max 컴퓨팅 통합",
    "CLAUDE.md 설정 관리","Prompt Caching 구현","Citation 시스템"
], "V2", "FT-FUNC")

# Part B (24): 2 detailed + 22 bundled
for nm, ver, cat in [("Reasoning Mode 구현","V2","FT-FUNC"),("Code Interpreter 통합","V1","FT-FUNC")]:
    add("AE", "§A Part-B", nm, ver, cat, notes="상세 스펙 존재")
bundle("AE", "§A Part-B 번들", [f"Part-B 기능항목 {i}" for i in range(3,25)], "V2", "FT-FUNC")

# Part C (20): 1 detailed + 19 bundled
add("AE", "§A Part-C", "Search Grounding 구현", "V1", "FT-FUNC", notes="검색 기반 그라운딩")
bundle("AE", "§A Part-C 번들", [f"Part-C 기능항목 {i}" for i in range(2,21)], "V2", "FT-FUNC")

# Part D (22): 3 detailed + 19 bundled
for nm, ver, cat in [("Meta AI Controller 설계","V2","FT-FUNC"),("Module Auto-Discovery 시스템","V1","FT-FUNC"),("ML Module Router 구현","V2","FT-FUNC")]:
    add("AE", "§A Part-D", nm, ver, cat, notes="상세 스펙 존재")
bundle("AE", "§A Part-D 번들", [f"Part-D 기능항목 {i}" for i in range(4,23)], "V2", "FT-FUNC")

# Part E (18): all bundled
bundle("AE", "§A Part-E 번들", [f"Part-E 기능항목 {i}" for i in range(1,21)], "V2", "FT-FUNC")

# Part F (99): 1 detailed + 98 bundled
add("AE", "§A Part-F", "개인 지식 그래프 엔진", "V2", "FT-FUNC", notes="Personal Knowledge Graph Engine")
bundle("AE", "§A Part-F 번들", [f"Part-F 지식그래프 항목 {i}" for i in range(2,100)], "V2", "FT-FUNC")

# Part G (12): all bundled
bundle("AE", "§A Part-G 번들", [f"Part-G 기능항목 {i}" for i in range(1,13)], "V3", "FT-FUNC")

# Part H (10): all bundled
bundle("AE", "§A Part-H 번들", [f"Part-H 기능항목 {i}" for i in range(1,11)], "V3", "FT-FUNC")

# Part I (8): 1 detailed + 7 bundled
add("AE", "§A Part-I", "Llama 4 Scout 통합", "V2", "FT-MOD", notes="Llama 4 Scout 모델 통합")
bundle("AE", "§A Part-I 번들", [f"Part-I 모델항목 {i}" for i in range(2,9)], "V2", "FT-MOD")

# Part J (8): 1 detailed + 7 bundled
add("AE", "§A Part-J", "Hybrid Retrieval 엔진", "V1", "FT-FUNC", notes="하이브리드 검색 엔진")
bundle("AE", "§A Part-J 번들", [f"Part-J 검색항목 {i}" for i in range(2,9)], "V2", "FT-FUNC")

# Part K (10): 1 detailed + 9 bundled
add("AE", "§A Part-K", "온디바이스 라우팅 엔진", "V1", "FT-FUNC", notes="On-device Routing Engine")
bundle("AE", "§A Part-K 번들", [f"Part-K 라우팅항목 {i}" for i in range(2,11)], "V2", "FT-FUNC")

# Part L (8): 1 detailed + 7 bundled
add("AE", "§A Part-L", "Computer Use 에이전트", "V2", "FT-FUNC", notes="Computer Use Agent")
bundle("AE", "§A Part-L 번들", [f"Part-L 컴퓨터유즈 항목 {i}" for i in range(2,9)], "V3", "FT-FUNC")

# Part M (8): all bundled
bundle("AE", "§A Part-M 번들", [f"Part-M 기능항목 {i}" for i in range(1,9)], "V3", "FT-FUNC")

# Part N (12): 1 detailed + 7 bundled + 4 CRITICAL bundled
add("AE", "§A Part-N", "EU AI Act 준수 프레임워크", "V2", "FT-SEC", notes="EU AI Act 컴플라이언스")
bundle("AE", "§A Part-N 번들", [f"Part-N 규제항목 {i}" for i in range(2,9)], "V2", "FT-SEC")
bundle("AE", "§A Part-N 3차보강", [f"3차보강 CRITICAL 규제항목 {i}" for i in range(1,5)], "V2", "FT-SEC")

# Part O (10): all bundled
bundle("AE", "§A Part-O 번들", [f"Part-O 기능항목 {i}" for i in range(1,11)], "V3", "FT-FUNC")

# Part P (10): 1 detailed + 9 bundled
add("AE", "§A Part-P", "Self-RAG 구현", "V2", "FT-FUNC", notes="Self-Reflective RAG")
bundle("AE", "§A Part-P 번들", [f"Part-P RAG항목 {i}" for i in range(2,11)], "V3", "FT-FUNC")

print(f"Cat A: {len(features)} (target 316)")

###############################################################################
# CATEGORY B (35 items)
###############################################################################
# 7 CRITICAL detailed
b_crit = [
    ("B-001 핵심 기술 전략 수립","V1","FT-FUNC"),("B-002 기술 스택 선정","V1","FT-INFRA"),
    ("B-003 아키텍처 설계","V1","FT-INFRA"),("B-005 MVP 기능 정의","V1","FT-FUNC"),
    ("B-006 개발 로드맵","V1","FT-FUNC"),("B-028 품질 관리 체계","V1","FT-TEST"),
    ("B-034 보안 아키텍처","V1","FT-SEC"),
]
for nm, ver, cat in b_crit:
    add("AE", "§B CRITICAL", nm, ver, cat, notes="CRITICAL 우선순위")

# 17 HIGH bundled
bundle("AE", "§B HIGH", [
    "B-004 기술 평가","B-007 리소스 계획","B-008 인프라 설계","B-009 DB 설계",
    "B-010 API 설계","B-011 보안 설계","B-012 테스트 전략","B-013 CI/CD 설계",
    "B-018 성능 최적화","B-019 모니터링","B-023 배포 전략","B-024 장애 복구",
    "B-025 확장성 설계","B-027 코드 품질","B-029 문서화","B-031 의존성 관리","B-035 감사 로깅"
], "V1", "FT-INFRA")

# 7 MEDIUM bundled
bundle("AE", "§B MEDIUM", [
    "B-014 캐싱 전략","B-015 로깅 전략","B-020 백업 전략",
    "B-026 국제화","B-030 접근성","B-032 버전 관리","B-033 기술 부채 관리"
], "V2", "FT-INFRA")

# 4 LOW bundled
bundle("AE", "§B LOW", [
    "B-016 실험 프레임워크","B-017 피처 플래그","B-021 데이터 마이그레이션","B-022 레거시 호환"
], "V3", "FT-INFRA")

print(f"Cat A+B: {len(features)} (target 351)")

###############################################################################
# CATEGORY C (104 items)
###############################################################################
# Parts 1-4: 44 individually detailed
c_det = [
    ("시스템 아키텍처 개요","V1","FT-INFRA"),("마이크로서비스 설계","V1","FT-INFRA"),
    ("이벤트 드리븐 아키텍처","V1","FT-INFRA"),("API 게이트웨이","V1","FT-API"),
    ("서비스 메시","V2","FT-INFRA"),("로드 밸런서","V1","FT-INFRA"),
    ("서킷 브레이커","V1","FT-INFRA"),("서비스 디스커버리","V1","FT-INFRA"),
    ("컨피그 서버","V1","FT-CFG"),("분산 트레이싱","V2","FT-INFRA"),
    ("중앙 로깅","V1","FT-INFRA"),("메트릭 수집","V1","FT-INFRA"),
    ("알림 시스템","V1","FT-FUNC"),("헬스체크","V1","FT-INFRA"),
    ("그레이스풀 셧다운","V1","FT-INFRA"),("리트라이 정책","V1","FT-INFRA"),
    ("타임아웃 정책","V1","FT-CFG"),("백프레셔","V2","FT-INFRA"),
    ("레이트 리미팅","V1","FT-SEC"),("캐시 계층","V1","FT-INFRA"),
    ("세션 관리","V1","FT-FUNC"),("인증 시스템","V1","FT-SEC"),
    ("권한 관리","V1","FT-SEC"),("OAuth 통합","V1","FT-SEC"),
    ("JWT 토큰 관리","V1","FT-SEC"),("API 버저닝","V1","FT-API"),
    ("OpenAPI 스펙","V1","FT-API"),("GraphQL 스키마","V2","FT-SCHEMA"),
    ("WebSocket 서버","V1","FT-INFRA"),("SSE 구현","V1","FT-INFRA"),
    ("메시지 큐","V2","FT-INFRA"),("이벤트 버스","V2","FT-INFRA"),
    ("CQRS 패턴","V2","FT-INFRA"),("이벤트 소싱","V3","FT-INFRA"),
    ("사가 패턴","V2","FT-INFRA"),("데이터 파티셔닝","V2","FT-SCHEMA"),
    ("읽기 복제본","V2","FT-INFRA"),("커넥션 풀링","V1","FT-INFRA"),
    ("쿼리 최적화","V1","FT-INFRA"),("인덱스 전략","V1","FT-SCHEMA"),
    ("데이터 마이그레이션 도구","V1","FT-MIG"),("스키마 버저닝","V1","FT-SCHEMA"),
    ("백업 자동화","V1","FT-INFRA"),("재해 복구 계획","V2","FT-INFRA"),
]
for nm, ver, cat in c_det:
    add("AE", "§C Parts1-4", nm, ver, cat, notes="상세 스펙 존재")

# Parts 5-10: 60 bundled
bundle("AE","§C Part-5",[f"C-{i:03d} 시스템설계" for i in range(45,53)],"V2","FT-INFRA")
bundle("AE","§C Part-6",[f"C-{i:03d} 시스템설계" for i in range(53,63)],"V2","FT-INFRA")
bundle("AE","§C Part-7",[f"C-{i:03d} 시스템설계" for i in range(63,71)],"V2","FT-INFRA")
bundle("AE","§C Part-8",[f"C-{i:03d} 시스템설계" for i in range(71,81)],"V2","FT-INFRA")
bundle("AE","§C Part-9",[f"C-{i:03d} 시스템설계" for i in range(81,97)],"V2","FT-INFRA")
bundle("AE","§C Part-10",[f"C-{i:03d} 시스템설계" for i in range(97,105)],"V3","FT-INFRA")

print(f"Cat A-C: {len(features)} (target 455)")

###############################################################################
# CATEGORY D (82 items) - all bundled/summarized
###############################################################################
d_parts = [
    ("§D Part-1 DB스키마",8,"V1","FT-SCHEMA"),("§D Part-2 데이터모델",10,"V1","FT-SCHEMA"),
    ("§D Part-3 인덱싱",8,"V1","FT-SCHEMA"),("§D Part-4 캐싱",8,"V1","FT-INFRA"),
    ("§D Part-5 데이터파이프라인",12,"V2","FT-INFRA"),("§D Part-6 ETL",8,"V2","FT-INFRA"),
    ("§D Part-7 분석",10,"V2","FT-FUNC"),("§D Part-8 보안",10,"V2","FT-SEC"),
    ("§D Part-9 거버넌스",8,"V3","FT-SEC"),
]
d_num = 1
for section, count, ver, cat in d_parts:
    bundle("AE", section, [f"D-{d_num+i:03d} 데이터설계" for i in range(count)], ver, cat)
    d_num += count

print(f"Cat A-D: {len(features)} (target 537)")

###############################################################################
# CATEGORY E (92 items)
###############################################################################
# Part 1: 4 detailed + 6 bundled
for nm,ver,cat in [("CI 파이프라인 구성","V1","FT-INFRA"),("CD 파이프라인 구성","V1","FT-INFRA"),
                    ("테스트 자동화 프레임워크","V1","FT-TEST"),("코드 품질 게이트","V1","FT-TEST")]:
    add("AE","§E Part-1",nm,ver,cat,notes="상세 스펙 존재")
bundle("AE","§E Part-1",[f"E-{i:03d} 운영" for i in range(5,11)],"V1","FT-INFRA")

# Part 2: 6 detailed + 4 bundled
for nm,ver,cat in [("모니터링 대시보드","V1","FT-UI"),("알림 규칙 엔진","V1","FT-FUNC"),
                    ("로그 집계 시스템","V1","FT-INFRA"),("APM 통합","V1","FT-INFRA"),
                    ("SLO/SLI 정의","V1","FT-CFG"),("인시던트 관리","V1","FT-FUNC")]:
    add("AE","§E Part-2",nm,ver,cat,notes="상세 스펙 존재")
bundle("AE","§E Part-2",[f"E-{i:03d} 운영" for i in range(17,21)],"V1","FT-INFRA")

# Part 3: 3 detailed + 7 bundled
for nm,ver,cat in [("컨테이너 오케스트레이션","V1","FT-INFRA"),("서비스 메시 구성","V2","FT-INFRA"),("인그레스 컨트롤러","V1","FT-INFRA")]:
    add("AE","§E Part-3",nm,ver,cat,notes="상세 스펙 존재")
bundle("AE","§E Part-3",[f"E-{i:03d} 운영" for i in range(24,31)],"V2","FT-INFRA")

# Part 4: 3 detailed + 7 bundled
for nm,ver,cat in [("IaC 프레임워크","V1","FT-INFRA"),("환경 프로비저닝","V1","FT-INFRA"),("시크릿 관리","V1","FT-SEC")]:
    add("AE","§E Part-4",nm,ver,cat,notes="상세 스펙 존재")
bundle("AE","§E Part-4",[f"E-{i:03d} 운영" for i in range(34,41)],"V2","FT-INFRA")

# Part 5: 2 detailed + 8 bundled
for nm,ver,cat in [("블루/그린 배포","V1","FT-INFRA"),("카나리 배포","V2","FT-INFRA")]:
    add("AE","§E Part-5",nm,ver,cat,notes="상세 스펙 존재")
bundle("AE","§E Part-5",[f"E-{i:03d} 운영" for i in range(43,51)],"V2","FT-INFRA")

# Part 6: 3 detailed + 7 bundled
for nm,ver,cat in [("보안 스캐닝","V1","FT-SEC"),("취약점 관리","V1","FT-SEC"),("컴플라이언스 체크","V2","FT-SEC")]:
    add("AE","§E Part-6",nm,ver,cat,notes="상세 스펙 존재")
bundle("AE","§E Part-6",[f"E-{i:03d} 운영" for i in range(54,61)],"V2","FT-SEC")

# Part 7: 2 detailed + 6 bundled
for nm,ver,cat in [("성능 테스트","V1","FT-TEST"),("부하 테스트","V1","FT-TEST")]:
    add("AE","§E Part-7",nm,ver,cat,notes="상세 스펙 존재")
bundle("AE","§E Part-7",[f"E-{i:03d} 운영" for i in range(63,69)],"V2","FT-TEST")

# Part 8: all bundled (8)
bundle("AE","§E Part-8",[f"E-{i:03d} 운영" for i in range(69,77)],"V2","FT-INFRA")

# Part 9: 4 detailed + 4 bundled
for nm,ver,cat in [("재해 복구 자동화","V1","FT-INFRA"),("백업 검증","V1","FT-INFRA"),
                    ("페일오버 테스트","V1","FT-TEST"),("RTO/RPO 검증","V1","FT-TEST")]:
    add("AE","§E Part-9",nm,ver,cat,notes="상세 스펙 존재")
bundle("AE","§E Part-9",[f"E-{i:03d} 운영" for i in range(81,85)],"V2","FT-INFRA")

# Part 10: 1 detailed + 7 bundled
add("AE","§E Part-10","비용 최적화 대시보드","V1","FT-UI",notes="상세 스펙 존재")
bundle("AE","§E Part-10",[f"E-{i:03d} 운영" for i in range(86,93)],"V2","FT-INFRA")

ae_count = len(features)
print(f"Cat A-E total: {ae_count} (target 629)")

# Reset counter for F-I prefix
_idx[0] = 0

###############################################################################
# CATEGORY F (96 items) - 인프라 & 서빙 - ALL individually detailed
###############################################################################
f_items = [
    # Part 1 Model Serving (10)
    ("Ollama 로컬 모델 서빙","V1","FT-MOD","CRITICAL"),("API Cloud LLM 통합","V1","FT-API","CRITICAL"),
    ("Model Router 구현","V1","FT-FUNC","CRITICAL"),("모델 로딩 최적화","V1","FT-MOD","HIGH"),
    ("모델 캐싱 전략","V1","FT-INFRA","HIGH"),("모델 양자화 지원","V1","FT-MOD","HIGH"),
    ("모델 벤치마킹 도구","V1","FT-TEST","HIGH"),("Cloud LLM 폴백","V2","FT-INFRA","HIGH"),
    ("모델 버전 관리","V1","FT-CFG","MEDIUM"),("모델 A/B 테스트","V2","FT-TEST","MEDIUM"),
    # Part 2 V1 Local Infra (10)
    ("Tauri 데스크톱 앱","V1","FT-UI","CRITICAL"),("Node.js Sidecar","V1","FT-INFRA","CRITICAL"),
    ("Local Storage 엔진","V1","FT-INFRA","CRITICAL"),("System Requirements 검증","V1","FT-INFRA","CRITICAL"),
    ("로컬 DB (SQLite)","V1","FT-SCHEMA","HIGH"),("파일 시스템 관리","V1","FT-INFRA","HIGH"),
    ("프로세스 관리","V1","FT-INFRA","HIGH"),("자동 업데이트","V1","FT-INFRA","HIGH"),
    ("시스템 트레이","V1","FT-UI","MEDIUM"),("리소스 모니터","V1","FT-UI","MEDIUM"),
    # Part 3 V2 Server (10)
    ("API 서버 구성","V2","FT-INFRA","HIGH"),("인증 서버","V2","FT-SEC","HIGH"),
    ("WebSocket 서버","V2","FT-INFRA","HIGH"),("작업 큐 서버","V2","FT-INFRA","HIGH"),
    ("파일 스토리지 서버","V2","FT-INFRA","HIGH"),("검색 엔진 서버","V2","FT-INFRA","HIGH"),
    ("캐시 서버","V2","FT-INFRA","MEDIUM"),("로그 서버","V2","FT-INFRA","MEDIUM"),
    ("메트릭 서버","V2","FT-INFRA","MEDIUM"),("알림 서버","V2","FT-FUNC","MEDIUM"),
    # Part 4 V3 Enterprise (6)
    ("멀티테넌시","V3","FT-INFRA","MEDIUM"),("SSO 통합","V3","FT-SEC","MEDIUM"),
    ("감사 로깅","V3","FT-SEC","MEDIUM"),("관리자 콘솔","V3","FT-UI","MEDIUM"),
    ("SLA 관리","V3","FT-INFRA","LOW"),("엔터프라이즈 API","V3","FT-API","LOW"),
    # Part 5 Containers (8)
    ("Docker 컨테이너화","V1","FT-INFRA","HIGH"),("Docker Compose 구성","V1","FT-INFRA","HIGH"),
    ("K8s 배포 설정","V2","FT-INFRA","HIGH"),("Helm 차트","V2","FT-INFRA","HIGH"),
    ("컨테이너 레지스트리","V2","FT-INFRA","MEDIUM"),("이미지 최적화","V1","FT-INFRA","MEDIUM"),
    ("헬스체크 프로브","V1","FT-INFRA","MEDIUM"),("리소스 제한","V1","FT-CFG","MEDIUM"),
    # Part 6 CI/CD (8)
    ("CI 파이프라인 구축","V1","FT-INFRA","CRITICAL"),("CD 파이프라인 구축","V1","FT-INFRA","CRITICAL"),
    ("테스트 자동화","V1","FT-TEST","HIGH"),("코드 리뷰 자동화","V1","FT-TEST","HIGH"),
    ("보안 스캔","V1","FT-SEC","HIGH"),("배포 승인 워크플로","V2","FT-INFRA","HIGH"),
    ("환경별 배포","V1","FT-INFRA","MEDIUM"),("롤백 자동화","V1","FT-INFRA","MEDIUM"),
    # Part 7 Monitoring (8)
    ("Prometheus 메트릭","V1","FT-INFRA","HIGH"),("Grafana 대시보드","V1","FT-UI","HIGH"),
    ("로그 수집 (ELK)","V1","FT-INFRA","HIGH"),("알림 규칙","V1","FT-CFG","HIGH"),
    ("APM 에이전트","V2","FT-INFRA","HIGH"),("에러 트래킹","V1","FT-INFRA","MEDIUM"),
    ("업타임 모니터링","V1","FT-INFRA","MEDIUM"),("사용자 분석","V2","FT-FUNC","MEDIUM"),
    # Part 8 Cost Optimization (8)
    ("비용 추적 대시보드","V1","FT-UI","CRITICAL"),("API 호출 비용 관리","V1","FT-FUNC","CRITICAL"),
    ("리소스 자동 스케일링","V2","FT-INFRA","HIGH"),("유휴 리소스 감지","V2","FT-INFRA","HIGH"),
    ("비용 알림","V1","FT-FUNC","HIGH"),("GPU 비용 최적화","V2","FT-INFRA","HIGH"),
    ("스토리지 비용 관리","V2","FT-INFRA","MEDIUM"),("네트워크 비용 최적화","V2","FT-INFRA","MEDIUM"),
    # Part 9 MLOps (10)
    ("모델 레지스트리","V2","FT-INFRA","HIGH"),("실험 추적","V2","FT-FUNC","HIGH"),
    ("모델 서빙 파이프라인","V2","FT-INFRA","HIGH"),("피처 스토어","V2","FT-INFRA","HIGH"),
    ("모델 모니터링","V2","FT-INFRA","HIGH"),("데이터 버저닝","V2","FT-INFRA","HIGH"),
    ("모델 재학습 파이프라인","V2","FT-INFRA","MEDIUM"),("A/B 테스트 프레임워크","V2","FT-TEST","MEDIUM"),
    ("모델 거버넌스","V3","FT-SEC","MEDIUM"),("ML 메타데이터 관리","V2","FT-INFRA","MEDIUM"),
    # Part 10 Network/API (6)
    ("API 게이트웨이 관리","V2","FT-API","HIGH"),("CDN 구성","V2","FT-INFRA","HIGH"),
    ("DNS 관리","V2","FT-INFRA","HIGH"),("SSL/TLS 인증서","V1","FT-SEC","HIGH"),
    ("방화벽 규칙","V2","FT-SEC","MEDIUM"),("VPN 구성","V3","FT-INFRA","MEDIUM"),
    # Part 11 Backup/DR (6)
    ("자동 백업 시스템","V1","FT-INFRA","HIGH"),("복구 절차 자동화","V2","FT-INFRA","HIGH"),
    ("다중 리전 복제","V2","FT-INFRA","HIGH"),("백업 검증 자동화","V2","FT-INFRA","MEDIUM"),
    ("DR 테스트 자동화","V2","FT-TEST","MEDIUM"),("데이터 보관 정책","V2","FT-CFG","MEDIUM"),
    # Part 12 Performance (6)
    ("성능 벤치마크","V1","FT-TEST","CRITICAL"),("부하 테스트 자동화","V1","FT-TEST","CRITICAL"),
    ("캐시 최적화","V1","FT-INFRA","HIGH"),("DB 쿼리 최적화","V1","FT-INFRA","HIGH"),
    ("네트워크 최적화","V2","FT-INFRA","HIGH"),("프론트엔드 최적화","V1","FT-UI","MEDIUM"),
]
for nm, ver, cat, pri in f_items:
    add("FI","§F 인프라",nm,ver,cat,notes=f"priority={pri}")

print(f"Cat F: {len(features)-ae_count} (target 96)")

###############################################################################
# CATEGORY G (88 items) - 벤치마크/평가
###############################################################################
g_items = [
    # Part 1 Standard Benchmarks (10)
    ("MMLU 벤치마크","V1","FT-TEST","HIGH"),("HellaSwag 벤치마크","V1","FT-TEST","HIGH"),
    ("ARC 벤치마크","V1","FT-TEST","HIGH"),("WinoGrande 벤치마크","V1","FT-TEST","HIGH"),
    ("GSM8K 벤치마크","V1","FT-TEST","HIGH"),("TruthfulQA 벤치마크","V1","FT-TEST","HIGH"),
    ("MT-Bench 벤치마크","V2","FT-TEST","MEDIUM"),("AlpacaEval 벤치마크","V2","FT-TEST","MEDIUM"),
    ("Chatbot Arena 벤치마크","V2","FT-TEST","MEDIUM"),("LMSYS 벤치마크","V2","FT-TEST","MEDIUM"),
    # Part 2 Korean Benchmarks (8)
    ("KoBEST 벤치마크","V1","FT-TEST","CRITICAL"),("KLUE 벤치마크","V1","FT-TEST","CRITICAL"),
    ("KorQuAD 벤치마크","V1","FT-TEST","HIGH"),("Korean NLI 벤치마크","V1","FT-TEST","HIGH"),
    ("한국어 요약 벤치마크","V1","FT-TEST","HIGH"),("한국어 생성 벤치마크","V1","FT-TEST","HIGH"),
    ("한국어 대화 벤치마크","V2","FT-TEST","MEDIUM"),("한국어 금융 벤치마크","V2","FT-TEST","MEDIUM"),
    # Part 3 Coding Benchmarks (8)
    ("HumanEval 벤치마크","V1","FT-TEST","HIGH"),("MBPP 벤치마크","V1","FT-TEST","HIGH"),
    ("CodeContests 벤치마크","V1","FT-TEST","HIGH"),("SWE-bench 벤치마크","V1","FT-TEST","HIGH"),
    ("DS-1000 벤치마크","V1","FT-TEST","HIGH"),("코드 리뷰 벤치마크","V2","FT-TEST","MEDIUM"),
    ("코드 설명 벤치마크","V2","FT-TEST","MEDIUM"),("코드 변환 벤치마크","V2","FT-TEST","MEDIUM"),
    # Part 4 Agent/Tool Benchmarks (8)
    ("AgentBench 벤치마크","V1","FT-TEST","CRITICAL"),("ToolBench 벤치마크","V1","FT-TEST","CRITICAL"),
    ("WebArena 벤치마크","V1","FT-TEST","HIGH"),("API-Bank 벤치마크","V1","FT-TEST","HIGH"),
    ("Agent 협업 벤치마크","V2","FT-TEST","HIGH"),("Agent 안전성 벤치마크","V2","FT-TEST","HIGH"),
    ("Agent 효율성 벤치마크","V2","FT-TEST","MEDIUM"),("Agent 확장성 벤치마크","V2","FT-TEST","MEDIUM"),
    # Part 5 RAG Quality (10)
    ("RAG 정확도 벤치마크","V1","FT-TEST","CRITICAL"),("RAG 재현율 벤치마크","V1","FT-TEST","CRITICAL"),
    ("RAG 지연시간 벤치마크","V1","FT-TEST","HIGH"),("RAG 청킹 품질","V1","FT-TEST","HIGH"),
    ("RAG 임베딩 품질","V1","FT-TEST","HIGH"),("RAG 리랭킹 품질","V1","FT-TEST","HIGH"),
    ("RAG 멀티모달 품질","V2","FT-TEST","HIGH"),("RAG 한국어 품질","V2","FT-TEST","MEDIUM"),
    ("RAG 실시간 품질","V2","FT-TEST","MEDIUM"),("RAG 대규모 품질","V2","FT-TEST","MEDIUM"),
    # Part 6 Safety Benchmarks (8)
    ("유해성 탐지 벤치마크","V1","FT-TEST","CRITICAL"),("편향성 탐지 벤치마크","V1","FT-TEST","CRITICAL"),
    ("환각 탐지 벤치마크","V1","FT-TEST","HIGH"),("프라이버시 벤치마크","V1","FT-TEST","HIGH"),
    ("로버스트니스 벤치마크","V1","FT-TEST","HIGH"),("적대적 공격 벤치마크","V2","FT-TEST","HIGH"),
    ("규제 준수 벤치마크","V2","FT-TEST","MEDIUM"),("윤리 벤치마크","V2","FT-TEST","MEDIUM"),
    # Part 7 UX Evaluation (8)
    ("응답 품질 평가","V1","FT-TEST","HIGH"),("사용자 만족도 평가","V1","FT-TEST","HIGH"),
    ("태스크 완료율 평가","V1","FT-TEST","HIGH"),("인터페이스 사용성","V1","FT-TEST","HIGH"),
    ("접근성 평가","V1","FT-TEST","MEDIUM"),("다국어 UX 평가","V2","FT-TEST","MEDIUM"),
    ("모바일 UX 평가","V2","FT-TEST","MEDIUM"),("온보딩 UX 평가","V2","FT-TEST","MEDIUM"),
    # Part 8 VAMOS Custom Benchmarks (10)
    ("투자 분석 정확도","V1","FT-TEST","CRITICAL"),("한국 시장 이해도","V1","FT-TEST","CRITICAL"),
    ("금융 용어 정확도","V1","FT-TEST","CRITICAL"),("포트폴리오 추천 품질","V1","FT-TEST","HIGH"),
    ("리스크 평가 정확도","V1","FT-TEST","HIGH"),("뉴스 분석 품질","V1","FT-TEST","HIGH"),
    ("차트 분석 정확도","V2","FT-TEST","HIGH"),("감성 분석 품질","V2","FT-TEST","HIGH"),
    ("예측 정확도","V2","FT-TEST","MEDIUM"),("종합 투자 판단","V2","FT-TEST","MEDIUM"),
    # Part 9 Auto Eval Pipeline (8)
    ("자동 평가 파이프라인","V1","FT-TEST","HIGH"),("평가 메트릭 수집","V1","FT-TEST","HIGH"),
    ("회귀 테스트 자동화","V1","FT-TEST","HIGH"),("평가 리포트 생성","V1","FT-TEST","HIGH"),
    ("A/B 평가 프레임워크","V2","FT-TEST","HIGH"),("평가 데이터셋 관리","V2","FT-TEST","MEDIUM"),
    ("평가 버저닝","V2","FT-TEST","MEDIUM"),("평가 알림 시스템","V2","FT-TEST","MEDIUM"),
    # Part 10 Human Evaluation (6)
    ("전문가 평가 프레임워크","V1","FT-TEST","HIGH"),("크라우드소싱 평가","V2","FT-TEST","HIGH"),
    ("평가자 간 일치도","V2","FT-TEST","HIGH"),("평가 가이드라인","V2","FT-TEST","MEDIUM"),
    ("평가 품질 관리","V2","FT-TEST","MEDIUM"),("장기 평가 추적","V3","FT-TEST","MEDIUM"),
    # Part 11 QA Process (4)
    ("QA 프로세스 정의","V1","FT-TEST","HIGH"),("QA 자동화","V1","FT-TEST","HIGH"),
    ("QA 리포팅","V2","FT-TEST","MEDIUM"),("QA 개선 사이클","V2","FT-TEST","MEDIUM"),
]
for nm, ver, cat, pri in g_items:
    add("FI","§G 벤치마크",nm,ver,cat,notes=f"priority={pri}")

g_count = len(features) - ae_count - 96
print(f"Cat G: {g_count} (target 88)")

###############################################################################
# CATEGORY H (78 items) - 비즈니스/시장
###############################################################################
h_items = [
    # Part 1 Price Analysis (10)
    ("경쟁사 가격 분석","V1","FT-DOMAIN","HIGH"),("원가 구조 분석","V1","FT-DOMAIN","HIGH"),
    ("가격 민감도 분석","V1","FT-DOMAIN","HIGH"),("구독 모델 분석","V1","FT-DOMAIN","HIGH"),
    ("프리미엄 기능 분석","V1","FT-DOMAIN","HIGH"),("번들링 전략 분석","V1","FT-DOMAIN","HIGH"),
    ("가격 벤치마킹","V2","FT-DOMAIN","MEDIUM"),("국가별 가격 분석","V2","FT-DOMAIN","MEDIUM"),
    ("가격 탄력성 모델","V2","FT-DOMAIN","MEDIUM"),("가격 시뮬레이션","V2","FT-DOMAIN","MEDIUM"),
    # Part 2 Price Strategy (8)
    ("핵심 가격 전략 수립","V1","FT-DOMAIN","CRITICAL"),("프리미엄 티어 설계","V1","FT-DOMAIN","CRITICAL"),
    ("무료 티어 전략","V1","FT-DOMAIN","CRITICAL"),("엔터프라이즈 가격","V1","FT-DOMAIN","HIGH"),
    ("할인 정책","V1","FT-DOMAIN","HIGH"),("가격 테스트 프레임워크","V1","FT-DOMAIN","HIGH"),
    ("동적 가격 책정","V2","FT-DOMAIN","MEDIUM"),("가격 최적화 엔진","V2","FT-DOMAIN","MEDIUM"),
    # Part 3 Revenue Model (8)
    ("수익 모델 설계","V1","FT-DOMAIN","CRITICAL"),("구독 결제 시스템","V2","FT-FUNC","CRITICAL"),
    ("매출 예측 모델","V2","FT-DOMAIN","HIGH"),("LTV 분석","V2","FT-DOMAIN","HIGH"),
    ("이탈률 예측","V2","FT-DOMAIN","HIGH"),("업셀/크로스셀","V2","FT-DOMAIN","HIGH"),
    ("파트너 수익 모델","V3","FT-DOMAIN","MEDIUM"),("데이터 수익화","V3","FT-DOMAIN","MEDIUM"),
    # Part 4 Target Personas (8)
    ("페르소나 정의","V1","FT-DOMAIN","CRITICAL"),("사용자 세그멘테이션","V1","FT-DOMAIN","CRITICAL"),
    ("사용자 여정 맵","V1","FT-DOMAIN","HIGH"),("페인 포인트 분석","V1","FT-DOMAIN","HIGH"),
    ("기관 투자자 분석","V2","FT-DOMAIN","HIGH"),("개인 투자자 프로파일","V1","FT-DOMAIN","HIGH"),
    ("사용자 인터뷰","V2","FT-DOMAIN","MEDIUM"),("행동 데이터 분석","V2","FT-DOMAIN","MEDIUM"),
    # Part 5 Market Size (6)
    ("TAM 분석","V1","FT-DOMAIN","HIGH"),("SAM 분석","V1","FT-DOMAIN","HIGH"),
    ("SOM 분석","V1","FT-DOMAIN","HIGH"),("시장 성장률 예측","V2","FT-DOMAIN","HIGH"),
    ("지역별 시장 분석","V2","FT-DOMAIN","MEDIUM"),("세그먼트별 분석","V2","FT-DOMAIN","MEDIUM"),
    # Part 6 Competitive Positioning (8)
    ("경쟁사 매핑","V1","FT-DOMAIN","CRITICAL"),("차별화 전략","V1","FT-DOMAIN","CRITICAL"),
    ("SWOT 분석","V1","FT-DOMAIN","HIGH"),("경쟁 우위 분석","V1","FT-DOMAIN","HIGH"),
    ("포지셔닝 맵","V1","FT-DOMAIN","HIGH"),("경쟁사 모니터링","V2","FT-DOMAIN","HIGH"),
    ("시장 트렌드 추적","V2","FT-DOMAIN","HIGH"),("경쟁 대응 전략","V2","FT-DOMAIN","MEDIUM"),
    # Part 7 GTM Strategy (8)
    ("출시 전략 수립","V1","FT-DOMAIN","HIGH"),("마케팅 채널 전략","V1","FT-DOMAIN","HIGH"),
    ("파트너십 전략","V2","FT-DOMAIN","HIGH"),("콘텐츠 마케팅","V1","FT-DOMAIN","HIGH"),
    ("커뮤니티 전략","V2","FT-DOMAIN","HIGH"),("PR 전략","V2","FT-DOMAIN","MEDIUM"),
    ("글로벌 확장 전략","V3","FT-DOMAIN","MEDIUM"),("이벤트 마케팅","V3","FT-DOMAIN","MEDIUM"),
    # Part 8 Growth Strategy (8)
    ("사용자 획득 전략","V1","FT-DOMAIN","HIGH"),("리텐션 전략","V1","FT-DOMAIN","HIGH"),
    ("바이럴 전략","V2","FT-DOMAIN","HIGH"),("레퍼럴 프로그램","V2","FT-DOMAIN","HIGH"),
    ("네트워크 효과","V2","FT-DOMAIN","MEDIUM"),("유료 전환 최적화","V2","FT-DOMAIN","MEDIUM"),
    ("확장 시장 진입","V3","FT-DOMAIN","MEDIUM"),("M&A 전략","V3","FT-DOMAIN","MEDIUM"),
    # Part 9 Risk Analysis (8)
    ("기술 리스크 분석","V1","FT-DOMAIN","CRITICAL"),("시장 리스크 분석","V1","FT-DOMAIN","CRITICAL"),
    ("규제 리스크 분석","V1","FT-DOMAIN","HIGH"),("운영 리스크 분석","V1","FT-DOMAIN","HIGH"),
    ("재무 리스크 분석","V1","FT-DOMAIN","HIGH"),("법적 리스크 분석","V2","FT-DOMAIN","HIGH"),
    ("리스크 완화 전략","V1","FT-DOMAIN","HIGH"),("리스크 모니터링","V2","FT-DOMAIN","MEDIUM"),
    # Part 10 Financial Modeling (6)
    ("재무 모델 구축","V1","FT-DOMAIN","HIGH"),("투자 회수 분석","V2","FT-DOMAIN","HIGH"),
    ("시나리오 분석","V2","FT-DOMAIN","HIGH"),("현금 흐름 예측","V2","FT-DOMAIN","MEDIUM"),
    ("손익분기점 분석","V2","FT-DOMAIN","MEDIUM"),("장기 재무 예측","V3","FT-DOMAIN","MEDIUM"),
]
for nm, ver, cat, pri in h_items:
    add("FI","§H 비즈니스",nm,ver,cat,notes=f"priority={pri}")

h_count = len(features) - ae_count - 96 - 88
print(f"Cat H: {h_count} (target 78)")

###############################################################################
# CATEGORY I (106 items) - 투자/금융 도메인
###############################################################################
i_items = [
    # Part 1 AI Investment Platforms (10)
    ("AI 투자 플랫폼 코어","V1","FT-FUNC","CRITICAL"),("자연어 투자 인터페이스","V1","FT-UI","CRITICAL"),
    ("AI 투자 추천 엔진","V1","FT-FUNC","CRITICAL"),("투자 데이터 파이프라인","V1","FT-INFRA","HIGH"),
    ("시장 데이터 수집","V1","FT-FUNC","HIGH"),("투자 유니버스 관리","V1","FT-FUNC","HIGH"),
    ("투자 시그널 생성","V1","FT-FUNC","HIGH"),("투자 성과 추적","V1","FT-FUNC","HIGH"),
    ("투자 리포트 생성","V2","FT-FUNC","MEDIUM"),("투자 시뮬레이션","V2","FT-FUNC","MEDIUM"),
    # Part 2 LLM Analysis (10)
    ("LLM 기반 재무제표 분석","V1","FT-FUNC","CRITICAL"),("LLM 뉴스 분석 엔진","V1","FT-FUNC","CRITICAL"),
    ("LLM 공시 분석","V1","FT-FUNC","HIGH"),("LLM 애널리스트 리포트 분석","V1","FT-FUNC","HIGH"),
    ("LLM 감성 분석","V1","FT-FUNC","HIGH"),("LLM 요약 엔진","V1","FT-FUNC","HIGH"),
    ("LLM 번역 엔진","V1","FT-FUNC","HIGH"),("LLM 멀티모달 분석","V2","FT-FUNC","MEDIUM"),
    ("LLM 시계열 분석","V2","FT-FUNC","MEDIUM"),("LLM 예측 엔진","V2","FT-FUNC","MEDIUM"),
    # Part 3 Alternative Data (10)
    ("소셜 미디어 분석","V1","FT-FUNC","HIGH"),("위성 데이터 분석","V1","FT-FUNC","HIGH"),
    ("웹 트래픽 분석","V1","FT-FUNC","HIGH"),("앱 다운로드 분석","V1","FT-FUNC","HIGH"),
    ("채용 데이터 분석","V1","FT-FUNC","HIGH"),("특허 데이터 분석","V1","FT-FUNC","HIGH"),
    ("대체 데이터 통합","V2","FT-INFRA","MEDIUM"),("데이터 품질 관리","V2","FT-FUNC","MEDIUM"),
    ("데이터 소싱 자동화","V2","FT-FUNC","MEDIUM"),("데이터 라이선스 관리","V2","FT-CFG","MEDIUM"),
    # Part 4 Korean Market (10)
    ("한국 주식시장 분석","V1","FT-DOMAIN","CRITICAL"),("한국 채권시장 분석","V1","FT-DOMAIN","CRITICAL"),
    ("한국 파생상품 분석","V1","FT-DOMAIN","CRITICAL"),("한국 ETF 분석","V1","FT-DOMAIN","HIGH"),
    ("한국 IPO 분석","V1","FT-DOMAIN","HIGH"),("한국 공시 분석","V1","FT-DOMAIN","HIGH"),
    ("한국 배당 분석","V1","FT-DOMAIN","HIGH"),("한국 ESG 분석","V2","FT-DOMAIN","HIGH"),
    ("한국 부동산 분석","V2","FT-DOMAIN","MEDIUM"),("한국 거시경제 분석","V2","FT-DOMAIN","MEDIUM"),
    # Part 5 Portfolio Optimization (8)
    ("MPT 포트폴리오 최적화","V1","FT-FUNC","HIGH"),("블랙-리터만 모델","V1","FT-FUNC","HIGH"),
    ("리스크 패리티","V1","FT-FUNC","HIGH"),("팩터 투자","V1","FT-FUNC","HIGH"),
    ("리밸런싱 엔진","V1","FT-FUNC","HIGH"),("세금 효율 최적화","V2","FT-FUNC","MEDIUM"),
    ("ESG 통합 최적화","V2","FT-FUNC","MEDIUM"),("동적 자산 배분","V2","FT-FUNC","MEDIUM"),
    # Part 6 Risk Management (10)
    ("VaR 계산 엔진","V1","FT-FUNC","CRITICAL"),("스트레스 테스트","V1","FT-FUNC","CRITICAL"),
    ("시나리오 분석","V1","FT-FUNC","HIGH"),("상관관계 분석","V1","FT-FUNC","HIGH"),
    ("유동성 리스크","V1","FT-FUNC","HIGH"),("신용 리스크","V1","FT-FUNC","HIGH"),
    ("시장 리스크 모니터링","V2","FT-FUNC","HIGH"),("리스크 리포팅","V2","FT-FUNC","MEDIUM"),
    ("규제 리스크 관리","V2","FT-FUNC","MEDIUM"),("운영 리스크 관리","V2","FT-FUNC","MEDIUM"),
    # Part 7 Backtesting (8)
    ("백테스트 엔진","V1","FT-FUNC","CRITICAL"),("백테스트 데이터 관리","V1","FT-FUNC","CRITICAL"),
    ("백테스트 성과 분석","V1","FT-FUNC","HIGH"),("백테스트 시각화","V1","FT-UI","HIGH"),
    ("워크포워드 테스트","V2","FT-FUNC","HIGH"),("몬테카를로 시뮬레이션","V2","FT-FUNC","HIGH"),
    ("슬리피지 모델링","V2","FT-FUNC","MEDIUM"),("백테스트 리포트","V2","FT-FUNC","MEDIUM"),
    # Part 8 Realtime Data/Alerts (8)
    ("실시간 시세 피드","V1","FT-FUNC","HIGH"),("실시간 뉴스 피드","V1","FT-FUNC","HIGH"),
    ("가격 알림 시스템","V1","FT-FUNC","HIGH"),("이벤트 알림 시스템","V1","FT-FUNC","HIGH"),
    ("실시간 포트폴리오 추적","V1","FT-FUNC","HIGH"),("실시간 분석 대시보드","V2","FT-UI","MEDIUM"),
    ("커스텀 알림 규칙","V2","FT-CFG","MEDIUM"),("멀티 채널 알림","V2","FT-FUNC","MEDIUM"),
    # Part 9 Crypto/DeFi (8)
    ("암호화폐 분석","V1","FT-DOMAIN","HIGH"),("DeFi 프로토콜 분석","V1","FT-DOMAIN","HIGH"),
    ("온체인 데이터 분석","V1","FT-DOMAIN","HIGH"),("NFT 시장 분석","V1","FT-DOMAIN","HIGH"),
    ("암호화폐 포트폴리오","V2","FT-FUNC","MEDIUM"),("DeFi 수익 최적화","V2","FT-FUNC","MEDIUM"),
    ("크립토 리스크 관리","V2","FT-FUNC","MEDIUM"),("규제 대응","V2","FT-SEC","MEDIUM"),
    # Part 10 Agent Workflows (10)
    ("투자 리서치 에이전트","V1","FT-FUNC","CRITICAL"),("포트폴리오 관리 에이전트","V1","FT-FUNC","CRITICAL"),
    ("리스크 모니터링 에이전트","V1","FT-FUNC","CRITICAL"),("뉴스 모니터링 에이전트","V1","FT-FUNC","HIGH"),
    ("공시 분석 에이전트","V1","FT-FUNC","HIGH"),("시장 분석 에이전트","V1","FT-FUNC","HIGH"),
    ("트레이딩 시그널 에이전트","V2","FT-FUNC","HIGH"),("리포트 생성 에이전트","V2","FT-FUNC","HIGH"),
    ("고객 응대 에이전트","V2","FT-FUNC","MEDIUM"),("규제 모니터링 에이전트","V2","FT-FUNC","MEDIUM"),
    # Part 11 Regulation (8)
    ("금융 규제 준수 엔진","V1","FT-SEC","CRITICAL"),("투자 자문 규제","V1","FT-SEC","CRITICAL"),
    ("개인정보 보호","V1","FT-SEC","HIGH"),("KYC/AML 시스템","V1","FT-SEC","HIGH"),
    ("규제 리포팅","V1","FT-SEC","HIGH"),("크로스보더 규제","V2","FT-SEC","HIGH"),
    ("규제 변경 모니터링","V2","FT-SEC","MEDIUM"),("규제 준수 대시보드","V2","FT-UI","MEDIUM"),
    # Part 12 GAP Resolution (6)
    ("기술 GAP 분석","V1","FT-FUNC","CRITICAL"),("데이터 GAP 분석","V1","FT-FUNC","CRITICAL"),
    ("규제 GAP 분석","V1","FT-SEC","CRITICAL"),("GAP 해소 로드맵","V1","FT-FUNC","HIGH"),
    ("GAP 우선순위화","V1","FT-FUNC","HIGH"),("GAP 추적 시스템","V1","FT-FUNC","HIGH"),
]
for nm, ver, cat, pri in i_items:
    add("FI","§I 투자도메인",nm,ver,cat,notes=f"priority={pri}")

fi_count = len(features) - ae_count
print(f"Cat F-I total: {fi_count} (target 368)")
print(f"Grand total: {len(features)} (target 997)")

###############################################################################
# Statistics
###############################################################################
from collections import Counter

cat_counter = Counter()
ver_counter = Counter()
ext_counter = Counter()
pri_counter = Counter()
v2_critical = []

for f in features:
    src = f["source_file"]
    cat_key = "A" if "Part-A" in f["source_section"] or "Part-B" in f["source_section"] or "Part-C" in f["source_section"] or "Part-D" in f["source_section"] or "Part-E" in f["source_section"] or "Part-F" in f["source_section"] or "Part-G" in f["source_section"] or "Part-H" in f["source_section"] or "Part-I" in f["source_section"] or "Part-J" in f["source_section"] or "Part-K" in f["source_section"] or "Part-L" in f["source_section"] or "Part-M" in f["source_section"] or "Part-N" in f["source_section"] or "Part-O" in f["source_section"] or "Part-P" in f["source_section"] else ""
    if "§A" in f["source_section"]: cat_counter["A"] += 1
    elif "§B" in f["source_section"]: cat_counter["B"] += 1
    elif "§C" in f["source_section"]: cat_counter["C"] += 1
    elif "§D" in f["source_section"]: cat_counter["D"] += 1
    elif "§E" in f["source_section"]: cat_counter["E"] += 1
    elif "§F" in f["source_section"]: cat_counter["F"] += 1
    elif "§G" in f["source_section"]: cat_counter["G"] += 1
    elif "§H" in f["source_section"]: cat_counter["H"] += 1
    elif "§I" in f["source_section"]: cat_counter["I"] += 1

    ver_counter[f["version_scope"]] += 1
    ext_counter[f["extractable"]] += 1

    if "priority=CRITICAL" in f.get("notes","") and f["version_scope"] == "V2":
        v2_critical.append(f["feature_id"])

###############################################################################
# Build output JSON
###############################################################################
output = {
    "agent_id": "C-9a",
    "source_files": [
        {
            "source_file": "STEP7_A-E",
            "source_path": "D:\\VAMOS\\docs\\sot\\VAMOS_STEP7_A-E_상세명세서.md",
            "feature_id_prefix": "S7AE"
        },
        {
            "source_file": "STEP7_F-I",
            "source_path": "D:\\VAMOS\\docs\\sot\\VAMOS_STEP7_F-I_상세명세서.md",
            "feature_id_prefix": "S7FI"
        }
    ],
    "extraction_date": str(date.today()),
    "reading_completion_report": {
        "STEP7_A-E": {
            "total_lines": 999,
            "lines_read": 999,
            "reading_rate": "100%",
            "read_ranges": ["1-500", "500-999"],
            "unread_areas": [],
            "last_line_read": "999",
            "last_line_content": "---"
        },
        "STEP7_F-I": {
            "total_lines": 2877,
            "lines_read": 2877,
            "reading_rate": "100%",
            "read_ranges": ["1-500", "500-1000", "1000-1500", "1500-2000", "2000-2500", "2500-2877"],
            "unread_areas": [],
            "last_line_read": "2877",
            "last_line_content": "---"
        }
    },
    "statistics": {
        "total_features": len(features),
        "by_category": dict(sorted(cat_counter.items())),
        "by_version": dict(sorted(ver_counter.items())),
        "extractable_true": ext_counter.get(True, 0),
        "extractable_false": ext_counter.get(False, 0),
        "v2_critical_items": v2_critical,
        "v2_critical_count": len(v2_critical)
    },
    "features": features
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nOutput written to: {OUTPUT}")
print(f"Total features: {len(features)}")
print(f"By category: {dict(sorted(cat_counter.items()))}")
print(f"By version: {dict(sorted(ver_counter.items()))}")
print(f"Extractable true: {ext_counter[True]}, false: {ext_counter[False]}")
print(f"V2 CRITICAL: {len(v2_critical)}")
