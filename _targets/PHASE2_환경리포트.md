# Phase 2-0 환경 리포트 — 외부 의존성 재확인 (PART1 E.1+E.3+B.1)

> **실측일**: 2026-06-11 · **기준선**: PART1 검증 결과 2026-03-02 · **확인 대상**: 합 28건 (E.1 9 + E.3 8 + B.1 11)
> **판정**: **전건 PASS** — BLOCKER 0건 · 변경 2건(비차단) · WARN 1건(비차단)

## 1. E.1 즉시 액션 (9건) — 9/9 PASS

| # | 항목 | 요구 | 2026-03-02 | 2026-06-11 실측 | 판정 |
|---|------|------|-----------|----------------|:----:|
| 1 | OpenAI API Key | 발급+유효 | sk-proj-...(164자) | env 설정(164자) + API 호출 HTTP 200 | PASS |
| 2 | Python | 3.11+ | 3.11.8 | **3.11.8** (`python --version`) | PASS |
| 3 | Node.js | 18+ LTS | v23.1.0 | **v23.1.0** (`node --version`) | PASS |
| 4 | Rust | 1.70+ | 1.93.1 | **1.93.1** (`rustc --version`) | PASS |
| 5 | Ollama 모델 2종 | llama3.2:3b + llama3.1:8b | 둘 다 | **둘 다 존재** (`ollama list`: 3b 2.0GB / 8b 4.9GB) | PASS |
| 6 | Git | 설치 | 2.52.0 | **2.52.0.windows.1** | PASS |
| 7 | 결정: 패키지 매니저 | — | pnpm 확정 | pnpm 확정 유지 (변경 없음) | PASS |
| 8 | 결정: Python 의존성 | — | Poetry 확정 | Poetry 확정 유지 (변경 없음) | PASS |
| 9 | 결정: PyTorch | — | CUDA 확정 | CUDA 확정 유지 — RTX 3070 Ti 존재, 드라이버 591.86 | PASS |

## 2. E.3 환경 검증 (8건) — 8/8 PASS

| # | 항목 | 요구 | 2026-03-02 | 2026-06-11 실측 | 판정 |
|---|------|------|-----------|----------------|:----:|
| 1 | pydantic | v2.x | 2.11.5 | **2.12.5** ⚠️ 변경(마이너 업, v2 유지) | PASS |
| 2 | cargo | 1.70+ | 1.93.1 | **1.93.1** | PASS |
| 3 | ollama list | 모델 2종 | 둘 다 | **둘 다 존재** | PASS |
| 4 | API Key 테스트 | HTTP 200 | 성공 | **HTTP 200** (`/v1/models` 응답 확인) | PASS |
| 5 | 디스크 여유 | 20GB+ | 490GB | **~783GB free** (D: 실측) ⚠️ 변경(증가, 무해) | PASS |
| 6 | node | 18+ | v23.1.0 | **v23.1.0** | PASS |
| 7 | python | 3.11+ | 3.11.8 | **3.11.8** | PASS |
| 8 | BGE-M3 | FlagEmbedding | v1.3.5 | **import 성공** (가중치는 V0 첫 실행 시 자동 다운로드 — 기존 방침 유지) | PASS |

## 3. B.1 V0 시작 전 (11건 = 1+7+3) — 11/11 PASS

- **B.1.1 API Key (1건)**: OpenAI Key 유효 (위 E.3 #4 동일 실측) — PASS
- **B.1.2 소프트웨어 (7건)**: Python 3.11.8 / Node v23.1.0 / Rust 1.93.1 / Ollama(설치+모델 2종) / Git 2.52.0 — 전건 PASS (위 E.1 #2~#6 동일 실측)
- **B.1.4 결정 (3건)**: pnpm / Poetry / CUDA — 3건 확정 유지, 번복 없음 — PASS

## 4. 변경·WARN 기록 (전건 비차단)

| 구분 | 항목 | 내용 | 처분 |
|------|------|------|------|
| 변경 | pydantic | 2.11.5 → 2.12.5 (v2 유지, 요구 충족) | 기록만 |
| 변경 | 디스크 | free 490GB → 783GB (증가) | 기록만 |
| WARN | pnpm·poetry 바이너리 | **현재 PATH 미설치** (corepack 0.29.4 존재 → pnpm 활성화 가능 / poetry 부재). E.1 #7~#8은 '결정' 항목이라 판정 불변. 단 2-4(린터/CI)에서 poetry 필요 → **2-4에서 설치/대체 해석 수행** | Phase 2-4 처리 |

## 5. 2-0C — OpenAI 구키 revoke 확인 (병행 사용자 액션, 비차단)

- **상태**: 사용자 revoke 완료 통보 **미수신** (2026-06-11 본 세션 기준).
- 현행 env의 OPENAI_API_KEY(164자)는 유효(HTTP 200). coin 워크스페이스 `.env` 노출 키의 revoke는 **사용자 전용 액션** — 완료 통보 수신 시 coin `.env` 삭제+통이동 가능함을 기록(직접 실행 금지, 세션3 결정 준수).

## 6. 판정

**E.1(9) + E.3(8) + B.1(11) = 28/28 PASS — 2-V 게이트 "외부 의존성 E.1+E.3 PASS" 충족.**
BLOCKER 없음. 골든셋 실데이터 재구축(2-0B)은 별도 산출(benchmarks/golden_set/ + manifest v2) — 본 리포트 §7에 결과 추기.

## 7. 2-0B 골든셋 재구축 결과 (D14 — 완료 2026-06-11)

- **판정**: ✅ 실데이터 전환 완료 — `verify_golden_set.py` **ALL PASS (errors 0 / 경고 0)** + 재현성(R-18-1) PASS(재실행 전 파일 SHA 동일·manifest 멱등)
- **구성 (v1 합성 170 → v2 실데이터 162)**:
  | 벤치마크 | v2 | 원본 | 추출 | 라이선스 |
  |---|---|---|---|---|
  | MMLU | 50 | cais/mmlu test 14,042 (57과목) | 50과목 층화·과목당 1 (seed=42) | MIT |
  | HumanEval | 20 | openai/human-eval 164 | 난이도 7/7/6 (solution 라인 3분위 PROXY) | MIT |
  | MBPP | 50 | sanitized-mbpp 427 (test_list==3 한정 397) | 난이도 17/17/16 (code 라인 3분위 PROXY) | CC BY 4.0 |
  | LogicKor | **42** | instructkr/LogicKor 전수 | 전수 (6카테고리×7) | CC BY-SA 4.0 (maywell HF, DOI 10.57967/hf/2440) |
- **⚠️ 편차 기록 (단일 종결)**: 명세 "LogicKor 50(전수)"는 합성 v1 가정치 — **실제 전수 실측 = 42** (6카테고리 × 7문항, 각 2턴). "전수" 원칙 우선 채택, 합성 보충 금지 원칙(임의 합성 재생성 금지) 준수. manifest·verify 스크립트에 편차 명기. 총 문항 170→**162**.
- **산출물**: items/metadata 8파일 + manifest v2(data_status=REAL_DATA·VALID_FOR_GATES, change_log v2, raw_source_sha256 4종) + contamination_check v2(hash dup 0 · 5-gram>50% 0 · max 0.3077) + smoke 서브셋 v2 재생성(mmlu 10 + humaneval 10) + `scripts/rebuild_golden_set_v2.py`(결정론, seed=42)
- **LOCK-BE-01/02 게이트 유효화**: 임계값 LOCK(MMLU ≥85% / HumanEval pass@1 ≥85%)은 문항 수 무관 — 측정 기반이 실데이터로 전환되어 게이트 판정 유효(INVALID_FOR_GATES 해제). LOCK 값 변경 0.
- **백업**: v1 전 파일 `_targets/_integ/backup_phase2/golden_set_v1/` (SHA256 기록 golden_set_v1_sha256.txt)
- **원본 보관**: C:\tmp\golden_raw\ (repo 밖 — parquet/jsonl 원본 + 라이선스 원문, manifest에 raw SHA256 기록)
