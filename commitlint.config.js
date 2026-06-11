// VAMOS 커밋 메시지 규칙 (Phase 2-5 — STRATEGY_09 §3 도구 표의 커밋 린터; §8 vamos_lint 범위 아님)
// 포맷 정본: PART1 §D.4 커밋 컨벤션 — type(scope): subject
//   예: feat(I-1): implement Intent Detector with IntentFrame schema
//       fix(I-5): correct Gate evaluation order (Policy > Approval > Cost > Evidence)
// 주의: 한국어 Phase 체크포인트 커밋("Phase 2-N: ...")은 문서 단계 한정 — 코드 커밋은 본 규칙 적용.
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'test', 'docs', 'refactor', 'chore', 'perf', 'ci', 'build', 'revert'],
    ],
    'subject-empty': [2, 'never'],
    'type-empty': [2, 'never'],
    // scope: 모듈 ID(I-1~I-25, E-#, S-#...) 또는 영역명(schemas, ipc, config 등) — 자유 형식 허용
    'scope-case': [0],
    'subject-case': [0],
    'header-max-length': [2, 'always', 100],
  },
};
