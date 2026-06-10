# 의존성 관리

> **L-ID**: L-031
> **V 배정**: V1 (즉시 구현)
> **Phase**: Phase 1 P1-1
> **수준**: L2 (D1 + D2 + D3)
> **의존 LOCK**: 없음

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|----------|----------|
| STEP7-L L-031 | 의존성 관리 구현 상세 |
| L-039 security_automation.md | CVE 체크 연동 |

---

## D1. Input Schema

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class DependencyOperation(Enum):
    VULNERABILITY_SCAN = "vulnerability_scan"
    LICENSE_CHECK = "license_check"
    UNUSED_DETECT = "unused_detect"
    UPDATE_CHECK = "update_check"
    CONFLICT_RESOLVE = "conflict_resolve"
    AUTO_UPDATE = "auto_update"

@dataclass
class DependencyRequest:
    """의존성 관리 요청"""
    operation: DependencyOperation
    project_root: str
    package_manager: str              # "pip", "npm", "cargo"
    manifest_file: Optional[str] = None  # requirements.txt, package.json
    auto_apply: bool = False          # 자동 적용 여부
    trace_id: Optional[str] = None
```

---

## D2. Output Schema

```python
@dataclass
class VulnerabilityInfo:
    """취약점 정보"""
    package: str
    version: str
    cve_id: str
    severity: str                  # "critical", "high", "medium", "low"
    fix_version: Optional[str] = None

@dataclass
class DependencyResponse:
    """의존성 관리 응답"""
    status: str
    vulnerabilities: list[VulnerabilityInfo] = field(default_factory=list)
    license_issues: list[dict] = field(default_factory=list)
    unused_packages: list[str] = field(default_factory=list)
    available_updates: list[dict] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    applied_changes: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    trace_id: Optional[str] = None
```

---

## D3. Algorithm

```
시간복잡도: O(P * C)
  P: 패키지 수
  C: CVE DB 조회 O(log(N)) per package
```

```python
async def manage_dependencies(request: DependencyRequest) -> DependencyResponse:
    """
    의존성 관리 파이프라인.
    ABC 패턴: Scanner → Analyzer → Resolver
    """
    manifest = load_manifest(request.project_root, request.package_manager)
    
    if request.operation == DependencyOperation.VULNERABILITY_SCAN:
        vulns = await scan_vulnerabilities(manifest, request.package_manager)
        return DependencyResponse(status="success", vulnerabilities=vulns)
    
    elif request.operation == DependencyOperation.LICENSE_CHECK:
        issues = check_license_compatibility(manifest)
        return DependencyResponse(status="success", license_issues=issues)
    
    elif request.operation == DependencyOperation.UNUSED_DETECT:
        unused = detect_unused_packages(
            request.project_root, manifest
        )
        return DependencyResponse(status="success", unused_packages=unused)
    
    elif request.operation == DependencyOperation.UPDATE_CHECK:
        updates = await check_available_updates(manifest)
        return DependencyResponse(status="success", available_updates=updates)
    
    elif request.operation == DependencyOperation.AUTO_UPDATE:
        # 보안 패치만 자동 (마이너), 메이저는 영향 분석 후
        applied = await auto_apply_security_patches(manifest)
        return DependencyResponse(status="success", applied_changes=applied)
    
    elif request.operation == DependencyOperation.CONFLICT_RESOLVE:
        conflicts = await resolve_version_conflicts(manifest, request.package_manager)
        return DependencyResponse(status="success", conflicts=conflicts)
    
    else:
        raise ValueError(f"Unsupported DependencyOperation: {request.operation}")
    
    elif request.operation == DependencyOperation.CONFLICT_RESOLVE:
        conflicts = await resolve_version_conflicts(manifest, request.package_manager)
        return DependencyResponse(status="success", conflicts=conflicts)
    
    else:
        raise ValueError(f"Unsupported DependencyOperation: {request.operation}")
```

---

## D4. Error Handling

| 에러 코드 | recoverable | 처리 |
|-----------|-------------|------|
| E_MANIFEST_NOT_FOUND | No | 매니페스트 파일 경로 안내 |
| E_CVE_DB_UNAVAILABLE | Yes | 캐시된 DB로 스캔 |
| E_UPDATE_CONFLICT | Yes | 충돌 해결 제안 |

---

## D5. Dependencies

| 의존성 | 용도 |
|--------|------|
| pip-audit | Python CVE 스캔 |
| npm audit | Node.js CVE 스캔 |

---

## D6. Performance

| 메트릭 | 목표 |
|--------|------|
| 취약점 스캔 | < 15초 |
| 라이선스 체크 | < 5초 |
| 미사용 감지 | < 10초 |

---

## D7. Test Spec — Phase 2 테스트 시나리오

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T1 | CVE 감지 | 취약한 패키지 포함 | vulnerabilities 비어있지 않음 |
| T2 | GPL 라이선스 | MIT 프로젝트 + GPL 의존성 | license_issues 감지 |
| T3 | 미사용 패키지 | import 없는 패키지 | unused_packages 목록 |
| T4 | 업데이트 확인 | 구버전 패키지 | available_updates 목록 |
| T5 | 자동 패치 | auto_apply=True | 마이너 패치 적용 |
| T6 | 메이저 업데이트 | 메이저 버전 변경 가능 | 영향 분석 포함 |
| T7 | npm 프로젝트 | package.json | npm audit 결과 |
| T8 | pip 프로젝트 | requirements.txt | pip-audit 결과 |
| T9 | 충돌 해결 | 버전 충돌 | 호환 버전 제안 |
| T10 | 매니페스트 없음 | 빈 프로젝트 | E_MANIFEST_NOT_FOUND |

---

## D8. Security

- CVE DB는 24시간 주기로 갱신
- 자동 업데이트는 테스트 통과 후에만 적용
