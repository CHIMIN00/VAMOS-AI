# -*- coding: utf-8 -*-
"""세션5 W2 결정 105+α edits 중앙 적용기.
원칙(창1 §8 계승): 파일별 1회 백업 → EOL/BOM 검출·보존 → old count==1 강제(불일치 시 SKIP 보고) → 치환 → RO 보존.
적용 순서: judge 지시 (D17 → 독립군 → D1→D2→D3→D4→D5 → D18)."""
import json, os, sys, shutil, stat

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\VAMOS\_targets\_integ'
BK = os.path.join(BASE, 'backup_session5')
os.makedirs(BK, exist_ok=True)

raw = json.load(open(os.path.join(BASE, 'w2_decisions_raw.json'), encoding='utf-8'))['result']
amend = json.load(open(os.path.join(BASE, 'amend_w2.json'), encoding='utf-8'))

decs = {d['decision_id']: d for d in raw['decisions']}

# 오버레이 적용
for r in amend.get('replace_new', []):
    decs[r['decision_id']]['edits'][r['edit_index']]['new'] = r['new']
for a in amend.get('add_edits', []):
    decs[a['decision_id']]['edits'].extend(a['edits'])

ORDER = ['D17', 'D19', 'D14', 'D15', 'D16', 'D6', 'D7', 'D9', 'D10', 'D11', 'D13',
         'D1', 'D2', 'D3', 'D4', 'D5', 'D18']

backed_up = {}
report = []

def detect_eol(text):
    crlf = text.count('\r\n')
    lf = text.count('\n') - crlf
    return '\r\n' if crlf >= lf else '\n'

for did in ORDER:
    d = decs[did]
    for i, e in enumerate(d['edits']):
        path = e['file']
        tag = f"{did}[{i}]"
        if not os.path.exists(path):
            report.append((tag, path, 'FILE_MISSING')); continue
        # 백업 (파일당 1회, 최초 상태)
        if path not in backed_up:
            bname = f"s5_{len(backed_up):03d}__{os.path.basename(path)}"
            shutil.copy2(path, os.path.join(BK, bname))
            backed_up[path] = bname
        with open(path, 'rb') as f:
            rb = f.read()
        bom = rb.startswith(b'\xef\xbb\xbf')
        text = rb.decode('utf-8-sig' if bom else 'utf-8')
        eol = detect_eol(text)
        old = e['old'].replace('\r\n', '\n').replace('\n', eol)
        new = e['new'].replace('\r\n', '\n').replace('\n', eol)
        n = text.count(old)
        if n == 0:
            report.append((tag, path, 'OLD_NOT_FOUND')); continue
        if n > 1:
            report.append((tag, path, f'AMBIGUOUS_x{n}')); continue
        text = text.replace(old, new, 1)
        out = text.encode('utf-8')
        if bom:
            out = b'\xef\xbb\xbf' + out
        ro = not os.access(path, os.W_OK)
        if ro:
            os.chmod(path, stat.S_IWRITE)
        with open(path, 'wb') as f:
            f.write(out)
        if ro:
            os.chmod(path, stat.S_IREAD)
        report.append((tag, path, 'APPLIED'))

ok = sum(1 for r in report if r[2] == 'APPLIED')
print(f"APPLIED {ok}/{len(report)} | backups: {len(backed_up)} -> {BK}")
for tag, path, status in report:
    if status != 'APPLIED':
        print(f"  !! {status:16s} {tag:9s} {path}")
with open(os.path.join(BASE, 'apply_w2_report.json'), 'w', encoding='utf-8') as f:
    json.dump([{'edit': t, 'file': p, 'status': s} for t, p, s in report], f, ensure_ascii=False, indent=1)
