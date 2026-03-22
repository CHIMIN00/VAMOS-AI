# AI INVESTING 충돌 기록부

> **Status**: ACTIVE
> **버전**: v1.0
> **작성일**: 2026-03-22

---

## 충돌 해결 프로토콜 (계획서 §9 발췌)

### 충돌 유형별 해결

| 충돌 유형 | 판정 기준 | 조치 |
|----------|----------|------|
| **sot 2/ ↔ LOCK/FREEZE** | LOCK이 절대 우선 | sot 2/ 즉시 수정. CONFLICT_LOG에 기록 |
| **sot 2/ ↔ SPEC 비-LOCK** | sot 2/가 상세 정본 | SPEC을 요약으로 축소 또는 리디렉트. 정본 소유자가 결정 |
| **sot 2/ 파일 간 중복** | canonical_owner_table 기준 | 정본 소유자 파일에 상세 유지, 나머지 `> 참조:` 링크로 교체 |
| **sot 2/ ↔ PART2 Phase** | PART2가 Phase 정본 | sot 2/에서 Phase 정보 삭제 |
| **sot 2/ ↔ STEP7-I** | sot 2/가 상세 정본 | step7i_mapping.md에 ABSORBED 마킹 |

### 충돌 기록 형식

```
| 날짜 | 충돌 유형 | 파일 A | 파일 B | 내용 | 판정 | 조치 완료 |
```

---

## 충돌 기록

| 날짜 | 충돌 유형 | 파일 A | 파일 B | 내용 | 판정 | 조치 완료 |
|------|----------|--------|--------|------|------|----------|
| 2026-03-22 | LOCK 위반 (참조 오류) | PART2 line 2549 (`D2.0-01 §5.9 = AI Investing 정본`) | D2.0-01 §5.9 (실제: A-Series Multi-Brain) | PART2가 D2.0-01 §5.9를 AI Investing 정본으로 잘못 참조 | D2.0-03 §1+§3.3 + VAMOS_AI_INVESTING_SPEC이 정본 | ✅ Phase 0-1에서 정정 완료 |
