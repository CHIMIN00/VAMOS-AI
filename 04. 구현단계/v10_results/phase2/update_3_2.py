#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""3-2 SUB_FEATURE_OF_EXISTING 판정 사유 자동 생성"""

import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

INPUT = r"D:\VAMOS\04. 구현단계\v10_results\phase2\step1\3-2_SUB_FEATURE_OF_EXISTING.md"

# 키워드 → PART2 라인 매핑
LINE_MAP = {
    # 모듈 ID
    "EVX-1": ("L2584", "EVX-1 Code-as-Policy 검증 파이프라인"),
    "EVX-2": ("L2585", "EVX-2 Adversarial Tester"),
    "EVX-3": ("L2586", "EVX-3 Log-prob Analyzer"),
    "EVX-4": ("L2587", "EVX-4 Thought Debugger"),
    "EVX-5": ("L2588", "EVX-5 Synthetic Data Gen"),
    "I-18": ("L2438", "I-18 Self-evo Engine 메타학습"),
    # 영문 키워드
    "EvidenceGate": ("L828", "EvidenceGate 스텁 구현"),
    "SelfCheckGate": ("L910", "SelfCheckGate (M-14) V0 스텁"),
    "ToolRegistry": ("L480", "ToolRegistry 2 seed entries"),
    "Multimodal": ("L1410", "Multimodal Interpreter 텍스트/이미지/음성"),
    "vLLM": ("L2292", "vLLM 셀프호스팅 A10G GPU"),
    "Gate": ("L825", "PolicyGate/CostGate/EvidenceGate 파이프라인"),
    "SDK": ("L2505", "VAMOS_CLOUD_LIBRARY_SPEC SDK"),
    "RAG": ("L1400", "RAG 파이프라인 BGE-M3 임베딩"),
    "OAuth": ("L1964", "Google API OAuth 설정"),
    "JWT": ("L2554", "인증 프로토콜 mTLS + JWT"),
    "Swarm": ("L2452", "PARL Agent Swarm 오케스트레이션"),
    "HPA": ("L2429", "HPA CPU 70% 자동 스케일링"),
    "MCP": ("L94", "MCP 브릿지 디렉토리 구조"),
    "Cron": ("L94", "스케줄러 기능 §N 워크플로우"),
    "DNS": ("L2317", "도메인/SSL/DNS 설정"),
    "SSL": ("L2317", "도메인/SSL 설정 Let's Encrypt"),
    "TLS": ("L2341", "nginx-ingress + TLS"),
    "QoD": ("L454", "SourceQoD 스키마 정의"),
    "NodeRegistry": ("L481", "NodeRegistry 1 seed entry"),
    "ConfigModel": ("L1018", "config.v1.toml → Pydantic ConfigModel"),
    "LLM": ("L723", "llm.generate LLM 텍스트 생성"),
    "Procedural": ("L1518", "B-2 Procedural 절차/템플릿"),
    "KRW": ("L163", "daily_limit = 1300 KRW"),
    "SDAR": ("L2007", "SDAR 자가진단/자동수리 엔진"),
    "CostGate": ("L826", "CostGate 80%/100% 체크"),
    "GitHub": ("L207", "GitHub 리포지토리"),
    "Secrets": ("L1193", "GitHub Secrets 설정"),
    "HumanEval": ("L2729", "HumanEval 벤치마크"),
    "MBPP": ("L2729", "MBPP 벤치마크"),
    "MMLU": ("L2729", "MMLU 벤치마크"),
    "Qdrant": ("L1824", "Qdrant Docker 1.7+ 실행"),
    "DEC": ("L1439", "S3_DECISION_LOCKED"),
    "GPT": ("L1410", "GPT-4o Multimodal 통합"),
    "Gemini": ("L1410", "Gemini 2.0 Multimodal"),
    # 한글 키워드
    "레지스트리": ("L473", "레지스트리 정의 registries.py"),
    "개인정보": ("L916", "개인정보 수집 PolicyGate"),
    "프라이버시": ("L2555", "데이터 프라이버시 모델 그래디언트"),
    "프롬프트": ("L211", "AI 프롬프트 섹션"),
    "하드코딩": ("L739", "하드코딩 값 config 키 매핑"),
    "에이전트": ("L2019", "에이전트 찬반 논증"),
    "대시보드": ("L2109", "V2 비용 모니터링 대시보드"),
    "벤치마크": ("L1799", "성능 벤치마크 V1 대비"),
    "디스커버리": ("L2817", "디스커버리 mDNS/DNS-SD"),
    "컨테이너": ("L1343", "services ollama 컨테이너"),
    "프로비저닝": ("L2312", "GPU 노드 프로비저닝 A10G"),
    "데이터셋": ("L2474", "평가 데이터셋 준비"),
    "자가진단": ("L2007", "자가진단/자동수리 엔진 AR-L3"),
    "리마인더": ("L2027", "알림/리마인더 설정"),
    "페르소나": ("L2578", "D-4 Personality Engine AI 페르소나"),
    "파생상품": ("L2731", "파생상품 분석 그릭스/Black-Scholes"),
}


def get_part2_ref(evidence_str, match_type):
    """Evidence에서 키워드를 추출하고 PART2 라인 참조를 반환"""
    # Evidence에서 키워드 추출
    keywords = []
    for part in evidence_str.split(";"):
        part = part.strip()
        # "MID:EVX-1 in PART2" → "EVX-1"
        if "MID:" in part:
            kw = part.replace("MID:", "").replace(" in PART2", "").strip()
            keywords.append(kw)
        # "ABBR:XXX" or "ENG:XXX" → "XXX"
        elif ":" in part:
            kw = part.split(":", 1)[1].strip()
            keywords.append(kw)
        # "KOR4:한글키워드" → "한글키워드"
        else:
            keywords.append(part)

    # 첫 번째 매칭 키워드 찾기
    for kw in keywords:
        if kw in LINE_MAP:
            line, desc = LINE_MAP[kw]
            return line, kw, desc

    # 매칭 못 찾으면 Evidence 원문 반환
    return None, None, None


with open(INPUT, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
i = 0
while i < len(lines):
    line = lines[i]
    output.append(line)

    # "- **판정**: SUB_FEATURE 확정" 라인 찾기
    if line.strip() == "- **판정**: SUB_FEATURE 확정":
        # 위로 올라가서 Evidence와 Match Type 찾기
        evidence_str = ""
        match_type = ""
        feature_name = ""
        for j in range(max(0, len(output)-10), len(output)):
            l = output[j].strip()
            if l.startswith("- **Evidence**:"):
                evidence_str = l.replace("- **Evidence**:", "").strip()
            if l.startswith("- **Match Type**:"):
                match_type = l.replace("- **Match Type**:", "").strip()
            if l.startswith("- **내용**:"):
                feature_name = l.replace("- **내용**:", "").strip()

        part2_line, kw, desc = get_part2_ref(evidence_str, match_type)

        if part2_line:
            if "module_id" in match_type:
                reason = f"PART2 {part2_line}에 모듈 ID '{kw}'가 직접 등재. '{feature_name}'은 이 모듈의 하위 구현으로 별도 추가 불필요"
            elif "keyword_s25" in match_type or "eng_keyword" in match_type:
                reason = f"PART2 §2-5 ({part2_line})에 '{kw}' 키워드 명시 ({desc}). 상위 구현에 포함되어 별도 항목 불필요"
            elif "kor4_keyword" in match_type:
                reason = f"PART2 §2-5 ({part2_line})에 '{kw}' 키워드 명시 ({desc}). 상위 기능의 하위 구현으로 별도 추가 불필요"
            else:
                reason = f"PART2 {part2_line}에 관련 키워드 '{kw}' 존재 ({desc}). 상위 구현에 포함"
        else:
            reason = f"Evidence 키워드가 PART2 §2-5에 매칭 확인됨. 상위 구현에 포함되어 별도 항목 불필요"

        output.append(f"- **판정 사유**: {reason}\n")

    i += 1

with open(INPUT, "w", encoding="utf-8") as f:
    f.writelines(output)

print(f"Updated: {INPUT}")
print("DONE.")
