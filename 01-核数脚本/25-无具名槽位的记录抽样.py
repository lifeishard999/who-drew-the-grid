# -*- coding: utf-8 -*-
"""
§一 脚注 [2] 说「另 2,520 条不含此类槽位」，但从没交代它们是什么。
§二 要补这一句，且这一句比前面几句都更硬：「有两千多条连一个空格都没有」。
写进稿子前必须验两件：
  ① 这 2,520 条里确实**没有任何**可填的装置（连别的括号写法也没有）；
  ② 抽几条看看它们长什么样，免得"整条都是写好的"这句话说过头。
"""
import json, os, io, re, sys, collections, itertools
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\25-无具名槽位的记录抽样-2026-10-09.txt'

SLOT = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
# 任何"看起来像占位符"的写法都列出来，宁可宽
ANY  = re.compile(r'\{[^}]{0,200}\}')

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

slotless = [r for r in rows if not SLOT.search(r.get('prompt') or '')]
withslt  = [r for r in rows if SLOT.search(r.get('prompt') or '')]

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')
P('无具名槽位的记录抽样    2026-10-09')
P('=' * 78)
P('  全库 %d；含具名槽位 %d；不含 %d（%.1f%%）'
  % (len(rows), len(withslt), len(slotless), 100.0 * len(slotless) / len(rows)))

P('')
P('【甲】这 %d 条里还有没有别的"括号占位"写法？' % len(slotless))
P('-' * 78)
pat = collections.Counter()
n_any = 0
for r in slotless:
    t = r.get('prompt') or ''
    ms = ANY.findall(t)
    if ms:
        n_any += 1
        for m in ms:
            pat[m[:60]] += 1
P('  含任意花括号片段的记录：%d 条' % n_any)
for k, v in pat.most_common(20):
    P('    %5d  %s' % (v, k))

P('')
P('【乙】不含任何花括号的记录数')
P('-' * 78)
n_plain = sum(1 for r in slotless if not ANY.search(r.get('prompt') or ''))
P('  %d 条（占全库 %.1f%%）' % (n_plain, 100.0 * n_plain / len(rows)))

P('')
P('【丙】随机 12 条（看它们长什么样）')
P('-' * 78)
for r in itertools.islice(iter(slotless), 0, 12):
    t = (r.get('prompt') or '').replace('\n', ' / ')
    P('  · %s' % t[:220])
    P('')

P('')
P('【丁】长度对比（汉字数中位）')
P('-' * 78)
HAN = re.compile(r'[\u4e00-\u9fff]')
def med(xs):
    xs = sorted(xs); return xs[len(xs) // 2] if xs else 0
a = [len(HAN.findall(r.get('prompt') or '')) for r in slotless]
b = [len(HAN.findall(r.get('prompt') or '')) for r in withslt]
P('  无槽位记录 汉字中位 %d（均值 %.0f）' % (med(a), sum(a) / len(a)))
P('  有槽位记录 汉字中位 %d（均值 %.0f）' % (med(b), sum(b) / len(b)))
o.close()
print('写盘：%s' % OUT)
print('OK')
