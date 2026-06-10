# Phase B: 소규모 처리 (< 50K 토큰)

> **소유 도메인**: 5-2_File-Context
> **상위 문서**: `../FILE_CONTEXT_구조화_종합계획서.md` §6.1
> **원본 참조**: `FILE CONTEXT/VAMOS_파일_컨텍스트_이해_최종_업데이트.md` §6 Phase B
> **작성일**: 2026-04-12
> **Phase**: P1-7 (Phase A~G 통합 파이프라인)

---

## 1. 개요

Phase B는 < 50K 토큰 문서를 직접 주입 방식으로 처리한다. 컨텍스트 윈도우 내에서 전체 문서를 직접 읽는 3-Pass 전략을 사용하며, W1 Smart Cascade, W9 Self-Consistency, W11 Attributed QA를 통해 품질을 보장한다.

**V1 배치 기술**: W1(B-1), W9(B-1), W11(B-3)
**V2 예정**: H5 FLARE(B-2) — 위치만 표기 (R7 준수)

**입력**: Phase A 출력 (`PhaseAOutput` — `target_phase == "B"`)
**출력**: 검증 전 응답 → Phase F로 전달

---

## 2. Step 정의

### B-1: 3-Pass 읽기 + [W1] Cascade + [W9] Self-Consistency

#### B-1.1: 3-Pass 읽기 전략 [A1 장점 활용]

**Pass 1: 구조 추출 (Structure Pass)**

| 항목 | 내용 |
|------|------|
| **처리** | 문서 골격 파악 — 제목, 섹션, 목차, 핵심 엔티티 목록 추출, 문서 유형별 스키마 매핑, 전체 요약 1문단 생성 |
| **모델** | W1 Cascade 전략에 따라 결정: 단순→로컬 100%, 중간→로컬, 복잡→로컬 |
| **출력** | `structure: DocumentStructure` |

**Pass 2: 상세 추출 (Detail Pass)**

| 항목 | 내용 |
|------|------|
| **처리** | Pass 1 구조를 프레임으로 사용 → 섹션별 상세 내용 추출, 수치/날짜/조건문 정밀 파악, 교차 참조 관계 기록 |
| **모델** | W1 Cascade: 단순→로컬 100%, 중간→Cloud Mini 30%, 복잡→Cloud Mini 40% |
| **출력** | `details: DetailedContent` |

**Pass 3: 검증 (Verification Pass)**

| 항목 | 내용 |
|------|------|
| **처리** | Pass 1 vs Pass 2 일관성 확인, 누락 섹션 체크, 모순 플래그, Fact Extraction → 원자 명제 분해 → 교차 검증 |
| **모델** | W1 Cascade: 단순→로컬 100%, 중간→로컬, 복잡→Cloud Main 20% |
| **출력** | `verification: VerificationResult` |

> **Cascade 매트릭스 참조**: 종합계획서 부록 A.2 — [`../03_weakness-mitigation/w01_smart_cascade.md`](../03_weakness-mitigation/w01_smart_cascade.md) 상세

#### B-1.2: [W1] Smart Cascade 연동

| 항목 | 내용 |
|------|------|
| **처리** | Phase A-9에서 결정된 `cascade_strategy`에 따라 각 Pass의 모델 선택 |
| **R10 준수** | 세션당 비용 상한 초과 시 로컬 전용 모드 자동 전환 |
| **L16 연동** | Cloud 호출 시 Prompt Caching 적용 (TTL 5분, 90% 절감) |
| **상세 문서** | [`../03_weakness-mitigation/w01_smart_cascade.md`](../03_weakness-mitigation/w01_smart_cascade.md) |

#### B-1.3: [W9] Self-Consistency 3x

| 항목 | 내용 |
|------|------|
| **처리** | **R-52-7 DEFINED-HERE LOCK**: N=3 샘플 생성 |
| **합의 규칙** | 3/3 일치 → 확정 / 2/3 → 다수결 / 불일치 → 재확인 |
| **트리거** | 10~50K 구간(B+): 항상 적용 / < 10K 구간(B): Phase A query 복잡도 점수 ≥ 0.7 시에만 적용 (H16 Confidence는 Phase F 산출물 — Phase B 시점 미존재, 전방 의존 제거) |
| **출력** | `consistency_result: ConsistencyResult` (합의 상태 + 최종 응답) |
| **상세 문서** | [`../03_weakness-mitigation/w09_self_consistency.md`](../03_weakness-mitigation/w09_self_consistency.md) |

### B-2: [H5] FLARE (V2 예정)

| 항목 | 내용 |
|------|------|
| **V1 상태** | **미구현** — 위치 예약만 수행 (R7: V1→V2 참조 금지) |
| **V2 구현** | jzbjyb/FLARE — 장문 생성 시 능동적 재검색, 장문 정확도 +5~15% |
| **V1 폴백** | 3-Pass 검증으로 장문 정확도 보완 |

### B-3: [W11] Attributed QA

| 항목 | 내용 |
|------|------|
| **입력** | B-1 3-Pass 최종 응답 |
| **처리** | 원문 발췌 부착 의무 + BERTScore 일치도 ≥ 0.8 + 출처 환각 탐지 |
| **0.7~0.8 구간** | 경고 플래그 (§8 RK-6 대응) |
| **출력** | `attributed_response: AttributedResponse` (응답 + 인용 목록 + 일치도 점수) |
| **상세 문서** | [`../03_weakness-mitigation/w11_attributed_qa.md`](../03_weakness-mitigation/w11_attributed_qa.md) |
| **Phase F 연동** | F-L3에서 Attribution 재검증 |

---

## 3. 데이터 흐름

```
Phase A 출력 (target_phase == "B")
     │
     ├── structured_elements (H10+H11)
     ├── cascade_strategy (W1)
     ├── sub_queries (H2)
     ├── routing_plan (H3)
     │
     ▼
 B-1: 3-Pass 읽기
     ├── Pass 1: 구조 추출 ──── structure
     ├── Pass 2: 상세 추출 ──── details   (W1 Cascade 모델 선택)
     └── Pass 3: 검증 ────────── verification
          │
          ├── [W9] Self-Consistency 3x ── consistency_result
          │
     ▼
 B-3: [W11] Attributed QA ──── attributed_response
     │
     ▼
 → Phase F (최종 검증)
```

---

## 4. 구간 세분화

| 세부 구간 | 처리 방식 | W9 적용 |
|----------|----------|---------|
| **< 10K** | Phase B 직접 주입, 3-Pass | 조건부 (H16 < 0.7) |
| **10~50K** | Phase B+ 직접 주입, Multi-Pass + 강화 | 항상 적용 |

---

## 5. Phase B 출력 스키마

```python
class PhaseBOutput(BaseModel):  # Pydantic v2 (R2)
    structure: DocumentStructure  # Pass 1
    details: DetailedContent  # Pass 2
    verification: VerificationResult  # Pass 3
    consistency_result: ConsistencyResult  # W9
    attributed_response: AttributedResponse  # W11
    cascade_log: CascadeLog  # W1 사용 이력 (R9: 사용자 노출 금지)
    trace_id: str  # R8: 서버 전용
```

---

## 6. LOCK 값 참조

| LOCK | 값 | Phase B 활용 |
|------|-----|-------------|
| L9 | QoD ≥ 0.6 — Accuracy(0.30)+Relevance(0.25)+Completeness(0.20)+Safety(0.15)+Efficiency(0.10) | Pass 3 QoD 검증 기반 |
| L16 | Prompt Caching — Anthropic ephemeral TTL 5분 90% 절감, OpenAI 자동 50% 절감 (D2.0-02 L1923-2046) | W1 Cloud 호출 시 |
| R-52-7 | Self-Consistency N=3 (DEFINED-HERE LOCK) | W9 샘플 수 |

---

## 7. 에러 핸들링

| 에러 상황 | 처리 |
|----------|------|
| Cloud 모델 타임아웃 | 로컬 모델 폴백 (W1 Cascade 자동 강등) |
| W9 3회 불일치 | 재확인 후 최고 신뢰도 응답 채택 + 불확실성 플래그 |
| W11 BERTScore < 0.7 | 출처 재탐색 (해당 문장 재처리) |
| 비용 상한 초과 | 로컬 전용 모드 전환 (R10) |

---

*변경 이력*

| 날짜 | 변경 | 사유 |
|------|------|------|
| 2026-04-12 | 초기 생성 | P1-7 Phase A~G 통합 파이프라인 문서 |

---

## V2 — Phase B V2 기술 통합 (V2-Phase 2, 2026-05-12, 세션 P2-7)

> **V단계**: V2-Phase 2 (V1 본문 byte EXACT 보존 + append-only) / **chain**: s9_43_c_2
> **종합계획서 §**: §7 Phase 2 P2-7 (L1212~L1235)

### V2 통합 매트릭스 (Phase B < 50K)

| Step | V1 | V2 추가 | V2 산출물 | LOCK |
|:-:|---|---|---|---|
| B-1 | W1 Cascade + W9 (V1) | (V1 유지) | `w01_smart_cascade.md` (V1) | - |
| **B-2** | (V1 미존재) | **H5 FLARE V2 (NEW)** | `../04_advanced-techniques/h05_flare.md` | L1/L15/L16 |
| B-3 | W11 Attributed (V1) | (V1 유지) | `w11_attributed_qa.md` (V1) | - |

### V2 통합 후 데이터 흐름

```
< 50K 입력
  ├─ B-1 (V1: W1 Cascade + W9 N=3 Self-Consistency)
  ├─ ★ B-2 NEW: H5 FLARE 능동 재검색 (장문 +5~15%, response_length > 500)
  └─ B-3 (V1: W11 Attribution)
```

### V2 종결 marker (Phase B)

★ V2 통합 1 NEW (H5) + V1 본문 byte EXACT ✅
★ L1 prefix + L15 NLI V2 CRITICAL 연쇄 + L16 캐시 90% 절감 ✅
★ V2 13개 중 H5 = 1/13 통합 ✅

---

## §V3 EXTEND (Phase 4 implementation)

> **Version**: V3 EXTEND
> **Status**: APPROVED
>
> Status (L4): APPROVED
> L3 판정 (L9): PASS
>
> Phase 4 entry-gate 매핑: P4-3 (Phase A~G V3 최종 통합)
> Phase 5 entry-gate forward-defined: 소규모(<50K) 단계 V3 경계 명시 100% + Phase 5+ 이월
> 작성일: 2026-05-31 (Phase 4 SPEC Stage B, chain phase4_spec_5-2_2026-05-31)

### V3.1 V3 경계 (소규모 <50K — V3 미트리거)

Phase B(소규모 <50K)는 **V3 분산/압축 메커니즘이 트리거되지 않는** 구간이다. <50K는 V1(L5 슬라이딩, ≤32K) 또는 V2 진입 초입(32K~50K)으로 처리되며, Ring Attention/Infini-Attention은 256K+ 전용. V3 단계에서는 **경계 보존**이 핵심 — 소규모 query가 불필요하게 분산 추론 오버헤드를 받지 않도록 라우팅 게이트(`phase_d_v3_strategy.md`)가 차단.

- L16 Prompt Caching(90% 절감) + L1 prefix는 V3에서도 소규모 query 효율 유지.
- L15 NLI V2 CRITICAL 연쇄 보존 (V3 무영향).

### V3.2 검증

- [x] Phase B V3 경계(소규모 V3 미트리거) 명시 + [x] Phase 5 entry-gate forward-defined + [x] V2 본문 byte EXACT 보존

★ V3-Phase 4 (2026-05-31, P4-3) ✅ | 소규모 V3 미트리거 경계 보존 (라우팅 게이트 차단) | L3 판정: PASS (Stage B 전환 완료)
