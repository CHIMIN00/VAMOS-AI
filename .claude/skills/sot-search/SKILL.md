---
name: sot-search
description: SOT 89,000줄을 벡터 임베딩으로 인덱싱하여 의미 검색
triggers:
  - /sot-search
args:
  - name: command
    description: "index | 검색어"
---

# `/sot-search` — SOT 벡터 검색

## 목적
SOT 68개 파일을 **벡터 임베딩으로 인덱싱**하여 키워드/개념으로 정확한 구절 검색.

## 전제 조건
- Milvus 서버 실행 중 (localhost:19530)
- `pip install pymilvus sentence-transformers`

## 실행 절차

### `/sot-search index`
1. SOT 68개 파일을 청크 단위로 분할 (500자, 100자 오버랩)
2. sentence-transformers로 벡터 임베딩 생성
3. Milvus에 인덱싱

```bash
python D:\VAMOS\.claude\hooks\sot_indexer.py \
  --sot-dir "D:\VAMOS\03. 분석단계" \
  --collection vamos_sot
```

### `/sot-search "검색어"`
```bash
python D:\VAMOS\.claude\hooks\sot_search.py \
  --query "검색어" \
  --collection vamos_sot \
  --top-k 5
```

### 보고서 출력
```
## SOT 검색 결과: "LOCK 관련 조항"

| # | 파일 | 위치 | 관련 구절 | 유사도 |
|---|------|------|----------|--------|
| 1 | D2.0-07_Safety.md | line 234 | "LOCK 상태에서는..." | 0.92 |
| 2 | D2.0-03_Module.md | line 89 | "모듈 잠금 조건..." | 0.87 |
```

## 판정 기준
- 검색 스킬이므로 PASS/FAIL 판정 없음 (정보 제공 목적)
- top-k 결과 중 유사도 ≥ 0.8인 항목이 있으면 **관련 구절 발견**, 없으면 **관련 구절 없음**

## 저장 위치
- 인덱스: Milvus `vamos_sot` 컬렉션 (localhost:19530)
- 검색 결과: 콘솔 출력 (Markdown 테이블). 필요시 `--output` 옵션으로 JSON 저장 가능

---

## [SOT 2 확장] SOT 2 벡터 검색 (v2 추가)

> 기존 SOT 68파일 인덱싱을 유지한 채, SOT 2 파일을 별도 컬렉션으로 인덱싱합니다.

### 추가 인덱스 대상

| 대상 | 파일 수 | 총 라인 | 컬렉션명 |
|------|--------|---------|---------|
| SOT 2 상세명세 | ~18 | ~10,000 | `vamos_sot2_specs` |
| SOT 2 방식 C 요약 | ~7 | ~2,000 | `vamos_sot2_method_c` |
| SOT 2 계획서 | ~18 | ~15,000 | `vamos_sot2_plans` |

### 추가 명령어

- `/sot-search sot2-index` → SOT 2 전체 인덱싱 (3개 컬렉션)
- `/sot-search sot2 "검색어"` → SOT 2에서만 검색
- `/sot-search all "검색어"` → SOT 원본 + SOT 2 + Part2 통합 검색
- `/sot-search sot2-status` → SOT 2 인덱스 상태 (문서 수, 청크 수, 최종 인덱싱일)

### 인덱싱 파라미터 (SOT 2 전용)

```
청크 크기: 500자 (기존 SOT와 동일)
오버랩: 100자
임베딩 모델: sentence-transformers (기존과 동일)
한국어 최적화: KR-SBERT 설치 시 자동 사용 (E-45)
```

### 통합 검색 결과 포맷

```
| 순위 | 유사도 | 소스 | 파일 | 라인 | 내용 (축약) |
|------|--------|------|------|------|-----------|
| 1 | 0.93 | SOT 2 | 3-2_Multimodal/상세명세.md | L45 | MultimodalRequest... |
| 2 | 0.89 | SOT | D2.0-01_Overview.md | L1234 | 멀티모달 해석기... |
| 3 | 0.85 | Part2 | PART2.md | L2147 | D-2 Multimodal Engine... |
```
