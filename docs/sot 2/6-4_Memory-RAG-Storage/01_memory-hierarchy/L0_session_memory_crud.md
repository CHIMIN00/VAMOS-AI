# L0 Session Memory CRUD 사양서

> **Phase**: P1-1 산출물
> **작성일**: 2026-04-13
> **정본 출처**: D2.0-06 §2.1 (L0 정의), D6 MemoryRecordSchema v3.0.0, Part2 V1-P2 항목1
> **권한 체인**: RULE 1.3 > PLAN 3.0 > D2.0-06 (LOCK) > D6 (Schema SOT) > Part2 (IMPL-GUIDE) > 본 문서 (IMPL-DETAIL)

---

## 0. 교차 참조 블록

| 참조 문서 | 역할 | 참조 위치 |
|-----------|------|----------|
| `D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` | DESIGN 정본 — L0 정의, TTL LOCK, §3.2 정책 | §2.1(L121), §2.5.3(L268), §3.2 |
| `D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` | Schema SOT — MemoryRecordSchema v3.0.0 | D6 전체 |
| `VAMOS_구현가이드_PART2_구현단계.md` | IMPL-GUIDE — V1-P2 항목1 L0 CRUD 요건 | L1907, L2004 |
| P0-1: `MemoryRecordSchema.md` | 확정 스키마 20개 필드 | §1.1~§1.4, §1.6 |
| P0-2: `sqlite_ddl.sql` | SQLite DDL — memory_records 테이블 | 전체 |
| 종합계획서 §7.3 | P1-1 작업 정의, LOCK-MR-003/017/018 | L574, L605~639 |
| `CONFLICT_LOG.md` #006 | L0 TTL 표기 모호성 — §2.1+Part2 기준 정본 | #006 |

---

## 1. 개요

### 1.1 목적

L0 Session Memory의 CRUD(Create/Read/Update/Delete) 전 동작을 L3(구현 상세) 수준으로 완성한다.

### 1.2 범위

- L0 전용 접근 레이어: `scope='L0'`, `memory_type='B-4'` 고정
- TTL: `session_end` 또는 `created_at + 30일` 중 먼저 (LOCK-MR-003)
- project_id 격리 (LOCK-MR-017)
- 저장 전 사용자 확인 훅 (LOCK-MR-018)
- 루프 저장 폭주 방지: content_summary에 원문 저장 금지 (LOCK-MR-019)

### 1.3 LOCK 준수 선언

> LOCK-MR-003 (D2.0-06 §2.1 + Part2 L1907): session_end 또는 created_at + 30일 중 먼저
> LOCK-MR-017 (D2.0-06 §1 / RULE 1.3 §7.2): 프로젝트 간 데이터 혼합 금지
> LOCK-MR-018 (RULE 1.3 §7.3): 저장 전 사용자 확인이 기본
> LOCK-MR-019 (D2.0-06 머리글): 반복 루프 중 원문 저장 금지, 요약/메타/링크만 허용
> LOCK-MR-001 (D2.0-06 §2): L0(Session) — 4계층 메모리
> LOCK-MR-002 (D2.0-06 §2 / Part2): B-4 → L0 매핑

---

## 2. 공통 자료 구조

### 2.1 L0MemoryRecord 타입 정의

> P0-1 MemoryRecordSchema §1.1 Required 7 + §1.2 Optional 6 = 13필드 중 L0 관련 서브셋

```python
@dataclass
class L0MemoryRecord:
    """L0 Session Memory 레코드.
    
    scope='L0', memory_type='B-4' 강제.
    P0-1 MemoryRecordSchema Required 7 + Optional 6 기반.
    """
    # === Required 필드 (7개) ===
    record_id: str             # 자동 생성 (UUID v4)
    project_id: str            # LOCK-MR-017: 프로젝트 격리 식별자
    scope: str = "L0"          # LOCK-MR-001: 불변 — 항상 'L0'
    memory_type: str = "B-4"   # LOCK-MR-002: 불변 — 항상 'B-4'
    content_summary: str = ""  # LOCK-MR-019: 원문 금지, 요약/메타/링크만
    created_at: str = ""       # ISO 8601
    policy_decision: str = ""  # allow | restrict | deny (LOCK-MR-015/018)

    # === Optional 필드 (6개) ===
    ttl: str = "session_end"   # LOCK-MR-003: session_end 또는 created_at+30d 중 먼저
    tags: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    masked: bool = False
    activation_state: str = "draft"  # L0에서는 draft→active 자동 전환
    version: str = "v1.0.0"

    # === L0 전용 메타 ===
    session_id: str = ""       # 세션 식별자 (외부 키 — memory_records 테이블 외부)
    expires_at: str = ""       # 계산된 만료 시각 (ISO 8601) — ttl 정책의 실체화
```

### 2.2 L0CrudRequest / L0CrudResponse

```python
@dataclass
class L0CreateRequest:
    """L0 레코드 생성 요청."""
    project_id: str              # 필수
    session_id: str              # 필수
    content_summary: str         # 필수 (원문 금지)
    tags: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    user_confirmed: bool = False # LOCK-MR-018: 사용자 확인 플래그

@dataclass
class L0ReadRequest:
    """L0 레코드 조회 요청."""
    project_id: str              # 필수 (LOCK-MR-017 격리)
    session_id: str              # 필수
    record_id: str | None = None # 특정 레코드 조회 시
    include_expired: bool = False

@dataclass
class L0UpdateRequest:
    """L0 레코드 수정 요청."""
    record_id: str               # 필수
    project_id: str              # 필수 (격리 검증용)
    content_summary: str | None = None  # 수정 대상 (optional)
    tags: list[str] | None = None       # 수정 대상 (optional)
    user_confirmed: bool = False        # LOCK-MR-018

@dataclass
class L0DeleteRequest:
    """L0 레코드 삭제 요청."""
    record_id: str               # 필수
    project_id: str              # 필수 (격리 검증용)
    hard_delete: bool = False    # True=물리 삭제, False=soft-delete(deprecated)

@dataclass
class L0CrudResponse:
    """CRUD 응답 공통 구조."""
    success: bool
    record_id: str | None = None
    error_code: str | None = None  # §6 에러 코드 참조
    error_message: str | None = None
    data: L0MemoryRecord | list[L0MemoryRecord] | None = None
    trace_id: str = ""             # R-01-7 추적 ID
```

---

## 3. L0 CRUD 상세 구현

### 3.1 Create — L0 레코드 생성

**흐름**:

```
[요청 수신] → [필수 필드 검증] → [LOCK-MR-018 사용자 확인 체크]
  → [LOCK-MR-019 원문 검사] → [policy_decision 검증]
  → [TTL 계산 (LOCK-MR-003)] → [INSERT] → [응답 반환]
```

**의사코드**:

```python
def create_l0_record(req: L0CreateRequest, db: Connection) -> L0CrudResponse:
    """L0 Session Memory 레코드 생성.
    
    시간복잡도: O(1) — 단일 INSERT
    LOCK 참조: LOCK-MR-003, LOCK-MR-017, LOCK-MR-018, LOCK-MR-019
    """
    trace_id = generate_trace_id()
    
    # 1. 필수 필드 검증
    if not req.project_id:
        # LOCK-MR-017: project_id 없는 요청 거부
        return L0CrudResponse(
            success=False, error_code="L0_ERR_001",
            error_message="project_id is required (LOCK-MR-017)",
            trace_id=trace_id
        )
    if not req.session_id:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_002",
            error_message="session_id is required for L0 scope",
            trace_id=trace_id
        )
    if not req.content_summary:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_003",
            error_message="content_summary is required",
            trace_id=trace_id
        )
    
    # 2. LOCK-MR-018: 저장 전 사용자 확인 체크
    if not req.user_confirmed:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_004",
            error_message="user_confirmed=True required (LOCK-MR-018)",
            trace_id=trace_id
        )
    
    # 3. LOCK-MR-019: 루프 저장 폭주 방지 — 원문 길이 체크
    if len(req.content_summary) > MAX_CONTENT_SUMMARY_LENGTH:  # 상수: 2000자
        return L0CrudResponse(
            success=False, error_code="L0_ERR_005",
            error_message="content_summary exceeds limit (LOCK-MR-019: summary only)",
            trace_id=trace_id
        )
    
    # 4. policy_decision 결정 — 외부 PolicyCheck 호출 결과 수신
    policy_result = invoke_policy_check(
        project_id=req.project_id,
        content=req.content_summary,
        action="STORE"
    )  # D2.0-07 PolicyCheck 트리거 (c) 저장/인덱싱 전
    
    if policy_result.decision == "deny":
        # LOCK-MR-015: deny 시 저장 금지
        log_audit(action="CREATE_DENIED", project_id=req.project_id,
                  session_id=req.session_id, reason="policy_deny",
                  trace_id=trace_id)
        return L0CrudResponse(
            success=False, error_code="L0_ERR_006",
            error_message="policy_decision=deny: storage forbidden (LOCK-MR-015)",
            trace_id=trace_id
        )
    
    # 5. TTL 계산 (LOCK-MR-003)
    now = utc_now_iso8601()
    session_end_time = get_session_end_time(req.session_id)  # 세션 종료 예정 시각
    created_plus_30d = add_days(now, 30)
    
    if session_end_time and session_end_time < created_plus_30d:
        expires_at = session_end_time
        ttl_value = "session_end"
    else:
        expires_at = created_plus_30d
        ttl_value = "30d"
    
    # 6. 레코드 구성
    # session_id를 tags에 포함 — DDL에 session_id 컬럼 없으므로 (§4.3 설계 결정)
    effective_tags = list(req.tags) + [f"session:{req.session_id}"]
    
    record = L0MemoryRecord(
        record_id=generate_uuid_v4(),
        project_id=req.project_id,
        scope="L0",               # 불변
        memory_type="B-4",        # 불변 (LOCK-MR-002)
        content_summary=req.content_summary,
        created_at=now,
        policy_decision=policy_result.decision,  # allow 또는 restrict
        ttl=ttl_value,
        tags=effective_tags,
        source_refs=req.source_refs,
        masked=(policy_result.decision == "restrict"),
        activation_state="active",  # L0는 생성 즉시 active
        session_id=req.session_id,
        expires_at=expires_at
    )
    
    # 7. restrict인 경우 마스킹 처리
    if policy_result.decision == "restrict":
        record.content_summary = apply_pii_masking(record.content_summary)
        record.masked = True
    
    # 8. INSERT
    db.execute("""
        INSERT INTO memory_records (
            record_id, project_id, scope, memory_type,
            content_summary, created_at, policy_decision,
            ttl, tags, source_refs, masked,
            activation_state, version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.record_id, record.project_id, record.scope,
        record.memory_type, record.content_summary, record.created_at,
        record.policy_decision, record.ttl,
        json.dumps(record.tags), json.dumps(record.source_refs),
        1 if record.masked else 0, record.activation_state, record.version
    ))
    db.commit()
    
    # 9. 구조화 로깅 (R-01-7)
    emit_structured_log({
        "event": "L0_RECORD_CREATED",
        "trace_id": trace_id,
        "context": {
            "project_id": record.project_id,
            "session_id": record.session_id,
            "scope": "L0",
            "memory_type": "B-4"
        },
        "result": {
            "record_id": record.record_id,
            "policy_decision": record.policy_decision,
            "ttl": record.ttl,
            "expires_at": record.expires_at
        },
        "error": {},
        "recovery": {}
    })
    
    return L0CrudResponse(
        success=True, record_id=record.record_id,
        data=record, trace_id=trace_id
    )
```

### 3.2 Read — L0 레코드 조회

**흐름**:

```
[요청 수신] → [project_id 격리 검증 (LOCK-MR-017)]
  → [scope='L0' 필터] → [TTL 만료 필터 (lazy expiration)]
  → [결과 반환]
```

**의사코드**:

```python
def read_l0_records(req: L0ReadRequest, db: Connection) -> L0CrudResponse:
    """L0 Session Memory 레코드 조회.
    
    시간복잡도: O(N) — N=해당 session/project의 L0 레코드 수
    LOCK 참조: LOCK-MR-017
    인덱스 활용: idx_memory_scope_project (scope, project_id)
    """
    trace_id = generate_trace_id()
    
    # 1. LOCK-MR-017: project_id 필수
    if not req.project_id:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_001",
            error_message="project_id is required (LOCK-MR-017)",
            trace_id=trace_id
        )
    if not req.session_id:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_002",
            error_message="session_id is required for L0 scope",
            trace_id=trace_id
        )
    
    # 2. 쿼리 구성 — scope='L0' 고정 + project_id 격리
    if req.record_id:
        # 특정 레코드 조회
        rows = db.execute("""
            SELECT * FROM memory_records
            WHERE record_id = ? AND project_id = ? AND scope = 'L0'
        """, (req.record_id, req.project_id)).fetchall()
    else:
        # 세션 전체 조회 — session_id를 tags 기반으로 필터 (§4.3 설계 결정)
        rows = db.execute("""
            SELECT * FROM memory_records
            WHERE project_id = ? AND scope = 'L0'
            AND tags LIKE ?
            ORDER BY created_at DESC
        """, (req.project_id, f'%"session:{req.session_id}"%')).fetchall()
    
    # 3. Lazy expiration: TTL 만료 레코드 필터
    now = utc_now_iso8601()
    results = []
    expired_ids = []
    for row in rows:
        expires_at = calculate_expires_at(row["created_at"], row["ttl"])
        if not req.include_expired and expires_at and now > expires_at:
            expired_ids.append(row["record_id"])
            continue
        results.append(row_to_l0_record(row))
    
    # 4. 만료 레코드 백그라운드 정리 (lazy expiration)
    if expired_ids:
        schedule_background_cleanup(expired_ids, trace_id)
    
    emit_structured_log({
        "event": "L0_RECORDS_READ",
        "trace_id": trace_id,
        "context": {
            "project_id": req.project_id,
            "session_id": req.session_id,
            "scope": "L0"
        },
        "result": {
            "count": len(results),
            "expired_filtered": len(expired_ids)
        },
        "error": {},
        "recovery": {}
    })
    
    return L0CrudResponse(
        success=True, data=results, trace_id=trace_id
    )
```

### 3.3 Update — L0 레코드 수정

**흐름**:

```
[요청 수신] → [record_id + project_id 격리 검증]
  → [불변 필드 보호 (scope, memory_type)]
  → [LOCK-MR-018 사용자 확인] → [UPDATE] → [응답]
```

**불변 필드 정책**:

| 필드 | 수정 가능 | 근거 |
|------|----------|------|
| `record_id` | 불가 | PK |
| `project_id` | 불가 | LOCK-MR-017 격리 |
| `scope` | 불가 | L0 고정 (승격 시 새 레코드 생성) |
| `memory_type` | 불가 | B-4 고정 (LOCK-MR-002) |
| `created_at` | 불가 | 생성 시각 불변 |
| `content_summary` | **가능** | 요약 갱신 허용 (LOCK-MR-019 제약 내) |
| `tags` | **가능** | 태그 추가/제거 |
| `policy_decision` | 불가 | PolicyCheck 재실행으로만 변경 |
| `activation_state` | **가능** | active → deprecated 전환 (soft-delete용) |

**의사코드**:

```python
def update_l0_record(req: L0UpdateRequest, db: Connection) -> L0CrudResponse:
    """L0 Session Memory 레코드 수정.
    
    시간복잡도: O(1) — 단일 UPDATE
    LOCK 참조: LOCK-MR-017, LOCK-MR-018, LOCK-MR-019
    """
    trace_id = generate_trace_id()
    
    # 1. project_id 필수 (LOCK-MR-017)
    if not req.project_id or not req.record_id:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_001",
            error_message="project_id and record_id required",
            trace_id=trace_id
        )
    
    # 2. 기존 레코드 조회 + 격리 검증
    existing = db.execute("""
        SELECT * FROM memory_records
        WHERE record_id = ? AND project_id = ? AND scope = 'L0'
    """, (req.record_id, req.project_id)).fetchone()
    
    if not existing:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_007",
            error_message="record not found or project_id mismatch",
            trace_id=trace_id
        )
    
    # 3. LOCK-MR-018: 사용자 확인
    if not req.user_confirmed:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_004",
            error_message="user_confirmed=True required (LOCK-MR-018)",
            trace_id=trace_id
        )
    
    # 4. 수정 가능 필드만 반영
    updates = {}
    if req.content_summary is not None:
        # LOCK-MR-019 체크
        if len(req.content_summary) > MAX_CONTENT_SUMMARY_LENGTH:
            return L0CrudResponse(
                success=False, error_code="L0_ERR_005",
                error_message="content_summary exceeds limit (LOCK-MR-019)",
                trace_id=trace_id
            )
        updates["content_summary"] = req.content_summary
    
    if req.tags is not None:
        updates["tags"] = json.dumps(req.tags)
    
    if not updates:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_008",
            error_message="no updatable fields provided",
            trace_id=trace_id
        )
    
    # 5. updated_at 추가 (DDL에 없으므로 content_summary 메타에 포함하거나 별도 컬럼 추가 필요)
    # V1 구현: version 증분으로 추적
    new_version = increment_version(existing["version"])
    updates["version"] = new_version
    
    # 6. UPDATE 실행 (낙관적 동시성 제어 — 읽은 version으로 가드)
    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [req.record_id, req.project_id, existing["version"]]
    cur = db.execute(f"""
        UPDATE memory_records SET {set_clause}
        WHERE record_id = ? AND project_id = ? AND scope = 'L0' AND version = ?
    """, values)
    if cur.rowcount == 0:
        raise L0MemoryError("L0_ERR_OCC", "동시 수정 충돌 (version mismatch) — 재조회 후 재시도")
    db.commit()
    
    emit_structured_log({
        "event": "L0_RECORD_UPDATED",
        "trace_id": trace_id,
        "context": {
            "project_id": req.project_id,
            "record_id": req.record_id,
            "scope": "L0"
        },
        "result": {
            "updated_fields": list(updates.keys()),
            "new_version": new_version
        },
        "error": {},
        "recovery": {}
    })
    
    return L0CrudResponse(
        success=True, record_id=req.record_id, trace_id=trace_id
    )
```

### 3.4 Delete — L0 레코드 삭제

**삭제 전략 결정**:

| 전략 | 동작 | 사용 시점 |
|------|------|----------|
| **Soft-delete** | `activation_state` → `deprecated` | 사용자 명시 삭제 요청 (복구 가능성 유지) |
| **Hard-delete** | `DELETE FROM memory_records` | TTL 만료 시 (P0-2 §8 설계 결정 준수) |
| **감사 로그** | 삭제 전 memory_audit_log INSERT | 양쪽 모두 (D2.0-06 L313) |

**의사코드**:

```python
def delete_l0_record(req: L0DeleteRequest, db: Connection) -> L0CrudResponse:
    """L0 Session Memory 레코드 삭제.
    
    시간복잡도: O(1) — 단일 UPDATE 또는 DELETE
    LOCK 참조: LOCK-MR-017
    """
    trace_id = generate_trace_id()
    
    # 1. project_id 격리 검증 (LOCK-MR-017)
    if not req.project_id or not req.record_id:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_001",
            error_message="project_id and record_id required",
            trace_id=trace_id
        )
    
    # 2. 기존 레코드 확인
    existing = db.execute("""
        SELECT * FROM memory_records
        WHERE record_id = ? AND project_id = ? AND scope = 'L0'
    """, (req.record_id, req.project_id)).fetchone()
    
    if not existing:
        return L0CrudResponse(
            success=False, error_code="L0_ERR_007",
            error_message="record not found or project_id mismatch",
            trace_id=trace_id
        )
    
    # 3. 감사 로그 기록 (삭제 전)
    log_audit(
        action="DELETE_INITIATED",
        project_id=req.project_id,
        record_id=req.record_id,
        hard_delete=req.hard_delete,
        trace_id=trace_id
    )
    
    # 4. 삭제 실행
    if req.hard_delete:
        # TTL 만료 또는 명시적 hard-delete 요청
        db.execute("""
            DELETE FROM memory_records
            WHERE record_id = ? AND project_id = ? AND scope = 'L0'
        """, (req.record_id, req.project_id))
    else:
        # Soft-delete: activation_state → deprecated
        db.execute("""
            UPDATE memory_records SET activation_state = 'deprecated'
            WHERE record_id = ? AND project_id = ? AND scope = 'L0'
        """, (req.record_id, req.project_id))
    
    db.commit()
    
    emit_structured_log({
        "event": "L0_RECORD_DELETED",
        "trace_id": trace_id,
        "context": {
            "project_id": req.project_id,
            "record_id": req.record_id,
            "scope": "L0",
            "delete_type": "hard" if req.hard_delete else "soft"
        },
        "result": {
            "deleted": True
        },
        "error": {},
        "recovery": {}
    })
    
    return L0CrudResponse(
        success=True, record_id=req.record_id, trace_id=trace_id
    )
```

---

## 4. TTL 만료 처리

### 4.1 TTL 정책 (LOCK-MR-003)

> LOCK-MR-003 (D2.0-06 §2.1 + Part2 L1907): session_end 또는 created_at + 30일 중 먼저
> CONFLICT_LOG #006: D2.0-06 §2.5.3(L268)은 "즉시 만료"로 약식 표기 — §2.1+Part2 기준 정본

| 만료 조건 | 트리거 | 동작 |
|-----------|--------|------|
| `session_end` 이벤트 수신 | 세션 종료 콜백 | 해당 세션의 모든 L0 레코드 hard-delete |
| `created_at + 30일` 초과 | 주기적 sweep (1시간/1일) | 대상 L0 레코드 hard-delete |
| 조회 시 만료 발견 | Lazy expiration | 결과에서 제외 + 백그라운드 삭제 스케줄 |

### 4.2 TTL 만료 sweep 구현

```python
def sweep_expired_l0_records(db: Connection) -> int:
    """L0 TTL 만료 레코드 일괄 삭제.
    
    시간복잡도: O(M) — M=만료 대상 레코드 수
    실행 주기: 1시간 (V1 기본) — 설정 가능
    인덱스 활용: idx_memory_scope + idx_memory_created_at
    """
    trace_id = generate_trace_id()
    now = utc_now_iso8601()
    threshold = subtract_days(now, 30)
    
    # 1. 만료 대상 조회 (감사 로그용)
    expired = db.execute("""
        SELECT record_id, project_id FROM memory_records
        WHERE scope = 'L0' AND created_at < ?
    """, (threshold,)).fetchall()
    
    # 2. 감사 로그 일괄 기록
    for row in expired:
        log_audit(
            action="TTL_EXPIRED_DELETE",
            project_id=row["project_id"],
            record_id=row["record_id"],
            trace_id=trace_id
        )
    
    # 3. 일괄 삭제
    result = db.execute("""
        DELETE FROM memory_records
        WHERE scope = 'L0' AND created_at < ?
    """, (threshold,))
    db.commit()
    
    deleted_count = result.rowcount
    
    emit_structured_log({
        "event": "L0_TTL_SWEEP",
        "trace_id": trace_id,
        "context": {"scope": "L0", "threshold": threshold},
        "result": {"deleted_count": deleted_count},
        "error": {},
        "recovery": {}
    })
    
    return deleted_count


def on_session_end(session_id: str, project_id: str, db: Connection) -> int:
    """세션 종료 이벤트 핸들러 — 해당 세션 L0 레코드 삭제.
    
    시간복잡도: O(K) — K=해당 세션의 L0 레코드 수
    LOCK-MR-003: session_end 조건
    """
    trace_id = generate_trace_id()
    
    # session_id는 memory_records 테이블 외부 메타이므로
    # 애플리케이션 레벨에서 session_id → record_id 매핑 유지 필요
    # 또는 tags에 session_id를 JSON 포함하여 조회
    
    expired = db.execute("""
        SELECT record_id FROM memory_records
        WHERE scope = 'L0' AND project_id = ?
        AND tags LIKE ?
    """, (project_id, f'%"session:{session_id}"%')).fetchall()
    
    for row in expired:
        log_audit(
            action="SESSION_END_DELETE",
            project_id=project_id,
            record_id=row["record_id"],
            session_id=session_id,
            trace_id=trace_id
        )
    
    result = db.execute("""
        DELETE FROM memory_records
        WHERE scope = 'L0' AND project_id = ?
        AND EXISTS (SELECT 1 FROM json_each(memory_records.tags) WHERE value = ?)
    """, (project_id, f'session:{session_id}'))
    db.commit()
    
    emit_structured_log({
        "event": "L0_SESSION_END_CLEANUP",
        "trace_id": trace_id,
        "context": {
            "session_id": session_id,
            "project_id": project_id,
            "scope": "L0"
        },
        "result": {"deleted_count": result.rowcount},
        "error": {},
        "recovery": {}
    })
    
    return result.rowcount
```

### 4.3 session_id 추적 설계 결정

> **문제**: P0-2 DDL의 `memory_records` 테이블에 `session_id` 컬럼이 없음.
> **결정**: V1에서는 `tags` JSON 배열에 `"session:<session_id>"` 태그를 포함하여 세션 식별.
> **근거**: DDL 스키마 변경 최소화 (P0-2 산출물 보호) + V2에서 전용 컬럼 추가 가능.
> **대안**: ALTER TABLE ADD COLUMN session_id TEXT — V2 마이그레이션 시 적용 권고.

---

## 5. 사용자 확인 훅 (LOCK-MR-018)

### 5.1 훅 포인트 정의

> LOCK-MR-018 (RULE 1.3 §7.3): 저장 전 사용자 확인이 기본

| CRUD 작업 | 훅 필요 | 설명 |
|-----------|---------|------|
| **Create** | 필수 | `user_confirmed=True` 필수. False 시 L0_ERR_004 |
| **Read** | 불필요 | 조회는 데이터 변경 없음 |
| **Update** | 필수 | content_summary/tags 변경 시 확인 필요 |
| **Delete (soft)** | 선택적 | soft-delete는 복구 가능 — 확인 권고 |
| **Delete (hard/TTL)** | 불필요 | TTL 만료는 시스템 자동 처리 |

### 5.2 훅 인터페이스

```python
class UserConfirmationHook:
    """저장 전 사용자 확인 인터페이스.
    
    6-1 UI-UX 도메인과의 경계:
    - 6-4(본 도메인): 훅 포인트 정의 + 확인 여부 검증
    - 6-1(UI-UX): 확인 모달 UI 구현 + user_confirmed 플래그 전달
    """
    
    @abstractmethod
    def request_confirmation(
        self,
        project_id: str,
        action: str,         # "CREATE" | "UPDATE" | "DELETE"
        content_preview: str,  # 요약 미리보기 (원문 아님)
        metadata: dict
    ) -> bool:
        """사용자 확인 요청. True=확인, False=취소."""
        ...
    
    @abstractmethod
    def get_confirmation_status(self, confirmation_id: str) -> str:
        """비동기 확인 상태 조회. pending | confirmed | cancelled | expired."""
        ...
```

### 5.3 자동 확인 예외 (V1)

| 시나리오 | 자동 확인 | 근거 |
|----------|----------|------|
| 세션 종료 시 자동 요약 저장 (L0→L1 승격 전처리) | 허용 | 세션 시작 시 일괄 동의로 처리 |
| TTL 만료 삭제 | 허용 | 시스템 정책 (LOCK-MR-003) |
| API 호출 시 명시적 `user_confirmed=True` | 허용 | 클라이언트 책임 |

---

## 6. 에러 처리 정책

### 6.1 에러 코드 표

| error_code | 설명 | recoverable | 처리 |
|------------|------|-------------|------|
| `L0_ERR_001` | project_id 누락 (LOCK-MR-017) | Yes | 클라이언트에 project_id 재요청 |
| `L0_ERR_002` | session_id 누락 | Yes | 클라이언트에 session_id 재요청 |
| `L0_ERR_003` | content_summary 누락 | Yes | 클라이언트에 content 재요청 |
| `L0_ERR_004` | 사용자 확인 미완료 (LOCK-MR-018) | Yes | 확인 훅 재실행 |
| `L0_ERR_005` | content_summary 길이 초과 (LOCK-MR-019) | Yes | 요약 축소 후 재시도 |
| `L0_ERR_006` | policy_decision=deny (LOCK-MR-015) | No | 저장 불가 — 감사 로그만 기록 |
| `L0_ERR_007` | 레코드 미존재 또는 project_id 불일치 | Yes | record_id/project_id 확인 후 재시도 |
| `L0_ERR_008` | 수정 가능 필드 없음 | Yes | 요청 재구성 |
| `L0_ERR_009` | DB 쓰기 실패 (SQLite lock) | Yes | 재시도 (V1 단일 writer — 최대 3회, 간격 100ms) |
| `L0_ERR_010` | PolicyCheck 서비스 호출 실패 | Yes | 재시도 2회 → 실패 시 에스컬레이션 |

### 6.2 에스컬레이션 흐름

> 에스컬레이션 경로: I-20 경유 (R-01-8)

```python
@dataclass
class EscalationPayload:
    """에스컬레이션 페이로드 구조.
    
    최소 필드: source, error_code, original_request, partial_result,
              retry_count, timestamp (P1-4/P1-5/P1-6 정합).
    """
    escalation_id: str          # 고유 ID
    trace_id: str               # 원본 요청 추적 ID
    source: str = "L0_session_memory_crud"  # 발생 모듈 (source 표준 필드)
    source_domain: str = "6-4"  # 발생 도메인
    error_code: str = ""        # L0_ERR_XXX
    error_message: str = ""
    severity: str = "HIGH"      # LOW | MEDIUM | HIGH | CRITICAL
    original_request: dict = field(default_factory=dict)  # 원본 요청 정보 (project_id, session_id 등)
    partial_result: dict = field(default_factory=dict)     # 부분 결과 (있는 경우)
    retry_count: int = 0        # 재시도 횟수
    context: dict = field(default_factory=dict)  # 추가 컨텍스트
    timestamp: str = ""         # ISO 8601
    recommended_action: str = ""  # 권고 조치
```

**에스컬레이션 트리거 조건**:

| 조건 | severity | 권고 조치 |
|------|----------|----------|
| PolicyCheck 서비스 3회 연속 실패 | HIGH | PolicyCheck 서비스 상태 점검 |
| DB 쓰기 실패 3회 연속 | CRITICAL | SQLite 파일 잠금/무결성 점검 |
| 비정상적 deny 비율 (>50% in 1h) | MEDIUM | 정책 규칙 점검 |

---

## 7. 로깅 포맷 (R-01-7)

> 모든 CRUD 작업에 structured JSON 로그 출력.
> 중첩 구조: error{}, context{}, recovery{}, trace_id 필수.

### 7.1 로그 스키마

```json
{
  "timestamp": "2026-04-13T09:00:00.000Z",
  "level": "INFO",
  "event": "L0_RECORD_CREATED",
  "trace_id": "tr-abc123-def456",
  "context": {
    "project_id": "proj-001",
    "session_id": "sess-abc",
    "scope": "L0",
    "memory_type": "B-4",
    "caller": "api.v1.memory.create"
  },
  "result": {
    "record_id": "rec-xyz789",
    "policy_decision": "allow",
    "ttl": "session_end",
    "expires_at": "2026-04-13T18:00:00.000Z"
  },
  "error": {
    "code": null,
    "message": null,
    "stack": null
  },
  "recovery": {
    "retry_count": 0,
    "fallback_used": false,
    "escalated": false
  }
}
```

### 7.2 에러 시 로그 예시

```json
{
  "timestamp": "2026-04-13T09:01:00.000Z",
  "level": "ERROR",
  "event": "L0_CREATE_FAILED",
  "trace_id": "tr-abc123-ghi789",
  "context": {
    "project_id": "proj-001",
    "session_id": "sess-abc",
    "scope": "L0",
    "memory_type": "B-4",
    "caller": "api.v1.memory.create"
  },
  "result": {},
  "error": {
    "code": "L0_ERR_006",
    "message": "policy_decision=deny: storage forbidden (LOCK-MR-015)",
    "stack": null
  },
  "recovery": {
    "retry_count": 0,
    "fallback_used": false,
    "escalated": false,
    "action": "audit_log_only"
  }
}
```

---

## 8. 복구 전략

### 8.1 Phase별 복구 흐름

```
[Phase 1 — L0 CRUD 단독 동작]

  실패 유형          → 1차 복구              → 2차 복구              → 최종
  ─────────────────────────────────────────────────────────────────────────
  DB Lock            → 100ms 후 재시도(3회)  → WAL checkpoint       → 에스컬레이션
  PolicyCheck 실패   → 200ms 후 재시도(2회)  → allow 기본값 금지*   → 에스컬레이션
  content 검증 실패  → 클라이언트 재요청     → —                    → L0_ERR_003/005
  TTL sweep 실패     → 다음 주기에 재실행    → 수동 sweep 트리거    → 에스컬레이션

  * PolicyCheck 실패 시 allow 기본값 사용 금지 — deny-by-default 정책
```

### 8.2 다운그레이드 시 confidence penalty 표

| 다운그레이드 사유 | confidence penalty | 설명 |
|------------------|-------------------|------|
| PolicyCheck 서비스 불가 → 저장 보류 | -1.0 (저장 불가) | deny-by-default |
| DB Lock → 재시도 성공 | 0.0 (페널티 없음) | 정상 복구 |
| TTL sweep 지연 (>24h) | -0.1 | 만료 레코드 존재 가능 — 조회 시 lazy filter 적용 |
| 세션 종료 이벤트 누락 → 30일 TTL fallback | -0.05 | 안전장치 동작 중 |

---

## 9. 단위 테스트

### 9.1 CRUD 4경로 테스트

| # | 테스트 케이스 | 검증 항목 | 예상 결과 |
|---|-------------|----------|----------|
| T-01 | Create 정상 — allow | scope=L0, memory_type=B-4 강제 확인 | 성공, record_id 반환 |
| T-02 | Create 정상 — restrict | masked=True, content 마스킹 확인 | 성공, masked=1 |
| T-03 | Create 실패 — deny | policy_decision=deny 시 저장 거부 | L0_ERR_006 |
| T-04 | Create 실패 — project_id 누락 | LOCK-MR-017 위반 | L0_ERR_001 |
| T-05 | Create 실패 — user_confirmed=False | LOCK-MR-018 위반 | L0_ERR_004 |
| T-06 | Read 정상 — 세션 전체 조회 | project_id 격리 + scope=L0 + session_id(tags) 필터 | 해당 세션 레코드만 반환 |
| T-07 | Read 정상 — 특정 record_id | record_id + project_id 일치 | 단일 레코드 반환 |
| T-08 | Read 격리 위반 — 다른 project_id | LOCK-MR-017 | 빈 결과 (에러 아님) |
| T-09 | Update 정상 — content_summary 변경 | 불변 필드 미변경 확인 | 성공, version 증가 |
| T-10 | Update 실패 — scope 변경 시도 | 불변 필드 보호 | 거부 (scope 필드 미포함) |
| T-11 | Delete soft — activation_state 변경 | deprecated 전환 확인 | 성공 |
| T-12 | Delete hard — 물리 삭제 | 레코드 존재 여부 | 성공, 조회 불가 |

### 9.2 TTL 만료 테스트

| # | 테스트 케이스 | 검증 항목 | 예상 결과 |
|---|-------------|----------|----------|
| T-13 | TTL 만료 — created_at + 30일 초과 | sweep 후 삭제 확인 | hard-delete 완료 |
| T-14 | TTL 만료 — session_end 이벤트 | on_session_end 호출 후 삭제 | hard-delete 완료 |
| T-15 | TTL 미만료 — 30일 이내 | sweep 후 존재 확인 | 레코드 유지 |
| T-16 | Lazy expiration — 조회 시 만료 필터 | 만료 레코드 결과 제외 | 미반환 + 삭제 스케줄 |

### 9.3 project_id 격리 위반 테스트

| # | 테스트 케이스 | 검증 항목 | 예상 결과 |
|---|-------------|----------|----------|
| T-17 | project_id 없이 Create | LOCK-MR-017 | L0_ERR_001 |
| T-18 | project_id=A로 생성, project_id=B로 Read | 격리 | 빈 결과 |
| T-19 | project_id=A로 생성, project_id=B로 Update | 격리 | L0_ERR_007 |
| T-20 | project_id=A로 생성, project_id=B로 Delete | 격리 | L0_ERR_007 |

### 9.4 session_id 추적 테스트

| # | 테스트 케이스 | 검증 항목 | 예상 결과 |
|---|-------------|----------|----------|
| T-21 | Create 시 tags에 session:<id> 자동 삽입 | §4.3 설계 결정 | tags JSON에 "session:sess-abc" 포함 |
| T-22 | Read 세션 전체 조회 — 다른 session_id | session_id 필터 | 빈 결과 |
| T-23 | on_session_end 호출 — 해당 세션 삭제 | §4.2 LOCK-MR-003 | 해당 세션 레코드 전부 hard-delete |

---

## 10. Phase 2 통합 테스트 시나리오

> Phase 2 진입 후 검증 대상. 본 문서에서는 힌트로 기록.

| # | 시나리오 | 관련 세션 | 검증 포인트 |
|---|---------|----------|------------|
| P2-T-01 | L0 Create 후 L0→L1 승격 흐름 | P1-2, P1-8 | 세션 종료 시 자동 요약 → L1 생성 |
| P2-T-02 | L0 + Chroma 벡터 삽입 연동 | P1-3 | allow/restrict 시 벡터 삽입, deny 시 절대 금지 |
| P2-T-03 | L0 CRUD + PII 마스킹 E2E | P1-7 | restrict → content 마스킹 → 벡터 마스킹 |
| P2-T-04 | L0 TTL sweep + 감사 로그 | P1-6 | 삭제 전 audit_log INSERT 확인 |
| P2-T-05 | L0 + Semantic Cache 히트 시 생성 건너뛰기 | P1-5 | cosine >= 0.95 시 중복 L0 생성 억제 |
| P2-T-06 | L0 CRUD 동시성 — 단일 writer 패턴 | P2-1 (Qdrant) | SQLite WAL 모드에서 동시 Read + 순차 Write |
| P2-T-07 | L0 + 6-Stage RAG Pipeline Stage 1 (Collect) | P1-10 | L0 레코드가 RAG 입력으로 수집되는 흐름 |
| P2-T-08 | L0 + GraphRAG JSON 노드 생성 | P1-4 | L0 메모리가 그래프 노드로 등록되는 경로 |
| P2-T-09 | L0 project_id 격리 + 크로스 프로젝트 검색 금지 | P2 전체 | 다른 project의 L0 데이터 접근 불가 |
| P2-T-10 | L0 대화 내보내기/가져오기 | P1-6 | L0 레코드 JSONL export → import 후 정합성 |
| P2-T-11 | L0 + Memory Decay (B-3) 연동 | P1-8 | L0 decay 비적용 확인 (B-4는 decay 대상 외) |
| P2-T-12 | L0 + DCL 기초 (Deny 필터) | P1-9 | DCL deny 판정 레코드의 L0 저장 차단 |

---

## 11. 세션 간 인터페이스 정합

### 11.1 P1-2 (L1 Project Memory) 접점

| 접점 | 본 세션 (P1-1) | P1-2 | 정합 방법 |
|------|---------------|------|----------|
| L0→L1 승격 | L0 레코드 생성/관리 | L1 레코드 수신 | 세션 종료 시 L0 요약 → L1 Create 호출 |
| project_id 격리 | LOCK-MR-017 검증 | LOCK-MR-017 동일 검증 | 동일 project_id 가드 로직 공유 |
| MemoryRecordSchema | P0-1 정본 참조 | P0-1 정본 참조 | 스키마 동일 |

### 11.2 P1-3 (Chroma Vector DB) 접점

| 접점 | 본 세션 (P1-1) | P1-3 | 정합 방법 |
|------|---------------|------|----------|
| 벡터 삽입 | policy_decision 판정 후 allow/restrict만 허용 | upsert 메서드 (LOCK-MR-014) | P1-1 → P1-3 upsert 호출 경로 |
| deny 삽입 금지 | L0_ERR_006 반환 | upsert 전 policy_decision 체크 | LOCK-MR-015 양측 준수 |

### 11.3 P1-7 (PII 마스킹) 접점

| 접점 | 본 세션 (P1-1) | P1-7 | 정합 방법 |
|------|---------------|------|----------|
| restrict 마스킹 | Create §3.1 step 7에서 `apply_pii_masking()` 호출 | 마스킹 함수 제공 | P1-7 마스킹 API 인터페이스 사용 |

---

## 12. LOCK-MR 준수 검증 요약

| LOCK-MR | 항목 | 본 문서 적용 위치 | 검증 |
|---------|------|-----------------|------|
| LOCK-MR-001 | 4계층 메모리 | §1.2 — scope='L0' 고정 | PASS |
| LOCK-MR-002 | B↔L 매핑 | §1.2 — memory_type='B-4' 고정 | PASS |
| LOCK-MR-003 | L0 TTL | §4.1 — session_end 또는 created_at+30d 중 먼저 | PASS |
| LOCK-MR-015 | Deny 벡터 삽입 금지 | §3.1 step 4 — deny 시 저장 자체 차단 | PASS |
| LOCK-MR-017 | project_id 격리 | §3.1~3.4 전체 — 모든 CRUD에 project_id 필수 | PASS |
| LOCK-MR-018 | 저장 전 사용자 확인 | §5 — Create/Update 시 user_confirmed 필수 | PASS |
| LOCK-MR-019 | 루프 저장 폭주 방지 | §3.1 step 3 — content_summary 길이 제한 | PASS |

---

## 13. P1-1 검증 체크리스트

| # | 검증 항목 | 결과 | 근거 |
|---|----------|------|------|
| 1 | L0 Create 시 scope=L0, memory_type=B-4 강제 | PASS | §3.1 step 6 |
| 2 | TTL 계산이 LOCK-MR-003 준수 | PASS | §4.1 |
| 3 | project_id 없는 요청 거부 (LOCK-MR-017) | PASS | §3.1 step 1, §6.1 L0_ERR_001 |
| 4 | CRUD 4개 경로 + 격리 + session 추적 단위 테스트 | PASS | §9.1 T-01~T-12, §9.3 T-17~T-20, §9.4 T-21~T-23 |
| 5 | LOCK-MR-018 저장 전 사용자 확인 훅 포인트 동작 | PASS | §5 |
| 6 | I-1 SHELL→FULL 전환 완료 (L0 영역) | PASS | 본 문서 전체 — L0 CRUD L3 수준 완성 |
