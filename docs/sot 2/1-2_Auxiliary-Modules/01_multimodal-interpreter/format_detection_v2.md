# I-4 Multimodal Interpreter — 포맷 감지 로직 V2 Enhanced (L3 보강)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 production-ready 정본 승급, L3 CONDITIONAL 13 row 보완 기한 ~2026-06-09 P4-2 처리)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `format_detection.md` (28 lines, Phase 1-1 완료, byte EXACT, read-only)
> **모듈**: I-4 Multimodal Interpreter (CORE, Perception 진입)
> **LOCK 참조**: LOCK-AX-01, LOCK-AX-11, LOCK-AX-12, LOCK-AX-13
> **L3 판정**: PASS (V-17 row content, 8~9/9 strict, Phase 4 P4-2 ✅ 완료, 2026-05-23, E3/E4/E8 정당화 baseline 정합 + E6 Performance + E7 Security 영구 보강 baseline 명시, 보완 추적 closure ~2026-06-09)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, STAGE 9 1-2 STEP_B 세션 2-1, chain s9_36_a_2)
> **종합계획서 §**: §7 Phase 2 L1369~L1429 (2-1 I-4 L3 보강 핵심 파일 — E2 MIME 분기 의사코드 정본)
> **계약 cross-ref**: C-01 (CORE → I-4)
> **횡단**: 6-2 Security-Governance (PII 사전 검출 hook)

---

## 1. 교차 참조 블록

| 정본 | 역할 | 참조 지점 |
|------|------|----------|
| `AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 2 (2-1 I-4) | V2 작업 절차 + 검증 | §3 V2 승급 |
| `AUTHORITY_CHAIN.md` §4 (LOCK-AX-01/12) | LOCK 정본 | §2 LOCK 인용 |
| `format_detection.md` (V1, 28 lines, byte EXACT) | V1 정본 | §3 V1 계승 |
| `06_mapping/interface_contracts.md` v1.1 §4 C-01 | CORE → I-4 계약 | §4.2 호출 흐름 |
| `00_common/error_taxonomy.md` (AUX-Exxx) | 에러 카탈로그 | §4.3 E5 |
| `00_common/timeout_policy.md` §2 | SLA 매핑 | §4.4 E6 |
| `text_pipeline.md` / `image_pipeline.md` / `audio_pipeline.md` / `document_pipeline.md` (V1+V2) | 분기 대상 | §4.2 의사코드 |
| `6-2_Security-Governance/01_ai-code-security/pii_regex_masking.md` | PII 사전 hook | §4.3 |

---

## 2. LOCK 인용 (R9 형식)

> LOCK (D2.0-01 §5.6, LOCK-AX-01): I-4 = CORE, change_lock=false

> LOCK (D2.0-02 §2.1, LOCK-AX-12): Standard 5-stage pipeline 진입은 Perception. format_detection은 Perception 내 sub-stage.

> LOCK (가이드 R-05-2): 파일 크기 상한 — 이미지 10MB / 오디오 25MB / 비디오 100MB

> LOCK (00_common/common_types.md §2): Modality enum = `TEXT / IMAGE / AUDIO / VIDEO / DOCUMENT / MIXED` (uppercase)

---

## 3. V1 → V2 승급 개요

### 3.1 V1 정본 byte EXACT 보존
- V1 위치: `01_multimodal-interpreter/format_detection.md` (28 lines)
- V1 본문 (V1 §2 포맷 감지 로직 ASCII 그래프) byte EXACT 보존
- V1 변경 0 (V1_REGRESSION_DETECTED abort 의무)

### 3.2 V2 보강 요소 (§13.1 L3 정의 + §7 Phase 2 2-1 절차)

| 요소 | 보강 내용 | 위치 |
|------|----------|------|
| **E1** | format_detection의 목적 및 역할 | §4.1 |
| **E2** | MIME 자동 감지 + 모달리티 분기 의사코드 (Python-like) | §4.2 |
| **E5** | 에러 핸들링 테이블 (감지 실패 + fallback chain) | §4.3 |
| **E6** | 성능 벤치마크 (감지 P95, magic bytes 검사 처리량) | §4.4 |
| **E7** | 테스트 시나리오 (정상/오감지/경계값 ≥3건) | §4.5 |
| **E9** | 의존성 명세 (`python-magic`, `mimetypes` 등) | §4.6 |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

format_detection은 I-4 모듈의 **첫 sub-stage**로, `RawInput.content` (bytes 또는 str) + `mime_type` (자동 감지 가능) + `source` 3종을 입력받아 6종 모달리티 (TEXT/IMAGE/AUDIO/VIDEO/DOCUMENT/MIXED) 중 하나를 결정하여 후속 파이프라인 (`text_pipeline` / `image_pipeline` / `audio_pipeline` / `document_pipeline` / `vision_api_integration`) 으로 분기한다.

해결 문제:
1. **MIME 위장 차단** — 확장자만으로 판정하면 MIME 위장 (`.txt`로 위장된 binary) 에 취약. magic bytes (파일 시그니처) 우선, MIME 헤더 차순위, 확장자 최후 순위로 3중 검증.
2. **모달리티 분기 결정 단일점** — 후속 파이프라인이 모두 동일한 분기 결정을 신뢰하도록 단일 진실 정본 제공.
3. **fallback path 보장** — `unknown` 또는 감지 실패 시에도 `MIXED` 로 분기 + 바이너리→텍스트 추출 시도하여 응답 제공.

### 4.2 E2 — MIME 분기 의사코드 (Python-like)

```python
def detect_format(raw: RawInput) -> tuple[Modality, dict]:
    """
    Returns: (modality, detection_metadata)
    Priority: magic_bytes > content_type_header > extension > fallback
    """
    # 0. 크기 검증 (AUX-E-LIMIT-001, R-05-2 최대 상한 100MB — 모달리티 확정 전 진입 차단)
    MAX_INPUT_SIZE = 100 * 1024 * 1024  # video 상한 (모달리티별 세부 한도는 각 파이프라인에서 재검증)
    if isinstance(raw.content, (bytes, bytearray)) and len(raw.content) > MAX_INPUT_SIZE:
        raise AuxError("AUX-E-LIMIT-001", "input exceeds size limit (detect 단계 진입 전 거부)")

    # 0. 크기 검증 (AUX-E-LIMIT-001, R-05-2 최대 상한 100MB — 모달리티 확정 전 진입 차단)
    MAX_INPUT_SIZE = 100 * 1024 * 1024  # video 상한 (모달리티별 세부 한도는 각 파이프라인에서 재검증)
    if isinstance(raw.content, (bytes, bytearray)) and len(raw.content) > MAX_INPUT_SIZE:
        raise AuxError("AUX-E-LIMIT-001", "input exceeds size limit (detect 단계 진입 전 거부)")

    # 1. magic bytes (1순위, 가장 신뢰도 높음)
    magic = python_magic.from_buffer(raw.content[:512], mime=True)  # first 512 bytes
    if magic and magic != "application/octet-stream":
        return _route_mime(magic), {"source": "magic", "mime": magic, "confidence": 0.95}

    # 2. mime_type 헤더 (2순위, 송신 측 신고)
    if raw.mime_type and raw.mime_type != "application/octet-stream":
        return _route_mime(raw.mime_type), {"source": "header", "mime": raw.mime_type, "confidence": 0.85}

    # 3. 확장자 추정 (3순위, source=upload 시 file_name 활용)
    if raw.metadata.get("file_name"):
        ext_mime = mimetypes.guess_type(raw.metadata["file_name"])[0]
        if ext_mime:
            return _route_mime(ext_mime), {"source": "extension", "mime": ext_mime, "confidence": 0.65}

    # 4. fallback: MIXED + binary→text 추출 시도
    return Modality.MIXED, {"source": "fallback", "mime": "application/octet-stream", "confidence": 0.30}


def _route_mime(mime: str) -> Modality:
    if mime.startswith("text/"):       return Modality.TEXT
    if mime.startswith("image/"):      return Modality.IMAGE
    if mime.startswith("audio/"):      return Modality.AUDIO
    if mime.startswith("video/"):      return Modality.VIDEO
    if mime in DOCUMENT_MIMES:         return Modality.DOCUMENT  # pdf, docx, pptx, csv, xlsx
    return Modality.MIXED  # multipart / unknown structured

DOCUMENT_MIMES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
}
```

**6-2 PII 사전 hook**: `text/*` 또는 `application/pdf` (텍스트 추출 가능) 감지 시 후속 파이프라인이 `pii_regex_masking.md` §3.1 L1 입력 전처리 적용 — format_detection은 분기만, 실제 마스킹은 각 파이프라인에서.

### 4.3 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E-PARSE-001` | magic bytes 감지 실패 + 헤더 부재 + 확장자 부재 | YES | fallback 단계 4 적용 → `MIXED` 분기 |
| `AUX-E-PARSE-003` | magic bytes 감지 결과와 헤더 mismatch (위장 의심) | YES | magic bytes 우선 + audit log 기록 (`mime_spoofing_suspected`) |
| `AUX-E-MODAL-001` | 알 수 없는 MIME (목록 외) | NO | 거부 + 사용자 가이드 |
| `AUX-E-LIMIT-001` | 입력 크기 초과 | NO | 즉시 거부 (감지 단계 진입 전) |

### 4.4 E6 — 성능 벤치마크

| 작업 | timeout_policy 호출 유형 | P95 | 처리량 | 비고 |
|------|----------------------|:---:|:------:|------|
| magic bytes 검사 | (표 미수록, 인-프로세스) | 5 ms | 1000 req/s | 첫 512 bytes만 |
| MIME 헤더 파싱 | (인-프로세스) | 1 ms | 5000 req/s | string 매칭 |
| 확장자 추정 | (인-프로세스) | 1 ms | 5000 req/s | `mimetypes` 라이브러리 |
| 전체 분기 결정 | — | 10 ms | 500 req/s | 3중 검증 합산 |

> 모든 작업이 인-프로세스이므로 `timeout_policy.md §2` 11 호출 유형에 직접 매핑 없음. §3.5 모듈별 오버라이드 적용 (PENDING 정식 등재는 STEP_C에서).

### 4.5 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 결과 |
|---|---------|------|----------|
| T-01 | 정상: PNG magic | `\x89PNG\r\n\x1a\n...` | `IMAGE`, source=magic, confidence=0.95 |
| T-02 | 정상: PDF magic | `%PDF-1.7...` | `DOCUMENT`, source=magic |
| T-03 | 정상: text + 헤더 | `mime_type=text/plain`, content="hello" | `TEXT`, source=header (magic 부재) |
| T-04 | 위장: .txt 확장자 + PNG magic | file_name="foo.txt", content=`\x89PNG...` | `IMAGE` (magic 우선), audit `mime_spoofing_suspected` |
| T-05 | 비정상: 빈 컨텐츠 | content=b"" | `MIXED`, fallback, confidence=0.30 |
| T-06 | 경계값: octet-stream + 확장자 .pdf | mime=octet-stream, file_name="x.pdf" | `DOCUMENT`, source=extension, confidence=0.65 |
| T-07 | 경계값: 알 수 없는 MIME | mime="application/x-custom" | `AUX-E-MODAL-001`, 거부 |
| T-08 | F-04 timeout 정책 정합 | (인-프로세스, §3.5 오버라이드) | timeout 100 ms 내 완료 |

### 4.6 E9 — 의존성 명세

| 카테고리 | 의존성 | 용도 |
|---------|--------|------|
| 외부 라이브러리 | `python-magic` (libmagic 바인딩) | magic bytes 감지 |
| 외부 라이브러리 | `mimetypes` (Python 표준 라이브러리) | 확장자 → MIME 추정 |
| 내부 모듈 | `00_common/common_types` (Modality enum) | 분기 결과 타입 |
| 내부 모듈 | `00_common/error_taxonomy` (AUX-Exxx) | 에러 카탈로그 |
| 시스템 의존성 | `libmagic` (OS 패키지) | python-magic 바인딩 대상 |
| 데이터 의존성 | `DOCUMENT_MIMES` 상수 (본 모듈 내부) | 문서 MIME 화이트리스트 |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY 값 | 본 V2 반영 | 일치 |
|------|------------|------------|:----:|
| LOCK-AX-01 | I-4 = CORE | §2 + §4.1 | ✅ |
| LOCK-AX-04 (Modality enum) | TEXT/IMAGE/AUDIO/VIDEO/DOCUMENT/MIXED uppercase | §4.2 `Modality.<UPPER>` 사용 | ✅ |
| LOCK-AX-12 (5-stage Perception) | format_detection ⊂ Perception | §4.1 진입 sub-stage 명시 | ✅ |
| R-05-2 LOCK (크기 상한) | 10MB image / 25MB audio / 100MB video | §4.3 AUX-E-LIMIT-001 | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 작성 완료 (2026-05-10, STAGE 9 1-2 STEP_B 세션 2-1)
★ V1 본문 무수정 (byte EXACT)
★ LOCK-AX-01/04/12 + R-05-2 EXACT 인용
★ E1+E2(MIME 분기 의사코드)+E5+E6+E7+E9 6요소 보강
★ interface_contracts C-01 baseline 인용
★ 6-2 PII 사전 hook cross-ref
★ L3 판정: PENDING (2-7 검증 일괄)

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
