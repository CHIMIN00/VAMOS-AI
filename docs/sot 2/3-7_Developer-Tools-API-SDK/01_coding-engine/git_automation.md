# Git 작업 자동화

> **L-ID**: L-008
> **V 배정**: V1 (즉시 구현)
> **Phase**: Phase 1 P1-1
> **수준**: L2 (D1 + D2 + D3)
> **의존 LOCK**: 없음

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|----------|----------|
| STEP7-L L-008 | Git 작업 자동화 구현 상세 |
| L-001 dev_node_architecture.md | 코딩 엔진 아키텍처 |

---

## D1. Input Schema

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class GitOperation(Enum):
    COMMIT_MESSAGE = "commit_message"
    BRANCH_CREATE = "branch_create"
    PR_DESCRIPTION = "pr_description"
    MERGE_CONFLICT = "merge_conflict"
    CHERRY_PICK = "cherry_pick"
    RELEASE_NOTES = "release_notes"

@dataclass
class GitAutomationRequest:
    """Git 자동화 요청"""
    operation: GitOperation
    repo_path: str
    staged_diff: Optional[str] = None       # COMMIT_MESSAGE 시
    issue_title: Optional[str] = None       # BRANCH_CREATE 시
    conflict_files: list[str] = field(default_factory=list)  # MERGE_CONFLICT 시
    commit_range: Optional[str] = None      # RELEASE_NOTES 시 (v1.0..v1.1)
    use_gitmoji: bool = False               # 이모지 옵션
    conventional_commits: bool = True       # Conventional Commits 형식
    trace_id: Optional[str] = None
```

---

## D2. Output Schema

```python
@dataclass
class GitAutomationResponse:
    """Git 자동화 응답"""
    status: str
    result: str                             # 생성된 메시지/브랜치명/설명
    alternatives: list[str] = field(default_factory=list)  # 대안 제안
    applied: bool = False                   # 자동 적용 여부
    latency_ms: float = 0.0
    trace_id: Optional[str] = None
```

---

## D3. Algorithm

```
시간복잡도: O(D + L)
  D: diff 분석 O(N) — N=변경 라인 수
  L: LLM 생성 O(T) — T=출력 토큰
```

```python
async def automate_git(request: GitAutomationRequest) -> GitAutomationResponse:
    """
    Git 작업 자동화 파이프라인.
    ABC 패턴: DiffAnalyzer → MessageGenerator → Applier
    """
    if request.operation == GitOperation.COMMIT_MESSAGE:
        # 1. diff 분석 → 변경 요약
        summary = analyze_diff(request.staged_diff)
        # 2. Conventional Commits 형식 메시지 생성
        message = await generate_commit_message(
            summary, request.conventional_commits, request.use_gitmoji
        )
        return GitAutomationResponse(status="success", result=message)
    
    elif request.operation == GitOperation.BRANCH_CREATE:
        branch_name = generate_branch_name(request.issue_title)
        return GitAutomationResponse(status="success", result=branch_name)
    
    elif request.operation == GitOperation.PR_DESCRIPTION:
        desc = await generate_pr_description(request.repo_path, request.commit_range)
        return GitAutomationResponse(status="success", result=desc)
    
    elif request.operation == GitOperation.MERGE_CONFLICT:
        resolution = await resolve_merge_conflict(request.conflict_files)
        return GitAutomationResponse(status="success", result=resolution)
    
    elif request.operation == GitOperation.RELEASE_NOTES:
        notes = await generate_release_notes(request.repo_path, request.commit_range)
        return GitAutomationResponse(status="success", result=notes)
    
    elif request.operation == GitOperation.CHERRY_PICK:
        result = await automate_cherry_pick(request.repo_path, request.commit_range)
        return GitAutomationResponse(status="success", result=result)
    
    else:
        raise ValueError(f"Unsupported GitOperation: {request.operation}")
    
    elif request.operation == GitOperation.CHERRY_PICK:
        result = await automate_cherry_pick(request.repo_path, request.commit_range)
        return GitAutomationResponse(status="success", result=result)
    
    else:
        raise ValueError(f"Unsupported GitOperation: {request.operation}")
```

---

## D4. Error Handling

| 에러 코드 | recoverable | 처리 |
|-----------|-------------|------|
| E_NOT_GIT_REPO | No | 에러 메시지 반환 |
| E_NO_STAGED | Yes | unstaged 변경 사항 안내 |
| E_CONFLICT_COMPLEX | Yes | 수동 해결 안내 + 부분 제안 |

---

## D5. Dependencies

| 의존성 | 용도 |
|--------|------|
| gitpython >= 3.1 | Git 저장소 접근 |
| LLM API | 메시지/설명 생성 |

---

## D6. Performance

| 메트릭 | 목표 |
|--------|------|
| 커밋 메시지 생성 | < 3초 |
| PR 설명 생성 | < 10초 |
| 머지 충돌 해결 제안 | < 15초 |

---

## D7. Test Spec — Phase 2 테스트 시나리오

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T1 | 커밋 메시지 생성 | staged_diff="함수 추가" | "feat: add ..." 형식 |
| T2 | gitmoji 커밋 | use_gitmoji=True | ":sparkles: feat: ..." |
| T3 | 브랜치명 생성 | issue="Fix login bug #42" | "fix/42-login-bug" |
| T4 | PR 설명 | commit_range="main..feature" | 변경 요약 포함 |
| T5 | 머지 충돌 | 2파일 충돌 시나리오 | 해결 제안 코드 |
| T6 | 릴리스 노트 | v1.0..v1.1 커밋 | 기능/버그 분류 노트 |
| T7 | 비Git 디렉토리 | .git 없는 경로 | E_NOT_GIT_REPO |
| T8 | 빈 diff | staged_diff="" | "chore: empty commit" 안내 |
| T9 | 대형 diff | 1000줄+ 변경 | 요약 후 정상 생성 |
| T10 | 복잡한 충돌 | 3-way 충돌 | 부분 해결 + 수동 안내 |

---

## D8. Security

- 커밋 메시지/PR 설명에 시크릿 값 마스킹
- .gitignore에 민감 파일 패턴 자동 확인
