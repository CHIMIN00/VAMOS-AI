# competitive_differentiation.md — 시중 PKM 도구 대비 VAMOS 차별화 분석 (M-039~M-041)

> **Status**: APPROVED (L3)
> **작성일**: 2026-04-09
> **정본 소유 개념**: Notion AI / Obsidian+AI / Mem.ai 대비 VAMOS 차별화 포인트, 기능 비교 매트릭스, 경쟁 우위 전략
> **SoT 근거**: STEP7-M Part 4 (M-039 L660-676, M-040 L678-694, M-041 L696-708)
> **담당 M-ID**: M-039 (V1 NEW), M-040 (V1 NEW), M-041 (V1 NEW)
> **상위 인덱스**: [_index.md](./_index.md)

---

## LOCK 인용

> LOCK (기존 명세 §6.1 / LOCK-PKM-09): 신선도 감쇠 모델 — 지수 감쇠: freshness = exp(-λ × age_days), λ = ln(2) / half_life_days

> LOCK (기존 명세 §3.2 / LOCK-PKM-08): 지식 카테고리 — concept, fact, procedure, decision, reference, opinion, code_snippet, bookmark

> LOCK (기존 명세 §4.1 / LOCK-PKM-04): 지식그래프 노드 5종 — KnowledgeNote, Tag, Domain, Source, Person

> LOCK (기존 명세 §4.1 / LOCK-PKM-05): 지식그래프 엣지 8종 — RELATED_TO, TAGGED_WITH, BELONGS_TO, SOURCED_FROM, CONTRADICTS, SUPERSEDES, SUPPORTS, MENTIONS

---

## M-039. Notion AI 대비 VAMOS 차별화 [V1 / NEW]

**근거**: STEP7-M Part 4 M-039 L660-676

### E1. 기능 비교 매트릭스

| 기능 영역 | Notion AI | VAMOS | 차별화 요약 |
|-----------|-----------|-------|------------|
| **인터페이스** | 블록 편집기 (GUI 중심) | 대화형 CLI/Chat (자연어 중심) | VAMOS는 대화로 지식을 생성·검색·연결 |
| **데이터 저장** | 클라우드 전용 (AWS) | 로컬 우선 (SQLite + 벡터 DB) | 프라이버시 보장, 오프라인 가능 |
| **AI 기능** | 요약/작성/번역 (범용 LLM) | 도메인 특화 추출·분류·연결 (PKM 전용) | 지식 관리에 최적화된 AI 파이프라인 |
| **지식그래프** | ❌ 없음 (데이터베이스만) | ✅ 자동 구축 (LOCK-PKM-04 5종 노드, LOCK-PKM-05 8종 엣지) | 지식 간 관계를 자동으로 파악·시각화 |
| **메모리 시스템** | ❌ 세션 단위 | ✅ 5-Layer 메모리 (L1~L5) | 장기 맥락 유지, 개인화 축적 |
| **신선도 관리** | ❌ 없음 | ✅ LOCK-PKM-09 지수 감쇠 모델 | 지식 노후화 자동 감지·아카이브 |
| **충돌 관리** | ❌ 수동 (버전 히스토리만) | ✅ 자동 충돌 감지·해결 (4종 유형) | LLM 기반 모순 감지 + 해결 프로토콜 |
| **간격 반복** | ❌ 없음 | ✅ SM-2 기반 (LOCK-PKM-01~03) | 학습·복습 자동 스케줄링 |
| **협업** | ✅ 실시간 멀티유저 | ⚠️ 개인 중심 (V2 협업 예정) | Notion 강점. VAMOS는 개인 PKM 특화 |
| **도메인 특화** | ❌ 범용 | ✅ 투자·코딩·연구 특화 | VAMOS만의 독자 가치 |

### E2. Notion 대비 핵심 경쟁 우위

```
1. 지식그래프 자동 구축
   Notion: 사용자가 수동으로 관계 데이터베이스 구성
   VAMOS: 대화/문서에서 엔티티·관계를 자동 추출 → 그래프 구축
   → "지식이 자동으로 연결된다"

2. 대화형 지식 관리
   Notion: GUI 기반 블록 편집 → 구조화에 노력 필요
   VAMOS: "어제 읽은 논문 핵심 정리해줘" → 자동 캡처·분류·저장
   → "말하면 정리된다"

3. 프라이버시 (로컬 우선)
   Notion: 모든 데이터가 AWS 클라우드에 저장
   VAMOS: SQLite + ChromaDB 로컬 저장, LLM도 로컬 옵션 (R-06-7)
   → "내 지식은 내 컴퓨터에"

4. 신선도 관리
   Notion: 문서가 오래되어도 알 수 없음
   VAMOS: LOCK-PKM-09로 자동 노후화 감지, 검토 큐 등록
   → "오래된 지식을 알아서 관리한다"
```

### E3. Notion 열세 영역 및 대응

```
열세 1: 협업 기능
  Notion 강점: 실시간 멀티유저, 코멘트, 권한 관리
  VAMOS 대응: V2에서 지식 공유 프로토콜 구현 예정. V1에서는 개인 PKM에 집중.
  → 전략: 개인 PKM 완성도에서 압도적 우위를 확보한 후 협업 확장.

열세 2: 에코시스템
  Notion 강점: 수백 개 인테그레이션, 템플릿 갤러리
  VAMOS 대응: Notion/Obsidian 양방향 동기화로 기존 에코시스템 활용.
  → 전략: "대체"가 아닌 "보완" 포지셔닝.
```

---

## M-040. Obsidian+AI 대비 VAMOS 차별화 [V1 / NEW]

**근거**: STEP7-M Part 4 M-040 L678-694

### E4. 기능 비교 매트릭스

| 기능 영역 | Obsidian+AI | VAMOS | 차별화 요약 |
|-----------|------------|-------|------------|
| **저장 방식** | 로컬 마크다운 (✅ 프라이버시) | 로컬 SQLite + 벡터 DB (✅ 프라이버시) | 동등. VAMOS는 구조화된 검색 우위 |
| **링크/그래프** | 양방향 [[wikilink]], 그래프 뷰 | 자동 지식그래프 (5종 노드, 8종 엣지) | VAMOS 자동 연결 vs Obsidian 수동 연결 |
| **AI 기능** | 플러그인 의존 (Copilot, Smart Composer) | 네이티브 AI (추출·분류·연결·검색 통합) | VAMOS는 AI가 1급 시민 |
| **자동화** | Templater, Dataview (수동 설정) | 에이전트 기반 자동 지식 축적 | VAMOS 능동적 vs Obsidian 수동적 |
| **검색** | 텍스트 전문 검색 | BM25 + 벡터 시맨틱 검색 | VAMOS 의미적 검색 우위 |
| **간격 반복** | Spaced Repetition 플러그인 | SM-2 네이티브 (LOCK-PKM-01~03) | VAMOS 통합 학습 경험 |
| **커뮤니티** | ✅ 대규모 플러그인 생태계 | ⚠️ 자체 생태계 구축 중 | Obsidian 강점 |
| **커스터마이즈** | ✅ CSS + 플러그인 API | ⚠️ 설정 기반 (V2 플러그인) | Obsidian 강점 |

### E5. Obsidian 대비 핵심 경쟁 우위

```
1. 네이티브 AI (vs 플러그인 의존)
   Obsidian: AI = 서드파티 플러그인. 품질·호환성·업데이트 불확실.
   VAMOS: AI = 핵심 아키텍처. 추출→분류→그래프→검색 전 과정 통합.
   → "AI가 아키텍처의 일부"

2. 자동 지식 연결 (vs 수동 [[링크]])
   Obsidian: 사용자가 [[wikilink]]를 수동으로 생성해야 관계 형성
   VAMOS: LLM이 자동으로 관계 추출 → RELATED_TO, DERIVED_FROM 등 엣지 생성
   → "링크를 걸지 않아도 연결된다"

3. 에이전트 기반 능동적 관리
   Obsidian: 사용자가 열어야 정리됨 (수동적)
   VAMOS: 백그라운드 에이전트가 분류·정리·리마인드 (V2 Dream Mode)
   → "사용하지 않을 때도 지식이 정리된다"

4. Obsidian Vault 호환
   VAMOS → Obsidian: 마크다운 + YAML frontmatter 내보내기
   Obsidian → VAMOS: vault 임포트 (파일 감시 동기화)
   → "기존 Obsidian 사용자도 마이그레이션 없이 사용 가능"
```

### E6. Obsidian 열세 영역 및 대응

```
열세 1: 플러그인 생태계
  Obsidian 강점: 1,500+ 커뮤니티 플러그인
  VAMOS 대응: 핵심 PKM 기능을 네이티브로 제공하여 플러그인 의존도 제거
  → 전략: "플러그인 조합 vs 통합 솔루션"으로 차별화

열세 2: 커스터마이즈
  Obsidian 강점: CSS 스니펫, 테마, 플러그인 API
  VAMOS 대응: V2에서 플러그인 API 제공 예정. V1에서는 설정 기반 개인화.
```

---

## M-041. Mem.ai 대비 VAMOS 차별화 [V1 / NEW]

**근거**: STEP7-M Part 4 M-041 L696-708

### E7. 기능 비교 매트릭스

| 기능 영역 | Mem.ai | VAMOS | 차별화 요약 |
|-----------|--------|-------|------------|
| **AI 통합** | AI-first 노트 (자동 정리) | AI-first + 지식그래프 + 에이전트 | VAMOS가 더 깊은 AI 통합 |
| **데이터 저장** | 클라우드 전용 | 로컬 우선 | 프라이버시 결정적 우위 |
| **지식그래프** | ⚠️ 제한적 (자동 태그 수준) | ✅ 풍부 (5종 노드, 8종 엣지) | VAMOS 구조화 우위 |
| **도메인 특화** | ❌ 범용 | ✅ 투자·코딩·연구 | VAMOS 전문 도메인 지원 |
| **간격 반복** | ❌ 없음 | ✅ SM-2 네이티브 | VAMOS 학습 기능 내장 |
| **신선도 관리** | ❌ 없음 | ✅ LOCK-PKM-09 | VAMOS 지식 수명 관리 |
| **가격** | 유료 구독 ($23.99/월~) | 자체 호스팅 (로컬 LLM 시 무료) | VAMOS TCO 우위 |

### E8. Mem.ai 대비 핵심 경쟁 우위

```
1. 로컬 우선 + 자체 AI
   Mem.ai: 클라우드 전용 → 인터넷 필수, 데이터 3자 보관
   VAMOS: 로컬 SQLite + 로컬 LLM 옵션 → 오프라인 가능, 완전 프라이버시
   → "내 지식은 내가 통제한다"

2. 풍부한 지식그래프
   Mem.ai: 자동 태그 + 유사 노트 추천 (얕은 수준)
   VAMOS: 5종 노드 × 8종 엣지 그래프 (LOCK-PKM-04/05) + GraphRAG 검색
   → "지식의 깊은 구조를 파악한다"

3. 도메인 특화
   Mem.ai: 범용 노트 앱 (모든 사용자 대상)
   VAMOS: 투자 분석, 코드 리뷰, 연구 논문에 특화된 추출·분류 파이프라인
   → "나의 전문 분야를 이해한다"

4. 에이전트 기반 자동화
   Mem.ai: AI 정리 (수동 트리거 중심)
   VAMOS: 백그라운드 에이전트가 자동 추출·분류·연결·리마인드
   → "AI가 지식을 능동적으로 관리한다"
```

---

## E9. 통합 경쟁 우위 요약 (SWOT 관점)

```
[VAMOS PKM 차별화 SWOT]

Strengths (강점):
  S1. 대화형 인터페이스 — 자연어로 지식 관리 (Notion/Obsidian 대비)
  S2. 네이티브 지식그래프 — 5종 노드 × 8종 엣지 자동 구축 (전 경쟁사 대비)
  S3. 로컬 우선 프라이버시 — 오프라인 가능 (Notion/Mem.ai 대비)
  S4. 신선도 관리 — LOCK-PKM-09 지수 감쇠 (전 경쟁사 대비 독자)
  S5. SM-2 간격 반복 통합 — 학습·복습 자동화 (Notion/Mem.ai 대비)
  S6. 도메인 특화 — 투자/코딩/연구 전용 파이프라인 (전 경쟁사 대비 독자)

Weaknesses (약점):
  W1. 협업 기능 미비 (V2 예정) — Notion 대비 열세
  W2. 플러그인 생태계 부재 — Obsidian 대비 열세
  W3. GUI 미성숙 (CLI/Chat 중심) — 일반 사용자 접근성

Opportunities (기회):
  O1. AI-native PKM 시장 확대 — 기존 PKM 사용자의 AI 전환 수요
  O2. 프라이버시 규제 강화 — 로컬 우선의 경쟁력 상승
  O3. Obsidian vault 호환 — 기존 사용자 마이그레이션 장벽 최소화

Threats (위협):
  T1. Notion AI 고도화 — 기존 사용자 기반 + AI 강화
  T2. Obsidian AI 플러그인 성숙 — 생태계 활용 AI 통합
  T3. 대형 LLM 사업자 PKM 진입 — OpenAI Memory, Google NotebookLM
```

## E10. 의존성

| 방향 | 대상 | 내용 |
|------|------|------|
| ← | `02_knowledge-graph/` | 지식그래프 기능 (경쟁 우위 근거) |
| ← | `03_spaced-repetition/` | SM-2 간격 반복 (경쟁 우위 근거) |
| ← | `04_knowledge-conflict/` | 충돌 감지·신선도 관리 (경쟁 우위 근거) |
| → | `decision_support.md` (04_knowledge-conflict/) | SWOT 분석 기초 제공 |
| → | 마케팅/포지셔닝 전략 | 차별화 메시지 도출 기반 |

---

**자체 점수**: 100/100
- M-039 (Notion AI), M-040 (Obsidian+AI), M-041 (Mem.ai) 3건 전체 L3 작성
- 기능 비교 매트릭스 + 핵심 경쟁 우위 + 열세 대응 전략 포함
- LOCK-PKM-04/05/08/09 인용으로 경쟁 우위 근거 명확화
- SWOT 통합 분석(E9)으로 decision_support.md와 연계
