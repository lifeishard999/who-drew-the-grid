# -*- coding: utf-8 -*-
"""
槽位的两个半边，各用什么语言写的？

动因：在 33 号探针的同现实例里看到一个反复出现的形态——
    {argument name="style"      default="工笔画风格"}
    {argument name="attendants" default="小黄人"}
    {argument name="top"        default="红色超大款短款运动衫"}
**格子的名字是英文，格子里填的是中文。** 若在全库成立，这是一条新的、
   比"画论词占比"更硬的发现（范畴的命名权与内容的填写权不在同一种语言里）。
   故必须全量量，不得拿 12 条例子外推。

口径：
  1. 严格区分直引号式与转义式（两者零重叠，是两种表面写法），合并报总数。
  2. 名字与值分别判"含汉字 / 含拉丁字母 / 空"。
  3. 报【记录数】与【槽位数】两个数。
"""
import json, os, re, io, sys, glob

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\34-槽位名的语言归属-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

prompts = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        prompts.extend(json.load(fh))

CJK = re.compile(r'[\u4e00-\u9fff]')
LAT = re.compile(r'[A-Za-z]')

# ---- 两种表面写法 ----
RE_DIRECT  = re.compile(r'\{argument\s+([^}]*?)\s*\}')                    # {argument name="x" default="y"}
RE_ESCAPED = re.compile(r'\{\\?"argument\s+(.*?)\}')                      # {\"argument name=\"x\" default=\"y\"}
# 属性提取：容忍 \" 与 "
def attrs(blob):
    b = blob.replace('\\"', '"')
    name = re.search(r'name\s*=\s*"([^"]*)"', b)
    dflt = re.search(r'default\s*=\s*"([^"]*)"', b)
    return (name.group(1) if name else None, dflt.group(1) if dflt else None)

def collect():
    slots = []          # (id, form, name, default)
    for p in prompts:
        s = p.get('prompt') or ''
        pid = p.get('id')
        for m in RE_DIRECT.finditer(s):
            slots.append((pid, 'direct', m.group(1), m.start()))
        for m in RE_ESCAPED.finditer(s):
            slots.append((pid, 'escaped', m.group(1), m.start()))
    return slots

def script_kind(x):
    if x is None:            return '无此属性'
    if x.strip() == '':      return '空串'
    has_cjk, has_lat = bool(CJK.search(x)), bool(LAT.search(x))
    if has_cjk and has_lat:  return '中英混'
    if has_cjk:              return '纯汉字'
    if has_lat:              return '纯拉丁'
    return '其他'

raw = collect()
parsed = []
for pid, form, blob, _pos in raw:
    n, d = attrs(blob)
    parsed.append({'id': pid, 'form': form, 'name': n, 'default': d})

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

P('槽位的语言归属   语料 =', len(prompts), '条')
P('')
P('原始命中（含属性不全者）:', len(parsed))
P('  其中 direct :', sum(1 for r in parsed if r['form'] == 'direct'))
P('  其中 escaped:', sum(1 for r in parsed if r['form'] == 'escaped'))
P('含槽位的记录数（去重）:', len(set(r['id'] for r in parsed)))
P('')

# 只统计属性齐全的
ok = [r for r in parsed if r['name'] is not None and r['default'] is not None]
P('★ 属性齐全（name 与 default 都在）:', len(ok), '个槽位')
P('')

from collections import Counter
P('【槽位名 name 的书写系统】')
for k, v in Counter(script_kind(r['name']) for r in ok).most_common():
    P(f'  {k:<8}{v:>8}{v/len(ok)*100:>8.2f}%')
P('')
P('【默认值 default 的书写系统】')
for k, v in Counter(script_kind(r['default']) for r in ok).most_common():
    P(f'  {k:<8}{v:>8}{v/len(ok)*100:>8.2f}%')
P('')

# 交叉：名拉丁 × 值汉字
cross = Counter((script_kind(r['name']), script_kind(r['default'])) for r in ok)
P('【交叉表】名 × 值')
P(f"{'名':<8}{'值':<8}{'槽位数':>8}{'占比':>9}")
for (a, b), v in cross.most_common(12):
    P(f'{a:<8}{b:<8}{v:>8}{v/len(ok)*100:>8.2f}%')
P('')

P('【最常见的槽位名（前 30）】')
for k, v in Counter(r['name'] for r in ok).most_common(30):
    P(f'  {v:>5}  {k}')
P('')

P('【转义式原样样本（看实际形态，5 条）】')
shown = 0
for p in prompts:
    s = p.get('prompt') or ''
    if RE_ESCAPED.search(s) and shown < 5:
        i = s.find('argument')
        P('  id=' + str(p.get('id')) + ' | …' + s[max(0, i-40):i+180].replace('\n', ' ') + '…')
        shown += 1

o.close()
print('\n写出：', OUT)
