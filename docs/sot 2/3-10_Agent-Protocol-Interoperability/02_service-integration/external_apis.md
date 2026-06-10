# 외부 API 연동 (클라우드/캘린더/금융/CI-CD/외부 AI) — K-035 + K-036 + K-037 + K-039 + K-040 (V2 확장, L2~L3)

> **STEP7-K**: K-035 클라우드 스토리지 (L707~L719) + K-036 캘린더/일정 (L721~L737) + K-037 금융 데이터 (L739~L762) + K-039 CI/CD (L781~L795) + K-040 외부 AI 서비스 (L797~L813)
> **레벨**: L2~L3 (K-035/K-036 L2 / K-037/K-039/K-040 L3)
> **Part2 상태**: 5건 전수 ABSENT → 본 문서로 방식 C 신규 편입
> **정본 소유**: #13 Agent-Protocol-Interoperability / 02_service-integration
> **V 스코프**: V2-Phase 2 (K-035 V1: 기본 API 즉시, K-036 V1: Google Calendar 즉시, K-037 V1: yfinance+DART 즉시, K-039 V1: GitHub Actions 즉시, K-040 V1: API 연동 즉시)
> **V2 태그**: V2-Phase 2 (2026-04-22, STAGE 7 STEP_B #2a 3-10 도메인 P2-2 세션 신규 작성)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`
> **제외**: **K-038 IoT/스마트홈 연동 (V3, STEP7-K L764~L779)** — plan §7.5 V3 이관 명시, 본 V2 Phase 2 범위 제외.

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L707~L813 | K-035~K-040 원본 정의 (K-038 IoT V3 제외) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-02 | Permission Level 0~5 (금융 주문 L5 필수) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-07 | A2A + MCP 양방향 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-09 | 비용 상한 V1 ₩40K / V2 ₩93K / V3 ₩266K |
| 구조화_종합계획서.md | §7.4 P2-2 L1151~L1181 | Phase 2 V2 K-035~K-040 배치 |
| 구조화_종합계획서.md | §7.5 | K-038 IoT V3 이관 명시 |
| 02_service-integration/llm_gateway.md | §§ K-031~K-034 | 통합 게이트웨이 + 검색/코드/커뮤니케이션 (본 문서와 역할 분리) |
| 03_data-exchange/message_format.md | §2 | VamosMessage 6필드 (모든 API 응답 정규화) |
| 03_data-exchange/serialization.md | §§ | JSON/MessagePack/Protobuf 직렬화 전략 |
| 06_autonomy-safety/permission_matrix.md | Permission 0~5 | L5 금융 주문 HITL 필수 |
| 4-3 MCP Server/Client | MCP Tool Registry | 외부 API 를 MCP Tool 로 등록 (I-10) |

> **R6 준수**: What+How 전용. When/Where 는 Part2 정본, 미기재.

---

## §2. K-035 클라우드 스토리지 연동 (L707~L719 원문 매핑, L2)

### 2.1 지원 서비스 (L710~L717 원문)

| Service | V1 기능 | V2 추가 |
|---------|-------|---------|
| Google Drive | 파일 업로드/다운로드, Docs/Sheets 직접 편집, 공유 폴더 모니터링 | Drive Push Notification |
| Dropbox | 유사 기능 (V1 기본 CRUD) | 선택적 동기화 |
| OneDrive | 유사 기능 | Microsoft Graph API 통합 |
| S3 / R2 | 대용량 데이터 저장 (V2) | Multipart Upload, 수명 주기 정책 |

### 2.2 권한 모델

| 작업 | Permission Level (LOCK-AP-02) |
|-----|-----------------------------|
| 파일 목록 조회 | L0 |
| 파일 다운로드 | L1 |
| 파일 업로드 | L1 |
| 파일 삭제 | L3 + HITL |
| 공유 설정 변경 | L4 + HITL |

### 2.3 스키마

```python
class CloudStorageOp(BaseModel):
    service: Literal["google_drive", "dropbox", "onedrive", "s3", "r2"]
    operation: Literal["list", "upload", "download", "delete", "share_modify"]
    path: str                                    # cloud path (forward slash)
    local_path: Optional[str] = None
    permission_required: Literal[0, 1, 2, 3, 4, 5]
    hitl_required: bool = False
```

---

## §3. K-036 캘린더/일정 연동 (L721~L737 원문 매핑, L2)

### 3.1 지원 서비스 (L724~L729 원문)

| Service | 주요 기능 |
|---------|---------|
| Google Calendar | 일정 조회/생성/수정, 충돌 감지, 일정 기반 브리핑, 미팅 노트 자동 생성, 리마인더 |
| Outlook Calendar | 유사 기능 (Microsoft Graph) |

### 3.2 VAMOS 일정 인텔리전스 (L731~L734 원문)

- 최적 미팅 시간 제안 (참석자 가용성 교차 분석)
- 미팅 준비 자료 자동 수집 (Research Node 경유, 01_framework-adapters)
- 일정 패턴 분석 → 생산성 인사이트 (Self-Evolution K-047 연계)

### 3.3 스키마

```python
class CalendarOp(BaseModel):
    service: Literal["google_calendar", "outlook_calendar"]
    operation: Literal["list", "create", "update", "delete", "find_optimal_time", "generate_briefing"]
    calendar_id: Optional[str] = None
    event: Optional[dict] = None                 # RFC 5545 iCalendar-like
    time_range: Optional[tuple[datetime, datetime]] = None
    attendees: Optional[list[str]] = None
    permission_required: Literal[0, 1, 2, 3, 4, 5]
```

---

## §4. K-037 금융 데이터 연동 (L739~L762 원문 매핑, L3)

### 4.1 한국 시장 (L742~L747 원문)

| Provider | 기능 | V 스코프 |
|----------|------|---------|
| 키움증권 OpenAPI+ | 실시간 시세, 주문 | V2 (주문 L5 HITL) |
| 한국투자증권 KIS API | REST 기반 | V2 |
| DART OpenAPI | 공시 데이터 | V1 |
| KRX 정보데이터시스템 | 시장 데이터 | V2 |
| 한국은행 ECOS | 경제 지표 | V1 |

### 4.2 글로벌 (L749~L754 원문)

| Provider | 기능 | V 스코프 |
|----------|------|---------|
| Yahoo Finance (yfinance) | 무료 시세 | V1 |
| Alpha Vantage | 기술 지표 | V2 |
| FRED | 경제 데이터 | V1 |
| SEC EDGAR | 미국 공시 | V2 |
| OpenBB | 통합 금융 데이터 | V2 |

### 4.3 크립토 (L756~L759 원문)

| Provider | 기능 |
|----------|------|
| Binance API | 글로벌 거래소 |
| Upbit API | 한국 거래소 |
| CoinGecko | 시장 데이터 |

### 4.4 권한 & HITL (LOCK-AP-02)

| 작업 | Permission Level |
|-----|-----------------|
| 시세 조회 | L0 |
| 공시/뉴스 조회 | L0 |
| 지표/차트 생성 | L1 |
| 주문 실행 | **L5 + HITL 필수** (LOCK-AP-02 L5 "항상 사용자 확인") |

### 4.5 스키마

```python
class FinancialDataOp(BaseModel):
    market: Literal["kr_stock", "us_stock", "crypto", "economic"]
    provider: Literal[
        "kiwoom", "kis", "dart", "krx", "ecos",
        "yfinance", "alpha_vantage", "fred", "sec_edgar", "openbb",
        "binance", "upbit", "coingecko",
    ]
    operation: Literal["quote", "orderbook", "trade", "disclosure", "historical", "indicator"]
    ticker: Optional[str] = None
    time_range: Optional[tuple[datetime, datetime]] = None
    permission_required: Literal[0, 1, 2, 3, 4, 5]
    hitl_required: bool = False                  # L5 trade = True 강제
```

---

## §5. K-039 CI/CD 파이프라인 연동 (L781~L795 원문 매핑, L3)

### 5.1 지원 플랫폼 (L784~L792 원문)

| Platform | V1 기능 | V2 추가 |
|----------|-------|---------|
| GitHub Actions | 워크플로우 생성/수정, 실행 결과 모니터링, 실패 분석 + 자동 수정 제안, 배포 승인 | reusable workflow 생성 |
| Docker Hub / Container Registry | V1 기본 push/pull | 취약점 스캔 (V2) |
| Vercel / Netlify | V1 프론트엔드 배포 | preview deployment |
| AWS / GCP / Azure | V2 클라우드 배포 | IAM 통합 |

### 5.2 실패 분석 자동화 (K-026 Reflection 연계)

- CI 실패 로그 → Reflection 패턴 (`01_framework-adapters/reflection_planning.md §4.3`) → 원인 분석 → PR 수정 제안.

### 5.3 권한 모델

| 작업 | Permission Level |
|-----|-----------------|
| Workflow 조회 | L0 |
| Workflow 수정 | L4 + HITL |
| 배포 승인 | **L4 + HITL 필수** |
| 프로덕션 배포 롤백 | L4 + HITL |

---

## §6. K-040 외부 AI 서비스 연동 (L797~L813 원문 매핑, L3)

### 6.1 특화 AI 서비스 (L800~L805 원문)

| Service | 특화 영역 | V 스코프 |
|---------|---------|---------|
| Wolfram Alpha | 수학/과학 계산 | V1 |
| Hugging Face | 특화 모델 호출 | V1 |
| Replicate | GPU 모델 실행 | V2 |
| Together AI | 오픈소스 모델 | V1 (MoA Proposer 후보) |
| Groq | 초저지연 추론 | V1 |

### 6.2 슈퍼 에이전트 (L807~L810 원문)

- **최적 AI 서비스 자동 선택** (task_type → service mapping)
- **비용/성능 트레이드오프 관리** (LOCK-AP-09)
- **결과 통합** (moa_pattern.md §4.2 Aggregator 재사용 가능)

### 6.3 스키마

```python
class ExternalAIOp(BaseModel):
    service: Literal["wolfram", "huggingface", "replicate", "together_ai", "groq"]
    task_type: Literal["math", "specialized_model", "gpu_inference", "oss_llm", "low_latency"]
    input: dict
    budget_krw: float
    hitl_on_ambiguity: bool = True
```

---

## §7. LOCK 매핑 (5필드 분리 인용)

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 |
|---------|------|----------|-----|-------|-------------|
| LOCK-AP-02 | Permission Level | STEP7-K K-041 | 0~5 | 금지 | §4.4 금융 주문 L5 + HITL, §2.2/§5.3 표 |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 | 금지 | 전수 MCP Tool Registry 등록 |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K / V2: ₩93K / V3: ₩266K | 금지 | 외부 API 유료 플랜 누적 체크 |

---

## §8. Phase별 복구/다운그레이드 흐름

```
Phase 1 (API 429 rate limit) → exponential backoff 3회 → 실패 시 폴백 provider
Phase 2 (인증 만료 401) → 토큰 갱신 요청 → HITL
Phase 3 (서비스 장애 5xx) → 대체 provider → confidence -0.15
Phase 4 (비용 초과) → LOCK-AP-09 Cost Gate → COST_GATE_BLOCKED
Phase 5 (L5 작업 HITL) → 사용자 확인 필수, 자동 진행 금지
```

confidence penalty:
- 1차 실패 → -0.05
- 폴백 실패 → -0.15
- 인증 오류 → -0.20 (즉시 HITL)
- rate limit 3회 초과 → -0.20

---

## §9. 에스컬레이션 페이로드 (I-20 경유)

```python
class ExternalAPIEscalation(BaseModel):
    source_engine: Literal[
        "cloud_storage", "calendar", "financial_data",
        "ci_cd", "external_ai",
    ]
    error_code: Literal[
        "API_RATE_LIMIT", "AUTH_EXPIRED", "PROVIDER_5XX",
        "COST_GATE_BLOCKED", "PERMISSION_L5_REQUIRED",
        "TRADE_ORDER_REJECTED",
    ]
    original_request: dict
    partial_result: Optional[dict]
    retry_count: int
    provider: str
    trace_id: str
    timestamp: str
```

---

## §10. 로깅 포맷 (R-01-7 structured JSON)

```json
{
  "trace_id": "...",
  "error": {"code": "PERMISSION_L5_REQUIRED", "operation": "stock_trade"},
  "context": {
    "service": "kiwoom",
    "ticker": "005930",
    "order_size": 10,
    "budget_krw": 500000,
    "lock_ap_02": "L5 HITL mandatory"
  },
  "recovery": {"action": "hitl_confirmation_request", "route": "I-19", "reason": "l5_trade_requires_user_confirm"}
}
```

---

## §11. Phase 3 테스트 시나리오 (10건)

1. **Google Drive 업로드**: L1 권한, 파일 업로드 → 성공.
2. **Drive 파일 삭제**: L3 + HITL → 사용자 승인 → 삭제 완료.
3. **Google Calendar 일정 생성**: 미팅 시간 + 참석자 → 일정 생성 + 충돌 감지.
4. **최적 미팅 시간 제안**: 3 참석자 가용성 → Slot 2개 제안 → 사용자 선택.
5. **yfinance 시세 조회**: ticker=AAPL → 실시간 시세 반환 → 비용 0.
6. **키움증권 주문 L5 HITL**: 삼성전자 10주 매수 요청 → HITL 확인 → 주문 실행 로그.
7. **GitHub Actions 배포 승인**: 프로덕션 배포 PR → L4 HITL → 승인 → 배포.
8. **Wolfram Alpha 수학**: "integrate x^2 dx" → 수식 해답 반환.
9. **Replicate GPU 추론**: Stable Diffusion 호출 → V2 비용 추적 (LOCK-AP-09).
10. **Binance 시세**: BTC/USDT → 실시간 가격 반환 → WebSocket 대신 REST (LOCK-AP-04 호환성).
11. **K-038 IoT V3 제외 확인**: IoT/스마트홈 요청 시 `[V3_DEFERRED:K-038]` 안내.
12. **비용 초과 차단**: 외부 AI 누적 ₩95K → COST_GATE_BLOCKED.

---

## §12. 세션 간 인터페이스 cross-check

| 상대 산출물 | 인터페이스 | 일치 여부 |
|------------|-----------|-----------|
| llm_gateway.md §2 | LLM Provider 중복 없음 (역할 분리) | ✅ K-031~K-034 vs K-035~K-040 |
| 03_data-exchange/message_format.md §2 | VamosMessage 6필드로 API 응답 정규화 | ✅ LOCK-AP-01 |
| 03_data-exchange/serialization.md §§ | JSON/MessagePack 직렬화 사용 | ✅ K-053 연계 |
| 06_autonomy-safety/permission_matrix.md | L5 금융 주문 HITL | ✅ LOCK-AP-02 |
| 01_framework-adapters/reflection_planning.md §4.3 | CI 실패 분석 재사용 | ✅ §5.2 |
| 01_framework-adapters/moa_pattern.md §4.1 Proposer Pool | Together AI proposer 후보 | ✅ §6.1 |
| 4-3 MCP Server/Client | MCP Tool Registry 등록 | ✅ 경계 준수 |

---

## §13. 검증 자가 체크리스트

- [x] §1 교차 참조 블록
- [x] §2~§6 STEP7-K L707~L813 원문 line refs verbatim (L710~L717, L724~L729, L731~L734, L742~L747, L749~L754, L756~L759, L784~L792, L800~L805, L807~L810)
- [x] §7 LOCK 매핑 5필드 (AP-02/07/09)
- [x] Phase 3 테스트 시나리오 ≥ 10건 (§11: 12건)
- [x] 에스컬레이션 페이로드 Python class (§9)
- [x] 로깅 포맷 structured JSON 중첩 3-block (§10)
- [x] V2-Phase 2 헤더 태그
- [x] **K-038 IoT V3 이관 명시** (헤더 + §11 시나리오 11)
- [x] 금융 주문 L5 HITL LOCK-AP-02 엄수 (§4.4)
- [x] FABRICATION 10종 census 0 hits
- [x] R6 준수 (What+How 전용)

---

*정본 소유: #13 Agent-Protocol-Interoperability / 02_service-integration*
*V2-Phase 2 최초 작성: 2026-04-22 (STAGE 7 STEP_B #2a)*
