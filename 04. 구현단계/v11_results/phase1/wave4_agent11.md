## [Agent 11] v11 검증 결과
> **PART2 버전**: v24.0.0
> **에이전트 버전**: v2.0.0

### 담당 GAP
- GAP-17: 비용 모델 적정성
- GAP-18: 타임라인 적정성

### 검사 통계
- 검사 항목 수: 26건
- ISSUE: 10건 / OK: 14건 / N/A: 2건

### 심각도 기준
- BLOCKER: 구현 진행 시 시스템 오동작 유발 또는 논리적 모순
- HIGH: 내부 불일치로 혼란 유발 (수정 필수)
- MEDIUM: 개선 권장 (품질 향상)
- LOW: 표기/포맷 수준 (선택적 수정)

---

## GAP-17 비용 분석: 버전별 비용 상한 vs 기술스택 실비용 추정

### V1 실비용 추정 (비용 상한: ₩40,000/월 = ~$30/월)

| 항목 | 월 비용 추정 | 근거 |
|------|-------------|------|
| Ollama (로컬 LLM) | ₩0 | 로컬 실행, llama3.2:3b / llama3.1:8b |
| BGE-M3 임베딩 (로컬) | ₩0 | 로컬 FlagEmbedding |
| Chroma Vector DB (embedded) | ₩0 | 로컬 내장 |
| SQLite | ₩0 | 로컬 파일 |
| gpt-4o-mini (fallback) | ₩5,000~15,000 | OpenAI mini: $0.15/1M input, $0.60/1M output |
| Claude API (5-Agent Pipeline) | ₩5,000~15,000 | Claude 3.5 Sonnet: $3/1M input, $15/1M output |
| Perplexity/Gemini/ChatGPT/Copilot | ₩3,000~10,000 | 각 API 소량 호출 |
| MCP 외부 서버 | ₩0~5,000 | 무료 티어 + 소량 |
| RSS/데이터 수집 (RT-BNP V1) | ₩0 | RSS 무료 |
| **합계 추정** | **₩13,000~45,000** | |

### V2 실비용 추정 (비용 상한: ₩93,000/월 = ~$70/월)

| 항목 | 월 비용 추정 | 근거 |
|------|-------------|------|
| VPS (Docker Compose) | ₩10,000~20,000 | 저가 VPS |
| PostgreSQL/Qdrant/Neo4j/Redis | ₩0 (VPS 포함) | Docker Compose 내 |
| LLM API (10 에이전트) | ₩15,000~35,000 | Sonnet Lead + Haiku Sub |
| REST API 데이터 (T2+T3+T4) | ₩5,000~10,000 | 6.10.1 명시 |
| LlamaGuard GPU | ? (ISSUE #3) | GPU 필요 |
| **합계 추정** | **₩30,000~65,000** (GPU 제외) | |

### V3 실비용 추정 (비용 상한: ₩266,000/월 = ~$200/월)

| 항목 | 월 비용 추정 | 근거 |
|------|-------------|------|
| Hetzner CX31 대안 합계 | ~$123-142 | PART2 L2606 명시 |
| AWS/GCP K8s 정식 | $300~600+ | EKS/GKE + GPU + 관리형 DB |

---

### ISSUE 목록

| # | GAP | PART2행 | 이슈 내용 | 비교 대상(PART2 내) | 심각도 | v24-DELTA |
|---|-----|---------|----------|-------------------|--------|-----------|
| 1 | GAP-17 | L2526, L2597 | **V3 비용 상한 ₩266,000/월은 정식 K8s 배포 시 심각하게 부족**. AWS EKS + A10G GPU($871/월 on-demand) + 관리형 DB 합산 $1,000+/월. Hetzner 대안은 Docker Compose 기반으로 "K8s Deploy" 로드맵(L32)과 모순. | L32 "K8s Deploy" vs L2598 "Docker Compose" | HIGH | |
| 2 | GAP-17 | L2544 | **V3-003 GPU 비용 ~$144/월 근거 불명**. On-demand A10G는 $533~871/월. RunPod Serverless만 $200 이내 가능하나 24시간 vLLM 서빙과 양립 불가. | L2606 합계 $123-142 vs A10G 실가격 | MEDIUM | |
| 3 | GAP-17 | L2388 | **V2 LlamaGuard L3 GPU 비용 미반영**. GPU VPS($150+/월)는 ₩93,000 상한 초과. 로컬 GPU 전제 시 명시 필요. | L1886 ₩93,000 vs L2388 "CUDA GPU 6GB+" | HIGH | |
| 4 | GAP-17 | L1529 | **I-9 비용 경보 임계값 불일치**: 70%/85%/95% 3단계 vs config 80%/100% 2단계. | L1529 vs L209-210 | HIGH | [v24-DELTA] |
| 5 | GAP-17 | L3469 | **Agent Teams V1 비용 ₩1,300/일 근거 불명**. 실추정 ~₩355/일로 3.7배 마진. | L207 daily_limit=1300 vs 실호출 비용 | LOW | |
| 6 | GAP-18 | L1552 | **V1-Phase 2: 59개 항목을 2주에 구현 (v10 추가 50건)**. 일 5.9개 항목으로 비현실적. | L1552 "Week 5-6" vs 59개 항목 | BLOCKER | [v24-DELTA] |
| 7 | GAP-18 | L1644 | **V1-Phase 3: 59개 항목을 2주에 구현 (v10 추가 44건)**. 핵심 아키텍처 + 44개 도메인 기능 혼재. | L1644 "Week 7-8" vs 59개 항목 | BLOCKER | [v24-DELTA] |
| 8 | GAP-18 | L2056 | **V2-Phase 2: 105개 항목을 3주에 구현 (v10 추가 95건)**. 일 7개 항목으로 극도 과중. | L2056 "Week 4-6" vs 105개 항목 | BLOCKER | [v24-DELTA] |
| 9 | GAP-18 | L1827 | **V1-Phase 6 병렬 실행이 Stage Gate 규칙과 잠재적 모순**. Phase 4 완료 전 Phase 6 시작 가능 여부 불명확. | L1781 Gate 규칙 vs L1827 "Week 10-12 병렬" | MEDIUM | |
| 10 | GAP-17 | L4035, L3953 | **DCL V3 비용(+₩15,000) < RT-BNP V3 비용(+₩30,000~50,000) 모순**. DCL-FIN이 RT-BNP 사용하므로 포함관계 불명확. | L4035 vs L3954 | HIGH | |

### OK 샘플 (검증 완료 확인)

| # | GAP | PART2행 | 확인 내용 | 결과 |
|---|-----|---------|----------|------|
| 1 | GAP-17 | L102 | V0 비용 ~₩5,000 — 로컬 전용으로 적정 | OK |
| 2 | GAP-17 | L208, L383 | config cost.monthly_limit=40000 두 곳 일치 | OK |
| 3 | GAP-17 | L1453 | V1 ₩40,000/월 — 로컬 Ollama 중심 달성 가능 | OK |
| 4 | GAP-17 | L2606 | V3 Hetzner 대안 $123-142/월 적산 합리적 | OK |
| 5 | GAP-17 | L3952 | RT-BNP V1 +₩0 RSS 무료 적정 | OK |
| 6 | GAP-17 | L4156 | V0 비용 상한 = V1 동일 적용 정합 | OK |
| 7 | GAP-17 | L4167 | 비용 엔진 ₩40,000 ABSOLUTE LOCK 일치 | OK |
| 8 | GAP-18 | L109 | V0-STEP-1 Day 1-2 스캐폴딩 적정 | OK |
| 9 | GAP-18 | L1458 | V1-Phase 1 Week 1-4 ORANGE CORE 17모듈 적정 | OK |
| 10 | GAP-18 | L1738 | V1-Phase 4 Week 9-10 UI/UX 19항목 적정 | OK |
| 11 | GAP-18 | L1891 | V2-Phase 1 Week 1-3 인프라 마이그레이션 7항목 적정 | OK |
| 12 | GAP-18 | L2531 | V3-Phase 1 Week 1-4 인프라 스케일업 적정 | OK |
| 13 | GAP-18 | L2998 | V3-Phase 3 Week 11-16 고급기능 14항목 적정 | OK |
| 14 | GAP-18 | L4125-4135 | 6.13 작업량 합계 ~462건 영역별 적산 일치 | OK |

### N/A 항목

| # | GAP | 사유 |
|---|-----|------|
| 1 | GAP-17 | V2/V3 클라우드 벤더 미확정으로 정밀 추정 불가 |
| 2 | GAP-18 | v10 추가 200건 개별 복잡도(person-day) 미정의 |

---

### 종합 소견

**GAP-17 비용 모델**: V1은 적정. V2는 LlamaGuard GPU 비용 미반영 시 조건부 적정. V3는 Hetzner 대안으로만 달성 가능하며 정식 K8s 배포 시 상한의 2.5~5배 초과 — Hetzner 경로 공식화 또는 상한 재검토 필요.

**GAP-18 타임라인**: v10 Phase 2 대량 추가(200건)로 **V1-Phase 2/3, V2-Phase 2가 BLOCKER급 과부하**. Phase 기간은 v10 추가 전 설계 기준이 그대로 유지됨. 별도 Phase 신설 또는 기간 확장 권장. V0, V1-Phase 1/4/5, V2-Phase 1, V3-Phase 1/3은 적정.