# -*- coding: utf-8 -*-
r"""
45 号：表 1「槽位名为拉丁字母者 9,077（99.55%）」↔ 36 号「纯拉丁 9,076（99.54%）」。
37 号报 9,077，36 号报 9,076，两者差 1 —— 差在哪一个名字上？当场找出。

三种判据同场比较：
  甲（36 号）含拉丁字母 且 不含汉字   → 纯拉丁
  乙（宽松）  不含汉字                → 计入拉丁（37 号大概用的这个）
"""
import json, os, re, io, sys, glob
from collections import Counter

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\45-槽名语言归属复核-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
CJK, LAT = re.compile(r'[\u4e00-\u9fff]'), re.compile(r'[A-Za-z]')
BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'

def strip_q(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre): s = s[len(pre):]; break
    for suf in (BACK2, BACK1, PLAIN, '\u201d'):
        if s.endswith(suf): s = s[:-len(suf)]; break
    return s

def name_of(blob):
    m = re.search(r'name\s*=\s*', blob)
    if not m: return None
    rest = blob[m.end():]
    nxt = re.search(r'\s+(?:name|default)\s*=', rest)
    return strip_q(rest[:nxt.start()] if nxt else rest)

names = []
for r in rows:
    for m in LOOSE.finditer(r.get('prompt') or ''):
        names.append(name_of(m.group(1)))

n_lat_strict = sum(1 for x in names if x and LAT.search(x) and not CJK.search(x))
n_notcjk     = sum(1 for x in names if x and not CJK.search(x))
odd          = [x for x in names if x and not CJK.search(x) and not LAT.search(x)]

o = io.open(OUT, 'w', encoding='utf-8')
def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

W('槽名语言归属复核   槽位 %d' % len(names))
W('=' * 78)
W('  甲 含拉丁字母且不含汉字（36 号判据） %5d  = %.2f%%' % (n_lat_strict, 100.0 * n_lat_strict / len(names)))
W('  乙 不含汉字（宽松）                %5d  = %.2f%%' % (n_notcjk, 100.0 * n_notcjk / len(names)))
W('  ★ 两者之差 ＝ %d 个：既不含汉字、也不含拉丁字母的名字' % (n_notcjk - n_lat_strict))
for x in Counter(odd).most_common():
    W('     %r ×%d' % (x[0], x[1]))
W('')
W('  → 表 1 现写「9,077（99.55%）」用的是**乙**；36 号（并集口径权威）是**甲**。')
W('  → 若采甲：**9,076 ＝ 99.54%**。')
o.close()
print('\n写出：', OUT)
