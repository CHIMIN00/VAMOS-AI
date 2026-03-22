"""
SOT Knowledge Graph Builder for VAMOS
SOT 파일 간 관계를 Neo4j 그래프로 구축
"""

import json
import os
import re
import sys
import argparse
import glob
from datetime import datetime

def get_neo4j_driver(uri="bolt://localhost:7687", user="neo4j", password="password"):
    from neo4j import GraphDatabase
    return GraphDatabase.driver(uri, auth=(user, password))

def extract_references(content, filename):
    """문서 내 다른 문서 참조 추출"""
    refs = set()
    # D2.0-XX 패턴
    for match in re.finditer(r'D\d+\.\d+-\d+', content):
        ref = match.group()
        if ref not in filename:
            refs.add(ref)
    # 모듈 참조 (I-1, E-2 등)
    for match in re.finditer(r'[A-Z]-\d+', content):
        refs.add(match.group())
    # 섹션 참조 (§, 참조, 참고)
    for match in re.finditer(r'(?:참조|참고|§)\s*[:\s]*([^\s,]+)', content):
        refs.add(match.group(1))
    return refs

def build_graph(sot_dir, neo4j_uri="bolt://localhost:7687"):
    """SOT 파일에서 그래프 구축"""
    driver = get_neo4j_driver(neo4j_uri)

    with driver.session() as session:
        # 기존 그래프 초기화
        session.run("MATCH (n) DETACH DELETE n")

        # SOT 파일 수집
        sot_files = []
        for ext in ["*.md", "*.txt"]:
            sot_files.extend(glob.glob(os.path.join(sot_dir, "**", ext), recursive=True))

        print(f"SOT 파일 {len(sot_files)}개 처리 중...")

        # 노드 생성
        for filepath in sot_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                continue

            filename = os.path.basename(filepath)
            line_count = content.count("\n") + 1

            # 문서 노드
            session.run(
                "CREATE (d:Document {name: $name, path: $path, lines: $lines})",
                name=filename, path=filepath, lines=line_count
            )

            # 참조 관계 추출
            refs = extract_references(content, filename)
            for ref in refs:
                session.run(
                    """
                    MERGE (target:Entity {name: $ref})
                    WITH target
                    MATCH (source:Document {name: $source})
                    CREATE (source)-[:REFERENCES {type: 'reference'}]->(target)
                    """,
                    ref=ref, source=filename
                )

            print(f"  {filename}: {len(refs)} 참조")

        # 통계
        node_count = session.run("MATCH (n) RETURN count(n) as cnt").single()["cnt"]
        edge_count = session.run("MATCH ()-[r]->() RETURN count(r) as cnt").single()["cnt"]

    driver.close()
    print(f"\n그래프 구축 완료: 노드={node_count}, 엣지={edge_count}")
    return {"nodes": node_count, "edges": edge_count}

def impact_analysis(doc_id, neo4j_uri="bolt://localhost:7687"):
    """문서 영향 분석"""
    driver = get_neo4j_driver(neo4j_uri)

    with driver.session() as session:
        # 직접 영향
        direct = session.run(
            """
            MATCH (d:Document)-[:REFERENCES]->(e:Entity {name: $doc_id})
            RETURN d.name as name
            """,
            doc_id=doc_id
        ).data()

        # 간접 영향 (2홉)
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
        "indirect_impact": [r["name"] for r in indirect]
    }

def main():
    parser = argparse.ArgumentParser(description="SOT graph builder")
    parser.add_argument("--action", choices=["build", "impact", "deps"], required=True)
    parser.add_argument("--sot-dir", help="SOT 디렉토리")
    parser.add_argument("--target", help="분석 대상 ID")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687")
    parser.add_argument("--output", help="출력 JSON")
    args = parser.parse_args()

    if args.action == "build":
        result = build_graph(args.sot_dir, args.neo4j_uri)
    elif args.action == "impact":
        result = impact_analysis(args.target, args.neo4j_uri)
    elif args.action == "deps":
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from sot_graph_query import deps_analysis
        result = deps_analysis(args.target, args.neo4j_uri)

    result["timestamp"] = datetime.now().isoformat()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
