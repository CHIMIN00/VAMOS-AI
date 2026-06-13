# Alembic 마이그레이션 — VAMOS V1 데이터 계층

> **근거**: PHASE5-DEC-001 item 16 (Alembic 초기 마이그레이션) · STRATEGY_06 §3.4 A23 (V0→V1 마이그레이션) · 세션 P6-1a (2026-06-13)

## 목적

V0는 `vamos_core/storage/memory_store.py`의 `CREATE TABLE IF NOT EXISTS`로 SQLite 스키마를 멱등 초기화했다(Alembic 미채택, PHASE5-DEC-001 item 16). V1 진입 시 본 디렉토리가 그 스키마를 **Alembic baseline(rev `0001_v0_baseline`)으로 동결**하고, 이후 스키마 변경을 revision 체인으로 관리한다.

## A23 V0→V1 마이그레이션 규칙 (STRATEGY_06 §3.4)

### 스키마 = Expand / Contract 3단계
1. **Expand** — 새 필드는 기존 필드 유지한 채 optional 추가 (예: `confidence_score REAL`). 기존 코드는 무시 → 무중단.
2. **Migrate** — 코드를 새 필드 사용으로 점진 전환.
3. **Contract** — 모든 코드가 새 필드 사용 확인 후에만 구 필드 제거. **V1 안정화 후(또는 V2까지 유지)**.

> env.py는 `render_as_batch=True` — SQLite의 `ALTER TABLE` 제약(컬럼 DROP/타입변경 불가)을 batch 모드로 우회해 Expand/Contract를 안전 수행한다.

### config 키 호환
- 기존 키 삭제 금지(하위 호환). 새 키 추가 시 기본값 필수. LOCK 키 변경은 Approval Gate 필수.
- DB URL은 `alembic/env.py`가 `VAMOS_DB_PATH > config.storage.db_path(${VAMOS_DATA_DIR} 치환) > ./data/sqlite/vamos.db` 순으로 해석 — 환경/배포별 data_dir 차이 흡수.

### 모듈 활성화 / 데이터 호환
- 모듈 OFF→ON은 config 수준(코드 변경 없이).
- **V0 SQLite 데이터 → V1 읽기 가능**(스키마 호환). baseline revision은 V0 스키마와 **의미적으로 동일**(테스트로 강제).

## baseline revision (`0001_v0_baseline`)

- `upgrade()`: `CREATE TABLE/INDEX IF NOT EXISTS` — 기존 V0 `vamos.db`에 실행해도 **no-op**(데이터·스키마 보존). 신규 db에는 V0 동일 스키마 생성.
- SQL은 V0 시점 `memory_store.py`(`_CREATE_TABLE`/`_CREATE_INDEXES`, PART2 L1260~1275 정본)에서 **frozen 복사**(마이그레이션 불변성 원칙). drift는 `tests/test_alembic_baseline.py`가 두 경로의 스키마 지문(PRAGMA)을 대조해 차단.
- `downgrade()`: **파괴적**(DROP — V0 데이터 전체 손실). 운영 db 절대 자동 실행 금지(II-1).

## 사용

```bash
cd backend
# 신규 db 생성(또는 최신화)
poetry run alembic upgrade head
# 기존 V0 vamos.db 무손실 등록(테이블 재생성 없이 버전만 기록)
poetry run alembic stamp 0001_v0_baseline
# 새 스키마 변경(Expand) revision 작성
poetry run alembic revision -m "expand: add <field>"
```

## 검증 (tests/test_alembic_baseline.py)

1. **drift-guard** — `alembic upgrade` 스키마 == `memory_store.init()` 스키마 (PRAGMA 지문 동일).
2. **V0 read-compat** — 기존 V0 데이터 db에 `upgrade` → 데이터 무손실.
3. **stamp** — 기존 V0 db `stamp` → `alembic_version` 기록 + 데이터·테이블 보존.
