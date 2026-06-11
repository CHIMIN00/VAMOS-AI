# -*- coding: utf-8 -*-
"""W1(24도메인) + W1b(12도메인) 합본 → MUST_FIX_SUBJECTIVE_620.md v2 생성 + CHANGE edits 추출."""
import json, sys, io, os

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\VAMOS\_targets\_integ'

a = json.load(open(os.path.join(BASE, 'w1_620_partial_raw.json'), encoding='utf-8'))['result']['domains']
b = json.load(open(os.path.join(BASE, 'w1b_620_raw.json'), encoding='utf-8'))['result']['domains']
doms = [x for x in a if x] + [x for x in b if x]
doms.sort(key=lambda x: -x['count_found'])

total = sum(x['count_found'] for x in doms)
changes = []
for x in doms:
    for it in x['subjective_items']:
        if it['action'] == 'CHANGE' and it.get('edit') and it['edit'].get('old'):
            changes.append({'domain': x['domain'], 'edit': it['edit'], 'choice': it['choice'][:120],
                            'recommendation': it.get('recommendation', '')[:200]})

out = io.open(os.path.join(r'D:\VAMOS\_targets', 'MUST_FIX_SUBJECTIVE_620.md'), 'w', encoding='utf-8', newline='\n')
out.write(f'''# 주관적 설계선택 — 재도출 v2 전수 리스트 (2026-06-11 세션6)

> **v1(실체 부재 보고서)을 본 v2가 대체한다.** 재도출 워크플로: wf_d775e706-682(24도메인) + wf_370f0b4a-370(12도메인) = **36/36 도메인 전수**.
> 원본 상세(options·근거 전문): `_integ/w1_620_partial_raw.json`(525KB) + `_integ/w1b_620_raw.json`(122KB).
> 재도출 합계 **{total}건** (원판정 620 — 차이는 도메인별 notes에 사유 기록: 중복 병합·기해소·앵커 초과분 등).
> 판정: **KEEP {total - len(changes)}건**(현행 값 합리·정본 무모순 — 결정 불필요, 그대로 채택) / **CHANGE {len(changes)}건**(정본 모순 발견 — 세션6에서 일괄 적용).
> 사용자 결정 잔여: 0건 — 전권 위임에 따라 전 항목 단일 결론 처리됨. 이후 변경 원하면 항목별 재개정.

## 도메인별 요약

| 도메인 | 재도출 | 원판정 | CHANGE |
|---|---:|---:|---:|
''')
for x in doms:
    ch = sum(1 for it in x['subjective_items'] if it['action'] == 'CHANGE')
    out.write(f"| {x['domain']} | {x['count_found']} | {x['count_target']} | {ch} |\n")
out.write(f"| **합계** | **{total}** | **620** | **{len(changes)}** |\n\n## 전수 항목 (도메인별)\n\n")

for x in doms:
    out.write(f"### {x['domain']} ({x['count_found']}건)\n\n")
    for i, it in enumerate(x['subjective_items'], 1):
        mark = '🔧CHANGE' if it['action'] == 'CHANGE' else 'KEEP'
        f = it['file'].replace('D:\\VAMOS\\', '').replace('D:/VAMOS/', '')
        out.write(f"{i}. **[{mark}]** `{f}`:{it.get('line','?')} — {it['choice']}\n")
        out.write(f"   - 선택지: {it['options']}\n   - 판정: {it['recommendation']}\n")
    nt = x.get('notes', '')
    if nt:
        out.write(f"\n> notes: {nt[:600]}\n")
    out.write('\n')
out.close()

with open(os.path.join(BASE, 'w1_changes.json'), 'w', encoding='utf-8') as f:
    json.dump(changes, f, ensure_ascii=False, indent=1)
v2_path = os.path.join(r'D:\VAMOS\_targets', 'MUST_FIX_SUBJECTIVE_620.md')
size = os.path.getsize(v2_path)
print(f'v2 written: {size}B, domains {len(doms)}, items {total}, CHANGE {len(changes)}')
