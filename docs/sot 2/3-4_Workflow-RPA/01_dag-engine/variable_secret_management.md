# 워크플로우 변수/시크릿 관리 — L3 상세 명세

> **N-ID**: N-008 (NEW)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 01_dag-engine
> **정본**: sot 2/3-4_Workflow-RPA/01_dag-engine/variable_secret_management.md

---

## 1. 개요

워크플로우 실행에 필요한 변수(Variable)와 시크릿(Secret)의 정의, 저장, 참조, 보안 관리를 정의한다. 노드 간 데이터 전달, 환경 변수, 전역 변수, 자격증명 암호화를 포함한다.

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 샌드박스 필수, 파일시스템 접근 제한, 자격증명 AES-256 암호화

---

## 2. 변수 체계

### 2.1 변수 유형

| 유형 | 스코프 | 설명 | 참조 문법 |
|------|--------|------|----------|
| **노드 출력** | 실행 단위 | 이전 노드 결과 참조 | `{{ nodes.<node_id>.output.<field> }}` |
| **워크플로우 변수** | 워크플로우 단위 | 실행 간 공유 데이터 | `{{ vars.<name> }}` |
| **환경 변수** | 전역 | API_KEY, DB_URL 등 | `{{ env.<name> }}` |
| **전역 변수** | 전역 | 모든 워크플로우 공유 | `{{ global_.<name> }}` |
| **트리거 입력** | 실행 단위 | 트리거가 전달한 데이터 | `{{ trigger.<field> }}` |
| **시스템 변수** | 실행 단위 | 실행 ID, 시작 시간 등 | `{{ system.<field> }}` |

### 2.2 변수 정의 스키마

```typescript
interface VariableDef {
  name: string;                      // 변수 이름 (영문, _, -)
  type: "string" | "number" | "boolean" | "object" | "array";
  scope: "workflow" | "environment" | "global";
  default_value?: any;               // 기본값
  description?: string;
  required: boolean;                 // 실행 시 필수 여부
  sensitive: boolean;                // 민감 데이터 여부 → true면 시크릿 처리
  validation?: {
    pattern?: string;                // regex 패턴
    min?: number;
    max?: number;
    enum?: any[];                    // 허용 값 목록
  };
}
```

### 2.3 변수 해석 엔진

```python
from jinja2 import Environment, StrictUndefined

class VariableResolver:
    """Jinja2 기반 변수 해석 — 노드 설정, 조건, 메시지 템플릿에서 사용."""

    def __init__(self):
        self._env = Environment(undefined=StrictUndefined)

    def resolve(self, template: str, context: VariableContext) -> any:
        """
        템플릿 문자열의 {{ }} 표현식을 실제 값으로 해석.
        context: nodes, vars, env, global, trigger, system 네임스페이스 포함.
        """
        jinja_template = self._env.from_string(template)
        return jinja_template.render(
            nodes=context.node_outputs,
            vars=context.workflow_variables,
            # env 네임스페이스 제거 — 임의 환경변수(API_KEY/DB_URL 등) 템플릿 노출 금지(LOCK-WF-10). 시크릿은 SecretRef 경로로만 접근.
            global_=context.global_variables,
            trigger=context.trigger_data,
            system=context.system_variables,
        )

    def resolve_node_config(self, config: dict, context: VariableContext) -> dict:
        """노드 config 내 모든 문자열 필드를 재귀적으로 해석."""
        resolved = {}
        for key, value in config.items():
            if isinstance(value, str) and "{{" in value:
                resolved[key] = self.resolve(value, context)
            elif isinstance(value, dict):
                resolved[key] = self.resolve_node_config(value, context)
            else:
                resolved[key] = value
        return resolved
```

### 2.4 시스템 변수 목록

| 변수 | 타입 | 설명 |
|------|------|------|
| `system.execution_id` | string | 현재 실행 ID |
| `system.workflow_id` | string | 워크플로우 ID |
| `system.workflow_name` | string | 워크플로우 이름 |
| `system.started_at` | string | 실행 시작 시각 (ISO 8601) |
| `system.current_node` | string | 현재 노드 ID |
| `system.iteration_index` | number | LoopNode 내 현재 반복 인덱스 |

---

## 3. 시크릿 관리

### 3.1 시크릿 저장

> LOCK (STEP7-N / 가이드 / LOCK-WF-10): 자격증명 AES-256 암호화

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class SecretStore:
    """시크릿 암호화 저장소 — AES-256-GCM 암호화."""

    def __init__(self, master_key: bytes):
        """master_key: 256-bit (32 bytes) 마스터 키."""
        assert len(master_key) == 32, "AES-256 requires 32-byte key"
        self._aesgcm = AESGCM(master_key)

    def store_secret(self, name: str, value: str, owner_id: str) -> SecretRef:
        """시크릿 암호화 후 저장."""
        nonce = os.urandom(12)
        plaintext = value.encode("utf-8")
        ciphertext = self._aesgcm.encrypt(nonce, plaintext, None)
        record = SecretRecord(
            name=name,
            owner_id=owner_id,
            ciphertext=ciphertext,
            nonce=nonce,
            algorithm="AES-256-GCM",
            created_at=datetime.utcnow(),
        )
        self._persist(record)
        return SecretRef(name=name, ref_id=record.id)

    def retrieve_secret(self, name: str, requester_id: str) -> str:
        """시크릿 복호화 — 권한 검증 후 반환."""
        record = self._load(name)
        if not self._check_access(record, requester_id):
            raise PermissionError(f"시크릿 '{name}' 접근 권한 없음")
        plaintext = self._aesgcm.decrypt(record.nonce, record.ciphertext, None)
        return plaintext.decode("utf-8")

    def delete_secret(self, name: str, owner_id: str) -> bool:
        """시크릿 삭제 — 소유자만 가능."""
        record = self._load(name)
        if record.owner_id != owner_id:
            raise PermissionError("소유자만 삭제 가능")
        self._delete(record)
        return True
```

### 3.2 시크릿 스키마

```typescript
interface SecretRecord {
  id: string;                        // UUID v7
  name: string;                      // 시크릿 이름 (예: "openai_api_key")
  owner_id: string;                  // 소유자 ID
  ciphertext: Uint8Array;            // AES-256-GCM 암호문
  nonce: Uint8Array;                 // 12-byte nonce
  algorithm: "AES-256-GCM";         // 암호화 알고리즘 (고정)
  created_at: string;                // ISO 8601
  updated_at: string;
  last_accessed_at?: string;
  access_policy: AccessPolicy;
}

interface AccessPolicy {
  allowed_workflows: string[];       // 접근 허용 워크플로우 ID (빈 배열 = 전체)
  allowed_nodes: string[];           // 접근 허용 노드 타입 (빈 배열 = 전체)
}
```

### 3.3 로그 마스킹

```python
class SecretMasker:
    """로그 출력 시 시크릿 값 자동 마스킹."""

    MASK = "***REDACTED***"

    def __init__(self, secret_store: SecretStore):
        self._known_secrets: set[str] = set()

    def register_secrets(self, secrets: list[str]):
        """현재 실행에서 사용되는 시크릿 값 등록."""
        self._known_secrets.update(secrets)

    def mask(self, text: str) -> str:
        """텍스트 내 시크릿 값을 마스킹."""
        for secret in self._known_secrets:
            if secret in text:
                text = text.replace(secret, self.MASK)
        return text

    def mask_dict(self, data: dict) -> dict:
        """딕셔너리 내 시크릿 키/값 재귀적 마스킹."""
        sensitive_keys = {"password", "secret", "token", "api_key", "credential"}
        masked = {}
        for key, value in data.items():
            if any(sk in key.lower() for sk in sensitive_keys):
                masked[key] = self.MASK
            elif isinstance(value, str):
                masked[key] = self.mask(value)
            elif isinstance(value, dict):
                masked[key] = self.mask_dict(value)
            else:
                masked[key] = value
        return masked
```

---

## 4. 변수/시크릿 관리 API

```python
class VariableSecretManager:
    """워크플로우 변수 + 시크릿 통합 관리."""

    async def set_variable(self, scope: str, name: str, value: any, var_def: VariableDef):
        """변수 설정 — sensitive=True이면 시크릿 저장소로 라우팅."""
        self._validate(value, var_def)
        if var_def.sensitive:
            await self._secret_store.store_secret(name, str(value), self._current_user)
        else:
            await self._variable_store.set(scope, name, value)

    async def get_variable(self, scope: str, name: str) -> any:
        """변수 조회 — 시크릿이면 복호화하여 반환."""
        var_def = await self._get_def(scope, name)
        if var_def and var_def.sensitive:
            return await self._secret_store.retrieve_secret(name, self._current_user)
        return await self._variable_store.get(scope, name)

    async def list_variables(self, scope: str) -> list[VariableSummary]:
        """변수 목록 조회 — 시크릿 값은 마스킹."""
        variables = await self._variable_store.list(scope)
        return [
            VariableSummary(
                name=v.name,
                type=v.type,
                value=self.MASK if v.sensitive else v.value,
                sensitive=v.sensitive,
            )
            for v in variables
        ]
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| L3 v1.0 | 2026-04-09 | Phase 1 1-1 — 변수 체계 6유형(노드출력/워크플로우/환경/전역/트리거/시스템), 시크릿 AES-256-GCM, 로그 마스킹, 변수 해석 엔진 |
