---
name: report
description: Phase별 종합 리포트 생성. 검증 결과 수집, 통계 계산(GOLD/SILVER/BRONZE/REJECT), 미해결 불일치 목록, v6~v12 대비 개선/악화 분석, Markdown verdict 문서 자동 생성.
---

# VAMOS 종합 리포트 스킬

> `/report [phase번호|summary|compare]` — 검증 결과 종합 리포트 생성

## 목적

지정 Phase의 모든 검증 결과를 수집하여 일관된 형식의
판정 문서를 자동 생성합니다.

---

## 실행 모드

### `/report {N}` — 특정 Phase 리포트

```
1. v13_results/phase{N}/ 디렉토리 스캔
   ↓
2. 검증 결과 수집:
   - _dv_result.json (Layer A 결과)
   - _sv_result.json (Layer B 결과)
   - _audit.json (적대적 감사 결과)
   - _sot_check.json (SOT 대조 결과)
   - _quality_gate.json (품질 게이트 결과)
   ↓
3. 통계 계산:
   - 총 검증 항목 수
   - PASS/FAIL 비율
   - CRITICAL/WARNING/INFO 분포
   - GOLD/SILVER/BRONZE/REJECT 분포
   ↓
4. 미해결 항목 목록:
   - FAIL 항목 상세
   - INCONSISTENT 항목 상세
   - SUSPICIOUS 항목 상세
   ↓
5. Markdown 리포트 생성
```

### `/report summary` — 전체 Phase 요약

```
1. Phase 0 ~ 현재까지의 모든 verdict 수집
2. Phase별 요약 테이블:

   | Phase | 대상 | 판정 | GOLD | SILVER | BRONZE | REJECT | 날짜 |
   |-------|------|------|------|--------|--------|--------|------|
   | 0     | SOT  | PASS | 13   | 1      | 1      | 0      | 3/18 |
   | 1     | v6   | -    | -    | -      | -      | -      | -    |
   ...

3. 전체 진행률 표시
4. 잔여 작업 목록
```

### `/report compare` — v6~v12 원본 대비 비교

```
1. 원본 결과 로딩:
   - v8_results/ (38 파일)
   - v9_results/ (38 파일)
   - v10_results/ (149 파일)
   - v11_results/ (80 파일)
   - v12/v12_results/ (70 파일)
   ↓
2. v13 재실행 결과와 비교:
   - 동일 검증 항목의 판정 변화
   - 새로 발견된 오류
   - 해소된 오류
   - delta 적용 효과
   ↓
3. 개선/악화 분석:
   - IMPROVED: 이전 FAIL → 현재 PASS
   - DEGRADED: 이전 PASS → 현재 FAIL (CRITICAL)
   - NEW_ISSUE: 이전에 없던 오류
   - RESOLVED: delta로 해소된 항목
```

---

## 리포트 형식

```markdown
# VAMOS v13 Phase {N} 검증 리포트

## 요약
- 대상: {검증 대상}
- 판정: {PASS|FAIL}
- 실행일: {날짜}
- PART2 버전: v{XX}.0.0

## 통계
| 등급 | 건수 | 비율 |
|------|------|------|
| GOLD | XX | XX% |
| SILVER | XX | XX% |
| BRONZE | XX | XX% |
| REJECT | XX | XX% |

## Layer A 결과 (결정론적)
...

## Layer B 결과 (AI 의미적)
...

## 적대적 감사 결과
...

## 미해결 항목
...

## v{이전버전} 대비 변화
...

## 권장 조치
...
```

## 출력

**저장 위치**: `v13_results/phase{N}/v13_phase{N}_report.md`
**전체 요약**: `v13_results/v13_summary_report.md`
**비교 리포트**: `v13_results/v13_comparison_report.md`