#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M-5a Agent 리파인: §6.1~§6.7 정밀 매핑
핵심 접근법: §6의 구체적 구현 항목을 먼저 추출 → Feature Registry와 엄격 매핑
"""

import json
import re
import sys
import os
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PART2_PATH = r"D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md"
REGISTRY_PATH = r"D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json"
OUTPUT_DIR = r"D:\VAMOS\04. 구현단계\v10_results\phase1"

# ============================================================
# 1. §6.1~§6.7에서 구현 항목 추출
# ============================================================

# 수동 정의: §6.1~§6.7의 모든 구체적 구현 항목 (PART2 텍스트에서 직접 추출)
S6_ITEMS = [
    # §6.1.1 핵심 레이아웃
    {"id": "S6-UI-001", "name": "3-Column Fluid Layout", "section": "§6.1.1", "line": 2860, "version": "V1",
     "keywords": ["3-column", "fluid layout", "리사이즈"]},
    {"id": "S6-UI-002", "name": "Builder View (Cockpit)", "section": "§6.1.1", "line": 2861, "version": "V1",
     "keywords": ["builder view", "cockpit", "리소스 트리", "그래프 캔버스"]},
    {"id": "S6-UI-003", "name": "Hologram View", "section": "§6.1.1", "line": 2862, "version": "V1",
     "keywords": ["hologram", "타임라인", "스트리밍", "glass hud"]},
    {"id": "S6-UI-004", "name": "CLI Interface", "section": "§6.1.1", "line": 2863, "version": "V1",
     "keywords": ["cli interface", "vamos run", "vamos approve", "vamos status"]},

    # §6.1.2 React 컴포넌트 (~44개)
    {"id": "S6-UI-005", "name": "Decision 컴포넌트 (3개)", "section": "§6.1.2", "line": 2869, "version": "V1",
     "keywords": ["decisioncard", "decisionlockbadge", "decision 시각화"]},
    {"id": "S6-UI-006", "name": "Chat 컴포넌트 (6개)", "section": "§6.1.2", "line": 2870, "version": "V1",
     "keywords": ["chatpanel", "userbubble", "aibubble", "thinkingblock", "artifactembed", "streamingeffect"]},
    {"id": "S6-UI-007", "name": "Approval 컴포넌트 (3개)", "section": "§6.1.2", "line": 2871, "version": "V1",
     "keywords": ["approvaldialog", "approvalcard", "p2 확인 모달"]},
    {"id": "S6-UI-008", "name": "Cost 컴포넌트 (5개)", "section": "§6.1.2", "line": 2872, "version": "V1",
     "keywords": ["costdashboard", "budgetgauge", "downshiftcontrol", "tokencounter", "경고 toast"]},
    {"id": "S6-UI-009", "name": "Evidence 컴포넌트 (4개)", "section": "§6.1.2", "line": 2873, "version": "V1",
     "keywords": ["verificationbadge", "uncertaintyalert", "인용 점프", "qod 표시"]},
    {"id": "S6-UI-010", "name": "Memory 컴포넌트 (4개)", "section": "§6.1.2", "line": 2874, "version": "V1",
     "keywords": ["memorycandidatelist", "maskingpreview", "commitbutton", "pii 거부 카드"]},
    {"id": "S6-UI-011", "name": "Node/Flow 컴포넌트 (4개)", "section": "§6.1.2", "line": 2875, "version": "V1",
     "keywords": ["nodestatusbadge", "orange 헥사곤", "blue 서클", "flow edge 애니메이션"]},
    {"id": "S6-UI-012", "name": "Guardrails 컴포넌트 (3개)", "section": "§6.1.2", "line": 2876, "version": "V1",
     "keywords": ["guardrailsalert", "policyblockedcard", "pii 감지 모달"]},
    {"id": "S6-UI-013", "name": "Input 컴포넌트 (4개)", "section": "§6.1.2", "line": 2877, "version": "V1",
     "keywords": ["멀티라인 텍스트", "드래그앤드롭", "클립보드", "음성 입력"]},
    {"id": "S6-UI-014", "name": "Navigation 컴포넌트 (3개)", "section": "§6.1.2", "line": 2878, "version": "V1",
     "keywords": ["대화 사이드바", "프로젝트 폴더", "세션 목록"]},
    {"id": "S6-UI-015", "name": "기타 컴포넌트 (5개)", "section": "§6.1.2", "line": 2879, "version": "V1",
     "keywords": ["modelselector", "table", "diagram", "log viewer", "keyboard shortcuts"]},

    # §6.1.3 Custom Hooks + Stores
    {"id": "S6-UI-016", "name": "Custom Hooks (8개)", "section": "§6.1.3", "line": 2884, "version": "V1",
     "keywords": ["usetauriipc", "usedecision", "useworkflow", "usememory", "usecost", "usenotification", "useautonomy", "uselog"]},
    {"id": "S6-UI-017", "name": "Stores (7개)", "section": "§6.1.3", "line": 2886, "version": "V1",
     "keywords": ["appstore", "decisionstore", "coststore", "notificationstore", "authstore", "memorystore", "workflowstore"]},

    # §6.1.4 구현 중 결정 항목
    {"id": "S6-UI-018", "name": "화면 레이아웃 수 결정", "section": "§6.1.4", "line": 2896, "version": "V1",
     "keywords": ["화면 레이아웃", "4 레이아웃", "7 페이지"]},
    {"id": "S6-UI-019", "name": "라우트 수 결정", "section": "§6.1.4", "line": 2897, "version": "V1",
     "keywords": ["라우트", "react router"]},
    {"id": "S6-UI-020", "name": "다크모드 변수 결정", "section": "§6.1.4", "line": 2898, "version": "V1",
     "keywords": ["다크모드", "dark mode", "css custom properties", "orange/blue 테마"]},
    {"id": "S6-UI-021", "name": "애니메이션 설정 결정", "section": "§6.1.4", "line": 2899, "version": "V1",
     "keywords": ["애니메이션", "framer motion", "css transition"]},

    # §6.1.5 멀티모달 UI
    {"id": "S6-UI-022", "name": "V1 이미지 입력 (CLIP)", "section": "§6.1.5", "line": 2905, "version": "V1",
     "keywords": ["이미지 입력", "clip"]},
    {"id": "S6-UI-023", "name": "V1 OCR (Tesseract+PyMuPDF)", "section": "§6.1.5", "line": 2906, "version": "V1",
     "keywords": ["ocr", "tesseract", "pymupdf"]},
    {"id": "S6-UI-024", "name": "V1 STT (Whisper 로컬)", "section": "§6.1.5", "line": 2907, "version": "V1",
     "keywords": ["stt", "whisper"]},
    {"id": "S6-UI-025", "name": "V1 TTS (Edge TTS)", "section": "§6.1.5", "line": 2908, "version": "V1",
     "keywords": ["tts", "edge tts"]},
    {"id": "S6-UI-026", "name": "V1 차트 (Mermaid+Plotly)", "section": "§6.1.5", "line": 2909, "version": "V1",
     "keywords": ["mermaid", "plotly", "차트"]},
    {"id": "S6-UI-027", "name": "V1 문서 (Markdown→PDF)", "section": "§6.1.5", "line": 2910, "version": "V1",
     "keywords": ["markdown", "pdf", "문서 변환"]},
    {"id": "S6-UI-028", "name": "V2 실시간 음성 채팅", "section": "§6.1.5", "line": 2905, "version": "V2",
     "keywords": ["실시간 음성", "음성 채팅"]},
    {"id": "S6-UI-029", "name": "V2 이미지 생성 게이트웨이", "section": "§6.1.5", "line": 2906, "version": "V2",
     "keywords": ["이미지 생성", "imagegengateway"]},
    {"id": "S6-UI-030", "name": "V2 Computer Use Agent", "section": "§6.1.5", "line": 2907, "version": "V2",
     "keywords": ["computer use"]},
    {"id": "S6-UI-031", "name": "V2 멀티모달 RAG", "section": "§6.1.5", "line": 2908, "version": "V2",
     "keywords": ["멀티모달 rag"]},
    {"id": "S6-UI-032", "name": "V2 PPT 자동 생성", "section": "§6.1.5", "line": 2909, "version": "V2",
     "keywords": ["ppt", "ppt 자동 생성"]},
    {"id": "S6-UI-033", "name": "V2 멀티모달 워크플로우", "section": "§6.1.5", "line": 2910, "version": "V2",
     "keywords": ["멀티모달 워크플로우"]},
    {"id": "S6-UI-034", "name": "V3 3D 생성", "section": "§6.1.5", "line": 2905, "version": "V3",
     "keywords": ["3d 생성"]},
    {"id": "S6-UI-035", "name": "V3 비디오 스트리밍", "section": "§6.1.5", "line": 2906, "version": "V3",
     "keywords": ["비디오 스트리밍"]},
    {"id": "S6-UI-036", "name": "V3 아바타/디지털 휴먼", "section": "§6.1.5", "line": 2907, "version": "V3",
     "keywords": ["아바타", "디지털 휴먼"]},
    {"id": "S6-UI-037", "name": "V3 음성 클로닝", "section": "§6.1.5", "line": 2908, "version": "V3",
     "keywords": ["음성 클로닝"]},
    {"id": "S6-UI-038", "name": "V3 AR/공간 이해", "section": "§6.1.5", "line": 2909, "version": "V3",
     "keywords": ["ar", "공간 이해"]},
    {"id": "S6-UI-039", "name": "V3 수어 생성", "section": "§6.1.5", "line": 2910, "version": "V3",
     "keywords": ["수어"]},

    # §6.1.6 UI State Machine (9-state)
    {"id": "S6-UI-040", "name": "UI State Machine 9-state", "section": "§6.1.6", "line": 2917, "version": "V1",
     "keywords": ["ui state machine", "ui_s0", "ui_s1", "ui_s2", "ui_s3", "ui_s4", "ui_s5", "ui_s6", "ui_s7", "ui_s8", "9-state"]},

    # §6.1.7 Failure/Fallback UI
    {"id": "S6-UI-041", "name": "Failure/Fallback UI 규칙", "section": "§6.1.7", "line": 2940, "version": "V1",
     "keywords": ["fm_err_timeout", "fm_err_rate_limit", "tl_err_exec", "mc_err_conn", "failurecode", "fallbackregistry"]},

    # §6.1.8 UI RBAC
    {"id": "S6-UI-042", "name": "UI RBAC 접근 제어", "section": "§6.1.8", "line": 2950, "version": "V1",
     "keywords": ["rbac", "owner", "admin", "operator", "viewer", "접근 제어"]},

    # §6.2.1 Tauri IPC 핸들러 (72개)
    {"id": "S6-RUST-001", "name": "Tauri IPC Core 핸들러 (15개)", "section": "§6.2.1", "line": 2965, "version": "V1",
     "keywords": ["vamos:decision:create", "vamos:workflow:start", "ipc core"]},
    {"id": "S6-RUST-002", "name": "Tauri IPC Agent 핸들러 (15개)", "section": "§6.2.1", "line": 2966, "version": "V1",
     "keywords": ["vamos:node:dispatch", "vamos:pipeline:hitl_respond", "ipc agent"]},
    {"id": "S6-RUST-003", "name": "Tauri IPC Storage 핸들러 (18개)", "section": "§6.2.1", "line": 2967, "version": "V1",
     "keywords": ["vamos:memory:save", "vamos:vector:search", "ipc storage", "graphrag", "qod"]},
    {"id": "S6-RUST-004", "name": "Tauri IPC Safety 핸들러 (19개)", "section": "§6.2.1", "line": 2968, "version": "V1",
     "keywords": ["vamos:policy:check", "vamos:cost:budget_get", "ipc safety", "guardrails"]},
    {"id": "S6-RUST-005", "name": "Tauri IPC UI 핸들러 (5개)", "section": "§6.2.1", "line": 2969, "version": "V1",
     "keywords": ["vamos:ui:log_stream", "vamos:ui:config_set", "ipc ui"]},

    # §6.2.2 Python-Rust JSON-RPC (13개)
    {"id": "S6-RUST-006", "name": "Python-Rust JSON-RPC 메서드 (13개)", "section": "§6.2.2", "line": 2974, "version": "V1",
     "keywords": ["langgraph.workflow.run", "langgraph.stage.execute", "langgraph.decision.create",
                   "langgraph.node.dispatch", "langgraph.verify.run_chain", "embedding.encode",
                   "embedding.store", "llm.generate", "llm.record_invoke", "llm.rate_limit.get",
                   "mcp.bridge.init", "mcp.bridge.health", "mcp.tools.discover",
                   "json-rpc", "python-rust"]},

    # §6.2.3 Rust 핵심 모듈
    {"id": "S6-RUST-007", "name": "ipc_protocol.rs", "section": "§6.2.3", "line": 2987, "version": "V1",
     "keywords": ["ipc_protocol.rs", "json 직렬화", "trace_id 주입"]},
    {"id": "S6-RUST-008", "name": "python_manager.rs", "section": "§6.2.3", "line": 2988, "version": "V1",
     "keywords": ["python_manager.rs", "python 프로세스", "스폰", "헬스체크"]},
    {"id": "S6-RUST-009", "name": "config.rs", "section": "§6.2.3", "line": 2989, "version": "V1",
     "keywords": ["config.rs", "config.toml", "env 오버라이드"]},
    {"id": "S6-RUST-010", "name": "serde 모델 25개", "section": "§6.2.3", "line": 2990, "version": "V1",
     "keywords": ["serde 모델", "d2.1 스키마"]},

    # §6.3 테스트
    {"id": "S6-TEST-001", "name": "Python Unit (pytest ~45)", "section": "§6.3", "line": 2998, "version": "V1",
     "keywords": ["pytest", "python unit"]},
    {"id": "S6-TEST-002", "name": "Rust Unit (cargo test ~8)", "section": "§6.3", "line": 2999, "version": "V1",
     "keywords": ["cargo test", "rust unit"]},
    {"id": "S6-TEST-003", "name": "React Unit (vitest ~15)", "section": "§6.3", "line": 3000, "version": "V1",
     "keywords": ["vitest", "react unit"]},
    {"id": "S6-TEST-004", "name": "Integration (~14)", "section": "§6.3", "line": 3001, "version": "V1",
     "keywords": ["integration", "ipc 브릿지", "파이프라인 e2e", "gate 검증"]},
    {"id": "S6-TEST-005", "name": "E2E (Playwright ~8)", "section": "§6.3", "line": 3002, "version": "V1",
     "keywords": ["playwright", "e2e", "채팅", "다운시프트", "hitl 승인", "guardrails 차단"]},
    {"id": "S6-TEST-006", "name": "VAL-001~VAL-010 검증 규칙", "section": "§6.3", "line": 3006, "version": "V1",
     "keywords": ["val-001", "val-002", "val-003", "val-004", "val-005", "val-006", "val-007", "val-008", "val-009", "val-010"]},
    {"id": "S6-TEST-007", "name": "AC 매핑 (50 AC → 79 테스트)", "section": "§6.3", "line": 3019, "version": "V1",
     "keywords": ["acceptance criteria", "ac 매핑", "50 ac", "79 테스트"]},

    # §6.4 CI/CD
    {"id": "S6-CICD-001", "name": "quality-python.yml (ruff+mypy)", "section": "§6.4", "line": 3032, "version": "V1",
     "keywords": ["quality-python", "ruff", "mypy"]},
    {"id": "S6-CICD-002", "name": "quality-rust.yml (cargo fmt+clippy)", "section": "§6.4", "line": 3033, "version": "V1",
     "keywords": ["quality-rust", "cargo fmt", "clippy"]},
    {"id": "S6-CICD-003", "name": "quality-react.yml (eslint+tsc)", "section": "§6.4", "line": 3034, "version": "V1",
     "keywords": ["quality-react", "eslint", "tsc"]},
    {"id": "S6-CICD-004", "name": "quality-schema.yml (Pydantic 검증)", "section": "§6.4", "line": 3035, "version": "V1",
     "keywords": ["quality-schema", "pydantic"]},
    {"id": "S6-CICD-005", "name": "test-python.yml", "section": "§6.4", "line": 3036, "version": "V1",
     "keywords": ["test-python"]},
    {"id": "S6-CICD-006", "name": "test-rust.yml", "section": "§6.4", "line": 3037, "version": "V1",
     "keywords": ["test-rust", "tarpaulin"]},
    {"id": "S6-CICD-007", "name": "test-react.yml", "section": "§6.4", "line": 3038, "version": "V1",
     "keywords": ["test-react", "v8 coverage"]},
    {"id": "S6-CICD-008", "name": "coverage-report.yml", "section": "§6.4", "line": 3039, "version": "V1",
     "keywords": ["coverage-report", "커버리지 병합"]},
    {"id": "S6-CICD-009", "name": "build-tauri.yml (크로스 플랫폼)", "section": "§6.4", "line": 3040, "version": "V1",
     "keywords": ["build-tauri", "크로스 플랫폼", "win/mac/linux"]},
    {"id": "S6-CICD-010", "name": "release.yml", "section": "§6.4", "line": 3041, "version": "V1",
     "keywords": ["release"]},
    {"id": "S6-CICD-011", "name": "security.yml (audit)", "section": "§6.4", "line": 3042, "version": "V1",
     "keywords": ["security.yml", "pip-audit", "cargo-audit", "npm audit"]},
    {"id": "S6-CICD-012", "name": "build-docker.yml", "section": "§6.4", "line": 3043, "version": "V2",
     "keywords": ["build-docker", "docker 이미지"]},
    {"id": "S6-CICD-013", "name": "deploy-v2.yml (Docker Compose)", "section": "§6.4", "line": 3044, "version": "V2",
     "keywords": ["deploy-v2", "docker compose", "ssh 배포"]},
    {"id": "S6-CICD-014", "name": "deploy-v3.yml (K8s Helm)", "section": "§6.4", "line": 3045, "version": "V3",
     "keywords": ["deploy-v3", "k8s", "helm", "blue-green"]},

    # §6.5 보안 (15개)
    {"id": "S6-SEC-001", "name": "NeMo Guardrails (L1)", "section": "§6.5", "line": 3053, "version": "V1",
     "keywords": ["nemo guardrails", "입력 방어"]},
    {"id": "S6-SEC-002", "name": "Guardrails AI (L2)", "section": "§6.5", "line": 3054, "version": "V1",
     "keywords": ["guardrails ai", "출력 검증", "구조화 출력"]},
    {"id": "S6-SEC-003", "name": "LlamaGuard (L3)", "section": "§6.5", "line": 3055, "version": "V2",
     "keywords": ["llamaguard", "안전 분류"]},
    {"id": "S6-SEC-004", "name": "PII Regex 마스킹", "section": "§6.5", "line": 3056, "version": "V1",
     "keywords": ["pii regex", "주민번호", "전화번호", "이메일", "카드번호", "pii 마스킹"]},
    {"id": "S6-SEC-005", "name": "RBAC 시스템", "section": "§6.5", "line": 3057, "version": "V1",
     "keywords": ["rbac 시스템", "4레벨"]},
    {"id": "S6-SEC-006", "name": "Autonomy 레벨 L0~L3", "section": "§6.5", "line": 3058, "version": "V1",
     "keywords": ["autonomy 레벨", "l0", "l1", "l2", "l3", "자율성 게이팅"]},
    {"id": "S6-SEC-007", "name": "P2 세션 승인 + 자동 OFF", "section": "§6.5", "line": 3059, "version": "V1",
     "keywords": ["p2 세션 승인", "자동 off", "자동 비활성"]},
    {"id": "S6-SEC-008", "name": "Docker 코드 샌드박스", "section": "§6.5", "line": 3060, "version": "V1",
     "keywords": ["docker 코드 샌드박스", "네트워크 격리", "30초 타임아웃", "코드 샌드박스"]},
    {"id": "S6-SEC-009", "name": "승인 타임아웃 10분 auto-deny", "section": "§6.5", "line": 3061, "version": "V1",
     "keywords": ["승인 타임아웃", "10분", "auto-deny"]},
    {"id": "S6-SEC-010", "name": "SQLCipher 암호화", "section": "§6.5", "line": 3062, "version": "V1",
     "keywords": ["sqlcipher", "aes-256-cbc"]},
    {"id": "S6-SEC-011", "name": "API Key 관리", "section": "§6.5", "line": 3063, "version": "V1",
     "keywords": ["api key", ".env", "dotenv", ".gitignore"]},
    {"id": "S6-SEC-012", "name": "입력 검증 (Zod+regex)", "section": "§6.5", "line": 3064, "version": "V1",
     "keywords": ["zod", "regex 패턴", "입력 검증"]},
    {"id": "S6-SEC-013", "name": "HMAC-SHA256 Agent 인증", "section": "§6.5", "line": 3065, "version": "V2",
     "keywords": ["hmac-sha256", "hmac", "agent messagebus 인증"]},
    {"id": "S6-SEC-014", "name": "GDPR 데이터 권리", "section": "§6.5", "line": 3066, "version": "V2",
     "keywords": ["gdpr", "데이터 권리", "열람", "이동", "삭제"]},
    {"id": "S6-SEC-015", "name": "DEC-003 도구 승인 Allowlist", "section": "§6.5", "line": 3067, "version": "V1",
     "keywords": ["dec-003", "도구 승인", "allowlist", "읽기전용=자동승인"]},

    # §6.6 MCP 서버/클라이언트 (~7개 + 11개 외부 카탈로그)
    {"id": "S6-MCP-001", "name": "MCP Bridge Layer", "section": "§6.6", "line": 3075, "version": "V1",
     "keywords": ["mcp bridge", "streamable http"]},
    {"id": "S6-MCP-002", "name": "MCP Server (20+ tools)", "section": "§6.6", "line": 3076, "version": "V1",
     "keywords": ["mcp server", "mcp 서버", "20+ tools"]},
    {"id": "S6-MCP-003", "name": "MCP Client", "section": "§6.6", "line": 3077, "version": "V1",
     "keywords": ["mcp client", "mcp 클라이언트"]},
    {"id": "S6-MCP-004", "name": "Pyodide MCP 래퍼", "section": "§6.6", "line": 3078, "version": "V1",
     "keywords": ["pyodide", "로컬 python 실행"]},
    {"id": "S6-MCP-005", "name": "PyMuPDF MCP 래퍼", "section": "§6.6", "line": 3079, "version": "V1",
     "keywords": ["pymupdf mcp", "로컬 pdf 파싱"]},
    {"id": "S6-MCP-006", "name": "CLIP MCP 래퍼", "section": "§6.6", "line": 3080, "version": "V2",
     "keywords": ["clip mcp", "로컬 이미지 분석"]},
    {"id": "S6-MCP-007", "name": "Playwright MCP 래퍼", "section": "§6.6", "line": 3081, "version": "V1",
     "keywords": ["playwright mcp", "브라우저 자동화"]},
    # 외부 서버 11개
    {"id": "S6-MCP-008", "name": "mcp.search.tavily", "section": "§6.6", "line": 3089, "version": "V1",
     "keywords": ["tavily", "웹 검색"]},
    {"id": "S6-MCP-009", "name": "mcp.search.serpapi", "section": "§6.6", "line": 3090, "version": "V1",
     "keywords": ["serpapi", "검색엔진"]},
    {"id": "S6-MCP-010", "name": "mcp.code.e2b", "section": "§6.6", "line": 3091, "version": "V1",
     "keywords": ["e2b", "코드 실행 샌드박스"]},
    {"id": "S6-MCP-011", "name": "mcp.code.pyodide", "section": "§6.6", "line": 3092, "version": "V1",
     "keywords": ["mcp.code.pyodide"]},
    {"id": "S6-MCP-012", "name": "mcp.doc.unstructured", "section": "§6.6", "line": 3093, "version": "V1",
     "keywords": ["unstructured", "문서 파싱"]},
    {"id": "S6-MCP-013", "name": "mcp.doc.pymupdf", "section": "§6.6", "line": 3094, "version": "V1",
     "keywords": ["mcp.doc.pymupdf"]},
    {"id": "S6-MCP-014", "name": "mcp.vision.clip", "section": "§6.6", "line": 3095, "version": "V2",
     "keywords": ["mcp.vision.clip"]},
    {"id": "S6-MCP-015", "name": "mcp.speech.whisper", "section": "§6.6", "line": 3096, "version": "V2",
     "keywords": ["mcp.speech.whisper"]},
    {"id": "S6-MCP-016", "name": "mcp.browser.playwright", "section": "§6.6", "line": 3097, "version": "V1",
     "keywords": ["mcp.browser.playwright"]},
    {"id": "S6-MCP-017", "name": "mcp.db.postgres", "section": "§6.6", "line": 3098, "version": "V2",
     "keywords": ["mcp.db.postgres"]},
    {"id": "S6-MCP-018", "name": "mcp.realtime.websocket", "section": "§6.6", "line": 3099, "version": "V3",
     "keywords": ["mcp.realtime.websocket", "실시간 통신"]},

    # §6.7 Agent Teams
    {"id": "S6-AT-001", "name": "V1 Agent 기본 구조 (Lead+2 Sub)", "section": "§6.7", "line": 3109, "version": "V1",
     "keywords": ["lead agent", "sub-agent", "에이전트 수", "3"]},
    {"id": "S6-AT-002", "name": "Sequential/Parallel 협업 패턴", "section": "§6.7", "line": 3110, "version": "V1",
     "keywords": ["sequential", "parallel", "협업 패턴"]},
    {"id": "S6-AT-003", "name": "위임 깊이 2단계", "section": "§6.7", "line": 3111, "version": "V1",
     "keywords": ["위임 깊이", "2단계", "lock-at-004"]},
    {"id": "S6-AT-004", "name": "MessageBus In-Memory Queue", "section": "§6.7", "line": 3112, "version": "V1",
     "keywords": ["messagebus", "in-memory queue"]},
    {"id": "S6-AT-005", "name": "Lead Agent (ORANGE CORE)", "section": "§6.7", "line": 3120, "version": "V1",
     "keywords": ["lead agent", "orange core", "i-5"]},
    {"id": "S6-AT-006", "name": "Research Agent (BLUE NODE)", "section": "§6.7", "line": 3121, "version": "V1",
     "keywords": ["research agent", "web_search", "rag"]},
    {"id": "S6-AT-007", "name": "Coding Agent (BLUE NODE)", "section": "§6.7", "line": 3122, "version": "V1",
     "keywords": ["coding agent", "code_gen", "debug"]},
    {"id": "S6-AT-008", "name": "V2 Quant Agent", "section": "§6.7", "line": 3128, "version": "V2",
     "keywords": ["quant agent", "data&quant"]},
    {"id": "S6-AT-009", "name": "V2 Content Agent", "section": "§6.7", "line": 3129, "version": "V2",
     "keywords": ["content agent"]},
    {"id": "S6-AT-010", "name": "V2 Trading Agent", "section": "§6.7", "line": 3130, "version": "V2",
     "keywords": ["trading agent", "opus"]},
    {"id": "S6-AT-011", "name": "V2 Productivity Agent", "section": "§6.7", "line": 3131, "version": "V2",
     "keywords": ["productivity agent"]},
    {"id": "S6-AT-012", "name": "V2 Critic Agent", "section": "§6.7", "line": 3132, "version": "V2",
     "keywords": ["critic agent", "verification"]},
    {"id": "S6-AT-013", "name": "V2 SDAR Agent", "section": "§6.7", "line": 3133, "version": "V2",
     "keywords": ["sdar agent", "i-25"]},
    {"id": "S6-AT-014", "name": "LOCK-AT 아키텍처 제약 (17건)", "section": "§6.7", "line": 3142, "version": "V1",
     "keywords": ["lock-at-001", "lock-at-002", "lock-at-003", "lock-at-004", "lock-at-005",
                   "lock-at-006", "lock-at-007", "lock-at-008", "lock-at-009", "lock-at-010",
                   "lock-at-011", "lock-at-012", "lock-at-013", "lock-at-014", "lock-at-015",
                   "lock-at-016", "lock-at-017"]},
    {"id": "S6-AT-015", "name": "Agent Marketplace", "section": "§6.7", "line": 3136, "version": "V2",
     "keywords": ["agent marketplace", "에이전트 마켓"]},
    {"id": "S6-AT-016", "name": "n8n + Flowise 노코드 빌더", "section": "§6.7", "line": 3160, "version": "V1",
     "keywords": ["n8n", "flowise", "노코드 빌더"]},
]

# ============================================================
# 2. 엄격 매핑 엔진
# ============================================================

def strict_match(feature, s6_item):
    """
    Feature와 §6 항목 간 엄격 매칭.
    최소 1개의 specific keyword가 feature_name 또는 tech_keywords에 존재해야 함.
    """
    fname = (feature.get('feature_name', '') or '').lower()
    tech = feature.get('tech_keywords', []) or []
    tech_lower = [t.lower() for t in tech if t]
    mod = (feature.get('module_id', '') or '').lower()
    notes = (feature.get('notes', '') or '').lower()
    src = (feature.get('source_section', '') or '').lower()

    all_text = f"{fname} {' '.join(tech_lower)} {mod} {notes} {src}"

    score = 0
    matched_kws = []
    for kw in s6_item['keywords']:
        kw_lower = kw.lower()
        if kw_lower in all_text:
            # 가중치: 길이가 긴 키워드일수록 높은 점수
            w = len(kw_lower)
            if w >= 10:
                score += 3
            elif w >= 5:
                score += 2
            else:
                score += 1
            matched_kws.append(kw)

    # 최소 점수 임계값: specific keyword 매칭 필요
    if score >= 3:
        return True, score, matched_kws
    return False, score, matched_kws


def main():
    print("=" * 70)
    print("M-5a Refined: §6.1~§6.7 구현 항목 ↔ Feature Registry 정밀 매핑")
    print("=" * 70)

    # Registry 로드
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)['features']
    print(f"Feature Registry: {len(registry)} features")

    # M-1~M-4 MISSING 로드
    m1_m4_missing = {}
    # M-1
    try:
        with open(os.path.join(OUTPUT_DIR, 'm1_v0_mapping_result.json'), 'r', encoding='utf-8') as f:
            m1 = json.load(f)
        for sev in ['BLOCKER','HIGH','MEDIUM','LOW']:
            for item in m1.get('missing_by_severity',{}).get(sev,[]):
                m1_m4_missing[item['feature_id']] = {'severity': sev, 'agent': 'M-1'}
    except: pass
    # M-2
    try:
        with open(os.path.join(OUTPUT_DIR, 'v10_m2_missing_items.json'), 'r', encoding='utf-8') as f:
            m2m = json.load(f)
        for item in m2m.get('items', []):
            m1_m4_missing[item.get('feature_id','')] = {'severity': item.get('severity','MEDIUM'), 'agent': 'M-2'}
    except: pass
    # M-3
    try:
        with open(os.path.join(OUTPUT_DIR, 'v10_m3_missing_final.json'), 'r', encoding='utf-8') as f:
            m3m = json.load(f)
        items = m3m.get('items', []) if isinstance(m3m, dict) else m3m
        for item in items:
            m1_m4_missing[item.get('feature_id','')] = {'severity': item.get('severity','MEDIUM'), 'agent': 'M-3'}
    except: pass
    # M-4
    try:
        with open(os.path.join(OUTPUT_DIR, 'v10_m4_missing_items.json'), 'r', encoding='utf-8') as f:
            m4m = json.load(f)
        for item in m4m.get('items', []):
            m1_m4_missing[item.get('feature_id','')] = {'severity': item.get('severity','MEDIUM'), 'agent': 'M-4'}
    except: pass
    print(f"M-1~M-4 MISSING: {len(m1_m4_missing)} items")

    # ============================================================
    # 임무 1: §6.1~§6.7에 있지만 §2-§5 Phase에 없는 기능 식별
    # ============================================================
    print("\n[임무 1] §6 항목 → Feature Registry 역매핑...")

    s6_to_features = {}  # s6_item_id -> [matched features]
    feature_to_s6 = defaultdict(list)  # feature_id -> [s6 items]

    for s6_item in S6_ITEMS:
        matched_features = []
        for feat in registry:
            ok, score, kws = strict_match(feat, s6_item)
            if ok:
                matched_features.append({
                    "feature_id": feat['feature_id'],
                    "feature_name": feat['feature_name'],
                    "version_scope": feat.get('version_scope', ''),
                    "part2_mapping_status": feat.get('part2_mapping_status', ''),
                    "part2_phase": feat.get('part2_phase', ''),
                    "score": score,
                    "matched_keywords": kws
                })
                feature_to_s6[feat['feature_id']].append(s6_item['id'])
        s6_to_features[s6_item['id']] = matched_features

    # §6 only: 매칭된 feature 중 Phase 미배정
    s6_only_items = []
    for s6_item in S6_ITEMS:
        matches = s6_to_features.get(s6_item['id'], [])
        phase_assigned = [m for m in matches if m['part2_mapping_status'] in ['PRE_MATCHED', 'PRE_GAP'] or (m['part2_phase'] and m['part2_phase'] not in ['', 'null', 'None'])]
        no_phase = [m for m in matches if m not in phase_assigned]

        if no_phase:
            s6_only_items.append({
                "s6_id": s6_item['id'],
                "s6_name": s6_item['name'],
                "s6_section": s6_item['section'],
                "s6_line": s6_item['line'],
                "features_no_phase": [{
                    "feature_id": m['feature_id'],
                    "feature_name": m['feature_name'],
                    "version_scope": m['version_scope'],
                    "matched_keywords": m['matched_keywords'],
                } for m in no_phase[:10]],  # 최대 10개
                "count_no_phase": len(no_phase),
                "count_with_phase": len(phase_assigned),
            })

    # ============================================================
    # 임무 2: M-1~M-4 MISSING 항목 §6 재확인
    # ============================================================
    print("[임무 2] M-1~M-4 MISSING → §6 재확인...")

    missing_found_in_s6 = []
    missing_not_found = []

    for fid, info in m1_m4_missing.items():
        feat = next((f for f in registry if f['feature_id'] == fid), None)
        if not feat:
            missing_not_found.append({"feature_id": fid, **info, "reason": "Feature not in registry"})
            continue

        found_s6 = []
        for s6_item in S6_ITEMS:
            ok, score, kws = strict_match(feat, s6_item)
            if ok:
                found_s6.append({
                    "s6_id": s6_item['id'],
                    "s6_name": s6_item['name'],
                    "s6_section": s6_item['section'],
                    "s6_line": s6_item['line'],
                    "score": score,
                    "matched_keywords": kws
                })

        if found_s6:
            missing_found_in_s6.append({
                "feature_id": fid,
                "feature_name": feat['feature_name'],
                "version_scope": feat.get('version_scope', ''),
                "original_severity": info['severity'],
                "source_agent": info['agent'],
                "s6_locations": found_s6,
                "verdict": "PARTIAL",
                "verdict_detail": f"§6 only ({', '.join(s['s6_section'] for s in found_s6[:3])}), Phase 미배정"
            })
        else:
            missing_not_found.append({
                "feature_id": fid,
                "feature_name": feat['feature_name'],
                "version_scope": feat.get('version_scope', ''),
                "original_severity": info['severity'],
                "source_agent": info['agent'],
                "verdict": "STILL_MISSING",
                "verdict_detail": "§6.1~§6.7에서도 미발견"
            })

    # ============================================================
    # 임무 3: V_UNKNOWN 항목 §6 발견 시도
    # ============================================================
    print("[임무 3] V_UNKNOWN 항목 §6 검색...")

    v_unknown = [f for f in registry if f.get('version_scope', '') == 'V_UNKNOWN']
    v_unknown_found = []
    for feat in v_unknown:
        for s6_item in S6_ITEMS:
            ok, score, kws = strict_match(feat, s6_item)
            if ok:
                v_unknown_found.append({
                    "feature_id": feat['feature_id'],
                    "feature_name": feat['feature_name'],
                    "s6_section": s6_item['section'],
                    "s6_version": s6_item['version'],
                    "suggested_version": s6_item['version'],
                    "evidence": kws
                })
                break
    print(f"  V_UNKNOWN: {len(v_unknown)} total, {len(v_unknown_found)} found in §6")

    # ============================================================
    # 결과 출력
    # ============================================================

    # §6 항목별 Feature 매핑 수
    print(f"\n{'='*70}")
    print(f"M-5a 정밀 매핑 결과 요약")
    print(f"{'='*70}")

    total_s6_items = len(S6_ITEMS)
    total_matched_features = len(feature_to_s6)
    unique_matched = set()
    for s6_id, feats in s6_to_features.items():
        for f in feats:
            unique_matched.add(f['feature_id'])

    print(f"\n§6.1~§6.7 구현 항목 수: {total_s6_items}")
    print(f"매칭된 고유 Feature 수: {len(unique_matched)}")

    # 섹션별 통계
    sec_stats = defaultdict(lambda: {"items": 0, "matched_features": 0, "no_phase": 0})
    for s6_item in S6_ITEMS:
        sec = s6_item['section'].split('.')[0] + '.' + s6_item['section'].split('.')[1] if '.' in s6_item['section'] else s6_item['section']
        sec_stats[sec]["items"] += 1
        matches = s6_to_features.get(s6_item['id'], [])
        sec_stats[sec]["matched_features"] += len(matches)
        no_phase_cnt = sum(1 for m in matches if m['part2_mapping_status'] not in ['PRE_MATCHED','PRE_GAP'] and not (m['part2_phase'] and m['part2_phase'] not in ['','null','None']))
        sec_stats[sec]["no_phase"] += no_phase_cnt

    print(f"\n섹션별 통계:")
    print(f"{'섹션':<10} {'§6항목수':>8} {'매칭Feature':>10} {'Phase미배정':>10}")
    print("-" * 42)
    for sec in sorted(sec_stats.keys()):
        s = sec_stats[sec]
        print(f"{sec:<10} {s['items']:>8} {s['matched_features']:>10} {s['no_phase']:>10}")

    print(f"\nM-1~M-4 MISSING 재확인:")
    print(f"  총 MISSING: {len(m1_m4_missing)}")
    print(f"  §6에서 발견: {len(missing_found_in_s6)}")
    print(f"  §6에서도 미발견: {len(missing_not_found)}")

    if missing_found_in_s6:
        print(f"\n  §6에서 발견된 MISSING 항목 (PARTIAL 판정):")
        by_sev = defaultdict(list)
        for item in missing_found_in_s6:
            by_sev[item['original_severity']].append(item)
        for sev in ['BLOCKER','HIGH','MEDIUM','LOW']:
            items = by_sev.get(sev, [])
            if items:
                print(f"\n  [{sev}] ({len(items)}건):")
                for item in items[:10]:
                    locs = ', '.join(s['s6_section'] for s in item['s6_locations'][:3])
                    print(f"    {item['feature_id']}: {item['feature_name'][:55]}")
                    print(f"      → {locs} | from {item['source_agent']}")

    # ============================================================
    # JSON 출력
    # ============================================================

    output = {
        "_meta": {
            "agent": "M-5a",
            "phase": "Phase 1",
            "scope": "§6.1~§6.7 시스템별 상세 (전반부)",
            "method": "§6 구현항목 기반 역매핑 (strict keyword matching)",
            "s6_items_total": total_s6_items,
            "total_features_scanned": len(registry),
            "generated_date": "2026-03-09",
            "part2_version": "v21.0.0",
            "part2_lines": f"L2848~L3165"
        },
        "statistics": {
            "s6_implementation_items": total_s6_items,
            "unique_features_matched_to_s6": len(unique_matched),
            "s6_only_no_phase_groups": len(s6_only_items),
            "m1_m4_missing_total": len(m1_m4_missing),
            "m1_m4_missing_found_in_s6": len(missing_found_in_s6),
            "m1_m4_missing_still_missing": len(missing_not_found),
            "v_unknown_total": len(v_unknown),
            "v_unknown_found_in_s6": len(v_unknown_found),
        },
        "subsection_stats": {k: dict(v) for k, v in sorted(sec_stats.items())},
        "task1_s6_only_no_phase": s6_only_items,
        "task2_missing_found_in_s6": missing_found_in_s6,
        "task2_missing_not_found": missing_not_found[:50],  # 상위 50건만
        "task3_v_unknown_in_s6": v_unknown_found,
        "s6_item_mapping_detail": {
            s6_item['id']: {
                "s6_name": s6_item['name'],
                "section": s6_item['section'],
                "line": s6_item['line'],
                "version": s6_item['version'],
                "matched_features_count": len(s6_to_features.get(s6_item['id'], [])),
                "top_matches": [
                    {"fid": m['feature_id'], "name": m['feature_name'][:60], "score": m['score']}
                    for m in sorted(s6_to_features.get(s6_item['id'], []), key=lambda x: -x['score'])[:5]
                ]
            }
            for s6_item in S6_ITEMS
        }
    }

    result_path = os.path.join(OUTPUT_DIR, 'v10_m5a_mapping_result.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Result: {result_path}")

    # Markdown 보고서
    report = generate_report(output, missing_found_in_s6, missing_not_found, s6_only_items, sec_stats, v_unknown_found)
    report_path = os.path.join(OUTPUT_DIR, 'v10_m5a_mapping_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ Report: {report_path}")


def generate_report(output, missing_found, missing_not_found, s6_only, sec_stats, v_unknown):
    lines = []
    lines.append("# M-5a 매핑 검증 보고서: §6.1~§6.7 시스템별 상세")
    lines.append("")
    lines.append(f"- **에이전트**: M-5a")
    lines.append(f"- **범위**: PART2 §6.1~§6.7 (L2848~L3165)")
    lines.append(f"- **방법**: §6 구현항목 {len(S6_ITEMS)}개 추출 → Feature Registry 역매핑")
    lines.append(f"- **생성일**: 2026-03-09")
    lines.append("")

    # 통계
    stats = output['statistics']
    lines.append("## 1. 통계 요약")
    lines.append("")
    lines.append(f"| 지표 | 값 |")
    lines.append(f"|------|-----|")
    lines.append(f"| §6 구현 항목 수 | {stats['s6_implementation_items']} |")
    lines.append(f"| 매칭된 고유 Feature 수 | {stats['unique_features_matched_to_s6']} |")
    lines.append(f"| §6 only (Phase 미배정) 그룹 수 | {stats['s6_only_no_phase_groups']} |")
    lines.append(f"| M-1~M-4 MISSING → §6 발견 | {stats['m1_m4_missing_found_in_s6']} |")
    lines.append(f"| M-1~M-4 MISSING → §6 미발견 | {stats['m1_m4_missing_still_missing']} |")
    lines.append(f"| V_UNKNOWN → §6 발견 | {stats['v_unknown_found_in_s6']} |")
    lines.append("")

    # 섹션별 통계
    lines.append("## 2. 섹션별 커버리지")
    lines.append("")
    lines.append(f"| 섹션 | §6항목수 | 매칭Feature | Phase미배정 |")
    lines.append(f"|------|---------|-----------|-----------|")
    for sec in sorted(sec_stats.keys()):
        s = sec_stats[sec]
        lines.append(f"| {sec} | {s['items']} | {s['matched_features']} | {s['no_phase']} |")
    lines.append("")

    # 임무 1: §6 only
    lines.append("## 3. [임무 1] §6 only, Phase 미배정 항목")
    lines.append("")
    lines.append("> §6.1~§6.7에 구현 항목으로 존재하지만 §2~§5 Phase에 배정되지 않은 Feature")
    lines.append("> → **PARTIAL** 판정: \"§6 only, Phase 미배정\"")
    lines.append("")
    for item in s6_only:
        lines.append(f"### {item['s6_id']}: {item['s6_name']} ({item['s6_section']} L{item['s6_line']})")
        lines.append(f"- Phase 미배정 Feature: **{item['count_no_phase']}건** (Phase 배정: {item['count_with_phase']}건)")
        if item['features_no_phase']:
            lines.append("")
            lines.append(f"| feature_id | feature_name | version_scope |")
            lines.append(f"|-----------|-------------|--------------|")
            for f in item['features_no_phase'][:10]:
                lines.append(f"| {f['feature_id']} | {f['feature_name'][:50]} | {f['version_scope']} |")
        lines.append("")

    # 임무 2: MISSING 재확인
    lines.append("## 4. [임무 2] M-1~M-4 MISSING → §6 재확인")
    lines.append("")

    if missing_found:
        lines.append(f"### §6에서 발견됨 ({len(missing_found)}건) → PARTIAL 재판정")
        lines.append("")
        lines.append(f"| feature_id | feature_name | severity | agent | §6 위치 |")
        lines.append(f"|-----------|-------------|---------|-------|--------|")
        for item in missing_found:
            locs = ', '.join(s['s6_section'] for s in item['s6_locations'][:3])
            lines.append(f"| {item['feature_id']} | {item['feature_name'][:40]} | {item['original_severity']} | {item['source_agent']} | {locs} |")
        lines.append("")

    lines.append(f"### §6에서도 미발견 ({len(missing_not_found)}건) → MISSING 유지")
    lines.append("")
    lines.append("> 이 항목들은 M-5b에서 §6.8~§6.13 + §7 검색 예정")
    lines.append("")

    # 임무 3: V_UNKNOWN
    if v_unknown:
        lines.append("## 5. [임무 3] V_UNKNOWN → §6 버전 확정 시도")
        lines.append("")
        lines.append(f"| feature_id | feature_name | §6 위치 | 추정 버전 |")
        lines.append(f"|-----------|-------------|--------|---------|")
        for item in v_unknown:
            lines.append(f"| {item['feature_id']} | {item['feature_name'][:40]} | {item['s6_section']} | {item['suggested_version']} |")
        lines.append("")

    return '\n'.join(lines)


if __name__ == "__main__":
    main()
