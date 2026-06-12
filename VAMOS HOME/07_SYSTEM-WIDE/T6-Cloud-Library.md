---
tags: [tier/T6, module/E-series, status/CORE, version/V1, type/domain, lock/FREEZE, lock/DEFINED-HERE]
aliases: [6-8, 클라우드 라이브러리, Cloud-Library]
tier: T6
domain: "6-8 Cloud-Library"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-8_Cloud-Library\\"
design_doc: "[[SPEC-Cloud-Library]]"
quality_gate: "APPROVED — Phase 7 FINAL PASS · Content A- (S10-3), Phase 4 RECOVERY 종료 2026-06-02"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: MVP | V2: 7-Stage | V3: 자율 수집"
created: 2026-06-12
---

# 6-8 Cloud-Library

## 한줄 요약
Cloud Library 10-Layer 수집 파이프라인, CL-G0~G4 Gate System, 소스 평가·스코어링, 배포/스케일링 인프라의 정본을 소유하는 Tier 6 도메인.

## 핵심 정의
- 10-Layer: L1 INPUT → L2 DISCOVERY → L3 EVALUATION → L4 COLLECTION → L5 DATA LAKE → L6 EXTRACTION → L7 ANALYSIS → L8 VALIDATION → L9 VERSION CONTROL → L10 OUTPUT
- 평가 배점: Trust(25) + Relevance(30) + Quality(25) + Access(20) = 100
- Gate: CL-G0(Format) / CL-G1(Quality≥40) / CL-G2(Consistency≥50) / CL-G3(Security≥30) / CL-G4(Final≥60)
- 배포(DH-CL-D1): V1 Docker Compose(Hetzner CX31) / V2 Docker Swarm / V3 K8s HPA

## LOCK 항목 (L1~L22, 22건 + DH-CL-D1)
- L1 10-Layer 아키텍처 / L2 평가 4카테고리 배점 / L3 소스 신뢰도 가중치(공식 1.0~SNS 0.3) / L4~L8 CL-G0~G4 Gate
- L9 동시 크롤러 5 / L10 크롤링 간격 ≥1초/도메인 / L11 페이지 깊이 3 / L12 단일 소스 50MB / L13 캐시 TTL 24시간
- L14 최대 저장 소스 10,000 / L15 임베딩 배치 32 / L16 재크롤링 7일 / L17 임베딩 워커 2 / L18 메타데이터 10KB
- L19 Quality 최소 40 / L20 Consistency 최소 50 / L21 일일 쿼터 1,000페이지 / L22 Gate ID 접두어 CL-G0~CL-G4

## 의존성 (Depends On)
- [[T4-Rust-Tauri]] — E-15 Cloud Collector IPC / [[T6-Security]] — 클라우드 배포 보안·네트워크 분할
- [[T6-Event-Logging]] — cl.rt.* 이벤트 / [[T6-Operations]] — 페일오버 운영 절차
- [[T6-RT-BNP-DCL]] — Fast Gate 공유·소스 가중치 (양방향 B20)

## 제공 (Provides To)
- [[T6-Memory-RAG]] — L10 OUTPUT → VectorStore 인덱싱 / [[T6-RT-BNP-DCL]] — 배치 파이프라인 (양방향 B20)

## 횡단 개념 연결
- [[Data-Governance-Pipeline]] — 수집·검증·버전관리 / [[RAG-Pipeline]] — L10 → 임베딩 인덱싱 연결

## 관련 모듈 시리즈
- [[MODULE-MAP]] — E-15 Cloud Collector (E-Series) 정본 인프라

## STEP7 매핑
- 출처: VAMOS_CLOUD_LIBRARY_SPEC §1~§16 + Part2 §6.10 (RT-BNP/DCL 제외, L5510-L5571/L5743-L5787)

## 버전별 범위
- V1: MVP (Docker Compose 단일 서버) / V2: 7-Stage 파이프라인 / V3: 자율 수집 + K8s 오토스케일링

## 검증 상태
- Quality Gate: APPROVED — Content A- / Phase 4 RECOVERY 리포트형 genuine write 도메인 종료 (2026-06-02)
- LOCK 검증: 22/22 일치 + DH-CL-D1 1 (AUTHORITY_CHAIN §3/§4 실측, 변경 0건 통산)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-8_Cloud-Library\
- Authority: 6-8_Cloud-Library\AUTHORITY_CHAIN.md
- Design: [[SPEC-Cloud-Library]] (§16 LOCK 13건)
