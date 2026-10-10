# -*- coding: utf-8 -*-
"""
§二 要**原样贴出**两条 JSON 版式块。逐字引用不能靠记忆，也不能靠 OCR 式转抄——
本脚本把要引的两块从语料里原样取出，并**把空格可视化**（空格→·），
供我逐字核对缩进与引号后写进稿子。

取两块：
  甲  最短的一条"管排版"的块（含 position / count → 证明它定的是"有几个、在哪儿"）
  乙  一条把画论词当**选项**开的块（keywords 里出现 写意／留白／气韵 一类）
"""
import json, os, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\20-要引的两条版式块-2026-10-09.txt'

SLOT = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
JB   = re.compile(r'\{[^{}]*?"[^"]+"\s*:[^{}]*?\}')

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')

P('§二 要原样引用的两条 JSON 版式块    2026-10-09')
P('=' * 78)

def show(tag, b, rec_prompt):
    P('')
    P('【%s】' % tag)
    P('-' * 78)
    P('  块长 %d 字符' % len(b))
    P('  ---- 原样（空格已换成 · 以便核缩进）----')
    for ln in b.split('\n'):
        P('    |' + ln.replace(' ', '\u00b7') + '|')
    P('  ---- 原样（可直接转抄）----')
    for ln in b.split('\n'):
        P('    ' + ln)
    P('  ---- 所在模板（头 200 字符）----')
    P('    ' + rec_prompt[:200].replace('\n', ' / '))

# 甲：最短且同时含 position 与 count 的块
cands = []
for r in rows:
    t = r.get('prompt') or ''
    rest = SLOT.sub('', t)
    for m in JB.finditer(rest):
        b = m.group(0)
        if 'argument' in b:
            continue
        if '"position"' in b and '"count"' in b:
            cands.append((len(b), b, t))
cands.sort(key=lambda x: x[0])
if cands:
    show('甲 最短的"管排版"块（含 position 与 count）', cands[0][1], cands[0][2])
    P('')
    P('  （同类块共 %d 个；长度分位 p50=%d 字符）'
      % (len(cands), sorted(c[0] for c in cands)[len(cands) // 2]))

# 乙：keywords 里同时含多个画论词的块，取最短
BING = ['写意', '留白', '气韵', '水墨', '工笔', '意境', '青绿', '山水']
cands2 = []
for r in rows:
    t = r.get('prompt') or ''
    rest = SLOT.sub('', t)
    for m in JB.finditer(rest):
        b = m.group(0)
        if 'argument' in b:
            continue
        if b.count('"keywords"') >= 1 and len([w for w in BING if w in b]) >= 3:
            cands2.append((len(b), b, t))
cands2.sort(key=lambda x: x[0])
if cands2:
    show('乙 keywords 里含三个以上画论词的块（最短）', cands2[0][1], cands2[0][2])
    P('')
    P('  （同类块共 %d 个）' % len(cands2))

o.close()
print('写盘：%s' % OUT)
print('OK')
