# 02_lock-freeze-registry — LOCK/FREEZE 레지스트리 인덱스

> **도메인**: 0-0 Governance-Rules-Meta
> **서브폴더 목적**: LOCK 값 23건, FREEZE 값 2건, K-값 레지스트리 11건, SLA 목표치 + 도메인별 DEFINED-HERE 항목 관리
> **정본 출처**: Part2 §1 config.v1.toml (L246-326) + PHASE_B4 §3 + 각 도메인 AUTHORITY_CHAIN
> **최종 갱신**: 2026-03-25 (S7-1 CAT-16)

---

## 포함 항목

| 항목 | 규칙서 위치 | 건수 |
|------|-----------|------|
| LOCK 값 전체 목록 | §2.5.1 (L1~L23) | 23건 |
| FREEZE 값 전체 목록 | §2.5.2 (F1~F2) | 2건 |
| K-값 레지스트리 | §2.6 (K-1~K-11) | 11건 |
| SLA 목표치 | §2.7 | 5개 지표 |
| LOCK 값 검증 체크리스트 | §3.6.5 | 10건 |
| SOURCE_CONFLICT 전수 인덱스 | §3.6.6 (SC-01~SC-15) | 15건 |
| **도메인 DEFINED-HERE 항목** | **아래 §DH** | **40건** |

---

## §DH: 도메인 DEFINED-HERE 동결 항목 레지스트리

> **목적**: 각 도메인 AUTHORITY_CHAIN에서 "DEFINED-HERE"로 표기된 항목의 중앙 추적.
> 이 항목들은 해당 도메인이 정의 원본(정본 소유자)이며, Phase 5 이후 동결됨.
> **등록일**: 2026-03-25 (S7-1 CAT-16 전수 추출)

### 2-1_Blue-Node-Architecture (1건)

| LOCK ID | 항목 | 값 | 동결 상태 |
|---------|------|-----|----------|
| LOCK-BN-05a | Node Lifecycle States | 8 states: CANDIDATE, LAZY, ACTIVATING, ACTIVE, BUSY, DRAINING, SUSPENDED, TERMINATED | Phase 5 frozen |

### 2-2_COND-Modules-Detail (3건)

| LOCK ID | 항목 | 값 | 동결 상태 |
|---------|------|-----|----------|
| LOCK-CD-01 | COND 코드 체계 | CAT-{A~G} + COND-{3-digit} | DEFINED-HERE (D2.0-01 §5 확장) |
| LOCK-CD-02 | E-series 분류 체계 | E-{3-digit} | DEFINED-HERE (D2.0-01 §5.8 확장) |
| LOCK-CD-03 | BaseModule ABC 인터페이스 | initialize/execute/health_check/shutdown | DEFINED-HERE (D2.0-02 통합 설계) |

### 3-2_Multimodal-Processing (5건)

| LOCK ID | 항목 | 값 | 동결 상태 |
|---------|------|-----|----------|
| LOCK-MM-03 | 처리 파이프라인 순서 | Input→Validation→Preprocess→Routing→Process→Integration | DEFINED-HERE supplement |
| LOCK-MM-05 | MultimodalMessage 스키마 | UUID v7, content[], metadata | Phase 5 frozen |
| LOCK-MM-07 | CLIP 임베딩 차원 | 768d (ViT-L/14@336) | Phase 5 frozen |
| LOCK-MM-08 | 오디오 샘플링 레이트 | 16kHz mono PCM | Phase 5 frozen |
| LOCK-MM-09 | 비디오 프레임 제한 | max_frames=100 | Phase 5 frozen |

### 4-1_Rust-Tauri-Infrastructure (3건 + 7건 unlabeled)

| LOCK ID | 항목 | 값 | 동결 상태 |
|---------|------|-----|----------|
| LOCK-RT-12 | Python 헬스체크 간격 | 15s interval, 5s timeout, 3 failures → restart | Phase 5 frozen |
| LOCK-RT-13 | 재시작 백오프 정책 | abnormal: 5× 1→2→4→8→16s; OOM: 3× 5s fixed; HC: 3× 2→4→8s | Phase 5 frozen |
| LOCK-RT-14 | TauriError enum | 7 variants: NotFound, ValidationError, PythonBridgeError, IoError, Timeout, PermissionDenied, InternalError | Phase 5 frozen |

> **참고**: 4-1 AUTHORITY_CHAIN은 LOCK-RT-01~15 (15건)로 확정 완료(Phase 2 변경 0건)되었으며, LOCK-RT-15는 'stderr 로그 분리'에 부여됨. 과거 '미명명 7건'(IPC signatures, Serde models, JSON-RPC schemas, Python process mgmt, SLA, security checklist, monitoring metrics)은 신규 ID 없이 기존 LOCK-RT-01(IPC 72-매트릭스)/-02(SLA 매핑)/-03·-11(JSON-RPC)/-12·-13(프로세스 관리)/-14(에러 enum) 등에 흡수됨 — LOCK-RT-16~21은 존재하지 않으며, 본 §DH 중앙 총계는 변동 없음(40건 유지).

### 6-5_SDAR-System (4건)

| DH ID | 항목 | 설명 | 동결 상태 |
|-------|------|------|----------|
| DH-SDAR-1 | 7-State 예외 전환 조건 | Detection/Diagnosis 타임아웃, Gate REJECT → ESCALATED | DEFINED-HERE |
| DH-SDAR-2 | 레이어별 오류 코드 카탈로그 | FailureCodes per Layer | DEFINED-HERE |
| DH-SDAR-3 | SDAR 모니터링 메트릭 | resolution rate, avg repair time, escalation ratio | DEFINED-HERE |
| DH-SDAR-4 | Self-evo 통합 데이터 형식 | repair_result event schema, S-Module feedback interface | DEFINED-HERE |

### 6-6_Self-Evolution-System (5건)

| DH ID | 항목 | 설명 | 동결 상태 |
|-------|------|------|----------|
| DH-SEVO-1 | S-Module 순차 활성 안정성 기준 | error <1%, schema 100%, I-Module ≥99%, resource <80%, 7일 | DEFINED-HERE |
| DH-SEVO-2 | S-8 거버넌스 규칙 엔진 상세 | allow/approve/prohibit 분류, audit log, rollback | DEFINED-HERE |
| DH-SEVO-3 | 모델 업그레이드 카나리 5단계 | Shadow → 5% → 25% → 75% → 100%, QoD gates | DEFINED-HERE |
| DH-SEVO-4 | SDAR ↔ Self-evo 양방향 통합 인터페이스 | repair_result event, repair pattern suggestion schema | DEFINED-HERE |
| DH-SEVO-5 | S-1 → 1-2 도메인 배치 결정 | CONFLICT_LOG SEVO-C002 참조 | DEFINED-HERE |

### 6-7_RT-BNP-DCL (5건)

| DH ID | 항목 | 설명 | 동결 상태 |
|-------|------|------|----------|
| DH-BNP-1 | Breaking Detector V2+ ML 파라미터 | FinBERT config, training data, refresh cycle, thresholds | DEFINED-HERE |
| DH-BNP-2 | 소스별 수집 어댑터 구현 상세 | T1~T4 connection/retry/error handling | DEFINED-HERE |
| DH-BNP-3 | DCL Aggregator 알고리즘 | 3-channel data integration, conflict resolution, priority | DEFINED-HERE |
| DH-BNP-4 | DCL 백그라운드 요약 생성 프로토콜 | summary model, token limit, context window | DEFINED-HERE |
| DH-BNP-5 | DCL-GEO 초기 소스 화이트리스트 | V2 DCL-GEO channel RSS sources | DEFINED-HERE |

### 6-9_Brain-Adapter-HAL (3건)

| DH ID | 항목 | 설명 | 동결 상태 |
|-------|------|------|----------|
| DH-BA-1 | LLM 라우팅 결정 트리 상세 | 4축(복잡도/도메인/비용/가용성) 분기 로직 + 모델 매핑 | DEFINED-HERE |
| DH-BA-2 | 폴백 시나리오 8건 | F1(타임아웃)~F8(모델 미등록) 상세 처리 절차 | DEFINED-HERE |
| DH-BA-3 | HAL 추상화 인터페이스 | ConnectorResponse 확장 필드(tool_calls, qod_hint), HAL adapter 계층 | DEFINED-HERE |

### 6-8_Cloud-Library (5건)

| DH ID | 항목 | 설명 | 동결 상태 |
|-------|------|------|----------|
| DH-CL-1 | L1~L10 레이어별 알고리즘 상세 | input/output/processing logic/error codes | DEFINED-HERE |
| DH-CL-2 | 클라우드 배포 전략 | Docker/K8s config, env-specific settings | DEFINED-HERE |
| DH-CL-3 | 스케일링 정책 | horizontal/vertical thresholds, auto-scaling rules | DEFINED-HERE |
| DH-CL-4 | CDN 캐시 전략 | static/dynamic content cache policy, TTL tiers | DEFINED-HERE |
| DH-CL-5 | v12 확장 구현 상세 | domain-specific items from Part2 v12 10 items | DEFINED-HERE |

---

## 관리 규칙

- LOCK 값 변경은 **본 도메인에서만 가능** (R-T0-2)
- 변경 시: 규칙서 §2.5 갱신 → CONFLICT_LOG 기록 → 영향 도메인 AUTHORITY_CHAIN 통지
- config.v1.toml 리터럴과 문서 간 불일치 발견 시: PHASE_B4 §3 정본 기준으로 해결
- **DEFINED-HERE 항목**: 해당 도메인 AUTHORITY_CHAIN이 정의 원본. 변경 시 본 레지스트리 동시 갱신 필수

---

## 변경 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2026-03-25 | S7-1 CAT-16: §DH 섹션 추가 — 8개 도메인 37건 DEFINED-HERE 항목 전수 등재 |
| 2026-03-26 | S8-6: 6-9 Brain-Adapter-HAL DH-BA-1~3 추가 (37→40건, 9개 도메인) |
