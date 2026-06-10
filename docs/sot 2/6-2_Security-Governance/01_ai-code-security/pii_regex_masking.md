# PII Regex 마스킹 상세 명세

> **Phase**: 1 (V1)
> **§7.3 항목**: #5 "PII Regex 마스킹"
> **세션**: P1-1
> **작성일**: 2026-04-12
> **상태**: DRAFT

---

## 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| Part2 구현가이드 | §6.5 #4 | PII 마스킹 구현 지침 |
| D2.0-07 | §15.4 | GDPR 데이터 보호 |
| 01_ai-code-security/_index.md | §B #4 | 보안 항목 목록 |
| nemo_guardrails_l1_input.md | §2.2 | L1 PII 입력 탐지 연동 |
| guardrails_ai_l2_output.md | §4.2 | L2 PII 출력 탐지 연동 |

---

## 1. PII 유형별 regex 패턴 라이브러리

### 1.1 이메일 (RFC 5322 패턴)

```typescript
const EMAIL_PATTERN = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
// 시간복잡도: O(n) — n=문자열 길이
```

### 1.2 전화번호 (국가 코드 포함)

```typescript
const PHONE_PATTERNS = {
  // 한국 전화번호
  KR_MOBILE: /01[016789]-?\d{3,4}-?\d{4}/g,
  KR_LANDLINE: /0\d{1,2}-?\d{3,4}-?\d{4}/g,
  // 국제 전화번호
  INTERNATIONAL: /\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}/g,
};
```

### 1.3 주민등록번호 / SSN

```typescript
const ID_NUMBER_PATTERNS = {
  // 한국 주민등록번호 (YYMMDD-GNNNNNN)
  KR_RRN: /\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])-?[1-4]\d{6}/g,
  // 미국 SSN (NNN-NN-NNNN)
  US_SSN: /\b\d{3}-?\d{2}-?\d{4}\b/g,
};
```

### 1.4 신용카드 (Luhn 사전 검증 포함)

```typescript
const CREDIT_CARD_PATTERNS = {
  VISA: /4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}/g,
  MASTERCARD: /5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}/g,
  AMEX: /3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}/g,
  GENERIC: /\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}/g,
};

// Luhn 사전 검증
function luhnCheck(num: string): boolean {
  const digits = num.replace(/\D/g, '');
  let sum = 0;
  let isEven = false;
  for (let i = digits.length - 1; i >= 0; i--) {
    let digit = parseInt(digits[i], 10);
    if (isEven) { digit *= 2; if (digit > 9) digit -= 9; }
    sum += digit;
    isEven = !isEven;
  }
  return sum % 10 === 0;
}
// 시간복잡도: O(d) — d=숫자 자릿수
```

### 1.5 IP 주소 (IPv4/IPv6)

```typescript
const IP_PATTERNS = {
  IPv4: /\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b/g,
  IPv6: /(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}/g,
};
```

### 1.6 이름 (NER 보조 필요)

> 참고: 이름은 regex만으로 정확한 탐지가 어려워 NER(Named Entity Recognition) 모델 보조 필요.
> V1 단계에서는 한국 이름 패턴(2~4글자 한글)과 영문 이름 패턴을 기본 제공하되,
> 오탐률이 높으므로 기본 비활성 상태. V2에서 NER 모델 연동 후 활성화.

```typescript
const NAME_PATTERNS = {
  // 한국 이름 (2~4글자, NER 보조 필요 — V2)
  KR_NAME: /[가-힣]{2,4}/g,  // 오탐 높음, 기본 비활성
  // 영문 이름 (Mr./Ms./Dr. 접두어 포함)
  EN_NAME: /(?:Mr|Ms|Mrs|Dr|Prof)\.\s?[A-Z][a-z]+(?:\s[A-Z][a-z]+)+/g,
};
```

---

## 2. 마스킹 전략 정의

### 2.1 부분 마스킹 (기본)

| PII 유형 | 원본 예시 | 마스킹 결과 | 용도 |
|---------|----------|------------|------|
| 이메일 | `user@example.com` | `u***@e***.com` | 사용자 응답 |
| 전화번호 | `010-1234-5678` | `010-****-5678` | 사용자 응답 |
| 카드번호 | `4123-4567-8901-2345` | `4123-****-****-2345` | 사용자 응답 |

### 2.2 전체 마스킹

| PII 유형 | 원본 예시 | 마스킹 결과 | 용도 |
|---------|----------|------------|------|
| 주민번호 | `901231-1234567` | `[PII_REDACTED:RRN]` | 로그 기록 |
| SSN | `123-45-6789` | `[PII_REDACTED:SSN]` | 로그 기록 |
| IP 주소 | `192.168.1.100` | `[PII_REDACTED:IP]` | 로그 기록 |

### 2.3 비복원 가명처리 (pseudonymization, 보안 감사용)

```typescript
interface PIIToken {
  token: string;              // "PII_TKN_a1b2c3d4"
  original_hash: string;      // SHA-256 해시 (원본 복원 불가, 동일성 확인용)
  pii_type: string;           // "EMAIL" | "PHONE" | "RRN" | ...
  created_at: string;         // ISO 8601
  expires_at: string;         // 90일 후 자동 삭제 (GDPR 최소 보존)
  access_level: 'ADMIN';      // L8 RBAC — ADMIN 이상만 토큰 매핑 조회
}
```

---

## 3. 적용 지점

### 3.1 L1 입력 전처리 (NeMo 연동)

```
[사용자 입력] → PII 탐지 → 마스킹 → [NeMo L1 필터링]
```
- **시점**: NeMo Guardrails 규칙 실행 전
- **목적**: LLM에 PII가 전달되지 않도록 사전 차단
- **전략**: 전체 마스킹 (`[PII_REDACTED:TYPE]`)

### 3.2 L2 출력 후처리 (Guardrails AI 연동)

```
[LLM 출력] → [Guardrails AI L2] → PII 탐지 → 마스킹 → [사용자 응답]
```
- **시점**: Guardrails AI Validator 체인 내 `DetectPII` Validator
- **목적**: LLM 출력에 포함된 PII 유출 방지
- **전략**: 부분 마스킹 (사용자 응답용)

### 3.3 로그 기록 시

```
[감사 로그 기록] → PII 탐지 → 전체 마스킹 → [로그 저장]
```
- **시점**: 모든 로그 기록 전
- **목적**: 로그에 PII 저장 방지 (GDPR 준수)
- **전략**: 전체 마스킹 + 토큰화 (감사 추적용)

---

## 4. 오탐·미탐 대응

### 4.1 허용 목록 (비 PII 이메일 형식)

```typescript
const PII_WHITELIST = [
  /noreply@.*\.com/,          // 시스템 이메일
  /support@vamos\..*$/,       // VAMOS 공식 이메일
  /example\.(com|org|net)/,   // 예시 도메인
  /test@test\.com/,           // 테스트 이메일
];
```

### 4.2 정기 패턴 업데이트

| 주기 | 작업 | 담당 |
|------|------|------|
| **분기 1회** | PII 패턴 라이브러리 검토 + 업데이트 | 6-2 도메인 관리자 |
| **연 1회** | NER 모델 재학습 (V2+) | ML 팀 |
| **즉시** | 새로운 PII 유형 요청 시 패턴 추가 | 6-2 도메인 관리자 |

### 4.3 오탐률 관리

| PII 유형 | 예상 오탐률 | 대응 |
|---------|:---------:|------|
| 이메일 | <1% | 허용 목록으로 관리 |
| 전화번호 | ~5% | 국가 코드 필수 매칭으로 정밀도 향상 |
| 주민번호 | ~2% | 날짜 유효성 추가 검증 |
| 카드번호 | <1% | Luhn 사전 검증으로 정밀도 보장 |
| 이름 | ~30% | V1 비활성, V2 NER 보조 |
| IP 주소 | ~3% | 사설 IP 대역 허용 목록 |

---

## 5. D2.0-07 §15.4 GDPR 요구사항 반영

| GDPR 원칙 | 본 문서 반영 | 구현 |
|----------|------------|------|
| 데이터 최소화 | §3.1 입력 전처리 | LLM에 PII 미전달 |
| 목적 제한 | §2.3 토큰화 | 감사 목적에만 토큰 사용 |
| 저장 제한 | §2.3 expires_at | 토큰 90일 후 자동 삭제 |
| 접근 제한 | §2.3 access_level | ADMIN 이상만 토큰 매핑 조회 (L8) |
| 무결성·기밀성 | §3.3 로그 마스킹 | 로그에 PII 저장 방지 |

---

## 6. 로깅 포맷 (R-01-7)

```json
{
  "event": "security.pii.masking",
  "trace_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
  "timestamp": "2026-04-12T13:00:00Z",
  "error": {
    "code": "PII-MASK-001",
    "message": "PII detected and masked",
    "severity": "MEDIUM"
  },
  "context": {
    "pii_type": "EMAIL",
    "masking_strategy": "partial",
    "apply_point": "L2_output",
    "token_generated": true,
    "token_id": "PII_TKN_a1b2c3d4"
  },
  "recovery": {
    "action": "masked_and_returned",
    "original_preserved": false,
    "token_expires": "2026-07-11T13:00:00Z"
  }
}
```

---

## 7. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| PII-MASK-001 | PII 탐지 + 마스킹 완료 | YES | 마스킹 후 정상 처리 |
| PII-MASK-002 | PII 탐지 + 마스킹 실패 | NO | 전체 문자열 차단, 감사 로그 |
| PII-MASK-003 | 토큰화 저장 실패 | YES | 마스킹 유지, 토큰 없이 진행 |
| PII-MASK-004 | 허용 목록 로딩 실패 | YES | 기본 규칙 적용 (오탐 증가 감수) |
| PII-MASK-005 | regex 패턴 컴파일 오류 | NO | 해당 PII 유형 비활성, P1 알림 |

---

## 8. Phase 2 통합 테스트 시나리오

| # | 시나리오 | 예상 결과 |
|---|---------|----------|
| T-01 | 이메일 `john@example.com` 포함 입력 | 부분 마스킹 `j***@e***.com` |
| T-02 | 주민번호 `901231-1234567` 포함 입력 | 전체 마스킹 `[PII_REDACTED:RRN]` |
| T-03 | 카드번호 `4123-4567-8901-2345` 포함 출력 | Luhn 검증 후 마스킹 |
| T-04 | 허용 목록 이메일 `noreply@vamos.ai` | 마스킹 미적용 |
| T-05 | 복수 PII 동시 포함 (이메일+전화+주민번호) | 3건 모두 개별 마스킹 |
| T-06 | PII 토큰 90일 후 자동 삭제 확인 | 만료 토큰 조회 시 404 |
| T-07 | OPERATOR 역할로 토큰 매핑 조회 시도 | 403 Forbidden (ADMIN 필요) |
| T-08 | 로그 파일에 PII 미저장 확인 | grep 검증 — PII 패턴 0건 |
| T-09 | IPv6 주소 `2001:0db8::1` 포함 로그 | 전체 마스킹 |
| T-10 | L1 입력 + L2 출력 + 로그 3곳 모두 PII 마스킹 동작 | 3곳 모두 마스킹 확인 |

---

## LOCK 교차 검증 결과

| LOCK | AUTHORITY_CHAIN §5 값 | 본 문서 반영 | 일치 |
|------|----------------------|------------|:----:|
| L7 | L1 NeMo(입력) → L2 Guardrails AI(처리) → L3 LlamaGuard(출력) | §3 적용 지점 (L1 입력/L2 출력) | OK |
| L8 | OWNER/ADMIN/OPERATOR/VIEWER | §2.3 토큰 access_level: ADMIN | OK |
| L15 | Non-goal 절대 금지 (개인정보 장기 저장 등) | §5 GDPR 요구사항 반영 | OK |
