# 데이터 정제 자동화 — L3 상세 명세

> **N-ID**: N-020 (NEW)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 01_dag-engine
> **정본**: sot 2/3-4_Workflow-RPA/01_dag-engine/data_cleaning.md

---

## 1. 개요

AI 기반 데이터 정제(클리닝) 자동화를 DAG 워크플로우 노드로 정의한다. 결측치 처리, 이상치 감지, 포맷 통일, 중복 제거, 데이터 검증을 포함하며, pandas 기반 V1 구현을 목표로 한다.

> LOCK (기존 명세 §2 / STEP7-N N-001 / LOCK-WF-01): DAG 노드 타입 12종 — 데이터 정제는 TransformNode, CodeNode, ConditionNode, LLMNode를 조합

---

## 2. 정제 파이프라인 구조

### 2.1 5단계 정제 흐름

```
[원본 데이터 입력]
  → [1. 프로파일링: 데이터 품질 진단]
  → [2. 결측치 처리: 추정/제거]
  → [3. 이상치 감지: 통계적+AI]
  → [4. 포맷 통일: 날짜/통화/전화번호]
  → [5. 중복 제거: 퍼지 매칭]
  → [데이터 검증: 규칙+AI 최종 확인]
  → [정제 완료 데이터 출력]
```

### 2.2 DAG 노드 매핑

| 정제 단계 | 사용 노드 타입 | 역할 |
|-----------|---------------|------|
| 프로파일링 | CodeNode | pandas profiling — 컬럼별 통계, null 비율, 타입 |
| 결측치 처리 | CodeNode + LLMNode | 통계적 보간 + LLM 기반 추정 |
| 이상치 감지 | CodeNode + LLMNode | IQR/Z-score + LLM 패턴 분석 |
| 포맷 통일 | TransformNode | Jinja2 기반 포맷 변환 규칙 |
| 중복 제거 | CodeNode | pandas + fuzzy matching |
| 데이터 검증 | ConditionNode + CodeNode | 규칙 기반 검증 + 스키마 확인 |

---

## 3. 데이터 프로파일링

### 3.1 프로파일링 출력 스키마

```typescript
interface DataProfile {
  row_count: number;                 // 총 행 수
  column_count: number;              // 총 컬럼 수
  columns: ColumnProfile[];
  quality_score: number;             // 0~100 종합 품질 점수
  issues: DataIssue[];               // 발견된 문제 목록
}

interface ColumnProfile {
  name: string;
  dtype: string;                     // 추론된 데이터 타입
  null_count: number;
  null_ratio: number;                // 0.0~1.0
  unique_count: number;
  unique_ratio: number;
  min?: any;
  max?: any;
  mean?: number;
  std?: number;
  sample_values: any[];              // 상위 5개 샘플
}

interface DataIssue {
  type: "missing" | "outlier" | "format" | "duplicate" | "type_mismatch";
  column: string;
  severity: "low" | "medium" | "high";
  count: number;
  description: string;
}
```

### 3.2 프로파일링 로직

```python
import pandas as pd
import numpy as np

class DataProfiler:
    """데이터 품질 프로파일링 — CodeNode에서 실행."""

    def profile(self, df: pd.DataFrame) -> DataProfile:
        columns = []
        issues = []

        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_ratio = null_count / len(df)

            col_profile = ColumnProfile(
                name=col,
                dtype=str(df[col].dtype),
                null_count=int(null_count),
                null_ratio=float(null_ratio),
                unique_count=int(df[col].nunique()),
                unique_ratio=float(df[col].nunique() / len(df)),
                sample_values=df[col].dropna().head(5).tolist(),
            )

            if pd.api.types.is_numeric_dtype(df[col]):
                col_profile.min = float(df[col].min())
                col_profile.max = float(df[col].max())
                col_profile.mean = float(df[col].mean())
                col_profile.std = float(df[col].std())

            columns.append(col_profile)

            # 이슈 감지
            if null_ratio > 0.1:
                issues.append(DataIssue(
                    type="missing", column=col, severity="high" if null_ratio > 0.5 else "medium",
                    count=null_count, description=f"{col}: {null_ratio:.1%} 결측"
                ))

        quality_score = self._calculate_quality_score(df, issues)
        return DataProfile(
            row_count=len(df), column_count=len(df.columns),
            columns=columns, quality_score=quality_score, issues=issues
        )
```

---

## 4. 결측치 처리

### 4.1 처리 전략

| 전략 | 적용 조건 | 구현 |
|------|----------|------|
| **삭제** | 결측 비율 > 70% (컬럼) 또는 행 단위 삭제 | `df.dropna()` |
| **통계적 보간** | 수치형 — 평균/중앙값/최빈값 | `df.fillna(df.median())` |
| **전후값 보간** | 시계열 데이터 — 선형/다항식 보간 | `df.interpolate(method='linear')` |
| **AI 추정** | 비정형/복합 데이터 — LLM 기반 추정 | LLMNode 호출 |

### 4.2 결측치 처리 설정

```typescript
interface MissingValueConfig {
  strategy: "drop" | "fill_mean" | "fill_median" | "fill_mode" | "interpolate" | "ai_estimate";
  column_rules?: Record<string, string>;  // 컬럼별 전략 오버라이드
  drop_threshold: number;            // 결측 비율 임계값 (기본 0.7 → 70% 이상이면 컬럼 삭제)
  ai_model?: string;                 // AI 추정 시 사용 모델
}
```

### 4.3 AI 기반 결측치 추정

```python
class AIImputer:
    """LLM 기반 결측치 추정 — 컨텍스트를 활용한 지능적 보간."""

    async def impute(self, df: pd.DataFrame, column: str, context_columns: list[str]) -> pd.Series:
        missing_indices = df[df[column].isnull()].index
        results = pd.Series(index=missing_indices, dtype=object)

        for idx in missing_indices:
            row_context = df.loc[idx, context_columns].to_dict()
            prompt = f"""
            다음 데이터의 '{column}' 값을 추정하세요.
            컨텍스트: {row_context}
            기존 값 분포: {df[column].dropna().describe().to_dict()}
            가장 적절한 값 하나만 반환하세요.
            """
            response = await llm_call(prompt, model="claude-3-haiku", temperature=0.1)
            results[idx] = self._parse_value(response, df[column].dtype)

        return results
```

---

## 5. 이상치 감지

### 5.1 감지 방법

| 방법 | 설명 | 적용 |
|------|------|------|
| **IQR** | Q1 - 1.5×IQR ~ Q3 + 1.5×IQR 범위 벗어남 | 수치형 기본 |
| **Z-Score** | |z| > 3 (평균에서 3σ 초과) | 정규분포 가정 |
| **Isolation Forest** | 비지도 학습 기반 이상치 탐지 | 다변량 데이터 |
| **AI 분석** | LLM 기반 패턴/문맥 이상 감지 | 비정형 데이터 |

### 5.2 이상치 감지 설정

```typescript
interface OutlierDetectionConfig {
  method: "iqr" | "zscore" | "isolation_forest" | "ai";
  threshold?: number;                // IQR 배수(기본 1.5), Z-score 임계(기본 3)
  action: "flag" | "remove" | "cap" | "replace_median";
  columns?: string[];                // 대상 컬럼 (null=전체 수치형)
}
```

### 5.3 이상치 처리 로직

```python
class OutlierDetector:
    def detect_iqr(self, series: pd.Series, multiplier: float = 1.5) -> pd.Series:
        """IQR 기반 이상치 마스크 반환."""
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        return (series < lower) | (series > upper)

    def detect_zscore(self, series: pd.Series, threshold: float = 3.0) -> pd.Series:
        """Z-score 기반 이상치 마스크 반환."""
        z = np.abs((series - series.mean()) / series.std())
        return z > threshold

    def handle_outliers(
        self, df: pd.DataFrame, column: str, mask: pd.Series, action: str
    ) -> pd.DataFrame:
        if action == "remove":
            return df[~mask]
        elif action == "cap":
            q1, q3 = df[column].quantile(0.25), df[column].quantile(0.75)
            iqr = q3 - q1
            df.loc[mask, column] = df[column].clip(q1 - 1.5*iqr, q3 + 1.5*iqr)
        elif action == "replace_median":
            df.loc[mask, column] = df[column].median()
        elif action == "flag":
            df[f"{column}_outlier"] = mask
        return df
```

---

## 6. 포맷 통일

### 6.1 포맷 규칙

| 데이터 유형 | 입력 예시 | 통일 형식 | 변환 규칙 |
|------------|----------|----------|----------|
| 날짜 | "2026-04-09", "20260409", "04/09/2026" | ISO 8601 (`YYYY-MM-DD`) | dateutil.parser |
| 통화 | "₩1,000,000", "1000000원", "1,000,000" | 정수 (원 단위) | regex + int 변환 |
| 전화번호 | "010-1234-5678", "01012345678" | `XXX-XXXX-XXXX` | regex 패턴 |
| 이메일 | "User@Example.COM" | 소문자 정규화 | `.lower().strip()` |
| 주소 | 다양한 형식 | 시/구/동 구조화 | 주소 파서 |

### 6.2 포맷 변환 설정

```typescript
interface FormatNormalizationConfig {
  rules: FormatRule[];
}

interface FormatRule {
  column: string;
  target_format: "iso_date" | "integer_krw" | "phone_kr" | "email_lower" | "custom";
  custom_pattern?: string;           // 정규식 패턴 (custom일 때)
  custom_replacement?: string;
}
```

---

## 7. 중복 제거

### 7.1 중복 감지 전략

| 전략 | 설명 | 적용 |
|------|------|------|
| **완전 일치** | 모든 필드가 동일 | `df.drop_duplicates()` |
| **키 기반** | 지정 컬럼이 동일 | `df.drop_duplicates(subset=[...])` |
| **퍼지 매칭** | 유사도 기반 (Levenshtein, Jaro-Winkler) | 이름/주소 등 비정형 |

### 7.2 퍼지 매칭 설정

```typescript
interface DeduplicationConfig {
  strategy: "exact" | "key_based" | "fuzzy";
  key_columns?: string[];            // key_based/fuzzy 대상 컬럼
  similarity_threshold?: number;     // 퍼지 매칭 임계값 (0.0~1.0, 기본 0.85)
  similarity_metric?: "levenshtein" | "jaro_winkler" | "cosine";
  keep: "first" | "last" | "best_quality";  // 중복 시 보존 기준
}
```

### 7.3 퍼지 중복 제거 로직

```python
from rapidfuzz import fuzz, process

class FuzzyDeduplicator:
    def deduplicate(
        self, df: pd.DataFrame, column: str, threshold: float = 0.85
    ) -> pd.DataFrame:
        """퍼지 매칭 기반 중복 제거."""
        seen = {}
        drop_indices = []

        for idx, value in df[column].items():
            if pd.isna(value):
                continue
            match = process.extractOne(
                str(value), seen.keys(),
                scorer=fuzz.ratio, score_cutoff=threshold * 100
            )
            if match:
                drop_indices.append(idx)
            else:
                seen[str(value)] = idx

        return df.drop(index=drop_indices).reset_index(drop=True)
```

---

## 8. 데이터 검증

### 8.1 검증 규칙

```typescript
interface ValidationRule {
  column: string;
  rule_type: "not_null" | "unique" | "range" | "pattern" | "enum" | "custom";
  params: Record<string, any>;       // rule_type별 파라미터
  severity: "error" | "warning";     // error=차단, warning=경고만
}
```

### 8.2 검증 실행

```python
class DataValidator:
    def validate(self, df: pd.DataFrame, rules: list[ValidationRule]) -> ValidationReport:
        violations = []
        for rule in rules:
            result = self._check_rule(df, rule)
            if result.violation_count > 0:
                violations.append(result)

        return ValidationReport(
            total_rules=len(rules),
            passed=len(rules) - len(violations),
            failed=len(violations),
            violations=violations,
            is_valid=all(v.severity != "error" for v in violations),
        )

    def _check_rule(self, df: pd.DataFrame, rule: ValidationRule) -> RuleResult:
        match rule.rule_type:
            case "not_null":
                mask = df[rule.column].isnull()
            case "unique":
                mask = df[rule.column].duplicated(keep=False)
            case "range":
                mask = ~df[rule.column].between(rule.params["min"], rule.params["max"])
            case "pattern":
                mask = ~df[rule.column].astype(str).str.match(rule.params["regex"])
            case "enum":
                mask = ~df[rule.column].isin(rule.params["values"])
            case "custom":
                # 사용자 정의 술어: params['predicate'](df[col]) -> 위반 마스크(bool Series)
                predicate = rule.params.get("predicate")
                if predicate is None:
                    raise ValueError(f"custom rule '{rule.column}' requires params['predicate']")
                mask = ~df[rule.column].map(predicate).astype(bool)
            case _:
                raise ValueError(f"지원하지 않는 rule_type: {rule.rule_type}")
        return RuleResult(rule=rule, violation_count=int(mask.sum()), violation_indices=mask[mask].index.tolist())
```

---

## 9. 정제 파이프라인 오케스트레이션

### 9.1 통합 정제 워크플로우

```python
class DataCleaningPipeline:
    """데이터 정제 파이프라인 — DAG 워크플로우로 오케스트레이션."""

    async def run(self, data: pd.DataFrame, config: CleaningConfig) -> CleaningResult:
        # 1. 프로파일링
        profile = DataProfiler().profile(data)

        # 2. 결측치 처리
        data = await MissingValueHandler(config.missing).handle(data)

        # 3. 이상치 감지/처리
        data = OutlierDetector(config.outlier).detect_and_handle(data)

        # 4. 포맷 통일
        data = FormatNormalizer(config.format).normalize(data)

        # 5. 중복 제거
        data = FuzzyDeduplicator(config.dedup).deduplicate(data)

        # 6. 최종 검증
        validation = DataValidator().validate(data, config.validation_rules)

        # 7. 정제 전후 비교
        after_profile = DataProfiler().profile(data)

        return CleaningResult(
            original_rows=profile.row_count,
            cleaned_rows=after_profile.row_count,
            removed_rows=profile.row_count - after_profile.row_count,
            quality_before=profile.quality_score,
            quality_after=after_profile.quality_score,
            validation=validation,
            data=data,
        )
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| L3 v1.0 | 2026-04-09 | Phase 1 1-1 — 5단계 정제 파이프라인, 프로파일링, 결측치/이상치/포맷/중복 처리, 검증 |
