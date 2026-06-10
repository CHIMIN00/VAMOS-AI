# Blue Node 인스턴스 카탈로그 — V3 (전체 50 인스턴스) ★ CORE

> **Status**: LOCKED  (DRAFT→APPROVED→LOCKED 2026-05-31 / ReadOnly TRUE)
> **버전**: v1.0
> **작성일**: 2026-05-31 (Phase 4 production promotion — RECOVERY Stage B genuine write)
> **출처**: BLUE_NODE_ARCHITECTURE_구조화_종합계획서 §7 P4-3 (P3-3 inheritance) + AUTHORITY_CHAIN.md §4 LOCK
> **§0-E 판정**: 본 카탈로그는 **단일 파일 내 50 row** (V1 3 + V2 7 + V3 40). 개별 instance .md 40개 생성은 과다 생성 = 오류 → 생성하지 않는다.
> **상속**: `v1_instances.md` 3 row + `v2_instances.md` 7 신규 row 그대로 계승
> **Last-reviewed**: 2026-05-31
> **Locked-date**: 2026-05-31
> **Locked-by**: phase4_2-1_recovery_stage_b_2026-05-31 (구조 변경 불가 — 변경 시 일시 RO 해제→fix→복원 EXACT + audit log)

---

## §1. 적용 LOCK (verbatim 인용 — 재정의 금지)

| LOCK ID | 정본 출처 | 값 (verbatim) |
|---------|----------|---------------|
| LOCK-BN-01 | D2.0-03 K-041 | BN 타입 4+1: Dev, Research, Content, Quant, Trading |
| LOCK-BN-12 | D2.0-03 §3.2.1(B) | active_node_cap V1=3, V2=10, V3=50 |
| LOCK-BN-13 | D2.0-03 §3.2.1(B) | candidate_node_cap V1=5, V2=20, V3=100 |
| LOCK-BN-14 | D2.0-05 §5.3.2 LOCK | 직접 Node-to-Node 통신 금지 — 모든 통신은 CORE 경유 |

> **50 인스턴스 산술**: V1 3 + V2 7 + V3 40 = **50 EXACT** (LOCK-BN-12 V3=50 active_node_cap verbatim 정합).

---

## §2. V1 + V2 인스턴스 (10 row 계승)

| # | instance_id | base 타입 | 등급 | 특화 |
|---|-------------|-----------|------|------|
| 1 | `bn.v1.dev` | Dev | V1 | 코드 보조 |
| 2 | `bn.v1.research` | Research | V1 | 리서치 |
| 3 | `bn.v1.content` | Content | V1 | 콘텐츠 |
| 4 | `bn.v2.quant` | Quant | V2 | 정량 분석 |
| 5 | `bn.v2.trading` | Trading | V2 | 트레이딩(P2) |
| 6 | `bn.v2.pkm` | Research | V2 | PKM |
| 7 | `bn.v2.education` | Content | V2 | 교육 |
| 8 | `bn.v2.health` | Research | V2 | 건강·웰니스 |
| 9 | `bn.v2.productivity` | Content | V2 | 생산성 |
| 10 | `bn.v2.communication` | Content | V2 | 커뮤니케이션 |

---

## §3. V3 인스턴스 (40 row — Tier 3 9 도메인 #5~#13 매핑)

> 9 도메인 분배: #5/#6/#7/#8 = 5 인스턴스 × 4 = 20 + #9/#10/#11/#12/#13 = 4 인스턴스 × 5 = 20 → **합계 40**. (plan §7 P4-3 절차 2 "9 도메인 × 평균 4~5 인스턴스")

### #5 Health-Wellness-EmotionAI (5)

| # | instance_id | base 타입 | 역할 |
|---|-------------|-----------|------|
| 11 | `bn.v3.health.tracker` | Research | 건강 지표 추적 |
| 12 | `bn.v3.health.wellness_coach` | Content | 웰니스 코칭 |
| 13 | `bn.v3.health.emotion_analyzer` | Research | 감정 분석(EmotionAI) |
| 14 | `bn.v3.health.nutrition_advisor` | Content | 영양 조언 |
| 15 | `bn.v3.health.sleep_monitor` | Research | 수면 모니터링 |

### #6 Productivity-Automation (5)

| # | instance_id | base 타입 | 역할 |
|---|-------------|-----------|------|
| 16 | `bn.v3.prod.task_automator` | Dev | 작업 자동화 |
| 17 | `bn.v3.prod.schedule_optimizer` | Content | 일정 최적화 |
| 18 | `bn.v3.prod.workflow_builder` | Dev | 워크플로 구성 |
| 19 | `bn.v3.prod.note_organizer` | Content | 노트 정리 |
| 20 | `bn.v3.prod.focus_assistant` | Content | 집중 보조 |

### #7 Communication-Collaboration (5)

| # | instance_id | base 타입 | 역할 |
|---|-------------|-----------|------|
| 21 | `bn.v3.comm.meeting_summarizer` | Research | 회의 요약 |
| 22 | `bn.v3.comm.message_drafter` | Content | 메시지 초안 |
| 23 | `bn.v3.comm.translation_assistant` | Content | 번역 보조 |
| 24 | `bn.v3.comm.team_coordinator` | Content | 팀 조율 |
| 25 | `bn.v3.comm.email_triage` | Research | 이메일 분류 |

### #8 PKM (5)

| # | instance_id | base 타입 | 역할 |
|---|-------------|-----------|------|
| 26 | `bn.v3.pkm.knowledge_linker` | Research | 지식 연결 |
| 27 | `bn.v3.pkm.research_curator` | Research | 리서치 큐레이션 |
| 28 | `bn.v3.pkm.summary_synthesizer` | Content | 요약 종합 |
| 29 | `bn.v3.pkm.citation_manager` | Research | 인용 관리 |
| 30 | `bn.v3.pkm.concept_mapper` | Content | 개념 매핑 |

### #9 Game-Education-Career (4)

| # | instance_id | base 타입 | 역할 |
|---|-------------|-----------|------|
| 31 | `bn.v3.edu.tutor_adaptive` | Content | 적응형 튜터 |
| 32 | `bn.v3.edu.quiz_generator` | Content | 퀴즈 생성 |
| 33 | `bn.v3.edu.career_advisor` | Research | 커리어 조언 |
| 34 | `bn.v3.edu.skill_assessor` | Research | 역량 평가 |

### #10 Marketing-Mobile (4)

| # | instance_id | base 타입 | 역할 |
|---|-------------|-----------|------|
| 35 | `bn.v3.mkt.campaign_planner` | Content | 캠페인 기획 |
| 36 | `bn.v3.mkt.content_scheduler` | Content | 콘텐츠 스케줄링 |
| 37 | `bn.v3.mkt.analytics_reporter` | Quant | 분석 리포팅 |
| 38 | `bn.v3.mkt.ab_tester` | Quant | A/B 테스트 |

### #11 Specialized-Domains (4)

| # | instance_id | base 타입 | 역할 |
|---|-------------|-----------|------|
| 39 | `bn.v3.spec.legal_assistant` | Research | 법률 보조 |
| 40 | `bn.v3.spec.finance_analyst` | Quant | 재무 분석 |
| 41 | `bn.v3.spec.scientific_researcher` | Research | 과학 리서치 |
| 42 | `bn.v3.spec.code_reviewer` | Dev | 코드 리뷰 |

### #12 Hardware-IoT (4)

| # | instance_id | base 타입 | 역할 |
|---|-------------|-----------|------|
| 43 | `bn.v3.iot.device_monitor` | Research | 디바이스 모니터링 |
| 44 | `bn.v3.iot.sensor_aggregator` | Research | 센서 집계 |
| 45 | `bn.v3.iot.firmware_assistant` | Dev | 펌웨어 보조 |
| 46 | `bn.v3.iot.automation_controller` | Dev | 자동화 제어 |

### #13 Travel-Lifestyle (4)

| # | instance_id | base 타입 | 역할 |
|---|-------------|-----------|------|
| 47 | `bn.v3.travel.trip_planner` | Content | 여행 기획 |
| 48 | `bn.v3.travel.booking_assistant` | Content | 예약 보조 |
| 49 | `bn.v3.travel.local_guide` | Research | 로컬 가이드 |
| 50 | `bn.v3.travel.expense_tracker` | Quant | 경비 추적 |

> **합계 검증**: V1 3 (#1~3) + V2 7 (#4~10) + V3 40 (#11~50) = **50 row EXACT**. base 타입은 LOCK-BN-01 4+1 유형(Dev/Research/Content/Quant/Trading)으로 전수 귀속.

---

## §4. 도메인 우선순위 매트릭스 (선점 가능 우선순위 + Cap 분배)

> active_node_cap V3=50 포화 시 선점(preempt) 우선순위. 우선순위 P1(최상)~P3(최하). Cap 분배는 운영 데이터 baseline(Phase 5)으로 조정.

| 우선순위 | 도메인 그룹 | 근거 | 권장 Cap 분배(예시) |
|---------|------------|------|---------------------|
| P1 | V1 Dev/Research/Content + Trading(P2 금융) | MVP 핵심 + 금융 민감 | active 3 + 1 = 4 보장 |
| P2 | Quant + #11 Specialized + #5 Health(민감 데이터) | 정량·전문·민감 | active ~15 |
| P3 | #6~#10, #12, #13 일반 도메인 | 일반 생산성·콘텐츠 | 잔여 active (≤31) |

> 선점은 LOCK-BN-19(P2 HITL 5분 Auto deny) + LOCK-BN-14(CORE 경유) 준수 하에서만 수행. 정밀 알고리즘은 `04_node-lifecycle/_index.md` + W-04(IT-LC) 정본.

---

## §5. 9 도메인 cross-handoff (소비자 cross-ref)

| Tier 3 도메인 | plan 정합 위치 | BN 인스턴스 소비 |
|--------------|---------------|------------------|
| #5~#13 (9 도메인) | L288~289 + L1347 + L1655 | 각 도메인이 본 카탈로그 V3 인스턴스를 BN 소비자로 cross-ref (LOCK-BN-12 V3=50 cap 준수) |

---

## §6. Phase 5 entry-gate (G4-3 forward-defined)

G4-3 "V3 50 인스턴스 배포" — 9개 Tier 3 도메인 매핑 + Cap V3=50 운영 + 도메인 우선순위 매트릭스 영구. V3 50 운영 데이터 baseline + 9 도메인 cross-handoff 영구.

---

## §7. 변경 이력

| 일자 | 변경 | 비고 |
|------|------|------|
| 2026-05-31 | NEW (Phase 4 RECOVERY Stage B genuine write) ★ CORE | P4-3 V3 50 인스턴스 production 정본 단일 카탈로그 — DRAFT 생성. APPROVED→LOCKED+RO TRUE는 Step 4.2.C |
