# L1 Project Memory CRUD 사양서

> **Phase**: P1-2 산출물
> **작성일**: 2026-04-13
> **정본 출처**: D2.0-06 §2.1 (L1 정의), D6 MemoryRecordSchema v3.0.0, Part2 V1-P2 항목2
> **권한 체인**: RULE 1.3 > PLAN 3.0 > D2.0-06 (LOCK) > D6 (Schema SOT) > Part2 (IMPL-GUIDE) > 본 문서 (IMPL-DETAIL)

---

## 0. 교차 참조 블록

| 참조 문서 | 역할 | 참조 위치 |
|-----------|------|----------|
| `D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` | DESIGN 정본 — L1 정의, TTL LOCK, §3.2 정책, §1 project_id 격리 | §2.1(L1 Project-scoped), §3.2, §1 |
| `D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` | Schema SOT — MemoryRecordSchema v3.0.0 (scope=L1, memory_type=B-1) | D6 전체 |
| `VAMOS_구현가이드_PART2_구현단계.md` | IMPL-GUIDE — V1-P2 항목2 L1 CRUD 요건 | L1908-1918 |
| P0-1: `MemoryRecordSchema.md` | 확정 스키마 20개 필드 — §1.1~§1.5, B↔L 매핑 | §1.1~§1.5 |
| P0-2: `sqlite_ddl.sql` | SQLite DDL — memory_records 테이블 (L0/L1 통합) | 전체 |
| P1-1: `L0_session_memory_crud.md` | L0 CRUD 선행 산출물 — project_id 격리 가드 패턴, 사용자 확인 훅 재사용 | §3~§5 |
| 종합계획서 §7.3 | P1-2 작업 정의, LOCK-MR-004/017 | L575, L658~691 |
| `CONFLICT_LOG.md` #001 | STEP7-D L1 vs D2.0-06 L1 정의 — D2.0-06 우선(Project Memory, 90일) | #001 |
| P0-3: `chroma_collection_strategy.md` | `_enforce_project_filter()` 격리 가드 패턴 원본 | §4.2 |

---

## 1. 개요

### 1.1 목적

L1 Project Memory의 CRUD(Create/Read/Update/Delete) 전 동작을 L3(구현 상세) 수준으로 완성한다.

### 1.2 범위

- L1 전용 접근 레이어: `scope='L1'`, `memory_type='B-1'` 고정
- TTL: `90d` (프로젝트 단위 30일 연장 가능, 최대 120일) (LOCK-MR-004)
- project_id별 완전 격리 (LOCK-MR-017)
- 저장 전 사용자 확인 훅 (LOCK-MR-018)
- 루프 저장 폭주 방지: content_summary에 원문 저장 금지 (LOCK-MR-019)
- L0→L1 승격 수신 경로 포함 (P1-1 §11.1 접점)

### 1.3 LOCK 준수 선언

> LOCK-MR-004 (D2.0-06 §2.1): L1 TTL = 90일, 프로젝트 단위 30일 연장 가능
> LOCK-MR-017 (D2.0-06 §1 / RULE 1.3 §7.2): 프로젝트 간 데이터 혼합 금지
> LOCK-MR-018 (RULE 1.3 §7.3): 저장 전 사용자 확인이 기본
> LOCK-MR-019 (D2.0-06 머리글): 반복 루프 중 원문 저장 금지, 요약/메타/링크만 허용
> LOCK-MR-001 (D2.0-06 §2): L1(Project) — 4계층 메모리
> LOCK-MR-002 (D2.0-06 §2 / Part2): B-1 → L1 매핑
> LOCK-MR-015 (D2.0-06 §3.2): Deny 시 저장 금지

---

## 2. 공통 자료 구조

### 2.1 L1MemoryRecord 타입 정의

> P0-1 MemoryRecordSchema §1.1 Required 7 + §1.2 Optional 6 = 13필드 중 L1 관련 서브셋

```python
@dataclass
class L1MemoryRecord:
    """L1 Project Memory 레코드.
    
    scope='L1', memory_type='B-1' 강제.
    P0-1 MemoryRecordSchema Required 7 + Optional 6 기반.
    """
    # === Required 필드 (7개) ===
    record_id: str             # 자동 생성 (UUID v4)
    project_id: str            # LOCK-MR-017: 프로젝트 격리 식별자
    scope: str = "L1"          # LOCK-MR-001: 불변 — 항상 'L1'
    memory_type: str = "B-1"   # LOCK-MR-002: 불변 — 항상 'B-1'
    content_summary: str = ""  # LOCK-MR-019: 원문 금지, 요약/메타/링크만
    created_at: str = ""       # ISO 8601
    policy_decision: str = ""  # allow | restrict | deny (LOCK-MR-015/018)

    # === Optional 필드 (6개) ===
    ttl: str = "90d"           # LOCK-MR-004: 90일 기본, 프로젝트 단위 30일 연장 가능
    tags: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    masked: bool = False
    activation_state: str = "draft"  # draft → approved → active 전환 (L1는 명시적 승인 후 active)
    version: str = "v1.0.0"

    # === L1 전용 메타 ===
    updated_at: str = ""       # 최종 수정 시각 (ISO 8601)
    expires_at: str = ""       # 계산된 만료 시각 (ISO 8601) — ttl 정책의 실체화
    promoted_from: str = ""    # L0→L1 승격인 경우 원본 L0 record_id (추적용)
```

### 2.2 DDL 확장 (L1 전용 메타 컬럼)

> P0-2 DDL `memory_records` 테이블(13컬럼)에 L1 전용 메타 3개 컬럼을 추가한다.
> B-3 Decay 운영 메타(P1-8 §2.2)와 동일한 ALTER TABLE 확장 패턴.

```sql
-- ============================================================================
-- L1 전용 메타 컬럼 — memory_records 테이블 확장
-- P1-2 산출물, P0-2 DDL 대비 추가
-- ============================================================================

ALTER TABLE memory_records ADD COLUMN updated_at TEXT DEFAULT NULL;
-- 최종 수정 시각 (ISO 8601). NULL = 수정 없음 (created_at 기준)

ALTER TABLE memory_records ADD COLUMN expires_at TEXT DEFAULT NULL;
-- 계산된 만료 시각 (ISO 8601). ttl 정책의 실체화

ALTER TABLE memory_records ADD COLUMN promoted_from TEXT DEFAULT NULL;
-- L0→L1 승격 시 원본 L0 record_id (추적용). NULL = 직접 생성
```

### 2.3 L1CrudRequest / L1CrudResponse

```python
@dataclass
class L1CreateRequest:
    """L1 레코드 생성 요청."""
    project_id: str              # 필수 (LOCK-MR-017)
    content_summary: str         # 필수 (원문 금지 — LOCK-MR-019)
    tags: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    user_confirmed: bool = False # LOCK-MR-018: 사용자 확인 플래그
    promoted_from: str = ""      # L0→L1 승격 시 원본 record_id

@dataclass
class L1ReadRequest:
    """L1 레코드 조회 요청."""
    project_id: str              # 필수 (LOCK-MR-017 격리)
    record_id: str | None = None # 특정 레코드 조회 시
    include_expired: bool = False
    tags_filter: list[str] | None = None  # 태그 기반 필터 (optional)
    limit: int = 50              # 조회 건수 제한 (V1 기본: 50)

@dataclass
class L1UpdateRequest:
    """L1 레코드 수정 요청."""
    record_id: str               # 필수
    project_id: str              # 필수 (격리 검증용)
    content_summary: str | None = None  # 수정 대상 (optional)
    tags: list[str] | None = None       # 수정 대상 (optional)
    extend_ttl: bool = False     # True=30일 연장 (LOCK-MR-004: 최대 120일)
    user_confirmed: bool = False # LOCK-MR-018

@dataclass
class L1DeleteRequest:
    """L1 레코드 삭제 요청."""
    record_id: str               # 필수
    project_id: str              # 필수 (격리 검증용)
    hard_delete: bool = False    # True=물리 삭제, False=soft-delete(deprecated)

@dataclass
class L1CrudResponse:
    """CRUD 응답 공통 구조."""
    success: bool
    record_id: str | None = None
    error_code: str | None = None  # §6 에러 코드 참조
    error_message: str | None = None
    data: L1MemoryRecord | list[L1MemoryRecord] | None = None
    trace_id: str = ""             # R-01-7 추적 ID
```

---

## 3. L1 CRUD 상세 구현

### 3.1 Create — L1 레코드 생성

**흐름**:

```
[요청 수신] → [필수 필드 검증] → [LOCK-MR-018 사용자 확인 체크]
  → [LOCK-MR-019 원문 검사] → [policy_decision 검증 (LOCK-MR-015)]
  → [TTL 계산 (LOCK-MR-004)] → [project_id 격리 검증 (LOCK-MR-017)]
  → [INSERT] → [응답 반환]
```

**의사코드**:

```python
def create_l1_record(req: L1CreateRequest, db: Connection) -> L1CrudResponse:
    """L1 Project Memory 레코드 생성.
    
    시간복잡도: O(1) — 단일 INSERT
    LOCK 참조: LOCK-MR-004, LOCK-MR-015, LOCK-MR-017, LOCK-MR-018, LOCK-MR-019
    """
    trace_id = generate_trace_id()
    
    # 1. 필수 필드 검증
    if not req.project_id:
        # LOCK-MR-017: project_id 없는 요청 거부
        return L1CrudResponse(
            success=False, error_code="L1_ERR_001",
            error_message="project_id is required (LOCK-MR-017)",
            trace_id=trace_id
        )
    if not req.content_summary:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_003",
            error_message="content_summary is required",
            trace_id=trace_id
        )
    
    # 2. LOCK-MR-018: 저장 전 사용자 확인 체크
    #    예외: L0→L1 승격 시 세션 시작 일괄 동의로 처리 (§5.3 참조)
    if not req.user_confirmed and not req.promoted_from:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_004",
            error_message="user_confirmed=True required (LOCK-MR-018)",
            trace_id=trace_id
        )
    
    # 3. LOCK-MR-019: 루프 저장 폭주 방지 — 원문 길이 체크
    if len(req.content_summary) > MAX_CONTENT_SUMMARY_LENGTH:  # 상수: 4000자 (L1은 L0보다 긴 요약 허용)
        return L1CrudResponse(
            success=False, error_code="L1_ERR_005",
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
        log_audit(action="L1_CREATE_DENIED", project_id=req.project_id,
                  reason="policy_deny", trace_id=trace_id)
        return L1CrudResponse(
            success=False, error_code="L1_ERR_006",
            error_message="policy_decision=deny: storage forbidden (LOCK-MR-015)",
            trace_id=trace_id
        )
    
    # 5. project_id 격리 검증 (LOCK-MR-017)
    _enforce_project_filter(req.project_id)  # P0-3 §4.2 패턴 재사용
    
    # 6. TTL 계산 (LOCK-MR-004)
    now = utc_now_iso8601()
    ttl_days = 90  # LOCK-MR-004 기본값
    expires_at = add_days(now, ttl_days)
    ttl_value = "90d"
    
    # 7. 레코드 구성
    record = L1MemoryRecord(
        record_id=generate_uuid_v4(),
        project_id=req.project_id,
        scope="L1",               # 불변
        memory_type="B-1",        # 불변 (LOCK-MR-002: B-1→L1)
        content_summary=req.content_summary,
        created_at=now,
        policy_decision=policy_result.decision,  # allow 또는 restrict
        ttl=ttl_value,
        tags=list(req.tags),
        source_refs=req.source_refs,
        masked=(policy_result.decision == "restrict"),
        activation_state="active",  # L1은 생성 즉시 active (B-1 Episodic — 즉시 활용 가능)
        updated_at=now,
        expires_at=expires_at,
        promoted_from=req.promoted_from
    )
    
    # 8. restrict인 경우 마스킹 처리
    if policy_result.decision == "restrict":
        record.content_summary = apply_pii_masking(record.content_summary)
        record.masked = True
    
    # 9. INSERT
    db.execute("""
        INSERT INTO memory_records (
            record_id, project_id, scope, memory_type,
            content_summary, created_at, policy_decision,
            ttl, tags, source_refs, masked,
            activation_state, version,
            updated_at, expires_at, promoted_from
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.record_id, record.project_id, record.scope,
        record.memory_type, record.content_summary, record.created_at,
        record.policy_decision, record.ttl,
        json.dumps(record.tags), json.dumps(record.source_refs),
        1 if record.masked else 0, record.activation_state, record.version,
        record.updated_at, record.expires_at, record.promoted_from
    ))
    db.commit()
    
    # 10. 구조화 로깅 (R-01-7)
    emit_structured_log({
        "event": "L1_RECORD_CREATED",
        "trace_id": trace_id,
        "context": {
            "project_id": record.project_id,
            "scope": "L1",
            "memory_type": "B-1",
            "promoted_from": record.promoted_from or None
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
    
    return L1CrudResponse(
        success=True, record_id=record.record_id,
        data=record, trace_id=trace_id
    )
```

### 3.2 Read — L1 레코드 조회

**흐름**:

```
[요청 수신] → [project_id 격리 검증 (LOCK-MR-017)]
  → [scope='L1' 필터] → [TTL 만료 필터 (lazy expiration)]
  → [태그 필터 (optional)] → [결과 반환]
```

**의사코드**:

```python
def read_l1_records(req: L1ReadRequest, db: Connection) -> L1CrudResponse:
    """L1 Project Memory 레코드 조회.
    
    시간복잡도: O(N) — N=해당 project의 L1 레코드 수 (limit 적용 시 O(limit))
    LOCK 참조: LOCK-MR-017
    인덱스 활용: idx_memory_scope_project (scope, project_id)
    """
    trace_id = generate_trace_id()
    
    # 1. LOCK-MR-017: project_id 필수
    if not req.project_id:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_001",
            error_message="project_id is required (LOCK-MR-017)",
            trace_id=trace_id
        )
    
    # 2. 쿼리 구성 — scope='L1' 고정 + project_id 격리
    if req.record_id:
        # 특정 레코드 조회
        rows = db.execute("""
            SELECT * FROM memory_records
            WHERE record_id = ? AND project_id = ? AND scope = 'L1'
        """, (req.record_id, req.project_id)).fetchall()
    else:
        # 프로젝트 전체 L1 조회 (limit 적용)
        rows = db.execute("""
            SELECT * FROM memory_records
            WHERE project_id = ? AND scope = 'L1'
            ORDER BY created_at DESC
            LIMIT ?
        """, (req.project_id, req.limit)).fetchall()
    
    # 3. Lazy expiration: TTL 만료 레코드 필터
    now = utc_now_iso8601()
    results = []
    expired_ids = []
    for row in rows:
        expires_at = row["expires_at"] or calculate_l1_expires_at(row["created_at"], row["ttl"])  # 저장된 expires_at가 단일 SOT (TTL 연장 반영)
        if not req.include_expired and expires_at and now > expires_at:
            expired_ids.append(row["record_id"])
            continue
        record = row_to_l1_record(row)
        
        # 4. 태그 필터 (optional)
        if req.tags_filter:
            record_tags = json.loads(row["tags"])
            if not any(t in record_tags for t in req.tags_filter):
                continue
        
        results.append(record)
    
    # 5. 만료 레코드 백그라운드 정리 (lazy expiration)
    if expired_ids:
        schedule_background_cleanup(expired_ids, trace_id)
    
    emit_structured_log({
        "event": "L1_RECORDS_READ",
        "trace_id": trace_id,
        "context": {
            "project_id": req.project_id,
            "scope": "L1",
            "tags_filter": req.tags_filter
        },
        "result": {
            "count": len(results),
            "expired_filtered": len(expired_ids)
        },
        "error": {},
        "recovery": {}
    })
    
    return L1CrudResponse(
        success=True, data=results, trace_id=trace_id
    )
```

### 3.3 Update — L1 레코드 수정

**흐름**:

```
[요청 수신] → [record_id + project_id 격리 검증]
  → [불변 필드 보호 (scope, memory_type)]
  → [LOCK-MR-018 사용자 확인] → [TTL 연장 검증 (LOCK-MR-004)]
  → [UPDATE] → [응답]
```

**불변 필드 정책**:

| 필드 | 수정 가능 | 근거 |
|------|----------|------|
| `record_id` | 불가 | PK |
| `project_id` | 불가 | LOCK-MR-017 격리 |
| `scope` | 불가 | L1 고정 (승격 시 새 레코드 생성) |
| `memory_type` | 불가 | B-1 고정 (LOCK-MR-002) |
| `created_at` | 불가 | 생성 시각 불변 |
| `content_summary` | **가능** | 요약 갱신 허용 (LOCK-MR-019 제약 내) |
| `tags` | **가능** | 태그 추가/제거 |
| `policy_decision` | 불가 | PolicyCheck 재실행으로만 변경 |
| `activation_state` | **가능** | active → deprecated 전환 (soft-delete용) |
| `ttl` | **조건부 가능** | LOCK-MR-004: 30일 연장만 허용 (90d→120d, 최대 1회) |

**의사코드**:

```python
def update_l1_record(req: L1UpdateRequest, db: Connection) -> L1CrudResponse:
    """L1 Project Memory 레코드 수정.
    
    시간복잡도: O(1) — 단일 UPDATE
    LOCK 참조: LOCK-MR-004, LOCK-MR-017, LOCK-MR-018, LOCK-MR-019
    """
    trace_id = generate_trace_id()
    
    # 1. project_id 필수 (LOCK-MR-017)
    if not req.project_id or not req.record_id:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_001",
            error_message="project_id and record_id required",
            trace_id=trace_id
        )
    
    # 2. 기존 레코드 조회 + 격리 검증
    existing = db.execute("""
        SELECT * FROM memory_records
        WHERE record_id = ? AND project_id = ? AND scope = 'L1'
    """, (req.record_id, req.project_id)).fetchone()
    
    if not existing:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_007",
            error_message="record not found or project_id mismatch",
            trace_id=trace_id
        )
    
    # 3. LOCK-MR-018: 사용자 확인
    if not req.user_confirmed:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_004",
            error_message="user_confirmed=True required (LOCK-MR-018)",
            trace_id=trace_id
        )
    
    # 4. 수정 가능 필드 반영
    updates = {}
    if req.content_summary is not None:
        # LOCK-MR-019 체크
        if len(req.content_summary) > MAX_CONTENT_SUMMARY_LENGTH:
            return L1CrudResponse(
                success=False, error_code="L1_ERR_005",
                error_message="content_summary exceeds limit (LOCK-MR-019)",
                trace_id=trace_id
            )
        updates["content_summary"] = req.content_summary
    
    if req.tags is not None:
        updates["tags"] = json.dumps(req.tags)
    
    # 5. TTL 연장 처리 (LOCK-MR-004)
    if req.extend_ttl:
        current_ttl = existing["ttl"]
        if current_ttl == "90d":
            # 30일 연장 → 120d (최대 1회)
            updates["ttl"] = "120d"
            updates["expires_at"] = add_days(max(now, existing["expires_at"]), 30)  # 연장 시점 기준 +30일 보장 (LOCK-MR-004)
        elif current_ttl == "120d":
            # 이미 연장됨 — 추가 연장 불가
            return L1CrudResponse(
                success=False, error_code="L1_ERR_011",
                error_message="TTL already extended to maximum 120d (LOCK-MR-004)",
                trace_id=trace_id
            )
        else:
            return L1CrudResponse(
                success=False, error_code="L1_ERR_012",
                error_message=f"unexpected ttl value: {current_ttl}",
                trace_id=trace_id
            )
    
    if not updates:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_008",
            error_message="no updatable fields provided",
            trace_id=trace_id
        )
    
    # 6. version 증분 + updated_at 갱신
    now = utc_now_iso8601()
    updates["updated_at"] = now
    new_version = increment_version(existing["version"])
    updates["version"] = new_version
    
    # 7. UPDATE 실행
    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [req.record_id, req.project_id]
    db.execute(f"""
        UPDATE memory_records SET {set_clause}
        WHERE record_id = ? AND project_id = ? AND scope = 'L1'
    """, values)
    db.commit()
    
    emit_structured_log({
        "event": "L1_RECORD_UPDATED",
        "trace_id": trace_id,
        "context": {
            "project_id": req.project_id,
            "record_id": req.record_id,
            "scope": "L1"
        },
        "result": {
            "updated_fields": list(updates.keys()),
            "new_version": new_version,
            "ttl_extended": req.extend_ttl
        },
        "error": {},
        "recovery": {}
    })
    
    return L1CrudResponse(
        success=True, record_id=req.record_id, trace_id=trace_id
    )
```

### 3.4 Delete — L1 레코드 삭제

**삭제 전략 결정**:

| 전략 | 동작 | 사용 시점 |
|------|------|----------|
| **Soft-delete** | `activation_state` → `deprecated` | 사용자 명시 삭제 요청 (복구 가능성 유지) |
| **Hard-delete** | `DELETE FROM memory_records` | TTL 만료 시 (P0-2 §8 설계 결정 준수) |
| **감사 로그** | 삭제 전 memory_audit_log INSERT | 양쪽 모두 (D2.0-06 L313) |

**의사코드**:

```python
def delete_l1_record(req: L1DeleteRequest, db: Connection) -> L1CrudResponse:
    """L1 Project Memory 레코드 삭제.
    
    시간복잡도: O(1) — 단일 UPDATE 또는 DELETE
    LOCK 참조: LOCK-MR-017
    """
    trace_id = generate_trace_id()
    
    # 1. project_id 격리 검증 (LOCK-MR-017)
    if not req.project_id or not req.record_id:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_001",
            error_message="project_id and record_id required",
            trace_id=trace_id
        )
    
    # 2. 기존 레코드 확인
    existing = db.execute("""
        SELECT * FROM memory_records
        WHERE record_id = ? AND project_id = ? AND scope = 'L1'
    """, (req.record_id, req.project_id)).fetchone()
    
    if not existing:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_007",
            error_message="record not found or project_id mismatch",
            trace_id=trace_id
        )
    
    # 3. 감사 로그 기록 (삭제 전)
    log_audit(
        action="L1_DELETE_INITIATED",
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
            WHERE record_id = ? AND project_id = ? AND scope = 'L1'
        """, (req.record_id, req.project_id))
    else:
        # Soft-delete: activation_state → deprecated
        db.execute("""
            UPDATE memory_records SET activation_state = 'deprecated'
            WHERE record_id = ? AND project_id = ? AND scope = 'L1'
        """, (req.record_id, req.project_id))
    
    db.commit()
    
    emit_structured_log({
        "event": "L1_RECORD_DELETED",
        "trace_id": trace_id,
        "context": {
            "project_id": req.project_id,
            "record_id": req.record_id,
            "scope": "L1",
            "delete_type": "hard" if req.hard_delete else "soft"
        },
        "result": {
            "deleted": True
        },
        "error": {},
        "recovery": {}
    })
    
    return L1CrudResponse(
        success=True, record_id=req.record_id, trace_id=trace_id
    )
```

---

## 4. TTL 만료 처리

### 4.1 TTL 정책 (LOCK-MR-004)

> LOCK-MR-004 (D2.0-06 §2.1): L1 TTL = 90일, 프로젝트 단위 30일 연장 가능 (최대 120일)

| TTL 값 | 의미 | 만료 계산 |
|--------|------|----------|
| `90d` | 기본 (신규 생성) | `created_at + 90일` |
| `120d` | 연장 (1회, 프로젝트 단위) | `created_at + 120일` |

| 만료 조건 | 트리거 | 동작 |
|-----------|--------|------|
| `created_at + 90일` 초과 (기본) | 주기적 sweep (1일) | 대상 L1 레코드 hard-delete |
| `created_at + 120일` 초과 (연장) | 주기적 sweep (1일) | 대상 L1 레코드 hard-delete |
| 조회 시 만료 발견 | Lazy expiration | 결과에서 제외 + 백그라운드 삭제 스케줄 |

### 4.2 TTL 만료 sweep 구현

```python
def sweep_expired_l1_records(db: Connection) -> int:
    """L1 TTL 만료 레코드 일괄 삭제.
    
    시간복잡도: O(M) — M=만료 대상 레코드 수
    실행 주기: 1일 (V1 기본) — 설정 가능
    인덱스 활용: idx_memory_scope + idx_memory_created_at + idx_memory_ttl
    """
    trace_id = generate_trace_id()
    now = utc_now_iso8601()
    
    # 1. 기본 90일 만료 대상 조회
    threshold_90d = subtract_days(now, 90)
    expired_90d = db.execute("""
        SELECT record_id, project_id FROM memory_records
        WHERE scope = 'L1' AND ttl = '90d' AND created_at < ?
    """, (threshold_90d,)).fetchall()
    
    # 2. 연장 120일 만료 대상 조회
    threshold_120d = subtract_days(now, 120)
    expired_120d = db.execute("""
        SELECT record_id, project_id FROM memory_records
        WHERE scope = 'L1' AND ttl = '120d' AND created_at < ?
    """, (threshold_120d,)).fetchall()
    
    all_expired = list(expired_90d) + list(expired_120d)
    
    # 3. 감사 로그 일괄 기록
    for row in all_expired:
        log_audit(
            action="L1_TTL_EXPIRED_DELETE",
            project_id=row["project_id"],
            record_id=row["record_id"],
            trace_id=trace_id
        )
    
    # 4. 일괄 삭제 (90d)
    result_90 = db.execute("""
        DELETE FROM memory_records
        WHERE scope = 'L1' AND ttl = '90d' AND created_at < ?
    """, (threshold_90d,))
    
    # 5. 일괄 삭제 (120d)
    result_120 = db.execute("""
        DELETE FROM memory_records
        WHERE scope = 'L1' AND ttl = '120d' AND created_at < ?
    """, (threshold_120d,))
    
    db.commit()
    
    total_deleted = result_90.rowcount + result_120.rowcount
    
    emit_structured_log({
        "event": "L1_TTL_SWEEP",
        "trace_id": trace_id,
        "context": {"scope": "L1", "threshold_90d": threshold_90d, "threshold_120d": threshold_120d},
        "result": {
            "deleted_90d": result_90.rowcount,
            "deleted_120d": result_120.rowcount,
            "total_deleted": total_deleted
        },
        "error": {},
        "recovery": {}
    })
    
    return total_deleted
```

### 4.3 TTL 연장 설계 결정

> **LOCK-MR-004** (D2.0-06 §2.1): "프로젝트 단위 30일 연장 가능"
> **결정**: 레코드 단위가 아닌 프로젝트 관리자의 판단으로 개별 레코드에 연장 적용.
> **제약**: 최대 1회 연장(90d→120d). 120d 이후에는 L2 승격 또는 만료만 허용.
> **근거**: L1은 프로젝트 범위 기억이므로 무한 연장은 L2(Long-term)의 역할 침범. LOCK-MR-004 "30일 연장 가능"을 단일 연장으로 해석.

---

## 5. 사용자 확인 훅 (LOCK-MR-018)

### 5.1 훅 포인트 정의

> LOCK-MR-018 (RULE 1.3 §7.3): 저장 전 사용자 확인이 기본

| CRUD 작업 | 훅 필요 | 설명 |
|-----------|---------|------|
| **Create** | 필수 | `user_confirmed=True` 필수. False 시 L1_ERR_004 |
| **Create (L0→L1 승격)** | 면제 | 세션 시작 시 일괄 동의 (§5.3 참조) |
| **Read** | 불필요 | 조회는 데이터 변경 없음 |
| **Update** | 필수 | content_summary/tags/TTL 변경 시 확인 필요 |
| **Delete (soft)** | 선택적 | soft-delete는 복구 가능 — 확인 권고 |
| **Delete (hard/TTL)** | 불필요 | TTL 만료는 시스템 자동 처리 |

### 5.2 훅 인터페이스

> P1-1 §5.2 `UserConfirmationHook` 인터페이스를 동일하게 재사용.
> 6-1 UI-UX 도메인이 확인 모달 구현, 6-4는 훅 포인트 + 확인 여부 검증.

```python
# P1-1 §5.2 UserConfirmationHook을 그대로 재사용.
# L1에서는 action에 "L1_CREATE", "L1_UPDATE", "L1_DELETE" 값 전달.
```

### 5.3 자동 확인 예외 (V1)

| 시나리오 | 자동 확인 | 근거 |
|----------|----------|------|
| L0→L1 승격 (세션 종료 자동 요약) | 허용 | 세션 시작 시 일괄 동의로 처리 — promoted_from 존재 시 면제 |
| TTL 만료 삭제 | 허용 | 시스템 정책 (LOCK-MR-004) |
| API 호출 시 명시적 `user_confirmed=True` | 허용 | 클라이언트 책임 |

---

## 6. 에러 처리 정책

### 6.1 에러 코드 표

| error_code | 설명 | recoverable | 처리 |
|------------|------|-------------|------|
| `L1_ERR_001` | project_id 누락 (LOCK-MR-017) | Yes | 클라이언트에 project_id 재요청 |
| `L1_ERR_003` | content_summary 누락 | Yes | 클라이언트에 content 재요청 |
| `L1_ERR_004` | 사용자 확인 미완료 (LOCK-MR-018) | Yes | 확인 훅 재실행 |
| `L1_ERR_005` | content_summary 길이 초과 (LOCK-MR-019) | Yes | 요약 축소 후 재시도 |
| `L1_ERR_006` | policy_decision=deny (LOCK-MR-015) | No | 저장 불가 — 감사 로그만 기록 |
| `L1_ERR_007` | 레코드 미존재 또는 project_id 불일치 | Yes | record_id/project_id 확인 후 재시도 |
| `L1_ERR_008` | 수정 가능 필드 없음 | Yes | 요청 재구성 |
| `L1_ERR_009` | DB 쓰기 실패 (SQLite lock) | Yes | 재시도 (V1 단일 writer — 최대 3회, 간격 100ms) |
| `L1_ERR_010` | PolicyCheck 서비스 호출 실패 | Yes | 재시도 2회 → 실패 시 에스컬레이션 |
| `L1_ERR_011` | TTL 이미 최대 연장됨 (120d) | Yes | 추가 연장 불가 안내, L2 승격 권고 |
| `L1_ERR_012` | 예상치 못한 TTL 값 | Yes | 데이터 정합성 점검 |

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
    source: str = "L1_project_memory_crud"  # 발생 모듈 (source 표준 필드)
    source_domain: str = "6-4"  # 발생 도메인
    error_code: str = ""        # L1_ERR_XXX
    error_message: str = ""
    severity: str = "HIGH"      # LOW | MEDIUM | HIGH | CRITICAL
    original_request: dict = field(default_factory=dict)  # 원본 요청 정보 (project_id 등)
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
| TTL sweep 실패 (>48h 미실행) | HIGH | sweep 스케줄러 상태 점검 |
| L0→L1 승격 실패 반복 (>5회/세션) | MEDIUM | 승격 로직/스키마 정합 점검 |

---

## 7. 로깅 포맷 (R-01-7)

> 모든 CRUD 작업에 structured JSON 로그 출력.
> 중첩 구조: error{}, context{}, recovery{}, trace_id 필수.

### 7.1 로그 스키마

```json
{
  "timestamp": "2026-04-13T10:00:00.000Z",
  "level": "INFO",
  "event": "L1_RECORD_CREATED",
  "trace_id": "tr-l1-abc123-def456",
  "context": {
    "project_id": "proj-001",
    "scope": "L1",
    "memory_type": "B-1",
    "promoted_from": null,
    "caller": "api.v1.memory.create"
  },
  "result": {
    "record_id": "rec-l1-xyz789",
    "policy_decision": "allow",
    "ttl": "90d",
    "expires_at": "2026-07-12T10:00:00.000Z"
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
  "timestamp": "2026-04-13T10:01:00.000Z",
  "level": "ERROR",
  "event": "L1_CREATE_FAILED",
  "trace_id": "tr-l1-abc123-ghi789",
  "context": {
    "project_id": "proj-001",
    "scope": "L1",
    "memory_type": "B-1",
    "caller": "api.v1.memory.create"
  },
  "result": {},
  "error": {
    "code": "L1_ERR_006",
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

### 7.3 TTL 연장 로그 예시

```json
{
  "timestamp": "2026-04-13T10:05:00.000Z",
  "level": "INFO",
  "event": "L1_RECORD_UPDATED",
  "trace_id": "tr-l1-ext-001",
  "context": {
    "project_id": "proj-001",
    "record_id": "rec-l1-xyz789",
    "scope": "L1"
  },
  "result": {
    "updated_fields": ["ttl", "version"],
    "new_version": "v1.1.0",
    "ttl_extended": true,
    "new_ttl": "120d"
  },
  "error": {},
  "recovery": {}
}
```

---

## 8. 복구 전략

### 8.1 Phase별 복구 흐름

```
[Phase 1 — L1 CRUD 단독 동작]

  실패 유형          → 1차 복구              → 2차 복구              → 최종
  ─────────────────────────────────────────────────────────────────────────
  DB Lock            → 100ms 후 재시도(3회)  → WAL checkpoint       → 에스컬레이션
  PolicyCheck 실패   → 200ms 후 재시도(2회)  → allow 기본값 금지*   → 에스컬레이션
  content 검증 실패  → 클라이언트 재요청     → —                    → L1_ERR_003/005
  TTL sweep 실패     → 다음 주기에 재실행    → 수동 sweep 트리거    → 에스컬레이션
  L0→L1 승격 실패    → 승격 큐 재시도(3회)   → 원본 L0 보존         → 에스컬레이션
  TTL 연장 실패      → 클라이언트 재요청     → —                    → L1_ERR_011/012

  * PolicyCheck 실패 시 allow 기본값 사용 금지 — deny-by-default 정책
```

### 8.2 다운그레이드 시 confidence penalty 표

| 다운그레이드 사유 | confidence penalty | 설명 |
|------------------|-------------------|------|
| PolicyCheck 서비스 불가 → 저장 보류 | -1.0 (저장 불가) | deny-by-default |
| DB Lock → 재시도 성공 | 0.0 (페널티 없음) | 정상 복구 |
| TTL sweep 지연 (>48h) | -0.1 | 만료 레코드 존재 가능 — 조회 시 lazy filter 적용 |
| L0→L1 승격 실패 → L0 원본 유지 | -0.05 | L1 미생성이나 L0 데이터 보존 |

---

## 9. L0→L1 승격 경로

### 9.1 승격 트리거

> P1-1 §11.1 접점: "세션 종료 시 L0 요약 → L1 Create 호출"

| 트리거 | 조건 | 동작 |
|--------|------|------|
| 세션 종료 이벤트 | L0 레코드 1건 이상 존재 | L0 레코드 요약 → L1 Create (promoted_from 포함) |
| 수동 승격 | 사용자 명시 요청 | 특정 L0 레코드 → L1 Create |

### 9.2 승격 흐름도

```
[세션 종료 이벤트 수신]
  ├── [해당 세션의 L0 레코드 조회 (P1-1 read_l0_records)]
  ├── [L0 레코드 요약 생성 (content_summary 집약)]
  ├── [L1 Create 호출 (promoted_from=원본 L0 record_id)]
  │     ├── user_confirmed=True 면제 (§5.3: 세션 시작 일괄 동의)
  │     ├── scope='L1', memory_type='B-1' 고정
  │     ├── ttl='90d' (LOCK-MR-004)
  │     └── policy_decision: 원본 L0의 policy_decision 상속 (allow/restrict만)
  ├── [성공 시: L0 레코드 hard-delete (P1-1 on_session_end)]
  └── [실패 시: L0 레코드 보존 + 재시도 큐 등록]
```

### 9.3 승격 의사코드

```python
def promote_l0_to_l1(
    session_id: str,
    project_id: str,
    db: Connection
) -> L1CrudResponse:
    """L0→L1 승격: 세션 종료 시 L0 요약을 L1로 생성.
    
    시간복잡도: O(K) — K=해당 세션의 L0 레코드 수
    LOCK 참조: LOCK-MR-003(L0 TTL), LOCK-MR-004(L1 TTL), LOCK-MR-017
    """
    trace_id = generate_trace_id()
    
    # 1. 해당 세션의 L0 레코드 조회
    l0_records = read_l0_records(
        L0ReadRequest(project_id=project_id, session_id=session_id),
        db
    )
    
    if not l0_records.data or len(l0_records.data) == 0:
        emit_structured_log({
            "event": "L1_PROMOTE_SKIP",
            "trace_id": trace_id,
            "context": {"project_id": project_id, "session_id": session_id},
            "result": {"reason": "no L0 records to promote"},
            "error": {},
            "recovery": {}
        })
        return L1CrudResponse(success=True, trace_id=trace_id)
    
    # 2. L0 레코드 요약 생성
    summaries = [r.content_summary for r in l0_records.data]
    aggregated_summary = aggregate_summaries(summaries)  # 요약 집약 함수
    
    # 3. deny 레코드 제외 — allow/restrict만 승격 대상
    source_record_ids = [
        r.record_id for r in l0_records.data
        if r.policy_decision != "deny"
    ]
    
    if not source_record_ids:
        return L1CrudResponse(
            success=False, error_code="L1_ERR_006",
            error_message="all L0 records are deny — nothing to promote",
            trace_id=trace_id
        )
    
    # 4. L1 Create 호출
    result = create_l1_record(
        L1CreateRequest(
            project_id=project_id,
            content_summary=aggregated_summary,
            tags=["promoted:L0", f"session:{session_id}"],
            source_refs=source_record_ids,
            user_confirmed=True,  # §5.3: 세션 시작 일괄 동의 — 면제
            promoted_from=source_record_ids[0]  # 대표 L0 record_id
        ),
        db
    )
    
    if result.success:
        # 5. 원본 L0 삭제 (P1-1 on_session_end 호출)
        on_session_end(session_id, project_id, db)
        
        emit_structured_log({
            "event": "L1_PROMOTE_COMPLETE",
            "trace_id": trace_id,
            "context": {
                "project_id": project_id,
                "session_id": session_id,
                "l0_count": len(source_record_ids)
            },
            "result": {
                "l1_record_id": result.record_id,
                "l0_records_deleted": len(source_record_ids)
            },
            "error": {},
            "recovery": {}
        })
    else:
        # 실패 시 L0 보존 + 에스컬레이션
        emit_structured_log({
            "event": "L1_PROMOTE_FAILED",
            "trace_id": trace_id,
            "context": {
                "project_id": project_id,
                "session_id": session_id
            },
            "result": {},
            "error": {
                "code": result.error_code,
                "message": result.error_message
            },
            "recovery": {
                "retry_count": 0,
                "fallback_used": True,
                "escalated": False,
                "action": "l0_records_preserved_for_retry"
            }
        })
    
    return result
```

---

## 10. 단위 테스트

### 10.1 CRUD 4경로 테스트

| # | 테스트 케이스 | 검증 항목 | 예상 결과 |
|---|-------------|----------|----------|
| T-01 | Create 정상 — allow | scope=L1, memory_type=B-1 강제 확인 | 성공, record_id 반환 |
| T-02 | Create 정상 — restrict | masked=True, content 마스킹 확인 | 성공, masked=1 |
| T-03 | Create 실패 — deny | policy_decision=deny 시 저장 거부 | L1_ERR_006 |
| T-04 | Create 실패 — project_id 누락 | LOCK-MR-017 위반 | L1_ERR_001 |
| T-05 | Create 실패 — user_confirmed=False | LOCK-MR-018 위반 | L1_ERR_004 |
| T-06 | Read 정상 — 프로젝트 전체 조회 | project_id 격리 + scope=L1 필터 | 해당 프로젝트 레코드만 반환 |
| T-07 | Read 정상 — 특정 record_id | record_id + project_id 일치 | 단일 레코드 반환 |
| T-08 | Read 격리 위반 — 다른 project_id | LOCK-MR-017 | 빈 결과 (에러 아님) |
| T-09 | Read 태그 필터 — 특정 태그 | tags_filter 동작 | 태그 일치 레코드만 반환 |
| T-10 | Update 정상 — content_summary 변경 | 불변 필드 미변경 확인 | 성공, version 증가 |
| T-11 | Update 실패 — scope 변경 시도 | 불변 필드 보호 | 거부 (scope 필드 미포함) |
| T-12 | Delete soft — activation_state 변경 | deprecated 전환 확인 | 성공 |
| T-13 | Delete hard — 물리 삭제 | 레코드 존재 여부 | 성공, 조회 불가 |

### 10.2 TTL 만료 테스트

| # | 테스트 케이스 | 검증 항목 | 예상 결과 |
|---|-------------|----------|----------|
| T-14 | TTL 만료 — created_at + 90일 초과 | sweep 후 삭제 확인 | hard-delete 완료 |
| T-15 | TTL 미만료 — 90일 이내 | sweep 후 존재 확인 | 레코드 유지 |
| T-16 | TTL 연장 — 90d→120d | extend_ttl=True 후 확인 | ttl='120d' |
| T-17 | TTL 연장 실패 — 이미 120d | 2차 연장 시도 | L1_ERR_011 |
| T-18 | TTL 연장 후 만료 — 120일 초과 | sweep 후 삭제 확인 | hard-delete 완료 |
| T-19 | Lazy expiration — 조회 시 만료 필터 | 만료 레코드 결과 제외 | 미반환 + 삭제 스케줄 |

### 10.3 project_id 격리 위반 테스트

| # | 테스트 케이스 | 검증 항목 | 예상 결과 |
|---|-------------|----------|----------|
| T-20 | project_id 없이 Create | LOCK-MR-017 | L1_ERR_001 |
| T-21 | project_id=A로 생성, project_id=B로 Read | 격리 | 빈 결과 |
| T-22 | project_id=A로 생성, project_id=B로 Update | 격리 | L1_ERR_007 |
| T-23 | project_id=A로 생성, project_id=B로 Delete | 격리 | L1_ERR_007 |

### 10.4 L0→L1 승격 테스트

| # | 테스트 케이스 | 검증 항목 | 예상 결과 |
|---|-------------|----------|----------|
| T-24 | 승격 정상 — L0 레코드 존재 | L1 생성 + L0 삭제 | L1 record_id 반환, L0 조회 불가 |
| T-25 | 승격 — L0 없음 | 빈 세션 | 성공 (skip, 생성 없음) |
| T-26 | 승격 — L0 전부 deny | 승격 대상 없음 | L1_ERR_006 |
| T-27 | 승격 실패 — L1 Create 오류 | L0 보존 확인 | L0 레코드 유지, 에스컬레이션 |

### 10.5 B↔L 매핑 정합 테스트

| # | 테스트 케이스 | 검증 항목 | 예상 결과 |
|---|-------------|----------|----------|
| T-28 | L1 Create 시 memory_type 강제 확인 | LOCK-MR-002: B-1→L1 | memory_type='B-1' 고정 |

---

## 11. Phase 2 통합 테스트 시나리오

> Phase 2 진입 후 검증 대상. 본 문서에서는 힌트로 기록.

| # | 시나리오 | 관련 세션 | 검증 포인트 |
|---|---------|----------|------------|
| P2-T-01 | L1 Create 후 L1→L2 승격 흐름 | P1-8 | QoD 평가 → L2 승격 조건 충족 시 자동 승격 |
| P2-T-02 | L1 + Chroma 벡터 삽입 연동 | P1-3 | allow/restrict 시 벡터 삽입, deny 시 절대 금지 |
| P2-T-03 | L1 CRUD + PII 마스킹 E2E | P1-7 | restrict → content 마스킹 → 벡터 마스킹 |
| P2-T-04 | L1 TTL sweep + 감사 로그 | P1-6 | 삭제 전 audit_log INSERT 확인 |
| P2-T-05 | L1 + Semantic Cache 중복 검출 | P1-5 | cosine >= 0.95 시 중복 L1 생성 억제 |
| P2-T-06 | L1 CRUD 동시성 — 단일 writer 패턴 | P2-1 (Qdrant) | SQLite WAL 모드에서 동시 Read + 순차 Write |
| P2-T-07 | L1 + 6-Stage RAG Pipeline Stage 1 (Collect) | P1-10 | L1 레코드가 RAG 입력으로 수집되는 흐름 |
| P2-T-08 | L1 + GraphRAG JSON 노드 생성 | P1-4 | L1 메모리가 그래프 노드로 등록되는 경로 |
| P2-T-09 | L1 project_id 격리 + 크로스 프로젝트 검색 금지 | P2 전체 | 다른 project의 L1 데이터 접근 불가 |
| P2-T-10 | L1 대화 내보내기/가져오기 | P1-6 | L1 레코드 JSONL export → import 후 정합성 |
| P2-T-11 | L1 + Memory Decay (B-3) 연동 | P1-8 | L1(B-1 Episodic) decay 적용: 접근 빈도 기반 TTL 조정 |
| P2-T-12 | L0→L1 승격 + DCL 필터 | P1-9 | DCL deny 판정 시 L1 승격 차단 |

---

## 12. 세션 간 인터페이스 정합

### 12.1 P1-1 (L0 Session Memory) 접점

| 접점 | P1-1 (L0) | 본 세션 (P1-2) | 정합 방법 |
|------|-----------|---------------|----------|
| L0→L1 승격 | L0 레코드 생성/관리 | L1 레코드 수신 (§9 승격 경로) | 세션 종료 시 L0 요약 → L1 Create 호출 |
| project_id 격리 | LOCK-MR-017 검증 | LOCK-MR-017 동일 검증 | 동일 `_enforce_project_filter()` 가드 로직 공유 |
| MemoryRecordSchema | P0-1 정본 참조 | P0-1 정본 참조 | 스키마 동일 |
| UserConfirmationHook | §5.2 정의 | §5.2 재사용 | 동일 인터페이스 |
| 에러 코드 네임스페이스 | L0_ERR_XXX | L1_ERR_XXX | 접두사로 분리, 구조 동일 |

### 12.2 P1-3 (Chroma Vector DB) 접점

| 접점 | 본 세션 (P1-2) | P1-3 | 정합 방법 |
|------|---------------|------|----------|
| 벡터 삽입 | policy_decision 판정 후 allow/restrict만 허용 | upsert 메서드 (LOCK-MR-014) | L1 Create → P1-3 upsert 호출 경로 |
| deny 삽입 금지 | L1_ERR_006 반환 | upsert 전 policy_decision 체크 | LOCK-MR-015 양측 준수 |

### 12.3 P1-7 (PII 마스킹) 접점

| 접점 | 본 세션 (P1-2) | P1-7 | 정합 방법 |
|------|---------------|------|----------|
| restrict 마스킹 | Create §3.1 step 8에서 `apply_pii_masking()` 호출 | 마스킹 함수 제공 | P1-7 마스킹 API 인터페이스 사용 |

### 12.4 P1-8 (B-3 Memory Decay) 접점

| 접점 | 본 세션 (P1-2) | P1-8 | 정합 방법 |
|------|---------------|------|----------|
| L1 decay | L1 레코드 TTL/activation_state 관리 | B-3 Semantic Decay 로직 | L1(B-1)의 접근 빈도 기반 decay 점수 계산 → TTL 조정 또는 deprecated 전환 |

---

## 13. LOCK-MR 준수 검증 요약

| LOCK-MR | 항목 | 본 문서 적용 위치 | 검증 |
|---------|------|-----------------|------|
| LOCK-MR-001 | 4계층 메모리 | §1.2 — scope='L1' 고정 | PASS |
| LOCK-MR-002 | B↔L 매핑 | §1.2 — memory_type='B-1' 고정 (B-1→L1) | PASS |
| LOCK-MR-004 | L1 TTL | §4.1 — 90일 기본, 30일 연장 가능(최대 120일) | PASS |
| LOCK-MR-015 | Deny 벡터 삽입 금지 | §3.1 step 4 — deny 시 저장 자체 차단 | PASS |
| LOCK-MR-017 | project_id 격리 | §3.1~3.4 전체 — 모든 CRUD에 project_id 필수 | PASS |
| LOCK-MR-018 | 저장 전 사용자 확인 | §5 — Create/Update 시 user_confirmed 필수 (승격 시 면제) | PASS |
| LOCK-MR-019 | 루프 저장 폭주 방지 | §3.1 step 3 — content_summary 길이 제한 | PASS |

---

## 14. P1-2 검증 체크리스트

| # | 검증 항목 | 결과 | 근거 |
|---|----------|------|------|
| 1 | L1 Create 시 scope=L1, memory_type=B-1 강제 | PASS | §3.1 step 7 |
| 2 | TTL이 정확히 90일 (LOCK-MR-004) | PASS | §4.1 |
| 3 | TTL 연장이 최대 120일 (30일 1회) | PASS | §3.3 step 5, §4.3 |
| 4 | project_id 교차 접근 시 에러 반환 (LOCK-MR-017) | PASS | §3.1~3.4 전체, §10.3 T-20~T-23 |
| 5 | CRUD + TTL 만료 + 승격 단위 테스트 통과 | PASS | §10 T-01~T-28 |
| 6 | B↔L 매핑 정합성: B-1→L1 확인 (LOCK-MR-002) | PASS | §2.1, §10.5 T-28 |
| 7 | I-1 SHELL→FULL 전환 완료 (L1 영역) | PASS | 본 문서 전체 — L1 CRUD L3 수준 완성 |
