# AI 브라우저 에이전트 — L3 상세 명세

> **N-ID**: N-011 (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 05_browser-rpa
> **정본**: sot 2/3-4_Workflow-RPA/05_browser-rpa/browser_agent.md

---

## 1. 개요

VAMOS AI 브라우저 에이전트는 **Playwright** 기반의 지능형 웹 자동화 실행기이다. 사용자의 자연어 명령을 10종 브라우저 액션 시퀀스로 변환하여 실행하며, LLM 기반 지능형 요소 선택과 에러 자동 복구를 통해 DOM 변화에 강건한 자동화를 제공한다.

> LOCK (기존 명세 §6 / LOCK-WF-07): navigate, click, type, extract, screenshot, wait, scroll, select, hover, execute_js — 10종 액션 타입은 제거 불가. 추가만 허용.

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화

---

## 2. 핵심 제약 (LOCK)

| # | LOCK 항목 | 값 |
|---|-----------|-----|
| LOCK-WF-07 | 브라우저 액션 타입 10종 | navigate, click, type, extract, screenshot, wait, scroll, select, hover, execute_js |
| LOCK-WF-10 | RPA 보안 정책 | 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화 |
| LOCK-WF-05 | 실행 엔진 제약 | LangGraph StateGraph 기반, 최대 동시 실행 수 = 10 |

---

## 3. 아키텍처

```
[자연어 명령]
    ↓
[LLM 의도 파싱] → [액션 시퀀스 생성]
    ↓
[Playwright 실행 엔진]
    ├─ BrowserContext (샌드박스)
    │   ├─ Page Pool (멀티 탭)
    │   └─ Credential Vault (AES-256)
    ↓
[액션 루프]
    ├─ navigate → click → type → ...
    ├─ [LLM 요소 선택기] ← DOM 스냅샷
    ├─ [에러 복구 엔진] ← 실패 시 재시도/대안 탐색
    └─ [결과 수집기] → 구조화 데이터 반환
```

---

## 4. 10종 브라우저 액션 타입 상세

### 4.1 액션 공통 스키마

```typescript
interface BrowserActionStep {
  action: BrowserActionType;
  selector?: string;                   // CSS/XPath 선택자 (LLM 폴백 가능)
  params: Record<string, any>;         // 액션별 파라미터
  timeout_ms?: number;                 // 기본 30000
  retry_on_fail?: boolean;             // 기본 true
  screenshot_before?: boolean;         // 실행 전 스크린샷 (디버그용)
  screenshot_after?: boolean;          // 실행 후 스크린샷
}

type BrowserActionType =
  | "navigate"
  | "click"
  | "type"
  | "extract"
  | "screenshot"
  | "wait"
  | "scroll"
  | "select"
  | "hover"
  | "execute_js";
```

### 4.2 navigate — URL 이동

```typescript
interface NavigateParams {
  url: string;                         // 대상 URL (Jinja2 템플릿 지원)
  wait_until?: "load" | "domcontentloaded" | "networkidle";  // 기본 "load"
  referer?: string;                    // Referer 헤더
}

interface NavigateOutput {
  final_url: string;                   // 리다이렉트 후 최종 URL
  status_code: number;
  page_title: string;
  load_time_ms: number;
}
```

### 4.3 click — 요소 클릭

```typescript
interface ClickParams {
  selector: string;                    // CSS/XPath
  button?: "left" | "right" | "middle";  // 기본 "left"
  click_count?: number;                // 기본 1 (2 = 더블클릭)
  force?: boolean;                     // 가시성 무시 강제 클릭
  position?: { x: number; y: number }; // 요소 내 클릭 좌표 (오프셋)
}

interface ClickOutput {
  clicked: boolean;
  element_text?: string;               // 클릭한 요소의 텍스트
  navigation_triggered: boolean;       // 클릭으로 페이지 이동 발생 여부
}
```

### 4.4 type — 텍스트 입력

```typescript
interface TypeParams {
  selector: string;                    // 입력 필드 선택자
  text: string;                        // 입력 텍스트 (Jinja2 템플릿 지원)
  delay_ms?: number;                   // 키 입력 간 지연 (기본 50)
  clear_before?: boolean;              // 기존 값 삭제 후 입력 (기본 true)
  press_enter_after?: boolean;         // 입력 후 Enter (기본 false)
}

interface TypeOutput {
  typed: boolean;
  final_value: string;                 // 입력 후 필드 값
}
```

### 4.5 extract — 데이터 추출

```typescript
interface ExtractParams {
  selector: string;                    // 추출 대상 선택자
  attribute?: string;                  // 추출할 속성 (기본 "textContent")
  multiple?: boolean;                  // 복수 요소 추출 (기본 false)
  format?: "text" | "html" | "json";   // 출력 형식 (기본 "text")
}

interface ExtractOutput {
  data: string | string[];             // 추출 데이터
  element_count: number;               // 매칭 요소 수
}
```

### 4.6 screenshot — 스크린샷

```typescript
interface ScreenshotParams {
  target?: "page" | "element";         // 기본 "page"
  selector?: string;                   // target="element"일 때 대상
  format?: "png" | "jpeg";             // 기본 "png"
  full_page?: boolean;                 // 전체 페이지 (기본 false)
  quality?: number;                    // JPEG 품질 (1-100)
}

interface ScreenshotOutput {
  image_path: string;                  // 저장 경로 (샌드박스 내)
  width: number;
  height: number;
  size_bytes: number;
}
```

### 4.7 wait — 대기

```typescript
interface WaitParams {
  type: "selector" | "timeout" | "navigation" | "network_idle";
  selector?: string;                   // type="selector"일 때 대상
  timeout_ms?: number;                 // type="timeout"일 때 대기 시간
  state?: "visible" | "hidden" | "attached" | "detached";  // 기본 "visible"
}

interface WaitOutput {
  waited_ms: number;                   // 실제 대기 시간
  condition_met: boolean;              // 조건 충족 여부
}
```

### 4.8 scroll — 스크롤

```typescript
interface ScrollParams {
  direction: "up" | "down" | "left" | "right";
  amount?: number;                     // 픽셀 (기본 500)
  selector?: string;                   // 특정 요소 내 스크롤
  to?: "top" | "bottom";              // 최상단/최하단으로 이동
}

interface ScrollOutput {
  scrolled_px: number;
  scroll_position: { x: number; y: number };
  at_boundary: boolean;                // 더 이상 스크롤 불가
}
```

### 4.9 select — 드롭다운 선택

```typescript
interface SelectParams {
  selector: string;                    // <select> 요소 선택자
  value?: string;                      // option value
  label?: string;                      // option 표시 텍스트 (value 없을 때)
  index?: number;                      // option 인덱스 (value/label 없을 때)
}

interface SelectOutput {
  selected_value: string;
  selected_label: string;
  option_count: number;
}
```

### 4.10 hover — 마우스 호버

```typescript
interface HoverParams {
  selector: string;                    // 호버 대상 선택자
  position?: { x: number; y: number }; // 요소 내 호버 좌표
  force?: boolean;                     // 가시성 무시 강제 호버
}

interface HoverOutput {
  hovered: boolean;
  tooltip_text?: string;               // 호버 후 나타난 툴팁 텍스트
}
```

### 4.11 execute_js — JavaScript 실행

```typescript
interface ExecuteJsParams {
  script: string;                      // JavaScript 코드
  args?: any[];                        // 함수 인자
  return_value?: boolean;              // 반환값 캡처 (기본 true)
}

interface ExecuteJsOutput {
  result: any;                         // JS 실행 반환값
  console_logs: string[];              // console.log 출력
  errors: string[];                    // JS 에러
}
```

---

## 5. LLM 기반 지능형 요소 선택

### 5.1 요소 선택 파이프라인

```
[사용자 의도 / 선택자 실패]
    ↓
[DOM 스냅샷 생성] → 간소화 DOM (태그+속성+텍스트만)
    ↓
[LLM 요소 추론]
    ├─ 입력: 간소화 DOM + 사용자 의도
    ├─ 출력: CSS 선택자 + 신뢰도
    └─ 검증: 선택자 실행 → 매칭 요소 존재 확인
    ↓
[선택자 캐싱] → 동일 패턴 재사용 (URL 패턴별)
```

### 5.2 선택자 해석 스키마

```typescript
interface ElementLocator {
  primary: string;                     // 기본 CSS/XPath 선택자
  fallback_strategy: "llm" | "text_match" | "aria_label";
  llm_description?: string;           // LLM에 전달할 요소 설명 ("로그인 버튼")
  text_content?: string;              // 텍스트 기반 매칭
  aria_label?: string;                // ARIA 라벨 기반 매칭
}

interface ElementResolution {
  selector_used: string;              // 최종 사용된 선택자
  resolution_method: "primary" | "llm" | "text_match" | "aria_label";
  confidence: number;                 // 0.0 ~ 1.0
  alternatives: string[];             // 대안 선택자 목록
}
```

### 5.3 DOM 스냅샷 간소화

```typescript
interface SimplifiedDOM {
  url: string;
  title: string;
  elements: SimplifiedElement[];
}

interface SimplifiedElement {
  tag: string;                        // "button", "input", "a", ...
  id?: string;
  class?: string;
  text?: string;                      // innerText (최대 100자)
  aria_label?: string;
  href?: string;                      // <a> 태그의 href
  type?: string;                      // <input>의 type
  placeholder?: string;
  role?: string;                      // ARIA role
  bounding_box: { x: number; y: number; w: number; h: number };
}
```

**간소화 규칙**: 비가시 요소 제외, `<script>`/`<style>` 제외, 텍스트 100자 트림, 최대 500 요소 캡처.

---

## 6. 에러 복구 엔진

### 6.1 에러 유형별 복구 전략

| 에러 유형 | 원인 | 복구 전략 |
|----------|------|----------|
| `element_not_found` | 선택자 무효 / DOM 변경 | LLM 폴백 → 대안 선택자 추론 → 재시도 (최대 2회) |
| `element_not_visible` | 요소 숨김 / 뷰포트 밖 | scroll → wait(visible) → 재시도 |
| `navigation_timeout` | 페이지 로딩 지연 | wait(networkidle) → 타임아웃 연장 (60초) → 재시도 |
| `captcha_detected` | CAPTCHA/봇 차단 | 실행 일시정지 → 사용자 개입 요청 (HumanApprovalNode 연동) |
| `session_expired` | 로그인 세션 만료 | 자동 재인증 (Credential Vault) → 이전 액션부터 재실행 |
| `rate_limited` | 요청 빈도 제한 | 지수 백오프 대기 (1/2/4초) → 재시도 (최대 3회) |

### 6.2 복구 엔진 스키마

```typescript
interface ErrorRecoveryConfig {
  max_recovery_attempts: number;       // 기본 3
  llm_fallback_enabled: boolean;       // 기본 true
  human_escalation_enabled: boolean;   // 기본 true
  screenshot_on_error: boolean;        // 기본 true (디버그용)
}

interface RecoveryAction {
  type: "retry" | "alternative_selector" | "scroll_and_retry" | "reauth" | "human_escalation" | "abort";
  delay_ms?: number;
  new_selector?: string;               // alternative_selector일 때
  reason: string;
}
```

**복구 의사코드**:
```
function recover(error, step, context):
    if error.type == "element_not_found" and config.llm_fallback_enabled:
        dom_snapshot = capture_simplified_dom(context.page)
        new_selector = llm_infer_selector(dom_snapshot, step.params.selector, error)
        if new_selector.confidence >= 0.7:
            return RecoveryAction(type="alternative_selector", new_selector=new_selector)
    if error.type == "captcha_detected":
        return RecoveryAction(type="human_escalation", reason="CAPTCHA 감지")
    if context.recovery_attempts < config.max_recovery_attempts:
        return RecoveryAction(type="retry", delay_ms=1000 * 2^context.recovery_attempts)
    return RecoveryAction(type="abort", reason="최대 복구 시도 초과")
```

---

## 7. 멀티 탭 / 멀티 컨텍스트 관리

```typescript
interface BrowserSessionConfig {
  browser_type: "chromium";            // Playwright 지원 브라우저
  headless: boolean;                   // 기본 true
  viewport: { width: number; height: number };  // 기본 1920×1080
  user_agent: string;                  // 기본 "VAMOS-Bot/1.0"
  max_pages: number;                   // 최대 탭 수 (기본 5)
  proxy?: ProxyConfig;                 // 프록시 설정
  locale?: string;                     // 기본 "ko-KR"
  timezone?: string;                   // 기본 "Asia/Seoul"
}

interface PageContext {
  page_id: string;                     // 탭 식별자
  url: string;                         // 현재 URL
  title: string;
  status: "active" | "idle" | "loading" | "error";
  created_at: string;
}
```

**세션 생명주기**: 워크플로우 실행 시작 → BrowserContext 생성 (샌드박스) → 액션 실행 → 결과 수집 → BrowserContext 종료 (쿠키/캐시 삭제)

---

## 8. 자격증명 관리 (Credential Vault 연동)

```typescript
interface BrowserCredential {
  id: string;                          // 크리덴셜 ID
  domain: string;                      // "naver.com", "dart.fss.or.kr"
  auth_type: "login_form" | "cookie" | "oauth" | "api_key";
  encrypted_data: string;              // AES-256 암호화 저장
  auto_login_steps?: BrowserActionStep[];  // 자동 로그인 액션 시퀀스
  session_check_selector?: string;     // 로그인 상태 확인 선택자
  last_used_at: string;
}
```

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 자격증명 AES-256 암호화 저장 필수. 평문 저장 발견 시 즉시 수정.

---

## 9. 워크플로우 노드 연동

AI 브라우저 에이전트는 DAG 워크플로우에서 별도 노드 타입이 아니라 **CodeNode 프리셋**(LOCK-WF-01 12 타입 위의 구성 프로파일)으로 실행된다. 'BrowserNode'는 신규 DAG 타입이 아니며, LOCK-WF-01 12 타입은 재정의·확장 없이 그대로 유지된다 (종합계획서 LOCK-WF-01 'ETL BrowserNode* 제거 확인' 정합).

```typescript
interface BrowserNodeConfig {
  session_config: BrowserSessionConfig;
  actions: BrowserActionStep[];        // 순차 실행할 액션 목록
  credentials?: string[];             // 사용할 크리덴셜 ID 목록
  error_recovery: ErrorRecoveryConfig;
  output_mapping: Record<string, string>;  // 액션 결과 → 워크플로우 변수 매핑
}

interface BrowserNodeOutput {
  action_results: Record<string, any>[]; // 각 액션 결과
  screenshots: string[];               // 캡처된 스크린샷 경로
  extracted_data: Record<string, any>; // 추출된 데이터
  total_duration_ms: number;
  pages_visited: string[];             // 방문 URL 목록
}
```

---

## 10. REST API

```
POST   /api/v1/browser/sessions                 // 브라우저 세션 생성
DELETE /api/v1/browser/sessions/:id              // 세션 종료
POST   /api/v1/browser/sessions/:id/actions      // 액션 실행
GET    /api/v1/browser/sessions/:id/screenshot   // 현재 스크린샷
GET    /api/v1/browser/sessions/:id/dom          // 간소화 DOM 조회
POST   /api/v1/browser/credentials               // 크리덴셜 등록
GET    /api/v1/browser/credentials               // 크리덴셜 목록 (암호화)
DELETE /api/v1/browser/credentials/:id           // 크리덴셜 삭제
```

---

## 11. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| 01_dag-engine | BrowserNode 타입 실행 | ← 사용 |
| browser_security.md | 샌드박스/암호화 정책 | ← 준수 |
| web_scraping.md (N-012) | 스크래핑 전용 확장 | → 제공 (기반) |
| web_monitoring.md (N-013) | 웹 변경 감지 확장 | → 제공 (기반) |
| form_autofill.md (N-014) | 폼 자동 입력 전용 확장 | → 제공 (기반) |
| file_download_upload.md (N-015) | 파일 다운로드/업로드 확장 | → 제공 (기반) |
| nocode_api.md (N-016) | API 문서 브라우저 탐색 | → 제공 (보조) |
| T2-CORE_AI | LLM 요소 선택, 의도 파싱 | ← 사용 |

---

*끝 — browser_agent.md L3 v1.0*
