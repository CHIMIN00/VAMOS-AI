---
name: trace
description: Langfuse를 통한 LLM 호출 자동 로깅, Phase별 환각률 추이, 비용 추적
triggers:
  - /trace
args:
  - name: command
    description: "start [phase번호] | stop | dashboard"
---

# `/trace` — Langfuse LLM 관측

## 목적
모든 EA 추출/검증/감사 결과를 **Langfuse에 자동 로깅**하여 Phase별 환각률 추이, 프롬프트 변경 전후 비교, 비용 추적을 수행.

## 전제 조건
- Langfuse 서버 실행 중 (localhost:3000)
- 환경변수: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`
- `pip install langfuse`

## 실행 절차

### `/trace start [phase번호]`
1. Langfuse 연결 확인
2. 해당 Phase의 모든 스킬 실행을 trace로 래핑
3. 각 trace에 메타데이터 기록:
   - phase, sot_file, ea_file, skill_name, timestamp
   - 입력/출력 토큰 수, 실행 시간
4. 결과를 Langfuse에 자동 전송

### `/trace stop`
로깅 중단, 현재 세션 요약 출력

### `/trace dashboard`
Langfuse 대시보드 URL 출력: http://localhost:3000

### 보고서 출력
```
## Trace 요약
- 세션: Phase 0
- 총 호출: N회
- 총 토큰: X (입력 Y + 출력 Z)
- 평균 응답시간: W초
- 대시보드: http://localhost:3000
```

## Python 스크립트
```bash
python D:\VAMOS\.claude\hooks\langfuse_logger.py --action start|stop|status
```
