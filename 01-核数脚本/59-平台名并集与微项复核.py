# -*- coding: utf-8 -*-
r"""
59：核报告 `57` 的「子」「微」两项，并为「丑」取判据。

子  L29「直呼任一平台名的仅 16 条」——四类平台的**并集**到底几条？16 是怎么来的？
微  L97「两千三百多种名字」对 2,395 ——「两千三百多」这个近似写法站不站得住？
丑  表 1「9,076」＝算 45 号「甲」判据（含拉丁字母且不含汉字）——能否逐字复现？

★ 本脚本一律**沿用 32 号自己的正则原文**（不另造），否则复算与原文不可比。
"""
import io, json, os, re, sys, glob

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))
N = len(rows)
print(f'记录 = {N:,}\n')

# ── 子：四类「直呼平台名」（★ 正则逐字取自 32 号）──────────
NAMES = [
    ('即梦',                 re.compile(r'即梦')),
    ('MJ/midjourney',        re.compile(r'midjourney|mj\b', re.I)),
    ('stable diffusion/sd',  re.compile(r'stable\s*diffusion|\bsd\b', re.I)),
    ('可灵/豆包/海螺/文心',     re.compile(r'可灵|豆包|海螺|文心一格')),
]
hit = [set() for _ in NAMES]
for i, r in enumerate(rows):
    s = r.get('prompt') or ''
    for k, (_, p) in enumerate(NAMES):
        if p.search(s):
            hit[k].add(i)

print('【子】直呼平台名（32 号四类正则逐字）')
for k, (lab, _) in enumerate(NAMES):
    print(f'  {lab:<22} {len(hit[k]):>6,}')
u4 = set().union(*hit)
print(f'  ★ 四类并集 = {len(u4):,}   （稿：16）')
print(f'  并集成员明细（{len(u4)} 条）：')
for i in sorted(u4):
    tags = '+'.join(NAMES[k][0] for k in range(4) if i in hit[k])
    print(f'    [{tags:<22}] {(rows[i].get("prompt") or "")[:56]}')
print()
print('  ★ 16 的两种可能来路：')
for k, (lab, _) in enumerate(NAMES):
    rest = [j for j in range(4) if j != k]
    u_wo = set().union(*(hit[j] for j in rest))
    print(f'     去掉「{lab}」后并集 = {len(u_wo):,}')
print()

# ── 微：槽名种数 ──────────────────────────────────────────
SLOT = re.compile(r'\{\s*\\{0,2}"?\s*argument\b([^}]*)\}', re.I)
def attr(a, s):
    m = re.search(r'\b' + a + r'\s*=\s*\\{0,2}"(.*?)\\{0,2}"', s, re.S | re.I)
    return m.group(1) if m else None
names = []
for r in rows:
    for m in SLOT.finditer(r.get('prompt') or ''):
        nm = attr('name', m.group(1))
        if nm is not None:
            names.append(nm.strip())
uniq = {}
for n in names:
    uniq[n] = uniq.get(n, 0) + 1
kinds = len(uniq)
once = sum(1 for v in uniq.values() if v == 1)
print('【微】槽名种数')
print(f'  槽位总数 {len(names):,}   种数 {kinds:,}   只出现 1 次 {once:,} = {once/kinds:.2%}')
print(f'  ★ 稿 L97「九千多个槽位用掉了两千三百多种名字」：{kinds:,} → 汉字读法「两千三百九十五」')
print(f'    「两千三百多」{"站得住" if 2300 <= kinds < 2400 else "★ 站不住"}（区间＝[2300,2400)）')
print()

# ── 丑：9,076 判据（45 号「甲」＝含拉丁字母且不含汉字）────
LAT = re.compile(r'[A-Za-z]')
HAN = re.compile(r'[\u4e00-\u9fff]')
a_ = sum(1 for n in names if LAT.search(n) and not HAN.search(n))
b_ = sum(1 for n in names if not HAN.search(n))
print('【丑】槽名拉丁判据（45 号原文）')
print(f'  甲 含拉丁字母且不含汉字 = {a_:,}  = {a_/len(names):.2%}   （稿：9,076 / 99.54%）')
print(f'  乙 不含汉字             = {b_:,}  = {b_/len(names):.2%}   （稿旧数 9,077）')
diff = [n for n in uniq if not HAN.search(n) and not LAT.search(n)]
print(f'  甲乙之差 {b_-a_} 个，即「不含汉字但也不含拉丁字母」者：{diff}')
print()
print(f'  ★ 判读：稿中 9,076 是**甲**（口径最严、最经得起追问）；99.54% = {a_}/9,118')
