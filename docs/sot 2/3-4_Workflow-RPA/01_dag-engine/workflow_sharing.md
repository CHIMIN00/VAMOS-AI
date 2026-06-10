# 워크플로우 공유/내보내기 — L3 상세 명세

> **N-ID**: N-010 (NEW)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 01_dag-engine
> **정본**: sot 2/3-4_Workflow-RPA/01_dag-engine/workflow_sharing.md

---

## 1. 개요

워크플로우 정의의 내보내기(Export), 가져오기(Import), 공유 기능을 정의한다. V1은 JSON/YAML 내보내기 + 가져오기, V2에서 n8n 호환 내보내기, V3에서 커뮤니티 공유를 지원한다.

---

## 2. 내보내기 (Export)

### 2.1 지원 형식

| 형식 | V단계 | 설명 |
|------|:-----:|------|
| **VAMOS JSON** | V1 | VAMOS 네이티브 형식 — 모든 노드, 엣지, 변수, 메타데이터 보존 |
| **VAMOS YAML** | V1 | 사람이 읽기 쉬운 YAML 형식 |
| **n8n JSON** | V2 | n8n 호환 워크플로우 형식 (노드 타입 매핑 필요) |

### 2.2 Export 스키마

```typescript
interface ExportOptions {
  format: "vamos_json" | "vamos_yaml" | "n8n_json";
  include_secrets: boolean;          // false 권장 — true 시 경고
  include_history: boolean;          // 버전 이력 포함 여부
  version?: number;                  // 특정 버전 내보내기 (기본: 최신)
  sanitize: boolean;                 // 민감 정보 제거 (기본 true)
}

interface ExportResult {
  filename: string;                  // "{workflow_name}_v{version}.{ext}"
  format: string;
  content: string;                   // 직렬화된 워크플로우
  size_bytes: number;
  exported_at: string;
  warnings: string[];                // 시크릿 미포함 경고 등
}
```

### 2.3 Export 로직

```python
class WorkflowExporter:
    """워크플로우 내보내기."""

    async def export(
        self, workflow_id: str, options: ExportOptions
    ) -> ExportResult:
        workflow = await self._load_workflow(workflow_id, version=options.version)

        # 시크릿 처리
        if options.sanitize:
            workflow = self._sanitize_secrets(workflow)
        elif options.include_secrets:
            warnings = ["경고: 시크릿이 평문으로 포함됩니다. 안전한 채널로만 공유하세요."]
        else:
            workflow = self._remove_secret_values(workflow)

        # 형식별 직렬화
        if options.format == "vamos_json":
            content = json.dumps(self._to_vamos_schema(workflow), indent=2, ensure_ascii=False)
            ext = "json"
        elif options.format == "vamos_yaml":
            content = yaml.dump(self._to_vamos_schema(workflow), allow_unicode=True)
            ext = "yaml"
        elif options.format == "n8n_json":
            content = json.dumps(self._to_n8n_schema(workflow), indent=2)
            ext = "json"
        else:
            raise UnsupportedFormatError(f"지원하지 않는 내보내기 형식: {options.format}")
        # 주의: n8n_json은 export 전용(import 미지원) — 라운드트립 비대칭은 의도된 설계

        return ExportResult(
            filename=f"{workflow.name}_v{workflow.version}.{ext}",
            format=options.format,
            content=content,
            size_bytes=len(content.encode()),
        )

    def _sanitize_secrets(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """시크릿 참조를 플레이스홀더로 교체."""
        sanitized = deepcopy(workflow)
        for var_name, var_def in sanitized.variables.items():
            if var_def.sensitive:
                var_def.default_value = "<<SECRET_PLACEHOLDER>>"
        return sanitized
```

### 2.4 VAMOS Export 스키마

```json
{
  "vamos_version": "1.0",
  "exported_at": "2026-04-09T12:00:00Z",
  "workflow": {
    "id": "...",
    "name": "일일 보고서 자동 생성",
    "version": 3,
    "nodes": [
      {
        "id": "node_001",
        "type": "APINode",
        "name": "DART 공시 조회",
        "config": { "url": "https://opendart.fss.or.kr/...", "method": "GET" }
      }
    ],
    "edges": [
      { "source": "node_001", "target": "node_002" }
    ],
    "variables": { ... },
    "trigger": { "type": "time", "cron": "0 9 * * 1-5" }
  }
}
```

---

## 3. 가져오기 (Import)

### 3.1 Import 로직

```python
class WorkflowImporter:
    """워크플로우 가져오기 + 검증."""

    async def import_workflow(
        self, content: str, format: str, owner_id: str
    ) -> ImportResult:
        # 1. 파싱
        if format == "vamos_json":
            workflow = self._parse_vamos_json(content)
        elif format == "vamos_yaml":
            workflow = self._parse_vamos_yaml(content)
        else:
            raise UnsupportedFormatError(f"지원하지 않는 형식: {format}")

        # 2. 검증 (LOCK 제약 포함)
        validation = validate_workflow(workflow)
        if any(not r.valid for r in validation):
            return ImportResult(success=False, errors=validation)

        # 3. 충돌 검사 (동일 ID 존재 여부)
        existing = await self._workflow_store.get(workflow.id)
        if existing:
            workflow.id = generate_uuid_v7()  # 새 ID 할당

        # 4. 시크릿 플레이스홀더 처리
        missing_secrets = self._find_secret_placeholders(workflow)
        if missing_secrets:
            return ImportResult(
                success=True,
                workflow_id=workflow.id,
                requires_secrets=missing_secrets,
                message="시크릿 설정이 필요합니다.",
            )

        # 5. 저장
        workflow.metadata.owner_id = owner_id
        workflow.metadata.created_at = datetime.utcnow().isoformat()
        await self._workflow_store.save(workflow)

        return ImportResult(success=True, workflow_id=workflow.id)
```

### 3.2 Import 검증 체크리스트

| 검증 항목 | 설명 |
|-----------|------|
| 스키마 검증 | VAMOS Export 스키마 준수 여부 |
| 노드 타입 검증 | LOCK-WF-01 12 타입 범위 내 |
| 노드 수 검증 | LOCK-WF-02 최대 50개 |
| DAG 순환 검증 | LOCK-WF-04 순환 금지 |
| 시크릿 참조 확인 | 플레이스홀더 식별 → 사용자에게 재설정 요청 |
| 버전 호환성 | vamos_version 호환 여부 |

---

## 4. 공유 (V1: 파일 기반)

### 4.1 공유 방식

| 방식 | V단계 | 설명 |
|------|:-----:|------|
| **파일 다운로드** | V1 | JSON/YAML 파일로 다운로드 후 전달 |
| **공유 링크** | V1 | 만료 기한 있는 임시 다운로드 링크 생성 |
| **커뮤니티 마켓** | V3 | 공개 템플릿 마켓플레이스 |

### 4.2 공유 링크 스키마

```typescript
interface ShareLink {
  link_id: string;                   // UUID v7
  workflow_id: string;
  version: number;
  created_by: string;
  created_at: string;
  expires_at: string;                // 기본 7일
  access_count: number;
  max_access: number;                // 기본 100
  include_secrets: false;            // 공유 링크에서 시크릿 항상 제외
  password?: string;                 // 선택적 암호 보호 (bcrypt hash)
}
```

### 4.3 공유 링크 생성/조회

```python
class ShareLinkManager:
    DEFAULT_EXPIRY_DAYS = 7
    DEFAULT_MAX_ACCESS = 100

    async def create_link(
        self, workflow_id: str, version: int, user_id: str, password: str | None = None
    ) -> ShareLink:
        """만료 기한 있는 공유 링크 생성."""
        link = ShareLink(
            link_id=generate_uuid_v7(),
            workflow_id=workflow_id,
            version=version,
            created_by=user_id,
            expires_at=(datetime.utcnow() + timedelta(days=self.DEFAULT_EXPIRY_DAYS)).isoformat(),
            max_access=self.DEFAULT_MAX_ACCESS,
            include_secrets=False,
            password=bcrypt_hash(password) if password else None,
        )
        await self._link_store.save(link)
        return link

    async def access_link(self, link_id: str, password: str | None = None) -> ExportResult:
        """공유 링크를 통한 워크플로우 다운로드."""
        link = await self._link_store.get(link_id)
        if not link:
            raise LinkNotFoundError()
        if datetime.fromisoformat(link.expires_at) < datetime.utcnow():
            raise LinkExpiredError()
        if link.access_count >= link.max_access:
            raise LinkAccessLimitError()
        if link.password and not bcrypt_verify(password, link.password):
            raise InvalidPasswordError()

        link.access_count += 1
        await self._link_store.save(link)

        return await self._exporter.export(
            link.workflow_id,
            ExportOptions(format="vamos_json", sanitize=True, version=link.version),
        )
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| L3 v1.0 | 2026-04-09 | Phase 1 1-1 — JSON/YAML 내보내기, 가져오기+검증, 공유 링크 |
