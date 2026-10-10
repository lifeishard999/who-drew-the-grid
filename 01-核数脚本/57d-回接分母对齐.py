# -*- coding: utf-8 -*-
r"""
57d：注[13] 的「回接得上的 3,437 条中带槽位者占 91.10%」——分母是哪一套？
★ 两把钥匙（52b：prompt 全串＋前 30 字）与四把钥匙（55b：＋title＋去空格 title）
  接上的条数不同（3,437 vs 3,475）。分子分母若各取一套，占比就错。
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'F:\数据集\水仙提示词库'

def load(fp):
    with io.open(fp, encoding='utf-8') as fh:
        d = json.load(fh)
    if isinstance(d, dict):
        d = d.get('prompts') or d.get('data') or d.get('items') or []
    return d

uni, old = [], []
for f in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    uni += load(os.path.join(ROOT, 'shuixian-unified', 'data', f))
    old += load(os.path.join(ROOT, 'old', 'shuixian-deploy', 'data', f))

SLOT = re.compile(r'\{\s*\\{0,2}"?\s*argument', re.I)
def has_slot(r): return bool(SLOT.search(str(r.get('prompt', ''))))
def norm(s): return re.sub(r'\s+', '', str(s or ''))

by_p  = {str(r.get('prompt', '')) for r in old}
by_h  = {str(r.get('prompt', ''))[:30] for r in old}
by_t  = {str(r.get('title', '')) for r in old}
by_nt = {norm(r.get('title', '')) for r in old}

m2 = [r for r in uni if str(r.get('prompt', '')) in by_p or str(r.get('prompt', ''))[:30] in by_h]
m4 = [r for r in uni
      if str(r.get('prompt', '')) in by_p or str(r.get('prompt', ''))[:30] in by_h
      or (str(r.get('title', '')) and str(r.get('title', '')) in by_t)
      or (norm(r.get('title', '')) and norm(r.get('title', '')) in by_nt)]
u4 = [r for r in uni if r not in m4]

def rate(name, ms):
    s = sum(1 for r in ms if has_slot(r))
    print(f'  {name:<34} 接上 {len(ms):>5,}   其中带槽位 {s:>5,} = {s/len(ms):.2%}')

print(f'精选版 {len(uni):,}   旧版 {len(old):,}')
print()
print('★ 回接「接得上的那批」带槽位率：')
rate('两把钥匙（52b 口径）', m2)
rate('四把钥匙（55b 口径）', m4)
print()
print('★ 四把钥匙接不上的那批：')
s = sum(1 for r in u4 if has_slot(r))
print(f'  {len(u4):,} 条，其中带槽位 {s:,} = {s/len(u4):.2%}')
print()
print(f'  2,283 − 不含槽位且四钥匙接不上 = {2283 - sum(1 for r in u4 if not has_slot(r))}')
print()
print('★ 稿中三个数各归哪一套：')
print(f'  注[12] 3,437（两把钥匙）  ✓ 自洽：3,437/5,452 = {3437/5452:.2%}')
print(f'  注[13] 1,977（四把钥匙）  ✓ 自洽：1,977/5,452 = {1977/5452:.2%}')
print(f'  ★ 但 3,437 + 1,977 = {3437+1977:,} ≠ 5,452（差 {5452-3437-1977}）')
print(f'  ★ 四把钥匙下「接得上」应为 {len(m4):,}（= 5,452 − 1,977）')
print(f'  ★ 稿中 91.10% 的三种可能配法：')
print(f'      3,131/3,437 = {3131/3437:.2%}   3,131/3,475 = {3131/3475:.2%}')
print(f'      （3,131 = 3,169 − 38，即「全库带槽位者中除去接不上那批的 38 条」）')
