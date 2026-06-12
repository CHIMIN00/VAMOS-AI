# VAMOS 횡단 엔지니어링 계획서 — cross_eng_plan.md (3-13)

> **확정일**: 2026-06-12 (P3-2) · **우선순위**: Should · **매트릭스 셀**: X2(횡단 실행) → X3(횡단 운영) → XF(역류)
> **입력**: X1 4개 전략(security/test/release/doc_strategy.md) · **위상**: 결정 요약 + 로드맵 바인딩, 정본 무대체

## 1. X1 4전략 → X2/X3 실행·운영 매핑

| X1 전략 | X2 실행 | X3 운영 |
|---------|---------|---------|
| 보안(3-8) | OWASP Top10 스캔 + PII 필터 검증 + consent 검증 | 정기 보안 감사 + 취약점 패치 |
| 테스트(3-9) | 단위(B2 동시)+통합(R2a+R2b)+E2E(R2c) 작성 | 회귀 테스트 자동 스케줄 |
| 릴리스(3-10) | 브랜치/PR 규칙 + commitlint | 버전 릴리스 + 핫픽스 |
| 문서화(3-11) | 코드 변경→VAMOS HOME 갱신 | 지식 그래프 최신성 유지 |

## 2. X2: 횡단 실행 (Phase 4~5)
- **입력**: X1 4전략 + B2/R2 코드 산출물
- **보안 실행**: OWASP Top10 코드 스캔(Critical 0) + PII 필터링 파이프라인 + consent 로직 검증 (security_strategy §6)
- **테스트 실행**: 단위 80%+/통합 60%+/E2E 100% (test_strategy §1) — pytest/cargo test/vitest/Playwright
- **버전 관리**: 브랜치+PR 규칙 + commitlint(Phase 2 기존재) (release_strategy §5)
- **문서화**: 코드 변경 시 VAMOS HOME 갱신 (doc_strategy §2)
- **완료조건**: 보안 Critical 0 + 테스트 커버리지 ≥80% + commitlint PASS
- **자동화**: CI 통합(Phase 2 ci.yml 3 job) + 수동(보안 리뷰)

## 3. X3: 횡단 운영 (Phase 6)
- **입력**: X2 실행 결과(테스트/보안/버전 체계) + R3 운영 데이터
- 보안 운영(정기 감사+패치) / 테스트 운영(회귀 자동 스케줄) / 릴리스 운영(릴리스+핫픽스) / 문서 운영(지식 그래프 최신성)
- **완료조건**: 보안 감사 주기 준수 + 회귀 100% 자동화 + 릴리스 프로세스 문서화

## 4. XF: 역류 (횡단 전략 수정 — A1)
- X3 운영 중 전략 부적합 발견 → **X1 전략 수정**(SOT 정본 우선). 이벤트 기반.
- 트리거 예: 보안 스캔 신규 취약점 패턴 → security_strategy 갱신 / 커버리지 목표 미달 지속 → test_strategy 조정(단, 80% 하한은 X2 완료조건 LOCK)

## 5. Phase 2 하네스 정합 (회귀 — X2 핵심 의존)
- **ruff 13룰**(E,F,W,I,N,UP,S,B,A,C4,DTZ,T20,ICN) — S(bandit)가 보안 실행 ①, 기타가 품질
- **vamos_lint VL-001~005** — 정합성 검증
- **ci.yml 3 job**(quality/test/vamos-lint) — X2 자동화 백본
- **Hook 18** — SOT 정합 + 코드 생산(.py→ruff, config→LOCK 검증)
- **commitlint.config.js** — X2 버전 관리 ⑧
- → 본 계획서는 Phase 2 하네스 **위에서** X2/X3를 실행 — 신규 충돌 0 (전부 기구축 자산 활용)

## 6. 의존 순서
```
X1(완료: 4전략) → X2(Phase 4~5 실행, ← B2/R2 코드) → X3(Phase 6 운영, ← R3) → XF(역류 시 X1로)
```

## 정본 인용
security/test/release/doc_strategy.md(X1) · STRATEGY_08 §4.4 X1/X2/X3 셀(L687-809) · Phase 2 하네스(ci.yml·ruff·vamos_lint·Hook 18·commitlint) · 로드맵 Phase 4(4-7 X2)/Phase 5(5-7 X3)
