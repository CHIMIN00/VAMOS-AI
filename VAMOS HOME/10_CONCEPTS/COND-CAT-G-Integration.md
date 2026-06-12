---
tags: [type/concept, module/COND, status/COND, tier/T2, version/V2]
aliases: [CAT-G, Integration COND, IntegrationMixin]
created: 2026-06-12
---

# COND CAT-G: Integration (4개)

## 정의
COND 106개 중 외부 서비스 통합 카테고리 4개 — **7개 CAT 중 최소**. `IntegrationMixin`으로 Blue Node에 외부 API/서비스 연동 능력을 제공한다. 모듈 ID 범위 **#90, #110-#112**. 주요 의존성: httpx, OAuth2.

## 등장 도메인
- [[T2-COND-Modules]] — 정본 소유 (2-2 COND 카테고리 체계)
- [[T2-Blue-Node]] — 외부 연동이 필요한 Node가 소비
- [[T4-MCP]] — 외부 도구 연결은 MCP Bridge(Streamable HTTP) 경유와 역할 분담
- [[T1-Auxiliary-Modules]] — E-10 External API Gateway(V3)·E-13/E-14 동기화 모듈 연계

## 값·수치 (LOCK 여부)
- COND 합산 (CLAUDE.md §6 정본): CAT-G **4** (13+13+53+8+7+8+4=106)
- 실행 모델: COND는 CORE 소비만 가능 — CORE→COND 역방향 import 금지 (R7, vamos_lint VL-003)
- DEC-003 (LOCK): 도구 승인 Allowlist — 읽기전용=자동, 외부API/쓰기/코드실행=확인 필요 (외부 통합 모듈 전체 적용)

## 버전별 차이
- 조건부 실행, 버전 게이트 Mixed — 외부 API 계열(E-10/E-13/E-14)은 V2 COND~V3 ON 흐름과 동조

## 원본 경로
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_DETAIL_구조화_종합계획서.md` (L67~76)
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_종합명세.md` / CAT-G 하위
