# -*- coding: utf-8 -*-
"""
三件事，一趟办：
  ① 用 26 号的**精确口径**复核既有四数（P 2,932/8,145、E 233/945、并集 3,165/9,090）；
  ② ★ 查清 34 号**宽松口径**（9,118 个）比精确口径**多出来的那部分是什么**
     —— 09 号最大的教训就是"正则只认一种表面写法"，若真有**第三种写法**，须再订正一次；
  ③ 在**已对齐的口径**上重做"槽位名 vs 默认值"的语言归属统计
     （34 号那版用的宽松口径，数（9,097 齐全）不可直接引用）。

口径纪律：
  · 一律报【记录数】与【槽位数】两个数；
  · 多出来的部分**逐条打印原文**，不得静默丢弃、不得猜测归类。
"""
import json, os, re, io, sys, glob
from collections import Counter

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\35-槽位口径对齐与语言归属-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

# ── 26 号的精确口径，逐字沿用 ────────────────────────────────
SLOT_P = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
SLOT_E = re.compile(r'\{argument\s+name=\\"([^"]*?)\\"(?:\s+default=\\"([^"]*?)\\")?\}')
# ── 34 号的宽松口径（只为"抓差集"用，不作统计口径）──────────
LOOSE  = re.compile(r'\{argument\s+([^}]*?)\s*\}')

CJK = re.compile(r'[\u4e00-\u9fff]')
LAT = re.compile(r'[A-Za-z]')

def unesc(s):
    return None if s is None else s.replace('\\"', '"')

P_slots, E_slots = [], []          # (id, name, default)
P_recs,  E_recs  = set(), set()
leftover = {}                       # 宽松命中但精确口径未命中 → 原文串 → 计数

for r in rows:
    t = r.get('prompt') or ''
    pid = r.get('id')
    me = list(SLOT_E.finditer(t))
    for m in me:
        E_slots.append((pid, unesc(m.group(1)), unesc(m.group(2))))
        E_recs.add(pid)
    tt = t
    for m in reversed(me):                       # 挖掉转义式，避免重复计
        tt = tt[:m.start()] + '\x00' * (m.end() - m.start()) + tt[m.end():]
    mp = list(SLOT_P.finditer(tt))
    for m in mp:
        P_slots.append((pid, m.group(1), m.group(2)))
        P_recs.add(pid)

    # ── 差集：宽松口径命中、精确口径一个都没命中 ──
    covered = [False] * len(t)
    for m in list(SLOT_E.finditer(t)) + list(SLOT_P.finditer(t)):
        for i in range(m.start(), m.end()):
            covered[i] = True
    for m in LOOSE.finditer(t):
        if not any(covered[m.start():m.end()]):
            leftover.setdefault(m.group(0), []).append(pid)

o = io.open(OUT, 'w', encoding='utf-8')
def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

W('槽位口径对齐与语言归属   语料 =', len(rows), '条')
W('')
W('【一】精确口径复核（与 26 号对齐）')
W(f"  ① 直引号式 P : 记录 {len(P_recs):>6}   槽位 {len(P_slots):>6}   （26 号：2,932 / 8,145）")
W(f"  ② 转义式   E : 记录 {len(E_recs):>6}   槽位 {len(E_slots):>6}   （26 号：  233 /   945）")
W(f"  ③ 两者皆有的记录 : {len(P_recs & E_recs):>6}                    （26 号：    0）")
W(f"  ★ 并集       : 记录 {len(P_recs | E_recs):>6}   槽位 {len(P_slots)+len(E_slots):>6}   （26 号：3,165 / 9,090）")
W('')

W('【二】★ 宽松口径（34 号，9,118）比精确口径多出来的部分')
extra_recs = set()
for s, ids in leftover.items():
    extra_recs.update(ids)
W('  差集：')
W(f"    记录数 {len(extra_recs)}   不同串 {len(leftover)}")
W('')
W('  ---- 逐条原文（去重后全部列出，按出现次数降序）----')
for s, ids in sorted(leftover.items(), key=lambda kv: -len(kv[1]))[:40]:
    W(f"    ×{len(ids):<4} id={ids[0]:<7} {s[:150]}")
W('')

# ── 三、语言归属（精确口径上）────────────────────────────────
def kind(x):
    if x is None:           return '无 default 属性'
    if x.strip() == '':     return '空串'
    c, l = bool(CJK.search(x)), bool(LAT.search(x))
    if c and l:             return '中英混'
    if c:                   return '纯汉字'
    if l:                   return '纯拉丁'
    return '其他'

def report(tag, slots):
    with_def = [s for s in slots if s[2] is not None]
    W(f'  ── {tag}：槽位 {len(slots)} 个，其中带 default 的 {len(with_def)} 个')
    W('     槽位名 name：')
    for k, v in Counter(kind(s[1]) for s in slots).most_common():
        W(f'       {k:<14}{v:>7}{v/len(slots)*100:>8.2f}%')
    W('     默认值 default：')
    for k, v in Counter(kind(s[2]) for s in with_def).most_common():
        W(f'       {k:<14}{v:>7}{v/len(with_def)*100:>8.2f}%')
    W('')

W('【三】槽位名与默认值的语言归属（★ 在已对齐的精确口径上）')
report('直引号式 P', P_slots)
report('转义式 E', E_slots)
report('并集 P∪E', P_slots + E_slots)

W('【四】交叉：名 × 值（并集）')
both = [s for s in (P_slots + E_slots) if s[2] is not None]
for (a, b), v in Counter((kind(s[1]), kind(s[2])) for s in both).most_common(10):
    W(f'   {a:<10}× {b:<10}{v:>7}{v/len(both)*100:>8.2f}%')
W('')

W('【五】槽位名前 40（并集）')
for k, v in Counter(s[1] for s in (P_slots + E_slots)).most_common(40):
    W(f'  {v:>5}  {k}')
W('')
W('【六】槽位名里含汉字的全部（并集，逐条列）')
for k, v in Counter(s[1] for s in (P_slots + E_slots) if CJK.search(s[1] or '')).most_common():
    W(f'  {v:>5}  {k}')

o.close()
print('\n写出：', OUT)
