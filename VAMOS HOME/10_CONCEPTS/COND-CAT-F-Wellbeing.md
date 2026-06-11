---
tags: [type/concept, module/COND, status/COND, tier/T2, version/V2]
aliases: [CAT-F, Wellbeing 모듈, 건강/웰니스 COND]
created: 2026-06-11
---

# COND CAT-F: Wellbeing (8개)

## 정의
COND 106개 중 건강/웰빙 카테고리. 수면(CBT-I), 운동(Progressive Overload), 식단/영양, 감정 일지(CBT 리프레이밍), 사회적 관계(Dunbar), 건강 인사이트, 감정 음악 추천(ISO-principle), 웰빙 대시보드를 담당한다. 모듈 ID 범위 #95-#101, #116. 8/8 L3 승급 완료(2026-04-19).

## 모듈 목록 (8)
| ID | 이름 | 우선순위 |
|---|---|---|
| COND-095 | 수면 개선 | MEDIUM |
| COND-096 | 운동/피트니스 | MEDIUM |
| COND-097 | 식단/영양 | MEDIUM |
| COND-098 | 감정 일지 | HIGH |
| COND-099 | 사회적 관계 | LOW |
| COND-100 | 건강 인사이트 (095~099 종합) | MEDIUM |
| COND-101 | 감정 음악 추천 | LOW |
| COND-116 | 웰빙 대시보드 | MEDIUM |

## 등장 도메인
- [[T2-COND-Modules]] — 정본 소유 (2-2 COND 카테고리 체계)
- [[T3-Health-EmotionAI]] — 3-6 웰니스/EmotionAI/CBT 문서 전체 교차 참조
- [[T2-Blue-Node]] — Wellness Node가 주요 소비 (**Permission P2 — 세션별 승인**, 건강 데이터 민감도)
- [[T0-Governance]] — Non-goal 2.3(의료 단정 금지)·2.4(민감정보 장기 저장 금지) 직접 적용 영역

## 값·수치 (LOCK 여부)
- 프라이버시 정책: 의료 면책 표시 필수 / 데이터 보존 기본 90일 후 자동 삭제 / at-rest·in-transit 암호화 필수 / GDPR granular consent
- Mixin: `WellbeingMixin` / Config Group: `wellbeing_config` (privacy_level, data_retention, medical_disclaimer, consent_required)
- 의존성: Apple HealthKit/Google Fit API, 감정 분석 모델 / CAT-A(감정 ML)·CAT-C(인프라)·CAT-D(오디오) 소비

## 원본 경로
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_DETAIL_구조화_종합계획서.md` (L67~76)
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\06_cat-f-wellbeing\_index.md`
