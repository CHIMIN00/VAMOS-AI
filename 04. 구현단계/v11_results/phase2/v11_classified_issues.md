# v11 Phase 2-A: REAL_ISSUE 분류표

> **입력**: v11_adversarial_report.md (Phase 1.5 확정 179건 REAL_ISSUE)
> **분류 유형**: FIX / ADD / RESTRUCTURE / CLARIFY
> **작성일**: 2026-03-12
> **Fix Group (FG)**: 동일 수정 패스에서 함께 처리해야 하는 이슈 묶음

---

## 분류 기준

| 유형 | 설명 | 예시 |
|------|------|------|
| **FIX** | 값/수치/용어/참조 오류 수정 | 63→64, Trust Score→Content Quality |
| **ADD** | 누락 내용 추가 | 전환조건, 운영 정보, 테스트 등 |
| **RESTRUCTURE** | 구조 변경 (균일성, 프롬프트 재설계 등) | §3 하위구조 신설, 테이블 재구조화 |
| **CLARIFY** | 모호한 표현/관계 명확화 | 포함 여부, 시점, 적용 범위 |

---

## 분류 통계

| 유형 | 건수 | 비율 |
|------|------|------|
| **FIX** | 52건 | 29.1% |
| **ADD** | 80건 | 44.7% |
| **RESTRUCTURE** | 17건 | 9.5% |
| **CLARIFY** | 30건 | 16.8% |
| **합계** | **179건** | 100% |

### 심각도 × 유형 교차표

| 심각도 | FIX | ADD | RESTRUCTURE | CLARIFY | 합계 |
|--------|-----|-----|-------------|---------|------|
| BLOCKER | 8 | 3 | 1 | 1 | **13** |
| HIGH | 22 | 16 | 5 | 7 | **50** |
| MEDIUM | 15 | 37 | 6 | 7 | **65** |
| LOW | 7 | 24 | 5 | 15 | **51** |

---

## Fix Group (FG) 목록 — 동일 수정 패스 묶음

> 교차 에이전트 중복/관련 이슈를 하나의 FG로 묶어 Ripple 1회로 처리.
> FG 내 이슈는 동시에 수정하여 ripple 재계산을 최소화.

| FG | 유형 | 포함 이슈 | 설명 |
|----|------|----------|------|
| FG-B01 | FIX | A1#1, A11#4 | 비용 알람 체계 통일 (70/85/95 vs 80/100) |
| FG-B02 | FIX | A6#17 | V2→V3 전환조건 Loki+Grafana 시간 모순 해소 |
| FG-B03 | FIX | A12#2 | SelfCheckGate 실행 위치 명확화 |
| FG-B04 | FIX | A12#4 | S3 타임아웃(120s) vs 승인 타임아웃(600s) 충돌 |
| FG-B05 | ADD | A12#17 | FailureCode↔Fallback 매핑 테이블 작성 |
| FG-B06 | RESTRUCTURE | A8#1 | V2-Phase 2 프롬프트 v10 추가분 반영 |
| FG-B07 | FIX | A11#6,#7,#8 | v10 추가 후 타임라인 재설계 |
| FG-B08 | FIX+ADD | A13#17,#18 | §6.3 테스트 수 갱신 + V2-PH2 테스트 보강 |
| FG-B09 | ADD | A14#25,#26 | 운영 섹션 신설 (모니터링/백업) |
| FG-H01 | FIX | A2#1-8,#12,#15-16; A5#6-9; A12#10-11 | FIX-09 Gate 명칭 전파 + B-시리즈 매핑 수정 |
| FG-H02 | ADD | A4#9,#10,#11-13; A4#3 | §3 V1 하위구조 보강 (실행가이드/프롬프트/규칙 등) |
| FG-H03 | ADD | A6#13-16; A6#18 | V1→V2/V2→V3 전환조건 TC 메커니즘 정의 |
| FG-H04 | ADD | A8#2-4,#8-11,#13-18 | 프롬프트 규칙 전파 (R1~R11 + v10 항목) |
| FG-H05 | FIX | A1#2,#4; A10#11 | config 값 불일치 (autonomy_level, max_turns, strict) |
| FG-H06 | FIX | A10#5,#8 | 코드블록 deprecated API/컴파일 오류 수정 |
| FG-H07 | ADD | A12#1,#9,#15,#18; A14#27-30 | 시스템설계 갭 (UI매핑/Gate관계/NEVER_AUTO/인시던트 등) |
| FG-H08 | ADD | A13#1-7 | 보안 모델 갭 (HMAC/STRIDE/OWASP LLM) |
| FG-H09 | ADD | A7#1 | STEP-2 모델 필드 정의 보충 |
| FG-H10 | FIX | A11#1,#3 | V3/V2 비용 모순 해소 (K8s, GPU) |
| FG-H11 | CLARIFY | A14#6 | config.v1.toml 이중 게시 정본 라벨 |
| FG-H12 | ADD | A14#4-5 | Glossary + Reading Guide 추가 |
| FG-H13 | ADD | A13#19-26 | 테스트 커버리지 보강 (VAL/SDAR/HMAC 등) |
| FG-M01 | FIX | A1#5, A6#1 | §7 GO/NO-GO 총수 63→64 (V3=11→12) |
| FG-M02 | FIX | A2#9-11,#17-18 | 용어 혼용 수정 (I-3/I-5/I-10, SC 총수, SDAR) |
| FG-M03 | CLARIFY | A1#3,#6; A5#1 | 수치/참조 모호성 해소 (dimension, EventType, SC-09) |
| FG-M04 | FIX | A10#3-4,#6-7 | 코드블록 import 누락 수정 |
| FG-M05 | ADD | A6#2-4,#5,#7-8,#12 | §7 체크리스트 보완 (역방향매핑, LOCK 검증) |
| FG-M06 | ADD | A7#5,#7-8; A8#7,#9 | 프롬프트 자기완결성 보강 |
| FG-M07 | CLARIFY | A7#6; A9#7; A11#2,#10; A12#14 | 관계/시점/범위 명확화 |
| FG-M08 | ADD | A9#1,#2,#5; A10#10 | 체크리스트/매핑/검증코드 보완 |
| FG-M09 | FIX | A5#5; A7#2; A9#4 | 참조 오류/역의존 수정 |
| FG-M10 | RESTRUCTURE | A7#3-4,#9; A10#12 | V3 모듈 분배/Method 분리/config 구조 |
| FG-M11 | ADD | A12#3,#5,#7,#12,#16 | 시스템설계 MEDIUM (SDAR매핑/UI복구/Gate규칙) |
| FG-M12 | ADD | A13#8-12 | 보안 MEDIUM (CAT-E/AI체크리스트/STRIDE) |
| FG-M13 | RESTRUCTURE | A14#1-3 | v10 테이블 가독성 (서브그룹 헤더, 정보밀도) |
| FG-M14 | CLARIFY+ADD | A14#7-16 | §1.3참조/관계도/용어정의/v10영향분석 등 |
| FG-M15 | ADD | A14#18-20 | 에러/폴백 관계도 + 상태머신 다이어그램 + 비교표 |
| FG-M16 | ADD | A11#9 | V1 Phase 간 병렬/순차 규칙 정의 |
| FG-M17 | ADD | A4#14; A5#11 | v10 정보밀도 보강 + 통신사 신뢰도 출처 |
| FG-L01 | FIX | A3#1 | 변경이력 v17.0.0 순서 오류 수정 |
| FG-L02 | ADD | A3#2; A4#5-6 | 변경이력 주석 보완 + 편집 잔류물 수정 |
| FG-L03 | ADD | A7#10-11; A9#6 | 코드블록 추가 (V3-PH2/PH3, STEP-6 테스트) |
| FG-L04 | ADD | A14#31-38 | 운영 MEDIUM/LOW (DR/헬스체크/로그보존 등) |
| FG-L05 | RESTRUCTURE | A14#23 | 행번호 참조 → 앵커 참조 전환 |
| FG-L06 | CLARIFY | A14#7; A1#7,#8 | LOCK-AT 적용범위/턴제한관계/StageGate수량 |

---

## 에이전트별 REAL_ISSUE 상세 분류

### Agent 1 (GAP-06,08) — 8건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | BLOCKER | FG-B01 | FIX | 비용 알람 70/85/95% 3단계 vs config 80%/100% 2단계 충돌 | L1529, L209 |
| 2 | HIGH | FG-H05 | FIX | `autonomy_level` L1490 "L2_COPILOT" vs L164 config "L1" | L1490, L164, L339 |
| 3 | HIGH | FG-M03 | CLARIFY | dimension=256 vs LOCK dimension=1024 혼동 (matryoshka_dim 혼재) | L1491, L179-180, L354-355 |
| 4 | HIGH | FG-H05 | FIX | max_turns(50) vs max_turns_per_session=100 (2배 차이) | L2214, L2293 |
| 5 | MEDIUM | FG-M01 | FIX | §7 "63건(V3=11)" vs 실제 V3=12(v22 PARL 추가 미반영) | L4142, L4231 |
| 6 | MEDIUM | FG-M03 | CLARIFY | EventTypeRegistry 123 vs 134: cl.rt.* 11건 포함 여부 명시 필요 | L4142 |
| 7 | MEDIUM | FG-L06 | CLARIFY | P-level 턴 제한(5/10/20)과 세션 max_turns(50/100) 관계 미정의 | L2214 |
| 8 | MEDIUM | FG-L06 | FIX | Stage Gate V2 헤더 35 vs 테이블 합산 36 수량 불일치 | §7.3 |

### Agent 2 (GAP-07,10) — 16건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | HIGH | FG-H01 | FIX | B-1 "Episodic"↔"Skill Library" 역할 충돌 | L1586, §5 모듈 |
| 2 | HIGH | FG-H01 | FIX | B-3 "Semantic"↔"Memory Decay" 역할 충돌 | L1588 |
| 3 | HIGH | FG-H01 | FIX | B-4 "Working"↔"DSPy Integration" 역할 충돌 | L1589 |
| 4 | HIGH | FG-H01 | FIX | FIX-09 미전파: L3875 "Trust Score" 잔존 | L3875 |
| 5 | HIGH | FG-H01 | FIX | FIX-09 미전파: L3876 "Relevance Score" 잔존 | L3876 |
| 6 | HIGH | FG-H01 | FIX | FIX-09 미전파: L3928 구명칭 잔존 | L3928 |
| 7 | HIGH | FG-H01 | FIX | B-시리즈 전체 매핑 불일치 (상위 일반화) | L1584-1589 |
| 8 | HIGH | FG-H01 | FIX | B-2 "Procedural"↔"Prompt Cache" 불일치 | L1587 |
| 9 | MEDIUM | FG-M02 | FIX | I-3 명칭 혼용 | §2~§6 |
| 10 | MEDIUM | FG-M02 | FIX | I-5 명칭 혼용 | §2~§6 |
| 11 | MEDIUM | FG-M02 | FIX | I-10 명칭 혼용 | §2~§6 |
| 12 | MEDIUM | FG-H01 | FIX | FIX-09 후 "Relevance"와 "Consistency" 혼재 | L3854-3876 |
| 15 | HIGH | FG-H01 | FIX | GAP-10: FIX-09 미전파 (LOCK > body 위반) | L3875 |
| 16 | HIGH | FG-H01 | FIX | GAP-10: FIX-09 미전파 (LOCK > body 위반) | L3876 |
| 17 | MEDIUM | FG-M02 | FIX | SC 총수 14 vs 15 불일치 | §7.5.5 |
| 18 | MEDIUM | FG-M02 | FIX | SDAR 정식명 이중 확장 | §6 |

### Agent 3 (GAP-05) — 2건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | HIGH | FG-L01 | FIX | L4395 v17.0.0이 v24.0.0 뒤에 위치 (시간순/버전순 위배) | L4395 |
| 2 | MEDIUM | FG-L02 | ADD | v20.4.0→v22.0.0 건너뛰기 면책 주석 부재 | 변경이력 |

### Agent 4 (GAP-01,02) — 10건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | HIGH | FG-M09 | CLARIFY | §1.3에서 schema_registry.toml 참조 (정의는 §2 STEP-2) | L94, L530 |
| 3 | HIGH | FG-H02 | RESTRUCTURE | §2(V0)→§3(V1) 상세도 급강하 | §3 전체 |
| 5 | LOW | FG-L02 | FIX | L1571 서술 잘림/불완전 (v10 편집 잔류물) | L1571 |
| 6 | LOW | FG-L02 | FIX | L1803 항목 설명 불완전 (v10 편집 잔류물) | L1803 |
| 9 | HIGH | FG-H02 | ADD | §3(V1) 실행가이드 전면 부재 | §3 |
| 10 | HIGH | FG-H02 | ADD | §3(V1) AI 프롬프트 전면 부재 | §3 |
| 11 | MEDIUM | FG-H02 | ADD | §3(V1) 규칙 부재 | §3 |
| 12 | MEDIUM | FG-H02 | ADD | §3(V1) 참조SOT 부재 | §3 |
| 13 | MEDIUM | FG-H02 | ADD | §3(V1) 완료검증 부재 | §3 |
| 14 | MEDIUM | FG-M17 | RESTRUCTURE | v10 추가분 정보밀도 저하 | §3~§5 테이블 |

### Agent 5 (GAP-03) — 7건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | MEDIUM | FG-M03 | CLARIFY | SC-09 "§5=5개" 참조 대상 모호 | §7.5.5 |
| 5 | HIGH | FG-M09 | FIX | §6.2.2 참조 오류 (IPC=§6.2.1, JSON-RPC=§6.2.2) | §6.2 |
| 6 | HIGH | FG-H01 | FIX | FIX-09 Gate 명칭 미전파 L3875 | L3875 |
| 7 | HIGH | FG-H01 | FIX | FIX-09 Gate 명칭 미전파 L3876 | L3876 |
| 8 | HIGH | FG-H01 | FIX | FIX-09 Gate 명칭 미전파 L3927 | L3927 |
| 9 | HIGH | FG-H01 | FIX | FIX-09 Gate 명칭 미전파 L3928 | L3928 |
| 11 | MEDIUM | FG-M17 | ADD | 통신사 신뢰도 0.85 출처 미정의 | §6.10 |

### Agent 6 (GAP-04,09) — 14건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | HIGH | FG-M01 | FIX | §7 총수 63(V3=11) vs 실제 64(V3=12) | L4142, L4231 |
| 2 | MEDIUM | FG-M05 | ADD | §7 체크리스트↔§2~§5 역방향 매핑 불완전 | §7 |
| 3 | MEDIUM | FG-M05 | ADD | §7 체크리스트 COND 10개 커버 부족 | §7 |
| 4 | MEDIUM | FG-M05 | ADD | §7 체크리스트↔§2~§5 역방향 매핑 불완전 (추가) | §7 |
| 5 | MEDIUM | FG-M05 | FIX | 산출물 인덱스 파일수 vs 실제 생성 불일치 | §7.6 |
| 7 | LOW | FG-M05 | ADD | LOCK 항목 개별 검증 체크리스트 누락 | §7 |
| 8 | LOW | FG-M05 | ADD | LOCK-AT 17건 개별 검증 체크리스트 부재 | §7 |
| 12 | MEDIUM | FG-M05 | ADD | v10 200건의 §7 체크리스트 미반영 | §7 |
| 13 | HIGH | FG-H03 | ADD | V1→V2 TC 측정 메커니즘 미정의 (memory error rate) | §7.3 전환조건 |
| 14 | HIGH | FG-H03 | ADD | V1→V2 TC 측정 메커니즘 미정의 (RAG accuracy) | §7.3 전환조건 |
| 15 | HIGH | FG-H03 | ADD | V2→V3 TC 2-tier LLM 미정의 | §7.4 전환조건 |
| 16 | HIGH | FG-H03 | ADD | V2→V3 TC P1 advanced 미정의 | §7.4 전환조건 |
| 17 | BLOCKER | FG-B02 | FIX | L4228 "Loki+Grafana 배포" V2→V3 전환조건에 시간적 모순 | L4228, L2564, L2639 |
| 18 | MEDIUM | FG-H03 | CLARIFY | V1→V2 TC 일부 조건 모호 | §7.3 |

### Agent 7 (GAP-11) — 11건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | HIGH | FG-H09 | ADD | STEP-2 25개 모델 지시하나 필드 정의 4개만 인라인 | §2 STEP-2 |
| 2 | HIGH | FG-M09 | FIX | STEP-3 존재하지 않는 [ipc] config 섹션 참조 | §2 STEP-3 |
| 3 | HIGH | FG-M10 | RESTRUCTURE | V3-Phase2 39모듈 불균등 분배 | §5 Phase 2 |
| 4 | HIGH | FG-M10 | RESTRUCTURE | V3-Phase3 과적재 | §5 Phase 3 |
| 5 | MEDIUM | FG-M06 | ADD | STEP-4에서 §6.5.1 참조만, 내용 미삽입 | §2 STEP-4 |
| 6 | MEDIUM | FG-M07 | CLARIFY | StateGraph와 LangGraph 단순 제어 흐름 규칙 관계 모호 | §2 STEP-4 |
| 7 | MEDIUM | FG-M06 | ADD | V2-PH1 전제조건 암묵적 | §4 Phase 1 |
| 8 | MEDIUM | FG-M06 | ADD | V3-PH1 인프라 판단 기준 미제공 | §5 Phase 1 |
| 9 | MEDIUM | FG-M10 | RESTRUCTURE | V3-PH2 구현/설계/테스트 Method 혼재 | §5 Phase 2 |
| 10 | LOW | FG-L03 | ADD | V3-PH2 코드블록 전무 | §5 Phase 2 |
| 11 | LOW | FG-L03 | ADD | V3-PH3 코드블록 전무 | §5 Phase 3 |

### Agent 8 (GAP-12,14) — 15건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | BLOCKER | FG-B06 | RESTRUCTURE | V2-Phase 2 프롬프트 10/116 커버 (v10 전혀 미반영) | §4 Phase 2 |
| 2 | HIGH | FG-H04 | ADD | v24 schema_registry.toml STEP-2 프롬프트 미포함 | §2 STEP-2 |
| 3 | HIGH | FG-H04 | ADD | V2-Phase 3 v10 추가항목 미반영 | §4 Phase 3 |
| 4 | HIGH | FG-H04 | ADD | V3-Phase 2 v10 추가항목 미반영 | §5 Phase 2 |
| 7 | MEDIUM | FG-M06 | CLARIFY | V3-Phase 3 기능 단위↔테이블 모듈 단위 매핑 불명확 | §5 Phase 3 |
| 8 | HIGH | FG-H04 | ADD | R1 Python ≥3.11 STEP-1/2 프롬프트 누락 | §2 STEP-1,2 |
| 9 | MEDIUM | FG-H04 | ADD | R2 Pydantic v2 V3 후반부 약함 | §5 프롬프트 |
| 10 | HIGH | FG-H04 | ADD | R3 no-create 전 프롬프트 0% 전파 | 전체 프롬프트 |
| 11 | HIGH | FG-H04 | ADD | R4 no-delete 전 프롬프트 0% 전파 | 전체 프롬프트 |
| 13 | MEDIUM | FG-H04 | ADD | R6 전파 0% | 전체 프롬프트 |
| 14 | MEDIUM | FG-H04 | ADD | R7 전파 0% | 전체 프롬프트 |
| 15 | MEDIUM | FG-H04 | ADD | R8 전파 0% | 전체 프롬프트 |
| 16 | MEDIUM | FG-H04 | ADD | R9 전파 0% | 전체 프롬프트 |
| 17 | MEDIUM | FG-H04 | ADD | R10 전파 0% | 전체 프롬프트 |
| 18 | MEDIUM | FG-H04 | ADD | R11 전파 0% (v24 신설 규칙) | 전체 프롬프트 |

### Agent 9 (GAP-13) — 7건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | MEDIUM | FG-M08 | ADD | schema_registry.toml STEP-2 완료 체크리스트 누락 | §2 STEP-2 |
| 2 | MEDIUM | FG-M08 | ADD | IPC method-to-module 매핑 불완전 | §2 STEP-3 |
| 4 | HIGH | FG-M09 | FIX | STEP-4→STEP-5 역의존: config_loader.py | §2 STEP-4, STEP-5 |
| 5 | MEDIUM | FG-M08 | ADD | V0→V1 체인 자동 검증 코드 부재 | §2→§3 전환 |
| 6 | LOW | FG-L03 | ADD | STEP-6 로깅 필드 매핑 테스트 누락 | §2 STEP-6 |
| 7 | HIGH | FG-M07 | CLARIFY | Redis 배포 시점 vs 사용 시점 모호 (Phase 1/2/3) | §4, §5 |
| 8 | HIGH | FG-M09 | FIX | V2 Phase 2↔3 SDAR AR-L3 중복 기술 | §4 Phase 2-3 |

### Agent 10 (GAP-15,16) — 9건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 3 | MEDIUM | FG-M04 | FIX | StateGraph import 누락 | §2 STEP-4 코드 |
| 4 | MEDIUM | FG-M04 | FIX | VamosState 타입 미정의 | §2 STEP-4 코드 |
| 5 | HIGH | FG-H06 | FIX | LangGraph 0.2+ deprecated API (set_entry_point→START/END) | §2 STEP-4 코드 |
| 6 | MEDIUM | FG-M04 | FIX | structlog 코드 `import logging` 누락 → NameError | §2 STEP-5 코드 |
| 7 | LOW | FG-M04 | FIX | BaseModel/ConfigDict import 누락 | §2 코드 |
| 8 | HIGH | FG-H06 | FIX | Rust HashMap::get() → Option, .map_err() 대신 .ok_or() 필요 | §2 STEP-3 코드 |
| 10 | MEDIUM | FG-M08 | ADD | pytest-asyncio 0.24.x asyncio_mode 설정 누락 | §2 STEP-6 |
| 11 | HIGH | FG-H05 | FIX | "V0: strict 미적용" 주석 vs `strict = true` 설정 모순 | config 코드 |
| 12 | MEDIUM | FG-M10 | RESTRUCTURE | s02_to_s08.enabled 묶음 키 → 개별 ON/OFF 불가 | config |

### Agent 11 (GAP-17,18) — 9건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | HIGH | FG-H10 | FIX | V3 ₩266,000/월 vs 정식 K8s $1,000+ 모순 | L2526, §5 |
| 2 | MEDIUM | FG-M07 | CLARIFY | V3-003 GPU $144/월 근거 불명 (A10G=$533+) | L2544 |
| 3 | HIGH | FG-H10 | FIX | V2 LlamaGuard GPU 비용 미반영 ($150+>₩93,000) | L1886, §4 |
| 4 | HIGH | FG-B01 | FIX | 비용 알람 70/85/95% vs config 80/100% (=Agent 1#1) | L1529, L209 |
| 6 | BLOCKER | FG-B07 | FIX | V1-Phase 2: 59개/2주 = 일 5.9개 (v10 후 미조정) | §3 Phase 2 |
| 7 | BLOCKER | FG-B07 | FIX | V1-Phase 3: 59개/2주 (동일 과부하) | §3 Phase 3 |
| 8 | BLOCKER | FG-B07 | FIX | V2-Phase 2: 105개/3주 = 일 7개 (극도 과부하) | §4 Phase 2 |
| 9 | MEDIUM | FG-M16 | ADD | V1-Phase 6 병렬 실행과 Stage Gate 순서 관계 미정의 | §3 Phase 6 |
| 10 | HIGH | FG-M07 | CLARIFY | DCL V3 비용(+₩15,000) < RT-BNP V3(+₩30~50K) 포함관계 | §5 비용 |

### Agent 12 (GAP-19,20,21) — 15건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | HIGH | FG-H07 | ADD | Pipeline S4~S6 UI 상태 전이 매핑 미정의 | §6.11 |
| 2 | BLOCKER | FG-B03 | FIX | SelfCheckGate: plan 노드에 나열 vs S6 verify 실행 위치 모순 | L973-975, L1011 |
| 3 | MEDIUM | FG-M11 | ADD | SDAR 7-state → Pipeline S0~S8 매핑 부재 | §6.11, §6.9 |
| 4 | BLOCKER | FG-B04 | FIX | S3=120s vs approval timeout=600s 파이프라인 타임아웃 | L1512, L220 |
| 5 | MEDIUM | FG-M11 | ADD | UI ERROR/TIMEOUT→Pipeline 복구 시 상태 동기화 경로 없음 | §6.11 |
| 7 | MEDIUM | FG-M11 | ADD | Gate 순차/조건부 실행 여부 미정의 | §6.5, §6.11 |
| 9 | HIGH | FG-H07 | ADD | RT-BNP Fast Gate와 5-Gate 체계 관계 미정의 | L3922, §6.5 |
| 10 | HIGH | FG-H01 | FIX | CL-G1 FIX-09 명칭 미전파 | L3927 |
| 11 | HIGH | FG-H01 | FIX | CL-G2 FIX-09 명칭 미전파 | L3928 |
| 12 | MEDIUM | FG-M11 | ADD | V2 COND 10개 추가 시 Gate 임계값 변경 미정의 | §6.5, §7.3 |
| 14 | MEDIUM | FG-M07 | CLARIFY | Fallback 최종 단계 불명확 | §6.9 |
| 15 | HIGH | FG-H07 | ADD | NEVER_AUTO 에러 자동 탐지 메커니즘 부재 | §6.9 |
| 16 | MEDIUM | FG-M11 | ADD | FailureCode 36건 중 ~16건 발생 모듈 불명확 | §6.9, L4081 |
| 17 | BLOCKER | FG-B05 | ADD | FailureCode 36건↔Fallback 23건 매핑 테이블 완전 부재 | §6.9 |
| 18 | HIGH | FG-H07 | ADD | V2/V3 추가 49개 모듈 전용 FailureCode 미정의 | §6.9 |

### Agent 13 (GAP-22,25) — 22건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | HIGH | FG-H08 | ADD | HMAC 타이밍 공격 방어 미정의 | §6.5 |
| 2 | HIGH | FG-H08 | ADD | 보안 리뷰 범위 불명확 | §6.5 |
| 3 | HIGH | FG-H08 | ADD | STRIDE Repudiation 갭 | §6.5 |
| 4 | HIGH | FG-H08 | ADD | OWASP LLM #1 Prompt Injection 방어 부족 | §6.5.1 |
| 5 | HIGH | FG-H08 | ADD | OWASP LLM #2 Output Handling 부족 | §6.5.1 |
| 6 | MEDIUM | FG-M12 | ADD | OWASP LLM #3 Training Data 관련 | §6.5.1 |
| 7 | MEDIUM | FG-M12 | ADD | OWASP LLM #4 Model DoS 관련 | §6.5.1 |
| 8 | MEDIUM | FG-M12 | ADD | CAT-E 미열거 항목 | §6.9 |
| 9 | MEDIUM | FG-M12 | ADD | NEVER_AUTO 탐지 메커니즘 | §6.9 |
| 10 | MEDIUM | FG-M12 | ADD | AI 체크리스트 갭 | §6.5.1 |
| 11 | MEDIUM | FG-M12 | ADD | STRIDE 부분 커버 | §6.5 |
| 12 | MEDIUM | FG-M12 | ADD | STRIDE 추가 커버 필요 | §6.5 |
| 17 | BLOCKER | FG-B08 | FIX | v10 ~378건 추가 후 §6.3 테스트 ~84건 미갱신 | L3332, §6.3 |
| 18 | BLOCKER | FG-B08 | ADD | V2-Phase 2: 116개 항목 vs ~5개 테스트 (4.3%) 저커버리지 | §6.3 |
| 19 | HIGH | FG-H13 | ADD | VAL-003 테스트 부재 | §6.3 |
| 20 | HIGH | FG-H13 | ADD | VAL-005 테스트 부재 | §6.3 |
| 21 | HIGH | FG-H13 | ADD | SDAR 테스트 0건 | §6.3 |
| 22 | HIGH | FG-H13 | ADD | HMAC 테스트 0건 | §6.3 |
| 23 | MEDIUM | FG-H13 | ADD | LlamaGuard 테스트 부재 | §6.3 |
| 24 | MEDIUM | FG-H13 | ADD | GDPR 관련 테스트 부재 | §6.3 |
| 25 | MEDIUM | FG-H13 | ADD | AC 매핑 테스트 부재 | §6.3 |
| 26 | MEDIUM | FG-H13 | ADD | 아키텍처 테스트 부재 | §6.3 |

### Agent 14 (GAP-23,24) — 34건 REAL

| # | 심각도 | FG | 유형 | 이슈 내용 | 주요 행 |
|---|--------|-----|------|----------|--------|
| 1 | HIGH | FG-M13 | RESTRUCTURE | v10 테이블 가독성 파괴 | §3~§5 테이블 |
| 2 | HIGH | FG-M13 | RESTRUCTURE | v10 정보밀도 극도 저하 | §3~§5 테이블 |
| 3 | HIGH | FG-M13 | RESTRUCTURE | v10 서브그룹 헤더 부재 | §3~§5 테이블 |
| 4 | HIGH | FG-H12 | ADD | ~4,400줄 문서에 Glossary 완전 부재 | §1 또는 말미 |
| 5 | HIGH | FG-H12 | ADD | ~4,400줄 문서에 Reading Guide 완전 부재 | §1 |
| 6 | HIGH | FG-H11 | CLARIFY | config.v1.toml 이중 게시(L162~240 vs L339~383) 정본 라벨 필요 | L162, L339 |
| 7 | HIGH | FG-L06 | CLARIFY | LOCK-AT 17건 버전 적용 범위(V1/V2) 불명확 | §6.7 |
| 8 | MEDIUM | FG-M14 | CLARIFY | §1.3 참조 연결 불명확 | §1.3 |
| 9 | MEDIUM | FG-M14 | CLARIFY | §6.5.1 관계 불명확 | §6.5.1 |
| 10 | MEDIUM | FG-M14 | ADD | schema_registry 관계 명시 필요 | §1.3, §2 |
| 11 | MEDIUM | FG-M14 | ADD | §6 상호참조 보강 | §6 |
| 12 | MEDIUM | FG-M14 | ADD | §3 개요 보강 | §3 |
| 13 | MEDIUM | FG-M14 | ADD | 용어 정의 지연 해소 | §1~§2 |
| 14 | MEDIUM | FG-M14 | CLARIFY | FIX-09 유지보수 관련 명확화 | §7.5.5 |
| 15 | MEDIUM | FG-M14 | ADD | v10 영향분석 명시 | §1 또는 변경이력 |
| 16 | MEDIUM | FG-M14 | ADD | §7 프로세스 보강 | §7 |
| 18 | MEDIUM | FG-M15 | ADD | 에러/폴백 관계도 부재 | §6.9 |
| 19 | MEDIUM | FG-M15 | ADD | 상태머신 다이어그램 부재 | §6.11 |
| 20 | MEDIUM | FG-M15 | ADD | 버전 비교표 부재 | §1 |
| 23 | LOW | FG-L05 | RESTRUCTURE | 행번호 기반 참조 취약성 | 전체 |
| 25 | BLOCKER | FG-B09 | ADD | §6.12 운영 DCL 이관 2건만 — 전체 운영 정책 부재 | §6.12 |
| 26 | BLOCKER | FG-B09 | ADD | V0/V1 모니터링 전략 부재 — 32모듈 장애 감지 불가 | §6.12 |
| 27 | HIGH | FG-H07 | ADD | 인시던트 대응 프로세스 전면 부재 | §6.12 신설 |
| 28 | HIGH | FG-H07 | ADD | 백업 RPO-RTO 정의 전면 부재 | §6.12 신설 |
| 29 | HIGH | FG-H07 | ADD | 롤백 프로세스 전면 부재 | §6.12 신설 |
| 30 | HIGH | FG-H07 | ADD | 알림 체계 전면 부재 | §6.12 신설 |
| 31 | MEDIUM | FG-L04 | ADD | DR(재해복구) 미정의 | §6.12 |
| 32 | MEDIUM | FG-L04 | ADD | 헬스체크 미정의 | §6.12 |
| 33 | MEDIUM | FG-L04 | ADD | 이벤트 모니터링 미정의 | §6.12 |
| 34 | MEDIUM | FG-L04 | ADD | SDAR 수동 폴백 미정의 | §6.12 |
| 35 | MEDIUM | FG-L04 | ADD | 비용 초과 대응 미정의 | §6.12 |
| 36 | LOW | FG-L04 | ADD | 로그 보존 정책 미정의 | §6.12 |
| 37 | LOW | FG-L04 | ADD | RT-BNP 소스 장애 대응 미정의 | §6.12 |
| 38 | LOW | FG-L04 | ADD | Cloud 페일오버 미정의 | §6.12 |

---

## 교차 패턴별 FG 매핑

| 패턴 | 관련 FG | FG 수 |
|------|---------|-------|
| **A: v10 대량 추가 연쇄 미갱신** | FG-B06, FG-B07, FG-B08, FG-M13, FG-H04 | 5 |
| **B: FIX-09 Gate 명칭 미전파** | FG-H01 | 1 |
| **C: §3(V1) 구조적 고립** | FG-H02 | 1 |
| **D: V3 후반부 품질 저하** | FG-M10, FG-L03, FG-M06 | 3 |
| **E: 운영/보안 인프라 부재** | FG-B09, FG-H07, FG-H08, FG-L04 | 4 |

---

*산출물: D:\VAMOS\04. 구현단계\v11_results\phase2\v11_classified_issues.md*