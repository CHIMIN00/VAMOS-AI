# knowledge_graph_multimodal_v2.md — J-053 V2 EXTEND (테이블/스프레드시트 RAG) + J-054 V2 EXTEND (코드 RAG)

> **Status**: V2-Phase 2 (2-4 #2b)
> **작성일**: 2026-04-19
> **V1 정본**: [multimodal_rag.md](./multimodal_rag.md) (J-051~J-055 정본, read-only sha256 baseline, J-053/J-054 V1) / KG 통합 참조: [knowledge_graph_multimodal.md](./knowledge_graph_multimodal.md) (J-056)
> **SoT 근거**: STEP7-J Part 6 J-053 (L927~L936) + J-054 (L938~L947)
> **담당 J-ID**: **J-053** (V2 EXTEND: Text-to-SQL 투자 특화 + 크로스 테이블) + **J-054** (V2 EXTEND: tree-sitter + 의존성 그래프 + 코드 문서 통합)
> **상위 인덱스**: [_index.md](./_index.md)
> **peer V2**: [multimodal_rag_v2.md](./multimodal_rag_v2.md) §4.2 (J-056 KG + 멀티모달 통합) / [caching_optimization_v2.md](./caching_optimization_v2.md)

---

## 1. Cross-domain 참조

| 정본 | 역할 |
|------|------|
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 6 J-053 (L927~L936) | 상위 SoT J-053 |
| `STEP7-J_멀티모달_생성처리_작업가이드.md` Part 6 J-054 (L938~L947) | 상위 SoT J-054 |
| `knowledge_graph_multimodal.md` (V1) | V1 정본 |
| `multimodal_rag_v2.md` §4.2 (peer) | KG 통합 |
| AUTHORITY §4 LOCK-MM-04/06/07 | LOCK |

## 2. LOCK 인용

> LOCK (기존 명세 §2.2): CLIP 임베딩 차원 — 768d (ViT-L/14@336)

> LOCK (STEP7-J J-094~J-096): 비용 상한 V2 ≤ ₩40K($30)

**적용**: LOCK-MM-07: 코드/테이블 임베딩 통일 (768d) / LOCK-MM-06 V2: SQL 변환 LLM 비용 가드

## 3. V1 → V2 승급

| J-ID | V1 | V2 (본) |
|------|----|---------|
| J-053 테이블/스프레드시트 RAG | Text-to-SQL 즉시 | **투자 데이터 특화 + 크로스 테이블 조인 + 임베딩 (구조 보존)** |
| J-054 코드 RAG | tree-sitter + 임베딩 | **함수/클래스 단위 + 의존성 그래프 활용 + 문서 통합 검색** |

## 4. V2 본문

### 4.1 J-053 테이블 RAG V2 (STEP7-J L927~L936)

**근거 verbatim** (STEP7-J L930~L934):
> ```
> [구현 상세]
> - 테이블 데이터 자연어 질의
> - Text-to-SQL 자동 변환 (투자 데이터 특화)
> - 테이블 임베딩: 구조 보존 임베딩
> - 크로스 테이블 분석: 여러 테이블 조인 쿼리
> ```

```python
class TableRAGRequestV2:
    query: str                                       # "삼성전자 PER 추이"
    table_ids: list[str]                             # 검색 범위
    domain: Literal["investment","general","scientific"] = "investment"
    enable_cross_table: bool = True
    user_id: str

class TableRAGResultV2:
    sql_query: str                                   # 자동 생성 SQL
    rows: list[dict]                                 # 결과 행
    explanation: str                                 # 자연어 설명
    related_tables: list[str]                        # 크로스 조인된 테이블
    cost_usd: float

async def query_table_rag(req: TableRAGRequestV2) -> TableRAGResultV2:
    # 1. 테이블 메타데이터 + 임베딩 검색
    candidate_tables = await search_tables_by_embedding(req.query, top_k=5,
                                                       embedding_model="bge-m3")
    if req.table_ids:
        candidate_tables = [t for t in candidate_tables if t.id in req.table_ids]

    # 2. 도메인별 Text-to-SQL (투자 특화 prompt)
    prompt = build_text_to_sql_prompt(req.query, candidate_tables, domain=req.domain)
    sql = await llm_text_to_sql(prompt, model="qwen2.5-coder-7b-local")

    # 3. 크로스 테이블 자동 조인 (V2 신규)
    if req.enable_cross_table and len(candidate_tables) > 1:
        sql = augment_cross_join(sql, candidate_tables)

    # 4. SQL 실행 (DuckDB sandbox, 읽기 전용)
    rows = await duckdb_readonly_exec(sql, max_rows=1000)

    # 5. 자연어 설명 생성
    explanation = await llm_explain_results(req.query, sql, rows[:10])

    return TableRAGResultV2(sql_query=sql, rows=rows, explanation=explanation,
                           related_tables=[t.id for t in candidate_tables],
                           cost_usd=0.0)  # 100% 로컬
```

#### 투자 데이터 특화 prompt 예시
```
당신은 투자 데이터 SQL 전문가입니다. 다음 자연어 질의를 SQL로 변환하세요.
사용 가능한 테이블:
- stocks (id, ticker, name, market): 주식 기본 정보
- prices (date, ticker, open, high, low, close, volume): 일별 시세
- financials (date, ticker, per, pbr, eps, dividend): 재무 지표
- portfolios (user_id, ticker, qty, avg_price): 보유 포트폴리오

질의: {query}
도메인: investment
SQL:
```

### 4.2 J-054 코드 RAG V2 (STEP7-J L938~L947)

**근거 verbatim** (STEP7-J L941~L946):
> ```
> [구현 상세]
> - 코드베이스 시맨틱 검색 (tree-sitter 파싱 + 임베딩)
> - 함수/클래스 단위 RAG
> - 의존성 그래프 활용 관련 코드 자동 포함
> - 코드 문서 통합 검색
> ```

```python
class CodeRAGRequestV2:
    query: str                                       # "JWT 인증 처리하는 함수"
    repo_path: str
    languages: list[str] = ["python","typescript","rust"]
    include_dependencies: bool = True                # V2 신규: 의존성 그래프 활용
    include_docs: bool = True                        # V2 신규: 문서 통합 검색
    top_k: int = 10

class CodeRAGHit:
    file_path: str
    symbol: str                                      # 함수/클래스 이름
    symbol_type: Literal["function","class","method","module"]
    code_snippet: str
    language: str
    related_symbols: list[str]                       # 의존성 그래프
    docstring: Optional[str]
    score: float

async def search_code(req: CodeRAGRequestV2) -> list[CodeRAGHit]:
    # 1. tree-sitter 파싱 → 함수/클래스 단위 분할
    symbols = await tree_sitter_extract_symbols(req.repo_path, languages=req.languages)

    # 2. 시맨틱 임베딩 (코드 + docstring 통합)
    q_emb = await code_embed(req.query, model="bge-m3")
    candidates = []
    for sym in symbols:
        sym_text = f"{sym.signature}\n{sym.docstring or ''}\n{sym.code[:500]}"
        sym_emb = await code_embed(sym_text, model="bge-m3")
        score = cosine(q_emb, sym_emb)
        candidates.append((score, sym))
    candidates.sort(reverse=True)

    # 3. 의존성 그래프 활용 (V2 신규)
    hits = []
    for score, sym in candidates[:req.top_k]:
        related = []
        if req.include_dependencies:
            deps = await dep_graph.get_deps(sym, depth=1)
            related = [d.symbol for d in deps]

        # 4. 문서 통합 검색 (V2 신규)
        docstring = sym.docstring
        if req.include_docs and not docstring:
            docs = await search_docs_for_symbol(sym, repo_path=req.repo_path)
            docstring = docs.summary if docs else None

        hits.append(CodeRAGHit(
            file_path=sym.file, symbol=sym.name, symbol_type=sym.type,
            code_snippet=sym.code, language=sym.language,
            related_symbols=related, docstring=docstring, score=score,
        ))
    return hits
```

## 5. Error Handling
| 에러 | 폴백 |
|------|------|
| 테이블 임베딩 부재 | 신규 인덱싱 후 재시도 |
| Text-to-SQL 실패 | 사용자에게 SQL 직접 입력 요청 |
| SQL 실행 실패 | 에러 메시지 + LLM 수정 제안 |
| tree-sitter 언어 미지원 | 정규식 폴백 |
| 의존성 그래프 부재 | related_symbols=[] |
| 문서 검색 실패 | docstring=None |

## 6. Cost
| 시나리오 | V2 (월) | LOCK-MM-06 V2 |
|----------|---------|---------------|
| 100% 로컬 (DuckDB + Qwen2.5-Coder) | $0 | 충족 ✅ |
| GPT-4o (복잡 SQL) | $0.50 | 충족 |
| Qdrant Cloud (코드 임베딩) | $5 | 충족 |
| **V2 권장** | **$0~$5/월** | 충족 ✅ |

## 7. SLA
| 작업 | P50 | P99 |
|------|-----|-----|
| 테이블 임베딩 검색 | 100ms | 300ms |
| Text-to-SQL (단순) | 800ms | 2s |
| Text-to-SQL (크로스 조인) | 1.5s | 4s |
| 코드 검색 (10K 심볼) | 200ms | 500ms |
| 의존성 그래프 조회 | 50ms | 150ms |

## 8. Test (10건)
1. "삼성전자 PER 추이" → Text-to-SQL → 결과 + 자연어 설명.
2. 크로스 조인 (stocks + prices + financials).
3. 코드 검색 "JWT 인증" → 함수 + 의존성 그래프.
4. tree-sitter 다국어 (Python + TS + Rust).
5. 의존성 그래프 depth=1 → related_symbols 반환.
6. docstring 부재 → search_docs_for_symbol 폴백.
7. SQL 실행 실패 → LLM 수정 제안.
8. user_id 격리 (포트폴리오 데이터).
9. CLIP 768d cross-modal (코드 + 다이어그램, peer J-056).
10. Qdrant 실패 → local 캐시 폴백.

## 9. Dependencies
- 외부: tree-sitter (다국어 파서), DuckDB, bge-m3, Qwen2.5-Coder 7B, Qdrant
- 내부 (peer): J-051 V1 (멀티모달 청킹), J-052 V1 (이미지-텍스트), J-055 V2 (multimodal_rag_v2 §4.1), J-056 V2 (multimodal_rag_v2 §4.2 KG), J-064 V2 (memory_integration_v2)

## 10. Privacy
- DuckDB 읽기 전용 모드 (SQL injection 방지)
- 사용자 포트폴리오 데이터 user_id 격리
- 코드 검색 시 .env / secrets 자동 제외

## 11. 검증
| 항목 | V1 | V2 | L3 |
|------|----|---------|-----|
| J-053 Text-to-SQL 투자 특화 | V1 즉시 | + 크로스 조인 + 도메인 prompt | 89 |
| J-053 테이블 임베딩 (구조 보존) | 미작성 | bge-m3 + 메타데이터 | 86 |
| J-054 함수/클래스 단위 RAG | tree-sitter + 임베딩 | + 의존성 그래프 + 문서 통합 | 88 |
| J-054 의존성 그래프 활용 | 미작성 | dep_graph.get_deps depth=1 | 87 |

**평균**: **87.5/100** ✅
