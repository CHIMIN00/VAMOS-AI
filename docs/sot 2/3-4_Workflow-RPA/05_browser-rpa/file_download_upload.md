# 파일 다운로드/업로드 자동화 — L3 상세 명세

> **N-ID**: N-015 (NEW)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 05_browser-rpa
> **정본**: sot 2/3-4_Workflow-RPA/05_browser-rpa/file_download_upload.md

---

## 1. 개요

VAMOS 파일 다운로드/업로드 자동화 모듈은 Playwright 브라우저 에이전트(N-011)를 활용하여 웹사이트에서 파일을 대량 다운로드하거나, 클라우드 서비스 간 파일을 이동하고, 웹 폼에 파일을 자동 업로드하는 기능을 제공한다. 다운로드된 파일은 샌드박스 내에서만 접근 가능하며, 파일 변환(PDF→TXT, CSV→JSON 등)을 후처리로 지원한다.

> LOCK (기존 명세 §6 / LOCK-WF-07): navigate, click, type, extract, screenshot, wait, scroll, select, hover, execute_js — 10종 브라우저 액션 기반

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화

---

## 2. 핵심 제약 (LOCK)

| # | LOCK 항목 | 값 |
|---|-----------|-----|
| LOCK-WF-07 | 브라우저 액션 타입 | click(다운로드 링크), navigate, execute_js 기반 |
| LOCK-WF-10 | RPA 보안 정책 | 다운로드 파일 샌드박스 내 저장, 파일시스템 접근 제한 |

---

## 3. 아키텍처

```
[파일 작업 요청]
    ├─ 다운로드: "DART에서 삼성전자 분기보고서 PDF 다운로드"
    └─ 업로드: "이 CSV 파일을 구글 드라이브에 업로드"
    ↓
[Playwright 브라우저 에이전트 (N-011)]
    ├─ [다운로드 흐름]
    │   ├─ navigate → 파일 목록 페이지
    │   ├─ extract → 파일 링크 추출
    │   ├─ click → 다운로드 트리거
    │   └─ wait → 다운로드 완료 대기
    │
    └─ [업로드 흐름]
        ├─ navigate → 업로드 폼 페이지
        ├─ execute_js → file input 요소에 파일 설정
        └─ click → 업로드 제출
    ↓
[파일 후처리 엔진]
    ├─ 파일 검증 (크기, 타입, 무결성)
    ├─ 파일 변환 (PDF→TXT, CSV→JSON 등)
    └─ 메타데이터 추출
    ↓
[결과] → 샌드박스 내 파일 경로 + 메타데이터
```

---

## 4. 다운로드 설정 스키마

### 4.1 DownloadConfig

```typescript
interface DownloadConfig {
  id: string;                          // 작업 ID
  name: string;                        // 작업명
  source_url: string;                  // 시작 URL
  file_selectors: FileSelector[];      // 파일 링크 선택자 목록
  download_dir: string;                // 저장 디렉터리 (샌드박스 내)
  naming_rule: NamingRule;             // 파일명 규칙
  filter?: FileFilter;                 // 파일 필터
  pagination?: PaginationConfig;       // 페이지네이션 (N-012 재사용)
  max_files: number;                   // 최대 다운로드 수 (기본 100)
  max_total_size_mb: number;           // 최대 총 크기 (기본 1024)
  concurrent_downloads: number;        // 동시 다운로드 수 (기본 3)
  retry_policy: RetryPolicy;
  auth_credential_id?: string;         // 인증 필요 시
}

interface FileSelector {
  link_selector: string;               // 다운로드 링크 선택자
  filename_selector?: string;          // 파일명 추출 선택자 (link text 대체)
  metadata_selectors?: Record<string, string>;  // 부가 정보 (날짜, 크기 등)
}

interface NamingRule {
  strategy: "original" | "pattern" | "sequential";
  pattern?: string;                    // "{{date}}_{{title}}.{{ext}}" (Jinja2)
  prefix?: string;
  suffix?: string;
}

interface FileFilter {
  extensions?: string[];               // 허용 확장자 ["pdf", "xlsx", "csv"]
  min_size_bytes?: number;
  max_size_bytes?: number;
  name_pattern?: string;               // 파일명 regex 필터
  date_after?: string;                 // 날짜 필터 (메타데이터 기반)
  date_before?: string;
}
```

### 4.2 다운로드 실행 로직

```
function execute_download(config):
    page = navigate(config.source_url)
    auth_if_needed(config.auth_credential_id)
    
    files_to_download = []
    while has_more_pages(config.pagination):
        links = extract_file_links(page, config.file_selectors)
        for link in links:
            if passes_filter(link, config.filter):
                files_to_download.append(link)
            if len(files_to_download) >= config.max_files:
                break
        next_page(config.pagination)
    
    results = []
    for batch in chunk(files_to_download, config.concurrent_downloads):
        batch_results = parallel_download(batch, config.download_dir, config.naming_rule)
        results.extend(batch_results)
        check_total_size(results, config.max_total_size_mb)
    
    return DownloadResult(files=results)
```

---

## 5. 업로드 설정 스키마

### 5.1 UploadConfig

```typescript
interface UploadConfig {
  id: string;
  name: string;
  target_url: string;                  // 업로드 대상 페이지 URL
  file_input_selector: string;         // <input type="file"> 선택자
  files: UploadFile[];                 // 업로드할 파일 목록
  submit_selector?: string;            // 제출 버튼 선택자
  pre_upload_actions?: BrowserActionStep[];  // 업로드 전 사전 액션
  post_upload_actions?: BrowserActionStep[]; // 업로드 후 후속 액션
  verify_upload: boolean;              // 업로드 성공 확인 (기본 true)
  verify_selector?: string;            // 성공 확인 선택자
  auth_credential_id?: string;
}

interface UploadFile {
  source: "sandbox" | "workflow_variable";
  path?: string;                       // sandbox 파일 경로
  variable_name?: string;              // 워크플로우 변수명 (바이너리)
  target_filename?: string;            // 업로드 시 파일명 변경
}
```

### 5.2 업로드 실행 로직

```
function execute_upload(config):
    page = navigate(config.target_url)
    auth_if_needed(config.auth_credential_id)
    
    execute_actions(page, config.pre_upload_actions)
    
    file_input = page.query_selector(config.file_input_selector)
    file_paths = resolve_file_paths(config.files)  // 샌드박스 내 경로
    file_input.set_input_files(file_paths)
    
    if config.submit_selector:
        page.click(config.submit_selector)
    
    if config.verify_upload:
        if not config.verify_selector:
            raise ConfigError("verify_upload=true 인 경우 verify_selector 필수")
        wait_for_element(page, config.verify_selector, timeout=30000)
    
    execute_actions(page, config.post_upload_actions)
    
    return UploadResult(uploaded=len(file_paths), verified=config.verify_upload)
```

---

## 6. 파일 후처리 엔진

### 6.1 변환 규칙

| 변환 | 입력 | 출력 | 사용 도구 |
|------|------|------|----------|
| PDF → TXT | .pdf | .txt | pdfplumber / PyMuPDF |
| PDF → Markdown | .pdf | .md | pdfplumber + LLM 구조화 |
| CSV → JSON | .csv | .json | pandas |
| XLSX → CSV | .xlsx | .csv | openpyxl → pandas |
| HTML → Markdown | .html | .md | markdownify |
| 이미지 → 텍스트 | .png/.jpg | .txt | OCR (Tesseract) |

### 6.2 FileConversionConfig

```typescript
interface FileConversionConfig {
  input_path: string;                  // 원본 파일 경로 (샌드박스 내)
  output_format: "txt" | "json" | "csv" | "md" | "markdown";
  output_path?: string;                // 출력 경로 (기본: 같은 디렉터리)
  encoding?: string;                   // 출력 인코딩 (기본 "utf-8")
  options?: Record<string, any>;       // 변환별 옵션
}

interface FileMetadata {
  filename: string;
  extension: string;
  size_bytes: number;
  mime_type: string;
  created_at: string;
  source_url: string;                  // 다운로드 원본 URL
  checksum_sha256: string;             // 무결성 검증용
}
```

---

## 7. 보안 정책

| 항목 | 정책 |
|------|------|
| 다운로드 저장 | 샌드박스 내 전용 디렉터리만 허용 (`~/.vamos/downloads/`) |
| 파일 크기 제한 | 단일 파일 최대 500MB, 작업당 총 1GB |
| 허용 파일 타입 | 화이트리스트 기반 (pdf, xlsx, csv, json, txt, png, jpg, html, xml) |
| 실행 파일 차단 | .exe, .bat, .sh, .ps1, .dll, .so → 다운로드 즉시 삭제 + 경고 |
| 업로드 검증 | 업로드 전 파일 타입 + 크기 사전 검증 |
| 파일 보관 | 30일 후 자동 삭제 (보관 정책 설정 가능) |

---

## 8. 워크플로우 노드 연동

```typescript
interface FileDownloadNodeConfig {
  download_config: DownloadConfig;
  post_processing?: FileConversionConfig[];  // 다운로드 후 변환
  output_variable: string;             // 결과 저장 변수 (파일 경로 목록)
}

interface FileUploadNodeConfig {
  upload_config: UploadConfig;
  source_variable?: string;            // 이전 노드 결과 파일 사용
}

interface FileOperationNodeOutput {
  files: FileMetadata[];               // 처리된 파일 메타데이터
  total_files: number;
  total_size_bytes: number;
  converted_files?: string[];          // 변환된 파일 경로
  duration_ms: number;
  errors: string[];
}
```

---

## 9. REST API

```
POST   /api/v1/files/download                    // 다운로드 작업 생성 + 실행
GET    /api/v1/files/download/:id                 // 다운로드 진행 상태
POST   /api/v1/files/upload                       // 업로드 작업 생성 + 실행
GET    /api/v1/files/upload/:id                   // 업로드 진행 상태
POST   /api/v1/files/convert                      // 파일 변환
GET    /api/v1/files/sandbox                       // 샌드박스 내 파일 목록
GET    /api/v1/files/sandbox/:path                 // 파일 메타데이터 조회
DELETE /api/v1/files/sandbox/:path                 // 파일 삭제
```

---

## 10. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| browser_agent.md (N-011) | Playwright 실행 엔진 | ← 사용 (기반) |
| form_autofill.md (N-014) | 파일 업로드 필드 위임 | ← 위임받음 |
| web_scraping.md (N-012) | 스크래핑 결과 파일 저장 | ← 연동 |
| browser_security.md | 샌드박스 파일 접근 정책 | ← 준수 |
| 01_dag-engine | FileNode / BrowserNode 연동 | ← 사용 |

---

*끝 — file_download_upload.md L3 v1.0*
