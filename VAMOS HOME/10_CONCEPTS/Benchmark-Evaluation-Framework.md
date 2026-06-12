---
tags: [type/concept, tier/T5, version/V1, lock/FREEZE]
aliases: [벤치마크 프레임워크, LOCK-BE, 골든셋]
created: 2026-06-12
---

# Benchmark Evaluation Framework (LOCK-BE · 골든셋)

## 정의
VAMOS 평가/벤치마크 체계(5-1 정본). LOCK-BE-01~15(15개, immutable)가 목표치·재현성·평가 절차를 고정하며, 골든셋은 분기별 일부 교체로 오염을 방지한다.

## 이 개념이 등장하는 모든 도메인
- [[T5-Benchmark]] — 5-1 정본(LOCK-BE-01~15, 골든셋·인간평가·88 매트릭스)
- [[T4-MLOps]] — auto_benchmark 연동(LOCK-ML-12 교차)
- [[T5-File-Context]] — Lost-in-the-Middle 등 측정 위임(W12)
- [[T0-Governance]] — 시드 고정 거버넌스(R-18-1)
- [[T6-Brain-Adapter]] — 라우팅 성능 벤치마크 소비(6-9)

## 값·수치 (LOCK)
- LOCK-BE-01: MMLU 전체 목표 **≥ 85%** (macro average)
- LOCK-BE-02: HumanEval **pass@1 ≥ 85%** (상세명세 A-2의 80%는 MBPP 최소 기준 해석, C-01)
- LOCK-BE-08: **seed=42** 기본 + 모델 버전/시스템 프롬프트 해시/실행 환경 기록 필수
- 기타: BE-05 Cohen's κ ≥ 0.6 / BE-06 95% CI 필수 / BE-07 2인+3번째 평가자 / BE-09 Injection 방어 ≥ 95% / BE-11 RAGAS 4지표 / BE-13 골든셋 분기 20% 교체 / BE-14 회귀 3% 알림 / BE-15 190+ 테스트
- 골든셋: V1 100건(층화 추출 seed=42) → **v2 실데이터 162문항 전환(2026-06-11, Phase 2-0)**

## 버전별 차이
- V1: 골든셋+VBS Core 일간(BE-12) / V2: 도메인 벤치마크 확장+인간평가 / V3: 장기 추적·분기 κ 리포트(2026Q3)

## 원본 참조
- `D:\VAMOS\docs\sot 2\5-1_Benchmark-Evaluation\AUTHORITY_CHAIN.md` / 동 폴더 `INDEX.md` / `D:\VAMOS\CLAUDE.md` §21/§23
