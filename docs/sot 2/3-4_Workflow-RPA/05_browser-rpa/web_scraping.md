# 웹 스크래핑 자동화 — L3 상세 명세

> **N-ID**: N-012 (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 05_browser-rpa
> **정본**: sot 2/3-4_Workflow-RPA/05_browser-rpa/web_scraping.md

---

## 1. 개요

VAMOS 웹 스크래핑 자동화는 Playwright 브라우저 에이전트(N-011) 위에 구축된 **구조화 데이터 추출 전문 모듈**이다. HTML → 정형 데이터 변환, 자동 페이지네이션, 동적 콘텐츠(JavaScript 렌더링) 처리, AI 기반 적응형 셀렉터를 제공한다. robots.txt 준수 및 Rate Limiting을 기본 적용한다.

> LOCK (기존 명세 §6 / LOCK-WF-07): navigate, click, type, extract, screenshot, wait, scroll, select, hover, execute_js — 10종 브라우저 액션 기반

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화

---

## 2. 핵심 제약 (LOCK)

| # | LOCK 항목 | 값 |
|---|-----------|-----|
| LOCK-WF-07 | 브라우저 액션 타입 | extract 액션 기반 데이터 추출 |
| LOCK-WF-10 | RPA 보안 정책 | 샌드박스 내 실행, 추출 데이터 암호화 저장 |

---

## 3. 아키텍처

```
[스크래핑 요청]
    ├─ 자연어: "네이버 금융에서 코스피 시가총액 상위 10종목 추출"
    └─ 구조화: ScrapingConfig JSON
    ↓
[URL 분석 + robots.txt 확인]
    ↓
[Playwright 브라우저 에이전트 (N-011)]
    ├─ navigate → 대상 페이지
    ├─ wait → 동적 콘텐츠 렌더링 대기
    ├─ scroll → 무한 스크롤 / 추가 콘텐츠 로딩
    ├─ extract → CSS/XPath 선택자 기반 데이터 추출
    └─ click → 페이지네이션 다음 페이지
    ↓
[데이터 정규화 엔진]
    ├─ 타입 추론 (숫자/날짜/통화/텍스트)
    ├─ 중복 제거
    └─ 스키마 검증
    ↓
[출력] → JSON / CSV / DataFrame
```

---

## 4. 스크래핑 설정 스키마

### 4.1 ScrapingConfig

```typescript
interface ScrapingConfig {
  id: string;                          // 스크래핑 작업 ID
  name: string;                        // 작업명
  url: string;                         // 시작 URL (Jinja2 템플릿 지원)
  selectors: Record<string, SelectorDef>;  // 추출 필드별 선택자
  pagination?: PaginationConfig;       // 페이지네이션 설정
  dynamic_content?: DynamicContentConfig;  // 동적 콘텐츠 처리
  rate_limit: RateLimitConfig;         // 요청 빈도 제한
  output: OutputConfig;                // 출력 설정
  robots_txt: boolean;                 // robots.txt 준수 (기본 true)
  max_pages: number;                   // 최대 페이지 수 (기본 10)
  cache_ttl_sec: number;               // 캐시 TTL (기본 3600)
  retry_policy: RetryPolicy;           // 재시도 정책
}

interface SelectorDef {
  css?: string;                        // CSS 선택자
  xpath?: string;                      // XPath 선택자
  attribute?: string;                  // 추출할 속성 (기본 "textContent")
  transform?: TransformRule;           // 후처리 규칙
  required?: boolean;                  // 필수 필드 여부 (기본 false)
}

interface TransformRule {
  type: "trim" | "number" | "date" | "currency" | "regex" | "replace";
  pattern?: string;                    // regex/replace 패턴
  replacement?: string;                // replace 대체 문자열
  locale?: string;                     // number/currency/date 로케일 (기본 "ko-KR")
  format?: string;                     // date 형식 (기본 "YYYY-MM-DD")
}
```

### 4.2 PaginationConfig

```typescript
interface PaginationConfig {
  strategy: "click_next" | "url_pattern" | "infinite_scroll" | "load_more";

  // click_next: "다음" 버튼 클릭
  next_button_selector?: string;       // 다음 페이지 버튼 선택자
  has_next_check?: string;             // 다음 페이지 존재 확인 선택자

  // url_pattern: URL 패턴 변환
  url_template?: string;               // "https://example.com/list?page={{page}}"
  start_page?: number;                 // 시작 페이지 (기본 1)

  // infinite_scroll: 무한 스크롤
  scroll_delay_ms?: number;            // 스크롤 후 대기 (기본 2000)
  no_new_content_threshold?: number;   // 연속 N회 새 콘텐츠 없으면 종료 (기본 3)

  // load_more: 더보기 버튼
  load_more_selector?: string;         // 더보기 버튼 선택자
}
```

### 4.3 DynamicContentConfig

```typescript
interface DynamicContentConfig {
  wait_strategy: "selector" | "network_idle" | "timeout";
  wait_selector?: string;              // 데이터 로딩 완료 표시 요소
  wait_timeout_ms?: number;            // 기본 10000
  execute_js_before?: string;          // 추출 전 실행할 JS (탭 전환 등)
}
```

---

## 5. AI 기반 적응형 스크래핑

### 5.1 자연어 → 선택자 자동 생성

```typescript
interface AIScrapingRequest {
  url: string;                         // 대상 URL
  description: string;                 // "이 페이지에서 제품 이름과 가격을 추출해"
  sample_count?: number;               // 샘플 추출 수 (기본 3, 확인용)
}

interface AIScrapingResult {
  inferred_selectors: Record<string, SelectorDef>;  // LLM이 추론한 선택자
  sample_data: Record<string, any>[];  // 샘플 추출 결과
  confidence: number;                  // 0.0 ~ 1.0
  needs_confirmation: boolean;         // 사용자 확인 필요 여부
}
```

**AI 스크래핑 의사코드**:
```
function ai_scrape(request):
    page = navigate(request.url)
    dom = capture_simplified_dom(page)
    
    selectors = llm_infer_selectors(
        dom=dom,
        description=request.description,
        prompt="DOM에서 사용자가 원하는 데이터의 CSS 선택자를 추론하시오"
    )
    
    sample = extract_with_selectors(page, selectors, limit=request.sample_count)
    
    if sample.confidence < 0.8:
        return AIScrapingResult(needs_confirmation=true, sample_data=sample)
    return AIScrapingResult(inferred_selectors=selectors, sample_data=sample)
```

### 5.2 선택자 자동 적응 (페이지 구조 변경 대응)

```typescript
interface SelectorAdaptation {
  original_selector: string;           // 원본 선택자
  adapted_selector: string;            // 적응된 선택자
  adaptation_method: "attribute_fallback" | "text_match" | "llm_inference";
  confidence: number;
  last_adapted_at: string;
}
```

원본 선택자 실패 시 3단계 폴백:
1. **속성 폴백**: id → class → aria-label → data-* 속성 순서로 대안 탐색
2. **텍스트 매칭**: 추출 대상 텍스트 패턴으로 요소 위치 추적
3. **LLM 추론**: 간소화 DOM + 이전 성공 패턴을 LLM에 전달하여 새 선택자 추론

---

## 6. 데이터 정규화 엔진

### 6.1 타입 추론 규칙

| 패턴 | 추론 타입 | 변환 규칙 |
|------|----------|----------|
| `^\d{1,3}(,\d{3})*(\.\d+)?$` | number | 콤마 제거 → float |
| `^\d{4}[-/.]\d{2}[-/.]\d{2}$` | date | ISO 8601 변환 |
| `^[₩$€¥]\s?\d+` | currency | 통화 기호 분리 → { amount, currency } |
| `^\d+(\.\d+)?%$` | percentage | % 제거 → float / 100 |
| 기타 | string | trim 처리 |

### 6.2 OutputConfig

```typescript
interface OutputConfig {
  format: "json" | "csv" | "markdown" | "dataframe";
  file_path?: string;                  // 파일 저장 경로 (샌드박스 내)
  encoding?: string;                   // 기본 "utf-8"
  include_metadata?: boolean;          // 추출 시각/URL 등 메타데이터 포함
  deduplicate?: boolean;               // 중복 제거 (기본 true)
  deduplicate_key?: string[];          // 중복 판정 키 필드
}
```

---

## 7. Rate Limiting / robots.txt 준수

```typescript
interface RateLimitConfig {
  requests_per_second: number;         // 기본 1.0
  burst_limit?: number;                // 버스트 허용 수 (기본 3)
  domain_specific?: Record<string, number>;  // 도메인별 제한
}
```

**robots.txt 처리**:
```
function check_robots_txt(url):
    robots_url = url.origin + "/robots.txt"
    rules = fetch_and_parse(robots_url)
    if rules.disallow(url.pathname, user_agent="VAMOS-Bot"):
        return BLOCKED  // 스크래핑 차단, 사용자에게 알림
    crawl_delay = rules.crawl_delay("VAMOS-Bot")
    if crawl_delay:
        rate_limit.requests_per_second = min(rate_limit.requests_per_second, 1/crawl_delay)
    return ALLOWED
```

---

## 8. 워크플로우 노드 연동

웹 스크래핑은 DAG 워크플로우에서 **BrowserNode** 의 스크래핑 전용 프리셋으로 실행된다.

```typescript
interface ScrapingNodeConfig {
  scraping_config: ScrapingConfig;     // 스크래핑 설정
  output_variable: string;             // 결과를 저장할 워크플로우 변수명
  fail_on_empty: boolean;              // 결과 0건이면 실패 처리 (기본 false)
}

interface ScrapingNodeOutput {
  data: Record<string, any>[];         // 추출된 데이터 배열
  total_records: number;
  pages_scraped: number;
  duration_ms: number;
  warnings: string[];                  // 부분 실패, 선택자 적응 등
}
```

---

## 9. REST API

```
POST   /api/v1/scraping/jobs                     // 스크래핑 작업 생성 + 실행
GET    /api/v1/scraping/jobs/:id                  // 작업 상태 조회
GET    /api/v1/scraping/jobs/:id/data             // 추출 데이터 조회
DELETE /api/v1/scraping/jobs/:id                  // 작업 취소
POST   /api/v1/scraping/preview                   // 선택자 미리보기 (샘플 3건)
POST   /api/v1/scraping/ai-infer                  // AI 선택자 추론
GET    /api/v1/scraping/robots-check?url=         // robots.txt 사전 확인
```

---

## 10. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| browser_agent.md (N-011) | Playwright 실행 엔진, 10종 액션 | ← 사용 (기반) |
| web_monitoring.md (N-013) | 변경 감지 시 스크래핑 트리거 | ← 트리거 |
| browser_security.md | 샌드박스/Rate Limit 정책 | ← 준수 |
| 01_dag-engine | BrowserNode 스크래핑 프리셋 | ← 사용 |
| T2-CORE_AI | LLM 선택자 추론, 자연어 파싱 | ← 사용 |

---

*끝 — web_scraping.md L3 v1.0*
