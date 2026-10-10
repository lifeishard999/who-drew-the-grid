# -*- coding: utf-8 -*-
"""
27 号按**两式并集**重算后，默认值含画论词的槽位从 44 个变成 50 个（新增 6 个都是转义写法）。
本脚本在并集上重新逐条判定同形异义，并写死留档（口径纪律：人工判定要留档）。
判定规则与 22 号一致、从宽：
  ✗ 青绿 → 颜色名（hair color / eye color / color palette / main green color / background colors）
  ✗ 留白 → 版面义（画面上的空白、脸上的空白）
  ✗ 淡彩 → "淡彩色"＝浅淡的颜色
  ✗ 宣纸 → "宣纸象牙白"＝纸的颜色名（但 "纹理米色宣纸" 作材料用，计入）
  ✗ 墨色 → "炭墨色"＝颜色名
"""
import json, os, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\28-并集同形异义判定-2026-10-09.txt'

SLOT_P = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
SLOT_E = re.compile(r'\{argument\s+name=\\"([^"]*?)\\"(?:\s+default=\\"([^"]*?)\\")?\}')

CN_SET = sorted(set(['水墨', '工笔', '写意', '山水', '画意', '意境', '宣纸', '留白', '皴', '泼墨',
            '白描', '气韵', '丹青', '没骨', '界画', '青绿', '卷轴', '立轴', '手卷', '斗方',
            '题跋', '章法', '笔法', '墨色', '淡彩', '重彩', '院体', '文人画', '国画',
            '花鸟', '人物画', '工笔画', '水墨画', '毛笔', '砚', '印章', '题款']), key=len, reverse=True)

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

def slots_of(t):
    out = [(m.group(1), m.group(2) or '', 'E') for m in SLOT_E.finditer(t)]
    tt = t
    for m in reversed(list(SLOT_E.finditer(t))):
        tt = tt[:m.start()] + '\x00' * (m.end() - m.start()) + tt[m.end():]
    out += [(m.group(1), m.group(2) or '', 'P') for m in SLOT_P.finditer(tt)]
    return out

# 剔除表：27 号【7】输出的序号（并集 50 个）
DROP = {3:'青绿＝眼睛的颜色', 7:'青绿＝颜色名（main green color）',
        12:'青绿＝颜色名（background colors）', 13:'青绿＝颜色名（color palette）',
        14:'留白＝画面上的空白（版面义）', 17:'淡彩＝"淡彩色"，浅淡的颜色',
        24:'宣纸＝"宣纸象牙白"，纸的颜色名', 30:'墨色＝"炭墨色"，颜色名',
        33:'青绿＝颜色名（color palette）', 36:'青绿＝头发的颜色', 38:'青绿＝头发的颜色',
        39:'青绿＝头发的颜色', 42:'青绿＝头发的颜色', 45:'留白＝脸上的空白（版面义）',
        47:'青绿＝头发的颜色'}

paint = []
for r in rows:
    for nm, d, style in slots_of(r.get('prompt') or ''):
        if any(w in d for w in CN_SET):
            paint.append((nm, d, style))

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')
P('并集上的同形异义判定    2026-10-09    含画论词的槽位 %d 个' % len(paint))
P('=' * 78)

STYLE_LIKE = ('style', 'medium', 'texture', 'detail')
keep = drop = 0
keep_style = 0
drop_words = collections.Counter()
for i, (nm, d, style) in enumerate(paint, 1):
    ok = i not in DROP
    if ok:
        keep += 1
        if any(k in nm.lower() for k in STYLE_LIKE): keep_style += 1
    else:
        drop += 1
        s = d
        for w in CN_SET:
            n = s.count(w)
            if n: drop_words[w] += n; s = s.replace(w, '\x00' * len(w))
    P('  %3d. [%s] %-22s(%s) = %s' % (i, '计入' if ok else '剔除', nm, style, d[:58]))
    if not ok: P('         └ %s' % DROP[i])

P('')
P('【结论】')
P('-' * 78)
P('  默认值含画论词的槽位（原样计）   %d' % len(paint))
P('  同形异义、剔除                   %d' % drop)
P('  ★ 画论词真的进了可写格子          %d 个槽位' % keep)
P('  剔除的词次按词：%s' % '、'.join('%s %d' % kv for kv in drop_words.most_common()))
P('  ★ 其中槽名本身即"风格／材质／技法"类（style/medium/texture/detail）%d 个，占 %.1f%%'
  % (keep_style, 100.0 * keep_style / keep))
o.close()
print('写盘：%s' % OUT)
print('OK')
