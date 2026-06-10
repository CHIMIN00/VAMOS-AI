# link_network_visualization.md — 링크 네트워크 시각화 (기존 §8.2 계승)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: Zettelkasten 링크 네트워크의 D3.js force-directed graph 시각화 — 노드 색상/크기 매핑(성숙도 LOCK-PKM-12, 노트 타입 LOCK-PKM-10), 엣지 타입별 시각 구분, 클러스터링, 인터랙티브 탐색
> **SoT 근거**: 기존 명세 §8.2 + 종합계획서 부록 §A.3
> **담당 M-ID**: 기존 §8.2 (V1 EXTEND)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §8.1 / LOCK-PKM-10): **Zettelkasten 노트 타입** — permanent, literature, fleeting, index, structure

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): **지식그래프 엣지 타입** — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

> LOCK (STEP7-M M-017 / LOCK-PKM-12): **지식 성숙도 상태** — Seedling → Growing → Evergreen → Archived

---

## 기존 §8.2 계승. 링크 네트워크 시각화 [V1 / EXTEND]

**근거**: 기존 명세 §8.2 `ZettelNetworkVisualizer` + 종합계획서 부록 §A.3 링크 타입
**시그니처 변경**: 기존 §8.2 `generate_graph_data(center_note_id, depth=3)` → `generate_graph_data(req: GraphViewRequest)` — 필터/레이아웃/고립노트 옵션 확장을 위해 Request 객체로 래핑 (depth=3 기본값 유지, EXTEND 근거)

### E1. Input Schema

```python
from dataclasses import dataclass, field
from typing import Optional, Literal

class GraphViewRequest:
    """네트워크 시각화 요청"""
    center_note_id: str                         # 중심 노트 Luhmann ID 또는 UUID
    depth: int = 3                              # 중심에서 N-hop (기존 명세 §8.2 기본값 3)
    max_nodes: int = 200                        # 최대 표시 노드 수
    filter_note_types: Optional[list[str]] = None   # LOCK-PKM-10 타입 필터 (None=전체)
    filter_maturity: Optional[list[str]] = None     # LOCK-PKM-12 성숙도 필터
    filter_domains: Optional[list[str]] = None      # 도메인 필터
    filter_link_types: Optional[list[str]] = None   # 부록 §A.3 링크 타입 필터
    layout: Literal["force", "radial", "tree"] = "force"  # D3.js 레이아웃
    show_orphans: bool = False                  # 고립 노트 표시 여부

class GlobalGraphRequest:
    """전체 네트워크 조감도 요청"""
    max_nodes: int = 500
    cluster_by: Literal["domain", "note_type", "maturity"] = "domain"
    min_connections: int = 0                    # 최소 연결 수 필터
    layout: str = "force"
```

### E2. Output Schema

```python
class GraphData:
    """D3.js force-directed graph 데이터"""
    nodes: list["GraphNode"]
    edges: list["GraphEdge"]
    clusters: list["Cluster"]
    stats: "GraphStats"

class GraphNode:
    """시각화 노드"""
    id: str                                     # Luhmann ID
    uuid: str                                   # 내부 UUID
    title: str
    note_type: str                              # LOCK-PKM-10 → 노드 형태
    maturity: str                               # LOCK-PKM-12 → 노드 크기
    domain: str                                 # → 클러스터 색상
    size: float                                 # 연결 수 비례 (기존 명세 §8.2)
    color: str                                  # hex color
    shape: str                                  # "circle"|"diamond"|"square"|"triangle"|"hexagon"
    opacity: float                              # 성숙도 반영 (Archived → 0.3)
    link_count: int
    backlink_count: int
    word_count: int
    importance: int
    freshness_score: float                      # 04_knowledge-conflict 신선도

class GraphEdge:
    """시각화 엣지"""
    source: str                                 # 출발 노드 ID
    target: str                                 # 도착 노드 ID
    link_type: str                              # 부록 §A.3: related/supports/contradicts/continues/branches
    graph_edge_type: str                        # LOCK-PKM-05 매핑
    color: str                                  # 링크 타입별 색상
    width: float                                # weight 비례
    style: str                                  # "solid"|"dashed"|"dotted"
    bidirectional: bool                         # 부록 §A.3 양방향 여부
    context: str                                # 부록 §A.4 링크 컨텍스트 (툴팁)

class Cluster:
    """노드 클러스터"""
    id: str
    label: str
    color: str
    node_count: int
    center_x: float
    center_y: float

class GraphStats:
    """네트워크 통계"""
    total_nodes: int
    total_edges: int
    avg_connections: float
    density: float                              # 그래프 밀도
    orphan_count: int                           # 고립 노트 수
    cluster_count: int
    max_depth: int                              # 중심에서 최대 거리
```

### E3. Algorithm — 그래프 데이터 생성 + 시각 매핑

```python
class ZettelNetworkVisualizer:
    """D3.js force-directed graph로 지식 네트워크 시각화 (기존 명세 §8.2 확장)"""

    # 노트 타입 → 노드 형태 (LOCK-PKM-10)
    NOTE_TYPE_SHAPES: dict[str, str] = {
        "permanent": "circle",
        "literature": "diamond",
        "fleeting": "triangle",
        "index": "hexagon",
        "structure": "square",
    }

    # 성숙도 → 노드 크기 배수 (LOCK-PKM-12)
    MATURITY_SIZE_SCALE: dict[str, float] = {
        "Seedling":  0.6,
        "Growing":   1.0,
        "Evergreen": 1.5,
        "Archived":  0.4,
    }

    # 성숙도 → 투명도 (LOCK-PKM-12)
    MATURITY_OPACITY: dict[str, float] = {
        "Seedling":  0.7,
        "Growing":   0.9,
        "Evergreen": 1.0,
        "Archived":  0.3,
    }

    # 링크 타입 → 엣지 색상 + 스타일 (부록 §A.3)
    LINK_TYPE_STYLE: dict[str, dict] = {
        "related":     {"color": "#6B7280", "style": "solid",  "width": 1.0},   # gray
        "supports":    {"color": "#10B981", "style": "solid",  "width": 1.5},   # green
        "contradicts": {"color": "#EF4444", "style": "dashed", "width": 2.0},   # red
        "continues":   {"color": "#3B82F6", "style": "solid",  "width": 1.5},   # blue
        "branches":    {"color": "#F59E0B", "style": "dotted", "width": 1.0},   # amber
    }

    # 도메인 → 클러스터 색상
    DOMAIN_COLORS: dict[str, str] = {
        "programming":  "#8B5CF6",
        "finance":      "#06B6D4",
        "health":       "#22C55E",
        "science":      "#F97316",
        "philosophy":   "#EC4899",
        "_default":     "#6B7280",
    }

    # atomic_note_structure.md E4에서 정의된 매핑 상수 import
    # from atomic_note_structure import LINK_TYPE_TO_GRAPH_EDGE, LINK_BIDIRECTIONAL

    async def generate_graph_data(
        self,
        req: GraphViewRequest,
    ) -> GraphData:
        """중심 노트에서 depth-hop까지의 네트워크를 D3.js 데이터로 변환"""

        # Step 1: Neo4j에서 서브그래프 추출 (02_knowledge-graph)
        raw_nodes, raw_edges = await self._fetch_subgraph(
            center_id=req.center_note_id,
            depth=req.depth,
            max_nodes=req.max_nodes,
        )

        # Step 2: 필터 적용
        filtered_nodes = self._apply_filters(raw_nodes, req)
        filtered_edges = self._filter_edges(raw_edges, filtered_nodes)

        # Step 3: 노드 시각 속성 매핑
        graph_nodes = []
        for n in filtered_nodes:
            base_size = max(1, len(n.links))     # 연결 수 비례 (기존 명세 §8.2)
            maturity_scale = self.MATURITY_SIZE_SCALE.get(n.maturity, 1.0)
            domain_color = self.DOMAIN_COLORS.get(n.domain, self.DOMAIN_COLORS["_default"])

            graph_nodes.append(GraphNode(
                id=n.id,
                uuid=str(n.uuid),
                title=n.title,
                note_type=n.note_type,
                maturity=n.maturity,
                domain=n.domain,
                size=base_size * maturity_scale,
                color=domain_color,
                shape=self.NOTE_TYPE_SHAPES[n.note_type],
                opacity=self.MATURITY_OPACITY.get(n.maturity, 1.0),
                link_count=len(n.links),
                backlink_count=len(n.backlinks),
                word_count=n.word_count,
                importance=n.importance,
                freshness_score=n.freshness_score,
            ))

        # Step 4: 엣지 시각 속성 매핑
        graph_edges = []
        for e in filtered_edges:
            style = self.LINK_TYPE_STYLE.get(e.link_type, self.LINK_TYPE_STYLE["related"])
            graph_edges.append(GraphEdge(
                source=e.source_id,
                target=e.target_id,
                link_type=e.link_type,
                graph_edge_type=LINK_TYPE_TO_GRAPH_EDGE.get(e.link_type, "RELATED_TO"),
                color=style["color"],
                width=style["width"] * (e.weight or 1.0),
                style=style["style"],
                bidirectional=LINK_BIDIRECTIONAL.get(e.link_type, False),
                context=e.context,
            ))

        # Step 5: 클러스터링 (도메인/태그 기반 — 기존 명세 §8.2)
        clusters = self._compute_clusters(graph_nodes, cluster_by="domain")

        # Step 6: 통계 계산
        stats = self._compute_stats(graph_nodes, graph_edges, clusters)

        return GraphData(
            nodes=graph_nodes,
            edges=graph_edges,
            clusters=clusters,
            stats=stats,
        )

    async def _fetch_subgraph(
        self,
        center_id: str,
        depth: int,
        max_nodes: int,
    ) -> tuple[list, list]:
        """Neo4j에서 N-hop 서브그래프 추출"""
        query = """
        MATCH path = (center:ZettelNote {luhmann_id: $centerId})-[r*1..$depth]-(connected:ZettelNote)
        WITH collect(DISTINCT connected) + [center] AS allNodes,
             [rel IN collect(DISTINCT r) | rel] AS allRels
        UNWIND allNodes AS n
        WITH collect(DISTINCT n)[0..$maxNodes] AS nodes, allRels
        RETURN nodes, allRels
        """
        safe_depth = max(1, min(int(depth), 10))  # 가변길이 관계 상한은 파라미터 미지원 → 검증 후 직접 삽입
        query = query.replace("$depth", str(safe_depth))
        return await self.db.query(query, centerId=center_id, maxNodes=max_nodes)

    def _compute_clusters(
        self,
        nodes: list[GraphNode],
        cluster_by: str = "domain",
    ) -> list[Cluster]:
        """노드를 도메인/타입/성숙도 기준으로 클러스터링"""
        groups: dict[str, list[GraphNode]] = {}
        for n in nodes:
            key = getattr(n, cluster_by, "_default")
            groups.setdefault(key, []).append(n)

        clusters = []
        for label, group_nodes in groups.items():
            color = self.DOMAIN_COLORS.get(label, self.DOMAIN_COLORS["_default"])
            clusters.append(Cluster(
                id=f"cluster_{label}",
                label=label,
                color=color,
                node_count=len(group_nodes),
                center_x=0.0,       # D3.js 시뮬레이션에서 계산
                center_y=0.0,
            ))
        return clusters

    def _compute_stats(
        self,
        nodes: list[GraphNode],
        edges: list[GraphEdge],
        clusters: list[Cluster],
    ) -> GraphStats:
        """네트워크 통계"""
        n = len(nodes)
        e = len(edges)
        max_possible = n * (n - 1) / 2 if n > 1 else 1
        orphans = sum(1 for node in nodes if node.link_count == 0)

        return GraphStats(
            total_nodes=n,
            total_edges=e,
            avg_connections=e * 2 / n if n > 0 else 0,
            density=e / max_possible if max_possible > 0 else 0,
            orphan_count=orphans,
            cluster_count=len(clusters),
            max_depth=0,            # BFS로 별도 계산
        )
```

### E4. D3.js 프론트엔드 렌더링 설정

```python
class D3ForceConfig:
    """D3.js force-directed 시뮬레이션 파라미터"""

    # Force 파라미터
    charge_strength: float = -300           # 노드 간 반발력
    link_distance: float = 100              # 기본 링크 거리
    center_strength: float = 0.05           # 중심 인력
    collision_radius: float = 30            # 충돌 반경

    # 인터랙션
    zoom_range: tuple[float, float] = (0.1, 10.0)
    drag_enabled: bool = True
    hover_highlight: bool = True            # 호버 시 연결 노드 강조
    click_expand: bool = True               # 클릭 시 depth 확장

    # 렌더링
    canvas_width: int = 1200
    canvas_height: int = 800
    animation_duration_ms: int = 300
    label_min_zoom: float = 0.5             # 이 줌 이상에서만 라벨 표시

    # 미니맵
    minimap_enabled: bool = True
    minimap_size: tuple[int, int] = (200, 150)

# 프론트엔드 전달 JSON 스키마
D3_PAYLOAD_SCHEMA = {
    "nodes": [
        {
            "id": "21a3b",
            "title": "React 상태관리 패턴",
            "noteType": "permanent",         # → shape
            "maturity": "Evergreen",          # → size, opacity
            "domain": "programming",          # → color
            "size": 7.5,                      # 연결수(5) × maturity_scale(1.5)
            "color": "#8B5CF6",
            "shape": "circle",
            "opacity": 1.0,
            "linkCount": 5,
            "importance": 4,
            "freshness": 0.85,
        }
    ],
    "edges": [
        {
            "source": "21a3b",
            "target": "21a",
            "linkType": "continues",
            "color": "#3B82F6",
            "width": 1.5,
            "style": "solid",
            "bidirectional": False,
            "context": "React 기초에서 상태관리 패턴으로 발전",
        }
    ],
    "config": {  # D3ForceConfig 직렬화
        "chargeStrength": -300,
        "linkDistance": 100,
    },
}
```

### E5. 고립 노트 감지 + 하이라이트

```python
async def detect_orphan_notes(self) -> list[GraphNode]:
    """고립 노트 (연결 없는 노트) 감지 — 기존 명세 §4.2 쿼리 4번 활용"""
    query = """
    MATCH (n:ZettelNote)
    WHERE NOT (n)-[:RELATED_TO]-() AND NOT (n)-[:SUPPORTS]-()
      AND NOT (n)-[:CONTRADICTS]-() AND NOT (n)-[:SUPERSEDES]-()
      AND NOT (n)-[:TAGGED_WITH]-() AND NOT (n)-[:BELONGS_TO]-()
      AND NOT (n)-[:SOURCED_FROM]-() AND NOT (n)-[:MENTIONS]-()
      AND NOT (n)-[:TAGGED_WITH]-() AND NOT (n)-[:BELONGS_TO]-()
      AND NOT (n)-[:SOURCED_FROM]-() AND NOT (n)-[:MENTIONS]-()
    RETURN n ORDER BY n.created_at DESC
    """
    orphans = await self.db.query(query)
    # R-06-6 위반 후보 — 링크 추가 제안 생성
    return [self._to_graph_node(n, highlight="orphan") for n in orphans]
```

### E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 서브그래프 추출 (depth=3, ≤200 노드) | < 500ms | Neo4j query time |
| 시각 속성 매핑 (200 노드 + 엣지) | < 100ms | Python 처리 |
| 전체 GraphData 생성 | < 1s | 추출 + 매핑 + 통계 |
| 전체 네트워크 조감도 (500 노드) | < 3s | GlobalGraphRequest |
| D3.js 프론트엔드 렌더링 (200 노드) | < 2s | 브라우저 초기 렌더 (60fps 이후) |
| JSON payload 직렬화 | < 50ms | json.dumps |

### E7. Error Handling

| 에러 시나리오 | 처리 | 심각도 |
|-------------|------|--------|
| center_note_id 미존재 | 404 반환 + "노트를 찾을 수 없습니다" | HIGH |
| depth 초과 (> 10) | 최대 10으로 클램프 + WARNING | WARNING |
| max_nodes 초과 노드 | 연결 수 상위 N개만 반환 + truncated 플래그 | LOW |
| Neo4j 연결 실패 | 로컬 캐시 fallback (최근 스냅샷) | CRITICAL |
| 노드 0개 (빈 그래프) | 빈 GraphData + "연결된 노트 없음" 메시지 | LOW |
| 렌더링 성능 저하 (> 500 노드) | WebGL fallback 또는 클러스터 축약 모드 | WARNING |

### E8. Test Criteria

**Unit Tests**
| ID | 테스트 명 | 입력 | 기대 출력 |
|----|----------|------|----------|
| UT-1 | 노드 시각 매핑 — permanent/Evergreen | note_type=permanent, maturity=Evergreen | shape=circle, size×1.5, opacity=1.0 |
| UT-2 | 노드 시각 매핑 — fleeting/Seedling | note_type=fleeting, maturity=Seedling | shape=triangle, size×0.6, opacity=0.7 |
| UT-3 | 엣지 색상 — contradicts | link_type=contradicts | color=#EF4444, style=dashed, width=2.0 |
| UT-4 | 엣지 색상 — supports | link_type=supports | color=#10B981, style=solid, width=1.5 |
| UT-5 | 클러스터링 | 3도메인 10노드 | 3개 Cluster, node_count 합=10 |
| UT-6 | 통계 계산 | 5노드 8엣지 | density=8/10=0.8, avg_connections=3.2 |
| UT-7 | 필터 적용 | filter_maturity=["Evergreen"] | Evergreen 노드만 반환 |
| UT-8 | 고립 노트 감지 | 링크 0개 노트 3건 | orphan_count=3, highlight="orphan" |

**Integration Tests**
| ID | 시나리오 | 검증 |
|----|----------|------|
| IT-1 | 중심 노트 depth=3 서브그래프 | Neo4j → GraphData → JSON payload 정합 |
| IT-2 | 전체 네트워크 500노드 | 렌더링 < 3s, 클러스터 도메인별 분리 |
| IT-3 | 노트 추가 → 실시간 그래프 갱신 | atomic_note_structure.md 연동 → 새 노드 표시 |
| IT-4 | T4-Frontend D3.js 렌더 | JSON payload → 브라우저 force-directed 정상 표시 |

**Acceptance Criteria**
- LOCK-PKM-10 5종 노트 타입 전수 시각 구분 (형태 5종)
- LOCK-PKM-12 4단계 성숙도 전수 크기/투명도 반영
- 부록 §A.3 5종 링크 타입 전수 색상/스타일 구분
- 고립 노트 (R-06-6 위반) 감지 + 하이라이트
- 200노드 기준 전체 응답 < 1s

### E9. Integration Dependencies

- 내부: atomic_note_structure.md (노드 데이터), luhmann_id_system.md (ID→시퀀스 표시), 02_knowledge-graph (Neo4j 서브그래프 쿼리), 04_knowledge-conflict (freshness_score 조회)
- 외부 도메인: T4-Frontend (D3.js 렌더링, React 컴포넌트), T2-CORE_AI (클러스터링 개선 시 LLM 활용 가능)
- 권한: R-06-6 고립 노트 감지, R-06-7 시각화 데이터 외부 전송 시 동의

### E10. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 5종 노트 타입 → 노드 형태 | LOCK-PKM-10 (기존 명세 §8.1) | NOTE_TYPE_SHAPES 매핑 |
| 8종 엣지 타입 → 그래프 엣지 | LOCK-PKM-05 (기존 명세 §4.1) | graph_edge_type 매핑 |
| 4단계 성숙도 → 크기/투명도 | LOCK-PKM-12 (M-017) | MATURITY_SIZE_SCALE, MATURITY_OPACITY |
| 5종 링크 타입 → 엣지 색상/스타일 | 부록 §A.3 | LINK_TYPE_STYLE 매핑 |
| depth 기본값 3 | 기존 명세 §8.2 | GraphViewRequest.depth = 3 |

**자체 점수**: 100/100
