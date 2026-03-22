---
session: 07
sections: [7.9, 7.10, 7.11, 7.12, 7.13, 7.14, 7.15, 7.16, 7.17]
status: complete
---

# §7. I-Series Part 2: I-9 ~ I-17 — ORANGE CORE 확장 모듈 상세

> **비유**: Part 1(I-1~I-8)이 두뇌의 **핵심 사고 영역**(이해, 기억, 판단)이었다면, Part 2(I-9~I-17)는 두뇌의 **관리·운영 영역**입니다. 가정에 비유하면, I-1~I-8이 "무엇을 할지 결정하는 가장"이라면, I-9~I-17은 "가계부를 쓰고(I-9), 도구를 정리하고(I-10), 보고서를 작성하고(I-11), 작업 순서를 짜고(I-12), 결과물을 예쁘게 꾸미고(I-13), 핵심만 요약하고(I-14), 자료 품질을 검사하고(I-15), 필요한 정보를 찾아오고(I-16), 실행팀을 관리하는(I-17) 살림꾼들"입니다.

[근거: D2.0-02 §0.1, §4.0, CLAUDE.md §6]

---

## §7.9 I-9 비용 관리자 (Cost Manager) 🔒

### 비유
가정의 **가계부 관리자**와 같습니다. 매달 정해진 생활비(예산) 안에서 돈을 쓰도록 관리하고, 예산의 80%를 넘기면 경고하고, 100%를 넘기면 카드를 차단합니다.

### 목적
VAMOS가 AI 모델(LLM)을 호출할 때마다 발생하는 **토큰 비용, API 호출 비용, 서버 시간** 등을 실시간으로 추적합니다. 각 버전(V1/V2/V3)에 정해진 **월간 비용 상한**을 초과하지 않도록 감시하며, 예산이 부족해지면 자동으로 **저비용 모델로 전환(Downshift)**하거나 작업을 **중단(Stop)**합니다. [근거: D2.0-02 §7.57, CLAUDE.md §7.3]

### ⚠️ ABSOLUTE LOCK — 비용 상한 (변경 불가)

> **이 값들은 ABSOLUTE LOCK으로 지정되어 있어 어떤 상황에서도 변경할 수 없습니다.**

| 버전 | 월간 상한 | 일간 상한 | 모델 전략 |
|------|----------|----------|----------|
| **V1** (MVP) | **₩40,000/월** ($30) | ₩1,300/일 ($1) | Mini 모델 90% 이상 사용 |
| **V2** (Pro) | **₩93,000/월** ($70) | ₩3,100/일 ($2.3) | Mini 60-70% / Main 30-40% |
| **V3** (Enterprise) | **₩266,000/월** ($200) | ₩8,900/일 ($6.7) | Main 중심, Flagship 적극 활용 |

[근거: CLAUDE.md §7.3 비용/안전 LOCK (ABSOLUTE)]

### 구조도

```
사용자 요청 → I-5 Decision 생성
                ↓
┌──────────────────────────────────────┐
│         I-9 Cost Manager             │
│  ┌────────────────────────────────┐  │
│  │ 1. estimate_cost()             │  │  → "이 작업에 약 ₩150 들겠네"
│  │ 2. track_actual_cost()         │  │  → "현재 이번 달 ₩32,000 사용 중"
│  │ 3. recommend_downshift()       │  │  → 80% 초과 시 "Mini로 바꿔!"
│  └────────────────────────────────┘  │
│                                      │
│  [Downshift 메커니즘]                │
│  ┌────────────────────────────────┐  │
│  │ 0~79%  → normal (정상 운영)    │  │
│  │ 80~99% → warn + force_mini    │  │  ← 경고 + 저비용 모델 강제
│  │ 100%   → block (완전 차단)     │  │  ← 월간 상한 도달, 작업 중단
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `intent_frame` | 필수 | I-1에서 생성한 의도 프레임 (예상 토큰 수 추정용) |
| `plan` | 필수 | 실행 계획 (어떤 모델/도구를 몇 번 호출할지) |
| `trace_id` | 필수 | 추적 ID (비용을 어떤 요청에 귀속시킬지) |
| `usage` | 실행 후 | 실제 사용량 데이터 (토큰 수, API 호출 횟수 등) |

[근거: D2.0-02 §7.58]

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `cost_estimate` | 예상 비용 | `₩150` |
| `cost_status` | 현재 비용 상태 | `{used: ₩32,000, limit: ₩40,000, ratio: 0.80}` |
| `recommendation` | 다운시프트 권고 | `normal` / `downshift` / `split` / `stop` |

[근거: D2.0-02 §7.58]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `NORMAL` | 예산 여유 있음 — 정상 운영 |
| `WARNING` | 80% 초과 — 경고 발생, Mini 모델로 전환 강제 |
| `BLOCKED` | 100% 도달 — 모든 유료 작업 차단 |
| `DOWNSHIFTED` | 저비용 모드로 전환 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i9.cost.estimated` | 비용 예측 완료 시 발생 |
| `oc.i9.cost.threshold_hit` | 예산 임계값(80%/100%) 도달 시 발생 |
| `oc.i9.cache.hit` | 프롬프트 캐시 적중 (비용 절감) |
| `oc.i9.cache.miss` | 프롬프트 캐시 미적중 |
| `oc.i9.cache.evicted` | 캐시 항목 만료/제거 |
| `oc.i9.batch.submitted` | 배치 요청 제출 |
| `oc.i9.batch.completed` | 배치 처리 완료 |

[근거: D2.0-02 §7.59, §7.59-A~C]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I9_COST_TRACK_FAIL` | 비용 추적 실패 | fallback → 보수적 추정 적용 |
| `OC_I9_CACHE_INIT_FAIL` | 프롬프트 캐시 초기화 실패 | 캐시 없이 진행 (성능 저하 허용) |
| `OC_I9_BATCH_TIMEOUT` | 배치 처리 시간 초과 | 실시간 API로 전환 |
| `OC_I9_BATCH_PARTIAL_FAIL` | 배치 일부 실패 | 실패 건만 재시도 |

[근거: D2.0-02 §7.59, §7.59-A~C]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_COST_DOWNSHIFT` | 예산 초과 시 저비용 모델/도구로 자동 전환 (예: GPT-4o → Mini 모델) |

[근거: D2.0-02 §6.3 FB_COST_DOWNSHIFT]

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| CostGate (S2~S4) | 파이프라인 S2(근거 준비)~S4(실행) 구간에서 비용 게이트 적용 |
| Downshift 자동 적용 | 80% 초과 시 Mini 강제 전환은 승인 불필요 (LOCK) |
| 100% 차단 | 상한 도달 시 자동 차단 — 우회 불가 (LOCK) |

[근거: CLAUDE.md §5 Gate 시스템, §7.3]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-5 (Condition & Decision Engine) | Decision 생성 시 비용 예측 결과 반영 |
| I-8 (Policy Engine) | 비용 정책 규칙 적용 |
| I-1 (Intent Detector) | Adaptive Thinking 레벨별 토큰 예산 연동 |
| I-12 (Workflow Builder) | 배치 작업 스케줄링과 통합 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| 모듈 상태 | CORE(LOCK) | CORE(LOCK) | CORE(LOCK) | CORE(LOCK) |

### 🔒 LOCK 여부

- **change_lock = true** (변경 불가)
- 비용 상한 값은 **ABSOLUTE LOCK** — 어떤 상황에서도 변경 불가
- Downshift 메커니즘(80% warn, 100% block)도 LOCK

### 비용 절감 기능 (STEP7 확장)

| 기능 | ID | 절감율 | 버전 |
|------|----|--------|------|
| 프롬프트 캐싱 (Prompt Caching) | S7B-028 | 30~90% | V1 |
| KV Cache 최적화 (PagedAttention) | S7B-029 | 메모리 +58%, 지연 -60% | V2 |
| 배치 처리 모드 | S7B-030 | 50% | V2 |

[근거: D2.0-02 §7.59-A~C]

### 핵심 요약 (3줄)
1. **I-9 Cost Manager**는 VAMOS의 가계부 관리자로, V1 ₩40K/V2 ₩93K/V3 ₩266K 월간 비용 상한을 절대 초과하지 않도록 관리합니다 (ABSOLUTE LOCK).
2. 예산 80% 초과 시 자동으로 저비용 모델로 전환(Downshift)하고, 100% 도달 시 완전 차단합니다.
3. 프롬프트 캐싱, KV Cache 최적화, 배치 처리 등으로 30~90%의 비용 절감이 가능합니다.

---

## §7.10 I-10 도구 등록소 (Tool Registry/Router)

### 비유
회사의 **총무부 겸 자재 관리실**과 같습니다. 어떤 도구(Tool)가 있는지 목록을 관리하고, 특정 작업에 가장 적합한 도구를 찾아서 연결해 주며, 도구 사용 권한도 검사합니다.

### 목적
VAMOS가 사용할 수 있는 모든 **외부 도구(Tool)**와 **API**를 등록·관리합니다. 사용자의 요청에 맞는 도구를 **자동으로 선택(Routing)**하고, 도구 호출 시 **권한 검사, 비용 추적, 로깅, 재시도**를 표준화된 방식으로 처리합니다. MCP(Model Context Protocol) 규격을 따릅니다. [근거: D2.0-02 §7.63~7.68, CLAUDE.md §6]

### 구조도

```
I-5 Decision (도구 사용 결정)
        ↓
┌──────────────────────────────────────────┐
│        I-10 Tool Registry/Router         │
│  ┌────────────────────────────────────┐  │
│  │ Tool Registry (도구 등록소)         │  │
│  │  - 웹 검색 (E-2)                   │  │
│  │  - 코드 실행 (E-4)                 │  │
│  │  - 문서 파서 (E-3)                 │  │
│  │  - 이미지 분석 (E-5)               │  │
│  │  - ... (MCP 도구들)                │  │
│  └────────────┬───────────────────────┘  │
│               ↓                          │
│  ┌────────────────────────────────────┐  │
│  │ Capability Matching (능력 매칭)     │  │  → 요청에 맞는 도구 선택
│  │ Permission Check (권한 검사)        │  │  → 읽기전용=자동, 쓰기=승인 필요
│  │ Cost Check (비용 검사)             │  │  → I-9와 연동
│  │ call_tool() (도구 호출)            │  │  → 표준 계약으로 실행
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
        ↓
  Tool Result (도구 실행 결과)
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `tool_id` | 필수 | 호출할 도구의 고유 ID |
| `input` | 필수 | 도구에 전달할 입력 데이터 |
| `policy_context` | 필수 | 정책 컨텍스트 (권한, 도메인, 위험도) |
| `cost_context` | 필수 | 비용 컨텍스트 (현재 예산 상태) |

[근거: D2.0-02 §7.64, §7.67]

### 출력 (Output)

| 필드 | 설명 |
|------|------|
| `tool_result` | 도구 실행 결과 데이터 |
| `ui_state` | UI에 전달할 상태 정보 (진행률, 상태 표시 등) |
| `preview` | 산출물 미리보기 (Artifact Preview) |

[근거: D2.0-02 §7.64]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `TOOL_AVAILABLE` | 도구 사용 가능 |
| `TOOL_UNAVAILABLE` | 도구 사용 불가 (오류/비활성) |
| `PERMISSION_GRANTED` | 권한 승인됨 |
| `PERMISSION_DENIED` | 권한 거부됨 |
| `EXECUTING` | 도구 실행 중 |
| `COMPLETED` | 도구 실행 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i10.ui.state.emitted` | UI 상태 이벤트 전송 완료 |
| `oc.i10.tool.called` | 도구 호출 시작 |
| `oc.i10.tool.failed` | 도구 호출 실패 |

[근거: D2.0-02 §7.65, §7.68]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I10_UI_EMIT_FAIL` | UI 상태 전송 실패 | 재시도 후 로그 기록 |
| `OC_I10_TOOL_FAIL` | 도구 실행 실패 | 대체 도구로 라우팅 또는 deny |

[근거: D2.0-02 §7.65, §7.68]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_ROUTE_SAFE_NODE` | 도구 라우팅 실패 시 안전한 기본 노드로 라우팅 |

[근거: D2.0-02 §6.3]

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| 도구 승인 Allowlist (DEC-003, LOCK) | 읽기전용 도구 = 자동 허용, 외부 API/쓰기/코드실행 = 확인 필요 |
| MCP 전송 방식 (DEC-017, LOCK) | Streamable HTTP 방식으로 도구 통신 |
| 5-Gate 통과 필수 | 위험 도구 (file_write, shell_exec 등)는 5-Gate 승인 필수 |

[근거: CLAUDE.md §7.1 DEC-003, DEC-017]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-5 (Condition & Decision Engine) | 도구 사용 결정 수신 |
| I-9 (Cost Manager) | 도구 호출 비용 추적 |
| I-17 (Blue Node Manager) | 블루 노드에서 도구 호출 시 중개 |
| E-1~E-16 (E-Series) | 실제 외부 기능 모듈들 (코딩, 검색, 파서 등) |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| 모듈 상태 | CORE | CORE | CORE | CORE |

### LOCK 여부
- **change_lock = false** — 새로운 도구/API 추가에 따라 확장 가능
- 단, 도구 승인 Allowlist(DEC-003)와 MCP 전송 방식(DEC-017)은 LOCK

### 핵심 요약 (3줄)
1. **I-10 Tool Registry/Router**는 VAMOS의 도구 관리실로, 사용 가능한 모든 도구를 등록하고 적합한 도구를 자동 선택합니다.
2. MCP(Model Context Protocol) 규격을 따르며, 도구 호출 시 권한/비용/로깅을 표준화된 방식으로 처리합니다.
3. 위험한 도구(파일 쓰기, 코드 실행 등)는 반드시 5-Gate 승인을 통과해야 사용할 수 있습니다.

---

## §7.11 I-11 출력 조합기 (Output Composer)

### 비유
여러 부서에서 올라온 보고서를 하나의 **최종 보고서로 편집·조립하는 편집장**과 같습니다. 핵심 답변, 근거 자료, 자체 점검 결과를 정해진 양식(ResponseEnvelope)에 맞춰 깔끔하게 조립합니다.

### 목적
I-5(Condition & Decision Engine)의 판단 결과, I-2(Context Builder)의 근거 자료, I-6(Self-check)의 검증 결과를 모아서 **3-Part Output**(답변 + 근거 + 자체점검)으로 구성된 **ResponseEnvelope**(응답 봉투)를 조립합니다. 이 봉투가 사용자에게 전달되는 최종 출력물의 원형입니다. [근거: D2.0-02 §5.1, CLAUDE.md §5]

### 구조도

```
┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│ I-5 Decision│  │ I-2 Evidence│  │ I-6 Self-check│
│  (판단 결과) │  │  (근거 자료) │  │  (검증 결과)  │
└──────┬──────┘  └──────┬──────┘  └──────┬───────┘
       └────────────────┼────────────────┘
                        ↓
         ┌──────────────────────────┐
         │   I-11 Output Composer   │
         │  ┌────────────────────┐  │
         │  │ ResponseEnvelope   │  │
         │  │ ┌────────────────┐ │  │
         │  │ │ 1. answer      │ │  │  → 사용자에게 보여줄 답변
         │  │ │ 2. evidence    │ │  │  → 근거 요약 + QoD 점수
         │  │ │ 3. self_check  │ │  │  → 자체 점검 결과
         │  │ │ 4. metadata    │ │  │  → trace_id, 에러 코드 등
         │  │ └────────────────┘ │  │
         │  └────────────────────┘  │
         └──────────────────────────┘
                        ↓
              최종 출력 → I-13 렌더러
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `decision` | 필수 | I-5에서 생성한 Decision 객체 (결론, 라우팅, 근거 포함) |
| `evidence_items` | 필수 | I-2/I-15에서 수집·검증한 근거 자료들 |
| `self_check_result` | 필수 | I-6에서 수행한 자체 점검 결과 |
| `output_spec` | 선택 | 출력 형식 제약 (format_constraints) |

### 출력 (Output) — ResponseEnvelope (LOCK)

| 필드 | 설명 | 예시 |
|------|------|------|
| `answer.summary` | 짧은 결론/요약 | `"삼성전자는 반도체 시장 회복과 함께..."` |
| `answer.details` | 상세 설명 | 마크다운 형식의 본문 |
| `answer.next_actions` | 후속 조치 제안 | `["추가 분석 요청", "관련 리포트 보기"]` |
| `evidence.coverage` | 근거 커버율 (%) | `85%` |
| `evidence.qod_score` | 근거 품질 점수 (0.0~1.0) | `0.82` |
| `evidence.items[]` | 근거 항목 리스트 | `[{source, snippet, relevance}]` |
| `self_check.score` | 자체 점검 점수 | `0.88` |
| `self_check.verdict` | 판정 결과 | `PASS` / `WARN` / `FAIL` |
| `metadata.trace_id` | 추적 ID | `"tr_xyz789"` |
| `metadata.failure_codes` | 발생한 에러 코드 목록 | `[]` |

[근거: D2.0-02 §5.1.1 ResponseEnvelope]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `COMPOSING` | 출력 조립 중 |
| `STRUCTURED` | 구조화 완료 |
| `VALIDATED` | 출력 규격 검증 완료 |
| `READY` | 전송 준비 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i11.output.structured` | 출력 구조화 완료 |
| `oc.i11.spec.violated` | 출력 규격 위반 감지 |
| `oc.i11.mask.applied` | PII 마스킹 적용됨 |

[근거: D2.0-02 §7.37, §6.1]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I11_OUTPUT_SPEC_VIOLATION` | 출력 규격 위반 | FB_OUTPUT_REFORMAT |
| `OC_I11_CITATION_MISSING` | 인용/출처 누락 | FB_POLICY_MASK |
| `OC_I11_MASK_FAIL` | PII 마스킹 실패 | FB_POLICY_MASK |

[근거: D2.0-02 §6.2]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_OUTPUT_REFORMAT` | 출력 규격 위반 시 구조 재정렬 + 누락 항목을 compliance_report로 명시 |
| `FB_OUTPUT_MINIMAL` | 심각한 실패 시 핵심 결론만 최소 포맷으로 출력 |
| `FB_POLICY_MASK` | 마스킹 실패 시 민감 필드 재탐지 후 재출력 |

[근거: D2.0-02 §6.3]

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| 출력 규격 준수 (LOCK) | ResponseEnvelope 3-Part 구조는 변경 불가 |
| PII 마스킹 | 민감 정보 자동 감지·마스킹 후 출력 |
| EvidenceGate 미달 시 | 근거 부족이면 결론을 HOLD/ESCALATE로 제한 |

[근거: D2.0-02 §5.1]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-5 (Condition & Decision Engine) | 판단 결과를 입력으로 수신 |
| I-2 (Context Builder) | 근거 자료 수신 |
| I-6 (Self-check Engine) | 자체 점검 결과 수신 |
| I-13 (Multimodal Renderer) | 조립된 봉투를 렌더링으로 전달 |
| I-15 (Evidence & QoD) | QoD 점수를 evidence 섹션에 반영 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| 모듈 상태 | CORE | CORE | CORE | CORE |

### LOCK 여부
- **change_lock = false** — 출력 형식은 확장 가능
- 단, **ResponseEnvelope 3-Part 구조** (answer + evidence + self_check)는 LOCK

### 핵심 요약 (3줄)
1. **I-11 Output Composer**는 편집장처럼 판단 결과·근거·자체 점검을 하나의 ResponseEnvelope(응답 봉투)로 조립합니다.
2. 3-Part Output(답변 + 근거 + 자체점검) 구조는 LOCK으로 고정되어 모든 응답이 동일한 형식을 따릅니다.
3. 근거가 부족하면 결론을 제한하고, 민감 정보는 자동 마스킹하여 안전한 출력을 보장합니다.

---

## §7.12 I-12 작업흐름 설계기 (Workflow Builder)

### 비유
복잡한 프로젝트의 **공정 관리자(PM)**와 같습니다. "먼저 자료를 검색하고 → 요약하고 → 비교하고 → 보고서 작성"처럼 여러 단계의 작업을 순서대로(또는 동시에) 배치하는 작업 흐름(Workflow)을 설계합니다.

### 목적
복잡한 요청을 여러 단계의 작업으로 분해하고, 작업 간 **의존성(DAG, Directed Acyclic Graph — 방향이 있고 순환이 없는 그래프)**을 파악하여 실행 가능한 작업 흐름을 생성합니다. Self-evo(자기진화) 후보 작업의 스케줄링도 담당하며, 자동 적용은 금지되고 반드시 승인을 거쳐야 합니다. [근거: D2.0-02 §7.69, CLAUDE.md §6]

### 구조도

```
복잡한 요청: "주요 반도체 기업 3곳을 비교 분석해줘"
                        ↓
┌──────────────────────────────────────────────┐
│          I-12 Workflow Builder                │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │ DAG (작업 흐름 그래프)                │    │
│  │                                      │    │
│  │  [검색: 삼성] ──┐                    │    │
│  │  [검색: TSMC] ──┼──→ [비교 분석] ──→ [보고서 작성] │
│  │  [검색: Intel] ─┘                    │    │
│  │                                      │    │
│  │  (검색 3건은 동시 실행, 비교는 이후)  │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │ Self-evo 스케줄링 (자동적용 금지!)    │    │
│  │  → 개선 후보 등록 → I-19로 승인 요청  │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `candidate_change` | 선택 | Self-evo 후보 변경 사항 (I-6 Self-check 결과에서 발생) |
| `intent_frame` | 필수 | I-1에서 생성한 의도 프레임 (작업 분해용) |
| `hints` | 선택 | I-18에서 추출한 개선 힌트 |

[근거: D2.0-02 §7.70]

### 출력 (Output)

| 필드 | 설명 |
|------|------|
| `job_id` | 스케줄링된 작업의 고유 ID |
| `workflow_dag` | 작업 흐름 DAG (노드=작업, 엣지=의존성) |
| `approval_request` | I-19로 보내는 승인 요청 (Self-evo 작업인 경우) |

[근거: D2.0-02 §7.70]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `TEMPLATE_SELECTED` | 작업 템플릿 선택됨 |
| `DAG_PLANNED` | 작업 흐름 DAG 생성 완료 |
| `JOB_SCHEDULED` | 작업 스케줄링됨 |
| `APPROVAL_PENDING` | 승인 대기 중 |
| `EXECUTING` | 워크플로우 실행 중 |
| `COMPLETED` | 워크플로우 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i12.job.scheduled` | 작업 스케줄링 완료 |

[근거: D2.0-02 §7.71]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I12_SCHED_FAIL` | 작업 스케줄링 실패 | 단순 순차 실행으로 대체 |

[근거: D2.0-02 §7.71]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| (DAG 실패 시) | 복잡한 DAG 대신 단순 순차 실행으로 다운그레이드 |
| (승인 미달 시) | 수동 워크플로우 실행으로 전환 |

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| Self-evo 자동적용 금지 (LOCK) | 개선 제안만 가능, 자동 반영 절대 금지 |
| 승인 게이트 연동 | Self-evo 작업은 I-19 Approval Manager를 통한 승인 필수 |
| 롤백 잠금 | 동일 제안이 롤백된 후 14일간 재적용 금지 (LOCK) |

[근거: CLAUDE.md §7.5 Self-evo LOCK]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-5 (Condition & Decision Engine) | Decision의 라우팅이 워크플로우 선택에 영향 |
| I-6 (Self-check Engine) | Self-check 결과가 워크플로우 개선 제안으로 연결 |
| I-9 (Cost Manager) | 배치 작업 비용 연동 |
| I-18 (Self-evo Engine) | 개선 힌트를 워크플로우 후보로 수신 |
| I-19 (Approval Manager) | Self-evo 작업의 승인 요청 전송 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | OFF | **OFF** | **COND** (조건부) | **ON** |
| 모듈 상태 | — | COND | COND | COND→ON |

> **참고**: COND(조건부)란 특정 조건이 충족되어야만 활성화되는 상태입니다. V2에서는 거버넌스 결정에 따라 활성화 여부가 결정됩니다.

### LOCK 여부
- **change_lock = false** — 워크플로우 패턴은 확장 가능
- 단, Self-evo 자동적용 금지 원칙은 LOCK

### 핵심 요약 (3줄)
1. **I-12 Workflow Builder**는 복잡한 요청을 여러 단계로 분해하여 DAG(방향 비순환 그래프) 기반 작업 흐름을 설계합니다.
2. Self-evo(자기진화) 작업의 스케줄링을 담당하되, 자동 적용은 절대 금지이고 반드시 승인을 거쳐야 합니다 (LOCK).
3. V1에서는 비활성이며, V2에서 조건부 활성, V3에서 완전 활성화됩니다.

---

## §7.13 I-13 다중 출력 렌더러 (Multimodal Output Renderer)

### 비유
보고서의 내용을 **예쁘게 꾸미는 디자이너**와 같습니다. 같은 내용이라도 텍스트, 코드 블록, 차트, 이미지 등 다양한 형태로 시각적으로 렌더링(표현)하여 사용자가 보기 쉽게 만듭니다.

### 목적
I-11(Output Composer)이 조립한 ResponseEnvelope의 내용을 사용자에게 보여줄 **최종 형태**로 렌더링합니다. 텍스트, 마크다운, 코드 블록, 차트, 이미지, 오디오 등 **다양한 출력 형식**을 지원하며, 도메인별 **템플릿(Template)**을 적용하여 일관된 품질의 출력을 생성합니다. [근거: D2.0-02 §7.72~7.74, CLAUDE.md §6]

### 구조도

```
I-11 ResponseEnvelope (조립된 응답)
            ↓
┌────────────────────────────────────────┐
│    I-13 Multimodal Output Renderer     │
│  ┌──────────────────────────────────┐  │
│  │ Template Engine (템플릿 엔진)     │  │
│  │  ┌─────────────────────────────┐ │  │
│  │  │ TS_CORE: 일반 대화/요약     │ │  │  ← 기본 템플릿
│  │  │ TS_WEB_RESEARCH: 웹 리서치  │ │  │  ← 인용·출처 중심
│  │  │ TS_CODE: 코딩/디버깅        │ │  │  ← 코드 블록 중심
│  │  └─────────────────────────────┘ │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │ 렌더링 출력 형식:                 │  │
│  │  📝 텍스트/마크다운               │  │
│  │  💻 코드 블록 (구문 강조)         │  │
│  │  📊 차트/그래프                   │  │
│  │  🖼️ 이미지                       │  │
│  │  🔊 오디오 (V2+)                 │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
            ↓
     Builder/Hologram UI에 표시
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `response_envelope` | 필수 | I-11에서 조립한 응답 봉투 |
| `template_set_id` | 필수 | 적용할 템플릿 세트 ID (TS_CORE, TS_WEB_RESEARCH, TS_CODE) |
| `format_constraints` | 선택 | 출력 형식 제약 조건 |
| `artifact_refs` | 선택 | 임베드할 산출물 참조 (이미지, 코드 등) |

### 출력 (Output)

| 필드 | 설명 |
|------|------|
| `rendered_components` | 렌더링된 UI 컴포넌트들 (텍스트, 코드, 차트 등) |
| `ui_events` | 프론트엔드에 전달할 UIEvent 메시지 |
| `preview_artifacts` | 사용자 확인용 산출물 미리보기 |

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `TEMPLATE_LOADED` | 템플릿 로드 완료 |
| `FORMATTING` | 템플릿에 맞게 형식 변환 중 |
| `RENDERING_COMPLETE` | 렌더링 완료 |
| `ARTIFACT_EMBEDDED` | 산출물(이미지/차트) 임베드 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i13.template.selected` | 템플릿 선택 완료 |

[근거: D2.0-02 §7.74]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I13_TEMPLATE_FAIL` | 템플릿 적용 실패 | 마크다운 기본 형식으로 대체 |

[근거: D2.0-02 §7.74]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| (템플릿 실패 시) | 마크다운 기본 형식으로 대체 출력 |
| (멀티미디어 실패 시) | 텍스트 전용 모드로 전환 |

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| TemplateSet = 3 최소 필수 (LOCK) | TS_CORE, TS_WEB_RESEARCH, TS_CODE 3가지 기본 템플릿 필수 |
| 템플릿 주입 규칙 (LOCK) | CORE가 템플릿을 선택, NODE는 수정 불가 (D2.0-03 §4.2) |
| DSPy 최적화 (V3) | 동적 프롬프트 튜닝으로 템플릿 파라미터 최적화 |

[근거: D2.0-02 §7.72~7.74, D2.0-03 §4.2]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-11 (Output Composer) | 조립된 ResponseEnvelope 수신 |
| I-17 (Blue Node Manager) | NODE 출력에 템플릿 적용 |
| I-10 (Tool Registry) | UI 상태 이벤트 연동 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| 모듈 상태 | CORE | CORE | CORE | CORE |

### LOCK 여부
- **change_lock = false** — 새로운 출력 형식/템플릿 추가 가능
- 단, 기본 3종 TemplateSet(TS_CORE, TS_WEB_RESEARCH, TS_CODE) 필수는 LOCK

### 핵심 요약 (3줄)
1. **I-13 Multimodal Output Renderer**는 디자이너처럼 응답 내용을 텍스트/코드/차트/이미지 등 다양한 형태로 시각적으로 렌더링합니다.
2. 3가지 기본 템플릿(일반 대화, 웹 리서치, 코딩)이 필수이며(LOCK), 도메인별로 확장 가능합니다.
3. CORE가 템플릿을 선택하고 NODE는 수정할 수 없는 **템플릿 주입 규칙**이 적용됩니다 (LOCK).

---

## §7.14 I-14 요약 & 기억 증류기 (Summarizer & Memory Distiller)

### 비유
긴 회의록을 읽고 **핵심 3줄로 요약하는 비서**와 같습니다. 또한 일시적인 대화 기록(L0)에서 중요한 내용을 선별하여 장기 기억(L1)으로 승격시킬지 판단하는 **기억의 문지기** 역할도 합니다.

### 목적
긴 대화 내용이나 실행 로그를 **압축·요약**하여 메모리 공간을 절약합니다. 또한 L0(세션 메모리, 단기 기억)에 저장된 정보 중 **중요한 것**을 L1(사용자 메모리, 장기 기억)으로 **승격(Promotion)**시킬지 판단합니다. 이를 통해 VAMOS가 사용자와의 과거 대화에서 핵심만 기억하고 불필요한 정보는 잊을 수 있습니다. [근거: CLAUDE.md §6 I-14 설명]

### 구조도

```
긴 대화 기록 / 실행 로그
            ↓
┌────────────────────────────────────────────┐
│    I-14 Summarizer & Memory Distiller      │
│  ┌──────────────────────────────────────┐  │
│  │ Summarizer (요약기)                   │  │
│  │  - 긴 텍스트 → 핵심 3줄 요약          │  │
│  │  - 대화 내용 → 주요 결정사항 추출      │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │ Memory Distiller (기억 증류기)        │  │
│  │  - L0 → L1 승격 판단                  │  │
│  │  - "이건 장기 기억할 가치가 있나?"      │  │
│  │  - 기억 압축 (불필요한 세부사항 제거)   │  │
│  └──────────────────────────────────────┘  │
└────────────────────────────────────────────┘
            ↓
   L1 메모리 저장 또는 L0 유지/삭제
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `conversation_history` | 필수 | 전체 대화/실행 로그 기록 |
| `session_context` | 필수 | 현재 세션의 맥락 정보 |
| `summary_target` | 선택 | 요약 대상 지정 (대화? 결정? 근거?) |

### 출력 (Output)

| 필드 | 설명 |
|------|------|
| `l2_summary` | 압축된 L2 수준 요약 |
| `key_points` | 핵심 포인트 추출 목록 |
| `promotion_decision` | L0→L1 승격 판단 결과 (승격/유지/삭제) |
| `distilled_memory` | 증류된(압축된) 기억 표현 |

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `SUMMARIZING` | 요약 처리 중 |
| `SUMMARY_GENERATED` | 요약 생성 완료 |
| `QOD_VALIDATED` | 요약 품질 검증 완료 (I-15 연동) |
| `STORED` | 메모리에 저장 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `mem.summary.generated` | 요약 생성 완료 |
| `mem.promotion.decided` | L0→L1 승격 판단 완료 |

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I14_SUMMARY_FAIL` | 요약 생성 실패 | L1에 원본(verbose) 형태로 저장 |

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| (요약 실패 시) | 원본 L0/L1 형태 그대로 저장 (압축 없이) |
| (승격 판단 불가 시) | 기본값으로 L0 유지 (안전한 선택) |

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| L2 저장 정책 (LOCK) | L2 계층 저장은 기본 "승인 필요" |
| 메모리 계층 정책 | D2.0-06 메모리 구조에 따른 저장/압축 규칙 |
| Memory Decay 연동 | B-3 모듈과 연동하여 오래된 기억 자동 감쇠 |

[근거: CLAUDE.md §7.2 L2 저장 정책]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-3 (Memory System) | 메모리 계층 구조와 직접 연동 (L0/L1/L2/L3) |
| I-15 (Evidence & QoD) | 요약 품질 검증 |
| B-3 (Memory Decay) | 기억 감쇠/망각과 연동 |
| I-6 (Self-check Engine) | 요약 정확도 검증 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| 모듈 상태 | CORE | CORE | CORE | CORE |

### LOCK 여부
- **change_lock = false** — 요약 알고리즘은 버전에 따라 개선 가능
- 단, L2 저장 시 "승인 필요" 정책은 LOCK

### 관련 STEP7 확장

| 기능 | ID | 설명 | 버전 |
|------|----|------|------|
| 대화 자동 요약 | S7B-026 | 긴 대화의 주기적 자동 요약 생성 | V2 |
| 감정 이력 추적 | S7B-020 | 대화 감정 변화 추적 + 대시보드 | V2 |

[근거: D2.0-02 §7.30-C, §7.30-D]

### 핵심 요약 (3줄)
1. **I-14 Summarizer & Memory Distiller**는 긴 대화를 핵심만 요약하고, 중요한 기억을 L0에서 L1으로 승격시키는 기억의 문지기입니다.
2. 메모리 공간을 효율적으로 관리하여 VAMOS가 핵심만 기억하고 불필요한 정보는 압축·삭제합니다.
3. L2 계층 저장은 "승인 필요" 정책이 적용되며(LOCK), Memory Decay(B-3)와 연동하여 기억을 관리합니다.

---

## §7.15 I-15 근거 품질 관리자 (Evidence & QoD Manager)

### 비유
논문 심사위원처럼 **자료의 품질을 점수로 평가하는 감정사**입니다. "이 근거는 얼마나 관련이 있는지", "최신 정보인지", "출처는 믿을 만한지"를 종합적으로 점수화하여, 품질이 낮은 근거는 걸러냅니다.

### 목적
I-2(Context Builder)가 수집한 **근거 자료의 품질(QoD, Quality of Data)**을 0.0~1.0 점수로 산출합니다. 품질이 임계값 미만인 근거는 필터링하고, 근거가 부족하면 **재검색을 트리거**합니다. 이를 통해 VAMOS의 응답이 항상 **검증된 고품질 근거**에 기반하도록 보장합니다. [근거: D2.0-02 §7.90~7.92, CLAUDE.md §7.4]

### 구조도

```
I-2에서 수집한 근거 자료들
            ↓
┌────────────────────────────────────────────────┐
│       I-15 Evidence & QoD Manager              │
│  ┌──────────────────────────────────────────┐  │
│  │ QoD 점수 산출 (4가지 기준)                │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │ 관련성 (Relevance)    — 0.30 가중치│  │  │
│  │  │ 정확성 (Accuracy)     — 0.25 가중치│  │  │
│  │  │ 최신성 (Freshness)    — 0.25 가중치│  │  │
│  │  │ 완성도 (Completeness) — 0.20 가중치│  │  │
│  │  └────────────────────────────────────┘  │  │
│  │  → 종합 QoD = 가중 합산 (0.0 ~ 1.0)      │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │ 필터링 & 판정                             │  │
│  │  QoD ≥ 임계값 → PASS (통과)              │  │
│  │  QoD < 임계값 → WARN/FAIL → 재검색!      │  │
│  └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
            ↓
     Evidence Gate (S2 단계)에 판정 결과 전달
```

### QoD 가중치 (LOCK)

> **DEC-014 (LOCK)**: RAG 소스 QoD 가중치는 아래 값으로 고정됩니다.

| 평가 기준 | 가중치 | 설명 |
|----------|--------|------|
| 관련성 (Relevance) | **0.30** | 검색 의도와 얼마나 관련 있는가 |
| 정확성 (Accuracy) | **0.25** | 정보가 정확한가 |
| 최신성 (Freshness) | **0.25** | 최신 정보인가 (시간 감쇠 적용) |
| 완성도 (Completeness) | **0.20** | 질문의 범위를 얼마나 커버하는가 |

[근거: CLAUDE.md §7.4 DEC-014]

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `source_item` | 필수 | 평가할 근거 자료 (출처: RAG, TOOL, MEMORY, WEB, USER) |
| `evaluation_criteria` | 선택 | 평가 기준 (기본값: 위 4가지 가중치 적용) |
| `threshold` | 선택 | QoD 필터링 임계값 (기본값: 도메인별 상이) |

[근거: D2.0-02 §7.91]

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `qod_score` | 종합 QoD 점수 (0.0~1.0) | `0.82` |
| `filtered_items` | 임계값 기반 필터링된 근거 목록 | 통과한 근거 자료들 |
| `coverage` | 근거 커버율 (%) | `85%` |
| `verdict` | Evidence Gate 판정 | `PASS` / `WARN` / `FAIL` |

[근거: D2.0-02 §7.91]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `COLLECTING` | 근거 수집 중 (I-2와 연동) |
| `SCORING` | QoD 점수 산출 중 |
| `THRESHOLD_EVALUATED` | 임계값 평가 완료 |
| `FILTERED_READY` | 필터링 완료, 결과 준비됨 |
| `INSUFFICIENT` | 근거 부족 — 재검색 트리거 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i15.qod.scored` | QoD 점수 산출 완료 |

[근거: D2.0-02 §7.92]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I15_QOD_FAIL` | QoD 점수 산출 실패 | 보수적으로 낮은 QoD 점수 부여 |
| `OC_I2_EVIDENCE_QOD_LOW` | 근거 품질 기준 미달 | FB_RAG_RETRY_EXPAND (검색 범위 확장) |

[근거: D2.0-02 §7.92, §6.2]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_RAG_RETRY_EXPAND` | 근거 부족 시 검색 범위를 확장하여 재검색 |
| `FB_RAG_SWITCH_SOURCE` | 소스 차단/정책 문제 시 다른 소스로 재시도 |

[근거: D2.0-02 §6.3]

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| Evidence Gate (S2, LOCK) | 파이프라인 S2 단계에서 근거 충분성 필수 검증 — 우회 불가 |
| QoD 스케일 (DEC-010, LOCK) | QoD 점수 범위: 0.0~1.0 |
| 근거 부족 시 결론 제한 | QoD 미달이면 결론을 HOLD/ESCALATE/REQUEST_EVIDENCE로 제한 |
| Semantic Cache (LOCK) | cosine ≥ 0.95인 경우에만 캐시 적중으로 인정 |

[근거: CLAUDE.md §7.4 DEC-010, §7.4 Semantic Cache]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-2 (Context Builder) | 근거 수집 소스 — QoD 평가 대상 제공 |
| I-5 (Condition & Decision Engine) | QoD 판정 결과를 Evidence Gate에서 활용 |
| I-6 (Self-check Engine) | 근거 충분성을 품질 지표로 평가 |
| I-11 (Output Composer) | QoD 점수를 evidence 섹션에 포함 |
| I-16 (Knowledge Search) | 재검색 트리거 시 I-16에 검색 요청 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| 모듈 상태 | CORE | CORE | CORE | CORE |

### LOCK 여부
- **change_lock = false** — QoD 평가 알고리즘은 개선 가능
- 단, QoD 가중치(DEC-014), QoD 스케일(DEC-010), Evidence Gate 기능은 LOCK

### 핵심 요약 (3줄)
1. **I-15 Evidence & QoD Manager**는 근거 자료의 품질(관련성·정확성·최신성·완성도)을 0.0~1.0 점수로 평가하는 감정사입니다.
2. QoD 가중치(관련성 0.30, 정확성 0.25, 최신성 0.25, 완성도 0.20)는 LOCK으로 고정됩니다.
3. 근거 품질이 미달이면 재검색을 트리거하고, 그래도 부족하면 결론을 HOLD/ESCALATE로 제한합니다.

---

## §7.16 I-16 지식 검색 엔진 (Knowledge Search Engine)

### 비유
도서관의 **사서(Librarian)**와 같습니다. 내부 지식 저장소와 외부 웹을 동시에 뒤져서 필요한 정보를 찾아오고, 관련도 순으로 정렬하여 전달합니다. 전통적 키워드 검색과 의미 기반 검색을 결합한 **하이브리드 검색**을 수행합니다.

### 목적
사용자의 요청에 필요한 **지식과 근거를 검색**합니다. 내부 지식 저장소(Knowledge Base)와 외부 소스(웹, API 등)를 대상으로 **Hybrid Search(BM25 키워드 검색 + Vector 의미 검색)**를 실행하고, 결과를 관련도 순으로 정렬하여 I-2(Context Builder)에 전달합니다. **Semantic Cache**(의미 기반 캐시)를 활용하여 유사한 질문에 빠르게 응답합니다. [근거: CLAUDE.md §6, §7.4]

### 구조도

```
I-1 IntentFrame (검색 의도)
            ↓
┌────────────────────────────────────────────────────┐
│         I-16 Knowledge Search Engine               │
│  ┌──────────────────────────────────────────────┐  │
│  │ Hybrid Search (하이브리드 검색)                │  │
│  │  ┌─────────────────┐  ┌───────────────────┐  │  │
│  │  │ BM25 키워드 검색  │  │ Vector 의미 검색   │  │  │
│  │  │ (전통적 매칭)     │  │ (벡터 유사도)      │  │  │
│  │  └────────┬────────┘  └────────┬──────────┘  │  │
│  │           └──────────┬─────────┘              │  │
│  │                      ↓                        │  │
│  │           결과 병합 + 순위 재정렬 (Re-rank)    │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │ Semantic Cache (의미 캐시)                     │  │
│  │  cosine ≥ 0.95 → 캐시 적중 (LOCK)             │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │ 검색 대상:                                    │  │
│  │  📚 내부 KB (지식 저장소)                      │  │
│  │  🌐 외부 웹 검색                               │  │
│  │  🔌 API/도구 결과                              │  │
│  │  🧠 메모리 (L1/L2/L3)                         │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
            ↓
     검색 결과 → I-2 Context Builder → I-15 QoD 평가
```

### RAG Pipeline (LOCK)

> 검색은 아래 6단계 파이프라인을 따릅니다:

| 단계 | 설명 | 세부 |
|------|------|------|
| 1. Collect | 데이터 수집 | 내부 KB + 외부 소스에서 원시 데이터 수집 |
| 2. Chunk | 청킹 (분할) | 300~500 토큰 단위로 분할 (LOCK) |
| 3. Embed | 임베딩 (벡터화) | V1: BGE-M3 (로컬, 1024dim) / text-embedding-3-small (클라우드) |
| 4. Store | 벡터 저장 | V1: Chroma (로컬) / V2+: Qdrant (서버) |
| 5. Retrieve | 검색 | Hybrid: BM25 + Vector 검색 |
| 6. Generate | 생성 | 검색 결과 기반 응답 생성 |

[근거: CLAUDE.md §7.4 RAG Pipeline, DEC-004, DEC-005]

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `query_intent` | 필수 | I-1에서 추출한 검색 의도 |
| `search_strategy` | 선택 | 검색 전략 (fast/thorough, 소스 지정 등) |
| `context_filters` | 선택 | 도메인, 날짜 범위, 언어 필터 |

### 출력 (Output)

| 필드 | 설명 |
|------|------|
| `search_results[]` | 관련도 순 정렬된 검색 결과 목록 |
| `result.source_id` | 소스 식별자 |
| `result.source_type` | 소스 유형 (RAG/TOOL/MEMORY/WEB/USER) |
| `result.relevance_score` | 관련도 점수 |
| `result.snippet` | 핵심 발췌문 |
| `search_metrics` | 검색 성과 (적중 수, 소요 시간, 조회 소스 수) |

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `SEARCH_INITIALIZED` | 검색 초기화 |
| `QUERIES_ROUTED` | 검색 쿼리가 각 소스로 라우팅됨 (병렬 실행) |
| `RESULTS_AGGREGATED` | 결과 수집 완료 |
| `RESULTS_RANKED` | 결과 순위 정렬 완료 |
| `RESULTS_RETURNED` | I-2에 결과 전달 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i2.search.executed` | 검색 실행 완료 |
| `oc.i2.cache.hit` | Semantic Cache 적중 |
| `oc.i2.source.failed` | 특정 소스 검색 실패 |

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I2_RAG_NO_SOURCE` | 검색 결과 없음 (0건) | FB_RAG_RETRY_EXPAND |
| `OC_I2_TIMEOUT` | 검색 시간 초과 | FB_RAG_SWITCH_SOURCE |
| `OC_I2_SOURCE_POLICY_BLOCK` | 소스 접근 정책 차단 | FB_RAG_SWITCH_SOURCE |

[근거: D2.0-02 §6.2]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_RAG_RETRY_EXPAND` | 검색 범위 확장 (내부→외부, 최신성 완화 등) 후 재시도 |
| `FB_RAG_SWITCH_SOURCE` | 다른 소스 세트로 재시도, 타임아웃 시 짧은 응답 모드로 축소 |

[근거: D2.0-02 §6.3]

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| 검색 깊이 결정 (I-5) | CORE가 검색 깊이(fast vs thorough) 결정 |
| 비용 통제 (I-9) | 세션당 검색 쿼리 수 제한 |
| 소스 Allowlist (DEC-003) | 승인된 소스만 검색 대상 |
| Semantic Cache 임계값 (LOCK) | cosine ≥ 0.95만 캐시 적중 인정 |

[근거: CLAUDE.md §7.4]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-1 (Intent Detector) | 검색 의도(IntentFrame) 수신 |
| I-2 (Context Builder) | 검색 결과를 근거로 전달 |
| I-15 (Evidence & QoD) | 검색 결과의 QoD 평가 요청 |
| I-21 (Source Evolution) | 소스별 성공/실패 평가 → 소스 전략 개선 제안 (V3) |
| S-6 (Search Evolution) | 검색 전략 자체를 평가·개선 제안 (V3) |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| RAG 수준 | — | Basic (64%+) | Hybrid+Rerank (83%+) | Self-RAG+Graph (90%+) |
| Vector DB | — | Chroma (로컬) | Qdrant (서버) | Qdrant (서버) |
| Embedding | — | BGE-M3 (1024dim) | BGE-M3 + Reranker | BGE-M3 + GraphRAG |

[근거: CLAUDE.md §7.4 DEC-004]

### LOCK 여부
- **change_lock = false** — 검색 알고리즘과 소스 통합은 진화 가능
- 단, Semantic Cache 임계값(cosine ≥ 0.95), RAG Pipeline 6단계, 청킹 크기(300~500tok)는 LOCK

### 핵심 요약 (3줄)
1. **I-16 Knowledge Search Engine**은 도서관 사서처럼 내부 KB와 외부 웹에서 Hybrid Search(BM25 + Vector)로 정보를 검색합니다.
2. Semantic Cache(cosine ≥ 0.95, LOCK)를 활용하여 유사 질문에 빠르게 응답하고, RAG 수준은 V1 Basic → V2 Hybrid → V3 Self-RAG+Graph로 진화합니다.
3. 검색 결과 없음/시간 초과 시 자동으로 검색 범위를 확장하거나 다른 소스로 전환합니다.

---

## §7.17 I-17 실행팀 관리자 (Blue Node Manager)

### 비유
회사의 **팀장/부서 관리자**와 같습니다. 각 부서(Blue Node)의 인력(실행 역량)을 파악하고, 적합한 부서에 업무를 배정하고, 업무 진행 상태를 모니터링하고, 문제가 생기면 상위(ORANGE CORE)에 보고합니다.

### 목적
VAMOS의 실행 계층인 **BLUE NODE**(도메인 전용 실행 스택)의 **생명주기(Lifecycle)**를 관리합니다. 어떤 Blue Node가 어떤 역량(Capability)을 가지고 있는지 등록·관리하고, ORANGE CORE의 결정(I-5)에 따라 적합한 Node에 작업을 **배정(Routing)**합니다. Node의 상태를 모니터링하고, 실패 시 에스컬레이션(상위 보고)합니다. [근거: CLAUDE.md §6, D2.0-03]

### 구조도

```
I-5 Decision (어떤 Node에 실행시킬지 결정)
            ↓
┌────────────────────────────────────────────────────────┐
│              I-17 Blue Node Manager                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Node Registry (노드 등록소)                       │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │ NodeCapabilityProfile (노드 역량 프로필)      │ │  │
│  │  │  - Dev Node: 코딩/시스템 설계                 │ │  │
│  │  │  - Research Node: 웹 리서치/분석              │ │  │
│  │  │  - Productivity Node: 문서/일정 관리          │ │  │
│  │  │  - Content Node: 글쓰기/번역                  │ │  │
│  │  │  - Quant Node: 투자/금융 분석 (P1/P2)        │ │  │
│  │  │  - Trading Node: 매매 전략 (P2)               │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Lifecycle Management (생명주기 관리)               │  │
│  │  생성 → 초기화 → 실행 → 완료/실패 → 정리          │  │
│  │                                                  │  │
│  │ Template Injection (템플릿 주입, LOCK)             │  │
│  │  → CORE가 선택한 템플릿으로만 실행                 │  │
│  │  → NODE가 템플릿 수정하는 것은 금지!               │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ P0/P1/P2 활성화 정책                              │  │
│  │  P0 (안전): 항상 활성 — 기본 도메인               │  │
│  │  P1 (주의): 조건부 활성 — 승인 필요               │  │
│  │  P2 (고위험): 기본 OFF — 세션별 명시적 승인 필요   │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
            ↓
   Blue Node 실행 결과 → I-6 Self-check → I-11 Output Composer
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `routing_decision` | 필수 | I-5에서 결정한 실행 대상 Node ID |
| `execution_mode` | 필수 | 실행 모드: `mini` (경량) / `main` (표준) / `tool` (도구만) |
| `decision_object` | 필수 | 제약 조건, 템플릿 ID, 메모리 계획 포함 |
| `node_capabilities` | 참조 | Node 역량 레지스트리 (어떤 Node가 무엇을 할 수 있는지) |

### 출력 (Output)

| 필드 | 설명 |
|------|------|
| `node_result` | Node 실행 결과 (도메인별 출력물) |
| `node_state_update` | Node 상태 업데이트 (성공/실패/에스컬레이션) |
| `execution_logs` | 실행 로그 및 트레이스 |
| `health_metrics` | Node 성능 지표 (비용, 지연, 성공률) |

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `REGISTRY_INITIALIZED` | Node 레지스트리 초기화 완료 |
| `NODE_CREATED` | Node 인스턴스 생성됨 |
| `NODE_EXECUTING` | Node 작업 실행 중 |
| `NODE_COMPLETED` | Node 작업 완료 |
| `NODE_FAILED` | Node 작업 실패 |
| `NODE_ESCALATED` | CORE로 에스컬레이션 (상위 보고) |
| `NODE_HEALTH_DEGRADED` | Node 성능 저하 감지 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `blue.node.created` | Blue Node 생성 |
| `blue.node.task.started` | Node 작업 시작 |
| `blue.node.task.completed` | Node 작업 완료 |
| `blue.node.task.failed` | Node 작업 실패 |
| `blue.node.escalated` | CORE로 에스컬레이션 발생 |
| `blue.node.health.degraded` | Node 성능 저하 |

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I5_ROUTE_NOT_FOUND` | 적합한 Node를 찾을 수 없음 | FB_ROUTE_SAFE_NODE |
| (NODE 정책 위반) | RULE 1.3 위반 감지 | 즉시 차단 + 감사 로그 |
| (도구 접근 거부) | Node의 도구 요청이 Gate에서 거부 | I-19 Approval Manager로 에스컬레이션 |

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_ROUTE_SAFE_NODE` | 적합한 Node 없을 시 범용 안전 Node로 라우팅 |
| (Mini Node 전환) | 실패 시 경량(Mini) 모드로 다운그레이드 |
| (도구 전용 실행) | Node 로직 우회, 도구만으로 실행 |

[근거: D2.0-02 §6.3]

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| Node 정책 상속 (LOCK) | NODE는 CORE 정책을 상속하며 재정의(override) 금지 |
| 템플릿 주입 (D2.0-03 §4.2, LOCK) | CORE가 `template_bundle_id`로 템플릿 선택, NODE는 수정 불가 |
| P0/P1/P2 활성화 정책 | P0=항상 ON, P1=승인 후 ON, P2=세션별 명시 승인 필수 |
| P2 자동 OFF (LOCK) | 세션 종료 시 P2 도메인 즉시 비활성화 |
| 동시성 상한 (LOCK) | MAX_CONCURRENT_BLUE_NODES = 3 |
| 도구 접근 제어 | NODE의 도구 요청은 5-Gate 평가 후 실행 |

[근거: CLAUDE.md §7.2, §7.3, D2.0-03 §4.2]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-1 (Intent Detector) | 의도 라우팅이 Node 선택에 영향 |
| I-5 (Condition & Decision Engine) | 실행 모드(mini/main/tool) 결정 |
| I-6 (Self-check Engine) | Node 출력을 전송 전에 검증 |
| I-9 (Cost Manager) | Node 실행 비용 추적 |
| I-10 (Tool Registry) | Node의 도구 호출 중개 |
| I-12 (Workflow Builder) | 여러 Node 호출을 워크플로우로 조합 |
| I-13 (Multimodal Renderer) | Node 출력에 템플릿 적용 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| 모듈 상태 | CORE | CORE | CORE | CORE |
| 동시 실행 | 1 | 3 (LOCK) | 3 (LOCK) | 3 (LOCK) |
| P2 도메인 | OFF | 세션별 승인 | 세션별 승인 | 세션별 승인 |

### LOCK 여부
- **change_lock = false** — Node 레지스트리는 새 도메인 추가에 따라 확장 가능
- 단, 아래 항목은 LOCK:
  - Node 정책 상속 규칙 (override 금지)
  - 템플릿 주입 규칙 (CORE 선택, NODE 수정 불가)
  - 동시 실행 상한 (MAX_CONCURRENT_BLUE_NODES = 3)
  - P2 세션 종료 시 자동 OFF

### 핵심 요약 (3줄)
1. **I-17 Blue Node Manager**는 팀장처럼 실행팀(Blue Node)의 생명주기를 관리하고, 적합한 Node에 작업을 배정합니다.
2. CORE가 선택한 템플릿으로만 실행되며(LOCK), Node가 템플릿을 수정하는 것은 금지됩니다.
3. 동시 실행 Node는 최대 3개(LOCK)이며, P2 고위험 도메인은 세션별 명시적 승인이 필요하고 세션 종료 시 자동 비활성화됩니다.

---

# 종합 비교표: I-9 ~ I-17

| 모듈 ID | 한글 명칭 | 영문 명칭 | 상태 | LOCK | V1 | V2 | V3 |
|---------|----------|----------|------|------|----|----|-----|
| I-9 | 비용 관리자 | Cost Manager | CORE(LOCK) | **true** | ON | ON | ON |
| I-10 | 도구 등록소 | Tool Registry/Router | CORE | false | ON | ON | ON |
| I-11 | 출력 조합기 | Output Composer | CORE | false | ON | ON | ON |
| I-12 | 작업흐름 설계기 | Workflow Builder | COND | false | OFF | COND | ON |
| I-13 | 다중 출력 렌더러 | Multimodal Output Renderer | CORE | false | ON | ON | ON |
| I-14 | 요약·기억 증류기 | Summarizer & Memory Distiller | CORE | false | ON | ON | ON |
| I-15 | 근거 품질 관리자 | Evidence & QoD Manager | CORE | false | ON | ON | ON |
| I-16 | 지식 검색 엔진 | Knowledge Search Engine | CORE | false | ON | ON | ON |
| I-17 | 실행팀 관리자 | Blue Node Manager | CORE | false | ON | ON | ON |

[근거: CLAUDE.md §6, D2.0-02 §4.0]

---

# 검증 체크리스트 결과

- [x] 9개 모듈 모두 작성 완료 (I-9 ~ I-17)
- [x] 각 모듈 13가지 항목 모두 포함 (비유, 목적, 입력, 출력, 상태, 이벤트, 에러코드, 폴백, Policy Hook, 관련 모듈, 버전별 활성, LOCK 여부, 핵심 요약)
- [x] I-9의 LOCK 표시 및 비용 상한 ABSOLUTE LOCK 명시
- [x] 모든 모듈에 비유 설명 포함
- [x] 근거 SOT 참조 표기 완료
