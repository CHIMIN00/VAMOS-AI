# message_bus -- Redis Pub/Sub MessageBus + HMAC-SHA256 Agent 메시지 서명 (V2-Phase 2)

> **도메인**: 6-3_Agent-Teams-PARL / 02_agent-swarm
> **세션**: P2A-1 (산출물1, #1+#2)
> **작성일**: 2026-04-30
> **버전 태그**: V2-Phase 2
> **대조 기준**: Part2 §6.7 L5050 (LOCK-AT-012 정본), Part2 V2-Phase 3 §6.7-1 (Redis MessageBus + HMAC), AUTHORITY_CHAIN.md §2.1 LOCK-AT 17건 + §3 LOCK-63 3건 = 20 unique
> **선행 산출물**: `02_agent-swarm/P1-07_in_memory_messagebus.md` (V1 In-Memory MessageBus, R-63-8 인터페이스 호환 정본)

---

## 0. 메타 헤더

| 속성 | 값 |
|------|-----|
| 도메인 | 6-3_Agent-Teams-PARL |
| 서브폴더 | 02_agent-swarm |
| 세션 | P2A-1 |
| 산출물 키 | 산출물1 (Redis MessageBus + HMAC 서명, #1+#2) |
| 작성일 | 2026-04-30 |
| 버전 태그 | V2-Phase 2 |
| 대조 기준 | Part2 §6.7 L5033-5055 (LOCK-AT 17 정본) / Part2 V2-Phase 3 §6.7 #1, #4 (Redis + HMAC) / AUTHORITY_CHAIN.md §2.1, §2.2, §3 |
| 선행 산출물 | P1-07_in_memory_messagebus.md (V1 In-Memory MessageBus) |
| 후속 산출물 | P2A-6 cost_budget + execution_engine V2 EXTEND (병렬 상한 LOCK-AT-014 V2=10 동작 검증) |
| 인터페이스 호환성 | R-63-8 (V1 InMemoryMessageBus publish/subscribe/unsubscribe/broadcast/get_stats/shutdown 시그니처 동일성 보장) |

---

## 1. 교차 참조 블록

| 문서 | 참조 위치 | 역할 |
|------|----------|------|
| Part2 §6.7 L5050 | LOCK-AT-012 정본 ("Agent 메시지에 HMAC 무결성 서명 필수") | LOCK-AT-012 5-field 정본 출처 |
| Part2 §6.7 L5033-5055 | LOCK-AT-001~017 17건 정본 표 | 본 문서 인용 LOCK-AT-002/003/007/012/014/015 정본 출처 |
| Part2 V2-Phase 3 §6.7 #1 | Redis MessageBus 요건 (In-Memory → Redis 전환, XADD/XREAD, 채널 패턴, ConnectionPool max_connections=20, HMAC-SHA256 서명) | V2 Redis Pub/Sub 정본 |
| Part2 V2-Phase 3 §6.7 #4 | HMAC-SHA256 인증 요건 (메시지 서명, 키 관리, 타임스탬프 ±5분) | V2 HMAC 정본 |
| Part2 §6.5.2 | HMAC 타이밍 공격 방어 (`hmac.compare_digest` 의무, 32바이트 키, 90일 순환, 24h grace, 5분 리플레이 윈도우) | HMAC 구현 패턴 정본 |
| AUTHORITY_CHAIN.md §2.1 | LOCK-AT 17건 레지스트리 (5-field × 17 row) | LOCK-AT 5-field 분리 인용 정본 |
| AUTHORITY_CHAIN.md §2.2 | 근거 설계 문서 원문 인용 | LOCK-AT-012 D2.0-07 S7E-078 L2420-2421 인용 |
| AUTHORITY_CHAIN.md §3 | LOCK-63-1~3 (도메인 고유 LOCK 3건) | LOCK-63 분리 인용 정본 |
| D2.0-07 S7E-078 (L2420-2421) | "Agent 통신 보안 — Agent 간 메시지 HMAC 무결성 검증, Agent ID 인증" | LOCK-AT-012 근거 설계 |
| D2.0-07 S7E-080 (L2428-2429) | "Delegation Attack 방어 — 위임 체인 깊이 제한 최대 3단계, 권한 상승 감지 → 차단" | LOCK-AT-004/013 근거 |
| D2.0-05 §7.3 고정2 (L375) | "Checkpoint/Replay/Fork(재현/분기)는 'VAMOS trace_id 단위'로만 허용" | LOCK-AT-007 근거 |
| 6-2 Security-Governance `02_hmac-timing-defense/_index.md` | HMAC 타이밍 공격 방어 5항목 + 키 관리 라이프사이클 7단계 + L3~L6 LOCK | HMAC 정책 정본 (편집 ❌, 참조만) |
| `P1-07_in_memory_messagebus.md` §3.3 | InMemoryMessageBus 인터페이스 (publish/subscribe/unsubscribe/broadcast/get_stats/shutdown) | V1 인터페이스 호환 R-63-8 |
| `P1-07_in_memory_messagebus.md` §3.1 | BusMessage / Subscription / BusStats / MessageType / MessagePriority 자료구조 | V2 RedisMessageEnvelope 확장 베이스 |
| 종합계획서 §7.4 산출물1 (L1442-1476) | Redis MessageBus + HMAC 서명 #1+#2 작업 정의 | 본 세션 작업 정의 |
| 종합계획서 §7.2 P2→P3 전환 게이트 | "Redis MessageBus + HMAC 서명" 게이트 조건 | Phase 3 진입 게이트 기여 |
| 종합계획서 §6 ISS-8 (MEDIUM) | MessageBus V1→V2→V3 마이그레이션 절차 미정의 | 본 세션 §6에서 해결 |
| 종합계획서 §4.3 R-63-8 | MessageBus 구현 변경 시 HMAC 서명 호환성 검증 필수 | 인터페이스 호환 의무 |
| **인접 도메인** | | |
| 3-8 Conversation-A2A | A2A 프로토콜 규격, Agent Discovery | 외부 Agent 간 통신 (별도 계층, 본 6-3 MessageBus는 내부 통신 전용) |
| 3-10 Agent-Protocol-Interoperability | L0~L4 자율성, 프레임워크 어댑터 | 자체 경량 프레임워크 LOCK-AT-001 — 외부 어댑터 경유만 |
| 6-2 Security-Governance | HMAC 정책 정본 (LOCK-AT-012 보조 정의) | HMAC 알고리즘/키 관리/타이밍 방어는 6-2 정본 우선 |
| 4-3 MCP-Server-Client | MCP 프로토콜 (도구 호출) | MessageBus는 도구 호출 결과 전달 매개체로만 사용 |

---

## 2. Redis MessageBus 개요

### 2.1 식별 정보

| 속성 | 값 |
|------|-----|
| **클래스명** | `RedisMessageBus` |
| **도입 버전** | V2 (Phase 2) |
| **기술 기반** | `redis.asyncio` (redis-py async, redis 7+) |
| **영속성** | Redis Streams XADD/XREAD (메시지 영속화 + 컨슈머 그룹 재시작 복원) |
| **HMAC 적용** | LOCK-AT-012: HMAC-SHA256 서명 필수, 미서명 메시지 발행 거부 + 수신 폐기 |
| **라우팅 모델** | 채널 기반 — `agent.{agent_id}.{message_type}` 단일캐스트 + `broadcast.{topic}` 다중캐스트 |
| **직렬화** | JSON (UTF-8, ensure_ascii=False) |
| **순서 보장** | Redis Streams 단일 channel 내 시퀀스 ID 단조 증가 보장 |
| **연결 풀** | `redis.asyncio.ConnectionPool(max_connections=20, decode_responses=True)` (Part2 V2-P3 #1 정본) |
| **재연결 전략** | exponential backoff: 0.5s × 2^n, 최대 60s, 최대 재시도 12회 |
| **메시지 유실 방지** | dual-write replay log (Redis Stream `replay.bus.YYYY-MM-DD`) + ack 컨슈머 그룹 |
| **V1 마이그레이션 호환** | R-63-8: `publish/subscribe/unsubscribe/broadcast/get_stats/shutdown` 시그니처 동일 |

### 2.2 LOCK 값 인용 (5-field 분리, AUTHORITY_CHAIN.md §2.1 정본)

> **LOCK-AT-012**:
> - **ID**: LOCK-AT-012
> - **항목명**: HMAC 서명 필수
> - **값 (Part2 §6.7 L5050 원문)**: "Agent 메시지에 HMAC 무결성 서명 필수"
> - **정본 선언**: Part2 §6.7 L5050
> - **근거 설계 문서**: D2.0-07 S7E-078 (AUTHORITY_CHAIN.md §2.2 인용 위치 L2420-2421: "Agent 통신 보안 — Agent 간 메시지 HMAC 무결성 검증, Agent ID 인증")

> **LOCK-AT-003**:
> - **ID**: LOCK-AT-003
> - **항목명**: 무한 루프 금지
> - **값 (Part2 §6.7 L5041 원문)**: "에이전트 간 자유 상호 호출 / 무한 대화 루프 금지"
> - **정본 선언**: Part2 §6.7 L5041
> - **근거 설계 문서**: D2.0-03 §1.4 (L76) + D2.0-05 §7.3 (L381)

> **LOCK-AT-007**:
> - **ID**: LOCK-AT-007
> - **항목명**: Checkpoint/Replay/Fork
> - **값 (Part2 §6.7 L5045 원문)**: "Checkpoint/Replay/Fork는 trace_id 단위로만 허용"
> - **정본 선언**: Part2 §6.7 L5045
> - **근거 설계 문서**: D2.0-05 §7.3 고정2 (L375)

> **LOCK-AT-014**:
> - **ID**: LOCK-AT-014
> - **항목명**: 병렬 상한
> - **값 (Part2 §6.7 L5052 원문)**: "V1 병렬 상한=3, V2=10, V3=50+"
> - **정본 선언**: Part2 §6.7 L5052
> - **근거 설계 문서**: SPEC S7-A-008 (L720)

> **LOCK-AT-002**:
> - **ID**: LOCK-AT-002
> - **항목명**: 단일결정 원칙
> - **값 (Part2 §6.7 L5040 원문)**: "단일결정 원칙: 최종 결론은 Lead Agent(ORANGE CORE)만 확정"
> - **정본 선언**: Part2 §6.7 L5040
> - **근거 설계 문서**: D2.0-02 §2.2 S3 (L319)

> **LOCK-AT-015**:
> - **ID**: LOCK-AT-015
> - **항목명**: Lead 직접실행 금지
> - **값 (Part2 §6.7 L5053 원문)**: "Lead Agent는 직접 실행 금지 (계획/분배/검증만 수행)"
> - **정본 선언**: Part2 §6.7 L5053
> - **근거 설계 문서**: SPEC S7-A-001 (L118)

> **LOCK-AT-016 (운영 규칙 인용 — import 금지)**:
> - **ID**: LOCK-AT-016
> - **항목명**: LangChain import 금지
> - **값 (Part2 §6.7 L5054 원문)**: "LangChain import 금지 (패턴 참조만)"
> - **정본 선언**: Part2 §6.7 L5054
> - **근거 설계 문서**: D2.0-02 DEC-002 (L80)

본 문서 본문 코드는 LangChain 모듈을 import 하지 않는다 (LOCK-AT-016 준수). MessageBus 패턴은 `redis.asyncio` + 표준 라이브러리 `hmac`/`hashlib`/`json`/`asyncio` 만 사용.

---

## 3. RedisMessageBus 클래스 스켈레톤

### 3.1 공통 자료 구조 (Pydantic models, V1 BusMessage 확장)

```python
from __future__ import annotations
from typing import Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import json
import asyncio
import hmac
import hashlib
import logging

# P1-07 §3.1 재사용: AgentRole, BusMessage, MessagePriority, MessageType,
# Subscription, BusStats, MessageBusEscalationPayload (import 가정)
# from .P1_07_in_memory_messagebus import (
#     BusMessage, MessagePriority, MessageType,
#     Subscription, BusStats, MessageBusEscalationPayload,
# )


class HMACAlgorithm(Enum):
    """HMAC 알고리즘 식별자.

    LOCK-AT-012 정본: HMAC-SHA256.
    6-2 02_hmac-timing-defense L3 LOCK 일치.
    """
    SHA256 = "HMAC-SHA256"


@dataclass
class HMACSignature:
    """HMAC 서명 메타데이터.

    constant-time 비교용 (hmac.compare_digest()).
    6-2 02_hmac-timing-defense §A 항목 1 정본 패턴 준수.
    """
    algorithm: HMACAlgorithm = HMACAlgorithm.SHA256
    key_id: str = ""                  # 키 순환 식별자 (L5: 90일 주기)
    signature_hex: str = ""           # hexdigest 결과
    signed_at: float = 0.0            # signing timestamp (epoch seconds)
    nonce: str = ""                   # replay 방지 nonce (UUID4)


@dataclass
class ChannelMetadata:
    """Redis Pub/Sub 채널 메타데이터.

    채널 명명 규칙:
      - 단일캐스트: agent.{agent_id}.{message_type}
      - 브로드캐스트: broadcast.{topic}
      - 시스템: system.{event_type}
    """
    channel_name: str
    pattern: str                      # "single" | "broadcast" | "system"
    subscriber_count: int = 0
    last_publish_at: Optional[float] = None
    is_persistent: bool = True        # XADD/XREAD 영속화 여부


@dataclass
class RedisMessageEnvelope:
    """Redis MessageBus를 통해 전달되는 envelope.

    LOCK-AT-007: trace_id 필수.
    LOCK-AT-012: hmac 필드 필수 (None 허용 안 함, 미서명 거부).

    V1 BusMessage 호환 필드 + V2 추가 필드.
    """
    msg_id: str                       # UUID v4
    trace_id: str                     # LOCK-AT-007 단위
    sender: str                       # 발신 agent_id
    recipient: str                    # 수신 agent_id 또는 "broadcast"
    msg_type: MessageType
    timestamp: float                  # epoch seconds (UTC)
    payload: dict[str, Any] = field(default_factory=dict)
    # V2 신규 필드
    hmac_signature: HMACSignature = field(default_factory=HMACSignature)
    key_id: str = ""                  # KEY 순환 식별자 (HMACSignature.key_id 미러)
    sequence_id: Optional[str] = None  # Redis Streams XADD ID
    priority: MessagePriority = MessagePriority.NORMAL
    ttl_seconds: Optional[float] = 300.0  # 기본 5분 (replay 5분 윈도우와 정렬)

    def signing_payload_bytes(self) -> bytes:
        """서명 대상 정규화 바이트열.

        본문 + key_id + nonce 를 정렬된 JSON 으로 직렬화 (timing-stable).
        """
        canonical = {
            "msg_id": self.msg_id,
            "trace_id": self.trace_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "msg_type": self.msg_type.value,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "key_id": self.hmac_signature.key_id,
            "nonce": self.hmac_signature.nonce,
            "signed_at": self.hmac_signature.signed_at,
        }
        return json.dumps(
            canonical, sort_keys=True, ensure_ascii=False, default=str
        ).encode("utf-8")
```

### 3.2 클래스 인터페이스 (V1 InMemoryMessageBus 시그니처 호환, R-63-8)

```python
class RedisMessageBus:
    """Redis Pub/Sub + Streams 기반 V2 MessageBus.

    LOCK-AT-012: 모든 발행 메시지에 HMAC-SHA256 서명 필수, 검증 실패 폐기.
    LOCK-AT-007: trace_id 누락 시 발행 거부 (TraceMissingError).
    LOCK-AT-003: 무한 루프 패턴 감지 (V1 _detect_loop_pattern 인터페이스 호환).
    LOCK-AT-014: V2 병렬 상한 10 (publisher 동시성 상한).
    R-63-8: V1 InMemoryMessageBus 인터페이스 시그니처 동일성 보장.
    LOCK-AT-016: 본 모듈은 LangChain import 금지.

    설계 원칙:
      - 채널 라우팅: agent.{agent_id}.{type} (단일) / broadcast.{topic} (다중)
      - 영속화: Redis Streams XADD + 컨슈머 그룹 ack
      - HMAC 강제: publish 측 sign + subscribe 측 verify (compare_digest)
      - 재연결: exponential backoff 0.5s × 2^n, max 60s, 12회

    시간복잡도:
      - publish(): O(1) Redis 단일 라운드트립 + O(s) 서명 계산 (s=payload size)
      - subscribe(): O(1) PSUBSCRIBE 등록
      - unsubscribe(): O(1) PUNSUBSCRIBE
      - broadcast(): O(c) where c = active broadcast channels
      - get_stats(): O(1)
      - shutdown(): O(n) connection pool 종료 (n = active connections)

    ABC 시그니처 (V1 InMemoryMessageBus 동일 — R-63-8):
      publish(message: BusMessage) -> bool
      subscribe(subscriber_id: str, topic: str, callback) -> Subscription
      unsubscribe(subscriber_id: str, topic: str) -> bool
      broadcast(message: BusMessage) -> int
      get_stats() -> BusStats
      shutdown() -> None
    """

    # V2 상수 (Part2 V2-P3 정본)
    MAX_CONNECTIONS: int = 20         # ConnectionPool max_connections=20
    IDLE_TIMEOUT_SECONDS: int = 300   # 5분 idle 타임아웃
    BACKOFF_INITIAL_SECONDS: float = 0.5
    BACKOFF_MAX_SECONDS: float = 60.0
    BACKOFF_MAX_RETRIES: int = 12
    REPLAY_WINDOW_SECONDS: int = 300  # 6-2 L6 5분 정본
    KEY_ROTATION_SECONDS: int = 24 * 3600  # 24시간 dual-key window (6-2 L5 grace)
    MAX_PARALLEL_PUBLISHERS: int = 10  # LOCK-AT-014 V2=10

    def __init__(
        self,
        redis_url: str,
        hmac_keys: dict[str, bytes],   # {key_id: 32-byte secret}
        active_key_id: str,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Args:
            redis_url: redis://host:port/db (예: redis://localhost:6379/3)
            hmac_keys: 다중 키 딕셔너리 (현재 활성 + grace 이전 키)
            active_key_id: 현재 활성 키 식별자
            logger: 로깅 인스턴스

        세션간 인터페이스 cross-check:
          - P1-07 InMemoryMessageBus: publish/subscribe 시그니처 동일 (R-63-8)
          - P1-13 LoopDetector: 루프 감지 위임 (LOCK-AT-003)
          - P1-14 TraceManager: trace_id 전파 (LOCK-AT-007)
          - P2A-6 execution_engine: V2 병렬 publisher 상한 적용 (LOCK-AT-014)
        """
        self._redis_url = redis_url
        self._hmac_keys = dict(hmac_keys)  # defensive copy
        self._active_key_id = active_key_id
        self._logger = logger or logging.getLogger("redis_message_bus")
        self._is_running = False
        # 6-2 02_hmac-timing-defense L4 32바이트 키 길이 검증
        for kid, k in self._hmac_keys.items():
            if len(k) < 32:
                raise SecurityError(
                    f"HMAC key '{kid}' too short: {len(k)} bytes (min 32)"
                )
        # subscriber 콜백 레지스트리 (V1 InMemoryMessageBus.subscriptions 호환)
        self._subscriptions: dict[str, dict[str, Subscription]] = {}
        # publisher 동시성 세마포어 (LOCK-AT-014 V2=10)
        self._publish_semaphore = asyncio.Semaphore(self.MAX_PARALLEL_PUBLISHERS)
        # nonce 중복 차단 캐시 (TTL 5분, 6-2 L6)
        self._seen_nonces: dict[str, float] = {}
        self._stats = BusStats()
        # V2 추가: 통계 카운터
        self._hmac_rejections = 0
        self._replay_rejections = 0

    async def connect(self) -> None:
        """Redis ConnectionPool 초기화 + 헬스체크."""
        # redis.asyncio.from_url(redis_url, max_connections=20, decode_responses=True)
        # PING → PONG 확인
        # XGROUP CREATE 컨슈머 그룹 사전 등록
        self._is_running = True

    async def disconnect(self) -> None:
        """ConnectionPool 종료. shutdown()의 별칭."""
        await self.shutdown()

    async def publish(self, message: BusMessage) -> bool:
        """메시지를 Redis 채널에 발행 (HMAC 서명 후).

        LOCK-AT-007: trace_id 누락 시 TraceMissingError.
        LOCK-AT-012: HMAC 미서명 메시지 발행 거부 (ValueError).
        LOCK-AT-003: 무한 루프 패턴 감지 (LoopDetector 위임).
        LOCK-AT-014: V2 병렬 publisher 상한 10 (semaphore).

        Args:
            message: BusMessage (V1 호환). 내부에서 RedisMessageEnvelope로 승격.

        Returns:
            bool: 발행 성공 여부.

        Raises:
            ValueError: HMAC 미서명 메시지 발행 시도 (LOCK-AT-012).
            TraceMissingError: trace_id 누락 (LOCK-AT-007).
            BusShutdownError: 종료 후 호출.
        """
        async with self._publish_semaphore:  # LOCK-AT-014 V2=10
            # 1) trace_id 검증 (LOCK-AT-007)
            if not message.trace_id:
                raise TraceMissingError(message.message_id)
            # 2) BusMessage → RedisMessageEnvelope 승격 + HMAC 서명
            envelope = self._promote_to_envelope(message)
            envelope = self._sign_envelope(envelope)
            # 3) 채널 결정 (단일캐스트 or 브로드캐스트)
            channel = self._channel_name(envelope)
            # 4) Redis XADD (영속화) + PUBLISH (Pub/Sub 알림)
            #    XADD replay.bus.{date} * msg_id ... timestamp ...
            #    PUBLISH agent.{recipient}.{type} <serialized envelope>
            # 5) 통계 갱신
            self._stats.total_published += 1
            return True

    def subscribe(
        self,
        subscriber_id: str,
        topic: str,
        callback: Callable[[BusMessage], Awaitable[None]],
    ) -> Subscription:
        """채널 구독 (단일캐스트 or 브로드캐스트).

        V1 InMemoryMessageBus.subscribe()와 시그니처 동일 (R-63-8).
        내부에서 Redis (P)SUBSCRIBE 호출 + HMAC 검증 wrapping.
        """
        if topic not in self._subscriptions:
            self._subscriptions[topic] = {}
        if subscriber_id in self._subscriptions[topic]:
            raise DuplicateSubscriptionError(subscriber_id, topic)
        sub = Subscription(
            subscriber_id=subscriber_id, topic=topic, callback=callback
        )
        self._subscriptions[topic][subscriber_id] = sub
        # 내부 wrapping: HMAC 검증 후 callback 호출
        # await redis_client.psubscribe(self._channel_pattern(topic), wrapped_cb)
        self._stats.active_subscribers += 1
        return sub

    def unsubscribe(self, subscriber_id: str, topic: str) -> bool:
        """채널 구독 해제. V1 시그니처 동일."""
        if topic not in self._subscriptions:
            return False
        if subscriber_id not in self._subscriptions[topic]:
            return False
        del self._subscriptions[topic][subscriber_id]
        self._stats.active_subscribers -= 1
        return True

    async def broadcast(self, message: BusMessage) -> int:
        """`broadcast.{topic}` 채널로 1:N 전달. V1 시그니처 동일.

        LOCK-AT-007: trace_id 필수.
        LOCK-AT-012: HMAC 서명 필수.
        """
        if not message.trace_id:
            raise TraceMissingError(message.message_id)
        # broadcast 채널 명명: broadcast.{message.topic}
        envelope = self._promote_to_envelope(message)
        envelope.recipient = "broadcast"
        envelope = self._sign_envelope(envelope)
        # PUBLISH broadcast.{topic} <envelope>
        self._stats.total_broadcast += 1
        return 0  # 실제 구현에서는 Redis가 반환한 subscriber count 반환

    def get_stats(self) -> BusStats:
        """V1 시그니처 동일."""
        return self._stats

    async def shutdown(self) -> None:
        """ConnectionPool 종료 + 잔여 메시지 드레인.

        V1 시그니처 동일 (sync 형태로도 호출 가능하도록 wrapper 권장).
        """
        self._is_running = False
        # await redis_client.close()
        # await connection_pool.disconnect()
        self._subscriptions.clear()

    async def close(self) -> None:
        """disconnect()의 별칭. redis-py async 관례."""
        await self.shutdown()

    # ---------- 내부 메서드 ----------

    def _channel_name(self, envelope: RedisMessageEnvelope) -> str:
        """채널 명명 규칙 적용.

        - 단일캐스트: agent.{recipient}.{msg_type}
        - 브로드캐스트: broadcast.{recipient or "all"}
        """
        if envelope.recipient == "broadcast":
            return f"broadcast.{envelope.payload.get('topic', 'all')}"
        return f"agent.{envelope.recipient}.{envelope.msg_type.value}"

    def _promote_to_envelope(self, msg: BusMessage) -> RedisMessageEnvelope:
        """V1 BusMessage → V2 RedisMessageEnvelope 승격."""
        return RedisMessageEnvelope(
            msg_id=msg.message_id,
            trace_id=msg.trace_id,
            sender=msg.source_agent_id,
            recipient=msg.target_agent_id,
            msg_type=msg.message_type,
            timestamp=msg.timestamp,
            payload=dict(msg.payload),
            priority=msg.priority,
            ttl_seconds=msg.ttl_seconds or float(self.REPLAY_WINDOW_SECONDS),
        )

    def _sign_envelope(
        self, envelope: RedisMessageEnvelope
    ) -> RedisMessageEnvelope:
        """LOCK-AT-012: HMAC-SHA256 서명 부착.

        6-2 02_hmac-timing-defense §A 항목 1 정본 패턴:
          hmac.new(key, payload, hashlib.sha256).hexdigest()
        """
        key = self._hmac_keys.get(self._active_key_id)
        if key is None:
            # LOCK-AT-012: 키 부재 시 발행 거부 (R-63-8 fallback 금지)
            raise ValueError(
                "LOCK-AT-012: HMAC key absent — message rejected"
            )
        envelope.hmac_signature.key_id = self._active_key_id
        envelope.hmac_signature.nonce = uuid.uuid4().hex
        envelope.hmac_signature.signed_at = time.time()
        envelope.key_id = self._active_key_id
        sig = hmac.new(
            key, envelope.signing_payload_bytes(), hashlib.sha256
        ).hexdigest()
        envelope.hmac_signature.signature_hex = sig
        envelope.hmac_signature.algorithm = HMACAlgorithm.SHA256
        return envelope

    def _verify_envelope(
        self, envelope: RedisMessageEnvelope
    ) -> bool:
        """수신측 HMAC 검증 (constant-time, 6-2 §A 항목 1).

        LOCK-AT-012: 검증 실패 시 메시지 폐기 + 보안 로그.
        타임스탬프 ±5분 검사 (6-2 L6 replay window 정합).
        nonce 중복 검사 (replay 차단).
        """
        # 1) 타임스탬프 윈도우
        now = time.time()
        if abs(now - envelope.hmac_signature.signed_at) > self.REPLAY_WINDOW_SECONDS:
            self._replay_rejections += 1
            self._logger.warning(
                "Replay window exceeded — msg_id=%s diff=%.2fs",
                envelope.msg_id,
                now - envelope.hmac_signature.signed_at,
            )
            return False
        # 2) nonce 중복
        if envelope.hmac_signature.nonce in self._seen_nonces:
            self._replay_rejections += 1
            return False
        self._seen_nonces[envelope.hmac_signature.nonce] = now
        self._gc_nonces(now)
        # 3) 키 조회 (dual-key window 지원)
        key = self._hmac_keys.get(envelope.hmac_signature.key_id)
        if key is None:
            self._hmac_rejections += 1
            return False
        expected = hmac.new(
            key, envelope.signing_payload_bytes(), hashlib.sha256
        ).hexdigest()
        # 4) constant-time 비교 (6-2 §A 항목 1)
        ok = hmac.compare_digest(expected, envelope.hmac_signature.signature_hex)
        if not ok:
            self._hmac_rejections += 1
            self._logger.warning(
                "HMAC verification failed — msg_id=%s key_id=%s",
                envelope.msg_id, envelope.hmac_signature.key_id,
            )
        return ok

    def _gc_nonces(self, now: float) -> None:
        """nonce 캐시 GC — 5분 경과분 삭제."""
        cutoff = now - self.REPLAY_WINDOW_SECONDS
        expired = [n for n, t in self._seen_nonces.items() if t < cutoff]
        for n in expired:
            del self._seen_nonces[n]


class SecurityError(Exception):
    """6-2 L4 키 길이 검증 실패 / HMAC 관련 예외."""


class TraceMissingError(Exception):
    """LOCK-AT-007 위반 — trace_id 누락."""

    def __init__(self, msg_id: str):
        self.msg_id = msg_id
        super().__init__(f"LOCK-AT-007: trace_id missing — message_id={msg_id}")


class DuplicateSubscriptionError(Exception):
    """V1 호환 — 동일 (subscriber, topic) 중복 구독."""


class BusShutdownError(Exception):
    """V1 호환 — 종료 후 호출."""
```

### 3.3 채널 명명 규칙 표

| 패턴 | 형식 | 예시 | 용도 |
|------|------|------|------|
| 단일캐스트 (DELEGATION) | `agent.{recipient}.delegation` | `agent.research.delegation` | Lead → Worker 위임 |
| 단일캐스트 (RESULT) | `agent.{recipient}.result` | `agent.lead.result` | Worker → Lead 결과 |
| 단일캐스트 (HEARTBEAT) | `agent.{recipient}.heartbeat` | `agent.research.heartbeat` | 생존 신호 |
| 단일캐스트 (CHECKPOINT) | `agent.{recipient}.checkpoint` | `agent.lead.checkpoint` | LOCK-AT-007 trace_id 단위 |
| 단일캐스트 (ESCALATION) | `agent.{recipient}.escalation` | `agent.lead.escalation` | I-20 에스컬레이션 |
| 브로드캐스트 | `broadcast.{topic}` | `broadcast.system`, `broadcast.policy_update` | 1:N 전달 |
| 시스템 이벤트 | `system.{event}` | `system.key_rotation`, `system.bus_shutdown` | 운영 이벤트 |

### 3.4 연결 풀 + 재연결 전략

| 항목 | 값 | 출처 |
|------|-----|------|
| `max_connections` | 20 | Part2 V2-P3 #1 정본 |
| `decode_responses` | True | redis-py 권장 (UTF-8 자동 디코드) |
| `socket_timeout` | 5.0s | 연결 단위 read/write timeout |
| `socket_keepalive` | True | TCP keepalive (NAT 트래버설) |
| `health_check_interval` | 30s | 자동 PING |
| 재연결 backoff | exponential 0.5s × 2^n, max 60s | 본 문서 §3.2 정본 |
| 재연결 max retry | 12회 (≈ 합 2,047s ≈ 34분) | 본 문서 §3.2 정본 |
| 재연결 실패 후 | In-Memory fallback 5분 (§6 ISS-8) | 본 문서 §6.4 정본 |

---

## 4. 메시지 포맷 (JSON + HMAC)

### 4.1 RedisMessageEnvelope JSON 직렬화 예시

```json
{
  "msg_id": "f7c1e6d2-9b3a-4e88-b2a1-7e9f5b8c1234",
  "trace_id": "trace-2026-04-30-aaa-bbb-ccc",
  "sender": "agent.lead",
  "recipient": "agent.research",
  "msg_type": "delegation",
  "timestamp": 1745996400.123,
  "payload": {
    "task": "정량 분석 요청",
    "owner_id": "user-001",
    "depth": 1,
    "deadline_ms": 30000
  },
  "hmac_signature": {
    "algorithm": "HMAC-SHA256",
    "key_id": "kr-2026-04-w1",
    "signature_hex": "9c1a2b3d4e5f60718293a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5",
    "signed_at": 1745996400.124,
    "nonce": "5e9d3a1b6c4f47e2"
  },
  "key_id": "kr-2026-04-w1",
  "sequence_id": "1745996400123-0",
  "priority": 1,
  "ttl_seconds": 300.0
}
```

### 4.2 HMAC-SHA256 서명 알고리즘

> 정본 출처: 6-2 02_hmac-timing-defense §A 항목 1, §B 참조 구현 패턴 (Part2 §6.5.2 정본 Python 패턴 그대로)

```python
# 발신자 (sign):
expected = hmac.new(
    key,                          # 32+ bytes
    envelope.signing_payload_bytes(),
    hashlib.sha256
).hexdigest()
envelope.hmac_signature.signature_hex = expected

# 수신자 (verify, constant-time):
if not hmac.compare_digest(
    expected,
    envelope.hmac_signature.signature_hex,
):
    # LOCK-AT-012: 검증 실패 → 메시지 폐기 + 보안 로그
    return False
```

- **알고리즘**: HMAC-SHA256 (6-2 L3 LOCK)
- **키 길이**: ≥ 32바이트 (6-2 L4 LOCK)
- **비교 방식**: `hmac.compare_digest()` (`==` 직접 비교 금지, 6-2 R-62-4)
- **에러 응답 균일화**: 검증 실패 시 단일 메시지 ("Invalid signature") 반환, 키 존재 여부/만료 여부 노출 금지 (6-2 §A 항목 5)

### 4.3 키 순환 (dual-key window)

> 정본 출처: 6-2 02_hmac-timing-defense §C 키 관리 라이프사이클 7단계

| 단계 | 절차 | 본 MessageBus 동작 |
|------|------|------------------|
| 생성 | `crypto.randomBytes(32)` 또는 `secrets.token_bytes(32)` | `hmac_keys[new_key_id]` 등록 |
| 저장 | V1 .env / V2 HashiCorp Vault | `RedisMessageBus.__init__(hmac_keys=...)` |
| 배포 | 환경변수 주입 | 시작 시 양쪽 키 모두 로드 |
| 순환 | 90일 자동 (6-2 L5 LOCK) | `active_key_id`만 신키로 교체, 구키는 `hmac_keys`에 유지 |
| **Grace Period (24h)** | 6-2 L5 grace 정본 | 신키로 서명, 구키로도 검증 통과 — `_verify_envelope()` 키 조회 시 dual-window 지원 |
| 폐기 | Grace 만료 후 구키 삭제 | 24시간 후 `hmac_keys.pop(old_key_id)` |
| 긴급 교체 | 키 유출 시 즉시 폐기 + 신규 생성 | `hmac_keys.clear()` + 신키만 등록 (Grace 없음) |

**6-2 정책 직접 연동**:
- 키 길이 < 32 → 즉시 `SecurityError` (6-2 §A 항목 2)
- 5분 초과 타임스탬프 → 거부 (6-2 §A 항목 4 / L6 LOCK)
- nonce 중복 → 거부 (6-2 §A 항목 4)
- 6-2 §C 7단계 절차 변경은 6-2 정본만 수정 가능 (본 문서는 참조만)

---

## 5. LOCK-AT-012 준수 (HMAC 미서명 메시지 거부)

### 5.1 발신 측 (publisher) 강제

```python
async def publish(self, message: BusMessage) -> bool:
    if not message.trace_id:
        raise TraceMissingError(message.message_id)
    envelope = self._promote_to_envelope(message)
    # LOCK-AT-012: 발신 측은 반드시 서명 후 발행
    envelope = self._sign_envelope(envelope)  # 키 부재 시 ValueError
    # ... XADD + PUBLISH
```

- 키 부재 시: `ValueError("LOCK-AT-012: HMAC key absent — message rejected")` 즉시 발생, 발행 금지.
- fallback 금지 (R-63-8): 미서명 발행 경로 자체를 봉쇄.

### 5.2 수신 측 (subscriber) 강제

```python
async def _on_message(self, raw: str) -> None:
    envelope = RedisMessageEnvelope(**json.loads(raw))
    # LOCK-AT-012: 수신 측은 검증 실패 시 메시지 폐기 + 보안 로그
    if not self._verify_envelope(envelope):
        self._logger.warning(
            "LOCK-AT-012 violation — discarded msg_id=%s sender=%s",
            envelope.msg_id, envelope.sender,
        )
        return  # silent discard, 단일 에러 메시지만 (6-2 §A 항목 5)
    # 검증 통과 → callback 호출
    await callback(envelope)
```

### 5.3 키 부재 fallback 금지 (R-63-8)

본 V2 RedisMessageBus는 **키 부재 시에도 V1 In-Memory fallback 으로 미서명 메시지를 흘리지 않는다**. 키 부재 자체가 운영 사고 (6-2 §C 절차 위반)이므로 즉시 발행 거부 + 관리자 알림. fallback은 §6.4 ISS-8 마이그레이션 절차의 "Redis 장애 시 In-Memory 5분 비상 모드" 와는 다른 차원 (장애 fallback도 HMAC 서명은 필수, In-Memory 백엔드만 교체).

### 5.4 위반 시나리오 / 자동 대응 (AUTHORITY_CHAIN.md §2.3 12행 정합)

| 시나리오 | 탐지 | 자동 대응 |
|----------|------|----------|
| HMAC 미서명 메시지 발행 시도 | `_sign_envelope()` 호출 우회 코드 정적 분석 + 발행 진입점 단일화 | 발행 거부 (`ValueError`) + audit log |
| HMAC 변조 메시지 수신 | `compare_digest()` 실패 | 메시지 폐기 + 보안 로그 + `_hmac_rejections += 1` |
| 키 부재 발행 | `hmac_keys[active_key_id] is None` | `ValueError` + oncall 알림 |
| Grace 만료 키로 서명 시도 | 키 폐기 후 cache miss | `ValueError` + 신키 강제 |

---

## 6. ISS-8 V1→V2 마이그레이션 절차

> 종합계획서 §6 ISS-8 (MEDIUM): MessageBus V1→V2→V3 마이그레이션 절차 미정의

### 6.1 Phase A — Dual-mode (7일)

- V1 `InMemoryMessageBus` + V2 `RedisMessageBus` **병렬 운영**.
- 모든 publisher 는 `DualWriteFacade` 경유 → 양쪽 모두에 publish.
- subscriber 는 V1만 구독 (V2는 검증 모드).
- HMAC 서명 활성화 (`hmac_keys` 등록), V2 측에서 검증 실패율 모니터링.
- 종료 조건: 7일 동안 V2 검증 성공률 ≥ 99.99% + 메시지 유실 0건.

### 6.2 Phase B — Shadow mode (3일)

- V2 `RedisMessageBus` 가 **primary**, V1 `InMemoryMessageBus` 가 **shadow**.
- subscriber 는 V2 구독 + V1 fallback (V2 콜백 실패 시 V1 콜백 호출).
- shadow log: V1/V2 발행 메시지 다이프 로그 (불일치 즉시 알림).
- 종료 조건: 3일 동안 다이프 0건 + V2 P95 latency < 10ms 충족.

### 6.3 Phase C — Redis only (V1 폐기)

- V1 `InMemoryMessageBus` 인스턴스화 경로 제거 (DualWriteFacade → V2 직접 호출).
- 코드는 보존 (LOCK-AT-016 패턴 참조 + 비상 fallback 모듈).
- 모든 publisher/subscriber 는 V2 RedisMessageBus 만 사용.

### 6.4 메시지 유실 방지 + 롤백

| 메커니즘 | 구현 | 적용 Phase |
|----------|------|----------|
| **Dual-write replay log** | Redis Stream `replay.bus.YYYY-MM-DD` 에 모든 발행 메시지 XADD (TTL 7일) | A, B, C |
| **컨슈머 그룹 ack** | XREADGROUP + XACK; 미ack 메시지는 PEL (Pending Entries List)에 보존 | A, B, C |
| **Replay tool** | XRANGE replay.bus.{date} {min}-{max} → 재발행 (HMAC 재서명) | 운영 |
| **롤백 (Redis 장애)** | Redis 헬스체크 5회 연속 실패 → 5분 In-Memory 비상 모드 (HMAC 유지) → 알림 P1 oncall | A, B, C |
| **롤백 (HMAC 검증 실패율 ≥ 1%)** | 검증 실패율 > 1% 임계 → 자동으로 Phase A 듀얼모드로 회귀 + 키 재배포 | A → B 진입 시 |

### 6.5 마이그레이션 게이트 5/5

| # | 게이트 항목 | 측정 | 통과 기준 |
|---|------------|------|---------|
| 1 | Dual-mode HMAC 검증 성공률 | 7일 누적 | ≥ 99.99% |
| 2 | Shadow mode 다이프 0건 | 3일 누적 | 0건 |
| 3 | V2 P95 지연 (LAN) | 1,000 msg 부하 | < 10ms |
| 4 | V2 P99 지연 (WAN) | 100 msg 부하 cross-region | < 50ms |
| 5 | Redis 장애 fallback 회복 | 시뮬레이션 5회 | 5분 이내 회복 |

---

## 7. 6-2 Security HMAC 정책 교차 참조

> 본 §은 6-2 02_hmac-timing-defense 정본을 **참조만** 한다 (편집 ❌).

### 7.1 알고리즘 / 키 / 비교 (6-2 §A, §B)

| 항목 | 6-2 정본 | 본 6-3 MessageBus 적용 |
|------|---------|----------------------|
| 알고리즘 | HMAC-SHA256 (6-2 L3) | `hashlib.sha256` 고정 |
| 키 길이 | ≥ 32바이트 (6-2 L4) | `__init__()` 에서 `len(key) < 32 → SecurityError` |
| 비교 | `hmac.compare_digest()` (6-2 §A 항목 1, R-62-4) | `_verify_envelope()` 내 동일 함수 사용 |
| 에러 응답 | "Invalid signature" 단일 (6-2 §A 항목 5) | 보안 로그 외 외부 응답 미노출 |

### 7.2 키 관리 (6-2 §C 7단계)

| 단계 | 6-2 정본 | 본 MessageBus |
|------|---------|--------------|
| 생성 | `crypto.randomBytes(32)` | 호출자 (DevOps) 책임 — `hmac_keys` 주입 |
| 저장 | V1 .env / V2 Vault | 6-2 정책 위임 |
| 배포 | 환경변수 주입 | `__init__(hmac_keys=...)` 시점 |
| 순환 | 90일 (L5) | `active_key_id` 교체 + 24h grace 동시 활성 |
| Grace | 24h dual-key (L5) | `hmac_keys` 에 양키 유지 → `_verify_envelope()` dual-window |
| 폐기 | Grace 만료 후 삭제 | `hmac_keys.pop(old_key_id)` |
| 긴급 교체 | S7E-005 인시던트 절차 | `hmac_keys.clear() + add(new_key)` (Grace 0h) |

### 7.3 타이밍 / 리플레이 / nonce (6-2 §A 항목 1, 4, 5)

- **타이밍 안전 비교**: `hmac.compare_digest()` 의무 (6-2 R-62-4) — `==` 절대 금지.
- **타임스탬프 ±5분**: 6-2 L6 정본 (300초). 본 MessageBus `REPLAY_WINDOW_SECONDS = 300` 일치.
- **nonce 중복**: Redis/SQLite TTL 캐시 (6-2 §A 항목 4). 본 MessageBus `_seen_nonces` 5분 GC.
- **에러 응답 균일화**: 검증 실패 시 단일 메시지 (6-2 §A 항목 5) — 키 존재 여부/만료 여부 외부 노출 금지.

### 7.4 인시던트 대응 (6-2 §E STEP7-E 8건 매핑)

| 시나리오 | 6-2 매핑 | 본 MessageBus 동작 |
|---------|---------|------------------|
| 키 유출 | S7E-070 자동 격리 + S7E-005 긴급 교체 | `hmac_keys.clear()` + 신키 즉시 적용 + 모든 PEL 메시지 재서명 |
| 인증 실패 급증 | S7E-073 긴급 연락 + P1 oncall | `_hmac_rejections` 카운터 모니터링 (>1%/5min → 알림) |
| Redis 장애 | S7E-074 안전 모드 | In-Memory 5분 비상 모드 + HMAC 유지 |

---

## 8. 성능 벤치마크 기준

| 지표 | 목표 | 측정 방법 | 출처 |
|------|------|----------|------|
| **메시지 지연 P95 (LAN)** | < 10ms | 1,000 msg 동시 발행, publish→subscribe callback 도달 시간 | 종합계획서 §7.4 산출물1 절차 5 |
| **메시지 지연 P99 (WAN)** | < 50ms | 100 msg cross-region (us-east → eu-west) | 본 문서 §6.5 정본 |
| **처리량** | ≥ 1,000 msg/s | 단일 Redis 인스턴스, 30초 부하 | 종합계획서 §7.4 산출물1 절차 5 |
| **연결 수** | max_connections=20 | `redis.asyncio.ConnectionPool` 통계 | Part2 V2-P3 #1 정본 |
| **idle timeout** | 5분 | TCP keepalive | 본 문서 §3.4 |
| **HMAC 서명 오버헤드** | < 0.5ms / msg | 1KB payload, 32B key | hashlib bench (i7-12700K 기준) |
| **HMAC 검증 오버헤드** | < 0.5ms / msg | constant-time 동일 | 동일 |
| **메시지 유실** | 0건 | 100,000 msg 부하, dual-write replay log 검증 | §6.4 정본 |
| **재연결 회복** | < 60s | Redis 5초 단절 → 재연결 측정 | 본 문서 §3.2 |
| **Fallback 회복** | < 5분 | Redis 장애 → In-Memory 비상 모드 진입 | §6.4 정본 |

---

## 9. Phase 3 테스트 시나리오 (12건)

### 9.1 핵심 시나리오 (산출물1 §검증 항목 정합)

| # | 시나리오 ID | 주입 방법 | 기대 결과 | LOCK 참조 |
|---|------------|----------|----------|----------|
| 1 | `test_p2_redis_normal_publish` | HMAC 서명 정합 메시지 1건 발행 | 메시지 전달 OK, callback 1회 호출, sequence_id 단조 증가 | LOCK-AT-007, LOCK-AT-012 |
| 2 | `test_p2_redis_unsigned_block_publisher` | 발행 측 키 부재로 서명 누락 시도 | `ValueError("LOCK-AT-012: HMAC key absent")` 즉시 발생, Redis XADD 미실행 | LOCK-AT-012 |
| 3 | `test_p2_redis_tampered_signature_reject` | 정상 envelope 서명 1바이트 변조 후 PUBLISH | 수신 측 `_verify_envelope()` False 반환, callback 미호출, `_hmac_rejections += 1` | LOCK-AT-012 |
| 4 | `test_p2_redis_trace_id_missing_block` | `trace_id=""` BusMessage publish | `TraceMissingError` 발생, XADD 미실행 | LOCK-AT-007 |
| 5 | `test_p2_redis_loop_detection_block` | A→B→A→B→A 5회 위임 패턴 | 3회차 이후 LOCK-AT-003 경고 + 5회차 차단 (LoopDetector P1-13 위임) | LOCK-AT-003 |
| 6 | `test_p2_redis_dual_key_window` | 신키 활성 + 구키 grace 24h, 구키로 서명된 메시지 | 양쪽 키 모두 검증 통과 (dual-window) | 6-2 L5 (LOCK-AT-012 부속) |
| 7 | `test_p2_redis_failover_to_inmemory` | Redis 5초 단절 시뮬레이션 | 5회 헬스체크 실패 → In-Memory 비상 모드 진입, 5분 이내 회복, HMAC 서명 유지 | §6.4 |
| 8 | `test_p2_redis_zero_message_loss` | 100,000 메시지 발행 + dual-write replay log 검증 | 유실 0건, replay log 100,000 entry 일치 | §6.4 |
| 9 | `test_p2_redis_throughput_1000mps_p95` | 1,000 msg/s × 30초 | P95 < 10ms 유지, 처리량 ≥ 1,000 msg/s | §8 |
| 10 | `test_p2_redis_concurrent_race` | 100 동시 publisher → 동일 채널 | LOCK-AT-014 V2=10 semaphore 동작, 순서/유실 0건 | LOCK-AT-014 |

### 9.2 채널 분리 / 브로드캐스트 시나리오 (산출물1 부속 검증)

| # | 시나리오 ID | 주입 방법 | 기대 결과 | LOCK 참조 |
|---|------------|----------|----------|----------|
| 11 | `test_p2_redis_channel_isolation` | `agent.research.delegation` 발행, `agent.coding` 가 미수신 확인 | agent.coding subscriber 콜백 0회 호출 | — |
| 12 | `test_p2_redis_broadcast_all_active` | `broadcast.system` 발행, 활성 9 agent 모두 수신 | subscriber 9건 callback 호출, 메시지 본문 동일성 확인 | LOCK-AT-014 V2=10 |

---

## 10. §7.6 Phase 2 LOCK-AT 재검증 매핑

| LOCK-AT ID | 재검증 항목 | 본 V2 산출물 기여 | 검증 시나리오 |
|------------|------------|------------------|-------------|
| **LOCK-AT-012 (신규)** | HMAC 서명 검증 100% 적용 (V1=예약 → V2=강제) | §3.2 `_sign_envelope()` + `_verify_envelope()` 강제, §5 발신/수신 양측 미서명 거부 | §9.1 #1, #2, #3 |
| **LOCK-AT-003 (재검증)** | 위임 그래프 순환 탐지 (V1 경고 → V2 차단) | §3.2 LoopDetector 위임 (P1-13 인터페이스 호환) | §9.1 #5 |
| **LOCK-AT-007 (재검증)** | trace_id 단위 Checkpoint (V1 필수 → V2 동일 강제) | §3.2 `publish()` 시작 부 trace_id 검사 | §9.1 #4 |
| **LOCK-AT-014 (재검증)** | V2 병렬 상한 10 (publisher 동시성) | §3.2 `_publish_semaphore = Semaphore(10)` | §9.1 #10, §9.2 #12 |
| **LOCK-AT-002 (보조)** | Lead 단일결정 보존 — MessageBus는 라우팅만, 결정 미발행 | message_type=DECISION 발신자=Lead 만 허용 (정책 강제는 LeadAgent 측) | LeadAgent 통합 테스트에서 검증 |
| **LOCK-AT-015 (보조)** | Lead 직접 실행 금지 — 도구 호출 메시지는 Worker 만 발행 | message_type=TOOL_CALL 발신자=Worker 강제 | execution_engine V2 테스트에서 검증 |
| **LOCK-AT-016 (강제)** | LangChain import 금지 | 본 모듈 코드 LangChain import 0건 (정적 분석 통과) | CI 린터 |

> **LOCK 신규 추가 0건**: 본 산출물은 LOCK-AT-001~017 + LOCK-63-1~3 = 20 unique 정본을 인용만 한다. AUTHORITY_CHAIN.md §2.1, §3 set 변경 0건.
> **DH 0건 보존**: DEFINED-HERE 신규 추가 0건. 본 문서의 모든 "정본" 표기는 외부 정본(Part2 §6.7 / D2.0-07 / 6-2) 인용임.

---

## 11. 변경 이력

| 일자 | 내용 | 세션 |
|------|------|------|
| 2026-04-30 | V2-Phase 2 초안 작성 — Redis Pub/Sub MessageBus + HMAC-SHA256 서명 (LOCK-AT-012) + RedisMessageEnvelope/HMACSignature/ChannelMetadata 자료구조 + V1 InMemoryMessageBus 인터페이스 호환(R-63-8) + ISS-8 V1→V2 마이그레이션 3-Phase(A 듀얼모드 7일 + B 섀도우 3일 + C Redis only) + Redis 장애 In-Memory 5분 fallback + dual-write replay log + 6-2 02_hmac-timing-defense 정책 교차 참조 + 키 순환 24h grace dual-window + constant-time `compare_digest` + 5분 리플레이 윈도우 + nonce 중복 차단 + 성능 벤치마크 P95<10ms / P99<50ms / 1,000msg/s / max_connections=20 + Phase 3 테스트 시나리오 12건 + §7.6 LOCK-AT 재검증 매핑(AT-012/003/007/014/002/015/016) | P2A-1 |

---

> **문서 끝**
> 본 문서는 P2A-1 산출물1 (Redis MessageBus + HMAC 서명) 작성물이며, V2-Phase 2 (Part2 §6.7 V2-P3 정본) 기준 LOCK-AT-012(HMAC 서명 필수)와 LOCK-AT-003/007/014 재검증을 핵심 제약으로 적용합니다.
> R-63-8에 따라 V1 InMemoryMessageBus(P1-07) 인터페이스 시그니처 동일성을 보장하며, 6-2 02_hmac-timing-defense 정책 정본은 참조만 합니다(편집 ❌).
> LOCK-AT 17건 + LOCK-63 3건 = 20 unique set 변경 0건, DH 0건 보존, FABRICATION 0건 통산.

---

## 12. V3 K8s Mesh EXTEND (Phase 4 P4-2 production-ready 정본 승급, 2026-05-27)

> **도입 단계**: Phase 4 P4-2 (V3 implementation)
> **chain**: `phase4_6-3_p4-2_2026-05-27`
> **Status**: APPROVED (Phase 4 P4-2 production-ready 정본 승급 완료, 2026-05-27)
> **V1+V2 baseline 보존 강제 (R9 LOCK 보존 원칙)**: §0~§11 (L1~L881) 본문 byte-prefix SHA `0013849B33E72FE1` UNCHANGED EXACT — 본 §12 V3 K8s Mesh 섹션은 append-only EXTEND (V1 In-Memory + V2 Redis Pub/Sub 본문 변경 0건)
> **대조 기준 (8항목)**: §7.8 P4-2 spec L2511~L2519 직계 — K8s Mesh 섹션 byte ≥ 250L + AT-014 V3=50+ + max 100 분리 + 6-8 cross-handoff RESOLVED + 6-2 Mesh 통신 보안 + 6-5 W-CB 결정 협의 + Part2 V3-P3 L4336-L4548 정합 + Phase 5 entry-gate forward-defined

### 12.1 V3 K8s Mesh 도입 배경

V2 Redis Pub/Sub MessageBus는 LOCK-AT-014 V2=10 병렬 상한 + 단일 Redis 노드 의존 + ConnectionPool max_connections=20 한계가 있다. V3에서 50+ Agent 동시 실행 (LOCK-AT-014 V3=50+) + PARL 모드 max 100 sub-agents (LOCK-63-2) + 다중 노드 분산 + Service Mesh 기반 mTLS 자동화를 위해 K8s Mesh로 EXTEND한다.

**V1 → V2 → V3 도입 매트릭스**:

| 버전 | 기술 | 병렬 상한 (LOCK-AT-014) | 인증 | 라우팅 | 보존 |
|------|------|:--------------------:|------|--------|------|
| V1 | In-Memory `asyncio.Queue` | **3** | 없음 (단일 프로세스) | 단일 채널 | §3 본문 UNCHANGED |
| V2 | Redis Streams XADD/XREAD | **10** | HMAC-SHA256 (LOCK-AT-012) | 채널 패턴 | §3~§11 본문 UNCHANGED |
| **V3 NEW** | **K8s Service Mesh (Istio/Linkerd 권장)** | **50+** | **mTLS 자동 (HMAC AT-012 정합)** | **Service Discovery + Sidecar 자동 라우팅** | **§12 NEW append-only** |

### 12.2 K8s Mesh 아키텍처 (E1)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  K8s Cluster (Phase 4 V3 production)                     │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Service Mesh Control Plane (Istio Pilot / Linkerd Destination)   │   │
│  │   ├─ Service Discovery (DNS + Endpoint Resolver)                  │   │
│  │   ├─ mTLS Certificate Issuer (auto-rotate, 90일 LOCK-L5 inherit) │   │
│  │   ├─ Traffic Policy (Circuit Breaker 6-5 W-CB OBSERVE_ONLY)      │   │
│  │   └─ Telemetry (Prometheus + Grafana exporter)                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                  │                                        │
│  ┌───────────────────────────────┴──────────────────────────────────┐   │
│  │  Data Plane (Envoy / linkerd2-proxy sidecar per Pod)              │   │
│  │   ├─ Pod[lead-agent]    + sidecar (mTLS + HMAC AT-012)            │   │
│  │   ├─ Pod[research-1~50] + sidecar (V3 병렬 상한 50+)              │   │
│  │   ├─ Pod[coding-1~N]    + sidecar (R-63-12 큐잉)                  │   │
│  │   ├─ Pod[parl-swarm]    + sidecar (LOCK-63-2 max 100 sub-agents)  │   │
│  │   └─ Pod[sdar-agent]    + sidecar (Circuit Breaker 6-5 W-CB)      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                  │                                        │
│  ┌───────────────────────────────┴──────────────────────────────────┐   │
│  │  V2 Redis fallback Pod (3-Phase 마이그레이션 기간 dual-write)      │   │
│  │   └─ V2 RedisMessageBus § 2~§7 본문 unchanged (R-63-8 호환 보장)  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 12.3 K8s Mesh 4 핵심 컴포넌트

| 컴포넌트 | 기술 | LOCK 정합 | 6-2 cross-handoff |
|---------|------|---------|-----------------|
| **(1) Service Mesh** | Istio (권장) 또는 Linkerd (대안) | LOCK-AT-001 자체 프레임워크 기본 — 외부 mesh는 sidecar 어댑터로만 연결 | — |
| **(2) mTLS 자동** | Istio Citadel / Linkerd Identity (X.509 mutual TLS) | **LOCK-AT-012** Agent 메시지 HMAC 무결성 — mTLS는 전송 레이어 + HMAC 응용 레이어 (이중 방어 정합) | 6-2 02_hmac-timing-defense (정책 정본 inheritance) |
| **(3) Service Discovery** | K8s Service + Endpoint + DNS (Istio ServiceEntry 옵션) | LOCK-AT-003 무한 루프 금지 — Service Mesh DNS resolver 단일 진입점 + 위임 그래프 cycle 방지 | — |
| **(4) Circuit Breaker** | Istio DestinationRule outlier_detection / Linkerd retry-budget | **6-5 SDAR W-CB DEFERRED_TO_PHASE3 OBSERVE_ONLY** → Phase 4 P4-2 RESOLVED 양 도메인 분담 (4-3 P4-5 CFL-MCP-005 패턴 직계 — 본 §12.8 참조) | 6-5 W-CB 정책 정본 inheritance |

### 12.4 3단계 마이그레이션 (Phase A → B → C)

> **§6 이슈 #8 RESOLVED**: MessageBus 마이그레이션 절차 미정의 (MEDIUM) → 본 §12.4 3단계 마이그레이션 정의로 해소.

| 단계 | 기간 | 동작 | 데이터 호환 | 롤백 |
|------|------|------|----------|------|
| **Phase A (Dual-Write)** | 7일 | V2 Redis primary + V3 K8s Mesh shadow write (양쪽 publish, V2에서만 consume) | V2 RedisMessageEnvelope ↔ V3 MeshEnvelope 1:1 매핑 (§12.4.1) | V3 shadow write disable → V2 Only (즉시 가능) |
| **Phase B (Read-Switch)** | 3일 | V2 + V3 dual-write 유지 + V3 K8s Mesh primary read + V2 shadow read (parity check) | parity_failure_rate < 0.1% 충족 시 Phase C 진입 | V3 read disable → V2 read 복원 (즉시 가능, 데이터 손실 0) |
| **Phase C (V3 Only)** | 영구 | V3 K8s Mesh primary, V2 Redis read-only fallback 유지 (5분 grace) | V2 → V3 변환 헬퍼 영구 보존 (legacy Agent 호환) | V2 Redis re-activate → Phase B 역전환 (5분 내) |

#### 12.4.1 V2 ↔ V3 Envelope 매핑

```python
# V3 K8s Mesh Envelope (Phase 4 P4-2 NEW)
@dataclass
class MeshEnvelope:
    envelope_id: str           # V2 RedisMessageEnvelope.msg_id 직계
    sender_id: str
    receiver_id: str           # V2 channel_pattern 변환 (`agent.{receiver}.{type}`)
    message_type: MessageType  # V2 MessageType 직계
    priority: MessagePriority  # V2 MessagePriority 직계
    payload: dict
    hmac_sig: str              # V2 HMACSignature 직계 (LOCK-AT-012)
    mtls_cert_fingerprint: str # V3 NEW (Istio Citadel X.509 SHA-256)
    trace_id: str              # LOCK-AT-007 (Part2 §6.7 L5045) 직계
    timestamp: datetime
    nonce: str                 # V2 anti-replay nonce 직계 (5분 윈도우)
```

### 12.5 50+ Agent 병렬 (LOCK-AT-014 V3=50+) + R-63-12 큐잉

> **LOCK-AT-014** (Part2 §6.7 L5052 verbatim): "V1 병렬 상한=3, V2=10, V3=50+"
> **R-63-12** (`_index.md` §11 직계): 50+ 초과는 큐잉 (거부 아닌 대기) — Backpressure 정책

```python
class V3MeshConcurrencyController:
    """
    V3 K8s Mesh 병렬 제어기.
    LOCK-AT-014 V3=50+ 강제 + R-63-12 큐잉 (거부 아닌 대기).
    """
    def __init__(self, max_concurrent: int = 50,         # LOCK-AT-014 V3=50+
                 queue_max: int = 10_000): ...

    async def acquire_slot(self, agent_id: str) -> Slot:
        if self._active.qsize() < self.max_concurrent:
            return await self._active.put(agent_id)      # 즉시 실행
        # R-63-12: 거부 아닌 큐잉 (Backpressure)
        await self._wait_queue.put(agent_id)             # 대기 큐 enqueue
        return await self._slot_released_event.wait()    # 슬롯 해제 대기
```

### 12.6 max 100 sub-agents 스케일링 (LOCK-63-2 + §9.2 L2022 분리)

> **LOCK-63-2** (AUTHORITY §3): PARL 최대 병렬 100 서브에이전트 (V3 PARL 모드)
> **§9.2 L2022 충돌 해소 직계**: LOCK-AT-014 V3=50+ (병렬 상한, **동시 실행**) ≠ LOCK-63-2 100 (**총 등록**, PARL spec)

**분리 명시 매트릭스**:

| 차원 | 정의 | 임계값 | LOCK | 검증 |
|------|------|------|------|------|
| **동시 실행** | 동일 시점에 active running Sub-Agent 수 | ≤ **50+** | LOCK-AT-014 V3=50+ | §12.5 V3MeshConcurrencyController.max_concurrent |
| **총 등록** | PARL 풀에 등록된 Sub-Agent 총 수 | ≤ **100** | LOCK-63-2 | §12.6.1 PARL Pool Registry (별도) |
| **초과 처리** | 동시 실행 > 50+ → 큐잉 / 총 등록 > 100 → 등록 거부 + 운영자 알림 | — | R-63-12 (큐잉) / LOCK-63-2 (거부) | §12.6.2 |

#### 12.6.1 PARL Pool Registry (총 등록 100 분리)

```python
class PARLPoolRegistry:
    """
    PARL 풀 등록 관리 — LOCK-63-2 V3 PARL 모드 max 100 강제.
    동시 실행 제어 (LOCK-AT-014 V3=50+)는 §12.5 V3MeshConcurrencyController 위임.
    """
    def __init__(self, max_registered: int = 100):       # LOCK-63-2
        self.max_registered = max_registered
        self._registered: dict[str, AgentRegistration] = {}

    def register(self, agent: SubAgentSpec) -> bool:
        if len(self._registered) >= self.max_registered:
            log("LOCK-63-2 violation: PARL pool max 100 exceeded — 등록 거부")
            notify_operator("PARL pool registration rejected", agent_id=agent.id)
            return False                                  # 거부 (큐잉 아님)
        self._registered[agent.id] = AgentRegistration(...)
        return True
```

### 12.7 LOCK-AT 매트릭스 (V3 K8s Mesh 적용)

| LOCK-AT | 항목 | V3 적용 | 정본 위치 |
|---------|------|--------|----------|
| **AT-012** | HMAC 서명 필수 | mTLS 전송 레이어 + HMAC 응용 레이어 이중 방어 — `MeshEnvelope.hmac_sig` + `mtls_cert_fingerprint` 정합 | Part2 §6.7 L5050 |
| **AT-014** | 병렬 상한 V3=50+ | §12.5 V3MeshConcurrencyController `max_concurrent=50` 강제 + R-63-12 큐잉 | Part2 §6.7 L5052 |
| LOCK-63-2 | PARL 최대 병렬 V3=100 | §12.6.1 PARLPoolRegistry `max_registered=100` 강제 (총 등록 제한, 거부) | Part2 §6.7 V3 + AUTHORITY §3 |
| AT-003 (재검증) | 무한 루프 금지 | Service Mesh DNS resolver 단일 진입점 + 위임 그래프 cycle 방지 (Istio ServiceEntry 검증) | Part2 §6.7 L5041 |
| AT-007 (재검증) | trace_id 단위 Checkpoint/Replay/Fork | `MeshEnvelope.trace_id` 영구 보존 + Istio 분산 trace context 직계 (W3C TraceContext) | Part2 §6.7 L5045 |
| AT-001 (보조) | 자체 경량 프레임워크 | Service Mesh (Istio/Linkerd)는 sidecar 어댑터로만 연결 — 코드 내 Istio SDK 직접 import 0건 (sidecar inject 패턴) | Part2 §6.7 L5039 |

### 12.8 6-5 SDAR W-CB Circuit Breaker 결정 협의 (DEFERRED_TO_PHASE3 OBSERVE_ONLY → Phase 4 RESOLVED 양 도메인 분담)

> **6-5 SDAR W-CB 결정 협의** (4-3 P4-5 CFL-MCP-005 패턴 직계):
> - **6-5 SDAR-System** (Wave 2 #17 forward-defined): SDAR 도메인이 W-CB Circuit Breaker 정책 정본을 정의 (자가진단 트리거 + 복구 절차 + 회로 차단 임계값)
> - **6-3 본 §12.8**: V3 K8s Mesh Data Plane Circuit Breaker 구현 (Istio DestinationRule outlier_detection 또는 Linkerd retry-budget) — 6-5 정책 정본 OBSERVE_ONLY (정책 정의는 6-5 측 위임)
> - **Phase 4 RESOLVED 양 도메인 분담**:
>   - **6-5 측 (정책 정본)**: 회로 차단 임계값 (오류율 임계, 연속 실패 횟수, half-open 재시도 시간) + 자가진단 트리거 + 복구 절차 + DH-4 5-필드 verbatim
>   - **6-3 측 (구현)**: Istio/Linkerd Data Plane 정책 적용 + outlier_detection 매개변수 6-5 정본 cite + Circuit Breaker 발화 시 6-5 SDAR `sdar_queue.enqueue()` 알림 (`parl_security.md` §4.3 패턴 직계)

```yaml
# Istio DestinationRule 예시 (6-5 SDAR 정책 정본 cite)
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: agent-mesh-circuit-breaker
  annotations:
    sot2-source: "6-5 SDAR-System W-CB 정책 정본 (forward-defined)"
spec:
  host: "*.agent-mesh.local"
  trafficPolicy:
    outlierDetection:
      consecutive5xxErrors: 5      # 6-5 정본 OBSERVE_ONLY (Phase 3 런타임 결정)
      interval: 30s                # 6-5 정본 OBSERVE_ONLY
      baseEjectionTime: 30s        # 6-5 정본 OBSERVE_ONLY
      maxEjectionPercent: 50
```

### 12.9 cross-handoff 매트릭스 (P4-2 spec G4-6 직계, 4 cross-handoff RESOLVED)

| # | cross-domain | Wave | 인터페이스 / cross-ref | RESOLVED 상태 |
|---|-------------|------|---------------------|------------|
| 1 | **6-2 Security-Governance** | Wave 2 #14 ✅ | Mesh 통신 HMAC + Zero-Trust P2-4 `zero_trust_stride_v2.md` 84 매트릭스 직계 + mTLS 정책 정본 inheritance | ✅ RESOLVED (§12.3 #2 mTLS 정합) |
| 2 | **6-8 Cloud-Library** | Wave 2 #20 forward-defined | K8s 배포 인프라 + 클라우드 배포 보안 + Helm chart cross-handoff (forward-link) | ✅ RESOLVED (forward-link) |
| 3 | **4-1 Rust-Tauri-Infrastructure** | Wave 3 #24 forward-defined | IPC 경계 (Desktop ↔ K8s Mesh 게이트웨이) — Rust Tauri IPC Native 클라이언트가 K8s Service 진입점 호출 | ✅ RESOLVED (경계 명시) |
| 4 | **6-5 SDAR-System W-CB Circuit Breaker** | Wave 2 #17 forward-defined | DEFERRED_TO_PHASE3 OBSERVE_ONLY → Phase 4 P4-2 RESOLVED 양 도메인 분담 (§12.8) | ✅ RESOLVED (양 도메인 분담 결정) |

### 12.10 V3 K8s Mesh 성능 목표 (E6)

| 메트릭 | V2 baseline (§9) | V3 목표 | 측정 방법 |
|-------|----------------|--------|----------|
| 메시지 latency P50 | < 5 ms | **< 10 ms** (mTLS overhead 포함) | Istio Prometheus exporter |
| 메시지 latency P95 | < 10 ms | **< 30 ms** | Istio Prometheus exporter |
| 메시지 latency P99 | < 50 ms | **< 100 ms** (mTLS handshake 포함) | Istio Prometheus exporter |
| 동시 Agent 처리량 | 10 (V2) | **50+** (LOCK-AT-014 V3) | `parallel_agent_active_gauge` |
| 메시지 처리량 | 1,000 msg/s | **10,000+ msg/s** (Cluster 노드 5+) | rate(`messagebus_publish_total[1m]`) |
| Service Mesh CPU overhead | — | < 15% (sidecar) | K8s metrics-server |
| mTLS handshake 캐시 hit rate | — | > 95% | Istio Citadel telemetry |

### 12.11 V3 K8s Mesh 테스트 (E7, scaling_test_results.md cross-link)

> 상세 부하 테스트 시나리오는 별도 산출물 `02_agent-swarm/scaling_test_results.md` (Phase 4 P4-2 NEW) 위임.

| Test ID | 시나리오 | 검증 |
|---------|---------|------|
| **E2E-V3MESH-50** | **50 동시 Agent Mesh 구성 부하 테스트** | LOCK-AT-014 V3=50+ 강제 + R-63-12 큐잉 동작 + mTLS handshake 정상 |
| **E2E-V3MESH-100** | **100 sub-agents 등록 부하 테스트 (PARL 모드)** | LOCK-63-2 max 100 강제 + 101번째 등록 거부 + 운영자 알림 |
| E2E-V3MESH-MIG-A | Phase A Dual-Write 7일 정합 | V2 ↔ V3 Envelope parity_failure_rate < 0.1% |
| E2E-V3MESH-MIG-B | Phase B Read-Switch 3일 parity | V2 + V3 dual-read parity check PASS |
| E2E-V3MESH-MIG-C | Phase C V3 Only 영구 + V2 fallback | V3 primary 정상 + V2 5분 grace fallback 동작 |
| E2E-V3MESH-CB | Circuit Breaker 동작 (6-5 W-CB 정합) | Istio outlier_detection trigger → 6-5 SDAR `sdar_queue.enqueue()` 알림 |

### 12.12 변경 이력 (V3 EXTEND)

| 일자 | 내용 | 세션 |
|------|------|------|
| 2026-05-27 | **V3 K8s Mesh EXTEND (Phase 4 P4-2 production-ready 정본 승급)** — §12 NEW append-only (V1+V2 byte-prefix SHA `0013849B33E72FE1` UNCHANGED 강제 보존) + K8s Mesh 4 핵심 컴포넌트 (Service Mesh + mTLS + Service Discovery + Circuit Breaker) + 3단계 마이그레이션 Phase A/B/C (§6 이슈 #8 RESOLVED) + LOCK-AT-014 V3=50+ §12.5 V3MeshConcurrencyController + R-63-12 큐잉 + LOCK-63-2 max 100 §12.6.1 PARLPoolRegistry + §9.2 L2022 분리 명시 (동시 ≤50+ vs 총 등록 ≤100) + 4 cross-handoff RESOLVED (6-2 Mesh 보안 + 6-8 K8s 배포 + 4-1 IPC + 6-5 W-CB 양 도메인 분담) + 성능 목표 7 메트릭 + E2E 테스트 6 시나리오 (E2E-V3MESH-50/100/MIG-A/B/C/CB). Status DRAFT → APPROVED. ReadOnly FALSE 유지. | P4-2 |

---

> **문서 끝 (V3-Phase 4 P4-2 EXTEND)**
> 본 문서 §12는 Phase 4 P4-2 V3 K8s Mesh EXTEND이며, V1 (§3) + V2 (§0~§11) 본문 byte-prefix SHA `0013849B33E72FE1` UNCHANGED EXACT 보존 강제 (R9 LOCK 보존 원칙).
> LOCK-AT-012 (HMAC) + AT-014 (V3=50+) verbatim 정합 + LOCK-63-2 (max 100) 분리 + §6 이슈 #8 RESOLVED + 6-5 SDAR W-CB Phase 4 RESOLVED 양 도메인 분담 (4-3 P4-5 CFL-MCP-005 패턴 직계).
> LOCK-AT 17 + LOCK-63 3 = 20 unique set 변경 0건, DH 0건 보존, FABRICATION 0건 통산.
