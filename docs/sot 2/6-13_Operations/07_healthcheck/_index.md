# 07_healthcheck — 헬스체크

> **도메인**: 6-13_Operations / 07_healthcheck
> **Part2 출처**: §6.12.6 (L6059-6066)
> **LOCK**: LOCK-OP-09 (V1: 30초 / V2: 15초 / V3: 10초)

---

## Part2 원문 (When/Where)

| 버전 | 대상 | 방식 | 주기 | 실패 시 |
|------|------|------|------|---------|
| V0-V1 | Python 프로세스 | `/health` HTTP (200 OK) | 30초 | 프로세스 재시작 |
| V2 | Docker 컨테이너 | `HEALTHCHECK CMD curl -f http://localhost:8000/health` | 15초 | Docker restart policy |
| V3 | K8s Pod | `livenessProbe` + `readinessProbe` (HTTP/TCP) | 10초 | Pod 재시작 + 자동 스케줄링 |

## SOT2 상세 (What/How)

### 헬스체크 엔드포인트 스펙

```json
GET /health
Response 200:
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "checks": {
    "database": "ok",
    "redis": "ok",
    "llm_api": "ok",
    "disk_space": "ok"
  }
}

Response 503:
{
  "status": "unhealthy",
  "checks": {
    "database": "ok",
    "redis": "fail",
    "llm_api": "timeout"
  }
}
```

### 의존성 체크 항목

| 의존성 | 체크 방법 | 실패 시 |
|--------|----------|---------|
| SQLite/PostgreSQL | SELECT 1 | 서비스 unhealthy |
| Redis | PING | 캐시 폴백 (인메모리 dict) |
| LLM API | 최소 인증 프로브 (짧은 타임아웃, HTTP 200/인증 성공 확인) | Ollama 로컬 폴백 |
| 디스크 | 여유 공간 > 1GB | 로그 로테이션 강제 실행 |

### 구현 시 결정 (§6.12.12 관련)

- 헬스체크 주기: V1 60초→30초, V2 30초→15초, V3 15초→10초 (실측 후 확정)

## 하위 파일 (Phase 예정)

| 파일 | 내용 | 상태 |
|------|------|------|
| `endpoint_spec.md` | /health 엔드포인트 상세 스펙 | 예정 |
| `dependency_checks.md` | 의존성 체크 항목 + 폴백 매핑 | 예정 |
