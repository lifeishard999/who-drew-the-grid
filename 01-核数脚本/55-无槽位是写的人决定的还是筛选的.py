# -*- coding: utf-8 -*-
r"""
55：检验 memory 里悬着的那条未排除疑点 ——
   §四 说 2,283 条无槽位「**是写的人决定的**」，**也可能是策展人筛选的结果**（注[1] 已引站点「会筛选……收录」）。

★ 三个检验，越往下越有力：
  (1) 旧版全集 13,479 的含槽位率 vs 精选版 5,452 的含槽位率
      —— 若精选显著偏高，则「筛选有偏」成立（策展人偏好收有槽位的）。
  (2) 精选里「能回接上旧版」的 3,437 条 与「接不上」的 2,015 条，各自含槽位率
      —— 接不上者若以无槽位为主，是又一层筛选痕迹。
  (3) **作者层面**：同一作者是否既写有槽位的、也写无槽位的
      —— 若是，则「加不加格子」是**逐条决定**，不是作者身份决定的；这是「写的人决定的」的正面证据。
"""
import io, json, os, re, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'F:\数据集\水仙提示词库'

def load(fp):
    with io.open(fp, encoding='utf-8') as fh:
        d = json.load(fh)
    if isinstance(d, dict):
        d = d.get('prompts') or d.get('data') or d.get('items') or []
    return d

uni = []
for f in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    uni += load(os.path.join(ROOT, 'shuixian-unified', 'data', f))
old = []
for f in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    old += load(os.path.join(ROOT, 'old', 'shuixian-deploy', 'data', f))
print(f'精选版 {len(uni)} 条 ／ 旧版（非 Twitter） {len(old)} 条')

# 具名槽位的三种表面写法：{argument / {\"argument / {\\"argument
SLOT = re.compile(r'\{\s*\\{0,2}"?\s*argument', re.I)
SLOT_LOOSE = re.compile(r'argument', re.I)

def has_slot(p):
    return bool(SLOT.search(p))

for tag, rows in (('精选版', uni), ('旧版全集', old)):
    n = sum(1 for r in rows if has_slot(str(r.get('prompt', ''))))
    n2 = sum(1 for r in rows if SLOT_LOOSE.search(str(r.get('prompt', ''))))
    print(f'  {tag:<8} 含具名槽位 {n:>6} / {len(rows):<6} = {n/len(rows):>6.2%}'
          f'   （宽松口径 argument 任意出现：{n2} = {n2/len(rows):.2%}）')

print()
# 回接
by_full, by_head = {}, {}
for r in old:
    pr = str(r.get('prompt', ''))
    by_full.setdefault(pr, r)
    by_head.setdefault(pr[:30], r)

matched, unmatched = [], []
for r in uni:
    pr = str(r.get('prompt', ''))
    o = by_full.get(pr) or by_head.get(pr[:30])
    (matched if o is not None else unmatched).append((r, o))

print(f'★ 精选 {len(uni)} 条：回接上 {len(matched)}（{len(matched)/len(uni):.1%}）／接不上 {len(unmatched)}')
for tag, grp in (('回接上的', matched), ('接不上的', unmatched)):
    n = sum(1 for r, _ in grp if has_slot(str(r.get('prompt', ''))))
    print(f'  {tag:<8} 含槽位 {n:>5} / {len(grp):<5} = {n/len(grp):>6.2%}')

print()
# ★ 作者层面：同一作者是否既写有槽位的、也写无槽位的
both, only_slot, only_noslot = [], [], []
byauthor = defaultdict(lambda: [0, 0])   # author -> [有槽位条数, 无槽位条数]
for r, o in matched:
    a = str(o.get('author', '')) or '（空）'
    if has_slot(str(r.get('prompt', ''))):
        byauthor[a][0] += 1
    else:
        byauthor[a][1] += 1

for a, (s, n) in byauthor.items():
    if s and n:
        both.append((a, s, n))
    elif s:
        only_slot.append(a)
    else:
        only_noslot.append(a)

tot_a = len(byauthor)
print(f'★ 能回接到作者的模板共涉及 {tot_a} 个作者')
print(f'  · 既写过有槽位的、也写过无槽位的：{len(both):>4} 个 = {len(both)/tot_a:.1%}   ← ★ 关键')
print(f'  · 只写过有槽位的：{len(only_slot):>4} 个 = {len(only_slot)/tot_a:.1%}')
print(f'  · 只写过无槽位的：{len(only_noslot):>4} 个 = {len(only_noslot)/tot_a:.1%}')
print()
print('  两栖作者里产出最多者（有槽位 / 无槽位）：')
for a, s, n in sorted(both, key=lambda x: -(x[1] + x[2]))[:12]:
    print(f'     {a[:34]:<36} 有 {s:>4} ／ 无 {n:>4}')

print()
# 无槽位记录的集中度：少数人包办，还是普遍？
ns = Counter()
for r, o in matched:
    if not has_slot(str(r.get('prompt', ''))):
        ns[str(o.get('author', '')) or '（空）'] += 1
tot_ns = sum(ns.values())
print(f'★ 回接上的条目里，无槽位共 {tot_ns} 条，出自 {len(ns)} 个作者')
top10 = ns.most_common(10)
print('  最多的 10 位占：', f'{sum(n for _, n in top10)}/{tot_ns} = {sum(n for _, n in top10)/tot_ns:.1%}')
for a, n in top10:
    print(f'     {a[:34]:<36} {n:>4}  ({n/tot_ns:.1%})')
