# -*- coding: utf-8 -*-
r"""
60：复核注[7] 的四数（2,515 ／ 2,305 ／ 161 ／ 210）是否出自**同一套口径**。

起因：报告 `57` 丑② 指出，注[7]「其中 2,305 个…，161 个…」读起来像相加，
而 161 实为 2,305 的子集。改稿要写「后者包含在前者之内，两数不相加；
其余 210 个非 ASCII 但同样不含汉字」，故须先把四数量在一处——
通则：凡有恒等关系的数，一律由脚本当场算，且**分子分母必须同源**。

★★ 本脚本第一版（同日）用的是「默认值必须带引号」的严格提取，得 2,518／2,308／167，
   与稿中所记各差 3／3／6 —— 那不是稿子错，是**两套提取口径不同**：
   严格式漏掉 3 个未加引号但有汉字默认值的槽位。判据须与 57b／39 号一脉相承。
   故本版改用 57b 号 `parse_default`（有 default 就取，不强求引号）＋ 39 号的数字标点式，
   一次把四数算齐。

口径（三段，务须分清）：
  A. 槽位总体         = 具名槽位三写法并集，共 9,118 个（其中 1 个无 default）
  B. 「不含任何汉字」   = 9,118 − 「含至少一个汉字」；**无／空 default 也算作不含汉字**
  C. 在 B 之内再分三档  = 全 ASCII ／ 仅数字与 .,:%/+- 及空格 ／ 非 ASCII
"""
import io, json, os, re, sys, glob
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

HAN = re.compile(r'[\u4e00-\u9fff]')
# ★ 逐字沿用 57b／39 号：提出式（有 default 即取，随后去引号）
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

defs = [parse_default(m.group(1)) for r in rows
        for m in LOOSE.finditer(str(r.get('prompt', '')))]
N = len(defs)
dd = [d for d in defs if d]                     # 有（非空）default 者
print(f'槽位总体 = {N:,}   有 default = {len(dd):,}   无/空 default = {N-len(dd):,}')
assert N == 9118, N
print()

# ── A/B：含汉字 与 不含汉字（互为补数）──
with_han = sum(1 for d in dd if HAN.search(d))
zero_han = N - with_han
print('【B】默认值是否含汉字（补数口径）')
print(f'  含至少一个汉字 {with_han:>6,}  = {with_han/N:.2%}   （稿：6,603 / 72.42%）')
print(f'  不含任何汉字   {zero_han:>6,}  = {zero_han/N:.2%}   （稿：2,515 / 27.58%）')
print(f'  ★ 两数之和 = {with_han+zero_han:,} = {N:,} ? {"✓" if with_han+zero_han==N else "✗"}')
print()

# ── C：在 zero_han 之内分三档（无/空 default 计入「全 ASCII」，空串视为 ASCII）──
z = [(d or '') for d in defs if not (d and HAN.search(d))]
assert len(z) == zero_han
a_ascii = [d for d in z if all(ord(c) < 128 for c in d)]
a_punct = [d for d in z if d and re.fullmatch(r'[\d\s.,:%/\-+]+', d)]
a_other = [d for d in z if not all(ord(c) < 128 for c in d)]
print('【C】在「不含任何汉字」的 %d 个之内再分三档' % zero_han)
print(f'  全 ASCII（码位<128）        {len(a_ascii):>6,}   （稿：2,305）')
print(f'  非 ASCII                    {len(a_other):>6,}   （稿拟写：210）')
print(f'    其中仅数字与 .,:%/+- 及空格 {len(a_punct):>6,}   （稿：161）')
print()
print(f'  ★ 161 是否为 2,305 的子集 ? '
      f'{"是（两数不相加）" if set(a_punct) <= set(a_ascii) else "否"}')
print(f'  ★ 2,305 ＋ 210 = {len(a_ascii)+len(a_other):,} = {zero_han:,} ? '
      f'{"✓" if len(a_ascii)+len(a_other)==zero_han else "✗"}')
print(f'  ★ 扣掉 161 后剩余的 ASCII 档 = {len(a_ascii)-len(a_punct):,}')
print()
ok = (with_han == 6603 and zero_han == 2515 and len(a_ascii) == 2305
      and len(a_punct) == 161 and len(a_other) == 210)
print(f'  ★★ 总判：{"四数同源、全部复现 ✓" if ok else "★ 与稿中所记不符 ✗✗✗"}')
print()

print('  非 ASCII 零汉字默认值样本（前 12）：')
seen = set()
for d in a_other:
    if d in seen: continue
    seen.add(d)
    print(f'    {d[:44]!r}')
    if len(seen) >= 12: break

print()
print('【零汉字槽位里出现最多的槽名】（须与注[7] 所列一致）')
nm = Counter()
for r in rows:
    for m in LOOSE.finditer(str(r.get('prompt', ''))):
        d = parse_default(m.group(1))
        if d and HAN.search(d): continue
        k = m.group(1).find('name=')
        if k < 0: continue
        rest = m.group(1)[k+5:]
        nx = re.search(r'\s+(?:name|default)\s*=', rest)
        nm[strip_q(rest[:nx.start()] if nx else rest)] += 1
for k, v in nm.most_common(6):
    print(f'    {k:<28} {v}')
