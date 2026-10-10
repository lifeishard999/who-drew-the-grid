# -*- coding: utf-8 -*-
r"""
外部清单要给正文加一张统计简表。表里的数全部出自 9,090 口径，须在 **9,118 口径**上重算。

自检顺序（★ 先复现旧数，复现不了就不许往新口径推）：
  1. 复现注[6] 末项：画论词落在槽位默认值里 = **54 词次 / 50 个槽位**（剔前）
  2. 复现注[2]：预制中位 **370** 汉字 : 槽位默认中位 **13** 汉字
  3. 复现注[5]：零汉字默认值 **2,509** 个，占 9,090 的 27.6%
  4. 复现 §二 L71：槽名 2,391 种、七成以上只出现一次、前 10 占 29.30%
  然后在 9,118 口径上重报全部。

★ 画论词判定是**人工归并**（注[4] 剔了 15 处同形异义），故本脚本一律报**剔前**，
  并把命中逐条列出，供人工重判——**绝不静默丢弃**（承 01 号脚本的口径声明）。
"""
import json, os, re, io, sys, glob
from collections import Counter

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\37-表内诸数在9118口径上重算-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
CJK   = re.compile(r'[\u4e00-\u9fff]')
BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'

# 注[4] 的 37 词表，逐字
WORDS = ['水墨','工笔','写意','山水','画意','意境','宣纸','留白','皴','泼墨','白描','气韵',
         '丹青','没骨','界画','青绿','卷轴','立轴','手卷','斗方','题跋','章法','笔法','墨色',
         '淡彩','重彩','院体','文人画','国画','花鸟','人物画','工笔画','水墨画','毛笔','砚',
         '印章','题款']
assert len(WORDS) == 37, len(WORDS)

def strip_q(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre): s = s[len(pre):]; break
    for suf in (BACK2, BACK1, PLAIN, '”'):
        if s.endswith(suf): s = s[:-len(suf)]; break
    return s

def parse(blob):
    out = {}
    for key in ('name', 'default'):
        m = re.search(key + r'\s*=\s*', blob)
        if not m: out[key] = None; continue
        rest = blob[m.end():]
        nxt = re.search(r'\s+(?:name|default)\s*=', rest)
        out[key] = strip_q(rest[:nxt.start()] if nxt else rest)
    return out['name'], out['default']

def han(s): return len(CJK.findall(s or ''))
def median(xs):
    xs = sorted(xs); n = len(xs)
    return 0 if n == 0 else (xs[n//2] if n % 2 else (xs[n//2-1]+xs[n//2])/2)

slots, rec_with = [], []
for r in rows:
    t = r.get('prompt') or ''
    ms = list(LOOSE.finditer(t))
    if not ms: continue
    pred = LOOSE.sub('', t)                        # 预制文本＝挖掉全部槽位串
    rec_with.append((r.get('id'), han(pred)))
    for m in ms:
        n, d = parse(m.group(1))
        slots.append((r.get('id'), n, d, m.group(0)))

N = len(rows); NS = len(slots); NR = len(rec_with)
pred_med = median([h for _, h in rec_with])
def_med  = median([han(s[2]) for s in slots])

o = io.open(OUT, 'w', encoding='utf-8')
def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

W('表内诸数 · 9,118 口径重算   语料 =', N, '条')
W('')
W('【零】自检：能不能复现旧数（9,090 口径）')
W(f"  含槽位记录      {NR:>6}   （注[2]：3,165）")
W(f"  槽位总数        {NS:>6}   （注[2]：9,090）")
W(f"  预制中位汉字    {pred_med:>6}   （注[2]：370）")
W(f"  槽位默认中位汉字{def_med:>6}   （注[2]：13）")
zero = sum(1 for s in slots if han(s[2]) == 0)
W(f"  零汉字默认值    {zero:>6}   占 {zero/NS*100:.1f}%   （注[5]：2,509 / 27.6%）")
names = Counter(s[1] for s in slots if s[1])
once  = sum(1 for k, v in names.items() if v == 1)
W(f"  槽名种数        {len(names):>6}   （§二：2,391）")
W(f"  只出现一次      {once:>6}   {once/len(names)*100:.2f}%   （§二：七成以上）")
top10 = sum(v for _, v in names.most_common(10))
W(f"  前 10 名占比    {top10/NS*100:>6.2f}%   （§二：29.30%）")
W('')

W('【一】★ 9,118 口径下的表（对外报数用）')
W(f"  全库模板数                       {N}")
W(f"  含具名槽位的模板数               {NR}  = {NR/N*100:.2f}%")
W(f"  不含槽位的模板数                 {N-NR}  = {(N-NR)/N*100:.2f}%")
W(f"  具名槽位总数                     {NS}")
W(f"  槽名种数                         {len(names)}")
W(f"  槽名只出现一次的占比             {once/len(names)*100:.2f}%")
W(f"  前 10 名槽名的占比               {top10/NS*100:.2f}%")
W(f"  预制文本中位汉字（写模板的人）   {pred_med}")
W(f"  槽位默认值中位汉字（填的人）     {def_med}")
W(f"  零汉字默认值的槽位               {zero}  = {zero/NS*100:.2f}%")
W(f"  槽位名为纯拉丁字母的槽位         {sum(1 for s in slots if s[1] and not CJK.search(s[1]))}"
  f"  = {sum(1 for s in slots if s[1] and not CJK.search(s[1]))/NS*100:.2f}%")
W('')

W('【二】★ 画论词落在槽位默认值里（剔前）')
hits = [(s[0], s[1], s[2], s[3]) for s in slots if s[2] and any(w in s[2] for w in WORDS)]
tot  = 0
per  = Counter()
for pid, nm, dv, _ in hits:
    for w in WORDS:
        c = dv.count(w)
        if c: tot += c; per[w] += c
W(f"  含画论词的槽位（剔前）  {len(hits)}   （注[6]：50）")
W(f"  词次（剔前）            {tot}   （注[6]：54）")
W(f"  分母＝全库画论词次      1,931  →  {tot/1931*100:.2f}%   （注[6] 原写 2.80%）")
W('')
W('  词频：' + '  '.join(f'{w}×{c}' for w, c in per.most_common()))
W('')
W('  ---- 逐条列出（供人工重判同形异义；★ 不得静默丢弃）----')
for pid, nm, dv, raw in hits:
    W(f"    id={pid:<7} name={nm!r:<28} default={dv[:60]!r}")

o.close()
print('\n写出：', OUT)
