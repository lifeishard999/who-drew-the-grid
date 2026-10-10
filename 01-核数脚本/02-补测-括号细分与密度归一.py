# -*- coding: utf-8 -*-
"""
01 号脚本炸出两个问题，本脚本专治：

【问题一】花括号分两类还是三类？
  01 把「非 slot 花括号」笼统算作 C 类 3,424 个。但首条样本
  `{argument name=\"main title\" default=\"出师表\"}` 是**转义引号**的 argument，
  与 `{"title": "学习目标", "position": "右上角方框"}` 这种真 JSON 块**不是一回事**。
  → 必须细分：A 原生／A' 转义／J JSON 块／O 其他。

【问题二】★ 「画种在固定、画法在槽位」这个假设，01 的数据看着像被否了——
  但那个比较有个**分母偏置**：固定文本中位 323 汉字，槽位默认中位 0 汉字（均值 9）。
  绝对值不可比。→ 必须**按汉字数归一化**（画论词次 / 千汉字）。

另出：槽位名的集中度（长尾有多长）。
"""
import json, os, io, re, sys, collections

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\02-括号语法细分与画论词密度-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

SLOT     = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
SLOT_ESC = re.compile(r'\{argument\s+name=\\"([^"\\]*)\\"(?:\s+default=\\"([^"\\]*)\\")?\}')
ANYBRACE = re.compile(r'\{[^{}]{0,400}\}')
HAN      = re.compile(r'[\u4e00-\u9fff]')

CN_PAINT = ['水墨', '工笔', '写意', '山水', '画意', '意境', '宣纸', '留白', '皴', '泼墨',
            '白描', '气韵', '丹青', '没骨', '界画', '青绿', '卷轴', '立轴', '手卷', '斗方',
            '题跋', '章法', '笔法', '墨色', '淡彩', '重彩', '院体', '文人画', '国画',
            '花鸟', '人物画', '工笔画', '水墨画', '毛笔', '砚', '印章', '题款']
CN_PAINT_SET = sorted(set(CN_PAINT), key=len, reverse=True)

# 画种（这是什么画）／画法（怎么画）
HUAZHONG = ['国画', '中国画', '水墨画', '工笔画', '文人画', '山水画', '院体', '没骨', '界画', '白描']
HUAYI    = ['工笔', '写意', '水墨', '泼墨', '淡彩', '重彩', '青绿', '皴', '笔法', '墨色', '章法']

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')
def han(s): return len(HAN.findall(s or ''))

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list): rows.extend(d)

P('=' * 78)
P('水仙 · 括号语法细分与画论词密度    2026-10-09      记录 %d' % len(rows))
P('=' * 78)

# ── 问题一：括号细分 ────────────────────────────────────────────
P('')
P('【一】花括号到底分几类（01 的 C 类须拆开）')
kinds = collections.Counter()
o_samples = []; j_samples = []
for r in rows:
    t = r.get('prompt') or ''
    for b in ANYBRACE.findall(t):
        if SLOT.fullmatch(b):
            kinds['A · {argument name=".." default=".."}  原生'] += 1
        elif SLOT_ESC.fullmatch(b):
            kinds['A′· {argument name=\\"..\\" ..}       转义引号'] += 1
        elif re.match(r'\{\s*"', b) and '":' in b:
            kinds['J · {"key": value, ...}               JSON 块'] += 1
            if len(j_samples) < 12: j_samples.append(b)
        else:
            kinds['O · 其他'] += 1
            if len(o_samples) < 12: o_samples.append(b)
tot = sum(kinds.values())
for k, v in kinds.most_common():
    P('  %-46s %6d  (%.2f%%)' % (k, v, 100.0*v/tot))
P('  ---- J 类（JSON 块）样本 ----')
for b in j_samples: P('    %s' % b[:180].replace('\n', ' '))
P('  ---- O 类（其他）样本 ----')
for b in o_samples: P('    %s' % b[:180].replace('\n', ' '))
if not o_samples: P('    （无 O 类——括号只有上述三种写法）')

# ── 问题二：画论词密度（按汉字归一）────────────────────────────
P('')
P('=' * 78)
P('【二】★ 画论词落在固定文本还是槽位默认——**按汉字数归一**')
P('=' * 78)

tot_fix_han = 0; tot_def_han = 0
cnt_fix = 0; cnt_def = 0          # 词次
grp = {'画种': (0, 0), '画法': (0, 0), '其余画论词': (0, 0)}

for r in rows:
    t = r.get('prompt') or ''
    ms = list(SLOT.finditer(t))
    fixed = SLOT.sub('', t)
    defs  = ' '.join((m.group(2) or '') for m in ms)
    tot_fix_han += han(fixed); tot_def_han += han(defs)
    for w in CN_PAINT_SET:
        cnt_fix += fixed.count(w); cnt_def += defs.count(w)
        if w in HUAZHONG:
            a, b = grp['画种']; grp['画种'] = (a + fixed.count(w), b + defs.count(w))
        elif w in HUAYI:
            a, b = grp['画法']; grp['画法'] = (a + fixed.count(w), b + defs.count(w))
        else:
            a, b = grp['其余画论词']; grp['其余画论词'] = (a + fixed.count(w), b + defs.count(w))

P('  固定文本总汉字 %d ；槽位默认总汉字 %d  →  固定占 %.2f%%'
  % (tot_fix_han, tot_def_han, 100.0*tot_fix_han/(tot_fix_han+tot_def_han)))
P('')
P('  %-12s %8s %8s %12s %12s %8s' % ('类别', '固定词次', '默认词次', '固定/千汉字', '默认/千汉字', '倍差'))
for name, (f, d) in [('画论词合计', (cnt_fix, cnt_def))] + list(grp.items()):
    rf = 1000.0*f/max(tot_fix_han, 1); rd = 1000.0*d/max(tot_def_han, 1)
    P('  %-12s %8d %8d %12.2f %12.2f %8s'
      % (name, f, d, rf, rd, ('%.1f×' % (rf/rd)) if rd else '∞（默认侧为 0）'))

P('')
P('  ★ 判读要点：')
P('    · 若「画种」「画法」两组的倍差接近，则「画种定义／画法可协商」**不成立**——')
P('      两类词的去向相同，说明可协商性不是按词类分配的。')
P('    · 若画法在默认侧的密度显著更高，则原假设成立。')

# ── 槽位名的集中度 ─────────────────────────────────────────────
P('')
P('=' * 78)
P('【三】槽位名的集中度（"可变性"的词汇表有多长尾）')
P('=' * 78)
names = collections.Counter()
for r in rows:
    for m in SLOT.finditer(r.get('prompt') or ''):
        names[m.group(1)] += 1
tot_s = sum(names.values())
once = sum(1 for v in names.values() if v == 1)
P('  槽位总数 %d ；槽位名种类 %d ；只出现 1 次的种类 %d (%.1f%%)'
  % (tot_s, len(names), once, 100.0*once/len(names)))
cum = 0
for n in (1, 5, 10, 20, 50, 100, 500):
    cum = sum(v for _, v in names.most_common(n))
    P('    前 %-4d 种槽位名 累计 %6d 个槽位 = %.2f%%' % (n, cum, 100.0*cum/tot_s))
P('  ★ 对照：JourneyDB 的 Style 层 TTR 0.018（极度收敛）／Content 层 0.086。')
P('    这里的"槽位名"是**词汇表**层，长尾长说明**可协商的名目高度个体化**；')
P('    但**发生量**集中在前几种，说明**实际可协商的东西高度雷同**。')

o.close()
sys.stderr.write('DONE\n')
print('写盘：%s' % OUT)
