# VAMOS 버전/릴리스 전략 — release_strategy.md (3-10, X1)

> **확정일**: 2026-06-12 (P3-2) · **우선순위**: Should · **매트릭스 셀**: X1 (버전/릴리스 전략 ⑥⑦⑧)
> **위상 (로드맵 L293)**: 기존 정본(PHASE_B6 CICD·PHASE_B7 MIGRATION·STRATEGY_06 A23)의 **결정 요약 + 로드맵 바인딩**. 정본 무대체, 충돌 시 정본 우선.

## 1. Git 브랜치 전략

- **기본 브랜치 = `main`** (release tag 부착 + ff-only 동기화)
- 작업 브랜치: `phase{N}-*` (현행 phase01-targeted-fixes) → feature/* (V1+ 본격 개발 시 `feature/*` 도입)
- **병합 정책 (P3-0 PHASE3-GATE-08 확정)**: 각 Phase 게이트 완료 커밋·태그 이후 `main`을 **`--ff-only`로 동기화 + push**. 체크아웃 왕복 금지 — `git fetch . <branch>:main`(작업 트리 비접촉)으로 수행 (autocrlf EOL 손상 방지, [[git-eol-autocrlf-checkout-hazard]] 규칙)
- X1 매트릭스 셀 표기 `main/develop/feature/*`는 V1+ 본격 개발 시점 정식 채택 — V0까지는 main + phase 브랜치로 충분

## 2. Semantic Versioning (SemVer)

- 규칙: `MAJOR.MINOR.PATCH` — 정본 문서 자체가 SemVer 사용 (PHASE_B7 v1.0.0)
- VAMOS 버전 사이클 ↔ SemVer 매핑:
  | VAMOS | SemVer | 게이트 | tag |
  |-------|--------|--------|-----|
  | V0 | v0.x | Phase 5 GO/NO-GO 16항 | (개발 단계) |
  | V1 | v1.0.0 | Phase 6 V1 GO 22항(§7.2) | `v1-release` |
  | V2 | v2.0.0 | Phase 7 V2 GO 14항(§7.3) | `v2-release` |
  | V3 | v3.0.0 | Phase 8 V3 GO 12항(§7.4) | `v3-release` |
- Phase 게이트 tag(phase{N}-complete)는 개발 추적용, v{N}-release는 제품 릴리스용 — 별개 네임스페이스

## 3. V0→V1→V2→V3 릴리스 기준
- 각 사이클 진입 = 직전 사이클 GO/NO-GO 전항목 PASS (분모: V0 16 / V1 22 / V2 14 / V3 12)
- V1 활성 모듈 = **CORE 32** (PHASE3-GATE-03 확정 — PART2 §1.1; STRATEGY_08 매트릭스 "26"은 구집계, 충돌 시 PART2 우선)

## 4. Expand/Contract 마이그레이션 (A23 — STRATEGY_06 §3.2)
- **3단계**: Expand(새 필드 optional 추가) → Migrate(점진 전환) → Contract(기존 필드 제거, V2까지 미룸 가능)
- **V0→V1 = Expand 단계만 적용** (Contract 금지 — §3.4 체크리스트)
- config 규칙: 기존 키 삭제 금지 / 새 키 기본값 필수 / **LOCK 키 변경 = Approval Gate 필수**
  - 예 (PHASE3-DEC-010 정합): `confidence_refuse_threshold = 0.30 (LOCK)` 신규 추가 = Expand → config 분모 20→23. `cost_monthly_limit = 40000` 등 기존 LOCK 키 전부 유지
- V0→V1 체크리스트: 스키마 Expand만 / config 기존 키 유지+새 키 기본값 / 모듈 OFF→ON은 config 수준 / **V0 테스트 케이스가 V1에서도 PASS**(왕복)

## 5. X2/X3 실행·운영 바인딩
- X2: 브랜치 관리 + PR 규칙 + **commitlint**(Phase 2 commitlint.config.js 기존재) + 커밋 메시지 린트
- X3: 버전 릴리스 + 핫픽스 관리 + 릴리스 노트
- CI/CD 정본: **PHASE_B6 §2 ci.yml 단일 통합**(Phase 2 기구축 — quality/test/vamos-lint 3 job). V1 역할별 분리 yml(PART2 §6.4 11종)은 V1 시점

## 6. 회귀 정합
- A24 배포 무결성(Smoke Test) → Phase 5/6 배포 시 / Phase 2 ci.yml·commitlint와 모순 0 — 본 전략은 그 위 바인딩

## 정본 인용
STRATEGY_06 §3.2 L107-153(Expand/Contract)·§3.3(config 규칙) · PHASE_B6 §2(ci.yml) · PHASE_B7 v1.0.0(SemVer) · STRATEGY_08 X1 셀 ⑥⑦⑧ · PHASE3-GATE-03/08 · PHASE3-DEC-010
