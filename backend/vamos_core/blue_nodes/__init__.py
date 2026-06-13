"""BLUE NODES 패키지 (4-6) — V0 디렉토리 스캐폴딩만 (구현 0).

V0 스코프 도메인 3종(정본 = D2.0-03 L353~357 / PHASE_B2 §5.3): dev · research · content.
(quant = V1, trading = V2+/investment — 본 스캐폴딩 제외.)

⚠️ 노드 로직(E-Series E-1~E-6 실행기)은 **V1-Phase 3**에서 구현한다. V0에서는 디렉토리 +
도메인 명칭 주석만 둔다(no-create 외 골격). NODE_REGISTRY_SEED(registries.py)는 현재
bn_web_research(domain=research) 1건만 시드 — 3 도메인과 충돌 없음.

※ 로드맵 L379의 노드 명칭 'Dev/Research/Productivity'는 SOT 실측과 불일치 —
  정본은 content(D2.0-03 L353~357). 'Productivity'는 D2.0-03 L214 *도메인 예시*(오기).
  SOT/로드맵 수정 금지 → edits 명기·승인대기(_targets/p4_2_roadmap_edits_pending.md).
"""

#: V0 BLUE NODE 도메인 (디렉토리 스캐폴딩 분모 — 구현 0)
V0_BLUE_NODE_DOMAINS: tuple[str, ...] = ("dev", "research", "content")
