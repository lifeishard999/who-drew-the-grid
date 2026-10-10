# -*- coding: utf-8 -*-
"""
口径订正：13 号复算查出「槽位默认中位 0 汉字」是**分母错**——
01 号脚本 len_def_han 是**按记录**算的（每条记录所有默认值拼接），
分母 5,452 里有 2,520 条根本没有槽位，中位数被这一半拉成 0。
03 号给它配的注解「半数以上的槽位默认值一个汉字都没有」是**错的**（按槽位算只有 27.5%）。

本脚本用 01 号**原样的** SLOT 正则（A 类，8,145 个），做三件更正性的事：
  ① 复现旧数（8,145／50,965），证明口径一致；
  ② 报**同一分母**下的配对比较：在**含槽位的记录**里，策展人预制汉字 与 留给用户填的汉字
     —— 这才是 §一 要的那个数（同一个记录，两边可比）；
  ③ 报**按槽位**的默认值汉字分布（更正后的口径）。
"""
import json, os, io, re, sys, statistics, collections

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\14-配对口径重算-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

SLOT = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')   # 与 01 号逐字相同
HAN  = re.compile(r'[\u4e00-\u9fff]')
def han(s): return len(HAN.findall(s or ''))

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')

P('配对口径重算    2026-10-09    记录 %d' % len(rows))
P('=' * 78)

fx_han, df_han, fx_ch, df_ch = [], [], [], []
has_slot = []          # ★ 判据＝"记录里有槽位"，与 01 号一致（不能用默认值字符数>0，
slot_han = []          #   否则 default="" 的那一条会被误算作无槽位）
n_slot = 0
for r in rows:
    t = r.get('prompt') or ''
    ms = list(SLOT.finditer(t))
    n_slot += len(ms)
    has_slot.append(1 if ms else 0)
    fixed = SLOT.sub('', t)
    defs = ' '.join((m.group(2) or '') for m in ms)
    fx_han.append(han(fixed)); df_han.append(han(defs))
    fx_ch.append(len(fixed));  df_ch.append(len(defs))
    for m in ms:
        slot_han.append(han(m.group(2) or ''))

P('')
P('【0】复现旧数（与 01 号口径逐字相同）')
P('-' * 78)
P('  总槽位            %d   （旧记 8,145）' % n_slot)
P('  默认侧汉字总量    %d   （旧记 50,965）' % sum(slot_han))
P('  固定侧汉字总量    %d   （旧记 1,906,553）' % sum(fx_han))
P('  含槽位记录        %d   （旧记 2,932）' % sum(has_slot))

P('')
P('【1】★ 分母甲＝全部 %d 条记录（01 号用的分母，含 %d 条无槽位者）'
  % (len(rows), has_slot.count(0)))
P('-' * 78)
P('  固定文本  中位 %d 汉字 / %d 字符' % (statistics.median(fx_han), statistics.median(fx_ch)))
P('  槽位默认  中位 %d 汉字 / %d 字符   ← 旧报告「6 字符 / 0 汉字」即此格'
  % (statistics.median(df_han), statistics.median(df_ch)))
P('  ★ 该 0 由 %d 条**没有槽位**的记录造成（占 %.1f%%）——不是"槽位默认值不含汉字"。'
  % (has_slot.count(0), 100.0 * has_slot.count(0) / len(rows)))

idx = [i for i, h in enumerate(has_slot) if h]
P('')
P('【2】★★ 分母乙＝只算**含槽位**的 %d 条记录（两边同一分母，可比）' % len(idx))
P('-' * 78)
f_s = [fx_han[i] for i in idx]; d_s = [df_han[i] for i in idx]
fc_s = [fx_ch[i] for i in idx]; dc_s = [df_ch[i] for i in idx]
P('  预制文本（策展人写的）  中位 %d 汉字 / %d 字符   均值 %.0f 汉字'
  % (statistics.median(f_s), statistics.median(fc_s), sum(f_s) / len(f_s)))
P('  空格默认（留给用户的）  中位 %d 汉字 / %d 字符   均值 %.0f 汉字'
  % (statistics.median(d_s), statistics.median(dc_s), sum(d_s) / len(d_s)))
P('  ★ 汉字中位比  预制 : 可填 = %d : %d  ＝ %.1f : 1'
  % (statistics.median(f_s), statistics.median(d_s),
     statistics.median(f_s) / max(statistics.median(d_s), 1)))
P('  ★ 总量比      固定 %d : 默认 %d  ＝ %.1f : 1'
  % (sum(f_s), sum(d_s), sum(f_s) / max(sum(d_s), 1)))
P('  ★ 逐条配对比：预制汉字÷可填汉字，中位 %.1f 倍'
  % statistics.median([f / max(d, 1) for f, d in zip(f_s, d_s)]))

P('')
P('【3】★ 分母丙＝按**槽位**（%d 个）——更正后的口径' % len(slot_han))
P('-' * 78)
P('  单个默认值  中位 %d 汉字 / %d 字符；均值 %.2f 汉字'
  % (statistics.median(slot_han), 0, sum(slot_han) / len(slot_han)))
P('  ★ 一个汉字也没有的槽位 %d 个（%.1f%%）'
  % (sum(1 for x in slot_han if x == 0),
     100.0 * sum(1 for x in slot_han if x == 0) / len(slot_han)))
P('  ★ 汉字数 ≤ 4 的槽位 %d 个（%.1f%%）'
  % (sum(1 for x in slot_han if x <= 4),
     100.0 * sum(1 for x in slot_han if x <= 4) / len(slot_han)))
q = statistics.quantiles(slot_han, n=4)
P('  四分位 p25=%d  p50=%d  p75=%d' % (q[0], statistics.median(slot_han), q[2]))
P('  分布：0 → %d ／ 1 → %d ／ 2–4 → %d ／ 5–9 → %d ／ 10–19 → %d ／ 20+ → %d'
  % (sum(1 for x in slot_han if x == 0), sum(1 for x in slot_han if x == 1),
     sum(1 for x in slot_han if 2 <= x <= 4), sum(1 for x in slot_han if 5 <= x <= 9),
     sum(1 for x in slot_han if 10 <= x <= 19), sum(1 for x in slot_han if x >= 20)))

# 每条记录里，若把全部默认值算作"用户可改的部分"的**上限**，字数最多的一条是多少
P('')
P('【4】§一 那条细读样本的逐字拆解（91 字符 / 49 汉字 那条）')
P('-' * 78)
TARGET = '中国传统水墨画风格演绎'
for i, r in enumerate(rows):
    t = r.get('prompt') or ''
    if t.startswith(TARGET):
        ms = list(SLOT.finditer(t))
        fixed = SLOT.sub('', t)
        defs = ' '.join((m.group(2) or '') for m in ms)
        P('  原文 %s' % t)
        P('  整条：%d 字符 ／ %d 汉字' % (len(t), han(t)))
        P('  预制部分（撤掉槽位）：%d 字符 ／ %d 汉字' % (len(fixed), han(fixed)))
        P('  槽位 %d 个；默认值：%s（%d 汉字）'
          % (len(ms), defs, han(defs)))
        P('  默认值占全条汉字数的 %.1f%%' % (100.0 * han(defs) / han(t)))
        break
else:
    P('  ⚠ 未找到以「%s」开头的记录' % TARGET)

o.close()
print('写盘：%s' % OUT)
print('OK')
