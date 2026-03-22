# VAMOS Cloud Library System - 통합 상세 명세서

> **문서 ID**: VAMOS_CLOUD_LIBRARY_UNIFIED_SPEC
> **버전**: 1.0
> **작성일**: 2026-02-23
> **소스 문서**: SPECIFICATION v1.0, 구현성 보완 방안 01, HYBRID ROADMAP v1.0, 대화 정리
> **상태**: 정본

---

## 목차

1. [시스템 정의 및 핵심 목표](#1-시스템-정의-및-핵심-목표)
2. [10-Layer 아키텍처 상세](#2-10-layer-아키텍처-상세)
3. [7-Stage 자율 사이트 발견 파이프라인](#3-7-stage-자율-사이트-발견-파이프라인)
4. [플랫폼 템플릿 시스템](#4-플랫폼-템플릿-시스템)
5. [스코어링 알고리즘](#5-스코어링-알고리즘)
6. [E-15 Collector + S-5 Evolver 하이브리드 구조](#6-e-15-collector--s-5-evolver-하이브리드-구조)
7. [스케줄러 시스템](#7-스케줄러-시스템)
8. [Gate 통합 검증 체계](#8-gate-통합-검증-체계)
9. [저장소 구조](#9-저장소-구조)
10. [충돌 해결 엔진](#10-충돌-해결-엔진)
11. [오류 처리 및 재시도 로직](#11-오류-처리-및-재시도-로직)
12. [자가 진화 시스템 (S Feature)](#12-자가-진화-시스템-s-feature)
13. [V0/V1/V2/V3 버전별 구현 로드맵](#13-v0v1v2v3-버전별-구현-로드맵)
14. [API 엔드포인트](#14-api-엔드포인트)
15. [Pydantic v2 스키마 정의](#15-pydantic-v2-스키마-정의)
16. [LOCK 결정사항](#16-lock-결정사항)
17. [보안 및 비용 제약](#17-보안-및-비용-제약)
18. [VAMOS 4계층 연계](#18-vamos-4계층-연계)
19. [구현 가능성 평가 및 핵심 수치](#19-구현-가능성-평가-및-핵심-수치)

---

## 1. 시스템 정의 및 핵심 목표

### 1.1 정의

VAMOS Cloud Library는 인터넷의 다양한 소스(YouTube, Instagram, Website, Blog, Academic 등)를 연결하여 지식을 수집하고, 자동으로 키워드를 추출하여 분석하며, 그 분석 결과를 기반으로 VAMOS AI를 지속적으로 업그레이드하고, 모든 변경사항을 자동으로 버전 관리하는 **통합 지식 시스템**이다.

### 1.2 핵심 목표 6가지

| 목표 | 설명 |
|------|------|
| **다중 소스 통합** (Multi-Source Integration) | YouTube, Instagram, Website, Blog, Academic 등 모든 인터넷 소스 연결 |
| **자동 키워드 추출** (Auto Keyword Extraction) | 플랫폼별 맞춤 템플릿 기반으로 키워드 자동 추출 |
| **지능형 분석** (Intelligent Analysis) | 교차 분석(Cross-Source), 충돌 해결(Conflict Resolution), 품질 검증(Quality Gate) |
| **자동 버전 관리** (Auto Versioning) | Semantic Versioning (1.0 -> 1.1 -> 1.2 -> 2.0) 자동 적용 |
| **VAMOS AI 연동** (VAMOS Integration) | RULE/PLAN/DESIGN/SCHEMA 4계층 자동 매핑 |
| **자가 진화** (Self-Evolution, S Feature) | 스스로 데이터를 수집하고 패턴을 학습하여 자율적으로 발달 |

### 1.3 핵심 기능 8가지

| # | 기능 | 설명 | 우선순위 |
|---|------|------|----------|
| 1 | **Conflict Resolution** | 소스 간 키워드 충돌 해결 메커니즘 (가중치 + 다수결) | CRITICAL |
| 2 | **Quality Gate** | 자동 생성 콘텐츠 품질 검증 (G0-G4 5단계) | CRITICAL |
| 3 | **Rollback System** | 버전 오류 시 체크포인트 기반 이전 버전 복구 | HIGH |
| 4 | **Source Priority** | 소스별 신뢰도 가중치 (학술 0.9 > 뉴스 0.6 > SNS 0.3) | HIGH |
| 5 | **Change Log** | 모든 변경사항 CHANGELOG 자동 기록 | HIGH |
| 6 | **Human-in-the-Loop** | 중요 결정(CRITICAL 변경, Score < 60)에서 사용자 승인 요청 | MEDIUM |
| 7 | **Scheduler** | 크론 기반 정기적 데이터 수집 + 이벤트 트리거 + 우선순위 큐 | MEDIUM |
| 8 | **Dashboard** | 시스템 상태, 수집 현황, 키워드 통계, 버전 이력 시각화 | LOW |

### 1.4 핵심 가치

> **"신뢰할 수 있는 자동화" > "예측 불가능한 완전 자율"**

| 원칙 | 원래 비전 | 실용적 대체 | 설명 |
|------|-----------|-------------|------|
| 1 | "완전 자율" | "증강된 자동화" | 99% 자동화 + 1% 핵심 인간 통제 |
| 2 | "무감독" | "효율적 감독" | 인간 검토를 14%로 최소화 (86% 감소) |
| 3 | "메타 학습" | "패턴 기반 학습" | 영구 저장 가능한 패턴 DB, 도메인 간 패턴 전이 |
| 4 | "자율 진화" | "제안 + 승인 진화" | 시스템이 제안하고, 인간이 승인 |
| 5 | "창발적 지능" | "구조화된 통찰" | 데이터 기반 연결 발견, 설명 가능한 인사이트 |

---

## 2. 10-Layer 아키텍처 상세

### 2.1 전체 구조 개요

```
Layer 1  INPUT           →  외부 입력 수신
Layer 2  DISCOVERY        →  자율 사이트 발견
Layer 3  EVALUATION       →  사이트 평가 (0-100점)
Layer 4  COLLECTION       →  데이터 수집
Layer 5  DATA LAKE        →  원본 데이터 저장
Layer 6  EXTRACTION       →  키워드 추출
Layer 7  ANALYSIS         →  분석 및 충돌 해결
Layer 8  VALIDATION       →  5단계 품질 검증 (G0-G4)
Layer 9  VERSION CONTROL  →  버전 관리
Layer 10 OUTPUT           →  결과 출력 및 진화
```

**E-15/S-5 분할**: Layer 1~6은 E-15 Collector(BLUE NODE), Layer 7~10은 S-5 Evolver(ORANGE CORE)가 담당한다.

### 2.2 Layer 1: INPUT (입력 계층)

- **담당 모듈**: E-15 Collector
- **구성요소**:
  - Manual Source Registration: 사용자가 직접 URL 또는 소스를 입력
  - URL Import: 일괄 URL 목록 가져오기
  - API Webhook: 외부 시스템으로부터의 자동 트리거
  - Seed Keywords: VAMOS DESIGN에서 추출한 초기 키워드 (LLM, RAG, Agent, Fine-tuning, Vector DB, Embedding 등)
  - Scheduled Trigger: 크론 기반 정기 실행
  - Event Webhook: 새 콘텐츠 감지 시 자동 트리거
- **입력**: URL 문자열, 키워드 목록, 웹훅 payload
- **출력**: 정규화된 수집 요청 객체 (CollectionRequest)
- **기술**: Python asyncio, Tauri IPC

### 2.3 Layer 2: DISCOVERY (발견 계층)

- **담당 모듈**: E-15 Collector
- **구성요소**:
  - Seed Keyword Manager: 초기 시드 키워드 관리 및 자동 갱신
  - Search Engine Connector: Google/Bing/DuckDuckGo 자동 검색 쿼리 생성
  - Site Candidate Pool: 발견된 URL 후보 관리 (중복 제거, [NEW] 태그 부여)
  - Autonomous Discovery Engine: 7-Stage 파이프라인 (별도 섹션 3 상세)
- **입력**: 시드 키워드, 기존 키워드 풀
- **출력**: 평가 대상 사이트 후보 목록 (SiteCandidateList)
- **기술**: GPT-4o mini(V2+), 검색 API(Google/Bing), Tavily Search(V3)

### 2.4 Layer 3: EVALUATION (평가 계층)

- **담당 모듈**: E-15 Collector
- **구성요소**:
  - Trust Score Calculator: 도메인 연령, HTTPS, 순위, 업데이트 빈도, 저자 정보 (25점)
  - Relevance Analyzer: VAMOS 키워드 매칭률 (30점)
  - Quality Assessor: 콘텐츠 길이, 코드 예제, 인용, 원본성 (25점)
  - Accessibility Checker: robots.txt, RSS, API, 페이월 여부 (20점)
- **입력**: 사이트 후보 URL + 콘텐츠
- **출력**: SiteEvaluation 객체 (total_score 0-100, 4개 세부 점수)
- **판단 기준**: AUTO(>=80), NOTIFY(60-79), MANUAL(30-59), BLOCK(<30)
- **기술**: 규칙 기반 휴리스틱 평가, Semantic Router(V2+)

### 2.5 Layer 4: COLLECTION (수집 계층)

- **담당 모듈**: E-15 Collector
- **구성요소**:
  - Platform Collectors: YouTube(yt-dlp), Instagram(yt-dlp+Whisper), Web(WebFetch), GitHub(API), Twitter/X(API), Paper(Semantic Scholar API), Blog(RSS), Discord(API)
  - Scheduler & Queue Manager: 크론 기반 정기 실행 + 우선순위 큐 (CRITICAL 소스 먼저)
  - Rate Limiter: 플랫폼별 API 호출 제한 준수
  - Error Handler & Retry: 실패 시 최대 3회 자동 재시도, 지수 백오프
  - Data Normalizer: 플랫폼별 데이터를 통합 형식으로 정규화
- **입력**: 승인된 사이트 목록 + 수집 스케줄
- **출력**: 정규화된 Raw Data (JSON/Markdown)
- **기술**: Python asyncio, yt-dlp, WebFetch, REST/GraphQL 클라이언트

### 2.6 Layer 5: DATA LAKE (데이터 레이크)

- **담당 모듈**: E-15 Collector
- **구성요소**:
  - Raw Data Storage: 원본 데이터 저장 (JSON/Markdown 형식)
  - Normalized Data: 정규화 데이터 저장
  - Metadata Index: 검색용 메타데이터 인덱스 (SQLite, V2+: Postgres)
  - Deduplication Engine: 글로벌 키워드 인덱스 유지, Levenshtein 유사도(>=0.85시 동일 취급), Cosine 유사도, 동의어 그룹화 (LLM = Large Language Model)
- **입력**: 수집된 Raw Data
- **출력**: 정규화/인덱싱된 데이터 + 중복 제거 결과
- **기술**: 파일 시스템(V0-V1), SQLite + JSONL(V1-V2), Postgres(V2+)

### 2.7 Layer 6: EXTRACTION (추출 계층)

- **담당 모듈**: E-15 Collector
- **구성요소**:
  - Template Matcher: URL 패턴 기반 1차 분류 + 콘텐츠 분석 기반 2차 분류
  - Keyword Extractor: 템플릿 v1.x 시리즈 기반 키워드 추출 (9종 템플릿)
  - Dynamic Template Generator: 신규 플랫폼 감지 시 기존 템플릿 참조하여 새 템플릿 초안 생성
  - VAMOS 4-Layer Mapper: 추출된 키워드를 RULE/PLAN/DESIGN/SCHEMA에 자동 매핑
  - Priority Classifier: 키워드를 CRITICAL/HIGH/MEDIUM/LOW로 자동 분류
- **입력**: 정규화된 데이터 + 템플릿 목록
- **출력**: 분류된 키워드 목록 + VAMOS 매핑 정보
- **기술**: 템플릿 매칭, 규칙 기반 분류, LLM 보조(V2+)

### 2.8 Layer 7: ANALYSIS (분석 계층)

- **담당 모듈**: S-5 Evolver
- **구성요소**:
  - Deep Analyzer: 템플릿 v2.3 기반 심화 분석 (트렌드, 상관관계, 패턴)
  - Cross-Source Analyzer: 소스 간 일관성 검사, 키워드 빈도 변화 추적, 갭 분석
  - Conflict Resolution Engine: 소스 가중치 + 다수결 원칙 기반 충돌 해결 (별도 섹션 10 상세)
  - Trend Detector: 키워드 트렌드 추적, 기초 예측 모델
  - Pattern Recognition: 키워드/소스/VAMOS 매핑 패턴 식별
- **입력**: 추출된 키워드 + 기존 키워드 DB
- **출력**: 분석 결과 + 충돌 해결 로그 + 트렌드 리포트
- **기술**: 규칙 기반 분석(V1), Cross-Source Analyzer(V2), 패턴 DB(V2+: Postgres), GraphRAG(V3)

### 2.9 Layer 8: VALIDATION (검증 계층)

- **담당 모듈**: S-5 Evolver
- **구성요소**: G0-G4 5단계 Gate 시스템 (별도 섹션 8 상세)
  - G0 Format Gate: 템플릿 섹션 완전성, 필수 필드, 마크다운 문법, 테이블 구조 (100% 필수)
  - G1 Content Gate: 키워드 최소 10개, 우선순위 분류, 검색 쿼리, VAMOS 매핑, 출처 명시 (95% 이상)
  - G2 Consistency Gate: 중복 확인, 동의어 일관성, 우선순위 논리성, 버전 호환성 (90% 이상)
  - G3 Security Gate: 악성 URL, 민감 정보, 저작권, 스팸, 비윤리 콘텐츠 필터 (100% 필수)
  - G4 Final Gate: G0-G3 통과 확인, 영향 범위 분석, 롤백 가능 여부, Human 승인 여부
- **입력**: 분석 완료 데이터
- **출력**: Gate 검증 결과 JSON (pass/fail + 점수 + 세부 체크)
- **기술**: 규칙 엔진(V1), LLM 보조(V2+), RAGAS + LLM Judge(V2+)

### 2.10 Layer 9: VERSION CONTROL (버전 관리 계층)

- **담당 모듈**: S-5 Evolver
- **구성요소**:
  - Semantic Versioning Engine: MAJOR.MINOR.PATCH 자동 결정
  - Changelog Generator: Added/Changed/Fixed/Statistics 형식 자동 생성
  - Checkpoint Manager: 단계별 체크포인트 저장 (롤백 가능 기간 7일)
  - Rollback System: 정확도 10% 이상 하락 시 자동 롤백, 롤백 후 동일 변경 재시도 24시간 금지
- **입력**: Gate 통과 데이터 + 변경 목록
- **출력**: 새 버전 번호 + CHANGELOG + 체크포인트
- **기술**: Git 연동(V1+), SQLite/Postgres 로그

### 2.11 Layer 10: OUTPUT (출력 계층)

- **담당 모듈**: S-5 Evolver
- **구성요소**:
  - VAMOS Document Updater: RULE/PLAN/DESIGN/SCHEMA 4계층 문서 자동 업데이트
  - Dashboard & Reporting: 실시간 수집 현황, 키워드 통계, 버전 이력 타임라인, 진화 로그
  - API Endpoint: Tauri IPC(V1), REST API(V2+), SDK(V3)
  - Notification System: Human Review 요청, 에러 알림 (이메일/웹훅)
  - Evolution Module (S Feature): S1-S5 자가 진화 단계 (별도 섹션 12 상세)
  - Multi-Format Export: Markdown, JSON, YAML, CSV(V2), Excel, PDF(V3)
- **입력**: 버전 관리 완료 데이터
- **출력**: 업데이트된 VAMOS 문서, 대시보드 데이터, API 응답, 알림
- **기술**: 파일 시스템(V1), Web Dashboard(V2), REST API + SDK(V3)

---

## 3. 7-Stage 자율 사이트 발견 파이프라인

### 3.1 파이프라인 개요

7-Stage Discovery Pipeline은 시드 키워드로부터 출발하여 자율적으로 새로운 정보 소스를 발견, 평가, 승인하는 시스템이다.

```
Stage 1: SEED KEYWORDS      →  시드 키워드 준비
Stage 2: SEARCH ENGINE QUERY →  검색 엔진 자동 쿼리
Stage 3: SITE CANDIDATE POOL →  후보 사이트 풀 구성
Stage 4: SITE EVALUATION     →  사이트 자동 평가 (0-100)
Stage 5: TEMPLATE MATCHING   →  템플릿 자동 매핑
Stage 6: APPROVAL GATE       →  승인 게이트 (AUTO/NOTIFY/MANUAL/BLOCK)
Stage 7: SITE REGISTRY       →  사이트 레지스트리 등록
```

### 3.2 Stage 1: SEED KEYWORDS (시드 키워드)

- **입력**: VAMOS DESIGN 문서에서 추출한 초기 키워드
- **키워드 풀**: LLM, RAG, Agent, Fine-tuning, Vector DB, Embedding, Transformer, Prompt Engineering, RLHF 등
- **자동 갱신**: 기존 추출 키워드 풀에서 빈도/트렌드 분석 후 자동으로 새로운 시드 키워드 추가
- **출력**: 검색에 사용할 키워드 목록 (keyword_pool.json)

### 3.3 Stage 2: SEARCH ENGINE QUERY (검색 엔진 쿼리)

- **자동 쿼리 생성 규칙**:
  - Google: `"{키워드} site:.edu"`, `"{키워드} tutorial 2026"`
  - Bing: `"{키워드} research paper"`
  - DuckDuckGo: `"{키워드} open source"`
- **검색 엔진**: Google Search API, Bing Search API, DuckDuckGo API
- **쿼리 확장**: 동의어, 관련어 자동 추가 (예: "RAG" -> "Retrieval Augmented Generation", "검색 증강 생성")
- **출력**: URL 목록 + 검색 메타데이터 (검색 순위, snippet)
- **V3 추가**: Tavily Search 통합으로 웹 검색 자동화 강화

### 3.4 Stage 3: SITE CANDIDATE POOL (사이트 후보 풀)

- **처리 과정**:
  1. 검색 결과에서 도메인 추출
  2. 기존 site_registry.json과 비교하여 중복 제거
  3. 새 사이트에 `[NEW]` 태그 부여
  4. 블랙리스트(blacklist.json) 대조 필터링
- **입력**: 검색 엔진 결과 URL 목록
- **출력**: 중복 제거된 신규 사이트 후보 목록

### 3.5 Stage 4: SITE EVALUATION (사이트 평가)

- **평가 점수 구성** (총 100점):

| 구분 | 배점 | 세부 항목 |
|------|------|-----------|
| 신뢰도 (Trust) | 25점 | 도메인 연령(5), HTTPS(5), Alexa 순위(5), 업데이트 빈도(5), 저자 정보(5) |
| 관련성 (Relevance) | 30점 | VAMOS 키워드 매칭률 (키워드당 2점, 최대 30점) |
| 품질 (Quality) | 25점 | 콘텐츠 길이(10), 코드 예제(5), 인용(5), 원본성(5) |
| 접근성 (Access) | 20점 | robots.txt 허용(5), RSS(5), API(5), 페이월 없음(5) |

- **알고리즘**: 별도 섹션 5 상세 참조
- **출력**: SiteEvaluation 객체 (total_score, trust, relevance, quality, access, recommendation)

### 3.6 Stage 5: TEMPLATE MATCHING (템플릿 매칭)

- **자동 분류 흐름**: URL 패턴 1차 분류 -> 콘텐츠 분석 2차 분류 -> 템플릿 할당
- **매핑 규칙**: 별도 섹션 4 상세 참조
- **신규 플랫폼 처리**: 기존 템플릿 유사도 분석 -> 초안 생성 -> Human 검토 -> 정식 등록
- **출력**: 할당된 템플릿 ID + 신뢰도 퍼센트

### 3.7 Stage 6: APPROVAL GATE (승인 게이트)

| 모드 | 점수 범위 | 동작 |
|------|-----------|------|
| **AUTO** | >= 80점 | 자동 추가, 인간 개입 없음 |
| **NOTIFY** | 60-79점 | 알림 발송 후 자동 추가 |
| **MANUAL** | 30-59점 | 사용자 승인 필요, 대기열에 등록 |
| **BLOCK** | < 30점 또는 블랙리스트 | 자동 거부, 로그 기록 |

### 3.8 Stage 7: SITE REGISTRY (사이트 레지스트리)

- 승인된 사이트를 `site_registry.json`에 등록
- `키워드 추출 대본.md` 자동 업데이트
- 다음 수집 사이클에 자동 포함
- 등록 정보: URL, 템플릿 ID, 평가 점수, 등록일, 수집 주기, 최종 수집일

---

## 4. 플랫폼 템플릿 시스템

### 4.1 자동 매핑 규칙

| URL 패턴 | 감지 방식 | 적용 템플릿 | 매핑 신뢰도 |
|----------|-----------|-------------|------------|
| `youtube.com/*` | 도메인 매칭 | YouTube v1.2 | 100% |
| `github.com/*` | 도메인 매칭 | GitHub v1.1 | 100% |
| `twitter.com/*`, `x.com/*` | 도메인 매칭 | Twitter/X v1.1 | 100% |
| `instagram.com/*` | 도메인 매칭 | Instagram v1.1 | 100% |
| `arxiv.org/*` | 도메인 매칭 | 논문/연구 v1.1 | 100% |
| `*.substack.com` | 서브도메인 매칭 | 뉴스레터 v1.1 | 95% |
| `discord.gg/*` | 도메인 매칭 | Discord v1.1 | 100% |
| `huggingface.co/spaces/*` | 경로 매칭 | 벤치마크 v1.1 | 90% |
| `*/blog/*`, `*/blogs/*` | 경로 매칭 | 기술 블로그 v1.1 | 85% |
| `*/docs/*`, `*/documentation/*` | 경로 매칭 | 웹사이트 v1.3 | 90% |
| (기타) | 콘텐츠 분석 | 웹사이트 v1.3 | 기본값 |

### 4.2 템플릿 구조

모든 키워드 추출 템플릿은 다음 표준 섹션을 포함한다:

- **Section 1~10**: 필수 섹션 (Executive Summary, 기본 정보, 키워드 추출, 검색 쿼리, VAMOS 매핑, 심화 분석 등)
- **검증 체크리스트**: C1~C11 (형식, 키워드 품질, 매핑 정확성 등)
- **부록**: A(용어사전), B(참조), C(변경 이력)
- **필수 필드**: 문서 ID, 작성일, 상태, 템플릿 버전

### 4.3 템플릿 파싱 규칙

1. **1차 분류**: URL의 도메인/경로 패턴으로 매칭 (정규식 기반)
2. **2차 분류**: 1차 매칭 실패 시 콘텐츠 유형 분석 (텍스트/비디오/이미지/코드)
3. **3차 폴백**: 기본 웹사이트 템플릿(v1.3) 적용

### 4.4 동적 템플릿 생성 프로세스

신규 플랫폼(예: TikTok) 발견 시:

1. **콘텐츠 유형 분석**: 숏폼 비디오 -> Instagram과 유사
2. **기존 템플릿 참조**: Instagram v1.1 (70% 유사도)
3. **차이점 식별**: 듀엣, 스티치 기능 등 고유 기능 파악
4. **신규 템플릿 초안 생성**: TikTok v0.1 (Draft) 자동 생성
5. **Human-in-the-Loop**: 사용자 검토 요청 발송
6. **승인 후 정식 등록**: TikTok v1.0으로 site_registry.json에 등록

### 4.5 지원 플랫폼 목록

| 플랫폼 | 수집 방식 | 추출 템플릿 | 상태 |
|--------|-----------|-------------|------|
| YouTube | yt-dlp 메타데이터 + 자막 | v1.2 (추출) / v2.3 (분석) | 완료 |
| Instagram | yt-dlp + Whisper 전사 | v1.1 | 완료 |
| 웹사이트 | WebFetch 스크래핑 | v1.3 | 완료 |
| GitHub | GitHub API | v1.1 | V2 예정 |
| Twitter/X | API | v1.1 | V2 예정 |
| arXiv | Semantic Scholar API | v1.1 | V2 예정 |
| Substack | RSS | v1.1 | V2 예정 |
| Discord | API | v1.1 | V2 예정 |
| HuggingFace | API | v1.1 | V2 예정 |

---

## 5. 스코어링 알고리즘

### 5.1 사이트 평가 알고리즘 (총 100점)

```python
def evaluate_site(url: str, existing_keywords: list[str]) -> SiteEvaluation:
    score = 0

    # 1. 신뢰도 점수 (0-25점)
    trust_score = 0
    if domain_age > 2_years:        trust_score += 5   # 도메인 연령
    if has_https:                    trust_score += 5   # HTTPS 지원
    if alexa_rank < 100_000:         trust_score += 5   # 글로벌 순위
    if update_frequency == "daily":  trust_score += 5   # 업데이트 빈도
    if has_author_info:              trust_score += 5   # 저자 정보 존재
    score += trust_score  # 최대 25점

    # 2. 관련성 점수 (0-30점)
    keyword_matches = count_keyword_matches(url_content, existing_keywords)
    relevance_score = min(30, keyword_matches * 2)  # 키워드당 2점, 최대 30점
    score += relevance_score

    # 3. 품질 점수 (0-25점)
    quality_score = 0
    if content_length > 1000_words:  quality_score += 10  # 충분한 콘텐츠 길이
    if has_code_examples:            quality_score += 5   # 코드 예제 포함
    if has_citations:                quality_score += 5   # 인용/출처 존재
    if is_original_content:          quality_score += 5   # 원본 콘텐츠 여부
    score += quality_score  # 최대 25점

    # 4. 접근성 점수 (0-20점)
    access_score = 0
    if allows_robots:  access_score += 5  # robots.txt 수집 허용
    if has_rss:        access_score += 5  # RSS 피드 제공
    if has_api:        access_score += 5  # API 접근 가능
    if no_paywall:     access_score += 5  # 페이월 없음
    score += access_score  # 최대 20점

    return SiteEvaluation(
        total_score=score,
        trust=trust_score,
        relevance=relevance_score,
        quality=quality_score,
        access=access_score,
        recommendation=get_recommendation(score)
    )

def get_recommendation(score: int) -> str:
    if score >= 80:   return "AUTO_APPROVE"    # 자동 승인
    elif score >= 60: return "NOTIFY_APPROVE"  # 알림 후 자동 추가
    elif score >= 30: return "MANUAL_REVIEW"   # 사용자 승인 필요
    else:             return "AUTO_REJECT"     # 자동 거부
```

### 5.2 소스 신뢰도 가중치

| 순위 | 소스 유형 | 가중치 | 예시 |
|------|-----------|--------|------|
| 1 | 공식 발표 | **1.0** | 기업 공식 블로그/문서 (OpenAI blog, Anthropic) |
| 2 | 논문/연구 | **0.9** | arXiv, peer-reviewed 학술지 |
| 3 | 기술 문서 | **0.85** | 공식 docs, API 문서 |
| 4 | 기술 블로그 | **0.7** | 기업 엔지니어링 블로그 (Netflix Tech Blog 등) |
| 5 | 뉴스 | **0.6** | 테크 미디어 (TechCrunch, The Verge 등) |
| 6 | 개인 블로그 | **0.5** | 전문가 개인 블로그 |
| 7 | SNS | **0.3** | Twitter/X, Reddit |

### 5.3 품질 예측 알고리즘 (V2+ 보완)

보완 기술: RAGAS + LLM Judge + Chain of Verification

```python
class QualityPredictor:
    def __init__(self):
        self.ragas = RAGASEvaluator()            # Faithfulness, Relevancy 메트릭
        self.llm_judge = LLMJudge()              # LLM 기반 품질 판단
        self.cov = ChainOfVerification()          # 다단계 검증

    def predict_quality(self, content) -> dict:
        ragas_score = self.ragas.evaluate(content)        # 1단계: RAGAS 메트릭
        judge_score = self.llm_judge.evaluate(content)    # 2단계: LLM Judge
        verified_score = self.cov.verify(                 # 3단계: CoV 검증
            content, ragas_score, judge_score
        )
        return {
            "predicted_quality": verified_score,
            "confidence": self._calculate_confidence(ragas_score, judge_score)
        }
```

### 5.4 신뢰도 라우팅 (C10-ALT, V3)

| 신뢰도 점수 | 라우팅 결과 | 설명 |
|-------------|-------------|------|
| >= 0.85 | AUTO_APPROVE | 자동 승인 |
| 0.60 - 0.85 | SAMPLING_REVIEW | 샘플링 검토 (일부만 인간 검토) |
| 0.40 - 0.60 | MANDATORY_REVIEW | 필수 검토 (전수 인간 검토) |
| < 0.40 | AUTO_REJECT | 자동 거부 |

---

## 6. E-15 Collector + S-5 Evolver 하이브리드 구조

### 6.1 분할 원칙

| 모듈 | 등록 위치 | 담당 Layer | 역할 |
|------|-----------|------------|------|
| **E-15 (Cloud Collector)** | E-Series (BLUE NODE) | Layer 1~6 | 데이터 수집, 발견, 평가, 추출 |
| **S-5 확장 (Cloud Evolver)** | S-Series (ORANGE CORE) | Layer 7~10 | 분석, 검증, 버전관리, 진화, 출력 |

**분할 기준**: E-15는 "외부 세계에서 데이터를 가져오는" BLUE NODE 실행 모듈이고, S-5는 "수집된 데이터로 VAMOS 자체를 진화시키는" ORANGE CORE 자가진화 엔진이다.

### 6.2 E-15 Collector 담당 기능 (10개)

| 기능 ID | 기능명 | Layer | 설명 |
|---------|--------|-------|------|
| A1 | 통합 수집 파이프라인 | L1+L4 | 단일 진입점, 자동 라우팅, 병렬 처리 |
| A4 전반 | 소스 품질 평가 | L3 | Trust/Relevance/Quality/Access 점수 (수집 전 평가) |
| C1 | 자율 사이트 발견 | L2 | 7단계 Discovery Pipeline |
| C2 | 동적 템플릿 생성 | L6 | 기존 템플릿 기반 변형/복제 |
| C7 | 적응형 우선순위 | L2+L3 | Semantic Router + Reranker 기반 수집 우선순위 |
| D1 | 외부 API 연동 | L1+L4 | 플랫폼 API, 검색 API, 학술 API |
| E1-ALT | 가이드된 자율 발견 | L2 | Seed -> Tavily -> Agentic RAG -> CrewAI |
| E4-ALT(수집부) | 수집 99% 자동화 | L4 | 예외만 인간 개입 |

### 6.3 S-5 Evolver 담당 기능 (20개)

| 기능 ID | 기능명 | Layer | 설명 |
|---------|--------|-------|------|
| A2 | Gate 자동 검증 | L8 | G0-G4 5단계 Gate |
| A3 | 버전 관리 자동화 | L9 | Semantic Versioning + CHANGELOG |
| A4 후반 | 콘텐츠 검증 | L8 | 수집 후 품질 검증 |
| B1 | 충돌 해결 엔진 | L7 | 소스 가중치 + 다수결 |
| B2 | 트렌드 분석 | L7 | 키워드 트렌드 추적, 예측 |
| B3 | 교차 소스 분석 | L7 | 상관관계, 갭 분석 |
| B4 | 패턴 인식 | L7 | 키워드/소스/매핑 패턴 |
| C3 | 규칙 제안 | L7+L10 | 패턴 -> 규칙 제안 -> 인간 승인 |
| C4 | 자동 버저닝 | L9 | 변경 유형 기반 major/minor/patch 자동 결정 |
| C5 | 패턴 기반 규칙 생성 | L7 | DSPy + LangGraph + Instructor |
| C6 | 품질 예측 | L8 | RAGAS + LLM Judge + CoV |
| C8-ALT | 가이드된 규칙 진화 | L7+L10 | Reflexion + Self-RAG + Guardrails + Human 승인 |
| C9-ALT | 패턴 기반 최적화 | L10 | DSPy + B-5 RL Trainer + 패턴 DB |
| C10-ALT | 효율적 감독 품질 | L8 | RAGAS + LLM Judge + EVX-2 + 신뢰도 라우팅 |
| D2 | 다중 포맷 내보내기 | L10 | MD, JSON, YAML, CSV, Excel, PDF |
| D3 | 대시보드 | L10 | 실시간 수집/분석 현황 |
| D4 | 알림 시스템 | L10 | Human Review 요청, 에러 알림 |
| D5 | 협업 도구 연동 | L10 | 파일 공유, 외부 도구 연동 |
| E2-ALT | 파라미터 자동 튜닝 | L10 | Reflexion -> DSPy -> 설정 자동 업데이트 |
| E3-ALT | 패턴 전이 학습 | L7+L10 | 도메인 간 패턴 재활용 |
| E5-ALT | 구조화된 통찰 생성 | L7+L10 | GraphRAG + I-20 + Cross-Source -> 인사이트 리포트 |

### 6.4 양쪽 분할 기능 (2개)

| 기능 ID | E-15 담당 | S-5 담당 |
|---------|-----------|----------|
| A4 | 수집 전 소스 평가 (L3) | 수집 후 콘텐츠 검증 (L8) |
| E4-ALT | 수집 99% 자동화 | 분석/검증 99% 자동화 (Level 3 AUTONOMOUS) |

### 6.5 E-15 <-> S-5 인터페이스

**중간 데이터 스키마**: E-15 출력(Layer 6) -> S-5 입력(Layer 7) 전달 규격은 JSON Schema 기반 계약으로 정의한다.

```json
{
  "extraction_id": "EXT-20260223-001",
  "source_url": "https://example.com/article",
  "template_used": "website_v1.3",
  "keywords": [
    {
      "term": "RAG",
      "priority": "CRITICAL",
      "vamos_mapping": ["D4", "D5"],
      "confidence": 0.92
    }
  ],
  "raw_data_path": "data_lake/raw/20260223_example.json",
  "metadata": {
    "collected_at": "2026-02-23T10:00:00Z",
    "collector_version": "E-15 v1.0"
  }
}
```

### 6.6 VAMOS 기존 모듈과의 연동

**E-15 연동**:
- I-2 (RAG 시스템): E-15 수집 데이터 -> I-2 벡터 DB 자동 삽입 (Cloud Library 핵심 가치: 빈 RAG 파이프라인 채움)
- I-1 (Brain Router): I-1이 정보 필요 시 E-15에 수집 요청 (능동적 수집 트리거)
- OTHER BRAINS: E-15 수집기들이 OTHER BRAINS(API, 외부 도구) 활용
- E-Series 동료: E-1(YouTube), E-2(Instagram) 등 기존 BLUE NODE를 서브 수집기로 재활용

**S-5 연동**:
- S-1 (Self-check/Self-evo): S-5 분석 결과를 S-1이 품질 점검
- S-4 (메타학습 파트): S-5 패턴 DB <-> S-4 패턴 분석 엔진 연동
- S-7 (VAMOS 자체 설계): S-5 인사이트 -> S-7이 아키텍처 개선 제안
- I-6 (Self-check): S-5 진화 결과를 I-6이 최종 검증
- I-3 (Memory): S-5 분석 결과를 L2(Global) 메모리에 저장
- I-20 (지식 그래프): S-5의 E5-ALT(GraphRAG) <-> I-20 관계 추론

### 6.7 전체 데이터 흐름

```
[인터넷] -> [E-15 Collector] -> [Raw Data]
                                    |
                                    +-> [I-2 RAG DB] -> [Main LLM 응답 품질 향상]
                                    |
                                    +-> [S-5 Evolver]
                                           |
                                           +-> [분석/패턴 발견] -> [S-4 메타학습]
                                           +-> [품질 검증 (Gate)] -> [I-6 Self-check]
                                           +-> [버전 관리] -> [VAMOS 문서 자동 업데이트]
                                           +-> [인사이트] -> [I-20 지식 그래프]
                                           +-> [진화 제안] -> [S-7 설계 개선] -> [Human 승인]
```

---

## 7. 스케줄러 시스템

### 7.1 크론 기반 정기 실행

| 소스 유형 | 수집 주기 | 크론 표현식 | 비고 |
|-----------|-----------|-------------|------|
| 뉴스 | 매일 1회 | `0 6 * * *` | 아침 6시 실행 |
| YouTube | 3일 1회 | `0 8 */3 * *` | 3일마다 아침 8시 |
| SNS (Twitter/X) | 매일 1회 | `0 7 * * *` | 아침 7시 실행 |
| 학술 (arXiv) | 주 1회 | `0 9 * * 1` | 매주 월요일 아침 9시 |
| 기술 블로그 | 주 2회 | `0 10 * * 1,4` | 월/목 아침 10시 |
| Instagram | 3일 1회 | `0 8 */3 * *` | 3일마다 |

V1은 수동 실행, V2부터 자동 스케줄링 활성화.

### 7.2 이벤트 트리거

- **RSS 업데이트 감지**: 구독 중인 소스에 새 콘텐츠 발행 시 자동 수집
- **사용자 질문 기반 능동 수집 (N1)**: I-2 RAG에 답이 없으면 E-15가 자동으로 해당 주제 수집 시작 (V2+)
- **Gate 실패 피드백**: S-5 Gate 거부 시 E-15에 재수집 요청 (소스 변경/추가 소스 탐색)

### 7.3 우선순위 큐

| 우선순위 | 조건 | 처리 |
|---------|------|------|
| P0 (긴급) | Human 요청 수집, CRITICAL 소스 업데이트 | 즉시 실행 |
| P1 (높음) | Gate 실패 재수집, 트렌드 급상승 키워드 | 1시간 내 실행 |
| P2 (보통) | 정기 스케줄 수집 | 스케줄 순서대로 |
| P3 (낮음) | 자율 발견 신규 사이트, 점수 60-79 사이트 | 큐 여유 시 실행 |

---

## 8. Gate 통합 검증 체계

### 8.1 G0: FORMAT GATE (형식 검증)

| 검증 항목 | 설명 | 기준 |
|-----------|------|------|
| 템플릿 섹션 완전성 | Section 1~10 존재 여부 | 필수 |
| 필수 필드 존재 | 문서 ID, 작성일, 상태 | 필수 |
| 마크다운 문법 유효성 | 문법 오류 검사 | 필수 |
| 테이블 형식 일관성 | 테이블 구조 검증 | 필수 |
| 코드 블록 닫힘 확인 | 열린 코드 블록 검사 | 필수 |

- **통과 기준**: **100%** 충족
- **실패 시**: 자동 수정 시도 -> 불가 시 거부

### 8.2 G1: CONTENT GATE (내용 검증)

| 검증 항목 | 설명 | 기준 |
|-----------|------|------|
| 키워드 최소 개수 | 10개 이상 추출 | 필수 |
| 우선순위 분류 존재 | CRITICAL/HIGH/MEDIUM/LOW | 필수 |
| 검색 쿼리 예시 포함 | 키워드별 검색 쿼리 | 필수 |
| VAMOS 연관 매핑 존재 | 4계층(RULE/PLAN/DESIGN/SCHEMA) 매핑 | 필수 |
| 출처 명시 | 추측 표현 불가: "아마도", "일반적으로" 사용 금지 | 필수 |

- **통과 기준**: **95%** 이상 충족
- **실패 시**: 누락 항목 보완 요청

### 8.3 G2: CONSISTENCY GATE (일관성 검증)

| 검증 항목 | 설명 | 기준 |
|-----------|------|------|
| 기존 키워드와 중복 확인 | 글로벌 인덱스 대조 | 필수 |
| 동의어 그룹 일관성 | LLM = Large Language Model 등 | 필수 |
| 우선순위 논리성 | CRITICAL이 LOW보다 중요 | 필수 |
| VAMOS 계층 매핑 정확성 | 올바른 계층 매핑 확인 | 필수 |
| 이전 버전과의 호환성 | 호환성 검증 | 필수 |

- **통과 기준**: **90%** 이상 충족
- **실패 시**: 충돌 항목 표시 + 해결 제안

### 8.4 G3: SECURITY GATE (보안 검증)

| 검증 항목 | 설명 | 기준 |
|-----------|------|------|
| 악성 URL 필터링 | 블랙리스트 대조 | 필수 |
| 민감 정보 누출 방지 | API 키, 비밀번호 패턴 탐지 | 필수 |
| 저작권 침해 콘텐츠 필터 | 저작권 검사 | 필수 |
| 스팸/광고 콘텐츠 필터 | 스팸 검사 | 필수 |
| 비윤리적 콘텐츠 필터 | 윤리 검사 | 필수 |

- **통과 기준**: **100%** 충족 (보안은 타협 불가)
- **실패 시**: 즉시 거부 + 알림

### 8.5 G4: FINAL GATE (최종 검증)

| 검증 항목 | 설명 | 기준 |
|-----------|------|------|
| G0-G3 모두 통과 확인 | 전 Gate 통과 필수 | 필수 |
| 변경 영향 범위 분석 완료 | 영향받는 VAMOS 문서 파악 | 필수 |
| 롤백 가능 여부 확인 | 체크포인트 존재 확인 | 필수 |
| Human 승인 필요 여부 | 정책에 따라 결정 | 조건부 |
| 배포 준비 상태 확인 | 모든 전제조건 충족 | 필수 |

- **통과 기준**: 체크리스트 **100%** 완료
- **통과 시**: 버전 업데이트 + 배포

### 8.6 Gate 검증 결과 JSON 형식

```json
{
  "document_id": "VAMOS_WEB_AMD_KEYWORD_v1.0",
  "validation_time": "2026-01-23T14:30:00Z",
  "gates": {
    "G0_FORMAT": {
      "passed": true, "score": 100,
      "checks": {
        "template_sections": "PASS",
        "required_fields": "PASS",
        "markdown_syntax": "PASS",
        "table_format": "PASS",
        "code_blocks": "PASS"
      }
    },
    "G1_CONTENT": {
      "passed": true, "score": 98,
      "checks": {
        "min_keywords": "PASS (45 keywords)",
        "priority_classification": "PASS",
        "search_queries": "PASS",
        "vamos_mapping": "PASS",
        "source_citation": "PARTIAL (2 items need review)"
      }
    },
    "G2_CONSISTENCY": {
      "passed": true, "score": 95,
      "checks": {
        "duplicate_check": "PASS",
        "synonym_consistency": "PASS",
        "priority_logic": "PASS",
        "vamos_accuracy": "PASS",
        "version_compatibility": "PASS"
      }
    },
    "G3_SECURITY": {
      "passed": true, "score": 100,
      "checks": {
        "malicious_url": "PASS",
        "sensitive_info": "PASS",
        "copyright": "PASS",
        "spam_filter": "PASS",
        "ethical_filter": "PASS"
      }
    },
    "G4_FINAL": {
      "passed": true,
      "human_approval_required": false,
      "ready_for_deploy": true
    }
  },
  "overall_result": "PASS",
  "recommended_action": "DEPLOY"
}
```

### 8.7 PolicyGate / CostGate 연동

Cloud Library의 Gate 시스템은 VAMOS DESIGN D7 (Safety/Cost/Approval)의 PolicyGate 및 CostGate와 연동한다:

- **PolicyGate 연동**: G3 Security Gate의 검증 정책은 VAMOS RULE의 윤리/법규 정책(Section 5)과 동기화
- **CostGate 연동**: V1/V2/V3 비용 모드에 따라 Cloud Library 호출 수준 제어
  - V1: E-15만 동작 (수집 -> 저장), S-5는 수동 트리거
  - V2: E-15 + S-5 반자동
  - V3: 전체 자율
- Brain Router(I-1)가 비용 모드에 따라 Cloud Library 호출 수준을 제어

---

## 9. 저장소 구조

### 9.1 파일 시스템 구조

```
CLOUD_LIBRARY/
  CONFIG/                    -- 설정 파일
    site_registry.json       -- 승인된 사이트 레지스트리
    source_priority.json     -- 소스 신뢰도 가중치 설정
    gate_rules.json          -- G0-G4 Gate 검증 규칙
    evolution_policy.json    -- 자가 진화 정책 설정
    blacklist.json           -- 차단 사이트 목록
    keyword_pool.json        -- 시드 키워드 풀
  DATA_LAKE/                 -- 데이터 저장소
    raw/                     -- 원본 데이터 (JSON/Markdown)
    normalized/              -- 정규화 데이터
  EXTRACTED/                 -- 추출된 키워드 결과
  ANALYZED/                  -- 분석 결과
  VERSIONS/                  -- 버전 히스토리 + 체크포인트
  SYSTEM/                    -- 시스템 문서
    VAMOS_CLOUD_LIBRARY_PLAN_v1_0.md
    VAMOS_CLOUD_LIBRARY_DESIGN_v1_0.md
    VAMOS_CLOUD_LIBRARY_SCHEMA_v1_0.md
  COLLECTORS/                -- 수집기 스크립트
    youtube_collector.py
    instagram_collector.py
    website_collector.py
```

### 9.2 벡터 DB 연동 (I-2 RAG)

- **V1**: Local embedding (파일 기반)
- **V2+**: API embedding -> 벡터 DB 삽입
- **자동 임베딩 트리거**: Gate G4 통과 후 자동으로 임베딩 생성 -> I-2 벡터 DB에 삽입
- **증분 임베딩 (N8)**: 전체 재임베딩 대신 변경 부분만 증분 임베딩 (V2+)

### 9.3 메타데이터 인덱스

- **V0-V1**: 파일 시스템 + JSON 인덱스
- **V1-V2**: SQLite + JSONL 로그
- **V2+**: Postgres + 시계열 분석

인덱싱 항목: 문서 ID, 소스 URL, 수집일, 키워드 목록, 평가 점수, Gate 통과 여부, 버전 번호

### 9.4 캐시 정책

- **수집 데이터 캐시**: 동일 URL 24시간 내 재수집 방지
- **평가 결과 캐시**: 사이트 평가 점수 7일간 캐시 (변경 감지 시 무효화)
- **키워드 인덱스 캐시**: 글로벌 키워드 인덱스 인메모리 캐시 (변경 시 즉시 업데이트)

### 9.5 데이터 신선도 관리 (TTL)

| 데이터 유형 | TTL | 만료 시 처리 |
|------------|-----|-------------|
| 기술 트렌드 | 30일 | 자동 재수집 |
| 뉴스/SNS | 7일 | 폐기 또는 아카이브 |
| 학술 논문 | 365일 | 유효성 재검토 |
| 공식 문서 | 90일 | 변경 확인 후 갱신 |

---

## 10. 충돌 해결 엔진

### 10.1 충돌 해결 알고리즘

동일 주제에 대해 소스 간 상반된 정보가 발견될 때의 해결 절차:

**Step 1: 소스 신뢰도 가중치 적용** (섹션 5.2 참조)

**Step 2: 다수결 원칙 적용**

| 조건 | 처리 방식 |
|------|-----------|
| 3개 이상 소스 일치 | 자동 채택 |
| 2개 소스 일치 | 높은 신뢰도 소스 우선 채택 + 경고 플래그 |
| 단일 소스만 존재 | 신뢰도 검토 + 경고 표시 |
| 모두 불일치 (해결 불가) | `CONFLICT_FLAG=true` + Human Review 대기열 등록 |

**Step 3: 결과 기록**

```json
{
  "keyword": "GPT-4 parameters",
  "adopted_value": "not disclosed (official)",
  "conflict_sources": ["Twitter", "News"],
  "resolution_method": "highest_trust_source",
  "confidence": 0.85,
  "human_review_needed": false,
  "alternatives": [
    {"value": "~1.8T", "source": "estimates", "trust_weight": 0.3}
  ]
}
```

### 10.2 분쟁 감사 로그 (Audit Trail, N7)

충돌 해결 시 어떤 소스가 선택/기각되었는지 전체 이력 보존. V1부터 적용하여 진화 결정의 투명성 보장.

---

## 11. 오류 처리 및 재시도 로직

### 11.1 Checkpoint & Resume System

- 각 Layer 처리 완료 시 체크포인트 자동 저장
- 실패 발생 시 마지막 성공 체크포인트부터 재시작 (처음부터 재시작 불필요)
- 체크포인트 보존 기간: 7일

### 11.2 재시도 정책

| 상황 | 재시도 횟수 | 백오프 전략 | 실패 후 처리 |
|------|------------|-------------|-------------|
| 네트워크 오류 | 최대 3회 | 지수 백오프 (1s, 2s, 4s) | 큐에 재등록 (P1 우선순위) |
| API 제한 (Rate Limit) | 최대 5회 | 고정 대기 (Rate Limit 해제까지) | 다음 스케줄로 연기 |
| 파싱 오류 | 최대 2회 | 즉시 재시도 (다른 파서) | Human Review 요청 |
| Gate 검증 실패 | 최대 3회 | 자동 수정 후 즉시 | Human Review 요청 |
| Gate 3회 연속 실패 | - | - | Human Review 대기열 등록 |

### 11.3 진화 안전장치

| 안전장치 | 상세 |
|---------|------|
| **Rate Limiting** | 하루 최대 버전 증가 5회, 연속 실패 3회 시 자동 중단, 쿨다운 1시간 |
| **Change Size Limit** | 단일 변경 최대 키워드 50개, 최대 파일 5개, 초과 시 분할 또는 Human 승인 |
| **Rollback Policy** | 롤백 가능 기간 7일, 정확도 10% 이상 하락 시 자동 롤백, 롤백 후 동일 변경 재시도 24시간 금지 |
| **Audit Trail** | 모든 자동 결정 로깅 필수, 결정 근거(reason) 필수 기록, 주간 진화 보고서 자동 생성 |

### 11.4 Gate 실패 피드백 루프

Gate 거부 시 S-5 -> E-15에 재수집 요청:
1. 거부 사유 분석 (소스 품질 문제? 데이터 부족? 충돌?)
2. E-15에 소스 변경 또는 추가 소스 탐색 요청
3. 재수집 후 다시 Gate 검증 파이프라인 진입

---

## 12. 자가 진화 시스템 (S Feature)

### 12.1 S1: PATTERN RECOGNITION (패턴 인식)

- 기존 키워드 추출 결과 분석
- 성공/실패 패턴 식별
- 빈번히 등장하는 새 용어 탐지
- 소스별 품질 점수 추적
- **예시**: "RAG" 키워드가 최근 3개월 동안 50% 증가 -> 트렌드 감지

### 12.2 S2: RULE GENERATION (규칙 생성)

- 새로운 키워드 카테고리 제안
- 검색 쿼리 패턴 개선 제안
- 템플릿 구조 최적화 제안
- 소스 우선순위 조정 제안
- **예시**: "RAG 관련 키워드가 많음 -> 'Retrieval' 하위 카테고리 추가 제안"
- **V2+ 보완**: DSPy + LangGraph + Instructor로 규칙 생성 패턴화

### 12.3 S3: VALIDATION (검증)

- 제안된 규칙의 시뮬레이션 실행
- 기존 데이터에 적용 시 영향 분석
- 예상 정확도/커버리지 계산
- Gate G0-G4 자동 통과 시험
- **예시**: "새 카테고리 적용 시 키워드 분류 정확도 +5% 예상"

### 12.4 S4: DEPLOYMENT (배포)

- Human-in-the-Loop 승인 요청 (CRITICAL 변경 시)
- 자동 배포 (MINOR 변경 시, 설정에 따라)
- 체크포인트 생성
- 변경 이력 기록
- **예시**: "[승인 요청] 새 카테고리 'Retrieval' 추가 - 영향: 템플릿 3개"

### 12.5 S5: FEEDBACK LOOP (피드백 학습)

- 배포 후 성과 측정 (예상 vs 실제 비교)
- 실패 시 롤백 + 원인 분석
- 성공 패턴 강화 학습 (패턴 DB 업데이트)
- **예시**: "새 카테고리 적용 후 키워드 정확도 +7% (예상 +5% 초과)" -> 유사 패턴 신뢰도 상향

### 12.6 진화 제어 정책

| 변경 유형 | 자동 허용 | 알림 필요 | Human 승인 |
|-----------|-----------|-----------|------------|
| 오타 수정 | O | X | X |
| 키워드 1-5개 추가 | O | X | X |
| 키워드 6-20개 추가 | X | O | X |
| 키워드 20개+ 추가 | X | O | O |
| 새 검색 쿼리 추가 | O | X | X |
| 소스 신뢰도 조정 | X | O | X |
| 새 카테고리 추가 | X | O | O |
| 템플릿 구조 변경 | X | O | O |
| 새 사이트 자동 추가 | 설정에 따름 | 설정에 따름 | 설정에 따름 |

### 12.7 V3 보완 기술

| 기능 | 보완 기술 | 효과 |
|------|-----------|------|
| C8-ALT 가이드된 규칙 진화 | Reflexion -> Self-RAG -> Guardrails AI -> S-1 -> Human 승인 | 25% -> 75% |
| C9-ALT 패턴 기반 최적화 | DSPy(#40+B-6) -> B-5 RL Trainer -> S-4 -> 패턴 DB | 20% -> 70% |
| C10-ALT 효율적 감독 | RAGAS -> LLM Judge -> EVX-2 -> 신뢰도 라우팅 | 30% -> 85% |
| E2-ALT 파라미터 튜닝 | S-1 -> Reflexion -> DSPy -> S-7 -> 설정 자동 업데이트 | 15% -> 70% |
| E3-ALT 패턴 전이 학습 | 도메인A 패턴 -> 추상화 -> 패턴DB -> 도메인B 특화 -> B-5 -> S-4 | 10% -> 65% |
| E5-ALT 구조화된 통찰 | GraphRAG -> I-20 지식 그래프 -> Cross-Source -> S-8 리포트 | 20% -> 70% |

### 스킬 큐레이션 및 공식 벤더 인증 [REF:영상4]

> find-skills 같은 검증된 스킬 목록 관리 및 공식 벤더 인증 마크 시스템

| 등급 | 마크 | 조건 |
|------|------|------|
| Official | [OFFICIAL] | VAMOS 팀 직접 개발/검수 |
| Verified | [VERIFIED] | 보안 스캔 통과 + 커뮤니티 평점 4.0+ |
| Community | [COMMUNITY] | 코드 공개 + 기본 스캔 통과 |
| Unverified | [UNVERIFIED] | 미검증 → 설치 시 경고 |

- **카탈로그 관리**: VAMOS Cloud Library 내 `/skills/catalog.yaml`
- **자동 추천**: 사용자 작업 패턴 기반 스킬 추천 (B-5 Skill Store Manager 연동)

---

## 13. V0/V1/V2/V3 버전별 구현 로드맵

### 13.1 V0 (기초 구조) - 로컬 단일 프로세스

| 모듈 | 적용 기능 | 구현 내용 | 기술 스택 |
|------|-----------|-----------|-----------|
| E-15 | A1 기초 | 수동 URL 입력 -> 단일 수집기(yt-dlp) | Python CLI, yt-dlp |
| E-15 | L5 기초 | Markdown/JSON 파일 저장 | 파일 시스템 |
| E-15 | L6 기초 | 기존 키워드 추출 템플릿 v1.2 적용 | 템플릿 매칭 |
| S-5 | A4 기초 | 수동 체크리스트 품질 검증 | 수동 |
| - | - | Cloud Library 자체 미활성 (기존 템플릿만 사용) | - |

### 13.2 V1 (기본 멀티모달) - 로컬 + 일부 GPT-4o mini

**E-15 (Collector) V1**:

| 기능 | 구현 내용 | 기술 스택 |
|------|-----------|-----------|
| A1 통합 수집 | 단일 진입점, 자동 라우팅, 병렬 처리 | Python asyncio, yt-dlp, WebFetch |
| A4 전반 소스 평가 | Trust/Relevance/Quality/Access 점수 (0-100) | 규칙 기반 평가 |
| C7 기초 우선순위 | 수동 + 규칙 기반 수집 우선순위 | JSON 설정 파일 |
| D1 기초 API | YouTube Data API, 기본 웹 스크래핑 | API 클라이언트 |
| L1-L6 파이프라인 | Input -> Discovery(수동) -> Evaluation -> Collection -> Data Lake -> Extraction | SQLite + JSONL |

**S-5 (Evolver) V1**:

| 기능 | 구현 내용 | 기술 스택 |
|------|-----------|-----------|
| A2 Gate 기초 | G0(Format) + G1(Content) 자동화 (G2-G4 수동) | 규칙 기반 검증 |
| A3 버전 관리 | Semantic Versioning + CHANGELOG 자동 생성 | Git 연동 |
| A4 후반 품질 검증 | 기본 품질 검증 (규칙 기반) | 체크리스트 자동화 |
| B1 기초 충돌 해결 | 소스 가중치 기반 단순 충돌 해결 | 우선순위 규칙 |
| L7-L9 파이프라인 | Analysis(기초) -> Validation(반자동) -> Version Control | SQLite + JSONL 로그 |

**V1 코드블럭**: CB1 기초 (Phase A 집중, 95% 구현 목표)

### 13.3 V2 (확장 멀티모달) - Docker Compose + GPT-4o mini/GPT-4o

**E-15 (Collector) V2**:

| 기능 | 구현 내용 | 기술 스택 |
|------|-----------|-----------|
| A1 완성 | 멀티 플랫폼 수집 (YouTube+Instagram+Web+Blog+학술) | Platform Collectors 모듈화 |
| C1 자율 사이트 발견 | 7단계 Discovery Pipeline (인간 승인 필수) | GPT-4o mini + 검색 API |
| C2 동적 템플릿 | 기존 템플릿 기반 변형 (복제+수정) | LLM 기반 템플릿 변형 |
| C7 적응형 우선순위 | Semantic Router + Reranker | Semantic Router |
| D1 확장 | Google/Bing 검색 API, Semantic Scholar, RSS | REST/GraphQL |
| E1-ALT 기초 | Seed 기반 가이드된 발견 (Layer 1-3) | Tavily Search |

**S-5 (Evolver) V2**:

| 기능 | 구현 내용 | 기술 스택 |
|------|-----------|-----------|
| A2 완성 | G0-G4 전체 Gate 자동화 | 규칙 엔진 + LLM 보조 |
| B1 완성 | 소스 가중치 + 다수결 + 충돌 로그 | Postgres + 충돌 해결 알고리즘 |
| B2 트렌드 분석 | 키워드 트렌드 추적, 기초 예측 | Postgres 집계 + 시계열 |
| B3 교차 소스 분석 | 상관관계/갭 분석 | Cross-Source Analyzer |
| B4 패턴 인식 | 키워드/소스/VAMOS 패턴 | 패턴 DB (Postgres) |
| C3 규칙 제안 | 패턴 -> 규칙 제안 -> 인간 승인 | LLM 기반 제안 |
| C4 자동 버저닝 | major/minor/patch 자동 결정 | 규칙 기반 |
| C5 패턴 기반 규칙 | DSPy + LangGraph + Instructor | DSPy, LangGraph |
| C6 품질 예측 | RAGAS + LLM Judge + CoV | RAGAS, GPT-4o mini |
| D2-D5 | 포맷 내보내기, 대시보드, 알림, 협업 | Web Dashboard, 웹훅 |

**V2 코드블럭**: CB2/CB3 (Phase A완성 + B완성 + C부분 + D완성)

### 13.4 V3 (AGI 고도화) - K8s + vLLM + 매니지드 서비스

**E-15 (Collector) V3**:

| 기능 | 구현 내용 | 기술 스택 |
|------|-----------|-----------|
| C1 완성 | 완전 자율 Discovery + 인간 승인 | 멀티 에이전트 탐색 |
| C2 완성 | 완전 동적 템플릿 생성 (신규 구조 가능) | LLM 기반 생성 |
| E1-ALT 완성 | 가이드된 자율 발견 (5-Layer 완전 구현) | Agentic RAG + CrewAI + Tavily |
| E4-ALT 수집부 | 수집 99% 자동화 | 자율 에이전트, WebSocket Streams |
| D1 고급 | Kafka/Redis 스트리밍, WebSocket 실시간 | Kafka, Redis |

**S-5 (Evolver) V3**:

| 기능 | 구현 내용 | 기술 스택 |
|------|-----------|-----------|
| C8-ALT | 가이드된 규칙 진화 | Reflexion, Self-RAG, Guardrails AI |
| C9-ALT | 패턴 기반 최적화 | DSPy, B-5, B-6 |
| C10-ALT | 효율적 감독 품질 | RAGAS, LLM Judge, EVX-2 |
| E2-ALT | 파라미터 자동 튜닝 | Reflexion, DSPy, S-1, S-7 |
| E3-ALT | 패턴 전이 학습 | 패턴 DB, B-5, S-4 |
| E4-ALT 분석부 | Level 3 AUTONOMOUS | LangSmith, LangFuse, Guardrails |
| E5-ALT | 구조화된 통찰 | GraphRAG, Neo4j, I-20, S-8 |

**V3 코드블럭**: CB4 (A+B+C대체+D+E대체 전체 구현, 보완 후 86%)

### 13.5 기술 스택 진화 요약

| 시기 | 수집 | 저장 | 분석 | 검증 | UI |
|------|------|------|------|------|-----|
| V0 (현재) | yt-dlp, WebFetch | Markdown, JSON | 템플릿 기반 | 수동 | CLI |
| V1 | + GitHub API | + SQLite, JSONL | + 규칙 매칭 | + G0-G1 자동 | CLI + 파일 |
| V2 | + RSS, GraphQL, 검색 API | + Postgres, ChromaDB | + LLM API, Embedding | + G0-G4 자동 | Web Dashboard |
| V3 | + WebSocket, Kafka, 멀티에이전트 | + Neo4j, Pinecone | + Fine-tuned LLM, RAG | + 이상 탐지 ML | REST API, SDK |

---

## 14. API 엔드포인트

### 14.1 Tauri IPC (V1)

| 커맨드 | 설명 | 입력 | 출력 |
|--------|------|------|------|
| `cloud_library.collect` | 단일 URL 수집 요청 | `{url, template_hint?}` | `CollectionResult` |
| `cloud_library.batch_collect` | 일괄 수집 요청 | `{urls: string[]}` | `BatchResult` |
| `cloud_library.evaluate_site` | 사이트 평가 | `{url}` | `SiteEvaluation` |
| `cloud_library.get_status` | 시스템 상태 조회 | `{}` | `SystemStatus` |
| `cloud_library.get_keywords` | 키워드 목록 조회 | `{filter?, page?}` | `KeywordList` |
| `cloud_library.validate` | Gate 검증 실행 | `{document_id}` | `GateResult` |
| `cloud_library.rollback` | 롤백 실행 | `{version}` | `RollbackResult` |

### 14.2 JSON-RPC (V2+)

```json
// 수집 요청
{
  "jsonrpc": "2.0",
  "method": "cloud_library.collect",
  "params": {
    "url": "https://example.com/article",
    "template_hint": "website_v1.3",
    "priority": "P2"
  },
  "id": 1
}

// 응답
{
  "jsonrpc": "2.0",
  "result": {
    "collection_id": "COL-20260223-001",
    "status": "queued",
    "estimated_completion": "2026-02-23T10:05:00Z"
  },
  "id": 1
}
```

### 14.3 REST API (V2+)

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/v1/collect` | 수집 요청 |
| POST | `/api/v1/collect/batch` | 일괄 수집 |
| GET | `/api/v1/sites` | 등록 사이트 목록 |
| GET | `/api/v1/sites/{id}/evaluate` | 사이트 평가 |
| GET | `/api/v1/keywords` | 키워드 목록 |
| POST | `/api/v1/validate/{document_id}` | Gate 검증 |
| POST | `/api/v1/rollback/{version}` | 롤백 |
| GET | `/api/v1/status` | 시스템 상태 |
| GET | `/api/v1/changelog` | 변경 이력 |
| GET | `/api/v1/dashboard` | 대시보드 데이터 |
| POST | `/api/v1/discover` | 자율 사이트 발견 트리거 |

---

## 15. Pydantic v2 스키마 정의

### 15.1 핵심 스키마

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class ApprovalMode(str, Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    NOTIFY_APPROVE = "NOTIFY_APPROVE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    AUTO_REJECT = "AUTO_REJECT"

class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"

# --- 사이트 평가 ---
class SiteEvaluation(BaseModel):
    url: str
    total_score: int = Field(ge=0, le=100)
    trust: int = Field(ge=0, le=25, description="도메인 연령, HTTPS, 순위, 빈도, 저자")
    relevance: int = Field(ge=0, le=30, description="VAMOS 키워드 매칭률")
    quality: int = Field(ge=0, le=25, description="콘텐츠 길이, 코드, 인용, 원본성")
    access: int = Field(ge=0, le=20, description="robots, RSS, API, 페이월")
    recommendation: ApprovalMode
    evaluated_at: datetime

# --- 키워드 ---
class Keyword(BaseModel):
    term: str
    priority: Priority
    vamos_mapping: list[str] = Field(description="RULE/PLAN/DESIGN/SCHEMA 매핑")
    source_url: str
    confidence: float = Field(ge=0.0, le=1.0)
    synonyms: list[str] = []

# --- 수집 요청 ---
class CollectionRequest(BaseModel):
    url: str
    template_hint: Optional[str] = None
    priority_level: str = "P2"
    requester: str = "system"

# --- Gate 검증 결과 ---
class GateCheck(BaseModel):
    name: str
    passed: bool
    score: int = Field(ge=0, le=100)
    details: dict = {}

class GateResult(BaseModel):
    document_id: str
    validation_time: datetime
    g0_format: GateCheck
    g1_content: GateCheck
    g2_consistency: GateCheck
    g3_security: GateCheck
    g4_final: GateCheck
    overall_passed: bool
    human_approval_required: bool
    recommended_action: str  # "DEPLOY" | "REVIEW" | "REJECT"

# --- 충돌 해결 ---
class ConflictResolution(BaseModel):
    keyword: str
    adopted_value: str
    conflict_sources: list[str]
    resolution_method: str  # "highest_trust_source" | "majority_vote" | "human_review"
    confidence: float = Field(ge=0.0, le=1.0)
    human_review_needed: bool
    alternatives: list[dict] = []

# --- 버전 관리 ---
class VersionChange(BaseModel):
    document_id: str
    old_version: str
    new_version: str
    change_type: str  # "MAJOR" | "MINOR" | "PATCH"
    changes: list[str]
    affected_layers: list[str]
    rollback_possible: bool
    created_at: datetime

# --- 사이트 레지스트리 ---
class SiteRegistryEntry(BaseModel):
    url: str
    template_id: str
    evaluation_score: int
    approval_mode: ApprovalMode
    registered_at: datetime
    collection_interval_days: int
    last_collected_at: Optional[datetime] = None
    total_collections: int = 0
    gate_pass_rate: float = 0.0
```

---

## 16. LOCK 결정사항

다음 항목은 확정(LOCK)되어 변경 불가한 설계 결정이다.

### 16.1 아키텍처 LOCK

| # | 결정 사항 | 근거 |
|---|-----------|------|
| L1 | **10-Layer 아키텍처 유지** | Input -> Discovery -> Evaluation -> Collection -> Data Lake -> Extraction -> Analysis -> Validation -> Version Control -> Output |
| L2 | **E-15/S-5 하이브리드 분할** | E-15(BLUE NODE) = L1-L6 수집, S-5(ORANGE CORE) = L7-L10 진화 |
| L3 | **5단계 Gate 시스템 (G0-G4)** | G0 Format(100%), G1 Content(95%), G2 Consistency(90%), G3 Security(100%), G4 Final(100%) |
| L4 | **Semantic Versioning MAJOR.MINOR.PATCH** | MAJOR=호환성 변경, MINOR=키워드 10+/섹션 추가, PATCH=오타/소수 변경 |

### 16.2 스코어링 LOCK

| # | 결정 사항 | 근거 |
|---|-----------|------|
| L5 | **평가 점수 배분 (100점)**: Trust 25, Relevance 30, Quality 25, Access 20 | 관련성 최우선 |
| L6 | **승인 임계값**: AUTO>=80, NOTIFY 60-79, MANUAL 30-59, BLOCK<30 | 품질-효율 균형 |
| L7 | **소스 가중치 7단계**: 공식(1.0) > 논문(0.9) > 기술문서(0.85) > 기술블로그(0.7) > 뉴스(0.6) > 개인블로그(0.5) > SNS(0.3) | 신뢰도 순위 |

### 16.3 진화 정책 LOCK

| # | 결정 사항 | 근거 |
|---|-----------|------|
| L8 | **S1-S5 진화 단계**: Pattern Recognition -> Rule Generation -> Validation -> Deployment -> Feedback Loop | 안전한 점진적 진화 |
| L9 | **Human-in-the-Loop 필수**: CRITICAL 변경, 키워드 20+개 추가, 새 카테고리, 템플릿 구조 변경 시 | 안전성 보장 |
| L10 | **일일 버전 증가 상한 5회**, 연속 실패 3회 시 자동 중단 | 진화 속도 제어 |

### 16.4 하이브리드 LOCK

| # | 결정 사항 | 근거 |
|---|-----------|------|
| L11 | **코드블럭 적용 순서**: CB1(V1-V2) -> CB3(V2) -> CB4(V3) | 점진적 확장 |
| L12 | **비현실적 기능 대체 필수**: C8(25%->75%), C9(20%->70%), C10(30%->85%), E1-E5 모두 ALT 버전 사용 | 실용성 우선 |
| L13 | **E-15 오케스트레이터 역할**: 기존 E-1(YouTube), E-2(Instagram) 등을 서브 수집기로 재활용 | 중복 방지 |

---

## 17. 보안 및 비용 제약

### 17.1 보안 제약

| 항목 | 제약 | 적용 Gate |
|------|------|-----------|
| 악성 URL 차단 | blacklist.json 대조, 실시간 위협 DB 연동(V2+) | G3 |
| 민감 정보 보호 | API 키, 비밀번호 패턴 자동 탐지 및 마스킹 | G3 |
| 저작권 준수 | robots.txt 존중 필수, API 우선, RSS 활용 | G3 + 수집 정책 |
| 윤리적 수집 | 비윤리적 콘텐츠 자동 필터링 | G3 |
| 데이터 보존 | 수집 데이터 암호화 저장(V2+), 접근 로그 기록 | 전체 |
| 감사 추적 | 모든 자동 결정에 대한 로깅 및 근거 기록 필수 | 전체 |

### 17.2 비용 제약

| 항목 | V1 | V2 | V3 |
|------|-----|-----|-----|
| LLM API 호출 | 최소화 (규칙 기반 우선) | GPT-4o mini 중심, GPT-4o 선택적 | vLLM 자체 호스팅 |
| 검색 API | 무료 티어 (DuckDuckGo) | Google/Bing 유료 API | 대량 할인 계약 |
| 임베딩 | 로컬 모델 | API 임베딩 (비용 모니터링) | 자체 임베딩 서버 |
| 스토리지 | 로컬 파일 | Postgres + 벡터 DB | 분산 저장소 |
| 비용 모니터링 | 수동 | CostGate 자동 모니터링 | 실시간 비용 대시보드 |

**CostGate 연동**: Brain Router(I-1)가 비용 모드(V1/V2/V3)에 따라 Cloud Library 호출 수준을 자동 제어한다.

### 17.3 수집 빈도 제한

| 플랫폼 | Rate Limit | 대응 |
|--------|-----------|------|
| YouTube Data API | 10,000 quota/day | 쿼터 모니터링, 초과 시 yt-dlp 폴백 |
| Google Search API | 100 queries/day (무료) | 검색 쿼리 최적화, 캐싱 |
| GitHub API | 5,000 req/hour | 토큰 기반 인증, 요청 배치 |
| 일반 웹사이트 | robots.txt Crawl-delay 준수 | Rate Limiter 적용 |

---

## 18. VAMOS 4계층 연계

### 18.1 Cloud Library -> VAMOS 매핑

| VAMOS 계층 | 연계 내용 | 연계 파일 |
|-----------|-----------|-----------|
| **RULE** | Cloud Library 운영 정책, 데이터 수집 윤리 규정, 자가 진화 제한 규칙, Human-in-the-Loop 정책 | VAMOS_RULE_1.3_BASE.md (Section 4, 5, 6) |
| **PLAN** | Cloud Library 구축 로드맵, 데이터 수집 일정 계획, 진화 단계 계획, 리소스 할당 | VAMOS_PLAN_3_0 (Section 2, 4.1) |
| **DESIGN** | 아키텍처 설계, 수집/분석/진화 파이프라인, Gate 검증, 버전 관리 시스템 | D4(Infra Core), D5(Agent Workflow), D6(Storage Memory), D7(Safety Cost) |
| **SCHEMA** | 키워드 데이터 스키마, 소스 메타데이터, 버전 이력, Gate 결과 | D1(Glossary), D6(Storage), D7(Safety) |

### 18.2 키워드 -> VAMOS 계층 자동 매핑 규칙

| 키워드 카테고리 | RULE | PLAN | DESIGN | SCHEMA |
|----------------|------|------|--------|--------|
| LLM/모델 | Section 1 | Section 5.2 | D2, D3 | D2, D3 |
| RAG/검색 | Section 4 | Section 4.1 | D4, D5 | D4, D5 |
| Agent/워크플로우 | - | Section 3 | D5 | D5 |
| 인프라/배포 | Section 3 | Section 1 | D4 | D4 |
| 데이터/저장 | - | Section 2 | D6 | D6 |
| 안전/비용 | Section 5, 6 | - | D7 | D7 |
| UI/UX | - | - | D8 | D8 |
| 보안/윤리 | Section 5 | - | D7 | D7 |

---

## 19. 구현 가능성 평가 및 핵심 수치

### 19.1 Phase별 구현 가능성

| Phase | 구현 가능성 (원래) | 보완 후 | 상태 |
|-------|-------------------|---------|------|
| Phase A (기초 자동화) | 95% | 95% | 현재 기술로 완전 구현 가능 |
| Phase B (지능형 분석) | 70% | 70% | LLM 환각 등 제한 있으나 실용적 |
| Phase C (자율 진화) | 37.5% | **76.7%** | 보완 기술 적용으로 대폭 상승 |
| Phase D (생태계 확장) | 80% | 80% | API 통합, 대시보드 등 표준 기술 |
| Phase E (완전 자율 -> 대체) | 19% | **72%** | ALT 버전으로 실용성 확보 |

### 19.2 코드블럭별 구현 가능성

| 코드블럭 | Phase 구성 | 원래 | 보완 후 | 적용 시점 |
|---------|------------|------|---------|-----------|
| CB1 | A+B+D | 85% | 85% | V1-V2 |
| CB2 | A+B+D+C옵션 | 75% | 82% | V2 중반 |
| CB3 | A+B+D+C대체 | 82% | **88%** | V2 후반 |
| CB4 | A+B+D+C+E대체 | 79% | **86%** | V3 |

### 19.3 기술적 한계

| 한계 | 문제 | 영향 | 대응 |
|------|------|------|------|
| LLM 환각 | 존재하지 않는 정보 생성 | 자율 의사결정 신뢰성 저하 | RAGAS + CoV + Guardrails AI |
| 비결정적 출력 | 같은 입력에 다른 출력 | 일관된 자율 동작 어려움 | Structured Outputs + Instructor + temperature 조절 |
| 장기 기억 부재 | 세션 간 학습 유지 불가 | 지속적 자기 개선 어려움 | MemGPT + 패턴 DB + L2 Global Memory |
| 인과 추론 한계 | 상관관계 vs 인과관계 구분 어려움 | 자율 의사결정 품질 저하 | Human-in-the-Loop 필수 |

### 19.4 핵심 수치 종합

| 항목 | 값 |
|------|-----|
| 아키텍처 계층 | 10개 (Layer 1-10) |
| Gate 검증 단계 | 5단계 (G0-G4) |
| 자가 진화 단계 | 5단계 (S1-S5) |
| 발전 로드맵 Phase | 5단계 (A-E) |
| 자율 발견 Pipeline | 7단계 (Stage 1-7) |
| 기존 단점 분석 | 10개 (W1-W10), 전부 극복 방안 수립 |
| 유사 시스템 비교 | 8개 (RAG, KG, MLOps, Semantic Web, AutoML, Zettelkasten, Crawler, RSS) |
| 코드블럭 버전 | 4개 (CB1-CB4) |
| E-15 담당 기능 | 10개 |
| S-5 담당 기능 | 20개 |
| 전체 기능 | 30개 (누락 없이 매핑 완료) |
| 최종 구현 가능성 (CB4) | **86%** (보완 후) |
| 권장 구현 순서 | A -> B -> D -> C-ALT -> E-ALT |
| 예상 구현 기간 | V0-V3 전체 10-15개월 |

### 19.5 개선 제안 사항 (Hybrid Roadmap 기반)

**핵심 개선 7건**:

| # | 개선 영역 | 현재 | 개선 방향 | **정의 (LOCK)** |
|---|-----------|------|-----------|----------------|
| G1 | E-15 <-> S-5 인터페이스 | **정의 완료** | JSON Schema 기반 계약 확정 | E-15 출력(Layer 6) -> S-5 입력(Layer 7) 전달 규격: `CollectorOutput` JSON Schema (source_id, extracted_keywords[], category, raw_data_path, metadata). 동기화 전략: E-15는 수집 완료 시 `collector.output.ready` 이벤트 발행 -> S-5가 구독하여 pull 방식으로 데이터 수신. 충돌 해결: 동일 소스 중복 수집 시 timestamp 최신 우선 + content_hash 비교로 dedup 처리. |
| G2 | 비용 모드별 동작 | **정의 완료** | V1/V2/V3별 차등 동작 정의 | V1: E-15만 동작(수집->저장), S-5 수동 트리거, API 호출 최소화(무료 소스 우선). V2: E-15+S-5 반자동, 스케줄 기반 수집+LLM 보조 분석, 일일 API 비용 상한 $1. V3: 전체 자율, ML 기반 소스 발견+자동 분석+자동 RAG 삽입, I-9 Cost Gate 연동 실시간 비용 추적. |
| G3 | Gate 실패 피드백 | **양방향 루프 확정** | S-5 -> E-15 재수집 요청 루프 | Gate 거부 시 S-5가 거부 사유를 분석하여 `gate.feedback.recollect` 이벤트로 E-15에 재수집 요청. 재수집 요청에는 `reject_reason`, `suggested_sources[]`, `priority` 포함. 최대 재수집 시도: 3회. 3회 초과 시 수동 검토 큐로 이관. |
| G4 | 수집 스케줄링 | **정책 확정** | 소스별 수집 주기 정책 확정 | CRITICAL 소스(학술DB, 공식 문서): 6시간 주기. HIGH 소스(기술 블로그, GitHub): 12시간 주기. NORMAL 소스(뉴스, SNS): 24시간 주기. LOW 소스(아카이브): 7일 주기. 이벤트 트리거: RSS 업데이트/사용자 요청 시 즉시 수집. 캐시 정책: 수집 데이터 TTL = 소스 우선순위별 차등(CRITICAL 30일, LOW 90일). 오프라인 모드: 로컬 캐시된 데이터로 서비스, 온라인 복귀 시 delta sync. |
| G5 | E-Series 중복 | **정의 완료** | E-15 오케스트레이터 + E-1~E-14 서브 수집기 | E-15는 오케스트레이터 역할: 수집 요청 수신 -> 적합한 서브 수집기(E-1 YouTube, E-2 Instagram 등) 선택 -> 위임 실행 -> 결과 통합. 버전 관리: 각 서브 수집기는 독립 버전 관리, E-15는 호환성 매트릭스 유지. 새 소스 추가 시 E-15 Adapter 인터페이스 구현만으로 확장 가능(플러그인 아키텍처). |
| G6 | RAG 업데이트 트리거 | 개념만 | G4 통과 후 자동 임베딩 -> I-2 삽입 |
| G7 | 보완 기술 도입 시점 | 순서만 | V1: 없음, V2: RAGAS+LLM Judge, V3: DSPy+Reflexion+GraphRAG |

**추가 기능 8건**:

| # | 기능 | 설명 | 적용 버전 |
|---|------|------|-----------|
| N1 | 사용자 질문 기반 능동 수집 | I-2 RAG에 답 없으면 E-15 자동 수집 | V2+ |
| N2 | 수집 데이터 신선도 관리 (TTL) | 유효기간 부여, 만료 시 재수집/폐기 | V2+ |
| N3 | 다국어 수집/분석 | 영어/일본어/중국어 소스 확장 | V2+ |
| N4 | 수집 성과 대시보드 (ROI) | I-2 실제 활용률 추적 | V2+ |
| N5 | 소스 평판 자동 업데이트 | Gate 통과율 기반 점수 자동 조정 | V2+ |
| N6 | Memory 시너지 | I-3 Global Memory 패턴 -> E-15 키워드 보강 | V3 |
| N7 | 분쟁 감사 로그 | 충돌 해결 전체 이력 보존 | V1+ |
| N8 | 점진적 RAG 임베딩 | 증분 임베딩으로 비용/시간 절감 | V2+ |

---

## 문서 정보

| 항목 | 값 |
|------|-----|
| 문서 ID | VAMOS_CLOUD_LIBRARY_UNIFIED_SPEC |
| 버전 | 1.0 |
| 작성일 | 2026-02-23 |
| 소스 문서 수 | 4개 (총 755KB) |
| 상태 | 정본 |

---

# END OF DOCUMENT
