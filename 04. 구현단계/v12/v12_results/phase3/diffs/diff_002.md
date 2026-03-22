# Diff 002: S2 BLOCKER 9건 신규 삽입

## 삽입 요약

| # | feature_id | feature_name | 삽입 위치 | 마커 |
|---|-----------|--------------|----------|------|
| S2-1 | v12_C09a_037 | Self-RAG 자기 반성 RAG | §4.P2 (V2-Phase 2) row 117 | <!-- v12_C09a_037 v26 --> |
| S2-2 | v12_C09b_451 | PagedAttention / vLLM | §4.P1 (V2-Phase 1) 추가 테이블 | <!-- v12_C09b_451 v26 --> |
| S2-3 | v12_C11_151 | LLM 비용 최적화 시스템 | §3.P2 (V1-Phase 2) row 14 | <!-- v12_C11_151 v26 --> |
| S2-4 | v12_C12_170 | 자율 코딩 에이전트 | §4.P2 (V2-Phase 2) row 118 | <!-- v12_C12_170 v26 --> |
| S2-5 | v12_C13_003 | 에이전트 공유 TaskBoard | §4.P2 (V2-Phase 2) row 119 | <!-- v12_C13_003 v26 --> |
| S2-6 | v12_C13_008 | 추론 모드 통합 (Reasoning Budget) | §4.P2 (V2-Phase 2) row 120 | <!-- v12_C13_008 v26 --> |
| S2-7 | v12_C13_013 | Personal Constitution 시스템 | §4.P3 (V2-Phase 3) row 24 | <!-- v12_C13_013 v26 --> |
| S2-8 | v12_C13_025 | EU AI Act 위험 분류 자동 평가 | §4.P3 (V2-Phase 3) row 25 | <!-- v12_C13_025 v26 --> |
| S2-9 | v12_C13_034 | 사용자 피드백 수집 시스템 | §3.P4 (V1-Phase 4) row 20 | <!-- v12_C13_034 v26 --> |

## BP 준수
- BP-4 ✅ 기존 행 삭제 없음
- BP-6 ✅ 테이블 끝에 추가
- BP-7 ✅ 모든 행에 `<!-- feature_id v26 -->` 마커
- BP-11 ✅ 기존 ID 충돌 없음 (신규 번호 사용)
