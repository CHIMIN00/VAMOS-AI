# Artifact Chunking — 대용량 아티팩트 분할 전송

> **도메인**: #11 Conversation-A2A (TIER3-DOMAIN-08)
> **서브폴더**: `01_a2a-protocol/`
> **V3 산출물**: P4-3 (Phase 4 #3, P2) — P3-3 forward-defined 정본 승급
> **작성일**: 2026-06-03
> **Status**: V3-Phase 4 APPROVED (production-ready)
> **상세명세 근거**: §2.1 JSON-RPC 메서드, §2.2 TaskArtifactEvent, §4.4 에러 코드 카탈로그
> **종합계획서 근거**: §6.1 구현 항목 #39 (Artifact Chunking), §7.3 P3-3 블록, §7.4 P4-3 블록
> **정본 위치 이동**: 원 04_advanced-features #39 → **01_a2a-protocol** (프로토콜 계층 정본, 04 _index 에 이동 주석)
> **LOCK 직접 보호**: LOCK-A2A-01 JSON-RPC 2.0 / LOCK-A2A-02 Task 상태 열거형
> **고유 규칙 직접 참조**: R-11-7 SSE 스트리밍 연결 타임아웃 300초

---

## 교차 참조

- `_index.md` — 01_a2a-protocol/ 항목 #9 Artifact Chunking (대용량 아티팩트 분할 전송 P2, Phase 3→4 APPROVED)
- `04_advanced-features/_index.md` — #39 Artifact Chunking 정본 위치 01_a2a-protocol 이동 주석 (영구 baseline)
- `04_advanced-features/streaming_sse.md` — §3.2 `artifact_chunk` 이벤트로 청크 전달, `last_chunk` 분할 (§3.2 향후 artifact_chunking 참조 실체화)
- `04_advanced-features/conversation_branching.md` — 분기 트리 스냅샷 64KB 초과 시 청크 전송 (P4-1 cross-ref)
- `task_lifecycle.md` — Task 상태 머신과 청크 전송 진행 정합
- `error_codes.md` — `-32001`~`-32005` 에러 카탈로그 정합
- `05_monitoring/vbs12_benchmark.md` — 시나리오 9 (청크 전송) 측정 대상 (P4-6 cross-ref)
- 상위 아키텍처 정본: `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md`
- 교차 도메인: 4-3★ MCP-Server-Client (대용량 도구 응답 청크 양방향, R-11-8 + CFL-A2A-002 RESOLVED), 6-12 Event-Logging (청크 이벤트 `a2a.artifact.chunk.*`)

---

## 1. 개요

### 1.1 목적

64KB 를 초과하는 대용량 아티팩트(코드 번들, 리뷰 문서, 데이터셋 등)를 **고정 크기 청크로 분할**하여 안정적으로 전송하고, 청크별·전체 SHA-256 해시로 무결성을 검증한다. JSON-RPC 2.0 (LOCK-A2A-01) `artifact.chunk` 메서드를 신규 정의하며, SSE 스트리밍(streaming_sse) 경로와 정합한다.

### 1.2 범위

- `artifact.chunk` 메서드 정의 (JSON-RPC 2.0 invariant 준수)
- 청크 분할 (64KB) + 청크별/전체 SHA-256
- 순차 전송 + 누락 청크 재요청 (missing_indices)
- 청크 손상 NACK 재전송
- 타임아웃 (300s, R-11-7) + cancel

### 1.3 범위 외 (Phase 5+ 이월)

- 청크 병렬 다중 스트림 전송 — 단일 스트림 안정화 후 검토
- 청크 압축(gzip/zstd) — 인프라 계층 결정 후 Phase 5
- 청크 재개(resumable upload) 영속 세션 — multi_turn_sessions 연계 후 검토

---

## 2. ArtifactChunk (Input Schema, D1)

### 2.1 method 정의

`artifact.chunk` 는 JSON-RPC 2.0 envelope 위에서 청크를 순차 전송한다. **LOCK-A2A-01 JSON-RPC 2.0 invariant** (`"jsonrpc": "2.0"`) 를 유지한다.

```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid",
  "method": "artifact.chunk",
  "params": {
    "artifact_id": "art-uuid",
    "chunk_index": 0,
    "total_chunks": 17,
    "payload_base64": "....",
    "chunk_hash_sha256": "ab12...",
    "mime_type": "text/markdown"
  }
}
```

### 2.2 Pydantic 모델

```python
from __future__ import annotations
from pydantic import BaseModel, Field


class ArtifactChunk(BaseModel):
    """artifact.chunk params. 64KB 고정 분할."""

    artifact_id: str
    chunk_index: int = Field(..., ge=0)
    total_chunks: int = Field(..., ge=1)
    payload_base64: str = Field(..., description="청크 페이로드 base64 (<= 64KB decoded)")
    chunk_hash_sha256: str = Field(..., min_length=64, max_length=64)
    mime_type: str = Field(default="application/octet-stream")
    overall_hash_sha256: str | None = Field(default=None, min_length=64, max_length=64, description="전체 artifact SHA-256. 마지막 청크(chunk_index == total_chunks-1)에 필수. 수신 측 expected_overall 원천.")
    overall_hash_sha256: str | None = Field(default=None, min_length=64, max_length=64, description="전체 artifact SHA-256. 마지막 청크(chunk_index == total_chunks-1)에 필수. 수신 측 expected_overall 원천.")
```

---

## 3. ChunkAck (Output Schema, D2)

```python
from typing import Literal


class ChunkAck(BaseModel):
    artifact_id: str
    received_index: int
    missing_indices: list[int] = Field(default_factory=list)
    overall_hash_status: Literal["pending", "ok", "mismatch"] = "pending"
```

- 수신 측은 각 청크 ACK 시 `received_index` 와 현재까지의 `missing_indices` 를 반환한다. 마지막 청크 수신 후 전체 재조립 해시를 검증하여 `overall_hash_status` 를 `ok` / `mismatch` 로 확정한다.
- 청크 전송 작업의 Task 상태는 **LOCK-A2A-02 열거형** (`submitted|working|input-required|completed|failed|canceled`) 을 따른다.

---

## 4. 청크 분할/재조립 알고리즘 (D3)

### 4.1 발신 측

```
def send_artifact(artifact_bytes, mime_type):
    overall_hash = sha256(artifact_bytes)
    chunks = split(artifact_bytes, size=64 * 1024)   # 64KB
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        send(ArtifactChunk(
            artifact_id=aid, chunk_index=i, total_chunks=total,
            payload_base64=b64(chunk), chunk_hash_sha256=sha256(chunk),
            mime_type=mime_type))
        ack = await_ack(timeout=300)                  # R-11-7 300s
        if ack.received_index != i:
            retransmit(ack.missing_indices)
    finalize(artifact_id=aid, overall_hash=overall_hash)
```

### 4.2 수신 측

```
def receive_chunk(chunk):
    if sha256(decode(chunk.payload_base64)) != chunk.chunk_hash_sha256:
        return NACK(chunk.chunk_index)               # 손상 → 재전송 요청
    store(chunk)
    missing = [j for j in range(chunk.total_chunks) if j not in received]
    if not missing:
        reassembled = concat(received)
        status = "ok" if sha256(reassembled) == expected_overall else "mismatch"
        return ChunkAck(..., overall_hash_status=status)
    return ChunkAck(..., missing_indices=missing)
```

- **무결성 2단 검증**: 청크별 `chunk_hash_sha256` (전송 손상 즉시 탐지) + 전체 재조립 `overall_hash` (순서·누락 종합 검증).

---

## 5. 에러 처리 (D4)

| 코드 | 상황 | 복구 |
|------|------|------|
| NACK (`-32034` 비표준) | chunk_hash 불일치 (청크 손상) | 해당 chunk_index 재전송 |
| `-32035` (비표준) | 누락 청크 (missing_indices 비어있지 않음) | missing_indices 재요청 |
| `-32036` (비표준) | timeout 300s (R-11-7) | 전송 cancel, 클라이언트 재시작 |
| `-32602` | invalid params (chunk_index ≥ total_chunks) | 400 |
| overall mismatch | 전체 해시 불일치 | 전체 재전송 (artifact 무효화) |

```json
{
  "trace_id": "trace-uuid",
  "error": { "code": "-32034", "message": "Chunk hash mismatch", "source": "artifact_chunking.verify" },
  "context": { "artifact_id": "art-uuid", "chunk_index": 5, "total_chunks": 17 },
  "recovery": { "strategy": "retransmit_chunk", "chunk_index": 5 }
}
```

---

## 6. 의존성 (D5)

| 대상 | 방향 | 내용 |
|------|------|------|
| `04_advanced-features/streaming_sse.md` | ← (소비) | SSE `artifact_chunk` 이벤트 전송 |
| base64 encoder | → | 청크 페이로드 인코딩 |
| SHA-256 | → | 청크별/전체 해시 |
| `04_advanced-features/conversation_branching.md` | ← (제공) | 분기 트리 스냅샷 청크 전송 |

---

## 7. 성능 SLA (D6)

| 메트릭 | 목표 | 측정 |
|--------|------|------|
| 1MB artifact 전송 P99 | < 1s | vbs12_benchmark 시나리오 9 |
| throughput | ≥ 10MB/s | metrics_dashboard |
| 청크 크기 | 64KB 고정 | 분할 규칙 |
| timeout | 300s (R-11-7) | SSE 정합 |

- 1MB = 16 청크 (64KB), 청크별 ACK 왕복 + 재조립 검증 포함 P99 < 1s.

---

## 8. 테스트 시나리오 (D7, AC-T01~T12)

| # | 시나리오 | 주입 | 기대 결과 |
|---|----------|------|----------|
| AC-T01 | 정상 청크 (1MB) | 16 청크 순차 | overall_hash_status=ok |
| AC-T02 | 청크 손상 NACK | 1개 청크 비트 변조 | NACK → 해당 청크 재전송 → ok |
| AC-T03 | 누락 청크 재전송 | 청크 5 누락 | missing_indices=[5] → 재요청 → ok |
| AC-T04 | 대용량 100MB | 1600 청크 | throughput ≥ 10MB/s |
| AC-T05 | SSE 타임아웃 | 300s 초과 idle | `-32001` cancel |
| AC-T06 | overall mismatch | 순서 뒤섞임 | overall_hash_status=mismatch → 전체 재전송 |
| AC-T07 | invalid chunk_index | index ≥ total | `-32602` 400 |
| AC-T08 | 분기 스냅샷 청크 | conversation_branching snapshot >64KB | 청크 분할 전송 (P4-1 연계) |
| AC-T09 | RBAC artifact 접근 | VIEWER 다운로드 | 권한 검증 통과 (조회 허용) |
| AC-T10 | RBAC 쓰기 거부 | VIEWER 업로드 | `-32600` 403 |
| AC-T11 | mime_type 검증 | 미지원 타입 | `-32005` 폴백 |
| AC-T12 | MCP 대용량 응답 | 4-3 도구 응답 청크 | 양방향 청크 정합 (R-11-8) |

---

## 9. 보안 / RBAC (D8)

- **hash 검증**: 모든 청크는 SHA-256 으로 무결성을 검증하며, 위변조 청크는 NACK 으로 거부된다.
- **RBAC artifact 접근 권한**: artifact 다운로드(조회)는 VIEWER 이상, 업로드(쓰기)는 EDITOR 이상으로 제한한다.
- 청크 전송 시작/완료/실패는 `03_security/audit_logging.md` 에 기록한다.
- 4-3 MCP-Server-Client 와의 대용량 도구 응답 청크 전송은 #16 정본 스키마(R-11-8)를 참조하며, A2A 측은 위임 인터페이스만 정의한다 (CFL-A2A-002 RESOLVED).

---

## 10. LOCK 인용 표 (5필드 분리 강제)

| LOCK ID | 항목 | 값 | 출처 | 변경 조건 |
|---------|------|-----|------|----------|
| LOCK-A2A-01 | JSON-RPC 2.0 프로토콜 버전 | `"jsonrpc": "2.0"` | Google A2A Spec | 스펙 업데이트 시 검토 |
| LOCK-A2A-02 | Task 상태 열거형 | `submitted\|working\|input-required\|completed\|failed\|canceled` | Google A2A Spec | 스펙 업데이트 시 검토 |

**고유 규칙**: R-11-7 SSE 스트리밍 연결 타임아웃 300초 (종합계획서 §4.3 정본) — §4.1/§7 적용.

- LOCK-A2A-01 적용 위치: §2.1 method envelope
- LOCK-A2A-02 적용 위치: §3 청크 전송 Task 상태

> **R2/R9 준수**: LOCK 값은 AUTHORITY_CHAIN.md §3 정본 verbatim. 청크 메서드 신설은 JSON-RPC 2.0 invariant 위에서 이루어지며 프로토콜 버전을 변경하지 않는다.

---

## 11. 세션 간 인터페이스 cross-check

| 항목 | 대상 산출물 | 일치 항목 |
|------|------------|----------|
| `artifact_chunk` 이벤트 | `04_advanced-features/streaming_sse.md` §3.2 | `last_chunk` 분할 |
| 분기 스냅샷 청크 | `conversation_branching.md` | snapshot >64KB |
| Task 상태 | `task_lifecycle.md` | LOCK-A2A-02 |
| 에러 코드 | `error_codes.md` | 표준 `-32005`/`-32602`/`-32600` 정합 + 비표준 확장 `-32034`/`-32035`/`-32036` (청크 전용, 카탈로그 -32001~-32008 와 비충돌) |
| 청크 측정 | `05_monitoring/vbs12_benchmark.md` | 시나리오 9 |

---

## 12. 변경 이력

| 날짜 | 변경자 | 내용 |
|------|--------|------|
| 2026-06-03 | Phase 4 RECOVERY (genuine write) | V3-Phase 4 NEW 최초 작성 (P4-3, P3-3 forward-defined 정본 승급). D1~D8 8섹션 + `artifact.chunk` 메서드 + 64KB 분할 + 2단 SHA-256 + NACK 재전송 + missing_indices. 정본 위치 01_a2a-protocol 이동(04 _index 주석). Status DRAFT→APPROVED. LOCK-A2A-01/02 verbatim + R-11-7. SPEC Stage B verify-only 착시(phase4_v3_p4-3_promotion_report) genuine write 해소. |

---

**[END OF artifact_chunking.md V3 — Phase 4 APPROVED, 2026-06-03]**
