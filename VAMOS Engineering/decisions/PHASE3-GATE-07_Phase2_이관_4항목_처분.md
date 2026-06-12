# PHASE3-GATE-07: Phase 2 이관 4항목 처분 (PROGRESS L21 정본 체크리스트)

> **결정일**: 2026-06-12 (P3-0 미결정 게이트 ⑦) · **포맷**: A6
> **원칙**: SOT(docs/sot·docs/sot 2) 자동 수정 0 — 수정 필요 판정 건은 대상·근거·edits를 본 결정문에 명기하고 **집행은 사용자 승인 후 책임 게이트에서** 수행.

---

## a. SOT 내부 이형 9건 처분 (step1 CONFLICT-001~008 + step3 R-8 사유 이형)

| ID | 정본 판정 (우선순위 적용) | 처분 | 수정 지시 edits (승인 후 집행) | 시점 |
|----|--------------------------|------|-------------------------------|------|
| C-001 | **5-Gate** (D2.0-02 §8.1 LOCK L2531: Policy→Approval→Cost→Evidence→SelfCheck) | **수정 지시** | ①D2.0-01 L208 ②MASTER_SPEC L1512 ③BEGINNER L1376 — 4-게이트 열거 → 5-Gate 전체 열거. ④sot CLAUDE.md L236은 **§b 스냅샷 동기화로 자동 해소**(루트 946줄판은 기정합) | P4-0 |
| C-002 | G0~G4 = **Cloud Library S-5 검증 게이트 전용 라벨** (안전 5-Gate와 별개 체계) | **수정 지시** | AGENT_TEAMS L50·STEP7_A-E L502/L977 라벨 한정 표기 — READINESS §8.3 #31(CL-G0~G4 접두어)과 동일 계열로 통합 집행 | P7-0 |
| C-003 | 운영 정본 = **70/75/80** (D2.0-02 §7.53-1 LOCK L1828-1830 — "PLAN 고정 관문 원칙 유지 + 런타임 위험도 가변" 명시 조정) | **RESOLVED (NO_FIX)** | 없음 — PLAN-3.0 L3760/L3776/L6604은 P0 기준·보수적 단순화 표현으로 해석 확정(step1 판정 채택). CLAUDE.md 946줄판 기정합 | — |
| C-004 | 운영 표기 = **PHASE_B4 §3.9 (V1/V2=2 · V3=3)** — §d와 통합 처분 | **RESOLVED(운영) + DEFER(V3 근거)** | V3=3의 D2.0-03 근거 보강 + B4 V3 예시 config L829-830에 `max_retries = 3` 명기 — V3 사이클 진입 전 | P8-0 |
| C-005 | 출력 QoD = **PLAN-3.0 5요소** 정본 (L239-243) / 4요소는 SourceQoD(RAG 소스, D2.0-06 L1333) 한정 — V1-006 기확정의 물리 미반영 잔존 | **수정 지시** | MASTER_SPEC L990·L1542 — 용도 한정 없는 "QoD 가중치" 4요소 표기를 5요소 정본+SourceQoD 한정 표기로 정정 (READINESS §8.2 #18과 동일 건) | P6-0 |
| C-006 | V2 비용 상한 = **₩93,000** (BASE-1.3 §5 L204-205 ABSOLUTE LOCK) | **수정 지시** | STEP7_보강_통합명세서 L526 "V2 월간 ₩40,000 예산" → "멀티모달/스케일링 서브예산 ₩40,000 (V2 상한 ₩93,000과 별개)" 한정 표기 | P7-0 |
| C-007 | V1 Embedding 기본 = **1024차원** (config LOCK 20 + D2.0-06 결정 섹션 L1338/L1487) / 256 = Matryoshka 경량 옵션 | **수정 지시** | D2.0-06 L779·L852·L854 (S7D-014/027) — "V1 기본 256" → "옵션: Matryoshka 256 (기본은 1024, 결정 섹션 정본)" 주석 | P6-0 |
| C-008 | I-모듈 = **25개** (D2.0-01 §5.6 LOCK) — 불일치 잔존처는 PLAN-2.0 L58 단독 | **RESOLVED (NO_FIX)** | 없음 — PLAN-2.0은 문서 전체가 SUPERSEDED 배너(L1 실측) 보유, 개별 행 배너 불요 | — |
| R-8 (9번째) | STEP7 60건 차이의 해소 기록 정본 = **READINESS_GUIDE L1003 "범위 묶음(range bundle) 전개"** (CC-011 등록·해소 절차를 거친 기록). 마스터인덱스 L26 "유령 ID 정정 전 추정치"는 사유 서술 이형(수치 ~1,485는 양측 일치) | **수정 지시 (경미)** | 마스터인덱스 L26에 CC-011 범위 묶음 사유 병기 1행 — 실질 영향 0, 비차단 | P6-0 |

**소계**: RESOLVED/NO_FIX 2건(C-003·C-008) + 운영확정·DEFER 1건(C-004) + 수정 지시 6건(C-001·C-002·C-005·C-006·C-007·R-8) — **전건 비차단, SOT 수정 0건 수행** (지시만 등재).

---

## b. docs\sot\CLAUDE.md 스냅샷 ↔ 루트 CLAUDE.md 비동기 — **동기화 채택**

**결정**: 루트 `D:\VAMOS\CLAUDE.md`(48,788B·946줄·GOLD)를 `docs\sot\CLAUDE.md`(실측 33,320B·709줄 = §21~§28 보강 전 구판)로 **byte 동일 전문 복사**하여 동기화한다. 집행은 SOT 폴더 변경이므로 **승인 후**(권장: 본 게이트 결과 승인과 함께) 수행하고, 집행 시 integrity 신규 snapshot으로 D2 기준선을 재기록한다. 이후 운영 규칙: 루트 CLAUDE.md 변경이 발생한 Phase의 게이트(A12 대조)마다 재동기화.

- 이유: ①구판 스냅샷이 SOT 코퍼스 내 이형 발생원(C-001의 "CLAUDE.md (sot) L236" 4-게이트 표기가 실례) ②보강전략 §1.1이 루트를 유일 보강 대상 정본으로 명시 — 스냅샷은 사본 위상이므로 정본 추종이 원칙 ③Phase 3 R1 작업이 SOT 폴더를 컨텍스트로 로딩할 때 구판 참조 오염 방지.
- 기각 대안: (i) 비동기 유지+표지 배너 — 이형 잔존 + 배너 추가 자체가 또 다른 내용 차이 생성. (ii) 스냅샷 삭제 — SOT 68 파일 분모·기존 참조(D1 산출물·step1 인용) 훼손.

---

## c. 5-4 SHELL 87 처분 — PHASE2-DEC-02 이연 결정의 집행 방침 확정

**결정**: 5-4_v23-Extension-Items SHELL 87건은 **전건 v23 확장(V2+) 스코프로 확정**하고, 상세화는 **P7-0(V2 진입 게이트)에서 V2/V3 귀속 분모 확정 후 해당 사이클 설계 세션이 작성**한다(GATE-05 reconcile 방침과 동일 경로). Phase 3~6 동안 작성 0건 · 오류리스트 §G.1 REGISTERED 추적 유지 · 5-4 도메인 EXCLUDED/SHELL 표기 유지.

- 이유: PHASE2-DEC-02 결정 1의 근거 ②("V2/V3 스코프 결정이 선행돼야 함 — 그 결정처가 3-0")를 본 게이트가 수행한 결과, 귀속 결정처는 V2 사이클 진입 게이트(P7-0)가 정본 위치다(로드맵 Phase 7 편입으로 착지점 존재). "없는 내용 창작 금지" 원칙상 귀속 미정 상태의 선제 작성은 계속 금지.

---

## d. LOCK-MCP-06(3회) vs PHASE_B4(V1/V2=2·V3=3) — 단일 표기 확정

**결정**: 운영 단일 표기 = **"MCP max_retries: V1/V2=2 · V3=3 — config 정본 PHASE_B4 §3.9"** (CLAUDE.md §7.4 기채택 표기 유지). LOCK-MCP-06("max 3회, 지수 백오프 factor 2.0", sot2 4-3 AUTHORITY_CHAIN L62)은 **MCP Bridge 구현 명세의 재시도 상한 LOCK**으로 무수정 보존(재정의 0)하며, V3 값(3)과 정합한다. V1/V2 런타임 재시도 횟수는 config 주입값(2)이 적용된다 — retry_circuit_breaker.md의 RetryPolicy 기본 3은 상한이며 config가 상한 이내로 결정(구현 시점 V1-Phase 6에서 config 연동 구현).

- 근거 계층: D2.0-03 L428/L1199 "max_retries = 2"(DESIGN 본문) > 상세명세 §B-3(LOCK-MCP-06 출처, STEP7 계열) — V1/V2=2가 상위 정본. V3=3은 PHASE_B4 §3.9 단독 표기로 CONFLICT-004의 D2.0-03 근거 보강이 잔여 → **P8-0 DEFER** (§a C-004 행과 동일).
- 기각 대안: (i) LOCK-MCP-06 값(3)을 전 버전 적용 — DESIGN 본문(2) 역행 + CLAUDE.md GOLD 표기·PHASE_B4·D3 스키마 기본값(2) 3곳 수정 유발. (ii) LOCK-MCP-06을 2로 수정 — sot2 LOCK 재정의(Phase 4 전 도메인 불변식 "LOCK 재정의 0" 파괴).

---

## 종합
4항목 전건 단일 결론 확정. SOT/SOT2 물리 수정 0건(수정 지시 7건은 P4-0/P6-0/P7-0/P8-0 배정 + §b 동기화 1건은 승인 후 집행). R1 차단 0.

---

## ⟦집행 기록 — §b 스냅샷 동기화 (사용자 승인 2026-06-12)⟧

**동기화 완료**: 루트 CLAUDE.md → docs\sot\CLAUDE.md byte 동일 복사. 양측 SHA-256 `1FF0D3C0…4862431A` 일치 · CR=0 · 48,788B · 946줄 (GOLD 상태). 구판(33,320B·709줄, SHA `192F534C…`) 백업: `_targets\_integ\backup_phase3\CLAUDE.md.sot.pre-sync-20260612`. integrity 신규 체크: `v13_integrity_check_20260612T175049.json` (changed 41 = 세션4~7 콘텐츠 수정분+본 동기화, 신규 참조 기준 — D-4 선례). 이에 따라 §a C-001의 sot CLAUDE.md L236 건은 해소 완료.

**⚠️ 부수 사건 — git EOL 손상 및 전수 복구 (동일 세션)**: GATE-08 main ff 1회차 집행의 브랜치 체크아웃 왕복이 `core.autocrlf=true`(시스템 설정)와 결합해 두 브랜치 간 차이 파일 824건의 작업 트리를 LF→CRLF로 재작성함을 발견.
- **복구**: ① repo-local `core.autocrlf=false` 설정 ② 06-04 integrity 기준 해시 ↔ 1c3cede blob의 LF/CRLF 양방 SHA 대조 + backup_session5 실측으로 824건의 역사적 디스크 EOL 기계 판정 ③ LF군 725건을 blob 원본으로 재작성(역사적 CRLF군 27건은 체크아웃이 byte 동일 재생성했으므로 무손상·무조치, 바이너리 29·LFS 14·HEAD삭제 29 제외) ④ 교차검증: 1-1 상세명세 blob = 11,960B·sha16 3AE9E739로 프로젝트 기록 불변식과 정확 일치 ⑤ 최종 검증: CLAUDE.md LF·946 GOLD / 로드맵·PROGRESS·프롬프트·STRATEGY_02 순수 LF / PART1(CR 1,329)·PART2(CR 6,454) CRLF 보존 / git diff 0 (blob 무변화 — 커밋 이력 무영향).
- **재발 방지 규칙 (확정)**: ① 본 repo에서 브랜치 체크아웃/전환 금지 원칙 — main 동기화는 `git fetch . <branch>:main`(작업 트리 비접촉)으로 수행 ② 역사적 CRLF-디스크/LF-blob 이중 상태 파일(~684건: PART1·PART2·READINESS_REVIEW·STEP7 가이드군·D2.0-03~06 등)의 EOL 정규화 여부는 P4-0에서 결정 후보로 등재.
