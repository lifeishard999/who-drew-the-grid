# -*- coding: utf-8 -*-
r"""
55b：把 55 号那句「接不上的 2,015 条」钉死。
★ 要回答：接不上，是「旧版真的没有」，还是「prompt 被改过所以对不上」？
  第二把钥匙：title。第三把：title 的前若干字 / 去空格。
★ 并算：旧版里「被精选排除」的那一批，含槽位率是多少。
"""
import io, json, os, re, sys
from collections import Counter

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

SLOT = re.compile(r'\{\s*\\{0,2}"?\s*argument', re.I)
def has_slot(r): return bool(SLOT.search(str(r.get('prompt', ''))))

def norm(s):
    return re.sub(r'\s+', '', str(s or ''))

old_by_prompt   = {str(r.get('prompt', '')): r for r in old}
old_by_head     = {}
old_by_title    = {}
old_by_ntitle   = {}
for r in old:
    old_by_head.setdefault(str(r.get('prompt', ''))[:30], r)
    t = str(r.get('title', ''))
    old_by_title.setdefault(t, r)
    old_by_ntitle.setdefault(norm(t), r)

only_uni = []          # 精选有、旧版无
matched_by = Counter()
for r in uni:
    p = str(r.get('prompt', ''))
    if p in old_by_prompt:
        matched_by['prompt全串'] += 1; continue
    if p[:30] in old_by_head:
        matched_by['prompt前30字'] += 1; continue
    t = str(r.get('title', ''))
    if t and t in old_by_title:
        matched_by['title'] += 1; continue
    if norm(t) and norm(t) in old_by_ntitle:
        matched_by['title去空格'] += 1; continue
    only_uni.append(r)

print('★ 精选 5,452 条的回接情况：')
for k, v in matched_by.most_common():
    print(f'   {k:<14} {v:>5}')
print(f'   完全找不到      {len(only_uni):>5}  = {len(only_uni)/len(uni):.2%}')
print()

n = sum(1 for r in only_uni if has_slot(r))
print(f'★ 「旧版完全找不到」的 {len(only_uni)} 条：含槽位 {n} = {n/len(only_uni):.2%}')
n2 = sum(1 for r in uni if has_slot(r))
print(f'   （精选全体含槽位 {n2}/{len(uni)} = {n2/len(uni):.2%}）')
print()

# 旧版里没进精选的
uni_prompts = {str(r.get('prompt', '')) for r in uni}
uni_titles  = {str(r.get('title', '')) for r in uni}
left = [r for r in old
        if str(r.get('prompt', '')) not in uni_prompts
        and str(r.get('title', '')) not in uni_titles]
n3 = sum(1 for r in left if has_slot(r))
print(f'★ 旧版 {len(old)} 条中，未进精选（prompt 与 title 都不在精选里）的 {len(left)} 条：')
print(f'   含槽位 {n3} = {n3/len(left):.2%}   （旧版全体 {sum(1 for r in old if has_slot(r))/len(old):.2%}）')
print()

print('★ 无槽位的 2,283 条，来源拆开：')
su = sum(1 for r in uni if not has_slot(r))
old_prompts = set(old_by_prompt)
from_old = sum(1 for r in uni if not has_slot(r) and str(r.get('prompt','')) in old_by_prompt)
print(f'   无槽位合计 {su}')
print(f'     · prompt 在旧版里找得到：{from_old}')
print(f'     · 旧版里找不到：{su - from_old}  = {(su-from_old)/su:.2%}')

print()
print('★ 抽样：旧版找不到的条目（前 10 条的 title）')
for r in only_uni[:10]:
    print('   ', str(r.get('title', ''))[:40], '｜槽位:', has_slot(r))
