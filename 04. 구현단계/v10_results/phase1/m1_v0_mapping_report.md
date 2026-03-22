# M-1 매핑 검증 보고서: V0 기능 → PART2 §2

> **에이전트**: M-1 | **Phase**: 1 | **생성일**: 2026-03-09
> **범위**: Feature Registry v10_feature_registry_final.json 중 version_scope에 "V0" 포함 항목 → PART2 §2 (V0 STEP 1~6, lines 54~1383)

---

## 1. 통계 요약

| 판정 | 건수 | 비율 |
|------|------|------|
| **MATCHED** | 17 | 8.7% |
| **SPREAD** | 163 | 83.6% |
| **PARTIAL** | 7 | 3.6% |
| **MISSING** | 8 | 4.1% |
| **NOT_APPLICABLE** | 0 | 0% |
| **합계** | **195** | 100% |

> SPREAD가 높은 이유: V0 기능 대부분이 여러 STEP에 걸쳐 구현됨 (예: 스키마는 STEP-1 seed + STEP-2 정의 + STEP-6 테스트).
> MATCHED + SPREAD = 180건 (92.3%)으로 V0 기능의 대부분이 PART2 §2에 커버됨.

---

## 2. MISSING 항목 (8건)

### BLOCKER: 0건

### HIGH: 1건

| feature_id | feature_name | 사유 |
|-----------|-------------|------|
| **D204-179** | 비용 관리 인프라 (가중치 테이블, 60/80/95% 경고) | PART2 V0 STEP에 미배정. I-9 stub은 80%/100%만 처리하고, 60%/95% 경고 및 가중치 테이블 누락. version_scope에 V0 포함되나 V0 구현 항목으로 미반영. |

### MEDIUM: 2건

| feature_id | feature_name | 사유 |
|-----------|-------------|------|
| **P30-054** | 승인 판단 트리 구현 (4단계 위험등급 분기) | V0 I-19 stub은 P0/P1→auto, P2→hold만 구현. 4단계 위험등급 분기 전체 트리 미반영. |
| **D204-182** | 라우팅 인프라 상세 (4축 결정트리, 동적 풀, A/B 자동승격) | V0 §2 전체에서 라우팅 인프라 관련 내용 없음. V1+ 범위로 추정되나 version_scope에 V0 포함. |

### LOW: 5건

| feature_id | feature_name | 사유 |
|-----------|-------------|------|
| P30-032 | V0 기초 골격 6대 영역 구현 | STEP-1~6 전체가 6대 영역을 암묵적으로 커버. 별도 구현 항목 불필요. |
| P30-041 | 파일 단위 저장 스펙 구현 (7 공통 항목) | STEP-5 MemoryRecord로 부분 커버. 별도 배정 없음. |
| P30-068 | 14개 목표 A/B/C/D 그룹 매핑 구현 | 상위 설계 수준 항목. V0 구현 항목으로 배정 불필요. |
| DD1-002 | Glossary 단일 소유 규칙 검증 모듈 구현 | 문서 관리 도구 성격. V0 코드 구현 대상 아님. |
| CLIB-123 | YouTube 수집기 (yt-dlp 메타데이터 + 자막) | Cloud Library 하위 기능. V0 기본 골격 범위에 부적합. |

---

## 3. PARTIAL 항목 (7건) — Phase 미배정

| feature_id | feature_name | 발견 위치 | 비고 |
|-----------|-------------|----------|------|
| CLAUDE-150 | datetime.utcnow() → datetime.now(timezone.utc) 전수 교체 | §7 L3761 | V1 GO/NO-GO에만 언급. V1 주 매핑 대상. |
| P30-030 | 모듈 의존성 매트릭스 구현 (14+ 모듈 쌍) | §6.3 L3010 | VAL 검증 규칙에만 존재. V0 STEP 미배정. |
| P30-038 | P0/P1/P2 도메인 분류 SOT 테이블 구현 | §6.11 L3655 | FailureCodeRegistry에만 존재. V0 STEP 미배정. |
| P30-047 | 사용자 동의 로그 시스템 구현 | §6.9 L3349 | SDAR 수리 액션에만 존재. V0 STEP 미배정. |
| P30-063 | 운영 한계(Limits) 시스템 구현 | §5 V3 L2327 | V3 인프라에만 존재. V0 미배정. |
| P30-064 | 버전/변경 관리 시스템 구현 (Change Management) | §4 V2 L1799 | V2 산출물에만 존재. V0 미배정. |
| CLIB-042 | Cloud Library 파일 시스템 디렉토리 구조 구현 | 목차 L33 | 목차에만 언급. V0 미배정. |

---

## 4. 교차 버전 기능 (W-28 방어)

V0 기능 195건 중 다중 버전 기능의 version_scope 첫 번째가 V0인 경우 M-1이 주 매핑 에이전트.
검토 결과, 필터링된 V0 기능은 모두 version_scope에서 V0가 첫 번째이거나 V0 전용이므로 M-1이 주 매핑을 담당합니다.

---

## 5. 검증 방법론

1. Feature Registry에서 version_scope에 "V0" 포함된 195건 필터
2. 각 feature의 feature_name, module_id, tech_keywords, source_section에서 키워드 추출
3. PART2 §2 (lines 54~1383) 내 4단계 검색:
   - feature_name 키워드 → PART2 텍스트 매칭
   - 모듈 ID (I-1, E-7 등) 검색
   - 기술명 (React, Qdrant 등) 검색
   - CamelCase 용어 (IntentFrame, DecisionSchema 등) 검색
4. MISSING 판정 항목에 대해 확장 키워드로 §6, §7 포함 전체 재검색
5. 용어 매핑 테이블 (Phase 0-B) 참조하여 SRC↔PART2 용어 불일치 해소
6. PRE_MATCHED/PRE_GAP 항목도 모두 재확인 (V8/V9 미신뢰 원칙)

---

## 6. 권고사항

### HIGH 대응 필요
- **D204-179**: 비용 관리 가중치 테이블과 60%/95% 경고 임계값을 V0-STEP-4 I-9 Cost Manager 또는 V0-STEP-5에 추가 배정 검토 필요.

### MEDIUM 모니터링
- **P30-054**: 4단계 위험등급 분기는 V1 I-19 본격 구현 시 포함 가능. V0 stub 수준으로는 충분.
- **D204-182**: 라우팅 인프라는 version_scope 재검토 필요 (V0 제외 가능성).

### PARTIAL 처리
- §6에만 존재하는 3건(P30-030, P30-038, P30-047)은 M-5a/M-5b 에이전트에서 상세 검증 예정.
- CLAUDE-150(datetime 교체)은 M-2(V1) 에이전트가 주 매핑.

---

## 7. 산출물

- `m1_v0_mapping_result.json`: 195건 전체 매핑 결과 (JSON)
- `m1_auto_mapping_raw.json`: 자동 매핑 1차 원본 (참고용)
- `v0_features_filtered.json`: V0 기능 필터 목록 (참고용)
- `m1_v0_mapping_report.md`: 본 보고서
