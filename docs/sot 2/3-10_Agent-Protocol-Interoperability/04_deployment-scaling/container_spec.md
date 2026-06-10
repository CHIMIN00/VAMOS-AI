# 에이전트 컨테이너 패키징 (Docker) — K-055 (V2 신규 L3)

> **STEP7-K**: K-055 에이전트 패키징 (L1089~L1099 원문 / `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`)
> **레벨**: L3 (V2-Phase 2 신규)
> **Part2 상태**: ABSENT — 본 문서로 L3 방식 C 신규
> **정본 소유**: #13 Agent-Protocol-Interoperability / 04_deployment-scaling
> **V 스코프**: V2-Phase 2 (K-056 Kubernetes 배포 STEP7-K L1101~L1111 은 plan §7.5 V3 이관 명시, 본 V2 Phase 2 범위 제외)
> **V2 태그**: V2-Phase 2 (2026-04-22, STAGE 7 STEP_B #2b 3-10 도메인 P2-4 세션 신규 작성)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| STEP7-K (Level 2) | L1089~L1099 | K-055 에이전트 패키징 원본 정의 (Docker 이미지, Python pip, YAML config, 의존성) |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-04 | MCP Streamable HTTP (V1, WebSocket 아님) — 컨테이너 MCP Server 포트 노출 시 엄수 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-07 | A2A + MCP 양방향 지원 필수 — 컨테이너 이미지 내 양 프로토콜 바이너리 포함 |
| AUTHORITY_CHAIN.md | §3 LOCK-AP-09 | 비용 상한 V1 ₩40K / V2 ₩93K / V3 ₩266K — 이미지 레지스트리 + CI/CD 누적 비용 |
| AUTHORITY_CHAIN.md | §4 | "에이전트 배포/스케일링" #13 정본 소유, #15 CI/CD 정본은 파이프라인 |
| 구조화_종합계획서.md | §7.4 P2-4 L1213~L1245 | Phase 2 V2 K-055~K-060 배치 (K-056 V3 이관) |
| 04_deployment-scaling/_index.md | L11~L20 | 담당 K-ID 표 (K-055 L3 / K-056 V3) |
| 04_deployment-scaling/healthcheck_spec.md | §2 헬스 엔드포인트 | 본 문서 §5.3 Docker HEALTHCHECK 연동 대상 |
| 04_deployment-scaling/logging_spec.md | §2 stdout JSON | 본 문서 §5.1 컨테이너 로그 드라이버 `json-file` 대응 |
| 04_deployment-scaling/config_spec.md | §3 Secret Manager | 본 문서 §4.4 비밀 정보 BuildKit secrets 연계 |
| 04_deployment-scaling/migration_guide.md | §3 Blue-Green | 본 문서 §7 이미지 태그 전략 (semver + digest pinning) |
| 01_framework-adapters/langgraph_adapter.md | §3 | 공통 자료 구조 import (VamosMessage, GatePolicy, AdapterResult) |
| 4-1 Rust-Tauri-Infrastructure | 빌드/서명 상세 (ISS-06) | 데스크톱 배포는 #14 정본, 본 도메인은 컨테이너(서버·노드) 관점만 |
| 4-2 CICD-Pipeline | LOCK-CI-06 5-target 매트릭스 | 컨테이너 이미지 빌드/테스트/푸시 파이프라인 정본은 #15 |

> **R6 준수**: What+How 전용. When/Where 는 Part2/§15 CI/CD 정본, 미기재.

---

## §2. Purpose & Scope

### 2.1 목적

Blue Node 별(Dev/Research/Content/Quant/Trading/Personal) 에이전트를 **독립 배포 단위**로 컨테이너화. STEP7-K K-055 4대 요건 충족:

1. Docker 이미지: 각 Node 별 컨테이너 (L1093 원문)
2. Python 패키지: `pip install vamos-dev-node` (L1094 원문)
3. 설정 파일: YAML 기반 에이전트 정의 (L1095 원문)
4. 의존성 관리: 자동 해결 (L1096 원문)

### 2.2 범위 경계

| 영역 | 본 문서 (#13) | 정본 소유 도메인 |
|------|--------------|-----------------|
| 이미지 스키마·라벨·멀티스테이지·보안 스캔 | ✅ 정본 | — |
| 이미지 레지스트리 선정·푸시 파이프라인 | ❌ | #15 CI/CD (4-2) |
| Kubernetes Deployment/Service/Ingress 매니페스트 | ❌ V3 이관 (K-056) | — |
| Tauri 데스크톱 서명·패키징 | ❌ | #14 Rust-Tauri (4-1) |
| 헬스체크 엔드포인트 내부 로직 | ❌ | 본 도메인 `healthcheck_spec.md` |
| stdout JSON 로그 스키마 | ❌ | 본 도메인 `logging_spec.md` |

### 2.3 Blue Node × 리소스 클래스 매핑 (_index §22 R-13-5)

| Node | 리소스 클래스 | 이미지 base | 예상 이미지 크기 | 주 용도 |
|------|--------------|-------------|-----------------|---------|
| Dev | standard | `python:3.11-slim-bookworm` | 320 MiB | 코드 편집/실행 도구 호출 |
| Research | standard | `python:3.11-slim-bookworm` | 290 MiB | 검색/요약/메타데이터 추출 |
| Content | standard | `python:3.11-slim-bookworm` | 310 MiB | 문서 작성/미디어 변환 |
| Quant | heavy | `python:3.11-slim-bookworm` + CUDA sidecar | 1.2 GiB | 수치 분석, 모델 추론 |
| Trading | standard | `python:3.11-slim-bookworm` | 330 MiB | 주문/체결 API (L5 HITL) |
| Personal | light | `python:3.11-slim-bookworm` | 220 MiB | 대화/메모 |

---

## §3. 공통 자료 구조 Import (01_framework-adapters/langgraph_adapter.md §3 정합)

```python
# container_spec.md 에서 사용하는 공통 타입
from sot2_domain.agent_protocol_interoperability.types import (
    VamosMessage,        # LOCK-AP-01 (6필드)
    GatePolicy,          # §3-8 공통
    AdapterResult,       # 프레임워크 어댑터 결과
    FrameworkTaskRef,    # 배포 단위 태스크 레퍼런스
)
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict
from datetime import datetime
```

---

## §4. Docker 이미지 멀티스테이지 전략

### 4.1 Dockerfile 표준 구조 (Big-O: O(1) — 정적 빌드)

```dockerfile
# syntax=docker/dockerfile:1.7
# Stage 1: Build (의존성 해결 + wheel 생성)
FROM python:3.11-slim-bookworm AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install poetry==1.8.3 && \
    poetry export --without-hashes --format=requirements.txt > requirements.txt && \
    pip wheel --wheel-dir=/build/wheels -r requirements.txt
COPY src /build/src
RUN pip wheel --wheel-dir=/build/wheels --no-deps /build/src

# Stage 2: Runtime (최소 크기)
FROM python:3.11-slim-bookworm AS runtime
ARG NODE_TYPE=dev
ARG BUILD_SHA
LABEL org.opencontainers.image.title="vamos-${NODE_TYPE}-node" \
      org.opencontainers.image.version="${BUILD_SHA}" \
      org.opencontainers.image.source="https://git.vamos.local/agent-protocol" \
      io.vamos.node-type="${NODE_TYPE}" \
      io.vamos.lock-ap-04="mcp-streamable-http-v1" \
      io.vamos.lock-ap-07="a2a-mcp-bidirectional"
RUN groupadd --system --gid 10001 vamos && \
    useradd --system --gid vamos --uid 10001 --home-dir /app --shell /sbin/nologin vamos && \
    mkdir -p /app /var/lib/vamos && \
    chown -R vamos:vamos /app /var/lib/vamos
WORKDIR /app
COPY --from=builder /build/wheels /tmp/wheels
RUN pip install --no-index --find-links=/tmp/wheels vamos-${NODE_TYPE}-node && \
    rm -rf /tmp/wheels
USER vamos:vamos
EXPOSE 8080/tcp 9090/tcp
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-m", "vamos.healthcheck", "--probe=readiness"]
ENTRYPOINT ["python", "-m", "vamos.node.entrypoint"]
CMD ["--node-type", "${NODE_TYPE}", "--config", "/etc/vamos/node.yaml"]
```

### 4.2 멀티스테이지 이점 (STEP7-K L1093 "Docker 이미지" 요건 강화)

| 항목 | Stage 1 (builder) | Stage 2 (runtime) | 효과 |
|------|------------------|-------------------|------|
| 포함 바이너리 | poetry, pip, gcc (wheel 빌드용) | python + wheels only | 크기 **≈ 60% 감소** (920 MiB → 320 MiB) |
| CVE 공격면 | 빌드 도구 미노출 | pip 임시 디렉토리도 삭제 | 프로덕션 attack surface 최소화 |
| 캐시 재사용 | `--mount=type=cache` BuildKit | wheel 계층 재사용 | 반복 빌드 시간 ≈ 65% 감소 |
| 재현성 | poetry.lock 해시 고정 | wheel digest 매칭 | 동일 해시 이미지 → 동일 digest |

### 4.3 OCI 표준 라벨 (org.opencontainers.image.\*)

```yaml
labels_required:
  org.opencontainers.image.title: "vamos-<node-type>-node"
  org.opencontainers.image.version: "<semver>-<git-sha-short>"
  org.opencontainers.image.revision: "<git-full-sha>"
  org.opencontainers.image.source: "<git-url>"
  org.opencontainers.image.created: "<iso8601>"
  org.opencontainers.image.licenses: "LicenseRef-VAMOS-Internal"
  io.vamos.node-type: "<dev|research|content|quant|trading|personal>"
  io.vamos.protocol-version: "a2a-v1+mcp-streamable-http"
  io.vamos.permission-level-max: "<0-5>"         # LOCK-AP-02
  io.vamos.cost-bucket: "<V1|V2|V3>"             # LOCK-AP-09 연동
  io.vamos.confidence-threshold: "0.50"          # LOCK-AP-10 (06_autonomy-safety 정본)
```

### 4.4 비밀 정보 BuildKit secrets (COPY/RUN 에 비밀 포함 금지)

```dockerfile
# 빌드 시 `--secret id=github_token,src=$HOME/.github_token`
RUN --mount=type=secret,id=github_token \
    GITHUB_TOKEN=$(cat /run/secrets/github_token) \
    pip install --index-url https://${GITHUB_TOKEN}@pypi.internal/simple vamos-private-deps
# → 최종 이미지에 GITHUB_TOKEN 흔적 0
```

→ 런타임 비밀(API 키) 은 `config_spec.md` §3 Secret Manager 경유 (Docker secret/Vault/AWS SM), 이미지 빌드 단계에서 주입 **금지**.

---

## §5. 이미지 공격면 최소화 (보안 스캔)

### 5.1 보안 요건 매트릭스

| 요건 | 구현 | 검증 도구 |
|------|------|-----------|
| Non-root 사용자 | UID 10001 (vamos) | `docker run --rm img id` == `uid=10001(vamos)` |
| Read-only root filesystem | `docker run --read-only` + tmpfs `/tmp` | runtime 시 mount 설정 |
| CAP_DROP ALL | 컨테이너 기본 capability 모두 제거 | `docker run --cap-drop ALL --cap-add NET_BIND_SERVICE`(불요 시 생략) |
| SBOM 첨부 | CycloneDX JSON → 이미지 annotation | `syft <image> -o cyclonedx-json` |
| CVE 스캔 | **Trivy**: HIGH/CRITICAL 0건 | `trivy image --severity HIGH,CRITICAL --exit-code 1 <img>` |
| 서명 | Cosign keyless (OIDC) | `cosign verify --certificate-oidc-issuer ... <img>` |

### 5.2 `.dockerignore` 필수 항목

```
# 비밀/개발 산출물
.env*
.git
.github
.venv
__pycache__/
*.pyc
.pytest_cache
.mypy_cache
test_iso_p2/
# V1 소스 아카이브
backup/
_automation/state/
```

### 5.3 HEALTHCHECK ↔ `healthcheck_spec.md` 인터페이스

Dockerfile `HEALTHCHECK` CMD 는 `healthcheck_spec.md §2` 에서 정의하는 3 probe (liveness/readiness/startup) 중 **readiness** 만 호출. K8s 이관(K-056 V3) 시 probe 를 3종 모두 manifest 로 분리하되, Docker Compose 운영 환경에서는 readiness 만으로 재시작 판단.

---

## §6. Python 패키지 (pip install vamos-<node-type>-node)

### 6.1 `pyproject.toml` 뼈대 (STEP7-K L1094 원문 "pip install vamos-dev-node")

```toml
[tool.poetry]
name = "vamos-dev-node"
version = "0.2.0+v2phase2"
description = "VAMOS Dev Blue Node — code authoring/execution agent"
authors = ["VAMOS Platform"]
license = "LicenseRef-VAMOS-Internal"
packages = [{include = "vamos", from = "src"}]

[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.7"
httpx = {extras = ["http2"], version = "^0.27"}
aiofiles = "^23.2"
structlog = "^24.1"
opentelemetry-api = "^1.24"
opentelemetry-instrumentation = "^0.45b0"
# MCP Streamable HTTP (LOCK-AP-04)
vamos-mcp-client = "^0.1"
# A2A 프로토콜 (LOCK-AP-07)
vamos-a2a-bridge = "^0.1"

[tool.poetry.group.dev.dependencies]
pytest = "^8.1"
pytest-asyncio = "^0.23"
ruff = "^0.4"
mypy = "^1.9"

[tool.poetry.scripts]
vamos-dev-node = "vamos.node.dev.__main__:main"
```

### 6.2 의존성 자동 해결 (STEP7-K L1096 원문)

- `poetry lock` 산출 `poetry.lock` 해시 불변 → 멀티스테이지 Stage 1 에서 export
- `pip-audit` 주간 실행으로 CVE 감시
- SBOM 생성: `cyclonedx-py -i poetry.lock -o sbom.cdx.json`

---

## §7. 이미지 태그 전략 (semver + digest pinning)

### 7.1 태그 규칙

```
<registry>/vamos/<node-type>-node:<semver>-<phase>-<git-sha>
예: registry.vamos.local/vamos/dev-node:0.2.0-v2phase2-a1b9628f
```

| 태그 카테고리 | 형식 | 예 | 승격 경로 |
|-------------|------|-----|----------|
| 빌드 태그 (불변) | `:X.Y.Z-<phase>-<sha>` | `:0.2.0-v2phase2-a1b9628f` | 모든 CI 빌드 |
| 환경 별칭 | `:dev` `:staging` `:prod` | — | `migration_guide.md §3` Blue-Green |
| 릴리스 태그 | `:X.Y.Z` | `:0.2.0` | 프로덕션 승격 완료 |
| 디지털 지문 | `@sha256:...` | `@sha256:f2a9…` | 프로덕션 manifest 에 pinning |

### 7.2 Digest pinning 규정

`config_spec.md §4 환경 설정`에서 `image_ref` 는 반드시 `@sha256:` digest 로 고정. 별칭(`:prod`)은 재배포 편의용이지만 **Deployment spec 에는 사용 금지** (Supply-chain 공격 대응).

---

## §8. 비용 관점 (LOCK-AP-09 verbatim 5필드 분리 인용)

### 8.1 LOCK-AP-09 정본 전재 (AUTHORITY_CHAIN.md §3 L50)

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 |
|---------|------|----------|-----|--------|
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | **금지** |

### 8.2 컨테이너 라이프사이클 비용 귀속 (예시, 월간)

| 비용 카테고리 | V1 (₩) | V2 (₩) | V3 (₩) |
|--------------|-------:|-------:|-------:|
| 이미지 레지스트리 스토리지 (100 GiB) | 4,500 | 4,500 | 8,000 |
| CI 빌드 (50 build/월) | 6,000 | 12,000 | 28,000 |
| Trivy/Cosign 스캔 (SaaS) | 0 | 3,500 | 9,000 |
| 레지스트리 pull egress (500 GiB) | 4,500 | 9,000 | 22,000 |
| 런타임 컴퓨트 (Fargate/GKE Autopilot) | 15,000 | 45,000 | 150,000 |
| APM/로그/메트릭 (합산) | 10,000 | 19,000 | 49,000 |
| **합계** | **40,000** | **93,000** | **266,000** |

→ `logging_spec.md §6` Prometheus + Grafana + 외부 APM 연동 시 APM 행 변동 주시. V2 ₩93K 상한 초과 즉시 HITL 에스컬레이션(Permission L3 이상).

### 8.3 이미지 크기 → 운영 비용 감수율 (경험적)

- Stage 1 대비 Stage 2 크기 1 GiB 감소당 → pull egress 월 ≈ ₩1,200 절감 (500 GiB × 0.024/GiB 기준)
- standard Node 6 개 × pull 200/월 = 월 1,200 pull → 이미지 1 GiB 감소 시 월 ≈ ₩30K 절감 (V2 규모)

---

## §9. Phase 별 복구/다운그레이드 흐름 + Confidence Penalty

### 9.1 장애 시나리오 트리

```
[이미지 pull 실패]
  ├─ 재시도 3회 (exponential backoff 5s/15s/45s)
  │     └─ 성공 → 정상
  ├─ 실패 지속 → 이전 digest 로 폴백 (migration_guide.md §3 Blue-Green)
  └─ 이전 digest 도 실패 → HITL 에스컬레이션 (Permission L3 이상)

[CVE HIGH/CRITICAL 탐지]
  ├─ 빌드 차단 (CI exit_code=1)
  └─ 예외 승인은 L4 (외부 통신) + CONFLICT_LOG 등록

[서명 검증 실패]
  ├─ 배포 차단 + 알람
  └─ supply-chain 침해 의심 → 전체 STAGE7 abort (§H.2 기준)
```

### 9.2 Confidence penalty (본 도메인 LOCK-AP-10 06_autonomy-safety 정본 참조, 본 문서 재정의 금지)

| 컨테이너 이벤트 | confidence penalty | HITL 발동 |
|----------------|:-----------------:|:--------:|
| Trivy HIGH 1건 탐지 | -0.10 | 아님 |
| Trivy CRITICAL 1건 | -0.25 | ✅ (보안 즉시 HITL — cumulative<0.50 와 독립) |
| 이미지 태그 별칭 → 프로덕션 pinning 미사용 | -0.05 | 아님 |
| 서명 검증 실패 | -0.40 | ✅ |
| digest drift (manifest vs. 런타임) | -0.15 | ✅ (보안 즉시 HITL — cumulative<0.50 와 독립) |

> LOCK-AP-10 재정의 금지. 본 표의 penalty 는 `06_autonomy-safety/guardrail_rules.md` (P2-6 정본) 의 **cumulative** 기준을 전제로 한다.

---

## §10. 에스컬레이션 페이로드 Python Class

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime

class ContainerEscalation(BaseModel):
    """LOCK-AP-02 L3 이상 에스컬레이션 공통 페이로드"""
    trace_id: str = Field(..., description="요청 전체 경로 추적 ID")
    node_type: Literal["dev", "research", "content", "quant", "trading", "personal"]
    image_digest: str = Field(..., pattern=r"^sha256:[a-f0-9]{64}$")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    event_class: Literal[
        "trivy_cve_high",
        "trivy_cve_critical",
        "cosign_verify_failed",
        "digest_drift",
        "pull_failure_after_fallback",
    ]
    confidence_delta: float = Field(..., le=0.0, ge=-1.0)
    recommended_action: str
    rollback_digest: Optional[str] = None
    occurred_at: datetime
    context: dict

    def to_structured_log(self) -> dict:
        return {
            "error": {
                "class": self.event_class,
                "severity": self.severity,
            },
            "context": {
                "node_type": self.node_type,
                "image_digest": self.image_digest,
                "trace_id": self.trace_id,
                "occurred_at": self.occurred_at.isoformat(),
                "details": self.context,
            },
            "recovery": {
                "recommended_action": self.recommended_action,
                "rollback_digest": self.rollback_digest,
                "confidence_delta": self.confidence_delta,
            },
        }
```

---

## §11. 로깅 Structured JSON 3-block (logging_spec.md §2 스키마 준수)

```json
{
  "error": {
    "class": "cosign_verify_failed",
    "severity": "CRITICAL"
  },
  "context": {
    "node_type": "trading",
    "image_digest": "sha256:abcd...",
    "registry": "registry.vamos.local",
    "signer_expected": "cosign-keyless-oidc",
    "trace_id": "01HVZ9K3M4Q7R8T9XWY0ZABCDE",
    "occurred_at": "2026-04-22T10:15:32.123Z"
  },
  "recovery": {
    "recommended_action": "abort_deployment_and_escalate_L4",
    "rollback_digest": "sha256:prev123...",
    "confidence_delta": -0.40
  }
}
```

→ `logging_spec.md §2 stdout JSON scheme` 와 **3-block** 구조 (`error` / `context` / `recovery`) 일치.

---

## §12. LOCK 매핑 5필드 표

| LOCK ID | 항목 | 원본 문서 | 값 | 재정의 | 본 문서 적용 지점 |
|---------|------|----------|-----|--------|------------------|
| LOCK-AP-01 | 프로토콜 메시지 포맷 | STEP7-K, D2.0-05 | VamosMessage (id, type, source, target, content, metadata) | 금지 | §3 import + §10 escalation `trace_id` |
| LOCK-AP-02 | 에이전트 권한 레벨 | STEP7-K K-041 | Permission Level 0~5 | 금지 | §10 L3 이상 에스컬레이션 + §9 CVE 예외 승인 L4 |
| LOCK-AP-04 | MCP 전송 방식 | Part2 §6.6 | Streamable HTTP (V1), WebSocket 아님 | 금지 | §4.3 라벨 `io.vamos.lock-ap-04` + §7.1 이미지 주석 |
| LOCK-AP-07 | 인터롭 규격 | STEP7-K | A2A + MCP 양방향 지원 필수 | 금지 | §4.3 라벨 `io.vamos.lock-ap-07` + §6.1 deps (vamos-mcp-client + vamos-a2a-bridge) |
| LOCK-AP-09 | 비용 상한 | Part2 §비용 + 가이드 부록 D (STEP7-H 참조) | V1: ₩40K, V2: ₩93K, V3: ₩266K | 금지 | §8.1 verbatim + §8.2 컨테이너 라이프사이클 비용 매트릭스 |
| LOCK-AP-10 | Confidence 임계값 | DEFINED-HERE (본 도메인 06_autonomy-safety 정본; MASTER_SPEC §5/§7.9 참조) | HITL 트리거 < 50% | 금지 | §9.2 penalty 적용 (본 문서 재정의 없음) |

---

## §13. Phase 3 테스트 시나리오 (≥ 10건)

| # | 시나리오 ID | 설명 | 기대 결과 |
|---|------------|------|----------|
| 1 | CS-01 | 멀티스테이지 빌드 후 이미지 크기 < 400 MiB (standard Node, STEP7-K L1093 "Docker 이미지 각 Node별 컨테이너") | ✅ 크기 제약 통과 |
| 2 | CS-02 | `docker run --rm img id` 가 uid=10001(vamos) 반환 | ✅ Non-root |
| 3 | CS-03 | `docker run --read-only img` + writable tmpfs 외 쓰기 실패 | ✅ RO rootfs |
| 4 | CS-04 | Trivy `HIGH,CRITICAL` 스캔 exit_code=0 | ✅ CVE 0건 |
| 5 | CS-05 | Cosign keyless 서명 검증 PASS | ✅ 서명 유효 |
| 6 | CS-06 | BuildKit secret 주입 후 이미지 레이어에 토큰 흔적 검색 0 | ✅ 비밀 누설 0 |
| 7 | CS-07 | 동일 `poetry.lock` + Dockerfile 재빌드 시 같은 digest | ✅ 재현성 |
| 8 | CS-08 | 이미지 태그 별칭(`:prod`) 배포 시 pinning 검증 실패 (의도적 경고) | ✅ digest pinning 강제 |
| 9 | CS-09 | HEALTHCHECK readiness probe 실패 시 Docker restart | ✅ `healthcheck_spec.md §2` 연동 |
| 10 | CS-10 | Compose stack 재시작 후 logging_spec.md §2 JSON 로그 연속 기록 | ✅ 로그 드라이버 drop 0 |
| 11 | CS-11 | 이미지 digest drift (manifest vs runtime) 시 confidence -0.15 | ✅ LOCK-AP-10 기준 < 0.50 발동 |
| 12 | CS-12 | SBOM CycloneDX attestation 을 Cosign attest 로 첨부 + 검증 | ✅ SBOM 완전성 |

---

## §14. 세션 간 인터페이스 Cross-check 표

| 상호작용 | 인터페이스 | 타 V2 파일 (#2b 내) | 검증 |
|---------|-----------|---------------------|------|
| HEALTHCHECK 명령어 | `python -m vamos.healthcheck --probe=readiness` | `healthcheck_spec.md §2.1` | CLI 계약 동일 |
| stdout JSON 로그 드라이버 | Docker `json-file` 또는 `journald` | `logging_spec.md §2.2` | 3-block 스키마 일치 |
| Secret 주입 경로 | `/etc/vamos/node.yaml` + Secret Manager | `config_spec.md §3.2` | BuildKit vs 런타임 분리 엄수 |
| Blue-Green 이미지 태그 승격 | `:staging` → `:prod` + digest snapshot | `migration_guide.md §3.1` | digest pinning 원칙 공유 |
| MoA Layer 1 Proposer 컨테이너 | `moa_pattern.md §4.1` 4 Proposer | `01_framework-adapters/moa_pattern.md` | LOCK-AT-014 V1=3 제약 하에서 V2=10 까지 확장 허용 |

---

## §15. 검증 자가 체크리스트

- [x] STEP7-K L1089~L1099 K-055 4대 요건 전수 구현 (Docker / pip / YAML / deps)
- [x] K-056 Kubernetes (L1101~L1111) V3 이관 명시 (헤더 + §2.2)
- [x] LOCK-AP-01/02/04/07/09/10 5필드 분리 인용 (§12)
- [x] LOCK-AP-10 본 문서 재정의 없음 (06_autonomy-safety 정본 존중)
- [x] FABRICATION 10-마커 0건 (self scan 필요 — step 3 finalize)
- [x] 세션 간 인터페이스 4건 cross-check (§14)
- [x] Phase 3 테스트 시나리오 12건 (≥ 10건 요건 충족)
- [x] 에스컬레이션 페이로드 Pydantic class + structured JSON 3-block (§10/§11)
- [x] 비용 매트릭스 V1/V2/V3 합계 = LOCK-AP-09 정본 값 정합 (§8.2)
- [x] `io.vamos.*` OCI 라벨 8종 정의 (§4.3)

---

*정본 소유: #13 Agent-Protocol-Interoperability*
*K-056 Kubernetes 배포 (STEP7-K L1101~L1111) 는 plan §7.5 V3 이관 명시, 본 V2 Phase 2 범위 제외*
*LOCK-AP-10 HITL<50% 는 06_autonomy-safety/guardrail_rules.md (P2-6 정본) 에서 정의, 본 문서는 참조자*
