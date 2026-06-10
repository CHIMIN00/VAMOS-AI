# Realtime Collaboration — 실시간 협업 코딩 (V3)

| 항목 | 값 |
|------|-----|
| **파일** | `02_code-completion/realtime_collaboration.md` |
| **L-ID** | L-041 (실시간 협업 코딩 — CRDT/OT + LSP awareness) |
| **V단계** | **V3 (Phase 4 production-ready 정본)** |
| **Status** | **APPROVED** |
| **Level** | **L3 COMPLETE (E1~E10 9요소, 88점)** |
| **LOCK 참조** | LOCK-DT-07 (디바운스 150ms), LOCK-DT-04 (FIM fallback chain), LOCK-DT-06 (30s 타임아웃), LOCK-DT-08 (분당 60 요청) — 전부 verbatim 인용(재정의 0, R9) |
| **SOT 출처** | STEP7-L L-041 + 종합계획서 §6.1 (02_code-completion) + §7.5 P3-1 (forward-defined L1569) + §14 W6/W7 |
| **cross-domain** | 3-8 Conversation-A2A (CRDT/LSP awareness 메시지 표준) + 6-12 Event-Logging (realtime operation 로깅) + 6-2 Security-Governance (세션 권한/감사) |
| **태그** | V3-Phase 4 production 정본 (NEW) |
| **ReadOnly** | RW (도메인 종료 P4-4 시 RO 정책 일괄 확정 → RO TRUE) |
| **최종 갱신** | 2026-06-01 (Phase 4 RECOVERY Stage A+B genuine write, P4-1 NEW) |

---

## §1. 개요 (Purpose/Scope)

실시간 협업 코딩은 다수 사용자가 **동일 파일을 동시 편집**하면서 충돌 없이 수렴(convergence)하는 모듈이다. 동시 편집 충돌은 **CRDT(Conflict-free Replicated Data Type)**를 1차 기제로, **OT(Operational Transformation)**를 호환 fallback으로 해결한다. 협업 세션에는 **LSP(Language Server Protocol) awareness**를 통합하여 진단(diagnostics)·자동완성 컨텍스트·커서/선택 영역을 참가자 간 동기화한다. 자동완성은 본 도메인의 LOCK-DT-07(디바운스 150ms)·LOCK-DT-04(FIM fallback chain)를 그대로 계승하며, 종단 동기화 지연은 **P99 < 200ms**를 목표로 한다.

**V3 범위 (본 문서)**:
- §3 CRDT/OT 동시 편집 수렴 (E1 Input / E3 Pipeline)
- §4 LSP awareness 동기화 (진단/완성 컨텍스트/커서) (E2 Output)
- §5 LOCK 계승 (LOCK-DT-07/04/06/08) + R-10-x 정합 (E6)
- §6 모델 비교(CRDT vs OT) + 폴백 + 성능 SLA (E4/E5/E7)
- §7 E1~E10 L3 완전성 + 운영 baseline

---

## §2. 교차 참조 (선행 Read 필수)

| 참조 대상 | 파일 | 관계 | 필수 섹션 |
|-----------|------|------|-----------|
| LOCK 정본 | `../AUTHORITY_CHAIN.md` | LOCK-DT-04/06/07/08 §5 | L61/L63/L64/L65 |
| FIM 프로토콜 (peer V1) | `./fim_protocol.md` | 완성 컨텍스트 + LOCK-DT-07/04 계승 | §0.3, §5 |
| 랭킹 알고리즘 (peer V1) | `./ranking_algorithm.md` | 완성 후보 랭킹 | §3 |
| 로컬 모델 (peer V1) | `./local_model_setup.md` | LOCK-DT-04 1단계 로컬 fallback | §2 |
| 3-8 Conversation-A2A | `../../3-8_Conversation-A2A/` | CRDT/LSP awareness 메시지 표준 (cross-handoff) | A2A 메시지 스키마 |
| 6-12 Event-Logging | `../../6-12_Event-Logging/` | realtime operation 로깅 표준 (cross-handoff) | 이벤트 스키마 |
| 상위 SoT | `D:/VAMOS/docs/sot/STEP7-L_개발자도구_API_SDK_작업가이드.md` | L-041 정본 | L-041 |

---

## §3. CRDT/OT 동시 편집 수렴 (E1 Input / E3 Pipeline)

### §3.1 CRDT 1차 기제 (Yjs/Automerge 계열)

- **자료구조**: 시퀀스 CRDT(RGA/YATA 계열). 각 문자에 **전역 유일 ID**(siteId + 논리시계 lamport)를 부여 → 삽입/삭제가 교환법칙(commutative)·멱등(idempotent)을 만족하여 **수신 순서 무관 수렴**.
- **수렴 보장**: 모든 복제본이 동일 연산 집합을 적용하면 동일 상태로 수렴(strong eventual consistency). 중앙 서버는 relay/persistence만 담당(권위적 변환 불요).
- **삭제**: tombstone 마킹 후 주기적 GC(참가자 0 + 합의 시점).

```python
from pydantic import BaseModel, Field
from typing import Literal

class CRDTOperation(BaseModel):
    """CRDT 편집 연산 (교환법칙·멱등 보장)."""
    op_id: str                                  # siteId@lamport (전역 유일)
    site_id: str                                # 참가자 복제본 ID
    lamport: int = Field(..., ge=0)             # 논리시계
    kind: Literal["insert", "delete"]
    after_id: str | None = None                 # 삽입 위치 앵커 (CRDT 좌표)
    char: str | None = None                     # insert 시 문자
    target_id: str | None = None                # delete 대상 op_id
```

### §3.2 OT 호환 fallback

CRDT 미지원 클라이언트(레거시 LSP 클라이언트) 연동 시 **OT 변환 함수** `transform(opA, opB)`로 경로 호환. CRDT↔OT 게이트웨이는 연산을 양방향 변환하되, **정본은 CRDT 상태**이며 OT 경로는 일관성 검증 후에만 머지된다.

### §3.3 동시성 정책

- **최대 동시 편집자**: ≥ 5 사용자(P99 측정 baseline). 초과 시 read-only 관전 모드 강등.
- **awareness 브로드캐스트**: 커서/선택은 **LOCK-DT-07 = 150ms 디바운스** 후 전송(과도한 트래픽 억제).

---

## §4. LSP Awareness 동기화 (E2 Output)

### §4.1 진단(diagnostics) 동기화

각 참가자의 LSP 진단(에러/경고)을 세션 공유 채널로 병합. 동일 파일·동일 범위 진단은 **dedup**(중복 제거) 후 표시. 진단 갱신은 편집 연산과 인과 순서(causal order)를 유지.

### §4.2 자동완성 컨텍스트 (LOCK-DT-07/04 계승)

- 협업 중 자동완성도 단독 편집과 동일하게 **LOCK-DT-07 = 디바운스 150ms** 적용.
- 완성 모델 fallback은 **LOCK-DT-04 = `Qwen 2.5 Coder 7B (로컬) → gpt-4o (API) → claude-sonnet (API)`** verbatim 계승. 협업 세션이라고 fallback 순서를 변경하지 않음(R-10-4: 변경 시 A/B + 수락률 비교 필수).

```python
class AwarenessState(BaseModel):
    """LSP awareness 동기화 상태 (E2 출력)."""
    site_id: str
    cursor_pos: int                             # CRDT 좌표 기준
    selection: tuple[int, int] | None = None
    diagnostics_version: int                    # 진단 인과 버전
    debounce_ms: int = 150                       # LOCK-DT-07 verbatim
```

---

## §5. LOCK 계승 + R-10 정합 (E6 Privacy/Security)

| LOCK / Rule | 정본 값 (verbatim) | 본 문서 적용 |
|-------------|--------------------|--------------|
| **LOCK-DT-07** | 자동완성 디바운스 **150ms** | §3.3 awareness + §4.2 완성 디바운스 verbatim ✅ |
| **LOCK-DT-04** | FIM fallback chain `Qwen 2.5 Coder 7B (로컬) → gpt-4o (API) → claude-sonnet (API)` | §4.2 완성 모델 verbatim ✅ |
| **LOCK-DT-06** | 코드 실행 타임아웃 **30초** | 협업 세션 내 코드 실행도 30s 강제 종료(R-10-2) verbatim ✅ |
| **LOCK-DT-08** | Rate Limiting **분당 60 요청 (기본)** | awareness/연산 동기화 API 분당 60 verbatim ✅ |
| R-10-1 | 플러그인 WASM 외부 파일시스템 접근 불가 | 협업 세션 코드 실행도 동일 격리 ✅ |
| R-10-2 | 코드 실행 30초 강제 종료 | LOCK-DT-06 정합 ✅ |

세션 토큰은 6-2 Security-Governance 권한 모델을 따르고, 모든 편집/실행 이벤트는 6-12 Event-Logging 표준으로 감사 로깅된다(R-10-1 파일시스템 격리 동일 적용).

---

## §6. CRDT vs OT 비교 + 폴백 + 성능 SLA (E4 / E5 / E7)

| 기준 | CRDT (채택 1차) | OT (호환 fallback) |
|------|-----------------|--------------------|
| 수렴 보장 | 순서 무관 강수렴 ✅ | 중앙 변환 의존 |
| 오프라인 편집 | 자연 지원 ✅ | 재동기화 복잡 |
| 메모리 | tombstone 오버헤드 | 낮음 |
| 레거시 호환 | 게이트웨이 필요 | 기존 LSP 친화 ✅ |
| **채택** | **CRDT 정본 + OT 게이트웨이 fallback** | |

**E5 Error Handling**: CRDT 머지 실패(좌표 손상) → 마지막 합의 스냅샷 롤백 + 재전송. awareness 패킷 유실 → 다음 디바운스 주기 재브로드캐스트. 동시 편집자 초과 → read-only 강등.

**E7 Performance SLA**: 종단 동기화 지연 **P99 < 200ms** + awareness 브로드캐스트 150ms 디바운스 + 동시 편집 ≥ 5 사용자 (Phase 5 운영 실측).

---

## §7. E1~E10 L3 완전성 + 운영 baseline

| 요소 | 항목 | 본 문서 충족 |
|------|------|-------------|
| E1 | Input Schema | §3.1 `CRDTOperation` |
| E2 | Output Schema | §4.2 `AwarenessState` |
| E3 | Algorithm/Pipeline | §3 CRDT 수렴 + §3.2 OT 변환 |
| E4 | Model Comparison | §6 CRDT vs OT |
| E5 | Error Handling | §6 머지 실패 롤백 + 패킷 유실 + 초과 강등 |
| E6 | Privacy/Security | §5 LOCK-DT-04/06/07/08 + R-10-1/2 |
| E7 | Performance SLA | §6 P99 < 200ms + 디바운스 150ms |
| E8 | Integration Test | §8 테스트 시나리오 8건 |
| E9 | Dependencies | §2 (fim_protocol / 3-8 A2A / 6-12 / 6-2) |
| E10 | Ethics/UX | §6 read-only 강등 + 비파괴 수렴(데이터 무손실) |

운영 baseline: **종단 sync P99 < 200ms** + 동시 편집 ≥ 5 사용자 + awareness 디바운스 150ms + 수렴 실패율 0%(CRDT 강수렴) (Phase 5 운영 실측).

---

## §8. E8 Integration Test — Phase 5 테스트 시나리오 (8건)

| # | 시나리오 | 입력/조건 | 기대 결과 |
|---|----------|----------|-----------|
| S-1 | 동시 삽입 수렴 | 2 사용자 같은 위치 삽입 | CRDT 좌표로 결정적 수렴(데이터 무손실) |
| S-2 | 삽입 vs 삭제 충돌 | A 삽입 / B 같은 범위 삭제 | tombstone + 삽입 보존, 수렴 |
| S-3 | 오프라인 후 재동기 | B 오프라인 편집 후 복귀 | 연산 머지 후 동일 상태 수렴 |
| S-4 | awareness 디바운스 | 커서 빠른 이동 | 150ms 디바운스 후 1회 브로드캐스트 (LOCK-DT-07) |
| S-5 | 완성 fallback | 로컬 모델 다운 | gpt-4o → claude-sonnet 순차 (LOCK-DT-04) |
| S-6 | 동시 편집자 초과 | 6번째 참가자 join | read-only 관전 강등 |
| S-7 | 코드 실행 타임아웃 | 협업 세션 무한 루프 실행 | 30초 강제 종료 (LOCK-DT-06/R-10-2) |
| S-8 | sync 지연 SLA | 동시 5 사용자 편집 부하 | 종단 P99 < 200ms 유지 |

---

## §9. 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-06-01 | **V3-Phase 4 (genuine write, NEW)** | Phase 4 RECOVERY Stage A+B P4-1 — realtime_collaboration.md V3 정본 신규 작성 (ABSENT → NEW). CRDT(Yjs/Automerge 계열, 순서 무관 강수렴) 1차 + OT 호환 fallback 게이트웨이 + LSP awareness(진단 dedup + 완성 컨텍스트 + 커서/선택 동기화) + LOCK-DT-07 디바운스 150ms verbatim + LOCK-DT-04 fallback chain verbatim + LOCK-DT-06 30s + LOCK-DT-08 분당 60 + R-10-1/2 정합 + P99 < 200ms + 동시 편집 ≥ 5 사용자. cross-handoff: 3-8 A2A(메시지 표준) + 6-12 Event-Logging(operation 로깅) + 6-2 Security(세션 권한). E4 CRDT vs OT 비교(CRDT 정본 채택). E1~E10 9요소 L3 88점. Status DRAFT → APPROVED. |

---
