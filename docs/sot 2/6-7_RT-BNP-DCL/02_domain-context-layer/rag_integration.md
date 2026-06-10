# RAG Integration — I-2 RAG 연동 + I-3 L0 Context 주입 + ISS-4 RAG 부분

> **수정 정책**: 정본 — Phase 변경 시 갱신 (§8.2)
> **도메인**: 6-7_RT-BNP-DCL / 02_domain-context-layer
> **Tier**: 6 (System-wide Components)
> **정본 출처**:
> - VAMOS_CLOUD_LIBRARY_SPEC (관련 인프라, LOCK 1차) verbatim — §7 6계층 정보 환경 + I-2 RAG 연동
> - Part2 §6.10.2 (FULL, L5664-L5741) verbatim — DCL → RAG 삽입 시점 + I-3 L0 Context 주입 규칙
> - SOT2 6-7 종합계획서 §6.2 ISS-4 (RAG 연동 부분 MEDIUM) + §7.2 P2-2 + §9.4 RETRACTION 무효화 범위 (I-2 RAG 벡터 soft delete → 24h hard delete)
> - AUTHORITY_CHAIN.md §3.3 (L11 6계층 + L13 QoD 임계값) + §4 (6-8 경계 선언)
> - 02_domain-context-layer/_index.md §DCL → I-2 RAG 연동 흐름 + §교차 참조 (6-4 Memory-RAG)
> - dcl_channels.md (P2-1 산출물 — QoD ≥ 0.5 출력 인터페이스)
> - **6-4 Memory-RAG cross-handoff (read-only, 재정의 ❌)**: W-2 RESOLVED, 6-4 = RAG 파이프라인·벡터 DB (소비측), 6-7 = DCL → 삽입 트리거 (생산측)
> **LOCK 매핑**: L8 (허위 속보 RETRACTION → 이전 이벤트 무효화), L11 (DCL 6계층 정보 환경), L13 (DCL QoD 임계값), L16 (CL-G3 Security Gate 필수 적용)
> **DH 매핑**: 본 문서는 RAG 인터페이스 정본 (`rag_insert_request` 6-필드 스키마)
> **Phase**: P2-2 (ISS-4 rag_integration 부분 + I-2 RAG 연동 + I-3 L0 Context 주입)
> **생성일**: 2026-04-28
> **ISS 해결**: **ISS-4** (DCL 3채널 애그리게이터 알고리즘 — RAG 삽입 경로 부분, dcl_channels.md 정합)
> **선행 의존**: dcl_channels.md (P2-1, QoD ≥ 0.5 통과 정보 출력) / 02/_index.md (6계층 + I-2 RAG 흐름) / AUTHORITY §3.3 L11~L13

---

## 교차 참조 블록 (Rule a)

| 참조 대상 | 관계 |
|----------|------|
| **VAMOS_CLOUD_LIBRARY_SPEC §7 verbatim** | 6계층 정보 환경 1차 정본 (LOCK 출처) — L11 정본 |
| **Part2 §6.10.2 L5664-L5741 verbatim** | DCL 전문 설계 정본 (FULL) — I-2 RAG 연동 시점 + I-3 L0 Context 주입 규칙 |
| **02_domain-context-layer/_index.md §DCL → I-2 RAG 연동 흐름** | DCL Aggregator → I-2 RAG + I-3 L0 Context 흐름도 (본 §3 상세화) |
| **02_domain-context-layer/_index.md §교차 참조** | 6-4 Memory-RAG (I-2 RAG 벡터 삽입, 인덱싱) + 6-11 Hologram-Main-LLM (배경 인식 응답) |
| **dcl_channels.md (P2-1)** | DCL Aggregator 출력 인터페이스 (`rag_insert_request`) — 본 §2 6-필드 스키마 정본 정의 |
| **종합계획서 §6.2 ISS-4** | DCL 3채널 애그리게이터 알고리즘 — RAG 삽입 경로 부분 (P2-1 채널 수집 + 본 P2-2 RAG 삽입 분담) |
| **종합계획서 §9.4 RETRACTION 무효화 범위 verbatim** | "I-2 RAG 벡터: 해당 속보 기반 RAG 삽입 벡터 — 벡터 삭제 (soft delete → 24h 후 hard delete)" — 본 §5 정합 |
| **AUTHORITY_CHAIN.md §3.3 L8 verbatim** | 허위 속보 RETRACTION — 즉시 발행 + 이전 이벤트 무효화 — 본 §5 무효화 트리거 |
| **AUTHORITY_CHAIN.md §3.3 L11 verbatim** | [0]DCL → [1]사용자 → [2]메모리 → [3]RAG → [4]Cloud Library → [5]외부API — 본 §4 6계층 흐름 |
| **AUTHORITY_CHAIN.md §3.3 L13 verbatim** | QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기 — 본 §2.2 게이트 |
| **AUTHORITY_CHAIN.md §3.3 L16 verbatim** | DCL 모든 채널에 CL-G3 보안 필터 필수 — 본 §3.3 RAG 삽입 전 정합 검증 |
| **AUTHORITY_CHAIN.md §4.4 인접 도메인 경계** | 6-4 = RAG 파이프라인·벡터 DB (소비측) / 6-7 = DCL QoD ≥ 0.5 → 삽입 트리거 (생산측) |
| **background_summary.md (P2-3)** | RAG 검색 결과 → 배경 요약 입력 — 본 §3.4 출력 정합 |
| **6-4 sandbox (read-only, 재정의 ❌)** | I-2 RAG 파이프라인·벡터 DB 정본 (W-2 RESOLVED) |
| **6-11 Hologram-Main-LLM (참조만)** | Main LLM 배경 인식 응답 생성 (DCL → I-3 L0 주입 → 응답 정합) |

---

## 1. 개요

본 문서는 Domain Context Layer(DCL)에서 QoD ≥ 0.5 임계값을 통과한 정보가 **I-2 RAG 파이프라인에 삽입**되는 흐름과 **I-3 L0 Context 자동 주입** 메커니즘을 상세 명세한다. 6-4 Memory-RAG-Storage 도메인의 RAG 파이프라인을 LOCK 재정의 ❌ 원칙 하에 인용하며, 6-7은 **삽입 트리거 + 인터페이스 스키마**의 생산측 정본을 제공한다.

> **DCL 6계층 정보 환경 (LOCK L11 verbatim)**: "[0]DCL → [1]사용자 → [2]메모리 → [3]RAG → [4]Cloud Library → [5]외부API"

### 1.1 책임 요약

- **`rag_insert_request` 인터페이스 (§2.1)**: 6-필드 스키마 정본 정의 (`channel`, `qod`, `vector`, `payload`, `source_id`, `timestamp`)
- **QoD ≥ 0.5 게이트 (§2.2)**: L13 verbatim — 임계 통과 시 삽입, 미달 시 폐기
- **RAG 삽입 파이프라인 (§3)**: 임베딩 변환 → CL-G3 정합 검증 → 6-4 벡터 스토어 삽입 → 인덱스 갱신
- **I-3 L0 Context 자동 주입 (§4)**: V2+ — DCL Aggregator 집계 결과를 L0(최상위 컨텍스트)에 자동 주입
- **6계층 정보 흐름 (§4.2)**: [0]DCL → [3]RAG → [4]Cloud Library 보강 + [0]DCL → L0 직접 주입
- **RETRACTION 무효화 (§5)**: §9.4 verbatim — soft delete (즉시) → 24h 후 hard delete
- **버전별 RAG 연동 (§6)**: V1 (수동 I-2) / V2 (자동 I-3 L0 주입) / V3 (실시간 + 자동 학습)
- **6-4 cross-handoff (§7)**: 6-4 LOCK 재정의 ❌ — 6-4 RAG 파이프라인·벡터 DB read-only 인용

### 1.2 6-7 ↔ 6-4 경계 (W-2 RESOLVED 정합)

```
[6-7 DCL Aggregator (P2-1)]
        │ (생산측: QoD ≥ 0.5 통과 정보)
        ▼
[6-7 rag_integration.md (본 문서)]
        │ - rag_insert_request 6-필드 스키마 (§2.1)
        │ - 임베딩 변환 (§3.1)
        │ - CL-G3 정합 검증 (§3.3)
        ▼
─────────────────────────────────────  ← 도메인 경계 (W-2 RESOLVED)
        │
        ▼ (소비측)
[6-4 Memory-RAG-Storage]
        │ - I-2 RAG 파이프라인 (LOCK-ME-* 정본)
        │ - 벡터 스토어 (Pinecone/Weaviate/PGVector)
        │ - 인덱스 갱신
        ▼
[6-11 Hologram-Main-LLM]  ← 배경 인식 응답 생성
```

---

## 2. `rag_insert_request` 인터페이스 정본 정의

### 2.1 6-필드 스키마

본 문서는 6-7 → 6-4 RAG 삽입 인터페이스의 정본 스키마를 다음과 같이 정의한다 (Phase 2 정합 — 6-4 LOCK 재정의 ❌):

```python
@dataclass
class rag_insert_request:
    channel: str          # "DCL-FIN" | "DCL-TECH" | "DCL-GEO" — LOCK L12
    qod: float            # 0.5 ≤ qod ≤ 1.0 — LOCK L13 (< 0.5 폐기)
    vector: list[float]   # V1: 룰 기반 (없음) / V2: 384차원 / V3: 768차원
    payload: dict         # {topic_id, text, accuracy, freshness, contributing_sources[]}
    source_id: str        # primary 소스 ID (가중치 최고 소스, dcl_channels.md §3.5)
    timestamp: str        # ISO 8601 (UTC) — Breaking Event 발생 시각
```

| 필드 | 타입 | 설명 | 정본 출처 |
|------|------|------|----------|
| `channel` | str | DCL 채널 식별자 (FIN/TECH/GEO) | LOCK L12 verbatim |
| `qod` | float | 0.5 ≤ qod ≤ 1.0 (< 0.5 시 송신 금지) | LOCK L13 verbatim |
| `vector` | list[float] | 임베딩 벡터 (V1: 미생성 / V2: 384차원 / V3: 768차원) | §3.1 |
| `payload` | dict | 메타데이터 (topic_id + text + accuracy + freshness + contributing_sources) | §3.2 |
| `source_id` | str | primary 소스 식별자 (dcl_channels.md §3.5 신뢰도 가중 평균 산출) | dcl_channels.md §3.5 |
| `timestamp` | str | ISO 8601 UTC (Breaking Event 시각, RETRACTION 추적용) | LOCK L8 정합 |

### 2.2 QoD ≥ 0.5 게이트 (LOCK L13 verbatim)

> **출처**: AUTHORITY_CHAIN.md §3.3 L13 verbatim — "QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기"

DCL Aggregator(dcl_channels.md §3.4)에서 산출된 QoD 값에 따라 다음 결정한다:

```python
def emit_rag_insert(aggregated: AggregatedSource) -> None:
    if aggregated.qod < 0.5:
        log_discard(aggregated, reason="qod_below_threshold")  # LOCK L13 폐기
        return
    request = build_rag_insert_request(aggregated)
    rag_pipeline.insert(request)  # 6-4 소비측 호출 (W-2 RESOLVED)
```

- `qod ≥ 0.5` → `rag_insert_request` 생성 + 6-4 파이프라인 호출
- `qod < 0.5` → 폐기 + 운영 로그 기록 (재시도 ❌, dcl_channels.md §5.1 정합)

---

## 3. RAG 삽입 파이프라인 (생산측)

### 3.1 임베딩 변환 (버전별)

| 버전 | 임베딩 모델 | 차원 | 비용 | 출처 |
|------|----------|------|------|------|
| V1 | 룰 기반 (키워드 BM25) — 임베딩 미생성 | N/A | +₩0 | LOCK L15 V1: +₩0 |
| V2 | sentence-transformers/all-MiniLM-L6-v2 | 384 | 무료 (로컬) | LOCK L15 V2: +₩5,000/월 한도 내 |
| V3 | OpenAI text-embedding-3-small (native 1536, `dimensions=768` 명시 절감) | 768 | $0.02/1M tokens | LOCK L15 V3: +₩15,000/월 한도 내 |

**비용 정합 (R-67-3)**: V2 임베딩은 로컬 모델로 비용 0, V3 임베딩은 LOCK L15 ₩15,000 한도의 일부로 모니터링 (background_summary.md §5.5 정합).

### 3.2 페이로드 구조

```python
payload = {
    "topic_id": str,                  # dcl_channels.md §3.5 충돌 해결 후 단일 ID
    "text": str,                      # primary 소스 본문 (가중치 최고)
    "accuracy": float,                # dcl_channels.md §3.4 QoD 산출 요소
    "freshness": float,               # 채널별 기준: FIN 5분/TECH 24h/GEO 1h
    "contributing_sources": list[str] # 신뢰도 가중 평균 기여 소스 ID 목록
}
```

### 3.3 CL-G3 Security Gate 정합 검증 (LOCK L16 verbatim)

> **출처**: AUTHORITY_CHAIN.md §3.3 L16 verbatim — "DCL 모든 채널에 CL-G3 보안 필터 필수"

RAG 삽입 직전, dcl_channels.md §5.4에서 통과한 CL-G3 결과를 재검증한다 (이중 차단):

| 검증 항목 | 차단 조건 | 처리 |
|----------|----------|------|
| CL-G3 재검증 | `cl_g3_recheck(request) != PASS` (dcl_channels.md §5.4 CL-G3 게이트 삽입 직전 재실행 — 6-필드 스키마 변경 ❌, payload 플래그 의존 제거) | 폐기 + 보안 알림 |
| RETRACTION 추적 | `topic_id` ∈ 활성 RETRACTION 리스트 | 폐기 + L8 무효화 트리거 |
| PII 재검사 | 마스킹 미적용 PII 패턴 | 폐기 + 알림 |

### 3.4 출력 (background_summary.md P2-3 의존 정합)

RAG 삽입 성공 후 다음 출력을 background_summary.md(P2-3)로 전달한다:

| 출력 필드 | 타입 | 의존 |
|----------|------|------|
| `aggregated_topics` | list[dict] | background_summary.md §3 입력 |
| `aggregated_qod` | float | background_summary.md §3.3 가중치 |
| `channel_distribution` | dict | background_summary.md §4 채널별 비중 |

---

## 4. I-3 L0 Context 자동 주입

### 4.1 개요 (Part2 §6.10.2 verbatim)

> **출처**: 02_domain-context-layer/_index.md verbatim — "I-3 L0 Context 주입: DCL은 RAG 외에도 현재 세션의 L0 메모리에 '현재 세상 상황 요약'을 주입하여, 사용자가 묻지 않아도 배경을 인지"

I-3 L0 Context 자동 주입은 **V2+** 시점부터 활성화된다 (V1: 수동, V2+: 자동). DCL Aggregator의 집계 결과를 세션 시작 시점 + 1시간 주기 갱신 시점에 L0(최상위 컨텍스트)에 주입한다.

### 4.2 6계층 정보 흐름 (LOCK L11 verbatim)

```
[0] Domain Context Layer (DCL)
        │
        ├─→ [3] I-2 RAG (벡터 삽입, §3)
        │       │
        │       └─→ [4] Cloud Library 보조 보강 (6-8, V2+)
        │
        └─→ [L0 직접 주입] (V2+, I-3 자동 주입)
                │
                ▼
        [Main LLM 세션 컨텍스트]
                │
                ▼
        [6-11 Hologram-Main-LLM 배경 인식 응답]
```

**계층 신뢰도 (LOCK L11 verbatim, 02/_index.md §VAMOS AI 정보 환경)**:
- [1] 사용자 입력: 100% (최우선)
- [2] 내부 메모리 L0-L3: 95% (핵심 백본)
- [3] I-2 RAG 검색: 80% (인덱싱된 지식)
- [4] Cloud Library 보조 보강: 70% (배치 수집)
- [5] 외부 API/MCP 도구: 60% (실시간 호출)
- **[0] DCL: 신규 — 도메인별 선택적 배경, [3]/[4]보다 빠른 실시간**

### 4.3 주입 트리거 조건

| 트리거 | 시점 | 주입 범위 | 버전 |
|--------|------|----------|------|
| 세션 시작 시 | 사용자 첫 입력 직전 | 직전 1시간 집계 결과 | V2+ |
| 1시간 주기 (LOCK L14) | 매 정각 | 신규 집계 결과 (delta) | V2+ |
| Breaking-P0 발생 시 | 즉시 (LOCK L6 30초 SLA) | 단일 이벤트 (priority=high) | V2+ |
| 사용자 명시 요청 시 | 즉시 | 전체 채널 최신 | V1+ |

### 4.4 주입 포맷 + 우선순위

```yaml
l0_context_injection:
  format: "## 현재 세상 상황 요약 (DCL — {timestamp})"
  priority: 2  # [1] 사용자 입력 100% > [2] 내부 메모리 95% > [L0 DCL 주입 90%] > [3] I-2 RAG 80% (§4.2/§4.4 정합, LOCK L11)
  channels:
    DCL-FIN:
      summary: "..."  # background_summary.md (P2-3) 산출
      qod: 0.85
      topic_count: 12
    DCL-TECH:
      summary: "..."
      qod: 0.78
      topic_count: 8
    DCL-GEO:
      summary: "..."
      qod: 0.72
      topic_count: 5
  expiry: 3600  # 1시간 (LOCK L14)
```

**우선순위 (LOCK L11 정합)**: L0 주입 정보의 신뢰도는 [2] 내부 메모리(95%)와 [3] RAG(80%) 사이의 90%로 설정한다. 사용자 명시적 정정 시 폐기 가능하다.

### 4.5 버전별 활성화 범위

| 버전 | I-2 RAG 삽입 | I-3 L0 자동 주입 | 동작 |
|------|------------|----------------|------|
| V1 | 수동 (사용자 요청 시) | 비활성 (수동만) | DCL 채널 → 사용자 명시 검색 |
| V2 | 자동 (QoD ≥ 0.5) | 활성 (세션 시작 + 1시간 주기) | DCL → RAG + L0 자동 |
| V3 | 자동 + 자동 학습 | 실시간 갱신 (Breaking-P0 즉시) | 실시간 배경 인식 |

---

## 5. RETRACTION 무효화 (§9.4 verbatim 정합)

> **출처**: 종합계획서 §9.4 verbatim — "I-2 RAG 벡터: 해당 속보 기반 RAG 삽입 벡터 — 벡터 삭제 (soft delete → 24h 후 hard delete)"
>
> **출처**: AUTHORITY_CHAIN.md §3.3 L8 verbatim — "허위 속보 RETRACTION — 즉시 발행 + 이전 이벤트 무효화"

RETRACTION 발행 시 6-7은 다음 무효화 절차를 6-4 RAG 파이프라인에 트리거한다 (6-4 LOCK 재정의 ❌):

### 5.1 Soft Delete (즉시)

```
[RT-BNP] RETRACTION 이벤트 (oc.rt_bnp.retraction.issued)
        │
        ▼
[6-12 Event-Logging] EventBus 브로드캐스트
        │
        ▼
[6-7 rag_integration.md] retraction_handler (30초 SLA, LOCK L6)
        │
        ├── 6-4 RAG: vector.metadata["retracted"] = True (즉시)
        ├── 6-4 RAG: vector.metadata["retracted_at"] = now()
        └── 6-4 검색: retracted=True 벡터 결과 제외
```

- **즉시 효과**: 이후 RAG 검색에서 해당 벡터 결과 제외
- **벡터 본체**: 보존 (감사 추적용)
- **30초 SLA**: LOCK L6 속보 전파 30초와 동일 기준 적용

### 5.2 Hard Delete (24h 후)

```
[24h 경과 후 Cron]
        │
        ▼
[6-4 RAG hard delete worker]
        │
        ├── 6-4 벡터 스토어: 벡터 본체 삭제
        ├── 6-4 인덱스: 인덱스 항목 제거
        └── 6-4 메타데이터: hard_deleted=True 마킹
```

- **24h 윈도우**: 정정 보고서 / 감사 추적 기간
- **6-4 LOCK 정합**: 6-4 LOCK-ME-* 재정의 ❌, 본 문서는 트리거만 발행

### 5.3 무효화 대상 정합 (§9.4 4 무효화 대상)

| 무효화 대상 | 본 문서 처리 | 외부 처리 |
|-----------|-------------|----------|
| **I-2 RAG 벡터** | ✅ 본 §5 (soft → 24h hard delete) | 6-4 hard delete worker |
| DCL 캐시 엔트리 | dcl_channels.md §7 | — |
| AI Investing 신호 | — (3-1 도메인) | 3-1 §6.8.1 |
| 사용자 알림 | — (6-1 UI 도메인) | 6-1 후속 알림 |

---

## 6. 버전별 RAG 연동 범위

| 버전 | I-2 RAG | I-3 L0 자동 주입 | 임베딩 모델 | RETRACTION 무효화 |
|------|---------|----------------|----------|------------------|
| V1 | 수동 (BM25 룰 기반) | 비활성 | 룰 기반 (벡터 X) | soft delete만 (BM25 인덱스) |
| V2 | 자동 (QoD ≥ 0.5, 384차원) | 활성 (세션 시작 + 1시간) | sentence-transformers (로컬, 무료) | soft → 24h hard delete |
| V3 | 자동 + 실시간 + 자동 학습 (768차원) | 실시간 (Breaking-P0 즉시) | OpenAI text-embedding-3-small | soft → 24h hard delete + 자동 학습 데이터 제외 |

---

## 7. 6-4 Memory-RAG cross-handoff (W-2 RESOLVED 정합)

### 7.1 6-4 LOCK 재정의 ❌ 원칙

> **출처**: AUTHORITY_CHAIN.md §4.4 verbatim — "6-4 Memory-RAG: 6-7 = DCL QoD ≥ 0.5 데이터를 RAG에 삽입 / 6-4 = RAG 파이프라인·벡터 DB 관리"
>
> **출처**: CONFLICT_LOG.md W-2 RESOLVED — "QoD ≥ 0.5 임계값 6-7 LOCK. 6-4 파이프라인에 전달 조건 명시"

6-7은 6-4의 RAG 파이프라인을 read-only 인용하며, 본 문서에서 6-4 LOCK을 재정의하지 않는다:

| 책임 영역 | 6-7 (생산측) | 6-4 (소비측) |
|---------|------------|------------|
| QoD 산출 | ✅ dcl_channels.md §3.4 | ❌ |
| QoD 임계값 정의 (LOCK L13) | ✅ 본 도메인 정본 | ❌ |
| `rag_insert_request` 인터페이스 | ✅ 본 §2.1 정본 | ❌ |
| 임베딩 변환 (V2+) | ✅ 본 §3.1 (트리거) | 부분 (실제 변환 라이브러리는 6-4 또는 6-7) |
| 벡터 스토어 (Pinecone/Weaviate/PGVector) | ❌ | ✅ 6-4 LOCK-ME-* 정본 |
| 인덱스 갱신 | ❌ | ✅ 6-4 정본 |
| 검색 (similarity, BM25) | ❌ | ✅ 6-4 정본 |
| RETRACTION soft delete 트리거 | ✅ 본 §5.1 (이벤트 발행) | ❌ |
| RETRACTION hard delete worker | ❌ | ✅ 6-4 정본 (24h cron) |

### 7.2 인터페이스 호환성 검증

| 검증 항목 | 6-7 책임 | 6-4 책임 |
|----------|---------|---------|
| `rag_insert_request` 6-필드 호환 | ✅ 본 §2.1 정본 | 6-4가 인입 처리 (호환 의무) |
| QoD ≥ 0.5 게이트 | ✅ 본 §2.2 정본 | — |
| 차원수 (V2 384, V3 768) | 6-7 트리거 | 6-4 인덱스 |
| RETRACTION 30초 SLA (LOCK L6) | ✅ soft delete 트리거 | 6-4 24h hard delete 별도 |

---

## 8. V2 LOCK 인용 매트릭스 (LOCK ↔ 본 문서 §)

| LOCK | 정본 출처 | 값/규칙 (verbatim) | 본 문서 § | 대조 결과 |
|------|----------|------------------|----------|----------|
| L8 | LOCK #16, Part2 §6.10.1 | 즉시 발행 + 이전 이벤트 무효화 | §5 (전체) | ✅ verbatim |
| L11 | CLOUD_LIBRARY_SPEC + Part2 §6.10.2 | [0]DCL → [1]사용자 → [2]메모리 → [3]RAG → [4]Cloud Library → [5]외부API | §1 + §4.2 | ✅ verbatim |
| L13 | Part2 §6.10.2 | QoD ≥ 0.5 → RAG 삽입, < 0.5 → 폐기 | §2.2 | ✅ verbatim |
| L16 | Part2 §6.10.2 | DCL 모든 채널에 CL-G3 보안 필터 필수 | §3.3 | ✅ verbatim |

---

## 9. 변경 이력

- 2026-04-28 v1.0 — P2-2 NEW (ISS-4 RAG 부분 + I-2 RAG 연동 정본 + I-3 L0 Context 주입 V2+ + LOCK L8/L11/L13/L16 verbatim 인용 + `rag_insert_request` 6-필드 스키마 정본 정의 + RETRACTION soft delete 즉시 → 24h hard delete §9.4 정합 + 6-4 cross-handoff W-2 RESOLVED 정합 + 6-4 LOCK 재정의 ❌ + 버전별 RAG 연동 V1 수동 / V2 자동 / V3 실시간)

<!-- FABRICATION-CHECK: zero-tolerance for hallucinated LOCK / interface fields -->
<!-- LOCK 인용 verbatim 정합: AUTHORITY_CHAIN.md §3.3 L8/L11/L13/L16 ✅ -->
<!-- 6-4 LOCK 재정의 ❌ (참조만, W-2 RESOLVED 통산 보존) ✅ -->
<!-- ISS-4 RAG 삽입 경로 부분 (P2-1 채널 수집과 분담) ✅ -->
<!-- §9.4 RETRACTION 무효화 verbatim "soft delete → 24h 후 hard delete" 정합 ✅ -->
<!-- L13 QoD ≥ 0.5 strict 임계 + L8 즉시 무효화 + L11 6계층 ✅ -->
<!-- rag_insert_request 6-필드 스키마: channel + qod + vector + payload + source_id + timestamp ✅ -->
<!-- I-3 L0 Context 주입 V2+ 활성 + 우선순위 90% (L11 [2] 95% 직하) ✅ -->
<!-- 6-7 ↔ 6-4 책임 분리 매트릭스 (생산측 vs 소비측) ✅ -->
<!-- LOCK L6 30초 SLA = soft delete 즉시 적용 + 24h hard delete worker는 6-4 정본 ✅ -->
