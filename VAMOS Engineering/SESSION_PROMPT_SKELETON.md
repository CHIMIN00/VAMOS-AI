# 세션 프롬프트 필수 골격 — 갭폐쇄 훅 (Opus 4.8 = Fable 5급 보장)

> **제정일**: 2026-06-13 · **위상**: 표준(STANDARD) — 모든 Phase 세션 프롬프트의 필수 포함 항목
> **근거**: `decisions/PHASE4-DEC-011_Opus-Fable_갭폐쇄_수단_및_SOP.md` (§A 도구·§B SOP·§C 보류·§D 경계·§E 모드)
> **목적**: 새 창(컨텍스트 0)에서 P4-3 이후 모든 Phase 프롬프트를 작성·실행할 때, 갭폐쇄 하네스/SOP가 **누락 없이 자동 적용**되도록 강제한다. 도구는 이미 커밋됨(`21ff6c4`) — 본 골격은 "프롬프트가 그 도구·모드를 *반드시 행사*하게" 만드는 규칙이다.

---

## 0. 적용 규칙 (MUST)

**P4-3·5·6·7·8의 모든 세션 프롬프트는 아래 H1~H8을 빠짐없이 포함한다.** 누락 시 그 프롬프트는 미완성(갭폐쇄 미적용 = Opus가 baseline 하네스로만 동작, Fable급 아님). 프롬프트 자체 검증(STEP 1 류)에 "H1~H8 포함 확인"을 넣는다.

---

## H1. 참조 (필수 Read)
- `VAMOS Engineering/decisions/PHASE4-DEC-011_Opus-Fable_갭폐쇄_수단_및_SOP.md` (§A~§E 전체)
- `VAMOS Engineering/SESSION_PROMPT_SKELETON.md` (본 문서)
- §A 도구 실존: `scripts/verify_artifacts.py`·`check_lockfiles.py`·`trace_matrix.py`(+`artifact_manifest.json`·`trace_matrix.map.json`) — 부재 시 갭폐쇄 미커밋 의심·즉시 보고

## H2. 산출물 실존 검증 STEP (R16 착시 방어 — Must, 어떤 Should에도 의존 금지)
프롬프트의 산출물 검증 STEP에 **반드시** 포함:
- **그 Phase 전용 매니페스트를 작성**(해당 Phase 산출물 경로+min_bytes+must_contain) → `python scripts/verify_artifacts.py <Phase매니페스트> --root .`(리포 루트서 실행) → PASS/FAIL 0.
  - ⚠️ **무인자 실행 금지**(무인자 = 갭폐쇄 기본 매니페스트만 검증 → 그 Phase 산출물 미검증인데 GREEN 착시).
- **명세↔테스트 추적(IV-3)**: `trace_matrix.map.json`에 그 Phase 요구사항↔테스트 매핑 추가 → `python scripts/trace_matrix.py --root .` 미커버 0·허위매핑 0.
- **락파일 정합(V-2)**: `python scripts/check_lockfiles.py --root .` drift 0 (신규 스택 생성 시 그 락파일 포함).

## H3. 실행 모드 (§E 티어 — Must)
| 작업 유형 | 모드 |
|---|---|
| 사소·기계적(config·보일러플레이트·단일파일) | Opus 평이 effort + 자동 하네스 |
| 표준 구현 모듈 | **effort high/max** + 자동 하네스 + 상시 자동 리뷰(II-3) |
| **고위험 모듈**(5-Gate·IPC·serde·spawn·RAG·라우팅·마이그레이션·A2A·self-evo) | **ultracode 워크플로**(II-1 적대검증 + II-2 N회 앙상블·심판 + II-4 역할분리[계획→구현→검증 별 컨텍스트] + III-3 독립검증) + effort max |
| **모든 GO/NO-GO 게이트**(P4-3·5-8·6-9·7-4·8-4) | **ultracode 워크플로**(II-5 loop-until-dry + II-6 교차모델 감사 + VI-3 완전성 비평가 + II-1/II-2) |
- 모델: Opus 4.8 (Fable 5 접근 복구 시 Fable). effort-max는 *기본 깊이*이며 단독으로는 갭 폐쇄 불가 — 고위험·게이트는 워크플로 필수.
- **VI-1 에스컬레이션(Must)**: 모듈이 검증 N회(권장 3) 실패 시 Fable(접근 복구 시)/사람으로 라우팅 — Opus 무한재시도 금지.

## H4. §C 보류항목 just-in-time 적용 (Must — 타깃 코드 생성 phase에 *동시* 적용)
> ⚠️ **세션라벨 ≠ 로드맵 작업번호**: P4-3=Phase 4 *게이트*(신규 코드 0), 로드맵 4-3=Tauri/프론트(세션 P4-2서 수행). §C 부착은 ADR §C 보류대장 부착열 기준. §C 9항(I-1~9) 부착열 9/9 ADR 일치(I-1/I-6/I-7/I-8은 다시점 부착).
| 세션 | 집행할 §C 항목 (PHASE4-DEC-011 §C 부착열) | ADR-게이트(§D) |
|---|---|---|
| P4-2 (로드맵 4-1/4-3/4-6) | **I-1** Rust/TS 하네스(4-3 셸 직후 — clippy/eslint/vitest 로컬)·**I-6** 골든/스냅샷(IPC 페이로드·생성 스키마, 4-2)·**I-8** 런타임 계약(4-1 — 4-1분은 잠긴 mypy strict로 충족, 신규 IPC 런타임검증은 5-4); VI-2 인간(IPC 계약 JSON-RPC 13) | I-1 CI job·I-6 신규 테스트 = PHASE4-DEC-012 선행 |
| P4-3 (Phase 4 Gate) | 신규 코드 0 — **게이트=H3 풀적용**(ultracode+교차모델+VI-3) | — |
| Phase 5 (V0 검증/GO) | **I-6** 골든/스냅샷(5-4)·**I-7** IPC/MCP 퍼징(5-7a)·**I-8** 런타임 계약(5-4); VI-2 인간(IPC 계약); 게이트 5-8=H3 풀 | I-6 신규 테스트 = ADR 선행 |
| **Phase 6 (V1)** | **I-1** 완성(6-5 clippy/eslint/vitest/Playwright→CI)·**I-2** 뮤테이션·**I-3** 커버리지 래칫·**I-4** 프로퍼티·**I-5** 메타모픽(RAG/에이전트)·**I-7** 퍼징(6-8)·**I-9** V0→V1 회귀코퍼스; VI-2 인간(5-Gate·Permission Matrix); 게이트 6-9=H3 풀 | 신규 테스트도구(I-2/4)·CI job(I-1/3) = `PHASE4-DEC-012+` ADR 선행 |
| Phase 7 (V2) | **I-5** 메타모픽(마이그레이션/인프라)·I-1 확장; VI-2 인간(마이그레이션 스크립트); 게이트 7-4=H3 풀 | 신규 CI job = ADR |
| Phase 8 (V3) | **I-5** 메타모픽(self-evo/A2A); VI-2 인간(Federated/A2A); 게이트 8-4=H3 풀 | 신규 CI job = ADR |
- 원칙: §C는 "능력 한계"가 아니라 *순서/성숙도* 보류 — 타깃 코드가 생기는 phase에서 그 코드와 *동시*(harness-first/concurrent)에 적용. 코드보다 그물이 늦는 구간 0.
- VI-2 인간 체크포인트 적용 모듈 전수(ADR §B VI-2): IPC 계약(P4-2/5)·5-Gate·Permission Matrix(6)·V2 마이그레이션(7)·A2A·Federated(8).

## H5. 수렴 STEP (loop-until-dry — Must)
산출물 검증 STEP 말미에 적대 라운드를 **신규 발견 0 라운드까지 반복** → "수렴 선언". 게이트 프롬프트는 이 적대 라운드를 ultracode 워크플로(독립 리뷰어 + 완전성 비평가 + 교차모델)로 구성.

## H6. 베이스라인 불변식 (Must — 잠긴 Phase 2/3 하네스, 변경 금지)
- 매 커밋: ruff(13룰)·mypy strict·vamos_lint(VL-001~005)·pytest → PASS → 커밋. (Rust/TS 생성 시 cargo build/test·tsc/eslint 로컬 하네스 동시)
- EOL LF·`.gitattributes` 준수 / SOT(docs/sot·sot 2) 수정금지(edits 명기·승인) / 브랜치 체크아웃 금지(main 동기=`git fetch . <branch>:main`) / 수치 인용 전 디스크 ReadAllLines 실측 / git-클린 판정은 *세션 스코프 경로*로 한정(리포 사전존재 untracked 다수는 스코프 외).
- **V-1 생성 결정성(Must)**: 코드생성 시 모델 id + temperature(저/0) 고정 + 런 메타(모델·시각·입력해시) 기록(A17의 *생성* 확장) — 재현·감사 가능성 확보.

## H7. 컨텍스트 규율 (§B IV — Must, 컨텍스트 0 새 창일수록 결정적)
프롬프트의 각 구현 STEP은 아래를 전제로 한다:
- **IV-1 컨텍스트 팩**: 작업별로 *해당 PART2 STEP + SOT 발췌 + 관련 LOCK + 스키마만* 로드(잡음 최소 → 환각/이탈 감소).
- **IV-2 원자적 분해**: 작업 단위를 *오라클(테스트/타입/LOCK)이 완전히 경계 지을 수 있는 최소*로 쪼갠다.
- **IV-4 STEP 사전점검 체크리스트**: 단계 진입 전 필요한 입력(SOT·스키마·선행 산출물)이 다 있는지 확인 후 진입(입력 누락 0).

## H8. 단계별 effort 결정·태깅 (Must — 프롬프트 헤더 + 각 STEP)
**규칙**: ① 세션 헤더 effort = 그 세션 STEP 중 *최대* effort 명시. ② 각 STEP 라인에 effort 태그를 부여(프롬프트 작성 시 자동 포함). ③ 모델 = Opus 4.8(Fable 5 접근 복구 시 Fable). effort는 *기본 깊이*, 갭폐쇄는 ultracode(uc) 층(H3/§E)이 담당.

**effort 결정 (작업 성격 기반):**
| effort | 적용 기준 | 예 |
|---|---|---|
| **medium** | 순수 전사·스캐폴딩·디렉토리·config 키·문서 (창의성·동시성 0, 오라클 자명) | config·BLUE NODE 디렉토리·Registry 전사 |
| **high** | 표준 구현 모듈·정합 검증·Eval (로직 有·명세 명확·단일 오라클) | Registry 정의·X2/X3·D3 정합·Eval·API 정합 |
| **max + uc** | 고위험: 3언어 seam·상태기계·동시성/spawn·RAG/에이전트·보안·DB 마이그레이션·self-evo·A2A + **착수 게이트(6-0/7-0/8-0)** | 타입동기화·ORANGE CORE·IPC/serde·CORE 활성화·LangGraph+RAG·마이그레이션·Agent Teams·self-evo·착수게이트 |
| **max + uc + 교차모델** | 전 GO/NO-GO 게이트 + Phase 4 게이트(P4-3) (II-6) — 착수 게이트(6-0/7-0/8-0)는 *제외*(max+uc) | P4-3·5-8·6-9·7-4·8-4 |

**Phase별 STEP effort 지도 (정본 — 프롬프트 작성 시 이 분류로 STEP 태깅):**
- **Phase 4(V0)**: 4-1 타입동기화(A20 왕복) `max+uc` · 4-2 ORANGE CORE(5-Phase+Gate+Defense) `max+uc` · 4-3 IPC/serde/spawn/Tauri `max+uc` · 4-4 Registry `high` · 4-5 config `medium` · 4-6 BLUE NODE 디렉토리 `medium` · 4-7 X2 `high` · **P4-3 게이트 `max+uc+교차`**
- **Phase 5(검증/GO)**: 5-1 Eval·5-2 QoD `high` · 5-3~5-6 D3 정합 `high` · 5-7 X3·5-7a 배포무결성 `high` · **5-8 GO/NO-GO `max+uc+교차`**
- **Phase 6(V1)**: **6-0 P6-0 게이트 `max+uc`** · 6-1 D1'·6-2 환경확장 `high` · **6-3 CORE 활성화 `max+uc`** · **6-4 에이전트+RAG `max+uc`** · 6-5 E2E UI `high` · 6-6 운영·6-7 Eval(I-2 setup은 uc)·6-8 API정합·6-8a 배포 `high` · **6-9 GO/NO-GO `max+uc+교차`**
- **Phase 7(V2)**: **7-0 게이트 `max+uc`** · **7-1 인프라 마이그레이션 `max+uc`+VI-2 인간(R17)** · 7-2 COND 활성화 `high` · **7-3 Agent Teams+보안 `max+uc`** · **7-4 GO/NO-GO `max+uc+교차`**
- **Phase 8(V3)**: **8-0 게이트 `max+uc`** · **8-1 인프라(K8s/vLLM) `max+uc`+VI-2 인간** · **8-2 self-evo/EXP 모듈 `max+uc`** · **8-3 A2A/Marketplace `max+uc`+VI-2 인간** · **8-4 GO/NO-GO `max+uc+교차`**

> 구현 세션은 대부분 ≥1 고위험 STEP 포함 → **세션 헤더 effort = `max`가 표준**. 순수 스캐폴딩/문서 전용 세션만 high/medium. (uc=ultracode 워크플로, §E/H3 정합)

---

## 부록 — 프롬프트 STEP에 박을 표준 문구 (복사용)

```
■ 헤더(H8): 모델 Opus 4.8(Fable 5 접근 복구 시 Fable), effort=세션 최대 STEP(구현 세션 보통 max) — 각 STEP 라인에 effort 태그(H8 Phase지도: medium/high/max+uc/max+uc+교차)
■ STEP(준비·H7 §B IV): IV-1 컨텍스트 팩(해당 PART2 STEP+SOT 발췌+LOCK+스키마만 로드) · IV-2 원자적 분해(작업=오라클 경계 가능 최소) · IV-4 사전점검 체크리스트(입력 누락 0 확인 후 진입)
■ STEP(검증): 산출물 실존(§A III-1/2/4) — <Phase>전용 매니페스트 작성 → python scripts/verify_artifacts.py <매니페스트> --root . (무인자 금지) PASS/0
   + trace_matrix.map.json 매핑 추가 → trace_matrix.py --root . 갭0·허위0 + check_lockfiles.py --root . drift0
■ STEP(검증·적대): [게이트/고위험이면] ultracode 워크플로 — 독립 적대 리뷰어(II-1) + II-2 N회 앙상블·심판 + II-4 역할분리 + III-3 독립검증 + VI-3 완전성비평가 (게이트는 II-6 교차모델) → 신규발견 0까지 loop-until-dry → 수렴 선언
■ 모드: 표준=effort high/max+하네스+상시리뷰(II-3) / 고위험·게이트=ultracode max (PHASE4-DEC-011 §E). VI-1: 검증 3회 실패→Fable/사람 라우팅(무한재시도 금지). V-1: 생성 모델id+temp 고정·런 메타.
■ §C: 본 Phase 타깃 코드에 해당하는 §C 항목 동시 적용(H4 표; 신규 도구/CI job은 PHASE4-DEC-012 ADR 선행). VI-2: 고폭발반경 모듈(IPC·5-Gate·Permission Matrix·마이그레이션·A2A)은 인간 체크포인트.
```

> ※ **후속(P4-2 완료 후)**: `ROADMAP_SESSION_EXECUTION_PROMPTS.md` 상단(§0)에서 본 골격을 "전 Phase 프롬프트 필수"로 링크. (P4-2 동시 실행 중이라 본 제정 시점엔 미편집 — 레이스 방지)
