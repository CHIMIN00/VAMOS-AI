#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v10 Phase 0-C Agent C-9b: Generate v10_src_C09b.json
   Sources: STEP7_J-M (284건) + STEP7_N-P_보강 (204건) + STEP7_보강_통합 (73건)
"""
import json
from datetime import date
from collections import Counter

OUTPUT = r"D:\VAMOS\04. 구현단계\v10_results\phase0-c\v10_src_C09b.json"
features = []

###############################################################################
# Helper
###############################################################################
_counters = {"S7JM": 0, "S7NP": 0, "S7BG": 0}

def nid(prefix):
    _counters[prefix] += 1
    return f"{prefix}-{_counters[prefix]:03d}"

def add(prefix, src_file, section, name, ver, cat, extractable=True,
        conf="명시적", impl="신규구현", notes="", deps=[]):
    features.append({
        "feature_id": nid(prefix),
        "source_file": src_file,
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

def jm(section, name, ver, cat, **kw):
    add("S7JM", "STEP7_J-M", section, name, ver, cat, **kw)

def np_(section, name, ver, cat, **kw):
    add("S7NP", "STEP7_N-P", section, name, ver, cat, **kw)

def bg(section, name, ver, cat, **kw):
    add("S7BG", "STEP7_보강", section, name, ver, cat, **kw)

def jm_ref(section, name, ver, cat):
    """참고자료/로드맵 — extractable=false"""
    jm(section, name, ver, cat, extractable=False, notes="참고자료/로드맵 메타")

###############################################################################
# FILE 1: STEP7_J-M (284건)
###############################################################################
# ===== CATEGORY J: 멀티모달 생성/처리 (98건) =====

# J-Part1: 비전-언어 모델 통합 (10)
jm("§J-Part1 비전-언어 모델 통합", "이미지 입력 처리 파이프라인", "V1,V2,V3", "FT-FUNC", notes="J-001")
jm("§J-Part1 비전-언어 모델 통합", "멀티모달 대화 컨텍스트 관리", "V1,V2", "FT-FUNC", notes="J-002")
jm("§J-Part1 비전-언어 모델 통합", "OCR + 문서 이해", "V1,V2", "FT-FUNC", notes="J-003")
jm("§J-Part1 비전-언어 모델 통합", "스크린 캡처 + 화면 이해", "V1,V2", "FT-FUNC", notes="J-004")
jm("§J-Part1 비전-언어 모델 통합", "차트/그래프/다이어그램 자동 분석", "V1,V2", "FT-FUNC", notes="J-005")
jm("§J-Part1 비전-언어 모델 통합", "실시간 비디오/카메라 입력 처리", "V1,V2,V3", "FT-FUNC", notes="J-006")
jm("§J-Part1 비전-언어 모델 통합", "멀티모달 임베딩 통합 검색", "V1,V2", "FT-FUNC", notes="J-007")
jm("§J-Part1 비전-언어 모델 통합", "비전 기반 코드 이해", "V1,V2", "FT-FUNC", notes="J-008")
jm("§J-Part1 비전-언어 모델 통합", "공간 이해 및 AR 연동", "V3", "FT-FUNC", notes="J-009")
jm("§J-Part1 비전-언어 모델 통합", "멀티모달 입력 품질 관리", "V1,V2", "FT-FUNC", notes="J-010")

# J-Part2: 이미지 생성/편집 (10)
jm("§J-Part2 이미지 생성/편집", "이미지 생성 통합 게이트웨이", "V2", "FT-FUNC", notes="J-011")
jm("§J-Part2 이미지 생성/편집", "프롬프트 엔지니어링 자동화", "V1,V2", "FT-FUNC", notes="J-012")
jm("§J-Part2 이미지 생성/편집", "이미지 편집 (인페인팅/아웃페인팅)", "V2", "FT-FUNC", notes="J-013")
jm("§J-Part2 이미지 생성/편집", "스타일 트랜스퍼", "V2", "FT-FUNC", notes="J-014")
jm("§J-Part2 이미지 생성/편집", "투자 차트 자동 생성", "V1,V2", "FT-UI", notes="J-015")
jm("§J-Part2 이미지 생성/편집", "로고/아이콘 생성", "V2", "FT-FUNC", notes="J-016")
jm("§J-Part2 이미지 생성/편집", "이미지 갤러리 관리", "V1", "FT-UI", notes="J-017")
jm("§J-Part2 이미지 생성/편집", "이미지 메타데이터 관리", "V1", "FT-FUNC", notes="J-018")
jm("§J-Part2 이미지 생성/편집", "배치 이미지 처리", "V2", "FT-FUNC", notes="J-019")
jm("§J-Part2 이미지 생성/편집", "이미지 비용 최적화", "V1", "FT-CFG", notes="J-020")

# J-Part3: 음성/오디오 (10)
jm("§J-Part3 음성/오디오", "STT 파이프라인 (Whisper v3)", "V1,V2", "FT-FUNC", notes="J-021")
jm("§J-Part3 음성/오디오", "실시간 STT 스트리밍", "V1,V2", "FT-FUNC", notes="J-022")
jm("§J-Part3 음성/오디오", "화자 분리 (Speaker Diarization)", "V2", "FT-FUNC", notes="J-023")
jm("§J-Part3 음성/오디오", "오디오 감정 분석", "V2", "FT-FUNC", notes="J-024")
jm("§J-Part3 음성/오디오", "TTS 통합 (Edge TTS/ElevenLabs)", "V1,V2", "FT-FUNC", notes="J-025")
jm("§J-Part3 음성/오디오", "AI 음성 클로닝", "V3", "FT-FUNC", notes="J-026")
jm("§J-Part3 음성/오디오", "음성 명령 시스템", "V1", "FT-FUNC", notes="J-027")
jm("§J-Part3 음성/오디오", "음성 대화 모드", "V1,V2", "FT-FUNC", notes="J-028")
jm("§J-Part3 음성/오디오", "오디오 파일 분석", "V1", "FT-FUNC", notes="J-029")
jm("§J-Part3 음성/오디오", "음성 품질 최적화", "V1", "FT-FUNC", notes="J-030")

# J-Part4: 비디오 처리 (10)
jm("§J-Part4 비디오 처리", "비디오 입력 분석", "V2", "FT-FUNC", notes="J-031")
jm("§J-Part4 비디오 처리", "비디오 요약 생성", "V2", "FT-FUNC", notes="J-032")
jm("§J-Part4 비디오 처리", "비디오 자막 생성", "V1,V2", "FT-FUNC", notes="J-033")
jm("§J-Part4 비디오 처리", "비디오 하이라이트 추출", "V2", "FT-FUNC", notes="J-034")
jm("§J-Part4 비디오 처리", "데이터 시각화 자동 생성", "V1,V2", "FT-UI", notes="J-035")
jm("§J-Part4 비디오 처리", "비디오 검색", "V2", "FT-FUNC", notes="J-036")
jm("§J-Part4 비디오 처리", "스크린 녹화 + AI 분석", "V2", "FT-FUNC", notes="J-037")
jm("§J-Part4 비디오 처리", "비디오 편집 AI 지원", "V3", "FT-FUNC", notes="J-038")
jm("§J-Part4 비디오 처리", "실시간 화면 공유 분석", "V2", "FT-FUNC", notes="J-039")
jm("§J-Part4 비디오 처리", "비디오 메타데이터 관리", "V2", "FT-FUNC", notes="J-040")

# J-Part5: 문서 처리 (10)
jm("§J-Part5 문서 처리", "PDF 분석 파이프라인", "V1", "FT-FUNC", notes="J-041")
jm("§J-Part5 문서 처리", "스프레드시트 분석", "V1", "FT-FUNC", notes="J-042")
jm("§J-Part5 문서 처리", "프레젠테이션 분석/생성", "V1,V2", "FT-FUNC", notes="J-043")
jm("§J-Part5 문서 처리", "마크다운/텍스트 변환", "V1", "FT-FUNC", notes="J-044")
jm("§J-Part5 문서 처리", "코드 생성/편집 멀티모달", "V2", "FT-FUNC", notes="J-045")
jm("§J-Part5 문서 처리", "문서 비교 분석", "V1", "FT-FUNC", notes="J-046")
jm("§J-Part5 문서 처리", "양식/폼 자동 생성", "V2", "FT-FUNC", notes="J-047")
jm("§J-Part5 문서 처리", "다국어 문서 처리", "V1,V2", "FT-FUNC", notes="J-048")
jm("§J-Part5 문서 처리", "문서 품질 평가", "V2", "FT-FUNC", notes="J-049")
jm("§J-Part5 문서 처리", "문서 보안/워터마크", "V2", "FT-SEC", notes="J-050")

# J-Part6: 멀티모달 생성 (10)
jm("§J-Part6 멀티모달 생성", "텍스트→이미지 파이프라인", "V2", "FT-FUNC", notes="J-051")
jm("§J-Part6 멀티모달 생성", "텍스트→오디오 파이프라인", "V2", "FT-FUNC", notes="J-052")
jm("§J-Part6 멀티모달 생성", "텍스트→비디오 파이프라인", "V3", "FT-FUNC", notes="J-053")
jm("§J-Part6 멀티모달 생성", "이미지→텍스트 설명", "V1", "FT-FUNC", notes="J-054")
jm("§J-Part6 멀티모달 생성", "AI 음악 생성 (Suno/MusicGen)", "V3", "FT-FUNC", notes="J-055")
jm("§J-Part6 멀티모달 생성", "3D 모델 생성", "V3", "FT-FUNC", notes="J-056")
jm("§J-Part6 멀티모달 생성", "인포그래픽 자동 생성", "V2", "FT-UI", notes="J-057")
jm("§J-Part6 멀티모달 생성", "마인드맵 자동 생성", "V1", "FT-UI", notes="J-058")
jm("§J-Part6 멀티모달 생성", "AI 프레젠테이션 생성", "V2", "FT-FUNC", notes="J-059")
jm("§J-Part6 멀티모달 생성", "멀티모달 콘텐츠 편집기", "V2", "FT-UI", notes="J-060")

# J-Part7: 멀티모달 파이프라인 (10)
jm("§J-Part7 멀티모달 파이프라인", "멀티모달 RAG", "V1,V2", "FT-FUNC", notes="J-061")
jm("§J-Part7 멀티모달 파이프라인", "크로스모달 검색", "V2", "FT-FUNC", notes="J-062")
jm("§J-Part7 멀티모달 파이프라인", "멀티모달 캐싱 전략", "V1", "FT-INFRA", notes="J-063")
jm("§J-Part7 멀티모달 파이프라인", "멀티모달 비용 관리", "V1", "FT-CFG", notes="J-064")
jm("§J-Part7 멀티모달 파이프라인", "멀티모달 A/B 테스트", "V2", "FT-TEST", notes="J-065")
jm("§J-Part7 멀티모달 파이프라인", "멀티모달 품질 평가", "V1,V2", "FT-TEST", notes="J-066")
jm("§J-Part7 멀티모달 파이프라인", "멀티모달 벤치마크", "V2", "FT-TEST", notes="J-067")
jm("§J-Part7 멀티모달 파이프라인", "멀티모달 안전 필터", "V1", "FT-SEC", notes="J-068")
jm("§J-Part7 멀티모달 파이프라인", "멀티모달 스트리밍", "V2", "FT-INFRA", notes="J-069")
jm("§J-Part7 멀티모달 파이프라인", "멀티모달 에러 핸들링", "V1", "FT-FUNC", notes="J-070")

# J-Part8: 특화 도메인 멀티모달 (10)
jm("§J-Part8 도메인 멀티모달", "의료 이미지 분석", "V3", "FT-DOMAIN", notes="J-071")
jm("§J-Part8 도메인 멀티모달", "법률 문서 분석", "V2", "FT-DOMAIN", notes="J-072")
jm("§J-Part8 도메인 멀티모달", "교육 콘텐츠 생성", "V2", "FT-DOMAIN", notes="J-073")
jm("§J-Part8 도메인 멀티모달", "부동산 이미지 분석", "V2", "FT-DOMAIN", notes="J-074")
jm("§J-Part8 도메인 멀티모달", "패션/이커머스 이미지", "V3", "FT-DOMAIN", notes="J-075")
jm("§J-Part8 도메인 멀티모달", "건축/인테리어 시각화", "V3", "FT-DOMAIN", notes="J-076")
jm("§J-Part8 도메인 멀티모달", "과학 데이터 시각화", "V2", "FT-DOMAIN", notes="J-077")
jm("§J-Part8 도메인 멀티모달", "회의록 멀티모달 분석", "V1,V2", "FT-FUNC", notes="J-078")
jm("§J-Part8 도메인 멀티모달", "투자 멀티모달 분석", "V1", "FT-DOMAIN", notes="J-079")
jm("§J-Part8 도메인 멀티모달", "크리에이티브 AI 도구", "V3", "FT-FUNC", notes="J-080")

# J-Part9: 차별화 + 참고 (18)
jm("§J-Part9 차별화", "Google 대비 VAMOS 멀티모달 차별화", "V1,V2", "FT-FUNC", notes="J-081")
jm("§J-Part9 차별화", "OpenAI 대비 VAMOS 멀티모달 차별화", "V1,V2", "FT-FUNC", notes="J-082")
jm("§J-Part9 차별화", "로컬 멀티모달 처리 우위", "V1", "FT-FUNC", notes="J-083")
jm("§J-Part9 차별화", "통합 멀티모달 메모리", "V1,V2", "FT-FUNC", notes="J-084")
jm("§J-Part9 차별화", "투자 특화 멀티모달", "V1", "FT-DOMAIN", notes="J-085")
jm("§J-Part9 차별화", "VBS-11 멀티모달 벤치마크", "V2", "FT-TEST", notes="J-086")
jm("§J-Part9 차별화", "VBS-12 멀티모달 생성 벤치마크", "V2", "FT-TEST", notes="J-087")
jm("§J-Part9 차별화", "멀티모달 KPI", "V1", "FT-TEST", notes="J-088")
# 참고자료 (extractable=false)
jm_ref("§J-Part9 참고", "참고 기술/서비스 (J)", "V1", "FT-DOMAIN")
jm_ref("§J-Part9 참고", "참고 논문 (J)", "V1", "FT-DOMAIN")
jm("§J-Part9 로드맵", "V1 구현 로드맵 (J)", "V1", "FT-CFG", notes="J-091")
jm("§J-Part9 로드맵", "V2 구현 로드맵 (J)", "V2", "FT-CFG", notes="J-092")
jm("§J-Part9 로드맵", "V3 구현 로드맵 (J)", "V3", "FT-CFG", notes="J-093")
jm_ref("§J-Part9 참고", "참고 오픈소스 (J)", "V1", "FT-DOMAIN")
jm_ref("§J-Part9 참고", "참고 API (J)", "V1", "FT-DOMAIN")
jm_ref("§J-Part9 참고", "참고 데이터셋 (J)", "V1", "FT-DOMAIN")
jm("§J-Part9 크로스 레퍼런스", "크로스 레퍼런스 + KPI (J)", "V1", "FT-TEST", notes="J-097")
jm("§J-Part9 크로스 레퍼런스", "J 카테고리 우선순위 정리", "V1", "FT-CFG", notes="J-098")

j_count = len(features)
print(f"Cat J: {j_count} (target 98)")

# ===== CATEGORY K: 에이전트 프로토콜/상호운용성 (76건) =====

# K-Part1: MCP 생태계 (10)
jm("§K-Part1 MCP 생태계", "MCP 서버 기본 구현", "V1", "FT-API", notes="K-001")
jm("§K-Part1 MCP 생태계", "MCP 클라이언트 SDK", "V1", "FT-API", notes="K-002")
jm("§K-Part1 MCP 생태계", "MCP 도구 레지스트리", "V1", "FT-INFRA", notes="K-003")
jm("§K-Part1 MCP 생태계", "MCP 리소스 관리", "V1", "FT-INFRA", notes="K-004")
jm("§K-Part1 MCP 생태계", "MCP 프롬프트 관리", "V1", "FT-FUNC", notes="K-005")
jm("§K-Part1 MCP 생태계", "MCP 샘플링 구현", "V1,V2", "FT-FUNC", notes="K-006")
jm("§K-Part1 MCP 생태계", "MCP 보안 레이어", "V1", "FT-SEC", notes="K-007")
jm("§K-Part1 MCP 생태계", "MCP 마켓플레이스", "V2", "FT-INFRA", notes="K-008")
jm("§K-Part1 MCP 생태계", "MCP 모니터링/디버깅", "V1", "FT-INFRA", notes="K-009")
jm("§K-Part1 MCP 생태계", "MCP 버전 관리", "V1", "FT-CFG", notes="K-010")

# K-Part2: A2A + Multi-Agent (10)
jm("§K-Part2 A2A 프로토콜", "A2A Protocol 기본 구현", "V2", "FT-API", notes="K-011")
jm("§K-Part2 A2A 프로토콜", "Agent Card 시스템", "V2", "FT-FUNC", notes="K-012")
jm("§K-Part2 A2A 프로토콜", "A2A Task 관리", "V2", "FT-FUNC", notes="K-013")
jm("§K-Part2 A2A 프로토콜", "A2A Streaming 통신", "V2", "FT-INFRA", notes="K-014")
jm("§K-Part2 A2A 프로토콜", "A2A 보안 프레임워크", "V2", "FT-SEC", notes="K-015")
jm("§K-Part2 A2A 프로토콜", "에이전트 디스커버리", "V2", "FT-FUNC", notes="K-016")
jm("§K-Part2 A2A 프로토콜", "에이전트 신뢰 등급", "V2", "FT-SEC", notes="K-017")
jm("§K-Part2 A2A 프로토콜", "A2A 테스트 프레임워크", "V2", "FT-TEST", notes="K-018")
jm("§K-Part2 A2A 프로토콜", "에이전트 오케스트레이터", "V2", "FT-MOD", notes="K-019")
jm("§K-Part2 A2A 프로토콜", "에이전트 메시지 버스", "V2", "FT-INFRA", notes="K-020")

# K-Part3: 에이전트 프레임워크 통합 (10)
jm("§K-Part3 에이전트 프레임워크", "LangGraph 통합", "V1,V2", "FT-MOD", notes="K-021")
jm("§K-Part3 에이전트 프레임워크", "LangChain 도구 호환", "V1", "FT-MOD", notes="K-022")
jm("§K-Part3 에이전트 프레임워크", "LlamaIndex 통합", "V1,V2", "FT-MOD", notes="K-023")
jm("§K-Part3 에이전트 프레임워크", "Semantic Kernel 호환", "V2", "FT-MOD", notes="K-024")
jm("§K-Part3 에이전트 프레임워크", "CrewAI 역할 패턴 참조", "V2", "FT-MOD", notes="K-025")
jm("§K-Part3 에이전트 프레임워크", "AutoGen 대화 패턴 참조", "V2", "FT-MOD", notes="K-026")
jm("§K-Part3 에이전트 프레임워크", "DSPy 프롬프트 최적화 통합", "V2", "FT-FUNC", notes="K-027")
jm("§K-Part3 에이전트 프레임워크", "Haystack 파이프라인 호환", "V2", "FT-MOD", notes="K-028")
jm("§K-Part3 에이전트 프레임워크", "프레임워크 추상화 레이어", "V1", "FT-MOD", notes="K-029")
jm("§K-Part3 에이전트 프레임워크", "프레임워크 마이그레이션 도구", "V2", "FT-MIG", notes="K-030")

# K-Part4: 도구 통합 (10)
jm("§K-Part4 도구 통합", "Tool 등록/실행 프레임워크", "V1", "FT-FUNC", notes="K-031")
jm("§K-Part4 도구 통합", "Tool 인증/권한 관리", "V1", "FT-SEC", notes="K-032")
jm("§K-Part4 도구 통합", "Tool 결과 캐싱", "V1", "FT-INFRA", notes="K-033")
jm("§K-Part4 도구 통합", "Tool 에러 핸들링", "V1", "FT-FUNC", notes="K-034")
jm("§K-Part4 도구 통합", "커스텀 Tool SDK", "V2", "FT-API", notes="K-035")
jm("§K-Part4 도구 통합", "Tool 테스트 프레임워크", "V1", "FT-TEST", notes="K-036")
jm("§K-Part4 도구 통합", "Tool 모니터링", "V1", "FT-INFRA", notes="K-037")
jm("§K-Part4 도구 통합", "Tool 버전 관리", "V1", "FT-CFG", notes="K-038")
jm("§K-Part4 도구 통합", "Tool 문서 자동 생성", "V1", "FT-FUNC", notes="K-039")
jm("§K-Part4 도구 통합", "Tool 사용량 분석", "V2", "FT-FUNC", notes="K-040")

# K-Part5: 프로토콜 브릿지 (10)
jm("§K-Part5 프로토콜 브릿지", "MCP ↔ OpenAI Function Calling 브릿지", "V2", "FT-API", notes="K-041")
jm("§K-Part5 프로토콜 브릿지", "MCP ↔ Anthropic Tool Use 브릿지", "V1", "FT-API", notes="K-042")
jm("§K-Part5 프로토콜 브릿지", "REST API → MCP 자동 변환", "V1,V2", "FT-API", notes="K-043")
jm("§K-Part5 프로토콜 브릿지", "GraphQL → MCP 브릿지", "V2", "FT-API", notes="K-044")
jm("§K-Part5 프로토콜 브릿지", "gRPC → MCP 브릿지", "V2", "FT-API", notes="K-045")
jm("§K-Part5 프로토콜 브릿지", "WebSocket 프로토콜 브릿지", "V1", "FT-INFRA", notes="K-046")
jm("§K-Part5 프로토콜 브릿지", "이벤트 드리븐 통합", "V2", "FT-INFRA", notes="K-047")
jm("§K-Part5 프로토콜 브릿지", "프로토콜 변환 미들웨어", "V2", "FT-MOD", notes="K-048")
jm("§K-Part5 프로토콜 브릿지", "프로토콜 모니터링", "V1", "FT-INFRA", notes="K-049")
jm("§K-Part5 프로토콜 브릿지", "프로토콜 보안 게이트웨이", "V2", "FT-SEC", notes="K-050")

# K-Part6: 에이전트 거버넌스 + 차별화 (16)
jm("§K-Part6 거버넌스", "에이전트 라이프사이클 관리", "V2", "FT-FUNC", notes="K-051")
jm("§K-Part6 거버넌스", "에이전트 SLA 관리", "V2", "FT-CFG", notes="K-052")
jm("§K-Part6 거버넌스", "에이전트 감사 로깅", "V1", "FT-SEC", notes="K-053")
jm("§K-Part6 거버넌스", "에이전트 비용 할당", "V1", "FT-CFG", notes="K-054")
jm("§K-Part6 거버넌스", "에이전트 성능 SLO", "V2", "FT-CFG", notes="K-055")
jm("§K-Part6 거버넌스", "에이전트 장애 복구", "V1", "FT-INFRA", notes="K-056")
jm("§K-Part6 거버넌스", "에이전트 롤백", "V2", "FT-INFRA", notes="K-057")
jm("§K-Part6 거버넌스", "에이전트 멀티테넌시", "V3", "FT-INFRA", notes="K-058")
jm("§K-Part6 거버넌스", "Anthropic 대비 VAMOS 차별화", "V1", "FT-FUNC", conf="추론", notes="K-059")
jm("§K-Part6 거버넌스", "OpenAI 대비 VAMOS 차별화", "V1", "FT-FUNC", conf="추론", notes="K-060")
jm("§K-Part6 거버넌스", "LangChain 대비 VAMOS 차별화", "V1", "FT-FUNC", conf="추론", notes="K-061")
jm("§K-Part6 거버넌스", "VBS-10 프로토콜 벤치마크", "V2", "FT-TEST", notes="K-062")
# 참고자료 (extractable=false)
jm_ref("§K-Part6 참고", "참고 프레임워크 (K)", "V1", "FT-DOMAIN")
jm_ref("§K-Part6 참고", "참고 논문 (K)", "V1", "FT-DOMAIN")
jm_ref("§K-Part6 참고", "참고 표준 (K)", "V1", "FT-DOMAIN")
jm_ref("§K-Part6 참고", "참고 도구 (K)", "V1", "FT-DOMAIN")
jm("§K-Part6 로드맵", "V1 구현 로드맵 (K)", "V1", "FT-CFG", notes="K-067")
jm("§K-Part6 로드맵", "V2 구현 로드맵 (K)", "V2", "FT-CFG", notes="K-068")
jm("§K-Part6 로드맵", "V3 구현 로드맵 (K)", "V3", "FT-CFG", notes="K-069")
jm_ref("§K-Part6 참고", "참고 오픈소스 (K-070)", "V1", "FT-DOMAIN")
jm_ref("§K-Part6 참고", "참고 사례 (K-071)", "V1", "FT-DOMAIN")
jm_ref("§K-Part6 참고", "참고 표준문서 (K-072)", "V1", "FT-DOMAIN")
jm("§K-Part6 크로스 레퍼런스", "크로스 레퍼런스 + KPI (K)", "V1", "FT-TEST", notes="K-073")
jm("§K-Part6 크로스 레퍼런스", "K 카테고리 우선순위 정리", "V1", "FT-CFG", notes="K-074")
jm("§K-Part6 크로스 레퍼런스", "K 카테고리 의존성 맵", "V1", "FT-CFG", notes="K-075")
jm("§K-Part6 크로스 레퍼런스", "K 카테고리 리스크 분석", "V1", "FT-CFG", notes="K-076")

k_count = len(features) - j_count
print(f"Cat K: {k_count} (target 76)")

# ===== CATEGORY L: 개발자도구/API/SDK (56건) =====

# L-Part1: 코딩 어시스턴트 (16)
jm("§L-Part1 코딩 어시스턴트", "코드 자동완성", "V1", "FT-FUNC", notes="L-001")
jm("§L-Part1 코딩 어시스턴트", "코드 리뷰 AI", "V1,V2", "FT-FUNC", notes="L-002")
jm("§L-Part1 코딩 어시스턴트", "코드 설명 생성", "V1", "FT-FUNC", notes="L-003")
jm("§L-Part1 코딩 어시스턴트", "리팩토링 제안", "V1", "FT-FUNC", notes="L-004")
jm("§L-Part1 코딩 어시스턴트", "버그 탐지/수정", "V1", "FT-FUNC", notes="L-005")
jm("§L-Part1 코딩 어시스턴트", "테스트 코드 생성", "V1", "FT-FUNC", notes="L-006")
jm("§L-Part1 코딩 어시스턴트", "코드 변환 (언어 간)", "V2", "FT-FUNC", notes="L-007")
jm("§L-Part1 코딩 어시스턴트", "문서/주석 생성", "V1", "FT-FUNC", notes="L-008")
jm("§L-Part1 코딩 어시스턴트", "Git 커밋 메시지 생성", "V1", "FT-FUNC", notes="L-009")
jm("§L-Part1 코딩 어시스턴트", "PR 리뷰 자동화", "V2", "FT-FUNC", notes="L-010")
jm("§L-Part1 코딩 어시스턴트", "디버깅 어시스턴트", "V1", "FT-FUNC", notes="L-011")
jm("§L-Part1 코딩 어시스턴트", "아키텍처 분석", "V2", "FT-FUNC", notes="L-012")
jm("§L-Part1 코딩 어시스턴트", "의존성 분석", "V1", "FT-FUNC", notes="L-013")
jm("§L-Part1 코딩 어시스턴트", "보안 취약점 스캔", "V1,V2", "FT-SEC", notes="L-014")
jm("§L-Part1 코딩 어시스턴트", "성능 프로파일링", "V1", "FT-FUNC", notes="L-015")
jm("§L-Part1 코딩 어시스턴트", "코드 검색 시맨틱", "V1,V2", "FT-FUNC", notes="L-016")

# L-Part2: VAMOS API 설계 (8)
jm("§L-Part2 VAMOS API 설계", "GraphQL API", "V3", "FT-API", notes="L-017")
jm("§L-Part2 VAMOS API 설계", "API 문서 자동 생성", "V2", "FT-FUNC", notes="L-018")

# L-Part3: 플러그인/확장 시스템 (8)
jm("§L-Part3 플러그인/확장", "VAMOS 플러그인 아키텍처", "V2", "FT-MOD", notes="L-019")
jm("§L-Part3 플러그인/확장", "Hook 시스템", "V1,V2", "FT-MOD", notes="L-020")
jm("§L-Part3 플러그인/확장", "UI 컴포넌트 확장", "V2,V3", "FT-UI", notes="L-021")
jm("§L-Part3 플러그인/확장", "테마/스킨 시스템", "V1,V2", "FT-UI", notes="L-022")
jm("§L-Part3 플러그인/확장", "키보드 단축키 시스템", "V1", "FT-UI", notes="L-023")
jm("§L-Part3 플러그인/확장", "커맨드 팔레트", "V1", "FT-UI", notes="L-024")
jm("§L-Part3 플러그인/확장", "플러그인 샌드박스", "V2", "FT-SEC", notes="L-025")
jm("§L-Part3 플러그인/확장", "플러그인 개발 도구", "V2", "FT-FUNC", notes="L-026")

# L-Part4: 개발 인프라 도구 (8)
jm("§L-Part4 개발 인프라 도구", "데이터베이스 관리 도구", "V1", "FT-FUNC", notes="L-027")
jm("§L-Part4 개발 인프라 도구", "컨테이너/Docker 관리", "V1", "FT-INFRA", notes="L-028")
jm("§L-Part4 개발 인프라 도구", "클라우드 인프라 관리 IaC", "V2", "FT-INFRA", notes="L-029")
jm("§L-Part4 개발 인프라 도구", "성능 프로파일링 (L)", "V1", "FT-FUNC", notes="L-030")
jm("§L-Part4 개발 인프라 도구", "의존성 관리 (L)", "V1", "FT-FUNC", notes="L-031")
jm("§L-Part4 개발 인프라 도구", "API 테스트 도구", "V1", "FT-TEST", notes="L-032")
jm("§L-Part4 개발 인프라 도구", "문서 생성 자동화 (L)", "V1", "FT-FUNC", notes="L-033")
jm("§L-Part4 개발 인프라 도구", "개발 환경 관리", "V1", "FT-INFRA", notes="L-034")

# L-Part5: 차별화 (8)
jm("§L-Part5 차별화", "프로젝트 전체 이해 (Codebase Understanding)", "V1,V2", "FT-FUNC", notes="L-035")
jm("§L-Part5 차별화", "투자+코딩 통합", "V1", "FT-DOMAIN", notes="L-036")
jm("§L-Part5 차별화", "메모리 기반 개인화 코딩", "V1,V2", "FT-FUNC", notes="L-037")
jm("§L-Part5 차별화", "자율 코딩 에이전트", "V2", "FT-FUNC", notes="L-038")
jm("§L-Part5 차별화", "코드 보안 자동화", "V1,V2", "FT-SEC", notes="L-039")
jm("§L-Part5 차별화", "코드 품질 대시보드", "V2", "FT-UI", notes="L-040")
jm("§L-Part5 차별화", "실시간 협업 코딩", "V3", "FT-FUNC", notes="L-041")
jm("§L-Part5 차별화", "코드 벤치마크 VBS-13", "V2", "FT-TEST", notes="L-042")

# L-Part6: 개발자 경험 DX (8)
jm("§L-Part6 개발자 경험 DX", "온보딩 마법사", "V1", "FT-UI", notes="L-043")
jm("§L-Part6 개발자 경험 DX", "에러 메시지 개선", "V1", "FT-FUNC", impl="보강", notes="L-044")
jm("§L-Part6 개발자 경험 DX", "대화형 튜토리얼", "V1,V2", "FT-UI", notes="L-045")
jm("§L-Part6 개발자 경험 DX", "피드백 수집 시스템", "V1", "FT-FUNC", notes="L-046")
jm("§L-Part6 개발자 경험 DX", "성능 최적화 DX", "V1", "FT-INFRA", impl="보강", notes="L-047")
jm("§L-Part6 개발자 경험 DX", "접근성 (Accessibility for DX)", "V1", "FT-UI", notes="L-048")
jm("§L-Part6 개발자 경험 DX", "다국어 지원 DX", "V1", "FT-UI", notes="L-049")
jm("§L-Part6 개발자 경험 DX", "오프라인 모드", "V1", "FT-FUNC", notes="L-050")

# L-Part7: 참고/로드맵 (6)
jm_ref("§L-Part7 참고", "참고 도구/서비스 (L)", "V1", "FT-DOMAIN")
jm_ref("§L-Part7 참고", "참고 논문 (L)", "V1", "FT-DOMAIN")
jm("§L-Part7 로드맵", "V1 구현 로드맵 (L)", "V1", "FT-CFG", notes="L-053")
jm("§L-Part7 로드맵", "V2 구현 로드맵 (L)", "V2", "FT-CFG", notes="L-054")
jm("§L-Part7 로드맵", "V3 구현 로드맵 (L)", "V3", "FT-CFG", notes="L-055")
jm("§L-Part7 크로스 레퍼런스", "크로스 레퍼런스 + KPI (L)", "V1", "FT-TEST", notes="L-056")

l_count = len(features) - j_count - k_count
print(f"Cat L: {l_count} (target 56)")

# ===== CATEGORY M: PKM/지식관리 (54건) =====

# M-Part1: 지식 캡처 (10)
jm("§M-Part1 지식 캡처", "자동 지식 추출 파이프라인", "V1", "FT-FUNC", notes="M-001")
jm("§M-Part1 지식 캡처", "웹 클리핑 + AI 요약", "V1,V2", "FT-FUNC", notes="M-002")
jm("§M-Part1 지식 캡처", "문서 인제스트 파이프라인", "V1", "FT-FUNC", notes="M-003")
jm("§M-Part1 지식 캡처", "스크린 캡처 지식화", "V1,V2", "FT-FUNC", notes="M-004")
jm("§M-Part1 지식 캡처", "대화 히스토리 지식화", "V1", "FT-FUNC", notes="M-005")
jm("§M-Part1 지식 캡처", "이메일/메시지 지식 추출", "V2", "FT-FUNC", notes="M-006")
jm("§M-Part1 지식 캡처", "코드 지식 추출", "V1", "FT-FUNC", notes="M-007")
jm("§M-Part1 지식 캡처", "투자 지식 자동 축적", "V1", "FT-DOMAIN", notes="M-008")
jm("§M-Part1 지식 캡처", "음성 메모 → 지식", "V1", "FT-FUNC", notes="M-009")
jm("§M-Part1 지식 캡처", "RSS/뉴스피드 지식화", "V1", "FT-FUNC", notes="M-010")

# M-Part2: 지식 조직화 (10)
jm("§M-Part2 지식 조직화", "자동 태깅 + 분류", "V1", "FT-FUNC", notes="M-011")
jm("§M-Part2 지식 조직화", "지식그래프 자동 구축", "V1,V2", "FT-FUNC", notes="M-012")
jm("§M-Part2 지식 조직화", "폴더/노트북 구조", "V1", "FT-FUNC", notes="M-013")
jm("§M-Part2 지식 조직화", "Zettelkasten 방법론 구현", "V1", "FT-FUNC", notes="M-014")
jm("§M-Part2 지식 조직화", "시맨틱 중복 감지", "V1", "FT-FUNC", notes="M-015")
jm("§M-Part2 지식 조직화", "시간 기반 지식 관리", "V1", "FT-FUNC", notes="M-016")
jm("§M-Part2 지식 조직화", "지식 성숙도 추적", "V1", "FT-FUNC", notes="M-017")
jm("§M-Part2 지식 조직화", "멀티 계층 카테고리", "V1", "FT-FUNC", notes="M-018")
jm("§M-Part2 지식 조직화", "북마크/즐겨찾기 시스템", "V1", "FT-UI", notes="M-019")
jm("§M-Part2 지식 조직화", "지식 임포트/익스포트", "V1,V2", "FT-MIG", impl="마이그레이션", notes="M-020")

# M-Part3: 지식 검색+활용 (10)
jm("§M-Part3 지식 검색+활용", "시맨틱 지식 검색", "V1", "FT-FUNC", notes="M-021")
jm("§M-Part3 지식 검색+활용", "컨텍스트 인식 지식 추천", "V1,V2", "FT-FUNC", notes="M-022")
jm("§M-Part3 지식 검색+활용", "지식 기반 RAG 최적화", "V1", "FT-FUNC", notes="M-023")
jm("§M-Part3 지식 검색+활용", "질의응답 QA over Knowledge", "V1", "FT-FUNC", notes="M-024")
jm("§M-Part3 지식 검색+활용", "지식 요약 및 종합", "V1", "FT-FUNC", notes="M-025")
jm("§M-Part3 지식 검색+활용", "지식 연결 탐색", "V1,V2", "FT-FUNC", notes="M-026")
jm("§M-Part3 지식 검색+활용", "스마트 리마인더", "V1", "FT-FUNC", notes="M-027")
jm("§M-Part3 지식 검색+활용", "지식 공유 및 협업", "V2,V3", "FT-FUNC", notes="M-028")
jm("§M-Part3 지식 검색+활용", "지식 버전 관리", "V1,V3", "FT-FUNC", notes="M-029")
jm("§M-Part3 지식 검색+활용", "지식 통계/분석", "V1", "FT-FUNC", notes="M-030")

# M-Part4: 지식그래프 심화 (8)
jm("§M-Part4 지식그래프 심화", "자동 온톨로지 구축", "V1,V2", "FT-SCHEMA", notes="M-031")
jm("§M-Part4 지식그래프 심화", "그래프 추론", "V2", "FT-FUNC", notes="M-032")
jm("§M-Part4 지식그래프 심화", "그래프 질의 언어", "V1,V2", "FT-FUNC", notes="M-033")
jm("§M-Part4 지식그래프 심화", "그래프 시각화 인터랙션", "V1,V2,V3", "FT-UI", notes="M-034")
jm("§M-Part4 지식그래프 심화", "지식그래프 ↔ 벡터DB 하이브리드", "V1,V2", "FT-FUNC", notes="M-035")
jm("§M-Part4 지식그래프 심화", "그래프 자동 정리", "V2", "FT-FUNC", notes="M-036")
jm("§M-Part4 지식그래프 심화", "개인 위키", "V1,V2", "FT-FUNC", notes="M-037")
jm("§M-Part4 지식그래프 심화", "그래프 기반 추천", "V2", "FT-FUNC", notes="M-038")

# M-Part5: 차별화 (10)
jm("§M-Part5 차별화", "Notion AI 대비 VAMOS 차별화", "V1", "FT-DOMAIN", conf="추론", notes="M-039 차별화 전략")
jm("§M-Part5 차별화", "Obsidian+AI 대비 VAMOS 차별화", "V1", "FT-DOMAIN", conf="추론", notes="M-040 차별화 전략")
jm("§M-Part5 차별화", "Mem.ai 대비 VAMOS 차별화", "V1", "FT-DOMAIN", conf="추론", notes="M-041 차별화 전략")
jm("§M-Part5 차별화", "지식의 Dream Mode 처리", "V2", "FT-FUNC", notes="M-042")
jm("§M-Part5 차별화", "예측적 지식 서핑", "V2", "FT-FUNC", notes="M-043")
jm("§M-Part5 차별화", "지식 기반 개인 어시스턴트", "V1,V2", "FT-FUNC", notes="M-044")
jm("§M-Part5 차별화", "지식 기반 의사결정 지원", "V1", "FT-FUNC", notes="M-045")
jm("§M-Part5 차별화", "지식 기반 글쓰기 지원", "V1", "FT-FUNC", notes="M-046")
jm("§M-Part5 차별화", "2차 뇌 (Second Brain) 대시보드", "V1,V2", "FT-UI", notes="M-047")
jm("§M-Part5 차별화", "VBS-14 지식관리 벤치마크", "V2", "FT-TEST", notes="M-048")

# M-Part6: 참고/로드맵 (6)
jm_ref("§M-Part6 참고", "참고 서적 (M)", "V1", "FT-DOMAIN")
jm_ref("§M-Part6 참고", "참고 논문 (M)", "V1", "FT-DOMAIN")
jm_ref("§M-Part6 참고", "참고 도구 (M)", "V1", "FT-DOMAIN")
jm("§M-Part6 로드맵", "V1 구현 로드맵 (M)", "V1", "FT-CFG", notes="M-052")
jm("§M-Part6 로드맵", "V2/V3 구현 로드맵 (M)", "V2,V3", "FT-CFG", notes="M-053")
jm("§M-Part6 크로스 레퍼런스", "크로스 레퍼런스 + KPI (M)", "V1", "FT-TEST", notes="M-054")

m_count = len(features) - j_count - k_count - l_count
print(f"Cat M: {m_count} (target 54)")
jm_total = len(features)
print(f"STEP7_J-M total: {jm_total} (target 284)")

###############################################################################
# FILE 2: STEP7_N-P_보강 (204건)
###############################################################################

# ===== CATEGORY N: 워크플로우/RPA (44건) =====
n_items = [
    ("워크플로우 빌더 (노코드)", "V1,V2", "FT-UI"),
    ("워크플로우 템플릿 라이브러리", "V1", "FT-FUNC"),
    ("조건 분기 (IF/ELSE/SWITCH)", "V1", "FT-FUNC"),
    ("루프/반복 처리", "V1", "FT-FUNC"),
    ("외부 API 호출 통합", "V1", "FT-API"),
    ("파일 처리 자동화", "V1", "FT-FUNC"),
    ("이메일 자동화", "V1,V2", "FT-FUNC"),
    ("스케줄러 (Cron)", "V1", "FT-FUNC"),
    ("이벤트 트리거", "V1", "FT-FUNC"),
    ("워크플로우 모니터링", "V1", "FT-FUNC"),
    ("워크플로우 버전 관리", "V1", "FT-CFG"),
    ("워크플로우 공유/마켓플레이스", "V2", "FT-FUNC"),
    ("RPA 브라우저 자동화", "V1,V2", "FT-FUNC"),
    ("RPA 데스크톱 자동화", "V2", "FT-FUNC"),
    ("데이터 파이프라인", "V1,V2", "FT-FUNC"),
    ("ETL 도구", "V2", "FT-FUNC"),
    ("폼 자동 입력", "V1", "FT-FUNC"),
    ("문서 자동 생성 워크플로우", "V1", "FT-FUNC"),
    ("알림/통보 워크플로우", "V1", "FT-FUNC"),
    ("에러 핸들링 워크플로우", "V1", "FT-FUNC"),
    ("병렬 실행", "V2", "FT-FUNC"),
    ("Human-in-the-Loop", "V1", "FT-FUNC"),
    ("워크플로우 디버깅", "V1", "FT-FUNC"),
    ("워크플로우 성능 분석", "V2", "FT-FUNC"),
    ("워크플로우 보안", "V1", "FT-SEC"),
    ("워크플로우 감사 로깅", "V1", "FT-SEC"),
    ("Zapier/Make 호환 패턴", "V2", "FT-FUNC"),
    ("Slack/Discord 통합", "V1", "FT-FUNC"),
    ("Google Workspace 통합", "V1,V2", "FT-FUNC"),
    ("Microsoft 365 통합", "V2", "FT-FUNC"),
    ("Notion/Obsidian 통합", "V1,V2", "FT-FUNC"),
    ("GitHub/GitLab 통합", "V1", "FT-FUNC"),
    ("JIRA/Linear 통합", "V2", "FT-FUNC"),
    ("CRM 통합", "V3", "FT-FUNC"),
    ("ERP 통합", "V3", "FT-FUNC"),
    ("투자 워크플로우 특화", "V1", "FT-DOMAIN"),
    ("코딩 워크플로우 특화", "V1", "FT-DOMAIN"),
    ("리서치 워크플로우 특화", "V1", "FT-DOMAIN"),
    ("VBS-15 워크플로우 벤치마크", "V2", "FT-TEST"),
    ("워크플로우 차별화 전략", "V1", "FT-FUNC"),
    ("V1 워크플로우 로드맵", "V1", "FT-CFG"),
    ("V2 워크플로우 로드맵", "V2", "FT-CFG"),
    ("V3 워크플로우 로드맵", "V3", "FT-CFG"),
    ("워크플로우 KPI/크로스 레퍼런스", "V1", "FT-TEST"),
]
for nm, ver, cat in n_items:
    np_("§N 워크플로우/RPA", nm, ver, cat, notes=f"N-{n_items.index((nm,ver,cat))+1:03d}")

# ===== CATEGORY O: 교육/학습/자기개발 (36건) =====
o_items = [
    ("개인화 학습 경로", "V1,V2", "FT-FUNC"),
    ("AI 튜터 대화", "V1", "FT-FUNC"),
    ("플래시카드 자동 생성", "V1", "FT-FUNC"),
    ("간격 반복 (Spaced Repetition)", "V1", "FT-FUNC"),
    ("퀴즈 자동 생성", "V1", "FT-FUNC"),
    ("학습 진도 추적", "V1", "FT-FUNC"),
    ("학습 분석 대시보드", "V1,V2", "FT-UI"),
    ("소크라테스식 대화", "V1", "FT-FUNC"),
    ("코딩 실습 환경", "V1", "FT-FUNC"),
    ("프로젝트 기반 학습", "V2", "FT-FUNC"),
    ("동료 학습 매칭", "V3", "FT-FUNC"),
    ("언어 학습 특화", "V1,V2", "FT-DOMAIN"),
    ("투자 교육 특화", "V1", "FT-DOMAIN"),
    ("코딩 교육 특화", "V1", "FT-DOMAIN"),
    ("시험 준비 도우미", "V2", "FT-FUNC"),
    ("논문 읽기 도우미", "V1", "FT-FUNC"),
    ("독서 관리", "V1", "FT-FUNC"),
    ("학습 목표 관리", "V1", "FT-FUNC"),
    ("마이크로러닝", "V1", "FT-FUNC"),
    ("학습 동기 부여", "V1", "FT-FUNC"),
    ("학습 커뮤니티", "V3", "FT-FUNC"),
    ("인증/배지 시스템", "V2", "FT-FUNC"),
    ("강의 요약 자동 생성", "V1", "FT-FUNC"),
    ("필기 AI 보조", "V1,V2", "FT-FUNC"),
    ("학습 콘텐츠 큐레이션", "V1,V2", "FT-FUNC"),
    ("VBS-16 교육 벤치마크", "V2", "FT-TEST"),
    ("교육 차별화 전략", "V1", "FT-FUNC"),
    ("교육 컨텐츠 생성", "V2", "FT-FUNC"),
    ("교육 평가 도구", "V2", "FT-FUNC"),
    ("V1 교육 로드맵", "V1", "FT-CFG"),
    ("V2 교육 로드맵", "V2", "FT-CFG"),
    ("V3 교육 로드맵", "V3", "FT-CFG"),
    ("교육 도메인 연동", "V1", "FT-DOMAIN"),
    ("교육 접근성", "V1", "FT-UI"),
    ("교육 다국어 지원", "V1,V2", "FT-FUNC"),
    ("교육 KPI/크로스 레퍼런스", "V1", "FT-TEST"),
]
for i, (nm, ver, cat) in enumerate(o_items):
    np_("§O 교육/학습/자기개발", nm, ver, cat, notes=f"O-{i+1:03d}")

# ===== CATEGORY P: 건강/웰니스/감성AI (42건) =====
p_items = [
    ("감정 인식 시스템", "V1,V2", "FT-MOD"),
    ("감정 대응 대화", "V1", "FT-FUNC"),
    ("스트레스 관리 도우미", "V1", "FT-FUNC"),
    ("명상/마음챙김 가이드", "V1", "FT-FUNC"),
    ("수면 개선 도우미", "V1,V2", "FT-FUNC"),
    ("운동/피트니스 트래커", "V2", "FT-FUNC"),
    ("식단/영양 관리", "V2", "FT-FUNC"),
    ("습관 추적기", "V1", "FT-FUNC"),
    ("일기 작성 도우미", "V1", "FT-FUNC"),
    ("감정 일지 분석", "V1,V2", "FT-FUNC"),
    ("웰빙 대시보드", "V1,V2", "FT-UI"),
    ("디지털 디톡스 도우미", "V1", "FT-FUNC"),
    ("긍정 심리 코칭", "V1", "FT-FUNC"),
    ("목표 설정/추적", "V1", "FT-FUNC"),
    ("시간 관리 최적화", "V1", "FT-FUNC"),
    ("집중 모드 (포모도로)", "V1", "FT-FUNC"),
    ("에너지 관리", "V2", "FT-FUNC"),
    ("사회적 관계 관리", "V2", "FT-FUNC"),
    ("감성 AI 대화 스타일", "V1,V2", "FT-FUNC"),
    ("건강 데이터 통합", "V2", "FT-FUNC"),
    ("Apple Health/Google Fit 연동", "V2", "FT-FUNC"),
    ("Wearable 디바이스 연동", "V3", "FT-INFRA"),
    ("생체 데이터 분석", "V3", "FT-FUNC"),
    ("개인화 건강 인사이트", "V2", "FT-FUNC"),
    ("웰니스 알림", "V1", "FT-FUNC"),
    ("감정 기반 음악 추천", "V2", "FT-FUNC"),
    ("감정 기반 콘텐츠 추천", "V2", "FT-FUNC"),
    ("투자 심리 분석", "V1", "FT-DOMAIN"),
    ("번아웃 예방", "V1", "FT-FUNC"),
    ("감정적 투자 방지", "V1", "FT-DOMAIN"),
    ("VBS-17 웰니스 벤치마크", "V2", "FT-TEST"),
    ("웰니스 차별화 전략", "V1", "FT-FUNC"),
    ("프라이버시 최우선 건강 데이터", "V1", "FT-SEC"),
    ("건강 AI 윤리 가이드라인", "V2", "FT-SEC"),
    ("V1 웰니스 로드맵", "V1", "FT-CFG"),
    ("V2 웰니스 로드맵", "V2", "FT-CFG"),
    ("V3 웰니스 로드맵", "V3", "FT-CFG"),
    ("웰니스 도메인 연동", "V1", "FT-DOMAIN"),
    ("웰니스 다국어 지원", "V1,V2", "FT-FUNC"),
    ("웰니스 접근성", "V1", "FT-UI"),
    ("웰니스 커뮤니티", "V3", "FT-FUNC"),
    ("웰니스 KPI/크로스 레퍼런스", "V1", "FT-TEST"),
]
for i, (nm, ver, cat) in enumerate(p_items):
    np_("§P 건강/웰니스/감성AI", nm, ver, cat, notes=f"P-{i+1:03d}")

# ===== 보강 항목 (A~I, 70건) =====
bogang_items = [
    # A (코어/LLM) — 18건
    ("§보강A 코어/LLM", "MoA 실전 적용", "V2", "FT-FUNC", "S7-ADD-A01"),
    ("§보강A 코어/LLM", "Claude 4.6 Extended Thinking 활용", "V1", "FT-FUNC", "S7-ADD-A02"),
    ("§보강A 코어/LLM", "Gemini 2.5 Pro 100만 토큰 활용", "V2", "FT-FUNC", "S7-ADD-A03"),
    ("§보강A 코어/LLM", "Llama 4 Scout 로컬 활용", "V1", "FT-MOD", "S7-ADD-A04"),
    ("§보강A 코어/LLM", "Phi-4 Mini 초경량 로컬", "V1", "FT-MOD", "S7-ADD-A05"),
    ("§보강A 코어/LLM", "Qwen 3 한중일 특화", "V2", "FT-MOD", "S7-ADD-A06"),
    ("§보강A 코어/LLM", "MoE 라우팅 최적화", "V2", "FT-FUNC", "S7-ADD-A07"),
    ("§보강A 코어/LLM", "컨텍스트 캐싱 전략", "V1", "FT-INFRA", "S7-ADD-A08"),
    ("§보강A 코어/LLM", "구조화 출력 JSON Mode", "V1", "FT-FUNC", "S7-ADD-A09"),
    ("§보강A 코어/LLM", "함수 호출 병렬 실행", "V1", "FT-FUNC", "S7-ADD-A10"),
    ("§보강A 코어/LLM", "스트리밍 응답 최적화", "V1", "FT-FUNC", "S7-ADD-A11"),
    ("§보강A 코어/LLM", "프롬프트 최적화 DSPy", "V2", "FT-FUNC", "S7-ADD-A12"),
    ("§보강A 코어/LLM", "멀티모달 LLM 통합", "V1,V2", "FT-FUNC", "S7-ADD-A13"),
    ("§보강A 코어/LLM", "LLM 레이트리밋 관리", "V1", "FT-INFRA", "S7-ADD-A14"),
    ("§보강A 코어/LLM", "LLM 비용 추적 정밀화", "V1", "FT-CFG", "S7-ADD-A15"),
    ("§보강A 코어/LLM", "LLM 폴백 전략 고도화", "V1", "FT-INFRA", "S7-ADD-A16"),
    ("§보강A 코어/LLM", "한국어 프롬프트 최적화", "V1", "FT-FUNC", "S7-ADD-A17"),
    ("§보강A 코어/LLM", "LLM 벤치마크 자동화", "V2", "FT-TEST", "S7-ADD-A18"),
    # B (대화) — 8건
    ("§보강B 대화", "System Prompt 관리", "V1", "FT-CFG", "S7-ADD-B01"),
    ("§보강B 대화", "대화 분기 관리", "V1", "FT-FUNC", "S7-ADD-B02"),
    ("§보강B 대화", "대화 요약 압축", "V1", "FT-FUNC", "S7-ADD-B03"),
    ("§보강B 대화", "대화 내보내기", "V1", "FT-FUNC", "S7-ADD-B04"),
    ("§보강B 대화", "대화 검색", "V1", "FT-FUNC", "S7-ADD-B05"),
    ("§보강B 대화", "대화 템플릿", "V1", "FT-FUNC", "S7-ADD-B06"),
    ("§보강B 대화", "멀티턴 컨텍스트 최적화", "V1", "FT-FUNC", "S7-ADD-B07"),
    ("§보강B 대화", "대화 품질 자동 평가", "V2", "FT-TEST", "S7-ADD-B08"),
    # C (UI/UX) — 6건
    ("§보강C UI/UX", "다크모드/라이트모드", "V1", "FT-UI", "S7-ADD-C01"),
    ("§보강C UI/UX", "반응형 레이아웃", "V1", "FT-UI", "S7-ADD-C02"),
    ("§보강C UI/UX", "키보드 내비게이션", "V1", "FT-UI", "S7-ADD-C03"),
    ("§보강C UI/UX", "드래그앤드롭", "V1", "FT-UI", "S7-ADD-C04"),
    ("§보강C UI/UX", "실시간 마크다운 렌더링", "V1", "FT-UI", "S7-ADD-C05"),
    ("§보강C UI/UX", "코드 하이라이팅", "V1", "FT-UI", "S7-ADD-C06"),
    # D (메모리) — 6건
    ("§보강D 메모리", "메모리 검색 최적화", "V1", "FT-FUNC", "S7-ADD-D01"),
    ("§보강D 메모리", "메모리 자동 정리", "V1", "FT-FUNC", "S7-ADD-D02"),
    ("§보강D 메모리", "메모리 시각화", "V1,V2", "FT-UI", "S7-ADD-D03"),
    ("§보강D 메모리", "메모리 백업/복구", "V1", "FT-INFRA", "S7-ADD-D04"),
    ("§보강D 메모리", "메모리 공유 (V3)", "V3", "FT-FUNC", "S7-ADD-D05"),
    ("§보강D 메모리", "메모리 프라이버시", "V1", "FT-SEC", "S7-ADD-D06"),
    # E (보안) — 6건
    ("§보강E 보안", "API 키 관리", "V1", "FT-SEC", "S7-ADD-E01"),
    ("§보강E 보안", "데이터 암호화 AES-256", "V1", "FT-SEC", "S7-ADD-E02"),
    ("§보강E 보안", "입력 검증 (Injection 방지)", "V1", "FT-SEC", "S7-ADD-E03"),
    ("§보강E 보안", "감사 로깅 보안", "V1", "FT-SEC", "S7-ADD-E04"),
    ("§보강E 보안", "RBAC 구현", "V1,V2", "FT-SEC", "S7-ADD-E05"),
    ("§보강E 보안", "제로트러스트 아키텍처", "V2", "FT-SEC", "S7-ADD-E06"),
    # F (인프라) — 8건
    ("§보강F 인프라", "LiteLLM Proxy 통합", "V1", "FT-INFRA", "S7-ADD-F01"),
    ("§보강F 인프라", "Redis 캐싱 고도화", "V1", "FT-INFRA", "S7-ADD-F02"),
    ("§보강F 인프라", "Qdrant 벡터DB 최적화", "V1", "FT-INFRA", "S7-ADD-F03"),
    ("§보강F 인프라", "NetworkX KG 최적화", "V1", "FT-INFRA", "S7-ADD-F04"),
    ("§보강F 인프라", "Ollama 0.5+ 멀티모달", "V1", "FT-INFRA", "S7-ADD-F05"),
    ("§보강F 인프라", "GGUF Q4_K_M 양자화", "V1", "FT-INFRA", "S7-ADD-F06"),
    ("§보강F 인프라", "1-bit LLM (BitNet)", "V3", "FT-INFRA", "S7-ADD-F07"),
    ("§보강F 인프라", "Infini-Attention", "V3", "FT-INFRA", "S7-ADD-F08"),
    # G (벤치마크) — 6건
    ("§보강G 벤치마크", "SWE-Bench 최신 변형", "V1", "FT-TEST", "S7-ADD-G01"),
    ("§보강G 벤치마크", "MoA 평가 기준", "V2", "FT-TEST", "S7-ADD-G02"),
    ("§보강G 벤치마크", "ARC-AGI 벤치마크", "V2", "FT-TEST", "S7-ADD-G03"),
    ("§보강G 벤치마크", "BFCL v3 (Berkeley Function Calling)", "V1", "FT-TEST", "S7-ADD-G04"),
    ("§보강G 벤치마크", "PolyBench", "V2", "FT-TEST", "S7-ADD-G05"),
    ("§보강G 벤치마크", "MMLU-Pro", "V2", "FT-TEST", "S7-ADD-G06"),
    # H (비즈니스) — 6건
    ("§보강H 비즈니스", "2025 AI 시장 데이터 업데이트", "V1", "FT-CFG", "S7-ADD-H01"),
    ("§보강H 비즈니스", "VAMOS 가격 전략 업데이트", "V1", "FT-CFG", "S7-ADD-H02"),
    ("§보강H 비즈니스", "MCP 생태계 수익 모델", "V2", "FT-CFG", "S7-ADD-H03"),
    ("§보강H 비즈니스", "AI Agent 마켓플레이스", "V3", "FT-CFG", "S7-ADD-H04"),
    ("§보강H 비즈니스", "B2B 컨설팅 모델", "V3", "FT-CFG", "S7-ADD-H05"),
    ("§보강H 비즈니스", "오픈소스 듀얼 라이선스", "V2", "FT-CFG", "S7-ADD-H06"),
    # I (투자) — 6건
    ("§보강I 투자", "AI 기반 개인 데이터 분석 투자", "V1", "FT-DOMAIN", "S7-ADD-I01"),
    ("§보강I 투자", "LLM 기반 실적 콜 분석", "V2", "FT-DOMAIN", "S7-ADD-I02"),
    ("§보강I 투자", "OpenBB v4 통합", "V1", "FT-DOMAIN", "S7-ADD-I03"),
    ("§보강I 투자", "FinGPT 활용", "V2", "FT-MOD", "S7-ADD-I04"),
    ("§보강I 투자", "SEC 13F 자동 분석", "V2", "FT-DOMAIN", "S7-ADD-I05"),
    ("§보강I 투자", "크립토 온체인 분석", "V3", "FT-DOMAIN", "S7-ADD-I06"),
]
for section, nm, ver, cat, note in bogang_items:
    np_(section, nm, ver, cat, impl="보강", notes=note)

# ===== 독자 혁신 아이디어 (12건) =====
innov_items = [
    ("Dream Mode (백그라운드 자기진화)", "V2", "FT-FUNC", "S7-INNOV-01 CRITICAL"),
    ("Predictive AI (예측형 AI 어시스턴트)", "V2", "FT-FUNC", "S7-INNOV-02"),
    ("Cross-Device Seamless State Sync", "V3", "FT-INFRA", "S7-INNOV-03"),
    ("Personal Data Analytics Dashboard", "V2", "FT-UI", "S7-INNOV-04"),
    ("Self-Evolving Agent Architecture", "V2", "FT-MOD", "S7-INNOV-05 CRITICAL"),
    ("Ambient Intelligence (앰비언트 인텔리전스)", "V2", "FT-FUNC", "S7-INNOV-06"),
    ("Collaborative Multi-User AI", "V3", "FT-INFRA", "S7-INNOV-07"),
    ("Time-Travel Debugging", "V2", "FT-FUNC", "S7-INNOV-08"),
    ("AI Personality Evolution", "V1", "FT-FUNC", "S7-INNOV-09"),
    ("감정적 투자 방지 시스템", "V1", "FT-DOMAIN", "S7-INNOV-10 CRITICAL"),
    ("지식-투자-코딩 통합 원스톱", "V1", "FT-FUNC", "S7-INNOV-11 CRITICAL"),
    ("로컬 우선 프라이버시", "V1", "FT-SEC", "S7-INNOV-12 CRITICAL"),
]
for nm, ver, cat, note in innov_items:
    np_("§독자 혁신 아이디어", nm, ver, cat, notes=note)

np_total = len(features) - jm_total
print(f"STEP7_N-P total: {np_total} (target 204)")

###############################################################################
# FILE 3: STEP7_보강_통합 (73건)
###############################################################################
bg_items = [
    # §1.2 Part F 혁신기술 (9건)
    ("§1.2 Part F 혁신기술", "Digital Twin 사용자 모델링", "V1,V2", "FT-FUNC", "S7-F-023"),
    ("§1.2 Part F 혁신기술", "Local+Cloud 하이브리드 실행 (HybridRouter)", "V1,V2", "FT-INFRA", "S7-F-024"),
    ("§1.2 Part F 혁신기술", "Confidence-based 응답 전략", "V1,V2", "FT-FUNC", "S7-F-025"),
    ("§1.2 Part F 혁신기술", "Causal Reasoning Engine", "V1,V2", "FT-FUNC", "S7-F-030"),
    ("§1.2 Part F 혁신기술", "Continual Learning 프레임워크", "V2", "FT-FUNC", "S7-F-040"),
    ("§1.2 Part F 혁신기술", "Privacy-Preserving Learning", "V2", "FT-SEC", "S7-F-045"),
    ("§1.2 Part F 혁신기술", "Rollback / Version Control (시스템 상태)", "V2", "FT-INFRA", "S7-F-050"),
    ("§1.2 Part F 혁신기술", "Dream Mode (비활성 시간 자기진화)", "V2", "FT-FUNC", "S7-F-055"),
    ("§1.2 Part F 혁신기술", "Dream Mode 지식 정리", "V1", "FT-FUNC", "S7-F-060"),
    # §1.3 경쟁사 참조 (9건)
    ("§1.3 Grok 참조", "Grok 실시간 소셜 데이터 연동 패턴", "V2", "FT-FUNC", "S7-G-003"),
    ("§1.3 Grok 참조", "Grok 유머/캐릭터 어시스턴트", "V2", "FT-FUNC", "S7-G-007"),
    ("§1.3 Apple 온디바이스", "Apple Intelligence 3단계 처리 계층 참조", "V1", "FT-INFRA", "S7-K-005"),
    ("§1.3 Computer Use", "브라우저 에이전트 Playwright 통합", "V1", "FT-MOD", "S7-L-003"),
    ("§1.3 Multi-Agent", "Swarm 오케스트레이션 패턴", "V2", "FT-FUNC", "S7-O-004"),
    ("§1.3 Multi-Agent", "A2A Protocol 실전 활용", "V2", "FT-API", "S7-O-008"),
    ("§1.3 RAG 최신기술", "GraphRAG 구현", "V2", "FT-FUNC", "S7-P-005"),
    ("§1.3 RAG 최신기술", "Self-RAG (자기 반성 RAG)", "V1,V2", "FT-FUNC", "S7-P-007"),
    ("§1.3 RAG 최신기술", "ColPali / Late Interaction 검색", "V2", "FT-FUNC", "S7-P-009"),
    # §2 카테고리F 인프라/배포 (8건)
    ("§2 카테고리F", "CI/CD 파이프라인", "V1,V2", "FT-INFRA", "S7F-001"),
    ("§2 카테고리F", "Docker Compose 로컬 개발 환경", "V1", "FT-INFRA", "S7F-003"),
    ("§2 카테고리F", "모델 라우팅 엔진 (ModelRouter)", "V1", "FT-INFRA", "S7F-005"),
    ("§2 카테고리F", "모니터링 스택", "V1", "FT-INFRA", "S7F-008"),
    ("§2 카테고리F", "Kubernetes 배포 매니페스트", "V2", "FT-INFRA", "S7F-020"),
    ("§2 카테고리F", "자동 스케일링 (HPA+KEDA)", "V2", "FT-INFRA", "S7F-025"),
    ("§2 카테고리F", "비용 최적화 엔진 (CostOptimizer)", "V1", "FT-FUNC", "S7F-030"),
    ("§2 카테고리F", "로깅/트레이싱 통합", "V1", "FT-INFRA", "S7F-035"),
    # §3 카테고리G 벤치마크/평가 (4건)
    ("§3 카테고리G", "응답 품질 자동 평가 (QoD)", "V1,V2,V3", "FT-TEST", "S7G-001"),
    ("§3 카테고리G", "할루시네이션 탐지 (HallucinationDetector)", "V1", "FT-FUNC", "S7G-005"),
    ("§3 카테고리G", "SWE-Bench 대응", "V1,V2,V3", "FT-TEST", "S7G-012"),
    ("§3 카테고리G", "도메인별 벤치마크 (VAMOS Benchmark Suite)", "V2", "FT-TEST", "S7G-020"),
    # §4 카테고리H 비즈니스모델 (3건)
    ("§4 카테고리H", "가격 전략 (3-Tier 가격 모델)", "V1,V2,V3", "FT-CFG", "S7H-001"),
    ("§4 카테고리H", "V1 MVP 정의", "V1", "FT-CFG", "S7H-010"),
    ("§4 카테고리H", "시장 분석 (TAM/SAM/SOM + 경쟁 매트릭스)", "V1", "FT-CFG", "S7H-020"),
    # §5 카테고리I AI Investing (4건)
    ("§5 카테고리I", "실시간 데이터 스트리밍 (Stream Gateway)", "V1,V2", "FT-FUNC", "S7I-010"),
    ("§5 카테고리I", "FinBERT 감성 분석", "V1", "FT-DOMAIN", "S7I-020"),
    ("§5 카테고리I", "백테스팅 고급", "V1", "FT-DOMAIN", "S7I-035"),
    ("§5 카테고리I", "대안 데이터 (Alternative Data)", "V2,V3", "FT-DOMAIN", "S7I-050"),
    # §6 카테고리J 멀티모달 (10건)
    ("§6 카테고리J", "이미지 생성 모델 통합 게이트웨이", "V2", "FT-FUNC", "J-011 보강", "추론"),
    ("§6 카테고리J", "이미지 편집 (인페인팅/아웃페인팅)", "V2", "FT-FUNC", "J-013 보강", "추론"),
    ("§6 카테고리J", "투자 차트 자동 생성", "V1,V2", "FT-UI", "J-015 보강", "추론"),
    ("§6 카테고리J", "STT (Speech-to-Text) 통합", "V1,V2", "FT-FUNC", "J-021 보강"),
    ("§6 카테고리J", "TTS (Text-to-Speech) 통합", "V1,V2", "FT-FUNC", "J-025 보강"),
    ("§6 카테고리J", "음성 대화 모드 (Voice Chat)", "V1,V2", "FT-FUNC", "J-028 보강"),
    ("§6 카테고리J", "비디오 입력 분석", "V2", "FT-FUNC", "J-031 보강", "추론"),
    ("§6 카테고리J", "데이터 시각화 자동 생성", "V1,V2", "FT-UI", "J-035 보강", "추론"),
    ("§6 카테고리J", "PDF 분석 파이프라인", "V1", "FT-FUNC", "J-041 보강", "추론"),
    ("§6 카테고리J", "코드 생성/편집 멀티모달", "V2", "FT-FUNC", "J-045 보강", "추론"),
    # §7 카테고리K 에이전트프로토콜 (7건)
    ("§7 카테고리K", "LangGraph 에이전트 오케스트레이션", "V1,V2", "FT-MOD", "K-021 보강"),
    ("§7 카테고리K", "CrewAI 역할 기반 에이전트 참조", "V2", "FT-MOD", "K-025 보강", "추론"),
    ("§7 카테고리K", "AutoGen 대화 패턴 참조", "V2", "FT-MOD", "K-028 보강"),
    ("§7 카테고리K", "MCP Tool Marketplace 구현", "V2", "FT-INFRA", "K-031 보강", "추론"),
    ("§7 카테고리K", "커스텀 Tool 개발 SDK", "V2", "FT-API", "K-035 보강", "추론"),
    ("§7 카테고리K", "MCP ↔ OpenAI Function Calling 브릿지", "V2", "FT-API", "K-041 보강", "추론"),
    ("§7 카테고리K", "REST API ↔ MCP 자동 변환", "V1,V2", "FT-API", "K-043 보강"),
    # §8 카테고리L 개발자도구 (5건)
    ("§8 카테고리L", "REST API 설계 (VAMOS API v1)", "V1,V2", "FT-API", "L-001 보강"),
    ("§8 카테고리L", "Python SDK (vamos-sdk)", "V1", "FT-API", "L-005 보강"),
    ("§8 카테고리L", "문서 자동 생성", "V1", "FT-INFRA", "L-010 보강"),
    ("§8 카테고리L", "Webhook 시스템", "V1", "FT-API", "L-020 보강"),
    ("§8 카테고리L", "IDE 플러그인 (VSCode Extension)", "V2,V3", "FT-UI", "L-030 보강"),
    # §9 카테고리M PKM/지식관리 (3건)
    ("§9 카테고리M", "지식 자동 축적 시스템", "V1", "FT-FUNC", "M-001 보강"),
    ("§9 카테고리M", "Obsidian 통합 (MCP 서버+플러그인)", "V1,V2", "FT-MOD", "M-005 보강"),
    ("§9 카테고리M", "마인드맵 자동 생성", "V1", "FT-UI", "M-015 보강"),
    # §10 보강 추가항목 (11건)
    ("§10 추가항목", "추론 UX 패턴 (Thinking 블록 UI)", "V2", "FT-UI", "B-ADD-03"),
    ("§10 추가항목", "A2A 대화 패턴 UX", "V2", "FT-UI", "B-ADD-05"),
    ("§10 추가항목", "NotebookLM Audio Overview UI", "V2", "FT-UI", "C-ADD-01"),
    ("§10 추가항목", "Microsoft Recall 로컬 구현", "V2", "FT-FUNC", "D-ADD-01"),
    ("§10 추가항목", "MemGPT/Letta 패턴 적용", "V2", "FT-FUNC", "D-ADD-04"),
    ("§10 추가항목", "A2A 보안 프레임워크", "V2", "FT-SEC", "E-ADD-01"),
    ("§10 추가항목", "PagedAttention / vLLM 최적화", "V2", "FT-INFRA", "F-ADD-01"),
    ("§10 추가항목", "Speculative Decoding", "V2", "FT-INFRA", "F-ADD-05"),
    ("§10 추가항목", "BFCL v3 (Function Calling 벤치마크)", "V1,V2", "FT-TEST", "G-ADD-04"),
    ("§10 추가항목", "VAMOS 가격 전략 상세", "V1,V2", "FT-CFG", "H-ADD-02"),
    ("§10 추가항목", "OpenBB v4 통합 (보강)", "V1,V2", "FT-DOMAIN", "I-ADD-03"),
]
for item in bg_items:
    if len(item) == 6:
        section, nm, ver, cat, note, conf = item
        bg(section, nm, ver, cat, impl="보강", notes=note, conf=conf)
    else:
        section, nm, ver, cat, note = item
        bg(section, nm, ver, cat, impl="보강", notes=note)

bg_total = len(features) - jm_total - np_total
print(f"STEP7_보강 total: {bg_total} (target 73)")
print(f"Grand total: {len(features)} (target 561)")

###############################################################################
# Statistics
###############################################################################
cat_counter = Counter(f["category"] for f in features)
ver_counter = Counter(f["version_scope"] for f in features)
impl_counter = Counter(f["implementation_type"] for f in features)
conf_counter = Counter(f["confidence"] for f in features)
ext_true = sum(1 for f in features if f["extractable"])
ext_false = sum(1 for f in features if not f["extractable"])

src_counter = {"STEP7_J-M": jm_total, "STEP7_N-P": np_total, "STEP7_보강": bg_total}

###############################################################################
# C-9a statistics (for merged report)
###############################################################################
c9a_stats = {
    "total_features": 997,
    "extractable_true": 488,
    "extractable_false": 509,
}

merged_total = len(features) + c9a_stats["total_features"]
merged_ext_true = ext_true + c9a_stats["extractable_true"]
merged_ext_false = ext_false + c9a_stats["extractable_false"]

###############################################################################
# Build output JSON
###############################################################################
output = {
    "agent_id": "C-9b",
    "source_files": [
        {"source_file": "STEP7_J-M", "source_path": "D:\\VAMOS\\docs\\sot\\VAMOS_STEP7_J-M_상세명세서.md", "feature_id_prefix": "S7JM"},
        {"source_file": "STEP7_N-P", "source_path": "D:\\VAMOS\\docs\\sot\\VAMOS_STEP7_N-P_보강_상세명세서.md", "feature_id_prefix": "S7NP"},
        {"source_file": "STEP7_보강", "source_path": "D:\\VAMOS\\docs\\sot\\VAMOS_STEP7_보강_통합명세서.md", "feature_id_prefix": "S7BG"}
    ],
    "extraction_date": str(date.today()),
    "reading_completion_report": {
        "STEP7_J-M": {
            "total_lines": 1824, "lines_read": 1824, "reading_rate": "100%",
            "read_ranges": ["1-500", "501-1000", "1001-1500", "1501-1824"],
            "unread_areas": [], "last_line_read": "1824",
            "last_line_content": "<!-- END OF DOCUMENT -->"
        },
        "STEP7_N-P": {
            "total_lines": 1809, "lines_read": 1809, "reading_rate": "100%",
            "read_ranges": ["1-500", "501-1000", "1001-1500", "1501-1809"],
            "unread_areas": [], "last_line_read": "1809",
            "last_line_content": "<!-- END OF DOCUMENT -->"
        },
        "STEP7_보강": {
            "total_lines": 1523, "lines_read": 1523, "reading_rate": "100%",
            "read_ranges": ["1-500", "501-1000", "1001-1523"],
            "unread_areas": [], "last_line_read": "1523",
            "last_line_content": "<!-- END OF DOCUMENT -->"
        }
    },
    "statistics": {
        "total_features": len(features),
        "by_source": src_counter,
        "extractable_true": ext_true,
        "extractable_false": ext_false,
        "by_category": dict(sorted(cat_counter.items())),
        "by_version_scope": dict(sorted(ver_counter.items())),
        "by_implementation_type": dict(sorted(impl_counter.items())),
        "confidence_explicit": conf_counter.get("명시적", 0),
        "confidence_inferred": conf_counter.get("추론", 0),
        "v_unknown_count": 0,
        "judgment_needed_count": 0
    },
    "c9a_c9b_merged_statistics": {
        "c9a_total": c9a_stats["total_features"],
        "c9b_total": len(features),
        "merged_total": merged_total,
        "merged_extractable_true": merged_ext_true,
        "merged_extractable_false": merged_ext_false,
        "note": "STEP7 전체(A~P+보강) 합산. C-9a=A-I(997건), C-9b=J-P+보강(561건)"
    },
    "features": features
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nOutput: {OUTPUT}")
print(f"Total: {len(features)} | By src: {src_counter}")
print(f"Extractable: true={ext_true}, false={ext_false}")
print(f"By category: {dict(sorted(cat_counter.items()))}")
print(f"By version: {dict(sorted(ver_counter.items()))}")
print(f"Confidence: 명시적={conf_counter.get('명시적',0)}, 추론={conf_counter.get('추론',0)}")
print(f"\n=== C-9a + C-9b Merged ===")
print(f"Total: {merged_total} | Extractable: true={merged_ext_true}, false={merged_ext_false}")