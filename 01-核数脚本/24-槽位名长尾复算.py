# -*- coding: utf-8 -*-
"""
§二 要写进稿子的一句是：「槽名的分布很怪——名目极度分散，内容极度雷同。」
所据的数是主题文件里已复核过的四个：2,109 种名 / 71.8% 只出现一次 / 前 10 种占 30.19% / hair color 占 7.08%。
写进稿子前按纪律**当场重算**一遍——引用别人的（哪怕是自己记的）数，也要在本语料上复现。
"""
import json, os, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\24-槽位名长尾复算-2026-10-09.txt'

SLOT = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

names = []
for r in rows:
    t = r.get('prompt') or ''
    names.extend(m.group(1) for m in SLOT.finditer(t))

c = collections.Counter(names)
tot = len(names)
kinds = len(c)
once = sum(1 for k, v in c.items() if v == 1)
top10 = sum(v for k, v in c.most_common(10))

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')
P('槽位名长尾复算    2026-10-09')
P('=' * 78)
P('  槽位总数            %d' % tot)
P('  不同槽名（种数）    %d' % kinds)
P('  只出现 1 次的种数   %d  ＝ %.2f%%' % (once, 100.0 * once / kinds))
P('  前 10 种合计        %d  ＝ %.2f%% 的词次' % (top10, 100.0 * top10 / tot))
P('')
P('  前 20 种：')
for k, v in c.most_common(20):
    P('    %-26s %5d  %5.2f%%' % (k, v, 100.0 * v / tot))
P('')
P('  ★ 复现核对：旧记 2,109 种 / 71.8%% / 前10 30.19%% / hair color 7.08%%')
o.close()
print('写盘：%s' % OUT)
print('OK')
