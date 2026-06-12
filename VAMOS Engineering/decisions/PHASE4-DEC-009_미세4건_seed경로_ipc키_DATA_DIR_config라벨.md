# PHASE4-DEC-009 (P4-0 ⑮): 미세 4건 — seed 경로 / [core] ipc 키 / ${VAMOS_DATA_DIR} / config 라벨

> **결정일**: 2026-06-12 (P4-0) · **포맷**: A6 · **우선순위**: Must(미세) · **출처**: P4-PRE B-01b~e

## 결정

### 1. seed 경로 = 리포 루트 `schemas/seed/` (B-01b)
PART2 STEP-2 전제 코드(`pathlib.Path("schemas/seed")`, CWD=리포 루트)와 표기 그대로 일치하는 **루트 채택**. seed는 SOT 추출 JSON(언어 중립·codegen/AI 입력)으로 backend 런타임 자산이 아님. 집행: PART2 STEP-1 디렉토리 트리 2곳에 `schemas/seed/` 1줄 추가(트리 누락 reconcile).

### 2. `[core]` ipc 키 포함 확정 (B-01c)
P4-1 config.v1.toml 생성 시 `[core] ipc_max_restart = 3`·`ipc_timeout_s = 30` 포함 — 값 정본 = PART2 L919/L921(FIX-027: [ipc] 섹션은 B4 미정의 → [core] 하위). 비-LOCK 키(분모 23 무영향). PART2 무수정(FIX-027 주석 기존재).

### 3. `${VAMOS_DATA_DIR}` 정의처 = `.env.example` 추가 — 집행 완료 (B-01d)
실측: 루트 `.env.example`(11변수 체계)에 VAMOS_DATA_DIR **부재** ↔ config 정본(PHASE_B4 §3.4~3.6)이 `${VAMOS_DATA_DIR}` 5곳 참조. `VAMOS_DATA_DIR=./data` 1줄 추가(Storage Paths 절, 기존 키 삭제 0 — R4). 기존 SQLITE_DB_PATH·CHROMA_PERSIST_DIR은 보존(레거시 직접 경로, config.v1.toml 도입 후 ${VAMOS_DATA_DIR} 일원화가 우선).

### 4. config 라벨 "17섹션" 표기 정정 (B-01e)
PART2 L418 "✅ V1 확장판 (정본, 17섹션)" → 실수록 13섹션(+confidence 14, DEC-003)이므로 "V0 14섹션 (PHASE_B4 §3 정본 LOCK 값 — V1+ 17섹션 확장은 B4 §3 전체 참조)"로 정정. L246 주석의 오포인터("아래 §2 STEP-3의 V1 확장판(17섹션)")도 "V1+ 확장 17섹션은 PHASE_B4 §3 정본 참조"로 정정. "13섹션" 연쇄(L246·L562·L1332·L1367)는 DEC-003 ⑧항과 통합 집행(14섹션).

### ※ 부수 발견 (본 세션 신규 — 기록·처분)
PART2 V0-STEP-2 "25개 모델 핵심 필드 참조" 약기 테이블이 D2.1 SOT와 다수 이탈(실측 확정: #3 Decision[SOT=ref 기반 18필드 ↔ 약기=chosen_action 등 별계열] · #11 CostBudget[SOT 9필드에 threshold 없음] · #12 Downshift[SOT=warn/block_percent+trigger ↔ 약기=from_model/to_model]). PART2 자체 중재 규칙(Method B/C: "불일치 시 근거 문서(SOT) 우선 채택") 기존재로 **차단 아님** — STEP 6 산출물은 전건 D2.1 SOT에서 직접 추출. 약기 테이블 전면 재작성은 과대 수정(2곳 × 25행)이므로 테이블 직상 경고 주석 1줄 보강으로 처분(Decision 행만 DEC-003 ⑦항이 교체).

## 근거
PART2 L516-523(seed 경로 표기)·L919/L921(FIX-027)·PART1 E.5 #3(.env.example 11변수)·PHASE_B4 §3(${VAMOS_DATA_DIR} 참조)·L418/L246 실측(13섹션 수록) · D2.1-D2 §4.1/D2.1-D7 §4.3·4.4 필드 실측.
