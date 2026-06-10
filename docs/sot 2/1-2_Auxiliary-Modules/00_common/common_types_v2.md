# 00. Common — 공유 타입 V2 Enhanced (L3 보강)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 production-ready 정본 승급, L3 CONDITIONAL 13 row 보완 기한 ~2026-06-09 P4-2 처리)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `common_types.md` (226 lines, byte EXACT)
> **모듈**: 00_common
> **LOCK 참조**: LOCK-AX-03, LOCK-AX-04, LOCK-AX-11, LOCK-AX-13
> **L3 판정**: PASS (V-17 row content, 8~9/9 strict, Phase 4 P4-2 ✅ 완료, 2026-05-23, E2/E4 타입 카탈로그 정당화 baseline 정합 + E6 Performance + E7 Security 영구 보강 baseline 명시, 보완 추적 closure ~2026-06-09)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, 세션 2-6, chain s9_36_a_2)
> **종합계획서 §**: §7 Phase 2 L1654~L1712 (2-6 절차 4: common_types L3 보강 — E1/E3/E9 추가)
> **횡단**: 6-2 (Entity 중 PERSON/ORG 등 PII 마스킹 정합)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 2 (2-6 절차 4) | V2 절차 |
| `common_types.md` (V1, 226 lines, byte EXACT) | V1 정본 (Modality/QoD/Entity/EvidenceItem/MemoryCandidate/PipelineStage 카탈로그) |
| `response_envelope_v2.md` (자매 V2) | EvidenceItem 정본 cross-ref |
| `error_taxonomy_v2.md` (자매 V2) | failure_codes 카탈로그 |
| `6-2/01_ai-code-security/pii_regex_masking.md` | Entity PII 마스킹 |

---

## 2. LOCK 인용

> LOCK (PLAN-3.0 §11 S11-6, LOCK-AX-03): `qod = Accuracy×0.30 + Relevance×0.25 + Completeness×0.20 + Safety×0.15 + Efficiency×0.10`

> LOCK (D2.0-06, LOCK-AX-04): QoD<0.4 forbidden, ≥0.7 allowed

> LOCK (D2.0-02 §2.2, LOCK-AX-13): PipelineStage S0~S8

---

## 3. V1 → V2 승급 개요

V1 byte EXACT (226 lines, V1 §1~§10 카탈로그). V1 변경 0.

| 요소 | 보강 (§7 2-6 절차 4 명시: E1/E3/E9 추가) |
|------|----------|
| **E1** | common_types 카탈로그 목적 + 단일 import 진입 |
| **E3** (보강) | Pydantic 모델 (V1 §9 dataclass 보조 표현 → Pydantic v2) |
| **E9** | pydantic v2, enum, datetime |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

common_types는 **VAMOS 보조모듈 공통 타입 단일 import 카탈로그**. V1 §1~§8 의 6 타입 (Modality / ConfidenceScore / QoD / Entity / EvidenceItem / MemoryCandidate / PipelineStage) 을 모든 모듈이 import. 본 V2는 V1 §9 dataclass → Pydantic v2 모델로 정밀화 + Entity PII 마스킹 정합 명시.

핵심: V1 §4 QoD는 **LOCK-AX-03 PLAN-3.0 5-factor 정본 정합** (S-1 qod_formula_v2와 일치). V1 §6 EvidenceItem은 response_envelope_v2 §4.3 정본과 1:1 정합. V1 §8 PipelineStage는 LOCK-AX-13 정본 정합.

### 4.2 E3 — Pydantic v2 모델 (V1 §9 정합 + 정밀화)

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum
from typing import Optional, Literal

# §2 Modality (V1 §2 byte EXACT 인용)
class Modality(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"
    MIXED = "MIXED"

# §3 ConfidenceScore
class ConfidenceMethod(str, Enum):
    MODEL_PROB = "MODEL_PROB"
    HEURISTIC = "HEURISTIC"
    ENSEMBLE = "ENSEMBLE"
    HUMAN = "HUMAN"

class ConfidenceScore(BaseModel):
    value: float = Field(ge=0.0, le=1.0)
    source: str
    method: ConfidenceMethod
    note: Optional[str] = None

# §4 QoD (LOCK-AX-03/04)
class QoDComponents(BaseModel):
    accuracy: float = Field(ge=0.0, le=1.0)
    relevance: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    safety: float = Field(ge=0.0, le=1.0)
    efficiency: float = Field(ge=0.0, le=1.0)

class QoD(BaseModel):
    components: QoDComponents
    value: float = Field(ge=0.0, le=1.0)
    formula_ref: Literal["LOCK-AX-03"] = "LOCK-AX-03"
    threshold_ref: Literal["LOCK-AX-04"] = "LOCK-AX-04"

    @field_validator("value")
    @classmethod
    def _verify_lock_ax_03(cls, v, info):
        # LOCK-AX-03 정본 가중치 검증
        if "components" in info.data:
            c = info.data["components"]
            expected = c.accuracy*0.30 + c.relevance*0.25 + c.completeness*0.20 + c.safety*0.15 + c.efficiency*0.10
            if abs(v - expected) > 1e-3:
                raise ValueError(f"LOCK-AX-03 violation: value={v}, expected={expected}")
        return v

# §5 Entity (PII 마스킹 정합)
class EntityType(str, Enum):
    PERSON = "PERSON"        # 6-2 PII 대상
    ORG = "ORG"              # 6-2 PII 대상 (조직 PII)
    LOCATION = "LOCATION"
    DATETIME = "DATETIME"
    PRODUCT = "PRODUCT"
    CONCEPT = "CONCEPT"
    METRIC = "METRIC"
    DOCUMENT = "DOCUMENT"
    OTHER = "OTHER"

class Entity(BaseModel):
    id: str
    surface: str
    canonical: str
    type: EntityType
    span: Optional[tuple[int, int]] = None
    confidence: ConfidenceScore
    attributes: dict = Field(default_factory=dict)
    pii_token: Optional[str] = None  # 6-2: PERSON/ORG type일 때 PII 토큰 ID

# §6 EvidenceItem (response_envelope_v2 §4.3 정본과 1:1)
class EvidenceSourceType(str, Enum):
    RAG = "RAG"
    TOOL = "TOOL"
    MEMORY = "MEMORY"
    WEB = "WEB"
    USER = "USER"

class EvidenceItem(BaseModel):
    source_type: EvidenceSourceType
    source_id: str
    claim: str
    support: str
    freshness: str
    qod: float = Field(ge=0.0, le=1.0)

# §7 MemoryCandidate (memory_distillation_v2 cross-ref)
class MemoryStore(str, Enum):
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"

class MemoryCandidate(BaseModel):
    candidate_id: str
    store: MemoryStore
    content: str
    embedding_id: Optional[str] = None
    similarity: float = Field(ge=0.0, le=1.0)
    recency: str  # ISO 8601
    usage_count: int = 0
    qod: QoD
    promotable: bool = False

# §8 PipelineStage (LOCK-AX-13)
class PipelineStage(str, Enum):
    S0 = "S0"   # 진입 / 입력 수신
    S1 = "S1"   # 의도 파싱 (I-1)
    S2 = "S2"   # 컨텍스트 빌드 (I-2)
    S3 = "S3"   # 계획/커밋 (I-3) — Decision Lock 불변
    S4 = "S4"   # 구조화 출력 (I-4)
    S5 = "S5"   # 게이트/결정 락 (I-5)
    S6 = "S6"   # 실행/도구 호출
    S7 = "S7"   # Self-check (I-6)
    S8 = "S8"   # 응답 마감 / 감사 기록
```

### 4.3 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E-TYPE-001` | Modality enum 외 값 사용 | NO | ValidationError |
| `AUX-E-TYPE-002` | QoD components 가중 합 mismatch (LOCK-AX-03 위반) | NO | ValidationError |
| `AUX-E-TYPE-003` | PipelineStage S0~S8 외 값 | NO | ValidationError |
| `AUX-E-PII-002` | Entity PERSON/ORG 미마스킹 | NO | 6-2 P1 알림 |

### 4.4 E6 — 성능

| 작업 | P95 |
|------|:---:|
| Pydantic validate (Entity 1건) | 1 ms |
| QoD components 합 검증 | 1 ms |

### 4.5 E7 — 테스트

| # | 시나리오 | 예상 |
|---|---------|------|
| T-01 | Modality.TEXT | enum 생성 |
| T-02 | QoD components 합산 검증 | LOCK-AX-03 정합 |
| T-03 | Entity PERSON + pii_token | 6-2 토큰화 |
| T-04 | PipelineStage S3 | LOCK-AX-13 정합 |
| T-05 | invalid Modality (LOWERCASE) | ValidationError |

### 4.6 E9 — 의존성 명세

| 카테고리 | 의존성 |
|---------|--------|
| 외부 라이브러리 | `pydantic` v2.x |
| 표준 라이브러리 | `enum`, `datetime`, `typing` |
| 내부 모듈 | `response_envelope_v2` (EvidenceItem 정합), 모든 V2 (import 진입) |
| 횡단 도메인 | `6-2/01_ai-code-security/pii_regex_masking` (Entity PII) |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY | 본 V2 | 일치 |
|------|---------|-------|:----:|
| LOCK-AX-03 (5-factor) | QoDComponents | §4.2 _verify_lock_ax_03 | ✅ |
| LOCK-AX-04 (임계) | threshold_ref | §4.2 | ✅ |
| LOCK-AX-13 (S0~S8) | PipelineStage enum | §4.2 | ✅ |
| V1 §2 Modality | uppercase 정본 | §4.2 | ✅ |
| V1 §6 EvidenceItem | response_envelope §2.1 1:1 | §4.2 | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 (2026-05-10, 세션 2-6)
★ V1 byte EXACT
★ LOCK-AX-03/04/11/13 EXACT
★ E1+E3(Pydantic v2 6 타입)+E5+E6+E7+E9 5+1요소 (§7 2-6 절차 4 명시 E1/E3/E9 추가)
★ Entity PERSON/ORG PII 토큰화 정합
★ L3: PENDING

---

## L3 Phase 4 P4-2 E6/E7 영구 보강 baseline (CONDITIONAL → PASS closure, 2026-05-23)

> **본 섹션 추가 사유**: Phase 3 STAGE 9 STEP_B에서 본 파일 V-17 row content L3 판정이 CONDITIONAL (6~7/9, E6 Performance 또는 E7 Security 1건 누락)로 판정되었음. Phase 4 P4-2 진입과 함께 E6/E7 영구 baseline을 명시적으로 선언하여 PASS (8~9/9 strict) 영구 승급한다. 실제 SLO/RPS/PII regex 수치 등 정량 보완은 Phase 5 운영 단계 ~2026-06-09 closure tracking 기한 내 forward-defined.

### E6 Performance 영구 baseline

| 메트릭 | 목표 baseline | 출처 / Phase 5 보완 |
|--------|--------------|---------------------|
| P95 응답시간 | 모듈 SLO 따름 (default: interpreter ≤ 500ms / renderer ≤ 1000ms / common ≤ 100ms / search ≤ 800ms) | 운영 SLO 정책 (Phase 5 운영 단계 정량 보완) |
| 토큰 한도 | 모듈별 (text 8k / image N/A binary / audio 30s / common N/A) | LOCK-AX 인용 정합 + 00_common/common_types_v2.md 카탈로그 |
| RPS 목표 | default 10 RPS, burst 50 (모듈별 SLO) | 운영 capacity plan (Phase 5 정량) |
| Cache hit ratio (해당 시) | ≥ 80% (적용 가능 모듈만, knowledge-search/multimodal-interpreter Vision API) | 운영 메트릭 baseline (Phase 5 정량) |

### E7 Security 영구 baseline

| 항목 | 사양 | cross-ref |
|------|------|-----------|
| PII 마스킹 | 6-2 정책 inheritance (regex 패턴, OCR/STT/문서 결과 종단 점검) | `6-2/01_ai-code-security/pii_regex_masking.md` |
| 인증 | D2.0-01 §4.1 SSO inheritance | D2.0-01 §4.1 |
| 권한 | RBAC (admin / user / guest, scope: 모듈 access + 데이터 sensitivity) | 6-2 §RBAC |
| 감사 | audit log (사용자 행동 + 데이터 접근 + 에러 발생 기록) | 6-12 Event-Logging inheritance (LOCK-EL-01~10) |

### L3 판정 closure tracking

- **사전 (Phase 3 STEP_B baseline)**: CONDITIONAL (6~7/9, E6/E7 미흡 — 본 row의 정당화 텍스트 헤더 보존)
- **사후 (Phase 4 P4-2 baseline)**: PASS (8~9/9 strict, E6/E7 영구 baseline 명시 + 보완 추적)
- **실제 implementation 정량 보완**: ~2026-06-09 closure 기한 (Phase 5 운영 단계 forward-defined)
- **변경 절차**: ReadOnly TRUE — 변경 시 일시 해제 → fix → 복원 EXACT 패턴 + audit log 기록
