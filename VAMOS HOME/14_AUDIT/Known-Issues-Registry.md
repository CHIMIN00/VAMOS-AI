---
tags: [type/audit, tier/T0, version/V0, version/V1, version/V2, version/V3]
aliases: [45개 이슈, 미해소 이슈 레지스트리, Known Issues]
created: 2026-06-11
source: "D:\\VAMOS\\CLAUDE.md §9 (45개 미해소 이슈 전수)"
---

# Known Issues Registry — 45개 미해소 이슈

> CLAUDE.md §9 전사. **HIGH 10 / MEDIUM 21 / LOW 9 / INFO 5 = 45건**. 버전별: V0 5 / V1 16 / V2 14 / V3 5 / CC 5. 해소 시점은 각 버전 진입 전 GO/NO-GO 체크리스트와 연동.

## HIGH (10건)

- **V0-002** IMPLEMENTATION 계층 부재 → PHASE_B = IMPLEMENTATION 명시 · **V0-004** 통신 계층 Python 백엔드 확정
- **V1-001** I-Series 카운트 I-1~I-25 정본 확정 · **V1-002** E-15 명칭 충돌(File System/Cloud Collector 겸용) · **V1-003** S-5 명칭 충돌(Router Evolution/Cloud Evolver 겸용)
- **V1-008** 38개 DEFER/TBD → V1 차단 0건 확인 완료 · **V1-015** Python 진입점 정의(V0 해소) · **V1-016** I-21~I-25 모듈 정의 추가
- **V2-003** Agent Teams vs FREEZE 충돌(Lead 단방향 V1, MessageBus V2) · **V2-008** STEP7 TITLE_ONLY ~675건 중 V2 CRITICAL ~190건 보강

## MEDIUM (21건)

- V0: **V0-001** V0 비용상한=V1 동일(₩40,000/월) · **V0-003** 디렉토리 구조 → PHASE_B2 정본
- V1: **V1-004** approval_status enum 통일 · **V1-005** datetime.utcnow() 전수 교체 · **V1-006** QoD 가중치 → PLAN-3.0 5요소 정본 · **V1-007** Front Mini LLM = I-1 내부 · **V1-010** Guardrails 4-Layer 정본 · **V1-013** 비용상한 ₩40,000 정본
- V2: **V2-001** 10-Layer 명칭 → CL-Layer 접두어 · **V2-002** SDAR V2 COND 활성화 조건 · **V2-004** JSONL→PostgreSQL+Loki · **V2-005** Chroma→Qdrant 재임베딩 · **V2-006** NetworkX→Neo4j · **V2-007** STEP7 vs BASE 비용 괴리 인지
- V3: **V3-001** K8s 배포 명세 보강 · **V3-002** S-8 거버넌스 상세화
- CC: **CC-001** 스키마 v3.0.0 승격 · **CC-003** QoD 이중 체계 구분 · **CC-006** EventTypeRegistry 통합 · **CC-007** Py/TS 스키마 동기화 · **CC-012** HMAC-SHA256 키관리

## LOW (9건)

- **V0-005** config.toml 통일 · **V1-009** LangChain Allowlist · **V1-011** (정합성 확인 완료) · **V1-014** React 18.3 통일
- **V3-003** V3 비용상한 현실성 재산정 · **V3-004** GraphRAG 90% 벤치마크 기준 미정의
- **CC-002** BEGINNER_GUIDE 갱신 · **CC-004** Gate → CL-G0~G4 접두어 · **CC-005** STEP7 모듈 연동 구체화

## INFO (5건)

- **V1-012** (정합 확인 완료) · **CC-008** 테스트 케이스 목록 → V1 AC 자동 도출 · **CC-009** B↔L 매핑 교차(LOCK 변경불가, 매핑표 명시) · **CC-010** 문서 인덱스 39 vs 38(PLAN-2.0 SUPERSEDED) · **CC-011** STEP7 60건 차이(개별 문서 기준 정본)

## 연결

- [[Phase11-Validation-Summary]] · [[VAMOS-Version-Strategy]] · [[Cost-Limits]] · [[BASE-1.3-Rules]]
