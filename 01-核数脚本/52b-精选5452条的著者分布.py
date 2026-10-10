# -*- coding: utf-8 -*-
r"""
52b：把现役 5,452 精选版逐条对回旧版 17,427 的 author 字段，
量出「这批散文到底出自多少人之手」。

★ 这一步是为了判 注[6]「策展人**自撰**的散文」与 L27「写作者身份明确」有没有据。
比对键：prompt 全文（先用前 30 字建索引，再对全串；同名不同串者取全串匹配）。
"""
import io, json, os, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'F:\数据集\水仙提示词库'

def load(fp):
    with io.open(fp, encoding='utf-8') as fh:
        d = json.load(fh)
    if isinstance(d, dict):
        d = d.get('prompts') or d.get('data') or d.get('items') or []
    return d

# 现役精选版
uni = []
for f in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    uni += load(os.path.join(ROOT, 'shuixian-unified', 'data', f))
print(f'精选版 {len(uni)} 条')

# 旧版（有 author）
old = []
for f in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    old += load(os.path.join(ROOT, 'old', 'shuixian-deploy', 'data', f))
print(f'旧版（非 Twitter） {len(old)} 条')

by_full = {}
by_head = {}
for r in old:
    pr = str(r.get('prompt', ''))
    by_full.setdefault(pr, r)
    by_head.setdefault(pr[:30], r)
au_full = Counter(str(r.get('author', '')) for r in old)
print(f'旧版 author 取值 {len(au_full)} 种；其中空串 {au_full.get("", 0)} 条')

# 逐条回找
hit_full = hit_head = miss = 0
authors = Counter()
matched_rows = []
for r in uni:
    pr = str(r.get('prompt', ''))
    o = by_full.get(pr)
    how = 'full'
    if o is None:
        o = by_head.get(pr[:30])
        how = 'head'
    if o is None:
        miss += 1
        continue
    if how == 'full':
        hit_full += 1
    else:
        hit_head += 1
    a = str(o.get('author', '')) or '（空）'
    authors[a] += 1
    matched_rows.append((r.get('title', ''), a))

tot = hit_full + hit_head
print()
print(f'★ 匹配上：{tot} / {len(uni)} = {tot/len(uni):.1%}   （全串 {hit_full} ／ 前30字 {hit_head} ／ 未匹配 {miss}）')
print(f'★ 这些条目出自 {len(authors)} 个不同的 author 取值')
print()
print('  前 25 位：')
for a, n in authors.most_common(25):
    print(f'     {a[:44]!r:<48} {n:>5}  ({n/tot:.2%})')
print()
top1 = authors.most_common(1)[0]
print(f'  ★ 最大单一作者 {top1[0]!r} 占 {top1[1]}/{tot} = {top1[1]/tot:.2%}')
print(f'  ★ 站点运营者 Kas2026 占 {authors.get("Kas2026",0)}/{tot} = {authors.get("Kas2026",0)/tot:.2%}')
only_once = sum(1 for a, n in authors.items() if n == 1)
print(f'  ★ 只出现一次的 author 取值 {only_once} 个')
print()
# 抽 8 条看
print('  抽样（title ← author）：')
for t, a in matched_rows[:8]:
    print(f'     {str(t)[:26]:<28} ← {a[:40]}')
print('     …')
for t, a in matched_rows[len(matched_rows)//2:len(matched_rows)//2+4]:
    print(f'     {str(t)[:26]:<28} ← {a[:40]}')
