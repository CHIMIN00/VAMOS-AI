# email_message_extraction.md — 이메일/메시지 지식 추출 (M-006)

> **Status**: APPROVED (L3) — V2 NEW
> **작성일**: 2026-04-23
> **정본 소유 개념**: Gmail/Outlook/Slack/Discord 연동, OAuth2 인증 흐름, 메시지 파싱, 스레드 요약, 지식 단위 추출, 증분 동기화, 중복 제거
> **SoT 근거**: STEP7-M Part 1 (M-006 L114-130) + 기존 명세 §2.3 + 종합계획서 §6.1
> **담당 M-ID**: M-006 (V2 NEW)
> **상위 인덱스**: [_index.md](./_index.md)

---

## §1. 교차 참조 블록

| # | 종류 | 대상 | 역할 |
|---|------|------|------|
| #1 | 상위 SoT | `sot/STEP7-M_PKM_지식관리_작업가이드.md` Part 1 L114-130 | M-006 요구사항 원천 |
| #2 | 권한 체인 | `AUTHORITY_CHAIN.md` §2 (LOCK-PKM-06/07/08) | 중복 임계 + 태그 + 카테고리 |
| #3 | 동일 폴더 | `auto_extraction_pipeline.md` (M-001) | `KnowledgeCandidate` 공통 스키마 |
| #4 | 동일 폴더 | `screen_capture.md` (M-004) | UI 컨텍스트 기반 추출 패턴 대칭 |
| #5 | 동일 폴더 | `document_ingest.md` (M-003) | 첨부파일 자동 인제스트 위임 |
| #6 | 타 폴더 | `02_knowledge-graph/knowledge_graph_construction.md` | 스레드 → 그래프 관계 매핑 |
| #7 | 타 폴더 | `03_spaced-repetition/semantic_search.md` | 이메일 시맨틱 검색 공유 |
| #8 | 타 도메인 | `#3 Workflow-RPA` (이메일 자동 분류 트리거) | 워크플로우 의존 |

---

## §2. LOCK 인용 (verbatim)

> LOCK (STEP7-M M-011 / LOCK-PKM-07): 태그 분류 체계 — 주제/유형/감정/중요도/프로젝트 5차원

> LOCK (기존 명세 §3.2 / LOCK-PKM-08): 지식 카테고리 — concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark

> LOCK (기존 명세 §3.3 / LOCK-PKM-06): 중복 감지 임계값 — MinHash Jaccard ≥ 0.7 (근사), 벡터 유사도 ≥ 0.85 (의미적)

> **참조** (SM-2 정본 소유, 3-5 Education 공유 대칭 — 본 문서는 참조만):
> - LOCK-PKM-01: MIN_EASINESS = 1.3
> - LOCK-PKM-02: DEFAULT_EASINESS = 2.5
> - LOCK-PKM-03: n=1: 1일, n=2: 6일, n≥3: I(n-1) × EF

---

## §3. 공통 자료 구조 재사용 (출처: 3-3 PKM `auto_extraction_pipeline.md` §E2)

`KnowledgeCandidate` 스키마는 `screen_capture.md` §3 와 동일 (재정의 ❌). 본 문서는 동일 출처의 동일 스키마를 인용한다.

```python
# 출처: 01_knowledge-capture/auto_extraction_pipeline.md §E2
class KnowledgeCandidate:
    candidate_id: UUID
    title: str
    body: str                       # 정본 auto_extraction_pipeline.md §E2 (원자적 노트 ≤300단어)
    category: KnowledgeCategory     # LOCK-PKM-08 8종
    tags: TagBundle                 # LOCK-PKM-07 5차원 (정본 §E2 TagBundle)
    source_ref: SourceRef
    captured_at: datetime
    confidence: float
```

추상 기반 클래스 (ABC): `BaseMessageExtractor` — `extract_from_message()` 구현 강제
시간 복잡도: 스레드 파싱 O(m) (m=메시지 수), 지식 추출 O(m·k) (k=추출 후보 수), 중복 O(m·k² MinHash) → 실무상 LSH 인덱스로 O(m·k·log n)

---

## §4. M-006 이메일/메시지 지식 추출 [V2 NEW]

### §4.1 아키텍처 개요

```
[어댑터 레이어]
        │
        ├── Gmail Adapter (Gmail API v1 + OAuth2)
        ├── Outlook Adapter (Microsoft Graph v1.0 + OAuth2)
        ├── Slack Adapter (Slack Web API + OAuth2 user token)
        └── Discord Adapter (Discord Gateway + Bot token)
        │
        ↓
[공통 메시지 모델]  ← §4.2 상세
        │
        └── CanonicalMessage (provider 중립 스키마)
        │
        ↓
[스레드 재조립]  ← §4.3 상세
        │
        ├── References / In-Reply-To (이메일)
        ├── thread_ts (Slack)
        └── message_reference (Discord)
        │
        ↓
[지식 추출 엔진]  ← §4.4 상세
        │
        ├── 메시지 본문 → KnowledgeCandidate
        ├── 첨부파일 → document_ingest.md 위임
        ├── 일정/약속 자동 추출 (NER + 날짜 파서)
        └── 코드 스니펫 (Slack triple-backtick / 이메일 <pre>)
        │
        ↓
[증분 동기화 상태 저장소]
        │
        ├── provider_state: {last_history_id, last_cursor, etag}
        ├── message_idempotency: {(provider, message_id) → candidate_ids}
        └── sync_checkpoints (중단 복구)
```

### §4.2 공통 메시지 모델 (provider-neutral)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from uuid import UUID

class MessageProvider(str, Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    SLACK = "slack"
    DISCORD = "discord"

@dataclass
class CanonicalAttachment:
    attachment_id: str
    filename: str
    mime_type: str
    size_bytes: int
    download_url_expires_at: Optional[datetime]   # provider 측 만료 시각
    local_path: Optional[str]                     # document_ingest.md 처리 후 경로

@dataclass
class CanonicalMessage:
    provider: MessageProvider
    message_id: str                # provider 고유 ID (ex. Gmail messageId)
    thread_id: str                 # 스레드 키 (provider 네이티브)
    sender: str                    # email / @user / user_id
    recipients: list[str]          # To + Cc (BCC 제외 — Phase 3 privacy_filter)
    subject: Optional[str]
    body_text: str                 # plaintext (HTML → 변환 후 저장)
    body_html: Optional[str]
    sent_at: datetime
    received_at: datetime
    channel_id: Optional[str]      # Slack/Discord 전용
    is_direct_message: bool
    attachments: list[CanonicalAttachment] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)   # Gmail labels / Slack reactions 등
    quoted_snippets: list[str] = field(default_factory=list)  # "On Mon, ... wrote:" 블록

class BaseMessageExtractor(ABC):
    @abstractmethod
    def authenticate(self) -> bool: ...
    @abstractmethod
    def fetch_incremental(self, since_state: dict) -> list[CanonicalMessage]: ...
    @abstractmethod
    def extract_from_message(self, msg: CanonicalMessage) -> list[KnowledgeCandidate]: ...
```

### §4.3 OAuth2 인증 흐름

| provider | 흐름 | 토큰 저장 | 갱신 |
|----------|------|-----------|------|
| Gmail | Authorization Code + PKCE (scope: `gmail.readonly`, `gmail.metadata`) | OS Keyring | refresh_token 자동 회전 |
| Outlook | Authorization Code + PKCE (scope: `Mail.Read`, `offline_access`) | OS Keyring | refresh_token |
| Slack | User token OAuth (scope: `channels:history`, `groups:history`, `im:history`) | OS Keyring | manual revoke |
| Discord | Bot token (서버 초대 후) | OS Keyring | permanent |

**토큰 부재 시**: escalation `oauth_token_missing` 발화 + 사용자 재인증 요구 (§6)

### §4.4 스레드 재조립 알고리즘

```python
def rebuild_thread(msgs: list[CanonicalMessage]) -> list[Thread]:
    """
    provider별 단서:
      - Gmail: References + In-Reply-To 헤더 (RFC 2822)
      - Outlook: conversationId + parentId
      - Slack: thread_ts (==ts 면 parent)
      - Discord: message_reference.message_id
    공통 fallback: 동일 subject + 60분 창 + 동일 참여자 부분집합
    """
    graph = build_reply_dag(msgs)
    threads = weakly_connected_components(graph)
    # 시간순 정렬
    for th in threads:
        th.sort(key=lambda m: m.sent_at)
    return [Thread(thread_id=t[0].thread_id, messages=t) for t in threads]
```

**시간 복잡도**: DAG 구축 O(m), WCC O(m+e), 정렬 O(k log k). 전체 O(m log m).

### §4.5 지식 추출 전략 (provider별 차등)

| provider | 지식 후보 | 추출 규칙 |
|----------|----------|----------|
| Gmail / Outlook | 본문 + 첨부 | 헤더(수신인/발신인/일자) → `SourceRef` / 본문 요약 3단계 (한줄/문단/구조화) / 일정 자동 추출 |
| Slack (공개 채널) | 스레드 요약 | 반응 ≥ 3 or 답글 ≥ 5 스레드 우선, 코드블록 자동 추출 |
| Slack (DM) | 사용자 명시 opt-in 시에만 | 프라이버시 기본 제외 |
| Discord (서버) | Bot 관리 채널 | 핀 메시지 + 역할 태그 기반 중요도 점수 |

**지식 추출 흐름**:
```python
def extract_from_message(msg: CanonicalMessage) -> list[KnowledgeCandidate]:
    # 0) 프라이버시 게이트
    if msg.provider in (MessageProvider.SLACK, MessageProvider.DISCORD) and msg.is_direct_message:
        if not user_opt_in_check(msg.sender):
            return []
    # 1) 인용/서명 블록 제거
    clean_body = strip_quoted_and_signature(msg.body_text, msg.quoted_snippets)
    # 2) 원자 단위 분해 (문단 + 불릿)
    atoms = atomize(clean_body, max_tokens=280)
    # 3) 카테고리 분류 (LOCK-PKM-08 8종)
    candidates = []
    for atom in atoms:
        cat = classify_category(atom)
        candidates.append(KnowledgeCandidate(
            title=derive_title(atom, max_chars=80),
            content=atom,
            category=cat,
            tags=auto_tag(atom, dimensions=["주제","유형","감정","중요도","프로젝트"]),
            source_ref=SourceRef(
                provider=msg.provider.value,
                message_id=msg.message_id,
                thread_id=msg.thread_id,
                sender=msg.sender,
                sent_at=msg.sent_at,
            ),
            captured_at=datetime.utcnow(),
            confidence=estimate_confidence(atom, cat),
        ))
    # 4) 일정/약속 추출 (NER)
    candidates.extend(extract_events(clean_body, msg.sent_at))
    # 5) 코드 스니펫 추출 (삼중 백틱 / <pre>)
    candidates.extend(extract_code_snippets(msg.body_html or clean_body))
    # 6) 중복 제거 (LOCK-PKM-06)
    candidates = dedupe(candidates, minhash_threshold=0.7, vector_threshold=0.85)
    return candidates
```

### §4.6 증분 동기화

| provider | 증분 단서 | 체크포인트 |
|----------|----------|-----------|
| Gmail | `historyId` + `users.history.list` | 마지막 성공 historyId |
| Outlook | `@odata.deltaLink` + `nextLink` | deltaLink 토큰 |
| Slack | `oldest` 타임스탬프 + `cursor` | 채널별 oldest ts |
| Discord | `after` snowflake | 채널별 마지막 message_id |

**중복 idempotency 키**: `(provider, message_id)` → SQLite `message_idempotency` 테이블. 재실행 시 스킵.

### §4.7 첨부파일 위임

첨부파일은 `document_ingest.md` 파이프라인에 위임한다. 본 문서는 `CanonicalAttachment` 메타만 보유하고 실제 파싱/임베딩은 `document_ingest.md` §E2 가 수행.

---

## §5. Rate Limit / 비용 가드

| provider | 제한 | 대응 |
|----------|------|------|
| Gmail API | 1 billion quota/day, 250 quota/user/sec | 지수 backoff + `quota_remaining` 헤더 모니터링 |
| Microsoft Graph | 10000 req / 10분 / app | 429 응답 시 `Retry-After` 준수 |
| Slack | Tier 3 (50+ req/min) | bucket별 별도 큐 |
| Discord | Per-route 5 req/5s | `X-RateLimit-Reset-After` 준수 |

**일일 비용 상한 (옵션)**:
```python
DAILY_MESSAGE_FETCH_CAP = 5000          # IMPL-DETAIL, 사용자 조정 가능
DAILY_LLM_SUMMARIZATION_CAP_USD = 0.50  # IMPL-DETAIL, 로컬 LLM 우선 정책
```

---

## §6. 에스컬레이션 Pydantic (Phase 3 테스트 대상)

```python
from pydantic import BaseModel, Field, conint
from typing import Literal

class MessageExtractionEscalation(BaseModel):
    provider: Literal["gmail","outlook","slack","discord"]
    severity: Literal["info","warning","error","critical"]
    reason: Literal[
        "oauth_token_missing",
        "oauth_token_revoked",
        "rate_limit_hit_hard",
        "incremental_state_corrupt",
        "attachment_download_failed",
        "privacy_opt_in_missing",
        "dedupe_conflict_unresolved",
    ]
    context: dict = Field(default_factory=dict)
    auto_remediation: bool = False
    requires_user_review: bool = True
    retry_after_seconds: conint(ge=0, le=86400) = 0
```

---

## §7. 로깅 (structured JSON 3-block)

```json
{
  "event": "email_message.fetch_incremental",
  "provider": "gmail",
  "since_state": {"historyId": "4821334"},
  "fetched_count": 47,
  "new_count": 12,
  "duration_ms": 1820
}
```

```json
{
  "event": "email_message.thread_rebuild",
  "provider": "slack",
  "thread_id": "1715000123.000200",
  "message_count": 8,
  "participants": 3,
  "rebuild_duration_ms": 14
}
```

```json
{
  "event": "email_message.knowledge_extracted",
  "provider": "outlook",
  "message_id": "AAMkADE1...",
  "candidate_count": 4,
  "categories": {"decision":1,"reference":2,"concept":1},
  "dedupe_dropped": 2,
  "code_snippets_extracted": 1
}
```

---

## §8. Phase 3 테스트 시나리오 (10건, V1+V2 exit_gate 충족)

| # | 시나리오 | 기대 결과 | LOCK |
|---|---------|----------|------|
| T1 | Gmail 50개 신규 메시지 증분 동기화 | 50개 CanonicalMessage + N개 KnowledgeCandidate | historyId 전이 |
| T2 | Outlook 스레드 3단 답장 | 단일 Thread로 재조립, 시간순 정렬 | §4.4 |
| T3 | Slack 코드블록 포함 메시지 | `category=code_snippet` 후보 생성 | LOCK-PKM-08 |
| T4 | Discord DM + opt-in 미설정 | 0 후보, 경고 로그 | privacy_opt_in_missing |
| T5 | OAuth 토큰 만료 | escalation `oauth_token_revoked` + 재인증 UI | §6 |
| T6 | 동일 내용 ≥0.85 벡터 유사도 중복 | dedupe 드롭 | LOCK-PKM-06 |
| T7 | Gmail 429 응답 | Retry-After 준수 + 지수 backoff | §5 |
| T8 | 첨부파일 3건 이메일 | CanonicalAttachment 3 + document_ingest 위임 | §4.7 |
| T9 | 일정 "내일 2시 회의" 본문 | 자동 event 후보 생성 | NER |
| T10 | 태그 5차원 전수 부여 | 모든 후보에 5 차원 태그 1개 이상 | LOCK-PKM-07 |

---

## §9. LOCK 5필드 매핑표

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-PKM-06 | 중복 감지 임계값 | 기존 명세 §3.3 / 가이드 R-06-1 | MinHash Jaccard ≥ 0.7, 벡터 유사도 ≥ 0.85 | ❌ |
| LOCK-PKM-07 | 태그 분류 체계 | STEP7-M M-011 | 주제/유형/감정/중요도/프로젝트 5차원 | ❌ |
| LOCK-PKM-08 | 지식 카테고리 | 기존 명세 §3.2 | concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark | ❌ |
| LOCK-PKM-04 (참조) | 그래프 노드 타입 | 기존 명세 §4.1 | KnowledgeNote, Tag, Domain, Source, Person | ❌ |
| LOCK-PKM-05 (참조) | 그래프 엣지 타입 | 기존 명세 §4.1 | RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS | ❌ |

---

## §10. 세션 간 cross-check

| V2 피어 | 공유 계약 | 현 상태 |
|---------|-----------|---------|
| `screen_capture.md` (M-004) | `KnowledgeCandidate` 스키마 (§3) | verbatim 동일 |
| `document_ingest.md` (M-003) | `CanonicalAttachment` 위임 | §4.7 계약 |
| `02_knowledge-graph/knowledge_graph_construction.md` | Thread → 그래프 `Source` 매핑 | LOCK-PKM-04/05 준수 |

---

## §11. 자가 체크리스트

- [x] LOCK-PKM-07/08/06 5필드 verbatim 인용 (§2)
- [x] STEP7-M M-006 L114-130 line refs 실측 근거 표기
- [x] KnowledgeCandidate 공통 스키마 출처 표기 (§3)
- [x] 4 provider 어댑터 전수 (§4.1)
- [x] OAuth2 흐름 정의 (§4.3)
- [x] 스레드 재조립 알고리즘 (§4.4)
- [x] 증분 동기화 체크포인트 (§4.6)
- [x] 에스컬레이션 Pydantic (§6)
- [x] 로깅 3-block JSON (§7)
- [x] Phase 3 테스트 시나리오 10건 (§8)
- [x] LOCK 5필드 매핑표 (§9)
- [x] 피어 cross-check (§10)
