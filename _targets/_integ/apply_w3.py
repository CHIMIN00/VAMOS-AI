# -*- coding: utf-8 -*-
"""세션5 W3 객관 잔존 168 fixes 중앙 적용기 (apply_w2.py와 동일 안전절차)."""
import json, os, sys, shutil, stat

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\VAMOS\_targets\_integ'
BK = os.path.join(BASE, 'backup_session5_w3')
os.makedirs(BK, exist_ok=True)

raw = json.load(open(os.path.join(BASE, 'w3_specs_raw.json'), encoding='utf-8'))['result']

backed_up = {}
report = []

def detect_eol(text):
    crlf = text.count('\r\n')
    lf = text.count('\n') - crlf
    return '\r\n' if crlf >= lf else '\n'

for cl in raw['clusters']:
    if not cl:
        continue
    cid = cl['cluster']
    for i, e in enumerate(cl['fixes']):
        path = e['file']
        tag = f"{cid}[{i}]"
        if not os.path.exists(path):
            report.append((tag, path, 'FILE_MISSING')); continue
        if path not in backed_up:
            bname = f"w3_{len(backed_up):03d}__{os.path.basename(path)}"
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
with open(os.path.join(BASE, 'apply_w3_report.json'), 'w', encoding='utf-8') as f:
    json.dump([{'edit': t, 'file': p, 'status': s} for t, p, s in report], f, ensure_ascii=False, indent=1)
