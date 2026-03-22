# RECLASSIFIED 276건 SOT 기준 재검토 보고서

> **작성일**: 2026-03-11
> **대화**: 대화 31 (추가 검토)
> **방법**: 3개 병렬 에이전트(Group A/B/C, 각 92건) × PART2 + SOT 교차 검증

---

## 1. 재검토 결과 요약

| 재판정 | 건수 | 비율 | 의미 |
|--------|------|------|------|
| **DESIGN_ONLY** | 249 | 90.2% | SOT에 구현 스펙 없음. 설계/프로세스/전략 문서 수준 |
| **ALREADY_COVERED** | 26 | 9.4% | PART2에 이미 상위 모듈로 커버됨 |
| **BORDERLINE** | 1 | 0.4% | feature_name 오기재 의심 (S7AE-321) |
| **SHOULD_ADD** | **0** | **0.0%** | **PART2 추가 반영 필요 항목 없음** |
| **합계** | **276** | **100%** | |

### 결론
> **276건 중 PART2에 추가 반영이 필요한 항목은 0건입니다.**
> - 249건: SOT(STEP7 작업가이드)에 구현 스펙 자체가 없는 설계/문서/전략 수준 항목
> - 26건: PART2에 이미 커버된 중복 항목
> - 1건: feature_name 오기재 의심 (실제 기능은 이미 PART2에 반영됨)

---

## 2. ALREADY_COVERED 26건 상세 (PART2에 이미 커버됨)

| # | feature_id | feature_name | severity | PART2 커버 근거 |
|---|-----------|-------------|----------|----------------|
| 1 | S7NP-203 | 지식-투자-코딩 통합 원스톱 | LOW | §1 VAMOS 플랫폼 전체 비전으로 포괄 |
| 2 | S7AE-329 | B-011 보안 설계 | MEDIUM | §6.5 보안 구현 15개 항목 (L3303) |
| 3 | S7AE-334 | B-023 배포 전략 | MEDIUM | §6.4 CI/CD GitHub Actions+Docker+Helm (L3280) |
| 4 | S7AE-336 | B-025 확장성 설계 | MEDIUM | V3-Phase 1 K8s HPA 기반 확장 (L2465) |
| 5 | S7AE-357 | 로드 밸런서 | MEDIUM | §6.8 Agent Mesh 로드 밸런싱 (L2983) |
| 6 | S7AE-551 | APM 통합 | MEDIUM | V2-Phase 3 Loki+Grafana Observability (L2555) |
| 7 | S7AE-560 | 인그레스 컨트롤러 | MEDIUM | V3 K8s ingress.yaml 설정 (L2519) |
| 8 | S7AE-578 | 블루/그린 배포 | MEDIUM | V2 블루/그린 배포 (L1950, L2469, L2574) |
| 9 | S7FI-051 | 환경별 배포 | MEDIUM | V3 Helm values.yaml 환경별 배포 (L2525) |
| 10 | BGNR-021 | AINV 안전장치 4종 | LOW | I-9 Cost Manager 3단계 경보(L1464) + I-19 Approval(L1404) |
| 11 | D202-053 | 사고 과정 표시 구현 (S7B-007) | LOW | I-1 Intent Detector 사고 수준 분류(L1399) + D-1 Think Engine(L1599) |
| 12 | D204-083 | 응답 결과 최소 필드 | LOW | ResponseEnvelope 5필드(L451) + DecisionSchema(L1548) |
| 13 | D204-125 | 분산 트레이싱 통합 (OpenTelemetry) | HIGH | V2-P2 #30 "분산 트레이싱" (L2028, S7AE-361) — **v23 패치로 이미 추가** |
| 14 | D205-126 | 언어 학습 지원 | HIGH | V2-P2 #115 "언어 학습 특화" (L2113, S7NP-056) |
| 15 | D205-127 | 독서 어시스턴트 | HIGH | V1-P3 #46 "독서 관리" (L1630, S7NP-061) |
| 16 | D205-128 | 퀴즈/테스트 자동 생성 | HIGH | V1-P3 #43 "퀴즈 자동 생성" (L1627, S7NP-049) |
| 17 | D205-130 | 학습 분석 대시보드 | HIGH | V2-P2 #114 "학습 분석 대시보드" (L2112, S7NP-051) |
| 18 | D205-134 | 책 요약 + 독서 관리 | HIGH | V1-P3 #46 "독서 관리" (L1630, S7NP-061) |
| 19 | D205-139 | 목표 관리 (OKR/SMART) | HIGH | V1-P3 #47 "학습 목표 관리"(L1631) + #54 "목표 설정/추적"(L1638) |
| 20 | D205-140 | 시간 관리 (포모도로) | HIGH | V1-P3 #55 "집중 모드 (포모도로)" (L1639, S7NP-096) |
| 21 | D205-145 | 네트워킹/인맥 관리 | HIGH | V2-P2 #99 "사회적 관계 관리" (L2097, S7NP-098) |
| 22 | D206-024 | SourceQoD 스코어 산출/기록 모듈 | HIGH | V1-P1 I-15 QoD Evaluator (L1401) |
| 23 | D206-202 | M-035 투자 리서치 노트 | HIGH | V1-P3 #18 "M-027 연구 노트 관리" (L1602, D206-198) |
| 24 | S7FI-295 | 한국 파생상품 분석 | HIGH | V3-P2 #10 파생상품 분석(그릭스/Black-Scholes) (L2927) |
| 25 | S7NP-078 | 교육 접근성 | LOW | V2-P2 #28 "B-030 접근성" (L2026, S7AE-345) |
| 26 | S7NP-120 | 웰니스 접근성 | LOW | V2-P2 #28 "B-030 접근성" (L2026, S7AE-345) |

---

## 3. BORDERLINE 1건

| feature_id | feature_name | severity | 사유 |
|-----------|-------------|----------|------|
| S7AE-321 | B-006 개발 로드맵 | HIGH | feature_name 오기재 의심. 실제 S7B-006은 "실시간 웹 검색 통합(Search Grounding)"이며 PART2 L1593 E-2 Web Search(Tavily MCP)로 이미 커버됨. 별도 추가 불필요. |

---

## 4. DESIGN_ONLY 249건 상세 분류

### 4.1 시스템/데이터설계 TITLE_ONLY — 140건

SOT에 S7AE-xxx 접두사의 "C-nnn 시스템설계" / "D-nnn 데이터설계" 형식. ID 자체가 SOT에 미존재하며, 실제 구현 기능은 S7C-xxx(UI/UX) / S7D-xxx(메모리/저장소) 시리즈에 별도 정의되어 있고 이미 PART2에 반영 완료.

| 패턴 | 건수 | severity 분포 | feature_id 범위 |
|------|------|--------------|----------------|
| C-045~C-104 시스템설계 | 60 | HIGH 60 | S7AE-396~455 |
| D-001~D-082 데이터설계 | 80 | HIGH 52, MEDIUM 12, LOW 16 | S7AE-456~537 |

### 4.2 운영/테스트/보안 설계 TITLE_ONLY — 10건

| feature_id | feature_name | severity |
|-----------|-------------|----------|
| S7AE-542 | E-005 운영 | MEDIUM |
| S7AE-543 | E-006 운영 | MEDIUM |
| S7AE-544 | E-007 운영 | MEDIUM |
| S7AE-545 | E-008 운영 | MEDIUM |
| S7AE-546 | E-009 운영 | MEDIUM |
| S7AE-547 | E-010 운영 | MEDIUM |
| S7AE-548 | E-011 운영 | MEDIUM |
| S7AE-552 | SRE 대시보드 | MEDIUM |
| S7AE-554 | 변경 관리 | MEDIUM |
| S7AE-555 | 용량 계획 | MEDIUM |

### 4.3 S7FI 비즈니스/전략 — 69건

SOT(STEP7-H 비즈니스 가이드) 영역. 코드 구현이 아닌 비즈니스 전략/분석 수준.

| 하위 분류 | 건수 | 대표 항목 |
|----------|------|---------|
| 한국 시장 상세 (주식/ETF/채권/파생/공시) | 18 | S7FI-287~304 |
| 비즈니스 분석 (SWOT/경쟁/마케팅) | 22 | S7FI-226~270 |
| 인프라/배포 전략 | 12 | S7FI-073~089 |
| 벤치마크/평가 도구 | 10 | S7FI-170~195 |
| 기타 비즈니스 | 7 | S7FI-062~285 |

### 4.4 S7AE 기타 설계 — 6건

| feature_id | feature_name | severity | 사유 |
|-----------|-------------|----------|------|
| S7AE-378 | OpenAPI 스펙 | HIGH | API 문서화 산출물, 구현 코드 아님 |
| S7AE-553 | 인시던트 관리 | HIGH | 운영 프로세스 수준 |
| S7AE-324 | B-004 기술 평가 | MEDIUM | 설계 단계 문서 |
| S7AE-337 | 장애 복구 전략 | MEDIUM | 설계 문서 (코드 구현은 SDAR로 커버) |
| S7AE-338 | 데이터 마이그레이션 전략 | MEDIUM | 설계 문서 (V2 마이그레이션 스크립트로 커버) |
| S7AE-353 | 마이크로서비스 설계 | MEDIUM | V1은 모놀리스, V3+ 설계 수준 |

### 4.5 S7NP 교육/웰니스/생활 — 5건

| feature_id | feature_name | severity | 사유 |
|-----------|-------------|----------|------|
| S7NP-071 | 교육 차별화 전략 | HIGH | 비즈니스 전략, 코드 구현 아님 |
| S7NP-112 | 웰니스 차별화 전략 | HIGH | 비즈니스 전략, 코드 구현 아님 |
| S7NP-179 | PolyBench | MEDIUM | 벤치마크 도구, QA 프로세스 |
| S7NP-180 | SWE-bench | MEDIUM | 벤치마크 도구, QA 프로세스 |
| S7NP-182 | HellaSwag | MEDIUM | 벤치마크 도구, QA 프로세스 |

### 4.6 D-series 상세설계 — 9건

| feature_id | feature_name | severity | 사유 |
|-----------|-------------|----------|------|
| D204-151 | 기여 가이드라인 (CONTRIBUTING.md) | MEDIUM | 문서 산출물 |
| D204-154 | R3~R6 추정 항목 (~102건) | MEDIUM | 메타 참조, 구현 항목 아님 |
| D206-237 | M-049~054 PKM 참고자료+로드맵 | MEDIUM | 참고자료/로드맵 문서 |
| D203-060 | W-33 오탐 방지 | LOW | 검증 프로세스 규칙, 코드 구현 아님 |
| D203-071 | P2 승인 조건 정의 | LOW | 정책 정의, 코드 구현은 I-19로 커버 |
| D204-072 | 멀티 LLM 허브 패턴 (A-1 기반) | LOW | 아키텍처 패턴 참조, A-1 MultiBrain으로 커버 |
| D204-076 | E-Series 확장 매핑 | LOW | 매핑 문서, 구현 항목 아님 |
| D204-077 | 학습/웰니스/투자 서비스 통합 | LOW | 통합 전략, 개별 모듈로 이미 커버 |
| D207-157 | Decoupled 자체진화 범위 정의 | LOW | 범위 정의 문서, S-8 Self-evo로 커버 |

### 4.7 기능그룹 (BGNR/AINV/BASE 등) — 0건

해당 없음 (전부 ALREADY_COVERED 또는 다른 그룹으로 분류됨)

### 4.8 기타 — 10건

| feature_id | feature_name | severity | 사유 |
|-----------|-------------|----------|------|
| P30-072 | IDEA 40건 로드맵 항목 추적 | HIGH | 프로젝트 관리/기획, SOT에 ID 미존재 |
| DD7-019 | 백테스팅 최소 5년 기간 규칙 | MEDIUM | 비즈니스 규칙 파라미터, 코드 구현은 백테스트 모듈에 내포 |
| S7JM-121 | LlamaIndex 통합 | MEDIUM | LlamaIndex는 기술 스택 선택지, RAG 파이프라인(I-2)으로 커버 |
| S7JM-210 | 크라우드소싱 품질 평가 | MEDIUM | QA 프로세스 |
| DD7-020 | 투자 전략별 백테스트 구성 | LOW | 비즈니스 규칙, 백테스트 모듈에 내포 |
| DD7-021 | 위험 관리 파라미터 설정 | LOW | 비즈니스 규칙, I-9 Cost Manager에 내포 |
| DD7-022 | 한국 시장 특화 지표 | LOW | 비즈니스 데이터 설정 |
| DD7-023 | 투자 성과 벤치마크 | LOW | 벤치마크 도구 |
| DD7-024 | 포트폴리오 리밸런싱 규칙 | LOW | 비즈니스 규칙, 리밸런싱 엔진에 내포 |
| DD7-025 | 세금/수수료 최적화 규칙 | LOW | 비즈니스 규칙, V3 범위 |

---

## 5. 최종 판정

| 항목 | 결과 |
|------|------|
| PART2에 추가 반영 필요 (SHOULD_ADD) | **0건** |
| 이미 커버됨 (ALREADY_COVERED) | 26건 — 별도 조치 불필요 |
| 경계 사례 (BORDERLINE) | 1건 — feature_name 오기재 의심, 실제 기능은 이미 커버 |
| 설계/문서/전략 수준 (DESIGN_ONLY) | 249건 — 코드 구현 대상 아님 |

> **276건 전체가 PART2 미반영 상태이나, SOT 기준 재검토 결과 추가 반영이 필요한 항목은 0건입니다.**
> 기존 RECLASSIFIED 판정이 적절했음을 확인합니다.

---

## 6. 상세 데이터 참조

- 전체 276건 재검토 결과: `recheck_276_consolidated.json`
- 그룹별 결과: `recheck_group_a.json` / `recheck_group_b.json` / `recheck_group_c.json`
- 원본 분류: `v10_step2_integrated_result.json` (final_classification=RECLASSIFIED 필터)
