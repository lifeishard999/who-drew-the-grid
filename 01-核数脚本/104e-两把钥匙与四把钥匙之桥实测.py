# -*- coding: utf-8 -*-
r"""
104e · 只验一件事：2,015（两把钥匙接不上）− 1,977（四把钥匙都接不上）＝ 38，
       与被「多出的两把钥匙」（title／去空格 title）**救回的那批**、
       以及注[13] 里「1,977 条中带槽位的 38 条」——**是不是同一批**。

  ★ 起因：我在 104a 的 A5b 里写了「多出的两把钥匙所救回者正是这 38 条」。
    **那是一个"同一批"的断言**，而两个 38 可能只是同数。**同数是巧合、同一批要证。**
    这正是通则⑨（结论要取自被检文本自身）与「先量后写要量到能推翻自己的候选句」要拦的东西。
"""
import io
import json
import os
import re
import sys

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
has_slot = lambda r: bool(SLOT.search(str(r.get('prompt', ''))))
norm = lambda s: re.sub(r'\s+', '', str(s or ''))
key = lambda r: (str(r.get('prompt', '')), str(r.get('title', '')))

by_p = {str(r.get('prompt', '')) for r in old}
by_h = {str(r.get('prompt', ''))[:30] for r in old}
by_t = {str(r.get('title', '')) for r in old}
by_nt = {norm(r.get('title', '')) for r in old}

m1 = lambda r: str(r.get('prompt', '')) in by_p
m2k = lambda r: str(r.get('prompt', ''))[:30] in by_h
m3 = lambda r: bool(str(r.get('title', ''))) and str(r.get('title', '')) in by_t
m4k = lambda r: bool(norm(r.get('title', ''))) and norm(r.get('title', '')) in by_nt

u2 = [r for r in uni if not (m1(r) or m2k(r))]
u4 = [r for r in uni if not (m1(r) or m2k(r) or m3(r) or m4k(r))]
rescued = [r for r in u2 if r not in u4]           # 被 title／去空格 title 救回的
slot_in_u4 = [r for r in u4 if has_slot(r)]        # 1,977 里带槽位的那批

print('精选版 %d ｜ 旧版 %d' % (len(uni), len(old)))
print('  两把钥匙接不上（u2）＝ %d     ← 注[12] 的 2,015' % len(u2))
print('  四把钥匙都接不上（u4）＝ %d     ← 注[13] 的 1,977' % len(u4))
print('  差额（u2 \\ u4）＝ %d' % (len(u2) - len(u4)))
print('  u4 中带槽位 ＝ %d' % len(slot_in_u4))
print()
A, B = {key(r) for r in rescued}, {key(r) for r in slot_in_u4}
print('★ rescued        n=%d  其中带槽位 %d' % (len(A), sum(1 for r in rescued if has_slot(r))))
print('★ slot_in_u4     n=%d' % len(B))
print('★ 交集            n=%d' % len(A & B))
print('★ A − B           n=%d' % len(A - B))
print('★ B − A           n=%d' % len(B - A))
print()
same = (A == B)
print('★★ 结论：%s' % ('两者**是同一批**——「多出的两把钥匙所救回者正是这 38 条」成立'
                     if same else
                     '两者**不是同一批**（只是同数 38）——A5b 那句必须改写'))
print()
print('★ rescued 里带槽位的那几条（若与 B 不同批，可见差异长什么样）：')
for r in rescued[:5]:
    print('   slot=%-5s title=%r prompt=%r' % (has_slot(r), str(r.get('title', ''))[:24],
                                             str(r.get('prompt', ''))[:40]))
sys.exit(0 if same else 2)
