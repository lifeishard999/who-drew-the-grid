# -*- coding: utf-8 -*-
r"""
槽位到底有几种表面写法？——第三类「双反斜杠转义」的发现与三重并集重算。

链条：
  `01`（与 `14`）只认直引号式                     → 2,932 条 / 8,145 个
  `26` 认出转义式 `name=\"…\"`                    → +233 条 / +945 个，重叠 0
  `35` 拿宽松口径一减，**又漏出 28 个串 / 12 条记录**，逐条读原文，分三类：
    ① 值里含**转义引号**（default="\"ENERGY\", …"）→ 精确口径 `[^"]*` 在第一个内部引号处截断
    ② 值尾多一个**中文右引号** `”`（default="…眼睛”}）→ 同上，截断后 `\}` 对不上
    ③ ★ **`name=\\\"…\\\"` 双反斜杠式** → 二次转义，`26` 的 `\\"` 只吃一个反斜杠，**一拍都拍不到**
  → 故本脚本改用"先定位 `{argument`、再按 `name=` 后接什么字符分类"的**扫描口径**，
    不再依赖任何一种写死的正则。

口径纪律：
  · 三种写法**分列报数**，再报并集；
  · 与 `26` 号并集**双向对账**（谁多认了、谁漏了）；
  · 语言归属统计只在**三重并集**上做。
"""
import json, os, re, io, sys, glob
from collections import Counter

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\36-槽位三种写法并集重算-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

# 26 号的两种口径，逐字沿用，用于对账
SLOT_P = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
SLOT_E = re.compile(r'\{argument\s+name=\\"([^"]*?)\\"(?:\s+default=\\"([^"]*?)\\")?\}')

LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
CJK, LAT = re.compile(r'[\u4e00-\u9fff]'), re.compile(r'[A-Za-z]')

BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'      # 三字符 / 两字符 / 一字符

def strip_quotes(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre):
            s = s[len(pre):]; break
    for suf in (BACK2, BACK1, PLAIN, '”'):
        if s.endswith(suf):
            s = s[:-len(suf)]; break
    return s

def parse(blob):
    """从 '{argument ...}' 的属性串里取 name 与 default（容忍三种引号写法）"""
    out = {}
    for key in ('name', 'default'):
        m = re.search(key + r'\s*=\s*', blob)
        if not m:
            out[key] = None; continue
        rest = blob[m.end():]
        # 值＝到下个 ' ' + 下个属性名 或 串尾
        nxt = re.search(r'\s+(?:name|default)\s*=', rest)
        val = rest[:nxt.start()] if nxt else rest
        out[key] = strip_quotes(val)
    return out['name'], out['default']

slots = []            # (id, form, name, default)
recs  = {}
recs26 = set()
for r in rows:
    t = r.get('prompt') or ''
    pid = r.get('id')
    if SLOT_P.search(t) or SLOT_E.search(t):
        recs26.add(pid)
    for m in LOOSE.finditer(t):
        blob = m.group(1)
        k = blob.find('name=')
        if k < 0:
            form = '其他（无 name 属性）'
        else:
            rest = blob[k+5:]
            if   rest.startswith(BACK2): form = 'E2 双反斜杠式'
            elif rest.startswith(BACK1): form = 'E1 转义式'
            elif rest.startswith(PLAIN): form = 'P  直引号式'
            else:                        form = '其他（引号形态不符）'
        n, d = parse(blob)
        slots.append((pid, form, n, d))
        recs.setdefault(form, set()).add(pid)

# 与 26 号对账
allrec = set(s[0] for s in slots)
only26 = recs26 - allrec
only36 = allrec - recs26

def kind(x):
    if x is None:        return '无 default 属性'
    if x.strip() == '':  return '空串'
    c, l = bool(CJK.search(x)), bool(LAT.search(x))
    if c and l:          return '中英混'
    if c:                return '纯汉字'
    if l:                return '纯拉丁'
    return '其他'

o = io.open(OUT, 'w', encoding='utf-8')
def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

W('槽位三种写法 · 并集重算   语料 =', len(rows), '条')
W('')
W('【一】按写法分列')
W(f"{'写法':<20}{'记录数':>8}{'槽位数':>8}")
for form in sorted(recs, key=lambda f: -len(recs[f])):
    W(f"{form:<20}{len(recs[form]):>8}{sum(1 for s in slots if s[1]==form):>8}")
W(f"{'★ 三重并集':<20}{len(allrec):>8}{len(slots):>8}")
W('')
W('【二】与 26 号（3,165 / 9,090）对账')
W(f"  26 号有、本脚本无 : {len(only26)}   {sorted(only26)[:10]}")
W(f"  ★ 本脚本有、26 号无 : {len(only36)}   {sorted(only36)}")
W(f"  记录数之差         : {len(allrec) - len(recs26)}")
W('')
W('【三】语言归属（★ 三重并集口径）')
W('  槽位名 name：')
for k, v in Counter(kind(s[2]) for s in slots).most_common():
    W(f'    {k:<14}{v:>7}{v/len(slots)*100:>8.2f}%')
W('  默认值 default：')
wd = [s for s in slots if s[3] is not None]
for k, v in Counter(kind(s[3]) for s in wd).most_common():
    W(f'    {k:<14}{v:>7}{v/len(wd)*100:>8.2f}%')
W('')
W('【四】分写法看槽位名（看三式是否一致）')
for form in sorted(recs, key=lambda f: -len(recs[f])):
    sub = [s for s in slots if s[1] == form]
    c = Counter(kind(s[2]) for s in sub)
    W(f"  {form:<20} 纯拉丁 {c['纯拉丁']:>5} / 纯汉字 {c['纯汉字']:>3} / 共 {len(sub)}")
W('')
W('【五】交叉：名 × 值（三重并集）')
for (a, b), v in Counter((kind(s[2]), kind(s[3])) for s in wd).most_common(8):
    W(f'    {a:<10}× {b:<10}{v:>7}{v/len(wd)*100:>8.2f}%')
W('')
W('【六】E2 双反斜杠式的全部实例（★ 新发现，逐条列）')
e2 = [s for s in slots if s[1].startswith('E2')]
W(f'  共 {len(e2)} 个槽位 / {len(set(s[0] for s in e2))} 条记录')
for s in e2:
    W(f'    id={s[0]:<7} name={s[2]!r:<38} default={(s[3] or "")[:50]!r}')

o.close()
print('\n写出：', OUT)
