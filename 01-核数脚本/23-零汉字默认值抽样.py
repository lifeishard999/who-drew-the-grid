# -*- coding: utf-8 -*-
"""
14 号量出：8,145 个具名槽位里，默认值**一个汉字都没有**的有 2,239 个（27.5%）。
14 号同时给了字符数口径：预制 中位 440 字符、空格默认 中位 24 字符（汉字口径 366 : 13）。

§二 要如实交代这件事——汉字口径**对被填的那一侧不利**（"hair color" 不算字、"3" 不算字），
所以 366 : 13 这个差距有一半是口径造成的。写进稿子之前，先看清那 2,239 个到底是什么样。
"""
import json, os, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\23-零汉字默认值抽样-2026-10-09.txt'

SLOT = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
HAN  = re.compile(r'[\u4e00-\u9fff]')

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')
P('零汉字默认值的抽样与分类    2026-10-09')
P('=' * 78)

zero, nonzero = [], 0
for r in rows:
    t = r.get('prompt') or ''
    for m in SLOT.finditer(t):
        nm, d = m.group(1), (m.group(2) or '')
        if not HAN.search(d):
            zero.append((nm, d))
        else:
            nonzero += 1

P('  具名槽位总数 %d；默认值零汉字 %d（%.1f%%）；非零 %d'
  % (len(zero) + nonzero, len(zero), 100.0 * len(zero) / (len(zero) + nonzero), nonzero))

P('')
P('【甲】零汉字默认值的**槽名**前 20 种（看它们是些什么格）')
P('-' * 78)
c = collections.Counter(nm for nm, d in zero)
for nm, n in c.most_common(20):
    P('  %-26s %5d' % (nm, n))

P('')
P('【乙】零汉字默认值的**内容**前 20 种（看填的是什么）')
P('-' * 78)
c2 = collections.Counter(d for nm, d in zero)
for d, n in c2.most_common(20):
    P('  %-40s %5d' % (repr(d)[1:-1][:38], n))

P('')
P('【丙】随机 30 条「槽名 = 默认值」（不排序，直接看）')
P('-' * 78)
import itertools
for nm, d in itertools.islice(iter(zero), 0, 30):
    P('  %-24s = %s' % (nm, repr(d)[1:-1]))

P('')
P('【丁】分类计数（按默认值内容形态粗分）')
P('-' * 78)
n_en   = sum(1 for nm, d in zero if d and all(ord(ch) < 128 for ch in d))
n_num  = sum(1 for nm, d in zero if d and all(ch in '0123456789 .%#' for ch in d))
n_empty= sum(1 for nm, d in zero if not d)
P('  纯 ASCII（英文/数字）      %5d' % n_en)
P('  其中纯数字                  %5d' % n_num)
P('  空字符串（default=""）      %5d' % n_empty)
P('  其他（含非汉字非 ASCII）    %5d' % (len(zero) - n_en - n_empty))

o.close()
print('写盘：%s' % OUT)
print('OK')
