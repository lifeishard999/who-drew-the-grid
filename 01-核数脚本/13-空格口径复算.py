# -*- coding: utf-8 -*-
"""
★ 冲突复核：03 号报告说「槽位默认值的中位汉字数是 0」「半数以上的槽位默认值一个汉字都没有」，
而 12 号脚本的 C 段实测是 **5,906 : 2,238（含汉字占 72.5%）**——两者不可能同真。

本节（§一）正文只报一个数，报的必须是真的。故先把口径摊开重算：

  1. 先复现旧数（槽位总数、默认侧汉字总量 50,965），确认提取口径没变；
  2. 然后把「中位 0 汉字」在**两种分母**上各算一遍：
       分母甲 = 每条模板（把所有默认值拼起来）——03 §一 的长度表看似是这一种
       分母乙 = 每个槽位（单个 default）
     看哪个给出 0，另一个给出什么。
  3. 另报：单个默认值的汉字数分布、字符数中位、零汉字占比。
"""
import json, os, io, re, sys, statistics

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\13-空格口径复算-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

# 同时吃 A 类与 A′ 类（转义引号变体）
SLOT = re.compile(r'\{argument\s+name=\\?"([^"\\]*)\\?"(?:\s+default=\\?"([^"\\]*)\\?")?\s*\}')
HAN  = re.compile(r'[\u4e00-\u9fff]')

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')

P('空格口径复算    2026-10-09    记录 %d' % len(rows))
P('=' * 78)

# ── 1 提取 ────────────────────────────────────────────────
slot_han, slot_char, slot_has_default = [], [], 0
per_tpl_han, per_tpl_char = [], []
slot_names = []
total_slot = 0

for r in rows:
    t = r.get('prompt') or ''
    ms = list(SLOT.finditer(t))
    total_slot += len(ms)
    acc_h = acc_c = 0
    for m in ms:
        slot_names.append(m.group(1))
        v = m.group(2)
        if v is None or v == '':
            continue
        slot_has_default += 1
        h = len(HAN.findall(v))
        slot_han.append(h)
        slot_char.append(len(v))
        acc_h += h
        acc_c += len(v)
    per_tpl_han.append(acc_h)
    per_tpl_char.append(acc_c)

P('')
P('【0】先复现旧数，确认提取口径一致')
P('-' * 78)
P('  槽位总数（本脚本提取）        %d      （旧记 8,145）' % total_slot)
P('  其中带非空 default 的槽位      %d' % slot_has_default)
P('  默认侧汉字总量                %d      （旧记 50,965）' % sum(slot_han))
P('  默认侧字符总量                %d' % sum(slot_char))
P('  槽位名种类                    %d      （旧记 2,109）' % len(set(slot_names)))

# ── 2 两种分母下的「中位」 ─────────────────────────────────
P('')
P('【1】★「中位 0 个汉字」到底是在哪个分母上算的')
P('-' * 78)
P('  分母甲＝每条模板（%d 条；无槽位的记录按 0 计）' % len(rows))
P('      汉字数中位 = %s    字符数中位 = %s'
  % (statistics.median(per_tpl_han), statistics.median(per_tpl_char)))
P('      汉字数为 0 的模板 %d 条（%.1f%%）'
  % (sum(1 for x in per_tpl_han if x == 0),
     100.0 * sum(1 for x in per_tpl_han if x == 0) / len(per_tpl_han)))
P('')
P('  分母甲′＝只算**含槽位**的模板（%d 条）'
  % sum(1 for x in per_tpl_char if x > 0))
sub_h = [x for x in per_tpl_han if True]
_nz = [x for x, c in zip(per_tpl_han, per_tpl_char) if c > 0]
P('      汉字数中位 = %s    字符数中位 = %s'
  % (statistics.median(_nz), statistics.median([c for c in per_tpl_char if c > 0])))
P('')
P('  分母乙＝每个槽位（%d 个非空默认值）' % len(slot_han))
P('      汉字数中位 = %s    汉字数均值 = %.2f'
  % (statistics.median(slot_han), sum(slot_han) / len(slot_han)))
P('      字符数中位 = %s    字符数均值 = %.1f'
  % (statistics.median(slot_char), sum(slot_char) / len(slot_char)))
P('      **汉字数为 0 的槽位 %d 个（%.1f%%）**'
  % (sum(1 for x in slot_han if x == 0),
     100.0 * sum(1 for x in slot_han if x == 0) / len(slot_han)))
P('      汉字数为 0 或 1 的槽位 %d 个（%.1f%%）'
  % (sum(1 for x in slot_han if x <= 1),
     100.0 * sum(1 for x in slot_han if x <= 1) / len(slot_han)))

# ── 3 分布 ───────────────────────────────────────────────
P('')
P('【2】单个默认值的汉字数分布（分母乙）')
P('-' * 78)
buckets = [('0', 0, 0), ('1', 1, 1), ('2–4', 2, 4), ('5–9', 5, 9),
           ('10–19', 10, 19), ('20–49', 20, 49), ('≥50', 50, 10 ** 9)]
for lab, lo, hi in buckets:
    n = sum(1 for x in slot_han if lo <= x <= hi)
    P('  %-6s %6d  %6.2f%%' % (lab, n, 100.0 * n / len(slot_han)))
P('')
P('  十分位（汉字数）：%s' % [int(statistics.quantiles(slot_han, n=10)[i]) for i in range(9)])
P('  四分位（汉字数）：p25=%d  p50=%d  p75=%d'
  % (int(statistics.quantiles(slot_han, n=4)[0]),
     int(statistics.median(slot_han)),
     int(statistics.quantiles(slot_han, n=4)[2])))

# ── 4 对照：若把空的 default 也算作 0 ──────────────────────
P('')
P('【3】对照：所有 %d 个槽位（含无默认值的）一并算' % total_slot)
P('-' * 78)
allh = slot_han + [0] * (total_slot - slot_has_default)
P('      汉字数中位 = %s    汉字数为 0 的占 %.1f%%'
  % (statistics.median(allh),
     100.0 * sum(1 for x in allh if x == 0) / len(allh)))

o.close()
print('写盘：%s' % OUT)
print('OK')
