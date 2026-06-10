# 12_cloud-library-failover — Cloud Library 페일오버

> **도메인**: 6-13_Operations / 12_cloud-library-failover
> **Part2 출처**: §6.12.11 (L6104-6113)
> **참조 도메인**: 6-8_Cloud-Library (클라우드 배포 아키텍처 정본)
> **LOCK**: (해당 없음 — 페일오버 RTO는 Part2 원문 참조)

---

## Part2 원문 (When/Where)

| 구성요소 | 주 경로 | 페일오버 | RTO |
|---------|--------|---------|-----|
| Vector DB (Chroma/Qdrant) | 로컬/Docker 인스턴스 | SQLite FTS5 키워드 검색 폴백 | 즉시 |
| LLM API (GPT-4o) | 직접 API 호출 | Ollama 로컬 모델 전환 | ~10초 |
| Redis (V2+) | Docker Redis | 인메모리 dict 캐시 폴백 | 즉시 |
| PostgreSQL (V2+) | Docker 인스턴스 | SQLite 임시 전환 (읽기 전용) | ~30초 |
| K8s 클러스터 (V3) | 주 노드풀 | Spot→On-Demand 전환 + Pod 재스케줄링 | 2-5분 |

## SOT2 상세 (What/How)

### 페일오버 트리거 조건

| 구성요소 | 트리거 | 자동/수동 |
|---------|--------|----------|
| Vector DB | 연속 3회 쿼리 실패 | 자동 |
| LLM API | API 응답 타임아웃 5초 (재시도 1회) | 자동 |
| Redis | PING 실패 3회 | 자동 |
| PostgreSQL | 연결 풀 고갈 또는 연결 불가 | 자동 (읽기), 수동 (쓰기) |
| K8s | Spot 인스턴스 회수 알림 | 자동 (Pod 재스케줄링) |

### LLM API → Ollama 전환 절차

1. LLM API 타임아웃 감지 (30초)
2. 6-12 Event-Logging 정본 이벤트 `cl.rt.source.disconnected` 발행 (6-12 발행 표준/스키마 인용 only — 6-13은 신규 이벤트 정의 금지, 도메인 경계 §7)
3. Ollama 로컬 모델 로드 확인 (`/api/tags`)
4. 라우팅 전환: `LLM_PROVIDER=ollama`
5. 사용자 알림: "로컬 모델로 전환 — 응답 품질 저하 가능"
6. 원본 API 60초 간격 재시도

### PostgreSQL → SQLite 임시 전환

- 읽기 전용 모드: 기존 SQLite 백업 파일에서 읽기 (Part2 §6.12.11 '읽기 전용' 정본 준수)
- 쓰기 거부: 모든 쓰기 요청은 명시적 오류(503 ServiceUnavailable, "읽기 전용 모드 — 쓰기 불가")로 즉시 반려 (버퍼링 없음, 데이터 유실 경로 제거)
- 클라이언트는 쓰기 실패를 상위로 전파하여 재시도 책임을 보유
- PG 복구 시: 읽기 전용 모드 해제 후 정상 쓰기 재개, audit log에 모드 진입/해제 시각 기록

### 페일오버 테스트 절차

| 주기 | 테스트 | 방법 |
|------|--------|------|
| 월 1회 | LLM API 페일오버 | API 키 임시 무효화 → Ollama 전환 확인 |
| 월 1회 | Redis 페일오버 | Docker Redis 정지 → dict 캐시 전환 확인 |
| 분기 1회 | PostgreSQL 페일오버 | PG 연결 차단 → SQLite 읽기 전환 확인 |

## 하위 파일 (Phase 예정)

| 파일 | 내용 | 상태 |
|------|------|------|
| `failover_matrix.md` | 구성요소별 페일오버 매트릭스 + 트리거/RTO | 예정 |
| `failover_test_plan.md` | 페일오버 테스트 절차 + 체크리스트 | 예정 |
