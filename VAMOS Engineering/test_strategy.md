# VAMOS 테스트 전략 — test_strategy.md (3-9, X1)

> **확정일**: 2026-06-12 (P3-2) · **우선순위**: Should · **매트릭스 셀**: X1 (테스트 전략 ④⑤)
> **위상 (로드맵 L293)**: 본 문서는 기존 정본 **PHASE_B5_TEST_STRATEGY.md**(테스트 피라미드·50AC→TC 완비)의 **결정 요약 + 로드맵 바인딩**이다. PHASE_B5를 대체하지 않으며 충돌 시 PHASE_B5 우선. 상세 테스트 케이스·AC 매핑은 PHASE_B5 + PART2 §6.3이 정본.

## 1. 테스트 피라미드 (PHASE_B5 §1.1 추인)

```
        /  E2E  \          ← 핵심 시나리오 100%
       / 통합 테스트 \       ← 60%+ 커버리지
      /  단위 테스트   \     ← 80%+ 커버리지
```

| 계층 | 범위 | 도구 | 커버리지 목표 |
|------|------|------|-------------|
| **단위 (Unit)** | 함수/클래스/모듈 | pytest(Python) · cargo test(Rust) · vitest(React) | **80%+** |
| **통합 (Integration)** | 모듈 간 인터페이스·Pipeline 흐름 | pytest + subprocess · Docker Compose | **60%+** |
| **E2E** | 사용자 시나리오 전체 | Tauri WebDriver(tauri-driver ≥2.0) + Playwright ≥1.45 | 핵심 시나리오 **100%** |

- 커버리지 측정: pytest-cov ≥5.0 · 정본 PHASE_B5 §1.1 L30-34

## 2. 테스트 원칙 (PHASE_B5 §1.2)
1. **AC 완전 매핑**: D2~D8 모든 AC는 최소 1 TC에 매핑
2. **스키마 우선**: Pydantic v2 모델은 유효/무효 인스턴스 모두 테스트 (A20 정본 검증 — PHASE3-DEC-006)
3. **비밀 분리**: 테스트도 실제 API 키 금지 → mock/fixture (Phase 2 conftest.py 기반)
4. **재현 가능성**: CI 독립 실행 가능, 외부 의존성 mock
5. **실패 추적**: 실패 시 AC ID + 스키마 REF 로그
- ID 규칙: `T-{U|I|E}-{D2~D8|SYS}-{순번}` (PHASE_B5 §1.3)

## 3. R1 10결정 연계 핵심 테스트 (바인딩)
- **DEC-006 A20 왕복 테스트**: Python→JSON→Rust→JSON→Python 동일성 = PASS (V0 GO/NO-GO 게이트, 로드맵 4-V) — `T-I` 계층
- **DEC-005 Downshift**: 80% → force_mini / 100% → block (PHASE_B5 `test_downshift.py` L200, T-E-SYS-002)
- **DEC-001 5-Gate 순서**: Policy→Approval→Cost→Evidence→SelfCheck 통과 순서 검증
- **DEC-008 A21 3계층 독립**: Gate A 비활성 시 나머지 4개 동작(§5 security_strategy 검증 방법과 동일)
- **DEC-010 A25**: confidence < 0.30 → REFUSE / EvidenceGate insufficient → REFUSE 분기 테스트

## 4. 커버리지 목표 (V1)
- 단위 **80%+** / 통합 60%+ / E2E 핵심 100% — X2 완료 조건(커버리지 ≥80% + commitlint PASS) 정합
- V0: 스캐폴드 단계 — pytest 0 tests 허용(exit 5), 하네스 동작 확인이 목표(Phase 2 기구축). 실질 커버리지는 V1부터.

## 5. 회귀 정합 (Phase 2 하네스)
- Phase 2 ci.yml 3 job(quality/test/vamos-lint) 중 **test job**이 본 전략의 실행 계층 — 모순 0
- pytest·pytest-cov는 Phase 2 backend/pyproject.toml에 기설정 / conftest.py·tests/__init__.py 기존재
- 본 전략은 PHASE_B5 정본 + Phase 2 하네스 위의 바인딩 — 신규 도구·신규 충돌 없음

## 정본 인용
PHASE_B5 §1.1 L19-34·§1.2 L36-42·§1.3 · PART2 §6.3(테스트 ~128+190) · PHASE3-DEC-005/006/008/010 · Phase 2 ci.yml·pyproject.toml
