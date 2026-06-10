# v12 컴포넌트 4건 구현 상세 — L3 명세

> **도메인**: 6-1_UI-UX-System / 04_react-components
> **세션**: P2-3 (Phase 2)
> **버전**: v1.0 (2026-04-26)
> **정본 출처**: Part2 §6.1.8 v12 추가 UI 컴포넌트 (L4664~L4671) / Part2 v23 추가 항목 (L2207~L2229) / 종합계획서 부록 A.2 (참조 ID D207-175/178/179 + S7NP-047/048)
> **종합계획서**: §7.3 P2-3 (L1652~L1685) / §6 ISS-4 (v12 4건 등록)
> **상위 SoT**: STEP7-C UI/UX 전수비교 작업가이드 (manifest L72 단일, 235 L)
> **선행**: 04_react-components/react_components_catalog.md (V1 1,715 L, LOCK L13 ~44개 10그룹 정본)

---

## 1. 개요

Part2 §6.1.8 v12 추가 UI 컴포넌트 4건 (스트레스 관리 / CBT 셀프케어 / 번아웃 예방 / 플래시카드 학습)을 L3 9요소(E1~E9) 수준으로 명세화하고, 04_react-components 카탈로그에 등록한다 (LOCK L13 ~44개 → 48개 확장 기록, **LOCK 정의 변경 없음 본문 카탈로그 append 만**).

**범위**: UI 레이어(6-1) — Props / State / Events / 렌더링 규칙 / 접근성. 감정 AI 모델 / 분석 알고리즘 / SM-2 Spaced Repetition 알고리즘은 3-6 Health-Wellness-EmotionAI 및 3-3 PKM-Knowledge-Management 소관 (참조만, LOCK-HW / LOCK-PKM 재정의 ❌).

**ISS-4 해결**: 본 V2 산출물 등록으로 ISS-4 (v12 추가 컴포넌트 관리 구조 없음) → RESOLVED 전환 (도메인 마감 step 7 cascade).

---

## 2. LOCK 참조 (4-field verbatim, AUTHORITY_CHAIN §4)

| LOCK ID | 항목 | 정본 출처 | LOCK 값 |
|---------|------|----------|---------|
| **L1** | UI 9-State | D2.0-08 §4.1 | UI_S0_BOOT, UI_S1_IDLE, UI_S2_EDITING, UI_S3_READY, UI_S4_RUNNING, UI_S5_AWAIT_APPROVAL, UI_S6_PRESENTING, UI_S7_RECOVERY, UI_S8_ARCHIVED (9개) |
| **L5** | ORANGE 테마색 | D2.0-08 §10.1 | #F97316 (ORANGE CORE) |
| **L6** | BLUE 테마색 | D2.0-08 §10.1 | #00F6FF (BLUE NODE) |
| **L7** | 다크모드 | D2.0-08 §10.1 / Part2 V1-P4 | 기본값 = Dark (#1E1E1E), Light는 토글 |
| **L8** | WCAG 접근성 | Part2 V1-P4 / §6.1.8 | WCAG 2.1 AA 준수 |
| **L13** | React 컴포넌트 수 | Part2 §6.1.2 | ~44개 (10그룹) |
| **L14** | Custom Hooks 수 | Part2 §6.1.3 | 8개 |
| **L17** | 상태 전이 지연 | D2.0-08 §4.4 | 최대 500ms |
| **L19** | 이벤트 네이밍 | D2.0-08 §5.1 | `ui.{layer}.{subject}.{action}` |

> **LOCK 정의 변경 0건** — L13 값 "~44개 (10그룹)"은 그대로 유지 (V2 P2-3 v12 4건 추가 → 48개로 확장 기록은 §11 변경 이력 + 본문 §3~§6 카탈로그 append 형태, LOCK 값 셀은 정본 verbatim). L14 값 "8개"도 그대로 유지 (V2 신규 Hooks 추가 0건 — v12 컴포넌트는 기존 Hook 재사용, footnote 분리). v12 4건은 카탈로그 본문에 추가만 (변경 이력 §11 명시), 11번째 그룹 신설 ❌ (10그룹 유지 해석: 기존 그룹에 v12 4건 추가 — 새 "Wellness/Learning" 카테고리 슬롯이 V3 범위로 평가).

> **L13 확장 기록 방식**: 본 V2 산출물 §3~§6에서 4 신규 컴포넌트 정의. 04_react-components/react_components_catalog.md V1 본문 변경 ❌ (P2-4 에서 V2 참조 섹션 append 형태로 처리, 본 P2-3 산출물은 NEW 파일).

---

## 3. v12 #1 — 스트레스 관리 UI (D207-175)

### 3.1 출처 (Part2 §6.1.8 L4668 정본 인용)

> 1 | **스트레스 관리 UI** | BreathingGuide 컴포넌트(4-7-8 호흡법 타이머), GroundingExercise(5-4-3-2-1 감각), MeditationTimer(가이드 명상 오디오 연동) | D207-175

> Part2 v23 §6.1.8 L2207 정본: "스트레스 관리 (호흡/그라운딩/명상)" [HIGH] | v10 Phase 2 추가 (D207-175)

### 3.2 컴포넌트 구성 (3 sub-component)

#### 3.2.1 `<BreathingGuide>` (4-7-8 호흡법)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { mode: "478" \| "box" \| "custom" = "478", cycles: number = 4, autoStart?: boolean, onComplete?: (summary: BreathingSummary) => void } |
| **E2 State** | UI_S2_EDITING (사용자 설정) → UI_S4_RUNNING (호흡 진행 4-7-8 타이머: 4초 들이마심 / 7초 참기 / 8초 내쉬기) → UI_S6_PRESENTING (완료 요약). 전이 ≤ 500ms (LOCK L17) |
| **E3 Output** | 시각적 호흡 원 (확대/축소) + 단계 라벨 + 카운트다운. 완료 시 `BreathingSummary { cycles_completed, total_seconds, hr_change?: number }` |
| **E4 Class/API** | `<BreathingGuide mode="478" cycles={4} onComplete={fn} />`. 3-6 Health-Wellness 인터페이스 — 심박수 변화 측정은 3-6 LOCK-HW 소관 (재정의 ❌, 본 컴포넌트는 onComplete 콜백으로 데이터 패스스루) |
| **E5 Style** | 호흡 원 ORANGE #F97316 (들이마심) / BLUE #00F6FF (내쉬기) / 회색 (참기). 다크 배경 #1E1E1E (LOCK L7). reduce-motion 사용자 설정 시 원 애니메이션 → 텍스트만 표시 |
| **E6 Accessibility** | aria-live="polite" 단계 안내 ("4초 들이마시세요"). 청각 장애 사용자: 시각 진행 + 햅틱 (지원 시). WCAG 2.1 AA 대비 ≥ 4.5:1 (LOCK L8) |
| **E7 Error** | `INVALID_MODE` → 기본 "478" fallback. 사용자 중도 종료 시 `onCancel()` 호출 + 부분 요약 보존 |
| **E8 Test** | unit: 4-7-8 단계 타이밍 (jest fake timers). integration: cycles=4 → 4×(4+7+8)=76초 진행. e2e: reduce-motion 토글 시 정적 텍스트 모드 |
| **E9 Event** | `ui.wellness.breathing.started` / `.cycle_completed` / `.completed` / `.cancelled` (LOCK L19) |

#### 3.2.2 `<GroundingExercise>` (5-4-3-2-1 감각 그라운딩)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { senses?: string[] = ["sight", "touch", "hearing", "smell", "taste"], inputMode: "text" \| "voice" = "text" } |
| **E2 State** | UI_S2_EDITING (각 단계 입력) — 5-4-3-2-1 진행 (5 sight / 4 touch / 3 hearing / 2 smell / 1 taste). 단계별 사용자 입력 후 다음 |
| **E3 Output** | `GroundingResult { entries: { sense, count, items: string[] }[], total_seconds }` (5+4+3+2+1=15 entries 전체) |
| **E4 Class/API** | `<GroundingExercise inputMode="text" />`. 음성 모드는 P2-1 `<VoiceToTextPanel>` 재사용 |
| **E5 Style** | 5단계 진행 바 ORANGE → BLUE 그라데이션. 각 단계 카드 (다크 #1E1E1E + ORANGE 보더 #F97316). 입력 폼 standard input |
| **E6 Accessibility** | 키보드 Tab 단계별 이동, Enter 다음 단계. 스크린리더 단계별 안내 ("5가지 보이는 것을 입력하세요") |
| **E7 Error** | 사용자 입력 누락 (count 미달) 시 "최소 1개 이상 입력" 인라인 메시지. 음성 모드 STT 실패 시 텍스트 모드 전환 |
| **E8 Test** | unit: 5-4-3-2-1 카운트 검증. integration: text → voice 모드 전환. e2e: 전체 5단계 완료 시 GroundingResult 구조 검증 |
| **E9 Event** | `ui.wellness.grounding.started` / `.sense_completed` / `.completed` (LOCK L19) |

#### 3.2.3 `<MeditationTimer>` (가이드 명상 오디오 연동)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { duration_seconds: number = 600, audio_url?: string, voice_guide_locale: "ko" \| "en" \| "ja" = "ko" } |
| **E2 State** | UI_S4_RUNNING (재생 + 카운트다운) ↔ UI_S2_EDITING (일시정지). 종료 시 UI_S6_PRESENTING (완료 메시지) |
| **E3 Output** | `MeditationSession { duration_completed, paused_count, audio_played }` |
| **E4 Class/API** | `<MeditationTimer duration_seconds={600} voice_guide_locale="ko" />`. 오디오 재생은 P1 `<AudioPlayer>` 재사용 (LOCK L16 i18n ko-KR / en-US / ja-JP) |
| **E5 Style** | 중앙 원형 타이머 (BLUE #00F6FF 진행 호). 다크 배경 #1E1E1E. 일시정지/종료 ORANGE #F97316 버튼 |
| **E6 Accessibility** | aria-label 분당 진행률 안내 "9분 남음". 음성 가이드 자막 토글 (청각 보조). reduce-motion 시 호 애니메이션 → 숫자만 |
| **E7 Error** | 오디오 로드 실패 → 무음 타이머로 진행 + 경고 토스트. 백그라운드 진입 시 자동 일시정지 |
| **E8 Test** | unit: 카운트다운 정확도. integration: pause/resume. e2e: 600초 완료 시 onComplete 호출 |
| **E9 Event** | `ui.wellness.meditation.started` / `.paused` / `.resumed` / `.completed` (LOCK L19) |

### 3.3 3-6 Health-Wellness-EmotionAI 인터페이스 (참조만)

```typescript
// 6-1 측 인터페이스 정의 — 3-6 LOCK-HW 재정의 ❌
interface WellnessSessionData {
  session_type: "breathing" | "grounding" | "meditation";
  duration_seconds: number;
  completion_status: "completed" | "cancelled" | "partial";
  user_id: string;
  // 감정 데이터 분석 / 스트레스 지표 계산은 3-6 EmotionAI 소관
  // 6-1은 onComplete 콜백을 통해 익명화된 세션 데이터를 3-6 으로 패스스루만
}
```

---

## 4. v12 #2 — CBT 셀프케어 UI (D207-178)

### 4.1 출처 (Part2 §6.1.8 L4669 정본 인용)

> 2 | **CBT 셀프케어 UI** | ThoughtRecord 폼(상황/자동사고/감정/증거/대안사고), CognitiveDistortionDetector(12종 인지왜곡 패턴 매칭), ProgressChart | D207-178

### 4.2 컴포넌트 구성 (3 sub-component)

#### 4.2.1 `<ThoughtRecord>` (사고 기록 폼)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { initialEntry?: Partial<ThoughtRecordEntry>, onSave: (entry: ThoughtRecordEntry) => Promise<void> } |
| **E2 State** | UI_S2_EDITING (5필드 입력: 상황 / 자동사고 / 감정 0-100 / 증거 / 대안사고) → UI_S5_AWAIT_APPROVAL (저장 확인) → UI_S6_PRESENTING (저장 완료 요약) |
| **E3 Output** | `ThoughtRecordEntry { situation, automatic_thought, emotions: { name, intensity_0_100 }[], evidence_for, evidence_against, alternative_thought, distortions_detected: DistortionType[], created_at }` |
| **E4 Class/API** | `<ThoughtRecord onSave={asyncFn} />`. 저장은 6-4 Memory-RAG-Storage 인터페이스 (참조만, 6-4 LOCK-MR 재정의 ❌) |
| **E5 Style** | 5단계 step-form (lo-fi wizard 패턴). 단계별 진행 바 ORANGE #F97316. 감정 강도 슬라이더 BLUE #00F6FF |
| **E6 Accessibility** | 각 step 의 textarea 에 명시적 label + aria-describedby 도움말 ("상황을 객관적 사실로 기술하세요"). Tab 순회 명확 |
| **E7 Error** | 필수 필드 누락 시 인라인 검증 메시지. 저장 실패 시 로컬 임시 저장 + 재시도 버튼 |
| **E8 Test** | unit: 5필드 폼 검증. integration: onSave async 모의. e2e: 전체 폼 → ThoughtRecordEntry 구조 검증 |
| **E9 Event** | `ui.cbt.thought_record.started` / `.field_updated` / `.saved` / `.save_failed` (LOCK L19) |

#### 4.2.2 `<CognitiveDistortionDetector>` (12종 인지왜곡 패턴 매칭)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { thought_text: string, locale?: "ko" \| "en" \| "ja" = "ko" } |
| **E2 State** | UI_S4_RUNNING (분석 중) → UI_S6_PRESENTING (감지된 왜곡 표시). ≤ 500ms (LOCK L17) |
| **E3 Output** | `Array<DistortionMatch>` — 12종 중 0~다수 — { type: DistortionType, confidence: 0~1, highlighted_phrase: string, suggestion: string } |
| **E4 Class/API** | `<CognitiveDistortionDetector thought_text={text} />`. 12종 패턴 분류는 3-6 EmotionAI 모델 소관 (참조만, LOCK-HW 재정의 ❌). 6-1은 표시만 |
| **E5 Style** | 왜곡 카드 12종 ORANGE 헤더 (예: "흑백사고", "과잉일반화", "감정적 추론"). hovered 시 BLUE 강조 highlight |
| **E6 Accessibility** | 각 왜곡 항목 expand/collapse, 키보드 Enter 토글. role="list" / role="listitem" 적용 |
| **E7 Error** | 분석 모델 연결 실패 → "분석 실패, 수동 검토 권장" + 12종 정의 정적 목록 표시 |
| **E8 Test** | unit: DistortionType enum 12 종. integration: 모의 thought_text → 0/1/다수 매칭. visual: 카드 레이아웃 1280×720 |
| **E9 Event** | `ui.cbt.distortion.analyzed` / `.match_clicked` / `.suggestion_applied` (LOCK L19) |

> **12종 인지왜곡 정의** (Part2 §6.1.8 L4669 인용 — 3-6 EmotionAI 정본 보존, 6-1은 화면 표시만):
> 1. 흑백사고 (All-or-Nothing) / 2. 과잉일반화 / 3. 정신적 여과 / 4. 긍정 무시 / 5. 결론 비약 / 6. 확대/축소 / 7. 감정적 추론 / 8. 당위적 사고 / 9. 명명/오명 / 10. 개인화 / 11. 비난 / 12. 마법적 사고

#### 4.2.3 `<ProgressChart>` (진행 추적 차트)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { entries: ThoughtRecordEntry[], date_range: "week" \| "month" \| "year" = "month", metric: "emotion_intensity" \| "distortion_count" = "emotion_intensity" } |
| **E2 State** | UI_S6_PRESENTING (차트 렌더링) |
| **E3 Output** | 시각적 라인 차트 + 통계 요약 (평균 감정 강도, 자주 등장한 왜곡 Top-3) |
| **E4 Class/API** | `<ProgressChart entries={list} date_range="month" />`. P1 `<ChartRenderer>` 재사용 (Mermaid + Plotly) |
| **E5 Style** | x축 시간 / y축 강도 0-100. ORANGE 라인 (감정), BLUE 영역 (이동 평균 7일). 다크 배경 #1E1E1E |
| **E6 Accessibility** | role="img" + aria-label 차트 요약 텍스트. 데이터 테이블 view 토글 (시각 보조) |
| **E7 Error** | entries 빈 배열 시 "데이터 없음" empty state 표시 |
| **E8 Test** | unit: date_range 필터 / metric 분기. integration: 30일 entries → 라인 차트 렌더링 |
| **E9 Event** | `ui.cbt.progress_chart.shown` / `.range_changed` (LOCK L19) |

---

## 5. v12 #3 — 번아웃 예방 UI (D207-179, S7NP-047 보강)

### 5.1 출처 (Part2 §6.1.8 L4670 정본 인용)

> 3 | **번아웃 예방 UI** | WorkloadMonitor(일일 활동 패턴 분석), ForcedBreakOverlay(과도 업무 감지 시 강제 휴식), ActivityHeatmap(주간 패턴 시각화) | D207-179

> Part2 v23 §6.1.8 L2208 정본: "번아웃 예방 (과도업무감지→중단)" [HIGH] | v10 Phase 2 추가 (D207-179)

### 5.2 컴포넌트 구성 (3 sub-component)

#### 5.2.1 `<WorkloadMonitor>` (일일 활동 패턴 분석)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { activity_log: ActivityLogEntry[], threshold_hours: number = 8, refresh_interval_seconds: number = 300 } |
| **E2 State** | UI_S6_PRESENTING (대시보드 표시) — 5분 (default) 마다 갱신 |
| **E3 Output** | `WorkloadStatus { current_hours_today, weekly_total_hours, burnout_index_0_100, recommendation: "ok" \| "take_break" \| "stop" }` |
| **E4 Class/API** | `<WorkloadMonitor activity_log={log} threshold_hours={8} />`. 번아웃 지수 계산은 3-6 EmotionAI 알고리즘 (참조만, LOCK-HW 재정의 ❌) |
| **E5 Style** | 게이지 바 (ORANGE 0-50% / 노랑 50-80% / 빨강 80-100%). 주간 누적 BLUE #00F6FF |
| **E6 Accessibility** | 게이지 색상 + 숫자 + 패턴 (3중 표기, 색약 사용자 고려, LOCK L8) |
| **E7 Error** | 활동 로그 데이터 부재 → "데이터 부족, 더 많은 사용 후 표시" empty state |
| **E8 Test** | unit: burnout_index 임계값 분기. integration: refresh_interval 5분 mock |
| **E9 Event** | `ui.wellness.workload.refreshed` / `.threshold_exceeded` (LOCK L19) |

#### 5.2.2 `<ForcedBreakOverlay>` (강제 휴식 오버레이)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { trigger_burnout_index: number = 80, break_duration_minutes: number = 15, dismissible: boolean = false } |
| **E2 State** | UI_S5_AWAIT_APPROVAL (강제 휴식 모달 표시) — 사용자 인터랙션 차단. break_duration_minutes 후 자동 해제 |
| **E3 Output** | `BreakSession { triggered_at, duration_minutes, dismissed: boolean, dismiss_reason?: string }` |
| **E4 Class/API** | `<ForcedBreakOverlay trigger_burnout_index={80} break_duration_minutes={15} />`. 백그라운드 작업 (저장 / 동기화) 은 계속 진행, UI 만 차단 |
| **E5 Style** | 풀스크린 다크 오버레이 #1E1E1E + 80% opacity. 중앙 카드: "잠시 쉬어가세요. 15분 휴식이 권장됩니다." ORANGE #F97316 헤더 |
| **E6 Accessibility** | Esc 로 모달 종료 허용 (WCAG 2.1 SC 2.1.2 No Keyboard Trap 준수, LOCK L8). 강제 휴식은 dismissible=false 로 UI '건너뛰기' 버튼만 비활성화하여 강제 (Esc 차단 아님). aria-modal="true". 시각/청각 다중 안내 |
| **E7 Error** | dismissible=true 인 경우 사용자가 "건너뛰기" 가능 (이유 입력 필수: "긴급 작업" / "데드라인" / "기타") — 익명 통계 누적 |
| **E8 Test** | unit: 카운트다운 정확도. integration: dismissible=false 시 Esc 비활성. e2e: 15분 후 자동 해제 |
| **E9 Event** | `ui.wellness.forced_break.shown` / `.dismissed` / `.completed` (LOCK L19) |

#### 5.2.3 `<ActivityHeatmap>` (주간 패턴 시각화)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { activity_log: ActivityLogEntry[], weeks: number = 12 } |
| **E2 State** | UI_S6_PRESENTING |
| **E3 Output** | 7×24 히트맵 격자 (요일 × 시간), 최근 N주 누적 |
| **E4 Class/API** | `<ActivityHeatmap activity_log={log} weeks={12} />` |
| **E5 Style** | 히트맵 ORANGE 그라데이션 (저 → 고). 주말 라벨 BLUE 차별. 다크 배경 |
| **E6 Accessibility** | role="img" + aria-label 요약. 셀 hover 툴팁 + 키보드 탐색 |
| **E7 Error** | 데이터 부재 → "최소 1주 사용 후 표시" empty state |
| **E8 Test** | unit: 7×24 격자 렌더링. integration: 12주 데이터 누적 |
| **E9 Event** | `ui.wellness.heatmap.shown` (LOCK L19) |

---

## 6. v12 #4 — 플래시카드 학습 UI (S7NP-047/048)

### 6.1 출처 (Part2 §6.1.8 L4671 정본 인용)

> 4 | **플래시카드/간격반복 교육 UI** | FlashcardEditor(앞/뒤 카드 편집), SM2ReviewEngine(SuperMemo-2 간격 계산), ReviewDashboard(복습 예정/통계/성취도) | S7NP-047/048

> Part2 v23 §6.1.8 L2228 "플래시카드 자동 생성" [HIGH] (S7NP-047) / L2229 "간격 반복 (Spaced Repetition)" [HIGH] (S7NP-048)

### 6.2 컴포넌트 구성 (3 sub-component)

#### 6.2.1 `<FlashcardEditor>` (앞/뒤 카드 편집)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { initialCard?: Partial<Flashcard>, onSave: (card: Flashcard) => Promise<void>, decks: Deck[] } |
| **E2 State** | UI_S2_EDITING (전면/후면 텍스트 / 이미지 첨부) → UI_S6_PRESENTING (저장 완료 미리보기) |
| **E3 Output** | `Flashcard { id, deck_id, front: { text, image_url?, audio_url? }, back: { text, image_url?, audio_url? }, tags: string[], created_at }` |
| **E4 Class/API** | `<FlashcardEditor onSave={asyncFn} decks={decks} />`. 저장은 6-4 Memory-RAG-Storage 또는 3-3 PKM (참조만, 재정의 ❌) |
| **E5 Style** | 카드 flip 애니메이션 (전면 ↔ 후면). 전면 ORANGE #F97316 헤더, 후면 BLUE #00F6FF 헤더 |
| **E6 Accessibility** | flip 키보드 단축키 (Space). 화면 낭독 시 양면 텍스트 모두 안내. reduce-motion 시 즉시 전환 |
| **E7 Error** | 빈 텍스트 + 이미지 + 오디오 모두 부재 시 저장 비활성. 이미지 업로드 실패 시 텍스트만 저장 |
| **E8 Test** | unit: front/back 입력 검증. integration: 이미지 첨부. e2e: 카드 생성 → onSave 호출 |
| **E9 Event** | `ui.education.flashcard.editing` / `.saved` / `.save_failed` (LOCK L19) |

#### 6.2.2 `<SM2ReviewEngine>` (SuperMemo-2 간격 계산)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { card: Flashcard, prevState: SM2State, onReview: (next: SM2State) => Promise<void> } |
| **E2 State** | UI_S2_EDITING (사용자 평가: Again / Hard / Good / Easy 4단계) → UI_S6_PRESENTING (다음 복습 일자 표시) |
| **E3 Output** | `SM2State { ease_factor, interval_days, repetition_count, next_review_at, last_grade: 0\|1\|2\|3\|4\|5 }` |
| **E4 Class/API** | `<SM2ReviewEngine card={card} prevState={state} onReview={asyncFn} />`. **SM-2 알고리즘 정본은 3-3 PKM-Knowledge-Management 도메인** (LOCK-PKM 정본, 본 6-1은 인터페이스 참조만, **재정의 ❌**) |
| **E5 Style** | 평가 4 버튼: Again 빨강 / Hard 노랑 / Good ORANGE / Easy BLUE. 다음 복습 카운트다운 표시 |
| **E6 Accessibility** | 키보드 단축키 1=Again / 2=Hard / 3=Good / 4=Easy. 음성 안내 옵션 |
| **E7 Error** | onReview 실패 → 로컬 임시 저장 + 재시도. 알고리즘 결과 비정상 (interval<0) 시 재계산 |
| **E8 Test** | unit: SM-2 공식 검증 (interval_days 계산). integration: 4 평가 분기. e2e: 복습 시퀀스 1주 시뮬레이션 |
| **E9 Event** | `ui.education.review.shown` / `.graded` / `.next_scheduled` (LOCK L19) |

> **SM-2 알고리즘 인터페이스 (3-3 PKM 정본 — 재정의 ❌, 인터페이스만)**:
> ```typescript
> interface SM2Algorithm {
>   // 3-3 도메인이 정본 소유 (LOCK-PKM 재정의 ❌)
>   computeNext(prev: SM2State, grade: 0|1|2|3|4|5): SM2State;
>   // 6-1은 호출 인터페이스만 정의 — 실제 구현은 3-3 (또는 backend 서비스)
> }
> ```

#### 6.2.3 `<ReviewDashboard>` (복습 예정/통계/성취도)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input Props** | { user_id: string, time_range: "today" \| "week" \| "month" = "today" } |
| **E2 State** | UI_S6_PRESENTING |
| **E3 Output** | `ReviewStats { due_today, completed_today, retention_rate_7days, retention_rate_30days, deck_progress: { deck_id, mastery_pct }[] }` |
| **E4 Class/API** | `<ReviewDashboard user_id={uid} time_range="today" />`. P1 `<ChartRenderer>` 재사용 |
| **E5 Style** | 카드 4 개 통계 (오늘 예정 / 완료 / 7일 보유율 / 30일 보유율). 덱별 진행률 BLUE 진행 바 |
| **E6 Accessibility** | 통계 카드 aria-label "오늘 예정 23개 카드". 차트 데이터 테이블 view 토글 |
| **E7 Error** | 데이터 0건 시 "첫 카드를 만들어 시작하세요" empty state + CTA 버튼 |
| **E8 Test** | unit: time_range 필터. integration: 통계 계산 |
| **E9 Event** | `ui.education.review_dashboard.shown` / `.range_changed` (LOCK L19) |

---

## 7. LOCK L13 카탈로그 확장 기록 (~44개 → 48개)

> **변경 방식**: 기존 10그룹 (Decision/Chat/Approval/Cost/Evidence/Memory/Node/Flow/Guardrails/Input/Navigation/기타) 위에 v12 4건 추가. 11번째 그룹 신설 ❌ (P2-3 신규 카테고리는 V3 평가 시점 결정).

### 7.1 v12 4건 카탈로그 entry (04_react-components/react_components_catalog.md V2 append 대상)

| # | 컴포넌트 | sub-components | 그룹 분류 (V2 잠정) | LOCK 매핑 |
|---|----------|----------------|---------------------|-----------|
| 45 | **스트레스 관리 UI** (D207-175) | BreathingGuide / GroundingExercise / MeditationTimer | "기타 (Wellness 잠정)" | L1 / L5 / L6 / L7 / L8 / L19 |
| 46 | **CBT 셀프케어 UI** (D207-178) | ThoughtRecord / CognitiveDistortionDetector / ProgressChart | "기타 (Wellness 잠정)" | L1 / L5 / L6 / L7 / L8 / L17 / L19 |
| 47 | **번아웃 예방 UI** (D207-179) | WorkloadMonitor / ForcedBreakOverlay / ActivityHeatmap | "기타 (Wellness 잠정)" | L5 / L6 / L7 / L8 / L19 |
| 48 | **플래시카드 학습 UI** (S7NP-047/048) | FlashcardEditor / SM2ReviewEngine / ReviewDashboard | "기타 (Education 잠정)" | L5 / L6 / L7 / L8 / L19 |

> **합계**: V1 ~44개 + v12 4건 = **48개**. 그룹 11번째 신설 검토는 V3 범위 (Wellness / Education 카테고리 정식화).

> **LOCK L13 정의 무변경**: "~44개 (10그룹)" 정의 그대로. v12 4건은 본 V2 산출물에서 sub-component 9개 (3+3+3+3=12개 sub) 기준으로 카탈로그 본문 append (P2-4 단계).

---

## 8. 3-6 / 3-3 cross-domain 인터페이스 매트릭스 (참조만, 재정의 ❌)

| 6-1 측 컴포넌트 | 외부 도메인 | 인터페이스 | 정본 소유 |
|----------------|-------------|-----------|-----------|
| `<BreathingGuide>` | 3-6 EmotionAI | onComplete 콜백 → 익명화된 `WellnessSessionData` 패스스루 | 3-6 LOCK-HW 재정의 ❌ |
| `<GroundingExercise>` | 3-6 EmotionAI | 동상 | 3-6 LOCK-HW 재정의 ❌ |
| `<MeditationTimer>` | 3-6 EmotionAI | 동상 | 3-6 LOCK-HW 재정의 ❌ |
| `<ThoughtRecord>` | 3-6 EmotionAI / 6-4 Memory-RAG-Storage | 저장 인터페이스 / 분석 인터페이스 | 3-6 (분석) / 6-4 (저장) — 재정의 ❌ |
| `<CognitiveDistortionDetector>` | 3-6 EmotionAI | 12종 분류 모델 호출 인터페이스 | 3-6 LOCK-HW 재정의 ❌ |
| `<ProgressChart>` | (없음 — 6-1 자체 렌더링) | — | — |
| `<WorkloadMonitor>` | 3-6 EmotionAI | burnout_index 계산 인터페이스 | 3-6 LOCK-HW 재정의 ❌ |
| `<ForcedBreakOverlay>` | (없음 — 6-1 자체 렌더링) | — | — |
| `<ActivityHeatmap>` | (없음 — 6-1 자체 렌더링) | — | — |
| `<FlashcardEditor>` | 6-4 Memory-RAG-Storage / 3-3 PKM | 저장 인터페이스 | 6-4 / 3-3 재정의 ❌ |
| `<SM2ReviewEngine>` | 3-3 PKM | SM-2 알고리즘 호출 인터페이스 (computeNext) | 3-3 LOCK-PKM 정본, 재정의 ❌ |
| `<ReviewDashboard>` | 6-4 / 3-3 | 통계 조회 인터페이스 | 6-4 / 3-3 재정의 ❌ |

> **본 §8 가 정의하지 않는 것**: SM-2 alpha factor 알고리즘 (3-3 LOCK-PKM 정본) / 12 인지왜곡 분류 모델 정확도 (3-6) / burnout_index 계산식 (3-6 LOCK-HW).

---

## 9. STEP7-C 상위 SoT 매핑 (P2-3 범위)

| STEP7-C 항목 ID | 출처 (235L) | V2 P2-3 매핑 |
|-----------------|-------------|--------------|
| (STEP7-C 본문에는 v12 4건 직접 항목 없음 — Part2 §6.1.8 v12 정본 직접 인용) | — | §3~§6 전 본문 (v12 정본 = Part2 §6.1.8) |

> **upstream baseline**: STEP7-C `9c7b4ea26c2d1d1d6cf32eaa8089e41ee5a16ce913c6f3cb4eed1e1b0f11f709` (235 L) UNCHANGED. **본 P2-3 산출물의 1차 정본 출처는 Part2 §6.1.8** (manifest L72 STEP7-C 단일 upstream 외에 6-1 내부 AUTHORITY 체인 4문서 1 = Part2).

---

## 10. Phase 배정 및 의존성

| 항목 | 값 |
|------|-----|
| **Phase 배정** | Phase 2 (V2 v12 컴포넌트 4건 추가) |
| **Phase 1 의존성** | react_components_catalog.md (V1 ~44개 정본), custom_hooks.md (8 Hooks), zustand_stores.md (7 Stores) |
| **Phase 3 이월** | "Wellness" / "Education" 11번째 그룹 신설 평가, v12 4건 → 3-6 EmotionAI 모델 통합 시점 추가 sub-component |
| **교차 도메인** | 3-6 Health-Wellness-EmotionAI (cross-ref 1, 인터페이스 명세만) / 3-3 PKM (SM-2 인터페이스만) / 6-4 Memory-RAG-Storage (저장 인터페이스만) |

---

## 11. 검증 (§7.3 P2-3 검증 항목 4/4 충족)

- [x] **v12 4건 각각 L3 9요소 (E1~E9) 프레임 포함**: §3 (3 sub) / §4 (3 sub) / §5 (3 sub) / §6 (3 sub) = 12 sub-components 전수
- [x] **ISS-4 해결**: 본 NEW 산출물 + §7 카탈로그 확장 기록으로 04_react-components 등록 명시화
- [x] **3-6 Health-Wellness-EmotionAI 연동 인터페이스 명시**: §3.3 `WellnessSessionData` + §8 cross-domain 매트릭스 (재정의 ❌)
- [x] **LOCK L13 (~44개 컴포넌트) → 48개 확장 기록**: §7 카탈로그 entry 표 + §2 LOCK 정의 변경 0건 명시

---

## 12. 변경 이력

| 일자 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-26 | v1.0 | NEW (P2-3) — v12 4건 (D207-175 / D207-178 / D207-179 / S7NP-047/048) L3 9요소 × 12 sub-components 전수. ISS-4 RESOLVED 대상. LOCK L13 ~44 → 48 확장 기록 (정의 변경 0). 3-6/3-3/6-4 cross-ref 인터페이스만 (재정의 ❌) |

<!-- END OF DOCUMENT -->
