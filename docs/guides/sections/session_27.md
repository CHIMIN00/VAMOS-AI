---
session: 27
sections: [35, 36]
status: complete
---

# §35. 이벤트 & 로깅 시스템 (Event & Logging System)

> **비유**: VAMOS 안에서 일어나는 모든 일은 **CCTV와 블랙박스**에 기록됩니다. 이벤트(Event)는 "언제, 어디서, 무엇이 일어났는가"를 실시간으로 알리는 **방송 시스템**이고, 로깅(Logging)은 그 기록을 영구 저장하는 **블랙박스**입니다. 에러코드(FailureCode)는 "무엇이 잘못됐는지" 알리는 **경보 코드**, 폴백(Fallback)은 "잘못됐을 때 어떻게 대처하는지" 알려주는 **비상 매뉴얼**입니다.

---

## §35.1 EventType Registry (이벤트 유형 등록부) — 123개 이벤트

> VAMOS에서 일어나는 모든 상황에 고유한 이름을 붙인 것이 **EventType**(이벤트 타입)입니다. 총 **123개**가 등록되어 있으며, 추가/변경 시 반드시 DESIGN 근거를 기록해야 합니다. [근거: D2.1-D2 §5.1]

### 이벤트 네이밍 규칙

- **표기법**: `lower.dot` (소문자 + 점 구분)
- **구조**: `네임스페이스.모듈.동작.상태`
- **예시**: `oc.i1.parse.started` → ORANGE CORE(oc) → I-1 모듈(i1) → 파싱 동작(parse) → 시작됨(started)

### 네임스페이스 (Namespace) 분류

| 네임스페이스 | 의미 | 이벤트 수 | 설명 |
|-------------|------|----------|------|
| `oc.*` | ORANGE CORE | 35개 | 핵심 두뇌의 의사결정 파이프라인 이벤트 |
| `wf.*` | Workflow | 4개 | 워크플로우 스테이지 진입/퇴장/승인/보고 |
| `ui.builder.*` | UI Builder | 14개 | 개발자 도구(Builder) 조작 이벤트 |
| `ui.frontmini.*` | UI FrontMini | 7개 | 입력 전처리(FrontMini) 이벤트 |
| `ui.core.*` | UI Core | 7개 | 코어 UI 상태 이벤트 |
| `ui.gate.*` | UI Gate | 9개 | 정책/비용/승인 게이트 이벤트 |
| `ui.node.*` | UI Node | 2개 | Blue Node 선택/로드 이벤트 |
| `ui.main.*` | UI Main | 11개 | 메인 실행/아티팩트/품질 이벤트 |
| `ui.tool.*` | UI Tool | 6개 | 도구 호출/에러 이벤트 |
| `ui.memory.*` | UI Memory | 5개 | 메모리 후보/마스킹/커밋 이벤트 |
| `ui.cli.*` | UI CLI | 10개 | CLI 명령/인증/세션 이벤트 |
| `mem.*` | Memory | 2개 | 메모리 참조 갱신/지식 파생 이벤트 |
| `storage.*` | Storage | 5개 | 저장소 정책/메모리 쓰기 이벤트 |
| `agent.*` | Agent | 3개 | 에이전트 작업 시작/완료/실패 이벤트 |
| `sdar.*` | SDAR | 3개 | 자가진단 위험 평가/감사/안전 이벤트 |

### 전체 이벤트 카테고리별 목록 (123개)

#### (1) ORANGE CORE 이벤트 (`oc.*`) — 35개

| # | 이벤트 이름 | 설명 | 생산자 |
|---|-----------|------|--------|
| 1 | `oc.request.received` | 사용자 요청 수신 | OC 입구 |
| 2 | `oc.i1.parse.started` | 의도 파싱(분석) 시작 | I-1 |
| 3 | `oc.i1.intent.parsed` | 의도 파싱 완료 | I-1 |
| 4 | `oc.i1.intent.ambiguous` | 의도가 모호함 감지 | I-1 |
| 5 | `oc.i1.parse.failed` | 의도 파싱 실패 | I-1 |
| 6 | `oc.i2.query.built` | 검색 쿼리 생성 완료 | I-2 |
| 7 | `oc.i2.fetch.started` | 근거 수집 시작 | I-2 |
| 8 | `oc.i2.evidence.ready` | 근거 수집 완료 | I-2 |
| 9 | `oc.i2.evidence.insufficient` | 근거 불충분 | I-2 |
| 10 | `oc.i2.fetch.blocked` | 근거 수집 차단됨 | I-2 |
| 11 | `oc.i2.fetch.failed` | 근거 수집 실패 | I-2 |
| 12 | `oc.i3.plan.created` | 메모리 계획 생성 | I-3 |
| 13 | `oc.i3.commit.requested` | 메모리 저장 요청 | I-3 |
| 14 | `oc.i3.commit.approval_required` | 메모리 저장 승인 필요 | I-3 |
| 15 | `oc.i3.commit.completed` | 메모리 저장 완료 | I-3 |
| 16 | `oc.i3.commit.denied` | 메모리 저장 거부됨 | I-3 |
| 17 | `oc.i3.commit.failed` | 메모리 저장 실패 | I-3 |
| 18 | `oc.i4.structuring.started` | 출력 구조화 시작 | I-4 |
| 19 | `oc.i4.output.structured` | 출력 구조화 완료 | I-4 |
| 20 | `oc.i4.spec.violated` | 출력 스펙 위반 | I-4 |
| 21 | `oc.i4.mask.applied` | 마스킹(가림) 적용 | I-4 |
| 22 | `oc.i4.structuring.failed` | 출력 구조화 실패 | I-4 |
| 23 | `oc.i5.gates.evaluated` | 게이트 평가 완료 | I-5 |
| 24 | `oc.i5.route.selected` | 라우팅 경로 선택 | I-5 |
| 25 | `oc.i5.decision.locked` | 결정 잠금 완료 | I-5 |
| 26 | `oc.i5.approval.required` | 승인 필요 판정 | I-5 |
| 27 | `oc.i5.cost.downshifted` | 비용 다운시프트 발동 | I-5 |
| 28 | `oc.i5.policy.blocked` | 정책에 의해 차단 | I-5 |
| 29 | `oc.i5.decision.failed` | 결정 실패 | I-5 |
| 30 | `oc.loop.retry.reasoning` | 추론 재시도 루프 | OC 루프 |
| 31 | `oc.loop.retry.action` | 액션 재시도 루프 | OC 루프 |
| 32 | `oc.deny.blocked` | 거부 차단 처리 | OC |
| 33 | `oc.done` | 처리 완료 | OC |

> P2 관련: `oc.p2.activated` (P2 활성화), `oc.p2.deactivated` (P2 비활성화) — 위 목록 외 추가 2건 포함하여 총 35개 [근거: D2.1-D2 §5.1]

#### (2) Workflow 이벤트 (`wf.*`) — 4개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `wf.stage.enter` | 워크플로우 스테이지 진입 |
| 2 | `wf.stage.exit` | 워크플로우 스테이지 퇴장 |
| 3 | `wf.approval.requested` | 워크플로우 승인 요청 |
| 4 | `wf.report.created` | 워크플로우 보고서 생성 |

#### (3) UI Builder 이벤트 (`ui.builder.*`) — 14개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `ui.builder.run.started` | Builder 실행 시작 |
| 2 | `ui.builder.node.inspected` | 노드 검사 |
| 3 | `ui.builder.approval.granted` | 승인 허가 |
| 4 | `ui.builder.approval.denied` | 승인 거부 |
| 5 | `ui.builder.cost.mode_changed` | 비용 모드 변경 |
| 6 | `ui.builder.memory.candidate_excluded` | 메모리 후보 제외 |
| 7 | `ui.builder.log.filtered` | 로그 필터링 |
| 8 | `ui.builder.debug.step_over` | 디버그 스텝 오버 |
| 9 | `ui.builder.session.loaded` | 세션 로드 |
| 10 | `ui.builder.artifact.exported` | 아티팩트 내보내기 |
| 11 | `ui.builder.policy.edit.attempted` | 정책 편집 시도 |
| 12 | `ui.builder.approval.requested` | 승인 요청 |
| 13 | `ui.builder.simulate.started` | 시뮬레이션 시작 |
| 14 | `ui.builder.simulate.finished` | 시뮬레이션 완료 |

#### (4) UI FrontMini 이벤트 (`ui.frontmini.*`) — 7개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `ui.frontmini.input.received` | 입력 수신 |
| 2 | `ui.frontmini.scan.started` | 입력 스캔 시작 |
| 3 | `ui.frontmini.pii.detected` | 개인정보(PII) 감지 |
| 4 | `ui.frontmini.malware.found` | 악성코드 발견 |
| 5 | `ui.frontmini.summary.ready` | 요약 준비 완료 |
| 6 | `ui.frontmini.package.ready` | 패키지 준비 완료 |
| 7 | `ui.frontmini.package.sent` | 패키지 전송 완료 |

#### (5) UI Core 이벤트 (`ui.core.*`) — 7개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `ui.core.received` | 코어 수신 |
| 2 | `ui.core.intent.analyzed` | 의도 분석 완료 |
| 3 | `ui.core.decision.locked` | 결정 잠금 |
| 4 | `ui.core.p2.locked` | P2 잠금 |
| 5 | `ui.core.p2.modal.shown` | P2 모달 표시 |
| 6 | `ui.core.p2.modal.confirmed` | P2 모달 확인 |
| 7 | `ui.core.p2.modal.cancelled` | P2 모달 취소 |

#### (6) UI Gate 이벤트 (`ui.gate.*` + `ui.policy.*`) — 9개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `ui.gate.policy.checked` | 정책 검사 완료 |
| 2 | `ui.gate.policy.violated` | 정책 위반 |
| 3 | `ui.gate.cost.calculated` | 비용 계산 완료 |
| 4 | `ui.gate.cost.warning` | 비용 경고 |
| 5 | `ui.gate.cost.warning_80` | 비용 80% 경고 |
| 6 | `ui.gate.cost.ceiling_100` | 비용 100% 도달 |
| 7 | `ui.gate.approval.required` | 승인 필요 |
| 8 | `ui.gate.approval.waiting` | 승인 대기 중 |
| 9 | `ui.policy.blocked` | 정책 차단 |

#### (7) UI Node 이벤트 (`ui.node.*`) — 2개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `ui.node.selected` | 노드 선택 |
| 2 | `ui.node.context.loaded` | 노드 컨텍스트 로드 |

#### (8) UI Main 이벤트 (`ui.main.*`) — 11개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `ui.main.job.queued` | 작업 큐 등록 |
| 2 | `ui.main.execution.started` | 실행 시작 |
| 3 | `ui.main.step.started` | 단계 시작 |
| 4 | `ui.main.stream.chunk` | 스트리밍 청크 |
| 5 | `ui.main.artifact.created` | 아티팩트 생성 |
| 6 | `ui.main.evidence.linked` | 근거 연결 |
| 7 | `ui.main.selfcheck.started` | 셀프체크 시작 |
| 8 | `ui.main.selfcheck.passed` | 셀프체크 통과 |
| 9 | `ui.main.selfcheck.failed` | 셀프체크 실패 |
| 10 | `ui.main.qod.updated` | QoD 점수 갱신 |
| 11 | `ui.main.alert.shown` | 알림 표시 |

#### (9) UI Tool 이벤트 (`ui.tool.*`) — 6개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `ui.tool.call.started` | 도구 호출 시작 |
| 2 | `ui.tool.call.finished` | 도구 호출 완료 |
| 3 | `ui.tool.error.timeout` | 도구 타임아웃 |
| 4 | `ui.tool.error.ratelimit` | 도구 속도 제한 |
| 5 | `ui.tool.error.parse` | 도구 파싱 에러 |
| 6 | `ui.tool.file.converted` | 파일 변환 완료 |

#### (10) UI Memory 이벤트 (`ui.memory.*`) — 5개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `ui.memory.candidate.found` | 메모리 후보 발견 |
| 2 | `ui.memory.masking.applied` | 메모리 마스킹 적용 |
| 3 | `ui.memory.commit.success` | 메모리 커밋 성공 |
| 4 | `ui.memory.commit.denied` | 메모리 커밋 거부 |
| 5 | `ui.memory.source.trust_updated` | 소스 신뢰도 갱신 |

#### (11) UI CLI 이벤트 (`ui.cli.*`) — 10개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `ui.cli.command.received` | CLI 명령 수신 |
| 2 | `ui.cli.command.completed` | CLI 명령 완료 |
| 3 | `ui.cli.command.failed` | CLI 명령 실패 |
| 4 | `ui.cli.auth.prompted` | CLI 인증 요청 |
| 5 | `ui.cli.auth.resolved` | CLI 인증 완료 |
| 6 | `ui.cli.progress.updated` | CLI 진행률 갱신 |
| 7 | `ui.cli.output.streamed` | CLI 출력 스트리밍 |
| 8 | `ui.cli.config.changed` | CLI 설정 변경 |
| 9 | `ui.cli.session.started` | CLI 세션 시작 |
| 10 | `ui.cli.session.ended` | CLI 세션 종료 |

#### (12) Memory 이벤트 (`mem.*`) — 2개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `mem.reference.updated` | 메모리 참조 소스 갱신 |
| 2 | `mem.kb.derived` | KB 임베딩에서 새 지식 파생 |

#### (13) Storage 이벤트 (`storage.*`) — 5개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `storage.policy.checked` | 저장소 정책 검사 |
| 2 | `storage.memory.write.requested` | 메모리 쓰기 요청 |
| 3 | `storage.memory.write.completed` | 메모리 쓰기 완료 |
| 4 | `storage.vector.insert.denied` | 벡터 삽입 거부 |
| 5 | `storage.pii.longterm.denied` | PII 장기 저장 거부 |

#### (14) Agent 이벤트 (`agent.*`) — 3개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `agent.task.started` | 에이전트 작업 시작 |
| 2 | `agent.task.completed` | 에이전트 작업 완료 |
| 3 | `agent.task.failed` | 에이전트 작업 실패 |

#### (15) SDAR 이벤트 (`sdar.*`) — 3개

| # | 이벤트 이름 | 설명 |
|---|-----------|------|
| 1 | `sdar.risk.assessed` | 위험 평가 완료 |
| 2 | `sdar.audit.logged` | 감사 로그 기록 |
| 3 | `sdar.safety.checked` | 안전 검사 완료 |

> **이벤트 등록 규칙**: contracts.py의 event_type 필드는 반드시 EventTypeRegistry의 Literal 타입으로 제한해야 합니다. 자유 문자열 사용은 금지됩니다. [근거: D2.1-D2 §5.1 S13-A-003]

### 핵심 요약 (3줄)
1. VAMOS의 모든 상황은 123개의 **표준 이벤트 타입**으로 분류되며, `lower.dot` 네이밍 규칙을 따릅니다.
2. 이벤트는 15개 네임스페이스(`oc`, `wf`, `ui.*`, `mem`, `storage`, `agent`, `sdar`)로 그룹화됩니다.
3. 이벤트 타입 추가/변경 시 반드시 **DESIGN 근거를 Q1에 기록**해야 하며, D2가 유일한 정본(SOT)입니다.

---

## §35.2 FailureCode Registry (에러코드 등록부) — 36개

> **비유**: 병원에서 환자의 증상을 코드로 분류하듯, VAMOS도 모든 오류에 **표준 코드**를 부여합니다. 이 코드를 보면 "어디서, 무슨 문제가 생겼는지" 즉시 파악할 수 있습니다.

### 에러코드 네이밍 규칙

- **표기법**: `UPPER_SNAKE` (대문자 + 밑줄 구분)
- **구조**: `모듈접두사_에러유형`
- **예시**: `OC_I1_PARSE_FAIL` → ORANGE CORE(OC) → I-1 모듈(I1) → 파싱 실패(PARSE_FAIL)

[근거: D2.1-D2 §5.2]

### 에러코드 전체 목록 (36개)

#### (1) ORANGE CORE I-1~I-5 에러 (`OC_I*_*`) — 17개

| # | 에러코드 | 설명 | 모듈 |
|---|---------|------|------|
| 1 | `OC_I1_PARSE_FAIL` | 의도 파싱 실패 | I-1 |
| 2 | `OC_I1_AMBIGUOUS_UNRESOLVED` | 모호한 의도 미해결 | I-1 |
| 3 | `OC_I2_RAG_NO_SOURCE` | RAG 소스 없음 | I-2 |
| 4 | `OC_I2_EVIDENCE_QOD_LOW` | 근거 품질(QoD) 낮음 | I-2 |
| 5 | `OC_I2_SOURCE_POLICY_BLOCK` | 소스 정책 차단 | I-2 |
| 6 | `OC_I2_TIMEOUT` | 근거 수집 타임아웃 | I-2 |
| 7 | `OC_I3_MEMORY_POLICY_DENY` | 메모리 정책 거부 | I-3 |
| 8 | `OC_I3_APPROVAL_REQUIRED` | 메모리 승인 필요 | I-3 |
| 9 | `OC_I3_COMMIT_FAIL` | 메모리 커밋 실패 | I-3 |
| 10 | `OC_I4_OUTPUT_SPEC_VIOLATION` | 출력 스펙 위반 | I-4 |
| 11 | `OC_I4_CITATION_MISSING` | 인용/출처 누락 | I-4 |
| 12 | `OC_I4_MASK_FAIL` | 마스킹 실패 | I-4 |
| 13 | `OC_I5_POLICY_BLOCK` | 정책 차단 | I-5 |
| 14 | `OC_I5_APPROVAL_REQUIRED` | 결정 승인 필요 | I-5 |
| 15 | `OC_I5_COST_OVER_BUDGET` | 비용 예산 초과 | I-5 |
| 16 | `OC_I5_EVIDENCE_INSUFFICIENT` | 근거 불충분 | I-5 |
| 17 | `OC_I5_ROUTE_NOT_FOUND` | 라우팅 경로 없음 | I-5 |

#### (2) 공통/정책 에러 — 4개

| # | 에러코드 | 설명 |
|---|---------|------|
| 18 | `PII_LONGTERM_DENIED` | PII(개인정보) 장기 저장 거부 |
| 19 | `POLICY_DENY` | 정책에 의한 거부 |
| 20 | `GT_ERR_COST_LIMIT` | 게이트 비용 한도 초과 |
| 21 | `TOOL_TIMEOUT` | 도구 호출 타임아웃 |

#### (3) FrontMini 에러 (`FM_ERR_*`) — 4개

| # | 에러코드 | 설명 |
|---|---------|------|
| 22 | `FM_ERR_FMT` | 입력 포맷 오류 |
| 23 | `FM_ERR_SIZE` | 입력 크기 초과 |
| 24 | `FM_ERR_PII` | 입력에서 PII 감지 |
| 25 | `FM_ERR_ZERO` | 빈 입력 (내용 없음) |

#### (4) ORANGE CORE UI 에러 (`OC_ERR_*`) — 5개

| # | 에러코드 | 설명 |
|---|---------|------|
| 26 | `OC_ERR_NONGOAL` | Non-goal(금지사항) 위반 요청 |
| 27 | `OC_ERR_P2_LOCK` | P2 잠금 위반 |
| 28 | `OC_ERR_COST_LV` | 비용 경고 수준(80%) 도달 |
| 29 | `OC_ERR_COST_OV` | 비용 상한(100%) 초과 |
| 30 | `OC_ERR_NO_ROUTE` | 라우팅 불가 |

#### (5) Tool Layer 에러 (`TL_ERR_*`) — 3개

| # | 에러코드 | 설명 |
|---|---------|------|
| 31 | `TL_ERR_TIMEOUT` | 도구 실행 타임아웃 |
| 32 | `TL_ERR_403` | 도구 접근 권한 없음 (403) |
| 33 | `TL_ERR_PARSE` | 도구 응답 파싱 실패 |

#### (6) Main-Check 에러 (`MC_ERR_*`) — 3개

| # | 에러코드 | 설명 |
|---|---------|------|
| 34 | `MC_ERR_LOW_QOD` | 품질(QoD) 점수 낮음 |
| 35 | `MC_ERR_CONFLICT` | 정보 충돌 감지 |
| 36 | `MC_ERR_STALE` | 정보 만료(오래됨) 감지 |

> **UI Layer 실패 코드 추가 배경**: D2.0-08 §7.6에서 FrontMini/Core/Tool/Main-Check 계층별 실패 유형을 커버하기 위해 15건이 추가 등록되었습니다. [근거: D2.1-D2 §5.2 UI-02]

### 핵심 요약 (3줄)
1. VAMOS의 모든 오류는 36개의 **표준 에러코드(FailureCode)**로 분류되며, `UPPER_SNAKE` 네이밍 규칙을 따릅니다.
2. 에러코드는 6개 카테고리로 나뉩니다: OC 파이프라인(17개), 공통/정책(4개), FrontMini(4개), OC UI(5개), Tool(3개), Main-Check(3개).
3. 에러코드는 **D2 SOT에서만 확정**되며, 타 문서에서 재정의할 수 없습니다.

---

## §35.3 Fallback Registry (폴백 등록부) — 23개 대응전략

> **비유**: 비행기에 엔진 고장이 나면 "대체 엔진 가동", "가까운 공항 비상착륙" 같은 **비상 대응 매뉴얼**이 있듯이, VAMOS도 오류 발생 시 자동으로 실행할 **대응 전략(Fallback)**을 미리 등록해 둡니다.

### 폴백 네이밍 규칙

- **표기법**: `FB_UPPER_SNAKE` (FB 접두사 + 대문자 밑줄)
- **구조**: `FB_대응영역_전략명`
- **예시**: `FB_RAG_RETRY_EXPAND` → 폴백(FB) → RAG 검색(RAG) → 재시도 확장(RETRY_EXPAND)

[근거: D2.1-D2 §5.3]

### 폴백 전략 전체 목록 (23개)

#### (1) 기존 핵심 폴백 — 14개

| # | 폴백 ID | 설명 (쉬운 말) |
|---|--------|--------------|
| 1 | `FB_INTENT_HEURISTIC_PARSE` | 의도 파싱 실패 시 → 휴리스틱(경험 규칙) 기반 재파싱 |
| 2 | `FB_ASK_CLARIFICATION` | 모호한 요청 시 → 사용자에게 명확히 물어보기 |
| 3 | `FB_RAG_RETRY_EXPAND` | 검색 결과 부족 시 → 검색 범위 확장 후 재시도 |
| 4 | `FB_RAG_SWITCH_SOURCE` | 검색 소스 문제 시 → 다른 소스로 전환 |
| 5 | `FB_MEMORY_META_ONLY` | 메모리 정책 거부 시 → 메타정보(제목 등)만 저장 |
| 6 | `FB_REQUIRE_APPROVAL` | 승인 필요 시 → 사용자에게 승인 요청 |
| 7 | `FB_OUTPUT_REFORMAT` | 출력 형식 오류 시 → 형식 재조정 |
| 8 | `FB_OUTPUT_MINIMAL` | 출력 불가 시 → 최소 정보만 출력 |
| 9 | `FB_POLICY_MASK` | 정책 위반 내용 시 → 해당 부분 마스킹(가림) |
| 10 | `FB_COST_DOWNSHIFT` | 비용 초과 시 → 저비용 모델로 전환 |
| 11 | `FB_ROUTE_SAFE_NODE` | 라우팅 실패 시 → 안전한 기본 노드로 라우팅 |
| 12 | `FB_RESTRICT_GENERAL_INFO` | 제한된 정보 시 → 일반 정보로 제한 응답 |
| 13 | `FB_DENY_WITH_REASON` | 거부 시 → 거부 사유와 함께 거절 |
| 14 | `FB_DENY_STORAGE` | 저장 거부 시 → 저장 거부 사유 안내 |

#### (2) UI Layer 추가 폴백 — 9개

| # | 폴백 ID | 설명 (쉬운 말) | 대응 에러 |
|---|--------|--------------|----------|
| 15 | `FB_REJECT_INPUT` | 입력 거부 → 포맷/크기 오류 안내 | FM_ERR_FMT, FM_ERR_SIZE |
| 16 | `FB_MASK_AND_CONFIRM` | PII 마스킹 후 사용자 확인 요청 | FM_ERR_PII |
| 17 | `FB_REQ_REUPLOAD` | 빈 파일 → 재업로드 요청 | FM_ERR_ZERO |
| 18 | `FB_RETRY_SOFT` | 소프트 재시도 (잠시 후 재시도) | TL_ERR_TIMEOUT |
| 19 | `FB_USE_WEB_SEARCH` | 접근 거부 시 → 웹 검색 우회 | TL_ERR_403 |
| 20 | `FB_RETURN_RAW` | 파싱 실패 시 → 원본 텍스트 반환 | TL_ERR_PARSE |
| 21 | `FB_AUTO_REPAIR` | 품질 낮을 시 → 자동 보완 | MC_ERR_LOW_QOD |
| 22 | `FB_SHOW_CONFLICT` | 정보 충돌 시 → 충돌 내용 표시 | MC_ERR_CONFLICT |
| 23 | `FB_SHOW_STALE` | 정보 만료 시 → 만료 표시 | MC_ERR_STALE |

[근거: D2.1-D2 §5.3 UI-02, D2.0-08 §7.6]

### 핵심 요약 (3줄)
1. VAMOS는 오류 발생 시 자동 대응하는 23개의 **표준 폴백 전략**을 등록해 두고 있습니다.
2. 기존 핵심 14개 + UI Layer 추가 9개로 구성되며, `FB_UPPER_SNAKE` 네이밍 규칙을 따릅니다.
3. 각 폴백은 특정 에러코드(FailureCode)와 매핑되어 자동 또는 반자동으로 실행됩니다.

---

## §35.4 FailureCode → Fallback 매핑 (36:23, 1:N)

> **비유**: 병원에서 "감기(진단)"이면 "약 처방 OR 주사 OR 수액" 등 여러 치료법 중 하나를 선택하듯, 하나의 에러코드에 여러 폴백 전략이 연결될 수 있습니다.

### 매핑 원리

- **관계**: 하나의 FailureCode(에러코드)가 하나 이상의 Fallback(폴백)에 매핑됩니다.
- **선택 기준**: 상황의 심각도, 사용자 설정, 비용 상태에 따라 적합한 폴백을 선택합니다.

### FailureCode → Fallback 매핑 표

| # | FailureCode (에러코드) | Fallback (대응전략) | 근거 |
|---|----------------------|-------------------|------|
| 1 | `OC_I1_PARSE_FAIL` | `FB_INTENT_HEURISTIC_PARSE` | §6.3 preconditions |
| 2 | `OC_I1_AMBIGUOUS_UNRESOLVED` | `FB_ASK_CLARIFICATION` | §6.3 preconditions |
| 3 | `OC_I2_RAG_NO_SOURCE` | `FB_RAG_RETRY_EXPAND` | §6.3 preconditions |
| 4 | `OC_I2_EVIDENCE_QOD_LOW` | `FB_RAG_RETRY_EXPAND` | §6.3 preconditions |
| 5 | `OC_I2_SOURCE_POLICY_BLOCK` | `FB_RAG_SWITCH_SOURCE` | §6.3 preconditions |
| 6 | `OC_I2_TIMEOUT` | `FB_RAG_SWITCH_SOURCE` | §6.3 preconditions |
| 7 | `OC_I3_MEMORY_POLICY_DENY` | `FB_MEMORY_META_ONLY` | §6.3 preconditions |
| 8 | `OC_I3_APPROVAL_REQUIRED` | `FB_REQUIRE_APPROVAL` | §6.3 preconditions |
| 9 | `OC_I3_COMMIT_FAIL` | `FB_DENY_WITH_REASON` | §7.29 |
| 10 | `OC_I4_OUTPUT_SPEC_VIOLATION` | `FB_OUTPUT_REFORMAT` | §6.3 preconditions |
| 11 | `OC_I4_CITATION_MISSING` | `FB_POLICY_MASK` | §6.3 preconditions |
| 12 | `OC_I4_MASK_FAIL` | `FB_POLICY_MASK` | §6.3 preconditions |
| 13 | `OC_I5_POLICY_BLOCK` | `FB_DENY_WITH_REASON` | §6.3 preconditions |
| 14 | `OC_I5_APPROVAL_REQUIRED` | `FB_REQUIRE_APPROVAL` | §6.3 preconditions |
| 15 | `OC_I5_COST_OVER_BUDGET` | `FB_COST_DOWNSHIFT` | §6.3 preconditions |
| 16 | `OC_I5_EVIDENCE_INSUFFICIENT` | `FB_RAG_RETRY_EXPAND` | §7.49 |
| 17 | `OC_I5_ROUTE_NOT_FOUND` | `FB_ROUTE_SAFE_NODE` | §6.3 preconditions |
| 18 | `PII_LONGTERM_DENIED` | `FB_DENY_WITH_REASON` | RULE 1.3 §2.4 |
| 19 | `POLICY_DENY` | `FB_DENY_WITH_REASON` | 05 §8.2 |
| 20 | `GT_ERR_COST_LIMIT` | `FB_COST_DOWNSHIFT` | 05 §8.2 |
| 21 | `TOOL_TIMEOUT` | `FB_RAG_RETRY_EXPAND` | 05 §8.2 |
| 22 | `STORAGE_POLICY_DENY` | `FB_DENY_STORAGE` | D2.0-06 §8 |

[근거: D2.1-D2 §8]

### 핵심 요약 (3줄)
1. 36개 에러코드와 23개 폴백 전략은 **1:N 관계**로 매핑됩니다 (하나의 에러에 여러 대응 가능).
2. 매핑 관계는 D2 문서에서 정본으로 관리되며, DESIGN 근거 없이 변경할 수 없습니다.
3. 시스템은 에러 발생 시 매핑 표를 조회하여 **자동으로 적절한 폴백을 선택**합니다.

---

## §35.5 NEVER_AUTO 에러 — 자동 탐지 금지 목록

> **비유**: 아무리 뛰어난 자동 소방 시스템이라도, **핵발전소의 원자로를 자동으로 끄거나 켜는 것은 절대 허용되지 않습니다**. VAMOS에서도 시스템이 아무리 똑똑해져도 **절대 자동으로 건드릴 수 없는 영역**이 있습니다.

### NEVER_AUTO 수리 액션 목록 (10개) — ⚠️ 변경 불가 (LOCK)

| 액션 ID | 명칭 | 설명 | 사유 |
|---------|------|------|------|
| `RA_NEVER_01` | `modify_safety_rules` | 안전 규칙 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_02` | `change_cost_ceiling` | 비용 상한 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_03` | `alter_approval_flow` | 승인 흐름 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_04` | `modify_non_goals` | Non-goal 목록 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_05` | `change_audit_format` | 감사 로그 형식 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_06` | `alter_data_retention` | 데이터 보존 정책 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_07` | `modify_user_consent` | 사용자 동의 설정 변경 | 7개 불변 구역 (LOCK) |
| `RA_NEVER_08` | `escalate_own_privilege` | SDAR 자체 권한 상승 | RBAC 원칙 위반 |
| `RA_NEVER_09` | `disable_guardrails` | Guardrails 비활성화 | Fail-safe 원칙 위반 |
| `RA_NEVER_10` | `bypass_gate` | Gate(검문소) 우회 | Gate 우회 불가 (LOCK) |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §5.1, VAMOS_MASTER_SPECIFICATION §19.7]

### NEVER_AUTO 보안 에러 카테고리 (Category E) — 6개

보안 관련 에러는 **절대 자동 수리 금지**이며, 즉시 차단 후 사람에게 에스컬레이션(보고)합니다:

| 에러 코드 | 설명 | 위험도 | 대응 |
|----------|------|--------|------|
| `SDAR_E01_INJECTION_DETECTED` | 프롬프트 인젝션(주입 공격) 감지 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E02_UNAUTHORIZED_ACCESS` | 무단 접근 시도 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E03_DATA_BREACH` | 데이터 유출 감지 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E04_PRIVILEGE_ESCALATION` | 권한 상승 시도 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E05_SAFETY_BYPASS` | 안전 필터 우회 시도 | CRITICAL | 즉시 차단 + 인간 알림 |
| `SDAR_E06_PII_EXPOSURE` | PII(개인정보) 노출 감지 | CRITICAL | 즉시 마스킹 + 인간 알림 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §4.1 Category E]

### 코드 레벨 보장

```python
# 절대 수정 불가 영역 (하드코딩) — 설정 파일로도 우회 불가
NEVER_AUTO_TARGETS: frozenset = frozenset({
    # 7개 불변구역
    "safety_rules",
    "cost_ceiling",
    "approval_flow",
    "non_goals",
    "audit_format",
    "data_retention",
    "user_consent",
    # 3개 운영금지
    "escalate_own_privilege",
    "disable_guardrails",
    "bypass_gate",
})
```

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9.1, v13 DELTA-005~006]

### 핵심 요약 (3줄)
1. NEVER_AUTO는 **어떤 자율 수준(AR-Level)에서도 절대 자동 실행이 금지**된 10개 수리 액션입니다.
2. 보안 에러(Category E) 6개는 감지 즉시 **차단 + 인간 에스컬레이션**으로 처리됩니다.
3. NEVER_AUTO는 코드 레벨에서 `frozenset`으로 **하드코딩**되어 있어, 설정 파일로도 우회할 수 없습니다.

---

## §35.6 로깅 스택 (Logging Stack) — 버전별 비교

> **비유**: V1은 **수첩에 손으로 기록**(JSONL 파일), V2는 **체계적인 서류 캐비닛**(Postgres 중앙 수집), V3는 **전산화된 관제 센터**(Loki+Grafana 시각화 대시보드)와 같습니다.

### 버전별 로깅 방식 비교

| 항목 | V1 (로컬 MVP) | V2 (서버) | V3 (엔터프라이즈) |
|------|-------------|----------|----------------|
| **기본 형식** | JSONL 파일 | JSONL + Postgres | Loki/ELK 계열 |
| **저장 위치** | `data/logs/events.jsonl` | Postgres 테이블 | Loki + Object Storage |
| **검색 방식** | 파일 직접 검색 | SQL 쿼리 | Grafana 대시보드 |
| **로그 출력 대상** | `file` (파일만) | `file` + `stdout` | `file` + `stdout` + `remote` |
| **로그 레벨** | INFO | INFO | WARN |
| **로그 보존** | 30일 | 60일 | 90일 |
| **trace_id 필수** | ✅ (항상 true) | ✅ (항상 true) | ✅ (항상 true) |
| **포맷** | JSON | JSON | JSON |
| **실시간 모니터링** | ❌ | ⚠️ (stdout) | ✅ (Grafana) |

[근거: B4 §3.12, D2.1-A1 §A1-5 LOCK]

### LogEventSchema (로그 이벤트 스키마)

모든 로그 이벤트는 아래 표준 구조를 따릅니다:

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `event_type` | enum | ✅ | 이벤트 타입 (EventTypeRegistry에서 선택) |
| `producer` | string | ✅ | 이벤트를 발생시킨 모듈 (예: "I-1") |
| `when` | string | ✅ | 발생 조건 설명 |
| `payload` | object | ✅ | 핵심 데이터 (trace_id, decision_id 등) |
| `severity` | enum | ✅ | 심각도: `info` / `warn` / `error` / `critical` |
| `sinks` | array | ❌ | 전달 대상: `file`, `db`, `audit` |
| `links` | object | ❌ | 연결된 failure_code / fallback_id |

[근거: D2.1-D2 §4.2]

### 로그 이벤트 실제 예시

```json
{
  "event_type": "oc.i5.decision.locked",
  "producer": "I-5",
  "when": "Decision 객체 잠금 완료 시점",
  "payload": {
    "trace_id": "trc_01HZX9R1ABCDE",
    "decision_id": "dec_01HZX9R1ABCDE",
    "conclusion": "ACCEPT"
  },
  "severity": "info",
  "sinks": ["file", "db", "audit"],
  "links": {
    "failure_code": [],
    "fallback_id": [],
    "policy_check": ["pol_01HZX9R1ABCDE"]
  }
}
```

[근거: D2.1-D2 §6.2]

### 핵심 요약 (3줄)
1. VAMOS 로깅은 V1(JSONL 파일) → V2(Postgres 중앙 수집) → V3(Loki+Grafana 관제)로 진화합니다.
2. 모든 로그에는 반드시 `trace_id`가 포함되어야 하며(LOCK), 이를 통해 요청의 전체 흐름을 추적합니다.
3. 로그 포맷은 JSON으로 통일되며, LogEventSchema 표준 구조(7개 필드)를 따릅니다.

---

---

# §36. Configuration 시스템 (설정 관리)

> **비유**: VAMOS의 Configuration(설정) 시스템은 **자동차의 세팅**과 같습니다. `.env` 파일은 **열쇠와 면허증** (비밀 정보), `config.toml`은 **시트 위치·에어컨·미러 설정** (일반 설정), DB 런타임 설정은 **운전 중 내비게이션 목적지 변경** (실시간 조정)입니다. 위험한 설정은 잠금(LOCK) 처리되어 함부로 바꿀 수 없습니다.

---

## §36.1 설정 계층: .env → config.toml → DB Runtime

### 3계층 구조

```
┌─────────────────────────────────────────────┐
│  L1 — .env 파일 (비밀 키)                    │  ← API 키, 비밀번호
│    🔒 Git에 절대 커밋 금지                    │
├─────────────────────────────────────────────┤
│  L2 — config/config.toml (앱 설정)           │  ← 모델, DB, 비용, 보안 등
│    📄 배포 시 변경                            │
├─────────────────────────────────────────────┤
│  L3 — DB Runtime (V2+)                      │  ← rate limit, feature flag
│    ⚡ 실시간 동적 변경                        │
└─────────────────────────────────────────────┘
```

| 계층 | 저장 위치 | 용도 | 변경 빈도 |
|------|----------|------|----------|
| **L1 — 비밀 키** | `.env` 파일 | API 키, 비밀번호, 인증 토큰 | 드물게 (수동) |
| **L2 — 앱 설정** | `config/config.toml` 파일 | 모델, DB, 비용, 보안, 로깅 등 | 배포 시 |
| **L3 — 런타임 설정** | DB (V2+, Postgres) | 동적 조정 항목 | 실시간 |

[근거: B4 §1.1]

### 오버라이드 우선순위

```
환경 변수 (.env)  >  런타임 DB (V2+)  >  config/config.toml  >  프리셋 기본값
```

> **쉬운 말**: 같은 설정이 여러 곳에 있으면, `.env`에 적힌 값이 가장 우선합니다. 그 다음은 DB, 그 다음은 config.toml 파일 순입니다. [근거: B4 §5.4]

### 핵심 원칙 5가지

1. **비밀 분리**: API 키/비밀번호는 반드시 `.env`에만 저장. 코드나 config.toml에 포함 금지.
2. **버전별 프리셋**: V1/V2/V3별 기본 설정 파일 제공 (`config.v1.toml`, `config.v2.toml`, `config.v3.toml`).
3. **환경 변수 우선**: `.env` 값이 최우선.
4. **Pydantic v2 검증**: 모든 설정은 로드 시 자동 검증.
5. **DESIGN 정합**: 설정 키는 D2.1 스키마 문서와 정합해야 하며, 임의 확장 금지.

[근거: B4 §1.2]

### 핵심 요약 (3줄)
1. VAMOS 설정은 **3계층**(L1 비밀 키 / L2 앱 설정 / L3 런타임)으로 분리 관리됩니다.
2. 우선순위는 `.env` > DB Runtime > `config.toml` > 프리셋 기본값입니다.
3. API 키와 비밀번호는 반드시 `.env`에만 저장하며, Git 커밋이 절대 금지됩니다.

---

## §36.2 config.toml 전체 섹션 (17개)

> config.toml 파일은 VAMOS의 **모든 일반 설정**을 담고 있습니다. 총 17개 섹션으로 구성되어 있으며, 각 섹션은 특정 기능 영역을 담당합니다.

### 17개 섹션 일람표

| # | 섹션 이름 | 역할 | 주요 설정 예시 | 연결 스키마 |
|---|----------|------|-------------|------------|
| 1 | `[core]` | ORANGE CORE 핵심 설정 | 자율성 수준, 실행 모드, 타임아웃 | D2, D7 |
| 2 | `[llm]` | LLM 모델 설정 | mini/main/fallback 모델, 온도, 최대 토큰 | D4 |
| 3 | `[embedding]` | 임베딩 모델 설정 | 모델 ID, 차원 수, 배치 크기 | D6, A1 |
| 4 | `[vector_db]` | 벡터 DB 설정 | 백엔드(Chroma/Qdrant), 연결 모드 | D6 |
| 5 | `[graph_db]` | 그래프 DB 설정 | 백엔드(JSON/Neo4j), 최대 홉 수 | D6 |
| 6 | `[storage]` | 저장소 설정 | 백엔드(SQLite/Postgres), 백업, 메모리 TTL | D4, D6 |
| 7 | `[cost]` | 비용 관리 설정 | 일일/월간 한도, 경고 임계값, 다운시프트 | D7 |
| 8 | `[guardrails]` | 보안 가드레일 설정 | L1~L4 활성화, 실패 정책 | D7 |
| 9 | `[self_check]` | 셀프체크 임계값 **(LOCK)** | P0/P1/P2 통과 기준, soft loop 횟수 | D2 |
| 10 | `[approval]` | 승인 타임아웃 **(LOCK)** | 일반/P2 승인 타임아웃 | D7 |
| 11 | `[mcp]` | MCP 브릿지 설정 | 전송 방식, 타임아웃, 브릿지 목록 | D3 |
| 12 | `[rbac]` | 역할 기반 접근 제어 | 기본 역할, 역할별 권한 | D7 |
| 13 | `[rate_limit]` | 속도 제한 설정 | 분당 요청 수, 토큰 수, 버스트 허용 | D4 |
| 14 | `[logging]` | 로깅 설정 | 로그 레벨, 포맷, 출력 대상 | D2 |
| 15 | `[blue_nodes]` | Blue Node 상한 설정 | 활성/후보 노드 상한 | D3 |
| 16 | `[ui]` | UI 레이아웃 설정 | 최소 너비, 기본 크기, 폰트 | D8 |
| 17 | `[semantic_cache]` | 시맨틱 캐시 설정 | 유사도 임계값, 최대 엔트리, TTL | D6 |

[근거: B4 §3.1~3.15]

### 버전별 주요 차이 (V1 vs V2 vs V3)

| 설정 항목 | V1 (로컬) | V2 (서버) | V3 (엔터프라이즈) |
|----------|----------|----------|----------------|
| `core.autonomy_level` | L1 | L2 | L3 |
| `core.default_execution_mode` | mini | main | main |
| `llm.mini_model` | ollama/llama3.2:3b | gpt-4o-mini | gpt-4o-mini |
| `llm.main_model` | ollama/llama3.1:8b | gpt-4o | gpt-4o |
| `llm.max_tokens` | 2048 | 4096 | 8192 |
| `embedding.model` | bge-m3 | text-embedding-3-small | text-embedding-3-small |
| `vector_db.backend` | chroma | qdrant | qdrant_cloud |
| `graph_db.backend` | json_file | neo4j | neo4j |
| `storage.backend` | sqlite | postgres | postgres |
| `cost.daily_limit` | 1,300원 | 3,100원 | 8,900원 |
| `cost.monthly_limit` | 40,000원 | 93,000원 | 266,000원 |
| `guardrails.layer3_enabled` | false | true | true |
| `rbac.default_role` | OWNER | OPERATOR | VIEWER |
| `rate_limit.enabled` | false | true | true |
| `logging.sinks` | [file] | [file, stdout] | [file, stdout, remote] |
| `logging.level` | INFO | INFO | WARN |

[근거: B4 §4.1~4.3]

### 핵심 요약 (3줄)
1. config.toml은 **17개 섹션**으로 구성되어 VAMOS의 모든 일반 설정을 관리합니다.
2. V1(로컬/저비용) → V2(서버/중간) → V3(엔터프라이즈/고성능)으로 갈수록 모델, 인프라, 비용이 확장됩니다.
3. 각 버전별 프리셋 파일(`config.v1.toml`, `config.v2.toml`, `config.v3.toml`)이 제공됩니다.

---

## §36.3 LOCK / FREEZE 값 목록

> **LOCK/FREEZE란?**: 시스템의 안정성과 보안을 위해 **절대 변경할 수 없도록 잠긴 설정값**입니다. 이 값들을 바꾸면 시스템이 오작동하거나 보안 사고가 날 수 있어서 코드 레벨에서 강제합니다.

### LOCK 값 목록 — ⚠️ 변경 불가

| # | 설정 키 | 잠긴 값 | 사유 | 근거 |
|---|--------|--------|------|------|
| 1 | `core.single_decision_lock` | `true` (항상) | 단일 결정 원칙: 하나의 요청에 하나의 결정만 | D2 DecisionSchema |
| 2 | `core.pipeline_stages` | `["intake","plan","execute","verify","deliver"]` (5단계 고정) | 파이프라인 구조 변경 불가 | D5 WorkflowStageSchema |
| 3 | `logging.trace_id_required` | `true` (항상) | 모든 로그에 trace_id 필수 | AC-D4-005 |
| 4 | `mcp.transport` | `"streamable_http"` (유일한 값) | stdio 제거, streamable_http만 허용 | AC-D3-008, DEC-017 |
| 5 | `semantic_cache.similarity_threshold` | `>= 0.95` (최소값 LOCK) | 캐시 정확도 보장 | AC-D6-010 |
| 6 | `self_check.threshold_p0` | `70` | P0 도메인 셀프체크 기준 | LOCK |
| 7 | `self_check.threshold_p1` | `75` | P1 도메인 셀프체크 기준 | LOCK |
| 8 | `self_check.threshold_p2` | `80` | P2 도메인 셀프체크 기준 | LOCK |
| 9 | `self_check.soft_loop_max` | `1` | 소프트 루프 자동 재시도 1회 | LOCK |
| 10 | `approval.timeout_s` | `600` (10분) | 승인 미응답 시 자동 거부 | LOCK |
| 11 | `approval.p2_timeout_s` | `300` (5분) | P2/HITL 고위험 승인 타임아웃 | LOCK |
| 12 | `blue_nodes.active_node_cap` (V1) | `3` | V1 세션당 활성 Blue Node 상한 | LOCK-AT-014 |
| 13 | `ui.min_width` | `1280` (V1) | V1 데스크톱 전용 최소 너비 | D8 §3.1 LOCK |

[근거: B4 §3.8a, §3.8b, §6.2]

### 핵심 요약 (3줄)
1. LOCK/FREEZE 값은 시스템 안정성과 보안을 위해 **코드 레벨에서 강제**되는 변경 불가 설정입니다.
2. 핵심 LOCK 항목: 단일 결정 원칙(true), 5단계 파이프라인 고정, trace_id 필수(true), MCP streamable_http 전용.
3. 셀프체크 임계값(P0:70/P1:75/P2:80)과 승인 타임아웃(일반:10분/P2:5분)도 LOCK으로 보호됩니다.

---

## §36.4 VAL-001 ~ VAL-010 검증 규칙

> **비유**: 자동차 시동을 걸 때 **안전벨트 경고등, 문 열림 경고, 연료 부족 경고**가 자동으로 체크되듯, VAMOS도 설정을 로드할 때 **10개의 검증 규칙**을 자동 체크합니다. 하나라도 실패하면 시스템이 시작되지 않습니다.

### 10대 검증 규칙

| 규칙 ID | 검증 내용 | 관련 AC | 위반 시 |
|---------|---------|---------|--------|
| **VAL-001** | `mcp.transport`는 반드시 `"streamable_http"` | AC-D3-008 | 시작 거부 |
| **VAL-002** | Guardrails 4-Layer(L1~L4) 중 하나라도 실패 시 `fail_policy` 적용 | AC-D7-005 | 정책에 따라 deny/restrict |
| **VAL-003** | `rbac.roles`의 키는 `OWNER/ADMIN/OPERATOR/VIEWER`만 허용 | AC-D7-006 | 시작 거부 |
| **VAL-004** | `core.autonomy_level`은 `L0~L3`만 허용 | AC-D7-007 | 시작 거부 |
| **VAL-005** | `cost.block_threshold >= cost.warn_threshold` 필수 | D7 DownshiftSchema | 시작 거부 |
| **VAL-006** | `semantic_cache.similarity_threshold >= 0.95` (LOCK) | AC-D6-010 | 시작 거부 |
| **VAL-007** | `core.pipeline_stages`는 정확히 5단계 고정 | D5 WorkflowStageSchema | 시작 거부 |
| **VAL-008** | `core.single_decision_lock`은 항상 `true` | D2 DecisionSchema | 시작 거부 |
| **VAL-009** | `logging.trace_id_required`는 항상 `true` | AC-D4-005 | 시작 거부 |
| **VAL-010** | `graph_db.scope`는 V1일 때 `"P1"`, V2+일 때 `"FULL"` 권장 | AC-D6-009 | 경고 (시작은 가능) |

[근거: B4 §6.2]

### 설정 로딩 흐름

```
1. load_dotenv(".env")                     ← L1: 비밀 키 로드
2. toml_data = tomli.load("config/config.toml")  ← L2: 앱 설정 파싱
3. config = VamosConfig(**toml_data)        ← Pydantic v2 자동 검증 (VAL-001~010)
4. if V2+:
     db_overrides = load_runtime_config(db) ← L3: 런타임 오버라이드
     config = config.model_copy(update=db_overrides)
5. validate_version_consistency(config, VAMOS_VERSION_TIER)
6. return config                           ← 검증 통과 시 설정 반환
```

> **쉬운 말**: 시스템이 켜질 때 (1) 비밀 키를 읽고 → (2) 설정 파일을 읽고 → (3) 10개 규칙으로 검증하고 → (4) 서버 버전이면 DB에서 추가 설정을 덮어씌우고 → (5) 버전 일관성을 최종 확인합니다. [근거: B4 §6.3]

### 핵심 요약 (3줄)
1. VAMOS는 시작 시 **10개의 검증 규칙(VAL-001~010)**으로 모든 설정을 자동 검증합니다.
2. 9개 규칙(VAL-001~009)은 위반 시 **시작 자체를 거부**하고, VAL-010만 경고 수준입니다.
3. 설정 로딩은 `.env 읽기 → TOML 파싱 → Pydantic 검증 → DB 오버라이드 → 버전 확인` 순서로 진행됩니다.

---

## §36.5 schema_registry.toml (단일 참조점)

> **비유**: 도서관의 **도서 목록 카드**처럼, VAMOS의 모든 스키마(데이터 구조 설계도)가 어디에 정의되어 있는지 **한 곳에서 찾을 수 있는 등록부**가 schema_registry입니다.

### schema_registry의 역할

| 항목 | 설명 |
|------|------|
| **목적** | 모든 스키마의 **단일 등록점(Single Source of Truth)** |
| **위치** | Pydantic v2 ConfigModel의 `model_config` 내 `x-schema-registry` 속성 |
| **관리 원칙** | 각 스키마 문서(D2~D8)가 SOT이며, schema_registry는 이들의 위치를 가리키는 **포인터** |

### 스키마 정본(SOT) 소유권 분류

| 스키마 문서 | 소유 스키마 | 역할 |
|-----------|-----------|------|
| **D2** (ORANGE CORE) | DecisionSchema, LogEventSchema, EventTypeRegistry, FailureCodeRegistry, FallbackRegistry | 핵심 결정/로그/이벤트 |
| **D3** (BLUE NODES) | BlueNodeSchema, MCPBridgeLayerSchema | 실행 노드/MCP 연결 |
| **D4** (INFRA CORE) | ToolRegistrySchema, BrainAdapterResponseSchema, BackupConfigSchema, RateLimitConfigSchema | 인프라/도구/백업 |
| **D5** (AGENT WORKFLOW) | WorkflowStageSchema, AgentTaskSchema | 워크플로우/에이전트 |
| **D6** (STORAGE MEMORY) | MemoryRecordSchema, VectorStoreAdapterSchema, GraphRAGConfigSchema, SemanticCacheSchema | 저장/메모리/벡터/캐시 |
| **D7** (SAFETY COST) | PolicyCheckSchema, RBACRoleSchema, AutonomyLevelSchema, CostBudgetSchema, GuardrailsCheckSchema | 보안/비용/승인 |
| **D8** (UI UX) | UILayoutSchema, UIEventSchema | UI 레이아웃/이벤트 |

[근거: D2.1-D1 §4.2, B7 §1]

### 핵심 원칙

1. **단일 정본**: 각 스키마는 정확히 **하나의 문서(D2~D8)**에서만 정의됩니다. 다른 문서는 `REF-only`로 참조만 합니다.
2. **임의 확장 금지**: DESIGN 근거 없이 스키마 필드를 추가할 수 없습니다.
3. **버전 추적**: 모든 스키마는 `_meta` 블록에 `schema_version`, `owner_doc`, `ref` 정보를 포함합니다.

### 핵심 요약 (3줄)
1. schema_registry는 VAMOS의 모든 스키마가 **어디에 정의되어 있는지** 한 곳에서 관리하는 등록점입니다.
2. 각 스키마는 D2~D8 중 **정확히 하나의 문서**에서만 정본(SOT)으로 관리되며, 타 문서는 참조만 합니다.
3. 스키마 필드 추가/변경 시 반드시 **DESIGN 근거**가 필요하며, 임의 확장은 금지됩니다.

---

## 검증 체크리스트

- [x] 123개 이벤트 카테고리별 (SOT 기준 123개, 15개 카테고리로 분류)
- [x] 36개 에러코드 (6개 카테고리로 분류)
- [x] 23개 폴백 (기존 14개 + UI Layer 9개)
- [x] FailureCode → Fallback 매핑 (22개 매핑 전수 기재)
- [x] NEVER_AUTO 목록 (수리 액션 10개 + 보안 에러 6개)
- [x] 로깅 스택 V1/V2/V3 비교 표
- [x] config.toml 17섹션 일람표
- [x] LOCK/FREEZE 목록 (13개 항목)
- [x] VAL-001~010 검증 규칙
- [x] 비유 설명 포함 (각 섹션 도입부)
- [x] 근거 SOT 참조 표기 (모든 주요 항목)
