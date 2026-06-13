# PHASE4-DEC-013 — jsonrpcserver 채택 및 버전 핀 (IPC 서버 라이브러리)

> **결정일**: 2026-06-13 · **우선순위**: Must (V0-STEP-3 IPC) · **상태**: 확정
> **적용 범위**: Phase 4 P4-2 (V0 IPC JSON-RPC 서버) 이상
> **근거**: PART2 §2 V0-STEP-3 L410(지정 라이브러리) · PHASE_B1 §5.2(13 메서드 계약) · PART2 §1.3.1 #3(SOT 미정의 시 판단+ADR)

---

## 1. 결정 (Decision)

Python IPC JSON-RPC 2.0 서버 구현에 **`jsonrpcserver`** 라이브러리를 채택하고, `backend/pyproject.toml`에 **`jsonrpcserver = ">=5.0,<6.0"`** 로 핀한다(설치 실측 = 5.0.9).

## 2. 이유 (Why)

- **PART2 V0-STEP-3(L410)가 `jsonrpcserver`를 명시 의존성으로 지정**한다 — 정본의 지명 라이브러리.
- 그러나 **PHASE_B3_DEPENDENCIES(의존성 정본)에는 핀이 부재**(grep 0)하여 버전 공백이 존재한다. PART2 §1.3.1 #3(정본이 값을 정하지 않은 지점은 판단으로 메우고 ADR로 기록)에 따라 본 ADR로 버전을 확정한다.
- `jsonrpcserver` 5.x는 ① `@method(name="langgraph.workflow.run")` 형태의 **점(dot) 포함 메서드명 등록**, ② `dispatch(request_str) -> response_str`의 순수 함수형 인터페이스(= stdin/stdout 루프와 자연 정합), ③ **미존재 메서드 자동 -32601(Method not found)**, ④ **필수 파라미터 누락 자동 -32602(Invalid params)** 를 제공 — V0-STEP-3 Stage Gate #2/#3 및 IPC 규칙(에러=JSON-RPC error object)을 라이브러리 차원에서 충족(실측 확인).
- 메이저 6.x 미존재(현행 안정 = 5.0.9)이므로 `<6.0` 상한으로 메이저 파괴 변경을 차단한다.

## 3. 검토한 대안

- **대안 1: 라이브러리 없이 stdin/stdout JSON-RPC 직접 구현** — 기각. PART2가 라이브러리를 *지정*했고, 직접 구현은 -32601/-32602/배치/에러객체 규약을 재작성해야 하며 버그 표면이 넓다(R16 착시 위험). 단, 본 결정은 `dispatch` 결과를 stdin/stdout 루프로 감싸는 *얇은* 서버 래퍼(`server.py`)는 자체 작성함을 포함한다(라이브러리는 디스패치 코어만 담당).
- **대안 2: `jsonrpclib`/`python-jsonrpc-server`(LSP 계열)** — 기각. PART2 지명과 불일치 + 전송계층(소켓/LSP) 결합이 강해 순수 stdin/stdout stub 용도에 과함.
- **채택: `jsonrpcserver >=5.0,<6.0`** — 정본 지명 + Stage Gate 요건 직결 + 전송 비결합.

## 4. 경계 / 제약

- 잠긴 정본(ruff 13룰·mypy strict·CI 3-job·테스트 피라미드)은 **무수정**(PHASE4-DEC-011 §D). 본 결정은 *의존성 1건 추가*이며 CI job 추가가 아니다(CI 변경은 PHASE4-DEC-012 게이트 사안 — 본 ADR 무관).
- `jsonrpcserver`는 transitive로 `jsonschema`·`oslash`·`referencing`·`rpds-py`를 끌어온다(실측). `check_lockfiles.py`로 pyproject↔poetry.lock 정합(main+dev 16건 drift 0) 확인.
- V0 13 메서드는 전부 **stub**(기본 응답 + 파라미터 검증). embedding.* = 임베딩 0(stub), mcp.* = 시그니처 예약(DEC-007 — 실구현 V1-Phase 6).

## 5. 검증

- 설치 실측: `jsonrpcserver 5.0.9` (poetry install). pytest **108 passed** 무회귀. `check_lockfiles.py --root .` drift 0.
- API 실측: 점 포함 메서드명 등록 OK · 정상 디스패치 OK · 미존재 메서드 -32601 · 필수 파라미터 누락 -32602.
- 본 ADR은 A6(의사결정 기록) 준수 산출물이며 PROGRESS.md / 로드맵 추적표에서 참조한다.
