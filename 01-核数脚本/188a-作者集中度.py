# -*- coding: utf-8 -*-
r"""188a · 「一千一百多位写模板的人」到底散不散——★ 集中度，不止最大值。

**为什么跑这一件**：稿子 §四（二）L256 用「写得最多的一个也只占 2.85%」一根柱子
撑起「一大群人，各自书写」这个论断。审稿人会问：**前十位合计占多少？**
若前十位吃掉四成，「配置实践没有统一主体」就要打折扣。

**口径来源**：回接逐字沿用 `57d-回接分母对齐.py` 的两把钥匙（prompt 全串 ＋ 前 30 字），
author 取值沿用 `52b-精选5452条的著者分布.py`。

**★ 四道对表**（我的管子必须复现稿子的数）：
  接得上 3,437 条 ／ 不同 author 取值 1,115 ／ 最多的一位 98 条 ／ 占比 2.85%

**★ 隐私**：伦理声明（L407）写明「未公开任何一位写作者的账号名」。
本脚本**不打印任何作者取值**，只出汇总量与匿名档位。
（维护者账号的取值只在判断「0 条」时用一次，且只打印个数。）

**★ 控制组**（房规 128）：把一个作者的全部记录复制三份，看集中度动不动。
"""
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

ROOT = r'F:\数据集\水仙提示词库'
OUT = (r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10'
       r'\188a-作者集中度-2026-10-12.txt')

# 沿用 52b 的取值；只在「是不是 0 条」这一处用，不打印
MAINTAINER = 'Kas2026'

SLOT = re.compile(r'\{\s*\\{0,2}"?\s*argument', re.I)


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

by_full, by_head = {}, {}
for r in old:
    pr = str(r.get('prompt', ''))
    by_full.setdefault(pr, r)
    by_head.setdefault(pr[:30], r)

matched = []          # (author, 是否带槽位)
for r in uni:
    pr = str(r.get('prompt', ''))
    o = by_full.get(pr)
    if o is None:
        o = by_head.get(pr[:30])
    if o is None:
        continue
    matched.append((str(o.get('author', '')), bool(SLOT.search(pr))))

total = len(matched)
authors = Counter(a for a, _ in matched)
empty_n = authors.get('', 0)
n_auth = len([a for a in authors if a])

o = io.open(OUT, 'w', encoding='utf-8')


def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n')
    print(line)


W('作者集中度 · 188a · 2026-10-12')
W('精选版 %d 条 ／ 旧版 %d 条 ／ 回接（两把钥匙）接上 %d 条' % (len(uni), len(old), total))
W('=' * 78)

W('')
W('【0】★ 四道对表（我的管子 vs 稿子的数）')
W('-' * 78)
top1_n = authors.most_common(1)[0][1]
checks = [
    ('接得上的条数', total, 3437),
    ('不同 author 取值', n_auth, 1115),
    ('最多的一位条数', top1_n, 98),
]
allok = True
for lab, got, want in checks:
    ok = (got == want)
    allok = allok and ok
    W('  %-18s 实测 %8s  稿中 %8s  %s' % (lab, got, want, '\u2713' if ok else '\u2605\u2605 \u4e0d\u5408'))
sh = top1_n / total
ok = abs(sh - 0.0285) < 0.0002
allok = allok and ok
W('  %-18s 实测 %8.2f%%  稿中 %8s  %s' % ('最多的一位占比', sh * 100, '2.85%', '\u2713' if ok else '\u2605\u2605'))
W('  空串 author 的记录数 %d  %s' % (empty_n, '（已剔除，不计入作者数）' if empty_n else '（无空串）'))
W('  \u21d2 四道全合：%s' % ('\u2713' if allok else '\u2605\u2605 \u5148\u6000\u7591\u7ba1\u5b50'))

W('')
W('【1】★ 集中度：两个方向各看一遍')
W('-' * 78)
W('  作者数 %d ／ 记录数 %d ／ 均摊 %.2f 条每人' % (n_auth, total, total / n_auth))
W('  按「作者」看（记录被多少作者分摊）     按「记录」看（记录落在多少作者手里）')
W('  %-10s %8s %8s   %8s %8s' % ('前 k 位', '作者占比', '', '记录占比', '累计'))
cum = 0
for k in (1, 3, 5, 10, 20, 50):
    if k > n_auth:
        break
    rec = sum(n for _, n in authors.most_common(k))
    cum = rec
    W('  %-10s %7.2f%% %8s   %7.2f%% %7.2f%%'
      % ('前 %d 位' % k, 100.0 * k / n_auth, '', 100.0 * rec / total, 100.0 * rec / total))
hhi = sum((n / total) ** 2 for n in authors.values()) * 10000
W('')
W('  HHI（赫芬达尔指数，按记录份额平方和 x 10000）= %.1f' % hhi)
W('    （参考：完全均分 %d 位 = %.1f；单一作者独占 = 10000）' % (total, 10000.0 / total))
W('  ★ 前 10 位合计占 %.2f%%；末位长尾：只写 1 条的作者 %d 位（占作者数 %.2f%%）'
  % (100.0 * sum(n for _, n in authors.most_common(10)) / total,
     sum(1 for n in authors.values() if n == 1),
     100.0 * sum(1 for n in authors.values() if n == 1) / n_auth))

W('')
W('【2】按「每人写了多少条」分档（作者数 / 记录数两个口径）')
W('-' * 78)
W('  %-14s %8s %8s   %8s %8s' % ('档', '作者数', '作者占比', '记录数', '记录占比'))
buckets = ((1, 1), (2, 4), (5, 9), (10, 49), (50, 10 ** 9))
for lo, hi in buckets:
    ks = [n for n in authors.values() if lo <= n <= hi]
    lab = ('%d 条' % lo) if lo == hi else ('%d-%d 条' % (lo, hi) if hi < 10 ** 9 else '%d 条以上' % lo)
    W('  %-14s %8d %7.2f%%   %8d %7.2f%%'
      % (lab, len(ks), 100.0 * len(ks) / n_auth, sum(ks), 100.0 * sum(ks) / total))
W('  中位数 %.1f 条每人   均值 %.2f 条每人'
  % (sorted(authors.values())[n_auth // 2], total / n_auth))

W('')
W('【3】★ 核稿子 L264「十个人里有一个两种都写」')
W('-' * 78)
per = defaultdict(lambda: [0, 0])      # author -> [带槽位, 不带槽位]
for a, hs in matched:
    per[a][0 if hs else 1] += 1
both = sum(1 for v in per.values() if v[0] and v[1])
only_slot = sum(1 for v in per.values() if v[0] and not v[1])
only_none = sum(1 for v in per.values() if v[1] and not v[0])
W('  两种都写的作者   %5d 位，占 %.2f%%   （稿中「十个人里有一个」= 约 10%%）' % (both, 100.0 * both / n_auth))
W('  只写带格子的     %5d 位，占 %.2f%%   （稿中「多数人只写带格子的」）' % (only_slot, 100.0 * only_slot / n_auth))
W('  只写不带格子的   %5d 位，占 %.2f%%   （稿中「少数人只写不带格子的」）' % (only_none, 100.0 * only_none / n_auth))

W('')
W('【4】维护者与空串')
W('-' * 78)
W('  站点维护者账号在这 %d 条中出现 %d 次（稿中 0 条）' % (total, authors.get(MAINTAINER, 0)))
W('  ★ 本脚本未打印任何作者取值（伦理声明 L407）')

W('')
W('【5】★ 控制组（房规 128）：把最大作者的三条记录复制三份，看集中度动不动')
W('-' * 78)
fake = list(matched)
biggest = authors.most_common(1)[0][0]
fake += [(biggest, True)] * 3 * max(1, top1_n // 3)
fa = Counter(a for a, _ in fake)
ft = len(fake)
f10 = 100.0 * sum(n for _, n in fa.most_common(10)) / ft
W('  注入前  前 10 位合计 %.2f%%' % (100.0 * sum(n for _, n in authors.most_common(10)) / total))
W('  注入后  前 10 位合计 %.2f%%' % f10)
moved = abs(f10 - 100.0 * sum(n for _, n in authors.most_common(10)) / total) > 0.01
W('  \u21d2 集中度随输入变化：%s' % ('\u2713 \u5224\u636e\u4f1a\u52a8' if moved else '\u2605\u2605 \u6052\u5b9a\u4e0d\u53d8'))

W('')
W('=' * 78)
W('总判：%s' % ('\u2713 四道对表全合，集中度数可用' if allok else '\u2605\u2605\u2605 对表未合'))
o.close()
print('\n写出：%s' % OUT)
