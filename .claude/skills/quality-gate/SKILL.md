---
name: quality-gate
description: 3개 검증 스킬을 순차 실행하는 통합 품질 게이트. EA 추출 완료 후 한 번에 전체 검증 파이프라인을 실행. /validate → /audit → /sot-check 자동 체인.
---

# VAMOS v13 통합 품질 게이트

> `/quality-gate [파일경로|all]` — 전체 검증 파이프라인 1회 실행

## 파이프라인

```
Step 1: Layer A 결정론적 검증 (python 스크립트)
  │ FAIL → 중단, CRITICAL 목록 반환
  │ PASS ↓
Step 2: Layer B AI 의미적 검증 (/validate의 SV-1~SV-3)
  │ FAIL → 중단, 오류 목록 반환
  │ PASS ↓
Step 3: 적대적 감사 (/audit의 AD-1~AD-3)
  │ CONTAMINATED → 중단, 환각 목록 반환
  │ CLEAN/SUSPICIOUS ↓
Step 4: SOT 원본 대조 (/sot-check, 의심 항목만)
  │
  ↓
Step 5: 종합 판정
```

## 종합 판정 기준

| 판정 | 조건 |
|------|------|
| **GOLD** | Layer A PASS + Layer B PASS + CLEAN + 전체 MATCH |
| **SILVER** | Layer A PASS + Layer B PASS + SUSPICIOUS + SHIFTED ≤ 5 |
| **BRONZE** | Layer A PASS + WARNING만 있음 |
| **REJECT** | Layer A FAIL 또는 CONTAMINATED 또는 NOT_FOUND ≥ 1 |

## OrgForge 원칙 (A-4)

> 기반: OrgForge Framework (2026) — "결정론적 엔진이 ground truth를 유지하고, LLM은 표면 텍스트만 생성"

이 파이프라인은 OrgForge 철학을 체현합니다:

| OrgForge 원칙 | VAMOS /quality-gate 대응 |
|--------------|------------------------|
| 결정론적 엔진 = ground truth | Step 1: python 스크립트(DV-1~DV-9)가 PASS/FAIL |
| LLM = 표면 텍스트만 | Step 2-3: AI는 의미적 판단 + 적대적 감사만 |
| 엔진 판정은 절대적 | Step 1 FAIL → 이후 단계 진행 불가 |

**적용 규칙**:
1. GOLD/SILVER/BRONZE 판정에서 Layer A(결정론적) PASS는 필수 전제조건입니다
2. AI의 감사 결과(CLEAN/SUSPICIOUS)는 Layer A PASS 위에서만 의미를 갖습니다
3. 프로그램이 검증 가능한 항목을 AI에게 위임하지 않습니다

## 실행 방법

### $ARGUMENTS 가 파일 경로인 경우:

1. **Step 1**: Bash tool로 실행 (파일 유형에 따라 분기)
   ```bash
   # EA 파일인 경우:
   python "D:/VAMOS/.claude/hooks/deterministic_validator.py" "$ARGUMENTS"
   # CM 파일인 경우:
   python "D:/VAMOS/.claude/hooks/cm_validator.py" "$ARGUMENTS"
   ```

2. **Step 2**: PASS이면 해당 EA의 SOT 파일을 Read로 읽고 SV-1~SV-3 수행

3. **Step 3**: Agent tool로 적대적 감사 에이전트 실행 (별도 컨텍스트)
   - 프롬프트: "이 산출물이 틀렸다고 가정하고 근거를 찾아라"
   - 반드시 **별도 Agent**로 실행 (동일 모델 편향 W1 대응)

4. **Step 4**: SUSPICIOUS 항목만 SOT 대조

5. **Step 5**: 종합 결과 JSON 저장

### $ARGUMENTS 가 `all`인 경우:

- extraction/ 디렉토리의 모든 v13_EA*.json에 대해 **Agent tool로 병렬 실행**
- 각 EA를 별도 Agent로 투입 (최대 5개 동시)

## 산출물

**파일**: `v13_results/phase0/extraction/validation/{파일명}_quality_gate.json`

```json
{
  "gate_metadata": {
    "target": "v13_EA01_claude_md.json",
    "verdict": "GOLD|SILVER|BRONZE|REJECT",
    "pipeline": {
      "layer_a": "PASS",
      "layer_b": "PASS",
      "audit": "CLEAN",
      "sot_check": "ALL_MATCH"
    }
  },
  "action_required": []
}
```

## v6~v12 대비 개선점

| v6~v12 방식 | v13 + quality-gate |
|-------------|-------------------|
| AI가 추출 → AI가 검증 (100% AI) | **프로그램이 팩트체크(DV) → AI는 의미만 판단** |
| 단일 컨텍스트에서 생성+검증 | **별도 Agent로 분리 (편향 차단)** |
| 검증 결과도 AI가 자체 판단 | **결정론적 스크립트가 PASS/FAIL 판정** |
| 환각 여부를 AI가 판단 | **프로그램이 source_text를 파일에서 직접 grep** |
