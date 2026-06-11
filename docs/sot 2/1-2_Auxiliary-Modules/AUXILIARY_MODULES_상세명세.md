# 1-2. Auxiliary I-Series Modules 상세명세 (REDIRECT — ARCHIVED)

> **버전**: v1.0
> **Status**: ARCHIVED (REDIRECT)
> **Archived-At**: 2026-04-07
> **작성일**: 2026-04-07
> **Last-reviewed**: 2026-04-07
> **모듈**: 1-2 Auxiliary Modules (I-4 / I-13 / I-14 / I-16 / S-1)
> **소관 태스크**: §7 1-9 (상세명세.md 아카이브)
> **L3 판정**: PENDING

> ⚠️ **이 파일은 아카이브되었습니다. 편집 금지.**
>
> Phase 1 (1-2 ~ 1-7 태스크) 에서 본 문서의 내용은 모듈별 서브폴더로 분배 완료되었으며, 1-9 태스크에서 동결되었습니다. 이중 편집 (원본 vs 분배본 동시 수정) 을 방지하기 위해 본문은 `_archive/` 로 byte-identical 이동되었고, 본 위치에는 진입점 안내만 남깁니다.

---

## 1. 분배 결과 위치 (모듈 ID 기준)

| 모듈 ID | 모듈 이름 | 분배 위치 | 분배 태스크 |
|---------|----------|-----------|------------|
| I-4  | Multimodal Interpreter (멀티모달 해석기) | [01_multimodal-interpreter/](01_multimodal-interpreter/) | 1-2 |
| I-13 | Multimodal Renderer (멀티모달 렌더러) | [02_multimodal-renderer/](02_multimodal-renderer/) | 1-3 |
| I-14 | Summarizer (요약기) | [03_summarizer/](03_summarizer/) | 1-4 |
| I-16 | Knowledge Search Engine (지식 검색 엔진) | [04_knowledge-search/](04_knowledge-search/) | 1-5 |
| S-1  | Self-check Engine (자가점검 엔진) | [05_self-check/](05_self-check/) | 1-6 |
| (공통) | 공유 타입·정책 | [00_common/](00_common/) | 1-3 ~ 1-7 (병행) |
| (매핑) | LOCK · 의존성 · 인터페이스 계약 | [06_mapping/](06_mapping/) | 1-7 |

> ⚠️ 모듈 ID 는 `I-5/I-6/I-7/I-8` 이 아니라 **`I-4 / I-13 / I-14 / I-16 / S-1`** 입니다 (D2.0-02 §7 정본).

---

## 2. 원본 (이력 보존용)

- **원본 아카이브 (byte-identical)**: [_archive/AUXILIARY_MODULES_상세명세_v1.0_archived.md](_archive/AUXILIARY_MODULES_상세명세_v1.0_archived.md) — 336 lines
- **아카이브 README**: [_archive/README.md](_archive/README.md)
- **마스터 인덱스**: [INDEX.md](INDEX.md)
- **종합계획서**: [AUXILIARY_MODULES_구조화_종합계획서.md](AUXILIARY_MODULES_구조화_종합계획서.md) §7 (1-2 ~ 1-9 태스크)

---

## 3. 라인 번호 참조 안내 (분배 산출물의 `> **출처**:` 필드)

분배 산출물 (47 파일) 의 `> **출처**: AUXILIARY_MODULES_상세명세.md L<n>-L<m>` 형식 인용은 본 redirect 파일이 아니라 **byte-identical 아카이브** 의 라인을 가리킵니다.

| 모듈 | 아카이브 내 시작 라인 |
|------|---------------------|
| I-4  Multimodal Interpreter | L16 |
| I-13 Multimodal Renderer | L86 |
| I-14 Summarizer | L143 |
| I-16 Knowledge Search Engine | L205 |
| S-1  Self-check Engine | L277 |

라인 번호 무결성 보장을 위해 아카이브 본문에는 어떤 라인도 추가/삭제되지 않습니다 ([_archive/README.md](_archive/README.md) §2 보존 원칙 참조).

---

## 4. 편집 정책

- 본 파일 (`AUXILIARY_MODULES_상세명세.md`) 은 **수정 금지** 입니다 (1-9 동결).
- 모듈별 변경은 위 §1 의 분배 위치 파일에서만 수행하세요.
- 분배 이전 원본을 확인해야 할 경우 `_archive/AUXILIARY_MODULES_상세명세_v1.0_archived.md` 를 읽기 전용으로 참조하세요.
- 본 redirect 파일을 삭제하지 마세요 — 외부 인용 (47 파일의 bare-name 출처 필드) 의 backstop 역할을 합니다.

---

## 5. 변경 이력

| 버전 | 일자 | 변경 내용 |
|------|------|-----------|
| v1.0 | 2026-04-07 | 1-9 태스크 — 원본을 `_archive/` 로 byte-identical 이동, 본 위치를 redirect 로 교체, INDEX.md §1 루트 정본 표 갱신 |
