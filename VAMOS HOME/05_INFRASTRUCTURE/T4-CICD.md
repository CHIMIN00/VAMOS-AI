---
tags: [tier/T4, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [4-2, CI/CD 파이프라인, CICD-Pipeline]
tier: T4
domain: "4-2 CICD-Pipeline"
sot_source: "D:\\VAMOS\\docs\\sot 2\\4-2_CICD-Pipeline\\"
design_doc: "[[D2.0-04-Infra]]"
quality_gate: "APPROVED — Phase 4 RECOVERY 도메인 종료 (10 V3 NEW, CFL OPEN 4→0, 2026-06-01)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P0 GATE PASS → P1 | V2: Docker Compose/K8s+ArgoCD | V3: 런북/장애대응 10 NEW"
created: 2026-06-11
---

# 4-2 CICD-Pipeline

## 한줄 요약
GitHub Actions 14개 워크플로우·브랜치 전략·커버리지 게이트·보안 스캔·배포 승인을 관장하는 CI/CD 정본 도메인.

## 핵심 정의
- 워크플로우 14개: ci/test/lint/build-tauri/release/deploy-staging/deploy-prod/security-scan/benchmark/docs-build/dependency-check/e2e-test/nightly/version-bump
- 권한 체계: PLAN-3.0 → D2.0 → PHASE_B6(CI/CD 전략 정본) → Part2 §V1-P6 → sot 2/4-2 → .github/workflows
- Docker V2 6서비스: orange-core, blue-nodes, api-gateway, postgres, qdrant, neo4j

## LOCK 항목 (LOCK-CI-01~12, 12건)
- CI-01 워크플로우 14개 목록 / CI-02 브랜치 전략 main·develop·feature·hotfix·release
- CI-03 커버리지 게이트 Python≥75%·Rust≥80%·React≥80% / CI-04 SemVer 2.0.0 / CI-05 Conventional Commits
- CI-06 Tauri 빌드 매트릭스 4플랫폼(Linux x64·Win x64·macOS ARM64/x64, F-15 옵션 B 보존)
- CI-07 코드 서명(Apple Dev ID·EV·GPG) / CI-08 보안 스캔 5도구(pip-audit·cargo-audit·semgrep·trufflehog·trivy)
- CI-09 CVE Critical/High 즉시 실패 / CI-10 프로덕션 배포 2인 승인 / CI-11 concurrency cancel-in-progress / CI-12 Docker V2 6서비스

## 의존성 (Depends On)
- [[T6-Security]] — SAST/DAST 스캔 정책 / [[T6-Operations]] — 배포 롤백·인시던트 대응
- [[T4-Rust-Tauri]] — Tauri 빌드 설정 (양방향 B11) / [[T0-Governance]] — R1~R11

## 제공 (Provides To)
- [[T4-Rust-Tauri]] — 빌드 워크플로우 (양방향) / [[T4-MLOps]] — 인프라 배포 게이트 (양방향 B12)
- [[T5-Benchmark]] — 커버리지 게이트·e2e-test 워크플로우 경계 공유

## 횡단 개념 연결
- [[SLA-Performance-Targets]] — 14 WF 실행 시간 baseline / [[Cost-Limits]] — 배포 게이트 비용 검증

## STEP7 매핑
- 출처: PHASE_B6_CICD_PIPELINE.md (Part2는 14 YAML 파일명만 — PARTIAL)

## 버전별 범위
- V1: 14 WF + 브랜치 전략 / V2: docker_compose·k8s_argocd·optimization·benchmark_baseline 4 NEW (2,268L) / V3: 런북 5 + 장애대응 4 + cross-validation 1 (68,767B)

## 검증 상태
- Quality Gate: APPROVED — Phase 4 RECOVERY Wave 1 #10 (2026-06-01), CFL OPEN 0
- LOCK 검증: 12/12 일치 (AUTHORITY_CHAIN v1.3, set accuracy 12 unique 보존)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\4-2_CICD-Pipeline\
- Authority: 4-2_CICD-Pipeline\AUTHORITY_CHAIN.md (v1.3)
- Design: PHASE_B6 + [[D2.0-04-Infra]]
