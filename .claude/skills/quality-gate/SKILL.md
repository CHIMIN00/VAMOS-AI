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

---

## [SOT 2 확장] SOT 2 품질 게이트 파이프라인 (v2 추가)

> 기존 EA JSON quality-gate를 유지한 채, SOT 2 산출물에 대한 품질 게이트 체인을 추가합니다.

### SOT 2 품질 게이트 체인

```
/quality-gate sot2 {도메인}

  Step 1: /validate sot2 → SDV-1~SDV-7 + SSV-1~SSV-3
  Step 2: /sot2-cross-ref {도메인} → Layer 1~4 교차 참조 검증
  Step 3: /sot-conflict sot2-scan → 해당 도메인 충돌 탐지
  Step 4: /sot-check sot2 {항목} → LOCK 값 spot-check (상위 10건)
  Step 5: Final Verdict
```

### SOT 2 품질 등급

| 등급 | 기준 |
|------|------|
| **GOLD** | SDV 전 PASS + SSV 전 PASS + 교차참조 0 MISMATCH + LOCK 전 CONSISTENT |
| **SILVER** | SDV 전 PASS + SSV 1건 이하 WARN + 교차참조 2건 이하 WARNING |
| **BRONZE** | SDV 1건 이하 FAIL + 교차참조 5건 이하 WARNING |
| **REJECT** | SDV 2건 이상 FAIL 또는 LOCK MISMATCH 1건 이상 |

### 추가 명령어

- `/quality-gate sot2 {도메인}` → 특정 도메인 SOT 2 품질 판정
- `/quality-gate sot2-all` → 34개 도메인 전수 판정
- `/quality-gate sot2-summary` → 전체 등급 분포 요약

### 저장 위치
- `D:/VAMOS/docs/sot 2/_quality-gate/{도메인}_verdict.json`
