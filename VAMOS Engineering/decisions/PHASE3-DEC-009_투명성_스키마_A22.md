# PHASE3-DEC-009 (3-7b): 사용자 투명성 — reasoning_trace/evidence_sources 스키마 상세 (A22)

> **결정일**: 2026-06-12 (P3-1) · **포맷**: A6 · **우선순위**: Must
> **전제 (재결정 아님)**: D6 기확정 (2026-06-11, DECISION_REGISTER) — **선택지A**: 신규 필드는 ResponseEnvelope.**metadata(dict) 내부** 포함, 기존 필드 LOCK 보존, 선택지B(top-level 추가·LOCK 해제) 기각. 본 결정은 그 틀 안의 **스키마 상세만** 확정.

## 결정 — metadata 내부 확장 키 4종 스키마

```python
# ResponseEnvelope.metadata 내부 (top-level 구조 무변경 — D6)
class GateTraceEntry(BaseModel):
    gate: Literal["PolicyGate","ApprovalGate","CostGate","EvidenceGate","SelfCheckGate"]
    result: Literal["PASS","FAIL","DOWNSHIFT","DENY","SKIP"]   # SKIP = V0 미구현 슬롯
    detail: dict = {}            # 게이트별 부가: evidence_count, confidence, downshift_to 등

class EvidenceSourceEntry(BaseModel):
    source: str                  # 소스 명칭/ID (D2.0-02 EvidenceItem.source_id 사상)
    date: str                    # ISO 8601
    relevance: float             # 0.0~1.0

metadata["reasoning_trace"]: list[GateTraceEntry]      # DEC-001 실행 순서대로 append
metadata["evidence_sources"]: list[EvidenceSourceEntry]
metadata["confidence_score"]: float                     # 0.0~1.0 — DEC-010과 동일 값 (단일 출처: Decision)
metadata["disclaimer"]: str | None                      # A16 — 민감 영역(투자/건강) 응답 시 필수
```

- **수용처 검증**: 스키마 정본 D2.1-D5 §4.9 ResponseEnvelopeSchema는 `metadata`(object, required) 필드 보유 (L394) — 구조 변경 없이 수용 가능. 설계 정본 D2.0-02 §5.1.1 envelope(answer/evidence/self_check/decision_ref/audit)와 D2.1-D5 9필드 표기 차이는 계층 차이(설계 vs 스키마)이며, 어느 표기 기준으로도 **top-level 불변 + metadata 내부 확장** 원칙(D6)이 동일 적용된다.
- **evidence_sources ↔ 기존 evidence 관계**: evidence_sources는 D2.0-02 EvidenceItem(L745-751)의 **UI 표시용 요약 사상**(source/date/relevance 3필드) — 원본 EvidenceItem을 대체하지 않음(중복 아닌 뷰).
- **UI 표현**: 기본 답변 + [왜?] 버튼 펼침(근거 N건·게이트 검증·신뢰도·면책) — STRATEGY_05 §4.3, 구현은 Phase 4 R2c(4-3).

## 근거 (정본 라인)
D6 (DECISION_REGISTER — "선택지A 채택 확정… 5필드 LOCK 보존", edits 1 기적용) · STRATEGY_05 §4.2 L154-169(선택지A 스키마 원형) · D2.1-D5 §4.9 L374-398(metadata object) · D2.0-02 §5.1.1 L723-759(envelope 정본+UI 최소 필드) — LOCK 재정의 0 (LOCK Registry 신규 등록 R1-A22: "확장은 metadata 내부 한정" 원칙).

## 이유·대안
D6 틀 준수가 전부 — top-level 추가 재론 금지. detail을 dict로 둔 것은 게이트별 이질 정보(비용/근거 수/점수)를 단일 스키마로 강제하지 않기 위함(과도한 조기 고정 회피).

## 구현 바인딩
V0: reasoning_trace(Gate 3종+SKIP 2)·confidence_score부터 기록(4-2). evidence_sources/disclaimer는 V1(RAG·민감 도메인 활성 시점).
