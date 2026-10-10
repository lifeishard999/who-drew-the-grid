# -*- coding: utf-8 -*-
"""
第一节要"细读"一条模板。**必须是语料里真实的原文，逐字可查**，不能凭记忆写。

本脚本挑样本，不做统计：
  A. 定位那条"铁证样本"（含 default="工笔画风格" 的模板），取出**完整原文**。
  B. 挑一批**短**的、同时含【槽位】与【画论词】的模板——短才好细读。
  C. 顺带确认：槽位默认值里出现汉字的情况到底长什么样。
"""
import json, os, io, re, sys

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\12-细读候选样本-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

SLOT = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
HAN  = re.compile(r'[\u4e00-\u9fff]')

CN_PAINT = ['水墨', '工笔', '写意', '山水', '画意', '意境', '宣纸', '留白', '皴', '泼墨',
            '白描', '气韵', '丹青', '没骨', '界画', '青绿', '卷轴', '立轴', '手卷', '斗方',
            '题跋', '章法', '笔法', '墨色', '淡彩', '重彩', '院体', '文人画', '国画',
            '花鸟', '人物画', '工笔画', '水墨画', '毛笔', '砚', '印章', '题款']

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')

P('水仙 · 细读候选样本    2026-10-09    记录 %d' % len(rows))
P('=' * 78)

# ── A 铁证样本的完整原文 ────────────────────────────────────
P('')
P('【A】含 default="工笔画风格" 的模板（全文，逐字）')
P('-' * 78)
n = 0
for i, r in enumerate(rows):
    t = r.get('prompt') or ''
    if '工笔画风格' in t:
        n += 1
        if n <= 6:
            P('  #%d  [id=%s]' % (n, r.get('id') or r.get('slug') or '?'))
            P('  %s' % t)
            P('  ---')
P('  共 %d 条含「工笔画风格」' % n)

# ── B 短样本：含槽位 + 画论词，按字符数升序 ────────────────
P('')
P('【B】既含【槽位】又含【画论词】的**短**模板（升序取 20 条，便于细读）')
P('-' * 78)
cands = []
for r in rows:
    t = (r.get('prompt') or '').strip()
    if not SLOT.search(t):
        continue
    hit = [w for w in CN_PAINT if w in t]
    if not hit:
        continue
    cands.append((len(t), han := len(HAN.findall(t)), hit, t, r))
cands.sort(key=lambda x: (x[0], x[2]))
cands = cands[:60]
# 再按长度分层，抽头 20 条
shown = 0
for L, H, hit, t, r in cands:
    if shown >= 20:
        break
    shown += 1
    P('  [%d 字符 / %d 汉字] 画论词：%s' % (L, H, '、'.join(sorted(set(hit)))))
    P('  %s' % t)
    P('  ---')

# ── C 默认值含汉字 / 不含汉字，各看几个 ─────────────────────
P('')
P('【C】槽位默认值的两种样子（各 12 条）')
P('-' * 78)
with_han, without_han = [], []
for r in rows:
    for m in SLOT.finditer(r.get('prompt') or ''):
        v = m.group(2) or ''
        if not v:
            continue
        (with_han if HAN.search(v) else without_han).append((m.group(1), v))
P('  · 默认值**不含汉字**（前 12）：')
for k, v in without_han[:12]:
    P('      %-28s = %s' % (k, v))
P('  · 默认值**含汉字**（前 12）：')
for k, v in with_han[:12]:
    P('      %-28s = %s' % (k, v))
P('  默认值非空总数 %d ；含汉字 %d ；不含汉字 %d'
  % (len(with_han) + len(without_han), len(with_han), len(without_han)))

o.close()
print('写盘：%s' % OUT)
print('OK')
