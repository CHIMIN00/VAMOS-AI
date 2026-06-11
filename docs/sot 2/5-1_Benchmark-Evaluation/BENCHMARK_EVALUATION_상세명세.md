# 5-1. Benchmark & Evaluation 상세명세

> **Tier**: 5 - Quality / Cross-cutting
> **Part2 상태**: PARTIAL (runner framework + 2 concrete only)
> **SOT 근거**: STEP7-G, PHASE_B5
> **Part2 위치**: V1-Phase 5 품질 섹션, V2/V3 벤치마크 항목 산재

---

## 개요

VAMOS AI의 벤치마크 평가 체계. Part2에는 벤치마크 러너 프레임워크와 2개 구체적 벤치마크만 정의되어 있으며, 개별 벤치마크 채점 기준, 테스트 데이터셋 구성, 도메인별 커스텀 벤치마크, 인간 평가 프로세스, 신규 테스트 항목 등이 부재.

---

## 섹션 A: 표준 벤치마크 평가 루브릭

### A-1. MMLU (Massive Multitask Language Understanding)

| 항목 | 상세 |
|------|------|
| **측정 대상** | 57개 과목 다중선택 문제 (STEM, 인문, 사회, 전문직) |
| **평가 방식** | 5-shot, 정답 일치 (exact match) |
| **채점 기준** | 정답률 (accuracy) per subject → macro average |
| **VAMOS 목표** | >= 85% (전체), >= 80% (한국어 번역 버전) |
| **한국어 특화** | KMMLU (한국어 MMLU) 병행 평가, 한국 법/역사/문화 과목 추가 |
| **데이터셋** | 14,042 문항 (표준), + 2,000 한국어 커스텀 |

**채점 세부 규칙**:
- 모델 출력에서 A/B/C/D 추출 (정규식: `^[A-D]` 또는 `answer is [A-D]`)
- 추출 실패 시: 오답 처리 (penalty for ambiguity)
- 과목별 가중치: 균등 (1/57)
- 신뢰구간: bootstrap 95% CI 리포트

### A-2. HumanEval (코드 생성)

| 항목 | 상세 |
|------|------|
| **측정 대상** | 164개 Python 함수 생성 문제 |
| **평가 방식** | pass@1, pass@5, pass@10 (샌드박스 실행) |
| **채점 기준** | 단위 테스트 통과 여부 (binary) |
| **VAMOS 목표** | pass@1 >= 85% |
| **확장** | HumanEval+ (보강된 테스트 케이스), MultiPL-E (다중 언어) |

**채점 세부 규칙**:
- 코드 추출: `\`\`\`python` ... `\`\`\`` 블록 또는 함수 본문
- 실행 환경: Docker 샌드박스, Python 3.11, 타임아웃 10초/문제
- pass@k 계산: `1 - C(n-c, k) / C(n, k)` (n=시도횟수, c=통과횟수)
- 부분 점수 없음 (pass or fail)

### A-3. MBPP (Mostly Basic Python Problems)

| 항목 | 상세 |
|------|------|
| **측정 대상** | 974개 기초~중급 Python 문제 |
| **평가 방식** | pass@1 (3개 테스트 케이스 전부 통과) |
| **채점 기준** | 테스트 통과 + 문법 정확성 |
| **VAMOS 목표** | pass@1 >= 75% |
| **필터** | sanitized 버전 (427개) 사용 권장 |

### A-4. LogicKor (한국어 논리/추론)

| 항목 | 상세 |
|------|------|
| **측정 대상** | 한국어 논리 추론, 독해, 수학, 코딩 (50문항) |
| **평가 방식** | GPT-4 심판 (judge) + 인간 평가 |
| **채점 기준** | 1~10점 척도, 정확성(40%) + 논리성(30%) + 완성도(30%) |
| **VAMOS 목표** | >= 8.0/10 (GPT-4 judge 기준) |
| **특화** | 한국어 능력 측정에 특화, VAMOS의 한국어 우선 전략 핵심 벤치마크 |

**채점 루브릭 (1~10)**:
- 1~3: 오답 또는 무관한 응답, 논리 비약 심각
- 4~5: 부분 정답, 핵심 누락 또는 논리 오류 존재
- 6~7: 대체로 정확, 사소한 누락 또는 개선 여지
- 8~9: 정확하고 논리적, 완성도 높음
- 10: 완벽한 응답, 추가 가치 제공

### A-5. ARC-AGI (Abstraction and Reasoning Corpus)

| 항목 | 상세 |
|------|------|
| **측정 대상** | 시각 패턴 추론 (그리드 변환 규칙 추론) |
| **평가 방식** | 정답 그리드 exact match (3회 시도 허용) |
| **채점 기준** | 정답률 (pass@3) |
| **VAMOS 목표** | >= 30% (현재 AI SOTA ~50%) |
| **의의** | AGI 수준 추상적 추론 능력 측정, 어렵지만 추적 가치 있음 |

**평가 프로토콜**:
- 입력: 2~5개 예시 쌍 (input grid → output grid) + 테스트 input
- 출력: 예측 output grid (최대 3회 시도)
- 그리드 크기: 최대 30x30, 10가지 색상
- 정답 판정: pixel-perfect match

---

## 섹션 B: 테스트 데이터셋 명세

### B-1. 벤치마크별 데이터셋 구성

| 벤치마크 | 전체 크기 | 평가 사용 | 샘플링 전략 | 골든 후보 풀 | 골든셋 (V1) | Phase |
|---------|----------|----------|------------|-------------|------------|-------|
| MMLU | 14,042 | 전체 | 전수 (표준) | 570개 (과목당 10개) | **50문항** (층화 추출 seed=42) | P0 |
| HumanEval | 164 | 전체 | 전수 (소규모) | 20개 (난이도 분포) | **20문항** (전수) | P0 |
| MBPP | 974 (427 sanitized) | 427 | sanitized 전수 | 50개 | **50문항** (전수) | P0 |
| LogicKor | 50 | 전체 | 전수 | 50개 (전체가 골든) | **50문항** (전수) | P0 |
| ARC-AGI | 400 (public) | 100 eval | 층화 샘플링 | 30개 | — (Phase 2 추가) | P2 |

> **용어 구분**: "골든 후보 풀"은 각 벤치마크에서 골든셋 추출 대상이 되는 상위 집합. "골든셋 (V1)"은 후보 풀에서 실제 추출하여 `benchmarks/golden_set/`에 저장하는 최종 문항. MMLU는 570개 후보 중 50문항만 V1 골든셋으로 선별.

### B-2. 골든셋 (스모크 테스트용)

- **목적**: 배포 전 빠른 검증 (5분 이내)
- **구성**: 각 벤치마크에서 난이도/도메인 분포를 유지하며 추출 (seed=42)
- **V1 규모**: 170문항 (MMLU 50 + HumanEval 20 + MBPP 50 + LogicKor 50) — Phase 0 F-04
- **V2 규모**: ~200문항 (V1 + ARC-AGI 30) — Phase 2 S7G-078 v2
- **최종 목표**: S7G-078 500건 (분기별 교체·신규 추가로 점진적 확장)
- **업데이트**: 분기별 (데이터 오염 방지를 위해 최소 20% 신규 문항 추가, R-18-4)
- **저장**: `benchmarks/golden_set/` (Git LFS + 암호화, 접근 권한 제한)

### B-3. 커스텀 VAMOS 데이터셋

| 이름 | 규모 | 설명 |
|------|------|------|
| VAMOS-Korean-QA | 500 | 한국어 질의응답 (뉴스/법률/의료/일상) |
| VAMOS-Agent-Tasks | 200 | 에이전트 태스크 완수 시나리오 |
| VAMOS-Memory-Recall | 100 | 장기 기억 활용 정확도 테스트 |
| VAMOS-Tool-Selection | 150 | 올바른 도구 선택 정확도 |
| VAMOS-Safety | 300 | 안전 가드레일 테스트 (jailbreak, PII, harmful) |

---

## 섹션 C: 도메인별 VAMOS Benchmark Suite (VBS)

### VBS-12: Agent Benchmark

| 메트릭 | 측정 방법 | 목표 |
|--------|----------|------|
| Task completion rate | 20개 시나리오 자동 실행 | >= 80% |
| Plan quality score | LLM judge (1~5) | >= 4.0 |
| Average steps to completion | 스텝 수 카운트 | <= 10 |
| HITL intervention rate | 사람 개입 빈도 | < 20% |
| Tool selection accuracy | 정답 도구 선택 비율 | >= 90% |

### VBS-13: Code Benchmark

| 메트릭 | 측정 방법 | 목표 |
|--------|----------|------|
| HumanEval pass@1 | 표준 HumanEval | >= 85% |
| MBPP pass@1 | sanitized MBPP | >= 75% |
| Bug detection rate | 50개 버그 포함 코드 | >= 70% |
| Code review quality | LLM judge (1~5) | >= 3.5 |
| Multi-file edit accuracy | 10개 리팩토링 시나리오 | >= 60% |

### VBS-14: Knowledge Benchmark

| 메트릭 | 측정 방법 | 목표 |
|--------|----------|------|
| RAG precision@10 | 관련 문서 검색 정확도 | >= 85% |
| Memory recall accuracy | 이전 대화 참조 정확도 | >= 80% |
| Knowledge graph query | Cypher 쿼리 정답률 | >= 70% |
| Cross-session consistency | 세션 간 일관성 점수 | >= 90% |

### VBS-15: Education Benchmark

| 메트릭 | 측정 방법 | 목표 |
|--------|----------|------|
| Explanation quality | 학습자 이해도 측정 (pre/post test) | >= 30% 향상 |
| Adaptive difficulty | 난이도 적응 정확도 | >= 80% |
| Flashcard generation quality | 인간 평가 (1~5) | >= 4.0 |
| Quiz generation accuracy | 정답/오답 구분 정확성 | >= 95% |
| Learning path coherence | 경로 일관성 점수 | >= 85% |

### VBS-16: Wellness Benchmark

| 메트릭 | 측정 방법 | 목표 |
|--------|----------|------|
| Emotion detection accuracy | 7가지 감정 분류 정확도 | >= 80% |
| Response empathy score | 인간 평가 (1~5) | >= 4.0 |
| Safety boundary compliance | 의료 경계 준수율 | 100% |
| CBT technique application | CBT 기법 적절 사용 비율 | >= 80% |
| Crisis detection sensitivity | 위기 감지 재현율 | >= 95% |

### VBS-17: Investing Benchmark (v12 추가)

| 메트릭 | 측정 방법 | 목표 |
|--------|----------|------|
| Financial analysis accuracy | 10개 케이스 스터디 | >= 70% |
| Risk assessment quality | 전문가 평가 (1~5) | >= 3.5 |
| Portfolio suggestion validity | 기본 제약 준수율 | 100% |
| Disclaimer compliance | 면책 조항 포함 여부 | 100% |

---

## 섹션 D: 인간 평가 프로세스

### D-1. 평가자 가이드

**평가자 자격**:
- 도메인 전문가 (해당 분야 경력 3년+) 또는 언어학/AI 전공자
- 한국어 원어민 (한국어 평가 시)
- 평가 교육 이수 (2시간 온라인 세션)
- 시범 평가 통과 (10개 문항, Cohen's kappa >= 0.6)

**평가 규칙**:
- 각 응답 독립적 평가 (이전 평가에 영향받지 않도록)
- 최소 2명 평가자가 동일 항목 평가
- 점수 차이 2점+ 시 3번째 평가자 투입
- 평가 세션 최대 2시간, 이후 30분 휴식 필수

### D-2. 점수 체계

| 점수 | 기준 | 예시 |
|------|------|------|
| 5 | 완벽 - 정확하고, 완성도 높고, 추가 가치 제공 | 질문 이상의 통찰 제공 |
| 4 | 우수 - 정확하고 충분하지만 탁월하지는 않음 | 정확한 답변, 적절한 설명 |
| 3 | 보통 - 대체로 정확하지만 일부 누락/부정확 | 핵심은 맞으나 디테일 부족 |
| 2 | 미흡 - 부분적으로만 정확, 주요 오류 존재 | 핵심 누락 또는 오해 |
| 1 | 실패 - 오답, 무관한 응답, 위험한 내용 | 환각, 잘못된 정보 |

### D-3. Cohen's Kappa 일치도

```
κ = (P_o - P_e) / (1 - P_e)

P_o = 관찰된 일치율
P_e = 우연 일치 기대율
```

| κ 범위 | 일치 수준 | 조치 |
|--------|----------|------|
| 0.81~1.00 | 거의 완벽 | 합격 |
| 0.61~0.80 | 실질적 일치 | 합격 (권장 수준) |
| 0.41~0.60 | 보통 | 추가 교육 후 재평가 |
| 0.21~0.40 | 약한 일치 | 가이드라인 재검토, 재교육 필수 |
| < 0.20 | 불일치 | 평가 무효, 전면 재설계 |

**목표**: 모든 평가 세션에서 κ >= 0.6 유지

### D-4. 인간 평가 스케줄

- **릴리스 평가**: 각 버전 릴리스 전 100개 항목 (2명 x 100 = 200 평가)
- **월간 샘플링**: 실 사용 대화 중 50개 랜덤 샘플 평가
- **분기별 전체**: VBS 전 항목 인간 평가 (500+ 항목)
- **소요 시간**: 항목당 평균 3분, 100개 기준 5시간 (2명)

---

## 섹션 E: +190개 신규 테스트 커버리지

> Part2 6.3 헤더에 언급된 신규 항목 분류

### E-1. 카테고리별 분류

| 카테고리 | 항목 수 | 테스트 유형 |
|---------|---------|-----------|
| Core Engine (ORANGE CORE) | 25 | 단위 + 통합 |
| Memory System (L0~L3) | 20 | 통합 + 회귀 |
| Search/RAG Pipeline | 18 | 통합 + 성능 |
| Agent Framework | 22 | E2E + 시나리오 |
| UI/UX Components | 30 | 컴포넌트 + 스냅샷 |
| MCP Integration | 15 | 통합 + 모의(mock) |
| Workflow/RPA | 12 | E2E + 시나리오 |
| Security/Safety | 20 | 퍼징 + 침투 |
| Performance | 15 | 벤치마크 + 부하 |
| 한국어 특화 | 13 | 정확도 + 회귀 |
| **합계** | **190** | |

### E-2. 우선순위별 분류

| 우선순위 | 항목 수 | 구현 시기 |
|---------|---------|----------|
| CRITICAL (배포 차단) | 45 | V1 |
| HIGH | 60 | V1~V2 |
| MEDIUM | 55 | V2 |
| LOW | 30 | V3 |

### E-3. 테스트 자동화 전략

- **단위 테스트**: pytest + hypothesis (property-based)
- **통합 테스트**: pytest + testcontainers (DB/서비스)
- **E2E 테스트**: Playwright + Tauri WebDriver
- **성능 테스트**: pytest-benchmark + locust (부하)
- **보안 테스트**: semgrep + custom fuzzer
- **커버리지 도구**: coverage.py (Python) + tarpaulin (Rust)
- **리포팅**: Allure Report (HTML), JUnit XML (CI)
