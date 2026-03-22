# v9 Phase 2-A: Ripple Map

> **Pipeline**: VAMOS v9.0.0
> **단계**: Phase 2-A (Ripple Map + PART2 수정)
> **작성일**: 2026-03-07
> **대상 문서**: VAMOS_구현가이드_PART2_구현단계.md v20.4.0 → v21.0.0
> **입력**: Phase 1 REAL_ERROR 26건 (고유 ~22건)

---

## 1. 수정 목록 (Severity 순)

### HIGH (FIX-01 ~ FIX-09)

| FIX ID | REAL_ERROR | 관점 | 내용 | 영향 위치 (줄) | Old | New | SOT 근거 |
|--------|-----------|------|------|---------------|-----|-----|---------|
| FIX-01 | RE-A-001, C-IMP-015, C-IMP-023 | A,C | LogEventSchema 필드명 혼재 | L1073 (프롬프트), L1153 (gate) | 프롬프트: trace_id/timestamp/level/module/event_type/message/data vs Gate: event_type/producer/when/payload/severity/sinks/links | 매핑 테이블 추가 + 정본 명시 | D2.1-D2 §4.2 |
| FIX-02 | RE-A-002, C-IMP-016 | A,C | GDPR '삭제' 누락 | L2046 | "열람/이동/제한" (3항) | "열람/이동/제한/삭제" (4항) | D2.0-07, V2-P3 gate #7 |
| FIX-03 | RE-A-003 | A | V2 비용 모니터링 대시보드 Gate 검증 부재 | V2-P2 또는 P3 gate 영역 | Gate 없음 | 비용 대시보드 검증 gate 추가 | V2-GNG-13 |
| FIX-04 | RE-A-004 | A | V3 Federated Agent 승인 체계 Gate 부재 | V3-P2 gate 영역 | gate #6 동작확인만 | 승인 체계 설계 검증 gate 추가 | V3-GNG-10, DEFER-AT-004 |
| FIX-05 | RE-F-001 | F | FinBERT transformers V범위 불일치 | L3060 | "없음" (V1 conflict) | V범위 주석 + sentence-transformers 대안 명시 | GT-4, RULE-2 |
| FIX-06 | C-V1-001, C-IMP-001, C-IMP-017 | C | V1-P1 Wk3-4 칼럼 부재 (5열→6열) | L1396-1408 | 5열 (산출물 참조 없음) | 6열 (산출물 참조 칼럼 추가) | RULE-2 |
| FIX-07 | C-V1-002, C-IMP-002 | C | V1 LOCK 제약 체계적 부재 | §3 V1 전반 | LOCK 주석 없음 | 각 Phase 테이블에 LOCK 참조 주석 추가 | RULE-4 |
| FIX-08 | C-V3-001, C-IMP-010 | C | V3-P2 39개 모듈 상세 명세 부족 | L2399~2430+ | 1-3줄 기능 설명만 | 그룹별 I/O 스키마 + 핵심 함수 시그니처 추가 | RULE-2 |
| FIX-09 | C-IMP-022 | C | Cloud Library Gate명 불일치 | L3279-3280 | G1="Trust Score", G2="Relevance" | G1="Content Quality", G2="Consistency" (SOT 정본) | CLOUD_LIBRARY_SPEC §8 |

### MEDIUM (FIX-10 ~ FIX-24)

| FIX ID | REAL_ERROR | 관점 | 내용 | 영향 위치 (줄) | Old | New | SOT 근거 |
|--------|-----------|------|------|---------------|-----|-----|---------|
| FIX-10 | RE-B-001 | B | config_loader.rs → config.rs | L2840 | config_loader.rs | config.rs | PHASE_B2 §4.1 |
| FIX-11 | RE-D-001 | D | V1 MCP Server/Client 개별 검증 부재 | V1-P6 gate 영역 | MCP 단일 항목 | MCP Bridge/Server/Client 개별 검증 | GT-2 V1-P6 |
| FIX-12 | RE-D-002 | D | GO/NO-GO vs Stage Gate 관계 미설명 | §7 서두 (L3564) | 관계 설명 없음 | 관계 요약문 추가 | GT-2 |
| FIX-13 | RE-D-003 | D | Stage Gate 합산 수치 미명시 | §7 (L3564) | 미명시 | "총 193건 (V0:58, V1:66, V2:35, V3:34)" 추가 | GT-2 |
| FIX-14 | RE-D-004 | D | §6.9 SDAR Phase별 참조 범위 미구분 | §6.9 (L3140) | 전체 참조 | V2=AR-L2~L3, V3=AR-L4+ 범위 구분 추가 | GT-2 XD-03 |
| FIX-15 | RE-F-002 | F | jsonrpcserver GT-4 미등록 | GT-4 (L273 참조) | GT-4 미등록 | GT-4에 jsonrpcserver 추가 | RULE-14 |
| FIX-16 | RE-F-003 | F | NetworkX GT-4 미등록 | GT-4 (L1462 참조) | GT-4 미등록 | GT-4에 networkx 추가 | RULE-14 |
| FIX-17 | RE-F-004 | F | TimescaleDB Docker Compose 미포함 | L1831 | Docker Compose에 없음 | TimescaleDB 서비스 또는 PG extension 설치 주석 추가 | RULE-11 |
| FIX-18 | C-IMP-003, C-V1-003 | C | V1 파일 경로 Phase 2~6 부재 | §3 V1-P2~P6 테이블 | 파일명 칼럼 없음 | §6/PHASE_B2 크로스참조 주석 추가 | RULE-2 |
| FIX-19 | C-IMP-005 | C | IPC 타임아웃/재시작 config 미매핑 | V0-STEP-3 (L700) | 하드코딩 30s/max 3 | config.v1.toml [ipc] 키 매핑 주석 추가 | - |
| FIX-20 | C-IMP-009 | C | V2-P2 COND config 키 부족 | V2-P2 프롬프트 (L1920) | 2/10 모듈만 config 명시 | 전체 10개 모듈 config.v2.toml 키 목록 추가 | RULE-4 |
| FIX-21 | C-IMP-011, C-IMP-012 | C | V3-P2 EXP 의존성/config 부재 | V3-P2 프롬프트 (L2399) | 5개 도구만 언급 | 그룹별 의존성 + config.v3.toml 키 추가 | - |
| FIX-22 | C-IMP-018 | C | V1-P3 구현 설명 모호 | V1-P3 (L1535) | 모호한 설명 | 주요 항목 구체화 주석 추가 | RULE-5 |
| FIX-23 | C-IMP-019 | C | V1-P6 구현 항목 모호 | V1-P6 (L1660) | 모호한 설명 | MCP tool list, 검증 로직 참조 주석 추가 | RULE-5 |
| FIX-24 | C-IMP-024 | C | GDPR 용어 불일치 (체크리스트 vs 프롬프트) | L2191 | "동의 관리/데이터 내보내기/삭제 요청/접근 로그" | "열람(Access)/이동(Portability)/제한(Restriction)/삭제(Erasure)" | D2.0-07 |

### LOW (10건) — 표기 불통일/경미 이슈

V1 테이블 표기 불통일, 칼럼 순서 차이, 명명 경미 차이 등은 FIX-06, FIX-07, FIX-18 수정 시 함께 정리.

---

## 2. Ripple 연쇄 영향 분석

| FIX | 직접 수정 | 연쇄 영향 | 영향 범위 |
|-----|----------|----------|----------|
| FIX-01 | L1073 매핑 테이블 | V0-STEP-5 gate(L1153)는 이미 정본 — 변경 불필요 | §2 V0-STEP-5 |
| FIX-02 | L2046 1항 추가 | 프롬프트(L2124-2129) 이미 4항 → 변경 불필요 | §4 V2-P3 테이블 |
| FIX-03 | V2-P2 gate 추가 | V2 GO/NO-GO #13과 정합 | §4 V2-P2, §7.3 |
| FIX-04 | V3-P2 gate 추가 | V3 GO/NO-GO #10과 정합 | §5 V3-P2, §7.4 |
| FIX-05 | L3060 주석 | FinBERT 참조 위치 전수 확인 필요 | §6.8 |
| FIX-06 | L1396-1408 칼럼 추가 | 11개 모듈 행에 산출물 참조 추가 | §3 V1-P1 Wk3-4 |
| FIX-09 | L3279-3280 | Cloud Library 전체 Gate 참조 일관성 | §6.10 |
| FIX-10 | L2840 1줄 | config 관련 참조 전수 grep 필요 | §6.2.3 |
| FIX-17 | L1831 | Docker Compose 서비스 목록 + §6.8 정합성 | §4 V2-P1 |
| FIX-24 | L2191 | FIX-02와 연동 — GDPR 4항 용어 통일 | §4 V2-P3 체크리스트 |

---

## 3. SOURCE_CONFLICT 신규 발생 여부

FIX-09 (Cloud Library Gate명)는 기존 SOURCE_CONFLICT 주석(L3279-3280)을 해소하는 수정.
FIX-01 (LogEventSchema)는 structlog 구현 vs D2.1-D2 정본 간 매핑으로 해결 — SC 신규 발생 없음.
FIX-05 (FinBERT)는 V범위 명확화 — SC 신규 발생 없음.

**신규 SOURCE_CONFLICT: 0건 예상**

---

## 4. GT 재구축 필요 항목 (Phase 2-B)

| GT | 재구축 필요 | 사유 |
|----|-----------|------|
| GT-1 | △ | FIX-10 (config.rs) — 경로 1건 변경 |
| GT-2 | ○ | FIX-03, FIX-04 — Gate 조건 추가, FIX-11 — MCP 분리 |
| GT-3 | × | 수량 변경 없음 (E 관점 전수 PASS) |
| GT-4 | ○ | FIX-15 (jsonrpcserver 추가), FIX-16 (networkx 추가) |
| GT-5 | △ | FIX-06~08 — 구현 가능성 체크리스트 보강 항목 |

---
