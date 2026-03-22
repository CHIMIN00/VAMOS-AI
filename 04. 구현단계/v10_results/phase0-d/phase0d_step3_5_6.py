"""
Phase 0-D 대화 15: STEP 3 + STEP 5 + STEP 6
- STEP 3: version_scope 불일치 → PLAN-3.0 기준 정답 확정
- STEP 5: V_UNKNOWN 버전 확정
- STEP 6: 중복 병합 → v10_merged_features.json
"""
import json, os, sys, copy, re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
PHASE0B = os.path.join(BASE, '..', 'phase0-b')
PHASE0C = os.path.join(BASE, '..', 'phase0-c')

# ============================================================
# 로드
# ============================================================
with open(os.path.join(BASE, 'v10_layer1_layer2_delta.json'), 'r', encoding='utf-8') as f:
    delta = json.load(f)

with open(os.path.join(PHASE0B, 'v10_layer1_claude_features.json'), 'r', encoding='utf-8') as f:
    l1_data = json.load(f)

l1_dict = {}
for feat in l1_data['features']:
    l1_dict[feat['feature_id']] = feat

l2_dict = {}
l2_by_file = defaultdict(list)
l2_files = sorted([f for f in os.listdir(PHASE0C) if f.endswith('.json')])
for fname in l2_files:
    with open(os.path.join(PHASE0C, fname), 'r', encoding='utf-8') as f2:
        data = json.load(f2)
    feats = data.get('features', data.get('data', []))
    if isinstance(feats, list):
        for feat in feats:
            fid = feat.get('feature_id', '')
            if fid:
                feat_copy = dict(feat)
                feat_copy['_src_file'] = fname
                l2_dict[fid] = feat_copy
                l2_by_file[fname].append(fid)

print(f"Loaded: L1={len(l1_dict)}, L2={len(l2_dict)}, L2 files={len(l2_files)}")

# ============================================================
# PLAN-3.0 버전 룰 테이블 (로드맵 기반 정답)
# ============================================================
# PLAN-3.0 §3 기준 버전 배정 규칙:
# - V0: 기초 골격 (I-1~I-25 인덱스/레지스트리 정의, 메모리 구조, config 스켈레톤, 디렉토리 구조)
# - V1: 기본 멀티모달, P0 도메인 일부 활성, I-모듈 실제 구현, BLUE NODE 기본형
# - V2: 확장 멀티모달, 2단 LLM, P0 전체 + P1 일부, Self-check 확장
# - V3: AGI 고도화, Self-evo 활성, P2 도메인, LLM+다른뇌+LLM

# I-모듈 버전 규칙 (PLAN-3.0 §3.1.2 + §3.2.1 + DESIGN 참조):
# I-1~I-25는 V0에서 "인덱스/레지스트리 정의"만, V1에서 "기본 구현"
# 단, 일부 모듈은 V2/V3에서만 실질 구현

VERSION_RULES = {
    # I-모듈 정답 버전 (PLAN-3.0 §3.1~3.4 + §0.5 + §1.3-A 기준)
    'I-1': 'V0,V1,V2,V3',   # Intent Detector: V0 골격 + V1 기본구현 + V2/V3 확장
    'I-2': 'V0,V1,V2,V3',   # Context Builder/RAG: V0 골격 + V1 텍스트 중심 + V2 프로젝트 RAG
    'I-3': 'V0,V1,V2,V3',   # Memory System: V0 4계층 정의 + V1 구현
    'I-4': 'V1,V2,V3',      # Multimodal Interpreter: V1 기본(이미지/문서/음성) + V2 확장 + V3 영상
    'I-5': 'V0,V1,V2,V3',   # Condition & Decision: V0 골격 + V1 구현
    'I-6': 'V1,V2,V3',      # Self-check: V1 기본 + V2 확장(재검색 루프)
    'I-7': 'V1,V2,V3',      # Project/Session Manager: V1 기본 (PLAN에 V0 언급 없음, 실제 세션관리는 V1)
    'I-8': 'V0,V1,V2,V3',   # Policy Engine: V0 정책 기본값 + V1 구현
    'I-9': 'V1,V2,V3',      # Cost Manager: V1 비용 모드 활성
    'I-10': 'V1,V2,V3',     # Tool Registry/Router: V1 구현
    'I-11': 'V1,V2,V3',     # Output Composer: V1 구현
    'I-12': 'V1,V2,V3',     # Workflow Builder: V1 기본 + V2 템플릿 연동
    'I-13': 'V2,V3',        # Multimodal Output Renderer: V2 확장
    'I-14': 'V1,V2,V3',     # Summarizer: V1 구현
    'I-15': 'V1,V2,V3',     # Evidence & QoD: V1 구현
    'I-16': 'V1,V2,V3',     # Knowledge Search: V1 기본
    'I-17': 'V1,V2,V3',     # Blue Node Manager: V1 기본
    'I-18': 'V3',           # Self-evo Engine: §3.4 V3 전용 (§1.3-A 확인)
    'I-19': 'V1,V2,V3',     # Approval Manager: V1 기본
    'I-20': 'V1,V2,V3',     # Failure/Fallback: V1 기본
    'I-21': 'V3',           # Source Evolution: §3.4 V3
    'I-22': 'V2,V3',        # Task/Project Manager: V2 (I-7과 구분, 고급 기능)
    'I-23': 'V2,V3',        # Doc/Code Structuring: V2
    'I-24': 'V3',           # Knowledge Graph Engine: V3 (§3.4)
    'I-25': 'V2,V3',        # SDAR Engine: V2 기본 + V3 고도화

    # S-모듈 (Self-evo 계열)
    'S-1': 'V3',            # Self-check Engine (S계열): V3
    'S-2': 'V3',
    'S-3': 'V3',
    'S-4': 'V3',
    'S-5': 'V3',

    # E-모듈 (External Tools)
    'E-1': 'V1,V2,V3',     # Code Executor
    'E-2': 'V1,V2,V3',     # Web Search
    'E-3': 'V1,V2,V3',     # File Manager
    'E-4': 'V1,V2,V3',     # Document Parser
    'E-5': 'V1,V2,V3',     # DB Connector
    'E-6': 'V1,V2,V3',     # API Caller
    'E-7': 'V1,V2,V3',     # Image Analyzer: V1(OCR) + V2(패턴) + V3(변환)
    'E-8': 'V1,V2,V3',     # Audio Processor: V1(STT) + V2(감정)
    'E-9': 'V2,V3',        # Video Analyzer: V2(장면) + V3(행동)
    'E-10': 'V1,V2,V3',    # Calculator
    'E-11': 'V2,V3',       # Notification
    'E-12': 'V2,V3',       # Calendar
    'E-13': 'V2,V3',       # Multimodal Overlay

    # C-모듈 (Checker/Verifier)
    'C-1': 'V1,V2,V3',
    'C-2': 'V1,V2,V3',
    'C-3': 'V1,V2,V3',
    'C-4': 'V1,V2,V3',
    'C-5': 'V3',           # Bayesian Belief: V3
    'C-6': 'V3',           # RL Advisor: V3

    # D-모듈 (Deep reasoning)
    'D-1': 'V1,V2,V3',     # Think Engine
    'D-2': 'V2,V3',        # Multi-Brain Router
    'D-3': 'V3',           # Long Horizon Planner
    'D-4': 'V3',           # Personality/Tone
    'D-5': 'V3',           # General Brain (Parallel)
}

# 특수 항목 버전 룰
SPECIAL_VERSION_RULES = {
    # config 관련: V0에서 스켈레톤, V1에서 값 적용
    'config.toml': 'V0',           # 구조 정의는 V0
    'config.v1.toml': 'V0,V1',    # V0에서 파일 생성, V1에서 LOCK 값 적용
    'config.v1->v2': 'V2',        # V2 전환

    # RAG: V1 기본 → V2/V3 확장
    'RAG 6단계': 'V1,V2,V3',

    # RBAC: V1 기본 → V2 AGENT 확장
    'RBAC': 'V1,V2',

    # Embedding: V1 BGE-M3 → V2+ 전환
    'Embedding': 'V1,V2,V3',

    # Semantic Cache: V1 기본
    'Semantic Cache': 'V1,V2',

    # Vector DB: V1 Chroma → V2 Qdrant
    'Vector DB': 'V1,V2,V3',

    # Storage: V1 SQLite → V2 PostgreSQL
    'Storage': 'V1,V2,V3',

    # Docker Compose: V2 Deploy
    'Docker Compose': 'V2',

    # Tauri: V0 골격 + V1 구현
    'Tauri': 'V0,V1,V2',

    # SDAR: V2 기본 + V3
    'SDAR': 'V2,V3',

    # 5가지 협업: V1
    '협업 패턴': 'V1,V2,V3',

    # datetime.utcnow 교체: V0 레거시 수정
    'datetime.utcnow': 'V0,V1',

    # 디렉토리/파일 구조: V0
    'data 디렉토리': 'V0',
    'directory': 'V0',

    # 타입 동기화: V0 생성 + V1 적용
    '타입 동기화': 'V0,V1',
    'contracts.py': 'V0,V1',

    # NodeRegistry: V1
    'NodeRegistry': 'V1',

    # VerifyChainRegistry: V1
    'VerifyChainRegistry': 'V1',

    # 설정 우선순위: V0
    '설정 우선순위': 'V0,V1',

    # 네이밍 컨벤션: V0
    '네이밍': 'V0',

    # Graph DB: V1 JSON → V2 Neo4j → V3 Aura
    'Graph DB': 'V1,V2,V3',

    # 보호 규칙: V1
    '보호 규칙': 'V1',

    # Ollama 초기화: V0
    'Ollama': 'V0',

    # 5-Phase Pipeline: V1
    '5-Phase': 'V0,V1,V2,V3',

    # Agent Team: V1
    'Agent Team': 'V1,V2,V3',

    # Brain Adapter: V1 기본 + V2 확장
    'Brain Adapter': 'V1,V2,V3',

    # Rust 구조: V0 골격 + V1 구현
    'Rust': 'V0,V1',

    # Python 구조: V0 골격 + V1 구현
    'Python': 'V0,V1',

    # Gate: V1
    'Gate': 'V1,V2,V3',
}

# V_UNKNOWN 확정 룰
V_UNKNOWN_RULES = {
    'P30-069': {
        'resolved': 'V2,V3',
        'reason': '시장 비교 8축 평가는 Data & Quant(P1) 고급 분석. PLAN-3.0 §3.3.2: P1 V2 활성'
    },
    'D204-155': {
        'resolved': 'V3',
        'reason': 'INT4 QAT 로컬 배포 = 고급 최적화. PLAN-3.0 §1.3-A: Fine-tuning V2+, 양자화는 V3'
    },
    'D204-156': {
        'resolved': 'V2,V3',
        'reason': '재무제표 시계열 DB = Data & Quant(P1) 인프라. PLAN-3.0 §3.3.2: P1 V2 활성'
    },
    'D204-157': {
        'resolved': 'V3',
        'reason': '엣지-클라우드 하이브리드 = V3 인프라 고도화. PLAN-3.0 §2.Y V3 하드웨어'
    },
    'D204-158': {
        'resolved': 'V3',
        'reason': '예측적 비용 최적화 30일 패턴 = Self-evo 기반 자동화. PLAN-3.0 §3.4: V3'
    },
}


def extract_module_id(name):
    """기능명에서 모듈 ID (I-1, E-2, S-1 등) 추출"""
    m = re.match(r'(I-\d+|E-\d+|S-\d+|C-\d+|D-\d+)', name)
    return m.group(1) if m else None


def resolve_version(l1_feat, l2_feat, l1_ver, l2_ver):
    """PLAN-3.0 기준으로 정답 버전 결정"""
    name = l1_feat.get('feature_name', '') if l1_feat else l2_feat.get('feature_name', '')

    # 1. 모듈 ID로 직접 매칭
    mod_id = extract_module_id(name)
    if mod_id and mod_id in VERSION_RULES:
        return VERSION_RULES[mod_id], f'PLAN-3.0 §3 모듈 {mod_id} 규칙'

    # 2. 특수 항목 키워드 매칭
    for keyword, ver in SPECIAL_VERSION_RULES.items():
        if keyword in name:
            return ver, f'PLAN-3.0 특수 규칙: {keyword}'

    # 3. L2(SRC)가 더 상세한 설계문서 기반이므로,
    #    매칭 점수가 높은 경우(>0.85) L2 우선
    #    그 외에는 L1(CLAUDE.md = 상위 계획) 우선
    return None, 'MANUAL_REVIEW_NEEDED'


# ============================================================
# STEP 3: version_scope 불일치 분석 및 수정
# ============================================================
print("\n" + "="*80)
print("STEP 3: version_scope 불일치 분석")
print("="*80)

s1 = delta['step1_layer1_only']
mismatches = []

for m in s1['matched'] + s1['partial_matches']:
    l1_id = m['feature_id']
    l2_id = m.get('best_match_l2_id', '')
    l1_ver = m.get('version_scope', '')
    score = m.get('best_match_score', 0)

    if l2_id in l2_dict:
        l2_ver = l2_dict[l2_id].get('version_scope', '')
        if l1_ver != l2_ver:
            l1_feat = l1_dict.get(l1_id, {})
            l2_feat = l2_dict[l2_id]

            resolved_ver, reason = resolve_version(l1_feat, l2_feat, l1_ver, l2_ver)

            correction_target = None
            if resolved_ver:
                if resolved_ver == l1_ver:
                    correction_target = 'L2'
                elif resolved_ver == l2_ver:
                    correction_target = 'L1'
                else:
                    correction_target = 'BOTH'

            mismatches.append({
                'l1_id': l1_id,
                'l2_id': l2_id,
                'l1_version_scope': l1_ver,
                'l2_version_scope': l2_ver,
                'match_score': score,
                'l1_name': m.get('feature_name', ''),
                'l2_name': l2_feat.get('feature_name', ''),
                'l2_src_file': l2_feat.get('_src_file', ''),
                'resolved_version': resolved_ver,
                'resolution_reason': reason,
                'correction_target': correction_target,
            })

auto_resolved = [m for m in mismatches if m['resolved_version'] is not None]
manual_needed = [m for m in mismatches if m['resolved_version'] is None]

print(f"\n총 불일치: {len(mismatches)}")
print(f"  자동 해결: {len(auto_resolved)}")
print(f"  수동 검토 필요: {len(manual_needed)}")

# 수정 방향 통계
correct_l1 = sum(1 for m in auto_resolved if m['correction_target'] == 'L2')
correct_l2 = sum(1 for m in auto_resolved if m['correction_target'] == 'L1')
correct_both = sum(1 for m in auto_resolved if m['correction_target'] == 'BOTH')
print(f"  L1 정답 (L2 수정): {correct_l1}")
print(f"  L2 정답 (L1 수정): {correct_l2}")
print(f"  양쪽 모두 수정: {correct_both}")

if manual_needed:
    print(f"\n수동 검토 필요 항목:")
    for m in manual_needed:
        print(f"  {m['l1_id']} vs {m['l2_id']}: L1={m['l1_version_scope']} L2={m['l2_version_scope']} | {m['l1_name'][:50]}")

# ============================================================
# STEP 5: V_UNKNOWN 버전 확정
# ============================================================
print("\n" + "="*80)
print("STEP 5: V_UNKNOWN 버전 확정")
print("="*80)

v_unknown_items = []
for fid, feat in l2_dict.items():
    vs = feat.get('version_scope', '')
    if 'UNKNOWN' in vs.upper():
        rule = V_UNKNOWN_RULES.get(fid, None)
        item = {
            'feature_id': fid,
            'feature_name': feat.get('feature_name', ''),
            'original_version': vs,
            'src_file': feat.get('_src_file', ''),
            'category': feat.get('category', ''),
        }
        if rule:
            item['resolved_version'] = rule['resolved']
            item['resolution_reason'] = rule['reason']
            item['status'] = 'RESOLVED'
        else:
            item['resolved_version'] = 'V_UNKNOWN'
            item['resolution_reason'] = '확정 불가 - Phase 1 전 Phase 검색 필요'
            item['status'] = 'UNRESOLVED'
        v_unknown_items.append(item)

resolved_count = sum(1 for v in v_unknown_items if v['status'] == 'RESOLVED')
unresolved_count = sum(1 for v in v_unknown_items if v['status'] == 'UNRESOLVED')

print(f"\nV_UNKNOWN 총: {len(v_unknown_items)}")
print(f"  확정: {resolved_count}")
print(f"  잔여(Phase 1 검색 예정): {unresolved_count}")

for v in v_unknown_items:
    print(f"\n  {v['feature_id']}: {v['feature_name'][:55]}")
    print(f"    원본: {v['original_version']} → 확정: {v['resolved_version']}")
    print(f"    근거: {v['resolution_reason']}")

# ============================================================
# STEP 6: 중복 병합 → v10_merged_features.json
# ============================================================
print("\n" + "="*80)
print("STEP 6: 중복 병합")
print("="*80)

# 6.1: 모든 features를 하나의 풀에 모음
all_features = {}

# Layer 1 features
for fid, feat in l1_dict.items():
    all_features[fid] = {
        'feature_id': fid,
        'feature_name': feat.get('feature_name', ''),
        'version_scope': feat.get('version_scope', ''),
        'category': feat.get('category', ''),
        'source_layer': 'L1',
        'source_section': feat.get('source_section', ''),
        'source_file': 'CLAUDE.md',
        'tech_keywords': feat.get('tech_keywords', []),
        'module_id': feat.get('module_id', ''),
        'is_lock': feat.get('is_lock', False),
        'cross_ref': [],
    }

# Layer 2 features
for fid, feat in l2_dict.items():
    # V_UNKNOWN 수정 반영
    vs = feat.get('version_scope', '')
    for v_item in v_unknown_items:
        if v_item['feature_id'] == fid and v_item['status'] == 'RESOLVED':
            vs = v_item['resolved_version']

    all_features[fid] = {
        'feature_id': fid,
        'feature_name': feat.get('feature_name', ''),
        'version_scope': vs,
        'category': feat.get('category', ''),
        'source_layer': 'L2',
        'source_file': feat.get('source_file', feat.get('_src_file', '')),
        'agent_file': feat.get('_src_file', ''),
        'tech_keywords': feat.get('tech_keywords', []),
        'module_id': feat.get('module_id', ''),
        'is_lock': feat.get('is_lock', False),
        'cross_ref': [],
        'sub_features': feat.get('sub_features', []),
    }

print(f"\n병합 전 총 features: {len(all_features)}")

# 6.2: 중복 감지 (W-31 방어: feature_name + version_scope + category + 모듈ID + 기술키워드)
def normalize_name(name):
    """기능명 정규화 (비교용)"""
    name = name.lower().strip()
    # 공백/특수문자 정규화
    name = re.sub(r'\s+', ' ', name)
    # (LOCK), (NEW) 등 태그 제거
    name = re.sub(r'\s*\(lock\)\s*', '', name)
    name = re.sub(r'\s*\(new\)\s*', '', name)
    return name

def compute_similarity_key(feat):
    """중복 감지를 위한 복합 키 생성"""
    name = normalize_name(feat.get('feature_name', ''))
    mod_id = feat.get('module_id', '') or ''
    # 모듈 ID가 없으면 기능명에서 추출 시도
    if not mod_id:
        extracted = extract_module_id(feat.get('feature_name', ''))
        if extracted:
            mod_id = extracted
    cat = feat.get('category', '')
    return (name[:50], mod_id, cat)

# 그룹화
groups = defaultdict(list)
for fid, feat in all_features.items():
    key = compute_similarity_key(feat)
    groups[key].append(fid)

# 중복 그룹 찾기 (2개 이상)
dup_groups = {k: v for k, v in groups.items() if len(v) >= 2}
print(f"키 기반 중복 그룹: {len(dup_groups)}")

# 추가: 이름 유사도 기반 중복 감지 (정규화 이름 동일)
name_groups = defaultdict(list)
for fid, feat in all_features.items():
    nname = normalize_name(feat.get('feature_name', ''))[:60]
    name_groups[nname].append(fid)

name_dup_groups = {k: v for k, v in name_groups.items() if len(v) >= 2}
print(f"이름 기반 중복 그룹: {len(name_dup_groups)}")

# 6.3: 병합 실행
merged_features = {}
merged_count = 0
merge_log = []

# 이름 기반 중복 처리 (더 포괄적)
merged_ids = set()

for nname, fids in name_dup_groups.items():
    if len(fids) < 2:
        continue

    # 가장 상세한 버전 선택 (sub_features가 많거나, tech_keywords가 많은 것)
    best_id = None
    best_score = -1

    for fid in fids:
        feat = all_features[fid]
        score = 0
        score += len(feat.get('sub_features', []))
        score += len(feat.get('tech_keywords', []))
        score += len(feat.get('feature_name', ''))
        # L2가 더 상세하므로 가산점
        if feat.get('source_layer') == 'L2':
            score += 10
        if score > best_score:
            best_score = score
            best_id = fid

    # primary 설정
    primary = all_features[best_id]
    cross_refs = [fid for fid in fids if fid != best_id]
    primary['cross_ref'] = list(set(primary.get('cross_ref', []) + cross_refs))

    merged_features[best_id] = primary
    merged_ids.update(fids)

    if len(cross_refs) > 0:
        merged_count += len(cross_refs)
        merge_log.append({
            'primary_id': best_id,
            'merged_ids': cross_refs,
            'feature_name': primary['feature_name'][:60],
        })

# 중복되지 않은 features 추가
for fid, feat in all_features.items():
    if fid not in merged_ids:
        merged_features[fid] = feat

print(f"\n병합 후 총 features: {len(merged_features)}")
print(f"중복 병합된 features: {merged_count}")
print(f"병합 그룹 수: {len(merge_log)}")

# STEP 3 수정 반영: 자동 해결된 version_scope 수정
version_corrections = 0
for m in auto_resolved:
    resolved = m['resolved_version']
    if m['correction_target'] == 'L1' and m['l1_id'] in merged_features:
        merged_features[m['l1_id']]['version_scope'] = resolved
        merged_features[m['l1_id']]['version_corrected'] = True
        merged_features[m['l1_id']]['version_correction_reason'] = m['resolution_reason']
        version_corrections += 1
    elif m['correction_target'] == 'L2' and m['l2_id'] in merged_features:
        merged_features[m['l2_id']]['version_scope'] = resolved
        merged_features[m['l2_id']]['version_corrected'] = True
        merged_features[m['l2_id']]['version_correction_reason'] = m['resolution_reason']
        version_corrections += 1
    elif m['correction_target'] == 'BOTH':
        for target_id in [m['l1_id'], m['l2_id']]:
            if target_id in merged_features:
                merged_features[target_id]['version_scope'] = resolved
                merged_features[target_id]['version_corrected'] = True
                merged_features[target_id]['version_correction_reason'] = m['resolution_reason']
                version_corrections += 1

print(f"STEP 3 버전 수정 적용: {version_corrections}건")

# ============================================================
# 출력 파일 생성
# ============================================================

# 1. delta.json 업데이트 (STEP 3 결과 추가)
delta['step3_version_mismatch'] = {
    'step': 'STEP 3',
    'description': '양쪽에 있지만 version_scope가 다른 항목 → PLAN-3.0 기준 정답 확정',
    'total_mismatches': len(mismatches),
    'auto_resolved': len(auto_resolved),
    'manual_review_needed': len(manual_needed),
    'corrections': {
        'l1_correct_l2_fix': correct_l1,
        'l2_correct_l1_fix': correct_l2,
        'both_fix': correct_both,
    },
    'items': mismatches,
}

# STEP 5 결과 추가
delta['step5_v_unknown'] = {
    'step': 'STEP 5',
    'description': 'V_UNKNOWN 버전 확정 (W-18 방어)',
    'total': len(v_unknown_items),
    'resolved': resolved_count,
    'unresolved': unresolved_count,
    'items': v_unknown_items,
}

# 메타 업데이트
delta['meta']['steps'].extend(['STEP 3', 'STEP 5', 'STEP 6'])
delta['meta']['generated_date'] = '2026-03-09'
delta['meta']['generator'] += ' + 대화 15'

# 통계 업데이트
delta['statistics']['step3'] = {
    'total_mismatches': len(mismatches),
    'auto_resolved': len(auto_resolved),
    'manual_review_needed': len(manual_needed),
}
delta['statistics']['step5'] = {
    'v_unknown_total': len(v_unknown_items),
    'resolved': resolved_count,
    'unresolved': unresolved_count,
}
delta['statistics']['step6'] = {
    'pre_merge_total': len(all_features),
    'post_merge_total': len(merged_features),
    'duplicates_merged': merged_count,
    'merge_groups': len(merge_log),
    'version_corrections_applied': version_corrections,
}

with open(os.path.join(BASE, 'v10_layer1_layer2_delta.json'), 'w', encoding='utf-8') as f:
    json.dump(delta, f, ensure_ascii=False, indent=2)
print(f"\n✓ v10_layer1_layer2_delta.json 업데이트 완료 (STEP 3/5 추가)")

# 2. v10_merged_features.json 생성
merged_output = {
    'meta': {
        'phase': '0-D',
        'step': 'STEP 6',
        'generated_date': '2026-03-09',
        'description': '중복 제거된 전체 기능 목록 (Layer1 + Layer2 병합)',
        'source_l1': 'v10_layer1_claude_features.json',
        'source_l2_files': l2_files,
        'pre_merge_count': len(all_features),
        'post_merge_count': len(merged_features),
        'duplicates_merged': merged_count,
        'version_corrections': version_corrections,
        'v_unknown_resolved': resolved_count,
    },
    'statistics': {
        'total_features': len(merged_features),
        'by_layer': {
            'L1_only': sum(1 for f in merged_features.values() if f.get('source_layer') == 'L1'),
            'L2_only': sum(1 for f in merged_features.values() if f.get('source_layer') == 'L2'),
        },
        'by_version': {},
        'by_category': {},
        'lock_count': sum(1 for f in merged_features.values() if f.get('is_lock')),
    },
    'merge_log': merge_log,
    'features': list(merged_features.values()),
}

# 버전별 통계
ver_counts = defaultdict(int)
for f in merged_features.values():
    vs = f.get('version_scope', '')
    for v in vs.split(','):
        v = v.strip()
        if v:
            ver_counts[v] += 1
merged_output['statistics']['by_version'] = dict(sorted(ver_counts.items()))

# 카테고리별 통계
cat_counts = defaultdict(int)
for f in merged_features.values():
    cat = f.get('category', 'UNKNOWN')
    cat_counts[cat] += 1
merged_output['statistics']['by_category'] = dict(sorted(cat_counts.items()))

with open(os.path.join(BASE, 'v10_merged_features.json'), 'w', encoding='utf-8') as f:
    json.dump(merged_output, f, ensure_ascii=False, indent=2)
print(f"✓ v10_merged_features.json 생성 완료 ({len(merged_features)} features)")

# ============================================================
# 최종 통계
# ============================================================
print("\n" + "="*80)
print("Phase 0-D 대화 15 최종 통계")
print("="*80)
print(f"\n[STEP 3] version_scope 불일치")
print(f"  총 불일치: {len(mismatches)}")
print(f"  자동 해결: {len(auto_resolved)} (L1정답:{correct_l1}, L2정답:{correct_l2}, 양쪽수정:{correct_both})")
print(f"  수동 검토: {len(manual_needed)}")

print(f"\n[STEP 5] V_UNKNOWN")
print(f"  총: {len(v_unknown_items)}")
print(f"  확정: {resolved_count}")
print(f"  잔여: {unresolved_count}")

print(f"\n[STEP 6] 중복 병합")
print(f"  병합 전: {len(all_features)}")
print(f"  병합 후: {len(merged_features)}")
print(f"  제거된 중복: {merged_count}")
print(f"  병합 그룹: {len(merge_log)}")
print(f"  버전 수정: {version_corrections}건")

print(f"\n[버전별 분포]")
for v in sorted(ver_counts.keys()):
    print(f"  {v}: {ver_counts[v]}")

print(f"\n[카테고리별 분포]")
for cat in sorted(cat_counts.keys()):
    print(f"  {cat}: {cat_counts[cat]}")

print(f"\n[LOCK 항목]: {merged_output['statistics']['lock_count']}")
print(f"\n완료.")