# PHASE4-DEC-002 (P4-0 ⑧): CostGate 임계 체계 — 게이트 80/100(LOCK) + 경보 70/85/95 병존, config 키 분리

> **결정일**: 2026-06-12 (P4-0) · **포맷**: A6 · **우선순위**: Must · **출처**: P4-PRE A-02 (HIGH)

## 결정

**2체계 병존을 공식 설계로 확정하고 config 키를 역할별로 분리한다.**

### 체계 1 — 게이트 집행 (DEC-005 LOCK, 판정·차단)
```toml
[cost]
warn_threshold = 80     # force_mini 다운시프트 시작 (OWNER 승인 조정 가능)
block_threshold = 100   # deny 차단 (LOCK — 변경 불가)
```
- **D13 LOCK 20키 분모에 이미 포함**: `scripts/check_config_lock.py` L28-29가 `cost.warn_threshold=80`/`cost.block_threshold=100`을 기대값으로 바인딩(Phase 2-4 기집행 자산) — PART2 템플릿의 70/95가 이 LOCK 키 이름을 점유한 것이 오류의 본질.
- D2.1-D7 §4.4 DownshiftSchema가 `warn_threshold_percent=80(LOCK)`/`block_threshold_percent=100(LOCK)`을 스키마 수준으로 명문화. EventTypeRegistry에 `ui.gate.cost.warning_80`/`ui.gate.cost.ceiling_100` 기존재.

### 체계 2 — 경보·완화 (P30-058, 통지 전용·차단 없음)
```toml
[cost]
alert_thresholds = [70, 85, 95]   # P30-058 3단계 경보 (비-LOCK): 70 경고 표시 / 85 알림+throttle / 95 사용자 알림
```
- `escalate_threshold` 단독 키는 폐지하고 경보 3값을 별도 키 `alert_thresholds`로 이전 — LOCK 키(warn/block)와 이름 충돌 제거.
- §6.12.8 비용 초과 대응 절차(70/85/95/100)는 이 경보 체계의 운영 절차로 기정합 — 95 단계의 "P2 일시 정지 대기"는 예고(대기)이며 차단 집행은 100(게이트)만 수행.

## 근거 (정본 라인)

DEC-005(D2.0-07 §4.2 L216 LOCK + LOCK Registry §3 "80 warn → 100 block") / check_config_lock.py L28-29(D13 분모) / D2.1-D7 §4.4 / PART2 §7.5.1 L6298(BLOCKER-11 "warn=80/block=100") / PLAN-3.0 P30-058(70/85/95 — 경보 원형). 두 체계 모두 정본 근거 보유 — 역할(집행 vs 통지)이 다르므로 병존이 유일한 무손실 정합.

## 기각 대안

- 단일화 80/100(경보 폐기) — P30-058 정본 삭제 유발 + 70% 조기 경고의 운영 가치 상실. 기각.
- 단일화 70/85/95(게이트 대체) — block=95는 "100% 차단선 LOCK 변경 불가"(DEC-005·D2.0-07 L2059-2060) 위반 + check_config_lock.py FAIL. 기각.

## 집행 (PART2 연쇄 — 본 세션, CRLF 보존)

1. 템플릿 2곳(L294-296·L470-472): `warn=70/escalate=85/block=95` → `warn_threshold=80(LOCK)·block_threshold=100(LOCK)·alert_thresholds=[70,85,95]`
2. L1097 V0-STEP-4 AI 프롬프트 CostGate 행: "70% warn, 85% escalate, 95% block" → 게이트 80/100 + 경보 70/85/95 역할 구분 표기
3. §6.12.8 표제 직하 1줄: 게이트 집행(DEC-005 LOCK)과 경보 체계(P30-058)의 관계 주석
4. §7.5.1 L6298: "유일 SOT" → "게이트 집행 SOT(경보 alert_thresholds는 P30-058 별도)" 한정 표기
5. L1009·L1063·L1192·L1489-1491(80/100 표기)은 기정합 — 무수정. config.v1.toml 실생성은 P4-1(4-5).
※ CostBudgetSchema(D2.1-D7 §4.3)에는 threshold 필드 자체가 없음(9필드: budget_id/mode/limits/used/forecast/actual/block_on_exceed) — PART2 L728 약기의 warn/escalate/block_threshold 표기는 SOT 불일치로 별도 정정(PHASE4-DEC-009 ※ 참조).
