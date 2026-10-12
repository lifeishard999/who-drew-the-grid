# -*- coding: utf-8 -*-
r"""187a · 可填侧到底能装多少字——★ 分布尾部，不是中位数。

**为什么跑这一件**：稿子 L145 用**中位数 13** 去支撑一个关于**容量**的论断
（「不足以容纳一个完整判断」）。中位数只说明一半记录如此；注[2] 自己写了
「这些量的分布均右偏，平均数高于中位数」。审稿人一句就能戳：
**有没有哪一条模板，可填侧大到足以容纳一个完整判断？**
故本脚本把可填侧的**分位数与最大值**摆出来，供落稿时决定那句话能不能站住。

**口径来源**：槽位扫描逐字沿用 `36-槽位三种写法并集重算.py`（三重并集）；
分段与汉字口径沿用 `27-两式合并后全面重算.py`。

**★ 六道对表**（我的管子必须复现稿子的数，否则先怀疑管子）：
  记录 3,169 ／ 槽位 9,118 ／ 可填侧汉字 56,851 ／ 零汉字槽位 2,515
  ／ 按记录中位 13 ／ 按单槽中位 4
**★ 控制组**（房规 128）：内存里注入一条「可填侧极大」的假记录，看尾部统计量动不动。
"""
import glob
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT = (r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10'
       r'\187a-可填侧分布尾部-2026-10-12.txt')

# ── 三重并集扫描（逐字沿用 36 号）─────────────────────────────
LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
CJK = re.compile(r'[\u4e00-\u9fff]')
BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'


def strip_quotes(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre):
            s = s[len(pre):]
            break
    for suf in (BACK2, BACK1, PLAIN, '\u201d'):
        if s.endswith(suf):
            s = s[:-len(suf)]
            break
    return s


def parse(blob):
    out = {}
    for key in ('name', 'default'):
        m = re.search(key + r'\s*=\s*', blob)
        if not m:
            out[key] = None
            continue
        rest = blob[m.end():]
        nxt = re.search(r'\s+(?:name|default)\s*=', rest)
        val = rest[:nxt.start()] if nxt else rest
        out[key] = strip_quotes(val)
    return out['name'], out['default']


rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        d = json.load(fh)
    if isinstance(d, list):
        rows.extend(d)

per_rec_han = []        # 每条记录：全部槽位默认值合计 汉字数
per_rec_ch = []         # 同上，字符数
per_rec_nslot = []
per_slot_han = []
detail = []             # (汉字数, 字符数, 槽数, id, title, 默认值拼接)
for r in rows:
    t = r.get('prompt') or ''
    ds = []
    for m in LOOSE.finditer(t):
        n, d = parse(m.group(1))
        if n is None and not d:
            continue
        ds.append(d or '')
    if not ds:
        continue
    h = sum(len(CJK.findall(d)) for d in ds)
    c = sum(len(d) for d in ds)
    per_rec_han.append(h)
    per_rec_ch.append(c)
    per_rec_nslot.append(len(ds))
    per_slot_han.extend(len(CJK.findall(d)) for d in ds)
    detail.append((h, c, len(ds), r.get('id'), r.get('title'), ' | '.join(ds)))

# ── 确定性统计（自算，不用 statistics 以免版本差异）─────────────
def pct(xs, p):
    s = sorted(xs)
    n = len(s)
    if n == 1:
        return s[0]
    x = p / 100.0 * (n - 1)
    lo = int(x)
    hi = min(lo + 1, n - 1)
    return s[lo] + (s[hi] - s[lo]) * (x - lo)


def med(xs):
    return pct(xs, 50)


o = io.open(OUT, 'w', encoding='utf-8')


def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n')
    print(line)


W('可填侧分布尾部 · 187a · 2026-10-12')
W('语料：shuixian-unified 精选版 %d 条' % len(rows))
W('=' * 78)

W('')
W('【0】★ 六道对表（我的管子 vs 稿子的数）')
W('-' * 78)
n_rec, n_slot, han_sum = len(per_rec_han), len(per_slot_han), sum(per_rec_han)
zero_han = sum(1 for x in per_slot_han if x == 0)
checks = [
    ('含槽位记录数', n_rec, 3169),
    ('槽位总数', n_slot, 9118),
    ('可填侧汉字合计', han_sum, 56851),
    ('零汉字槽位', zero_han, 2515),
    ('按记录 汉字中位', med(per_rec_han), 13),
    ('按单槽 汉字中位', med(per_slot_han), 4),
]
allok = True
for lab, got, want in checks:
    ok = (got == want)
    allok = allok and ok
    W('  %-18s 实测 %8s  稿中 %8s  %s' % (lab, got, want, '\u2713' if ok else '\u2605\u2605 \u4e0d\u5408'))
W('  \u21d2 六道全合：%s' % ('\u2713' if allok else '\u2605\u2605 \u5148\u6000\u7591\u7ba1\u5b50'))

W('')
W('【1】★ 按记录：可填侧汉字数的分布（分母 = 有槽位的 %d 条）' % n_rec)
W('-' * 78)
W('  均值 %.2f   中位 %.1f' % (sum(per_rec_han) / n_rec, med(per_rec_han)))
W('  %-8s %8s' % ('分位', '汉字'))
for p in (1, 5, 10, 25, 50, 75, 90, 95, 99):
    W('  P%-7d %8.1f' % (p, pct(per_rec_han, p)))
W('  %-8s %8d' % ('最大', max(per_rec_han)))
W('')
W('  分档：')
buckets = ((0, 0), (1, 4), (5, 9), (10, 19), (20, 29), (30, 49), (50, 99), (100, 10 ** 9))
cum = 0
for lo, hi in buckets:
    k = sum(1 for x in per_rec_han if lo <= x <= hi)
    cum += k
    lab = ('%d' % lo) if lo == hi else ('%d-%d' % (lo, hi) if hi < 10 ** 9 else '%d+' % lo)
    W('    %-10s %6d  %6.2f%%   累计 %6.2f%%' % (lab, k, 100.0 * k / n_rec, 100.0 * cum / n_rec))
W('')
W('  ★ 三个候选阈值下「可填侧够不够宽」：')
for th in (20, 30, 50):
    k = sum(1 for x in per_rec_han if x >= th)
    W('    可填侧汉字 >= %-3d 的记录：%5d 条，占 %.2f%%' % (th, k, 100.0 * k / n_rec))

W('')
W('【2】同一分布，改按字符计（汉字口径对非中文默认值不利，见注[7]）')
W('-' * 78)
W('  均值 %.2f   中位 %.1f' % (sum(per_rec_ch) / n_rec, med(per_rec_ch)))
for p in (75, 90, 95, 99):
    W('  P%-7d %8.1f' % (p, pct(per_rec_ch, p)))
W('  最大 %d' % max(per_rec_ch))
for th in (20, 30, 50):
    k = sum(1 for x in per_rec_ch if x >= th)
    W('    可填侧字符 >= %-3d 的记录：%5d 条，占 %.2f%%' % (th, k, 100.0 * k / n_rec))

W('')
W('【3】★ 尾部极值：可填侧汉字最多的 12 条（看有没有「装得下一整个判断」的）')
W('-' * 78)
W('  %-6s %-6s %-6s %s' % ('汉字', '字符', '槽数', '标题 / 默认值'))
for h, c, ns, rid, ti, ds in sorted(detail, reverse=True)[:12]:
    W('  %-6d %-6d %-6d %s' % (h, c, ns, str(ti)[:30]))
    W('        默认值：%s' % ds[:150])
W('')
W('  ★ 槽数最多的 5 条（看「格子多」与「装得多」是不是一回事）：')
for h, c, ns, rid, ti, ds in sorted(detail, key=lambda x: -x[2])[:5]:
    W('    槽数 %-4d 汉字 %-5d 字符 %-5d  %s' % (ns, h, c, str(ti)[:30]))

W('')
W('【4】★ 控制组（房规 128）：注入一条「可填侧极大」的假记录，看尾部动不动')
W('-' * 78)
FAKE = 10 ** 6
probe = list(per_rec_han) + [FAKE]
W('  注入前  最大 %-10d  P99 %-8.1f  汉字>=50 者 %d'
  % (max(per_rec_han), pct(per_rec_han, 99), sum(1 for x in per_rec_han if x >= 50)))
W('  注入后  最大 %-10d  P99 %-8.1f  汉字>=50 者 %d'
  % (max(probe), pct(probe, 99), sum(1 for x in probe if x >= 50)))
moved = (max(probe) != max(per_rec_han)) and (pct(probe, 99) != pct(per_rec_han, 99))
W('  \u21d2 尾部统计量随输入变化：%s' % ('\u2713 \u5224\u636e\u4f1a\u52a8' if moved else '\u2605\u2605 \u6052\u5b9a\u4e0d\u53d8\uff0c\u5224\u636e\u574f'))

W('')
W('=' * 78)
W('总判：%s' % ('\u2713 六道对表全合，尾部数可用'
                if allok else '\u2605\u2605\u2605 对表未合，先别用这些数'))
o.close()
print('\n写出：%s' % OUT)
