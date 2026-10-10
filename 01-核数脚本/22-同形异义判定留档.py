# -*- coding: utf-8 -*-
"""
21 号把 A 段（具名槽位默认值）里 44 个含画论词的槽位摊开，肉眼一看就有假货：
    hair color = 青绿色          ← 这是头发的颜色
    character name = 一位面部留白的…  ← "留白"是版面义（与 [[shuixian-corpus]] 记的"留白 606 是排版义"同源）
§二 要报的数是"画论词真的进了可写格子的次数"，所以必须逐条判、并把判定**写死留档**
（口径纪律：人工判定要留档，否则下次无法复算）。

判定规则（保守，只踢掉"该词在此处根本不是画论义"的）：
    ✗ 青绿 → 颜色名（hair color / eye color / color palette / main green color / background colors）
    ✗ 留白 → 版面义（背景上的空白、脸部的空白）
    ✗ 淡彩 → "淡彩色"＝浅淡的颜色，不是"淡彩"这一画法
    ✗ 宣纸 → "宣纸象牙白"＝一种纸的颜色名
    ✗ 墨色 → "炭墨色"＝颜色名
其余一律计入（含"山水"作普通名词用的那些——宁可宽，不可窄）。
"""
import json, os, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙题库\..\水仙提示词库\shuixian-unified\data'
BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\22-同形异义判定-2026-10-09.txt'

SLOT = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
JB   = re.compile(r'\{[^{}]*?"[^"]+"\s*:[^{}]*?\}')
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

# ------- 人工判定表：按 21 号输出的序号 -------
# 值＝(是否计入, 剔除理由)
JUDGE = {
    2:  (False, '青绿＝眼睛的颜色'),
    5:  (False, '青绿＝颜色名（main green color）'),
    8:  (False, '青绿＝颜色名（background colors）'),
    9:  (False, '留白＝画面上的空白（版面义）'),
    12: (False, '淡彩＝"淡彩色"，浅淡的颜色'),
    19: (False, '宣纸＝"宣纸象牙白"，纸的颜色名'),
    24: (False, '墨色＝"炭墨色"，颜色名'),
    27: (False, '青绿＝颜色名（color palette）'),
    30: (False, '青绿＝头发的颜色'),
    32: (False, '青绿＝头发的颜色'),
    33: (False, '青绿＝头发的颜色'),
    36: (False, '青绿＝头发的颜色'),
    39: (False, '留白＝脸上的空白（版面义）'),
    41: (False, '青绿＝头发的颜色'),
}

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')

P('槽位侧画论词的同形异义判定    2026-10-09')
P('=' * 78)
P('记录 %d 条' % len(rows))
P('')

items = []
for r in rows:
    t = r.get('prompt') or ''
    for m in SLOT.finditer(t):
        nm, d = m.group(1), (m.group(2) or '')
        hit, s = [], d
        for w in sorted(set(CN_PAINT), key=len, reverse=True):
            n = s.count(w)
            if n:
                hit.append((w, n)); s = s.replace(w, '\x00' * len(w))
        if hit:
            items.append((nm, d, hit))

P('【甲】逐条判定')
P('-' * 78)
keep_n = drop_n = 0
drop_words = collections.Counter()
style_like = ('style', 'medium', 'texture', 'detail')
keep_style = 0
for i, (nm, d, hit) in enumerate(items, 1):
    ok, why = JUDGE.get(i, (True, ''))
    flag = '计入' if ok else '剔除'
    if ok:
        keep_n += 1
        if any(k in nm.lower() for k in style_like):
            keep_style += 1
    else:
        drop_n += 1
        for w, n in hit:
            drop_words[w] += n
    P('  %2d. [%s] %-20s = %s' % (i, flag, nm, d[:60]))
    if why:
        P('        └ %s' % why)

P('')
P('【乙】结论')
P('-' * 78)
P('  默认值含画论词的槽位（原样计）        %d 个' % len(items))
P('  其中同形异义、应予剔除               %d 个' % drop_n)
P('  ★ 画论词真的进了可写格子的槽位        %d 个' % keep_n)
P('  被剔除的词次按词分布：%s'
  % '、'.join('%s %d' % kv for kv in drop_words.most_common()))
P('')
P('  ★ 在这 %d 个里，槽名本身就是"风格／材质／技法"一类的（style / medium / texture / detail）'
  % keep_n)
P('    共 %d 个，占 %.1f%%' % (keep_style, 100.0 * keep_style / keep_n))

P('')
P('【丙】含 JSON 版式块的**记录数**（§二 若要报"多少条模板里都有这样一段"，报这个）')
P('-' * 78)
rec_with_j = 0
blk_total = 0
for r in rows:
    t = r.get('prompt') or ''
    rest = SLOT.sub('', t)
    bs = [m.group(0) for m in JB.finditer(rest) if 'argument' not in m.group(0)]
    if bs:
        rec_with_j += 1
        blk_total += len(bs)
P('  含至少一个 JSON 版式块的记录：%d 条（占全库 %.1f%%）'
  % (rec_with_j, 100.0 * rec_with_j / len(rows)))
P('  这些记录里的块总数：%d 个' % blk_total)
P('  ★ 口径注记：块数的两种正则给出不同结果（19 号 2,313 ／ 02 号 2,250），')
P('    故正文只报"记录数"，不报块数。')

o.close()
print('写盘：%s' % OUT)
print('OK')
