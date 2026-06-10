# 03_backup-recovery — 백업 및 복구

> **도메인**: 6-13_Operations / 03_backup-recovery
> **Part2 출처**: §6.12.2 (L6021-6028)
> **LOCK**: LOCK-OP-01~06 (RPO/RTO V0~V3)

---

## Part2 원문 (When/Where)

| 버전 | 데이터 | RPO | RTO | 백업 방식 |
|------|--------|-----|-----|----------|
| V0-V1 | SQLite + Chroma + JSONL | 1일 | 30분 | git 커밋 + SQLite `.backup` (자동/수동) |
| V2 | PostgreSQL + Qdrant + Neo4j | 1시간 | 2시간 | pg_dump cron (6h), Qdrant snapshot, Neo4j backup |
| V3 | 관리형 DB + PVC | 15분 | 30분 | RDS 자동 백업 + PVC 스냅샷 + Velero K8s 백업 |

## SOT2 상세 (What/How)

### V0-V1 백업 절차

```bash
# 자동 백업 (git pre-commit hook)
sqlite3 data/vamos.db ".backup data/backup/vamos_$(date +%Y%m%d).db"
# 수동 복구
cp data/backup/vamos_YYYYMMDD.db data/vamos.db
```

### V2 백업 cron 설정

```
0 * * * * pg_dump -Fc vamos > /backup/pg_$(date +\%Y\%m\%d_\%H).dump
0 2 * * *   curl -XPOST http://qdrant:6333/collections/vamos/snapshots
0 3 * * *   neo4j-admin database dump neo4j --to-path=/backup/neo4j_$(date +\%Y\%m\%d)
```

### 복구 테스트 일정

| 버전 | 테스트 주기 | 테스트 내용 |
|------|-----------|-----------|
| V0-V1 | 월 1회 | git restore + SQLite 복구 확인 |
| V2 | 격주 1회 | pg_restore + Qdrant 스냅샷 복원 |
| V3 | 주 1회 | Velero restore + PVC 복원 + DR 시뮬레이션 |

### 구현 시 결정 (§6.12.12 관련)

- 백업 주기: V0-V1은 git 커밋, V2는 6시간 (RPO 1시간 보장), V3는 자동
- DR(재해복구): V0-V1 해당없음, V2 리전 내, V3 멀티 리전

## 하위 파일 (Phase 예정)

| 파일 | 내용 | 상태 |
|------|------|------|
| `backup_scripts.md` | 버전별 백업 스크립트 + cron 설정 | 예정 |
| `recovery_runbook.md` | 복구 절차 런북 + 테스트 체크리스트 | 예정 |
