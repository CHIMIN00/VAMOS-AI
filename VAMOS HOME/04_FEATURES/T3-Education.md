---
tags: [tier/T3, module/COND, status/COND, version/V1, type/domain, lock/FREEZE]
aliases: [3-5, 교육·학습, Education-Learning]
tier: T3
domain: "3-5 Education-Learning"
sot_source: "D:\\VAMOS\\docs\\sot 2\\3-5_Education-Learning\\"
design_doc: "[[D2.0-01-Overview]]"
quality_gate: "APPROVED — Phase 5 FINAL PASS / Phase 4 RECOVERY V3 8건 등재 (2026-05-31)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 적응+SM-2 | V2: P2 투자교육+언어 | V3: P3 VR/AR"
created: 2026-06-12
---

# 3-5 Education-Learning

## 한줄 요약
IRT 적응형 난이도·SM-2 간격반복·소크라테스 교수법 기반 학습 시스템을 구현 정본으로 관리하는 Tier 3 교육 도메인.

## 핵심 정의
- 핵심 모듈: COND CAT-E 교육 모듈 7개 + UI 1건 (D2.0-01~07)
- SM-2 파라미터는 #6 PKM 정본(LOCK-PKM-01~03) 참조만 — 단독 변경 금지(R-08-1), 커스터마이징은 EF 보정 가중치·Bloom 연동 매핑에 한정
- 감정 기반 학습 적응: #9 Health 정본(LOCK-HW-01) 수신, 사용자 opt-in 필수·기본 비활성 (R-08-6)

## LOCK 항목 (LOCK-ED-01~10, 10건)
- ED-01 학습 경로 구조(목표→Phase 분해→자료+실습+체크포인트+소요시간) / ED-02 IRT 5단계 난이도·정답률 70-85%
- ED-03 평가 3종(진단/진행/최종)·3등급(미달/달성/우수) / ED-04 SM-2 정본=#6 PKM(MIN_EF=1.3, DEFAULT_EF=2.5, I(1)=1d, I(2)=6d) 참조만
- ED-05 Bloom 택소노미 6단계(Remember~Create) / ED-06 소크라테스 교수법(직접 답 금지→질문 유도→힌트 3단계)
- ED-07 학습자 프로필 스키마 5필드 / ED-08 플래시카드 4유형(기본/빈칸/이미지오클루전/코드)
- ED-09 VBS-16 학습 지속률≥60%·기억 유지율≥80% / ED-10 게이미피케이션 XP→레벨→배지→Streak→챌린지→리더보드

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 / [[T2-Blue-Node]] — BN 런타임 (#5) / [[T2-COND-Modules]] — CAT-E 모듈 (#8)
- [[T3-PKM]] — SM-2 파라미터 정본 (B4) / [[T3-Multimodal]] — TTS 강의·이미지 교재 (#11)
- [[T3-Health-EmotionAI]] — 감정 상태 데이터 opt-in (#15, B7) / [[T3-Dev-Tools]] — 코드 실행 환경·린터·테스트 러너 (#17)

## 제공 (Provides To)
- [[T3-PKM]] — SM-2 교육 특화 커스터마이징 (B4) / [[T3-Health-EmotionAI]] — 학습 스트레스 신호 (B7)

## 횡단 개념 연결
- [[COND-CAT-E-Education]] — CAT-E 카탈로그 / [[Benchmark-Evaluation-Framework]] — VBS-16 기준
- [[Module-Classification]] — COND 모듈 분류 체계

## 관련 모듈 시리즈
- [[MODULE-MAP]] — CAT-E 교육 모듈 7개 (COND)

## STEP7 매핑
- 출처: STEP7-O (69항목, 읽기 전용 체크리스트)

## 버전별 범위
- V1: P1 적응형+SM-2 / V2: P2 투자교육+언어 / V3: P3 VR/AR

## 검증 상태
- Quality Gate: APPROVED (AUTHORITY v2.4, Phase 4 RECOVERY Sub-A+Sub-B genuine write 2026-05-31, §9 V3 8건 등재)
- LOCK 검증: 10/10 일치 (immutable 확정, 재정의 0)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\3-5_Education-Learning\
- Authority: 3-5_Education-Learning\AUTHORITY_CHAIN.md (v2.4)
- Design: [[D2.0-01-Overview]] (COND CAT-E)
