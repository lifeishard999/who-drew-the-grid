# -*- coding: utf-8 -*-
r"""
57c：补核两处「稿里报了、但须按原脚本口径复算」的数。
  G  注[3]「5,452 条模板里含此类片段的只有 305 条，占 5.6%」
     与「两种正则的命中数并不相同（2,313 与 2,250）」
  F  L29「直呼任一平台名的仅 16 条」
"""
import io, json, os, re, sys, glob

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))
L = len(rows)
print(f'记录 = {L:,}\n')

# ── 19 号 JB ─────────────────────────────
JB19 = re.compile(r'\{[^{}]*?"[^"]+"\s*:[^{}]*?\}')
n_rec19 = sum(1 for r in rows if JB19.search(r.get('prompt') or ''))
n_frag19 = sum(len(JB19.findall(r.get('prompt') or '')) for r in rows)
print('G ★ 19 号 JB 正则  {[^{}]*?"..."\s*:[^{}]*?}')
print(f'   命中记录 {n_rec19:,}  = {n_rec19/L:.2%}   （稿：305 ／ 5.6%）')
print(f'   命中片段 {n_frag19:,}   （稿：2,313）')
print()

# ── 02 号 ANYBRACE + 「像 JSON」 判据 ────
ANYBRACE = re.compile(r'\{[^{}]{0,400}\}')
def looks_json(b):
    inner = b[1:-1]
    return bool(re.search(r'"?[\w\u4e00-\u9fff]+"?\s*:\s*', inner)) and inner.count(':') >= 1
n_rec02 = sum(1 for r in rows if any(looks_json(m.group(0)) for m in ANYBRACE.finditer(r.get('prompt') or '')))
n_frag02 = sum(1 for r in rows for m in ANYBRACE.finditer(r.get('prompt') or '') if looks_json(m.group(0)))
print('G ★ 02 号 ANYBRACE + 冒号判据')
print(f'   命中记录 {n_rec02:,}  = {n_rec02/L:.2%}')
print(f'   命中片段 {n_frag02:,}   （稿：2,250）')
print()

# ── 32 号平台名四类（并集） ──────────────
PLAT = [re.compile(r'即梦'),
        re.compile(r'midjourney|mj\b', re.I),
        re.compile(r'stable\s*diffusion|\bsd\b', re.I),
        re.compile(r'可灵|豆包|海螺|文心一格')]
labels = ['即梦', 'MJ/midjourney', 'SD/stable diffusion', '可灵/豆包/海螺/文心一格']
hit = [set(), set(), set(), set()]
for i, r in enumerate(rows):
    s = r.get('prompt') or ''
    for k, p in enumerate(PLAT):
        if p.search(s):
            hit[k].add(i)
print('F ★ 直呼平台名（32 号四类，逐类）')
for k, lab in enumerate(labels):
    print(f'   {lab:<24} {len(hit[k]):>5,}')
u = set().union(*hit)
print(f'   ★ 并集 = {len(u):,}   （稿：16）')
print()
print('   合并前几个实例看：')
n = 0
for i in sorted(u):
    if n >= 8: break
    m = [labels[k] for k in range(4) if i in hit[k]]
    print(f'     [{"+".join(m)}] {(rows[i].get("prompt") or "")[:70]}')
    n += 1
