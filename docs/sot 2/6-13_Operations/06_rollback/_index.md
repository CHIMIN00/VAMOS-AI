# 06_rollback — 롤백 프로세스

> **도메인**: 6-13_Operations / 06_rollback
> **Part2 출처**: §6.12.5 (L6051-6058)
> **LOCK**: LOCK-OP-12 (P0 시 즉시 롤백)

---

## Part2 원문 (When/Where)

| 버전 | 롤백 방식 | 소요 시간 | 자동화 |
|------|----------|----------|--------|
| V0-V1 | git revert + 재빌드 | 5-10분 | 수동 |
| V2 | Docker Compose 이전 이미지 태그로 재배포 | 2-3분 | CI/CD 트리거 |
| V3 | K8s Blue-Green 스위치백 | 30초 | Helm rollback 자동 |

## SOT2 상세 (What/How)

### 롤백 판단 기준

| 조건 | 판단 | 조치 |
|------|------|------|
| P0 인시던트 | 즉시 롤백 (LOCK-OP-12) | 원인 분석은 롤백 후 수행 |
| P1 인시던트 + Fallback 실패 | 롤백 | Fallback 먼저 시도, 실패 시 롤백 |
| P2 + 핫픽스 가능 | 핫픽스 우선 | 핫픽스 1시간 내 불가 시 롤백 |
| 배포 후 에러율 > 5% | 자동 롤백 (V3) | Canary 배포 실패 시 자동 |

### V2 롤백 실행

```bash
# 이전 이미지 태그로 롤백 (Part2 §6.12.5 '이전 이미지 태그로 재배포' 정본)
# 1) 직전 정상 이미지 태그 확보 후 compose env에 반영 (필수 — 미반영 시 동일 실패 이미지 재사용)
export PREVIOUS_IMAGE_TAG="$(cat .last_good_image_tag)"
sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=${PREVIOUS_IMAGE_TAG}/" .env.prod
# 2) 이전 태그 이미지로 재배포
docker compose -f docker-compose.prod.yml --env-file .env.prod down
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
# 데이터 롤백 주의: DB 스키마 변경 시 별도 마이그레이션 롤백 필요
```

### 데이터 롤백 주의사항

- DB 스키마 변경이 포함된 배포: 반드시 `down migration` 준비
- Redis 캐시: 롤백 시 flush 필요 (stale 데이터 방지)
- Qdrant 인덱스: 스키마 호환 확인 후 롤백 (비호환 시 재색인)

## 하위 파일 (Phase 예정)

| 파일 | 내용 | 상태 |
|------|------|------|
| `rollback_runbook.md` | 버전별 롤백 실행 절차 + 명령어 | 예정 |
| `data_rollback_guide.md` | 데이터 롤백 주의사항 + 마이그레이션 관리 | 예정 |
