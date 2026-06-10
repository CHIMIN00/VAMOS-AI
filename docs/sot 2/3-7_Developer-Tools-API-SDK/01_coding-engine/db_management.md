# 데이터베이스 관리 도구

> **L-ID**: L-027
> **V 배정**: V1 (Text-to-SQL 즉시)
> **Phase**: Phase 1 P1-1
> **수준**: L2 (D1 + D2 + D3)
> **의존 LOCK**: LOCK-DT-06 (코드 실행 타임아웃 30초)

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|----------|----------|
| STEP7-L L-027 | 데이터베이스 관리 도구 구현 상세 |
| L-001 dev_node_architecture.md | 코딩 엔진 아키텍처 |

---

## D1. Input Schema

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class DBOperation(Enum):
    TEXT_TO_SQL = "text_to_sql"
    QUERY_OPTIMIZE = "query_optimize"
    MIGRATION_GENERATE = "migration_generate"
    SCHEMA_ANALYZE = "schema_analyze"
    ROLLBACK_GENERATE = "rollback_generate"

class DBType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"

@dataclass
class DBManagementRequest:
    """DB 관리 요청"""
    operation: DBOperation
    db_type: DBType
    natural_query: Optional[str] = None       # TEXT_TO_SQL
    sql_query: Optional[str] = None           # QUERY_OPTIMIZE
    schema_definition: Optional[str] = None   # 현재 스키마
    schema_change: Optional[str] = None       # MIGRATION_GENERATE
    timeout_ms: int = 30000                   # LOCK-DT-06
    trace_id: Optional[str] = None
```

---

## D2. Output Schema

```python
@dataclass
class DBManagementResponse:
    """DB 관리 응답"""
    status: str
    generated_sql: Optional[str] = None
    optimized_sql: Optional[str] = None
    migration_script: Optional[str] = None
    rollback_script: Optional[str] = None
    schema_analysis: Optional[dict] = None
    explanation: str = ""
    confidence: float = 0.0
    visualization_data: Optional[dict] = None  # 결과 시각화용
    latency_ms: float = 0.0
    trace_id: Optional[str] = None
```

---

## D3. Algorithm

```
시간복잡도: O(S + L)
  S: 스키마 분석 O(T) — T=테이블 수
  L: LLM 생성 O(T_out) — T_out=출력 토큰
```

```python
async def manage_db(request: DBManagementRequest) -> DBManagementResponse:
    """
    DB 관리 파이프라인.
    ABC 패턴: SchemaParser → QueryGenerator → Validator
    """
    if request.operation == DBOperation.TEXT_TO_SQL:
        # 1. 스키마 자동 인식
        schema = parse_schema(request.schema_definition, request.db_type)
        # 2. 자연어 → SQL 생성
        sql = await llm_text_to_sql(
            request.natural_query, schema, request.db_type
        )
        # 3. SQL 검증
        is_valid = validate_sql(sql, schema)
        return DBManagementResponse(
            status="success", generated_sql=sql,
            confidence=0.9 if is_valid else 0.5
        )
    
    elif request.operation == DBOperation.QUERY_OPTIMIZE:
        optimized = await optimize_query(request.sql_query, request.db_type)
        return DBManagementResponse(
            status="success", optimized_sql=optimized,
            explanation=explain_optimization(request.sql_query, optimized)
        )
    
    elif request.operation == DBOperation.MIGRATION_GENERATE:
        migration = generate_migration(
            request.schema_change, request.db_type
        )
        rollback = generate_rollback(migration)
        return DBManagementResponse(
            status="success",
            migration_script=migration,
            rollback_script=rollback
        )
    
    elif request.operation == DBOperation.SCHEMA_ANALYZE:
        schema = parse_schema(request.schema_definition, request.db_type)
        analysis = analyze_schema(schema, request.db_type)
        return DBManagementResponse(
            status="success", schema_analysis=analysis
        )
    
    elif request.operation == DBOperation.ROLLBACK_GENERATE:
        rollback = generate_rollback(request.schema_change)
        return DBManagementResponse(
            status="success", rollback_script=rollback
        )
    
    else:
        raise ValueError(f"Unsupported DBOperation: {request.operation}")
    
    elif request.operation == DBOperation.SCHEMA_ANALYZE:
        schema = parse_schema(request.schema_definition, request.db_type)
        analysis = analyze_schema(schema, request.db_type)
        return DBManagementResponse(
            status="success", schema_analysis=analysis
        )
    
    elif request.operation == DBOperation.ROLLBACK_GENERATE:
        rollback = generate_rollback(request.schema_change)
        return DBManagementResponse(
            status="success", rollback_script=rollback
        )
    
    else:
        raise ValueError(f"Unsupported DBOperation: {request.operation}")
```

---

## D4. Error Handling

| 에러 코드 | recoverable | 처리 |
|-----------|-------------|------|
| E_SCHEMA_NOT_FOUND | Yes | 스키마 없이 일반 SQL 생성 |
| E_INVALID_SQL | Yes | 재생성 (다른 프롬프트) |
| E_DB_CONNECT_FAIL | No | 연결 정보 확인 안내 |

---

## D5. Dependencies

| 의존성 | 용도 |
|--------|------|
| sqlparse | SQL 파싱/검증 |
| alembic | Python DB 마이그레이션 |
| LLM API | Text-to-SQL |

---

## D6. Performance

| 메트릭 | 목표 |
|--------|------|
| Text-to-SQL | < 5초 |
| 쿼리 최적화 | < 10초 |
| 마이그레이션 생성 | < 15초 |

---

## D7. Test Spec — Phase 2 테스트 시나리오

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T1 | 자연어 → SELECT | "매출 100억 이상 종목" | 유효 SELECT 쿼리 |
| T2 | JOIN 쿼리 생성 | 2테이블 관계 질의 | 정확한 JOIN SQL |
| T3 | 쿼리 최적화 | N+1 패턴 SQL | 최적화된 SQL + 설명 |
| T4 | 마이그레이션 생성 | 컬럼 추가 스키마 변경 | ALTER TABLE 스크립트 |
| T5 | 롤백 스크립트 | 마이그레이션 역방향 | 롤백 가능한 스크립트 |
| T6 | MongoDB 쿼리 | db_type=MONGODB | MongoDB 쿼리 구문 |
| T7 | 스키마 분석 | 복잡한 스키마 입력 | 관계 분석 + 인덱스 제안 |
| T8 | 잘못된 자연어 | 모호한 질의 | 명확화 요청 |
| T9 | 빈 스키마 | schema_definition=None | 일반 SQL + 경고 |
| T10 | 다운타임 없는 마이그레이션 | 대규모 테이블 변경 | 온라인 DDL 제안 |

---

## D8. Security

- 생성된 SQL에 DROP/TRUNCATE 시 사용자 확인 필수
- SQL 인젝션 방지: 파라미터 바인딩 권장
- LOCK-DT-06: DB 쿼리 실행 30초 타임아웃
