# -*- coding: utf-8 -*-
r"""
57b：L161「默认值则有百分之六十八点五三为纯汉字」——全项目无出处（57 号已证）。
本脚本把能想到的判据全部算一遍，看 68.53% 究竟对应哪一个（若一个都不对应，即孤数）。
"""
import io, json, os, re, sys, glob
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
HAN = re.compile(r'[\u4e00-\u9fff]')
LAT = re.compile(r'[A-Za-z]')

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'
def strip_q(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre): s = s[len(pre):]; break
    for suf in (BACK2, BACK1, PLAIN, '\u201d'):
        if s.endswith(suf): s = s[:-len(suf)]; break
    return s
def parse_default(blob):
    m = re.search(r'default\s*=\s*', blob)
    if not m: return None
    rest = blob[m.end():]
    nxt = re.search(r'\s+(?:name|default)\s*=', rest)
    return strip_q(rest[:nxt.start()] if nxt else rest)

defs = [d for d in (parse_default(m.group(1)) for r in rows
                    for m in LOOSE.finditer(str(r.get('prompt', ''))))]
print(f'槽位总数（含无 default 者） = {len(defs):,}')
dd = [d for d in defs if d]                     # 有 default 的
print(f'其中有 default 的 = {len(dd):,}')
N = len(defs)
print()

def rep(lab, n, den=None):
    den = den or N
    print(f'  {lab:<46} {n:>6,}  = {n/den:.2%}   （×9,118 = {9118*n/den:,.0f}）')

print('★ 各种「默认值是中文」的判据：')
rep('有 default 的槽位', len(dd))
rep('默认值不含任何汉字', N - sum(1 for d in dd if HAN.search(d)))
rep('默认值含至少一个汉字', sum(1 for d in dd if HAN.search(d)))
rep('默认值全部为汉字（严格）', sum(1 for d in dd if all('\u4e00' <= c <= '\u9fff' for c in d)))
rep('默认值全部为汉字（容许空白）',
    sum(1 for d in dd if all(('\u4e00' <= c <= '\u9fff') or c.isspace() for c in d)))
rep('默认值全部为汉字或数字/标点（无拉丁）',
    sum(1 for d in dd if not LAT.search(d)))
rep('默认值不含拉丁字母', sum(1 for d in dd if not LAT.search(d)))
rep('默认值以汉字开头', sum(1 for d in dd if d and HAN.match(d[0])))
rep('默认值汉字数 > 拉丁字母数', sum(1 for d in dd if len(HAN.findall(d)) > len(LAT.findall(d))))

print()
print('★ 字符口径（把默认值当一整片文本）：')
allc = ''.join(dd)
print(f'  默认值总字符 {len(allc):,}；其中汉字 {len(HAN.findall(allc)):,} '
      f'= {len(HAN.findall(allc))/len(allc):.2%}')
nonblank = re.sub(r'\s', '', allc)
print(f'  去空白后字符 {len(nonblank):,}；其中汉字 {len(HAN.findall(nonblank)):,} '
      f'= {len(HAN.findall(nonblank))/len(nonblank):.2%}')

print()
print('★ 按记录口径（3,169 条含槽位者）')
byrec = {}
for i, r in enumerate(rows):
    ds = [parse_default(m.group(1)) for m in LOOSE.finditer(str(r.get('prompt', '')))]
    ds = [d for d in ds if d]
    if ds: byrec[i] = ds
print(f'  含 default 的记录 = {len(byrec):,}')
rep('该记录全部默认值皆为汉字（严格）',
    sum(1 for ds in byrec.values() if all(all('\u4e00' <= c <= '\u9fff' for c in d) for d in ds)),
    len(byrec))
rep('该记录默认值汉字数 ≥ 拉丁字母数',
    sum(1 for ds in byrec.values()
        if len(HAN.findall(' '.join(ds))) >= len(LAT.findall(' '.join(ds)))), len(byrec))

print()
print('★ 目标：68.53%')
print(f'   ×9,118 = {9118*0.6853:,.1f}')
print(f'   ×5,452 = {5452*0.6853:,.1f}')
print(f'   ×3,169 = {3169*0.6853:,.1f}')
print(f'   ×9,090 = {9090*0.6853:,.1f}')
