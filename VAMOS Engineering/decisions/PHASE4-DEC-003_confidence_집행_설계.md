# PHASE4-DEC-003 (P4-0 ⑨): confidence 집행 설계 — DecisionSchema 20필드 + [confidence] 섹션 3키 + PART2 연쇄 갱신

> **결정일**: 2026-06-12 (P4-0) · **포맷**: A6 · **우선순위**: Must · **출처**: P4-PRE A-04 · **키 사양 정본**: PHASE3-DEC-010

## 결정

### 1. DecisionSchema 18 → 20필드 (FREEZE 확장 — DEC-010 기확정의 집행)
- `confidence_score: float` (0.0~1.0) + `confidence_level: Literal["HIGH","MEDIUM","LOW","REFUSE"]` — **둘 다 required** → **16 required + 4 optional = 20**.
- required 채택 이유: DEC-010 행동 분기(REFUSE 포함)가 모든 Decision에 level 판정을 요구하며 EvidenceGate insufficient→강제 REFUSE도 값 존재를 전제. A23 Expand(optional 권장)는 가동 중 시스템 마이그레이션용 — V0는 신규 생성이라 비적용. V0부터 산출 로직 포함(runtime_eng_plan R2a V0 스코프 "confidence_score").
- 필드 정의의 나머지 18필드 정본 = D2.1-D2 §4.1 (14+4) — 창작 0.

### 2. config 키 배치 — 신규 `[confidence]` 섹션 (V0 config 13→14섹션)
```toml
[confidence]                          # PHASE3-DEC-010 신규 LOCK 3키 (Registry §8 R1-A25)
confidence_high_threshold = 0.85      # LOCK
confidence_medium_threshold = 0.60    # LOCK
confidence_refuse_threshold = 0.30    # LOCK
```
- 키 이름은 DEC-010 등록 명칭 그대로 보존(LOCK 명칭 불변). PHASE_B4 §3에 없는 신규 섹션이므로 **B4 SOT 동기는 수정 지시로 등재**(승인 후, P4-1 비차단: 구현 상세 정본은 PART2).
- ⟦집행 기록 (사용자 승인 2026-06-12)⟧ **B4 §3.16 신설 완료** — 실측 B4 §3 = 3.1~3.15(+3.8a/3.8b)=17섹션, 다음 번호 **3.16**(초안 "§3.17"은 추정 오기 정정). §4.1 V1 프리셋 toml에 [confidence] 동반 추가. integrity v13_integrity_check_20260612T230000.json CHANGED_AS_APPROVED.
- config.v1.toml 실생성·LOCK 분모 23 적용·check_config_lock.py 분모 갱신은 **4-5 바인딩**(DEC-010 기확정 — 재론 없음).

### 3. PART2 V0-STEP-2 연쇄 갱신 (본 세션 집행, CRLF 보존)
① 25모델 표 2곳(L581·L687) "DecisionSchema | 18 (FREEZE)" → "20 (FREEZE+DEC-010 confidence 2필드)" ② 사용자 작업(L645) ③ 규칙(L768) "18필드 (14+4)" → "20필드 (16+4)" ④ FREEZE_SNAPSHOT 주석+본문(L778-782) 18fields→20fields ⑤ Stage Gate #2(L817) `len==18`→`len==20` ⑥ STEP-6 test 예시(L1463-1466) `== 18`→`== 20` ⑦ 약기 테이블 Decision 행(L720)을 D2.1-D2 §4.1 실필드+confidence 2필드로 교체 ⑧ config 템플릿 2곳에 [confidence] 섹션 추가 + "13섹션" 표기 연쇄(L246·L562·L1332·L1367) 14섹션 현행화 ⑨ VamosConfig 서브모델 목록(L1314-1330)에 `confidence: ConfidenceConfig` 추가. seed json·test 실파일은 STEP 6 산출물이 20필드로 생성.

## 근거
PHASE3-DEC-010(스키마 확장+3키 LOCK+분기 — 기확정) · D2.1-D2 §4.1 18필드 실측 · P4-PRE A-04(PART2 미반영 적시) · 로드맵 4-5 행(confidence 3키 기반영).

## 기각 대안
- confidence 2필드 optional(14+6) — REFUSE 분기 무결성 약화, V0 신규 생성에 Expand 패턴 불필요. 기각.
- 기존 섹션([self_check] 등) 편입 — 의미 불일치(self_check는 S6 품질 게이트 임계) + B4 §3.8a LOCK 4키 구조 교란. 기각.
