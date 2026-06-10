# health_data_privacy.md — 건강 데이터 프라이버시

> **P-ID**: P-018, P-018-a
> **V단계**: V1
> **상태**: P-018 EXTEND / P-018-a NEW
> **L3 완성**: 2026-04-10
> **정본 소유자**: sot 2/3-6_Health-Wellness-EmotionAI/03_health-data/

---

## 교차 참조 블록

| 참조 문서 | 위치 | 참조 내용 |
|----------|------|----------|
| 종합계획서 §6.3 | P-018, P-018-a | 건강 데이터 프라이버시 + 3단계 등급 매핑 |
| 종합계획서 §3.4 | LOCK-HW-02/03/04/06 | LOCK 보호 값 |
| 종합계획서 부록 §A | §A.1~A.5 | 프라이버시 프레임워크 상세 |
| 상세명세 §4.2 | HealthKitSync.PRIVACY_CONFIG | 프라이버시 설정 명세 |
| STEP7-P | P-018 | 건강 데이터 프라이버시 원본 |
| AUTHORITY_CHAIN.md | §1~§5 | 정본 계층 및 충돌 해결 |
| ethics_framework.md | 06_ethics-privacy/ | PrivacyLevel/DataClassification 정의 원본 |
| activity_exercise.md | 동일 폴더 | ActivityDataPipeline 프라이버시 적용 |
| sleep_management.md | 동일 폴더 | SleepDataPipeline 프라이버시 적용 |
| nutrition_management.md | 동일 폴더 | NutritionDataPipeline 프라이버시 적용 |
| weight_body_composition.md | 동일 폴더 | WeightDataPipeline 프라이버시 적용 |
| work_health.md | 동일 폴더 | WorkHealthPipeline 프라이버시 적용 |

---

## 1. 개요

본 문서는 VAMOS 건강 데이터 프라이버시 정책의 L3 구현 정본이다. 프라이버시 3등급 체계(LOCK-HW-02), 데이터 보존 기간 TTL(LOCK-HW-03), AES-256-GCM 암호화 파이프라인(LOCK-HW-06)을 횡단 적용 가능한 구현 상세로 정의한다. 03_health-data 서브폴더의 모든 파일이 본 문서의 정책을 참조하여 프라이버시를 적용한다.

> **비의료 면책 (LOCK-HW-04)**: VAMOS는 의료 서비스가 아닙니다. 건강 데이터는 참고용으로 수집/관리되며, 의학적 판단이나 치료 결정의 근거로 사용할 수 없습니다.

---

## 2. LOCK 인용

> LOCK (LOCK-HW-02, 기존 명세 §1/P-018): 감정=PRIVATE(로컬전용), 건강=PROTECTED(AES-256+별도PIN), 의료=HIGHEST(외부전송절대금지)

> LOCK (LOCK-HW-03, 기존 명세 §4): 원시건강데이터 24시간TTL, 집계데이터 90일, 감정로그 사용자설정(기본180일)

> LOCK (LOCK-HW-04, STEP7-P 윤리원칙): "VAMOS는 의료 서비스가 아닙니다" 모든 건강 관련 응답에 포함

> LOCK (LOCK-HW-06, 기존 명세 §4): 건강 데이터 저장 시 AES-256-GCM 필수

---

## 3. 프라이버시 3등급 체계 (P-018, P-018-a)

### 3.1 등급 정의

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

class PrivacyLevel(Enum):
    """
    건강 데이터 프라이버시 등급 (LOCK-HW-02).
    
    ethics_framework.md §3.2에서 최초 정의.
    본 문서에서 건강 데이터 특화 구현 상세를 확장.
    """
    PRIVATE = "PRIVATE"      # 감정 데이터 — 로컬 전용, 외부 전송 금지
    PROTECTED = "PROTECTED"  # 건강 데이터 — AES-256 + 별도 PIN, 집계만 동의 시 공유
    HIGHEST = "HIGHEST"      # 의료 데이터 — 외부 전송 절대 금지, 격리 저장
```

### 3.2 등급별 상세 정책

```python
@dataclass
class PrivacyPolicy:
    """등급별 프라이버시 정책 상세"""
    level: PrivacyLevel
    storage_location: str
    encryption_algorithm: str
    encryption_key_type: str
    external_transfer: str
    retention_raw: str
    retention_aggregate: str
    access_control: str
    audit_logging: bool
    user_consent_required: bool
    deletion_method: str

PRIVACY_POLICIES = {
    PrivacyLevel.PRIVATE: PrivacyPolicy(
        level=PrivacyLevel.PRIVATE,
        storage_location="local_only",
        encryption_algorithm="AES-256-GCM",
        encryption_key_type="device_key",
        external_transfer="prohibited",
        retention_raw="user_setting_default_180d",
        retention_aggregate="user_setting_default_180d",
        access_control="user_only",
        audit_logging=True,
        user_consent_required=True,
        deletion_method="crypto_shredding",
    ),
    PrivacyLevel.PROTECTED: PrivacyPolicy(
        level=PrivacyLevel.PROTECTED,
        storage_location="local_preferred",
        encryption_algorithm="AES-256-GCM",
        encryption_key_type="user_pin_derived",
        external_transfer="summary_with_explicit_consent",
        retention_raw="24h_ttl",
        retention_aggregate="90d",
        access_control="user_only_with_pin",
        audit_logging=True,
        user_consent_required=True,
        deletion_method="crypto_shredding",
    ),
    PrivacyLevel.HIGHEST: PrivacyPolicy(
        level=PrivacyLevel.HIGHEST,
        storage_location="isolated_partition",
        encryption_algorithm="AES-256-GCM",
        encryption_key_type="master_key_with_pin",
        external_transfer="absolutely_prohibited",
        retention_raw="until_explicit_delete",
        retention_aggregate="until_explicit_delete",
        access_control="user_only_with_biometric_or_master_pin",
        audit_logging=True,
        user_consent_required=True,
        deletion_method="crypto_shredding_with_verification",
    ),
}
```

### 3.3 데이터 유형별 등급 분류

```python
HEALTH_DATA_CLASSIFICATION = {
    # PRIVATE (감정)
    "emotion_analysis": PrivacyLevel.PRIVATE,
    "mood_log": PrivacyLevel.PRIVATE,
    "stress_level": PrivacyLevel.PRIVATE,
    "emotion_journal": PrivacyLevel.PRIVATE,
    
    # PROTECTED (건강)
    "activity_exercise": PrivacyLevel.PROTECTED,
    "sleep_data": PrivacyLevel.PROTECTED,
    "nutrition_data": PrivacyLevel.PROTECTED,
    "weight_body": PrivacyLevel.PROTECTED,
    "work_health": PrivacyLevel.PROTECTED,
    "wellness_score": PrivacyLevel.PROTECTED,
    
    # HIGHEST (의료)
    "medical_records": PrivacyLevel.HIGHEST,
    "medication": PrivacyLevel.HIGHEST,
    "diagnosis_history": PrivacyLevel.HIGHEST,
    "lab_results": PrivacyLevel.HIGHEST,
}

class HealthDataClassifier:
    """
    건강 데이터 프라이버시 등급 분류기.
    
    분류 규칙 (종합계획서 부록 §A.1):
    1. 불명확 → 상위 등급 적용 (보수적)
    2. 복합 데이터 → 구성 요소 중 최고 등급
    3. 집계/익명화 → 원본 등급에서 최대 1단계 완화
    
    시간복잡도: O(k) — k=데이터 유형 수 (일반적 k < 5)
    """
    
    LEVEL_ORDER = [PrivacyLevel.PRIVATE, PrivacyLevel.PROTECTED, PrivacyLevel.HIGHEST]
    
    def classify(self, data_types: list[str]) -> PrivacyLevel:
        """
        복합 데이터의 프라이버시 등급 판정.
        최고 등급을 반환한다.
        """
        if not data_types:
            return PrivacyLevel.HIGHEST  # 규칙 1: 불명확 시 최고
        
        levels = []
        for dt in data_types:
            level = HEALTH_DATA_CLASSIFICATION.get(dt)
            if level is None:
                return PrivacyLevel.HIGHEST  # 미등록 유형 → 최고 등급
            levels.append(level)
        
        # 규칙 2: 최고 등급 반환
        return max(levels, key=lambda l: self.LEVEL_ORDER.index(l))
    
    def can_aggregate_downgrade(self, original_level: PrivacyLevel) -> PrivacyLevel:
        """
        집계/익명화 시 등급 완화 (최대 1단계).
        규칙 3: HIGHEST → PROTECTED 가능, PROTECTED → PRIVATE 가능, PRIVATE 유지.
        """
        # LOCK-HW-02: HIGHEST(의료)는 집계 후에도 외부전송 절대금지 — 등급 완화 금지 (HIGHEST 유지)
        if original_level == PrivacyLevel.HIGHEST:
            return PrivacyLevel.HIGHEST
        # LOCK-HW-02: HIGHEST(의료)는 집계 후에도 외부전송 절대금지 — 등급 완화 금지 (HIGHEST 유지)
        if original_level == PrivacyLevel.HIGHEST:
            return PrivacyLevel.HIGHEST
        idx = self.LEVEL_ORDER.index(original_level)
        if idx > 0:
            return self.LEVEL_ORDER[idx - 1]
        return original_level  # PRIVATE → PRIVATE (최하 유지)
```

---

## 4. 데이터 보존 기간 TTL 로직 (LOCK-HW-03)

```python
from datetime import datetime, timedelta

@dataclass
class RetentionPolicy:
    """데이터 보존 정책"""
    raw_ttl: timedelta
    aggregate_retention: timedelta
    description: str

RETENTION_POLICIES = {
    "raw_health": RetentionPolicy(
        raw_ttl=timedelta(hours=24),
        aggregate_retention=timedelta(days=90),
        description="LOCK-HW-03: 원시 건강 데이터 24h TTL, 집계 90일",
    ),
    "emotion_log": RetentionPolicy(
        raw_ttl=timedelta(days=180),      # 사용자 설정 기본값
        aggregate_retention=timedelta(days=180),
        description="LOCK-HW-03: 감정 로그 사용자 설정 (기본 180일)",
    ),
    "medical_record": RetentionPolicy(
        raw_ttl=timedelta(days=36500),    # 사용자 명시 삭제까지 (100년 = 사실상 무기한)
        aggregate_retention=timedelta(days=36500),
        description="사용자 명시적 삭제 요청까지 보존",
    ),
}

class TTLManager:
    """
    데이터 보존 기간(TTL) 관리.
    
    주기적으로 만료 데이터를 식별하고 삭제한다.
    삭제 시 Crypto-Shredding 적용 (암호화 키 삭제).
    
    시간복잡도: O(n) — n=검사 대상 레코드 수
    """
    
    async def check_and_purge(self, data_type: str) -> dict:
        """
        TTL 만료 데이터 식별 및 삭제.
        
        Returns:
            {
                "data_type": str,
                "checked_count": int,
                "expired_count": int,
                "purged_count": int,
                "purge_method": "crypto_shredding",
                "errors": list[str],
            }
        """
        policy = RETENTION_POLICIES.get(data_type)
        if not policy:
            raise ValueError(f"Unknown data type: {data_type}")
        
        now = datetime.utcnow()
        
        # 1. 만료 레코드 식별
        expired_records = await self._find_expired(data_type, policy.raw_ttl, now)
        
        # 2. Crypto-Shredding 삭제
        purged = 0
        errors = []
        for record_id in expired_records:
            try:
                await self._crypto_shred(record_id)
                purged += 1
            except Exception as e:
                errors.append(f"{record_id}: {str(e)}")
        
        return {
            "data_type": data_type,
            "checked_count": len(expired_records),
            "expired_count": len(expired_records),
            "purged_count": purged,
            "purge_method": "crypto_shredding",
            "errors": errors,
        }
    
    async def _find_expired(
        self, data_type: str, ttl: timedelta, now: datetime
    ) -> list[str]:
        """만료 레코드 ID 목록 조회"""
        ...
    
    async def _crypto_shred(self, record_id: str) -> None:
        """
        Crypto-Shredding: 암호화 키를 삭제하여 데이터를 복구 불가능하게 만든다.
        데이터 자체를 삭제하지 않아도 키 부재 시 복호화 불가.
        """
        ...
    
    async def user_delete_all(self, user_id: str) -> dict:
        """
        사용자 요청에 의한 전체 데이터 삭제 (GDPR Right to Erasure).
        
        1. 모든 데이터 유형의 암호화 키 삭제
        2. 원시 + 집계 데이터 물리 삭제
        3. 삭제 로그 기록 (메타데이터만, 내용 미포함)
        """
        results = {}
        for data_type in RETENTION_POLICIES:
            results[data_type] = await self._delete_user_data(user_id, data_type)
        
        return {
            "user_id": user_id,
            "deletion_results": results,
            "deletion_method": "crypto_shredding_with_physical_delete",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def _delete_user_data(self, user_id: str, data_type: str) -> dict:
        ...
```

---

## 5. AES-256-GCM 암호화 파이프라인 (LOCK-HW-06)

```python
import os
from dataclasses import dataclass

@dataclass
class EncryptionResult:
    """암호화 결과"""
    ciphertext: bytes
    nonce: bytes               # 12바이트 GCM nonce
    tag: bytes                 # 16바이트 인증 태그
    key_id: str                # 사용된 키 식별자
    algorithm: str = "AES-256-GCM"

class HealthDataEncryptor:
    """
    건강 데이터 AES-256-GCM 암호화/복호화.
    
    LOCK-HW-06: 모든 건강 데이터 저장 시 AES-256-GCM 필수.
    
    키 관리:
    - PRIVATE: device_key (기기 바인딩)
    - PROTECTED: user_pin_derived (PBKDF2 + PIN)
    - HIGHEST: master_key + PIN (이중 키)
    
    시간복잡도: O(n) — n=데이터 크기 (바이트)
    """
    
    KEY_DERIVATION = "PBKDF2-HMAC-SHA256"
    KEY_ITERATIONS = 600_000          # OWASP 2023 권장
    NONCE_SIZE = 12                    # GCM 표준 nonce 크기
    KEY_ROTATION_DAYS = 90             # 키 로테이션 주기
    
    def encrypt(
        self, plaintext: bytes, privacy_level: PrivacyLevel, user_pin: Optional[str] = None
    ) -> EncryptionResult:
        """
        프라이버시 등급에 따른 암호화.
        
        Args:
            plaintext: 평문 데이터
            privacy_level: 프라이버시 등급
            user_pin: 사용자 PIN (PROTECTED/HIGHEST 시 필수)
            
        Returns:
            EncryptionResult
            
        Raises:
            SecurityError: PIN 미제공 시 (PROTECTED/HIGHEST)
        """
        if privacy_level in (PrivacyLevel.PROTECTED, PrivacyLevel.HIGHEST):
            if not user_pin:
                raise SecurityError("PROTECTED/HIGHEST 등급은 PIN 필수")
        
        # 1. 키 획득
        key, key_id = self._get_or_derive_key(privacy_level, user_pin)
        
        # 2. Nonce 생성 (12바이트 랜덤)
        nonce = os.urandom(self.NONCE_SIZE)
        
        # 3. AES-256-GCM 암호화
        ciphertext, tag = self._aes_gcm_encrypt(key, nonce, plaintext)
        
        return EncryptionResult(
            ciphertext=ciphertext,
            nonce=nonce,
            tag=tag,
            key_id=key_id,
        )
    
    def decrypt(
        self, result: EncryptionResult, privacy_level: PrivacyLevel, user_pin: Optional[str] = None
    ) -> bytes:
        """
        복호화.
        
        Raises:
            SecurityError: 인증 태그 불일치 (변조 감지)
        """
        key, _ = self._get_or_derive_key(privacy_level, user_pin)
        plaintext = self._aes_gcm_decrypt(key, result.nonce, result.ciphertext, result.tag)
        return plaintext
    
    def _get_or_derive_key(
        self, privacy_level: PrivacyLevel, user_pin: Optional[str]
    ) -> tuple[bytes, str]:
        """
        등급별 키 획득/파생.
        
        PRIVATE: 기기 키스토어에서 획득
        PROTECTED: PIN + PBKDF2로 파생
        HIGHEST: 마스터 키 + PIN + PBKDF2로 파생
        """
        ...
    
    def _aes_gcm_encrypt(self, key: bytes, nonce: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
        """AES-256-GCM 암호화 (cryptography 라이브러리 사용)"""
        ...
    
    def _aes_gcm_decrypt(self, key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes) -> bytes:
        """AES-256-GCM 복호화 + 인증 태그 검증"""
        ...
    
    async def rotate_key(self, user_id: str, privacy_level: PrivacyLevel) -> dict:
        """
        키 로테이션 (90일 주기).
        
        1. 새 키 생성
        2. 모든 해당 등급 데이터 재암호화
        3. 구 키 삭제
        4. 로테이션 로그 기록
        """
        ...
```

---

## 6. 동의 관리

```python
@dataclass
class HealthDataConsent:
    """
    건강 데이터 수집 동의 관리.
    
    종합계획서 부록 §A.4 기반.
    각 데이터 유형별 개별 동의/거부 가능.
    """
    user_id: str
    consents: dict = field(default_factory=dict)  # {data_type: bool}
    updated_at: str = ""
    
    CONSENT_ITEMS = [
        {"key": "activity_exercise", "description": "활동/운동 데이터 수집", "level": "PROTECTED"},
        {"key": "sleep_data", "description": "수면 데이터 수집", "level": "PROTECTED"},
        {"key": "nutrition_data", "description": "영양 데이터 수집", "level": "PROTECTED"},
        {"key": "weight_body", "description": "체중/체성분 데이터 수집", "level": "PROTECTED"},
        {"key": "work_health", "description": "직장 건강 데이터 수집", "level": "PROTECTED"},
        {"key": "emotion_analysis", "description": "감정 분석 데이터 수집", "level": "PRIVATE"},
    ]
    
    def grant(self, data_type: str) -> None:
        """동의 부여"""
        self.consents[data_type] = True
        self.updated_at = datetime.utcnow().isoformat()
    
    def revoke(self, data_type: str) -> None:
        """
        동의 철회.
        즉시 해당 유형의 데이터 수집 중단.
        기존 데이터는 사용자 선택에 따라 삭제 또는 보존.
        """
        self.consents[data_type] = False
        self.updated_at = datetime.utcnow().isoformat()
    
    def is_consented(self, data_type: str) -> bool:
        """동의 여부 확인"""
        return self.consents.get(data_type, False)
```

---

## 7. 접근 제어

```python
class HealthDataAccessControl:
    """
    건강 데이터 접근 제어.
    
    원칙:
    1. 사용자 본인만 접근 가능 (LOCK-HW-02)
    2. PROTECTED 이상은 PIN/생체 인증 필수
    3. 외부 모듈 접근 차단 (R-09-7)
    4. 모든 접근 시도 로깅
    
    시간복잡도: O(1) per access check
    """
    
    ALLOWED_MODULES = {
        PrivacyLevel.PRIVATE: ["emotion_engine", "journal_module"],
        PrivacyLevel.PROTECTED: ["health_dashboard", "wellness_score", "vws_engine"],
        PrivacyLevel.HIGHEST: [],  # 어떤 외부 모듈도 접근 불가
    }
    
    def check_access(
        self,
        requester_module: str,
        data_type: str,
        user_authenticated: bool,
        pin_verified: bool = False,
    ) -> bool:
        """
        접근 권한 확인.
        
        Returns:
            True=접근 허용, False=차단
        """
        level = HEALTH_DATA_CLASSIFICATION.get(data_type)
        if level is None:
            return False  # 미등록 유형 차단
        
        # 사용자 인증 필수
        if not user_authenticated:
            self._log_access_denied(requester_module, data_type, "not_authenticated")
            return False
        
        # PROTECTED/HIGHEST는 PIN 필수
        if level in (PrivacyLevel.PROTECTED, PrivacyLevel.HIGHEST) and not pin_verified:
            self._log_access_denied(requester_module, data_type, "pin_not_verified")
            return False
        
        # HIGHEST는 외부 모듈 접근 절대 금지
        if level == PrivacyLevel.HIGHEST:
            self._log_access_denied(requester_module, data_type, "highest_external_blocked")
            return False
        
        # 허용 모듈 확인
        allowed = self.ALLOWED_MODULES.get(level, [])
        if requester_module not in allowed and requester_module != "user_direct":
            self._log_access_denied(requester_module, data_type, "module_not_allowed")
            return False
        
        self._log_access_granted(requester_module, data_type)
        return True
    
    def _log_access_denied(self, module: str, data_type: str, reason: str) -> None:
        """접근 거부 로그"""
        ...
    
    def _log_access_granted(self, module: str, data_type: str) -> None:
        """접근 허용 로그"""
        ...
```

---

## 8. R-01-7 중첩 JSON 로깅

```json
{
  "trace_id": "hlth-prv-{uuid}",
  "event": "privacy_policy_applied",
  "context": {
    "module": "health_data.health_data_privacy",
    "user_id": "{user_uuid}",
    "operation": "data_ingestion",
    "data_type": "activity_exercise"
  },
  "privacy": {
    "level": "PROTECTED",
    "encryption": "AES-256-GCM",
    "key_type": "user_pin_derived",
    "storage": "local_preferred",
    "external_transfer": "prohibited",
    "retention_raw": "24h",
    "retention_aggregate": "90d"
  },
  "consent": {
    "granted": true,
    "consent_timestamp": "2026-04-01T10:00:00Z"
  },
  "timestamp": "2026-04-10T09:00:00Z"
}
```

---

## 9. 에스컬레이션 페이로드

```python
@dataclass
class PrivacyEscalationPayload:
    """
    프라이버시 위반 에스컬레이션. I-20 경유 (R-01-8).
    """
    escalation_id: str           # "ESC-PRV-{uuid}"
    severity: str                # "P0" (프라이버시 위반은 항상 P0)
    violation_type: str          # "unauthorized_access" | "external_transfer" | "consent_violation"
    privacy_level_affected: str  # "PRIVATE" | "PROTECTED" | "HIGHEST"
    data_types_affected: list[str]
    detail: str
    evidence: dict
    timestamp: str
    auto_action_taken: str
    
    def to_i20_payload(self) -> dict:
        return {
            "source": "health-wellness-emotionai/health-data-privacy",
            "escalation_id": self.escalation_id,
            "severity": self.severity,
            "category": "privacy_violation",
            "detail": {
                "violation_type": self.violation_type,
                "privacy_level": self.privacy_level_affected,
                "data_types": self.data_types_affected,
                "description": self.detail,
            },
            "evidence_ref": self.evidence,
            "auto_action": self.auto_action_taken,
            "timestamp": self.timestamp,
        }
```

---

## 10. 예외 처리 정책 표

| error_code | 설명 | recoverable | 처리 |
|-----------|------|-------------|------|
| PRV-001 | 암호화 키 파생 실패 | YES | 재시도 3회, 실패 시 데이터 저장 거부 |
| PRV-002 | PIN 인증 실패 (3회 초과) | NO | 계정 잠금 15분 + 에스컬레이션 |
| PRV-003 | 비인가 모듈 접근 시도 | NO | 즉시 차단 + P0 에스컬레이션 |
| PRV-004 | 외부 전송 시도 (PRIVATE/HIGHEST) | NO | 즉시 차단 + P0 에스컬레이션 + 보안팀 알림 |
| PRV-005 | 키 로테이션 실패 | YES | 재시도 3회, 실패 시 긴급 키 갱신 + 관리자 알림 |
| PRV-006 | Crypto-Shredding 실패 | YES | 물리 삭제 폴백 + 에스컬레이션 |
| PRV-007 | 동의 없는 데이터 수집 | NO | 수집 즉시 중단 + 수집 데이터 삭제 + P0 |
| PRV-008 | TTL 만료 데이터 미삭제 | YES | 강제 삭제 실행 |
| PRV-009 | 복호화 태그 불일치 (변조 의심) | NO | 데이터 격리 + P0 에스컬레이션 |
| PRV-010 | 면책 문구 누락 | YES | 강제 삽입 |

---

## 11. Phase별 복구 전략

### Phase 1 (현재): 기본 복구

```
[프라이버시 위반 감지]
  → 즉시 차단 (접근/전송)
  → 로그 기록
  → P0 에스컬레이션
  → 영향 범위 파악
```

### Phase 2: 자동 복구 강화

```
[위반 감지]
  → 자동 격리 + 영향 범위 분석
  → 키 긴급 로테이션
  → 위반 패턴 학습 → 예방 규칙 갱신
```

### Phase 3: 예측 기반 예방

```
[사전 예측]
  → 접근 패턴 이상 감지 (ML)
  → 위반 가능성 사전 차단
  → 자동 감사 보고서
```

### 다운그레이드 시 confidence penalty 표

| 다운그레이드 상황 | penalty | 결과 |
|-----------------|---------|------|
| Phase 3 → Phase 2 | -0.1 | ML 예측 비활성, 규칙 기반만 |
| Phase 2 → Phase 1 | -0.2 | 자동 격리 비활성, 수동 대응 |
| Phase 1 → 긴급 모드 | -0.5 | 모든 건강 데이터 접근 차단, 읽기 전용 |

---

## 12. Phase 2 테스트 시나리오

| # | 시나리오 | 입력/조건 | 기대 결과 | 관련 LOCK |
|---|---------|----------|----------|----------|
| T-PRV-01 | PRIVATE 등급 분류 | 감정 분석 데이터 | level=PRIVATE, 로컬 전용 | HW-02 |
| T-PRV-02 | PROTECTED 등급 분류 | 활동 데이터 | level=PROTECTED, PIN 필요 | HW-02 |
| T-PRV-03 | HIGHEST 등급 분류 | 의료 기록 | level=HIGHEST, 외부 전송 금지 | HW-02 |
| T-PRV-04 | 복합 데이터 최고 등급 | 감정+건강 결합 | PROTECTED (최고 등급) | HW-02 |
| T-PRV-05 | AES-256-GCM 암호화 | 건강 데이터 저장 | 암호화 + 태그 생성 | HW-06 |
| T-PRV-06 | 복호화 태그 검증 | 정상 ciphertext | 정상 복호화 | HW-06 |
| T-PRV-07 | 변조 감지 | 태그 불일치 | SecurityError + 격리 | HW-06 |
| T-PRV-08 | 원시 TTL 24h | 24h 경과 | Crypto-Shredding 삭제 | HW-03 |
| T-PRV-09 | 집계 90일 보존 | 90일 경과 | 집계 삭제 | HW-03 |
| T-PRV-10 | 동의 철회 즉시 중단 | 활동 데이터 동의 OFF | 수집 즉시 중단 | - |
| T-PRV-11 | 비인가 모듈 접근 | marketing 모듈 → 건강 API | 차단 + P0 | HW-02 |
| T-PRV-12 | PIN 3회 실패 | 잘못된 PIN 3회 | 계정 잠금 15분 | - |
| T-PRV-13 | 키 로테이션 90일 | 90일 경과 | 자동 로테이션 + 재암호화 | HW-06 |
| T-PRV-14 | 전체 삭제 요청 (GDPR) | 사용자 전체 삭제 | 모든 키+데이터 삭제 | - |
| T-PRV-15 | 면책 문구 포함 | 건강 데이터 응답 | LOCK-HW-04 포함 | HW-04 |

---

## 13. 공통 자료 구조 선정의

| 클래스/Enum | 용도 | 참조 위치 |
|------------|------|----------|
| `PrivacyLevel` | 프라이버시 등급 3단계 | §3.1 (ethics_framework.md 원본) |
| `PrivacyPolicy` | 등급별 정책 상세 | §3.2 |
| `HEALTH_DATA_CLASSIFICATION` | 데이터 유형별 등급 | §3.3 |
| `HealthDataClassifier` | 등급 분류기 | §3.3 |
| `RetentionPolicy` | 보존 정책 | §4 |
| `TTLManager` | TTL 관리기 | §4 |
| `HealthDataEncryptor` | 암호화 엔진 | §5 |
| `HealthDataConsent` | 동의 관리 | §6 |
| `HealthDataAccessControl` | 접근 제어 | §7 |
| `PrivacyEscalationPayload` | 에스컬레이션 | §9 |

---

## 14. 세션 간 인터페이스 cross-check

| 인터페이스 | 제공 측 | 소비 측 | 상태 |
|-----------|--------|--------|------|
| `PrivacyLevel` | ethics_framework.md (원본), 본 문서 (확장) | 전 서브폴더 | V1 정의 완료 |
| `HEALTH_DATA_CLASSIFICATION` | 본 문서 | 전 health-data 파일 | V1 정의 완료 |
| `HealthDataEncryptor` | 본 문서 | 모든 DataPipeline 클래스 | V1 정의 완료 |
| `TTLManager` | 본 문서 | 모든 DataPipeline 클래스 | V1 정의 완료 |
| `HealthDataConsent` | 본 문서 | 모든 데이터 수집 모듈 | V1 정의 완료 |
| `HealthDataAccessControl` | 본 문서 | 모든 데이터 조회 모듈 | V1 정의 완료 |
| `PrivacyEscalationPayload` | 본 문서 | 에스컬레이션 엔진 | V1 정의 완료 |

---

> **문서 끝** — health_data_privacy.md V1 L3 완성 (2026-04-10)
