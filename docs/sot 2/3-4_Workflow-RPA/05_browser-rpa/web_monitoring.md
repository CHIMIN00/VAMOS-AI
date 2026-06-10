# 웹 변경 감지 — L3 상세 명세

> **N-ID**: N-013 (NEW)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 05_browser-rpa
> **정본**: sot 2/3-4_Workflow-RPA/05_browser-rpa/web_monitoring.md

---

## 1. 개요

VAMOS 웹 변경 감지 모듈은 지정된 웹페이지의 콘텐츠 변화를 주기적으로 모니터링하여, 변경이 감지되면 워크플로우 트리거를 발화하거나 사용자에게 알림을 전송한다. 가격 변동, 채용 공고, 뉴스 키워드, 공시(DART), 경쟁사 웹사이트 변경 추적 등의 시나리오를 지원한다.

> LOCK (기존 명세 §6 / LOCK-WF-07): navigate, click, type, extract, screenshot, wait, scroll, select, hover, execute_js — 10종 브라우저 액션 기반

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화

---

## 2. 핵심 제약 (LOCK)

| # | LOCK 항목 | 값 |
|---|-----------|-----|
| LOCK-WF-07 | 브라우저 액션 타입 | extract 기반 콘텐츠 스냅샷 비교 |
| LOCK-WF-10 | RPA 보안 정책 | 샌드박스 내 실행, 모니터링 데이터 암호화 저장 |

---

## 3. 아키텍처

```
[모니터링 작업 등록]
    ↓
[스케줄러 (Condition Trigger)]
    ├─ 체크 주기: 1분 ~ 24시간
    └─ cron 표현식 지원
    ↓
[Playwright 브라우저 에이전트 (N-011)]
    ├─ navigate → 대상 URL
    ├─ wait → 동적 콘텐츠 렌더링
    ├─ extract → 감시 영역 콘텐츠 추출
    └─ screenshot → 변경 전/후 스크린샷 (선택)
    ↓
[변경 감지 엔진]
    ├─ diff 비교 (텍스트 / 구조 / 시각)
    ├─ 변경 유형 분류 (추가/삭제/수정/가격변동)
    └─ 임계값 필터링 (노이즈 제거)
    ↓
[변경 감지됨?]
    ├─ Yes → [알림 발송] + [워크플로우 트리거 발화]
    └─ No  → [다음 체크 대기]
```

---

## 4. 모니터링 작업 스키마

### 4.1 MonitoringJob

```typescript
interface MonitoringJob {
  id: string;                          // 작업 ID (UUID v7)
  name: string;                        // 작업명 ("네이버 금융 삼성전자 시세 감시")
  url: string;                         // 감시 대상 URL
  check_interval_sec: number;          // 체크 주기 (초), 최소 60
  cron?: string;                       // cron 표현식 (check_interval 대신 사용 가능)
  selectors: MonitorSelector[];        // 감시 영역 선택자 목록
  change_detection: ChangeDetectionConfig;
  notification: NotificationConfig;
  trigger_workflow_id?: string;        // 변경 감지 시 발화할 워크플로우 ID
  auth_credential_id?: string;         // 로그인 필요 시 크리덴셜 ID
  enabled: boolean;                    // 활성화 상태
  created_at: string;
  last_checked_at?: string;
  last_changed_at?: string;
}

interface MonitorSelector {
  name: string;                        // 감시 필드명 ("price", "title")
  selector: string;                    // CSS/XPath 선택자
  attribute?: string;                  // 추출 속성 (기본 "textContent")
  transform?: TransformRule;           // 후처리 (N-012 TransformRule 재사용)
}
```

### 4.2 ChangeDetectionConfig

```typescript
interface ChangeDetectionConfig {
  mode: "text" | "structure" | "visual" | "value";
  
  // text: 텍스트 diff (기본)
  text_threshold?: number;             // 변경 문자 수 임계값 (노이즈 필터, 기본 5)
  ignore_patterns?: string[];          // 무시할 패턴 (타임스탬프, 광고 등)
  
  // structure: DOM 구조 변경 감지
  structural_depth?: number;           // 비교 깊이 (기본 3)
  
  // visual: 스크린샷 픽셀 비교 (V2)
  visual_threshold?: number;           // 픽셀 차이 비율 임계값 (기본 0.05 = 5%)
  
  // value: 숫자값 변동 감지 (가격/지표)
  value_type?: "number" | "currency" | "percentage";
  change_direction?: "any" | "up" | "down";  // 감시 방향
  change_threshold?: number;           // 변동 임계값 (절대값 또는 %)
  change_threshold_type?: "absolute" | "percentage";
}
```

### 4.3 NotificationConfig

```typescript
interface NotificationConfig {
  channels: ("push" | "email" | "slack" | "webhook")[];
  template?: string;                   // 알림 메시지 템플릿 (Jinja2)
  include_diff?: boolean;              // 변경 내용 포함 (기본 true)
  include_screenshot?: boolean;        // 변경 전/후 스크린샷 포함 (기본 false)
  cooldown_sec?: number;               // 알림 중복 방지 쿨다운 (기본 300)
}
```

---

## 5. 변경 감지 엔진

### 5.1 스냅샷 저장 스키마

```typescript
interface ContentSnapshot {
  job_id: string;
  captured_at: string;                 // ISO 8601
  url: string;
  fields: Record<string, string>;      // { field_name: extracted_value }
  raw_html_hash: string;               // SHA-256 (전체 HTML)
  screenshot_path?: string;            // 스크린샷 파일 경로 (샌드박스 내)
}
```

### 5.2 Diff 비교 로직

```typescript
interface ChangeResult {
  job_id: string;
  detected_at: string;
  has_changes: boolean;
  changes: FieldChange[];
  previous_snapshot: ContentSnapshot;
  current_snapshot: ContentSnapshot;
}

interface FieldChange {
  field_name: string;
  change_type: "added" | "removed" | "modified" | "value_change";
  old_value?: string;
  new_value?: string;
  diff_detail?: string;                // unified diff 형식
  
  // value_change 전용
  numeric_old?: number;
  numeric_new?: number;
  change_amount?: number;              // new - old
  change_percent?: number;             // (new - old) / old * 100
}
```

**변경 감지 의사코드**:
```
function detect_changes(job, current_snapshot):
    previous = get_latest_snapshot(job.id)
    if previous is None:
        save_snapshot(current_snapshot)
        return ChangeResult(has_changes=false)  // 첫 번째 스냅샷
    
    changes = []
    for field_name in job.selectors:
        old_val = previous.fields[field_name]
        new_val = current_snapshot.fields[field_name]
        
        if job.change_detection.mode == "value":
            old_num = parse_number(old_val)
            new_num = parse_number(new_val)
            delta = abs(new_num - old_num)
            threshold = job.change_detection.change_threshold
            if threshold_type == "percentage":
                if old_num == 0:
                    # 0 기준값: 분모 0 회피 — 새 값이 0이 아니면 100% 변동으로 간주
                    if new_num != 0:
                        changes.append(FieldChange(type="value_change", ...))
                elif (delta / old_num * 100) >= threshold:
                    changes.append(FieldChange(type="value_change", ...))
            elif delta >= threshold:
                changes.append(FieldChange(type="value_change", ...))
        
        elif job.change_detection.mode == "text":
            diff = compute_text_diff(old_val, new_val)
            if len(diff.changed_chars) >= job.change_detection.text_threshold:
                if not matches_ignore_patterns(diff, job.change_detection.ignore_patterns):
                    changes.append(FieldChange(type="modified", ...))
    
    save_snapshot(current_snapshot)
    return ChangeResult(has_changes=len(changes) > 0, changes=changes)
```

---

## 6. 모니터링 시나리오 프리셋

| 시나리오 | 체크 주기 | 감시 모드 | 임계값 | 알림 |
|----------|----------|----------|--------|------|
| 주식 시세 변동 | 5분 | value (percentage) | ±3% | push + slack |
| 쇼핑 가격 변동 | 1시간 | value (absolute) | 사용자 설정 | push |
| 채용 공고 변경 | 6시간 | text | 5자 이상 | email |
| DART 공시 신규 | 30분 | structure (행 추가) | 1건 이상 | push + email |
| 경쟁사 페이지 변경 | 24시간 | text | 50자 이상 | email |
| 뉴스 키워드 감지 | 15분 | text (키워드 포함) | 키워드 1회 | push |

---

## 7. 워크플로우 노드 연동

웹 변경 감지는 DAG 워크플로우에서 두 가지 방식으로 연동된다:

### 7.1 트리거로 사용 (ConditionTrigger)

```typescript
interface WebMonitorTriggerConfig {
  monitoring_job_id: string;           // 모니터링 작업 ID
  trigger_on: "any_change" | "value_up" | "value_down" | "keyword_added";
  keyword_filter?: string[];           // 키워드 필터 (trigger_on="keyword_added")
}
```

변경 감지 시 → 연결된 워크플로우 자동 실행. ChangeResult가 워크플로우 초기 변수로 주입됨.

### 7.2 노드로 사용 (BrowserNode 프리셋)

```typescript
interface MonitorCheckNodeConfig {
  monitoring_job_id: string;
  output_variable: string;             // ChangeResult 저장 변수
}

interface MonitorCheckNodeOutput {
  change_result: ChangeResult;
  has_changes: boolean;
}
```

---

## 8. 스냅샷 보관 정책

| 항목 | 값 |
|------|-----|
| 스냅샷 보관 기간 | 30일 |
| 최대 스냅샷 수 (작업당) | 1000개 |
| 스크린샷 보관 | 변경 감지 건만 보관 (7일) |
| 스냅샷 저장 위치 | 샌드박스 내 `~/.vamos/monitoring/snapshots/` |

---

## 9. REST API

```
POST   /api/v1/monitoring/jobs                   // 모니터링 작업 생성
GET    /api/v1/monitoring/jobs                    // 작업 목록
GET    /api/v1/monitoring/jobs/:id                // 작업 상세
PUT    /api/v1/monitoring/jobs/:id                // 작업 수정
DELETE /api/v1/monitoring/jobs/:id                // 작업 삭제
POST   /api/v1/monitoring/jobs/:id/check          // 즉시 체크 실행
GET    /api/v1/monitoring/jobs/:id/history         // 변경 이력 조회
GET    /api/v1/monitoring/jobs/:id/snapshots       // 스냅샷 목록
PATCH  /api/v1/monitoring/jobs/:id/toggle          // 활성화/비활성화 전환
```

---

## 10. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| browser_agent.md (N-011) | Playwright 실행 엔진 | ← 사용 (기반) |
| web_scraping.md (N-012) | 변경 감지 → 스크래핑 트리거 | → 트리거 |
| 03_trigger-system | ConditionTrigger 연동 | ← 사용 |
| 04_template-library | 모니터링 템플릿 (주식, 채용 등) | → 제공 |
| browser_security.md | 샌드박스/크리덴셜 정책 | ← 준수 |

---

*끝 — web_monitoring.md L3 v1.0*
