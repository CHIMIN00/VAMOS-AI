# P4-2 로드맵 edits 명기 (승인 대기 — SOT/로드맵 수정 금지)

> 작성: 2026-06-13 (P4-2 STEP 7) · 상태: ✅ **RESOLVED 2026-06-13**(사용자 재검증 승인 — D2.0-03 L213 도메인예시 vs L353~357 노드명 Content 직접 확인, 오판 아님 확정 → 마스터 로드맵 L379 'Productivity'→'Content' 교정 집행) · 위반 시 §1.3.1 #1

## E-1. 로드맵 L379 BLUE NODE 노드 명칭 'Productivity' 오기 — ✅ RESOLVED

- **현재(로드맵 L379)**: 4-6 BLUE NODE 3종 = "Dev / Research / **Productivity**"
- **정본(SOT 실측)**:
  - `D2.0-03` L353~357 = Dev / Research / **Content** / Quant / Trading Node (노드명 정본)
  - `D2.0-03` L214 = 도메인 *예시* 목록에 'Productivity' 등장 — **도메인 예시이지 노드명 아님**
  - `PHASE_B2 §5.3`(L367~) blue_nodes/ = dev/research/content/quant/trading (V0 4-6 = 앞 3개)
- **판정**: 로드맵 L379 'Productivity'는 오기. V0 BLUE NODE 정본 3 도메인 = **dev / research / content**.
- **집행(본 세션)**: 스캐폴딩은 SOT 정본(content) 기준 생성(`backend/vamos_core/blue_nodes/{dev,research,content}/`).
  로드맵 L379 텍스트는 **수정하지 않음**(edits 명기·승인 대기 — SOT/로드맵 물리수정 금지 규칙).
- **권고 수정(승인 시)**: 로드맵 L379 "Productivity" → "Content" (D2.0-03 L353~357 정합).

## 참고 — 본 세션이 수정하지 않은 잠금 정본
- contracts.py(25모델) · registries.py(NODE_REGISTRY_SEED 1건 research) · SOT(docs/sot·sot 2) — 무변경.
