# -*- coding: utf-8 -*-
"""
26 号查出：槽位有两种**互不重叠**的写法——
  ① 直引号式  {argument name="hair color" default="浅蓝色"}          8,145 个槽 / 2,932 条记录
  ② 转义式    {argument name=\"hair color\" default=\"浅蓝色\"}       945 个槽 /   233 条记录
`01` 号只认前者，于是稿子里所有建立在它上面的数都偏小。本脚本按**并集**重算全部要用的量。
（口径：两种写法在文本层是同一个装置——一个有名字、有默认值的洞；分开只是因为它嵌在 JSON 字符串里。）

重算清单：
  分段 R / J / A（A ＝两式之和）的汉字数与画论词词次
  分母乙（含槽位的 3,165 条）：预制中位 : 可填默认中位（汉字 与 字符 两个口径）
  分母丙（每槽 9,090 个）：默认值汉字中位、零汉字比例、分布
  槽位名分布（种数、长尾、前 20）
  零汉字默认值的槽位与槽名前列
  含 JSON 版式块的记录数
  默认值含画论词的槽位**全表**（供重新逐条判定同形异义）
"""
import json, os, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\27-两式合并后全面重算-2026-10-09.txt'

SLOT_P = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
SLOT_E = re.compile(r'\{argument\s+name=\\"([^"]*?)\\"(?:\s+default=\\"([^"]*?)\\")?\}')
JB     = re.compile(r'\{[^{}]*?"[^"]+"\s*:[^{}]*?\}')
HAN    = re.compile(r'[\u4e00-\u9fff]')

CN_PAINT = ['水墨', '工笔', '写意', '山水', '画意', '意境', '宣纸', '留白', '皴', '泼墨',
            '白描', '气韵', '丹青', '没骨', '界画', '青绿', '卷轴', '立轴', '手卷', '斗方',
            '题跋', '章法', '笔法', '墨色', '淡彩', '重彩', '院体', '文人画', '国画',
            '花鸟', '人物画', '工笔画', '水墨画', '毛笔', '砚', '印章', '题款']
CN_SET = sorted(set(CN_PAINT), key=len, reverse=True)

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

def count_words(s):
    s = s or ''; hit = collections.Counter()
    for w in CN_SET:
        n = s.count(w)
        if n: hit[w] += n; s = s.replace(w, '\x00' * len(w))
    return hit

def slots_of(t):
    """返回 [(名, 默认值, 式样)]，两式并集，互不重叠。"""
    out = []
    for m in SLOT_E.finditer(t):
        out.append((m.group(1), m.group(2) or '', 'E'))
    tt = t
    for m in reversed(list(SLOT_E.finditer(t))):
        tt = tt[:m.start()] + '\x00' * (m.end() - m.start()) + tt[m.end():]
    for m in SLOT_P.finditer(tt):
        out.append((m.group(1), m.group(2) or '', 'P'))
    return out

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')
P('两式合并后全面重算    2026-10-09    记录 %d' % len(rows))
P('=' * 78)

tot_han = collections.Counter(); tot_words = collections.Counter()
words_in = {'A': collections.Counter(), 'J': collections.Counter(), 'R': collections.Counter()}
slot_names = []
per_slot_han = []
per_slot_ch  = []
zero_han_slots = []
paint_slots = []          # 默认值含画论词的槽位
phen_han = []; phan_def = []      # 分母乙：每条记录的预制汉字 / 默认值汉字
phen_ch  = []; pch_def = []
n_with_slot = 0
rec_with_j = 0

for r in rows:
    t = r.get('prompt') or ''
    ss = slots_of(t)
    if ss: n_with_slot += 1
    a_txt = ' '.join(d for _, d, _ in ss)
    for nm, d, style in ss:
        slot_names.append(nm)
        h = len(HAN.findall(d)); c = len(d)
        per_slot_han.append(h); per_slot_ch.append(c)
        if h == 0: zero_han_slots.append((nm, d))
        if any(w in d for w in CN_SET): paint_slots.append((nm, d))
    # rest：把两式槽位都挖掉
    rest = SLOT_P.sub('', SLOT_E.sub('', t))
    j_parts = []
    for m in JB.finditer(rest):
        b = m.group(0)
        if 'argument' in b: continue
        j_parts.append(b)
    if j_parts: rec_with_j += 1
    j_txt = ' '.join(j_parts)
    r_txt = JB.sub(lambda m: '' if 'argument' not in m.group(0) else m.group(0), rest)

    # 分母乙：预制 = 原串减去两式槽位（连同默认值）
    pref = SLOT_P.sub('', SLOT_E.sub('', t))
    if ss:
        phan_def.append(sum(len(HAN.findall(d)) for _, d, _ in ss))
        pch_def.append(sum(len(d) for _, d, _ in ss))
        phen_han.append(len(HAN.findall(pref))); phen_ch.append(len(pref))

    for k, s in (('A', a_txt), ('J', j_txt), ('R', r_txt)):
        tot_han[k] += len(HAN.findall(s))
        w = count_words(s); tot_words[k] += sum(w.values()); words_in[k].update(w)

def med(xs):
    xs = sorted(xs); n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2

P('')
P('【0】分段（A ＝两式槽位默认值之和）')
P('-' * 78)
# A 段汉字用 per_slot_han 直接加总，与 tot_han['A'] 对齐（a_txt 用空格拼接，空格不算汉字）
th = sum(tot_han.values())
for k, lab in (('R', '其余正文'), ('J', 'JSON 版式块'), ('A', '槽位默认值（可填）')):
    P('  %-22s %10d 汉字  %6.2f%%' % (lab, tot_han[k], 100.0 * tot_han[k] / th))
P('  合计 %d 汉字' % th)
P('  ★ A 段汉字合计（逐槽累加）%d' % sum(per_slot_han))

P('')
P('【1】画论词在三段的分布（词次）')
P('-' * 78)
tw = sum(tot_words.values())
for k, lab in (('R', '其余正文'), ('J', 'JSON 版式块'), ('A', '槽位默认值')):
    P('  %-22s %8d  %6.2f%%' % (lab, tot_words[k], 100.0 * tot_words[k] / tw))
P('  合计 %d' % tw)
P('  逐词（R / J / A）：')
for w in sorted(set().union(*[set(v) for v in words_in.values()]),
                key=lambda x: -(words_in['R'][x] + words_in['J'][x] + words_in['A'][x])):
    P('    %-8s R=%-6d J=%-6d A=%-6d' % (w, words_in['R'][w], words_in['J'][w], words_in['A'][w]))

P('')
P('【2】分母乙：含槽位的 %d 条记录（旧记 2,932；并集应为 3,165）' % n_with_slot)
P('-' * 78)
P('  预制部分   汉字 中位 %d  均值 %.0f ｜ 字符 中位 %d'
  % (med(phen_han), sum(phen_han) / len(phen_han), med(phen_ch)))
P('  可填默认值 汉字 中位 %d  均值 %.0f ｜ 字符 中位 %d'
  % (med(phan_def), sum(phan_def) / len(phan_def), med(pch_def)))
P('  ★ 汉字中位比 %d : %d   ；字符中位比 %d : %d'
  % (med(phen_han), med(phan_def), med(phen_ch), med(pch_def)))

P('')
P('【3】分母丙：每一个槽位（共 %d 个）' % len(per_slot_han))
P('-' * 78)
P('  默认值汉字中位 %d  均值 %.2f ｜ 字符中位 %d' % (med(per_slot_han), sum(per_slot_han)/len(per_slot_han), med(per_slot_ch)))
P('  零汉字 %d（%.1f%%）  ≤4 汉字 %d（%.1f%%）'
  % (sum(1 for x in per_slot_han if x == 0), 100.0*sum(1 for x in per_slot_han if x==0)/len(per_slot_han),
     sum(1 for x in per_slot_han if x <= 4), 100.0*sum(1 for x in per_slot_han if x<=4)/len(per_slot_han)))
for lo, hi in ((0,0),(1,1),(2,4),(5,9),(10,19),(20,10**9)):
    P('    %s: %d' % ('%d'%lo if lo==hi else ('%d-%d'%(lo,hi) if hi<10**9 else '%d+'%lo),
                      sum(1 for x in per_slot_han if lo <= x <= hi)))

P('')
P('【4】槽位名分布（共 %d 个槽位）' % len(slot_names))
P('-' * 78)
c = collections.Counter(slot_names)
once = sum(1 for k, v in c.items() if v == 1)
top10 = sum(v for k, v in c.most_common(10))
P('  不同槽名 %d 种；只出现 1 次 %d 种（%.2f%%）；前 10 种合计 %d（%.2f%%）'
  % (len(c), once, 100.0 * once / len(c), top10, 100.0 * top10 / len(slot_names)))
for k, v in c.most_common(20):
    P('    %-26s %5d  %5.2f%%' % (k, v, 100.0 * v / len(slot_names)))

P('')
P('【5】零汉字默认值（%d 个槽位）的槽名前列' % len(zero_han_slots))
P('-' * 78)
c2 = collections.Counter(nm for nm, d in zero_han_slots)
for k, v in c2.most_common(12):
    P('    %-26s %5d' % (k, v))
P('  纯 ASCII 默认值 %d' % sum(1 for nm, d in zero_han_slots if d and all(ord(ch) < 128 for ch in d)))
P('  纯数字 %d' % sum(1 for nm, d in zero_han_slots if d and all(ch in '0123456789 .%#' for ch in d)))

P('')
P('【6】含 JSON 版式块的记录数 %d（占 %.1f%%）' % (rec_with_j, 100.0 * rec_with_j / len(rows)))

P('')
P('【7】★ 默认值含画论词的槽位全表（两式并集，共 %d 个）—— 供逐条重判同形异义' % len(paint_slots))
P('-' * 78)
for i, (nm, d) in enumerate(paint_slots, 1):
    P('  %3d. %-24s = %s' % (i, nm, d[:70]))

o.close()
print('写盘：%s' % OUT)
print('OK')
