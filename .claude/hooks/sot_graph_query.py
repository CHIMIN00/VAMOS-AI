"""
SOT Knowledge Graph Query for VAMOS
Neo4j 그래프 쿼리 (영향 분석, 의존성 트리)
"""

import json
import sys
import argparse
from datetime import datetime

def get_neo4j_driver(uri="bolt://localhost:7687", user="neo4j", password="password"):
    from neo4j import GraphDatabase
    return GraphDatabase.driver(uri, auth=(user, password))

def impact_analysis(doc_id, neo4j_uri="bolt://localhost:7687"):
    """문서 영향 분석: 이 문서를 수정하면 어떤 문서가 영향받는지"""
    driver = get_neo4j_driver(neo4j_uri)

    with driver.session() as session:
        # 직접 영향: 이 문서를 참조하는 문서들
        direct = session.run(
            """
            MATCH (d:Document)-[:REFERENCES]->(e:Entity {name: $doc_id})
            RETURN d.name as name
            """,
            doc_id=doc_id
        ).data()

        # 간접 영향 (2홉): 직접 영향 문서를 참조하는 문서들
        indirect = session.run(
            """
            MATCH (d:Document)-[:REFERENCES*2]->(e:Entity {name: $doc_id})
            WHERE NOT (d)-[:REFERENCES]->(e)
            RETURN DISTINCT d.name as name
            """,
            doc_id=doc_id
        ).data()

    driver.close()
    return {
        "target": doc_id,
        "direct_impact": [r["name"] for r in direct],
        "indirect_impact": [r["name"] for r in indirect],
        "total_affected": len(direct) + len(indirect)
    }

def deps_analysis(module_id, neo4j_uri="bolt://localhost:7687"):
    """의존성 트리: 이 모듈이 의존하는 모든 모듈"""
    driver = get_neo4j_driver(neo4j_uri)

    with driver.session() as session:
        # 직접 의존: 이 모듈이 참조하는 엔티티들
        direct_deps = session.run(
            """
            MATCH (d:Document)-[:REFERENCES]->(e:Entity)
            WHERE d.name CONTAINS $module_id
            RETURN DISTINCT e.name as name
            """,
            module_id=module_id
        ).data()

        # 역방향 의존: 이 모듈을 참조하는 문서들
        dependents = session.run(
            """
            MATCH (d:Document)-[:REFERENCES]->(e:Entity {name: $module_id})
            RETURN DISTINCT d.name as name
            """,
            module_id=module_id
        ).data()

        # 전체 의존성 트리 (가변 깊이)
        dep_tree = session.run(
            """
            MATCH path = (d:Document)-[:REFERENCES*1..3]->(e:Entity)
            WHERE d.name CONTAINS $module_id
            RETURN [n IN nodes(path) | n.name] as chain
            LIMIT 50
            """,
            module_id=module_id
        ).data()

    driver.close()
    return {
        "module": module_id,
        "direct_dependencies": [r["name"] for r in direct_deps],
        "dependents": [r["name"] for r in dependents],
        "dependency_chains": [r["chain"] for r in dep_tree],
        "total_deps": len(direct_deps),
        "total_dependents": len(dependents)
    }

def main():
    parser = argparse.ArgumentParser(description="SOT graph query")
    parser.add_argument("--action", choices=["impact", "deps"], required=True)
    parser.add_argument("--target", required=True, help="문서 ID 또는 모듈 ID")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687")
    parser.add_argument("--output", help="출력 JSON")
    args = parser.parse_args()

    if args.action == "impact":
        result = impact_analysis(args.target, args.neo4j_uri)
        print(f"영향 분석: {args.target}")
        print(f"  직접 영향: {len(result['direct_impact'])}개 — {result['direct_impact']}")
        print(f"  간접 영향: {len(result['indirect_impact'])}개 — {result['indirect_impact']}")
    else:
        result = deps_analysis(args.target, args.neo4j_uri)
        print(f"의존성 분석: {args.target}")
        print(f"  의존 대상: {result['total_deps']}개 — {result['direct_dependencies']}")
        print(f"  의존하는 문서: {result['total_dependents']}개 — {result['dependents']}")

    result["timestamp"] = datetime.now().isoformat()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
