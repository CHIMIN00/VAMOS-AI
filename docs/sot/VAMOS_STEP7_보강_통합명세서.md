# VAMOS STEP7 보강 통합명세서 -- TITLE_ONLY 항목 상세 확장

> **문서 버전**: v1.0
> **작성일**: 2026-02-23
> **범위**: STEP7 1,545건 중 TITLE_ONLY(약 29%, ~448건) 항목의 상세 구현 명세
> (주: 본 문서 전반의 1,545 표기는 2026-06-11 재계수로 1,485 정정 — 유령 ID 60, 마스터인덱스 실측 주석 정본)
> **원칙**: 껍데기(제목만) 절대 불가 -- 모든 항목에 구현 방식, 기술 스택, 스키마, API, 연동 모듈 명시
> **VAMOS 연결**: I/E/S/A 시리즈, 5 Gates, 9-State Machine, 3-Part Output 연동점 포함

---

## 문서 구조 안내

STEP7 마스터인덱스 16개 카테고리(A~P + 보강) 중, R1~R6 라운드 문서에서 이미 상세 스펙이 작성된 항목(약 71%)을 제외하고, **TITLE_ONLY 상태**로 남아 있는 항목들을 카테고리별로 식별하여 상세 내용을 확장한다.

### TITLE_ONLY 판별 기준
1. 마스터인덱스에 "요약" 1줄만 존재하고, R1~R6 문서에 구현 상세가 없는 항목
2. R1~R6에 "~추정" / "원본 소스 파일 참조" 로 표기된 F~M 카테고리 대부분 항목
3. 보강 추가항목 중 B-ADD ~ I-ADD의 개별 구현 스펙 미작성 항목

### 카테고리별 TITLE_ONLY 분포 (추정)

| 카테고리 | 총 건수 | 상세 완료 | TITLE_ONLY | 비율 |
|---------|--------|----------|-----------|------|
| A (경쟁분석/혁신) | 316 | ~180 | ~136 | 43% |
| B (대화프로세스) | 35 | 35 | 0 | 0% |
| C (UI/UX) | 104 | 104 | 0 | 0% |
| D (메모리/저장소) | 82 | 82 | 0 | 0% |
| E (보안/안전) | 92 | 92 | 0 | 0% |
| F (인프라/배포) | 96 | ~30 | ~66 | 69% |
| G (벤치마크/평가) | 88 | ~25 | ~63 | 72% |
| H (비즈니스모델) | 78 | ~20 | ~58 | 74% |
| I (AI Investing) | 106 | ~40 | ~66 | 62% |
| J (멀티모달) | 98 | ~25 | ~73 | 74% |
| K (에이전트프로토콜) | 86 | ~25 | ~61 | 71% |
| L (개발자도구) | 82 | ~20 | ~62 | 76% |
| M (PKM/지식관리) | 78 | ~20 | ~58 | 74% |
| N (워크플로우) | 44 | 44 | 0 | 0% |
| O (교육/학습) | 36 | 36 | 0 | 0% |
| P (건강/웰니스) | 42 | 42 | 0 | 0% |
| 보강 | 82 | ~50 | ~32 | 39% |
| **합계** | **1,545** | **~870** | **~675** | **44%** |

> 주: B~E, N~P 카테고리는 개별 작업가이드에서 전수 상세 스펙이 이미 작성됨. F~M, A일부, 보강일부가 핵심 보강 대상.

---

## 1. 카테고리 A -- 경쟁분석/혁신기술 (TITLE_ONLY ~136건)

### 1.1 현황 분석

A 카테고리 316건 중:
- Part A~E (Claude/GPT/Gemini/Kimo/VAMOS강점): 작업가이드에서 상세 스펙 완료 (~174건)
- Part F (혁신기술 99건): R1에서 V1 CRITICAL ~22건 상세 완료, 나머지 ~77건 TITLE_ONLY
- Part G~P (추가 경쟁사 98건): 마스터인덱스 요약만 존재, 대부분 TITLE_ONLY

### 1.2 Part F -- 혁신기술 TITLE_ONLY 상세 확장 (주요 항목)

#### S7-F-023 | Digital Twin 사용자 모델링 | HIGH V1~V2
```
[구현 상세]
- 목적: 사용자의 디지털 트윈을 생성하여 행동 예측 및 맞춤 서비스 제공
- 구현 방식:
  ├─ L3 장기 메모리에서 사용자 행동 패턴 추출
  ├─ 패턴 벡터화: 시간대별 활동, 선호 주제, 대화 스타일, 의사결정 패턴
  ├─ Digital Twin Schema:
  │   {
  │     user_id: str,
  │     behavior_profile: {
  │       peak_hours: List[int],           # [9, 14, 21]
  │       topic_distribution: Dict[str, float],  # {"coding": 0.4, "investing": 0.3}
  │       response_length_pref: "concise"|"detailed",
  │       decision_speed: float,           # 0-1 (cautious ~ impulsive)
  │       risk_tolerance: float            # 0-1 (conservative ~ aggressive)
  │     },
  │     prediction_model: "gradient_boost"|"neural",
  │     last_updated: datetime,
  │     confidence: float
  │   }
  ├─ 예측 활용: 다음 질문 예측, 최적 응답 톤 사전 결정
  └─ 프라이버시: 로컬 전용, 사용자 opt-in, 삭제 가능

- VAMOS 아키텍처 연동:
  ├─ D2.0-06 (STORAGE/MEMORY): L3 메모리에서 데이터 수집
  ├─ D2.0-02 (ORANGE CORE): Stage 2 Analysis에서 Twin 데이터 참조
  ├─ 9-State Machine: PREDICT 상태에서 Twin 기반 사전 분석
  └─ 5 Gates: Policy Gate에서 Twin 데이터 프라이버시 검증

- 기술 스택: scikit-learn (V1), PyTorch (V2)
- V1: 규칙 기반 프로필 (즉시), V2: ML 기반 예측 (3개월)
```

#### S7-F-024 | Local+Cloud 하이브리드 실행 | HIGH V1
```
[구현 상세]
- 목적: 로컬 LLM과 클라우드 API를 동적으로 전환하여 비용/품질 최적화
- 구현 방식:
  ├─ HybridRouter 모듈:
  │   class HybridRouter:
  │     def route(self, query: Query) -> ModelEndpoint:
  │       sensitivity = self.classify_sensitivity(query)
  │       complexity = self.classify_complexity(query)
  │       budget_remaining = self.cost_gate.get_remaining()
  │
  │       if sensitivity == "high":
  │         return LocalEndpoint(model="llama4-scout")  # 민감 데이터 로컬 전용
  │       elif complexity == "low" and budget_remaining < threshold:
  │         return LocalEndpoint(model="phi-4")          # 간단 질문 + 예산 부족
  │       elif complexity == "high":
  │         return CloudEndpoint(model="claude-sonnet-4.6")  # 복잡한 분석
  │       else:
  │         return self.cost_optimal_route(query)        # 비용 최적 자동 선택
  │
  ├─ 네트워크 상태 감지: 오프라인 시 자동 로컬 전환
  ├─ 비용 추적: 클라우드 호출당 비용 기록, 일/월 예산 관리
  └─ 품질 피드백: 사용자 피드백 기반 라우팅 정책 학습

- VAMOS 아키텍처 연동:
  ├─ D2.0-04 (INFRA): LiteLLM 추상화 레이어 위에 구축
  ├─ D2.0-07 (SAFETY/COST): Cost Gate 연동, 비용 한도 초과 시 로컬 강제 전환
  ├─ I-9 (비용 상한): 월간 비용 한도 ₩10,000(V1) 준수
  └─ 5 Gates: Cost Gate에서 라우팅 결정 검증

- 기술 스택: Ollama (로컬), LiteLLM (추상화), Redis (캐시)
- V1: 즉시 구현, V2: ML 기반 자동 라우팅 (2개월)
```

#### S7-F-025 | Confidence-based 응답 전략 | HIGH V1
```
[구현 상세]
- 목적: LLM 응답의 신뢰도를 정량화하여 사용자에게 투명하게 전달
- 구현 방식:
  ├─ ConfidenceEstimator:
  │   def estimate(self, response: str, context: Context) -> ConfidenceScore:
  │     scores = {
  │       "source_coverage": self.eval_source_support(response, context.sources),
  │       "self_consistency": self.eval_consistency(response, n_samples=3),
  │       "knowledge_recency": self.eval_recency(context.timestamps),
  │       "domain_expertise": self.eval_domain_match(context.domain),
  │       "hallucination_risk": 1.0 - self.detect_hallucination(response)
  │     }
  │     return ConfidenceScore(
  │       overall=weighted_mean(scores),
  │       breakdown=scores,
  │       display_level=self.map_to_display(scores)  # "높음"/"보통"/"낮음"
  │     )
  │
  ├─ 표시 방식: 3-Part Output의 header에 신뢰도 바 표시
  ├─ 낮은 신뢰도 대응: 자동 면책 고지 + 추가 검증 제안
  └─ 투자 도메인: confidence < 0.7이면 자동으로 "참고용" 레이블

- VAMOS 아키텍처 연동:
  ├─ D2.0-02 (ORANGE CORE): Stage 6 Self-Check에서 신뢰도 산출
  ├─ I-6 (Self-check): QoD Score와 통합
  ├─ 3-Part Output: [header: confidence_bar] [body: 응답] [footer: 근거]
  └─ Evidence Gate: 신뢰도가 임계값 미만이면 Evidence Gate 재검증

- V1: 규칙 기반 신뢰도 (즉시), V2: ML 기반 정밀 신뢰도 (3개월)
```

#### S7-F-030 | Causal Reasoning Engine | HIGH V2
```
[구현 상세]
- 목적: 상관관계가 아닌 인과관계 기반 추론 능력 강화
- 구현 방식:
  ├─ 인과관계 그래프 구축:
  │   - KG(Knowledge Graph)에 인과 관계 edge 타입 추가
  │   - relation_type: "causes", "prevents", "enables", "correlates"
  │   - 강도: causal_strength: float (0-1)
  │
  ├─ 인과 추론 파이프라인:
  │   1. 질문 분석 → 인과 질문 감지 ("왜?", "때문에", "영향")
  │   2. KG 인과 경로 검색 (BFS on causal edges)
  │   3. 반사실 분석 (counterfactual): "만약 X가 아니었다면?"
  │   4. 교란 변수 식별 (confounding variables)
  │   5. 인과 강도 기반 결론 도출
  │
  ├─ 투자 도메인 특화:
  │   - "금리 인상 → 기술주 하락" 인과 체인 자동 구축
  │   - 역사적 인과 패턴 DB
  │   - 인과 vs 상관 자동 구분 레이블
  │
  └─ LLM 프롬프트 강화: Chain-of-Thought에 인과 추론 단계 추가

- VAMOS 아키텍처 연동:
  ├─ D2.0-06 (STORAGE): KG에 causal_edge 스키마 확장
  ├─ D2.0-02 (ORANGE CORE): Stage 2 Analysis에서 인과 질문 감지
  ├─ Evidence Gate: 인과 주장에 대한 근거 검증 강화
  └─ AI Investing: Quant Node에서 인과 분석 활용

- 기술 스택: NetworkX (V1 경량), DoWhy/CausalML (V2)
- V1: KG 인과 edge 수동 등록, V2: 자동 인과 추출 (4개월)
```

#### S7-F-040~060 | Continual Learning / Self-Evolution 관련 (대표 항목)
```
[S7-F-040] Continual Learning 프레임워크 | MED V2
- 대화/피드백에서 지속적으로 모델 성능 개선
- 구현: 사용자 피드백 -> reward_signal -> 프롬프트 최적화 (LoRA 미세 조정은 V3)
- fine_tune_policy: {"method": "prompt_tuning", "min_samples": 100, "eval_threshold": 0.8}
- VAMOS 연동: I-6 Self-check 피드백 루프, D2.0-06 학습 데이터 저장

[S7-F-045] Privacy-Preserving Learning | MED V2
- 로컬 데이터로 학습하되 프라이버시 보장
- 구현: Federated Learning 패턴 적용 (단일 사용자이므로 로컬 LoRA)
- 기법: Differential Privacy (epsilon=1.0), Gradient Clipping
- VAMOS 연동: D2.0-07 프라이버시 정책, PII 자동 제거 후 학습

[S7-F-050] Rollback / Version Control | HIGH V2
- 시스템 상태를 특정 시점으로 되돌리는 기능
- 구현:
  ├─ 스냅샷: daily_snapshot = {memory_state, kg_state, config, model_version}
  ├─ 롤백: rollback_to(snapshot_id) → 메모리/KG/설정 복원
  ├─ 버전 비교: diff(snapshot_a, snapshot_b)
  └─ 자동 백업: V1 일일 1회, V2 변경 이벤트마다
- VAMOS 연동: D2.0-04 백업 자동화, D2.0-06 스냅샷 저장

[S7-F-055] Dream Mode (비활성 시간 자기진화) | HIGH V2
- 사용자가 VAMOS를 사용하지 않는 시간에 자동 최적화 수행
- 구현:
  ├─ 야간 배치 작업:
  │   1. 메모리 정리: L0→L1→L2 승격/강등
  │   2. KG 업데이트: 새 사실 통합, 충돌 해소
  │   3. 캐시 최적화: TTL 만료 정리, 사전 워밍
  │   4. 성능 리포트 생성: 일일 사용 통계
  │   5. 프롬프트 최적화: 피드백 기반 시스템 프롬프트 개선
  ├─ 스케줄: cron "0 3 * * *" (매일 새벽 3시)
  ├─ 비용 제한: Dream Mode 일일 예산 ₩500 이하
  └─ 사용자 리포트: 아침에 "지난밤 개선 사항" 요약 표시
- VAMOS 연동: D2.0-05 스케줄러, I-9 비용 제한, D2.0-06 메모리 관리

[S7-F-060] Dream Mode 지식 정리 | HIGH V1
- 오프라인/유휴 시간에 축적된 지식을 정리·강화
- 구현:
  ├─ 중복 메모리 병합
  ├─ 약한 연결(weak link) KG 노드 강화
  ├─ 미사용 30일 이상 메모리 L3 아카이브 이동 (정본: 4계층 L0~L3)
  ├─ 새로운 패턴 발견 → 인사이트 메모 자동 생성
  └─ 전체 실행 시간 < 5분 (V1)
- VAMOS 연동: D2.0-06 4-Layer Memory(정본 L0~L3), KG (NetworkX V1 / Neo4j V2)
> [PART1 ST-02] 정본: 4계층(L0~L3). L4 Archive는 V2+ 참조용.
```

### 1.3 Part G~P -- 추가 경쟁사 분석 TITLE_ONLY 확장 (주요 항목)

#### Part G: xAI Grok (12건 중 TITLE_ONLY ~8건)
```
[S7-G-003] Grok 실시간 소셜 데이터 연동 패턴 | HIGH V2
- Grok의 X/Twitter 실시간 데이터 접근 패턴을 VAMOS에 적용
- 구현:
  ├─ 소셜 미디어 MCP 서버: X/Twitter, Reddit, Hacker News API
  ├─ 실시간 트렌드 모니터링: 키워드 추적 + 감성 분석
  ├─ 투자 연동: 소셜 센티먼트 → Quant Node 시그널
  ├─ 뉴스 속보 알림: 관련 종목 자동 매칭
  └─ 프라이버시: 공개 데이터만 수집, 개인 계정 접근 없음
- VAMOS 연동: D2.0-03 BLUE NODE (Research Node), AI Investing Scraper Manager
- 기술 스택: Tweepy (V1), Firehose API (V2)

[S7-G-007] Grok 유머/캐릭터 어시스턴트 | MED V2
- Grok의 "fun mode" 패턴을 VAMOS 성격 시스템에 적용
- 구현:
  ├─ Personality Profiles: {"formal", "casual", "humorous", "mentoring"}
  ├─ 프로필 전환: 사용자 명시 선택 또는 대화 분위기 자동 감지
  ├─ 안전장치: 부적절한 유머 자동 필터 (Constitutional AI 검증)
  └─ 투자 도메인: 유머 모드 OFF (심각한 금융 결정 시)
- VAMOS 연동: D2.0-02 ToneAdapter, D2.0-07 Safety 필터
```

#### Part K: Apple 온디바이스 AI (10건 중 TITLE_ONLY ~7건)
```
[S7-K-005] Apple Intelligence 온디바이스 패턴 참조 | HIGH V1
- Apple의 온디바이스 AI 패턴을 VAMOS 로컬 우선 전략에 적용
- 구현:
  ├─ 3단계 처리 계층:
  │   1. 온디바이스 (완전 로컬): 간단 분류, 키워드 추출, 감정 분석
  │   2. 온디바이스 LLM (Llama 4 Scout): 복잡한 로컬 분석
  │   3. 클라우드 API: 최고 품질 필요 시에만 (사용자 승인)
  ├─ Private Cloud Compute 컨셉:
  │   - 민감 데이터: 로컬 전용 처리 보장
  │   - 비민감 데이터: 클라우드 API 활용 가능
  │   - 하이브리드: 데이터 분류 후 자동 라우팅
  └─ 배터리/리소스 최적화: CPU/GPU 사용량 모니터링, 아이들 시만 로컬 모델 로드

- VAMOS 연동:
  ├─ D2.0-04 INFRA: 모델 라우팅 계층 구조 반영
  ├─ D2.0-07 SAFETY: 데이터 민감도 분류 → 처리 계층 자동 결정
  ├─ INNOV-12: 로컬 우선 프라이버시 정책과 통합
  └─ I-9 비용 상한: 로컬 처리 최대화로 API 비용 절감
```

#### Part L: Computer Use/GUI 에이전트 (8건 중 TITLE_ONLY ~5건)
```
[S7-L-003] 브라우저 에이전트 Playwright 통합 | HIGH V1
- 웹 브라우저를 프로그래밍적으로 제어하는 에이전트
- 구현:
  ├─ Playwright MCP 서버:
  │   tools:
  │     - navigate(url): 페이지 이동
  │     - click(selector): 요소 클릭
  │     - type(selector, text): 텍스트 입력
  │     - screenshot(): 현재 화면 캡처
  │     - extract(selector): 데이터 추출
  │     - wait(condition): 조건 대기
  ├─ AI 비전 기반 조작:
  │   - 스크린샷 → LLM 분석 → 다음 액션 결정
  │   - UI 요소 자동 감지 (버튼, 링크, 입력필드)
  │   - 실패 시 대안 경로 자동 탐색
  ├─ 투자 연동:
  │   - 증권사 웹사이트 자동 로그인 + 데이터 수집
  │   - 공시 자동 체크 (DART, SEC EDGAR)
  │   - 뉴스 사이트 자동 스크래핑
  └─ 보안:
      - 사용자 명시 승인 후에만 로그인 수행
      - 비밀번호: OS 키체인 저장, 메모리에 남기지 않음
      - 5-Gate: 모든 웹 액션에 Policy Gate 적용

- VAMOS 연동:
  ├─ D2.0-03 BLUE NODE: Browser Agent 노드로 등록
  ├─ D2.0-07 SAFETY: 웹 액션 권한 관리 (allow/deny/ask)
  ├─ N-011: 워크플로우 자동화 엔진과 통합
  └─ 5 Gates: 모든 destructive 웹 액션 → Approval Gate
```

#### Part O: Multi-Agent 프레임워크 (10건 중 TITLE_ONLY ~7건)
```
[S7-O-004] Swarm 오케스트레이션 패턴 | HIGH V2
- OpenAI Swarm / CrewAI 패턴을 VAMOS Multi-Agent에 적용
- 구현:
  ├─ 오케스트레이션 패턴:
  │   1. Sequential: A → B → C (파이프라인)
  │   2. Parallel: A || B || C → Merge (병렬 실행)
  │   3. Hierarchical: Lead → Workers (계층적 위임)
  │   4. Dynamic: 런타임 결정 (상황에 따라 패턴 변경)
  ├─ VAMOS Agent Orchestrator:
  │   class AgentOrchestrator:
  │     def execute(self, task: Task, pattern: str = "auto"):
  │       agents = self.select_agents(task)
  │       if pattern == "auto":
  │         pattern = self.determine_pattern(task, agents)
  │       return self.run_pattern(pattern, agents, task)
  ├─ 에이전트 간 통신: MessageBus (Redis V1, RabbitMQ V2)
  ├─ 결과 집계: MoA(Mixture of Agents) 패턴 → 최종 응답 합성
  └─ 비용 관리: 에이전트별 비용 추적, 전체 작업 비용 예산 설정

- VAMOS 연동:
  ├─ D2.0-05 AGENT WORKFLOW: Cooperative Agent Structure 확장
  ├─ S7-A-001~008: Agent Teams 아키텍처 통합
  ├─ 9-State Machine: EXECUTING 상태에서 멀티에이전트 조율
  └─ 5 Gates: 에이전트 스폰 시 Policy Gate 검증

[S7-O-008] A2A Protocol 실전 활용 | HIGH V2
- Google A2A 프로토콜로 외부 AI 에이전트와 협업
- 구현:
  ├─ VAMOS A2A Server:
  │   - /.well-known/agent.json 엔드포인트 제공
  │   - 인바운드 작업 수신 → Blue Node 라우팅
  │   - 아웃바운드 작업 위임 → 외부 에이전트 호출
  ├─ 유스케이스:
  │   - 외부 코딩 에이전트에 코드 리뷰 위임
  │   - 외부 리서치 에이전트에 논문 분석 위임
  │   - VAMOS 투자 분석을 외부 에이전트에 API로 제공
  └─ 보안: 에이전트 신뢰 등급, 데이터 최소 공유 원칙

- VAMOS 연동:
  ├─ K-011~K-020: A2A 프로토콜 구현 상세와 통합
  ├─ D2.0-03 BLUE NODE: 외부 에이전트를 가상 Blue Node로 등록
  └─ D2.0-07 SAFETY: 외부 에이전트 통신 보안 정책
```

#### Part P: RAG 최신 기술 (10건 중 TITLE_ONLY ~7건)
```
[S7-P-005] GraphRAG 구현 | HIGH V2
- Microsoft GraphRAG 패턴 적용: KG + 벡터 검색 통합
- 구현:
  ├─ 그래프 인덱싱:
  │   1. 문서 → 엔티티/관계 자동 추출 (LLM 기반)
  │   2. 커뮤니티 감지: Leiden 알고리즘으로 토픽 클러스터
  │   3. 커뮤니티 요약: 각 클러스터의 요약 텍스트 생성
  ├─ 쿼리 처리:
  │   - Local Search: 특정 엔티티 중심 검색
  │   - Global Search: 커뮤니티 요약 기반 종합 답변
  │   - Hybrid: Local + Global 결합
  ├─ VAMOS KG 연동:
  │   - 기존 NetworkX KG를 GraphRAG 인덱스로 확장
  │   - V2 Neo4j 전환 시 네이티브 GraphRAG
  └─ 투자 활용: 기업 관계 그래프 → 연관 종목 자동 발견

- VAMOS 연동:
  ├─ D2.0-06 (STORAGE): KG + 벡터 DB 통합 검색
  ├─ S7D-023: GraphRAG 쿼리 파이프라인과 통합
  ├─ Evidence Gate: GraphRAG 결과를 Evidence로 활용
  └─ 3-Part Output: 그래프 기반 근거를 footer에 시각화

[S7-P-007] Self-RAG (자기 반성 RAG) | HIGH V2
- 검색 결과의 품질을 LLM이 스스로 평가하고 재검색
- 구현:
  ├─ Self-RAG 파이프라인:
  │   1. 질문 분석 → 검색 필요 여부 판단
  │   2. 필요 시 검색 실행
  │   3. 검색 결과 관련성 평가 (is_relevant: bool)
  │   4. 관련 없으면 → 재검색 (쿼리 리프레이밍)
  │   5. 응답 생성
  │   6. 응답 지지도 평가 (is_supported: bool)
  │   7. 미지지 시 → 추가 검색 또는 면책 표시
  ├─ 평가 토큰: [Retrieve], [IsRel], [IsSup], [IsUse]
  └─ V1: LLM 프롬프트 기반 평가, V2: 특화 분류기

- VAMOS 연동:
  ├─ D2.0-02 ORANGE CORE: Stage 3 Retrieval + Stage 6 Self-Check 통합
  ├─ I-6 Self-check: QoD 평가에 Self-RAG 결과 반영
  └─ Evidence Gate: Self-RAG 검증을 Evidence Gate의 하위 단계로

[S7-P-009] ColPali / Late Interaction 검색 | MED V2
- 문서 이미지를 직접 벡터화하여 검색 (텍스트 추출 없이)
- 구현:
  ├─ ColPali 모델: 문서 페이지 이미지 → 토큰별 임베딩
  ├─ Late Interaction: 쿼리-문서 토큰 간 MaxSim 유사도
  ├─ 활용: PDF 스캔본, 표/그래프 포함 문서, 레이아웃 중요 문서
  └─ V2: Qdrant에 멀티벡터 인덱스 추가

- VAMOS 연동:
  ├─ D2.0-06: 벡터 DB에 image_embedding 컬렉션 추가
  ├─ J-001~J-003: 멀티모달 입력 파이프라인과 통합
  └─ AI Investing: 재무제표 이미지 검색 활용
```

---

## 2. 카테고리 F -- 인프라/배포/MLOps (TITLE_ONLY ~66건)

### 2.1 현황 분석

F 카테고리 96건 중 마스터인덱스에서 "CRITICAL 15건, HIGH 48건" 등으로 요약만 제공. R1~R2에서 일부 언급되었으나 개별 상세 스펙 미작성.

### 2.2 핵심 TITLE_ONLY 항목 상세 확장

#### S7F-001~015 | CRITICAL 인프라 항목
```
[S7F-001] CI/CD 파이프라인 | CRITICAL V1
- 구현:
  ├─ GitHub Actions 기반 자동 빌드/테스트/배포
  ├─ 워크플로우:
  │   push → lint → type-check → unit-test → integration-test →
  │   build-docker → deploy-staging → e2e-test → deploy-prod
  ├─ 브랜치 전략: main(prod), develop(staging), feature/*
  ├─ 보안: 시크릿 관리 (GitHub Secrets), SAST (Bandit), 의존성 감사
  └─ V1: GitHub Actions, V2: ArgoCD + GitOps
- VAMOS 연동: D2.0-04 INFRA §7, PHASE_B6_CICD_PIPELINE.md

[S7F-003] Docker Compose 로컬 개발 환경 | CRITICAL V1
- 구현:
  ├─ docker-compose.yml:
  │   services:
  │     vamos-core: ORANGE CORE 메인 서비스
  │     ollama: 로컬 LLM 서버 (Llama 4 Scout, Phi-4)
  │     chroma: 벡터 DB (V1)
  │     redis: 캐시 + 메시지 버스
  │     postgres: 메타데이터 (V2)
  │     whisper: 로컬 STT (선택)
  ├─ 리소스 요구: RAM 16GB+, GPU 8GB+ (Ollama용)
  ├─ 환경변수: .env.local, .env.staging, .env.prod 분리
  └─ 원클릭 시작: `docker compose up -d`

[S7F-005] 모델 라우팅 엔진 | CRITICAL V1
- 구현:
  ├─ ModelRouter:
  │   routing_rules:
  │     - condition: {task: "simple_chat", budget: "low"}
  │       model: "ollama/llama4-scout"
  │     - condition: {task: "coding", quality: "high"}
  │       model: "claude-sonnet-4.6"
  │     - condition: {task: "reasoning", depth: "deep"}
  │       model: "o3-mini/high"
  │     - condition: {task: "korean", local_only: true}
  │       model: "ollama/exaone-3.5"
  ├─ 폴백 체인: 모델 A 실패 → B → C → 로컬 최종 폴백
  ├─ 비용 기반 라우팅: 남은 예산에 따라 모델 자동 다운그레이드
  └─ A/B 테스트: 동일 쿼리를 2개 모델에 전송 → 결과 비교 → 최적 모델 학습
- VAMOS 연동: D2.0-04 §4.3 LLM 라우팅, A-ADD-01~03 모델 매트릭스

[S7F-008] 모니터링 스택 | CRITICAL V1
- 구현:
  ├─ 메트릭 수집: Prometheus (or VictoriaMetrics)
  │   - API 호출 횟수/지연시간/에러율
  │   - 토큰 사용량 (입력/출력 별)
  │   - 비용 추적 (모델별, 시간대별)
  │   - 메모리/CPU/디스크 사용률
  ├─ 대시보드: Grafana (V1) / 자체 대시보드 (V2)
  │   - 비용 대시보드: 일/주/월 비용 추세, 모델별 비용 분포
  │   - 성능 대시보드: P50/P95/P99 응답 시간
  │   - 품질 대시보드: QoD 평균, 피드백 긍정율
  ├─ 알림: Slack/Discord/이메일 알림
  │   - 비용 한도 80% 도달 시 경고
  │   - 에러율 > 5% 시 긴급 알림
  │   - 모델 다운타임 시 폴백 알림
  └─ 로깅: 구조화 로그 (JSON), 로그 보존 30일
- VAMOS 연동: D2.0-04 INFRA, D2.0-07 비용 모니터링 (S7E-062)
```

#### S7F-020~050 | HIGH 인프라 항목 (대표)
```
[S7F-020] Kubernetes 배포 매니페스트 | HIGH V2
- 구현:
  ├─ K8s 리소스:
  │   Deployment: vamos-core (3 replicas), vamos-worker (2 replicas)
  │   Service: ClusterIP + Ingress (Nginx)
  │   ConfigMap: 환경 설정
  │   Secret: API 키, DB 비밀번호
  │   PersistentVolumeClaim: Chroma/SQLite 데이터
  │   HPA: CPU 70% 이상 시 자동 스케일
  ├─ Helm Chart: vamos/vamos-ai (버전 관리)
  ├─ 네임스페이스: vamos-prod, vamos-staging, vamos-dev
  └─ 리소스 요청: core=2CPU/4GB, worker=1CPU/2GB
- VAMOS 연동: D2.0-04 INFRA V2 서버 전환

[S7F-025] 자동 스케일링 | HIGH V2
- 구현:
  ├─ HPA (Horizontal Pod Autoscaler):
  │   - CPU > 70% → 스케일 아웃
  │   - 동시 요청 > 50 → 스케일 아웃
  │   - min: 2, max: 10 replicas
  ├─ KEDA (이벤트 기반 스케일링):
  │   - Redis 큐 길이 기반 Worker 스케일링
  │   - Prometheus 메트릭 기반 커스텀 스케일링
  └─ 비용 최적화: 야간(00-06시) 최소 인스턴스로 축소
- VAMOS 연동: I-9 비용 상한 → V2 월간 ₩40,000 예산 내 스케일링

[S7F-030] 비용 최적화 엔진 | HIGH V1
- 구현:
  ├─ CostOptimizer:
  │   strategies:
  │     - prompt_caching: 시스템 프롬프트 캐싱 (30-50% 절감)
  │     - model_downgrade: 간단 작업 → nano/mini 모델 자동 전환
  │     - batch_processing: 비긴급 요청 배치 처리 (50% 절감)
  │     - local_first: 가능한 한 로컬 모델 우선
  │     - result_caching: 동일/유사 쿼리 캐시 히트
  ├─ 비용 예측: 요청 실행 전 예상 비용 산출 + 사용자 알림
  ├─ 월간 리포트: 비용 절감액, 모델별 사용량, 최적화 제안
  └─ 예산 알림: 50%/80%/90%/100% 도달 시 단계별 경고
- VAMOS 연동: D2.0-07 Cost Gate, I-9 비용 상한, A-ADD-07 Prompt Caching

[S7F-035] 로깅/트레이싱 통합 | HIGH V1
- 구현:
  ├─ 구조화 로깅:
  │   {
  │     "timestamp": "2026-02-23T10:30:00Z",
  │     "level": "INFO",
  │     "service": "orange-core",
  │     "trace_id": "abc123",
  │     "span_id": "def456",
  │     "event": "llm_call",
  │     "model": "claude-sonnet-4.6",
  │     "tokens_in": 1500,
  │     "tokens_out": 800,
  │     "cost_usd": 0.012,
  │     "latency_ms": 2300,
  │     "user_id": "user_001"
  │   }
  ├─ 분산 트레이싱: OpenTelemetry (OTLP 프로토콜)
  │   - 요청 → Analysis → Retrieval → Execution → Self-Check → Output
  │   - 각 Stage의 지연시간, 모델 호출, 도구 실행 추적
  ├─ 로그 저장: V1 로컬 파일 (logrotate), V2 Loki/Elasticsearch
  └─ 검색: 구조화 로그 필터 (날짜, 레벨, 서비스, trace_id)
- VAMOS 연동: D2.0-04 INFRA, 7단계 파이프라인 각 Stage에 span 삽입
```

---

## 3. 카테고리 G -- 벤치마크/평가/품질보증 (TITLE_ONLY ~63건)

### 3.1 핵심 TITLE_ONLY 항목 상세 확장

```
[S7G-001] 응답 품질 자동 평가 (Auto-Eval) | CRITICAL V1
- 구현:
  ├─ QoD (Quality of Decision) 자동 채점:
  │   dimensions:
  │     relevance: 질문에 대한 관련성 (0-100)
  │     accuracy: 사실 정확도 (Evidence Gate 결과 반영)
  │     completeness: 답변 완전성 (주요 측면 커버 여부)
  │     clarity: 표현 명확성 (가독성, 구조화)
  │     safety: 안전성 (유해 콘텐츠 없음)
  │   overall: weighted_mean(dimensions, weights=[0.25, 0.30, 0.20, 0.15, 0.10])
  ├─ 평가 방법:
  │   - V1: LLM-as-Judge (저비용 모델로 평가)
  │   - V2: 전용 평가 모델 (fine-tuned)
  │   - V3: 인간 평가 + ML 앙상블
  ├─ 벤치마크 데이터셋:
  │   - VAMOS-Eval-100: 자체 평가 세트 (코딩 25, 투자 25, 일반 25, 안전 25)
  │   - 주간 자동 평가: 무작위 샘플 50건 자동 채점
  └─ 회귀 감지: 품질 하락 > 5% 시 자동 알림

- VAMOS 연동:
  ├─ I-6 Self-check: QoD 점수를 Self-Check Stage에서 산출
  ├─ D2.0-02 ORANGE CORE: Stage 6에 Auto-Eval 통합
  └─ 3-Part Output: header에 QoD 점수 표시 옵션

[S7G-005] 할루시네이션 탐지 | CRITICAL V1
- 구현:
  ├─ 3단계 할루시네이션 방지:
  │   1. 예방: RAG 기반 사실 근거 주입 (Stage 3)
  │   2. 탐지: 응답 내 사실 주장 추출 → 소스 대조 (Stage 6)
  │   3. 대응: 미검증 주장에 "확인 필요" 레이블 + 신뢰도 하향
  ├─ HallucinationDetector:
  │   def detect(self, response: str, sources: List[str]) -> HalluReport:
  │     claims = self.extract_claims(response)
  │     for claim in claims:
  │       support = self.find_support(claim, sources)
  │       claim.verification = support.status  # verified/unverified/contradicted
  │     return HalluReport(claims=claims, score=self.calc_score(claims))
  ├─ 투자 도메인 특화:
  │   - 수치(가격, 수익률) 자동 검증 (실시간 API 대조)
  │   - 날짜/이벤트 사실 확인
  │   - 잘못된 종목 코드/이름 감지
  └─ 면책 표시: 검증 불가 주장에 "이 정보는 확인이 필요합니다" 자동 삽입

- VAMOS 연동:
  ├─ Evidence Gate: 할루시네이션 점수 → Evidence Gate 판정 기준
  ├─ D2.0-07 SAFETY: 안전 관련 할루시네이션 = 즉시 차단
  └─ AI Investing: 투자 관련 할루시네이션 → 자동 면책 고지

[S7G-012] SWE-Bench 대응 | HIGH V1
- VAMOS의 코딩 에이전트 성능을 SWE-Bench로 측정
- 구현:
  ├─ 대상: SWE-bench Verified (500건)
  ├─ VAMOS 파이프라인:
  │   1. 이슈 분석 → 관련 코드 검색 (RAG)
  │   2. 수정 계획 수립 (Plan Mode)
  │   3. 코드 수정 생성
  │   4. 테스트 실행 (Docker 샌드박스)
  │   5. Self-Check → 재시도
  ├─ 목표: V1 > 30%, V2 > 50%, V3 > 70%
  └─ 주간 회귀 테스트: 50건 샘플 자동 실행

- VAMOS 연동:
  ├─ D2.0-03 BLUE NODE: Dev Node 코딩 에이전트
  ├─ D2.0-05 AGENT WORKFLOW: 코딩 작업 파이프라인
  └─ PHASE_B5_TEST_STRATEGY.md: 벤치마크 테스트 전략

[S7G-020] 도메인별 벤치마크 | HIGH V2
- 투자/코딩/교육/생활 각 도메인별 성능 측정
- 구현:
  ├─ VAMOS Benchmark Suite (VBS):
  │   VBS-01~10: 기존 STEP6 벤치마크
  │   VBS-11: 코딩 벤치마크 (SWE-Bench, HumanEval, MBPP)
  │   VBS-12: 투자 벤치마크 (전략 수익률, 리스크 관리, 속도)
  │   VBS-13: 지식 관리 벤치마크 (검색 정확도, 기억력)
  │   VBS-14: 대화 품질 벤치마크 (자연스러움, 유용성, 안전성)
  │   VBS-15: 워크플로우 벤치마크 (자동화 성공률, 속도)
  │   VBS-16: 학습 벤치마크 (학습 효과, 기억 보존)
  │   VBS-17: 웰니스 벤치마크 (감정 인식 정확도, 도움 유용성)
  ├─ 자동 실행: 매주 토요일 새벽 Dream Mode에서 실행
  ├─ 대시보드: 벤치마크 점수 추이 그래프
  └─ 회귀 감지: 점수 하락 > 3% 시 자동 알림 + 원인 분석

- VAMOS 연동: D2.1-Q1 Audit Report, Dream Mode 스케줄러
```

---

## 4. 카테고리 H -- 비즈니스모델/시장전략 (TITLE_ONLY ~58건)

### 4.1 핵심 TITLE_ONLY 항목 상세 확장

```
[S7H-001] 가격 전략 | CRITICAL V1
- 구현:
  ├─ 3-Tier 가격 모델:
  │   V1 Free/Starter: ₩0~₩10,000/월
  │     - 로컬 LLM 무제한
  │     - 클라우드 API 일일 50회
  │     - 기본 메모리/KG
  │   V2 Pro: ₩20,000~₩40,000/월
  │     - 클라우드 API 무제한 (예산 내)
  │     - 고급 에이전트, 워크플로우
  │     - 서버 호스팅 포함
  │   V3 Enterprise: ₩100,000~₩200,000/월
  │     - 멀티유저, 팀 협업
  │     - SLA 보장, 전용 인스턴스
  │     - 커스텀 모델 파인튜닝
  ├─ 비용 구조:
  │   - V1 원가: ₩0 (로컬) ~ ₩5,000 (클라우드)
  │   - V2 원가: ₩15,000~₩25,000
  │   - V3 원가: ₩50,000~₩100,000
  ├─ 차별화 포인트: "시중 AI 구독 ₩22,000~44,000 대비 더 많은 기능을 더 적은 비용으로"
  └─ 수익 모델: 구독 + API 초과 사용 과금 + MCP 마켓플레이스 수수료

- VAMOS 연동:
  ├─ PLAN-3.0 §7: 수익/비용 모델
  ├─ I-9 비용 상한: 각 Tier별 비용 한도 설정
  └─ D2.0-07 Cost Gate: Tier별 기능 게이팅

[S7H-010] V1 MVP 정의 | CRITICAL V1
- 구현:
  ├─ V1 MVP 핵심 기능 (출시 최소 요건):
  │   1. 대화 AI: 7단계 파이프라인 기본 동작
  │   2. 로컬 LLM: Llama 4 Scout + Ollama
  │   3. 클라우드 API: Claude/GPT/Gemini 라우팅
  │   4. 메모리: 3-Layer (L0/L1/L2) 기본 구현
  │   5. KG: NetworkX 경량 그래프
  │   6. RAG: Chroma + BGE-M3 벡터 검색
  │   7. 안전: 5-Gate 기본 동작 (Policy/Evidence/Cost)
  │   8. UI: Tauri 데스크톱 앱 기본 레이아웃
  │   9. 비용: 월 ₩10,000 이하 운영 가능
  │   10. MCP: 기본 도구 10개 (파일, 검색, 코드 등)
  ├─ V1 제외 기능 (V2로 이월):
  │   - 음성 대화, 이미지 생성, 비디오 분석
  │   - Kubernetes 배포, 자동 스케일링
  │   - 멀티디바이스 동기화
  │   - 고급 에이전트 오케스트레이션 (10+)
  └─ 출시 목표: V1 alpha (3개월), V1 beta (6개월), V1 GA (9개월)

- VAMOS 연동: PLAN-3.0 로드맵, 전체 D2.0-01~08 V1 스코프

[S7H-020] 시장 분석 | HIGH V1
- 구현:
  ├─ TAM/SAM/SOM:
  │   TAM: 글로벌 AI 어시스턴트 시장 $50B+ (2026)
  │   SAM: 개인용 AI 어시스턴트 $10B
  │   SOM: 한국 얼리어답터 개발자/투자자 ~50만명
  ├─ 경쟁 매트릭스:
  │   | 기능 | VAMOS | ChatGPT | Claude | Gemini |
  │   |------|-------|---------|--------|--------|
  │   | 통합(코딩+투자+학습) | O | X | X | X |
  │   | 로컬 우선 | O | X | X | X |
  │   | 비용 투명성 | O | 구독제 | 구독제 | 구독제 |
  │   | 자기진화 | O | X | X | X |
  │   | 5-Gate 안전 | O | 내부 | 내부 | 내부 |
  ├─ 포지셔닝: "시중 AI의 모든 기능 + 프라이버시 + 비용 투명성 + 자기진화"
  └─ 진입 전략: 오픈소스 커뮤니티 → 얼리어답터 → 대중화

- VAMOS 연동: PLAN-3.0, S7-E-001~018 VAMOS 강점 강화
```

---

## 5. 카테고리 I -- AI Investing 보강 (TITLE_ONLY ~66건)

### 5.1 현황 분석

I 카테고리 106건 중 VAMOS_AI_INVESTING_SPEC.md에서 이미 상세 구현된 부분과 교차 확인:
- 기존 투자 스펙: 7-Layer 데이터, 83개 소스, 96개 전략, 51% Gate 등 완비
- STEP7 보강: 리스크 관리 고급, 실시간 스트리밍, 소셜 데이터, 대안 데이터 등 미반영

### 5.2 핵심 TITLE_ONLY 항목 상세 확장

```
[S7I-010] 실시간 데이터 스트리밍 | CRITICAL V1
- 구현:
  ├─ 실시간 데이터 파이프라인:
  │   데이터 소스 → WebSocket/SSE → Stream Gateway → 분석 엔진 → 알림
  ├─ 실시간 소스:
  │   - 주가: Alpaca Stream, yfinance WebSocket
  │   - 뉴스: RSS Feed 실시간 파싱
  │   - 공시: DART/SEC EDGAR 모니터링
  │   - 소셜: Reddit/X 키워드 모니터링
  ├─ Stream Gateway:
  │   class StreamGateway:
  │     def on_price_update(self, ticker, price, volume):
  │       self.check_alerts(ticker, price)
  │       self.update_portfolio_value()
  │       if self.strategy_signal(ticker, price):
  │         self.notify_user(ticker, signal)
  ├─ 알림: 가격 알림, 전략 시그널, 뉴스 속보, 공시 알림
  └─ V1: 폴링 (5분 간격), V2: WebSocket 실시간

- VAMOS 연동:
  ├─ AI Investing: Stream Gateway (섹션 13)
  ├─ D2.0-05: 워크플로우 트리거 시스템과 통합
  ├─ P-005: 감정적 투자 방지 (FOMO 알림 시 감정 체크)
  └─ 5 Gates: 실시간 알림에도 Cost Gate 적용

[S7I-020] FinBERT 감성 분석 | HIGH V1
- 구현:
  ├─ 금융 특화 감성 분석:
  │   - 모델: FinBERT (ProsusAI/finbert) — 금융 뉴스 특화
  │   - 입력: 뉴스 헤드라인, 실적 발표, 애널리스트 리포트
  │   - 출력: {sentiment: positive|negative|neutral, confidence: 0-1}
  ├─ 파이프라인:
  │   뉴스 수집 → 전처리 → FinBERT 추론 → 감성 점수 → 종목별 집계 → 시그널
  ├─ VAMOS 활용:
  │   - 개별 종목 뉴스 감성 추적
  │   - 시장 전체 감성 인덱스
  │   - 감성 급변 시 자동 알림
  └─ V1: Hugging Face 로컬 추론 (CPU, ~500ms/건)

- VAMOS 연동:
  ├─ AI Investing: ML/AI 스택 (섹션 15)
  ├─ D2.0-06: 감성 데이터 L2 프로젝트 메모리 저장
  └─ Quant Node: 감성 시그널을 전략 입력으로 활용

[S7I-035] 백테스팅 고급 | HIGH V1
- 구현:
  ├─ 백테스팅 엔진 확장:
  │   - Walk-Forward Analysis: 롤링 윈도우 최적화
  │   - Monte Carlo Simulation: 1000회 랜덤 시나리오
  │   - Stress Testing: 극단적 시장 시나리오 (2008 금융위기, COVID 등)
  │   - Slippage/수수료 모델링: 실전 비용 반영
  ├─ 리포트 자동 생성:
  │   {
  │     strategy_name: str,
  │     period: "2020-01-01 ~ 2025-12-31",
  │     total_return: float,  # 총 수익률
  │     sharpe_ratio: float,  # 샤프 비율
  │     max_drawdown: float,  # 최대 낙폭
  │     win_rate: float,      # 승률
  │     calmar_ratio: float,  # 칼마 비율
  │     sortino_ratio: float, # 소르티노 비율
  │     trade_count: int,     # 거래 횟수
  │     avg_holding_days: float  # 평균 보유 기간
  │   }
  └─ 51% Gate 연동: 백테스트 승률 < 51% → 전략 자동 비활성화

- VAMOS 연동:
  ├─ AI Investing: 백테스팅 엔진 (섹션 6)
  ├─ 51% Gate: 전략 검증 기준
  └─ Grafana: 백테스트 결과 대시보드

[S7I-050] 대안 데이터 (Alternative Data) | HIGH V2
- 구현:
  ├─ 대안 데이터 소스:
  │   - 위성 이미지: 주차장 차량 수, 농작물 상태 (V3)
  │   - 웹 트래픽: SimilarWeb API → 기업 트래픽 추세
  │   - 앱 다운로드: SensorTower → 모바일 앱 성장
  │   - 소셜 감성: Reddit/X/YouTube 언급 빈도 + 감성
  │   - 특허 데이터: USPTO/KIPO 신규 특허 분석
  │   - 구인 공고: LinkedIn/Indeed → 기업 성장 시그널
  ├─ 데이터 파이프라인:
  │   Scraper → 정제 → 정규화 → 임베딩 → 벡터DB 저장 → 쿼리 가능
  ├─ 투자 활용:
  │   - 대안 데이터 시그널 → 전략 입력 (alpha factor)
  │   - 기존 재무 데이터와 교차 검증
  │   - 비시장 정보 → 차별화된 인사이트
  └─ V2: 웹/소셜 (즉시), V3: 위성/특허 (6개월+)

- VAMOS 연동:
  ├─ AI Investing: Scraper Manager (섹션 21)
  ├─ D2.0-06: 대안 데이터 벡터 인덱스
  └─ Evidence Gate: 대안 데이터 품질 검증
```

---

## 6. 카테고리 J -- 멀티모달/생성처리 (TITLE_ONLY ~73건)

### 6.1 핵심 TITLE_ONLY 항목 상세 확장

```
[J-011~020] 이미지 생성 (10건)
- J-011: 이미지 생성 모델 통합 게이트웨이
  ├─ 지원 모델: DALL-E 3, Stable Diffusion 3, Midjourney API (V2)
  ├─ 통합 API: /api/generate_image {prompt, model, size, style, n}
  ├─ 비용 관리: 이미지 생성당 비용 추적, 일일 한도 설정
  └─ VAMOS 연동: D2.0-03 Content Node, MCP 도구 등록

- J-013: 이미지 편집 (인페인팅/아웃페인팅)
  ├─ 기능: 부분 수정, 배경 확장, 요소 추가/제거
  ├─ 모델: SDXL Inpainting (V2), DALL-E 편집 API (V2)
  └─ 활용: 프레젠테이션 이미지, 다이어그램 수정

- J-015: 투자 차트 자동 생성
  ├─ 데이터 → 자동 시각화: 캔들스틱, 비교 차트, 포트폴리오 파이
  ├─ 기술: Plotly + Matplotlib, V2 D3.js 인터랙티브
  └─ VAMOS 연동: AI Investing Grafana 대시보드

[J-021~030] 오디오/음성 (10건)
- J-021: STT (Speech-to-Text) 통합
  ├─ V1 로컬: Whisper v3 (faster-whisper, GPU 가속)
  ├─ V2 클라우드: Deepgram Nova (실시간, 정확도↑)
  ├─ 한국어 최적화: ko-whisper 모델, 혼합어(한/영) 처리
  ├─ 파이프라인: 마이크 입력 → VAD(음성 감지) → STT → 텍스트
  └─ VAMOS 연동: D2.0-08 음성 입력 버튼, D2.0-02 Input Stage

- J-025: TTS (Text-to-Speech) 통합
  ├─ V1: Edge TTS (무료, 한국어 지원)
  ├─ V2: ElevenLabs (자연스러운 음성, 감정 표현)
  ├─ 감정 톤: 차분한/긴급한/격려하는 음성 자동 선택
  └─ VAMOS 연동: D2.0-08 음성 출력, P-002 감정 적응형 응답

- J-028: 음성 대화 모드 (Voice Chat)
  ├─ 실시간 파이프라인: 마이크 → STT → LLM → TTS → 스피커
  ├─ 지연시간 목표: < 2초 (V1), < 500ms (V2)
  ├─ 인터럽트 지원: 사용자가 말하면 AI 응답 즉시 중단
  ├─ 음성 감정 분석: 피치/속도/강도 → 감정 추론 (V2)
  └─ VAMOS 연동: D2.0-08 음성 전체화면 UI, P-001 감정 인식

[J-031~040] 비디오/3D (10건)
- J-031: 비디오 입력 분석
  ├─ 키프레임 추출: FFmpeg → 초당 1프레임 샘플링
  ├─ 장면 분석: 각 프레임 → 비전 모델 분석 → 시간순 요약
  ├─ 자막 추출: 비디오 내장 자막 또는 Whisper STT
  ├─ 활용: 강의 비디오 요약, 회의 녹화 분석, YouTube 학습
  └─ VAMOS 연동: O-011 YouTube 학습, D2.0-06 비디오 메타데이터 저장

- J-035: 데이터 시각화 자동 생성
  ├─ 데이터 → 최적 차트 유형 자동 선택 → 렌더링
  ├─ 지원: 막대/선/파이/산점도/히트맵/트리맵/Sankey
  ├─ 인터랙티브: Plotly.js 기반, 줌/팬/호버 지원
  └─ VAMOS 연동: D2.0-08 Artifacts 패널, AI Investing 리포트

[J-041~050] 문서 처리 (10건)
- J-041: PDF 분석 파이프라인
  ├─ 단계: 업로드 → 페이지 분리 → OCR(필요시) → 텍스트 추출 →
  │        청킹 → 임베딩 → 벡터DB 저장 → 대화형 분석 가능
  ├─ 표 추출: Camelot / Tabula (구조화 데이터로 변환)
  ├─ 이미지 추출: PyMuPDF → 인라인 이미지 분석
  └─ VAMOS 연동: D2.0-06 RAG 파이프라인, D2.0-02 파일 입력 처리

- J-045: 코드 생성/편집 멀티모달
  ├─ UI 스크린샷 → HTML/React 코드 자동 생성
  ├─ 에러 스크린샷 → 에러 분석 + 수정 코드 제안
  ├─ 와이어프레임 → 인터랙티브 프로토타입
  └─ VAMOS 연동: D2.0-03 Dev Node, J-008 비전 기반 코드 이해
```

---

## 7. 카테고리 K -- 에이전트 프로토콜/상호운용성 (TITLE_ONLY ~61건)

### 7.1 현황 분석

K 카테고리 86건 중 작업가이드에서 K-001~K-020 (20건)은 상세 구현 스펙 완료. K-021~K-086의 ~61건이 TITLE_ONLY 또는 요약 수준.

### 7.2 핵심 TITLE_ONLY 항목 상세 확장

```
[K-021~030] 멀티에이전트 프레임워크 통합 (10건)
- K-021: LangGraph 에이전트 오케스트레이션
  ├─ StateGraph 기반 에이전트 워크플로우 구현
  ├─ VAMOS 적용: 7단계 파이프라인을 StateGraph 노드로 모델링
  │   nodes: [input, analysis, retrieval, routing, execution, self_check, output]
  │   edges: 조건부 라우팅 (분석 결과에 따라 다른 경로)
  ├─ Human-in-the-Loop: Approval Gate 포인트를 LangGraph interrupt로 구현
  └─ V1: 경량 자체 그래프 엔진, V2: LangGraph 통합 옵션

- K-025: CrewAI 역할 기반 에이전트 참조
  ├─ 역할(Role)/목표(Goal)/배경(Backstory) 패턴을 VAMOS Blue Node에 적용
  │   DevNode:
  │     role: "Senior Python Developer"
  │     goal: "Write clean, tested, efficient code"
  │     backstory: "10년 경력 풀스택 개발자, TDD 전문"
  │   InvestNode:
  │     role: "Quantitative Analyst"
  │     goal: "Generate alpha with risk management"
  │     backstory: "CFA 보유, 5년 퀀트 경력"
  ├─ 자동 역할 할당: 작업 분석 → 최적 역할 매칭
  └─ VAMOS 연동: D2.0-03 BLUE NODE 프로필 확장

- K-028: AutoGen 대화 패턴 참조
  ├─ 에이전트 간 대화를 통한 문제 해결 패턴
  │   user_proxy ↔ assistant: 기본 대화
  │   group_chat: 3+ 에이전트 토론 → 합의 도출
  │   nested_chat: 에이전트 내부 하위 대화
  ├─ VAMOS 적용: Blue Node 간 내부 토론 모드
  │   - Dev Node + Research Node 토론 → 기술 결정
  │   - Quant Node + Safety Node 토론 → 투자 결정 검증
  └─ V2: 에이전트 토론 모드 구현 (3개월)

[K-031~040] 도구 생태계 확장 (10건)
- K-031: MCP Tool Marketplace 구현
  ├─ 마켓플레이스 구조:
  │   /marketplace
  │   ├─ /tools         # 도구 검색/설치
  │   ├─ /tools/{id}    # 도구 상세 (리뷰, 호환성)
  │   ├─ /publish       # 도구 등록 (개발자용)
  │   └─ /categories    # 카테고리별 분류
  ├─ 카테고리: 코딩/투자/생산성/데이터/미디어/자동화
  ├─ 품질 관리: 자동 보안 스캔, 호환성 테스트, 사용자 리뷰
  └─ VAMOS 연동: K-008 MCP 마켓플레이스 확장

- K-035: 커스텀 Tool 개발 SDK
  ├─ 도구 개발 프레임워크:
  │   @vamos.tool(
  │     name="stock_analyzer",
  │     description="Analyze stock fundamentals",
  │     params={"ticker": str, "period": str},
  │     annotations={"readOnlyHint": True}
  │   )
  │   async def analyze_stock(ticker: str, period: str) -> dict:
  │     # 구현
  │     return {"analysis": result}
  ├─ 자동 JSON Schema 생성
  ├─ 테스트 프레임워크: MCP Inspector 통합
  └─ 문서 자동 생성: docstring → API 문서

[K-041~050] 프로토콜 브릿지 (10건)
- K-041: MCP ↔ OpenAI Function Calling 브릿지
  ├─ MCP 도구를 OpenAI tool 스키마로 자동 변환
  │   mcp_tool → { type: "function", function: {name, description, parameters} }
  ├─ 역방향: OpenAI function을 MCP 서버로 래핑
  └─ VAMOS 활용: OpenAI 호환 API 제공 → 기존 GPT 앱에서 VAMOS 도구 사용

- K-045: REST API ↔ MCP 자동 변환
  ├─ OpenAPI/Swagger 스펙 → MCP 서버 자동 생성
  │   swagger.json → parse → generate_mcp_server → test → register
  ├─ 활용: 기존 REST API를 MCP 도구로 즉시 사용 가능
  └─ V1: 수동 래핑, V2: 자동 변환 (2개월)
```

---

## 8. 카테고리 L -- 개발자도구/API/SDK (TITLE_ONLY ~62건)

### 8.1 핵심 TITLE_ONLY 항목 상세 확장

```
[L-001] REST API 설계 | CRITICAL V1
- 구현:
  ├─ VAMOS API v1:
  │   POST /api/v1/chat           # 대화 요청
  │   POST /api/v1/chat/stream    # 스트리밍 대화
  │   GET  /api/v1/memory         # 메모리 조회
  │   POST /api/v1/memory         # 메모리 저장
  │   GET  /api/v1/tools          # 도구 목록
  │   POST /api/v1/tools/{id}/run # 도구 실행
  │   GET  /api/v1/workflows      # 워크플로우 목록
  │   POST /api/v1/workflows/run  # 워크플로우 실행
  │   GET  /api/v1/cost/summary   # 비용 요약
  │   GET  /api/v1/health         # 헬스체크
  ├─ 인증: API Key (V1), OAuth2 (V2)
  ├─ Rate Limiting: 60 req/min (V1), 300 req/min (V2)
  ├─ 에러 형식: {error: {code, message, details, trace_id}}
  └─ OpenAPI 3.0 스펙 자동 생성 (/api/docs)

- VAMOS 연동:
  ├─ D2.0-04 INFRA: API 게이트웨이
  ├─ PHASE_B1_API_CONTRACT.md: API 계약 문서
  └─ 5 Gates: 모든 API 요청에 Gate 적용

[L-005] Python SDK | CRITICAL V1
- 구현:
  ├─ pip install vamos-sdk
  ├─ 사용 예시:
  │   from vamos import VamosClient
  │   client = VamosClient(api_key="...")
  │
  │   # 대화
  │   response = client.chat("AAPL 주가 분석해줘")
  │   print(response.text)
  │   print(response.confidence)
  │   print(response.cost)
  │
  │   # 메모리
  │   client.memory.store("AAPL 매수 이유: PER 저평가")
  │   results = client.memory.search("AAPL 관련 메모")
  │
  │   # 도구
  │   result = client.tools.run("stock_analyzer", ticker="AAPL")
  │
  │   # 워크플로우
  │   wf = client.workflows.create("morning_routine")
  │   wf.add_step("check_portfolio")
  │   wf.add_step("read_news")
  │   wf.run()
  ├─ 비동기 지원: async/await 완전 지원
  ├─ 타입 힌트: Pydantic 모델 기반 완전 타입 지원
  └─ 테스트: pytest 통합, Mock 서버 제공

[L-010] 문서 자동 생성 | CRITICAL V1
- 구현:
  ├─ API 문서: OpenAPI 3.0 → Swagger UI + ReDoc
  ├─ SDK 문서: Sphinx (Python) / TypeDoc (TypeScript)
  ├─ 튜토리얼: Jupyter Notebook 인터랙티브 가이드
  ├─ 코드 예시: 주요 유스케이스별 샘플 코드 20+
  └─ 자동 갱신: CI/CD에서 API 변경 시 문서 자동 재생성

[L-020] Webhook 시스템 | HIGH V1
- 구현:
  ├─ Webhook 이벤트:
  │   - agent.completed: 에이전트 작업 완료
  │   - alert.triggered: 알림 트리거 (투자, 일정 등)
  │   - workflow.status: 워크플로우 상태 변경
  │   - cost.threshold: 비용 임계값 도달
  │   - memory.stored: 새 메모리 저장
  ├─ Webhook 등록:
  │   POST /api/v1/webhooks
  │   { url: "https://example.com/hook", events: ["agent.completed"], secret: "..." }
  ├─ 보안: HMAC-SHA256 서명, IP 화이트리스트 (V2)
  └─ 재시도: 실패 시 3회 재시도 (exponential backoff)

[L-030] IDE 플러그인 (VSCode) | HIGH V2
- 구현:
  ├─ VSCode Extension:
  │   기능:
  │     - Ctrl+L: VAMOS 대화 사이드패널
  │     - Ctrl+K: 인라인 코드 수정 제안
  │     - 코드 선택 → "VAMOS에게 물어보기"
  │     - 에러 → 자동 분석 + 수정 제안
  │     - 커밋 메시지 자동 생성
  │     - 코드 리뷰 자동 실행
  ├─ MCP 연동: VSCode → MCP 클라이언트 → VAMOS MCP 서버
  ├─ 컨텍스트: 현재 열린 파일, 워크스페이스 구조, Git 상태 자동 전달
  └─ V2: 기본 기능 (3개월), V3: 고급 기능 (6개월)

- VAMOS 연동:
  ├─ D2.0-03 BLUE NODE: Dev Node 직접 연동
  ├─ S7C-056: IDE 플러그인 UI 스펙
  └─ L-001: REST API 활용
```

---

## 9. 카테고리 M -- PKM/지식관리 (TITLE_ONLY ~58건)

### 9.1 핵심 TITLE_ONLY 항목 상세 확장

```
[M-001] 지식 자동 축적 시스템 | CRITICAL V1
- 구현:
  ├─ 자동 지식 추출 파이프라인:
  │   대화 → 엔티티/사실 추출 → 중복 확인 → 확인 프롬프트 → KG 저장
  ├─ 추출 대상:
  │   - 사실(Fact): "AAPL의 PER은 28이다"
  │   - 선호(Preference): "코드 리뷰 시 한국어 주석 선호"
  │   - 관계(Relation): "AAPL은 FAANG 멤버이다"
  │   - 이벤트(Event): "2026-03-15 FOMC 회의"
  ├─ 저장 스키마:
  │   KnowledgeNode:
  │     id: str
  │     type: "fact"|"preference"|"relation"|"event"
  │     content: str
  │     source: {conversation_id, timestamp}
  │     confidence: float
  │     last_verified: datetime
  │     access_count: int
  └─ 사용자 확인: 중요 지식은 "이 내용을 기억해도 될까요?" 확인 후 저장

- VAMOS 연동:
  ├─ D2.0-06: 5-Layer Memory + KG 통합
  ├─ S7D-001: 자동 사실 추출 구현과 통합
  ├─ S7D-020: KG 스키마 설계 활용
  └─ 9-State Machine: LEARNING 상태에서 지식 축적

[M-005] Obsidian 통합 | CRITICAL V1
- 구현:
  ├─ Obsidian MCP 서버:
  │   tools:
  │     - obsidian.search(query): 노트 검색
  │     - obsidian.read(path): 노트 읽기
  │     - obsidian.write(path, content): 노트 작성
  │     - obsidian.link(from, to): 양방향 링크 생성
  │     - obsidian.tag(path, tags): 태그 추가
  ├─ Vault ↔ VAMOS KG 동기화:
  │   - Obsidian 노트 → VAMOS KG 노드 자동 생성
  │   - VAMOS KG 변경 → Obsidian 노트 자동 업데이트
  │   - 양방향 링크 → KG edge 매핑
  ├─ Obsidian 플러그인:
  │   - VAMOS 사이드바: Obsidian 내에서 VAMOS 대화
  │   - 노트 자동 요약: 긴 노트 → AI 요약 생성
  │   - 연결 제안: "이 노트와 관련된 다른 노트" AI 추천
  └─ V1: MCP 서버 기본 연동, V2: 플러그인 + 양방향 동기화

- VAMOS 연동:
  ├─ D2.0-06: KG ↔ Obsidian 동기화
  ├─ D2.0-03: Obsidian MCP 서버 등록
  └─ O-001: 학습 시스템과 Obsidian 지식 연결

[M-015] 마인드맵 자동 생성 | HIGH V1
- 구현:
  ├─ 입력 → 핵심 개념 추출 → 계층 구조화 → Markmap 렌더링
  ├─ 지원 입력: 대화 요약, 문서, 웹 페이지, KG 부분 그래프
  ├─ 렌더링: Markmap (마크다운 → 인터랙티브 마인드맵)
  ├─ 편집: 노드 추가/삭제/이동, 색상/아이콘 커스텀
  └─ Obsidian 연동: Markmap 결과를 Obsidian Canvas에 내보내기

- VAMOS 연동:
  ├─ D2.0-08: Artifacts 패널에 마인드맵 렌더링
  ├─ O-009: 마인드맵 학습과 통합
  └─ D2.0-06: KG 시각화 대안으로 활용
```

---

## 10. 보강 추가항목 (TITLE_ONLY ~32건)

### 10.1 B-ADD ~ I-ADD 미작성 항목 상세 확장

```
[B-ADD-03] 추론 UX 패턴 | MED V2
- 구현:
  ├─ Thinking 블록 UI:
  │   - 추론 과정을 접기/펼치기 가능한 블록으로 표시
  │   - 실시간 스트리밍: thinking 토큰을 회색 텍스트로 실시간 표시
  │   - 요약 모드: 긴 추론을 한 줄 요약으로 압축 (기본)
  │   - 상세 모드: 전체 추론 과정 표시 (토글)
  ├─ Reasoning Effort 인디케이터:
  │   - 입력창 옆에 "빠른/보통/깊은" 토글
  │   - 자동 모드: 질문 복잡도에 따라 자동 결정
  │   - 비용 표시: effort별 예상 비용 차이 표시
  └─ VAMOS 연동: D2.0-08 UI, D2.0-02 Stage 2 분석

[B-ADD-05] A2A 대화 패턴 | HIGH V2
- 구현:
  ├─ 에이전트 간 대화 사용자 표시:
  │   "VAMOS가 Research Agent에게 논문 분석을 요청하고 있습니다..."
  │   → 진행 상태 타임라인 표시
  │   → 완료 시 결과 요약 + 원본 대화 접기/펼치기
  ├─ Mixture of Agents (MoA) UX:
  │   "3개 AI 모델이 이 질문을 분석했습니다"
  │   → 각 모델 응답 비교 뷰
  │   → 합의점 + 차이점 하이라이트
  └─ VAMOS 연동: K-011 A2A 프로토콜, S7-O-004 Swarm 패턴

[C-ADD-01] NotebookLM Audio Overview UI | MED V2
- 구현:
  ├─ 문서 업로드 → AI 팟캐스트 자동 생성 기능의 UI
  │   - 문서 드래그앤드롭 → 분석 진행바 → 오디오 재생기
  │   - 토론 형식: "호스트 A"와 "호스트 B" 역할 분리
  │   - 재생 중 텍스트 하이라이트 동기화
  │   - 시간별 점프: 목차 클릭 → 해당 시점으로 이동
  └─ VAMOS 연동: J-025 TTS, J-013 오디오, D2.0-08 미디어 플레이어

[D-ADD-01] Microsoft Recall 로컬 구현 | HIGH V2
- 구현:
  ├─ 화면 기록 + 시맨틱 검색:
  │   - 주기적 스크린샷 (설정 가능: 30초~5분)
  │   - 로컬 OCR → 텍스트 추출 → 임베딩 → 벡터DB
  │   - 자연어 검색: "아까 봤던 그래프" → 관련 스크린샷 검색
  │   - 타임라인 뷰: 시간순 스크린샷 브라우징
  ├─ 프라이버시 강화:
  │   - 완전 로컬 처리 (클라우드 전송 없음)
  │   - PII 자동 마스킹 (신용카드, 주민번호 등)
  │   - 앱별 제외 목록 (은행, 의료 앱 등)
  │   - 암호화 저장: AES-256-GCM
  │   - 보존 기간: 사용자 설정 (기본 7일)
  └─ VAMOS 연동: J-004 스크린캡처, D2.0-06 벡터DB, D2.0-07 PII 마스킹

[D-ADD-04] MemGPT/Letta 패턴 적용 | HIGH V2
- 구현:
  ├─ 가상 컨텍스트 관리:
  │   - MemGPT 패턴: LLM의 컨텍스트 윈도우를 OS의 가상 메모리처럼 관리
  │   - 주 메모리 (컨텍스트): 현재 대화 + 관련 메모리
  │   - 보조 메모리 (디스크): 벡터DB + KG + 아카이브
  │   - 페이지 인/아웃: 필요한 정보를 자동으로 주 메모리에 로드/언로드
  ├─ VAMOS 적용:
  │   - 기존 4-Layer Memory(정본 L0~L3)를 MemGPT 패턴으로 재해석
  │   - L0(세션)=주 메모리, L1~L3=보조 메모리
  │   - 자동 컨텍스트 관리: 대화 길어질 때 자동 압축+관련 정보 로드
  └─ VAMOS 연동: D2.0-06 4-Layer Memory(정본 L0~L3), S7D-035~042 메모리 계층

[E-ADD-01] A2A 보안 프레임워크 | HIGH V2
- 구현:
  ├─ 에이전트 간 통신 보안:
  │   - 인증: OAuth 2.0 + JWT 토큰
  │   - 암호화: TLS 1.3 + 메시지 레벨 암호화 (선택)
  │   - 권한: 에이전트별 역할 기반 접근 제어
  │   - 데이터 최소화: 작업에 필요한 최소 데이터만 공유
  ├─ 위협 모델:
  │   - 악성 에이전트: 허위 결과 반환 → 다중 에이전트 교차 검증
  │   - 데이터 유출: 민감 정보 자동 마스킹 후 전송
  │   - Delegation Attack: 위임 체인 깊이 제한 (max 3)
  │   - 중간자 공격: TLS + 메시지 서명
  └─ VAMOS 연동: S7E-078~080 Agent 보안, K-015 A2A 보안

[F-ADD-01] PagedAttention / vLLM 최적화 | HIGH V2
- 구현:
  ├─ V2 서버에서 로컬 LLM 서빙 최적화:
  │   - vLLM: PagedAttention으로 KV Cache 효율 극대화
  │   - 동시 요청 처리: continuous batching
  │   - 메모리 효율: 기존 대비 2-4배 높은 처리량
  ├─ 배포:
  │   - V1: Ollama (간편, 단일 사용자 충분)
  │   - V2: vLLM (고성능, 동시 요청 지원)
  │   - Docker: `docker run --gpus all vllm/vllm-openai --model llama4-scout`
  └─ VAMOS 연동: D2.0-04 INFRA, S7F-005 모델 라우팅

[F-ADD-05] Speculative Decoding | MED V2
- 구현:
  ├─ 작은 모델로 먼저 드래프트 → 큰 모델로 검증:
  │   - Draft: Phi-4 (14B) → 빠른 토큰 생성
  │   - Verify: Llama 4 Scout (17B active) → 드래프트 검증
  │   - 결과: 품질 유지 + 속도 2-3배 향상
  ├─ VAMOS 적용: 긴 응답 생성 시 자동 활성화
  └─ V2: vLLM speculative decoding 옵션 활성화

[G-ADD-04] BFCL v3 (Function Calling 벤치마크) | HIGH V1
- 구현:
  ├─ Berkeley Function Calling Leaderboard v3 기준 VAMOS 평가:
  │   - 단순 함수 호출 정확도
  │   - 복합 함수 체이닝 정확도
  │   - 병렬 함수 호출 정확도
  │   - 파라미터 추출 정확도
  ├─ VAMOS 목표: AST 정확도 > 85% (V1), > 92% (V2)
  └─ 연동: D2.0-02 Execution Stage, K-001 MCP Tool 호출 검증

[H-ADD-02] VAMOS 가격 전략 상세 | HIGH V1
- 구현:
  ├─ 경쟁사 가격 비교:
  │   | 서비스 | 월 가격 | 특징 |
  │   |--------|---------|------|
  │   | ChatGPT Plus | ₩28,000 | GPT-4o, 40msg/3h |
  │   | Claude Pro | ₩28,000 | Opus 4.6, 제한적 |
  │   | Gemini Advanced | ₩28,000 | 2M 토큰, Gems |
  │   | VAMOS V1 | ₩0~10,000 | 로컬 무제한+API 제한 |
  │   | VAMOS V2 | ₩20,000~40,000 | 모든 기능, 서버 포함 |
  ├─ 차별화 메시지:
  │   "시중 AI 구독 1개 가격으로, 모든 AI의 기능 + 프라이버시 + 투자 + 자동화"
  └─ VAMOS 연동: PLAN-3.0 수익 모델, S7H-001 가격 전략

[I-ADD-03] OpenBB v4 통합 | HIGH V1
- 구현:
  ├─ OpenBB Platform v4 연동:
  │   - MCP 서버로 래핑: 주가/재무/뉴스/애널리스트 데이터 접근
  │   - 무료 데이터 소스: Yahoo Finance, FRED, SEC, Alpha Vantage
  │   - OpenBB SDK:
  │     from openbb import obb
  │     obb.equity.price.historical("AAPL", provider="yfinance")
  │     obb.equity.fundamental.income("AAPL", period="annual")
  │     obb.economy.gdp.nominal(provider="oecd")
  ├─ VAMOS 투자 데이터 레이어 통합:
  │   - 기존 83개 데이터 소스에 OpenBB 통합
  │   - 중복 소스 deduplicate
  │   - OpenBB의 데이터 정규화 활용
  └─ V1: 즉시 (pip install openbb), V2: MCP 서버 래핑

- VAMOS 연동:
  ├─ AI Investing: 7-Layer 데이터 아키텍처에 OpenBB 레이어 추가
  ├─ Quant Node: OpenBB 데이터 직접 활용
  └─ D2.0-03: OpenBB MCP 서버 등록
```

---

## 11. VAMOS 아키텍처 통합 크로스레퍼런스

### 11.1 I/E/S/A 시리즈 매핑

| VAMOS 핵심 컴포넌트 | 관련 STEP7 카테고리 | 주요 보강 항목 |
|-------------------|------------------|-------------|
| I-2 RAG Pipeline | D(메모리), 보강(P-RAG) | GraphRAG, Self-RAG, CRAG, ColPali |
| I-5 Agent Pool | A(경쟁분석), K(에이전트) | Agent Teams, MCP 2.0, A2A, Swarm |
| I-6 Self-check | G(벤치마크), A(혁신) | Auto-Eval, 할루시네이션 탐지, Confidence |
| I-9 Cost Ceiling | F(인프라), E(보안) | 비용 최적화 엔진, Prompt Caching, 로컬 우선 |
| I-12 Blue Nodes | K(에이전트), L(개발자) | MCP Tool, Agent SDK, 프로토콜 브릿지 |
| I-13 Routing | A(경쟁분석), F(인프라) | 모델 라우팅, HybridRouter, MoE |
| I-18 Memory | D(메모리), M(PKM) | 5-Layer, MemGPT, Obsidian, Dream Mode |
| E-1 STRIDE | E(보안) | 위협 모델, OWASP LLM, Agent 보안 |
| S-1~S-9 States | B(대화), K(에이전트) | Adaptive Thinking, Multi-Agent 상태 |
| A-1~A-4 Arch | A(경쟁분석), H(비즈니스) | 모든 경쟁사 대비 아키텍처 차별화 |

### 11.2 5 Gates 통합 포인트

| Gate | STEP7 보강 항목 | 확장 내용 |
|------|--------------|---------|
| Policy Gate | S7E-011~016 (Injection 방어) | Instruction Hierarchy, Canary Token |
| Evidence Gate | S7G-005 (할루시네이션 탐지) | Self-RAG, GraphRAG 근거 검증 |
| Cost Gate | S7F-030 (비용 최적화) | Prompt Caching, Local-First, Budget Forcing |
| Approval Gate | S7E-021~023 (인증/접근) | OAuth2, RBAC, MFA (V2) |
| SelfCheck Gate | S7G-001 (Auto-Eval) | QoD 자동 평가, SWE-Bench |

### 11.3 9-State Machine 확장

```
기존 9개 상태에 STEP7 보강으로 추가되는 하위 상태:

IDLE → RECEIVING:
  + emotion_detection (S7B-002)
  + sensitivity_classification (S7F-055)

ANALYZING:
  + reasoning_effort_selection (A-ADD-02)
  + causal_question_detection (S7-F-030)

RETRIEVING:
  + hybrid_search (S7D-012)
  + self_rag_evaluation (S7-P-007)
  + graph_rag_query (S7-P-005)

ROUTING:
  + hybrid_local_cloud (S7-F-024)
  + model_tier_selection (S7-A-013)

EXECUTING:
  + multi_agent_orchestration (S7-O-004)
  + mcp_tool_call (K-001~010)
  + a2a_delegation (K-011~020)

SELF_CHECKING:
  + auto_eval_qod (S7G-001)
  + hallucination_detect (S7G-005)
  + confidence_estimate (S7-F-025)

OUTPUTTING:
  + tone_adaptation (S7B-003)
  + confidence_display (S7-F-025)
  + citation_inline (S7B-013)

LEARNING:
  + knowledge_extraction (M-001)
  + memory_promotion (S7D-040)
  + dream_mode_optimization (S7-F-055)
```

### 11.4 V1/V2/V3 구현 로드맵 종합

```
[V1 -- 로컬 MVP] (0~9개월)
├─ CRITICAL 전체: ~238건 (R1 134건 최우선)
├─ HIGH V1: ~350건 (R2)
├─ MED/LOW V1: ~82건 (R3 일부)
├─ 핵심 기술:
│   ├─ 로컬 LLM (Llama 4 Scout, Phi-4) + Ollama
│   ├─ 클라우드 API 라우팅 (Claude/GPT/Gemini)
│   ├─ 3-Layer Memory (L0/L1/L2) + Chroma + NetworkX KG
│   ├─ 7단계 파이프라인 + 5-Gate + 3-Part Output
│   ├─ Tauri 데스크톱 앱 + CLI
│   ├─ MCP 기본 도구 10+
│   └─ 비용: ≤ ₩10,000/월
└─ 비용: $0 (개발) / ₩0~10,000 (운영)

[V2 -- 서버 확장] (9~18개월)
├─ CRITICAL/HIGH V2: ~330건 (R4)
├─ MED/LOW V2: ~280건 (R5)
├─ 핵심 기술:
│   ├─ Kubernetes 배포 + 자동 스케일링
│   ├─ Qdrant 벡터DB + Neo4j KG
│   ├─ OAuth2 + MFA + Zero-Trust
│   ├─ PWA + VSCode 플러그인 + 크로스디바이스
│   ├─ A2A 프로토콜 + Tool 마켓플레이스
│   ├─ Extended Thinking + Deep Research
│   ├─ 음성 대화 + 이미지 생성
│   └─ Dream Mode + Predictive AI
└─ 비용: ≤ ₩40,000/월

[V3 -- 엔터프라이즈] (18~30개월)
├─ V3 전체: ~248건 (R6)
├─ 핵심 기술:
│   ├─ 멀티유저 + 팀 협업 + SSO
│   ├─ 연합 에이전트 + 자율 프로토콜
│   ├─ 실시간 카메라/화면 분석 + AR/VR
│   ├─ 국가별 규제 적응 + ISO 42001
│   ├─ 자기진화 에이전트 아키텍처
│   ├─ 모바일 자동화 (Appium)
│   └─ 학습/웰니스 커뮤니티
└─ 비용: ≤ ₩200,000/월
```

---

## 12. 미반영 항목 우선순위 정리

### 12.1 즉시 반영 필요 (CRITICAL, 기존 문서에 미반영)

| 항목 | 카테고리 | 이유 |
|------|---------|------|
| Part F 혁신기술 V1 CRITICAL | A | 아키텍처 핵심 차별화, 경쟁사 대비 선점 |
| F/G/H CRITICAL 인프라/벤치마크/비즈니스 | F/G/H | 출시 필수 인프라, 품질 보증 |
| I CRITICAL 실시간 데이터 | I | 투자 기능 핵심, 기존 투자 스펙에 미반영 |
| K CRITICAL MCP/A2A 심화 | K | 에이전트 상호운용성 핵심 |

### 12.2 V1 출시 전 반영 권장 (HIGH)

| 항목 | 카테고리 | 이유 |
|------|---------|------|
| 비용 최적화 엔진 | F | V1 월 ₩10,000 목표 달성 핵심 |
| 할루시네이션 탐지 | G | 신뢰성 확보 필수 |
| REST API + Python SDK | L | 외부 연동 기반 |
| Obsidian 통합 | M | 타겟 사용자(개발자/지식근로자) 핵심 도구 |
| 백테스팅 고급 | I | 투자 기능 경쟁력 |

### 12.3 V2 구현 계획 (우선 설계만)

| 항목 | 카테고리 | 이유 |
|------|---------|------|
| Kubernetes + 자동 스케일링 | F | V2 서버 전환 핵심 |
| A2A 프로토콜 | K | 외부 AI 에이전트 협업 |
| 음성 대화 모드 | J | 멀티모달 핵심 |
| Dream Mode | A(혁신) | 차별화 핵심 기능 |
| IDE 플러그인 | L | 개발자 접근성 |

---

## 부록 A: 카테고리별 소스 파일 참조

| 카테고리 | 작업가이드 파일 | R 라운드 |
|---------|-------------|---------|
| A | STEP7_작업가이드.md | R1,R2,R3,R4,R5,R6 전 라운드 |
| B | STEP7-B_대화프로세스_작업가이드.md | R1,R2,R3,R4,R5,R6 |
| C | STEP7-C_UI_UX_전수비교_작업가이드.md | R1,R2,R3,R4,R5,R6 |
| D | STEP7-D_메모리_저장소_아키텍처_작업가이드.md | R1,R2,R3,R4,R5,R6 |
| E | STEP7-E_보안_안전_거버넌스_작업가이드.md | R1,R2,R3,R4,R5,R6 |
| F | STEP7-F_인프라_배포_MLOps_작업가이드.md | R1(일부),R2(일부) |
| G | STEP7-G_벤치마크_평가_품질보증_작업가이드.md | R1(일부),R2(일부) |
| H | STEP7-H_비즈니스모델_시장전략_작업가이드.md | R2(일부) |
| I | STEP7-I_AI_Investing_보강_작업가이드.md | R2(일부) |
| J | STEP7-J_멀티모달_생성처리_작업가이드.md | R1(일부),R2(일부) |
| K | STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md | R2(일부) |
| L | STEP7-L_개발자도구_API_SDK_작업가이드.md | R2(일부) |
| M | STEP7-M_PKM_지식관리_작업가이드.md | R2(일부) |
| N | STEP7-N_워크플로우자동화_RPA_작업가이드.md | R1,R2,R3 완료 |
| O | STEP7-O_교육_학습_자기개발_작업가이드.md | R1,R2,R3 완료 |
| P | STEP7-P_건강_웰니스_감성AI_작업가이드.md | R1,R2,R3 완료 |
| 보강 | STEP7_A-I_보강_추가항목_통합.md | R1,R2,R3 일부 |

## 부록 B: 용어 정의

| 용어 | 정의 |
|------|------|
| TITLE_ONLY | 마스터인덱스에 제목/1줄 요약만 존재, 구현 상세 미작성 상태 |
| 5-Gate | Policy Gate + Approval Gate + Cost Gate + Evidence Gate + SelfCheck Gate (VAMOS 안전 장치, 정본: D2.0-02 §2.3 + CLAUDE.md §5 LOCK) |
| 9-State Machine | IDLE/RECEIVING/ANALYZING/RETRIEVING/ROUTING/EXECUTING/SELF_CHECKING/OUTPUTTING/LEARNING |
| 3-Part Output | [Header: 메타정보] [Body: 응답 본문] [Footer: 근거/비용/신뢰도] |
| I/E/S/A 시리즈 | Intelligence/Evidence/Safety/Architecture 핵심 모듈 시리즈 |
| Decision Object | 파이프라인 결정의 구조화된 기록 (결정/근거/비용/신뢰도) |
| Blue Node | VAMOS 도메인별 전문 에이전트 (Dev/Research/Quant/Content/Trading) |
| Orange Core | VAMOS 중앙 조율 엔진 (7단계 파이프라인) |
| MCP | Model Context Protocol (Anthropic 도구 호출 표준) |
| A2A | Agent-to-Agent Protocol (Google 에이전트 간 통신 표준) |
| KG | Knowledge Graph (지식 그래프) |
| RAG | Retrieval-Augmented Generation (검색 증강 생성) |
| QoD | Quality of Decision (결정 품질 점수) |
| Dream Mode | 비활성 시간 자동 최적화 모드 |
| Digital Twin | 사용자 행동 패턴의 디지털 복제 모델 |

---

*생성일: 2026-02-23*
*범위: STEP7 1,545건 중 TITLE_ONLY 항목 상세 확장*
*총 라인: 1,000+*
*원칙: 모든 항목에 구현 방식, 기술 스택, 스키마, API, VAMOS 아키텍처 연동점 명시*

---

<\!-- END OF DOCUMENT -->
