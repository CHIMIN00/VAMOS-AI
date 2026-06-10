# DCL Channels — 3채널 애그리게이터 + ISS-4 + P4 DCL-GEO 화이트리스트

> **수정 정책**: 정본 — Phase 변경 시 갱신 (§8.2)
> **도메인**: 6-7_RT-BNP-DCL / 02_domain-context-layer
> **Tier**: 6 (System-wide Components)
> **정본 출처**:
> - VAMOS_CLOUD_LIBRARY_SPEC (관련 인프라, LOCK 1차) verbatim — §7 정보 환경 6계층 + §8 Gate System
> - Part2 §6.10.2 (FULL, L5664-L5741) verbatim — DCL 채널 정의 + QoD ≥ 0.5 + 비용 상한 + 1시간 갱신
> - Part2 §6.10 공통 (G0-G4 Gate, 소스 가중치, LOCK #1~13)
> - SOT2 6-7 종합계획서 §6.2 ISS-4 (DCL 3채널 애그리게이터 알고리즘 MEDIUM) + §6.2 P4 (DCL-GEO V2+ 소스 목록 미정의 LOW) + §7.2 P2-1 + §4.3 R-67-3/R-67-5 + §9.4 RETRACTION 무효화 범위
> - AUTHORITY_CHAIN.md §3.3 (L11~L16) + §3.4 (L17~L18) + §4 (6-8 경계 선언)
> - 02_domain-context-layer/_index.md §3채널 + §품질 관리 + §6-8 연동 참조
> - **6-8 LOCK 인용 정본 (read-only, 재정의 ❌)**:
>   - `D:\VAMOS\docs\test_iso_p2\sot 2\6-8_Cloud-Library\02_service-mesh\_index.md` Fast Gate CL-G0~G4 공통 정의 (LOCK #1~13)
> **LOCK 매핑**: L4 (Fast Gate 적용 규칙), L5 (RT-BNP 전용 소스 가중치), L11 (DCL 6계층 정보 환경), L12 (DCL 3채널 정의), L13 (DCL QoD 임계값), L15 (DCL 비용 상한), L16 (CL-G3 Security Gate 필수 적용), L17 (Fast Gate ↔ VAMOS 5-Gate 분리)
> **DH 매핑**: DH-3 (DCL Aggregator 알고리즘 — 본 문서 정본), DH-5 (DCL-GEO 초기 소스 화이트리스트 — 본 문서 정본)
> **Phase**: P2-1 (ISS-4 dcl_channels 부분 + P4 해결)
> **생성일**: 2026-04-28
> **ISS 해결**: **ISS-4** (DCL 3채널 애그리게이터 알고리즘 — 본 문서 + rag_integration.md 분담) + **P4** (DCL-GEO 초기 소스 화이트리스트 5건 이상 정의)
> **선행 의존**: 02/_index.md (3채널 총괄 + L11~L16 LOCK 매핑) / 01/_index.md (RT-BNP 파이프라인 — DCL-FIN 경유) / 6-8 sandbox 02_service-mesh/_index.md (Fast Gate 공유) / AUTHORITY_CHAIN.md §3.3 + §4

---

## 교차 참조 블록 (Rule a)

| 참조 대상 | 관계 |
|----------|------|
| **VAMOS_CLOUD_LIBRARY_SPEC §7 verbatim** | 6계층 정보 환경 1차 정본 (LOCK 출처) — L11 정본 |
| **Part2 §6.10.2 L5664-L5741 verbatim** | DCL 전문 설계 정본 (FULL) — 채널 정의·QoD·비용·갱신 주기 |
| **Part2 §6.10.1 verbatim (소스 가중치)** | RT-BNP 전용 소스 가중치 (L5) — DCL-FIN 채널 가중치 정합 |
| **02_domain-context-layer/_index.md §3개 도메인 컨텍스트 채널** | 3채널 총괄 정의 (L12) — 본 §2~§4 상세화 |
| **02_domain-context-layer/_index.md §DCL 품질 관리** | L13/L14/L15/L16 + R-67-3 — 본 §5 상세화 |
| **02_domain-context-layer/_index.md §6-8 연동 참조** | DCL-TECH 배치 경유 + LOCK #1~13 공통 준수 — 본 §6 상세화 |
| **01_rt-bnp-pipeline/_index.md §파이프라인 아키텍처** | DCL-FIN 경유 정본 (R-67-5) — 본 §2 정합 |
| **종합계획서 §6.2 ISS-4** | DCL 3채널 애그리게이터 알고리즘 (MEDIUM, Phase 2) — dcl_channels.md + rag_integration.md 분담 |
| **종합계획서 §6.2 P4** | DCL-GEO V2+ 소스 목록 미정의 (LOW, Phase 2) — 본 §4 화이트리스트 정본 정의 |
| **종합계획서 §4.3 R-67-3** | DCL 비용 상한 준수 — 본 §5.5 운영 비용 모니터링 |
| **종합계획서 §4.3 R-67-5** | DCL-FIN ↔ RT-BNP 결합 — 본 §2.1 별도 수집 경로 생성 금지 |
| **종합계획서 §9.4 RETRACTION 무효화 범위** | DCL 캐시 엔트리 무효화 — 본 §7 RETRACTION 처리 |
| **AUTHORITY_CHAIN.md §3.3 L11~L16** | DCL LOCK 정본 — 본 §2~§5 verbatim 인용 (재정의 ❌) |
| **AUTHORITY_CHAIN.md §3.4 L17** | Fast Gate ↔ VAMOS 5-Gate 분리 — 본 §6.1 BaseGate(ABC) 인터페이스만 공유 |
| **AUTHORITY_CHAIN.md §4 6-8 경계** | 데이터 흐름=6-7 / 인프라 운영=6-8 — 본 §6 정합 |
| **rag_integration.md (P2-2)** | DCL → RAG 삽입 트리거 — 본 §3.4 QoD ≥ 0.5 출력 인터페이스 정합 |
| **background_summary.md (P2-3)** | DCL 채널 집계 결과 → 배경 요약 입력 — 본 §3.6 출력 정합 |
| **6-8 sandbox 02_service-mesh/_index.md (read-only)** | Fast Gate CL-G0~G4 공통 정의 + LOCK #1~13 — 본 §6 인용 (baseline 불변) |
| **6-4 Memory-RAG (참조만)** | DCL QoD ≥ 0.5 → 6-4 RAG 파이프라인 (W-2 RESOLVED, 6-4 LOCK 재정의 ❌) |
| **6-13 Operations (참조만)** | RT-BNP 소스 장애 대응 (W-3 RESOLVED, 6-13 LOCK 재정의 ❌) |

---

## 1. 개요

본 문서는 Domain Context Layer(DCL)의 3채널(DCL-FIN/DCL-TECH/DCL-GEO) 각각의 소스 목록·수집 방식·QoD(Quality of Data) 산출 로직·충돌 시 신뢰도 가중 평균 알고리즘을 상세 명세하고, **P4 DCL-GEO 초기 소스 화이트리스트**를 정본 정의한다. **L13(QoD ≥ 0.5 → RAG 삽입)**, **L16(CL-G3 Security Gate 필수 적용)**, **R-67-5(DCL-FIN ↔ RT-BNP 결합)**, **R-67-3(DCL 비용 상한 준수)** 규칙을 각 채널에 강제한다.

> **DCL 핵심 원칙 (Part2 §6.10.2 verbatim)**: "모든 정보를 가져오는 것"보다 "필요한 정보를 빠르게 가져오는 것" — 전체 인터넷 크롤링의 비용/품질 문제 없이 도메인별 선택적 실시간 배경 맥락을 제공한다.

### 1.1 책임 요약

- **3채널 정의 (§2~§4)**: DCL-FIN(금융, RT-BNP 경유) / DCL-TECH(기술, RSS+6-8 배치) / DCL-GEO(지정학, RSS) — LOCK L12 verbatim 인용
- **QoD 산출 로직 (§3.4)**: 신뢰도(소스 가중치 L5) + 정확성 + 신선도 + 완전성 + 일관성 → 0.0~1.0 정규화. **L13: ≥ 0.5 → RAG 삽입 / < 0.5 → 폐기**
- **충돌 해결 알고리즘 (§3.5)**: 동일 주제 다수 소스 → 신뢰도 가중 평균 (ISS-4 핵심) — `result = Σ(qod_i × weight_i) / Σ(weight_i)`
- **DCL-GEO 초기 소스 화이트리스트 (§4.2)**: P4 해결 — RSS 기반 7건 (Reuters World + AP World + BBC World + Al Jazeera + 연합뉴스 국제 + RFI + Deutsche Welle)
- **CL-G3 Security Gate 적용 (§5.4)**: L16 — 모든 채널에 보안 필터 필수 (악성 URL + 허위 정보 + 개인정보)
- **6-8 cross-handoff (§6)**: Fast Gate 공유 (BaseGate(ABC) 인터페이스만, L17) + DCL-TECH 배치 경유 (6-8 LOCK #1~13 read-only)
- **비용 상한 준수 (§5.5)**: R-67-3 — V1: +₩0 / V2: +₩5,000/월 / V3: +₩15,000/월 (LOCK L15)
- **RETRACTION 처리 (§7)**: §9.4 4 무효화 대상 중 DCL 캐시 엔트리 — 캐시 키 삭제 + 다음 갱신 주기 시 재생성

### 1.2 채널별 의존 흐름

```
DCL-FIN ──── RT-BNP 파이프라인 (§6.10.1, R-67-5) ───┐
                                                       │
DCL-TECH ─── RSS Collector (§6.10.2 V1)             │
       └──── 6-8 Cloud Library 배치 (V2+, §7.4)     ├─→ DCL Aggregator (§3) ─→ rag_integration.md (P2-2)
                                                       │                       ─→ background_summary.md (P2-3)
DCL-GEO ──── RSS Collector (§4.2 화이트리스트, P4) ─┘
```

---

## 2. DCL-FIN 채널 (금융/투자)

### 2.1 채널 개요 (LOCK L12 verbatim)

> **출처**: AUTHORITY_CHAIN.md §3.3 L12 + Part2 §6.10.2 verbatim — "DCL-FIN(금융) / DCL-TECH(기술) / DCL-GEO(지정학)"
>
> **R-67-5 (종합계획서 §4.3 verbatim)**: "DCL-FIN 채널은 반드시 RT-BNP 파이프라인을 경유하며, 별도 수집 경로 생성 금지"

DCL-FIN 채널은 시장 뉴스·경제 지표·기업 실적·금리 정책을 수집하여 VAMOS AI의 금융 도메인 배경 맥락을 형성한다. **별도 수집 경로 생성 금지** — 모든 금융 데이터는 [01_rt-bnp-pipeline](../01_rt-bnp-pipeline/_index.md) 경유로 통일한다.

### 2.2 소스 목록 (LOCK L5 verbatim 인용)

> **출처**: AUTHORITY_CHAIN.md §3.3 L5 verbatim — "공식=1.0, 통신사/금융=0.95, 주요 언론=0.75, SNS=0.4"
>
> **출처**: 01_rt-bnp-pipeline/_index.md §RT-BNP 전용 소스 가중치 (LOCK L5)

| 소스 카테고리 | 예시 소스 | 소스 가중치 (L5) | Tier (L2) | 버전 |
|-------------|----------|----------------|----------|------|
| 공식 발표 (정부/중앙은행) | Federal Reserve, BoK, ECB | 1.0 | T2 (REST API) | V2+ |
| 통신사 (속보 전문) | Reuters, AP, 연합뉴스 | 0.95 | T1~T3 | V1+ |
| 금융 데이터 (시장 데이터 전문) | Bloomberg, Finnhub, Alpha Vantage | 0.95 | T1 (WebSocket) / T2 (REST) | V2 (T2) / V3 (T1) |
| 주요 언론 | Wall Street Journal, Financial Times | 0.75 | T3 (RSS) | V1+ |
| SNS/소셜 | Twitter/X (금융 인플루언서) | 0.4 (다수 소스 교차 확인 시) | T4 | V2+ |

> **NOTE (Part2 §6.10.1 verbatim)**: 이 가중치는 CLOUD_LIBRARY_SPEC 일반 가중치(1.0/0.9/0.85/0.7/0.6/0.5/0.3)와 다르다. RT-BNP는 도메인 특화 가중치를 사용한다.

### 2.3 수집 방식 (버전별)

| 버전 | 수집 방식 | Tier 범위 | 갱신 주기 | 비용 (L15 누적) |
|------|----------|----------|----------|----------------|
| V1 | RSS 60초 폴링 | T3만 | 60초 | +₩0 (RSS 무료) |
| V2 | REST API 30초 폴링 | T2+T3+T4 | 30초~120초 | +₩2,000~5,000/월 (§5.3 DCL-FIN 분배 ~₩2,500, LOCK L15 V2 +₩5,000 한도 내) |
| V3 | WebSocket 스트리밍 | T1~T4 전체 | 실시간 | +₩9,000~15,000/월 (§5.3 DCL-FIN WebSocket ~₩9,000, LOCK L15 V3 +₩15,000 한도 내) |

### 2.4 QoD 산출 (§3.4 공통 로직 적용)

DCL-FIN 채널의 QoD 산출은 §3.4 공통 로직에 따르되, 시장 영향도(Impact Score, RT-BNP Breaking Detector 산출)를 가중치로 추가한다:

```
qod_fin = (accuracy × 0.30) + (freshness × 0.25) + (consistency × 0.20)
        + (source_weight × 0.15) + (impact_score × 0.10)
```

- `accuracy`: 다수 소스 교차 확인 비율 (0~1)
- `freshness`: 발행 후 경과 시간 역수 (5분 이내=1.0, 1시간=0.5, 24시간=0.1)
- `consistency`: 동일 주제 소스 간 일관성 (Cosine similarity, 0~1)
- `source_weight`: L5 가중치 정규화 (1.0=1.0, 0.95=0.95, 0.4=0.4)
- `impact_score`: RT-BNP Breaking Detector 출력 (0~100 → 0~1 정규화)

---

## 3. DCL-TECH 채널 (기술/AI 동향)

### 3.1 채널 개요

DCL-TECH 채널은 LLM 릴리스, 프레임워크 업데이트, 보안 취약점, 학술 논문 동향을 수집하여 VAMOS AI의 기술 도메인 배경 맥락을 형성한다. **6-8 Cloud Library 배치 파이프라인 경유**로 심층 지식을 보강한다.

### 3.2 소스 목록

| 소스 카테고리 | 예시 소스 | 수집 경로 | 갱신 주기 |
|-------------|----------|----------|----------|
| LLM/AI 릴리스 RSS | Anthropic Blog, OpenAI Blog, Google AI Blog | RSS 폴링 | 1시간 |
| 프레임워크 업데이트 RSS | LangChain Release, LlamaIndex Release | RSS 폴링 | 1시간 |
| 보안 취약점 RSS | CVE Feed, NIST NVD, Anthropic Security Advisory | RSS 폴링 | 1시간 |
| 학술 논문 (V2+) | arXiv cs.AI/cs.CL Daily, Papers with Code | 6-8 배치 파이프라인 | 매일 |
| 산업 분석 (V2+) | The Verge AI, MIT Tech Review | 6-8 배치 파이프라인 | 매일 |

### 3.3 수집 방식 (버전별)

| 버전 | 수집 방식 | 심층 지식 보강 | 비용 (L15 누적) |
|------|----------|--------------|----------------|
| V1 | RSS 1시간 폴링 (LLM/AI 릴리스 + 보안 취약점) | 미구현 | +₩0 (RSS 무료) |
| V2 | RSS 1시간 + 6-8 Cloud Library 배치 | 매일 (V2 비용 한도 ₩5,000 내) | +₩0~₩2,000/월 |
| V3 | 실시간 + 자동 학습 + 6-8 배치 통합 | 실시간 | +₩2,000~₩5,000/월 |

### 3.4 QoD 산출 공통 로직 (LOCK L13 verbatim)

> **출처**: AUTHORITY_CHAIN.md §3.3 L13 verbatim — "QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기"

```
qod = (accuracy × 0.30) + (freshness × 0.25) + (consistency × 0.20)
    + (source_weight × 0.15) + (completeness × 0.10)
```

- `accuracy`: 사실 검증 (다수 소스 교차 확인) — 0.0~1.0
- `freshness`: 발행 후 경과 시간 역수 — DCL-FIN은 5분/DCL-TECH는 24시간/DCL-GEO는 1시간 기준
- `consistency`: 동일 주제 소스 간 일관성 — 0.0~1.0
- `source_weight`: L5 가중치 정규화 — 0.0~1.0
- `completeness`: 필수 필드(제목, 본문, 발행 시각, 출처) 완전성 — 0.0~1.0

**판정**:
- `qod ≥ 0.5` → RAG 삽입 (rag_integration.md P2-2 트리거)
- `qod < 0.5` → 폐기 (Discard, 로그만 기록)

### 3.5 충돌 해결: 신뢰도 가중 평균 알고리즘 (ISS-4 핵심)

동일 주제(topic_id)에 대해 N개의 소스에서 정보가 수집된 경우, 다음 알고리즘으로 단일 결과를 도출한다:

```python
def resolve_conflict(sources: list[Source]) -> AggregatedSource:
    """
    sources: 동일 topic_id를 가진 N개의 소스
    반환: 신뢰도 가중 평균으로 통합된 단일 결과
    """
    total_weight = sum(s.source_weight for s in sources)
    if total_weight == 0:
        return None  # 모든 소스 가중치 0 → 폐기

    aggregated_qod = sum(s.qod * s.source_weight for s in sources) / total_weight
    aggregated_accuracy = sum(s.accuracy * s.source_weight for s in sources) / total_weight

    # 텍스트 내용은 가장 가중치 높은 소스 채택
    primary_source = max(sources, key=lambda s: s.source_weight)

    return AggregatedSource(
        topic_id=primary_source.topic_id,
        text=primary_source.text,
        qod=aggregated_qod,
        accuracy=aggregated_accuracy,
        contributing_sources=[s.source_id for s in sources],
    )
```

- **충돌 임계**: 동일 topic_id가 3개 이상 소스에서 5분 윈도우 내 발생 시 (RT-BNP L9 5분 중복 억제 정합)
- **폐기 조건**: 가중치 합 = 0 또는 aggregated_qod < 0.5

### 3.6 출력 인터페이스 (P2-2/P2-3 의존)

DCL Aggregator는 QoD ≥ 0.5 통과 정보를 다음 두 경로로 출력한다:

| 출력 경로 | 인터페이스 | 의존 |
|----------|----------|------|
| RAG 삽입 | `rag_insert_request = {channel, qod, vector, payload, source_id, timestamp}` | rag_integration.md (P2-2) |
| 배경 요약 | `aggregated_topics = [{channel, topics[], aggregated_qod}]` | background_summary.md (P2-3) |

---

## 4. DCL-GEO 채널 (지정학/시사)

### 4.1 채널 개요

DCL-GEO 채널은 전쟁·제재·정책 변경·자연재해·국제 협상 정보를 수집하여 VAMOS AI의 지정학 도메인 배경 맥락을 형성한다. **V2+ 도입** (V1 미구현, LOCK L12 + Part2 §6.10.2 정합).

### 4.2 P4 해결 — DCL-GEO 초기 소스 화이트리스트 (DH-5 정본 정의)

> **출처**: 종합계획서 §6.2 P4 verbatim — "DCL-GEO V2+ 소스 목록 미정의 LOW, Phase 2 해결"
>
> **출처**: AUTHORITY_CHAIN.md §5 DH-5 verbatim — "DCL-GEO 초기 소스 화이트리스트 — V2 DCL-GEO 채널의 RSS 소스 목록"

본 문서는 DCL-GEO 채널의 초기 소스 화이트리스트를 정본 정의한다. RSS 폴링 5분 주기 대상으로 다음 7개 소스를 등재한다 (P4 검증 기준 5건 이상 충족):

| # | 소스명 | URL 패턴 | 카테고리 | 신뢰도 가중치 (L5 매핑) | 폴링 주기 |
|---|--------|----------|----------|----------------------|----------|
| 1 | Reuters World | reuters.com/world/feed | 통신사 (국제) | 0.95 | 5분 |
| 2 | AP World News | apnews.com/world-news/feed | 통신사 (국제) | 0.95 | 5분 |
| 3 | BBC World | feeds.bbci.co.uk/news/world/rss.xml | 주요 언론 (영국) | 0.75 | 5분 |
| 4 | Al Jazeera English | aljazeera.com/xml/rss/all.xml | 주요 언론 (중동) | 0.75 | 5분 |
| 5 | 연합뉴스 국제 | yna.co.kr/rss/international.xml | 통신사 (한국) | 0.95 | 5분 |
| 6 | RFI English | rfi.fr/en/rss | 공영 (프랑스) | 0.75 | 5분 |
| 7 | Deutsche Welle | dw.com/atom/rss-en-all | 공영 (독일) | 0.75 | 5분 |

**선정 기준**:
- 다국가 분산 (북미 2 + 한국 1 + 유럽 3 + 중동 1) → 단일 관점 편향 방지
- 통신사 우선 (Reuters / AP / 연합) → 가중치 0.95 (L5)
- 영어 + 한국어 혼합 → VAMOS 사용자 다국어 정합
- RSS 무료 → V2 비용 한도 ₩5,000 내 추가 비용 0 (R-67-3 준수)

### 4.3 수집 방식 (버전별)

| 버전 | 수집 방식 | 갱신 주기 | 비용 (L15 누적) |
|------|----------|----------|----------------|
| V1 | 미구현 | N/A | +₩0 |
| V2 | RSS 5분 폴링 (§4.2 화이트리스트 7건) | 5분 | +₩0 (RSS 무료) |
| V3 | 실시간 + RT-BNP 확장 (BREAKING-P0 지정학 이벤트 즉시 전파) | 실시간 | +₩0~₩1,000/월 |

### 4.4 QoD 산출 (§3.4 공통 로직 적용)

DCL-GEO는 §3.4 공통 로직에 따르되, **freshness 기준을 1시간**으로 설정한다 (지정학 이벤트는 5분 이내 발생 빈도 낮음):

- `freshness`: 발행 후 경과 시간 역수 — 1시간 이내=1.0, 6시간=0.5, 24시간=0.1
- 나머지 가중치는 §3.4 공통 적용

---

## 5. DCL 품질 관리 (L13/L14/L15/L16)

### 5.1 QoD 임계값 (LOCK L13 verbatim)

> **출처**: AUTHORITY_CHAIN.md §3.3 L13 verbatim — "QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기"
>
> **출처**: 02_domain-context-layer/_index.md §DCL 품질 관리 verbatim — "DCL 데이터 QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기 (LOCK L13)"

모든 DCL 채널(FIN/TECH/GEO)은 QoD ≥ 0.5 임계값을 통과한 정보만 RAG 삽입 및 배경 요약 입력으로 전달한다. 임계값 미달 정보는 폐기되며, 폐기 사유는 운영 로그에 기록된다.

### 5.2 배경 요약 갱신 주기 (LOCK L14 verbatim)

> **출처**: AUTHORITY_CHAIN.md §3.3 L14 verbatim — "1시간마다 재생성"

DCL 3채널 집계 결과는 1시간마다 [background_summary.md (P2-3)](background_summary.md) 알고리즘에 의해 재생성된다. 본 문서는 채널 수집 단계까지를 다루며, 요약 알고리즘 상세는 P2-3 문서 참조.

### 5.3 비용 상한 (LOCK L15 verbatim)

> **출처**: AUTHORITY_CHAIN.md §3.3 L15 verbatim — "V1: +₩0, V2: +₩5,000/월, V3: +₩15,000/월"
>
> **출처**: 종합계획서 §4.3 R-67-3 verbatim — "DCL 비용 상한 준수 — 각 버전별 DCL 비용 상한(L15)을 초과하는 소스 추가 금지"

| 버전 | 비용 상한 (L15) | 채널별 분배 |
|------|---------------|-------------|
| V1 | +₩0/월 | RSS만 (무료) |
| V2 | +₩5,000/월 | DCL-FIN REST API 50% (~₩2,500) + DCL-TECH 6-8 배치 30% (~₩1,500) + DCL-GEO RSS 0% + 운영 예비 20% (~₩1,000) |
| V3 | +₩15,000/월 | DCL-FIN WebSocket 60% (~₩9,000) + DCL-TECH 실시간+학습 25% (~₩3,750) + DCL-GEO 실시간 5% (~₩750) + 운영 예비 10% (~₩1,500) |

### 5.4 CL-G3 Security Gate 적용 (LOCK L16 verbatim)

> **출처**: AUTHORITY_CHAIN.md §3.3 L16 verbatim — "DCL 모든 채널에 CL-G3 보안 필터 필수"
>
> **출처**: 6-8 sandbox 02_service-mesh/_index.md (read-only) — Fast Gate CL-G3 (Security) 정의

모든 DCL 채널 수집 데이터는 RAG 삽입 전 CL-G3 Security Gate를 필수 통과한다:

| 검사 항목 | 차단 조건 | 폴백 |
|----------|----------|------|
| 악성 URL 검사 | 블랙리스트 매칭 / 피싱 도메인 | 폐기 + 로그 |
| 허위 정보 휴리스틱 | 이미 RETRACTION 발행된 topic_id 참조 | 폐기 + 로그 |
| 개인정보 검사 (PII) | 이메일 / 주민번호 / 카드번호 패턴 | 마스킹 후 통과 |
| 악성 코드 휴리스틱 | XSS / SQL injection 패턴 | 폐기 + 보안 알림 |

**Fast Gate ≠ VAMOS 5-Gate (LOCK L17)**: 본 CL-G3는 6-8 Cloud Library 전용이며, VAMOS 5-Gate(Policy → Approval → Cost → Evidence → SelfCheck)와 별도 체계이다. BaseGate(ABC) 인터페이스만 공유한다.

### 5.5 운영 비용 모니터링 (R-67-3 강제)

| 모니터링 항목 | 주기 | 임계 알림 | 폴백 |
|-------------|------|----------|------|
| DAILY 비용 집계 | 매일 00:00 | 누적 ≥ L15 80% | DCL-FIN T2/T3 폴링 주기 2배 연장 |
| MONTHLY 비용 집계 | 매월 마지막 날 23:59 | 누적 ≥ L15 100% | 익월 1일까지 신규 소스 추가 동결 |
| 모델 폴백 (V2+) | 비용 초과 시 즉시 | DCL-TECH 6-8 배치 호출 0회 (무료 RSS만) | 익월 정상 복구 |

---

## 6. 6-8 Cloud Library 경계 정합

### 6.1 Fast Gate 공유 (LOCK L17 — BaseGate(ABC) 인터페이스만)

> **출처**: AUTHORITY_CHAIN.md §3.4 L17 verbatim — "Fast Gate는 Cloud Library 전용, VAMOS 5-Gate와 별도 체계. BaseGate(ABC) 인터페이스만 공유"
>
> **출처**: AUTHORITY_CHAIN.md §4.2 verbatim — "RT-BNP → Fast Gate(CL-G0~G4): 6-8에서 정의한 G0-G4 Gate 로직 공유"

DCL 채널은 6-8 Cloud Library의 Fast Gate CL-G0~G4를 다음과 같이 적용한다 (LOCK L4 정합, 6-8 LOCK 재정의 ❌):

| Gate | 적용 (DCL) | 출처 정본 |
|------|-----------|----------|
| CL-G0 (Format) | ✅ 적용 — URL 유효성 + RSS/JSON 형식 검증 | 6-8 sandbox 02_service-mesh/_index.md |
| CL-G1 (Content Quality) | ⚡ 간소화 — 사전 등록 화이트리스트 자동 통과 | 6-8 정본 (재정의 ❌) |
| CL-G2 (Consistency) | ⏭️ 스킵 — DCL은 임팩트보다 신뢰도 가중 (§3.5) | 6-8 정본 |
| CL-G3 (Security) | ✅ 적용 — §5.4 CL-G3 4 검사 항목 (LOCK L16) | 6-8 정본 + L16 |
| CL-G4 (Final) | ⏭️ 스킵 — 사후 검증으로 대체 | 6-8 정본 |

### 6.2 DCL-TECH 배치 경유 (6-8 LOCK #1~13 read-only)

> **출처**: AUTHORITY_CHAIN.md §4.2 verbatim — "RT-BNP → Cloud Library 배치: DCL-TECH 채널의 심층 지식은 6-8 배치 파이프라인 경유"
>
> **출처**: AUTHORITY_CHAIN.md §4.3 verbatim — "6-7은 6-8의 LOCK #1~13 (Cloud Library 공통 LOCK)을 준수한다"

DCL-TECH 채널의 심층 지식 (학술 논문, 산업 분석)은 6-8 Cloud Library 배치 파이프라인을 경유한다 (V2+). 6-8 LOCK #1~13(크롤링 간격, 소스 수, 동시 연결 등)은 read-only 인용이며, 본 6-7에서 재정의하지 않는다.

| 6-8 LOCK | 적용 범위 (DCL-TECH) | 6-7 재정의 |
|---------|--------------------|----------|
| LOCK #1 (크롤링 간격) | 6-8 정본 준수 | ❌ |
| LOCK #2 (소스 수 상한) | 6-8 정본 준수 | ❌ |
| LOCK #3~13 | 6-8 정본 준수 | ❌ |

### 6.3 인접 도메인 경계 (W-1/W-2/W-3 RESOLVED 정합)

| 인접 도메인 | 경계 | 출처 |
|-----------|------|------|
| **6-4 Memory-RAG** | DCL = QoD ≥ 0.5 → RAG 삽입 트리거 (생산측) / 6-4 = RAG 파이프라인·벡터 DB (소비측) | W-2 RESOLVED, AUTHORITY §4.4 |
| **6-13 Operations** | DCL = 채널 운영 trigger / 6-13 = 소스 장애 대응 운영 절차 (Part2 §6.12.10) | W-3 RESOLVED, AUTHORITY §4.4 |
| **6-3 Agent-Teams** | DCL = 컨텍스트 데이터 제공 / 6-3 = 에이전트 팀이 컨텍스트 소비 | AUTHORITY §4.4 |

---

## 7. RETRACTION 처리 (§9.4 무효화 범위 정합)

> **출처**: 종합계획서 §9.4 verbatim — "DCL 캐시 엔트리: 해당 Breaking Event ID를 소스로 참조하는 DCL-FIN/TECH/GEO 캐시 — 캐시 키 삭제 + 다음 갱신 주기 시 재생성"

DCL 캐시 엔트리는 RETRACTION 발행 시 다음과 같이 무효화된다 (LOCK L8 정합):

```
[RT-BNP] RETRACTION 이벤트 (oc.rt_bnp.retraction.issued)
        │
        ▼
[6-12 Event-Logging] EventBus 브로드캐스트 (payload: breaking_event_id, reason, timestamp)
        │
        ▼
[6-7 DCL Aggregator] 무효화 핸들러 (30초 SLA)
        │
        ├── DCL-FIN 캐시 키 삭제 (breaking_event_id 참조)
        ├── DCL-TECH 캐시 키 삭제
        └── DCL-GEO 캐시 키 삭제
        │
        ▼
[다음 갱신 주기] 캐시 재생성 (DCL-FIN 60초~/TECH 1h/GEO 5분)
```

**무효화 지연 상한**: RETRACTION 발행 후 **30초 이내** 전 채널 캐시 무효화 완료 (LOCK L6 속보 전파 30초와 동일 기준 적용, §9.4 verbatim).

---

## 8. V2 LOCK 인용 매트릭스 (LOCK ↔ 본 문서 §)

| LOCK | 정본 출처 | 값/규칙 (verbatim) | 본 문서 § | 대조 결과 |
|------|----------|------------------|----------|----------|
| L4 | Part2 §6.10.1 | CL-G0(적용) + CL-G1(간소화) + CL-G2(스킵) + CL-G3(적용) + CL-G4(스킵) | §6.1 | ✅ verbatim |
| L5 | Part2 §6.10.1 | 공식=1.0, 통신사/금융=0.95, 주요 언론=0.75, SNS=0.4 | §2.2 + §4.2 | ✅ verbatim |
| L11 | CLOUD_LIBRARY_SPEC + Part2 §6.10.2 | [0]DCL → [1]사용자 → [2]메모리 → [3]RAG → [4]Cloud Library → [5]외부API | §1 (개요), §1.2 흐름도 | ✅ 인용 |
| L12 | Part2 §6.10.2 | DCL-FIN(금융) / DCL-TECH(기술) / DCL-GEO(지정학) | §2.1 + §3.1 + §4.1 | ✅ verbatim |
| L13 | Part2 §6.10.2 | QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기 | §3.4 + §5.1 | ✅ verbatim |
| L15 | Part2 §6.10.2 | V1: +₩0, V2: +₩5,000/월, V3: +₩15,000/월 | §5.3 | ✅ verbatim |
| L16 | Part2 §6.10.2 | DCL 모든 채널에 CL-G3 보안 필터 필수 | §5.4 | ✅ verbatim |
| L17 | Part2 §6.10.1 | Fast Gate는 Cloud Library 전용, VAMOS 5-Gate와 별도 체계. BaseGate(ABC) 인터페이스만 공유 | §5.4 (말미) + §6.1 | ✅ verbatim |

---

## 9. 변경 이력

- 2026-04-28 v1.0 — P2-1 NEW (ISS-4 dcl_channels 부분 + P4 DCL-GEO 화이트리스트 7건 정본 정의 + LOCK L4/L5/L11/L12/L13/L15/L16/L17 verbatim 인용 + 신뢰도 가중 평균 알고리즘 ISS-4 핵심 + DCL Aggregator DH-3 정본 + DCL-GEO 화이트리스트 DH-5 정본 + 6-8 cross-handoff Fast Gate 공유 + DCL-TECH 배치 경유 + RETRACTION 처리 §9.4 정합)

<!-- FABRICATION-CHECK: zero-tolerance for hallucinated LOCK / DH / source IDs -->
<!-- LOCK 인용 verbatim 정합: AUTHORITY_CHAIN.md §3.3 L11~L16 + §3.4 L17 ✅ -->
<!-- DH 정본 정의: DH-3 (DCL Aggregator §3.5) + DH-5 (DCL-GEO 화이트리스트 §4.2) ✅ -->
<!-- 6-8 LOCK #1~13 read-only 인용 (재정의 ❌) ✅ -->
<!-- 6-4/6-13 LOCK 재정의 ❌ (참조만) ✅ -->
<!-- R-67-3 비용 상한 + R-67-5 RT-BNP 결합 verbatim 인용 ✅ -->
<!-- ISS-4 신뢰도 가중 평균 알고리즘 + P4 DCL-GEO 화이트리스트 7건 (≥5 충족) ✅ -->
<!-- §9.4 RETRACTION 무효화 §7 정합 (4 무효화 대상 중 DCL 캐시 엔트리) ✅ -->
<!-- L13 QoD ≥ 0.5 strict 임계 ✅ -->
<!-- CL-G3 4 검사 항목 (악성 URL + 허위 정보 + PII + 악성 코드) ✅ -->
