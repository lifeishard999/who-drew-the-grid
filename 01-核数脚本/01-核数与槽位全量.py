# -*- coding: utf-8 -*-
"""
路径甲（书写语法）开写前的核数与补测。只读语料，只写一份结果文件。

做四件事：
  ① 复核 2026-09-20 那轮的四条硬数（槽位 8,145／53.78%／1.49／497:6）——不预设它还对
  ② 补做 §八 未做 4：全量弄清花括号的**第二种结构化语法**（非 slot 的 3,420 个是什么）
  ③ 补做 §八 未做 5：中国画子集里「画种 vs 画法」的固定/槽位切分
  ④ 口径写死：长度同时报**字符数**与**汉字数**两个口径（旧报告只报了字符数却称"字"）

口径纪律（本项目历次翻车的教训）：
  · 凡占比一律写明是【记录数】还是【词次/槽位数】；
  · 词表写死在文件里，不由当前状态重算；
  · 人工归并的分组另立映射表，并列出**未归并**的槽位名，绝不静默丢弃。
"""
import json, os, io, re, sys, collections

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\01-语料核数与槽位全量实测-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

SLOT     = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
ANYBRACE = re.compile(r'\{[^{}]{0,200}\}')
HAN      = re.compile(r'[\u4e00-\u9fff]')

CN_PAINT = ['水墨', '工笔', '写意', '山水', '画意', '意境', '宣纸', '留白', '皴', '泼墨',
            '白描', '气韵', '丹青', '没骨', '界画', '青绿', '卷轴', '立轴', '手卷', '斗方',
            '题跋', '章法', '笔法', '墨色', '淡彩', '重彩', '院体', '文人画', '国画',
            '花鸟', '人物画', '工笔画', '水墨画', '毛笔', '砚', '印章', '题款']
CN_PAINT_SET = sorted(set(CN_PAINT), key=len, reverse=True)

# 画种词（"这是什么画"）与画法/风格词（"怎么画"）分列——第三项的判据靠它们
HUAZHONG = ['国画', '中国画', '水墨画', '工笔画', '文人画', '山水画', '院体', '没骨', '界画', '白描']
HUAYI    = ['工笔', '写意', '水墨', '泼墨', '淡彩', '重彩', '青绿', '皴', '没骨', '白描', '笔法', '墨色', '章法']

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')

def han(s): return len(HAN.findall(s or ''))

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    fp = os.path.join(BASE, nm)
    with io.open(fp, 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

P('=' * 78)
P('水仙提示词库 · 核数与槽位全量实测     2026-10-09')
P('数据：%s' % BASE)
P('记录总条数 %d' % len(rows))
P('=' * 78)

# ── ① 复核旧四条 ────────────────────────────────────────────────
P('')
P('【一】复核 2026-09-20 那轮的四条硬数')
n_slot = 0; n_slot_rec = 0; n_brace = 0
slot_names = collections.Counter()
len_fixed_ch = []; len_def_ch = []; len_fixed_han = []; len_def_han = []
brace_kinds = collections.Counter(); brace_other_samples = []
fixed_with_paint = 0; def_with_paint = 0

for r in rows:
    t = r.get('prompt') or ''
    ms = list(SLOT.finditer(t))
    if ms:
        n_slot_rec += 1; n_slot += len(ms)
    allb = ANYBRACE.findall(t)
    n_brace += len(allb) - len(ms)
    for b in allb:
        if SLOT.fullmatch(b):
            brace_kinds['A·{argument name=.. default=..}'] += 1
        elif re.fullmatch(r'\{argument\s+name="[^"]*"\}', b):
            brace_kinds['B·{argument name=..}（无 default）'] += 1
        else:
            brace_kinds['C·其他'] += 1
            if len(brace_other_samples) < 40:
                brace_other_samples.append(b)
    fixed = SLOT.sub('', t)
    defs  = ' '.join((m.group(2) or '') for m in ms)
    len_fixed_ch.append(len(fixed));      len_def_ch.append(len(defs))
    len_fixed_han.append(han(fixed));     len_def_han.append(han(defs))
    if any(w in fixed for w in CN_PAINT_SET): fixed_with_paint += 1
    if any(w in defs  for w in CN_PAINT_SET): def_with_paint += 1
    for m in ms: slot_names[m.group(1)] += 1

def med(a):
    s = sorted(a); return s[len(s)//2] if s else 0
def mean(a):
    return (sum(a)/len(a)) if a else 0

P('  总槽位数              %d' % n_slot)
P('  含槽位记录            %d  = %.2f%%  （分母＝记录数 %d）' % (n_slot_rec, 100.0*n_slot_rec/len(rows), len(rows)))
P('  平均每条槽位          %.2f' % (n_slot/max(len(rows),1)))
P('  非 slot 花括号        %d   ← 旧报告 3,420' % n_brace)
P('')
P('  ---- ★ 长度：两个口径并报（旧报告只报字符数却称"字"）----')
P('  固定文本  中位 %d 字符 / %d 汉字    平均 %.0f 字符 / %.0f 汉字'
  % (med(len_fixed_ch), med(len_fixed_han), mean(len_fixed_ch), mean(len_fixed_han)))
P('  槽位默认  中位 %d 字符 / %d 汉字    平均 %.0f 字符 / %.0f 汉字'
  % (med(len_def_ch), med(len_def_han), mean(len_def_ch), mean(len_def_han)))
P('  ★ 汉字口径下的比值 固定:默认 = %.1f : 1' % (med(len_fixed_han)/max(med(len_def_han),1)))
P('')
P('  画论语汇落【固定文本】的记录 %d = %.2f%%' % (fixed_with_paint, 100.0*fixed_with_paint/len(rows)))
P('  画论语汇落【槽位默认值】的记录 %d = %.2f%%' % (def_with_paint, 100.0*def_with_paint/len(rows)))

# ── ② 花括号全量语法 ───────────────────────────────────────────
P('')
P('=' * 78)
P('【二】★ 补做 §八-4：花括号到底是什么语法')
P('=' * 78)
tot_b = sum(brace_kinds.values())
for k, v in brace_kinds.most_common():
    P('  %-34s %6d  (%.2f%%)' % (k, v, 100.0*v/max(tot_b,1)))
P('')
if brace_other_samples:
    P('  ---- C 类（其他）样本，前 %d 条 ----' % len(brace_other_samples))
    seen = set()
    for b in brace_other_samples:
        key = re.sub(r'"[^"]*"', '"…"', b)
        if key in seen: continue
        seen.add(key)
        P('    %s' % b[:150])
    P('  去重后形态数 %d' % len(seen))
else:
    P('  ---- 无 C 类：所有花括号都是 {argument} 语法 ----')

# ── ③ 槽位名全表 ───────────────────────────────────────────────
P('')
P('=' * 78)
P('【三】槽位名全表（共 %d 种）' % len(slot_names))
P('=' * 78)
for i, (k, v) in enumerate(slot_names.most_common(), 1):
    P('  %3d. %-32s %6d' % (i, k, v))

# ── ④ 中国画子集的「画种 vs 画法」切分 ────────────────────────
P('')
P('=' * 78)
P('【四】★ 补做 §八-5：中国画子集里，画种在固定、画法在槽位？')
P('=' * 78)

cn_recs = [r for r in rows if any(w in (r.get('prompt') or '') for w in CN_PAINT_SET)]
P('  中国画子集（内容判定，词表 %d 词）＝ %d 条 = %.2f%%'
  % (len(CN_PAINT_SET), len(cn_recs), 100.0*len(cn_recs)/len(rows)))

cn_slot_recs = [r for r in cn_recs if SLOT.search(r.get('prompt') or '')]
P('  其中【含槽位】者 %d 条 = 该子集的 %.2f%%' % (len(cn_slot_recs), 100.0*len(cn_slot_recs)/max(len(cn_recs),1)))

P('')
P('  ---- 4.1 画种词与画法词，各落在哪一侧（记录数，分母＝中国画子集 %d）----' % len(cn_recs))
P('  %-10s %10s %10s %10s' % ('词', '固定文本', '槽位默认', '固定:槽位'))
for w in (['国画', '中国画', '水墨画', '工笔画', '文人画', '山水画'] +
          ['工笔', '写意', '水墨', '泼墨', '淡彩', '重彩', '青绿', '白描', '笔法', '墨色']):
    nf = sum(1 for r in cn_recs
             if w in SLOT.sub('', r.get('prompt') or ''))
    nd = sum(1 for r in cn_recs
             if any(w in (m.group(2) or '') for m in SLOT.finditer(r.get('prompt') or '')))
    ratio = ('%.1f' % (nf/nd)) if nd else ('%d:0' % nf)
    P('  %-10s %10d %10d %10s' % (w, nf, nd, ratio))

P('')
P('  ---- 4.2 该子集内出现过的槽位名（哪些东西被当作"可协商"）----')
cn_slot_names = collections.Counter()
for r in cn_slot_recs:
    for m in SLOT.finditer(r.get('prompt') or ''):
        cn_slot_names[m.group(1)] += 1
for k, v in cn_slot_names.most_common(30):
    P('      %-30s %5d' % (k, v))

P('')
P('  ---- 4.3 ★ 默认值含画论语汇的槽位，都是些什么槽 ----')
defslot = collections.Counter()
for r in rows:
    for m in SLOT.finditer(r.get('prompt') or ''):
        if any(w in (m.group(2) or '') for w in CN_PAINT_SET):
            defslot[m.group(1)] += 1
for k, v in defslot.most_common(30):
    P('      %-30s %5d' % (k, v))

P('')
P('  ---- 4.4 ★ 铁证样本：默认值含画论语汇的槽位，逐条列（上限 60）----')
n = 0
for r in rows:
    t = r.get('prompt') or ''
    for m in SLOT.finditer(t):
        d = m.group(2) or ''
        if any(w in d for w in CN_PAINT_SET):
            n += 1
            if n <= 60:
                P('   [%s] slot=%s default=%s' % (r.get('category'), m.group(1), d))
P('      合计 %d 个这样的槽位' % n)

o.close()
sys.stderr.write('DONE\n')
print('写盘：%s' % OUT)
