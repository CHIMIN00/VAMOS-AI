# Before Fix 009 — FG-B06: V2-Phase 2 프롬프트 재설계
# Snapshot at: 2026-03-12
# Issue: AI 프롬프트가 원본 10개 COND 모듈만 커버, v10 추가 106개(#11~#116) 미반영 (커버리지 10/116 ≈ 8.6%)

## L2211-2332 (AI 프롬프트 전체)
```
````text
VAMOS 프로젝트 V2-Phase 2: COND 모듈 활성화를 진행합니다.

## 작업 목표
V2 COND 모듈 10개를 구현하고 활성화합니다.
...
## 10. E-16 Cloud Storage Sync → ...

## 규칙
- 모든 모듈은 BaseModule(ABC) 상속, `enabled` 플래그로 ON/OFF 제어
...

**config.v2.toml COND 모듈 키 목록** (FIX-20):
```toml
[modules.cond]
i07.enabled = false          # Project/Session Manager
...
e16.sync_interval_min = 30
```

## 참조 SOT 문서
...
````
```

## L2334-2352 (완료 검증)
```
| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | 10개 COND 모듈 코드 | 10개 모듈 파일 존재 + BaseModule 상속 + enabled 플래그 동작 | ✅ |
...
| 14 | 개별→통합 테스트 | 10개 모듈 개별 활성화 검증 후 전체 동시 활성화 상호작용 검증 | ✅ |
```

## L2201-2208 (사용자 직접 작업)
```
1. **COND 활성화 조건 확인**: V1→V2 전환 조건 6항 충족 여부 검증
2. **외부 서비스 API 키 발급**: Google Calendar API ...
3. **RSS 피드 소스 등록**: RT-BNP V1용 ...
4. **config.v2.toml 모듈 활성화**: 각 COND 모듈 `enabled = true` 전환
5. **각 모듈 통합 테스트**: 10개 모듈 개별 활성화 후 기능 동작 검증
6. **SDAR AR-L3 승인 정책 설정**: MEDIUM risk 자동 수리 범위 확인
```
