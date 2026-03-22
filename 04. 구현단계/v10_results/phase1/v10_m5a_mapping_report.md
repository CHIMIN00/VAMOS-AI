# M-5a 매핑 검증 보고서: §6.1~§6.7 시스템별 상세

- **에이전트**: M-5a
- **범위**: PART2 §6.1~§6.7 (L2848~L3165)
- **방법**: §6 구현항목 122개 추출 → Feature Registry 역매핑
- **생성일**: 2026-03-09

## 1. 통계 요약

| 지표 | 값 |
|------|-----|
| §6 구현 항목 수 | 122 |
| 매칭된 고유 Feature 수 | 269 |
| §6 only (Phase 미배정) 그룹 수 | 52 |
| M-1~M-4 MISSING 총 | 1074 |
| M-1~M-4 MISSING → §6 발견 | 7 |
| M-1~M-4 MISSING 총 | 1074 |
| M-1~M-4 MISSING → §6 미발견 | 1067 |
| V_UNKNOWN → §6 발견 | 0 |

## 2. 섹션별 커버리지

| 섹션 | §6항목수 | 매칭Feature | Phase미배정 |
|------|---------|-----------|-----------|
| §6.1 | 42 | 59 | 31 |
| §6.2 | 10 | 48 | 27 |
| §6.3 | 7 | 20 | 15 |
| §6.4 | 14 | 25 | 22 |
| §6.5 | 15 | 59 | 40 |
| §6.6 | 18 | 32 | 21 |
| §6.7 | 16 | 90 | 58 |

## 3. [임무 1] §6 only, Phase 미배정 항목

> §6.1~§6.7에 구현 항목으로 존재하지만 §2~§5 Phase에 배정되지 않은 Feature
> → **PARTIAL** 판정: "§6 only, Phase 미배정"

### S6-UI-002: Builder View (Cockpit) (§6.1.1 L2861)
- Phase 미배정 Feature: **4건** (Phase 배정: 3건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| P30-018 | 2윈도우 구조 구현 (Builder View + Hologram View) | V1 |
| D208-015 | Builder View 사용자 행동 → AI 반응 → LogEvent 매핑 (12개 이벤트 | V1 |
| AINV-079 | No-code Builder View 프론트엔드 (frontend/) | V3 |
| SDAR-102 | SDAR 대시보드 UI (UI Builder View에 SDAR 탭 추가) | V3 |

### S6-UI-005: Decision 컴포넌트 (3개) (§6.1.2 L2869)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| PB5-005 | React vitest 컴포넌트/Store/Hook 테스트 구현 (11개) | V1 |

### S6-UI-008: Cost 컴포넌트 (5개) (§6.1.2 L2872)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| PB5-005 | React vitest 컴포넌트/Store/Hook 테스트 구현 (11개) | V1 |

### S6-UI-017: Stores (7개) (§6.1.3 L2886)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D202-102 | DI Kernel (의존성 주입 컨테이너) 구현 | V0,V1 |

### S6-UI-022: V1 이미지 입력 (CLIP) (§6.1.5 L2905)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D208-027 | 비전-언어 모델 통합 (J-001~J-010, 10건: 이미지 파이프라인/멀티모달 대화/O | V1,V2,V3 |

### S6-UI-023: V1 OCR (Tesseract+PyMuPDF) (§6.1.5 L2906)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D208-027 | 비전-언어 모델 통합 (J-001~J-010, 10건: 이미지 파이프라인/멀티모달 대화/O | V1,V2,V3 |

### S6-UI-024: V1 STT (Whisper 로컬) (§6.1.5 L2907)
- Phase 미배정 Feature: **4건** (Phase 배정: 2건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D204-018 | STT 엔진 선택 (Whisper v3 vs Deepgram 자동 선택) | V1 |
| D205-116 | 회의 자동화 (Whisper STT 노트 회의록 후속, Calendar API) | V1,V2 |
| D208-030 | 오디오/음성 처리 (J-021~J-032, 12건: STT/TTS/음성대화/오디오분석/음악 | V1,V2,V3 |
| D208-086 | IDEA-H03 네이티브 음성/오디오 + IDEA-H05 음성 인터페이스 STT/TTS | V2,V3 |

### S6-UI-026: V1 차트 (Mermaid+Plotly) (§6.1.5 L2909)
- Phase 미배정 Feature: **3건** (Phase 배정: 1건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D205-105 | 리포트 자동 생성 파이프라인 (수집 분석 차트 문서 배포) | V1 |
| D208-029 | 이미지 생성 (J-011~J-020, 10건: 생성 게이트웨이/프롬프트/인페인팅/차트생성/ | V1,V2,V3 |
| AINV-135 | Z-Session TradingView 대체: Plotly/Dash/Matplotlib 차 | V2 |

### S6-UI-030: V2 Computer Use Agent (§6.1.5 L2907)
- Phase 미배정 Feature: **2건** (Phase 배정: 2건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D205-074 | Computer Use 에이전트 (브라우저/데스크톱 직접 조작) | V3 |
| D208-034 | 멀티모달 에이전트 (J-059~J-066, 8건: Computer Use/작업플래너/피드백 | V1,V2,V3 |

### S6-UI-038: V3 AR/공간 이해 (§6.1.5 L2909)
- Phase 미배정 Feature: **1건** (Phase 배정: 1건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D208-028 | ★ AR 공간 이해 및 ARKit/ARCore 연동 (J-009, V3) | V3 |

### S6-UI-040: UI State Machine 9-state (§6.1.6 L2917)
- Phase 미배정 Feature: **2건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D208-021 | UI 상태머신 구현 (UI_S0~S8 9-state + 전이 조건) | V1 |
| D208-023 | Pipeline S0~S8 ↔ UI 상태 크로스 매핑 (D8-M11) | V1 |

### S6-UI-041: Failure/Fallback UI 규칙 (§6.1.7 L2940)
- Phase 미배정 Feature: **3건** (Phase 배정: 10건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-047 | 6개 레지스트리 구현 (EventType 53+, FailureCode 20, Fallba | V2,V3 |
| SDAR-067 | SDAR FailureCodeRegistry 확장 구현 (13개 SDAR 내부 실패 코드  | V1 |
| SDAR-068 | SDAR FallbackRegistry 확장 구현 (4개 Fallback 등록 및 Fail | V1 |

### S6-UI-042: UI RBAC 접근 제어 (§6.1.8 L2950)
- Phase 미배정 Feature: **7건** (Phase 배정: 3건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-112 | RBAC 4역할 구현 (OWNER/ADMIN/OPERATOR/VIEWER + 권한 매트릭스 | V1,V2 |
| D207-038 | RBAC 4역할 구현 (OWNER/ADMIN/OPERATOR/VIEWER + AGENT 시 | V1,V2 |
| DD7-006 | RBACRoleSchema Pydantic v2 모델 코드 생성 (OWNER/ADMIN/O | V1 |
| TEAM-033 | AgentRBACPolicy 구현 (역할별 접근 제어) | V1 |
| SDAR-028 | AR-Level 변경 규칙 구현 (상승: ADMIN+I-19 승인, 하락: OPERATOR | V1 |
| SDAR-029 | RBAC 역할별 AR-Level 설정 권한 제어 구현 (OWNER:L0~L4/ADMIN:L | V1 |
| SDAR-085 | SDARKillSwitch 클래스 구현 (activate/deactivate, 5초 gra | V1 |

### S6-RUST-004: Tauri IPC Safety 핸들러 (19개) (§6.2.1 L2968)
- Phase 미배정 Feature: **24건** (Phase 배정: 10건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-031 | V0 진입 전 필수 구현 16항목 (통신 확정, IMPL 계층, 비용 상한, 디렉토리, c | V0 |
| CLAUDE-032 | V1 진입 전 필수 구현 21항목 (I-Series 25개 확정, E-15/S-5 명칭,  | V1 |
| CLAUDE-035 | V1 기술 스택 구현 (Ollama+GPT-4o mini, BGE-M3, Chroma, J | V1 |
| CLAUDE-114 | Guardrails 4-Layer 안전 필터 구현 (L1:NeMo + L2:Guardrai | V1,V2 |
| CLAUDE-176 | Guardrails L1+L2 초기 설정 | V0 |
| V0RD-002 | React ~39개 컴포넌트 구현 (Decision/Chat/Approval/Cost/Ev | V1 |
| D205-053 | 4레이어 Guardrails 연동 (NeMo/Guardrails AI/LlamaGuard/ | V1 |
| D207-002 | Layer 1 입력 방어: NeMo Guardrails 구현 | V1 |
| D207-003 | Layer 2 처리 방어: Guardrails AI 구현 | V1 |
| D207-004 | Layer 3 출력 방어: LlamaGuard 구현 | V1 |

### S6-RUST-006: Python-Rust JSON-RPC 메서드 (13개) (§6.2.2 L2974)
- Phase 미배정 Feature: **2건** (Phase 배정: 3건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| PB1-020 | Python-Rust JSON-RPC 2.0 프로토콜 구현 | V1 |
| PB1-031 | Python-Rust gRPC 전환 대응 | V2 |

### S6-RUST-009: config.rs (§6.2.3 L2989)
- Phase 미배정 Feature: **1건** (Phase 배정: 6건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| P30-027 | Runtime Brain Switching 구현 (실시간 뇌 전환) | V2 |

### S6-TEST-002: Rust Unit (cargo test ~8) (§6.3 L2999)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| PB5-004 | Rust cargo test IPC/subprocess 단위 테스트 구현 (8개) | V1 |

### S6-TEST-004: Integration (~14) (§6.3 L3001)
- Phase 미배정 Feature: **5건** (Phase 배정: 2건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| P30-012 | Brain Adapter 테스트 프레임워크 구현 (5 Adapter × 5 테스트유형) | V1 |
| D204-114 | 테스트 자동화 피라미드 (Unit 70%/Integration 25%/E2E 5%) | V1 |
| PB2-027 | 전체 테스트 디렉토리 구조 생성 (Python/React/Rust/통합) | V1 |
| PB5-001 | 3-Layer 테스트 피라미드 구조 + 테스트 ID 체계 (T-{layer}-{docID} | V1 |
| TEAM-031 | AgentTeamGateIntegration 구현 (5 Gates ↔ Agent Teams | V1 |

### S6-TEST-005: E2E (Playwright ~8) (§6.3 L3002)
- Phase 미배정 Feature: **7건** (Phase 배정: 2건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D203-084 | MCP 단일 표준 채택 및 서버 카탈로그 구현 (S11-001/S11-006) | V1,V2 |
| D203-088 | C8 크롤러 → MCP 기반 수집 구조 전환 (S14-A-010) | V1 |
| D205-095 | AI 브라우저 에이전트 (Playwright + AI 비전) | V1,V2 |
| D205-098 | 폼 자동 입력 (Playwright + AI 답변 제안) | V1 |
| PB5-009 | 테스트 인프라 구성 (도구 스택 + conftest.py 계층 + 실행 명령어) | V1 |
| AINV-009 | scraper_drift_handler.py Scraper Manager (Playwrig | V1 |
| AINV-093 | Scraper Manager Playwright 헤드리스 브라우저 (정기 스크래핑 + Sc | V1 |

### S6-TEST-007: AC 매핑 (50 AC → 79 테스트) (§6.3 L3019)
- Phase 미배정 Feature: **2건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| DD8-005 | D8 수용 기준 5개 (AC-D8-001~005) 구현 검증 | V1 |
| PB5-008 | 50 AC -> 79 테스트 케이스 매핑 구현 | V1 |

### S6-CICD-001: quality-python.yml (ruff+mypy) (§6.4 L3032)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| PB6-002 | 3개 언어 코드 품질 워크플로우 (Python ruff+mypy / Rust clippy+ | V1 |

### S6-CICD-003: quality-react.yml (eslint+tsc) (§6.4 L3034)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| PB6-002 | 3개 언어 코드 품질 워크플로우 (Python ruff+mypy / Rust clippy+ | V1 |

### S6-CICD-005: test-python.yml (§6.4 L3036)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| PB6-003 | 3개 언어 테스트 워크플로우 + 커버리지 합산 (Python pytest+Postgres  | V1 |

### S6-CICD-008: coverage-report.yml (§6.4 L3039)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| PB6-003 | 3개 언어 테스트 워크플로우 + 커버리지 합산 (Python pytest+Postgres  | V1 |

### S6-CICD-011: security.yml (audit) (§6.4 L3042)
- Phase 미배정 Feature: **2건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D207-010 | Supply Chain 보안 (npm audit/pip-audit/SBOM) | V1,V2 |
| PB6-010 | 보안 스캔 워크플로우 (의존성 취약점 + gitleaks + 라이선스 검사) | V1 |

### S6-CICD-012: build-docker.yml (§6.4 L3043)
- Phase 미배정 Feature: **2건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D203-095 | 에이전트 패키징 구현 (Docker/pip/YAML/의존성관리) | V2 |
| PB6-005 | Docker 이미지 빌드 워크플로우 (V2+ GHCR) | V2 |

### S6-CICD-013: deploy-v2.yml (Docker Compose) (§6.4 L3044)
- Phase 미배정 Feature: **10건** (Phase 배정: 3건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-036 | V2 기술 스택 마이그레이션 (Qdrant서버, Neo4j Community, Postgr | V2 |
| CLAUDE-201 | V2 Deploy: Docker Compose 구성 | V2 |
| D204-002 | V2 Docker Compose 셋업 절차 (Postgres 마이그레이션, Qdrant 헬 | V2 |
| D204-051 | V2 인프라 조합 (Docker Compose, Postgres+Qdrant, Alembi | V2 |
| D204-140 | 로컬 개발 환경 (Docker Compose 원클릭) | V1 |
| DA1-006 | Deploy 방식 전환 구현 (V1: 로컬, V2: Docker Compose, V3: K | V1,V2,V3 |
| PB6-008 | V2 Docker Compose 배포 워크플로우 + 서비스 정의 (deploy-v2.yml | V2 |
| PB7-014 | 블루-그린 배포 롤백 전략 구현 | V2 |
| AINV-047 | 14-Item Locked 기술 스택 인프라 구성 (Airflow/asyncio/Kafka | V1 |
| AINV-066 | Docker Compose 전체 스택 구성 (docker-compose.yml: Times | V0 |

### S6-CICD-014: deploy-v3.yml (K8s Helm) (§6.4 L3045)
- Phase 미배정 Feature: **4건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| P30-077 | 마이그레이션/배포 전략 구현 (Blue-Green, 환경분리) | V1 |
| D203-100 | 에이전트 V1→V2→V3 마이그레이션 구현 (Blue-Green 배포/롤백지원) | V2 |
| D204-181 | 배포/환경 분리 (Blue-Green, dev→staging→prod, Alembic) | V0,V1,V2,V3 |
| PB6-009 | V3 Kubernetes Helm 배포 워크플로우 (deploy-v3.yml) | V3 |

### S6-SEC-001: NeMo Guardrails (L1) (§6.5 L3053)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D207-002 | Layer 1 입력 방어: NeMo Guardrails 구현 | V1 |

### S6-SEC-002: Guardrails AI (L2) (§6.5 L3054)
- Phase 미배정 Feature: **7건** (Phase 배정: 1건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-035 | V1 기술 스택 구현 (Ollama+GPT-4o mini, BGE-M3, Chroma, J | V1 |
| CLAUDE-114 | Guardrails 4-Layer 안전 필터 구현 (L1:NeMo + L2:Guardrai | V1,V2 |
| D205-053 | 4레이어 Guardrails 연동 (NeMo/Guardrails AI/LlamaGuard/ | V1 |
| D207-003 | Layer 2 처리 방어: Guardrails AI 구현 | V1 |
| DA1-008 | Guardrails 3-Layer 방어 체계 구현 (NeMo + Guardrails AI  | V1,V2 |
| CLIB-059 | C8-ALT 가이드된 규칙 진화 (Reflexion + Self-RAG + Guardrai | V3 |
| TEAM-093 | 에이전트 Prompt Injection 방어 4계층 구현 (NeMo/Guardrails A | V1 |

### S6-SEC-003: LlamaGuard (L3) (§6.5 L3055)
- Phase 미배정 Feature: **8건** (Phase 배정: 3건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-036 | V2 기술 스택 마이그레이션 (Qdrant서버, Neo4j Community, Postgr | V2 |
| CLAUDE-114 | Guardrails 4-Layer 안전 필터 구현 (L1:NeMo + L2:Guardrai | V1,V2 |
| D202-099 | Llama 모델 Ollama 로컬 배포 구현 | V1,V2 |
| D205-053 | 4레이어 Guardrails 연동 (NeMo/Guardrails AI/LlamaGuard/ | V1 |
| D207-004 | Layer 3 출력 방어: LlamaGuard 구현 | V1 |
| DA1-008 | Guardrails 3-Layer 방어 체계 구현 (NeMo + Guardrails AI  | V1,V2 |
| PB3-011 | 가드레일 패키지 설치 (NeMo/GuardrailsAI V1 / Transformers V | V1,V2 |
| TEAM-093 | 에이전트 Prompt Injection 방어 4계층 구현 (NeMo/Guardrails A | V1 |

### S6-SEC-006: Autonomy 레벨 L0~L3 (§6.5 L3058)
- Phase 미배정 Feature: **17건** (Phase 배정: 14건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-031 | V0 진입 전 필수 구현 16항목 (통신 확정, IMPL 계층, 비용 상한, 디렉토리, c | V0 |
| CLAUDE-046 | 4계층 메모리 시스템 구현 (L0 Session 7일, L1 Project 90일, L2  | V1,V2,V3 |
| CLAUDE-049 | SDAR I-25 시스템 구현 (5-Layer Detection→Diagnosis→Pres | V2,V3 |
| CLAUDE-114 | Guardrails 4-Layer 안전 필터 구현 (L1:NeMo + L2:Guardrai | V1,V2 |
| P30-011 | 메모리 저장 형식 JSON+SQLite 하이브리드 구현 | V0 |
| P30-016 | Fallback/Retry/Recovery 시스템 구현 | V1 |
| P30-041 | 파일 단위 저장 스펙 구현 (7 공통 항목) | V0 |
| P30-048 | 메모리 승격/강등 트리거 구현 (L0→L1→L2, 강등/아카이브) | V1 |
| BASE-002 | 4계층 메모리 TTL 정책 구현 (L0:7일/L1:90일/L2:영구/L3:영구) | V1 |
| D202-107 | 4-Level 평가 프레임워크 구현 (L1단위/L2에이전트/L3시스템/L4안전) | V1,V2 |

### S6-SEC-009: 승인 타임아웃 10분 auto-deny (§6.5 L3061)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-118 | 승인 타임아웃 구현 (10분 미응답 → 자동 거부) | V1 |

### S6-SEC-010: SQLCipher 암호화 (§6.5 L3062)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| PB7-013 | BackupManager 백업/복원 모듈 구현 | V2 |

### S6-SEC-011: API Key 관리 (§6.5 L3063)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D204-098 | API Key 관리 (.env+keyring, 90일 만료, Key Scoping) | V1 |

### S6-SEC-013: HMAC-SHA256 Agent 인증 (§6.5 L3065)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-165 | HMAC-SHA256 키관리/검증 상세화 (Agent Teams MessageBus) (C | V2 |

### S6-SEC-015: DEC-003 도구 승인 Allowlist (§6.5 L3067)
- Phase 미배정 Feature: **3건** (Phase 배정: 1건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-097 | 도구 승인 Allowlist 구현 (읽기전용=자동, 외부API/쓰기/코드실행=확인 필요) | V1 |
| CLAUDE-178 | 15개 보안 항목 (S7E + DEC-003 Allowlist) 구현 | V1 |
| D205-005 | Allowlist 자동승인 / 명시적 확인 이원화 도구 승인 | V1 |

### S6-MCP-001: MCP Bridge Layer (§6.6 L3075)
- Phase 미배정 Feature: **12건** (Phase 배정: 9건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-002 | 통신 계층 구현 (React UI ↔ Tauri IPC ↔ Rust Backend ↔ JS | V0,V1 |
| CLAUDE-035 | V1 기술 스택 구현 (Ollama+GPT-4o mini, BGE-M3, Chroma, J | V1 |
| CLAUDE-098 | MCP Streamable HTTP 전송 구현 | V1 |
| D203-013 | MCP 서버 구현 아키텍처 (Stdio/Streamable HTTP/WebSocket) | V1,V2,V3 |
| D203-059 | 외부 도구 E-* MCP 전송 계층 확정 (Streamable HTTP) 및 접근 게이트  | V1 |
| D203-076 | 스트리밍 프로토콜 구현 (Streamable HTTP/WebSocket/gRPC/NATS) | V1,V2,V3 |
| D203-085 | Claude Tool Use → MCP Bridge Layer 구현 (S09-B29-001 | V1 |
| D203-088 | C8 크롤러 → MCP 기반 수집 구조 전환 (S14-A-010) | V1 |
| D203-089 | MCP Python SDK 통합 구현 (MCPClientManager/Context Pro | V1 |
| D203-116 | MCP 2.0 Streamable HTTP 전송 계층 구현 + OAuth 2.1 인증 | V1 |

### S6-MCP-002: MCP Server (20+ tools) (§6.6 L3076)
- Phase 미배정 Feature: **4건** (Phase 배정: 1건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D203-044 | A2A ↔ MCP 브리지 (양방향 변환) | V2 |
| D203-104 | 웹 검색 MCP Server 구현 (Brave Search/Tavily/Serper 연동) | V1 |
| D203-105 | 금융 데이터 수집 MCP Server 5종 구현 (DART/EDGAR/Yahoo Finan | V1,V2 |
| D203-106 | Webhook MCP Server 구현 (register_webhook/list_webho | V2 |

### S6-MCP-008: mcp.search.tavily (§6.6 L3089)
- Phase 미배정 Feature: **3건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D202-034 | 실시간 웹 검색 통합 구현 (S7B-006) | V1 |
| D202-119 | WebSearchTool MCP 서버 구현 (Tavily/SerpAPI) | V1 |
| D203-104 | 웹 검색 MCP Server 구현 (Brave Search/Tavily/Serper 연동) | V1 |

### S6-MCP-010: mcp.code.e2b (§6.6 L3091)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D202-006 | Docker 기반 코드 실행 샌드박스 구현 | V1 |

### S6-MCP-016: mcp.browser.playwright (§6.6 L3097)
- Phase 미배정 Feature: **1건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D203-088 | C8 크롤러 → MCP 기반 수집 구조 전환 (S14-A-010) | V1 |

### S6-AT-001: V1 Agent 기본 구조 (Lead+2 Sub) (§6.7 L3109)
- Phase 미배정 Feature: **8건** (Phase 배정: 5건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-145 | Agent Teams vs FREEZE 충돌 해결 (V2-003): Lead Agent 단 | V1,V2 |
| CLAUDE-248 | Lead Agent + Sub-Agents 위임 구현 (최대 깊이 3단계) | V1,V2,V3 |
| CLAUDE-250 | 에이전트 수 확장 구현 (V1=3, V2=10, V3=50+) | V1,V2,V3 |
| D203-096 | 에이전트 수평 스케일링 구현 (Kubernetes 기반 오토스케일링) | V3 |
| TEAM-002 | Lead Agent 상태 머신 구현 (IDLE→PLANNING→ASSIGNING→MONIT | V1 |
| TEAM-007 | InMemoryDispatcher 구현 (V1 MessageBus) | V1 |
| TEAM-008 | RedisMessageBus 구현 (V2+ MessageBus) | V2 |
| TEAM-098 | I-5 Decision Engine 확장 (Lead Agent DelegationPlan  | V1 |

### S6-AT-002: Sequential/Parallel 협업 패턴 (§6.7 L3110)
- Phase 미배정 Feature: **6건** (Phase 배정: 2건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-249 | 5가지 협업 패턴 구현 (Sequential/Parallel/Debate/Superviso | V1,V2,V3 |
| MSTR-011 | 12개 워크플로우 패턴 카탈로그 구현 (Sequential~Event Sourcing) | V1 |
| D205-047 | Prompt Chaining 패턴 (Sequential/Branching/Aggregati | V1 |
| TEAM-014 | TaskDecomposer 구현 (복합 작업→하위 작업 분해) | V1 |
| TEAM-025 | Sequential 협업 패턴 구현 | V1 |
| TEAM-026 | Parallel 협업 패턴 구현 (Semaphore 기반 최대 병렬 수 제한) | V1 |

### S6-AT-004: MessageBus In-Memory Queue (§6.7 L3112)
- Phase 미배정 Feature: **8건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-033 | V2 진입 전 필수 구현 14항목 (전환조건 6개, Agent Teams, STEP7 ~1 | V2 |
| CLAUDE-145 | Agent Teams vs FREEZE 충돌 해결 (V2-003): Lead Agent 단 | V1,V2 |
| CLAUDE-165 | HMAC-SHA256 키관리/검증 상세화 (Agent Teams MessageBus) (C | V2 |
| CLAUDE-185 | MessageBus 구현 결정 (Redis vs In-Memory) | V2 |
| TEAM-007 | InMemoryDispatcher 구현 (V1 MessageBus) | V1 |
| TEAM-008 | RedisMessageBus 구현 (V2+ MessageBus) | V2 |
| TEAM-009 | MessageBus ORANGE CORE Auditor (메시지 감사/HMAC 검증/정책  | V1 |
| TEAM-109 | HMAC 무결성 서명 모듈 구현 (AgentMessage 서명/검증) | V1 |

### S6-AT-005: Lead Agent (ORANGE CORE) (§6.7 L3120)
- Phase 미배정 Feature: **16건** (Phase 배정: 10건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-001 | 4계층 아키텍처 구현 (Front Mini LLM → ORANGE CORE → BLUE N | V0,V1,V2,V3 |
| CLAUDE-051 | V1 주차별 구현 계획 (1~2주 ORANGE CORE, 3~4주 Storage/RAG,  | V1 |
| CLAUDE-145 | Agent Teams vs FREEZE 충돌 해결 (V2-003): Lead Agent 단 | V1,V2 |
| CLAUDE-248 | Lead Agent + Sub-Agents 위임 구현 (최대 깊이 3단계) | V1,V2,V3 |
| CLAUDE-254 | 주 1~2: ORANGE CORE 기본 파이프라인 구현 (I-1→I-2→I-5→I-8) | V1 |
| P30-018 | 2윈도우 구조 구현 (Builder View + Hologram View) | V1 |
| D201-001 | 3-Layer 아키텍처 구현 (ORANGE CORE ↔ BLUE NODE ↔ INFRA-C | V0,V1,V2,V3 |
| D202-005 | Runnable 프로토콜 구현 (ADD-001) | V1 |
| D203-007 | Magentic-One 패턴 적용 (Orchestrator/WebSurfer/Coder 등 | V2 |
| AINV-082 | ORANGE CORE 정책/비용/Self-check/라우팅 모듈 | V3 |

### S6-AT-006: Research Agent (BLUE NODE) (§6.7 L3121)
- Phase 미배정 Feature: **1건** (Phase 배정: 1건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D203-104 | 웹 검색 MCP Server 구현 (Brave Search/Tavily/Serper 연동) | V1 |

### S6-AT-007: Coding Agent (BLUE NODE) (§6.7 L3122)
- Phase 미배정 Feature: **1건** (Phase 배정: 1건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| TEAM-091 | FileOwnership 모델 구현 (writable/readonly/forbidden 경 | V1 |

### S6-AT-012: V2 Critic Agent (§6.7 L3132)
- Phase 미배정 Feature: **9건** (Phase 배정: 8건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-049 | SDAR I-25 시스템 구현 (5-Layer Detection→Diagnosis→Pres | V2,V3 |
| CLAUDE-245 | SDAR 5-Layer 구현 (Detection→Diagnosis→Prescription→ | V2,V3 |
| CLIB-025 | 품질 예측 알고리즘 (RAGAS + LLM Judge + CoV) | V2 |
| SDAR-014 | Repair Plan Generation - 수리 계획 수립 (Pre-conditions/ | V1 |
| SDAR-020 | Post-Repair Validation 구현 - post_conditions 충족 확인/ | V1 |
| SDAR-021 | Regression Check 구현 - Blast Radius 내 모듈 상태 확인/성능 지 | V2 |
| SDAR-022 | Rollback Trigger 구현 - 롤백 조건 판정 및 자동 롤백 실행 (스냅샷 복원/ | V1 |
| SDAR-024 | Layer 5 이벤트 발행 구현 (verification.started/passed/war | V1 |
| SDAR-069 | SDAR 모듈 디렉토리 구조 생성 (sdar/ 하위 detection/diagnosis/p | V1 |

### S6-AT-014: LOCK-AT 아키텍처 제약 (17건) (§6.7 L3142)
- Phase 미배정 Feature: **3건** (Phase 배정: 2건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| TEAM-107 | LOCK-AT-001 V1 자체 경량 프레임워크 + 외부 엔진 어댑터 구현 | V1 |
| TEAM-108 | LOCK-AT-017 노코드 빌더 n8n + Flowise 듀얼 구조 | V2 |
| TEAM-109 | HMAC 무결성 서명 모듈 구현 (AgentMessage 서명/검증) | V1 |

### S6-AT-015: Agent Marketplace (§6.7 L3136)
- Phase 미배정 Feature: **4건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| CLAUDE-034 | V3 진입 전 필수 구현 11항목 (K8s 배포, S-8 거버넌스, 비용 재산정, Grap | V3 |
| CLAUDE-193 | Agent Marketplace 기준 확정 구현 | V3 |
| D205-049 | Agent Marketplace (에이전트/워크플로우 템플릿 공유) | V3 |
| TEAM-106 | DEFER-AT-003 Agent Marketplace 등록/공유 기준 | V2 |

### S6-AT-016: n8n + Flowise 노코드 빌더 (§6.7 L3160)
- Phase 미배정 Feature: **2건** (Phase 배정: 0건)

| feature_id | feature_name | version_scope |
|-----------|-------------|--------------|
| D205-054 | 듀얼 에이전트 (코드+노코드) + n8n/Flowise 노코드 빌더 | V1,V2 |
| TEAM-108 | LOCK-AT-017 노코드 빌더 n8n + Flowise 듀얼 구조 | V2 |

## 4. [임무 2] M-1~M-4 MISSING → §6 재확인

### §6에서 발견됨 (7건) → PARTIAL 재판정

| feature_id | feature_name | severity | agent | §6 위치 |
|-----------|-------------|---------|-------|--------|
| P30-041 | 파일 단위 저장 스펙 구현 (7 공통 항목) | LOW | M-1 | §6.5 |
| D207-032 | 자율 운영 수준 4단계 (L0 FULL_MANUAL~L3 FULL_AUT | LOW | M-4 | §6.5 |
| D208-090 | P7-UIS(4건) + P7-NSP(1건) + P7-LOG(1건) + P | MEDIUM | M-3 | §6.1.1 |
| PB7-013 | BackupManager 백업/복원 모듈 구현 | MEDIUM | M-3 | §6.5 |
| TEAM-021 | TradingAnalysisAgent 구현 (투자 분석, AINV 연동) | MEDIUM | M-3 | §6.7 |
| D206-025 | 계층별 TTL 정책 구현 (L0 세션종료/L1 90일/L2 무기한/L3  | LOW | M-4 | §6.5 |
| S7JM-009 | 공간 이해 및 AR 연동 | MEDIUM | M-4 | §6.1.5 |

### §6에서도 미발견 (1067건) → MISSING 유지

> 이 항목들은 M-5b에서 §6.8~§6.13 + §7 검색 예정
