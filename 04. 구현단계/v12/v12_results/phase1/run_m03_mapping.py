#!/usr/bin/env python3
"""M-3 Agent: Map V2 features to PART2 §4 — improved matching"""
import json, re, os

# Load feature registry
with open(r'D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_feature_registry_final.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

v2_features = [ft for ft in registry['features'] if ft.get('version_scope') == 'V2']
print(f'V2 features: {len(v2_features)}')

# Load PART2
with open(r'D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md', 'r', encoding='utf-8') as f:
    all_lines = f.readlines()

s4_lines = all_lines[2676:3461]  # lines 2677-3461
s6_lines = all_lines[4180:5858]  # lines 4181-5858

# Minimum score threshold for a match to count
MIN_MATCH_SCORE = 8  # At least a 4-char specific term match

def find_in_section(feature, lines, offset):
    name = feature['feature_name']
    src_text = feature.get('source_text', '')
    desc = feature.get('feature_description', '')
    combined = name + ' ' + src_text + ' ' + desc

    # Build search terms with weights
    # (term, weight_multiplier) - higher weight = more specific
    weighted_terms = []

    # Module IDs like I-7, E-15, A-4, I-25 — very specific
    for m in re.findall(r'[IAEM]-\d+', combined):
        weighted_terms.append((m, 5))

    # S7 references — very specific
    for m in re.findall(r'S7[A-Z]*-\d+', src_text):
        weighted_terms.append((m, 6))

    # v10 reference IDs like AINV-056, D202-059, S7AE-344, CLIB-057 — very specific
    for m in re.findall(r'[A-Z]+\d*-\d+', src_text):
        if len(m) > 5:
            weighted_terms.append((m, 6))

    # Feature-specific technical terms (multi-word, very specific)
    specific_terms_high = [
        'SQLite → PostgreSQL', 'JSONL → PostgreSQL', 'Chroma → Qdrant',
        'JSON → Neo4j', 'Docker Compose', 'config.v2.toml',
        'Redis MessageBus', 'HMAC-SHA256', 'LlamaGuard',
        'RT-BNP', 'DCL-GEO', 'SDAR Engine', 'AR-L2', 'AR-L3',
        'Debate Mode', 'Workflow Builder', 'SHAP/LIME',
        'MemGPT/Letta', 'Cognee', 'FinGPT', 'Qwen 3',
        'CrewAI', 'Zettelkasten', 'Zapier/Make', 'JIRA/Linear',
        'Notion/Obsidian', 'Cloud Library', 'Cloud Collector',
        'Breaking Detector', 'Circuit Breaker', 'Agent Teams',
        'Computer Use', 'A2A 프로토콜', 'REST API', 'Agent SDK',
        'VamosAgent', 'TaskBoard', 'File Ownership',
        'OAuth2', 'TOTP', 'WebAuthn', 'Canary 배포', 'Blue-Green',
        'TimescaleDB', 'Alembic', 'Dual-Collection',
        'BGE-M3', 'HNSW', 'BaseModule', 'BaseGate',
        'Self-RAG', 'GraphRAG', 'NeMo Guardrails', 'GuardrailsAI',
        '51% Gate', 'AINV', 'Self-evo', 'Dream Mode',
        'DSPy', 'AutoGen', 'Multi-Persona',
        'Adaptive Thinking', 'reasoning_budget', 'think_depth',
        'Immutable Zone', 'Kill Switch', 'NEVER_AUTO',
        'Personal Constitution', 'EU AI Act',
        'Quant Agent', 'Content Agent', 'Trading Agent',
        'Productivity Agent', 'Critic Agent', 'SDAR Agent',
        '7-Stage Discovery', '10-Step Migration',
        'LOCK-AT', 'HandoffPacket', 'AgentPool',
        'repair_success_rate', 'Backtesting',
        'I-7 Project', 'I-12 Workflow', 'I-22 Task', 'I-23 Doc',
        'I-25 SDAR', 'A-4 Debate', 'E-13 Calendar', 'E-14 Email',
        'E-15 Cloud', 'E-16 Cloud Storage',
        'Project/Session Manager', 'Task/Project Manager',
        'Doc/Code Structuring',
    ]
    for term in specific_terms_high:
        if term.lower() in combined.lower():
            weighted_terms.append((term, 4))

    # Moderately specific terms
    specific_terms_med = [
        'SDAR', 'GDPR', 'HMAC', 'Kafka', 'CQRS', 'CDN',
        'Qdrant', 'Neo4j', 'PostgreSQL', 'Redis',
        'Grafana', 'Prometheus', 'RBAC',
        'Explainability', 'backtest',
        'delegation', '핸드오프', 'Handoff',
        '마이그레이션', '자가진단', '자동수리',
        '배치 처리', '분산 트레이싱', '백프레셔',
        '읽기 복제본', '사가 패턴', '국제화', '접근성',
        '작업 큐', '검색 엔진 서버', '알림 서버', '피처 스토어', '방화벽',
        '스타일 트랜스퍼', '화자 분리', '크로스모달',
        '코드 변환', '개인 위키', '학습 경로', '시험 준비',
        '교육 컨텐츠', '교육 평가', '수면 개선', '피트니스',
        '식단', '감정 일지', '사회적 관계', '건강 인사이트',
        '음악 추천', '웰빙 대시보드', '학습 분석',
        '언어 학습', '인포그래픽', '스크린 캡처',
        '예측적 지식', '감정 패턴', '편향 감사',
        '지식 신선도', '지식 충돌', '멀티미디어 라이브러리',
        'Ambient Intelligence', '피드백 학습', '규칙 제안',
        '형태소 분석', '자기진화', '자율 코딩',
        '파일 소유권', '공유 작업', '협업 패턴',
        '프로젝트 컨텍스트', '태스크 관리', '문서 구조화',
        '캘린더', '이메일 처리', '클라우드 스토리지',
        '시간 여행', 'A/B 테스팅', '작업 패턴',
        '지식 임포트', 'Recall', '타임라인뷰',
        '행동예측', '프로젝트 세션',
        'idle_timeout', 'session_end',
    ]
    for term in specific_terms_med:
        if term.lower() in combined.lower():
            weighted_terms.append((term, 3))

    # E-0xx operation module IDs - very specific
    e_modules = re.findall(r'E-0\d\d', combined)
    for em in e_modules:
        weighted_terms.append((em, 5))

    # Key multi-word phrases from feature name (4+ word length pieces)
    name_words = [w for w in name.split() if len(w) >= 5]
    for w in name_words:
        # Skip very common words
        if w.lower() not in {'agent', '에이전트', '모듈', '시스템', '구현', '관리', '기반', '통합', '설계', '엔진', '패턴'}:
            weighted_terms.append((w, 2))

    best_match = None
    best_score = 0

    for term, weight in weighted_terms:
        if not term or len(term) < 2:
            continue
        try:
            pat = re.escape(term)
            for i, line in enumerate(lines):
                if re.search(pat, line, re.IGNORECASE):
                    line_num = offset + i + 1
                    matched = line.strip()[:50]
                    score = len(term) * weight
                    # Bonus for exact feature name match
                    if name.lower() in line.lower():
                        score += 200
                    # Bonus for feature_id match
                    if feature['feature_id'] in line:
                        score += 150
                    if score > best_score:
                        best_score = score
                        best_match = (line_num, matched, score)
        except:
            pass

    if best_match and best_match[2] >= MIN_MATCH_SCORE:
        return (best_match[0], best_match[1])
    return None


def determine_s4_section(line_num):
    if line_num <= 2685:
        return '§4'
    elif line_num <= 2851:
        return '§4.P1'
    elif line_num <= 3278:
        return '§4.P2'
    else:
        return '§4.P3'


def determine_s6_section(line_num):
    boundaries = [
        (4181, 4285, '§6.1'), (4286, 4320, '§6.2'), (4321, 4452, '§6.3'),
        (4453, 4475, '§6.4'), (4476, 4576, '§6.5'), (4577, 4608, '§6.6'),
        (4609, 4738, '§6.7'), (4739, 4860, '§6.8'), (4861, 4973, '§6.9'),
        (4974, 5236, '§6.10'), (5237, 5424, '§6.11'), (5425, 5541, '§6.12'),
        (5542, 5858, '§6.13')
    ]
    for start, end, sec in boundaries:
        if start <= line_num <= end:
            return sec
    return '§6'


results = []
stats = {'MATCHED': 0, 'PARTIAL': 0, 'MISSING': 0, 'SPREAD': 0, 'NOT_APPLICABLE': 0}

for ft in v2_features:
    fid = ft['feature_id']
    fname = ft['feature_name']
    src_file = ft.get('source_file', '')
    src_line = ft.get('source_line', 0)
    src_text = ft.get('source_text', '')[:50]
    extractable = ft.get('extractable', True)
    priority = ft.get('priority', '')

    if not extractable:
        result = {
            'feature_id': fid,
            'feature_name': fname,
            'status': 'NOT_APPLICABLE',
            'part2_section': None,
            'part2_line': None,
            'part2_text': None,
            'evidence_source': src_file,
            'evidence_line': src_line,
            'evidence_text': src_text,
            'severity': None,
            'notes': 'extractable=false'
        }
        results.append(result)
        stats['NOT_APPLICABLE'] += 1
        continue

    s4_match = find_in_section(ft, s4_lines, 2676)
    s6_match = find_in_section(ft, s6_lines, 4180)

    if s4_match and s6_match:
        s4_sec = determine_s4_section(s4_match[0])
        s6_sec = determine_s6_section(s6_match[0])
        result = {
            'feature_id': fid,
            'feature_name': fname,
            'status': 'SPREAD',
            'part2_section': s4_sec,
            'part2_line': s4_match[0],
            'part2_text': s4_match[1][:50],
            'evidence_source': src_file,
            'evidence_line': src_line,
            'evidence_text': src_text,
            'severity': None,
            'notes': f'primary={s4_sec}, secondary=[{s6_sec}] line {s6_match[0]}'
        }
        results.append(result)
        stats['SPREAD'] += 1
    elif s4_match:
        s4_sec = determine_s4_section(s4_match[0])
        result = {
            'feature_id': fid,
            'feature_name': fname,
            'status': 'MATCHED',
            'part2_section': s4_sec,
            'part2_line': s4_match[0],
            'part2_text': s4_match[1][:50],
            'evidence_source': src_file,
            'evidence_line': src_line,
            'evidence_text': src_text,
            'severity': None,
            'notes': ''
        }
        results.append(result)
        stats['MATCHED'] += 1
    elif s6_match:
        s6_sec = determine_s6_section(s6_match[0])
        sev = 'MEDIUM'
        if priority == 'CRITICAL':
            sev = 'BLOCKER'
        elif priority == 'HIGH':
            sev = 'HIGH'
        elif priority == 'LOW':
            sev = 'LOW'
        result = {
            'feature_id': fid,
            'feature_name': fname,
            'status': 'PARTIAL',
            'part2_section': s6_sec,
            'part2_line': s6_match[0],
            'part2_text': s6_match[1][:50],
            'evidence_source': src_file,
            'evidence_line': src_line,
            'evidence_text': src_text,
            'severity': sev,
            'notes': f'§6 참조만 존재 ({s6_sec}), §4에 직접 가이드 없음'
        }
        results.append(result)
        stats['PARTIAL'] += 1
    else:
        sev = 'MEDIUM'
        if priority == 'CRITICAL':
            sev = 'BLOCKER'
        elif priority == 'HIGH':
            sev = 'HIGH'
        elif priority == 'LOW':
            sev = 'LOW'
        result = {
            'feature_id': fid,
            'feature_name': fname,
            'status': 'MISSING',
            'part2_section': None,
            'part2_line': None,
            'part2_text': None,
            'evidence_source': src_file,
            'evidence_line': src_line,
            'evidence_text': src_text,
            'severity': sev,
            'notes': '§4, §6 어디에도 매칭 없음'
        }
        results.append(result)
        stats['MISSING'] += 1

# §4.P2 special check: count how many features map to §4.P2 AI prompt area (lines 3003-3248)
s4p2_prompt_matched = 0
s4p2_total_spread_matched = 0
for r in results:
    if r['status'] in ('MATCHED', 'SPREAD') and r.get('part2_section') == '§4.P2':
        s4p2_total_spread_matched += 1
        if r.get('part2_line') and 3003 <= r['part2_line'] <= 3248:
            s4p2_prompt_matched += 1

output = {
    'agent': 'M-3',
    'scope': 'V2',
    'part2_sections': ['§4'],
    'total_features': len(v2_features),
    'results': results,
    'statistics': stats,
    'special_checks': {
        's4p2_ai_prompt_coverage': {
            'description': '§4.P2 AI 프롬프트 영역(L3003-3248) 커버리지 점검',
            's4p2_total_features_mapped': s4p2_total_spread_matched,
            's4p2_prompt_area_mapped': s4p2_prompt_matched,
            'note': 'v10에서 V2_P2에 106건 TRUE_MISSING 패치됨. v11 V2-P2 저커버리지 패턴 관련 116건 중 §4.P2 프롬프트 커버 점검'
        },
        'blocker_count': len([r for r in results if r.get('severity') == 'BLOCKER']),
        'high_missing_count': len([r for r in results if r['status'] == 'MISSING' and r.get('severity') == 'HIGH']),
    }
}

os.makedirs(r'D:\VAMOS\04. 구현단계\v12\v12_results\phase1', exist_ok=True)
with open(r'D:\VAMOS\04. 구현단계\v12\v12_results\phase1\v12_mapping_M03_v2.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f'Output written. Total: {len(v2_features)}')
print(f'Statistics: {stats}')
print(f'Sum check: {sum(stats.values())}')
print(f'\n§4.P2 prompt coverage: {s4p2_prompt_matched}/{s4p2_total_spread_matched} features in prompt area')
print(f'BLOCKER count: {output["special_checks"]["blocker_count"]}')
print(f'HIGH MISSING count: {output["special_checks"]["high_missing_count"]}')

# Print MISSING BLOCKERs
blockers = [r for r in results if r['status'] == 'MISSING' and r.get('severity') == 'BLOCKER']
print(f'\nMISSING BLOCKERs ({len(blockers)}):')
for b in blockers:
    print(f"  {b['feature_id']}: {b['feature_name'][:60]}")

# Print some MISSING HIGH
high_miss = [r for r in results if r['status'] == 'MISSING' and r.get('severity') == 'HIGH']
print(f'\nMISSING HIGH ({len(high_miss)}, first 15):')
for h in high_miss[:15]:
    print(f"  {h['feature_id']}: {h['feature_name'][:60]}")
