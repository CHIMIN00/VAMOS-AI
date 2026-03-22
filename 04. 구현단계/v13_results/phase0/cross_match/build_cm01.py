import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r"D:\VAMOS\04. 구현단계\v13_results\phase0\extraction"
files = sorted([f for f in os.listdir(BASE) if f.endswith('.json')])

ea_map = {
    'v13_EA01_claude_md.json': 'EA-1',
    'v13_EA02_base_plan.json': 'EA-2',
    'v13_EA03_master_spec.json': 'EA-3',
    'v13_EA04_d20_01_02.json': 'EA-4',
    'v13_EA05_d20_03_04.json': 'EA-5',
    'v13_EA06_d20_05_06.json': 'EA-6',
    'v13_EA07_d20_07_08.json': 'EA-7',
    'v13_EA08_d21_schemas.json': 'EA-8',
    'v13_EA09_phase_b1_b3.json': 'EA-9',
    'v13_EA10_phase_b4_b7.json': 'EA-10',
    'v13_EA11_spec_4.json': 'EA-11',
    'v13_EA12_step7_spec.json': 'EA-12',
    'v13_EA13_step7_guides.json': 'EA-13',
    'v13_EA14_step7_rest.json': 'EA-14',
    'v13_EA15_etc.json': 'EA-15',
}

all_c1 = {}
total_c1_count = 0

for fname in files:
    ea_agent = ea_map.get(fname, fname)
    fpath = os.path.join(BASE, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = data.get('items', [])
    for item in items:
        if item.get('category') == 'C1':
            total_c1_count += 1
            key = item.get('key', '')
            if key not in all_c1:
                all_c1[key] = []
            all_c1[key].append({
                'ea_agent': ea_agent,
                'item_id': item.get('item_id', ''),
                'source_file': item.get('source_file', ''),
                'source_line': item.get('source_line', None),
                'source_text': item.get('source_text', ''),
                'value': item.get('value', None),
                'value_type': item.get('value_type', ''),
                'context': item.get('context', ''),
            })

multi = {k: v for k, v in all_c1.items() if len(v) > 1}
single = {k: v for k, v in all_c1.items() if len(v) == 1}

def make_sources(items):
    return [{
        'ea_agent': s['ea_agent'],
        'item_id': s['item_id'],
        'source_file': s['source_file'],
        'source_line': s['source_line'],
        'source_text': s['source_text'],
        'value': s['value'],
    } for s in items]

comparisons = []
cmp_id = 1

# ================================================
# MULTI-SOURCE COMPARISONS (21 unique multi keys)
# ================================================

# 001 AINV_DATA_SOURCE_COUNT
k = 'AINV_DATA_SOURCE_COUNT'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-3(number:83)과 EA-15(string:"83") 모두 83으로 일치. 타입 표현만 다르고 값은 동일. 의미론적으로 동등.',
    'recommendation': '구현 시 number 타입(83)으로 통일 권장.',
})
cmp_id += 1

# 002 AINV_STRATEGY_COUNT
k = 'AINV_STRATEGY_COUNT'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-3(number:96)과 EA-15(string:"96") 모두 96으로 일치. 타입 표현만 다르고 값은 동일.',
    'recommendation': '구현 시 number 타입(96)으로 통일 권장.',
})
cmp_id += 1

# 003 API_CALL_RATE_PER_MIN
k = 'API_CALL_RATE_PER_MIN'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-3(60)과 EA-5(60) 완전 일치. EA-5는 Burst 제한(10초 내 10회) 추가 명시이나 기본 RPM 값은 동일.',
    'recommendation': '일치. 현행 유지.',
})
cmp_id += 1

# 004 API_ENDPOINT_COUNT
k = 'API_ENDPOINT_COUNT'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-1(88), EA-3(88), EA-9(88) 3개 소스 완전 일치.',
    'recommendation': '일치. 현행 유지.',
})
cmp_id += 1

# 005 BACKUP_RETENTION_DAYS
k = 'BACKUP_RETENTION_DAYS'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-3(7)과 EA-5(7) 완전 일치. 최근 7일분 보존 정책 동일.',
    'recommendation': '일치. 현행 유지.',
})
cmp_id += 1

# 006 C1_FAILURE_CODE_COUNT
k = 'C1_FAILURE_CODE_COUNT'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-1(20)과 EA-9(20) 완전 일치. D2 FailureCodeRegistry 실패코드 수 20개 동일.',
    'recommendation': '일치. 현행 유지.',
})
cmp_id += 1

# 007 C1_L0_TTL_MAX_DAYS
k = 'C1_L0_TTL_MAX_DAYS'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-6 내 두 항목 모두 30일로 동일. 동일 소스 파일 내 다른 섹션에서 중복 추출된 것으로 실질적 단일 소스.',
    'recommendation': '일치. EA-6 내 중복 추출 항목임.',
})
cmp_id += 1

# 008 C1_L1_TTL_DAYS
k = 'C1_L1_TTL_DAYS'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-1(90일)과 EA-6(90일, 2개 중복 추출) 완전 일치. L1 프로젝트 메모리 기본 TTL 90일 확정.',
    'recommendation': '일치. 현행 유지.',
})
cmp_id += 1

# 009 C1_V2_STORAGE_COST_MONTHLY
k = 'C1_V2_STORAGE_COST_MONTHLY'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': '동일 EA-6 내 두 방식 추출: 서술형("~$40/월", string)과 숫자형(40, number). 의미론적 동등. 실질적 단일 소스. ~$40 표기는 근사치 표현.',
    'recommendation': '구현 시 숫자형(40)과 단위($USD/월)를 분리 사용 권장.',
})
cmp_id += 1

# 010 C1_V3_STORAGE_COST_MONTHLY
k = 'C1_V3_STORAGE_COST_MONTHLY'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': '동일 EA-6 내 두 방식 추출: 서술형("~$150/월", string)과 숫자형(150, number). 의미론적 동등. 실질적 단일 소스.',
    'recommendation': '구현 시 숫자형(150)과 단위($USD/월)를 분리 사용 권장.',
})
cmp_id += 1

# 011 C1_VECTOR_SEARCH_DEFAULT_TOP_K
k = 'C1_VECTOR_SEARCH_DEFAULT_TOP_K'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'INCONSISTENT',
    'severity': 'WARNING',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-6(10)과 EA-9(5) 불일치. EA-6: VectorStore 어댑터 search() 함수 기본값 top_k=10 (Python 백엔드). EA-9: TypeScript API 인터페이스 기본값 top_k=5 (프론트엔드/IPC). 서로 다른 계층의 기본값이나 실제 검색 결과 수에 영향.',
    'recommendation': 'API 레이어(EA-9, top_k=5)와 VectorStore 레이어(EA-6, top_k=10) 간 기본값 통일 필요. 최종 SOT 결정 후 양 계층 동기화.',
})
cmp_id += 1

# 012 CORE_MODULE_COUNT
k = 'CORE_MODULE_COUNT'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'SOURCE_CONFLICT',
    'severity': 'WARNING',
    'sources': make_sources(all_c1[k]),
    'analysis': ('3개 소스 다른 값: EA-1(23: CORE/CORE(LOCK) status 모듈 수), EA-3(6: "핵심 철학 6대 원칙" - 모듈 수가 아님), EA-11(3, 3: V1 최대 병렬 에이전트 수 - 모듈 수가 아님). '
                 'EA-3와 EA-11은 CORE_MODULE_COUNT 키를 다른 개념에 잘못 사용. EA-1의 23이 실제 CORE 상태 모듈 수.'),
    'recommendation': 'CORE_MODULE_COUNT=23(EA-1)이 정확한 값. EA-3 항목(6)은 CORE_PRINCIPLE_COUNT로, EA-11 항목(3)은 AGENT_PARALLEL_MAX_V1로 재분류 필요.',
})
cmp_id += 1

# 013 COST_CEILING_DAILY
k = 'COST_CEILING_DAILY'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': ('다중 소스, 다중 표현 형식이나 값 일치. '
                 'V1: 1300원/$1 (EA-3, EA-15), V2: 3100원/$2.3 (EA-3, EA-11), V3: 8900원/$6.7 (EA-3, EA-11). '
                 'EA-10: JSON 구조체 {V1:1300, V2:3100, V3:8900} (KRW). '
                 '모든 소스 간 수치 완전 일치. 표현 형식(KRW/USD/JSON/string)만 다름.'),
    'recommendation': '일치. EA-10의 JSON 구조체 형식이 구현에 최적. 현행 유지.',
})
cmp_id += 1

# 014 COST_CEILING_MONTHLY
k = 'COST_CEILING_MONTHLY'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': ('다중 소스, 다중 표현 형식이나 값 일치. '
                 'V1: 40000원/$30, V2: 93000원/$70, V3: 266000원/$200 (EA-3). '
                 'EA-10: JSON {V1:40000, V2:93000, V3:266000}. EA-15: V1=40000, V2=93000, V3=266000. '
                 '모든 소스 완전 일치.'),
    'recommendation': '일치. 현행 유지.',
})
cmp_id += 1

# 015 HIGH_COST_MODEL_RATE_PER_MIN
k = 'HIGH_COST_MODEL_RATE_PER_MIN'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-3(3)과 EA-5(3) 완전 일치. 고비용 모델 분당 호출 제한 3회 동일.',
    'recommendation': '일치. 현행 유지.',
})
cmp_id += 1

# 016 HITL_CONFIDENCE_THRESHOLD
k = 'HITL_CONFIDENCE_THRESHOLD'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'INCONSISTENT',
    'severity': 'WARNING',
    'sources': make_sources(all_c1[k]),
    'analysis': ('EA-3(0.5, float 0~1 스케일: "confidence < 0.5 시 HITL")과 EA-5(70, 퍼센트(%): "Confidence < 70% 시 HITL") 불일치. '
                 '단위 변환 후에도 0.5(=50%)와 70(=70%)로 수치 차이 존재. '
                 'EA-3는 코드 내 float 타입(Python confidence score), EA-5는 UI/문서 퍼센트 표기. '
                 '50%와 70%는 서로 다른 HITL 개입 임계값으로 실제 동작에 영향.'),
    'recommendation': ('SOT를 EA-3 또는 EA-5 중 하나로 결정 필요. '
                       '0.5(50%) vs 70% 중 의도한 임계값 확인 후 모든 소스 동기화. '
                       'HITL 개입 빈도에 직접 영향을 미치는 파라미터이므로 신속한 결정 필요.'),
})
cmp_id += 1

# 017 MCP_MAX_RETRIES
k = 'MCP_MAX_RETRIES'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-3(2)과 EA-5(2) 완전 일치. MCP 일시적 실패 시 최대 재시도 횟수 2회 동일.',
    'recommendation': '일치. 현행 유지.',
})
cmp_id += 1

# 018 OPENAI_CACHE_DISCOUNT_PCT
k = 'OPENAI_CACHE_DISCOUNT_PCT'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'CONSISTENT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': 'EA-3(50)과 EA-5(50) 완전 일치. OpenAI Automatic Caching 할인율 50% 동일.',
    'recommendation': '일치. 현행 유지.',
})
cmp_id += 1

# 019 THRESHOLD_VALUE
k = 'THRESHOLD_VALUE'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'SOURCE_CONFLICT',
    'severity': 'INFO',
    'sources': make_sources(all_c1[k]),
    'analysis': ('EA-11 내에서만 발생하는 단일 소스 내 키 충돌. THRESHOLD_VALUE 키에 20개 서로 다른 임계값 할당: '
                 'agent_budget_ratio=0.8, max_conversation_turns_p0=5, max_tee_iterations_p0=3, '
                 'skill_fit_weight=0.4, min_win_rate=0.51, min_sharpe=1.0, circuit_daily_loss=-0.03, '
                 'position_stop_loss=-0.1, max_position_size=0.1, ddof=1, annualization_factor=252, '
                 'current_win_rate=61.8, current_pf=1.74, mdd_limit=0.1, cb4_feasibility=86, '
                 'daily_version_limit=5, max_sdar_instances=3, max_auto_repairs=3, observation_period_s=300, snapshot_retention_hours=168. '
                 '모두 실질적으로 다른 파라미터를 동일 키명으로 잘못 분류한 EA-11 내부 추출 오류.'),
    'recommendation': '각 임계값에 고유한 키명 사용 필요. THRESHOLD_VALUE는 너무 일반적인 키명으로 EA-11 재추출 시 수정 요망.',
})
cmp_id += 1

# 020 TIMEOUT_DEFAULT
k = 'TIMEOUT_DEFAULT'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'INCONSISTENT',
    'severity': 'WARNING',
    'sources': make_sources(all_c1[k]),
    'analysis': ('EA-1(10: "승인 타임아웃 10분 미응답 → 자동 거부")과 EA-10(JSON: V1=30000ms, V2=30000ms, V3=60000ms: "Decision Kernel 최대 타임아웃") 불일치. '
                 '단위 변환: EA-1의 10분=600,000ms. EA-10 V3=60,000ms=1분. '
                 '수치가 다를 뿐 아니라 대상 컨텍스트 자체가 다름: EA-1은 HITL/사용자 승인 대기 타임아웃, EA-10은 내부 AI Decision Kernel 처리 타임아웃.'),
    'recommendation': ('TIMEOUT_DEFAULT 키가 두 다른 개념에 사용되어 모호함. '
                       'APPROVAL_TIMEOUT_MINUTES(=10, EA-1)와 DECISION_KERNEL_TIMEOUT_MS(V1/V2=30000, V3=60000, EA-10)로 분리 명명 필요.'),
})
cmp_id += 1

# 021 TOTAL_MODULE_COUNT
k = 'TOTAL_MODULE_COUNT'
comparisons.append({
    'comparison_id': f'CM-1_{cmp_id:03d}',
    'key': k,
    'result': 'SOURCE_CONFLICT',
    'severity': 'WARNING',
    'sources': make_sources(all_c1[k]),
    'analysis': ('EA-1(81: "모듈 시스템 전체 81개")과 EA-15(string:"81": "4계층/5Phase/9State/5Gate/81모듈")은 일치. '
                 'EA-11이 동일 키에 6개 다른 값 할당: '
                 '3=최대위임깊이, 27=RSI_BB파라미터조합, 56=전략파일수, 10=Cloud_Library레이어수, 30=Cloud_Library기능수, 5=SDAR파이프라인레이어. '
                 'EA-11의 모든 항목은 총 모듈 수가 아닌 다른 개념이므로 잘못된 키 분류.'),
    'recommendation': ('TOTAL_MODULE_COUNT=81(EA-1, EA-15 일치)이 정확. '
                       'EA-11의 항목들은 각각 MAX_DELEGATION_DEPTH(3), RSI_BB_PARAM_COMBINATIONS(27), '
                       'STRATEGY_FILE_COUNT(56), CLOUD_LIBRARY_LAYERS(10), CLOUD_LIBRARY_FEATURES(30), '
                       'SDAR_PIPELINE_LAYERS(5)로 재분류 필요.'),
})
cmp_id += 1

# ==================================================
# SINGLE-SOURCE comparisons (all 1177 single-source keys)
# ==================================================
single_keys_sorted = sorted(single.keys())
for key in single_keys_sorted:
    items = all_c1[key]
    s = items[0]
    comparisons.append({
        'comparison_id': f'CM-1_{cmp_id:03d}',
        'key': key,
        'result': 'SINGLE_SOURCE',
        'severity': 'INFO',
        'sources': make_sources(items),
        'analysis': f'단일 소스({s["ea_agent"]})에서만 추출됨. 교차 검증 불가.',
        'recommendation': '단일 소스 항목. 구현 시 해당 소스 문서를 SOT로 사용.',
    })
    cmp_id += 1

# Count results
result_counts = {'CONSISTENT': 0, 'INCONSISTENT': 0, 'SOURCE_CONFLICT': 0, 'SINGLE_SOURCE': 0}
severity_counts = {'CRITICAL': 0, 'WARNING': 0, 'INFO': 0}
for c in comparisons:
    result_counts[c['result']] = result_counts.get(c['result'], 0) + 1
    severity_counts[c['severity']] = severity_counts.get(c['severity'], 0) + 1

output = {
    'metadata': {
        'agent': 'CM-1',
        'category': 'C1',
        'version': 'v13',
        'created': '2026-03-17',
        'description': 'C1(Numeric/Parameter) 항목 교차 검증 결과. 15개 EA 파일에서 추출한 1263개 C1 항목(1198개 고유 키) 분석.',
        'total_c1_items_extracted': total_c1_count,
        'total_unique_keys': len(all_c1),
        'multi_source_keys': len(multi),
        'single_source_keys': len(single),
        'total_comparisons': len(comparisons),
        'results': result_counts,
        'severity': severity_counts,
        'known_issues_note': (
            'IMMUTABLE_ZONE_COUNT(7)는 EA-11에서 C1으로 추출됨 → SINGLE_SOURCE 처리. '
            'NEVER_AUTO_COUNT(EA-1:10, EA-3:6, EA-11:10, EA-15:6)는 C2 카테고리로 C1 범위 외 → CM-2에서 처리 필요. '
            '불일치A(정책수준7 vs 시행수준10)는 IMMUTABLE_ZONE_COUNT(C1:7)와 NEVER_AUTO_COUNT(C2:10/6) 간 개념 범위 차이로 다른 카테고리 비교임.'
        ),
    },
    'comparisons': comparisons,
}

outpath = r"D:\VAMOS\04. 구현단계\v13_results\phase0\cross_match\v13_CM01_values.json"
with open(outpath, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print('Written:', outpath)
print(f'Total comparisons: {len(comparisons)}')
print(f'Results: {result_counts}')
print(f'Severity: {severity_counts}')
