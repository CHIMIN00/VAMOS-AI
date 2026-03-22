# Before Fix 002 — FG-B02: V2→V3 전환조건 Loki+Grafana 시간 모순 해소
# Snapshot at: 2026-03-12
# Decision: A (전환조건에서 삭제)

## L2566 (§5 V3 Phase 1 사용자 직접 작업 #7)
```
7. **V2→V3 전환 조건 확인**: QoD ≥ 0.90 (60일), 2-tier LLM 최적화 완료, P1 고급 테스트 통과, Self-evo 시스템 검증, V3 비용 리뷰 + 승인, Loki+Grafana 배포 완료
```

## L4229-4230 (§7.3 V2→V3 전환 조건)
```
QoD ≥ 0.90 (60일) / 2-tier LLM 최적화 완료 / P1 고급 테스트 통과
Self-evo 체계 검증 / V3 비용 재검토 + 승인 / Loki+Grafana 배포
```

## 참고: 유지되는 Loki+Grafana 항목 (V3-Phase 1 구축)
- L2542: V3 인프라 테이블 (Loki + Grafana 항목)
- L2641: V3-Phase 1 구현 섹션 (Loki + Grafana Observability)
- L2691: V3-Phase 1 완료 검증 체크리스트
