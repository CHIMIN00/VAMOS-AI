---
name: integrity
description: SOT 68개 파일 무결성 모니터. 현재 hash vs EA 기록 hash 비교, 변경된 파일/영향받는 EA/CM 목록 출력, 재추출 필요 범위 사전 안내.
---

# VAMOS SOT 무결성 모니터 스킬

> `/integrity [파일명|all|impact]` — SOT 파일 변경 감지 및 영향 범위 분석

## 목적

SOT 파일이 수정되면 기존 EA의 source_line, source_text가 무효화됩니다.
이 스킬은 SOT 변경을 사전에 감지하고 영향 범위를 안내합니다.

---

## 동작 원리

```
EA JSON의 metadata.source_file_hashes (추출 시점 SHA-256)
  vs
현재 SOT 파일의 SHA-256
  → 불일치 시 해당 EA 무효화
```

---

## 실행 모드

### `/integrity all` — 전체 SOT 무결성 체크

```
1. v13_results/phase0/extraction/v13_EA*.json 전체 로딩
   ↓
2. 각 EA의 source_file_hashes 추출
   ↓
3. 현재 SOT 파일의 hash 계산:
   python -c "
   import hashlib, sys
   print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())
   " "D:/VAMOS/docs/sot/{파일명}"
   ↓
4. 비교 결과:

   | SOT 파일 | EA | 추출시 hash | 현재 hash | 상태 |
   |---------|-----|-----------|----------|------|
   | D2.0-01 | EA-02 | abc123 | abc123 | OK |
   | D2.0-07 | EA-07 | def456 | xyz789 | CHANGED |
   ...
   ↓
5. CHANGED 파일에 대해:
   - git diff로 변경 내용 확인
   - 변경된 줄 범위 파악
   - 해당 줄에 매핑된 EA item_id 특정
```

### `/integrity {파일명}` — 특정 SOT 파일 체크

```
1. 해당 파일의 hash 계산
2. 관련 EA 찾기 (source_files에 포함된 EA)
3. hash 비교
4. 변경 시 영향받는 항목 상세 출력
```

### `/integrity impact` — 영향 범위 분석

```
1. CHANGED 상태인 SOT 파일 목록
2. 각 파일에 대해:
   - 영향받는 EA 목록
   - 영향받는 CM 목록 (해당 EA를 참조하는 CM)
   - 재추출 필요 여부 판정:
     * 줄 삽입/삭제 → source_line 전체 shift → 재추출 필수
     * 내용 수정 → 해당 item만 업데이트 가능
     * 줄 끝 공백 등 무의미 변경 → 무시 가능
3. 권장 조치:
   - FULL_RE_EXTRACT: 줄 번호 변경 → /extract 재실행
   - PARTIAL_UPDATE: 특정 item만 수정
   - NO_ACTION: 무의미한 변경
```

---

## 출력 형식

```json
{
  "check_timestamp": "2026-03-18T...",
  "sot_total": 68,
  "changed": 3,
  "unchanged": 65,
  "details": [
    {
      "sot_file": "D2.0-07_Safety_Cost_Approval.md",
      "status": "CHANGED",
      "hash_at_extraction": "def456...",
      "hash_current": "xyz789...",
      "affected_eas": ["EA-07"],
      "affected_cms": ["CM-C6", "CM-C7"],
      "affected_items": [12, 15, 23],
      "recommendation": "FULL_RE_EXTRACT",
      "git_diff_summary": "+3 lines, -1 line, modified lines: 145, 267, 389"
    }
  ]
}
```

## 저장 위치

`v13_results/phase0/integrity/v13_integrity_check_{timestamp}.json`

## 사용 시점

- SOT 파일 수정 후 (delta 적용 후)
- Phase 재실행 전 (/phase-run 실행 전)
- 정기적 무결성 확인
- `/extract` 실행 전 변경 여부 사전 확인