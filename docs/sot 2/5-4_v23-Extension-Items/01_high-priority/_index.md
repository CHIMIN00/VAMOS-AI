# HIGH 우선순위 32건 추적 인덱스

> **범위**: v23 확장 항목 중 HIGH 우선순위 — 즉시 착수 대상
> **항목 수**: 32건 (V2-P2 24건 + V2-P3 5건 + V3-P3 3건)
> **상태**: 전 항목 SHELL 초기값
> **LOCK 참조**: LOCK-V23-03 (HIGH 32건 목록 — 변경 시 Part2 + 인덱스 동시 변경 필요)
> **작성일**: 2026-04-12
> **세션**: P1-1

---

## 교차 참조

| 정본 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| V23_EXTENSION_ITEMS_구조화_종합계획서.md | §6.1 01_high-priority/ | HIGH 32건 정본 테이블 |
| V23_EXTENSION_ITEMS_인덱스.md | V2-P2, V2-P3, V3-P3 섹션 | 87건 정본 인덱스 (HIGH 항목 교차 확인) |
| AUTHORITY_CHAIN.md | LOCK-V23-03 | HIGH 32건 목록 보호 |
| Part2 구현가이드 | V2-Phase 2/3, V3-Phase 3 | 항목 정의 정본 (Phase 배정, 우선순위) |

---

## 상태 범례

| 상태 | 설명 |
|------|------|
| SHELL | 이름 + 1줄 설명만 존재, 상세 미작성 |
| STUB | 이름 + 3~5줄 설명 존재, 스키마 미정의 |
| REF | 다른 SOT 2 문서에서 상세화 완료 (참조 경로 기재) |

---

## V2-Phase 2 HIGH (24건)

| # | 항목명 | 소스 ID | 소스 Phase | SOT 2 참조 | 상태 | STAGE 9 추적 상태 |
|---|--------|---------|-----------|-----------|------|---------------------|
| 1 | Advanced Reasoning Chain | V2-P2-11 | V2-Phase 2 | `1-1_Verifier-Reasoning-Engines/` | SHELL | Part2 대기 (SHELL initial) |
| 2 | Multi-step Planning Engine | V2-P2-12 | V2-Phase 2 | `1-1_Verifier-Reasoning-Engines/` | SHELL | Part2 대기 (SHELL initial) |
| 3 | Self-correction Loop | V2-P2-13 | V2-Phase 2 | `1-1_Verifier-Reasoning-Engines/` | SHELL | Part2 대기 (SHELL initial) |
| 4 | Confidence Calibration | V2-P2-14 | V2-Phase 2 | `1-1_Verifier-Reasoning-Engines/` | SHELL | Part2 대기 (SHELL initial) |
| 5 | Episodic Memory Engine | V2-P2-16 | V2-Phase 2 | `2-1_Blue-Node-Architecture/` | SHELL | Part2 대기 (SHELL initial) |
| 6 | Semantic Memory Consolidation | V2-P2-17 | V2-Phase 2 | `2-1_Blue-Node-Architecture/` | SHELL | Part2 대기 (SHELL initial) |
| 7 | Cross-session Recall | V2-P2-20 | V2-Phase 2 | `2-1_Blue-Node-Architecture/` | SHELL | Part2 대기 (SHELL initial) |
| 8 | Knowledge Graph Builder v2 | V2-P2-21 | V2-Phase 2 | `3-3_PKM-Knowledge-Management/` | SHELL | Part2 대기 (SHELL initial) |
| 9 | ColBERT v3 Integration | V2-P2-24 | V2-Phase 2 | `2-2_COND-Modules-Detail/` | SHELL | Part2 대기 (SHELL initial) |
| 10 | Self-RAG Implementation | V2-P2-25 | V2-Phase 2 | `2-2_COND-Modules-Detail/` | SHELL | Part2 대기 (SHELL initial) |
| 11 | CRAG (Corrective RAG) | V2-P2-26 | V2-Phase 2 | `2-2_COND-Modules-Detail/` | SHELL | Part2 대기 (SHELL initial) |
| 12 | Multi-agent Orchestrator | V2-P2-31 | V2-Phase 2 | `3-8_Conversation-A2A/` | SHELL | Part2 대기 (SHELL initial) |
| 13 | Task Decomposition Engine | V2-P2-33 | V2-Phase 2 | `3-4_Workflow-RPA/` | SHELL | Part2 대기 (SHELL initial) |
| 14 | Human-in-the-Loop Protocol v2 | V2-P2-36 | V2-Phase 2 | `3-4_Workflow-RPA/` | SHELL | Part2 대기 (SHELL initial) |
| 15 | Voice Input/Output | V2-P2-38 | V2-Phase 2 | `3-2_Multimodal-Processing/` | SHELL | Part2 대기 (SHELL initial) |
| 16 | Accessibility Compliance (WCAG 2.1 AA) | V2-P2-41 | V2-Phase 2 | `3-7_Developer-Tools-API-SDK/` | SHELL | Part2 대기 (SHELL initial) |
| 17 | Spaced Repetition Engine v2 | V2-P2-42 | V2-Phase 2 | `3-5_Education-Learning/` | SHELL | Part2 대기 (SHELL initial) |
| 18 | Adaptive Learning Path | V2-P2-43 | V2-Phase 2 | `3-5_Education-Learning/` | SHELL | Part2 대기 (SHELL initial) |
| 19 | Emotion Detection v2 | V2-P2-45 | V2-Phase 2 | `3-6_Health-Wellness-EmotionAI/` | SHELL | Part2 대기 (SHELL initial) |
| 20 | Portfolio Optimizer | V2-P2-48 | V2-Phase 2 | `Ai-investing-detail/` | SHELL | Part2 대기 (SHELL initial) |
| 21 | Plugin Architecture v2 | V2-P2-51 | V2-Phase 2 | `3-7_Developer-Tools-API-SDK/` | SHELL | Part2 대기 (SHELL initial) |
| 22 | Auto-update Mechanism | V2-P2-53 | V2-Phase 2 | `4-1_Rust-Tauri-Infrastructure/` | SHELL | Part2 대기 (SHELL initial) |
| 23 | End-to-End Encryption | V2-P2-56 | V2-Phase 2 | `4-1_Rust-Tauri-Infrastructure/` | SHELL | Part2 대기 (SHELL initial) |
| 24 | Backup & Restore | V2-P2-57 | V2-Phase 2 | `4-1_Rust-Tauri-Infrastructure/` | SHELL | Part2 대기 (SHELL initial) |

## V2-Phase 3 HIGH (5건)

| # | 항목명 | 소스 ID | 소스 Phase | SOT 2 참조 | 상태 | STAGE 9 추적 상태 |
|---|--------|---------|-----------|-----------|------|---------------------|
| 25 | Sparse Attention Implementation | V2-P3-10 | V2-Phase 3 | `1-1_Verifier-Reasoning-Engines/` | SHELL | Part2 대기 (SHELL initial) |
| 26 | Mixture-of-Experts Routing | V2-P3-11 | V2-Phase 3 | `1-1_Verifier-Reasoning-Engines/` | SHELL | Part2 대기 (SHELL initial) |
| 27 | Advanced A2A Protocol | V2-P3-14 | V2-Phase 3 | `3-8_Conversation-A2A/` | SHELL | Part2 대기 (SHELL initial) |
| 28 | Natural Language Workflow | V2-P3-16 | V2-Phase 3 | `3-4_Workflow-RPA/` | SHELL | Part2 대기 (SHELL initial) |
| 29 | Privacy-preserving Inference | V2-P3-21 | V2-Phase 3 | `4-1_Rust-Tauri-Infrastructure/` | SHELL | Part2 대기 (SHELL initial) |

## V3-Phase 3 HIGH (3건)

| # | 항목명 | 소스 ID | 소스 Phase | SOT 2 참조 | 상태 | STAGE 9 추적 상태 |
|---|--------|---------|-----------|-----------|------|---------------------|
| 30 | AGI Safety Framework | V3-P3-11 | V3-Phase 3 | `1-1_Verifier-Reasoning-Engines/` | SHELL | Part2 대기 (SHELL initial) |
| 31 | Emergent Behavior Monitor | V3-P3-12 | V3-Phase 3 | `4-4_MLOps-LLMOps/` | SHELL | Part2 대기 (SHELL initial) |
| 32 | AI Ethics Governance Module | V3-P3-21 | V3-Phase 3 | `3-9_Business-Model-Strategy/` | SHELL | Part2 대기 (SHELL initial) |

---

## 검산

| 소스 Phase | 항목 수 | 비고 |
|-----------|---------|------|
| V2-Phase 2 | 24 | #1~#24 |
| V2-Phase 3 | 5 | #25~#29 (V2-P3-10, 11, 14, 16, 21) |
| V3-Phase 3 | 3 | #30~#32 (V3-P3-11, 12, 21) |
| **합계** | **32** | LOCK-V23-03 정본 32건과 일치 |

> **V2-P2 LOW = 0건 확인**: V2-P2 #11~#61 전부 HIGH 또는 MEDIUM (인덱스 원본 전수 대조 완료)

---

## SOT 2 참조 폴더 분포

| SOT 2 폴더 | HIGH 항목 수 | 해당 소스 ID |
|-----------|------------|------------|
| `1-1_Verifier-Reasoning-Engines/` | 7 | V2-P2-11~14, V2-P3-10~11, V3-P3-11 |
| `2-1_Blue-Node-Architecture/` | 3 | V2-P2-16~17, V2-P2-20 |
| `2-2_COND-Modules-Detail/` | 3 | V2-P2-24~26 |
| `3-2_Multimodal-Processing/` | 1 | V2-P2-38 |
| `3-3_PKM-Knowledge-Management/` | 1 | V2-P2-21 |
| `3-4_Workflow-RPA/` | 3 | V2-P2-33, V2-P2-36, V2-P3-16 |
| `3-5_Education-Learning/` | 2 | V2-P2-42~43 |
| `3-6_Health-Wellness-EmotionAI/` | 1 | V2-P2-45 |
| `3-7_Developer-Tools-API-SDK/` | 2 | V2-P2-41, V2-P2-51 |
| `3-8_Conversation-A2A/` | 2 | V2-P2-31, V2-P3-14 |
| `3-9_Business-Model-Strategy/` | 1 | V3-P3-21 |
| `4-1_Rust-Tauri-Infrastructure/` | 4 | V2-P2-53, V2-P2-56~57, V2-P3-21 |
| `4-4_MLOps-LLMOps/` | 1 | V3-P3-12 |
| `Ai-investing-detail/` | 1 | V2-P2-48 |
| **합계** | **32** | 14개 폴더 |

---

## 교차 대조 결과

### 인덱스 원본 대조

종합계획서 §6.1 01_high-priority/ 테이블 32건과 V23_EXTENSION_ITEMS_인덱스.md의 HIGH 항목을 1:1 교차 대조한 결과:

- **항목명 일치**: 32/32 (100%)
- **소스 ID 일치**: 32/32 (100%)
- **SOT 2 참조 일치**: 32/32 (100%)
- **누락 항목**: 0건
- **초과 항목**: 0건

---

## Phase 2 테스트 시나리오

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T-01 | HIGH 32건 전수 카운트 검증 | _index.md 파싱하여 행 수 집계 | 정확히 32행 |
| T-02 | 소스 ID 유일성 검증 | 소스 ID 열 중복 검사 | 32개 모두 고유 |
| T-03 | LOCK-V23-03 항목 목록 대조 | V23_EXTENSION_ITEMS_인덱스.md HIGH 항목 + 종합계획서 §6.1/부록 A.2 의 32건 목록과 교차 비교 (AUTHORITY_CHAIN.md LOCK-V23-03은 항목 목록 미수록, 정본 출처만 지정) | 32건 목록 완전 일치 |
| T-04 | 인덱스 원본 항목명 정합성 | V23_EXTENSION_ITEMS_인덱스.md와 항목명 diff | 0건 차이 |
| T-05 | SOT 2 참조 폴더 존재 확인 | 14개 SOT 2 폴더 실제 존재 여부 fs.stat | 14/14 존재 |
| T-06 | 상태 열 초기값 검증 | 상태 열 전수 스캔 | 전부 SHELL |
| T-07 | Phase별 검산 정합성 | V2-P2(24) + V2-P3(5) + V3-P3(3) 합산 | = 32 |
| T-08 | 소스 Phase 열 값 검증 | 소스 Phase 열이 V2-Phase 2/V2-Phase 3/V3-Phase 3 중 하나 | 32건 모두 유효 |
| T-09 | 항목 번호 연속성 검증 | # 열이 1~32 연속 | 누락/중복 0건 |
| T-10 | MEDIUM/LOW 항목 혼입 검증 | 인덱스 원본에서 MEDIUM/LOW 태깅된 항목이 본 파일에 없는지 확인 | 혼입 0건 |
| T-11 | 검산 섹션 합계 일치 | 검산 테이블 합계와 실제 행 수 비교 | 일치 |
| T-12 | SOT 2 참조 폴더 분포 합계 | 분포 테이블 합계와 32건 일치 | 일치 |

---

## STAGE 9 추적 검산 (B-1.4 NEW, 2026-05-12, chain s9_39_b_1)

> **STAGE 9 추적 합계**: HIGH 32 (V2-P2 24 + V2-P3 5 + V3-P3 3) = **32** ✅ (Part2 로드맵 종속 추적 전용)

| 검산 항목 | 값 | 결과 |
|---|:-:|:-:|
| V2-Phase 2 | 24 | ✅ |
| V2-Phase 3 | 5 | ✅ |
| V3-Phase 3 | 3 | ✅ |
| **합계** | **32** | ✅ |

**STAGE 9 추적 상태 column 활성화**: 87 inventory 1:1 매핑 EXACT — Part2 로드맵 종속, 본 도메인 자체 실행 없음, SHELL→STUB→REF transition awaiting Part2 V2/V3 진행.

## 변경 이력

| 일자 | 내용 | 세션 |
|------|------|------|
| 2026-04-12 | P1-1 작성: 6열 구조로 32건 전수 등록, 검산/교차 대조/테스트 시나리오 추가 | P1-1 |
