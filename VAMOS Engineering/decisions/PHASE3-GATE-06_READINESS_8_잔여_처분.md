# PHASE3-GATE-06: READINESS §8 문서수정 매트릭스 38건 — 잔여 확인·처분

> **결정일**: 2026-06-12 (P3-0 미결정 게이트 ⑥) · **포맷**: A6
> **정본**: `docs/sot/VAMOS_IMPLEMENTATION_READINESS_GUIDE.md` §8 (L1050~1108, 38건)
> **방법**: 38건 전수 디스크 실측(Select-String 패턴 대조, 2026-06-12) — 본 게이트에서 SOT 수정 0건(원칙 준수), 잔여는 책임 게이트 배정.

## 결정 — 분류 확정: 기집행/실효해소 22건 · supersede 3건 · 잔여 13건 (R1 차단 0)

### A. 기집행 / 실효 해소 (22건 — 추가 액션 불요)
#1(S7F-012 Python 정본 L145) · #2(PHASE_B2 정본 오버라이드 L156) · #3(config.yaml 잔존 0 — L441은 promptfooconfig.yaml로 별개 도구 파일명, 비해당) · #6(MASTER_SPEC config.yaml 0) · #7/#8/#9(I-21~25 BEGINNER·MASTER_SPEC·PLAN-3.0 전수 존재) · #14(D2.0-01 버전 태그 L882~) · #15(utcnow 잔존 0) · #19(BEGINNER 4요소 잔존 0) · #21/#22(Front Mini 위치·책임 명시 — D2.0-02 §1.4, MASTER_SPEC L149/L160) · #23(D2.1-D7 GuardrailsCheckSchema ADD-013~015 반영 L13/L173) · #24(D2.0-07 4-Layer L1743) · #26(React 18 L139-140) · #27(DEC-001 Allowlist L3898) · #32(AGENT_TEAMS HMAC L317~) · #33(sdar.* L259-260) · #35(D2.1 v3.0.1 승격 — 세션7 기집행) · #38(PLAN-2.0 SUPERSEDED — 자체 L1 배너 + MASTER_SPEC L39 표기)

### B. 후속 결정으로 supersede (3건 — 원 액션 폐기, 집행 금지)
- **#5** (D2.0-01 §8.5 "V0 비용 상한 = V1 동일 적용 ₩40,000 명시"): **D10이 반대 방향으로 확정** — V0 정본 비용 = ₩0(로컬 전용), ₩40,000은 V1 한도의 엔진 사전 설정. 원문대로 집행하면 D10 위반. §9.1 #3 체크 항목도 D10 프레임("V0=₩0 + V1 한도 사전 설정")으로 읽는다.
- **#16/#17** (approval_status에 pending/expired 추가): **PL-09 FIX가 D7 정본 2값(approved/denied)으로 확정** — MASTER_SPEC L434 실측 "approval_status: Literal[\"approved\",\"denied\"] # D7 정본 2값 (PL-09 FIX)". 원 액션 폐기.

### C. 잔여 (13건 — 책임 게이트 배정, 전부 SOT 수정이므로 집행은 해당 게이트에서 승인 후)
| 시점 | 항목 | 책임 게이트 |
|------|------|------------|
| **V0 전 (1건)** | #4 MASTER_SPEC §0 인덱스 B그룹 "(= IMPLEMENTATION 계층)" 추가 (V0-002) — "IMPLEMENTATION" 문자열 실측 0 | **P4-0** (스킬 점검 세션 선행 액션) |
| V1 전 (5건) | #18 MASTER_SPEC L990/L1542 QoD 4요소 잔존 정정(=CONFLICT-005, GATE-07 §a 연동) · #20 D2.1-D6 SourceQoD 5필드 반영 확인 · #25 STEP7_F-I 비용 "BASE ₩40,000 / 최소 운영 $8" 구분 · #36 BEGINNER B↔L 매핑표(L656 매핑표의 B↔L 충족 여부 확인 포함) · #37 STEP7_보강_통합명세서 "범위 묶음 ~1,485" 비고 | **P6-0** |
| V1 전 → **V2 전 재배정 (4건)** | #10/#11(E-15 "File System / Cloud Collector") · #12/#13(S-5 "Router Evolution / Cloud Evolver") — GATE-04에서 E-15/S-5 본체 V2 이연 확정에 따라 시점 이동 | **P7-0** |
| V2 전 (5건) | #28(FREEZE 해석) · #29(Lead 위임 vs MessageBus) · #30(CL-Layer 접두어) · #31(CL-G0~G4 접두어 — GATE-07 §a C-002 연동) · #34(QoD=RAG 소스 신뢰도 명시) | **P7-0** |

## 판정
**R1(Phase 3) 차단 항목 = 0.** V0 전 잔여는 #4 단 1건이며 표기 명확화(값 충돌 아님)로 P4-0 선행 액션으로 충분.

## 검토 대안 (기각)
- 본 게이트에서 잔여 13건 일괄 집행 — SOT 자동 수정 금지 원칙(게이트 프롬프트 ⑦a·D1 원칙) 위반 — 기각.
