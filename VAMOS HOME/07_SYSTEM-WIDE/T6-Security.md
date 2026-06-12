---
tags: [tier/T6, module/I-series, status/CORE, version/V1, type/domain, lock/FREEZE, responsible-ai]
aliases: [6-2, 보안 거버넌스, Security-Governance, A16]
tier: T6
domain: "6-2 Security-Governance"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-2_Security-Governance\\"
design_doc: "[[D2.0-07-Safety-Cost]]"
quality_gate: "APPROVED (AUTHORITY v1.5, Phase 4 V3 Stage B 2026-05-27)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 12항목 | V2: P2 HMAC+GDPR | V3: P3 ML 탐지"
created: 2026-06-12
---

# 6-2 Security-Governance

## 한줄 요약
STRIDE/OWASP LLM Top 10 위협 모델, HMAC 통신 보안, Guardrails 3-Layer, NEVER_AUTO 정책 등 보안 실행 정책 정본을 소유하는 Tier 6 횡단 보안 도메인 (Responsible AI: A16).

## 핵심 정의
- 위협 모델: STRIDE 6대 분류 + OWASP LLM01~LLM10 (2025, 10개 고정)
- HMAC-SHA256(상수 시간 비교), 키 최소 32바이트, 90일 순환, 리플레이 윈도우 5분(300초)
- Guardrails 3-Layer: L1 NeMo(입력) → L2 Guardrails AI(처리) → L3 LlamaGuard(출력)
- 12개 소비 도메인 통보 정책(R-62-1), 횡단 관심사 도메인(R-T6-2)

## LOCK 항목 (L1~L20, 20건)
- L1 OWASP LLM Top 10 / L2 STRIDE 6대 / L3 HMAC-SHA256 / L4 키 32바이트 / L5 키 순환 90일 / L6 리플레이 5분
- L7 Guardrails 3-Layer / L8 RBAC 4단계(OWNER/ADMIN/OPERATOR/VIEWER) / L9 P2 승인 타임아웃 / L10 비용 상한 ₩40K/93K/266K
- L11 5-Gate System / L12 Docker 샌드박스 30초+`--network=none` / L13 SQLCipher AES-256-CBC / L14 자율 운영 L0~L3
- L15 Non-goal 절대 금지 7종 / L16 Rate Limiting 10 req/min / L17 Cost Gate 일일 한도 / L18 trace_id 서버 UUID v4
- L19 DEC-003 도구 승인 / L20 NEVER_AUTO (P1 이상 자동승인 금지)

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 규칙 정의 (0-0=규칙, 6-2=실행) / [[T6-Memory-RAG]] — PII 마스킹·저장 정책 적용 대상
- [[T6-Event-Logging]] — 보안 이벤트 수집 (양방향 B15) / [[T6-Agent-Teams]] [[T6-SDAR]] — 양방향 (B16/B14)

## 제공 (Provides To)
- [[T1-Verifier-Engines]] — OWASP 체크리스트 / [[T1-Auxiliary-Modules]] — PII 마스킹 / [[T2-Blue-Node]] — HMAC 통신
- [[T2-COND-Modules]] — 106개 모듈 보안 체크리스트 / [[T3-Dev-Tools]] — 코드 샌드박스 / [[T3-Agent-Protocol]] — 자율성 게이팅 L0~L4
- [[T4-Rust-Tauri]] — IPC 보안 / [[T4-CICD]] — SAST/DAST 정책 / [[T4-MCP]] — Tool 화이트리스트·서명 검증
- [[T6-Agent-Teams]] — NEVER_AUTO / [[T6-SDAR]] — STRIDE→SDAR 트리거 매핑 / [[T6-Cloud-Library]] — 배포 보안

## 횡단 개념 연결
- [[5-Gate-Decision-Framework]] — Gate 순서 강제 / [[Autonomy-Level-Framework]] — L0~L3 정본
- [[Cost-Limits]] — 비용 상한 LOCK / [[Permission-Matrix-System]] — RBAC 연계

## 관련 모듈 시리즈
- [[MODULE-MAP]] — I-19 ApprovalGate 등 Gate 모듈 보안 정책 연계

## STEP7 매핑
- 출처: STEP7-E (보강 항목 92건, CRITICAL/HIGH/MED)

## 버전별 범위
- V1: P1 보안 12항목 / V2: P2 HMAC+GDPR / V3: P3 ML 이상 탐지 (anomaly_detection_v3 등 3 V3)

## 검증 상태
- Quality Gate: APPROVED (Phase 4 V3 Stage B, LOCK 20/20 전수 인용 매트릭스 first specialty)
- LOCK 검증: 20/20 일치 (AUTHORITY_CHAIN §4/§5 실측, 변경 0건 통산) / Responsible AI 지정: A16

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-2_Security-Governance\
- Authority: 6-2_Security-Governance\AUTHORITY_CHAIN.md
- Design: [[D2.0-07-Safety-Cost]]
