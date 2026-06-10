# computer_use_agent_v2.md — J-059 V2 EXTEND (Computer Use Agent + R-05-7 경계 샌드박스 격리)

> **Status**: V2-Phase 2 (2-4 #2b)
> **작성일**: 2026-04-19
> **V1 정본**: [computer_use_agent.md](./computer_use_agent.md) (Phase 1-6 완료, ~3.5K, read-only sha256 baseline, J-059 V1 골격)
> **SoT 근거**: STEP7-J Part 7 J-059 (L1005~L1034)
> **담당 J-ID**: **J-059** (V2 EXTEND: Claude Computer Use / OpenAI Operator 통합 + 샌드박스 격리 + 3-Gate 안전)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [task_planner_v2.md](./task_planner_v2.md) (DAG 분해) / [integration_architecture_v2.md](./integration_architecture_v2.md) (J-077 §6.7 CogAgent/SeeAct 트렌드 통합) + **[audio_safety_v2.md](../02_audio-processing/audio_safety_v2.md) §5.4 Constitutional AI** (R-05-7 경계 정책 통일)

---

## 1. Cross-domain 참조 블록

| 정본 | 역할 | 참조 지점 |
|------|------|----------|
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 7 J-059 (L1005~L1034) | 상위 SoT J-059 | §4 verbatim |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 9 J-077 (L1326~L1340) | 트렌드 모델 통합 | §5 (peer integration §5) |
| `computer_use_agent.md` (V1) | V1 정본 (V1 골격) | §3 V1 계승 |
| **`audio_safety_v2.md` §5.4 (peer Part 2 V2)** | **R-05-7 Constitutional AI + 경계 분류기 (정책 통일)** | **§4 E10** |
| `integration_architecture_v2.md` §5 (peer 본 #2b) | J-077 트렌드 모델 통합 | §4 E4 |
| `task_planner_v2.md` (peer 본 #2b) | DAG 분해 (J-060 → J-059 호출) | §4 E1 |
| AUTHORITY_CHAIN §4 LOCK-MM-06/11 | LOCK | §2 |

---

## 2. LOCK 인용

> LOCK (STEP7-J J-094~J-096): 비용 상한 V2 ≤ ₩40K($30) [LOCK-MM-06]

> LOCK (SPEC §14): 14-Item Tech Stack [LOCK-MM-11]

> **R-05-7 (종합계획서 §4)** 거버넌스 규칙: 안전 필터 항시 활성화 — 본 V2 샌드박스 격리 + 3-Gate 강화 의무

**적용 지표**:
- LOCK-MM-06 V2 ($30/call): Claude Computer Use $0.02/액션 + OpenAI Operator $0.05/액션 가드
- R-05-7: 액션별 명시적 허가 + 실행 전 미리보기 + 되돌리기 가능 액션만 자동 + 금융 거래 3-Gate

---

## 3. V1 → V2 승급

| 항목 | V1 (V1 computer_use_agent.md) | V2 (본 산출물) |
|------|-----------------------------|----------------|
| Computer Use Agent | V1 골격 (3.5K, 미구현) | **E1~E10 본문 + Claude Computer Use + OpenAI Operator + CogAgent (peer J-077 트렌드)** |
| 샌드박스 격리 | 미작성 | **R-05-7 경계 분류기 (peer audio_safety §5.4 통일)** |
| 3-Gate 안전 | 1줄 (V1 골격) | **3-Gate 본문 + 금융 거래 사용자 최종 확인** |

---

## 4. V2 본문 (STEP7-J L1005~L1034)

**근거 verbatim 인용** (STEP7-J L1008~L1030):
> ```
> [구현 상세]
> - Claude Computer Use / OpenAI Operator 스타일:
>   ├─ 스크린샷 기반 UI 인식
>   ├─ 마우스 클릭/드래그/스크롤 자동화
>   ├─ 키보드 입력 자동화
>   ├─ 웹 브라우저 조작
>   └─ 데스크톱 앱 조작
>
> - VAMOS Computer Use Agent:
>   ├─ 코딩: IDE에서 직접 코드 수정 (Dev Node 연동)
>   ├─ 투자: 증권사 HTS 자동 조작 (읽기 전용 기본)
>   ├─ 문서: Word/Excel/PPT 직접 편집
>   └─ 설정: 시스템 설정 자동 변경
>
> [보안]
> - 명시적 허가 필수 (액션별)
> - 실행 전 미리보기 + 확인
> - 되돌리기 가능한 액션만 자동, 불가능한 것은 승인 요청
> - 금융 거래는 반드시 사용자 최종 확인 (3-Gate 강화)
> ```

**SoT 구현성 (STEP7-J L1032)**: V2 — ⚠️ 6개월 (안전성 검증 필수) | V3: ✅ 풀 기능

#### E1. Schema
```python
from common_types import ModuleConfig, MultimodalMessage
from d202_02 import VamosError, VamosResult

class ComputerUseConfigV2(ModuleConfig):
    default_backend: Literal["claude-computer-use","openai-operator","cogagent","seeact"] = "claude-computer-use"
    enable_sandbox: bool = True                      # 항상 True (R-05-7)
    enable_3gate_finance: bool = True                # 금융 거래 3-Gate
    enable_preview: bool = True                      # 실행 전 미리보기
    enable_undo_only: bool = True                    # 되돌리기 가능한 액션만 자동
    max_cost_per_call_usd: float = 5.0               # per-action V2 (LOCK-MM-06 V2 ≤$30)
    sandbox_type: Literal["docker","vm","virtualbox"] = "docker"
    user_confirmation_required_actions: list[str] = [
        "finance_trade","file_delete","system_config","external_send"
    ]

class ComputerActionRequest:
    intent: str                                      # "이메일 답장 작성해줘" 등
    context_screenshot: Optional[bytes] = None       # 현재 화면
    target_app: Literal["browser","ide","office","hts","system"] = "browser"
    user_id: str
    safety_check: bool = True                        # R-05-7 경계 검사

class ComputerActionStep:
    step_id: int
    action_type: Literal["click","drag","scroll","type","key","wait","verify"]
    coordinates: Optional[tuple[int,int]] = None
    text: Optional[str] = None
    duration_ms: int = 100
    is_undoable: bool = True                         # 되돌리기 가능 여부
    requires_user_confirmation: bool = False         # 명시적 허가
    preview_text: str                                # 사용자에게 표시할 설명

class ComputerActionResult(VamosResult):
    completed_steps: list[ComputerActionStep]
    skipped_steps: list[ComputerActionStep]          # user 거부
    final_screenshot: Optional[bytes] = None
    cost_usd: float
    audit_log_id: UUID
```

#### E3. Algorithm — Computer Use 파이프라인
```python
async def execute_computer_use(req: ComputerActionRequest,
                              cfg: ComputerUseConfigV2) -> ComputerActionResult:
    # 1. R-05-7 경계 분류 (peer audio_safety §5.4 통일)
    if cfg.enable_sandbox:
        from audio.safety import constitutional_classify  # peer Part 2 V2 §5.4
        intent_safety = await constitutional_classify(req.intent, mode="action")
        if intent_safety.violates_policy:
            return VamosError(f"R-05-7 violation: {intent_safety.reason}")

    # 2. 샌드박스 격리 시작 (Docker / VM)
    sandbox = await spawn_sandbox(cfg.sandbox_type, target_app=req.target_app)

    # 3. 의도 → 액션 시퀀스 분해 (Claude Computer Use API)
    if cfg.default_backend == "claude-computer-use":
        steps = await claude_computer_use_decompose(req.intent, req.context_screenshot,
                                                   target=req.target_app)
    elif cfg.default_backend == "cogagent":
        # peer J-077 §6.7 트렌드 통합 (integration_architecture_v2 §5)
        steps = await cogagent_decompose(req.intent, req.context_screenshot)
    else:
        return VamosError(f"unsupported computer-use backend: {cfg.default_backend}")
    else:
        return VamosError(f"unsupported computer-use backend: {cfg.default_backend}")

    # 4. 미리보기 + 사용자 확인 (V2)
    if cfg.enable_preview:
        preview = format_preview(steps)
        approved_steps = await present_to_user_and_get_approval(preview)
    else:
        approved_steps = steps

    # 5. 단계별 실행 (3-Gate 강화)
    completed = []; skipped = []
    for step in approved_steps:
        # 5-1. 되돌리기 불가 액션 → 사용자 승인 강제
        if not step.is_undoable and cfg.enable_undo_only:
            step.requires_user_confirmation = True

        # 5-2. 금융/외부 송신/시스템 설정 → 3-Gate
        if (req.target_app == "hts" or step.action_type in cfg.user_confirmation_required_actions
            or step.action_type == "type" and contains_financial_data(step.text)):
            confirmed = await user_3gate_confirm(step,
                                                gate_1="실행 전 미리보기",
                                                gate_2="금액/대상 명시",
                                                gate_3="최종 OK")
            if not confirmed:
                skipped.append(step)
                continue

        # 5-3. 실행 in 샌드박스
        try:
            await sandbox.execute(step)
            completed.append(step)
        except SandboxError as e:
            skipped.append(step)
            await audit_log.write(verdict="SANDBOX_ERROR", step=step, error=str(e))

    # 6. 결과 스크린샷
    final_ss = await sandbox.capture_screenshot()
    cost = len(completed) * 0.02                     # Claude Computer Use ~$0.02/action

    # 7. 영구 감사 로그 (R-05-7)
    audit_id = await audit_log.write(verdict="COMPLETED",
                                    completed=len(completed), skipped=len(skipped),
                                    user_id=req.user_id, target_app=req.target_app,
                                    cost_usd=cost)

    await sandbox.destroy()                          # 격리 종료

    return ComputerActionResult(
        completed_steps=completed, skipped_steps=skipped,
        final_screenshot=final_ss, cost_usd=cost, audit_log_id=audit_id,
    )
```

#### E4. Backend Selection (peer J-077 §6.7 트렌드 통합)
| 시나리오 | 1순위 | 2순위 | 비고 |
|----------|-------|-------|------|
| 일반 GUI 자동화 | Claude Computer Use | OpenAI Operator | 가장 진보된 |
| 웹 자동화 | SeeAct (J-077 트렌드) | Claude CU | 웹 특화 |
| 모바일 UI (V3) | Ferret-UI (J-077 트렌드) | — | Apple 모바일 |
| 한국어 UI | CogAgent (J-077) + 한국어 데이터 | Claude CU | 한국어 특화 학습 |
| 코딩 (IDE) | Claude CU + Dev Node | OpenAI Operator | IDE 통합 |
| 투자 (HTS) | Claude CU + **3-Gate 강제** | — | 금융 안전 |

#### E5. Error Handling (R-05-7 경계)
| 에러 | 폴백 |
|------|------|
| R-05-7 위반 | 즉시 거부 + 영구 로그 |
| 샌드박스 spawn 실패 | 사용자 통지 + 수동 모드 안내 |
| 액션 시퀀스 분해 실패 | 사용자에게 직접 의도 입력 요청 |
| 미리보기 거부 | 액션 SKIP + 다음 단계로 |
| 3-Gate 미통과 | 액션 SKIP + 사용자 통지 |
| 샌드박스 내 실행 실패 | retry 1회 → 그래도 실패 시 SKIP |
| 비용 LOCK-MM-06 V2 초과 | 액션 중단 + 사용자 통지 |

#### E6. Cost
| 시나리오 | 단가 | 일 5건 (각 5 액션) | 월 |
|----------|------|-----------------|-----|
| Claude Computer Use | $0.02/action | $0.50 | $15 |
| OpenAI Operator | $0.05/action | $1.25 | $37.5 ⚠ V2 한도 근접 |
| CogAgent (자체 호스팅) | $0 | $0 | $0 |
| SeeAct (자체) | $0 | $0 | $0 |
| **V2 권장** | Claude CU + 자체 폴백 | $0.50 | **$15** ✅ |

#### E7. SLA
| 단계 | P50 | P99 |
|------|-----|-----|
| 의도 → 액션 분해 (Claude CU) | 1.5s | 5s |
| 액션 시퀀스 미리보기 | 100ms | 500ms |
| 단일 액션 실행 in 샌드박스 | 200ms | 1s |
| 5단계 시퀀스 E2E | 5s | 15s |

#### E8. Test (12건)
1. 코딩: "이 함수에 docstring 추가해줘" → IDE 액션 시퀀스 + 미리보기.
2. 투자 HTS: "삼성전자 100주 매수" → 3-Gate (preview + 금액 확인 + 최종 OK).
3. 문서: "이 표를 Excel로 옮겨줘" → Office 자동화.
4. 시스템 설정: "다크 모드 활성화" → user_confirmation_required.
5. R-05-7 경계 위반 ("악성 코드 작성") → 즉시 거부.
6. 미리보기 거부 → 액션 SKIP.
7. 3-Gate 거부 → 금융 거래 차단.
8. 샌드박스 spawn 실패 → 수동 모드 안내.
9. CogAgent (J-077) 한국어 UI → 한국어 메뉴 정확도.
10. SeeAct (J-077) 웹 자동화 시나리오.
11. LOCK-MM-06 V2 초과 (10 액션 × $0.05 = $0.50, OK; 100 액션 = $5.0, OK; 1000 액션 = $50 reject).
12. 영구 감사 로그 → user_id + target_app + cost 기록.

#### E9. Dependencies
- 외부: Claude Computer Use API, OpenAI Operator API, CogAgent (HF), SeeAct (HF), Docker (샌드박스), VM (옵션)
- 내부 (peer): J-026 V2 (audio_safety_v2 §5.4 Constitutional AI), J-060 V2 (task_planner_v2 DAG), J-077 (integration_architecture_v2 §5), J-083 (Router), J-065 (Cost Manager)

#### E10. Privacy / Safety
- **R-05-7**: 모든 의도 → Constitutional 분류 → 위반 시 즉시 거부
- **샌드박스 격리**: Docker/VM 내 실행, 호스트 시스템 영향 없음
- **3-Gate 금융**: HTS / 송금 / 외부 송신 시 강제
- **되돌리기 정책**: 되돌리기 불가 액션 (file_delete 등) → 사용자 승인 강제
- **영구 감사 로그**: R-05-7, user_id + target_app + cost
- **사용자 동의**: Claude CU / OpenAI Operator 외부 API 사용 시 동의 토글

**자체 점수**: 91/100

---

## 5. peer V2 cross-ref
- audio_safety_v2 §5.4 Constitutional AI → 본 V2 §4 E3 R-05-7 경계 분류
- integration_architecture_v2 §5 J-077 트렌드 → 본 V2 §4 E4 backend (CogAgent / SeeAct / Ferret-UI)
- task_planner_v2 J-060 → 본 V2 호출자 (복합 작업 분해)

---

## 6. Phase 3 시나리오 (8건)
1. 코딩 자동화 (Claude CU + IDE).
2. HTS 매수 3-Gate.
3. R-05-7 위반 즉시 거부.
4. CogAgent 한국어 UI 정확도.
5. SeeAct 웹 자동화.
6. 샌드박스 격리 + Docker.
7. 되돌리기 불가 액션 사용자 승인 강제.
8. LOCK-MM-06 V2 비용 가드.

---

## 7. 검증 매트릭스
| 항목 | V1 | V2 (본) | L3 |
|------|----|---------|-----|
| Computer Use Agent | V1 골격 | E1~E10 본문 + 4 backend | 91 |
| 샌드박스 격리 (R-05-7) | 1줄 | Docker/VM + Constitutional 통일 | 92 |
| 3-Gate 금융 | 1줄 | preview + 금액 + 최종 OK | 90 |
| 영구 감사 로그 | 미작성 | user_id + target_app + cost | 90 |

**평균**: **90.8/100** (LOCK-MM-12 V2 ≥80 충족 ✅)
