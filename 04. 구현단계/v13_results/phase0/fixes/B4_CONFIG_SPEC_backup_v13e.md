# PHASE_B4_CONFIG_SPEC (v1.0.0)

## 0. 문서 메타

| 항목 | 값 |
|------|-----|
| 문서 ID | B4 |
| 문서명 | PHASE_B4_CONFIG_SPEC |
| 버전 | 1.0.0 |
| 역할 | 환경 설정 파일 스펙 (Config Specification) |
| 상위 정본 | BASE 1.3 > PLAN 3.0 > DESIGN 2.0 > D2.1 Schema > A1 Tech Stack |
| 생성 일자 | 2026-02-22 |
| 연결 참조 | D7 (RBAC/Autonomy/Guardrails), D4 (ToolRegistry), D6 (Memory/VectorStore), D5 (Workflow), A1 (Tech Stack LOCK) |

---

## 1. 개요 (설정 관리 원칙)

### 1.1 설정 계층 구조

VAMOS 플랫폼의 설정은 3계층으로 분리 관리한다.

| 계층 | 저장 위치 | 용도 | 변경 빈도 |
|------|----------|------|----------|
| **L1 — 비밀 키** | `.env` 파일 | API 키, 비밀번호, 인증 토큰 | 드물게 (수동) |
| **L2 — 앱 설정** | `config/config.toml` 파일 | 모델, DB, 비용, 보안, 로깅 등 | 배포 시 |
| **L3 — 런타임 설정** | DB (V2+) | 동적 조정 항목 (rate limit, feature flag) | 실시간 |

### 1.2 핵심 원칙

1. **비밀 분리**: API 키/비밀번호는 반드시 `.env`에만 저장. `config/config.toml`이나 코드에 포함 금지.
2. **버전별 프리셋**: V1/V2/V3별로 기본 설정 파일(`config/config.v1.toml`, `config/config.v2.toml`, `config/config.v3.toml`)을 제공.
3. **환경 변수 우선**: `.env` > `config/config.toml` > DB 런타임 설정 순으로 오버라이드.
4. **Pydantic v2 검증**: 모든 설정은 `ConfigModel`(Pydantic v2)로 로드 시점에 검증.
5. **DESIGN 정합**: 설정 키는 D2.1 스키마 문서(D2~D8)의 SOT와 정합해야 하며, 임의 확장을 금지.

### 1.3 파일 레이아웃 (V1 로컬)

```
vamos/
  .env                    # L1: 비밀 키
  config/                 # L2: 앱 설정 (B2 프로젝트 구조 정합)
    config.toml           # 앱 설정 (버전별 프리셋 기반)
    config.v1.toml        # V1 프리셋 (기본값)
    config.v2.toml        # V2 프리셋 (변경 항목만)
    config.v3.toml        # V3 프리셋 (변경 항목만)
  data/
    sqlite/               # SQLite DB
    chroma/               # Chroma Vector DB (V1)
    graph/                # JSON Graph DB (V1)
    logs/                 # 로그 파일
    backups/              # 백업
```

---

## 2. 환경 변수 (.env)

> **원칙**: `.env` 파일은 Git에 커밋하지 않는다. `.env.example`만 템플릿으로 제공.

### 2.1 공통 환경 변수

| 키 | 타입 | 기본값 | 설명 | 연결 스키마 |
|----|------|--------|------|------------|
| `VAMOS_VERSION_TIER` | `string` | `"V1"` | 현재 버전 티어. enum: `V1` \| `V2` \| `V3` | A1 Stack Combos |
| `VAMOS_DATA_DIR` | `string` | `"./data"` | 데이터 루트 디렉토리 경로 | D4 BackupConfigSchema |
| `VAMOS_LOG_LEVEL` | `string` | `"INFO"` | 글로벌 로그 레벨. enum: `DEBUG` \| `INFO` \| `WARN` \| `ERROR` | D2 LogEventSchema |
| `VAMOS_ENV` | `string` | `"development"` | 실행 환경. enum: `development` \| `staging` \| `production` | -- |
| `VAMOS_HOST` | `string` | `"127.0.0.1"` | 서비스 바인드 주소 | -- |
| `VAMOS_PORT` | `integer` | `8000` | 서비스 포트 | -- |

### 2.2 LLM API 키

| 키 | 타입 | 기본값 | 설명 | 연결 스키마 |
|----|------|--------|------|------------|
| `OPENAI_API_KEY` | `string` | `""` | OpenAI API 키 (GPT-4o mini, GPT-4o, text-embedding-3-small) | D4 BrainAdapterResponseSchema |
| `ANTHROPIC_API_KEY` | `string` | `""` | Anthropic API 키 (Claude Sonnet) | D4 BrainAdapterResponseSchema |
| `OLLAMA_BASE_URL` | `string` | `"http://localhost:11434"` | Ollama 로컬 서버 URL (V1) | D4 BrainAdapterResponseSchema |
| `LM_STUDIO_BASE_URL` | `string` | `"http://localhost:1234"` | LM Studio 로컬 서버 URL (V1) | D4 BrainAdapterResponseSchema |

### 2.3 외부 서비스

| 키 | 타입 | 기본값 | 설명 | 연결 스키마 |
|----|------|--------|------|------------|
| `MCP_AUTH_TOKEN` | `string` | `""` | MCP 브릿지 인증 토큰 | D3 MCPBridgeLayerSchema |
| `QDRANT_API_KEY` | `string` | `""` | Qdrant Cloud API 키 (V2+) | D6 VectorStoreAdapterSchema |
| `QDRANT_URL` | `string` | `"http://localhost:6333"` | Qdrant 서버 URL (V2+) | D6 VectorStoreAdapterSchema |
| `NEO4J_URI` | `string` | `"bolt://localhost:7687"` | Neo4j 서버 URI (V2+) | D6 GraphRAGConfigSchema |
| `NEO4J_USER` | `string` | `"neo4j"` | Neo4j 사용자명 (V2+) | D6 GraphRAGConfigSchema |
| `NEO4J_PASSWORD` | `string` | `""` | Neo4j 비밀번호 (V2+) | D6 GraphRAGConfigSchema |
| `POSTGRES_DSN` | `string` | `""` | PostgreSQL 연결 문자열 (V2+) | D4 BackupConfigSchema |
| `NEMO_GUARDRAILS_ENDPOINT` | `string` | `""` | NeMo Guardrails 서버 URL (L1) | D7 GuardrailsCheckSchema |
| `LLAMAGUARD_ENDPOINT` | `string` | `""` | LlamaGuard 서버 URL (L3) | D7 GuardrailsCheckSchema |

### 2.4 `.env.example` 템플릿

```dotenv
# ============================================================
# VAMOS .env — 비밀 키 및 환경 변수
# ============================================================
# 이 파일을 .env로 복사한 후 실제 값을 입력하세요.
# .env 파일은 절대 Git에 커밋하지 마세요.
# ============================================================

# --- 공통 ---
VAMOS_VERSION_TIER=V1
VAMOS_DATA_DIR=./data
VAMOS_LOG_LEVEL=INFO
VAMOS_ENV=development
VAMOS_HOST=127.0.0.1
VAMOS_PORT=8000

# --- LLM API 키 ---
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434
LM_STUDIO_BASE_URL=http://localhost:1234

# --- 외부 서비스 (V2+에서 활성화) ---
MCP_AUTH_TOKEN=
QDRANT_API_KEY=
QDRANT_URL=http://localhost:6333
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=
POSTGRES_DSN=
NEMO_GUARDRAILS_ENDPOINT=
LLAMAGUARD_ENDPOINT=
```

---

## 3. 앱 설정 파일 (config/config.toml)

> **원칙**: 비밀이 아닌 모든 설정은 `config/config.toml`에 TOML 형식으로 정의. Pydantic v2로 파싱/검증.

### 3.1 [core] -- ORANGE CORE 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `autonomy_level` | `string` | `"L1"` | `"L2"` | `"L3"` | 기본 자율성 수준. enum: `L0` \| `L1` \| `L2` \| `L3` | D7 AutonomyLevelSchema (AC-D7-007) |
| `default_execution_mode` | `string` | `"mini"` | `"main"` | `"main"` | 기본 실행 모드. enum: `mini` \| `main` \| `tool` | D2 DecisionSchema.routing |
| `max_decision_timeout_ms` | `integer` | `30000` | `30000` | `60000` | Decision Kernel 최대 타임아웃 (ms) | D2 DecisionSchema |
| `single_decision_lock` | `boolean` | `true` | `true` | `true` | 단일 결정 원칙 잠금 (항상 true) | D2 DecisionSchema.locked |
| `pipeline_stages` | `array` | `["intake","plan","execute","verify","deliver"]` | 동일 | 동일 | 5단계 파이프라인 스테이지 | D5 WorkflowStageSchema |

```toml
[core]
autonomy_level = "L1"
default_execution_mode = "mini"
max_decision_timeout_ms = 30000
single_decision_lock = true
pipeline_stages = ["intake", "plan", "execute", "verify", "deliver"]
```

### 3.2 [llm] -- LLM 모델 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `mini_model` | `string` | `"ollama/llama3.2:3b"` | `"gpt-4o-mini"` | `"gpt-4o-mini"` | mini 모드 모델 ID | D4 BrainAdapterResponseSchema |
| `main_model` | `string` | `"ollama/llama3.1:8b"` | `"gpt-4o"` | `"gpt-4o"` | main 모드 모델 ID | D4 BrainAdapterResponseSchema |
| `fallback_model` | `string` | `"gpt-4o-mini"` | `"claude-sonnet"` | `"claude-sonnet"` | 폴백 모델 ID | D4 BrainAdapterResponseSchema |
| `temperature` | `float` | `0.3` | `0.3` | `0.3` | 기본 temperature | D4 BrainAdapterResponseSchema |
| `max_tokens` | `integer` | `2048` | `4096` | `8192` | 기본 최대 토큰 수 | D4 BrainAdapterResponseSchema |
| `streaming_enabled` | `boolean` | `true` | `true` | `true` | 스트리밍 응답 활성화 | D4 BrainAdapterResponseSchema |
| `prompt_cache_enabled` | `boolean` | `true` | `true` | `true` | 프롬프트 캐시 활성화 | D4 PromptCacheManagerSchema |
| `prompt_cache_ttl_sec` | `integer` | `3600` | `3600` | `7200` | 프롬프트 캐시 TTL (초) | D4 PromptCacheManagerSchema |

```toml
[llm]
mini_model = "ollama/llama3.2:3b"
main_model = "ollama/llama3.1:8b"
fallback_model = "gpt-4o-mini"
temperature = 0.3
max_tokens = 2048
streaming_enabled = true
prompt_cache_enabled = true
prompt_cache_ttl_sec = 3600
```

### 3.3 [embedding] -- Embedding 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `model` | `string` | `"bge-m3"` | `"text-embedding-3-small"` | `"text-embedding-3-small"` | 임베딩 모델 ID | D6 VectorStoreAdapterSchema (A1 DEC-005) |
| `dimension` | `integer` | `1024` | `1536` | `1536` | 임베딩 차원 수 | D6 VectorStoreAdapterSchema |
| `matryoshka_dim` | `integer` | `256` | `0` | `0` | Matryoshka 경량 차원 (0=비활성) | D6 VectorStoreAdapterSchema (A1 DEC-005) |
| `batch_size` | `integer` | `32` | `64` | `128` | 배치 임베딩 크기 | D6 VectorStoreAdapterSchema |
| `local_enabled` | `boolean` | `true` | `false` | `false` | 로컬 임베딩 활성화 여부 | A1 §A1-2A |

```toml
[embedding]
model = "bge-m3"
dimension = 1024
matryoshka_dim = 256
batch_size = 32
local_enabled = true
```

### 3.4 [vector_db] -- Vector DB 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `backend` | `string` | `"chroma"` | `"qdrant"` | `"qdrant_cloud"` | Vector DB 백엔드. enum: `chroma` \| `qdrant` \| `qdrant_cloud` \| `pgvector` | D6 VectorStoreAdapterSchema (AC-D6-008) |
| `mode` | `string` | `"embedded"` | `"client"` | `"cloud"` | 연결 모드. enum: `embedded` \| `client` \| `cloud` | D6 VectorStoreAdapterSchema |
| `collection_name` | `string` | `"vamos_default"` | `"vamos_default"` | `"vamos_default"` | 기본 컬렉션 이름 | D6 VectorStoreAdapterSchema |
| `persist_directory` | `string` | `"${VAMOS_DATA_DIR}/chroma"` | `""` | `""` | 로컬 영속 디렉토리 (V1 only) | D6 VectorStoreAdapterSchema |
| `similarity_metric` | `string` | `"cosine"` | `"cosine"` | `"cosine"` | 유사도 메트릭. enum: `cosine` \| `dot` \| `euclidean` | D6 VectorStoreAdapterSchema |

```toml
[vector_db]
backend = "chroma"
mode = "embedded"
collection_name = "vamos_default"
persist_directory = "${VAMOS_DATA_DIR}/chroma"
similarity_metric = "cosine"
```

### 3.5 [graph_db] -- Graph DB 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `backend` | `string` | `"json_file"` | `"neo4j"` | `"neo4j"` | Graph DB 백엔드. enum: `json_file` \| `neo4j` | D6 GraphRAGConfigSchema (AC-D6-009) |
| `json_path` | `string` | `"${VAMOS_DATA_DIR}/graph/graph.json"` | `""` | `""` | JSON 그래프 파일 경로 (V1 only) | D6 GraphRAGConfigSchema |
| `max_hops` | `integer` | `2` | `3` | `4` | 그래프 탐색 최대 홉 수 | D6 GraphRAGConfigSchema |
| `scope` | `string` | `"P1"` | `"FULL"` | `"FULL"` | GraphRAG 범위. V1=P1(간이), V2+=FULL | D6 GraphRAGConfigSchema (AC-D6-009) |
| `cache_enabled` | `boolean` | `true` | `true` | `true` | 그래프 쿼리 캐시 활성화 | D6 GraphRAGConfigSchema |

```toml
[graph_db]
backend = "json_file"
json_path = "${VAMOS_DATA_DIR}/graph/graph.json"
max_hops = 2
scope = "P1"
cache_enabled = true
```

### 3.6 [storage] -- Storage 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `backend` | `string` | `"sqlite"` | `"postgres"` | `"postgres"` | 메인 스토리지 백엔드. enum: `sqlite` \| `postgres` | D4 BackupConfigSchema (A1 §A1-4) |
| `db_path` | `string` | `"${VAMOS_DATA_DIR}/sqlite/vamos.db"` | `""` | `""` | SQLite DB 파일 경로 (V1 only) | D4 BackupConfigSchema |
| `log_format` | `string` | `"jsonl"` | `"jsonl"` | `"jsonl"` | 로그 스토리지 형식. enum: `jsonl` \| `structured` | D2 LogEventSchema |
| `log_path` | `string` | `"${VAMOS_DATA_DIR}/logs/events.jsonl"` | `""` | `""` | JSONL 로그 경로 (V1) | D2 LogEventSchema |
| `backup_enabled` | `boolean` | `true` | `true` | `true` | 자동 백업 활성화 | D4 BackupConfigSchema |
| `backup_schedule` | `string` | `"daily"` | `"6h"` | `"1h"` | 백업 주기. enum: `daily` \| `6h` \| `1h` \| `manual` | D4 BackupConfigSchema |
| `backup_retain_count` | `integer` | `7` | `14` | `30` | 보존 백업 수 | D4 BackupConfigSchema |
| `memory_ttl_L0` | `string` | `"session_end"` | `"session_end"` | `"session_end"` | L0(Session) 메모리 TTL | D6 MemoryRecordSchema (AC-D6-002) |
| `memory_ttl_L1` | `string` | `"90d"` | `"90d"` | `"90d"` | L1(Project) 메모리 TTL | D6 MemoryRecordSchema |
| `memory_ttl_L2` | `string` | `"indefinite"` | `"indefinite"` | `"indefinite"` | L2(Long-term) 메모리 TTL | D6 MemoryRecordSchema |
| `memory_ttl_L3` | `string` | `"policy_based"` | `"policy_based"` | `"policy_based"` | L3(Procedural) 메모리 TTL | D6 MemoryRecordSchema |

```toml
[storage]
backend = "sqlite"
db_path = "${VAMOS_DATA_DIR}/sqlite/vamos.db"
log_format = "jsonl"
log_path = "${VAMOS_DATA_DIR}/logs/events.jsonl"
backup_enabled = true
backup_schedule = "daily"
backup_retain_count = 7

memory_ttl_L0 = "session_end"
memory_ttl_L1 = "90d"
memory_ttl_L2 = "indefinite"
memory_ttl_L3 = "policy_based"
```

### 3.7 [cost] -- 비용 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `daily_limit` | `integer` | `1300` | `3100` | `8900` | 일일 비용 상한 (원) | D7 CostBudgetSchema (Downshift) |
| `monthly_limit` | `integer` | `40000` | `93000` | `266000` | 월간 비용 상한 (원) | D7 CostBudgetSchema |
| `warn_threshold` | `integer` | `80` | `80` | `80` | 경고 임계값 (%) — 80% 도달 시 force_mini | D7 DownshiftSchema |
| `block_threshold` | `integer` | `100` | `100` | `100` | 차단 임계값 (%) — 100% 도달 시 block | D7 DownshiftSchema |
| `downshift_model` | `string` | `"ollama/llama3.2:3b"` | `"gpt-4o-mini"` | `"gpt-4o-mini"` | 다운시프트 시 사용 모델 | D7 DownshiftSchema |
| `currency` | `string` | `"KRW"` | `"KRW"` | `"KRW"` | 통화 단위 | D7 CostBudgetSchema |
| `tracking_enabled` | `boolean` | `true` | `true` | `true` | 비용 추적 활성화 | D7 CostBudgetSchema |

```toml
[cost]
daily_limit = 1300
monthly_limit = 40000
warn_threshold = 80
block_threshold = 100
downshift_model = "ollama/llama3.2:3b"
currency = "KRW"
tracking_enabled = true
```

### 3.8 [guardrails] -- Guardrails 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `layer1_enabled` | `boolean` | `true` | `true` | `true` | NeMo Guardrails (L1) 활성화 | D7 GuardrailsCheckSchema (AC-D7-005) |
| `layer1_provider` | `string` | `"nemo"` | `"nemo"` | `"nemo"` | L1 프로바이더 | D7 GuardrailsCheckSchema |
| `layer2_enabled` | `boolean` | `true` | `true` | `true` | Guardrails AI (L2) 활성화 | D7 GuardrailsCheckSchema (AC-D7-005) |
| `layer2_provider` | `string` | `"guardrails_ai"` | `"guardrails_ai"` | `"guardrails_ai"` | L2 프로바이더 | D7 GuardrailsCheckSchema |
| `layer3_enabled` | `boolean` | `false` | `true` | `true` | LlamaGuard (L3) 활성화 | D7 GuardrailsCheckSchema (AC-D7-005) |
| `layer3_provider` | `string` | `"llamaguard"` | `"llamaguard"` | `"llamaguard"` | L3 프로바이더 | D7 GuardrailsCheckSchema |
| `layer4_enabled` | `boolean` | `false` | `true` | `true` | 사후감사 (L4) 활성화 — V2+ 전용 | D7 GuardrailsCheckSchema (AC-D7-005) |
| `layer4_provider` | `string` | `"audit_log"` | `"audit_log"` | `"audit_log"` | L4 프로바이더 (사후 감사 로그 분석) | D7 GuardrailsCheckSchema |
| `layer4_schedule` | `string` | `"disabled"` | `"daily"` | `"realtime"` | L4 감사 실행 주기. enum: `disabled` \| `daily` \| `hourly` \| `realtime` | D7 GuardrailsCheckSchema |
| `fail_policy` | `string` | `"deny"` | `"deny"` | `"deny"` | 어느 Layer든 실패 시 정책. enum: `deny` \| `restrict` | D7 GuardrailsCheckSchema (AC-D7-005) |
| `sensitive_types` | `array` | `["PII","AUTH","MEDICAL","LEGAL"]` | 동일 | 동일 | 탐지 민감 유형 목록 | D7 PolicyCheckSchema |

```toml
[guardrails]
layer1_enabled = true
layer1_provider = "nemo"
layer2_enabled = true
layer2_provider = "guardrails_ai"
layer3_enabled = false          # V1: L3 비활성 (LlamaGuard GPU 필요)
layer3_provider = "llamaguard"
layer4_enabled = false          # V1: L4 비활성 (사후감사는 V2+)
layer4_provider = "audit_log"
layer4_schedule = "disabled"    # V2: "daily", V3: "realtime"
fail_policy = "deny"
sensitive_types = ["PII", "AUTH", "MEDICAL", "LEGAL"]
```
### 3.8a [self_check] -- Self-check 임계값 (LOCK)

| 키 | 타입 | V1 기본값 | 설명 | LOCK |
|----|------|----------|------|------|
| `threshold_p0` | `integer` | `70` | P0 도메인 Self-check 통과 임계값 | LOCK |
| `threshold_p1` | `integer` | `75` | P1 도메인 Self-check 통과 임계값 | LOCK |
| `threshold_p2` | `integer` | `80` | P2 도메인 Self-check 통과 임계값 | LOCK |
| `soft_loop_max` | `integer` | `1` | Soft loop 자동 재시도 횟수 (이후 승인 필요) | LOCK |

```toml
[self_check]
threshold_p0 = 70
threshold_p1 = 75
threshold_p2 = 80
soft_loop_max = 1
```

### 3.8b [approval] -- 승인 타임아웃 (LOCK)

| 키 | 타입 | V1 기본값 | 설명 | LOCK |
|----|------|----------|------|------|
| `timeout_s` | `integer` | `600` | 승인 타임아웃 (초, 10분 미응답 시 자동 거부) | LOCK |
| `p2_timeout_s` | `integer` | `300` | P2/HITL 고위험 타임아웃 (초, 5분) | LOCK |

```toml
[approval]
timeout_s = 600
p2_timeout_s = 300
```

### 3.9 [mcp] -- MCP 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `transport` | `string` | `"streamable_http"` | `"streamable_http"` | `"streamable_http"` | MCP 전송 방식 (DEC-017 LOCK, stdio 제거) | D3 MCPBridgeLayerSchema (AC-D3-008) |
| `default_timeout_ms` | `integer` | `10000` | `10000` | `15000` | MCP 요청 기본 타임아웃 (ms) | D3 MCPBridgeLayerSchema |
| `max_retries` | `integer` | `3` | `3` | `3` | MCP 요청 최대 재시도 횟수 (exponential backoff 1s→2s→4s) | D3 MCPBridgeLayerSchema |
| `bridges` | `array` | `[]` | `[]` | `[]` | MCP 브릿지 서버 목록 (아래 참조) | D3 MCPBridgeLayerSchema |

#### MCP 브릿지 항목 스키마

```toml
[[mcp.bridges]]
bridge_id = "mcp_web_search"
endpoint = "http://localhost:9100/mcp"
transport = "streamable_http"
capabilities = ["web_search", "url_fetch"]
timeout_ms = 15000
enabled = true
```

| 키 | 타입 | 설명 |
|----|------|------|
| `bridge_id` | `string` | 브릿지 고유 ID |
| `endpoint` | `string` | 브릿지 서버 엔드포인트 URL |
| `transport` | `string` | 전송 방식 (반드시 `"streamable_http"`) |
| `capabilities` | `array` | 브릿지 제공 기능 목록 |
| `timeout_ms` | `integer` | 개별 브릿지 타임아웃 (ms) |
| `enabled` | `boolean` | 활성화 여부 |

### 3.10 [rbac] -- RBAC 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `default_role` | `string` | `"OWNER"` | `"OPERATOR"` | `"VIEWER"` | 신규 사용자 기본 역할 | D7 RBACRoleSchema (AC-D7-006) |
| `roles` | `object` | 아래 참조 | 아래 참조 | 아래 참조 | 역할별 권한 정의 | D7 RBACRoleSchema (AC-D7-006) |

```toml
[rbac]
default_role = "OWNER"     # V1: 단일 사용자이므로 OWNER

[rbac.roles.OWNER]
description = "플랫폼 소유자. 모든 권한 보유."
can_configure = true
can_approve = true
can_execute = true
can_view = true
max_autonomy = "L3"

[rbac.roles.ADMIN]
description = "관리자. 설정 변경 및 승인 가능."
can_configure = true
can_approve = true
can_execute = true
can_view = true
max_autonomy = "L2"

[rbac.roles.OPERATOR]
description = "운영자. 실행 및 조회 가능."
can_configure = false
can_approve = false
can_execute = true
can_view = true
max_autonomy = "L1"

[rbac.roles.VIEWER]
description = "조회자. 읽기 전용."
can_configure = false
can_approve = false
can_execute = false
can_view = true
max_autonomy = "L0"
```

### 3.11 [rate_limit] -- Rate Limit 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `enabled` | `boolean` | `false` | `true` | `true` | Rate Limit 활성화 | D4 RateLimitConfigSchema |
| `targets` | `array` | `[]` | 아래 참조 | 아래 참조 | Rate Limit 대상 목록 | D4 RateLimitConfigSchema |

#### Rate Limit 대상 스키마

```toml
[[rate_limit.targets]]
target_id = "openai_api"
requests_per_minute = 60
tokens_per_minute = 90000
burst_allowance = 10
cooldown_sec = 5

[[rate_limit.targets]]
target_id = "mcp_bridge"
requests_per_minute = 30
tokens_per_minute = 0          # 토큰 기반 제한 미적용
burst_allowance = 5
cooldown_sec = 10
```

| 키 | 타입 | 설명 |
|----|------|------|
| `target_id` | `string` | Rate Limit 대상 ID |
| `requests_per_minute` | `integer` | 분당 최대 요청 수 |
| `tokens_per_minute` | `integer` | 분당 최대 토큰 수 (0=미적용) |
| `burst_allowance` | `integer` | 버스트 허용 추가 요청 수 |
| `cooldown_sec` | `integer` | 한도 초과 후 대기 시간 (초) |

### 3.12 [logging] -- Logging 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `level` | `string` | `"INFO"` | `"INFO"` | `"WARN"` | 로그 레벨. enum: `DEBUG` \| `INFO` \| `WARN` \| `ERROR` | D2 LogEventSchema |
| `format` | `string` | `"json"` | `"json"` | `"json"` | 로그 포맷. enum: `json` \| `text` | D2 LogEventSchema |
| `trace_id_required` | `boolean` | `true` | `true` | `true` | 모든 로그에 trace_id 포함 필수 | D2 LogEventSchema, D4 (AC-D4-005) |
| `sinks` | `array` | `["file"]` | `["file","stdout"]` | `["file","stdout","remote"]` | 로그 출력 대상 | D2 LogEventSchema |

#### Logging Sink 스키마

```toml
[[logging.sinks]]
sink_id = "file"
type = "file"
path = "${VAMOS_DATA_DIR}/logs/vamos.log"
rotation = "daily"
retain_days = 30

[[logging.sinks]]
sink_id = "stdout"
type = "stdout"
colored = true
```

| 키 | 타입 | 설명 |
|----|------|------|
| `sink_id` | `string` | Sink 고유 ID |
| `type` | `string` | 출력 유형. enum: `file` \| `stdout` \| `remote` |
| `path` | `string` | 파일 경로 (type=file일 때) |
| `rotation` | `string` | 로테이션 주기 (type=file일 때) |
| `retain_days` | `integer` | 보존 일수 (type=file일 때) |
| `colored` | `boolean` | 컬러 출력 (type=stdout일 때) |
| `endpoint` | `string` | 원격 서버 URL (type=remote일 때, V3) |

```toml
[logging]
level = "INFO"
format = "json"
trace_id_required = true
sinks = ["file"]
```

### 3.13 [blue_nodes] -- Blue Node 상한 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `active_node_cap` | `integer` | `3` | `10` | `50` | 세션당 활성 Blue Node 상한 (LOCK: D2.0-03 §4.3-B) | D3 BlueNodeSchema (LOCK-AT-014) |
| `candidate_node_cap` | `integer` | `5` | `20` | `100` | 세션당 후보 Blue Node 상한 | D3 BlueNodeSchema |
| `cap_exceeded_action` | `string` | `"reuse"` | `"reuse"` | `"queue"` | 상한 도달 시 동작. enum: `reuse` \| `queue` \| `reject` | D3 BlueNodeSchema |

```toml
[blue_nodes]
active_node_cap = 3          # V1: Lead + 2 Sub
candidate_node_cap = 5        # V1: 활성 3 + 대기 2
cap_exceeded_action = "reuse" # 상한 시 기존 노드 재사용
```

### 3.14 [ui] -- UI 레이아웃 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `min_width` | `integer` | `1280` | `768` | `375` | 최소 화면 너비 (px) | D8 §3.1 LOCK |
| `default_width` | `integer` | `1440` | `1440` | `1440` | 기본 윈도우 너비 (px) | D8 §3 |
| `default_height` | `integer` | `900` | `900` | `900` | 기본 윈도우 높이 (px) | D8 §3 |
| `font_family` | `string` | `"system-ui, sans-serif"` | `"system-ui, sans-serif"` | `"system-ui, sans-serif"` | 기본 폰트 스택 | D8 §10.2a |

```toml
[ui]
min_width = 1280              # V1: 데스크톱 전용
default_width = 1440
default_height = 900
font_family = "system-ui, sans-serif"
```

### 3.15 [semantic_cache] -- Semantic Cache 설정

| 키 | 타입 | V1 기본값 | V2 기본값 | V3 기본값 | 설명 | 연결 스키마 |
|----|------|----------|----------|----------|------|------------|
| `enabled` | `boolean` | `true` | `true` | `true` | Semantic Cache 활성화 | D6 SemanticCacheSchema (AC-D6-010) |
| `similarity_threshold` | `float` | `0.95` | `0.95` | `0.95` | 캐시 히트 유사도 임계값 (LOCK) | D6 SemanticCacheSchema (AC-D6-010) |
| `max_entries` | `integer` | `1000` | `5000` | `20000` | 최대 캐시 엔트리 수 | D6 SemanticCacheSchema |
| `ttl_sec` | `integer` | `3600` | `7200` | `14400` | 캐시 TTL (초) | D6 SemanticCacheSchema |

```toml
[semantic_cache]
enabled = true
similarity_threshold = 0.95    # LOCK: 0.95 이상만 캐시 히트
max_entries = 1000
ttl_sec = 3600
```

---

## 4. 버전별 프리셋 (V1/V2/V3)

### 4.1 config/config.v1.toml (기본값 -- 로컬 MVP)

> 비용: <=40,000원/월, 로컬 실행 우선

```toml
# ============================================================
# VAMOS config/config.v1.toml — V1 로컬 MVP 프리셋
# ============================================================

[core]
autonomy_level = "L1"
default_execution_mode = "mini"
max_decision_timeout_ms = 30000
single_decision_lock = true
pipeline_stages = ["intake", "plan", "execute", "verify", "deliver"]

[llm]
mini_model = "ollama/llama3.2:3b"
main_model = "ollama/llama3.1:8b"
fallback_model = "gpt-4o-mini"
temperature = 0.3
max_tokens = 2048
streaming_enabled = true
prompt_cache_enabled = true
prompt_cache_ttl_sec = 3600

[embedding]
model = "bge-m3"
dimension = 1024
matryoshka_dim = 256
batch_size = 32
local_enabled = true

[vector_db]
backend = "chroma"
mode = "embedded"
collection_name = "vamos_default"
persist_directory = "${VAMOS_DATA_DIR}/chroma"
similarity_metric = "cosine"

[graph_db]
backend = "json_file"
json_path = "${VAMOS_DATA_DIR}/graph/graph.json"
max_hops = 2
scope = "P1"
cache_enabled = true

[storage]
backend = "sqlite"
db_path = "${VAMOS_DATA_DIR}/sqlite/vamos.db"
log_format = "jsonl"
log_path = "${VAMOS_DATA_DIR}/logs/events.jsonl"
backup_enabled = true
backup_schedule = "daily"
backup_retain_count = 7
memory_ttl_L0 = "session_end"
memory_ttl_L1 = "90d"
memory_ttl_L2 = "indefinite"
memory_ttl_L3 = "policy_based"

[cost]
daily_limit = 1300
monthly_limit = 40000
warn_threshold = 80
block_threshold = 100
downshift_model = "ollama/llama3.2:3b"
currency = "KRW"
tracking_enabled = true

[guardrails]
layer1_enabled = true
layer1_provider = "nemo"
layer2_enabled = true
layer2_provider = "guardrails_ai"
layer3_enabled = false
layer3_provider = "llamaguard"
fail_policy = "deny"
sensitive_types = ["PII", "AUTH", "MEDICAL", "LEGAL"]

[mcp]
transport = "streamable_http"
default_timeout_ms = 10000
max_retries = 3
bridges = []

[rbac]
default_role = "OWNER"

[rbac.roles.OWNER]
description = "플랫폼 소유자"
can_configure = true
can_approve = true
can_execute = true
can_view = true
max_autonomy = "L3"

[rbac.roles.ADMIN]
description = "관리자"
can_configure = true
can_approve = true
can_execute = true
can_view = true
max_autonomy = "L2"

[rbac.roles.OPERATOR]
description = "운영자"
can_configure = false
can_approve = false
can_execute = true
can_view = true
max_autonomy = "L1"

[rbac.roles.VIEWER]
description = "조회자"
can_configure = false
can_approve = false
can_execute = false
can_view = true
max_autonomy = "L0"

[rate_limit]
enabled = false
targets = []

[logging]
level = "INFO"
format = "json"
trace_id_required = true
sinks = ["file"]

[[logging.sinks]]
sink_id = "file"
type = "file"
path = "${VAMOS_DATA_DIR}/logs/vamos.log"
rotation = "daily"
retain_days = 30

[semantic_cache]
enabled = true
similarity_threshold = 0.95
max_entries = 1000
ttl_sec = 3600
```

### 4.2 config/config.v2.toml (변경 항목만 -- 서버)

> 비용: <=93,000원/월, Docker Compose 배포

```toml
# ============================================================
# VAMOS config/config.v2.toml — V2 서버 프리셋 (V1 대비 변경 항목만)
# ============================================================
# 기저: config/config.v1.toml 의 모든 값을 상속하며, 아래 항목만 오버라이드

[core]
autonomy_level = "L2"
default_execution_mode = "main"

[llm]
mini_model = "gpt-4o-mini"
main_model = "gpt-4o"
fallback_model = "claude-sonnet"
max_tokens = 4096

[embedding]
model = "text-embedding-3-small"
dimension = 1536
matryoshka_dim = 0
batch_size = 64
local_enabled = false

[vector_db]
backend = "qdrant"
mode = "client"
persist_directory = ""

[graph_db]
backend = "neo4j"
json_path = ""
max_hops = 3
scope = "FULL"

[storage]
backend = "postgres"
db_path = ""
log_path = ""
backup_schedule = "6h"
backup_retain_count = 14

[cost]
daily_limit = 3100
monthly_limit = 93000
downshift_model = "gpt-4o-mini"

[guardrails]
layer3_enabled = true

[mcp]
max_retries = 3

[rbac]
default_role = "OPERATOR"

[rate_limit]
enabled = true

[[rate_limit.targets]]
target_id = "openai_api"
requests_per_minute = 60
tokens_per_minute = 90000
burst_allowance = 10
cooldown_sec = 5

[[rate_limit.targets]]
target_id = "mcp_bridge"
requests_per_minute = 30
tokens_per_minute = 0
burst_allowance = 5
cooldown_sec = 10

[logging]
sinks = ["file", "stdout"]

[[logging.sinks]]
sink_id = "file"
type = "file"
path = "${VAMOS_DATA_DIR}/logs/vamos.log"
rotation = "daily"
retain_days = 60

[[logging.sinks]]
sink_id = "stdout"
type = "stdout"
colored = true

[semantic_cache]
max_entries = 5000
ttl_sec = 7200
```

### 4.3 config/config.v3.toml (변경 항목만 -- 엔터프라이즈)

> 비용: <=266,000원/월, K8s 배포

```toml
# ============================================================
# VAMOS config/config.v3.toml — V3 엔터프라이즈 프리셋 (V2 대비 변경 항목만)
# ============================================================
# 기저: config/config.v2.toml 의 모든 값을 상속하며, 아래 항목만 오버라이드

[core]
autonomy_level = "L3"
max_decision_timeout_ms = 60000

[llm]
max_tokens = 8192
prompt_cache_ttl_sec = 7200

[embedding]
batch_size = 128

[vector_db]
backend = "qdrant_cloud"
mode = "cloud"

[storage]
backup_schedule = "1h"
backup_retain_count = 30

[cost]
daily_limit = 8900
monthly_limit = 266000

[mcp]
default_timeout_ms = 15000

[rbac]
default_role = "VIEWER"

[[rate_limit.targets]]
target_id = "openai_api"
requests_per_minute = 120
tokens_per_minute = 200000
burst_allowance = 20
cooldown_sec = 3

[[rate_limit.targets]]
target_id = "mcp_bridge"
requests_per_minute = 60
tokens_per_minute = 0
burst_allowance = 10
cooldown_sec = 5

[[rate_limit.targets]]
target_id = "vllm_self_hosted"
requests_per_minute = 200
tokens_per_minute = 500000
burst_allowance = 50
cooldown_sec = 2

[logging]
level = "WARN"
sinks = ["file", "stdout", "remote"]

[[logging.sinks]]
sink_id = "file"
type = "file"
path = "${VAMOS_DATA_DIR}/logs/vamos.log"
rotation = "daily"
retain_days = 90

[[logging.sinks]]
sink_id = "stdout"
type = "stdout"
colored = true

[[logging.sinks]]
sink_id = "remote"
type = "remote"
endpoint = "https://logging.vamos.internal/ingest"

[semantic_cache]
max_entries = 20000
ttl_sec = 14400
```

---

## 5. 런타임 설정 (DB 저장 -- V2+)

V2 이상에서는 일부 설정을 DB(Postgres)에 저장하여 런타임 동적 변경을 지원한다.

### 5.1 런타임 설정 테이블 스키마

```sql
CREATE TABLE IF NOT EXISTS runtime_config (
    config_key    VARCHAR(128) PRIMARY KEY,
    config_value  JSONB        NOT NULL,
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_by    VARCHAR(64)  NOT NULL,        -- RBAC user_id
    version       INTEGER      NOT NULL DEFAULT 1
);
```

### 5.2 런타임 변경 가능 항목

| config_key | 변경 가능 범위 | 최소 역할 | 설명 |
|-----------|--------------|----------|------|
| `cost.daily_limit` | V2+ | ADMIN | 일일 비용 상한 동적 조정 |
| `cost.warn_threshold` | V2+ | ADMIN | 경고 임계값 동적 조정 |
| `rate_limit.targets.*` | V2+ | ADMIN | Rate Limit 규칙 동적 조정 |
| `guardrails.layer3_enabled` | V2+ | OWNER | L3 Guardrails 온/오프 |
| `core.autonomy_level` | V2+ | OWNER | 기본 자율성 수준 변경 |
| `semantic_cache.max_entries` | V2+ | ADMIN | 캐시 크기 동적 조정 |
| `logging.level` | V2+ | OPERATOR | 로그 레벨 동적 변경 |

### 5.3 변경 이력 추적

```sql
CREATE TABLE IF NOT EXISTS config_audit_log (
    audit_id      SERIAL       PRIMARY KEY,
    config_key    VARCHAR(128) NOT NULL,
    old_value     JSONB,
    new_value     JSONB        NOT NULL,
    changed_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    changed_by    VARCHAR(64)  NOT NULL,
    reason        TEXT
);
```

### 5.4 오버라이드 우선순위 (최종)

```
환경 변수 (.env)  >  런타임 DB (V2+)  >  config/config.toml  >  프리셋 기본값
```

---

## 6. 설정 검증 규칙 (Pydantic v2 ConfigModel)

### 6.1 최상위 ConfigModel

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from enum import Enum


class AutonomyLevel(str, Enum):
    """D7 AutonomyLevelSchema 정합 (AC-D7-007)"""
    L0 = "L0"
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class ExecutionMode(str, Enum):
    """D2 DecisionSchema.routing.execution_mode 정합"""
    MINI = "mini"
    MAIN = "main"
    TOOL = "tool"


class VectorBackend(str, Enum):
    """D6 VectorStoreAdapterSchema.backend 정합 (AC-D6-008)"""
    CHROMA = "chroma"
    QDRANT = "qdrant"
    QDRANT_CLOUD = "qdrant_cloud"
    PGVECTOR = "pgvector"


class GraphBackend(str, Enum):
    """D6 GraphRAGConfigSchema.backend 정합"""
    JSON_FILE = "json_file"
    NEO4J = "neo4j"


class StorageBackend(str, Enum):
    """A1 Storage LOCK 정합"""
    SQLITE = "sqlite"
    POSTGRES = "postgres"


class RBACRole(str, Enum):
    """D7 RBACRoleSchema.role 정합 (AC-D7-006)"""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"


class LogLevel(str, Enum):
    """D2 LogEventSchema 정합"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class MCPTransport(str, Enum):
    """D3 MCPBridgeLayerSchema.transport 정합 (AC-D3-008, DEC-017 LOCK)"""
    STREAMABLE_HTTP = "streamable_http"


# ---- Section Models ----

class CoreConfig(BaseModel):
    autonomy_level: AutonomyLevel = AutonomyLevel.L1
    default_execution_mode: ExecutionMode = ExecutionMode.MINI
    max_decision_timeout_ms: int = Field(default=30000, ge=1000, le=120000)
    single_decision_lock: Literal[True] = True
    pipeline_stages: list[str] = [
        "intake", "plan", "execute", "verify", "deliver"
    ]

    @field_validator("pipeline_stages")
    @classmethod
    def validate_stages(cls, v: list[str]) -> list[str]:
        required = ["intake", "plan", "execute", "verify", "deliver"]
        if v != required:
            raise ValueError(
                f"pipeline_stages must be {required}"
            )
        return v


class LLMConfig(BaseModel):
    mini_model: str = "ollama/llama3.2:3b"
    main_model: str = "ollama/llama3.1:8b"
    fallback_model: str = "gpt-4o-mini"
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=256, le=32768)
    streaming_enabled: bool = True
    prompt_cache_enabled: bool = True
    prompt_cache_ttl_sec: int = Field(default=3600, ge=60, le=86400)


class EmbeddingConfig(BaseModel):
    model: str = "bge-m3"
    dimension: int = Field(default=1024, ge=64, le=4096)
    matryoshka_dim: int = Field(default=256, ge=0, le=2048)
    batch_size: int = Field(default=32, ge=1, le=512)
    local_enabled: bool = True


class VectorDBConfig(BaseModel):
    backend: VectorBackend = VectorBackend.CHROMA
    mode: Literal["embedded", "client", "cloud"] = "embedded"
    collection_name: str = "vamos_default"
    persist_directory: str = ""
    similarity_metric: Literal["cosine", "dot", "euclidean"] = "cosine"


class GraphDBConfig(BaseModel):
    backend: GraphBackend = GraphBackend.JSON_FILE
    json_path: str = ""
    max_hops: int = Field(default=2, ge=1, le=10)
    scope: Literal["P1", "FULL"] = "P1"
    cache_enabled: bool = True


class StorageConfig(BaseModel):
    backend: StorageBackend = StorageBackend.SQLITE
    db_path: str = ""
    log_format: Literal["jsonl", "structured"] = "jsonl"
    log_path: str = ""
    backup_enabled: bool = True
    backup_schedule: Literal["daily", "6h", "1h", "manual"] = "daily"
    backup_retain_count: int = Field(default=7, ge=1, le=365)
    memory_ttl_L0: str = "session_end"
    memory_ttl_L1: str = "90d"
    memory_ttl_L2: str = "indefinite"
    memory_ttl_L3: str = "policy_based"


class CostConfig(BaseModel):
    daily_limit: int = Field(default=1300, ge=0)
    monthly_limit: int = Field(default=40000, ge=0)
    warn_threshold: int = Field(default=80, ge=0, le=100)
    block_threshold: int = Field(default=100, ge=0, le=100)
    downshift_model: str = "ollama/llama3.2:3b"
    currency: Literal["KRW", "USD"] = "KRW"
    tracking_enabled: bool = True

    @field_validator("block_threshold")
    @classmethod
    def block_gte_warn(cls, v: int, info) -> int:
        warn = info.data.get("warn_threshold", 80)
        if v < warn:
            raise ValueError(
                "block_threshold must be >= warn_threshold"
            )
        return v


class GuardrailsConfig(BaseModel):
    layer1_enabled: bool = True
    layer1_provider: str = "nemo"
    layer2_enabled: bool = True
    layer2_provider: str = "guardrails_ai"
    layer3_enabled: bool = False
    layer3_provider: str = "llamaguard"
    layer4_enabled: bool = False          # V2+: 사후감사 (B4-03 ADD)
    layer4_provider: str = "audit_log"
    layer4_schedule: Literal["disabled", "daily", "hourly", "realtime"] = "disabled"
    fail_policy: Literal["deny", "restrict"] = "deny"
    sensitive_types: list[str] = ["PII", "AUTH", "MEDICAL", "LEGAL"]


class MCPBridge(BaseModel):
    bridge_id: str
    endpoint: str
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP
    capabilities: list[str] = []
    timeout_ms: int = Field(default=10000, ge=1000, le=60000)
    enabled: bool = True


class MCPConfig(BaseModel):
    transport: MCPTransport = MCPTransport.STREAMABLE_HTTP
    default_timeout_ms: int = Field(default=10000, ge=1000, le=60000)
    max_retries: int = Field(default=3, ge=0, le=10)
    bridges: list[MCPBridge] = []


class RBACRoleConfig(BaseModel):
    description: str = ""
    can_configure: bool = False
    can_approve: bool = False
    can_execute: bool = False
    can_view: bool = True
    max_autonomy: AutonomyLevel = AutonomyLevel.L0


class RBACConfig(BaseModel):
    default_role: RBACRole = RBACRole.OWNER
    roles: dict[RBACRole, RBACRoleConfig] = {}


class RateLimitTarget(BaseModel):
    target_id: str
    requests_per_minute: int = Field(default=60, ge=1)
    tokens_per_minute: int = Field(default=0, ge=0)
    burst_allowance: int = Field(default=10, ge=0)
    cooldown_sec: int = Field(default=5, ge=0)


class RateLimitConfig(BaseModel):
    enabled: bool = False
    targets: list[RateLimitTarget] = []


class LogSink(BaseModel):
    sink_id: str
    type: Literal["file", "stdout", "remote"]
    path: Optional[str] = None
    rotation: Optional[str] = None
    retain_days: Optional[int] = None
    colored: Optional[bool] = None
    endpoint: Optional[str] = None


class LoggingConfig(BaseModel):
    level: LogLevel = LogLevel.INFO
    format: Literal["json", "text"] = "json"
    trace_id_required: Literal[True] = True
    sinks: list[str] = ["file"]


class SemanticCacheConfig(BaseModel):
    """D6 SemanticCacheSchema 정합 (AC-D6-010)"""
    enabled: bool = True
    similarity_threshold: float = Field(default=0.95, ge=0.90, le=1.0)
    max_entries: int = Field(default=1000, ge=100, le=100000)
    ttl_sec: int = Field(default=3600, ge=60, le=86400)

    @field_validator("similarity_threshold")
    @classmethod
    def threshold_lock(cls, v: float) -> float:
        if v < 0.95:
            raise ValueError(
                "similarity_threshold LOCK: must be >= 0.95 (AC-D6-010)"
            )
        return v


# ---- Root Model ----

class VamosConfig(BaseModel):
    """VAMOS 플랫폼 설정 최상위 모델. Pydantic v2."""
    core: CoreConfig = CoreConfig()
    llm: LLMConfig = LLMConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    vector_db: VectorDBConfig = VectorDBConfig()
    graph_db: GraphDBConfig = GraphDBConfig()
    storage: StorageConfig = StorageConfig()
    cost: CostConfig = CostConfig()
    guardrails: GuardrailsConfig = GuardrailsConfig()
    mcp: MCPConfig = MCPConfig()
    rbac: RBACConfig = RBACConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    logging: LoggingConfig = LoggingConfig()
    semantic_cache: SemanticCacheConfig = SemanticCacheConfig()
```

### 6.2 검증 규칙 요약

| 규칙 ID | 설명 | 관련 AC |
|---------|------|---------|
| VAL-001 | `mcp.transport`는 반드시 `"streamable_http"` | AC-D3-008 |
| VAL-002 | `guardrails` 4-Layer(L1~L3 실시간 + L4 사후감사) 중 하나라도 실패 시 `fail_policy` 적용 | AC-D7-005 |
| VAL-003 | `rbac.roles`의 키는 `OWNER/ADMIN/OPERATOR/VIEWER`만 허용 | AC-D7-006 |
| VAL-004 | `core.autonomy_level`은 `L0~L3`만 허용 | AC-D7-007 |
| VAL-005 | `cost.block_threshold >= cost.warn_threshold` 필수 | D7 DownshiftSchema |
| VAL-006 | `semantic_cache.similarity_threshold >= 0.95` (LOCK) | AC-D6-010 |
| VAL-007 | `core.pipeline_stages`는 정확히 5단계 고정 | D5 WorkflowStageSchema |
| VAL-008 | `core.single_decision_lock`은 항상 `true` | D2 DecisionSchema.locked |
| VAL-009 | `logging.trace_id_required`는 항상 `true` | AC-D4-005 |
| VAL-010 | `graph_db.scope`는 V1일 때 `"P1"`, V2+일 때 `"FULL"` 권장 | AC-D6-009 |

### 6.3 설정 로딩 흐름

```
1. load_dotenv(".env")              # L1: 비밀 키 로드
2. toml_data = tomli.load("config/config.toml")  # L2: 앱 설정 파싱
3. config = VamosConfig(**toml_data)     # Pydantic v2 검증
4. if V2+:
     db_overrides = load_runtime_config(db)  # L3: 런타임 오버라이드
     config = config.model_copy(update=db_overrides)
5. validate_version_consistency(config, VAMOS_VERSION_TIER)
6. return config
```

---

## 7. 문서 이력

| 버전 | 일자 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-22 | Phase B4 초판. 환경 변수(.env), 앱 설정(config.toml), 버전별 프리셋(V1/V2/V3), 런타임 설정(V2+), Pydantic v2 ConfigModel 검증 규칙 정의. D2~D8 AC 정합 반영. |
| 1.0.1 | 2026-03-01 | PB-01: config 경로 통일 — 루트 레벨 `config.toml`/`config.v1.toml` → `config/config.toml`/`config/config.v1.toml`로 정정 (B2 프로젝트 구조 정합). |

---

---

<\!-- END OF DOCUMENT -->
