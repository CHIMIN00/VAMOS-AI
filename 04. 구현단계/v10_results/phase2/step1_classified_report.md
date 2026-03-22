# VAMOS v10 Phase 2 - Step 1: 확실한 분류 상세 리포트

- 일시: 2026-03-10
- 전체 항목: 1,068건
- Step 1 분류 완료: 347건
- 미분류(→Step 2): 721건

## 1. 분류 요약

| 분류(substatus) | 건수 | 분류 기준 | 신뢰도 |
|----------------|------|----------|--------|
| NOT_APPLICABLE | 140 | suggested_phase=NOT_APPLICABLE (STEP7 TITLE_ONLY) | 100% |
| SUB_FEATURE_OF_EXISTING | 133 | PART2 §2-5에 고유 키워드 직접 매칭 | 100% |
| SKIP_CONFIRMED | 60 | 원본 데이터 action=SKIP 필드 | 100% |
| RESOLVED | 10 | 원본 데이터 status=RESOLVED 필드 | 100% |
| SECTION6_DETAILED | 3 | PART2 §6에 고유 키워드 직접 매칭 | 100% |
| DUPLICATE | 1 | D207-108 = AINV-056 하드코딩 | 100% |
| **TOTAL** | **347** | | |

## 2. Match Type 상세 분포

| Match Type | 건수 | 설명 |
|-----------|------|------|
| suggested_phase | 140 | suggested_phase 필드가 NOT_APPLICABLE으로 시작 |
| eng_keyword_s25 | 71 | 영문 3+자 고유 키워드가 PART2 §2-5에 word-boundary 매칭 |
| action_skip | 60 | action 필드가 SKIP |
| kor4_keyword_s25 | 53 | 한글 4+자 고유 키워드가 PART2 §2-5에 매칭 |
| status_field | 10 | status 필드가 RESOLVED |
| module_id_exact | 9 | feature_name에 모듈 ID(I-XX, E-XX 등)가 있고 PART2에 동일 ID 존재 |
| eng_keyword_s6 | 2 | 영문 3+자 고유 키워드가 PART2 §6에 word-boundary 매칭 |
| kor4_keyword_s6 | 1 | 한글 4+자 고유 키워드가 PART2 §6에 매칭 |
| hardcoded | 1 | 하드코딩 규칙 (D207-108=AINV-056) |

## 3-1. NOT_APPLICABLE (140건)

> 구현 범위 밖 항목 (STEP7 TITLE_ONLY 등). PART2 반영 불필요.

### S7AE-396
- **Feature**: C-045 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-397
- **Feature**: C-046 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-398
- **Feature**: C-047 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-399
- **Feature**: C-048 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-400
- **Feature**: C-049 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-401
- **Feature**: C-050 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-402
- **Feature**: C-051 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-403
- **Feature**: C-052 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-404
- **Feature**: C-053 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-405
- **Feature**: C-054 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-406
- **Feature**: C-055 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-407
- **Feature**: C-056 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-408
- **Feature**: C-057 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-409
- **Feature**: C-058 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-410
- **Feature**: C-059 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-411
- **Feature**: C-060 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-412
- **Feature**: C-061 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-413
- **Feature**: C-062 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-414
- **Feature**: C-063 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-415
- **Feature**: C-064 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-416
- **Feature**: C-065 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-417
- **Feature**: C-066 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-418
- **Feature**: C-067 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-419
- **Feature**: C-068 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-420
- **Feature**: C-069 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-421
- **Feature**: C-070 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-422
- **Feature**: C-071 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-423
- **Feature**: C-072 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-424
- **Feature**: C-073 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-425
- **Feature**: C-074 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-426
- **Feature**: C-075 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-427
- **Feature**: C-076 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-428
- **Feature**: C-077 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-429
- **Feature**: C-078 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-430
- **Feature**: C-079 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-431
- **Feature**: C-080 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-432
- **Feature**: C-081 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-433
- **Feature**: C-082 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-434
- **Feature**: C-083 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-435
- **Feature**: C-084 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-436
- **Feature**: C-085 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-437
- **Feature**: C-086 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-438
- **Feature**: C-087 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-439
- **Feature**: C-088 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-440
- **Feature**: C-089 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-441
- **Feature**: C-090 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-442
- **Feature**: C-091 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-443
- **Feature**: C-092 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-444
- **Feature**: C-093 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-445
- **Feature**: C-094 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-446
- **Feature**: C-095 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-447
- **Feature**: C-096 시스템설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-448
- **Feature**: C-097 시스템설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-449
- **Feature**: C-098 시스템설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-450
- **Feature**: C-099 시스템설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-451
- **Feature**: C-100 시스템설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-452
- **Feature**: C-101 시스템설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-453
- **Feature**: C-102 시스템설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-454
- **Feature**: C-103 시스템설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-455
- **Feature**: C-104 시스템설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-490
- **Feature**: D-035 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-491
- **Feature**: D-036 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-492
- **Feature**: D-037 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-493
- **Feature**: D-038 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-494
- **Feature**: D-039 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-495
- **Feature**: D-040 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-496
- **Feature**: D-041 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-497
- **Feature**: D-042 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-498
- **Feature**: D-043 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-499
- **Feature**: D-044 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-500
- **Feature**: D-045 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-501
- **Feature**: D-046 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-502
- **Feature**: D-047 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-503
- **Feature**: D-048 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-504
- **Feature**: D-049 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-505
- **Feature**: D-050 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-506
- **Feature**: D-051 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-507
- **Feature**: D-052 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-508
- **Feature**: D-053 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-509
- **Feature**: D-054 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-510
- **Feature**: D-055 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-511
- **Feature**: D-056 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-512
- **Feature**: D-057 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-513
- **Feature**: D-058 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-514
- **Feature**: D-059 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-515
- **Feature**: D-060 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-516
- **Feature**: D-061 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-517
- **Feature**: D-062 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-518
- **Feature**: D-063 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-519
- **Feature**: D-064 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-520
- **Feature**: D-065 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-521
- **Feature**: D-066 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-522
- **Feature**: D-067 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-523
- **Feature**: D-068 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-524
- **Feature**: D-069 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-525
- **Feature**: D-070 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-526
- **Feature**: D-071 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-527
- **Feature**: D-072 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-528
- **Feature**: D-073 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-529
- **Feature**: D-074 데이터설계
- **Severity**: HIGH | **Version**: V2
- **Match Type**: suggested_phase

### S7AE-530
- **Feature**: D-075 데이터설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-531
- **Feature**: D-076 데이터설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-532
- **Feature**: D-077 데이터설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-533
- **Feature**: D-078 데이터설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-534
- **Feature**: D-079 데이터설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-535
- **Feature**: D-080 데이터설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-536
- **Feature**: D-081 데이터설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-537
- **Feature**: D-082 데이터설계
- **Severity**: HIGH | **Version**: V3
- **Match Type**: suggested_phase

### S7AE-456
- **Feature**: D-001 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-457
- **Feature**: D-002 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-458
- **Feature**: D-003 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-459
- **Feature**: D-004 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-460
- **Feature**: D-005 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-461
- **Feature**: D-006 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-462
- **Feature**: D-007 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-463
- **Feature**: D-008 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-464
- **Feature**: D-009 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-465
- **Feature**: D-010 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-466
- **Feature**: D-011 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-468
- **Feature**: D-013 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-469
- **Feature**: D-014 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-470
- **Feature**: D-015 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-471
- **Feature**: D-016 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-472
- **Feature**: D-017 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-474
- **Feature**: D-019 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-475
- **Feature**: D-020 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-476
- **Feature**: D-021 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-477
- **Feature**: D-022 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-478
- **Feature**: D-023 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-479
- **Feature**: D-024 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-480
- **Feature**: D-025 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-481
- **Feature**: D-026 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-482
- **Feature**: D-027 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-483
- **Feature**: D-028 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-484
- **Feature**: D-029 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-485
- **Feature**: D-030 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-486
- **Feature**: D-031 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-487
- **Feature**: D-032 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-488
- **Feature**: D-033 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

### S7AE-489
- **Feature**: D-034 데이터설계
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: suggested_phase

## 3-2. SUB_FEATURE_OF_EXISTING (133건)

> PART2에 이미 존재하는 모듈/기능의 하위 기능. 별도 추가 불필요.

### AINV-056
- **Feature**: SHAP/LIME Explainability 모듈 (explainer.py)
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:SHAP, ABBR:SHAP

### CLAUDE-089
- **Feature**: EVX-1 Code-as-Policy 검증 구현
- **Severity**: HIGH | **Version**: V1,V2,V3
- **Match Type**: module_id_exact
- **Evidence**: MID:EVX-1 in PART2

### CLAUDE-090
- **Feature**: EVX-2 Adversarial 검증 구현
- **Severity**: HIGH | **Version**: V1,V2,V3
- **Match Type**: module_id_exact
- **Evidence**: MID:EVX-2 in PART2

### CLAUDE-091
- **Feature**: EVX-3 Log-prob Confidence 검증 구현
- **Severity**: HIGH | **Version**: V1,V2,V3
- **Match Type**: module_id_exact
- **Evidence**: MID:EVX-3 in PART2

### CLAUDE-092
- **Feature**: EVX-4 Thought Buffer 검증 구현
- **Severity**: HIGH | **Version**: V1,V2,V3
- **Match Type**: module_id_exact
- **Evidence**: MID:EVX-4 in PART2

### CLAUDE-093
- **Feature**: EVX-5 Gen-Verify-Learn 검증 구현
- **Severity**: HIGH | **Version**: V1,V2,V3
- **Match Type**: module_id_exact
- **Evidence**: MID:EVX-5 in PART2

### D202-073
- **Feature**: I-18 Meta-learning 모듈 구현
- **Severity**: HIGH | **Version**: V2
- **Match Type**: module_id_exact
- **Evidence**: MID:I-18 in PART2

### D202-085
- **Feature**: G3 EvidenceGate 구현
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:EvidenceGate, ENG:EvidenceGate

### D202-087
- **Feature**: G4 SelfCheckGate 구현
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:SelfCheckGate, ENG:SelfCheckGate

### D202-094
- **Feature**: ToolRegistry 통합 구현
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:ToolRegistry, ENG:ToolRegistry

### D203-008
- **Feature**: Mixture of Agents (MoA) 다중 LLM 합의 구현
- **Severity**: HIGH | **Version**: V1,V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:LLM, ABBR:LLM, ENG:Agents

### D203-082
- **Feature**: Provider 자동 선택 규칙 구현 (risk_class/cost_class 기준)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Provider

### D204-021
- **Feature**: Native Multimodal 활용 (GPT-4o/Gemini 2.0 네이티브)
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Multimodal, PENG:Gemini, ENG:GPT, ABBR:GPT, PENG:GPT-4o

### D204-026
- **Feature**: PagedAttention/vLLM 고효율 추론 서빙
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:vLLM

### D204-042
- **Feature**: OTHER BRAINS→07 Gate 연결 규칙 (ToolRegistry 경유, Gate 결과 기록)
- **Severity**: HIGH | **Version**: V1,V2,V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:ToolRegistry, PENG:Gate, ABBR:ToolRegistry, ENG:Gate, PENG:ToolRegistry

### D204-143
- **Feature**: SDK 코드 생성 (OpenAPI→다국어 자동)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:SDK, ENG:SDK

### D205-025
- **Feature**: 중앙 프롬프트 라이브러리
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:라이브러리, KOR4:프롬프트

### D205-057
- **Feature**: 오케스트레이션 패턴 (Centralized/Hierarchical/Market-based/Stigmergic)
- **Severity**: HIGH | **Version**: V1,V2,V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Market, ENG:based

### D206-066
- **Feature**: Contextual Retrieval 벤치마크 적용 (67% 향상)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### D206-087
- **Feature**: Self-RAG 자기 평가 루프
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:RAG, ENG:RAG

### D206-115
- **Feature**: 개인 멀티미디어 라이브러리
- **Severity**: HIGH | **Version**: V2
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:라이브러리

### D206-128
- **Feature**: Self-RAG 루프 구현
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:RAG, ENG:RAG

### D206-199
- **Feature**: M-029 코드 스니펫 라이브러리
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:라이브러리

### D206-222
- **Feature**: M-004 스크린 캡처 지식화 (Microsoft Recall 로컬 버전)
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: PENG:Recall, ENG:Recall

### D207-045
- **Feature**: Zero-Trust Architecture
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Trust

### D207-056
- **Feature**: SelfCheckGate 구현 (P0≥70/P1≥75/P2≥80)
- **Severity**: HIGH | **Version**: V1,V2,V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:SelfCheckGate, ENG:SelfCheckGate

### D207-100
- **Feature**: Human-in-the-Loop (고위험 결정 사람 확인)
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Loop

### D207-169
- **Feature**: 프라이버시 우선 모드
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:프라이버시

### S7AE-307
- **Feature**: Self-RAG 구현
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:RAG, ENG:RAG

### S7AE-375
- **Feature**: OAuth 통합
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:OAuth, ENG:OAuth

### S7AE-376
- **Feature**: JWT 토큰 관리
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:JWT, ABBR:JWT

### S7BG-003
- **Feature**: Confidence-based 응답 전략
- **Severity**: HIGH | **Version**: V1,V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:based, ENG:Confidence

### S7BG-014
- **Feature**: Swarm 오케스트레이션 패턴
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Swarm

### S7BG-024
- **Feature**: 자동 스케일링 (HPA+KEDA)
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:HPA, ABBR:HPA, PENG:HPA

### S7FI-069
- **Feature**: 모델 레지스트리
- **Severity**: HIGH | **Version**: V2
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:레지스트리

### S7FI-081
- **Feature**: DNS 관리
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:DNS, ENG:DNS

### S7FI-082
- **Feature**: SSL/TLS 인증서
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:SSL, ABBR:TLS, ENG:SSL, ENG:TLS

### S7FI-286
- **Feature**: 앱 다운로드 분석
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:다운로드

### S7FI-357
- **Feature**: 개인정보 보호
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:개인정보

### S7JM-103
- **Feature**: MCP 프롬프트 관리
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:MCP, ABBR:MCP

### S7JM-105
- **Feature**: MCP 보안 레이어
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:MCP, ABBR:MCP

### S7JM-158
- **Feature**: OpenAI 대비 VAMOS 차별화
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:OpenAI, ENG:OpenAI

### S7JM-253
- **Feature**: 지식 기반 RAG 최적화
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:RAG, ENG:RAG

### S7JM-257
- **Feature**: 스마트 리마인더
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:리마인더

### S7NP-008
- **Feature**: 스케줄러 (Cron)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Cron, PENG:Cron

### S7NP-022
- **Feature**: Human-in-the-Loop
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Loop

### S7NP-029
- **Feature**: Google Workspace 통합
- **Severity**: HIGH | **Version**: V1,V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Google

### S7NP-032
- **Feature**: GitHub/GitLab 통합
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:GitHub, ENG:GitHub

### S7NP-139
- **Feature**: 한국어 프롬프트 최적화
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:프롬프트

### S7NP-204
- **Feature**: 로컬 우선 프라이버시
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:프라이버시

### SDAR-051
- **Feature**: NEVER_AUTO 10개 수리 액션 하드코딩 차단 구현 (RA_NEVER_01~RA_NEVER_10)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:하드코딩

### SDAR-055
- **Feature**: SDAR-CostGate 통합 구현 (수리로 인한 추가 비용 발생 여부 확인)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:CostGate, ENG:SDAR, ABBR:SDAR, ABBR:CostGate

### SDAR-057
- **Feature**: SDAR-EvidenceGate 통합 구현 (진단 근거 충분성 확인)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:SDAR, ABBR:EvidenceGate, ABBR:SDAR, ENG:EvidenceGate

### SDAR-083
- **Feature**: NEVER_AUTO_TARGETS frozenset 하드코딩 및 validate_repair_target 함수 구현
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:하드코딩

### TEAM-012
- **Feature**: AgentMatcher 구현 (작업-에이전트 매칭 알고리즘)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:에이전트

### TEAM-074
- **Feature**: V1 @vamos.agent 데코레이터(내부 Agent SDK 베이스)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: PENG:SDK, ABBR:SDK, ENG:SDK

### TEAM-103
- **Feature**: I-18 Meta-learning 연동 (팀 실행 패턴 학습 → 향후 자동 개선)
- **Severity**: HIGH | **Version**: V2
- **Match Type**: module_id_exact
- **Evidence**: MID:I-18 in PART2

### AINV-025
- **Feature**: EngineConfig 설정 모델 (fee_rate, slippage_rate, risk_free_rate, frequency)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:frequency, PENG:frequency

### AINV-052
- **Feature**: 프로덕션 OHLCV str+Decimal 타입 의무화
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:프로덕션

### AINV-070
- **Feature**: Mean-Variance Optimization 구현 (portfolio_optimizer.py)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Optimization

### AINV-080
- **Feature**: 실전 거래 소액 시작 모드 (Real Trading)
- **Severity**: MEDIUM | **Version**: V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Trading, PENG:Trading

### AINV-136
- **Feature**: Z-Session auto_decision_controller.py 전략 유지 자동 판단
- **Severity**: MEDIUM | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Session

### AINV-141
- **Feature**: alerts.yaml 알림 설정 파일
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:alerts

### AINV-143
- **Feature**: Z-Session 거래 로그 + 슬리피지 추적기
- **Severity**: MEDIUM | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Session

### CLAUDE-188
- **Feature**: QoD ≥ 0.90 (60일) 달성 검증
- **Severity**: MEDIUM | **Version**: V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:QoD, ABBR:QoD

### CLAUDE-238
- **Feature**: NodeRegistry 구현 (domain_name 기반)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:NodeRegistry, ABBR:NodeRegistry

### CLAUDE-239
- **Feature**: VerifyChainRegistry 구현 (EVX-1~EVX-6)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: module_id_exact
- **Evidence**: MID:EVX-1 in PART2

### D203-025
- **Feature**: MCP 디버깅 도구 (Inspector/Playground/로그뷰어/성능프로파일러)
- **Severity**: MEDIUM | **Version**: V1,V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:MCP, ABBR:MCP

### D203-070
- **Feature**: CORE↔NODE 요청/응답 엔벨로프 구현 (필수+optional 확장 필드)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:optional, PENG:optional

### D204-080
- **Feature**: LLM 메트릭 수집 (토큰/비용/지연/캐시율/에러율)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:LLM, ENG:LLM

### D204-105
- **Feature**: 응답 시간 SLO (채팅 P50<1s, 검색<3s, 코드<5s)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:P50

### D205-001
- **Feature**: AgentMode Enum 정의 (MANUAL/SEMI_AUTO/SUPERVISED_AUTO)
- **Severity**: MEDIUM | **Version**: V1,V2,V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Enum

### D206-006
- **Feature**: L2 Long-term Knowledge 구현 (전역 검색 기반)
- **Severity**: MEDIUM | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:term, ENG:Knowledge, ENG:Long

### D206-022
- **Feature**: L3 Procedural 폐기/롤백 메커니즘
- **Severity**: MEDIUM | **Version**: V2,V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Procedural

### D206-139
- **Feature**: RAG 품질 자동 평가 (RAGAS, 주간)
- **Severity**: MEDIUM | **Version**: V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:RAG, ABBR:RAG

### D207-049
- **Feature**: 비용 상한 구현 (V1:40K/V2:93K/V3:266K KRW 월)
- **Severity**: MEDIUM | **Version**: V1,V2,V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:KRW, ENG:KRW, PENG:KRW

### D207-195
- **Feature**: 이용약관/개인정보 법적 문서 표시 + 동의 관리
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:개인정보

### DD4-011
- **Feature**: contracts.py KBEmbeddingRecord 필드 추가 구현 (vector_dim, embedded_at_utc)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:contracts

### DD5-010
- **Feature**: VerifyChainRegistry 구현 (EVX-1~6, JSON 형식, DN-006 해소)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: module_id_exact
- **Evidence**: MID:EVX-1 in PART2

### P30-049
- **Feature**: 유형별 가변 청크 크기 구현 (DEC-004)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:DEC, ENG:DEC

### PB2-006
- **Feature**: 루트 설정 파일 생성 (package.json, tsconfig.json 등)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: PENG:package.json, ENG:package

### PB4-003
- **Feature**: [core] 섹션 ConfigModel 구현
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:ConfigModel, ABBR:ConfigModel

### PB4-004
- **Feature**: [llm] 섹션 ConfigModel 구현
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:ConfigModel, ENG:llm, ABBR:ConfigModel

### PB4-006
- **Feature**: [vector_db] + [graph_db] 섹션 ConfigModel 구현
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:vector_db, ENG:graph_db, ENG:ConfigModel, ABBR:ConfigModel

### PB4-009
- **Feature**: [mcp] 섹션 ConfigModel 구현 (streamable_http LOCK)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:mcp, ENG:streamable_http, ENG:ConfigModel, ABBR:ConfigModel, PENG:streamable_http

### PB6-013
- **Feature**: GitHub Secrets 14개 등록 설정
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:GitHub, ENG:GitHub, ENG:Secrets

### S7AE-359
- **Feature**: 서비스 디스커버리
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:디스커버리

### S7AE-558
- **Feature**: 컨테이너 오케스트레이션
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:컨테이너

### S7AE-569
- **Feature**: 환경 프로비저닝
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:프로비저닝

### S7FI-172
- **Feature**: 평가 데이터셋 관리
- **Severity**: MEDIUM | **Version**: V2
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:데이터셋

### S7NP-138
- **Feature**: LLM 폴백 전략 고도화
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:LLM, ENG:LLM

### S7NP-169
- **Feature**: Qdrant 벡터DB 최적화
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:Qdrant

### S7NP-173
- **Feature**: 1-bit LLM (BitNet)
- **Severity**: MEDIUM | **Version**: V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:LLM, ABBR:LLM

### S7NP-180
- **Feature**: MMLU-Pro
- **Severity**: MEDIUM | **Version**: V2
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:MMLU, ENG:MMLU, ENG:Pro

### TEAM-022
- **Feature**: SDARAgent 구현 (자가진단/자동복구)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:자가진단

### TEAM-024
- **Feature**: ProductivityAgent 구현 (일정관리, 리마인더, 노트)
- **Severity**: MEDIUM | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:리마인더

### S7AE-622
- **Feature**: 비용 최적화 대시보드
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:대시보드

### S7BG-027
- **Feature**: 응답 품질 자동 평가 (QoD)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: eng_keyword_s25
- **Evidence**: ENG:QoD, ABBR:QoD, PENG:QoD

### S7BG-071
- **Feature**: BFCL v3 (Function Calling 벤치마크)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-061
- **Feature**: 비용 추적 대시보드
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:대시보드

### S7FI-091
- **Feature**: 성능 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-097
- **Feature**: MMLU 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:MMLU, ENG:MMLU

### S7FI-098
- **Feature**: HellaSwag 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-100
- **Feature**: WinoGrande 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-101
- **Feature**: GSM8K 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-102
- **Feature**: TruthfulQA 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-107
- **Feature**: KoBEST 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-108
- **Feature**: KLUE 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-109
- **Feature**: KorQuAD 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-110
- **Feature**: Korean NLI 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-111
- **Feature**: 한국어 요약 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-112
- **Feature**: 한국어 생성 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-115
- **Feature**: HumanEval 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:HumanEval, ENG:HumanEval

### S7FI-116
- **Feature**: MBPP 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:MBPP, ENG:MBPP

### S7FI-117
- **Feature**: CodeContests 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-118
- **Feature**: SWE-bench 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-119
- **Feature**: DS-1000 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-123
- **Feature**: AgentBench 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-124
- **Feature**: ToolBench 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-125
- **Feature**: WebArena 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-126
- **Feature**: API-Bank 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-132
- **Feature**: RAG 재현율 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:RAG, ENG:RAG

### S7FI-133
- **Feature**: RAG 지연시간 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: eng_keyword_s25
- **Evidence**: ABBR:RAG, ENG:RAG

### S7FI-141
- **Feature**: 유해성 탐지 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-142
- **Feature**: 편향성 탐지 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-143
- **Feature**: 환각 탐지 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-144
- **Feature**: 프라이버시 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:프라이버시, KOR4:벤치마크

### S7FI-145
- **Feature**: 로버스트니스 벤치마크
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:벤치마크

### S7FI-211
- **Feature**: 페르소나 정의
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:페르소나

### S7FI-295
- **Feature**: 한국 파생상품 분석
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:파생상품

### S7JM-096
- **Feature**: 참고 데이터셋 (J)
- **Severity**: LOW | **Version**: V1
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:데이터셋

### S7NP-051
- **Feature**: 학습 분석 대시보드
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:대시보드

### S7NP-091
- **Feature**: 웰빙 대시보드
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: kor4_keyword_s25
- **Evidence**: KOR4:대시보드

## 3-3. SKIP_CONFIRMED (60건)

> 원본 검토 시 SKIP으로 판정된 항목. 구현 범위 밖.

### AINV-003
- **Feature**: 5-Agent 워크플로우 오케스트레이션
- **Severity**: HIGH | **Version**: V1
- **Match Type**: action_skip

### AINV-066
- **Feature**: Docker Compose 전체 스택 설정
- **Severity**: MEDIUM | **Version**: V0
- **Match Type**: action_skip

### BGNR-006
- **Feature**: UI 상태 머신 6단계 (UIS1_IDLE → UIS2_PROCESSING → UIS3_LOCKED → UIS4_RUNNING → UIS5_AWAIT_APPROVAL → UIS6_PRESENTING)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### BGNR-021
- **Feature**: AINV 안전장치 4종 (VaR 5% 경고+P2승인, 면책문구 100%삽입, 금융환각탐지, FOMO/패닉 15분 쿨다운)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### CLAUDE-053
- **Feature**: 45개 미해소 이슈 해결 구현 (HIGH 10건, MEDIUM 21건, LOW 9건, INFO 5건)
- **Severity**: LOW | **Version**: V0,V1,V2,V3
- **Match Type**: action_skip

### CLAUDE-063
- **Feature**: A-1 MultiBrain Adapter 모듈 구현
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### CLAUDE-077
- **Feature**: C-2 Math Verifier 모듈 구현
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### CLAUDE-135
- **Feature**: P2 재확인 모달 구현 (DEC-011)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### CLAUDE-136
- **Feature**: 비용 경고 색상 표시 구현 (80%=#FBBF24노란, 100%=#EF4444빨간, DEC-015)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### CLAUDE-247
- **Feature**: NEVER_AUTO 10개 영역 보호 구현
- **Severity**: LOW | **Version**: V2,V3
- **Match Type**: action_skip

### D202-053
- **Feature**: 사고 과정 표시 구현 (S7B-007)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D202-097
- **Feature**: 중국 AI 모델 Brain Adapter 등록 (참조/Failover)
- **Severity**: LOW | **Version**: V2,V3
- **Match Type**: action_skip

### D202-108
- **Feature**: LM-Eval Harness 통합 구현
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D202-115
- **Feature**: 3단계 테스트 전략 구현 (단위≥80%/통합≥90%/시나리오≥95%)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D203-083
- **Feature**: MCP 도구 4단계 검증 절차 구현 (Inspector→trial→안전테스트→active)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D204-005
- **Feature**: LLM 서빙 엔진 비교/선택 (10개 엔진 전수비교)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D204-040
- **Feature**: Hardware Abstraction Layer (동일 계약 호출 추상화)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D204-060
- **Feature**: 비용 상한 초과 자동 차단 (승인 없이 즉시 deny)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D204-067
- **Feature**: API/모델 호출 Rate Limit (외부 10/분, 고비용 3/분, 전체 60/분)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D204-075
- **Feature**: JSON Structured Logging 표준 (timestamp/level/module/event/trace_id/payload)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D204-081
- **Feature**: 비용 대시보드 (일/주/월+모델별+예산 진행바)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D204-083
- **Feature**: 응답 결과 최소 필드 (model_id/trace_id/policy_decision/cost_summary)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D204-095
- **Feature**: 전체 요청 trace_id 체인 추적 (ui→oc→bn→if→wf→mem/sc)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D204-117
- **Feature**: 프롬프트 테스트 (promptfoo YAML 회귀 테스트)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D204-123
- **Feature**: Fallback Chain (config/fallback_chains.yaml, 최대 3단계)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D204-125
- **Feature**: 분산 트레이싱 통합 (OpenTelemetry, V2=Jaeger, V3=Tempo)
- **Severity**: LOW | **Version**: V2,V3
- **Match Type**: action_skip

### D205-028
- **Feature**: 프롬프트 A/B 테스트
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D205-126
- **Feature**: 언어 학습 지원 (AI 대화/발음 평가/문법/어휘/게이미피케이션)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D205-127
- **Feature**: 독서 어시스턴트 (챕터 핵심/Q&A/논문 분석)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D205-128
- **Feature**: 퀴즈/테스트 자동 생성 (객관식/주관식/코드/시나리오, 난이도 자동 조정)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D205-130
- **Feature**: 학습 분석 대시보드 (학습시간/진행률/테스트/간격반복/강점/약점)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D205-133
- **Feature**: 팟캐스트/오디오 학습 (전사 요약 카드, NotebookLM 스타일 오디오 생성)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D205-134
- **Feature**: 책 요약 + 독서 관리 (트래킹/노트/인용구/책 간 연결)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D205-136
- **Feature**: 온라인 강의 통합 (Coursera/edX/Udemy 보조)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D205-139
- **Feature**: 목표 관리 (OKR/SMART)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D205-140
- **Feature**: 시간 관리 (포모도로/시간 기록/효율 분석/일정 최적화)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D205-142
- **Feature**: 커리어 개발 지원 (스킬 갭 분석/이력서/자기소개서)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D205-144
- **Feature**: 프레젠테이션 코칭 (슬라이드/스크립트/리허설/Q&A)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D205-145
- **Feature**: 네트워킹/인맥 관리 (연락처/리마인더/인맥 KG)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D205-161
- **Feature**: 크립토/DeFi 통합 (시장데이터/온체인/감성/포트폴리오/DeFi/NFT/규제/에어드랍)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D206-024
- **Feature**: SourceQoD 스코어 산출/기록 모듈 (0~1)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D206-025
- **Feature**: 계층별 TTL 정책 구현 (L0 세션종료/L1 90일/L2 무기한/L3 정책기반)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D206-083
- **Feature**: KG 자동 구축 (엔티티/관계 추출)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D206-155
- **Feature**: RAG 통합 API (retrieve/index/delete/status)
- **Severity**: LOW | **Version**: V2,V3
- **Match Type**: action_skip

### D206-202
- **Feature**: M-035 투자 리서치 노트
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D206-210
- **Feature**: M-028 지식 공유 및 협업
- **Severity**: LOW | **Version**: V2,V3
- **Match Type**: action_skip

### D207-001
- **Feature**: Non-goal 절대 금지 7항목 정책 구현 (실거래/해킹/의료법률/PII/저작권/P2자동/위험자동)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D207-028
- **Feature**: Prompt Injection 탐지 모델 (규칙→ML)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### D207-081
- **Feature**: ISO 42001 준비
- **Severity**: LOW | **Version**: V2,V3
- **Match Type**: action_skip

### D207-180
- **Feature**: 웰니스-투자 연동 (수면부족→결정연기)
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### D208-001
- **Feature**: i18n 국제화 기반 구조 (ko-KR 기본, en-US 보조, ja-JP V2 확장)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D208-052
- **Feature**: S7C-008~012 대화 분기/공유/편집/멀티탭/ORANGE-BLUE 상태 표시
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D208-053
- **Feature**: Canvas/Artifacts/편집 모드 (S7C-013~022, 10건)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D208-054
- **Feature**: 입력 영역 Composer 패턴 (S7C-023~032, 10건)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### D208-056
- **Feature**: 음성 모드 UI (S7C-045~052, 8건)
- **Severity**: LOW | **Version**: V2,V3
- **Match Type**: action_skip

### D208-067
- **Feature**: 설정/커스터마이징/피드백 UI (S7C-071~080, 10건)
- **Severity**: LOW | **Version**: V1,V2
- **Match Type**: action_skip

### DA1-009
- **Feature**: Graph DB 전환 구현 (V1: JSON 파일, V2+: Neo4j Community, V3: Aura)
- **Severity**: LOW | **Version**: V1,V2,V3
- **Match Type**: action_skip

### DD8-005
- **Feature**: D8 수용 기준 5개 (AC-D8-001~005) 구현 검증
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### P30-073
- **Feature**: MOAT 4건 경쟁우위 구현 추적
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

### P30-088
- **Feature**: 요청 자동 원자화 + 진행률 표시 구현
- **Severity**: LOW | **Version**: V1
- **Match Type**: action_skip

## 3-4. RESOLVED (10건)

> 이전 단계에서 이미 해결 완료된 항목.

### D202-130
- **Feature**: Agent Swarm (PARL) 병렬 실행 구현
- **Severity**: BLOCKER | **Version**: V3
- **Match Type**: status_field

### D205-067
- **Feature**: PARL Agent Swarm Execute 단계
- **Severity**: BLOCKER | **Version**: V3
- **Match Type**: status_field

### D205-076
- **Feature**: Agent Specialization Protocol (자동 fork/특화/retire)
- **Severity**: BLOCKER | **Version**: V3
- **Match Type**: status_field

### CLAUDE-108
- **Feature**: 대화 턴 상한 구현 (P0=5, P1=10, P2=20)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: status_field

### DA1-016
- **Feature**: P6-INV-03 섹터/피어 그룹 비교 분석 모듈 (PER/PBR/EV-EBITDA)
- **Severity**: HIGH | **Version**: V3
- **Match Type**: status_field

### DA1-019
- **Feature**: P6-INV-06 옵션/파생상품 분석 (그릭스/Black-Scholes/변동성 서피스)
- **Severity**: HIGH | **Version**: V3
- **Match Type**: status_field

### P30-009
- **Feature**: DomainScore 종합 점수화 공식 구현
- **Severity**: HIGH | **Version**: V1
- **Match Type**: status_field

### P30-029
- **Feature**: 비용 기반 뇌 선택 정책 구현 (V1/V2/V3 모드별)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: status_field

### P30-058
- **Feature**: 비용 3단계 경보 체계 구현 (70%/85%/95%)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: status_field

### P30-061
- **Feature**: 고비용 모델 사용 제약 구현 (기본차단+조건부허용)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: status_field

## 3-5. SECTION6_DETAILED (3건)

> §6(시스템 횡단 상세)에 이미 기술된 항목.

### CLIB-023
- **Feature**: 사이트 평가 알고리즘 구현 (evaluate_site 함수)
- **Severity**: HIGH | **Version**: V1
- **Match Type**: kor4_keyword_s6
- **Evidence**: KOR4:알고리즘

### S7AE-035
- **Feature**: Citation 시스템
- **Severity**: HIGH | **Version**: V2
- **Match Type**: eng_keyword_s6
- **Evidence**: ENG:Citation

### D208-090
- **Feature**: P7-UIS(4건) + P7-NSP(1건) + P7-LOG(1건) + P7-NGO(1건) UI 실행 메커니즘
- **Severity**: MEDIUM | **Version**: V2
- **Match Type**: eng_keyword_s6
- **Evidence**: ABBR:UIS, ENG:UIS

## 3-6. DUPLICATE (1건)

> 다른 항목과 중복.

### D207-108
- **Feature**: XAI 설명 가능한 AI (SHAP/LIME)
- **Severity**: HIGH | **Version**: V2
- **Match Type**: hardcoded
- **Evidence**: =AINV-056 (SHAP/LIME)
