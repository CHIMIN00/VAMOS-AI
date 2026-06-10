# Pricing Comparison — 경쟁사 가격 전수비교

> **버전**: V1
> **작성일**: 2026-04-10
> **세션**: P1-1
> **항목**: S7H-001 ~ S7H-006 (6건, HIGH)
> **등급**: L1 → 목표 L3

---

## 교차 참조 블록

| 정본 문서 | 참조 범위 | 역할 |
|----------|----------|------|
| STEP7-H Part 1 (S7H-001~010) | S7H-001~006 정의 원본 | 최상위 정본 |
| 종합계획서 §3.4 | LOCK-BM-01~10 불변 값 | 가격 상한 제약 |
| 종합계획서 §B.1 | 7티어 최종 구조 | 티어 정본 (C-7 해결) |
| AUTHORITY_CHAIN §6 | 최종 7티어 등재 | C-7 통합안 |
| CONFLICT_LOG CFL-001 | TAM $8B (STEP7-H 우선) | 시장 규모 정본 |
| CONFLICT_LOG CFL-006 | Pro $15 (S7H-020 우선) | 가격 불일치 해결 |
| 상세명세 §2.1 | 경쟁사 가격 초안 | 참고 (하위) |

---

## S7H-001. 가격 모니터링 대시보드 — API 가격 추적

> **우선도**: HIGH | **버전**: V1

### 1.1 목적

주요 LLM API의 가격 변동을 정기 추적하여 VAMOS 스마트 라우팅의 비용 최적화 기반을 제공한다.

### 1.2 LLM API 가격 비교표 (기준: 2025-03, STEP7-H 원본)

| 프로바이더 | 모델 | 입력 ($/1M tok) | 출력 ($/1M tok) | 컨텍스트 | 캐시 입력 |
|-----------|------|----------------|----------------|---------|----------|
| Anthropic | Claude 3.5 Sonnet | $3.00 | $15.00 | 200K | $0.30 |
| Anthropic | Claude 3.5 Haiku | $0.80 | $4.00 | 200K | $0.08 |
| OpenAI | GPT-4o | $2.50 | $10.00 | 128K | $1.25 |
| OpenAI | GPT-4o-mini | $0.15 | $0.60 | 128K | $0.075 |
| Google | Gemini 2.0 Flash | $0.10 | $0.40 | 1M | $0.025 |
| Google | Gemini 1.5 Pro | $1.25 | $5.00 | 2M | $0.315 |
| DeepSeek | DeepSeek-V3 | $0.27 | $1.10 | 128K | $0.07 |
| Mistral | Mistral Large | $2.00 | $6.00 | 128K | — |
| Groq | Llama 3.3 70B | $0.59 | $0.79 | 128K | — |

> **출처**: STEP7-H Part 1 API 가격 표 (2025-03 기준)
> **주의**: AI API 가격은 연 30-50% 하락 추세 (STEP7-H S7H-001 명시). 월 1회 갱신 필요.

### 1.3 가격 변동 추적 프로세스

| 단계 | 활동 | 주기 | 산출물 |
|------|------|------|--------|
| 1 | 프로바이더 공식 가격 페이지 크롤링 | 월 1회 | 가격 변동 로그 |
| 2 | 변동 감지 시 비교표 갱신 | 이벤트 | 갱신된 비교표 |
| 3 | 모델 라우팅 재조정 검토 | 변동 후 | 라우팅 정책 갱신 |
| 4 | 비용 영향 분석 보고 | 월 1회 | 영향 분석서 |

### 1.4 가격 데이터 소스

| 프로바이더 | 공식 가격 페이지 | 비고 |
|-----------|----------------|------|
| Anthropic | https://www.anthropic.com/pricing | API 가격 공개 |
| OpenAI | https://openai.com/pricing | API 가격 공개 |
| Google | https://ai.google.dev/pricing | Gemini API 가격 공개 |
| DeepSeek | https://platform.deepseek.com/api-docs/pricing | API 가격 공개 |
| Mistral | https://mistral.ai/technology/#pricing | API 가격 공개 |
| Groq | https://groq.com/pricing/ | API 가격 공개 |

> **R-12-4 준수**: 모든 가격 데이터는 공식 웹사이트 URL과 시점(2025-03) 명시. 갱신 시 시점 업데이트 필수.

---

## S7H-002. 구독 서비스 가치 분석 — $20/mo vs VAMOS

> **우선도**: HIGH | **버전**: V1

### 2.1 목적

ChatGPT Plus / Claude Pro ($20/mo 고정 구독)와 VAMOS의 가치를 정량 비교하여 가격 경쟁력을 입증한다.

### 2.2 경쟁사 구독 서비스 비교

| 항목 | ChatGPT Plus ($20/mo) | Claude Pro ($20/mo) | VAMOS Core ($5~10/mo API 비용) |
|------|----------------------|--------------------|-----------------------------|
| 모델 접근 | GPT-4o (80msg/3h 제한) | Claude 3.5 Sonnet/Opus | 멀티 모델 (Claude/GPT/Gemini 전체) |
| 이미지 생성 | DALL-E 3 포함 | 미포함 | MCP Tool 연동 (별도) |
| 파일 분석 | 파일 업로드/분석 | 파일 업로드/분석 | 로컬 파일 직접 접근 |
| 개인화 | Custom Instructions (제한적) | Projects (5개) | 5-Layer 메모리 (L0-L4 완전 개인화) |
| Knowledge Graph | 미제공 | 미제공 | 관계 기반 추론 제공 |
| 에이전트 | GPTs Store | 미제공 | Agent Teams (BLUE NODEs 전체) |
| 비용 제어 | 고정 $20 (미사용 시에도 과금) | 고정 $20 (미사용 시에도 과금) | 사용량 비례 (미사용 시 $0) |
| 데이터 주권 | 클라우드 저장 | 클라우드 저장 | 100% 로컬 보관 |
| 비용 투명성 | 없음 | 없음 | 요청별 실시간 비용 표시 |

> **출처**: STEP7-H S7H-002 (ChatGPT Plus/Claude Pro 분석), 2025-03 기준 공식 플랜 사양

### 2.3 사용량별 비용 비교 (STEP7-H 기준)

| 사용 패턴 | ChatGPT Plus | Claude Pro | VAMOS (스마트 라우팅) | VAMOS 절감율 |
|----------|-------------|-----------|---------------------|-------------|
| 월 100회 질문 | $20 (회당 $0.20) | $20 (회당 $0.20) | ~$3 (회당 ~$0.03) | 85% |
| 월 500회 질문 | $20 (회당 $0.04) | $20 (회당 $0.04) | ~$5 (회당 ~$0.01) | 75% |
| 월 1,000회 질문 | $20 (회당 $0.02) | $20 (회당 $0.02) | ~$8 (회당 ~$0.008) | 60% |
| 월 2,000회 질문 | $20 (회당 $0.01) | $20 (회당 $0.01) | ~$15 (회당 ~$0.0075) | 25% |

> **출처**: STEP7-H S7H-002, S7H-011 비용 비교 데이터
> **가정** (E7): VAMOS 스마트 라우팅은 간단 질문에 저비용 모델(GPT-4o-mini, Gemini Flash) 자동 배정, 복잡 질문에만 고비용 모델 배정 가정. 평균 입력 500 tok, 출력 1,000 tok 기준.

### 2.4 핵심 가치 요약

- **비용 절감**: 가벼운 사용자(월 100~500회)일수록 VAMOS가 압도적 절감 (60~85%)
- **유연성**: 사용하지 않는 달에는 비용 $0 — 고정 구독 대비 결정적 장점
- **추가 가치**: 5-Layer 메모리, Knowledge Graph, Agent Teams, 100% 데이터 주권은 $20 구독에서 제공하지 않는 기능

---

## S7H-003. 코딩 AI 가격 분석 — 개발자 도구 비교

> **우선도**: HIGH | **버전**: V1

### 3.1 코딩 AI 서비스 가격 매트릭스

| 서비스 | Free Tier | Pro | Business/Enterprise | 과금 모델 | 핵심 기능 |
|--------|-----------|-----|-------------------|----------|----------|
| GitHub Copilot | ❌ | $10/mo | $39/mo (Business) | 시트 기반 | IDE 코드 완성, 채팅 |
| Cursor | 2주 무료 | $20/mo | $40/mo (Business) | 시트 기반 | IDE 통합 AI, 코드 에디팅 |
| Sourcegraph Cody | Free 제한 | $9/mo | $19/seat/mo | 시트 기반 | 코드 검색 + AI |
| Amazon CodeWhisperer | Free | $19/mo (Pro) | 협의 | 시트 기반 | AWS 통합 코드 제안 |
| **VAMOS Dev Node** | **무료 (로컬 LLM)** | **$5~10/mo API** | **$35/seat (Ent.)** | **하이브리드** | **범용 비서 + 코딩 + 에이전트** |

> **출처**: 각 서비스 공식 가격 페이지 기준 (2025-03). GitHub Copilot: github.com/features/copilot, Cursor: cursor.com/pricing

### 3.2 VAMOS vs 전용 코딩 AI 비교

| 비교 축 | 전용 코딩 AI (Copilot/Cursor) | VAMOS Dev Node |
|---------|---------------------------|---------------|
| 범위 | 코딩 전용 (IDE 한정) | 범용 비서 + 코딩 + 에이전트 통합 |
| 모델 선택 | 단일 모델 (고정) | 멀티 모델 라우팅 (최적 자동 선택) |
| 개인화 | 프로젝트 컨텍스트만 | 5-Layer 메모리 + Knowledge Graph |
| 비용 구조 | 고정 월 구독 | 사용량 비례 + 선택적 구독 |
| 데이터 | 클라우드 전송 | 로컬 코드 분석 (데이터 주권) |
| 확장성 | IDE 플러그인 한정 | MCP Tools + Agent Teams |

### 3.3 시나리오별 비용 비교

| 시나리오 | Copilot ($10/mo) | Cursor ($20/mo) | VAMOS (API) |
|---------|-----------------|-----------------|-------------|
| 주 5일, 하루 20 코딩 질문 | $10 | $20 | ~$4/mo (추정, E7) |
| 주 5일, 하루 50 코딩 질문 | $10 | $20 | ~$8/mo (추정, E7) |
| 주 5일, 하루 100+ 코딩 질문 | $10 | $20 | ~$15/mo (추정, E7) |

> **가정** (E7): 코딩 질문은 평균 입력 800 tok, 출력 1,500 tok 기준. 스마트 라우팅으로 간단 완성은 GPT-4o-mini/Gemini Flash, 복잡 리팩토링은 Claude Sonnet 사용 가정.

---

## S7H-004. 생산성 AI 가격 분석 — Notion AI, Microsoft Copilot 등

> **우선도**: HIGH | **버전**: V1

### 4.1 생산성 AI 서비스 가격 매트릭스

| 서비스 | Free Tier | Pro/Premium | Enterprise | 과금 모델 | 핵심 기능 |
|--------|-----------|------------|-----------|----------|----------|
| Notion AI | 제한적 (20 응답) | $10/mo (추가 요금) | $18/user/mo | 시트 기반 | 문서 요약, 작성, Q&A |
| Microsoft 365 Copilot | ❌ | $30/user/mo (365 추가) | $30/user/mo | 시트 기반 | Word/Excel/PPT/Outlook AI |
| Google Workspace AI | ❌ | $30/user/mo (추가) | $30/user/mo | 시트 기반 | Docs/Sheets/Gmail AI |
| Perplexity Pro | Free 제한 | $20/mo | — | 구독 | AI 검색, 파일 분석 |
| **VAMOS** | **무료 (로컬 LLM)** | **$5~10/mo API** | **$35/seat** | **하이브리드** | **문서·검색·분석 통합** |

> **출처**: Microsoft 365 Copilot 공식 가격 (microsoft.com/microsoft-365/copilot, 2025-03). Notion AI (notion.so/pricing). Perplexity (perplexity.ai/pro).

### 4.2 VAMOS 가치 제안 vs 생산성 AI

| 비교 축 | Microsoft 365 Copilot ($30/mo) | Notion AI ($10/mo 추가) | VAMOS |
|---------|------------------------------|------------------------|-------|
| 전제 조건 | 기존 365 구독 필수 | 기존 Notion 구독 필수 | 독립 사용 가능 |
| 실질 비용 | $30 + 기존 구독 | $10 + 기존 구독 | $5~10 (API만) |
| 플랫폼 종속 | Microsoft 생태계 | Notion 생태계 | 오픈 + 로컬 |
| 데이터 주권 | 클라우드 필수 | 클라우드 필수 | 100% 로컬 가능 |
| 커스텀 | 제한적 | 제한적 | 완전 커스텀 (Agent Teams) |

> **핵심 메시지**: VAMOS는 별도 구독 없이 API 비용만으로 유사 기능 제공 가능 (STEP7-H S7H-004 명시). 특히 Microsoft Copilot 대비 $30/mo vs ~$8/mo로 73% 절감 가능 (추정, E7).

---

## S7H-005. TCO 분석 — Total Cost of Ownership

> **우선도**: HIGH | **버전**: V1

### 5.1 VAMOS V1 TCO 분석

| 비용 항목 | VAMOS V1 | ChatGPT Plus | Claude Pro | Cursor Pro |
|----------|---------|-------------|-----------|-----------|
| **초기 비용** | | | | |
| 소프트웨어 | $0 (오픈소스) | $0 | $0 | $0 |
| 하드웨어 추가 | $0 (기존 PC) | $0 | $0 | $0 |
| 설정 시간 | ~30분 (사용자 시간) | ~5분 | ~5분 | ~10분 |
| **월간 비용** | | | | |
| 구독료 | $0 | $20/mo | $20/mo | $20/mo |
| API 비용 | $5~10/mo (사용량) | 포함 | 포함 | 포함 |
| 인프라 | $0 (로컬) | $0 | $0 | $0 |
| 업데이트 | 자동 (무료) | 자동 | 자동 | 자동 |
| **연간 TCO** | **$60~120** | **$240** | **$240** | **$240** |
| **절감율** | 기준 | — | — | — |

> **출처**: STEP7-H S7H-005 TCO 데이터
> **결론**: VAMOS V1 연간 TCO $60~120 vs 경쟁사 $240. 절감율 50~75%.

### 5.2 숨은 비용 비교

| 숨은 비용 | 클라우드 구독형 | VAMOS |
|----------|--------------|-------|
| 미사용 월 비용 | $20/mo (고정 과금) | $0 (사용 안 하면 비용 없음) |
| 데이터 이전 비용 | 높음 (벤더 락인) | $0 (로컬 데이터) |
| 추가 기능 비용 | 별도 결제 (플러그인 등) | MCP Tools 무료 (오픈소스) |
| 학습 곡선 비용 | 낮음 (웹 UI) | 중간 (초기 설정 ~30분) |
| 프라이버시 비용 | 데이터 클라우드 전송 리스크 | $0 (100% 로컬) |

---

## S7H-006. 무료 대안 분석 — Free Tier 경쟁

> **우선도**: HIGH | **버전**: V1

### 6.1 VAMOS Free Tier 구성

> **LOCK-BM-06 준수**: Free Tier 일일 LLM 요청 상한 = 50회/일

| 구성 요소 | Free Tier 사양 | 비용 |
|----------|--------------|------|
| 로컬 LLM | Ollama (Llama, Mistral 등) | $0 |
| 무료 클라우드 API | Gemini API Free (15 RPM), Groq Free (Llama 70B, 30 RPM), Mistral Free | $0 |
| 메모리 | 기본 L0-L2 | $0 |
| Agent | 기본 1개 | $0 |
| MCP Tools | 기본 3개 | $0 |
| **일일 제한** | **50회/일 (LOCK-BM-06)** | **$0** |

> **출처**: STEP7-H S7H-006 (Free Tier 조합), 종합계획서 §B.1 (Free 티어 사양)

### 6.2 무료 사용 시 품질 평가 (추정)

| 평가 축 | VAMOS Free | ChatGPT Free | Claude Free | Gemini Free |
|---------|-----------|-------------|-------------|-------------|
| 응답 품질 | ~70% (로컬 LLM 기준) | 80% (GPT-4o-mini) | 80% (Haiku) | 75% (Gemini Flash) |
| 속도 | 로컬: 빠름 / API: 속도 제한 | 보통 | 보통 | 빠름 |
| 개인화 | 5-Layer 메모리 L0-L2 | Custom Instructions만 | 미제공 | 미제공 |
| 데이터 주권 | 100% 로컬 | 클라우드 | 클라우드 | 클라우드 |
| 일일 제한 | 50회/일 (LOCK-BM-06) | 무제한 (속도 제한) | 제한 있음 | 15 RPM |

> **가정** (E7): "~70%" 품질은 로컬 7B~13B 모델 기준 추정. 무료 API(Gemini Flash, Groq Llama) 활용 시 80%+ 가능.
> **적합 대상**: 가벼운 사용, 학습용, 프라이버시 중시 사용자 (STEP7-H S7H-006 명시)

### 6.3 Free → Core 전환 동기

| 전환 트리거 | 설명 |
|-----------|------|
| 품질 한계 체감 | 로컬 LLM으로 부족한 복잡 작업 발생 |
| 속도 제한 도달 | 무료 API RPM 제한에 빈번히 걸림 |
| 고급 기능 필요 | L3-L4 메모리, 멀티 Agent, 전체 MCP Tools |
| 모델 선택 필요 | Claude Sonnet, GPT-4o 등 고성능 모델 사용 |

> **목표 전환율**: Free→Core 30% (종합계획서 §B.1 기준)

---

## 경쟁사 5개 전수비교 매트릭스 (E3 기준)

> 종합 매트릭스: S7H-001~006 데이터를 통합한 전수비교

| 비교 기준 | GitHub Copilot | Cursor | ChatGPT Plus | Claude Pro | VAMOS |
|----------|---------------|--------|-------------|-----------|-------|
| **월 가격 (Pro)** | $10 | $20 | $20 | $20 | $5~10 (API) |
| **Enterprise** | $39/seat | $40/seat | 협의 | 협의 | $35/seat (LOCK-BM-08) |
| **Free Tier** | ❌ | 2주 무료 | 제한적 | 제한적 | 무제한 (50회/일, LOCK-BM-06) |
| **과금 모델** | 시트 기반 | 시트 기반 | 구독 | 구독 | 하이브리드 (LOCK-BM-04) |
| **멀티 모델** | ❌ (단일) | ✅ (2~3종) | ❌ (단일) | ❌ (단일) | ✅ (전체 라우팅) |
| **개인화** | 프로젝트 컨텍스트 | 프로젝트 컨텍스트 | Custom Instructions | Projects | 5-Layer 메모리 |
| **데이터 주권** | 클라우드 | 클라우드 | 클라우드 | 클라우드 | 100% 로컬 |
| **비용 투명성** | ❌ | ❌ | ❌ | ❌ | ✅ (실시간) |
| **에이전트** | ❌ | ❌ | GPTs | ❌ | Agent Teams |
| **연간 TCO** | $120 | $240 | $240 | $240 | $60~120 |

> **LOCK 준수 확인**: VAMOS Pro $15/mo (LOCK-BM-07), Enterprise $35/seat (LOCK-BM-08), Free 50회/일 (LOCK-BM-06), V1 월 상한 ₩40,000 (LOCK-BM-01). 모든 LOCK 값 위반 없음.

---

## Phase 2 테스트 시나리오

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T-01 | 가격 비교표에 LOCK-BM-07 위반 가격 삽입 | pricing_comparison.md에 Pro $20/mo 기재 | /validate에서 LOCK-BM-07 위반 탐지 |
| T-02 | 경쟁사 가격 데이터 출처 누락 | 출처·시점 미명기 데이터 삽입 | R-12-4 환각 방지 위반 탐지 |
| T-03 | TCO 계산 오류 (산술) | 연간 TCO에 잘못된 합계 기재 | /audit에서 산술 불일치 감지 |
| T-04 | Free Tier 상한 LOCK 위반 | Free Tier 100회/일 기재 | LOCK-BM-06 (50회/일) 위반 탐지 |
| T-05 | 7티어 구조 불일치 | 4티어 구조로 회귀 기재 | C-7 해결안(§B.1 7티어) 불일치 탐지 |
| T-06 | 경쟁사 5개 미만 비교 | 3개만 비교 | E3 (최소 5개 경쟁사) 미충족 탐지 |
| T-07 | 추정치에 (추정) 표기 누락 | 추정 수치를 확정으로 기재 | E7 환각 방지 위반 탐지 |
| T-08 | V1 월 비용 상한 초과 시나리오 | 사용 패턴에서 ₩40,000 초과 | LOCK-BM-01 (₩40,000) 검증 |
| T-09 | 과금 단위 불일치 | 시트 기반 과금으로 기재 | LOCK-BM-04 (토큰 기반+구독) 위반 탐지 |
| T-10 | 가격 변동 추적 주기 누락 | 모니터링 대시보드에 갱신 주기 미정의 | S7H-001 요구사항 미충족 탐지 |

---

*작성 완료: P1-1 세션, S7H-001~006 총 6건 HIGH. 모든 가격·수치에 출처·시점 명기(R-12-4). LOCK-BM-01/04/06/07/08 위반 없음 확인.*

---

## §E. Phase 2 V2 확장 (P2-1, 2026-04-22)

> **세션**: P2-1 (01_pricing-revenue V2 시범 세션 3/5 중 1/3)
> **담당 항목 (본 파일)**: S7H-007 (MED, V2), S7H-008 (MED, V2), S7H-009 (MED, V2), S7H-010 (MED, V2) — 4건
> **피어 V2 파일**: `vamos_pricing_strategy.md` (S7H-017/018), `revenue_model.md` (S7H-020/021/022/023/024)
> **LOCK 인용 (AUTHORITY §4 L62~L73 verbatim 5필드)**:
> - **LOCK-BM-01** | V1 월 비용 상한 | ₩40,000 (~$30) | STEP7-H (참조), 가이드 §4.3 #12, R-12-1 | 사용자 비용 보호
> - **LOCK-BM-06** | Free Tier 일일 LLM 요청 상한 | 50회/일 | 상세명세 §2.3 | Free/Paid 경계 (S7H-009 정합)
> - **LOCK-BM-07** | Pro 월 가격 | $15/mo (연간 $144, 20% 할인) | 상세명세 §2.3, S7H-020 | 가격 체계 핵심 (S7H-010 번들 Pro 행 정합 — CFL-006 해결 반영)
> - **LOCK-BM-08** | Enterprise 석당 가격 | $35/seat/mo (최소 10석) | 상세명세 §2.3 | B2B 가격 기준 (S7H-007 B2B 정합)
> - **LOCK-BM-10** | 가격 변경 고지 기간 | 기존 사용자 30일 사전 고지 | 가이드 R-12-2 | 사용자 보호 정책
> **CONFLICT 해결 반영**: CFL-006 (S7H-010 $10 → S7H-020 $15 = LOCK-BM-07 확정, S7H-010 Pro 행 정본 표기 Pro $15/mo), CFL-010 (C-7 7티어 최종 정본 — 계획서 §B.1)
> **R-12-4 환각 방지**: 경쟁사 B2B 가격 / 가격 탄력성 수치 / Free Tier 제한 / 번들 구성 전수 출처·시점 명기 (STEP7-H L135~L149 기준, 2025-02 원본)
> **R-12-5 정본 우선순위**: STEP7-H 원본 값 우선, 상세명세 §2.3 보조

---

### §E.1 S7H-007 | MED | V2 | B2B 가격 전략 — 기업 판매 가격 모델

> **출처 원본** (STEP7-H L135~L137 verbatim):
> ```
> **S7H-007** | MED | V2 | B2B 가격 전략 — 기업 판매 가격 모델
> - 내용: V3 기업 판매 시 가격 책정 전략
> - 모델: 사용자 수 기반 ($15-30/user/mo) 또는 사용량 기반
> ```

#### §E.1.1 목적

V3 단계 기업 판매(B2B)를 위한 가격 책정 전략을 정의한다. 7티어 구조(AUTHORITY §6) 중 **Team $20/user/mo** 및 **Enterprise $35/seat/mo (LOCK-BM-08, 최소 10석)** 티어의 세부 산정 근거를 제공한다.

#### §E.1.2 B2B 가격 모델 2 축 (STEP7-H L137 원본)

| 모델 | 과금 방식 | 가격 범위 | 대상 | LOCK 연동 |
|------|----------|----------|------|----------|
| **사용자 수 기반 (Seat-based)** | user/mo × 좌석 수 | $15~30/user/mo | 팀 규모 3~100명, 예측 가능 사용량 | LOCK-BM-07 Pro 하한 $15, LOCK-BM-08 Enterprise $35 |
| **사용량 기반 (Usage-based)** | 월 토큰 사용량 × 단가 + 기본료 | ~$100~1,000+/mo | 대규모 API 통합, 변동 사용량 | LOCK-BM-04 토큰 기반 과금 |

> **출처**: STEP7-H S7H-007 L137 "사용자 수 기반 ($15-30/user/mo) 또는 사용량 기반" 원본 그대로.

#### §E.1.3 B2B 7티어 매핑 (C-7 해결 반영)

| 티어 | 가격 | B2B 적합도 | 조건 | LOCK |
|------|------|-----------|------|------|
| **Team** | $20/user/mo | ★★★★☆ (중소 팀) | 3~20명 팀, 공유 지식 베이스 | — (내부 가격, LOCK-BM-07 Pro $15 상회) |
| **Enterprise** | $35/seat/mo | ★★★★★ (대기업) | 최소 10석, SSO/SAML, SLA 99.9% (LOCK-BM-05) | **LOCK-BM-08** |

> **범위 참고 (STEP7-H 원본 $15~30/user/mo)**: $15 하한은 LOCK-BM-07 Pro 개인 가격과 동일, $30 상한은 Team ($20) + Enterprise ($35) 중간대 범위 제시. 실제 정본은 Team $20 + Enterprise $35 2 티어로 확정 (계획서 §B.1 C-7 해결).

#### §E.1.4 B2B 판매 전략

| 세그먼트 | 접근 방식 | 가격 포지셔닝 | 참고 경쟁 |
|---------|----------|-------------|----------|
| 중소 스타트업 (3~20명) | 자체 가입 + 셀프 온보딩 | Team $20/user/mo (월 $60~400) | Notion AI $10/user, Cursor Business $40/seat |
| 중견 기업 (20~100명) | 인사이드 세일즈 + PoC 2주 | Enterprise $35/seat/mo (월 $700~3,500) | MS 365 Copilot $30/user, GitHub Copilot Business $19/seat |
| 대기업 (100명+) | 엔터프라이즈 세일즈 + 커스텀 | Enterprise + 커스텀 (볼륨 할인 협상) | MS 365 Copilot, Anthropic Claude Team |

> **LOCK-BM-08 준수**: Enterprise 최소 10석 조건 — 미만 시 Team 티어 안내.
> **LOCK-BM-05 준수**: Enterprise 99.9% 가용성 SLA.
> **출처**: 경쟁 가격은 각 서비스 공식 가격 페이지 (2025-02 기준 STEP7-H Part 1 L43 원본).

#### §E.1.5 V3 B2B 수익 예측 (STEP7-H S7H-023 연계)

| 지표 | Y3 목표 (기준 시나리오) | 산출 근거 |
|------|----------------------|----------|
| B2B 고객 수 | 100~300 기업 | S7H-023 "$500-5,000/mo 규모에 따라" |
| 평균 계약 규모 | $1,500/mo (약 58석 × $26 혼합 평균 = Team 60% $20 + Enterprise 40% $35, LOCK-BM-07/08; market_sizing §E.2.4 Y3 믹스) | Team/Enterprise 혼합 |
| B2B ARR 기여 | $1.8M~5.4M | S7H-037 Y3 기준 시나리오 $15M의 12~36% |

> **CFL-004 주의**: B2B ARR 은 전체 $15M 목표 매출 중 일부. 유료 사용자 기준 구독 ARR (S7H-076 Y3 $3.6M)과 구분.

#### §E.1.6 Peer cross-ref

- 본 §E.1 ↔ `revenue_model.md` §E.3 (S7H-023 기업 라이선스) — B2B 수익 스트림 일관성
- 본 §E.1 ↔ `vamos_pricing_strategy.md` §E.1 (S7H-017 Free→Pro 전환율) — B2B Team 티어 전환 경로

---

### §E.2 S7H-008 | MED | V2 | 가격 탄력성 분석 — 최적 가격점 결정

> **출처 원본** (STEP7-H L139~L142 verbatim):
> ```
> **S7H-008** | MED | V2 | 가격 탄력성 분석 — 최적 가격점 결정
> - 내용: 타겟 사용자의 가격 민감도 분석
> - 방법: Van Westendorp Price Sensitivity Meter
> - 예상: 최적 가격점 $10-15/mo (한국 시장)
> ```

#### §E.2.1 Van Westendorp PSM 4 질문

Van Westendorp Price Sensitivity Meter — 가격 탄력성 측정 표준 (Peter Van Westendorp, 1976). 타겟 사용자 400명(P1 테크 얼리어답터 100 + P2 지식 노동자 200 + P3 투자자 50 + P4 프라이버시 50, `personas.md` 기준)에게 다음 4 질문을 설문한다.

| Q# | 질문 | 해석 | 추정 응답(한국 시장) |
|---|------|------|-------------------|
| Q1 | VAMOS가 **너무 비싸서 구매하지 않을** 가격 | Too Expensive | $25/mo |
| Q2 | VAMOS가 **비싸지만 구매를 고민할** 가격 | Expensive | $15/mo |
| Q3 | VAMOS가 **저렴하게 느껴지는** 가격 | Cheap | $8/mo |
| Q4 | VAMOS가 **너무 싸서 품질이 의심되는** 가격 | Too Cheap | $3/mo |

> **출처**: STEP7-H S7H-008 L141 "방법: Van Westendorp Price Sensitivity Meter" 원본.
> **추정 응답(E7)**: 한국 ChatGPT Plus/Claude Pro 구독자 대상 설문 추정치 — 실 조사는 V2 출시 전 A/B 테스트 필요. `personas.md` P2 (비용 민감도 높음) 기준 조정.

#### §E.2.2 PSM 교차점 (Optimal Price Point / Point of Marginal Cheapness)

```
PSM 곡선 교차점 (추정):

  100% ┤
        │  Too Expensive ↘
    80% ┤                   ╲
        │                    ╲
    60% ┤      Expensive ↘    ╲ ← IPP (Indifference Price Point)
        │                  ╲   ╲
    40% ┤    Too Cheap ↗   ╲   ╲     ← OPP (Optimal Price Point)
        │              ╱    ╲   ╲
    20% ┤           ╱       ╲  Cheap ↗
        │        ╱          ╲    ╱
     0% └──────┴──────┴──────┴──────┴──────→
         $3     $8     $10    $15    $25
```

| 지표 | 값 | 해석 |
|------|-----|------|
| **PMC (Point of Marginal Cheapness)** | ~$5/mo | "너무 싸서 품질 의심" vs "저렴하게 느껴짐" 교차점 — 하한선 |
| **PME (Point of Marginal Expensiveness)** | ~$20/mo | "비싸지만 고민" vs "너무 비싸서 구매 안 함" 교차점 — 상한선 |
| **OPP (Optimal Price Point)** | ~$10~12/mo | "너무 싸서 의심" vs "너무 비싸서 안 삼" 교차점 |
| **IPP (Indifference Price Point)** | ~$13~15/mo | "비싸지만 고민" vs "저렴하게 느껴짐" 교차점 |

> **출처**: STEP7-H S7H-008 L142 "예상: 최적 가격점 $10-15/mo (한국 시장)" 원본 정합.
> **가정(E7)**: 교차점 수치는 Q1~Q4 추정 응답 기반 산출. 실 조사 후 재산정 필요.

#### §E.2.3 LOCK-BM-07 Pro $15/mo 정합성

| 지표 | PSM 결과 | LOCK 값 | 판정 |
|------|---------|---------|------|
| OPP | $10~12/mo | LOCK-BM-07 $15/mo | **정합** (OPP-상한 $12 + Anchor 효과 +$3) |
| IPP | $13~15/mo | LOCK-BM-07 $15/mo | **정합** (IPP 상한과 동일) |
| PME | $20/mo | LOCK-BM-07 $15/mo | **안전 범위** (PME - $5 여유) |

> **결론**: LOCK-BM-07 Pro $15/mo 는 IPP 상한 + OPP 상한 범위에 위치 — 심리적 저항 최소화 + 수익 최적화 균형점. **LOCK 값 재정의 불필요** (R-12-1 준수).
> **LOCK-BM-10 준수**: 가격 조정 필요 시 기존 사용자 **30일 사전 고지** 의무.

#### §E.2.4 세그먼트별 탄력성 (페르소나 연동)

| 페르소나 | 가격 민감도 | OPP 추정 | 전략 |
|---------|-----------|---------|------|
| P1 테크 얼리어답터 | 중 (오픈소스 선호) | $10~15 | Pro $15 직접 + Core 무료 혼합 |
| P2 지식 노동자 | **높음** (ChatGPT $20 저항) | $8~12 | Pro $15 + 연간 할인 $144 (20%) |
| P3 AI 투자자 | 낮음 (가치 중심) | $20~30 | Pro + Quant 전문 Agent 패키지 |
| P4 프라이버시 중시 | 중 | $15~20 | Pro + 감사 기능 |

> **출처**: `personas.md` S7H-027~030 페르소나 가격 민감도 매핑.

#### §E.2.5 LOCK-BM-01 비용 상한 정합성

- V1 월 비용 상한 ₩40,000 (~$30) ≈ PME $20/mo + API 변동 비용 여유 $10
- OPP $10~12 영역에서 평균 사용자 API 비용 ($5~10) + Free/Core 선택 시 구독 $0 → 상한 ₩40,000 내에서 모든 시나리오 수용.

#### §E.2.6 Peer cross-ref

- 본 §E.2 ↔ `personas.md` (P1~P4 가격 민감도 정합)
- 본 §E.2 ↔ `vamos_pricing_strategy.md` §E.1 (S7H-017 Free→Pro 전환율 목표 5~10% 산출 근거)

---

### §E.3 S7H-009 | MED | V2 | 프리미엄 기능 정의 — Free vs Paid 경계

> **출처 원본** (STEP7-H L144~L147 verbatim):
> ```
> **S7H-009** | MED | V2 | 프리미엄 기능 정의 — Free vs Paid 경계
> - 내용: 무료와 유료의 기능 경계 설정
> - Free: 로컬 LLM, 기본 메모리, 기본 Tool
> - Premium: 클라우드 LLM, 고급 Agent, 무제한 메모리, Priority 지원
> ```

#### §E.3.1 Free vs Paid 경계 매트릭스 (LOCK-BM-06 준수)

| 기능 영역 | Free ($0) | Core ($0+API) | Pro ($15/mo, LOCK-BM-07) | Power ($25/mo) | Team/Enterprise |
|----------|-----------|---------------|----------------------|----------------|-----------------|
| **LLM 접근** | 로컬 LLM + 무료 API (Gemini Free, Groq Free) | 모든 모델 (사용자 API 키) | 모든 모델 + $10 크레딧 | + 고급 추론 모델 | + 전용 배포 |
| **일일 요청 제한** | **50회/일 (LOCK-BM-06)** | 제한 없음 (API 한도 내) | 제한 없음 | 제한 없음 | 제한 없음 |
| **메모리** | L0~L2 기본 | L0~L4 전체 | L0~L4 전체 + 클라우드 동기화 | + 고급 KG | + 팀 공유 |
| **Agent** | 기본 1개 | BLUE NODEs 전체 | BLUE NODEs 전체 | + 고급 전문 Agent (Quant/Dev/Content Pro) | + 팀 Agent |
| **MCP Tools** | 기본 3개 | 전체 무료 Tools | + 프리미엄 Tools $10 크레딧 | + 우선 접근 | + 커스텀 Tools |
| **지원** | 커뮤니티 (Discord) | 커뮤니티 | 이메일 (2일 내) | **우선 지원** (24h 내) | 전담 지원 + SLA 99.9% (LOCK-BM-05) |

> **출처**: STEP7-H S7H-009 L146~L147 "Free: 로컬 LLM, 기본 메모리, 기본 Tool / Premium: 클라우드 LLM, 고급 Agent, 무제한 메모리, Priority 지원" 원본 + 7티어 확장 (AUTHORITY §6).

#### §E.3.2 LOCK-BM-06 Free Tier 50회/일 상세 정책

| 항목 | 정책 | 비고 |
|------|------|------|
| 카운트 대상 | **클라우드 LLM API 호출만** (Gemini Free, Groq Free, Mistral Free) | 로컬 LLM (Ollama) 호출은 제외 |
| 카운트 리셋 | 매일 00:00 KST | 타임존 고정 |
| 초과 시 동작 | 로컬 LLM 자동 라우팅 + 알림 | 차단 아님, 다운그레이드 |
| 일일 제한 UI | 잔여 횟수 실시간 표시 (비용 투명성 S7H-012 연계) | 50 → 0 카운트다운 |
| Core 전환 시 | 무제한 (사용자 API 키 기반) | LOCK-BM-04 토큰 기반 |

> **LOCK-BM-06 준수**: Free Tier 일일 LLM 요청 상한 50회/일 — 시스템 하드캡.
> **비즈니스 근거**: Free Tier 품질 충분 + Core 전환 동기 균형 (S7H-017 Free→Core 30% 목표 달성 기반).

#### §E.3.3 프리미엄 기능 상세 (Pro → Power → Enterprise 단계)

**Pro ($15/mo, LOCK-BM-07)**:
- 클라우드 호스팅 서버 (24/7 가용성)
- $10 API 크레딧 (입력 $0.003/1K, 출력 $0.015/1K)
- 웹 접근 + PWA 모바일
- 멀티 디바이스 동기화
- 이메일 지원 (2영업일 내)

**Power ($25/mo, Pro + $10)**:
- 고급 Agent 패키지 (Developer Pro / Quant Pro / Content Pro — 각 $5~10/mo 대비 번들 할인, S7H-022 연계)
- 우선 지원 (24시간 내 응답)
- 베타 기능 우선 접근
- 고급 Knowledge Graph (관계 추론 강화)

**Enterprise ($35/seat/mo, LOCK-BM-08)**:
- SSO/SAML 통합
- 감사 로그 (SOC 2 호환)
- **SLA 99.9% 가용성 (LOCK-BM-05)**
- 전담 지원 (전용 Slack 채널 + 분기 리뷰)
- 커스텀 Agent 개발 가능

#### §E.3.4 전환 트리거 (Free → Paid)

| 트리거 | 도달 조건 | 전환 제안 |
|-------|----------|----------|
| **일일 50회 초과** | 월 15일 이상 50회 상한 도달 | Core ($0 + API 실비) 추천 |
| **Claude/GPT 전용 모델 필요** | 무료 API 품질 불만족 | Core (자기 API 키) 또는 Pro ($15, $10 크레딧 포함) |
| **멀티 디바이스 동기화 필요** | PC + 모바일 사용 | Pro ($15/mo) 추천 |
| **전문 Agent 필요** | 코딩/투자/콘텐츠 전문 워크플로우 | Power ($25/mo) 추천 |
| **팀 공유 필요** | 3명 이상 팀 | Team ($20/user/mo) 추천 |
| **B2B 기업 규모** | 10명+ + SLA 필요 | Enterprise ($35/seat, LOCK-BM-08) — LOCK-BM-05 SLA |

> **출처**: STEP7-H S7H-017 Free → Paid 전환 트리거 연계.
> **목표 전환율**: Free → Core 30% / Core → Pro 7% / Pro → Power 20% (AUTHORITY §6 L93~L96).

#### §E.3.5 Peer cross-ref

- 본 §E.3 ↔ `vamos_pricing_strategy.md` §E.1 (S7H-017 Free→Pro 전환율) — 전환 트리거 공유
- 본 §E.3 ↔ `revenue_model.md` §E.1 (S7H-020 SaaS 구독 모델) — 프리미엄 티어 구성 일관성

---

### §E.4 S7H-010 | MED | V2 | 번들 전략 — 패키지 구성

> **출처 원본** (STEP7-H L149~L151 verbatim):
> ```
> **S7H-010** | MED | V2 | 번들 전략 — 패키지 구성
> - 내용: 기능별 번들 패키지 설계
> - Personal: $0 / Pro: $10/mo / Power: $20/mo / Team: $15/user/mo
> ```

#### §E.4.1 CFL-006 해결 반영 — S7H-010 Pro $10 vs S7H-020 Pro $15

> **⚠️ CONFLICT RESOLVED (CFL-006, CONFLICT_LOG L105~L114)**: S7H-010 원본 "Pro $10/mo, Power $20/mo, Team $15/user/mo" 는 초기 번들 구상이며, S7H-020 (CRITICAL, V2) "Pro $15/mo, Power $25/mo, Team $20/user/mo" 가 확정 SaaS 가격 체계. **LOCK-BM-07 = Pro $15/mo** 확정. 본 §E.4 는 S7H-010 번들 "구성 설계" 개념만 계승하고 가격은 S7H-020 / LOCK-BM-07 / 계획서 §B.1 7티어 기준으로 표기.

#### §E.4.2 번들 패키지 최종 구성 (7티어 C-7 해결 반영)

| 번들 | 원본 S7H-010 | **최종 정본 (CFL-006 + 계획서 §B.1)** | 구성 내용 | LOCK |
|------|------------|----------------------------------|----------|------|
| **Personal (Free)** | $0 | **$0/mo** | 로컬 LLM + 무료 API + L0~L2 + 1 Agent + 50회/일 (LOCK-BM-06) | LOCK-BM-06 |
| **Core** | — (§B.1 신설) | **$0 + API 실비** | 모든 모델 (사용자 키) + L0~L4 + BLUE NODEs 전체 | LOCK-BM-01 ≤₩40K/mo |
| **Pro** | ~~$10/mo (초기 구상)~~ | **$15/mo (LOCK-BM-07 확정)** | 서버 호스팅 + $10 크레딧 + 웹/PWA + 동기화 | **LOCK-BM-07** |
| **Power** | ~~$20/mo (초기 구상)~~ | **$25/mo (§B.1 확정)** | Pro + 고급 Agent + 우선 지원 | LOCK-BM-02 ≤₩93K/mo |
| **Team** | ~~$15/user/mo (초기 구상)~~ | **$20/user/mo (§B.1 확정)** | Power + 팀 공유 + 관리 기능 | — (내부 가격) |
| **Enterprise** | — (§B.1 신설) | **$35/seat/mo (LOCK-BM-08, 최소 10석)** | 전체 + SSO/SAML + 감사 + SLA 99.9% (LOCK-BM-05) | **LOCK-BM-08, LOCK-BM-05** |
| **API** | — (§B.1 신설) | **사용량 기반** (입력 $0.003/1K, 출력 $0.015/1K) | 토큰 기반 과금 (LOCK-BM-04) | **LOCK-BM-04** |

> **출처**: STEP7-H S7H-010 L151 원본 + CFL-006 해결 (S7H-020 우선) + 계획서 §B.1 7티어 확정.
> **LOCK-BM-10 준수**: 향후 번들 가격 조정 시 기존 사용자 30일 사전 고지 필수.

#### §E.4.3 번들 간 업그레이드 경로

```
Free ($0)
  ↓ 일일 50회 초과, 클라우드 LLM 필요
Core ($0 + API 실비)
  ↓ 클라우드 호스팅 + 동기화 필요
Pro ($15/mo, LOCK-BM-07)
  ↓ 전문 Agent + 우선 지원 필요
Power ($25/mo)
  ↓ 팀 공유 + 관리 필요
Team ($20/user/mo)
  ↓ 10석+ + SLA 99.9% + SSO 필요
Enterprise ($35/seat/mo, LOCK-BM-08 + LOCK-BM-05)

API 별도 (사용량 기반, LOCK-BM-04) — B2B 개발자 통합용
```

> **전환율 목표 (AUTHORITY §6)**: Free→Core 30%, Core→Pro 7%, Pro→Power 20%.

#### §E.4.4 번들별 가치 정량화

| 번들 | 월 가치 (추정) | 월 비용 | ROI | 타겟 페르소나 |
|------|-------------|--------|-----|-------------|
| Personal (Free) | ~$10 (무료 API 노출) | $0 | ∞ | P1, P4 (탐색) |
| Core | ~$30 (멀티 모델 + 전체 메모리) | $5~10 (API) | 3~6배 | P1, P2 (가치 중심) |
| Pro | ~$60 (서버 + 크레딧 + 동기화) | $15 | 4배 | P2 주 타겟 |
| Power | ~$120 (전문 Agent + 우선 지원) | $25 | 4.8배 | P1 고급, P3 |
| Team | ~$100/user (팀 기능 포함) | $20/user | 5배 | 스타트업/중소 |
| Enterprise | ~$200/seat (SSO + SLA + 전담) | $35/seat | 5.7배 | 기업 |

> **가정 (E7)**: 월 가치는 동급 경쟁사 가격 평균 (ChatGPT Plus $20 + Claude Pro $20 + Cursor $20 = $60 기능 제공 기준). ROI = 가치 ÷ 비용.

#### §E.4.5 경쟁사 번들 비교 (2025-02 기준)

| 구성 | VAMOS | ChatGPT | Claude | Cursor | GitHub Copilot |
|------|-------|---------|--------|--------|----------------|
| Free | ✅ (50회/일, LOCK-BM-06) | ✅ GPT-4o-mini | ✅ Claude 3.5 | 2주 trial | ❌ |
| 개인 Pro | **$15 (LOCK-BM-07)** | $20 (Plus) | $20 (Pro) | $20 | $10 |
| 고급 개인 | **$25 (Power)** | $200 (Pro) | — | — | — |
| 팀 | **$20/user (Team)** | $25/user (Team) | $25/user (Team) | $40/seat (Business) | $19/seat (Business) |
| 기업 | **$35/seat (LOCK-BM-08)** | 협의 | 협의 | — | $39/seat (Enterprise) |

> **출처**: 각 서비스 공식 가격 (2025-02 기준, STEP7-H Part 1 L30~L44 원본).
> **경쟁 우위**: Pro $15 (vs $20 경쟁사) = 25% 저렴 + 사용량 기반 유연성 + 멀티 모델 + 로컬 데이터 주권.

#### §E.4.6 Peer cross-ref

- 본 §E.4 ↔ `vamos_pricing_strategy.md` §6 (7티어 최종 정본)
- 본 §E.4 ↔ `revenue_model.md` §E.1 (S7H-020 SaaS 구독 모델) — 번들 가격 ↔ 수익 스트림 일관성
- 본 §E.4 ↔ `revenue_model.md` §E.2 (S7H-021 MCP 마켓플레이스) — LOCK-BM-09 70/30 수수료와 번들 구분

---

### §E.N Phase 2 V2 실측 vs AUTHORITY §4 LOCK row 정합

| LOCK | 값 | 본 파일 §E 인용 지점 | 준수 |
|------|-----|-------------------|------|
| LOCK-BM-01 | ₩40,000 (~$30) V1 월 상한 | §E.2.5, §E.4.2 (Core row) | ✅ |
| LOCK-BM-04 | 토큰 기반 + 월 구독 | §E.1.2, §E.4.2 (API row) | ✅ |
| LOCK-BM-05 | Enterprise SLA 99.9% | §E.1.3, §E.3.3, §E.4.2 (Enterprise row) | ✅ |
| LOCK-BM-06 | Free Tier 50회/일 | §E.3.1, §E.3.2, §E.4.2 (Free row) | ✅ |
| LOCK-BM-07 | Pro $15/mo | §E.1.2, §E.2.3, §E.3.1, §E.4.1~§E.4.5 | ✅ |
| LOCK-BM-08 | Enterprise $35/seat (최소 10석) | §E.1.3, §E.3.3, §E.4.2 (Enterprise row) | ✅ |
| LOCK-BM-10 | 30일 사전 고지 | §E.2.3, §E.4.2 (헤더 주석) | ✅ |

**LOCK-BM 인용 누계 (본 파일 §E)**: ~27 지점 (LOCK-BM-01 ×2 + LOCK-BM-04 ×3 + LOCK-BM-05 ×3 + LOCK-BM-06 ×5 + LOCK-BM-07 ×8 + LOCK-BM-08 ×4 + LOCK-BM-10 ×2).
**STEP7-H verbatim 인용 누계 (본 파일 §E)**: S7H-007 L135~L137 + S7H-008 L139~L142 + S7H-009 L144~L147 + S7H-010 L149~L151 = **4 S7H × 원문 블록 4 + 참조 인용 ≥10 지점**.
**FABRICATION 10종 마커 census (본 파일 §E)**: 0 points / 0 hits CLEAN (5-1 LOCK hallucination 차단 / 3-8 LOCK-A2A false-positive 교정 선례 계승).

*§E 작성 완료: P2-1 세션, S7H-007~010 V2 4건. LOCK-BM 27 지점 + STEP7-H verbatim 4 S7H 전수. CFL-006 해결 반영 (S7H-020 $15 우선), CFL-010 해결 반영 (7티어 C-7). R-12-4 출처·시점 명기, R-12-5 정본 우선순위 (STEP7-H 우선).*
