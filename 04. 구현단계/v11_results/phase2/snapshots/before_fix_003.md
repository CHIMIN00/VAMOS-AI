# Before Fix 003 — FG-B03: SelfCheckGate 실행 위치 명확화
# Snapshot at: 2026-03-12

## L970-977 (§2 STEP-4 섹션 3: I-5 Decision Engine)
```
최소 4-Gate 구현 (V0), V1에서 5-Gate로 확장:
- PolicyGate: I-8 stub 호출 → 기본 allow, deny 목록 매칭 시 deny
- CostGate: I-9 stub 호출 → 80% warn, 100% block (config.v1.toml 값 참조)
- ApprovalGate: priority level 체크 → P2 감지 시 hold 반환
- EvidenceGate: 스텁 → 항상 sufficient 반환
- **SelfCheckGate (M-14)**: V0에서는 스텁 (항상 pass). V1에서 I-6 Self-check 엔진과 연동. **파이프라인 위치: verify 노드 (execute 다음, deliver 이전)** — S5(Execute)→SelfCheck→S6(Deliver)
- Gate 결과를 종합하여 DecisionSchema 생성 (locked=true)
- Gate 실행 순서: Policy → Approval → Cost → Evidence → **SelfCheck** (CLAUDE.md §7.2 정본 + M-14 보강)
```

## L1011 (§2 STEP-4 파이프라인 코드)
```
graph.add_node("plan", plan_node)          # I-2 Context Builder + I-5 Decision
```

## L1013 (§2 STEP-4 파이프라인 코드)
```
graph.add_node("verify", verify_node)      # SelfCheckGate 위치 (M-14): V0=스텁(pass), V1=I-6 연동
```

## L1494 (§3 V1 LOCK 값)
```
> - I-5: 5-Gate 순서 LOCK (Policy→Approval→Cost→Evidence→SelfCheck)
```

## L1540 (§3 V1 완료 검증)
```
| 2 | 5-Gate 전체 동작 | Policy → Approval → Cost → Evidence → SelfCheck 순서 실행 확인 (CLAUDE.md §7.2) | ✅ |
```
