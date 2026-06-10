# MUST_FIX_BACKLOG — 구현 전 필수 수정 (객관적·원본확인 결함)

> 2026-06-06 · TIER 3 재판정(워크플로 `w9gt6mb6z`, 36 도메인) · **READ-ONLY 보고**(정본 무수정)
> 심판=원본. 각 CL-C(HIGH/both)+GP-A(confident) finding을 **객관적 결함 / 주관적 설계선택 / 오탐**으로 분류, 객관분만 원본 재독 확인.

## 0. 요약
| 구분 | 수 |
|---|---|
| **확정 MUST-FIX (원본확인)** | **881** |
| ├ CRITICAL | 26 |
| ├ HIGH | 685 |
| └ MED | 170 |
| 미확인 후보(원본 재확인 필요) | 56 |
| 주관적 설계선택 → 사람 검토 | 620 |
| 오탐(원본 재독 시 기각) | 284 |

**카테고리**: SECURITY 115 · LOGIC 378 · CONTRACT 292 · DATA_LOSS 26 · CONCURRENCY 13 · MISSING_CRITICAL 57

> 우선순위: CRITICAL → SECURITY/DATA_LOSS/CONCURRENCY HIGH → LOGIC/CONTRACT HIGH → MED. 전체 항목·도메인별 그룹은 `MUST_FIX_BACKLOG.json`.

## A. CRITICAL (26) — 전수

1. **[CRITICAL/CONTRACT]** `0-0_Governance-Rules-Meta` — V0 비용 상한이 §1.5에서는 ₩0(로컬)으로 정의되지만, §3.2 GO/NO-GO 항목 #3에서는 'V0 비용 상한 = V1 동일', 항목 #14에서는 '비용 엔진 ₩40,000/월 하드코딩'으로 기재되어 동일 버전의 비용 기준이 정면 충돌한다.
   - 수정: V0 비용 상한을 단일 LOCK으로 확정하라. §1.5와 §3.2 #3/#14 중 하나를 정본으로 지정하고, 나머지를 DEPRECATE 처리한 후 config.v1.toml에 반영하라.
   - 근거: §1.5: '비용 상한 | ₩0 (로컬)' vs §3.2 #3: 'V0 비용 상한 = V1 동일 명시' and #14: '비용 엔진 ₩40,000/월 하드코딩'

2. **[CRITICAL/CONTRACT]** `0-0_Governance-Rules-Meta` — GOVERNANCE §1.2/§1.5는 V0=L1(수동), V1=L2(COPILOT)로 정의하나, 정본인 GLOSSARY_CROSS_DOMAIN §14는 L0=MANUAL, L1=SUPERVISED, L2=COPILOT로 정의하여 GOVERNANCE 기준이 정본 대비 1레벨 오프셋되어 있다.
   - 수정: GOVERNANCE §1.2/§1.5의 자율도 단계를 정본(GLOSSARY §14, 3-10 LOCK-AP)에 맞게 V0=L0(MANUAL), V1=L1(SUPERVISED)... 로 수정하거나, LOCK L1 값을 'L0'으로 수정하라.
   - 근거: GOVERNANCE L25: 'V0=L1(수동), V1=L2(COPILOT)' vs GLOSSARY L166: 'L0(MANUAL) → L1(SUPERVISED) → L2(COPILOT)'

3. **[CRITICAL/CONTRACT]** `2-1_Blue-Node-Architecture` — Permission Level definitions in 상세명세 §1.1 (NONE/READ_ONLY/EXECUTE/WRITE/CROSS_DOMAIN/ADMIN, Level 0-5) directly contradict LOCK-BN-02 canonical values (Level 0=읽기전용/1=생성/2=수정/3=실행/4=외부통신/5=금융). Same level number carries different semantics across the spec corpus, making permission enforcement ambiguous—e.g., Level 2 means EXECUTE in 상세명세 but 수정(Modify) per LOCK.
   - 수정: Replace 상세명세 §1.1 table with the LOCK-BN-02 canonical table (읽기전용/생성/수정/실행/외부통신/금융), or mark 상세명세 §1 as superseded by 01_permission-matrix/_index.md which correctly implements LOCK-BN-02.
   - 근거: | 1 | `READ_ONLY` | 읽기 전용 | 자기 도메인 데이터 읽기 | (상세명세 L29) vs LOCK-BN-02: Level 1 생성 (AUTHORITY_CHAIN.md L54)

4. **[CRITICAL/CONTRACT]** `6-9_Brain-Adapter-HAL` — BrainRequest is instantiated with fields domain, complexity, and payload (e.g. domain='general', complexity='medium', payload={...}) that do not exist in the P1-1 canonical schema, which defines only task_type, prompt, system_prompt, tier, max_tokens, temperature, cost_cap, timeout_ms, tools, metadata, trace_id with Config.extra='forbid'. These instantiations would raise ValidationError at runtime.
   - 수정: Remove domain, complexity, payload from BrainRequest calls in e2e_reasoning_integration.md and encode intent via the existing fields (task_type, metadata, system_prompt). Alternatively, if these fields are needed, add them to the canonical BrainRequest schema and update Config.extra accordingly.
   - 근거: class BrainRequest(BaseModel):\n    task_type: Literal[...]\n    prompt: str\n    ...\n    cost_cap: float = Field(..., ge=0.0)\n    ...\n    class Config: extra = \"forbid\"

5. **[CRITICAL/LOGIC]** `2-2_COND-Modules-Detail` — For explain_type='global', variable `instance` is never assigned, yet line 182 calls `model.predict(instance)` unconditionally, causing NameError at runtime. Additionally `base_value` and `plot` are only assigned on the SHAP-local or SHAP-global path respectively; the return statement at L175-184 references both unconditionally.
   - 수정: Initialize `instance=None`, `base_value=None`, `plot=None` before the conditional branches, and guard each use. Skip `model.predict(instance)` when `instance is None`.
   - 근거: RETURN ShapLimeResponse(..., prediction=model.predict(instance), ...)  # line 182, `instance` only set inside explain_type=='local' branches

6. **[CRITICAL/LOGIC]** `3-2_Multimodal-Processing` — clone_voice_v2 references bare name `voice_id` in the audit_log_insert call (line 214) and in VoiceCloneResultV2 return (line 220), but voice_id is never bound as a local variable. `uuid7()` is passed inline to `audioseal_embed(..., voice_id=uuid7())` at line 207 without assignment, causing NameError on every successful clone.
   - 수정: Assign `voice_id = uuid7()` before the `audioseal_embed` call and use that variable consistently.
   - 근거: watermarked_audio = audioseal_embed(cloned_audio, user_id=session.user_id, voice_id=uuid7())
...
"voice_id": voice_id, "duration_sec": len(cloned_audio) / 32000,

7. **[CRITICAL/LOGIC]** `3-2_Multimodal-Processing` — In clone_voice_v2, `emb_sample` is assigned only inside the `if req.speaker_challenge_audio:` branch (line 148), but `voiceprint_db_search(emb_sample, ...)` at line 156 is called unconditionally outside that branch. When `speaker_challenge_audio` is None, `emb_sample` is undefined, causing NameError.
   - 수정: Move the `voiceprint_db_search` call inside the `if req.speaker_challenge_audio:` block, or assign `emb_sample = await pyannote_embedding(req.sample_audio)` before the conditional.
   - 근거: if req.speaker_challenge_audio:
    emb_sample = await pyannote_embedding(req.sample_audio)
...
        other_match = await voiceprint_db_search(emb_sample, exclude_user=session.user_id)

8. **[CRITICAL/LOGIC]** `3-2_Multimodal-Processing` — `pcm` is assigned only inside the `if cfg.check_deepfake:` block (line 191 conditional). It is used unconditionally at line 235 `check_csam_audio_v2(pcm, ...)` and line 246 `chromaprint_fingerprint(pcm)` in CSAM and copyright checks. When check_deepfake=False, pcm is undefined — NameError crashes the safety pipeline.
   - 수정: Extract pcm from the audio track in a shared preprocessing step before any conditional block, or guard each use with an explicit `if pcm` check.
   - 근거: if analysis.transcript and req.audio_check:
    pcm = await ffmpeg_extract_pcm(req.video, sr=16000, ch=1)  # LOCK-MM-08
...
if not csam_detected and analysis.transcript and req.audio_check:
    audio_

9. **[CRITICAL/LOGIC]** `3-5_Education-Learning` — calculate_next_review() is declared as a synchronous `def` but contains `await self._schedule_cascade_review(dep_card_id)` at line 249. This is a Python SyntaxError/RuntimeError that makes the entire cascade review path non-functional.
   - 수정: Declare calculate_next_review as `async def` and ensure all callers await it, or move the cascade scheduling out to an async wrapper caller.
   - 근거: def calculate_next_review(self, card: EducationFlashCard, quality: int) -> ReviewSchedule: ... await self._schedule_cascade_review(dep_card_id)

10. **[CRITICAL/LOGIC]** `3-5_Education-Learning` — `HintSystem.get_hint` references `self.HINT_LEVELS_PENALTY[level]` at line 392, but only `HINT_LEVELS` dict is defined in the class (line 373). `HINT_LEVELS_PENALTY` is never declared anywhere, causing AttributeError at every hint invocation.
   - 수정: Define `HINT_LEVELS_PENALTY = {1: 0.0, 2: 0.1, 3: 0.2, 4: 0.25, 5: 0.3}` (or equivalent) in HintSystem, or rename the reference to `HINT_LEVELS`.
   - 근거: HINT_LEVELS = {1: '방향 제시...', ...} ... penalty=self.HINT_LEVELS_PENALTY[level]

11. **[CRITICAL/LOGIC]** `3-6_Health-Wellness-EmotionAI` — CrisisKeywordMatcher.__init__ initializes only self.dictionary and self.automaton, but match() accesses self.morpheme_analyzer (L205) which is never declared or injected. Any call to match() raises AttributeError, crashing Stage 1 of the life-safety crisis detection pipeline.
   - 수정: Inject a morpheme_analyzer dependency in __init__ and document the required interface, or remove the morpheme analysis step if unused.
   - 근거: morphemes = self.morpheme_analyzer.analyze(text) (L205) — __init__ only sets self.dictionary and self.automaton (L191-193)

12. **[CRITICAL/LOGIC]** `4-4_MLOps-LLMOps` — Confidence interval formula computes `mean_b - mean_a ± 1.96 * (p_value ** 0.5)`. Using sqrt(p_value) as a substitute for standard error is mathematically invalid — p_value is a probability, not variance.
   - 수정: Replace with correct CI: `effect ± 1.96 * sqrt(pooled_var/n_a + pooled_var/n_b)` where pooled_var is computed from the sample variances.
   - 근거: "confidence_interval": (mean_b - mean_a - 1.96 * (p_value ** 0.5), mean_b - mean_a + 1.96 * (p_value ** 0.5),)

13. **[CRITICAL/LOGIC]** `4-4_MLOps-LLMOps` — CanaryJudge.judge() promotes when p_value >= 0.05 (fail to reject H0), but a canary that is statistically significantly BETTER (p < 0.05 AND qod_mean >= baseline) falls through to WAIT — it can never be promoted under this logic.
   - 수정: Add a branch: `if p_value < 0.05 and canary_metrics.qod_mean >= baseline_metrics.qod_mean: return Decision.PROMOTE` before the WAIT return.
   - 근거: if len(canary_metrics.samples) >= self.min_samples and p_value >= 0.05:
            return Decision.PROMOTE
        return Decision.WAIT

14. **[CRITICAL/LOGIC]** `4-4_MLOps-LLMOps` — _mann_whitney_pass() is a placeholder that unconditionally returns True. Stage 1 (Canary) promotion is gated solely on this method per _judge_promotion, so any canary meeting dwell time and min_samples is auto-promoted with no statistical validation whatsoever.
   - 수정: Implement the Mann-Whitney U test using actual QoD/error sample arrays from StageMetrics, or block promotion when raw samples are unavailable (raise rather than return True).
   - 근거: def _mann_whitney_pass(self, canary: StageMetrics, baseline: StageMetrics, *, alpha: float) -> bool:
        ...
        # placeholder: 실제 구현은 raw 샘플 분포가 필요 (StageMetrics 확장)
        return True

15. **[CRITICAL/LOGIC]** `5-2_File-Context` — Routing gate at L48 (`if token_count <= 256_000`) catches the 200K–256K interval and returns v2_mla_offload before the V3 branch at L55 is ever reached. The §1.3 mapping table at L75 specifies 200K–256K must route to v3_ring_infini (≥80%), making the V3 path for this interval unreachable.
   - 수정: Evaluate the 200K–256K V3 condition (token_count > 200_000 and token_count <= 256_000 and gpu_available >= 2) before the V2 <= 256K branch, or restructure the gate to match the §1.3 mapping table priority order.
   - 근거: L48: `if token_count <= 256_000:` ... `return PhaseD0V3Decision(strategy="v2_mla_offload"...` / L55: `if token_count <= 1_000_000 and gpu_available >= 2:` ... `strategy="v3_ring_infini"` — the V3 bran

16. **[CRITICAL/LOGIC]** `6-9_Brain-Adapter-HAL` — ParallelExecutor.submit() pseudocode only does 'async with self.semaphore' then _execute — it never calls pending_queue.put(), never emits brain.parallel.queued event, and never measures queue_wait_ms. The fields pending_queue and active_tasks are declared but unused. PAR-2 scenario's expected queued event (brain.parallel.queued) and user_alert_sent=true are not realizable from this implementation.
   - 수정: Either (a) add explicit pending_queue.put() logic before semaphore acquisition and emit brain.parallel.queued on enqueue, or (b) remove the pending_queue declaration and the PAR-2 queued-event requirement and acknowledge that semaphore blocking is the sole queuing mechanism.
   - 근거: async def submit(self, request: BrainRequest) -> ConnectorResponse:\n        async with self.semaphore:  # 상한 초과 시 자동 대기 (큐잉)\n            slot_id = self._acquire_slot()

17. **[CRITICAL/MISSING_CRITICAL]** `3-6_Health-Wellness-EmotionAI` — UsagePatternAnalyzer.analyze() calls self._score_breaks(latest) and self._score_notifications(latest) at L185-186 and uses them in a weighted sum at L189, but neither method is defined anywhere in the class or file. Any invocation of analyze() raises AttributeError.
   - 수정: Implement _score_breaks and _score_notifications with documented scoring logic, or remove the calls and adjust the weighted sum.
   - 근거: break_score = self._score_breaks(latest) / notif_score = self._score_notifications(latest) (L185-186) — no def _score_breaks or _score_notifications found in file

18. **[CRITICAL/SECURITY]** `2-1_Blue-Node-Architecture` — DynamicPermissionAdjuster in 상세명세 §1.3 applies `adjustments.append(+1)` when trust_score>0.9, enabling runtime privilege escalation (e.g., base_level=4 → effective=5=ADMIN). LOCK-BN-17 mandates 'Only Stricter' direction; the canonical 01_permission-matrix/_index.md §5.2 explicitly enforces downward-only adjustment (`min(0, total_adjustment)`). The 상세명세 code contradicts both.
   - 수정: Remove `adjustments.append(+1)` from 상세명세 §1.3. Any upward permission change must route through 07 Gate approval. Align with 01_permission-matrix/_index.md RULES table (all deltas negative).
   - 근거: if context.trust_score > 0.9:
    adjustments.append(+1)  # 신뢰도 높으면 레벨 상향 (상세명세 L79)

19. **[CRITICAL/SECURITY]** `2-2_COND-Modules-Detail` — Neo4j password 'vamos_kg_2024' is hardcoded as a default value in Cond018Config at line 800.
   - 수정: Replace default with a SecretRef/environment variable reference (e.g., `neo4j_password: SecretRef = Field(default_factory=lambda: SecretRef('VAMOS_NEO4J_PASSWORD'))`). Never embed literal credentials.
   - 근거: neo4j_password: str = "vamos_kg_2024"  # line 800

20. **[CRITICAL/SECURITY]** `3-10_Agent-Protocol-Interoperability` — enforce() step 2 branches only on cell=='NO'. The §2.3 Autonomy×Permission table contains zero 'NO' cells (only YES/Ask/HITL). All 'Ask' and 'HITL' cells fall through to the allow path without triggering any user query or human-approval gate — Ask and HITL requirements are silently bypassed.
   - 수정: Add elif cell == 'Ask': trigger user_query_flow() and elif cell == 'HITL': return _hitl(req, reasons, 'PE-006', ...) branches before the allow path in enforce().
   - 근거: cell = LOOKUP[(agent_state.autonomy_level, req.required_permission)]
if cell == "NO":
    return _deny(req, reasons, "PE-002", penalty=0.20)
# [no else-if for Ask or HITL] ...
return PermissionDecisio

21. **[CRITICAL/SECURITY]** `3-2_Multimodal-Processing` — The deepfake weighted score formula (image×0.4 + audio×0.3 + lipsync×0.3) means a single-modality detection score of 1.0 can never exceed 0.4, which is below the 0.5 reject threshold. Integration test 2 in E8 explicitly confirms: 'image 0.8 → 0.32 → PASS'. A fully face-swapped video with no audio is never rejected.
   - 수정: Add a hard per-modality reject: if any individual score >= deepfake_threshold, trigger reject/manual_review regardless of weighted score.
   - 근거: deepfake_score = (max_image_dfake * 0.4 +
                 max_audio_dfake * 0.3 +
                 max_lipsync_dfake * 0.3)
...
Test 2: image 0.8 + audio 0.0 + lipsync 0.0 → (0.8×0.4 = 0.32) → PASS

22. **[CRITICAL/SECURITY]** `3-6_Health-Wellness-EmotionAI` — HumeAIClient.analyze() sends raw audio/video bytes to https://api.hume.ai/v0/batch/jobs, transmitting PRIVATE emotion data to an external third party. LOCK-HW-02 declares emotion data PRIVATE with external transfer 'absolutely prohibited' (local-only).
   - 수정: Remove Hume AI external call path or replace with a local-only model. Raw emotion/audio data must not leave the device per LOCK-HW-02.
   - 근거: async def analyze(self, data: bytes, modality: str) -> HumeEmotionResult:
    response = await self._api_call(f"/batch/jobs", data, modality) (L184-186)

23. **[CRITICAL/SECURITY]** `3-6_Health-Wellness-EmotionAI` — EmotionAIGlobalToggle.disable_all() calls self.crisis_detection.stop(), silently disabling the life-safety crisis detection path. R-09-2 declares crisis detection as '예외 없음' (no exceptions). Only a code comment warns; no user re-confirmation or retention gate exists.
   - 수정: Remove crisis_detection.stop() from disable_all(). Crisis detection must remain active regardless of the global emotion AI toggle, per R-09-2.
   - 근거: self.crisis_detection.stop()  # 주의: 위기 감지도 중단됨 (L390)

24. **[CRITICAL/SECURITY]** `6-3_Agent-Teams-PARL` — admin_decision() enforces P0 OWNER+ADMIN authorization via `assert is_owner_admin(admin_id)`. Python assert is stripped under -O/optimized build mode, entirely removing the authz guard for permanent marketplace removal.
   - 수정: Replace assert with an explicit conditional raise (e.g., `if not is_owner_admin(admin_id): raise PermissionError(...)`)
   - 근거: assert is_owner_admin(admin_id), "P0 인간 승인 필수 — OWNER+ADMIN만 가능"

25. **[CRITICAL/SECURITY]** `6-3_Agent-Teams-PARL` — _verify_gate_07 accepts any non-empty string as a valid Gate token (returns gate_token is not None and gate_token != ''), never contacting gate_07_endpoint or validating cryptographic authenticity. Any non-empty string such as 'x' bypasses LOCK-AT-005 gate enforcement.
   - 수정: Implement actual token verification by calling gate_07_endpoint and validating token authenticity/expiry; reject non-cryptographic bare strings.
   - 근거: return gate_token is not None and gate_token != ""

26. **[CRITICAL/SECURITY]** `6-3_Agent-Teams-PARL` — _check_gate_07 in CodingAgent is also a stub that returns True for any non-empty gate_token, never using gate_07_endpoint. LOCK-AT-005 gate is bypassed on all coding agent executions.
   - 수정: Implement real gate endpoint call and cryptographic token validation; raise GateViolation on invalid tokens.
   - 근거: # 실제 구현에서는 gate_07_endpoint로 토큰 검증
        return True

## B. SECURITY (HIGH/MED, 106) — 전수

- **[HIGH]** `1-2_Auxiliary-Modules` — WebAdapter sends the Tavily API key in the JSON request body (`json={'api_key': api_key, ...}`) rather than in an Authorization header, increasing key exposure surface in (`external_sources_v2.md`)
- **[HIGH]** `2-1_Blue-Node-Architecture` — MCPBlueNodeServer._create_handler hardcodes auth_token="" (empty string) in the VamosMessage passed to node_handle.execute(). The comment states 'Auth Gateway에서 주입' but t (`BLUE_NODE_ARCHITECTURE_상세명세.md`)
- **[HIGH]** `2-1_Blue-Node-Architecture` — The Node-to-Node block rule is specified as: detect violation when `source.node_type != 'core' AND target.node_type != 'core'`. This trusts self-declared node_type in the (`integration_test_core_bn.md`)
- **[HIGH]** `2-1_Blue-Node-Architecture` — MCPBridgeLayer.base_url validator accepts both http:// and https:// schemes. A comment notes 'dev/test 환경 호환을 위해 http 도 허용', but there is no environment flag or productio (`_index.md`)
- **[HIGH]** `2-2_COND-Modules-Detail` — request.memory_context.user_id is used directly as a memory namespace key (user_profile.id) across all memory tiers without any ownership or authorization check — enablin (`cond_017_memgpt_letta_memory.md`)
- **[HIGH]** `2-2_COND-Modules-Detail` — user_id from the request body is used directly to query personal memory (`memory_l0.search(request.user_id, ...)`) for knowledge_scope='personal' with no check that reque (`cond_089_knowledge_assistant.md`)
- **[HIGH]** `2-2_COND-Modules-Detail` — Config management module handles 'secret' writes (set/dynamic change) with no authorization check, no audit log, and no value validation in the algorithm. Permission is P (`cond_046_e038_config_management.md`)
- **[HIGH]** `2-2_COND-Modules-Detail` — Secret management module (get/set/rotate/audit) uses the same Permission Level P0 (always active) model as feature_flag — no RBAC, no PERMISSION_DENIED failure code, no e (`cond_051_e045_secret_management.md`)
- **[HIGH]** `2-2_COND-Modules-Detail` — Audit-log 'write' (declared as append-only, tamper-proof, compliance-critical) maps backend-unavailable to fallback FB_COND_SKIP — silently dropping audit events with no  (`cond_055_e049_audit_log.md`)
- **[HIGH]** `2-2_COND-Modules-Detail` — revoke at line 197 calls `token_store.blacklist_access(meta.access_jti, ...)` but `save_refresh` at line 151 never persists the access token's jti — the field `meta.acces (`cond_036_e025_auth_token_mgmt.md`)
- **[HIGH]** `3-10_Agent-Protocol-Interoperability` — event_bus.md §9 structured log example includes 'error': {'stack': '...'} (raw stack trace). logging_spec.md §2 explicitly forbids raw stack traces and requires stack_has (`event_bus.md`)
- **[HIGH]** `3-2_Multimodal-Processing` — E5 error handling states 'Celebrity DB 타임아웃 → approved 유지 + flag celebrity_check_skipped'. A content-safety gate defaulting to 'approved' on timeout is a fail-open securi (`image_safety_metadata_v2.md`)
- **[HIGH]** `3-2_Multimodal-Processing` — J-017 E3 pre_generation pipeline applies user_constitution rules (step 3) without any validation or signature check on the attacker-supplied `user_constitution: Optional[ (`image_safety_metadata_v2.md`)
- **[HIGH]** `3-2_Multimodal-Processing` — J-010 E3 calls `pil_load` (lines 959-960) before `scan_polyglot` (line 976). Malicious SVG with embedded JS or EXIF polyglot payloads are parsed by Pillow before the secu (`vision_language_integration.md`)
- **[HIGH]** `3-2_Multimodal-Processing` — The semantic cache key contains only `method` and `query_embedding` — no `user_id`, `project_id`, or permission scope. One user's cached result can be returned to a diffe (`caching_optimization_v2.md`)
- **[HIGH]** `3-2_Multimodal-Processing` — AVRAGRequest and HybridSearchRequest include user_id, but the Qdrant search calls (visual_hits, text_hits, audio_hits) at lines 112-116 include no user_id filter. The pri (`multimodal_rag_v2.md`)
- **[HIGH]** `3-2_Multimodal-Processing` — auto_promote_to_l3=True promotes assets with importance >= 0.8 directly to L3 permanent storage without user consent. voice_chat.md (line 251-255) requires explicit user  (`memory_integration_v2.md`)
- **[HIGH]** `3-3_PKM-Knowledge-Management` — batch_maturity_check(user_id) accepts a user_id parameter but the Cypher query at line 240 is MATCH (n:KnowledgeNote) WHERE n.maturity <> 'archived' with no user_id filte (`maturity_tracking.md`)
- **[HIGH]** `3-3_PKM-Knowledge-Management` — can_access ABAC guard compares note.sensitivity > g.attribute_policy.max_sensitivity using raw string literals. String '>' compares lexicographically, not by sensitivity  (`knowledge_sharing.md`)
- **[HIGH]** `3-3_PKM-Knowledge-Management` — Notion bidirectional sync SYNC_CONFIG maps note.content/title/tags to Notion with no filter on privacy_level. Notes marked 'private' or 'sensitive' (per schema line 173)  (`PKM_KNOWLEDGE_MANAGEMENT_상세명세.md`)
- **[HIGH]** `3-4_Workflow-RPA` — HumanApprovalNode on_timeout allows value 'approve', which causes the execution logic to auto-approve on timeout (decision = node.config.on_timeout). This silently bypass (`dag_architecture.md`)
- **[HIGH]** `3-4_Workflow-RPA` — Version management rollback and merge API endpoints accept user_id/created_by but the implementation performs no authorization or ownership check. Any caller can rollback (`workflow_versioning.md`)
- **[HIGH]** `3-4_Workflow-RPA` — DatabaseConditionSource.query is a raw user-supplied SQL string. The comment '(SELECT만 허용)' is the only enforcement mechanism — there is no parameterized query, SQL AST v (`condition_trigger.md`)
- **[HIGH]** `3-4_Workflow-RPA` — _fetch_web_page and _fetch_api pass user-supplied source.url directly to httpx without any SSRF protection (no private IP range blocking, no scheme whitelist, no allowlis (`condition_trigger.md`)
- **[HIGH]** `3-4_Workflow-RPA` — WebhookTrigger auth field allows 'none' with no restriction, meaning the publicly-exposed /api/v1/webhooks/{workflow_id} endpoint can trigger workflow execution with zero (`WORKFLOW_RPA_상세명세.md`)
- **[HIGH]** `3-4_Workflow-RPA` — TriggerEvent payload includes 'headers': dict(request.headers) — the full headers dict including X-Webhook-Signature-256 and X-API-Key auth headers. These propagate into  (`webhook_trigger.md`)
- **[HIGH]** `3-4_Workflow-RPA` — VariableResolver passes env=context.environment_variables directly as a Jinja2 namespace, exposing all environment variables (API_KEY, DB_URL, etc.) to any template autho (`variable_secret_management.md`)
- **[HIGH]** `3-4_Workflow-RPA` — CodeNodeConfig has 'allowed_imports?: string[]' as optional with no default. If undefined means all imports are allowed (a common sandbox default), workflow authors could (`dag_architecture.md`)
- **[HIGH]** `3-4_Workflow-RPA` — SecretStore.store_secret() calls self._aesgcm.encrypt(nonce, plaintext, None) with None as associated_data (AAD). Without AAD binding the ciphertext to the secret name/ow (`variable_secret_management.md`)
- **[HIGH]** `3-5_Education-Learning` — Code-card output validation executes auto-generated/LLM-sourced code via `safe_execute(card.code_snippet, language, timeout=5s)` (line 267) with only a 5-second timeout a (`flashcard_auto_generation.md`)
- **[HIGH]** `3-5_Education-Learning` — The LLM prompt at line 248 injects raw `{source.content}` with no truncation, sanitization, or max-length guard. Attacker-controlled content (via the `url` content_source (`quiz_test_generation.md`)
- **[HIGH]** `3-5_Education-Learning` — BookSource accepts arbitrary `file_path` and `url` values (lines 38-40). `_parse_book` passes these directly to `_parse_pdf(source.file_path)` and `_parse_url(source.url) (`book_reading.md`)
- **[HIGH]** `3-6_Health-Wellness-EmotionAI` — PrivacyClassifier.classify() uses max(levels, key=lambda l: list(PrivacyLevel).index(l)) to pick the 'highest' grade. list(PrivacyLevel) ordering is PRIVATE=0, PROTECTED= (`ethics_framework.md`)
- **[HIGH]** `3-6_Health-Wellness-EmotionAI` — PrivacyGuard.check_access() hard-blocks HIGHEST at L535 ('절대 금지') before the allowlist check at L541, making the user_direct branch unreachable for HIGHEST data. Per §8 L (`health_data_privacy.md`)
- **[HIGH]** `3-6_Health-Wellness-EmotionAI` — can_aggregate_downgrade() allows HIGHEST → PROTECTED privacy level downgrade after aggregation. HIGHEST data is subject to 'absolutely prohibited' external transfer; once (`health_data_privacy.md`)
- **[HIGH]** `3-6_Health-Wellness-EmotionAI` — ManipulationGuard checks for literal meta-label substrings ('구매를 유도', '감정을 이용', 'FOMO 유발'). Real manipulative LLM output does not contain these meta-labels, so the guard  (`emotion_adaptive_response.md`)
- **[HIGH]** `3-6_Health-Wellness-EmotionAI` — NonDiagnosticFilter.PROHIBITED_TERMS includes '치료법' but not '치료' (L62). T-ETH-15 (L788) expects '치료' to be blocked, and SOT R-09-4 explicitly bans '치료' AND '진단'. The filt (`ethics_framework.md`)
- **[HIGH]** `3-6_Health-Wellness-EmotionAI` — ActivityDataStore._validate() raises `SecurityError` at L436 when data is not encrypted, but SecurityError is not a Python built-in and is not imported or defined in the  (`activity_exercise.md`)
- **[HIGH]** `3-7_Developer-Tools-API-SDK` — Plugin SDK architecture diagram (§6.1 L380) includes Node.js VM and Python Subprocess runtimes alongside WASM Sandbox. LOCK-DT-05 mandates WASM-only isolation. Node.js VM (`DEVELOPER_TOOLS_API_SDK_상세명세.md`)
- **[HIGH]** `3-7_Developer-Tools-API-SDK` — enforce_fs_capability() only validates against allowed_read_paths (L133) for all file operations. FSCapability.allowed_write_paths is defined (L107) but never checked, al (`wasm_sandbox.md`)
- **[HIGH]** `3-7_Developer-Tools-API-SDK` — DNS rebinding defense (§4.3) blocks only RFC1918 and IPv6 link-local. Loopback (127.0.0.0/8), IPv4 link-local (169.254/16), cloud metadata (169.254.169.254), and IPv6 ULA (`wasm_sandbox.md`)
- **[HIGH]** `3-7_Developer-Tools-API-SDK` — run_autonomous() sets deploy_approved=True without user interaction when safety_level=AUTO and auto_approve_deploy=True (L265), directly contradicting the stated policy ' (`autonomous_coding.md`)
- **[HIGH]** `3-8_Conversation-A2A` — `issue_delegation_token()` sets `expires_at=parent_token.expires_at` (L277) without checking remaining TTL. If the parent token expires in 1 second, the newly issued chil (`delegation_chain.md`)
- **[HIGH]** `3-8_Conversation-A2A` — `issue_delegation_token()` code only validates `max_tokens` against the parent budget (L256), but the §5.1 invariant states all three fields must satisfy child ≤ parent:  (`delegation_chain.md`)
- **[HIGH]** `3-8_Conversation-A2A` — Child token permissions are never validated to be a subset of parent permissions. `issue_delegation_token()` accepts any `permissions` list without checking `child.permis (`delegation_chain.md`)
- **[HIGH]** `3-8_Conversation-A2A` — Fallback behavior for EXP_A2A_AUTH_FAIL → FB_A2A_RETRY: after 3 failed retries, task is FORCE_COMPLETE'd. Authentication failure should terminate to `failed`/`canceled`;  (`CONVERSATION_A2A_구조화_종합계획서.md`)
- **[HIGH]** `4-1_Rust-Tauri-Infrastructure` — message_framing.md §3.1 shows the frontend providing trace_id, correlation_id, issued_at, and source in the Tauri invoke payload. rpc_protocol.md §4.2 states React UI has (`message_framing.md`)
- **[HIGH]** `4-1_Rust-Tauri-Infrastructure` — tauri_build_config.md §4.3 allowlist enables 'path: {all: true}', 'window: {all: true}', 'os: {all: true}' — blanket permissions far broader than the sandbox restriction  (`tauri_build_config.md`)
- **[HIGH]** `4-2_CICD-Pipeline` — macOS keychain is created and unlocked with the hardcoded literal password 'ci' on lines 124-128. Though the runner is ephemeral, any process on the runner during the bui (`WF-4_build-tauri.md`)
- **[HIGH]** `4-2_CICD-Pipeline` — The prod ArgoCD Application manifest (lines 114-118) has 'syncPolicy.automated:' block present with only 'selfHeal: false'. In ArgoCD, an 'automated:' block (even with se (`k8s_argocd_pipeline.md`)
- **[HIGH]** `4-2_CICD-Pipeline` — Lines 399-408 write POSTGRES_PASSWORD, QDRANT_API_KEY, NEO4J_AUTH, and OPENAI_API_KEY in plaintext to 'deploy/.env' in the runner workspace. No chmod, cleanup, or artifac (`docker_compose_pipeline.md`)
- **[HIGH]** `4-3_MCP-Server-Client` — F-2 file_write schema (the Phase 0 canonical schema) lacks the allowlist path-matching and path-traversal protection defined in A-6 (L167-168). F-2 also adds create_dirs: (`MCP_SERVER_CLIENT_상세명세.md`)
- **[HIGH]** `4-3_MCP-Server-Client` — Multiple external MCP server runtime commands use @latest (e.g., '@modelcontextprotocol/server-filesystem@latest') without version pinning or integrity hashing. marketpla (`development_servers.md`)
- **[HIGH]** `4-4_MLOps-LLMOps` — QualityGateConfig.evaluate() skips missing metrics with `continue`. If a block-severity metric (e.g., safety_violation_rate) is absent from the results dict, block_failur (`promptfoo_test_spec.md`)
- **[HIGH]** `5-2_File-Context` — The plan at §10.2 (L1688–1694) mandates PII detection gate, masking, KG pre-injection scan, and KV-cache masking before any text enters the pipeline. Phase A's A-1 throug (`phase_a_reception.md`)
- **[HIGH]** `5-3_v12-Additions-Detail` — PromptRegistryAPI spec defines rollback(), promote_winner(), register_prompt(), and resolve_for_agent() with no authentication, authorization, ownership, approval gate, o (`V12_ADDITIONS_상세명세.md`)
- **[HIGH]** `6-10_EXP-Modules-Detail` — A-7 Remote Executor accepts `RemoteTask(command: str, ...)` as a free-form string and executes it via SSH or K8s Job. No command allowlist, no execution sandbox boundary, (`EXP_MODULES_DETAIL_카탈로그.md`)
- **[HIGH]** `6-11_Hologram-Main-LLM` — authStore defines Role as 'OWNER'|'OPERATOR'|'VIEWER' but page_routing.md §3.1 uses 'member' and 'admin' as routing permission requirements (Workflow, NodeDetail: '로그인 +  (`page_routing.md`)
- **[HIGH]** `6-12_Event-Logging` — EscalationPayload §6 (L331) declares `original_request: Dict[str, Any]  # 원본 이벤트 envelope (마스킹 전)` — explicitly unmasked. But §2.2.6 (L106) mandates 'PII 직접 포함 금지'. failu (`event_schema.md`)
- **[HIGH]** `6-1_UI-UX-System` — UIExtensionSlot defines `render: () => ReactNode` (in-process React render) alongside `sandbox: boolean` claimed to represent Docker container isolation. A Docker contain (`extension_slots_v3.md`)
- **[HIGH]** `6-1_UI-UX-System` — ForcedBreakOverlay E6 specifies '키보드 Esc 차단 (강제 휴식 의도)', which violates WCAG 2.1 SC 2.1.2 (No Keyboard Trap). The document simultaneously claims LOCK L8 WCAG 2.1 AA compl (`v12_components.md`)
- **[HIGH]** `6-1_UI-UX-System` — RBACRouteGuard evaluates `RBAC_LEVEL[currentRole]` without null/undefined check. When currentRole is null or undefined (unauthenticated state), RBAC_LEVEL[undefined] retu (`rbac_access_control.md`)
- **[HIGH]** `6-1_UI-UX-System` — getVisibility() returns 'visible' when no RBAC rule is found for a componentId (`if (!rule) return 'visible'`). This fail-open default means any unregistered component —  (`rbac_access_control.md`)
- **[HIGH]** `6-1_UI-UX-System` — RBACGuard 'disabled' case wraps children in `<div aria-disabled='true'>` with CSS `pointer-events: none`. CSS pointer-events does not block keyboard events (Tab/Enter/Spa (`rbac_access_control.md`)
- **[HIGH]** `6-2_Security-Governance` — seccomp allowlist uses defaultAction=SCMP_ACT_ERRNO but only allows 19 syscalls, omitting syscalls required by Python3 at startup (rt_sigaction, rt_sigprocmask, getrandom (`docker_sandbox.md`)
- **[HIGH]** `6-2_Security-Governance` — DB init uses PRAGMA key = "x'{key_hex}'" (raw hex form). In SQLCipher, x'...' raw key notation bypasses PBKDF2 KDF entirely, so the kdf_iter=256000 set on line 80 (and ci (`sqlcipher_aes256.md`)
- **[HIGH]** `6-2_Security-Governance` — §3.3 entropy detection auto-blocks users for 90 days on a 2σ statistical signal (line 76: '자동 차단 + 90일 grace 차단'). This auto-blocking is a P2-level action (user suspensio (`anomaly_detection_v3.md`)
- **[HIGH]** `6-2_Security-Governance` — The allowed_roles schema enum includes 'VIEWER' (line 76). RBAC policy (rbac_4level.md) defines VIEWER as read-only with no execution rights. The validator only checks `t (`dec003_tool_allowlist.md`)
- **[HIGH]** `6-3_Agent-Teams-PARL` — _check_gate_07 in LeadAgent has identical stub logic (gate_token is not None and gate_token != ''), and is never called from delegate() or decide(). AT-005 '07 Gate 선행 통과 (`P1-01_lead_agent_definition.md`)
- **[HIGH]** `6-3_Agent-Teams-PARL` — HMAC signed_at timestamp is set after signing_payload_bytes() is computed, and signed_at is NOT included in the canonical signing payload. An attacker can modify signed_a (`message_bus.md`)
- **[HIGH]** `6-3_Agent-Teams-PARL` — _seen_nonces is a local in-memory dict per RedisMessageBus instance. In K8s multi-pod deployment (§12), each pod has its own nonce store, so a replayed message accepted o (`message_bus.md`)
- **[HIGH]** `6-3_Agent-Teams-PARL` — check_selfcheck() defaults selfcheck_passed to True when the context key is absent: `request.context.get('selfcheck_passed', True)`. This means SelfCheckGate always passe (`P1-08_gate_integration.md`)
- **[HIGH]** `6-3_Agent-Teams-PARL` — FORGED_TOKEN violation type is declared but verify_token only checks dict membership and expiry; _issue_token uses random uuid with no cryptographic signature. A forged t (`P1-08_gate_integration.md`)
- **[HIGH]** `6-3_Agent-Teams-PARL` — HMAC in register() is computed over the entire manifest object including manifest.signature itself. No canonical exclusion of the signature field is defined, so HMAC veri (`marketplace.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — Session filtering uses 'tags LIKE %"session:<id>"%' for both reads (§3.2) and mass-DELETE on session end (§4.2). A session_id containing '%', '_', or the substring '"sess (`L0_session_memory_crud.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — save() and get() build SQL via f-strings with the `table` argument interpolated directly: f"INSERT INTO {table} ..." and f"SELECT * FROM {table} WHERE...". The `table` pa (`managed_db_v3.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — The RLS policy 'tenant_isolation ON memory_records' has only a USING clause. In PostgreSQL, USING applies to SELECT/UPDATE/DELETE row filtering; without WITH CHECK, INSER (`multi_tenancy_v3.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — When policy_check_enabled=False, _call_d7_policy_check() returns 'PASS' unconditionally with no warning or escalation. A misconfigured production deployment (e.g., debug  (`dcl_basic.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — _resolve_conflict enforces L3 ApprovalGate only in the OVERWRITE branch when incoming.scope=='L3'. The USER_CHOICE branch (lines 583-592) returns 'incoming' with no L3 ga (`export_import.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — Export step [4]: when policy_decision='restrict' AND masked=False, EI_ERR_005 is issued as a warning but processing continues ('경고 + 계속'). The unmasked restrict record is (`export_import.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — §7.2 skips remap_project_id when source_project_id == target_project_id, but _validate_cross_project reads source_project_id from the export file header (line 642). An at (`export_import.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — LOCK-MR-018 confirmation hook: when _confirmation_hook is None and user_confirmation_default=True, _check_user_confirmation returns True (confirming storage) without any  (`dcl_basic.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — SemanticCache.put() has no policy_decision, sensitivity_level, or masked parameters. RAG Stage 6 calls semantic_cache.put() unconditionally. The spec declares deny-result (`semantic_cache.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — search() defaults policy_decision to 'allow' when missing from metadata (metadata.get('policy_decision', 'allow')). A corrupt or missing metadata entry is silently promot (`chroma_adapter.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — Tenant isolation validation relies on Python assert statements (assert tenant_id and project_id). Python asserts are stripped when running with optimization flags (-O), m (`multi_tenancy_v3.md`)
- **[HIGH]** `6-4_Memory-RAG-Storage` — Import OVERWRITE strategy proceeds when existing.policy_decision='deny' is overwritten by incoming.policy_decision!='deny'; only EI_WARN_001 (warning) is issued and impor (`export_import.md`)
- **[HIGH]** `6-5_SDAR-System` — attempt_circuit_breaker_restore() for P2 domain only checks `is_p2_domain and not human_approval_token` (line 211). If a token is present, requested_state=CLOSED is allow (`circuit_breaker_v3.md`)
- **[HIGH]** `6-7_RT-BNP-DCL` — When CL-G3 Bloom filter (Redis) is unavailable (G3_BLOOM_UNAVAILABLE), fast_gate.md §9.1 flowchart (L500) and exception table (L533) specify 'open-circuit: allow + penalt (`fast_gate.md`)
- **[HIGH]** `6-7_RT-BNP-DCL` — RetractionRequest (§2.1) and ConsumerAck (§2.2) schemas contain no authentication or authorization fields (no issuer_service, signature, auth_token, nonce, role, or repla (`retraction_protocol.md`)
- **[HIGH]** `6-8_Cloud-Library` — Fast Gate skips CL-G2 (Consistency) and CL-G4 (Final) and exposes content to users within 30 minutes, but no rollback, retraction, or notification procedure is defined fo (`gate_details.md`)
- **[HIGH]** `6-9_Brain-Adapter-HAL` — RoutingWeightUpdate schema accepted from external domain 4-4 carries no authentication, authorization, or integrity verification field — only trace_id. A spoofed or repla (`drift_routing_integration.md`)
- **[HIGH]** `6-9_Brain-Adapter-HAL` — The ENV variable VAMOS_ROUTING_MAX_CONCURRENT overrides routing.parallel.max_concurrent directly, allowing V1/V2 fixed limit of 3 and V3 Approval Gate to be bypassed by s (`P1-3_llm_router_v1_spec.md`)
- **[HIGH]** `6-9_Brain-Adapter-HAL` — LiteLLM proxy is exposed on host port 4000:4000 with API keys for Anthropic, OpenAI, and DeepSeek injected into the container environment. The deployment spec defines no  (`hal_v2_deployment.md`)
- **[HIGH]** `6-9_Brain-Adapter-HAL` — Redis is deployed with only maxmemory and eviction policy settings — no requirepass, no ACL, no TLS, no AOF/RDB persistence. Redis serves as the cost accumulation counter (`hal_v2_deployment.md`)
- **[HIGH]** `Ai-investing-detail` — get_index_constituents builds a query string by f-string interpolating index_name and as_of_date directly into a pandas/DB query expression without any escaping or valida (`survivorship_bias.md`)
- **[HIGH]** `Ai-investing-detail` — KIS broker order passes `account_no=client.token.appkey[:8]` — using a truncated API credential (appkey) as the account number. This is both a logic error (wrong account  (`execution_algorithms.md`)
- **[HIGH]** `Ai-investing-detail` — MAX_SINGLE_ORDER_USD=100_000 is compared against order_value = quantity * current_price without currency conversion. For KR_STOCK (KRW prices) and CRYPTO (USDT), the USD  (`order_safety.md`)
- **[HIGH]** `Ai-investing-detail` — manage_rules() has user_id defaulting to empty string and remove/toggle operations are performed on rule_id alone with no ownership verification. Any caller knowing a rul (`user_communication.md`)
- **[HIGH]** `Ai-investing-detail` — FX orders above $100K are declared to require P2 HITL approval in E9 LOCK (D2.0-07 I-19), but plan_fx_execution and FxExecutionPlan contain no approval_required flag, no  (`asset_class_execution.md`)
- **[MED]** `1-2_Auxiliary-Modules` — AR-L4 Emergency Kill Switch is delivered as a fire-and-forget event push (C-13) with no guaranteed-delivery, ACK, or retry; on failure only 'local queue 보존' (AUX-E005) —  (`interface_contracts.md`)
- **[MED]** `2-1_Blue-Node-Architecture` — PolicyResolver.resolve() accepts new policy parameters (not in global baseline) from domain/node scopes and logs MISSING_GLOBAL_BASELINE as INFO, then adds them to Resolv (`_index.md`)
- **[MED]** `3-3_PKM-Knowledge-Management` — handle_webhook processes NotionWebhookPayload (line 300) with no signature/HMAC verification step, despite the schema defining NOTION_WEBHOOK_SIGNATURE_INVALID (line 343) (`notion_sync.md`)
- **[MED]** `3-4_Workflow-RPA` — ConditionTrigger and EventTrigger pass user-supplied 'expected' or 'threshold' values directly to re.search/re.match with no timeout, RE2 safe-engine, or pattern length l (`condition_trigger.md`)
- **[MED]** `3-9_Business-Model-Strategy` — vamos_pricing_strategy.md §14 states 'Data Storage: 100% Local' and '당신의 데이터는 당신의 컴퓨터에만 존재합니다' as a core privacy guarantee. kpi_definitions.md §1.2 defines the MAU data s (`vamos_pricing_strategy.md`)
- **[MED]** `6-10_EXP-Modules-Detail` — EVX-4 Thought Buffer accepts `DebugRequest(trace_id: str, depth: int)` and returns a `ThoughtGraph` containing full reasoning chains. No access control, authentication ga (`EXP_MODULES_DETAIL_카탈로그.md`)
- **[MED]** `6-8_Cloud-Library` — The EvolutionApproval schema declares approver as Optional[str] = None, meaning MAJOR_APPROVE changes (including gate_threshold_change and lock_value_change) can be appli (`v12_extensions.md`)

## C. DATA_LOSS (26) · CONCURRENCY (13) — 전수

- **[HIGH/DATA_LOSS]** `1-2_Auxiliary-Modules` — `KNOWN_AUX_CODES` contains only 10 V1 codes; all V2 series codes (AUX-E-ENV-*, AUX-E-STT-*, AUX-E-PII-*, etc.) are in comments only, so `_is_known_code()` returns False f
- **[HIGH/DATA_LOSS]** `2-2_COND-Modules-Detail` — The update path (line ~406-427) soft-deletes existing graph elements then re-ingests; if re-ingestion fails it warns and CONTINUEs — leaving elements in soft-deleted stat
- **[HIGH/DATA_LOSS]** `3-10_Agent-Protocol-Interoperability` — ConfigReloader.reload() overwrites self._current = new_cfg (line 318) before calling request_readiness_recheck(). §7.4 specifies 'fail → 이전 config 즉시 rollback', but no re
- **[HIGH/DATA_LOSS]** `3-10_Agent-Protocol-Interoperability` — Dedup LRU cache holds 8,192 entries while the ring buffer holds 10,000. Under a burst of >8,192 distinct event keys, older entries evict from the LRU; if the ring buffer 
- **[HIGH/DATA_LOSS]** `3-3_PKM-Knowledge-Management` — create_version SUPERSEDES edge uses from_id=note.id AND to_id=note.id (same UUID) to represent 'previous snapshot'. A self-loop edge cannot distinguish version A from ver
- **[HIGH/DATA_LOSS]** `3-4_Workflow-RPA` — rollback() checks for active executions and logs a warning but does NOT stop them or block the rollback. Active runs continue executing the old version definition while t
- **[HIGH/DATA_LOSS]** `3-4_Workflow-RPA` — ConditionTrigger fire_policy='once' marks state as fired and disables the trigger (config.enabled=False) BEFORE publishing the trigger event via EventBus. If publish fail
- **[HIGH/DATA_LOSS]** `3-7_Developer-Tools-API-SDK` — §7.2 idempotency handler records delivery via redis.sadd before process_event (L299). A crash after sadd but before processing marks the event as delivered but never actu
- **[HIGH/DATA_LOSS]** `3-8_Conversation-A2A` — SSE backpressure policy (§4.3 L163) silently drops `artifact_chunk` events when the in-memory queue is full, only incrementing a counter. artifact_chunking.md defines NAC
- **[HIGH/DATA_LOSS]** `4-4_MLOps-LLMOps` — rollback() mutates in-memory state (current.status='deprecated', target.status='production') then performs registry updates, git commit, and history record sequentially w
- **[HIGH/DATA_LOSS]** `5-1_Benchmark-Evaluation` — insert_run() atomicity spec (L1318): Parquet is written first, then SQLite INSERT; on SQLite failure the Parquet file is unlinked. But if the process crashes between the 
- **[HIGH/DATA_LOSS]** `6-11_Hologram-Main-LLM` — SeqTracker.onChunk(): after handleGap(resync) completes, the OOO-buffered chunk that originally triggered the gap (stored at buffer.set(chunk.seq, chunk) L702) is never d
- **[HIGH/DATA_LOSS]** `6-12_Event-Logging` — EL_EVT_PAYLOAD_NULL auto-corrects `payload=null` to `payload={}` (L282, §5.1 table '1회 한정'). However §2.2.6 (L103) and §8 anti-patterns explicitly prohibit `payload: null
- **[HIGH/DATA_LOSS]** `6-13_Operations` — V0-V1 data scope is defined as SQLite + Chroma + JSONL (line 13), but the entire backup and recovery procedure covers only SQLite (.backup command) and git restore. There
- **[HIGH/DATA_LOSS]** `6-13_Operations` — V2 data scope includes Neo4j (line 14), but the V2 cron schedule covers only pg_dump and Qdrant snapshot. The recovery test table also lists only pg_restore and Qdrant. N
- **[HIGH/DATA_LOSS]** `6-13_Operations` — PostgreSQL failover is specified as 'SQLite 임시 전환 (읽기 전용)' in the Part2 table (line 17), but the SOT2 section simultaneously defines write buffering to a memory queue: 'n
- **[HIGH/DATA_LOSS]** `6-3_Agent-Teams-PARL` — Phase 3 overflow handling: when gate_ok is False for an overflow task, the task is silently dropped — not added to failed_summaries, not escalated, not counted in any res
- **[HIGH/DATA_LOSS]** `6-3_Agent-Teams-PARL` — replay_trace() mutates cp.status = CheckpointStatus.REPLAYING on the stored CheckpointRecord objects in self._traces (not on copies). Subsequent get_latest_checkpoint() o
- **[HIGH/DATA_LOSS]** `6-3_Agent-Teams-PARL` — publish() inserts the message into asyncio.Queue (await queue.put) AND immediately invokes subscriber callbacks. No consumer ever drains the queue. The queue accumulates 
- **[HIGH/DATA_LOSS]** `6-3_Agent-Teams-PARL` — scan_file() PARSE_ERROR early returns (OSError/UnicodeDecodeError at L401-406, SyntaxError at L411-416) return a FileScanResult without appending to self._file_results or
- **[HIGH/DATA_LOSS]** `6-4_Memory-RAG-Storage` — The AWS S3 lifecycle rule 'L4-Erasure' sets Expiration {Days: 1}, deleting GDPR-tagged objects 1 day after tagging. §9.2 specifies a 1-month erasure grace period for resp
- **[HIGH/DATA_LOSS]** `6-4_Memory-RAG-Storage` — add_edge stores edges in nx.DiGraph via G.add_edge(source, target, ...). DiGraph permits only ONE edge per (u,v) pair; a second edge between the same nodes with a differe
- **[HIGH/DATA_LOSS]** `6-4_Memory-RAG-Storage` — In upsert(), _sync_bm25_index() is called unguarded after collection.upsert() completes. If _sync_bm25_index raises, the exception propagates to the caller making the ent
- **[HIGH/DATA_LOSS]** `Ai-investing-detail` — update_volume_profile_incremental hardcodes elapsed_hours=1.0 with a comment that the real value should come from outside, but no such parameter exists in the function si
- **[HIGH/DATA_LOSS]** `Ai-investing-detail` — _article_history is initialized to an empty DataFrame at __init__ and is never written to anywhere in the class. compute_impact_score reads it to compute repetition_count
- **[MED/DATA_LOSS]** `5-2_File-Context` — §10.3 emergency purge procedure (L1696–1705) has no rollback or recovery step. After soft-delete of KG nodes (step 3), if the purge is a false positive, there is no resto
- **[HIGH/CONCURRENCY]** `3-3_PKM-Knowledge-Management` — PreloadQueue.push() mutates existing.neg_priority in-place (line 245) without calling heapq.heapify() or using any sift operation. This corrupts the min-heap invariant so
- **[HIGH/CONCURRENCY]** `3-3_PKM-Knowledge-Management` — The while loop at line 115 (while await registry.exists(candidate)) has no maximum retry limit, but E7 error table states 'max 5 retries'. The constraint is never enforce
- **[HIGH/CONCURRENCY]** `3-3_PKM-Knowledge-Management` — The exists() check and register() call in ID allocation are not atomic (lines 115-121): a concurrent coroutine can register the same candidate ID between these two calls,
- **[HIGH/CONCURRENCY]** `3-4_Workflow-RPA` — Redis debounce _is_debounced performs GET then SETEX as two separate operations — not atomic. Concurrent events can all pass the GET check before any SETEX is written, al
- **[HIGH/CONCURRENCY]** `3-5_Education-Learning` — Optimistic-lock comment `// version conflict → retry` at line 269 is purely textual with no retry loop, backoff, or conflict-detection logic in `update_profile` or `updat
- **[HIGH/CONCURRENCY]** `3-6_Health-Wellness-EmotionAI` — EmpathyDialogueEngine stores a single shared _context (DialogueContext) as an instance field. When one engine instance serves multiple concurrent users/sessions, recent_e
- **[HIGH/CONCURRENCY]** `4-4_MLOps-LLMOps` — rollback(), tag(), and promote() have no concurrency control (no lock/mutex on prompt_name). §8 defines ROLLBACK_ACTIVE_CONFLICT ('롤백 중 동시 태깅 충돌'). Concurrent invocations
- **[HIGH/CONCURRENCY]** `6-3_Agent-Teams-PARL` — _active_tokens dict and _violation_log list are mutated by issue/verify/revoke/log with no asyncio.Lock or threading.Lock. IT-11 test confirms concurrent 10-agent gate ve
- **[HIGH/CONCURRENCY]** `6-3_Agent-Teams-PARL` — record_edge() mutates shared _adjacency, _edges, _visited, _message_patterns dicts with no asyncio.Lock or threading.Lock. ParallelDispatcher (P1-05) is explicitly expect
- **[HIGH/CONCURRENCY]** `6-9_Brain-Adapter-HAL` — select() is declared as a synchronous abstract method (`def select(...)`) in the BaseLLMRouter ABC, but §4.6 specifies that the router maintains an internal `asyncio.Sema
- **[HIGH/CONCURRENCY]** `6-9_Brain-Adapter-HAL` — Router state S6 acquires a parallel slot and returns (adapter, decision) to the caller, who then calls invoke() and separately releases the slot. If the caller raises an 
- **[MED/CONCURRENCY]** `3-9_Business-Model-Strategy` — The budget hardcap state machine has no defined atomicity policy for concurrent requests at the 95% threshold. A user's 'continue' action at 95% allows additional request
- **[MED/CONCURRENCY]** `6-4_Memory-RAG-Storage` — The update path reads the existing record (to get current version), increments version, then blindly executes UPDATE with no WHERE version=old_version check. Concurrent u

## D. 도메인 × 카테고리 매트릭스 (확정 MUST-FIX)

| 도메인 | SEC | LOGIC | CONTRACT | DATA | CONC | MISS | 계 |
|---|--:|--:|--:|--:|--:|--:|--:|
| 3-6_Health-Wellness-EmotionAI | 8 | 21 | 7 | 0 | 1 | 5 | **42** |
| 2-2_COND-Modules-Detail | 7 | 29 | 2 | 1 | 0 | 2 | **41** |
| 3-3_PKM-Knowledge-Management | 4 | 16 | 13 | 1 | 3 | 2 | **39** |
| 3-4_Workflow-RPA | 10 | 13 | 10 | 2 | 1 | 3 | **39** |
| 6-4_Memory-RAG-Storage | 12 | 12 | 6 | 3 | 1 | 5 | **39** |
| 6-3_Agent-Teams-PARL | 9 | 17 | 2 | 4 | 2 | 4 | **38** |
| 3-10_Agent-Protocol-Interoperability | 2 | 10 | 18 | 2 | 0 | 1 | **33** |
| 3-8_Conversation-A2A | 4 | 3 | 21 | 1 | 0 | 1 | **30** |
| 1-2_Auxiliary-Modules | 2 | 13 | 10 | 1 | 0 | 3 | **29** |
| 5-2_File-Context | 1 | 18 | 7 | 1 | 0 | 2 | **29** |
| Ai-investing-detail | 5 | 15 | 2 | 2 | 0 | 5 | **29** |
| 3-2_Multimodal-Processing | 7 | 19 | 2 | 0 | 0 | 0 | **28** |
| 4-3_MCP-Server-Client | 2 | 11 | 15 | 0 | 0 | 0 | **28** |
| 3-7_Developer-Tools-API-SDK | 4 | 9 | 12 | 1 | 0 | 1 | **27** |
| 6-2_Security-Governance | 4 | 13 | 9 | 0 | 0 | 0 | **26** |
| 4-1_Rust-Tauri-Infrastructure | 2 | 10 | 12 | 0 | 0 | 1 | **25** |
| 6-11_Hologram-Main-LLM | 1 | 11 | 11 | 1 | 0 | 1 | **25** |
| 6-5_SDAR-System | 1 | 10 | 13 | 0 | 0 | 1 | **25** |
| 3-5_Education-Learning | 3 | 19 | 0 | 0 | 1 | 1 | **24** |
| 5-1_Benchmark-Evaluation | 0 | 7 | 12 | 1 | 0 | 3 | **23** |
| 1-1_Verifier-Reasoning-Engines | 0 | 8 | 12 | 0 | 0 | 1 | **21** |
| 4-2_CICD-Pipeline | 3 | 8 | 7 | 0 | 0 | 3 | **21** |
| 6-1_UI-UX-System | 5 | 5 | 11 | 0 | 0 | 0 | **21** |
| 6-6_Self-Evolution-System | 0 | 11 | 9 | 0 | 0 | 0 | **20** |
| 3-9_Business-Model-Strategy | 1 | 12 | 5 | 0 | 1 | 0 | **19** |
| 4-4_MLOps-LLMOps | 1 | 10 | 4 | 1 | 1 | 2 | **19** |
| 6-12_Event-Logging | 1 | 11 | 5 | 1 | 0 | 1 | **19** |
| 6-9_Brain-Adapter-HAL | 4 | 5 | 8 | 0 | 2 | 0 | **19** |
| 6-8_Cloud-Library | 2 | 7 | 7 | 0 | 0 | 2 | **18** |
| 5-3_v12-Additions-Detail | 1 | 6 | 9 | 0 | 0 | 1 | **17** |
| 2-1_Blue-Node-Architecture | 5 | 2 | 6 | 0 | 0 | 3 | **16** |
| 6-7_RT-BNP-DCL | 2 | 5 | 6 | 0 | 0 | 1 | **14** |
| 6-13_Operations | 0 | 7 | 3 | 3 | 0 | 0 | **13** |
| 0-0_Governance-Rules-Meta | 0 | 3 | 7 | 0 | 0 | 0 | **10** |
| 6-10_EXP-Modules-Detail | 2 | 0 | 6 | 0 | 0 | 1 | **9** |
| 5-4_v23-Extension-Items | 0 | 2 | 3 | 0 | 0 | 1 | **6** |

## E. LOGIC(378)·CONTRACT(292)·MISSING_CRITICAL(57) HIGH/MED
> 수가 많아(개별 727건) 본문 생략 — 전수는 `MUST_FIX_BACKLOG.json › confirmed_by_domain`. 도메인별 분포는 §D.

## F. 한계 (R16)
- **확정 %d건은 원본 재독으로 객관 결함임을 확인**(보안/로직/데이터손실/계약모순/동시성/필수컴포넌트). 그러나 구현 맥락에 따라 일부는 의도된 단순화일 수 있어, 적용 전 도메인 오너 확인 권장.
- **미확인 %d건**: 에이전트가 원본에서 확정하지 못함 → 재확인 대상(기각 아님).
- **주관 %d건**은 설계 선택(SLA 값·아키텍처·효율) → 단일 정답 없음, 사람 결정(본 백로그 제외).
- 이 작업은 SOT 정본을 수정하지 않았다.