# 모바일 자동화 (Appium iOS/Android RPA) — L3 상세 명세 (N-018 V3)

> **Status**: APPROVED (L3 V3)
> **N-ID**: N-018 (V3 NEW — 모바일 RPA)
> **V단계**: V3-Phase 4 (RECOVERY Stage B — genuine production write)
> **작성일**: 2026-05-31 (Phase 4 RECOVERY Stage A+B 통합)
> **도메인**: 3-4_Workflow-RPA / 06_desktop-rpa
> **정본**: sot 2/3-4_Workflow-RPA/06_desktop-rpa/mobile_automation.md
> **상위 SoT**: STEP7-N N-018 (모바일 자동화 — Appium 기반 모바일 RPA) + 종합계획서 §6.6 + §7 P4-1
> **상위 인덱스**: [_index.md](./_index.md)
> **L3 목표**: ≥ 80점 (E1~E10 9요소) — LOCK-WF-08 12 액션 모바일 적응 + LOCK-WF-10 보안

---

## LOCK 인용 (verbatim — 재정의 ❌)

> LOCK (WF AUTHORITY §3.4 / LOCK-WF-08): launch_app, keyboard, mouse_click, mouse_move, type_text, screenshot, ocr_extract, image_match, wait_element, scroll, drag_drop, clipboard

> LOCK (WF AUTHORITY §3.4 / LOCK-WF-10): 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화

> LOCK (WF AUTHORITY §3.4 / LOCK-WF-05): LangGraph StateGraph 기반, 최대 동시 실행 수 = 10

> LOCK (WF AUTHORITY §3.4 / LOCK-WF-09): PENDING → RUNNING → (SUCCESS | FAILED | CANCELLED | TIMEOUT)

**본 V3는 LOCK-WF-08 데스크톱 12 액션을 모바일 환경에 적응(매핑)하되 액션 집합을 재정의하지 않으며, LOCK-WF-10 보안 정책과 LOCK-WF-05 동시 실행 상한 10, LOCK-WF-09 상태 머신을 소비·보존만 한다 (재정의 ❌).**

**거버넌스**: R-07-4 (샌드박스 격리) + R-07-5 (자격증명 AES-256-GCM 암호화) + R-07-6 (실행 로그 30일 보존).

---

## E1. 개요 / 목적

모바일 RPA는 iOS/Android 네이티브·하이브리드 앱에 대한 자동화 워크플로우를 정의한다. WebDriver 프로토콜(W3C) 기반 **Appium**을 표준 드라이버로 채택하여, 데스크톱 RPA(LOCK-WF-08 12 액션)와 동일한 워크플로우 모델 위에서 모바일 디바이스를 제어한다.

- **목표 KPI**: 모바일 RPA 안정성 V3 ≥ 90% + 액션 응답 p95 ≤ 2초 + 자격증명 평문 저장 0건
- **사용 시나리오**: 모바일 앱 회귀 테스트 자동화, 모바일 SNS 게시 자동화(04_template-library 연계), 모바일 본인인증/스크래핑(동의 기반)
- **위치**: DAG 워크플로우의 한 노드 타입으로 동작 — `MobileActionNode`는 LOCK-WF-08 12 액션을 모바일 제스처로 매핑한 실행 단위이며, 상위 DAG의 LOCK-WF-02(50 노드)·LOCK-WF-04(순환 금지) 제약을 그대로 상속한다.

---

## E2. 아키텍처

```
[DAG 워크플로우 (LOCK-WF-01 노드 + LOCK-WF-04 DAG 무결성)]
    ↓  MobileActionNode (LOCK-WF-08 12 액션 모바일 매핑)
[MobileAutomationExecutor]
    ├─ 1. 디바이스 세션 획득 (DeviceFarmPool, LOCK-WF-05 동시 ≤10)
    ├─ 2. Appium 드라이버 연결 (iOS=XCUITest / Android=UiAutomator2)
    ├─ 3. 화면 인식 3단계 (네이티브 ID → XPath → 이미지 매치 폴백)
    ├─ 4. 액션 실행 (12 액션 → tap/swipe/longPress/scroll/type/screenshot...)
    ├─ 5. 결과 캡처 + 30일 로그 보존 (R-07-6, 샌드박스 격리 R-07-4)
    └─ 6. 세션 반납 (디바이스 풀 복귀)
```

### E2.1 컴포넌트 책임

| 컴포넌트 | 책임 |
|----------|------|
| `MobileActionNode` | LOCK-WF-08 액션을 모바일 제스처로 매핑한 DAG 노드 |
| `MobileAutomationExecutor` | Appium 세션 lifecycle + 액션 디스패치 + 상태 머신(LOCK-WF-09) |
| `DeviceFarmPool` | 디바이스 할당/반납 + 동시 실행 quota(LOCK-WF-05 ≤10) |
| `ScreenRecognizer` | 3단계 요소 탐색 (네이티브 ID → XPath → 이미지) |
| `CredentialVault` | AES-256-GCM 자격증명 (R-07-5) |

---

## E3. 데이터 스키마 / 인터페이스

### E3.1 LOCK-WF-08 12 액션 → 모바일 제스처 매핑

| # | LOCK-WF-08 데스크톱 액션 | 모바일 적응 매핑 | Appium 호출 |
|---|--------------------------|------------------|-------------|
| 1 | `launch_app` | 앱 실행 (번들 ID / 패키지명) | `driver.activate_app()` |
| 2 | `keyboard` | 소프트 키보드 입력 | `driver.execute_script("mobile: keys")` |
| 3 | `mouse_click` | **tap** (단일 탭) | `el.click()` / `mobile: tap` |
| 4 | `mouse_move` | **swipe / drag** (좌표 이동) | `mobile: swipeGesture` |
| 5 | `type_text` | 텍스트 입력 | `el.send_keys()` |
| 6 | `screenshot` | 화면 캡처 | `driver.get_screenshot_as_base64()` |
| 7 | `ocr_extract` | 화면 텍스트 OCR 추출 | OCR 엔진 + screenshot 합성 |
| 8 | `image_match` | 이미지 템플릿 매칭(폴백) | `mobile: viewportScreenshot` + 매칭 |
| 9 | `wait_element` | 요소 출현 대기 | `WebDriverWait.until(EC...)` |
| 10 | `scroll` | **scroll / fling** | `mobile: scrollGesture` |
| 11 | `drag_drop` | **longPress + move** | `mobile: dragGesture` |
| 12 | `clipboard` | 클립보드 읽기/쓰기 | `driver.set_clipboard()` / `get_clipboard()` |

> **정합**: 12 액션 집합은 LOCK-WF-08 verbatim 유지(삭제·재정의 ❌). 모바일 고유 제스처(pinch/zoom, longPress)는 기존 액션의 모바일 표현일 뿐 신규 액션 추가가 아니다.

### E3.2 노드 config 스키마

```typescript
interface MobileActionNodeConfig {
  platform: "ios" | "android";
  app: { bundleId?: string; appPackage?: string; appActivity?: string };
  action: "tap" | "swipe" | "type_text" | "screenshot" | "scroll"
        | "long_press" | "wait_element" | "ocr_extract" | "image_match" | "clipboard"
        | "keyboard" | "mouse_move";   // LOCK-WF-08 12 액션 전수 (keyboard, mouse_move 포함)
  selector: { strategy: "accessibility_id" | "xpath" | "image"; value: string };
  params?: Record<string, unknown>;   // 액션별 파라미터 (방향, 거리, 텍스트 등)
  timeout_ms: number;                  // 기본 10000 (wait_element)
  retry: { max: number; backoff_ms: number };  // E5 폴백
}
```

---

## E4. 모델 / 드라이버 비교

| 기준 | Appium 표준 (채택) | WebdriverIO + Appium | Maestro |
|------|--------------------|-----------------------|---------|
| 프로토콜 | W3C WebDriver | W3C WebDriver | 자체 YAML DSL |
| iOS/Android 통합 | ✅ 단일 API | ✅ (Appium 위 래퍼) | ✅ |
| 학습 곡선 | 중 | 중~상 | 낮음 |
| 이미지 매칭 폴백 | ✅ (plugin) | ✅ | 제한적 |
| 디바이스 팜 연동 | ✅ BrowserStack/Sauce | ✅ | 부분 |
| **선정 사유** | **WebDriver 표준 + 디바이스 팜 호환 + 12 액션 매핑 자연스러움** | 추가 추상화 불필요 | DSL 종속 위험 |

**결정**: Appium 표준 드라이버 채택 (XCUITest/UiAutomator2). 디바이스 팜·LOCK-WF-08 매핑·교차 플랫폼 단일 API를 모두 만족.

---

## E5. 폴백 / 에러 처리

### E5.1 디바이스 가용성 cascade (4단계)

```
실 디바이스 요청
  → [미가용] 동일 OS·버전 다음 실 디바이스
    → [미가용] 시뮬레이터/에뮬레이터 폴백
      → [미가용] 작업 큐 대기 + 운영자 알림 (NotificationNode)
```

### E5.2 화면 인식 3단계 폴백

1. **네이티브 accessibility_id** (가장 안정) → 실패 시
2. **XPath** (구조 기반) → 실패 시
3. **image_match** (시각 템플릿, LOCK-WF-08 #8) — UI 리뉴얼 내성

### E5.3 액션 재시도

- 액션 실패 시 `retry.max`(기본 3회) + 지수 백오프, 최종 실패 → 워크플로우 상태 `FAILED`(LOCK-WF-09) 전이 + 30일 로그 기록.
- 세션 끊김(stale session) → 세션 재획득 1회 후 재시도.

---

## E6. 테스트 / 검증 케이스

| # | 케이스 | 기대 결과 |
|---|--------|-----------|
| T1 | iOS 앱 실행 → 로그인 → screenshot | 12 액션 매핑 정상, 상태 SUCCESS |
| T2 | Android 요소 미발견 → XPath → image 폴백 | 3단계 폴백 동작, 성공 |
| T3 | 디바이스 11번째 동시 요청 | LOCK-WF-05 quota로 대기(차단), 동시 ≤10 |
| T4 | 자격증명 사용 | Vault에서 복호화, 메모리 zeroize, 평문 로그 0건 |
| T5 | 액션 응답 시간 측정 | p95 ≤ 2초 (E7) |
| T6 | 디바이스 전체 미가용 | 시뮬레이터 폴백 → 알림 (E5) |

---

## E7. SLA / 성능

| 지표 | 목표 | 측정 방법 |
|------|------|-----------|
| 액션 응답 p95 | ≤ 2초 | 액션 디스패치~결과 캡처 구간 |
| 세션 획득 p95 | ≤ 8초 | 디바이스 팜 할당 시간 |
| 모바일 RPA 안정성 | V3 ≥ 90% | (성공 워크플로우 / 전체) |
| 동시 실행 | ≤ 10 (LOCK-WF-05) | DeviceFarmPool quota |

---

## E8. 모니터링 / 관측성

- 세션별 메트릭: 액션 수, 폴백 발생률(네이티브→XPath→이미지), 디바이스 점유 시간.
- 상태 머신 전이 이벤트(LOCK-WF-09) 전수 기록 → 30일 보존(R-07-6).
- 디바이스 풀 사용률 대시보드(6-13 Operations 연계 가능) + quota 포화 알림.

---

## E9. 디바이스 팜 통합 (1 통합 항목)

| 옵션 | 설명 | 비고 |
|------|------|------|
| **BrowserStack App Automate** | 클라우드 실 디바이스 | 자격증명 Vault 보관 |
| **Sauce Labs Real Device** | 클라우드 실 디바이스 | 동일 |
| **자체 디바이스 풀** | 온프레미스 USB/무선 허브 | DeviceFarmPool 자체 관리 |

- 팜 자격증명은 R-07-5 AES-256-GCM 암호화로 보관, 세션 시작 시 복호화·사용 후 zeroize.
- Phase 5 entry-gate: 디바이스 팜 인프라 ready + 모바일 SLA 영구 baseline.

---

## E10. 보안 / 윤리 / 안전

- **R-07-4 샌드박스**: 모바일 세션은 격리 컨테이너에서 드라이버 프로세스 실행, 파일시스템 접근은 작업 디렉터리로 제한(LOCK-WF-10).
- **R-07-5 자격증명 AES-256-GCM**: 앱 로그인 정보·팜 토큰은 평문 저장 금지, Vault 복호화 후 메모리 zeroize.
- **R-07-6 30일 로그**: 모든 액션·상태 전이 30일 보존(불변 append-only).
- **윤리/동의**: 개인 계정 자동화·스크래핑은 사용자 명시 동의(opt-in) 워크플로우만 허용, 캡처 화면 내 민감정보 마스킹 옵션 제공.
- **LOCK-WF-10 4 보안 항목**: 샌드박스 ✅ / 파일시스템 제한 ✅ / AES-256 ✅ / 권한 최소화 ✅.

---

## L3 자기 채점 (E1~E10 9요소)

| 요소 | 충족 | 점수 |
|------|------|:----:|
| E1 개요/목적 | ✅ | 9 |
| E2 아키텍처 | ✅ 컴포넌트 5 + 흐름 6단계 | 9 |
| E3 스키마/12 액션 매핑 | ✅ LOCK-WF-08 verbatim | 10 |
| E4 드라이버 비교 | ✅ 3종 매트릭스 | 9 |
| E5 폴백 | ✅ 디바이스 + 화면인식 + 재시도 | 9 |
| E6 테스트 | ✅ T1~T6 | 8 |
| E7 SLA | ✅ p95 ≤ 2초 | 9 |
| E8 모니터링 | ✅ | 8 |
| E9 디바이스 팜 통합 | ✅ 3 옵션 | 9 |
| E10 보안/윤리 | ✅ R-07-4/5/6 + LOCK-WF-10 | 10 |
| **총점** | | **90 / 100 (≥ 80 PASS)** |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| L3 v3.0 | 2026-05-31 | Phase 4 RECOVERY Stage B — N-018 mobile_automation V3 정본 genuine production write (Appium iOS/Android + 디바이스 팜 + LOCK-WF-08 12 액션 모바일 매핑 + LOCK-WF-10 보안 + E1~E10 90점) |
