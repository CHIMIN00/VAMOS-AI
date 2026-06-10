# 폼 자동 입력 — L3 상세 명세

> **N-ID**: N-014 (NEW)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 05_browser-rpa
> **정본**: sot 2/3-4_Workflow-RPA/05_browser-rpa/form_autofill.md

---

## 1. 개요

VAMOS 폼 자동 입력 모듈은 Playwright 브라우저 에이전트(N-011) 위에 구축된 **반복 폼 입력 자동화 전문 모듈**이다. 사용자의 개인 정보, 비즈니스 데이터, 이력서 정보를 암호화 저장하고 웹 폼에 자동으로 입력한다. AI 기반 필드 매칭으로 다양한 폼 레이아웃에 적응하며, 입력 전 사용자 확인(Human-in-the-Loop)을 지원한다.

> LOCK (기존 명세 §6 / LOCK-WF-07): navigate, click, type, extract, screenshot, wait, scroll, select, hover, execute_js — 10종 브라우저 액션 기반

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화

---

## 2. 핵심 제약 (LOCK)

| # | LOCK 항목 | 값 |
|---|-----------|-----|
| LOCK-WF-07 | 브라우저 액션 타입 | type, select, click 액션 기반 폼 입력 |
| LOCK-WF-10 | RPA 보안 정책 | 개인 정보 AES-256 암호화 저장, 샌드박스 내 실행 |
| LOCK-WF-03 | Human Approval 타임아웃 | 민감 정보 입력 전 사용자 확인 10분 |

---

## 3. 아키텍처

```
[폼 자동 입력 요청]
    ├─ 자연어: "잡코리아 지원서에 내 이력서 정보로 입력해줘"
    └─ 구조화: AutofillRequest
    ↓
[Playwright 브라우저 에이전트 (N-011)]
    ├─ navigate → 폼 페이지
    ├─ extract → 폼 구조 분석 (필드 목록 추출)
    └─ screenshot → 폼 미리보기
    ↓
[폼 분석 엔진]
    ├─ 필드 타입 추론 (text/email/phone/date/select/radio/checkbox)
    ├─ 필드 라벨 추출 (label, placeholder, aria-label)
    └─ 필수/선택 판별
    ↓
[AI 필드 매칭]
    ├─ 프로필 데이터 ↔ 폼 필드 자동 매핑
    └─ 신뢰도 < 0.8 → 사용자 확인 요청
    ↓
[입력 실행]
    ├─ type → 텍스트 필드
    ├─ select → 드롭다운
    ├─ click → 라디오/체크박스
    └─ [사용자 확인] → 제출 전 미리보기
    ↓
[결과] → 입력 완료 보고 + 스크린샷
```

---

## 4. 프로필 데이터 스키마

### 4.1 AutofillProfile

```typescript
interface AutofillProfile {
  id: string;                          // 프로필 ID
  name: string;                        // 프로필명 ("기본 프로필", "이력서 프로필")
  personal: PersonalInfo;
  contact: ContactInfo;
  address?: AddressInfo;
  employment?: EmploymentInfo;
  education?: EducationInfo;
  custom_fields: Record<string, string>;  // 사용자 정의 필드
  encrypted: boolean;                  // AES-256 암호화 여부 (항상 true)
  created_at: string;
  updated_at: string;
}

interface PersonalInfo {
  full_name: string;                   // 성명
  full_name_en?: string;               // 영문 성명
  birth_date?: string;                 // YYYY-MM-DD
  gender?: "male" | "female" | "other";
  national_id_masked?: string;         // 주민번호 앞자리만 (뒷자리 미저장)
}

interface ContactInfo {
  email: string;
  phone: string;                       // 010-XXXX-XXXX
  phone_alt?: string;                  // 보조 연락처
}

interface AddressInfo {
  postal_code: string;
  address_line1: string;               // 도로명 주소
  address_line2?: string;              // 상세 주소
  city: string;
  province: string;
}

interface EmploymentInfo {
  company: string;                     // 회사명
  title: string;                       // 직함
  department?: string;                 // 부서
  start_date: string;                  // YYYY-MM
  end_date?: string;                   // YYYY-MM (현재 재직 시 null)
}

interface EducationInfo {
  school: string;                      // 학교명
  degree: "highschool" | "associate" | "bachelor" | "master" | "doctorate";
  major?: string;                      // 전공
  graduation_year?: number;
}
```

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 프로필 데이터는 AES-256 암호화 저장 필수. 주민번호 뒷자리, 비밀번호 등 고위험 정보는 저장 불가.

---

## 5. 폼 분석 엔진

### 5.1 폼 구조 추출

```typescript
interface FormStructure {
  url: string;
  form_selector: string;               // <form> 요소 선택자
  fields: FormField[];
  submit_button?: string;              // 제출 버튼 선택자
  has_captcha: boolean;
  has_file_upload: boolean;
}

interface FormField {
  selector: string;                    // 필드 선택자
  field_type: "text" | "email" | "tel" | "number" | "date" | "password"
              | "select" | "radio" | "checkbox" | "textarea" | "file";
  label: string;                       // 추출된 라벨 텍스트
  name?: string;                       // input name 속성
  placeholder?: string;
  required: boolean;                   // required 속성 또는 * 표시
  options?: string[];                  // select/radio의 옵션 목록
  max_length?: number;
  pattern?: string;                    // input validation 패턴
  current_value?: string;              // 기존 입력값
}
```

### 5.2 필드 타입 추론 규칙

| 라벨 패턴 | 추론 타입 | 매핑 대상 |
|----------|----------|----------|
| 이름, 성명, name | text | personal.full_name |
| 이메일, email, e-mail | email | contact.email |
| 전화, 연락처, phone, tel | tel | contact.phone |
| 생년월일, birth, 생일 | date | personal.birth_date |
| 주소, address | text | address.address_line1 |
| 우편번호, zip, postal | text | address.postal_code |
| 학교, 대학, school | text | education.school |
| 회사, company, 직장 | text | employment.company |
| 직함, title, 직위 | text | employment.title |

### 5.3 설문 AI 답변 제안

설문 폼의 경우, 프로필 데이터만으로 답변이 어려운 주관식 항목에 대해 LLM 기반 답변 제안을 제공한다.

```typescript
interface SurveyAssistConfig {
  enabled: boolean;                    // AI 답변 제안 활성화 (기본 false)
  context?: string;                    // 설문 맥락 ("채용 지원서", "고객 만족도 조사")
  tone?: "formal" | "casual";         // 답변 톤 (기본 "formal")
  max_length_per_answer?: number;      // 답변 최대 길이 (기본 200자)
}

interface SurveyAnswerSuggestion {
  field_selector: string;              // 설문 필드 선택자
  question_text: string;               // 질문 텍스트
  suggested_answer: string;            // AI 제안 답변
  confidence: number;                  // 신뢰도
  requires_review: boolean;            // 항상 true (AI 답변은 반드시 사용자 확인)
}
```

**규칙**: AI 설문 답변은 항상 `requires_review=true`이며, 사용자 확인 없이 자동 제출하지 않는다.

---

## 6. AI 필드 매칭

### 6.1 매칭 스키마

```typescript
interface FieldMapping {
  form_field: string;                  // 폼 필드 선택자
  profile_path: string;                // 프로필 데이터 경로 ("contact.email")
  value: string;                       // 입력할 값
  confidence: number;                  // 매칭 신뢰도 (0.0 ~ 1.0)
  method: "rule_based" | "llm_inferred";  // 매칭 방법
  needs_confirmation: boolean;         // 신뢰도 < 0.8이면 true
}

interface AutofillPlan {
  form_url: string;
  profile_id: string;
  mappings: FieldMapping[];
  unmapped_fields: FormField[];        // 매칭 실패 필드
  warnings: string[];                  // 경고 (필수 필드 미매핑 등)
  requires_human_review: boolean;      // 전체 확인 필요 여부
}
```

**매칭 의사코드**:
```
function create_autofill_plan(form, profile):
    mappings = []
    for field in form.fields:
        // 1단계: 규칙 기반 매칭 (라벨 패턴)
        match = rule_based_match(field.label, field.name, field.field_type)
        if match and match.confidence >= 0.7:
            mappings.append(FieldMapping(
                profile_path=match.path,
                confidence=match.confidence,
                method="rule_based",
                needs_confirmation=(match.confidence < 0.9)
            ))
            continue
        
        // 2단계: LLM 추론 매칭
        llm_match = llm_infer_mapping(
            field_label=field.label,
            field_type=field.field_type,
            field_context=field.placeholder,
            available_data=profile.to_field_list()
        )
        if llm_match.confidence >= 0.7:
            mappings.append(FieldMapping(
                profile_path=llm_match.path,
                confidence=llm_match.confidence,
                needs_confirmation=(llm_match.confidence < 0.8)
            ))
        else:
            unmapped.append(field)
    
    return AutofillPlan(mappings=mappings, unmapped_fields=unmapped)
```

---

## 7. 입력 실행 엔진

### 7.1 입력 순서 및 전략

```typescript
interface AutofillExecution {
  plan: AutofillPlan;
  execution_order: string[];           // 필드 입력 순서 (의존 관계 고려)
  delay_between_fields_ms: number;     // 필드 간 지연 (기본 200, 봇 탐지 방지)
  simulate_human: boolean;             // 인간 유사 타이핑 (기본 true)
  verify_after_input: boolean;         // 입력 후 값 검증 (기본 true)
  screenshot_before_submit: boolean;   // 제출 전 스크린샷 (기본 true)
  auto_submit: boolean;                // 자동 제출 (기본 false, 사용자 확인 후)
}
```

### 7.2 필드 타입별 입력 전략

| 필드 타입 | 사용 액션 | 특수 처리 |
|----------|----------|----------|
| text / email / tel / textarea | type | clear_before=true, 인간 유사 타이핑 딜레이 |
| number | type | 숫자만 입력, 포맷 변환 (콤마 제거) |
| date | type 또는 execute_js | 브라우저 날짜 피커 호환 (YYYY-MM-DD) |
| select | select | value 또는 label 기반 선택 |
| radio | click | 매칭 option 클릭 |
| checkbox | click | 필요 시 체크/해제 토글 |
| password | (입력 불가) | 보안 정책: 비밀번호 자동 입력 차단 |
| file | (N-015 연동) | 파일 업로드 전용 모듈 위임 |

---

## 8. 보안 정책

| 항목 | 정책 |
|------|------|
| 프로필 저장 | AES-256 암호화 필수 (LOCK-WF-10) |
| 고위험 정보 | 주민번호 뒷자리, 비밀번호, 카드 번호 → 저장 불가 |
| 민감 필드 입력 | 사용자 확인(HumanApproval) 후 입력 |
| 입력 로그 | 필드명만 기록, 입력값은 마스킹 처리 |
| 세션 종료 | 입력 완료 후 브라우저 컨텍스트 즉시 종료 (쿠키/캐시 삭제) |

---

## 9. 워크플로우 노드 연동

```typescript
interface AutofillNodeConfig {
  profile_id: string;                  // 사용할 프로필 ID
  form_url: string;                    // 폼 페이지 URL
  form_selector?: string;              // 특정 <form> 선택자 (페이지 내 복수 폼)
  custom_values?: Record<string, string>;  // 프로필 외 추가 입력값
  require_confirmation: boolean;       // 입력 전 사용자 확인 (기본 true)
  auto_submit: boolean;                // 자동 제출 (기본 false)
}

interface AutofillNodeOutput {
  filled_fields: number;               // 입력 완료 필드 수
  skipped_fields: number;              // 건너뛴 필드 수
  unmapped_fields: string[];           // 매핑 실패 필드
  screenshot_path: string;             // 입력 후 스크린샷
  submitted: boolean;                  // 제출 여부
  duration_ms: number;
}
```

---

## 10. REST API

```
GET    /api/v1/autofill/profiles                 // 프로필 목록
POST   /api/v1/autofill/profiles                 // 프로필 생성
GET    /api/v1/autofill/profiles/:id             // 프로필 상세
PUT    /api/v1/autofill/profiles/:id             // 프로필 수정
DELETE /api/v1/autofill/profiles/:id             // 프로필 삭제
POST   /api/v1/autofill/analyze                  // 폼 구조 분석
POST   /api/v1/autofill/plan                     // 자동 입력 계획 생성
POST   /api/v1/autofill/execute                  // 자동 입력 실행
```

---

## 11. 교차참조

| 참조 모듈 | 연관 항목 | 참조 방향 |
|----------|---------|----------|
| browser_agent.md (N-011) | Playwright 10종 액션 | ← 사용 (기반) |
| file_download_upload.md (N-015) | 파일 업로드 필드 위임 | → 위임 |
| browser_security.md | AES-256 암호화, 샌드박스 | ← 준수 |
| T2-CORE_AI | LLM 필드 매칭 추론 | ← 사용 |

---

*끝 — form_autofill.md L3 v1.0*
