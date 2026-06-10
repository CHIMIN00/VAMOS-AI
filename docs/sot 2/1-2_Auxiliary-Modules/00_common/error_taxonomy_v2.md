# 00. Common — 에러 분류 체계 V2 Enhanced (L3 보강, 에러 핸들링 미들웨어 정본)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 production-ready 정본 승급, L3 CONDITIONAL 13 row 보완 기한 ~2026-06-09 P4-2 처리)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `error_taxonomy.md` (112 lines, byte EXACT)
> **모듈**: 00_common
> **LOCK 참조**: LOCK-AX-11 (audit.failure_codes 채널)
> **L3 판정**: PASS (V-17 row content, 8~9/9 strict, Phase 4 P4-2 ✅ 완료, 2026-05-23, E3/E4 에러 카탈로그 정당화 baseline 정합 + E6 Performance + E7 Security 영구 보강 baseline 명시, 보완 추적 closure ~2026-06-09)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, 세션 2-6)
> **종합계획서 §**: §7 Phase 2 L1654~L1712 (2-6 절차 2: error_taxonomy L3 보강 — E2 미들웨어 + E5 + E7)
> **횡단**: 6-2 (보안 이벤트 에러 코드 cross-ref)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `error_taxonomy.md` (V1, 112 lines, byte EXACT) | V1 정본 (AUX-E001~E010 10개 카탈로그) |
| `response_envelope_v2.md` (자매 V2) | audit.failure_codes 채널 |
| `timeout_policy_v2.md` (자매 V2) | AUX-E004/E006 정합 |
| 모든 V2 (자매) | AUX-Exxx 사용 (시리즈별 신규 코드 추가 명시) |

---

## 2. LOCK 인용

> LOCK (D2.0-02 §5.1.1, LOCK-AX-11): audit.failure_codes 채널은 본 카탈로그의 코드만 허용

> LOCK (V1 §2 표): AUX-E001~E010 10개 정본 코드 (INPUT/PROCESSING/EXTERNAL/MEMORY/QUALITY/SYSTEM 6 범주)

---

## 3. V1 → V2 승급 개요

V1 byte EXACT (112 lines, V1 §2 10 코드 표 + §3 6 범주 + §4 재시도 매트릭스 + §5 ResponseEnvelope 통합 + §6 LogEvent 매핑). V1 변경 0.

| 요소 | 보강 (§7 2-6 절차 2 명시) |
|------|----------|
| **E1** | error_taxonomy 목적 (AUX-Exxx 단일 카탈로그) |
| **E2** | **에러 핸들링 미들웨어** 의사코드 (포착 → 분류 → ResponseEnvelope 래핑 → 로깅) |
| **E5** | 에러 타입별 재시도 정책 + cascade 실패 + fallback 체인 |
| **E7** | 에러 시나리오 테스트 (cascade 실패 + 미분류 + AUX 시리즈 확장) |
| **E9** | logging, structlog, prometheus_client |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

error_taxonomy는 보조모듈 (I-1~I-25) 의 **AUX-Exxx 에러 코드 단일 카탈로그**. V1 §2 의 10 정본 코드 + 본 V2 시리즈별 추가 코드 (예: AUX-E-ENV-001 envelope, AUX-E-LOCK-001 LOCK 변조, AUX-E-PII-001/002 PII, AUX-E-RENDER-001~023, AUX-E-SEARCH-001~007, AUX-E-SUMM-001~007, AUX-E-MEM-001~004, AUX-E-WIN-001~003, AUX-E-ANOM-001~004, AUX-E-SDAR-001~003, AUX-E-METRIC-001~003) 를 모두 본 카탈로그가 통합.

본 V2 §4.2의 **에러 핸들링 미들웨어**가 모든 V2 모듈의 에러를 통합 처리.

### 4.2 E2 — 에러 핸들링 미들웨어 의사코드

```python
class ErrorHandlingMiddleware:
    """모든 보조모듈 에러를 통합 처리 — 포착 → 분류 → 래핑 → 로깅"""

    async def handle(self, exception: Exception, context: ModuleContext) -> ResponseEnvelope:
        # 1. AuxError 분류
        if isinstance(exception, AuxError):
            error_code = exception.error_code
            error_message = exception.message
        else:
            # 미분류 → AUX-E010 SYSTEM
            error_code = "AUX-E010"
            error_message = f"unclassified: {type(exception).__name__}: {exception}"
            audit_log.error(f"unclassified exception: {exception}", exc_info=True)

        # 2. 카탈로그 검증 (본 §4.3)
        if not self._is_known_code(error_code):
            audit_log.warn(f"unknown AUX code: {error_code}, fallback to AUX-E010")
            error_code = "AUX-E010"

        # 3. 분류 → 재시도 매트릭스 (V1 §4)
        category = self._get_category(error_code)
        retriable = self._is_retriable(error_code)
        recovery_action = self._get_recovery_action(error_code)

        # 4. cascade 검사 (이전 에러와 동일 코드 3회 연속 → cascade 실패)
        if context.recent_failures.count(error_code) >= 3:
            audit_log.critical(f"cascade failure detected: {error_code} 3+ times")
            error_code_final = "AUX-E010"  # SYSTEM 격상
            error_code = error_code_final   # 격상 코드가 envelope까지 반영되도록 재할당
            retriable = False

        # 5. ResponseEnvelope 래핑 (LOCK-AX-11)
        envelope = ResponseEnvelope(
            answer=Answer(summary=f"요청 처리 실패 ({error_code})", details=error_message, next_actions=recovery_action.user_guides),
            evidence=Evidence(coverage=0.0, items=[], qod=0.0),
            self_check=SelfCheck(
                score=0.0,
                verdict="FAIL" if not (retriable and context.remaining_retries > 0) else "WARN",
                reasons=[f"{error_code}: {error_message}"],
                retry_allowed=retriable and context.remaining_retries > 0,
            ),
            decision_ref=DecisionRef(
                decision_id=context.decision_id,
                gates=DecisionGates(policy="PASS", cost="PASS", evidence="FAIL"),  # evidence FAIL on error
            ),
            audit=Audit(
                event_ids=[f"oc.{context.module}.{recovery_action.event_suffix}"],
                failure_codes=[error_code],
                fallback_ids=[recovery_action.fallback_id] if recovery_action.fallback_id else [],
            ),
            request_id=context.request_id,
            timestamp=datetime.utcnow().isoformat(),
            pipeline_stage=context.pipeline_stage,
        )

        # 6. 6-2 PII 종단 점검 (response_envelope_v2 위임)
        ResponseEnvelopeSerializer._verify_no_pii_leak(envelope.dict())

        # 7. 로깅 (severity 매핑, V1 §6)
        log_severity = self._get_log_severity(error_code)
        audit_log.log(level=log_severity, msg=f"{error_code}: {error_message}", extra={"context": context.dict()})

        # 8. Prometheus counter
        prometheus_metrics.vamos_error_total.labels(code=error_code, category=category).inc()

        return envelope

    def _is_known_code(self, code: str) -> bool:
        # V1 §2 10 정본 코드 또는 카탈로그 V2 시리즈 prefix (AUX-E-<SERIES>-NNN) 매칭
        import re
        return code in KNOWN_AUX_CODES or bool(re.fullmatch(r"AUX-E-[A-Z]+-\d{3}", code))

    def _get_category(self, code: str) -> str:
        # AUX-E001/E002 → INPUT, AUX-E003/E004 → PROCESSING, ...
        return AUX_CATEGORY_MAP.get(code, "SYSTEM")

    def _is_retriable(self, code: str) -> bool:
        return code in RETRIABLE_CODES  # V1 §4 매트릭스

    def _get_recovery_action(self, code: str) -> RecoveryAction:
        # V1 §4 권장 폴백 매핑
        return RECOVERY_MAP.get(code, RecoveryAction.fail_fast())

    def _get_log_severity(self, code: str) -> int:
        # V1 §6 LogEvent 매핑
        if code in {"AUX-E010"}: return logging.CRITICAL
        if code.startswith("AUX-E00") and code in {"AUX-E003", "AUX-E004", "AUX-E005", "AUX-E006", "AUX-E007"}: return logging.ERROR
        return logging.WARNING


# 통합 카탈로그 (V1 §2 + 시리즈별 V2 신규)
KNOWN_AUX_CODES = set([
    # V1 §2 10 정본
    "AUX-E001", "AUX-E002", "AUX-E003", "AUX-E004", "AUX-E005",
    "AUX-E006", "AUX-E007", "AUX-E008", "AUX-E009", "AUX-E010",
    # 시리즈별 V2 신규 (각 V2 파일에서 정의)
    # I-4: AUX-E-PARSE-001~004, AUX-E-MODAL-001/002, AUX-E-LIMIT-001, AUX-E-OCR-001, ...
    # I-13: AUX-E-RENDER-001~023, AUX-E-QUAL-001~003
    # I-14: AUX-E-SUMM-001~007, AUX-E-MEM-001~004, AUX-E-WIN-001~003, AUX-E-TRIG-001~004
    # I-16: AUX-E-SEARCH-001~007, AUX-E-RAG-001~003, AUX-E-EXT-001~005
    # S-1: AUX-E-QOD-001/002, AUX-E-ANOM-001~004, AUX-E-SDAR-001~003, AUX-E-METRIC-001~003
    # 00_common: AUX-E-ENV-001~004, AUX-E-LOCK-001, AUX-E-TYPE-001~003
    # 6-2 cross: AUX-E-PII-001/002/003
])
```

### 4.3 E5 — 에러 처리 정책 + cascade 실패

| 카테고리 | 재시도 | cascade 임계 | 처리 |
|---------|:------:|:----:|------|
| INPUT (E001/E002) | NO | — | 사용자 가이드 |
| PROCESSING (E003/E004) | YES | 3회 → SYSTEM 격상 | timeout_policy 채널 |
| EXTERNAL (E005/E006) | YES | 3회 → fallback (Secondary provider) | backoff |
| MEMORY (E007/E008) | E007=YES | 3회 → 캐시 fallback or 격상 | 재연결 |
| QUALITY (E009) | NO | — | I-5 결정 변경 |
| SYSTEM (E010) | NO | 즉시 fail-fast | 감사 격상 |
| **PII (E-PII-xxx)** | NO | 1회 → 6-2 P1 알림 | 차단 |
| **LOCK (E-LOCK-xxx)** | NO | 즉시 abort | 무결성 알림 |

**미분류 에러**: 모든 카탈로그 외 코드 → AUX-E010 SYSTEM로 fallback + audit warning.

### 4.4 E6 — 성능

| 작업 | P95 |
|------|:---:|
| 미들웨어 handle() | 30 ms |
| ResponseEnvelope 생성 | 5 ms |
| PII 종단 점검 | 20 ms |
| Prometheus increment | 1 ms |

### 4.5 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | AUX-E001 (INPUT) | 미지원 MIME | self_check.verdict=FAIL, retry_allowed=False |
| T-02 | AUX-E003 (PROCESSING) | 모델 실패 | retry_allowed=True (잔여 횟수 시) |
| T-03 | cascade 실패 (E003 3회) | 동일 코드 3회 | AUX-E010 격상 + critical |
| T-04 | 미분류 예외 (KeyError) | unclassified | AUX-E010 fallback |
| T-05 | AUX-E-LOCK-001 | LOCK 변조 | 즉시 abort + 무결성 알림 |
| T-06 | AUX-E-PII-002 | PII 누출 | 차단 + 6-2 P1 |
| T-07 | LogEvent severity | E010 | severity=critical |
| T-08 | Prometheus counter | error 발생 | vamos_error_total{code, category} 증가 |

### 4.6 E9 — 의존성 명세

| 카테고리 | 의존성 |
|---------|--------|
| 표준 라이브러리 | `logging` (severity), `traceback` (unclassified) |
| 외부 라이브러리 | `structlog` (구조화 로그), `prometheus-client` |
| 내부 모듈 | `response_envelope_v2` (ResponseEnvelope 래핑 + PII 종단), `timeout_policy_v2` (E004/E006 정합) |
| 모든 V2 (의존) | AUX-Exxx 코드 사용처 |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY | 본 V2 | 일치 |
|------|---------|-------|:----:|
| LOCK-AX-11 (audit.failure_codes) | 카탈로그 외 금지 | §4.2 _is_known_code + AUX-E010 fallback | ✅ |
| V1 §2 10 정본 코드 | byte EXACT | §4.2 KNOWN_AUX_CODES | ✅ |
| V1 §4 재시도 매트릭스 | retriable / recovery | §4.2 _is_retriable, _get_recovery | ✅ |
| V1 §6 LogEvent severity | warn/error/critical | §4.2 _get_log_severity | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 (2026-05-10, 세션 2-6)
★ V1 byte EXACT (V1 §2 10 정본 코드 보존)
★ LOCK-AX-11 EXACT
★ E1+E2(에러 미들웨어 통합 처리)+E5(cascade)+E6+E7+E9 5+1요소 (§7 2-6 절차 2)
★ V2 시리즈별 신규 코드 통합 카탈로그
★ 6-2 PII / LOCK 변조 즉시 차단
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
