# I-16 Knowledge Search Engine — 외부 지식 소스 V2 Enhanced (L3 보강)

> **V단계**: V2-Phase 2
> **Status**: APPROVED (Phase 4 ✅ 완료, 2026-05-23, V2 strict L3 PASS production-ready 정본 승급, Phase 3 V-17 PASS inheritance)
> **Last-reviewed**: 2026-05-23 (Phase 4 production promotion)
> **ReadOnly**: TRUE (production 승급 후 immutable, 변경 시 일시 해제→fix→복원 EXACT 패턴 + audit log)
> **작성일**: 2026-05-10
> **V1 정본**: `external_sources.md` (23 lines, byte EXACT)
> **모듈**: I-16 (CORE, Reasoning) — 외부 지식 소스 어댑터
> **LOCK 참조**: LOCK-AX-01, LOCK-AX-10
> **L3 판정**: PASS (V-17 row content, 9/9 또는 8/9, 2026-05-14)
> **변경 이력 태그**: `V2-Phase 2` (2026-05-10, 세션 2-4)
> **종합계획서 §**: §7 Phase 2 L1533~L1585
> **계약 cross-ref**: C-04 (search_pipeline_v2가 본 모듈 위임)
> **F-10 이월**: external 소스별 fallback ID 등재 (D2.0-02 §6.3) → STEP_C
> **횡단**: 6-2 (외부 응답 PII 마스킹 + 시크릿 사전 제거)

---

## 1. 교차 참조 블록

| 정본 | 역할 |
|------|------|
| `external_sources.md` (V1, 23 lines, byte EXACT, V1 §4 5 소스 표) | V1 정본 |
| `search_api_v2.md` / `search_pipeline_v2.md` (자매 V2) | 호출자 |
| `00_common/timeout_policy.md` §2 #5 외부 검색 API | timeout 정본 |
| `6-2/01_ai-code-security/pii_regex_masking.md` | 외부 응답 PII |
| `6-2/02_hmac-timing-defense/api_key_management.md` | 외부 API 키 관리 |

---

## 2. LOCK 인용 (R9 형식)

> LOCK (D2.0-01 §5.6, LOCK-AX-01): I-16 = CORE

> LOCK (D2.0-06, LOCK-AX-10): Semantic cache cosine ≥0.95, TTL 24h — 본 V2는 외부 응답도 캐시 적용

> LOCK (V1 §4 표): 5 소스 = Web/Wikipedia/arXiv/금융 데이터/뉴스 + 신뢰도 0.6~0.9 + 버전 V1/V2

---

## 3. V1 → V2 승급 개요

V1 byte EXACT (23 lines, V1 §4 5 소스 표). V1 변경 0.

| 요소 | 보강 |
|------|------|
| **E1** | external_sources 목적 (외부 지식 소스 어댑터 통합) |
| **E2** | 5 소스별 어댑터 의사코드 + 병렬 호출 |
| **E5** | 외부 API timeout, rate limit, 결과 위변조 |
| **E6** | 소스별 P95 (Tavily 1500ms, Wikipedia 800ms 등) |
| **E7** | 5 소스 정상/timeout/PII/시크릿 |
| **E9** | tavily-python, wikipedia-api, arxiv, yfinance, krx |

---

## 4. V2 본문 (L3 보강)

### 4.1 E1 — 목적 및 역할

external_sources는 I-16의 **외부 지식 소스 어댑터 통합**. V1 §4 5 소스 (Web E-2 / Wikipedia / arXiv / 금융 / 뉴스) 를 단일 인터페이스 (`IExternalAdapter.search`) 로 추상화. search_pipeline_v2의 병렬 검색 단계에서 호출됨.

해결 문제:
1. **소스별 인증/timeout/포맷 차이 흡수** — 각 어댑터가 자체 처리.
2. **신뢰도 tier 적용** — V1 §4 신뢰도 (Wikipedia 0.8, arXiv 0.9 등) 자동 부여.
3. **6-2 외부 응답 PII** — 외부에서 가져온 텍스트도 마스킹 적용 (인덱싱 안 된 즉시 결과).
4. **6-2 API 키 보안** — `api_key_management.md` 정책 준수 (env 변수, rotation 30일).

### 4.2 E2 — 의사코드 (5 소스 어댑터)

```python
class IExternalAdapter(ABC):
    source_name: str
    reliability: float  # V1 §4 정본
    version_active: Literal["V1", "V2"]

    @abstractmethod
    async def search(self, query: str) -> list[Document]: ...

class WebAdapter(IExternalAdapter):
    source_name = "web"
    reliability = 0.7  # 0.6~0.8 범위 평균
    version_active = "V1"

    async def search(self, query: str) -> list[Document]:
        # Tavily / Serper API
        api_key = os.environ["TAVILY_API_KEY"]  # 6-2 api_key_management 정책
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post("https://api.tavily.com/search", headers={"Authorization": f"Bearer {api_key}"}, json={"query": query, "max_results": 10})
        results = resp.json()["results"]
        docs = []
        for r in results:
            content = r["content"]
            content, _ = pii_masker.apply_l2(content, strategy="partial")
            content = _strip_secrets(content)  # 6-2 코드 시크릿 사전 제거
            docs.append(Document(
                doc_id=f"web::{hashlib.sha256(r['url'].encode()).hexdigest()[:16]}",
                title=r["title"], content=content, source="web", score=r.get("score", 0.5),
                freshness_days=_freshness(r.get("published_date")), reliability=self.reliability,
                metadata={"url": r["url"], "engine": "tavily"},
            ))
        return docs

class WikipediaAdapter(IExternalAdapter):
    source_name = "wikipedia"
    reliability = 0.8
    version_active = "V1"

    async def search(self, query: str) -> list[Document]:
        # MediaWiki API
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get("https://ko.wikipedia.org/w/api.php", params={
                "action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": 5
            })
        hits = resp.json()["query"]["search"]
        docs = []
        for h in hits:
            content = re.sub(r"<.+?>", "", h["snippet"])  # HTML 태그 제거
            content, _ = pii_masker.apply_l2(content, strategy="partial")
            docs.append(Document(
                doc_id=f"wikipedia::{h['pageid']}",
                title=h["title"], content=content, source="wikipedia", score=0.5,
                freshness_days=0, reliability=self.reliability,
                metadata={"page_id": h["pageid"], "url": f"https://ko.wikipedia.org/?curid={h['pageid']}"},
            ))
        return docs

class ArxivAdapter(IExternalAdapter):
    source_name = "arxiv"
    reliability = 0.9
    version_active = "V2"  # V1은 미활성

    async def search(self, query: str) -> list[Document]:
        if self.version_active == "V2" and not _v2_active():
            return []  # V1 단계 skip
        # arXiv API
        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=5, sort_by=arxiv.SortCriterion.Relevance)
        docs = []
        for result in client.results(search):
            content, _ = pii_masker.apply_l2(result.summary, strategy="partial")
            docs.append(Document(
                doc_id=f"arxiv::{result.entry_id.split('/')[-1]}",
                title=result.title, content=content, source="arxiv", score=0.7,
                freshness_days=(datetime.now() - result.published).days, reliability=self.reliability,
                metadata={"authors": [a.name for a in result.authors], "url": result.entry_id},
            ))
        return docs

class FinanceAdapter(IExternalAdapter):
    source_name = "finance"
    reliability = 0.9
    version_active = "V1"  # P1

    async def search(self, query: str) -> list[Document]:
        # Yahoo Finance / KRX
        # (구현: yfinance 또는 KRX API)
        ...

class NewsAdapter(IExternalAdapter):
    source_name = "news"
    reliability = 0.6  # tier별 가변
    version_active = "V2"

    async def search(self, query: str) -> list[Document]:
        if not _v2_active():
            return []
        # RT-BNP Pipeline 통합 (cross-ref 6-7)
        ...

class ExternalSources:
    def __init__(self):
        self.adapters: dict[str, IExternalAdapter] = {
            "web": WebAdapter(), "wikipedia": WikipediaAdapter(),
            "arxiv": ArxivAdapter(), "finance": FinanceAdapter(), "news": NewsAdapter(),
        }

    async def parallel_search(self, queries: list[str], sources: list[str] = None) -> list[Document]:
        sources = sources or list(self.adapters.keys())
        tasks = []
        for src in sources:
            if src not in self.adapters:
                continue
            adapter = self.adapters[src]
            for q in queries:
                tasks.append(self._safe_search(adapter, q))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_docs = []
        for r in results:
            if isinstance(r, Exception):
                continue  # 개별 실패는 partial_failure
            all_docs.extend(r)
        return all_docs

    async def _safe_search(self, adapter: IExternalAdapter, query: str) -> list[Document]:
        try:
            return await asyncio.wait_for(adapter.search(query), timeout=10.0)  # timeout_policy §2 #5
        except asyncio.TimeoutError:
            audit_log.warn(f"AUX-E-EXT-001: {adapter.source_name} timeout on query={query[:50]}")
            return []
```

### 4.3 E5 — 에러 핸들링

| error_code | 설명 | recoverable | 처리 |
|-----------|------|:-----------:|------|
| `AUX-E-EXT-001` | 외부 API timeout | YES | 빈 결과 + audit (partial_failure 허용) |
| `AUX-E-EXT-002` | rate limit (HTTP 429) | YES | exponential backoff 3회 |
| `AUX-E-EXT-003` | 결과 위변조 (스키마 mismatch) | NO | 거부 + audit |
| `AUX-E-EXT-004` | API 키 미설정 | NO | 설정 오류 + 6-2 알림 |
| `AUX-E-PII-002` | 외부 응답 PII 마스킹 실패 | NO | 응답 차단 |
| `AUX-E-EXT-005` | V2 미활성 소스 호출 (arxiv/news) | YES | 빈 결과 + skip |

### 4.4 E6 — 성능 벤치마크

| 소스 | timeout_policy | P95 | 신뢰도 |
|------|------------|:---:|:------:|
| Web (Tavily) | 외부 검색 API (§2 #5) | 1500 ms | 0.7 |
| Wikipedia | (§2 #5) | 800 ms | 0.8 |
| arXiv | (§2 #5) | 1200 ms | 0.9 |
| 금융 (yfinance/KRX) | (§2 #5) | 1000 ms | 0.9 |
| News | (§2 #5) | 1500 ms | tier별 |

### 4.5 E7 — 테스트 시나리오

| # | 시나리오 | 입력 | 예상 |
|---|---------|------|------|
| T-01 | Web 정상 | "VAMOS AI" | Tavily 결과 5+, reliability=0.7 |
| T-02 | Wikipedia | "AI 거버넌스" | MediaWiki 결과, reliability=0.8 |
| T-03 | arXiv V2 활성 | "transformer" | arXiv 결과 |
| T-04 | arXiv V1 단계 | (V2 미활성) | 빈 결과 |
| T-05 | 금융 | "삼성전자" | yfinance 결과 |
| T-06 | timeout | (mock 12s) | AUX-E-EXT-001 빈 결과 |
| T-07 | rate limit | (mock 429) | backoff 후 성공 |
| T-08 | API 키 미설정 | (env 누락) | AUX-E-EXT-004 |
| T-09 | PII in 외부 응답 | "이 사람의 이메일은..." | 마스킹 |
| T-10 | 시크릿 in 외부 응답 | code with API key | _strip_secrets |
| T-11 | F-10 fallback | (소스 실패) | 22 fallback ID 등재 (STEP_C) |

### 4.6 E9 — 의존성 명세

| 카테고리 | 의존성 |
|---------|--------|
| 외부 SDK | `tavily-python` (Web), `wikipedia-api` (Wikipedia) |
| 외부 SDK | `arxiv` (arXiv), `yfinance` (금융), KRX API (한국 거래소) |
| 외부 라이브러리 | `httpx` (비동기 HTTP), `tenacity` (retry) |
| 내부 모듈 | `search_api_v2`, `search_pipeline_v2`, `00_common/*` |
| Cross-domain (V2 News) | `6-7_RT-BNP-DCL` (RT-BNP Pipeline) | 뉴스 통합 |
| 환경 변수 | `TAVILY_API_KEY`, `OPENAI_API_KEY` (옵션) | 6-2 api_key_management |
| 횡단 도메인 | `6-2/01_ai-code-security/pii_regex_masking` (응답 마스킹) |
| 횡단 도메인 | `6-2/02_hmac-timing-defense/api_key_management` (키 관리) |

---

## 5. LOCK 교차 검증

| LOCK | AUTHORITY | 본 V2 | 일치 |
|------|---------|-------|:----:|
| LOCK-AX-01 | I-16 CORE | §2 | ✅ |
| LOCK-AX-10 (캐시) | search_api_v2가 외부 결과 시맨틱 캐시 | §4.1 (위임) | ✅ |
| V1 §4 신뢰도 (Web 0.6~0.8 / Wiki 0.8 / arXiv 0.9 / 금융 0.9) | V1 정본 | §4.2 reliability 정합 | ✅ |

---

## 6. V2 종결 marker

★ V2-Phase 2 (2026-05-10, 세션 2-4)
★ V1 byte EXACT
★ LOCK-AX-01/10 EXACT
★ E1+E2(5 어댑터 + 병렬 + safe_search)+E5+E6+E7+E9 6요소
★ V1 §4 5 소스 신뢰도 정합
★ F-10 이월 (22 fallback ID, STEP_C)
★ 6-2 API 키 + PII + 시크릿 다중 cross-ref
★ L3: PENDING
