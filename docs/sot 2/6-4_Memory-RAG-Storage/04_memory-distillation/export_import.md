# P1-6. 대화 내보내기/가져오기 구현 상세 (V1)

> **세션**: P1-6 (2026-04-13)
> **산출물 버전**: v1.1 (step2 재검증: 3건 수정)
> **상태**: COMPLETE
> **LOCK 준수**: LOCK-MR-016 (L3 활성 게이트), LOCK-MR-017 (project_id 격리), LOCK-MR-018 (저장 전 사용자 확인), LOCK-MR-015 (Deny 벡터 삽입 금지 — 간접)
> **이슈 전환**: 해당 없음 (§6 이슈 —)
> **정본**: D2.0-06 §2.4 마이그레이션 원칙 + S7D-008, D6 MemoryRecordSchema v3.0.0, Part2 V1-Phase 2 항목6
> **교차 참조**: P0-1 MemoryRecordSchema, P1-1 L0_session_memory_crud, P1-2 L1_project_memory_crud, P1-4 json_graphrag, P1-7 pii_masking (✅ 완료 2026-04-13 COMPLETE — 작성 시점 '미완' 표기 stale, 2026-06-11 정정)
> **권한 체인**: RULE 1.3 > PLAN 3.0 > D2.0-06 (LOCK) > D6 (Schema SOT) > Part2 V1-P2 (구현가이드) > 본 문서 (IMPL-DETAIL)
>
> **LOCK 준수 상세**:
>   - LOCK-MR-017: project_id 기반 격리 내보내기/가져오기, 프로젝트 간 데이터 혼합 금지
>   - LOCK-MR-016: L2/L3 내보내기 시 별도 승인 확인 (L3=ApprovalGate 필수)
>   - LOCK-MR-018: 가져오기 시 저장 전 사용자 확인 기본
>   - LOCK-MR-015: Deny 판정 레코드는 내보내기 포함 가능(메타데이터), 가져오기 시 벡터 삽입 금지
>
> **입력 파일**:
>   - D2.0-06 §2.4 마이그레이션 원칙 (V1→V2 Export→Load 경로)
>   - D2.0-06 S7D-008 메모리 내보내기/가져오기 (JSON/SQLite, 스키마 정의, 중복 해소)
>   - Part2 V1-Phase 2 항목6 (JSON/Markdown export/import, UI: V1-Phase 4 Settings 뷰)
>   - P0-1: `MemoryRecordSchema.md` (확정 스키마 — Required 7 + Optional 6 + L3/B-2 확장 7 = 총 20필드)
>
> **이전 단계 이월 사항**: P1-1~P1-5 모두 이월 없음.

---

## 목차

1. [ExportImportManager 클래스 설계](#1-exportimportmanager-클래스-설계)
2. [내보내기 포맷 규격](#2-내보내기-포맷-규격)
3. [내보내기 대상 범위 정의](#3-내보내기-대상-범위-정의)
4. [Export 함수 구현](#4-export-함수-구현)
5. [Import 함수 구현](#5-import-함수-구현)
6. [가져오기 충돌 처리 전략](#6-가져오기-충돌-처리-전략)
7. [project_id 격리 (LOCK-MR-017)](#7-project_id-격리-lock-mr-017)
8. [PII 마스킹 연동 (P1-7)](#8-pii-마스킹-연동-p1-7)
9. [스키마 유효성 검증](#9-스키마-유효성-검증)
10. [에러 코드 정의](#10-에러-코드-정의)
11. [복구/재시도 전략](#11-복구재시도-전략)
12. [에스컬레이션 정책](#12-에스컬레이션-정책)
13. [로깅 규격 (R-01-7)](#13-로깅-규격-r-01-7)
14. [시간복잡도 분석 (Big-O)](#14-시간복잡도-분석-big-o)
15. [예외 처리 정책 표](#15-예외-처리-정책-표)
16. [단위 테스트 시나리오](#16-단위-테스트-시나리오)
17. [Phase 2 통합 테스트](#17-phase-2-통합-테스트)
18. [세션 간 인터페이스 cross-check](#18-세션-간-인터페이스-cross-check)
19. [LOCK-MR 참조 추적표](#19-lock-mr-참조-추적표)
20. [교차 참조 블록](#20-교차-참조-블록)

---

## 1. ExportImportManager 클래스 설계

### 1.1 클래스 계층

```
ExportImportManager (본 문서)
  ├── __init__(config: ExportImportConfig)
  ├── export_memories(project_id: str, options: ExportOptions) -> ExportResult
  ├── import_memories(file_path: str, project_id: str, options: ImportOptions) -> ImportResult
  ├── _validate_export_scope(scope_filter: list[str], project_id: str) -> bool
  ├── _check_pii_masking_status(records: list[MemoryRecord]) -> list[PIIMaskingCheck]
  ├── _serialize_record(record: MemoryRecord) -> dict
  ├── _deserialize_record(data: dict) -> MemoryRecord
  ├── _validate_schema(data: dict) -> ValidationResult
  ├── _resolve_conflict(existing: MemoryRecord, incoming: MemoryRecord, strategy: ConflictStrategy) -> MemoryRecord | None
  ├── _remap_project_id(record: MemoryRecord, target_project_id: str) -> MemoryRecord
  ├── _check_duplicate(record_id: str, project_id: str) -> MemoryRecord | None
  ├── _request_user_confirmation(action: str, details: dict) -> bool
  └── _write_export_file(data: ExportPayload, path: str, format: ExportFormat) -> str
```

### 1.2 ExportImportConfig 구조

```python
@dataclass
class ExportImportConfig:
    """Export/Import 설정 — D2.0-06 S7D-008 + Part2 V1-P2 항목6 기반"""
    default_format: ExportFormat = ExportFormat.JSONL     # 기본 내보내기 포맷
    export_dir: str = "~/.vamos/exports/"                 # S7D-008: 백업 디렉토리
    max_export_records: int = 10_000                      # V1 단일 내보내기 상한
    include_graph_data: bool = True                       # S7D-008: kg_nodes + kg_edges 포함
    include_source_qod: bool = True                       # SourceQoDSchema 동반 내보내기
    default_conflict_strategy: ConflictStrategy = ConflictStrategy.SKIP  # 기본: 기존 우선
    require_user_confirmation: bool = True                # LOCK-MR-018: 저장 전 확인 기본
    pii_check_on_export: bool = True                      # 내보내기 시 PII 마스킹 상태 확인
    pii_check_on_import: bool = True                      # 가져오기 시 PII 재검사
    schema_version: str = "v1.0.0"                        # 내보내기 스키마 버전
    compression: bool = False                             # V1=무압축, V2+=ZSTD 옵션
```

### 1.3 ExportFormat 열거형

```python
class ExportFormat(str, Enum):
    """내보내기 포맷 — Part2 항목6 (JSON/Markdown)"""
    JSONL = "jsonl"         # JSON Lines — 대용량 스트리밍 내보내기 (기본)
    JSON = "json"           # 구조화 JSON — S7D-008 스키마 포맷
    MARKDOWN = "markdown"   # Markdown — 사람 읽기용 내보내기
```

### 1.4 ConflictStrategy 열거형

```python
class ConflictStrategy(str, Enum):
    """가져오기 시 중복 memory_id 충돌 해소 전략 — S7D-008"""
    SKIP = "skip"               # 기존 우선 (기본) — 동일 record_id 존재 시 무시
    OVERWRITE = "overwrite"     # 신규 우선 — 동일 record_id 존재 시 덮어쓰기
    USER_CHOICE = "user_choice" # 사용자 선택 — 건별 확인 다이얼로그
```

---

## 2. 내보내기 포맷 규격

### 2.1 구조화 JSON 포맷 (S7D-008 정본)

> **REF**: D2.0-06 S7D-008 스키마: `{version, export_date, memories: MemoryEntry[], kg_nodes: Node[], kg_edges: Edge[]}`

```json
{
  "version": "v1.0.0",
  "export_date": "2026-04-13T10:00:00Z",
  "exporter": "vamos_export_import_v1",
  "source_project_id": "proj_abc123",
  "schema_ref": "D6:MemoryRecordSchema:v3.0.0",
  "record_count": 42,
  "scopes_included": ["L0", "L1"],
  "memories": [
    {
      "record_id": "mem_001",
      "project_id": "proj_abc123",
      "scope": "L0",
      "memory_type": "B-4",
      "content_summary": "세션 내 작업 메모",
      "created_at": "2026-04-13T09:00:00Z",
      "policy_decision": "allow",
      "ttl": "session_end",
      "tags": ["session", "draft"],
      "source_refs": ["src_001"],
      "masked": false,
      "activation_state": "active",
      "version": "v1.0.0"
    }
  ],
  "source_qod": [
    {
      "source_id": "src_001",
      "project_id": "proj_abc123",
      "qod_score": 0.85,
      "freshness": 0.9,
      "reliability": 0.8,
      "completeness": 0.85,
      "computed_at": "2026-04-13T09:01:00Z"
    }
  ],
  "kg_nodes": [
    {
      "node_id": "n_001",
      "node_type": "Decision",
      "label": "아키텍처 선택",
      "project_id": "proj_abc123",
      "properties": {}
    }
  ],
  "kg_edges": [
    {
      "edge_id": "e_001",
      "source_node_id": "n_001",
      "target_node_id": "n_002",
      "edge_type": "CAUSED_BY",
      "project_id": "proj_abc123",
      "properties": {}
    }
  ],
  "checksum": "sha256:abcdef1234567890..."
}
```

### 2.2 JSONL 포맷 (대용량 스트리밍)

```
{"_type": "header", "version": "v1.0.0", "export_date": "2026-04-13T10:00:00Z", "source_project_id": "proj_abc123", "schema_ref": "D6:MemoryRecordSchema:v3.0.0"}
{"_type": "memory", "record_id": "mem_001", "project_id": "proj_abc123", "scope": "L0", ...}
{"_type": "memory", "record_id": "mem_002", "project_id": "proj_abc123", "scope": "L1", ...}
{"_type": "source_qod", "source_id": "src_001", "project_id": "proj_abc123", ...}
{"_type": "kg_node", "node_id": "n_001", "node_type": "Decision", ...}
{"_type": "kg_edge", "edge_id": "e_001", "source_node_id": "n_001", ...}
{"_type": "footer", "record_count": 42, "checksum": "sha256:abcdef..."}
```

### 2.3 Markdown 포맷 (사람 읽기용)

```markdown
# VAMOS Memory Export — proj_abc123
> Exported: 2026-04-13T10:00:00Z | Schema: D6:MemoryRecordSchema:v3.0.0 | Records: 42

## L0 Session Memory (3건)
### mem_001 — B-4 Working
- **content_summary**: 세션 내 작업 메모
- **created_at**: 2026-04-13T09:00:00Z
- **policy_decision**: allow
- **ttl**: session_end
- **tags**: session, draft
...

## L1 Project Memory (39건)
...
```

> **포맷 선택 가이드**: 프로그래밍 Import/Export 순환에는 JSONL(기본) 또는 JSON을 사용한다. Markdown은 사람 검토/아카이브 용도이며 Import 대상이 아니다.

### 2.4 무결성 체크섬

- **알고리즘**: SHA-256
- **범위**: 모든 `memories` + `source_qod` + `kg_nodes` + `kg_edges` 레코드를 `record_id`/`source_id`/`node_id`/`edge_id` 정렬 후 직렬화 → SHA-256
- **검증**: Import 시 `checksum` 필드와 재계산 값 비교. 불일치 시 `EI_ERR_009` (파일 변조 의심)

---

## 3. 내보내기 대상 범위 정의

### 3.1 계층별 내보내기 권한

| 계층 | scope | 기본 내보내기 | 승인 요건 | 근거 |
|------|-------|-------------|----------|------|
| **L0** | `L0` | 허용 | 없음 (세션 레벨 임시 데이터) | Part2 항목6 |
| **L1** | `L1` | 허용 | 없음 (프로젝트 레벨) | Part2 항목6 |
| **L2** | `L2` | 조건부 | 별도 승인 필요 (Core 지식 보호) | LOCK-MR-016 간접 |
| **L3** | `L3` | 조건부 | **D7 ApprovalGate 필수** (LOCK-MR-016) | LOCK-MR-016 |

### 3.2 내보내기 필터 옵션

```python
@dataclass
class ExportOptions:
    """내보내기 필터 — project_id 필수"""
    scope_filter: list[str] | None = None        # ["L0", "L1"] — None=전체 (L0+L1만 기본)
    memory_type_filter: list[str] | None = None  # ["B-1", "B-4"] — None=전체
    date_from: str | None = None                  # ISO 8601 — created_at 하한
    date_to: str | None = None                    # ISO 8601 — created_at 상한
    tags_filter: list[str] | None = None          # 태그 AND 필터
    include_denied: bool = False                  # deny 레코드 포함 여부 (메타데이터만, content_summary 제외)
    format: ExportFormat = ExportFormat.JSONL      # 출력 포맷
    include_graph: bool = True                     # KG 노드/엣지 포함
    include_source_qod: bool = True                # QoD 데이터 포함
    output_path: str | None = None                 # None=기본 경로 (~/.vamos/exports/)
```

### 3.3 scope_filter 기본 동작

- `scope_filter=None` → **L0 + L1만 내보내기** (기본 안전 정책)
- `scope_filter=["L0", "L1", "L2"]` → L2 포함 시 승인 확인 호출
- `scope_filter=["L3"]` 또는 L3 포함 → **D7 ApprovalGate 확인 필수** (LOCK-MR-016)
- 승인 미통과 시 `EI_ERR_003` 발생, 내보내기 중단

---

## 4. Export 함수 구현

### 4.1 export_memories 메인 플로우

```python
def export_memories(
    self,
    project_id: str,
    options: ExportOptions = ExportOptions()
) -> ExportResult:
    """
    대화 메모리 내보내기.

    Args:
        project_id: 프로젝트 식별자 (LOCK-MR-017 격리)
        options: 내보내기 옵션

    Returns:
        ExportResult: 내보내기 결과 (파일 경로, 레코드 수, 체크섬)

    Raises:
        ProjectIdRequiredError (EI_ERR_001): project_id 누락
        ScopeApprovalError (EI_ERR_003): L2/L3 승인 미통과
        ExportLimitExceededError (EI_ERR_004): max_export_records 초과
        PIIMaskingIncompleteError (EI_ERR_005): PII 미마스킹 레코드 발견 (restrict)
    """
```

### 4.2 Export 처리 흐름

```
[1] project_id 유효성 검증
  ├── 누락 → EI_ERR_001 (ProjectIdRequiredError)
  └── 유효 → [2]

[2] scope_filter 승인 검증
  ├── L2 포함 → 별도 승인 확인 → 미통과 시 EI_ERR_003
  ├── L3 포함 → D7 ApprovalGate 호출 → 미통과 시 EI_ERR_003
  └── L0/L1만 → [3]

[3] 메모리 레코드 조회 (project_id 필터 강제)
  ├── SQLite: SELECT * FROM memory_records WHERE project_id = ? AND scope IN (?)
  ├── 날짜/태그/memory_type 필터 적용
  └── record_count > max_export_records → EI_ERR_004

[4] PII 마스킹 상태 확인 (pii_check_on_export=True)
  ├── policy_decision="restrict" AND masked=False → EI_ERR_005 (차단 — 해당 레코드 스킵, 미마스킹 원문 유출 방지; 강제 시 마스킹 적용 후 포함)
  ├── policy_decision="deny" AND include_denied=False → 해당 레코드 스킵
  ├── policy_decision="deny" AND include_denied=True → content_summary 제외, 메타만 포함
  └── 정상 → [5]

[5] 연관 데이터 수집
  ├── source_refs → SourceQoDSchema 조회 (include_source_qod=True)
  ├── KG 노드/엣지 조회 (include_graph=True, project_id 필터)
  └── [6]

[6] 직렬화 + 체크섬 생성
  ├── _serialize_record() × N건
  ├── SHA-256 checksum 계산
  └── [7]

[7] 파일 출력
  ├── ExportFormat.JSONL → _write_jsonl()
  ├── ExportFormat.JSON → _write_json()
  ├── ExportFormat.MARKDOWN → _write_markdown()
  └── 파일명: {project_id}_{export_date}_{uuid_short}.{ext}

[8] 로깅 + ExportResult 반환
```

### 4.3 ExportResult 구조

```python
@dataclass
class ExportResult:
    """내보내기 결과"""
    success: bool
    file_path: str                    # 출력 파일 절대 경로
    record_count: int                 # 내보낸 메모리 레코드 수
    source_qod_count: int             # 내보낸 QoD 레코드 수
    kg_node_count: int                # 내보낸 KG 노드 수
    kg_edge_count: int                # 내보낸 KG 엣지 수
    checksum: str                     # SHA-256 체크섬
    scopes_exported: list[str]        # 실제 내보낸 scope 목록
    skipped_deny_count: int           # deny로 스킵된 레코드 수
    pii_warnings: list[str]           # PII 관련 경고 목록
    export_duration_ms: float         # 소요 시간
    format: ExportFormat              # 출력 포맷
```

### 4.4 _serialize_record 상세

```python
def _serialize_record(self, record: MemoryRecord) -> dict:
    """MemoryRecordSchema 전체 필드 직렬화.
    
    P0-1 스키마 기준: Required 7 + Optional 6 + L3/B-2 확장 7 = 최대 20필드.
    L3/B-2 확장 필드는 scope='L3' AND memory_type='B-2'인 경우에만 포함.
    """
    base = {
        # Required 7
        "record_id": record.record_id,
        "project_id": record.project_id,
        "scope": record.scope,
        "memory_type": record.memory_type,
        "content_summary": record.content_summary,
        "created_at": record.created_at,
        "policy_decision": record.policy_decision,
        # Optional 6
        "ttl": record.ttl,
        "tags": record.tags or [],
        "source_refs": record.source_refs or [],
        "masked": record.masked or False,
        "activation_state": record.activation_state or "draft",
        "version": record.version or "v1.0.0",
    }
    # L3/B-2 확장 필드 (Procedural Memory 전용)
    if record.scope == "L3" and record.memory_type == "B-2":
        base.update({
            "procedure_id": record.procedure_id,
            "target_scope": record.target_scope,
            "trigger_conditions": record.trigger_conditions,
            "steps": record.steps or [],
            "required_tools": record.required_tools or [],
            "safety_notes": record.safety_notes,
            "provenance": record.provenance or {},
        })
    return base
```

---

## 5. Import 함수 구현

### 5.1 import_memories 메인 플로우

```python
def import_memories(
    self,
    file_path: str,
    project_id: str,
    options: ImportOptions = ImportOptions()
) -> ImportResult:
    """
    대화 메모리 가져오기.

    Args:
        file_path: 가져올 파일 경로 (.jsonl 또는 .json)
        project_id: 대상 프로젝트 ID (LOCK-MR-017 — 가져온 레코드의 project_id를 이 값으로 재매핑)
        options: 가져오기 옵션

    Returns:
        ImportResult: 가져오기 결과 (성공/실패 레코드 수, 충돌 해소 내역)

    Raises:
        ProjectIdRequiredError (EI_ERR_001): project_id 누락
        FileNotFoundError (EI_ERR_006): 파일 없음
        InvalidFormatError (EI_ERR_007): 지원하지 않는 파일 형식
        SchemaValidationError (EI_ERR_008): 스키마 검증 실패
        ChecksumMismatchError (EI_ERR_009): 체크섬 불일치
    """
```

### 5.2 ImportOptions 구조

```python
@dataclass
class ImportOptions:
    """가져오기 옵션"""
    conflict_strategy: ConflictStrategy = ConflictStrategy.SKIP  # 기본: 기존 우선
    remap_project_id: bool = True          # True=target project_id로 재매핑 (기본)
    validate_checksum: bool = True          # 체크섬 검증 활성화
    dry_run: bool = False                   # True=실제 저장 없이 검증만 수행
    skip_denied: bool = True                # deny 레코드 가져오기 스킵 (기본)
    import_graph: bool = True               # KG 노드/엣지 가져오기
    import_source_qod: bool = True          # QoD 데이터 가져오기
    batch_size: int = 100                   # 배치 단위 처리
    require_user_confirmation: bool = True  # LOCK-MR-018: 저장 전 확인
```

### 5.3 Import 처리 흐름

```
[1] 파일 존재 + 포맷 확인
  ├── 파일 없음 → EI_ERR_006
  ├── .md 확장자 → EI_ERR_007 (Markdown은 import 대상 아님)
  └── .jsonl / .json → [2]

[2] 헤더/메타 읽기 + 스키마 버전 확인
  ├── version 필드 호환성 확인 (현재 파서가 지원하는 버전)
  └── schema_ref 확인 → D6:MemoryRecordSchema 매핑

[3] 체크섬 검증 (validate_checksum=True)
  ├── footer/checksum 필드 추출
  ├── 전체 레코드 재계산 → 비교
  └── 불일치 → EI_ERR_009

[4] 레코드별 스키마 유효성 검증 (§9 상세)
  ├── Required 7필드 존재 확인
  ├── enum 제약 (scope: L0~L3, memory_type: B-1~B-4, policy_decision: allow/restrict/deny)
  ├── 타입 검증 (string, array, boolean, object)
  └── 실패 → EI_ERR_008 (건별 스킵 또는 전체 중단)

[5] project_id 재매핑 (remap_project_id=True)
  ├── 모든 레코드의 project_id → target project_id로 변환
  ├── source_qod의 project_id도 동일 변환
  ├── kg_nodes/kg_edges의 project_id도 동일 변환
  └── 원본 project_id는 메타데이터로 보존 (_original_project_id)

[6] PII 재검사 (pii_check_on_import=True)
  ├── 각 레코드 content_summary에 PII 탐지 수행
  ├── PII 탐지 + policy_decision="restrict" → 마스킹 후 진행
  ├── PII 탐지 + policy_decision="deny" + skip_denied=True → 스킵
  └── 정상 → [7]

[7] 중복 체크 + 충돌 해소 (건별)
  ├── record_id 기준 기존 레코드 조회 (_check_duplicate)
  ├── 중복 없음 → INSERT 대기열
  ├── 중복 있음 + SKIP → 스킵 (카운트 기록)
  ├── 중복 있음 + OVERWRITE → UPDATE 대기열
  └── 중복 있음 + USER_CHOICE → _request_user_confirmation()

[8] 사용자 확인 (require_user_confirmation=True, LOCK-MR-018)
  ├── dry_run=True → 확인 스킵, 결과만 반환
  ├── 총 INSERT/UPDATE 건수 요약 제시
  └── 사용자 거부 → 전체 취소

[9] 배치 저장 실행 (batch_size 단위)
  ├── INSERT: memory_records 테이블 삽입
  ├── UPDATE: 기존 레코드 덮어쓰기
  ├── source_qod: source_qod 테이블 삽입/갱신
  ├── kg_nodes/kg_edges: graph 저장소 삽입 (P1-4 JsonGraphStore 연동)
  └── 배치별 커밋 (V1 SQLite 단일 writer 패턴)

[10] 로깅 + ImportResult 반환
```

### 5.4 ImportResult 구조

```python
@dataclass
class ImportResult:
    """가져오기 결과"""
    success: bool
    total_records: int                  # 파일 내 총 레코드 수
    inserted_count: int                 # 신규 삽입 수
    updated_count: int                  # 덮어쓰기 수
    skipped_count: int                  # 스킵 수 (중복/deny/검증실패)
    failed_count: int                   # 실패 수
    conflict_details: list[ConflictDetail]   # 충돌 해소 내역
    validation_errors: list[ValidationError] # 스키마 검증 실패 상세
    source_qod_imported: int            # QoD 레코드 가져온 수
    kg_nodes_imported: int              # KG 노드 가져온 수
    kg_edges_imported: int              # KG 엣지 가져온 수
    pii_masked_count: int               # PII 마스킹 처리된 레코드 수
    pii_denied_skip_count: int          # PII deny로 스킵된 레코드 수
    import_duration_ms: float           # 소요 시간
    dry_run: bool                       # dry_run 모드 여부
```

### 5.5 ConflictDetail 구조

```python
@dataclass
class ConflictDetail:
    """충돌 해소 상세"""
    record_id: str
    strategy_applied: ConflictStrategy
    existing_version: str          # 기존 레코드 version
    incoming_version: str          # 들어온 레코드 version
    resolution: str                # "skipped" | "overwritten" | "user_kept_existing" | "user_chose_incoming"
    existing_created_at: str
    incoming_created_at: str
```

---

## 6. 가져오기 충돌 처리 전략

### 6.1 전략별 동작

| 전략 | record_id 중복 시 동작 | 사용자 개입 | 적합 시나리오 |
|------|----------------------|-----------|-------------|
| **SKIP** (기본) | 기존 레코드 유지, 들어온 레코드 무시 | 없음 | 백업 복원 (기존 데이터 보존 우선) |
| **OVERWRITE** | 기존 레코드를 들어온 레코드로 덮어쓰기 | 없음 | 다른 기기에서 최신 데이터 동기화 |
| **USER_CHOICE** | 건별 사용자 선택 다이얼로그 | 건별 확인 | 소량 레코드 정밀 병합 |

### 6.2 OVERWRITE 시 보호 규칙

1. **version 비교**: 들어온 레코드의 `version`이 기존보다 구 버전이면 경고 (강제 진행은 가능)
2. **policy_decision 보호**: 기존 `deny` → 들어온 `allow`로 덮어쓰기 시 `EI_WARN_001` 경고 (보안 약화 가능)
3. **activation_state 보호**: 기존 `deprecated` → 들어온 `active`로 복원 시 `EI_WARN_002` 경고
4. **L3 Procedural 보호**: L3 레코드 덮어쓰기 시 D7 ApprovalGate 확인 필수 (LOCK-MR-016)

### 6.3 _resolve_conflict 구현

```python
def _resolve_conflict(
    self,
    existing: MemoryRecord,
    incoming: MemoryRecord,
    strategy: ConflictStrategy
) -> MemoryRecord | None:
    """
    충돌 해소.
    
    Returns:
        MemoryRecord: 적용할 레코드 (None=스킵)
    """
    if strategy == ConflictStrategy.SKIP:
        return None  # 기존 유지

    if strategy == ConflictStrategy.OVERWRITE:
        # 보호 규칙 경고 발행
        if existing.policy_decision == "deny" and incoming.policy_decision != "deny":
            self._log_warning("EI_WARN_001", record_id=incoming.record_id)
            # 보안: deny→non-deny 강등은 자동 진행 금지 — D7 ApprovalGate 재평가 승인 필수
            if not self._check_approval_gate(incoming):
                raise ScopeApprovalError("EI_ERR_003")  # deny 강등은 명시적 보안 승인 없이는 차단
            # 보안: deny→non-deny 강등은 자동 진행 금지 — D7 ApprovalGate 재평가 승인 필수
            if not self._check_approval_gate(incoming):
                raise ScopeApprovalError("EI_ERR_003")  # deny 강등은 명시적 보안 승인 없이는 차단
        if existing.activation_state == "deprecated" and incoming.activation_state == "active":
            self._log_warning("EI_WARN_002", record_id=incoming.record_id)
        if incoming.scope == "L3":
            if not self._check_approval_gate(incoming):
                raise ScopeApprovalError("EI_ERR_003")
        return incoming

    if strategy == ConflictStrategy.USER_CHOICE:
        user_choice = self._request_user_confirmation(
            action="resolve_conflict",
            details={
                "record_id": existing.record_id,
                "existing": self._serialize_record(existing),
                "incoming": self._serialize_record(incoming),
            }
        )
        if user_choice:
            if incoming.scope == "L3" and not self._check_approval_gate(incoming):
                raise ScopeApprovalError("EI_ERR_003")  # LOCK-MR-016: L3 덮어쓰기 ApprovalGate 필수
            return incoming
        return None
```

---

## 7. project_id 격리 (LOCK-MR-017)

### 7.1 내보내기 격리

- `export_memories(project_id=X)`는 **project_id=X인 레코드만** 조회한다.
- SQL 쿼리에 `WHERE project_id = ?` 파라미터 바인딩 강제.
- project_id가 누락되거나 빈 문자열이면 `EI_ERR_001` 즉시 발생.
- 내보내기 파일의 `source_project_id` 필드에 원본 project_id를 기록한다.

### 7.2 가져오기 격리

- `import_memories(file_path, project_id=Y)`는 모든 레코드를 **project_id=Y로 재매핑**한다.
- 원본 project_id는 `_original_project_id` 메타데이터로 보존 (감사 추적용).
- `remap_project_id=False` 옵션 시 원본 project_id 유지 — 단, **동일 프로젝트 간 내보내기/가져오기**에만 허용.
  - 원본 project_id != target project_id AND remap_project_id=False → `EI_ERR_002` (크로스 프로젝트 혼합 금지)

### 7.3 _remap_project_id 구현

```python
def _remap_project_id(
    self,
    record: MemoryRecord,
    target_project_id: str
) -> MemoryRecord:
    """
    project_id 재매핑. LOCK-MR-017 준수.
    
    원본 project_id는 _original_project_id로 보존.
    source_refs가 참조하는 SourceQoD도 별도로 재매핑 필요.
    """
    original_pid = record.project_id
    record.project_id = target_project_id
    record._original_project_id = original_pid
    return record
```

### 7.4 크로스 프로젝트 가져오기 방지 검증

```python
def _validate_cross_project(
    self,
    source_project_id: str,
    target_project_id: str,
    remap: bool
) -> None:
    if source_project_id != target_project_id and not remap:
        raise CrossProjectError(
            "EI_ERR_002: 크로스 프로젝트 가져오기 시 remap_project_id=True 필수. "
            f"source={source_project_id}, target={target_project_id}"
        )
```

---

## 8. PII 마스킹 연동 (P1-7)

> **P1-7 상태 정정 (2026-06-11)**: P1-7 (PII 마스킹)은 2026-04-13 완료(pii_masking.md v1.1, 상태: COMPLETE) — 본 문서 작성 시점의 '미완성' 전제가 stale. 본 절의 **인터페이스 계약** 정의는 유지하며, P1-7 정본과의 구현 통합 여부는 별도 검증 대상.

### 8.1 Export 시 PII 확인

```python
def _check_pii_masking_status(
    self,
    records: list[MemoryRecord]
) -> list[PIIMaskingCheck]:
    """
    내보내기 대상 레코드의 PII 마스킹 상태를 확인.
    
    - policy_decision="restrict" AND masked=False → 경고 (EI_ERR_005)
    - policy_decision="deny" → content_summary 제외 옵션 적용
    
    P1-7 완료 전: masked 필드 기반 정적 검사만 수행.
    P1-7 완료 후: PIIMasker.detect() 호출로 실시간 PII 재탐지.
    """
    results = []
    for record in records:
        check = PIIMaskingCheck(
            record_id=record.record_id,
            policy_decision=record.policy_decision,
            masked=record.masked,
            pii_detected=False,  # P1-7 연동 전 기본값
            action="pass",
        )
        if record.policy_decision == "restrict" and not record.masked:
            check.action = "warn"
            check.pii_detected = True  # 마스킹 누락 의심
        elif record.policy_decision == "deny":
            check.action = "exclude_content"
        results.append(check)
    return results
```

### 8.2 Import 시 PII 재검사

```python
# P1-7 연동 인터페이스 (P1-7 완료 후 활성화)
# from vamos_core.safety.guardrails.pii_masker import PIIMasker

def _recheck_pii_on_import(
    self,
    record: MemoryRecord,
    pii_masker  # PIIMasker 인스턴스 (P1-7)
) -> MemoryRecord:
    """
    가져오기 시 content_summary에 PII 재탐지.
    
    - PII 탐지 + restrict → 마스킹 후 저장 (masked=True)
    - PII 탐지 + deny → 저장 차단 (LOCK-MR-015)
    - PII 미탐지 → 통과
    """
    detection = pii_masker.detect(record.content_summary)
    if detection.pii_found:
        if record.policy_decision == "deny":
            raise PIIDenyError(f"EI_ERR_010: deny 레코드에 PII 탐지. record_id={record.record_id}")
        elif record.policy_decision == "restrict":
            mask_result = pii_masker.mask(record.content_summary)
            record.content_summary = mask_result.masked_text
            record.masked = True
    return record
```

---

## 9. 스키마 유효성 검증

### 9.1 검증 규칙

| # | 검증 항목 | 조건 | 실패 코드 |
|---|----------|------|----------|
| V-1 | Required 필드 존재 | record_id, project_id, scope, memory_type, content_summary, created_at, policy_decision 전부 존재 | EI_ERR_008-R |
| V-2 | scope enum | `L0` \| `L1` \| `L2` \| `L3` | EI_ERR_008-S |
| V-3 | memory_type enum | `B-1` \| `B-2` \| `B-3` \| `B-4` | EI_ERR_008-M |
| V-4 | policy_decision enum | `allow` \| `restrict` \| `deny` | EI_ERR_008-P |
| V-5 | created_at 형식 | ISO 8601 파싱 가능 | EI_ERR_008-D |
| V-6 | tags 타입 | array\<string\> | EI_ERR_008-T |
| V-7 | source_refs 타입 | array\<string\> | EI_ERR_008-F |
| V-8 | masked 타입 | boolean | EI_ERR_008-B |
| V-9 | activation_state enum | `draft` \| `approved` \| `active` \| `deprecated` | EI_ERR_008-A |
| V-10 | L3/B-2 확장 필드 조건 | scope=L3 AND memory_type=B-2 → procedure_id 필수 | EI_ERR_008-L3 |
| V-11 | B↔L 매핑 정합 | B-4→L0, B-1→L1, B-3→L2, B-2→L3 (LOCK-MR-002) — 경고만, 차단 안 함 | EI_WARN_003 |

### 9.2 _validate_schema 구현

```python
def _validate_schema(self, data: dict) -> ValidationResult:
    """
    단일 레코드 스키마 검증.
    
    Returns:
        ValidationResult: valid=True/False, errors=list[str], warnings=list[str]
    """
    errors = []
    warnings = []
    
    # V-1: Required 필드
    required_fields = ["record_id", "project_id", "scope", "memory_type",
                       "content_summary", "created_at", "policy_decision"]
    for f in required_fields:
        if f not in data or data[f] is None:
            errors.append(f"EI_ERR_008-R: Required 필드 누락 — {f}")
    
    # V-2~V-4: enum 검증
    if data.get("scope") not in ("L0", "L1", "L2", "L3"):
        errors.append(f"EI_ERR_008-S: scope 값 유효하지 않음 — {data.get('scope')}")
    if data.get("memory_type") not in ("B-1", "B-2", "B-3", "B-4"):
        errors.append(f"EI_ERR_008-M: memory_type 값 유효하지 않음 — {data.get('memory_type')}")
    if data.get("policy_decision") not in ("allow", "restrict", "deny"):
        errors.append(f"EI_ERR_008-P: policy_decision 값 유효하지 않음 — {data.get('policy_decision')}")
    
    # V-5: created_at ISO 8601
    try:
        datetime.fromisoformat(data.get("created_at", ""))
    except (ValueError, TypeError):
        errors.append(f"EI_ERR_008-D: created_at ISO 8601 파싱 실패")
    
    # V-6: tags 타입 (optional)
    if "tags" in data and data["tags"] is not None:
        if not isinstance(data["tags"], list) or not all(isinstance(t, str) for t in data["tags"]):
            errors.append(f"EI_ERR_008-T: tags 타입 불일치 — array<string> 필요")
    
    # V-7: source_refs 타입 (optional)
    if "source_refs" in data and data["source_refs"] is not None:
        if not isinstance(data["source_refs"], list) or not all(isinstance(r, str) for r in data["source_refs"]):
            errors.append(f"EI_ERR_008-F: source_refs 타입 불일치 — array<string> 필요")
    
    # V-8: masked 타입 (optional)
    if "masked" in data and data["masked"] is not None:
        if not isinstance(data["masked"], bool):
            errors.append(f"EI_ERR_008-B: masked 타입 불일치 — boolean 필요")
    
    # V-9: activation_state enum (optional)
    if "activation_state" in data:
        if data["activation_state"] not in ("draft", "approved", "active", "deprecated"):
            errors.append(f"EI_ERR_008-A: activation_state 값 유효하지 않음 — {data['activation_state']}")
    
    # V-10: L3/B-2 확장 필드
    if data.get("scope") == "L3" and data.get("memory_type") == "B-2":
        if "procedure_id" not in data or not data["procedure_id"]:
            errors.append("EI_ERR_008-L3: L3/B-2 레코드에 procedure_id 누락")
    
    # V-11: B↔L 매핑 경고 (LOCK-MR-002)
    bl_map = {"B-4": "L0", "B-1": "L1", "B-3": "L2", "B-2": "L3"}
    expected_scope = bl_map.get(data.get("memory_type"))
    if expected_scope and data.get("scope") != expected_scope:
        warnings.append(
            f"EI_WARN_003: B↔L 매핑 불일치 — memory_type={data.get('memory_type')} "
            f"기본 scope={expected_scope}, 실제 scope={data.get('scope')}"
        )
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
```

---

## 10. 에러 코드 정의

| 코드 | 이름 | 설명 | 심각도 | 복구 가능 |
|------|------|------|--------|----------|
| EI_ERR_001 | ProjectIdRequiredError | project_id 누락 또는 빈 문자열 | CRITICAL | No (호출자 수정 필요) |
| EI_ERR_002 | CrossProjectError | 크로스 프로젝트 혼합 시도 (LOCK-MR-017 위반) | CRITICAL | No |
| EI_ERR_003 | ScopeApprovalError | L2/L3 내보내기 승인 미통과 | HIGH | Yes (승인 후 재시도) |
| EI_ERR_004 | ExportLimitExceededError | max_export_records 초과 | MEDIUM | Yes (필터 조정) |
| EI_ERR_005 | PIIMaskingIncompleteError | restrict 레코드 중 미마스킹 발견 | HIGH | Yes (마스킹 후 재시도) |
| EI_ERR_006 | FileNotFoundError | 가져오기 파일 없음 | CRITICAL | No (경로 수정 필요) |
| EI_ERR_007 | InvalidFormatError | 지원하지 않는 파일 형식 (.md 등) | CRITICAL | No |
| EI_ERR_008 | SchemaValidationError | 스키마 검증 실패 (하위 코드: R/S/M/P/D/T/F/B/A/L3) | HIGH | Partial (건별 스킵 가능) |
| EI_ERR_009 | ChecksumMismatchError | 파일 체크섬 불일치 (변조 의심) | CRITICAL | No (원본 확인 필요) |
| EI_ERR_010 | PIIDenyError | deny 레코드에 PII 탐지 (P1-7 연동) | CRITICAL | No |
| EI_ERR_011 | StorageWriteError | SQLite/저장소 쓰기 실패 | CRITICAL | Yes (재시도) |
| EI_ERR_012 | GraphImportError | KG 노드/엣지 가져오기 실패 (P1-4 연동) | HIGH | Yes (건별 스킵) |

| 경고 코드 | 설명 |
|-----------|------|
| EI_WARN_001 | 덮어쓰기로 인한 보안 약화 (deny→allow) |
| EI_WARN_002 | deprecated→active 복원 |
| EI_WARN_003 | B↔L 매핑 불일치 (LOCK-MR-002 경고) |

---

## 11. 복구/재시도 전략

### 11.1 Phase별 복구 전략

| Phase | 실패 지점 | 복구 전략 | 최대 재시도 |
|-------|----------|----------|-----------|
| **Export [3]** | SQLite 조회 실패 | 연결 재시도 → 실패 시 에스컬레이션 | 3회 |
| **Export [7]** | 파일 쓰기 실패 | 임시 파일(.tmp) → rename 패턴. 디스크 공간 확인 | 2회 |
| **Import [3]** | 체크섬 검증 실패 | 재시도 불가 — 원본 파일 재확인 요청 | 0회 |
| **Import [4]** | 스키마 검증 실패 | 건별 스킵 + 결과에 validation_errors 기록 | N/A (건별) |
| **Import [9]** | SQLite 쓰기 실패 | 배치 롤백 → 재시도. 전체 실패 시 partial result 반환 | 3회 |
| **Import [9]** | KG 노드/엣지 저장 실패 | 건별 스킵 + EI_ERR_012 기록. 메모리 레코드는 별도 저장 | N/A (건별) |

### 11.2 트랜잭션 보장 (V1 SQLite)

- Import 배치 처리는 SQLite 트랜잭션 내에서 수행.
- 배치 중 일부 실패 시 **해당 배치만 롤백**, 이전 배치는 커밋 유지.
- `dry_run=True` 시 트랜잭션을 시작하되 항상 롤백 (데이터 변경 없음).
- V1 단일 writer 패턴 준수: export/import 중 다른 writer 차단 (SQLite WAL 모드 + `PRAGMA busy_timeout=5000`).

### 11.3 원자적 파일 쓰기 (Export)

```python
def _write_export_file(self, data: ExportPayload, path: str, format: ExportFormat) -> str:
    """
    원자적 파일 쓰기: .tmp 파일에 먼저 쓴 후 rename.
    실패 시 .tmp 파일 정리.
    """
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            if format == ExportFormat.JSONL:
                self._write_jsonl_stream(f, data)
            elif format == ExportFormat.JSON:
                json.dump(data.to_dict(), f, ensure_ascii=False, indent=2)
            elif format == ExportFormat.MARKDOWN:
                self._write_markdown(f, data)
        os.replace(tmp_path, path)  # atomic rename
        return path
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
```

---

## 12. 에스컬레이션 정책

### 12.1 EscalationPayload 구조

> **정합 기준**: P1-4 (JsonGraphStore), P1-5 (SemanticCache) EscalationPayload JSON 구조와 동일 패턴.

```json
{
  "escalation_id": "ESC-EI-{uuid}",
  "timestamp": "2026-04-13T10:30:00Z",
  "source": "ExportImportManager",
  "severity": "WARN | ERROR | CRITICAL",
  "category": "EXPORT_IMPORT",
  "project_id": "proj_xxx",
  "operation": "export | import | validate | checksum",
  "error_type": "EI_ERR_001 | EI_ERR_009 | ...",
  "message": "사람이 읽을 수 있는 오류 설명",
  "record_id": null,
  "retry_count": 0,
  "recommended_action": "권장 조치 문자열",
  "auto_resolved": false,
  "details": {}
}
```

### 12.2 에스컬레이션 트리거 조건

| 조건 | 이벤트 | 심각도 | 권장 조치 |
|------|--------|--------|----------|
| Export 3회 재시도 후 SQLite 실패 | `ei.export.failed` | CRITICAL | SQLite 연결/잠금 상태 확인 |
| Import 체크섬 불일치 | `ei.checksum.mismatch` | CRITICAL | 파일 변조 가능성 — 원본 확인 |
| Import 중 deny 레코드 PII 탐지 | `ei.pii.deny_detected` | HIGH | PII 정책 위반 — 보안팀 알림 |
| Import 배치 3회 재시도 후 쓰기 실패 | `ei.import.failed` | CRITICAL | 디스크 공간/SQLite 상태 확인 |
| Export 중 미마스킹 restrict 레코드 50건 초과 | `ei.pii.masking_incomplete` | HIGH | PII 마스킹 파이프라인 점검 |

---

## 13. 로깅 규격 (R-01-7)

### 13.1 로그 이벤트 정의

| 이벤트 | 네임스페이스 | 레벨 | 필수 필드 |
|--------|------------|------|----------|
| 내보내기 시작 | `mem.export.start` | INFO | project_id, scope_filter, format |
| 내보내기 완료 | `mem.export.complete` | INFO | project_id, record_count, file_path, checksum, duration_ms |
| 내보내기 실패 | `mem.export.error` | ERROR | project_id, error_code, details |
| 가져오기 시작 | `mem.import.start` | INFO | project_id, file_path, conflict_strategy |
| 가져오기 완료 | `mem.import.complete` | INFO | project_id, inserted, updated, skipped, failed, duration_ms |
| 가져오기 실패 | `mem.import.error` | ERROR | project_id, error_code, details |
| 스키마 검증 실패 | `mem.import.validation_error` | WARN | project_id, record_id, errors |
| 충돌 해소 | `mem.import.conflict_resolved` | INFO | project_id, record_id, strategy, resolution |
| PII 경고 | `mem.export.pii_warning` | WARN | project_id, record_id, action |
| 체크섬 불일치 | `mem.import.checksum_mismatch` | ERROR | project_id, expected, actual |
| 사용자 확인 | `mem.import.user_confirmation` | INFO | project_id, action, result |
| project_id 재매핑 | `mem.import.project_remap` | INFO | original_project_id, target_project_id, record_count |

### 13.2 중첩 JSON 로그 구조

> **정합 기준**: P1-4 (JsonGraphStore §12), P1-5 (SemanticCache §13) 중첩 JSON 로그 패턴과 동일.

```json
{
  "log_id": "LOG-EI-{uuid}",
  "timestamp": "2026-04-13T10:30:00.123Z",
  "level": "INFO",
  "component": "ExportImportManager",
  "operation": "export",
  "project_id": "proj_investment_01",
  "entity_id": "export_file_20260413_abc.jsonl",
  "status": "SUCCESS",
  "duration_ms": 800,
  "details": {
    "record_count": 42,
    "file_path": "~/.vamos/exports/proj_abc123_20260413_abc.jsonl",
    "checksum": "sha256:abcdef...",
    "scopes_exported": ["L0", "L1"],
    "format": "jsonl",
    "skipped_deny_count": 0,
    "pii_warnings": []
  },
  "lock_checks": {
    "MR-017_project_isolation": "PASS",
    "MR-016_l3_approval": "N/A",
    "MR-018_user_confirmation": "PASS",
    "MR-015_deny_vector_block": "PASS"
  },
  "trace_id": "TRACE-{session_uuid}"
}
```

**Python 발행 예시**:

```python
import json, uuid, logging
from datetime import datetime, timezone

logger = logging.getLogger("vamos.export_import")

def _log(self, level: str, operation: str, project_id: str,
         status: str, duration_ms: float = 0, **extra) -> None:
    """중첩 JSON 로그 발행 — §13.2 구조 준수."""
    lock_checks = extra.pop("lock_checks", {
        "MR-017_project_isolation": "PASS" if status == "SUCCESS" else "N/A"
    })
    log_entry = {
        "log_id": f"LOG-EI-{uuid.uuid4()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "component": "ExportImportManager",
        "operation": operation,
        "project_id": project_id,
        "status": status,
        "duration_ms": duration_ms,
        "details": extra or {},
        "lock_checks": lock_checks,
    }
    logger.info(json.dumps(log_entry, ensure_ascii=False))
```

---

## 14. 시간복잡도 분석 (Big-O)

| 연산 | 시간복잡도 | 공간복잡도 | 설명 |
|------|-----------|-----------|------|
| `export_memories` | O(N + M + G) | O(N + M + G) | N=메모리 레코드, M=QoD 레코드, G=KG 노드+엣지 |
| `import_memories` | O(N * (V + D)) | O(B) | N=레코드 수, V=검증 O(1), D=중복 체크 O(1 SQLite 인덱스), B=batch_size |
| `_serialize_record` | O(F) | O(F) | F=필드 수 (최대 20) = O(1) |
| `_validate_schema` | O(F) | O(1) | F=필드 수 (최대 20) = O(1) |
| `_resolve_conflict` | O(1) | O(1) | SKIP/OVERWRITE=O(1), USER_CHOICE=사용자 대기 |
| `checksum 계산` | O(N * F) | O(1) (스트리밍) | N=전체 레코드, F=필드 수 |
| `_check_duplicate` | O(1) | O(1) | SQLite record_id 인덱스 기반 |

### 14.1 V1 성능 예상

- **Export 10,000건**: ~500ms (SQLite 조회) + ~200ms (직렬화) + ~100ms (파일 쓰기) = ~800ms
- **Import 10,000건**: ~1,000ms (검증) + ~500ms (중복 체크) + ~2,000ms (SQLite 배치 INSERT) = ~3,500ms
- **병목**: Import 시 SQLite 쓰기 (WAL 모드 + 배치 커밋으로 최적화)

---

## 15. 예외 처리 정책 표

| 예외 상황 | 에러 코드 | 동작 | 사용자 메시지 |
|----------|----------|------|-------------|
| project_id 누락 | EI_ERR_001 | 즉시 실패 | "프로젝트 ID가 필요합니다." |
| 크로스 프로젝트 혼합 | EI_ERR_002 | 즉시 실패 | "다른 프로젝트로 가져오기 시 project_id 재매핑이 필요합니다." |
| L3 승인 미통과 | EI_ERR_003 | 즉시 실패 | "L3 절차 메모리 내보내기에는 승인이 필요합니다." |
| 레코드 수 초과 | EI_ERR_004 | 즉시 실패 | "내보내기 상한(10,000건)을 초과합니다. 필터를 조정하세요." |
| PII 미마스킹 | EI_ERR_005 | 경고 + 계속 | "PII 마스킹이 완료되지 않은 레코드가 있습니다." |
| 파일 없음 | EI_ERR_006 | 즉시 실패 | "가져오기 파일을 찾을 수 없습니다." |
| 잘못된 형식 | EI_ERR_007 | 즉시 실패 | "지원하지 않는 파일 형식입니다. (JSON/JSONL만 지원)" |
| 스키마 검증 실패 | EI_ERR_008 | 건별 스킵 | "레코드 {record_id}의 스키마 검증 실패: {details}" |
| 체크섬 불일치 | EI_ERR_009 | 즉시 실패 | "파일 무결성 검증에 실패했습니다. 파일이 변조되었을 수 있습니다." |
| Deny PII 탐지 | EI_ERR_010 | 즉시 실패 | "보안 정책(deny)이 적용된 레코드에서 PII가 탐지되었습니다." |
| 저장소 쓰기 실패 | EI_ERR_011 | 재시도 3회 → 실패 | "저장소 쓰기에 실패했습니다. 디스크 공간을 확인하세요." |
| KG 가져오기 실패 | EI_ERR_012 | 건별 스킵 | "그래프 데이터 가져오기 부분 실패. 메모리 레코드는 정상 처리." |

---

## 16. 단위 테스트 시나리오

### 16.1 Export 테스트

| # | 테스트 ID | 시나리오 | 기대 결과 |
|---|----------|---------|----------|
| 1 | UT-EI-E01 | L0+L1 기본 내보내기 (JSONL) | ExportResult.success=True, record_count > 0, 파일 생성 |
| 2 | UT-EI-E02 | L3 내보내기 승인 거부 | EI_ERR_003 발생 |
| 3 | UT-EI-E03 | 빈 프로젝트 내보내기 | ExportResult.record_count=0, 파일 생성 (헤더만) |
| 4 | UT-EI-E04 | project_id 누락 | EI_ERR_001 발생 |
| 5 | UT-EI-E05 | deny 레코드 포함 내보내기 (include_denied=True) | content_summary 제외, 메타데이터만 포함 |
| 6 | UT-EI-E06 | PII 미마스킹 restrict 레코드 경고 | EI_ERR_005 경고 발생, 내보내기 계속 |
| 7 | UT-EI-E07 | max_export_records 초과 | EI_ERR_004 발생 |
| 8 | UT-EI-E08 | JSON 포맷 내보내기 | 유효한 JSON 파일, S7D-008 스키마 준수 |
| 9 | UT-EI-E09 | Markdown 포맷 내보내기 | 사람 읽기 가능한 Markdown 파일 |
| 10 | UT-EI-E10 | 체크섬 생성 검증 | SHA-256 체크섬이 파일 내용과 일치 |

### 16.2 Import 테스트

| # | 테스트 ID | 시나리오 | 기대 결과 |
|---|----------|---------|----------|
| 11 | UT-EI-I01 | 정상 JSONL 가져오기 | ImportResult.success=True, inserted_count=N |
| 12 | UT-EI-I02 | 체크섬 불일치 파일 | EI_ERR_009 발생 |
| 13 | UT-EI-I03 | Required 필드 누락 레코드 | EI_ERR_008-R, 해당 건 스킵 |
| 14 | UT-EI-I04 | 중복 record_id + SKIP 전략 | skipped_count 증가, 기존 유지 |
| 15 | UT-EI-I05 | 중복 record_id + OVERWRITE 전략 | updated_count 증가, 신규 데이터 반영 |
| 16 | UT-EI-I06 | project_id 재매핑 | 모든 레코드 target project_id로 변환 |
| 17 | UT-EI-I07 | 크로스 프로젝트 + remap=False | EI_ERR_002 발생 |
| 18 | UT-EI-I08 | dry_run=True | 데이터 변경 없음, 검증 결과만 반환 |
| 19 | UT-EI-I09 | L3/B-2 레코드 procedure_id 누락 | EI_ERR_008-L3 |
| 20 | UT-EI-I10 | .md 파일 가져오기 시도 | EI_ERR_007 발생 |

### 16.3 왕복 (Round-Trip) 테스트

| # | 테스트 ID | 시나리오 | 기대 결과 |
|---|----------|---------|----------|
| 21 | UT-EI-RT01 | Export → Import 왕복 무손실 (JSONL) | 모든 필드 값 동일, diff 없음 |
| 22 | UT-EI-RT02 | Export → Import 왕복 무손실 (JSON) | 모든 필드 값 동일, diff 없음 |
| 23 | UT-EI-RT03 | L3/B-2 확장 필드 왕복 | procedure_id, steps 등 7개 확장 필드 보존 |
| 24 | UT-EI-RT04 | source_qod 왕복 | QoD 8필드 전수 보존 |
| 25 | UT-EI-RT05 | kg_nodes + kg_edges 왕복 | KG 노드/엣지 전수 보존, project_id 재매핑 포함 |

---

## 17. Phase 2 통합 테스트

| # | 테스트 ID | 시나리오 | 관련 컴포넌트 | 기대 결과 |
|---|----------|---------|-------------|----------|
| 1 | IT-EI-01 | Export → 다른 프로젝트 Import | L0/L1 CRUD, ExportImport | project_id 재매핑 + 레코드 격리 |
| 2 | IT-EI-02 | Export 후 V1→V2 마이그레이션 로드 | ExportImport, D2.0-06 §2.4 | JSONL → Postgres COPY 경로 검증 |
| 3 | IT-EI-03 | PII 마스킹 후 Export | P1-7 PIIMasker, ExportImport | masked=True 레코드 정상 내보내기 |
| 4 | IT-EI-04 | Import + GraphRAG 연동 | P1-4 JsonGraphStore, ExportImport | KG 노드/엣지 정상 삽입 |
| 5 | IT-EI-05 | Import + Semantic Cache 무효화 | P1-5 SemanticCache, ExportImport | 가져온 데이터와 관련 캐시 무효화 |
| 6 | IT-EI-06 | 대용량 Import (10,000건) 배치 처리 | ExportImport, SQLite | 배치 커밋 + 전체 완료 |
| 7 | IT-EI-07 | Import 중 SQLite 장애 → 부분 복구 | ExportImport, SQLite | 실패 배치 롤백 + 이전 배치 유지 |
| 8 | IT-EI-08 | L3 Export → ApprovalGate 연동 | ExportImport, D7 ApprovalGate | 승인 없이 L3 내보내기 차단 |
| 9 | IT-EI-09 | 다른 기기 간 메모리 이전 (S7D-008) | ExportImport | 완전 왕복 무손실 |
| 10 | IT-EI-10 | B↔L 매핑 불일치 레코드 Import | ExportImport, LOCK-MR-002 | EI_WARN_003 경고 발행 + 저장 허용 |

---

## 18. 세션 간 인터페이스 cross-check

### 18.1 P1-1 (L0 Session Memory CRUD) 연동

| 인터페이스 | P1-6 사용 방식 | 정합 상태 |
|-----------|---------------|----------|
| `create_memory(project_id, scope="L0", ...)` | Import 시 L0 레코드 INSERT | OK — project_id 필수, LOCK-MR-017 |
| `read_memory(record_id, project_id)` | 중복 체크 시 기존 레코드 조회 | OK — record_id + project_id 기반 |
| `update_memory(record_id, project_id, ...)` | OVERWRITE 전략 시 기존 레코드 갱신 | OK |
| TTL 적용 | Import된 L0 레코드에 TTL 자동 적용 | OK — LOCK-MR-003: session_end or 30d |

### 18.2 P1-2 (L1 Project Memory CRUD) 연동

| 인터페이스 | P1-6 사용 방식 | 정합 상태 |
|-----------|---------------|----------|
| `create_memory(project_id, scope="L1", ...)` | Import 시 L1 레코드 INSERT | OK — TTL 90d, LOCK-MR-004 |
| `read_memory(record_id, project_id)` | 중복 체크 | OK |
| L0→L1 승격 | Import된 L0 레코드가 승격 조건 충족 시 | OK — 승격은 별도 트리거, Import 직접 관여 안 함 |

### 18.3 P1-4 (JSON GraphRAG) 연동

| 인터페이스 | P1-6 사용 방식 | 정합 상태 |
|-----------|---------------|----------|
| `add_node(node_type, label, project_id, properties)` | Import 시 kg_nodes 삽입 | OK — project_id 격리 |
| `add_edge(source_id, target_id, edge_type, project_id)` | Import 시 kg_edges 삽입 | OK |
| `get_node(node_id, project_id)` | 중복 노드 체크 | OK |

### 18.4 P1-5 (Semantic Cache) 연동

| 인터페이스 | P1-6 사용 방식 | 정합 상태 |
|-----------|---------------|----------|
| `invalidate_by_source(source_ref, project_id)` | Import 후 관련 캐시 무효화 (IT-EI-05) | OK — source_refs 기반 |

### 18.5 P1-7 (PII 마스킹) 연동 — P1-7 완료 (2026-04-13, 구 '미완' 표기 2026-06-11 정정; 통합 검증은 PENDING 유지)

| 인터페이스 | P1-6 사용 방식 | 정합 상태 |
|-----------|---------------|----------|
| `PIIMasker.detect(text)` | Import 시 PII 재탐지 | PENDING — P1-7 완료 후 통합 |
| `PIIMasker.mask(text)` | restrict 레코드 마스킹 | PENDING |

> **인터페이스 계약**: P1-7이 `detect(text) -> DetectionResult`와 `mask(text) -> str` 시그니처를 제공하면 §8.2의 `_recheck_pii_on_import()`를 활성화한다.

---

## 19. LOCK-MR 참조 추적표

| LOCK ID | 항목 | 본 문서 참조 위치 | 준수 방식 |
|---------|------|-----------------|----------|
| LOCK-MR-002 | B↔L 매핑 | §9 V-11 | B↔L 매핑 불일치 시 EI_WARN_003 경고 발행 |
| LOCK-MR-015 | Deny 벡터 삽입 금지 | §4.2 [4], §8 | deny 레코드 내보내기 시 content 제외, Import 시 벡터 삽입 안 함 |
| LOCK-MR-016 | L3 활성 게이트 | §3.1, §4.2 [2], §6.2 | L3 Export/Import 시 D7 ApprovalGate 확인 |
| LOCK-MR-017 | project_id 격리 | §7 전체 | Export/Import 전 경로에 project_id 파라미터 강제, 재매핑 메커니즘 |
| LOCK-MR-018 | 저장 전 사용자 확인 | §5.3 [8] | Import 실행 전 사용자 확인 (LOCK-MR-018 기본 정책) |
| LOCK-MR-019 | 루프 저장 폭주 방지 | §4.4 | content_summary만 직렬화 (원문 아닌 요약/메타) |

---

## 20. 교차 참조 블록

### 20.1 상위 문서 참조

| 참조 ID | 문서 | 구체 위치 | 관련 내용 |
|---------|------|----------|----------|
| REF-D206-S24 | D2.0-06 | §2.4 마이그레이션 원칙 | V1 JSONL/SQLite → V2 Postgres Export→Load 경로 |
| REF-D206-S7D008 | D2.0-06 | S7D-008 | 메모리 내보내기/가져오기 스키마, 중복 감지, 충돌 해소 |
| REF-D6-MRS | D6 | MemoryRecordSchema v3.0.0 | 전체 필드 정의 (Required 7 + Optional 6 + L3/B-2 7) |
| REF-D6-SQOD | D6 | SourceQoDSchema v3.0.0 | QoD 8필드 — 동반 내보내기/가져오기 |
| REF-P2-ITEM6 | Part2 V1-P2 | 항목6 | JSON/Markdown export/import, UI: Settings 뷰 버튼 |
| REF-D207-PII | D2.0-07 | §6.4 PII 정책 | restrict 마스킹, deny 차단 규칙 |

### 20.2 도메인 내 참조

| 참조 ID | 산출물 | 관련 내용 |
|---------|--------|----------|
| REF-P01-SCHEMA | P0-1 MemoryRecordSchema.md | 직렬화/역직렬화 필드 정의 정본 |
| REF-P11-L0CRUD | P1-1 L0_session_memory_crud.md | L0 CRUD 인터페이스 (Import INSERT 연동) |
| REF-P12-L1CRUD | P1-2 L1_project_memory_crud.md | L1 CRUD 인터페이스 (Import INSERT 연동) |
| REF-P14-GRAPH | P1-4 json_graphrag.md | KG 노드/엣지 Import 연동 |
| REF-P15-CACHE | P1-5 semantic_cache.md | Import 후 캐시 무효화 연동 |
| REF-P17-PII | P1-7 pii_masking.md (완료 2026-04-13 — 구 '미완' 표기 2026-06-11 정정) | PII 탐지/마스킹 인터페이스 계약 |

### 20.3 D2.0-06 §2.4 마이그레이션 원칙 정합 확인

> **D2.0-06 원문**: "V1에서 쌓인 JSONL/SQLite는 '내보내기(Export) → 적재(Load)' 경로로 V2(Postgres)로 이전 가능해야 한다. 이전은 스키마 정합(REF/ID/정책결과 링크)을 깨지 않는 방식으로만 수행한다."

| 정합 항목 | 본 문서 준수 여부 |
|----------|-----------------|
| JSONL 내보내기 포맷 | OK — ExportFormat.JSONL (기본) |
| 스키마 정합 (REF 보존) | OK — record_id, source_refs, policy_decision 전수 직렬화 |
| ID 링크 보존 | OK — record_id, source_id, node_id, edge_id 원본 유지 |
| 정책결과 링크 | OK — policy_decision 필드 필수 포함 |
| V2 Postgres 적재 호환 | OK — JSONL → COPY 명령 또는 행 단위 INSERT 가능한 구조 |

### 20.4 S7D-008 체크리스트 정합

| S7D-008 요건 | 본 문서 구현 | 상태 |
|-------------|-------------|------|
| JSON/SQLite 형식으로 전체 메모리 내보내기 | §2 JSON/JSONL 포맷 (SQLite 직접은 V2+) | OK |
| 스키마: {version, export_date, memories, kg_nodes, kg_edges} | §2.1 구조화 JSON 포맷 — 5개 필드 모두 포함 + source_qod 추가 | OK |
| 가져오기: 중복 감지 + 충돌 해소 | §6 ConflictStrategy 3종 (SKIP/OVERWRITE/USER_CHOICE) | OK |
| 백업 디렉토리 ~/.vamos/exports/ | §1.2 ExportImportConfig.export_dir 기본값 | OK |
| 다른 기기 간 메모리 이전 | §7 project_id 재매핑 + 왕복 무손실 | OK |

---

> **세션 종료 기록**
> - LOCK 변경: 0건 (LOCK-MR-002/015/016/017/018/019 무위반)
> - CONFLICT: 0건 (P1-6 신규 없음)
> - 이월: 없음
