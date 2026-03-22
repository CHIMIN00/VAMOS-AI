---
name: delta-apply
description: SOT 수정사항(delta) 추적 및 적용. v13_sot_delta.json 기반으로 변경사항 상태 관리, SOT 파일 반영, 영향받는 EA/CM 재검증 트리거.
---

# VAMOS Delta 적용 스킬

> `/delta-apply [delta번호|status|all]` — SOT 수정사항 추적 및 적용

## 목적

Phase 0에서 발견한 불일치 수정사항(delta)을 SOT 파일에 적용하고,
영향 범위를 추적하여 관련 EA/CM의 재검증을 트리거합니다.

---

## Delta 소스

**Primary**: `D:/VAMOS/04. 구현단계/v13_results/phase0/v13_sot_delta.json`
- 20개 delta (12개 SOT 파일 대상)

**Secondary** (이전 버전 수정사항):
- `D:/VAMOS/04. 구현단계/v9_results/phase2/v9_phase2_ripple_map.md` (24개 FIX)
- `D:/VAMOS/04. 구현단계/v10_results/phase2/v10_phase_c_patches.json` (200개 TRUE_MISSING)
- `D:/VAMOS/04. 구현단계/v12/v12_results/phase2/v12_update_plan.md` (279개 수정)

---

## 실행 모드

### `/delta-apply status` — 현재 상태 확인

```
1. v13_sot_delta.json 읽기
2. 각 delta의 대상 SOT 파일 현재 hash 확인
3. 적용 상태 판정:
   - APPLIED: SOT에 이미 반영됨
   - PENDING: 미적용
   - CONFLICT: SOT가 변경되어 delta 내용과 충돌
   - OUTDATED: delta 자체가 더 이상 유효하지 않음
4. 상태 요약 테이블 출력
```

### `/delta-apply {번호}` — 특정 delta 적용

```
1. 해당 delta 내용 확인
2. 대상 SOT 파일 Read
3. 변경 위치(line) 확인 → 현재 내용과 비교
4. 사용자에게 변경 내용 표시 (before/after)
5. 사용자 승인 후 Edit tool로 적용
6. 영향받는 EA/CM 목록 출력
7. /integrity 실행 권장 메시지 표시
```

### `/delta-apply all` — 전체 미적용 delta 순차 적용

```
1. PENDING 상태인 delta 목록 추출
2. 의존성 순서로 정렬 (같은 파일 내 line 역순)
3. 각 delta를 순차 적용 (사용자 확인 후)
4. 적용 결과 JSON 저장
```

---

## 영향 범위 추적

delta 적용 후 자동으로 계산:

```json
{
  "delta_id": "D-01",
  "target_sot": "D2.0-07_Safety.md",
  "affected_eas": ["EA-07", "EA-12"],
  "affected_cms": ["CM-C7", "CM-C6"],
  "action_required": "EA-07, EA-12 재추출 또는 해당 항목 수정 필요"
}
```

## 출력

**상태 파일**: `v13_results/phase0/delta/v13_delta_status.json`
**적용 로그**: `v13_results/phase0/delta/v13_delta_apply_log.json`

## 주의사항

- delta 적용 전 반드시 SOT 파일의 현재 상태 확인
- 같은 파일에 여러 delta 적용 시 **line 번호 역순**으로 적용 (앞쪽 수정이 뒤쪽 line에 영향 주지 않도록)
- 적용 후 git diff로 변경 확인 권장
- CONFLICT 상태 delta는 수동 해결 필요