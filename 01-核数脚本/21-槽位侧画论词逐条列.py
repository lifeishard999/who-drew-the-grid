# -*- coding: utf-8 -*-
"""
§二 的唯一一个数，原拟报「默认值含画论词的槽位 44 个」。
但 19 号脚本把清单摊开一看，里面明显混着**同形异义**：
    hair color = 青绿色   ← 头发的颜色，不是"青绿山水"的青绿
    character name = 一位面部留白的柔和色调公主法师  ← "留白"是版面义（与 [[shuixian-corpus]] 记的"留白 606 是排版义"同源）
报数前必须逐条判。本脚本把 A 段（具名槽位默认值）里**每一处**画论词逐条列出，
连同槽位名与所在模板，供人工判定，并把判定结果写死留档。
"""
import json, os, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\21-槽位侧画论词逐条列-2026-10-09.txt'

SLOT = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')

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

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')

P('槽位默认值里的画论词，逐条（A 段）    2026-10-09')
P('=' * 78)

# 色彩／外貌类槽位名：这里的"青绿"多半是颜色名而非画论词
COLORISH = ('color', 'colour', 'palette', 'hair', 'eye', 'skin', 'green', 'print')

items = []
for r in rows:
    t = r.get('prompt') or ''
    for m in SLOT.finditer(t):
        nm, d = m.group(1), (m.group(2) or '')
        hit = []
        s = d
        for w in CN_SET:
            n = s.count(w)
            if n:
                hit.append((w, n))
                s = s.replace(w, '\x00' * len(w))
        if hit:
            items.append((nm, d, hit, t))

n_occ = 0
per_word = collections.Counter()
P('')
P('  共 %d 个槽位（与旧记 44 对照），逐条：' % len(items))
P('-' * 78)
for i, (nm, d, hit, t) in enumerate(items, 1):
    for w, n in hit:
        n_occ += n
        per_word[w] += n
    mark = ' ←色彩／外貌类槽名' if any(k in nm.lower() for k in COLORISH) else ''
    P('  %2d. %-20s = %s' % (i, nm, d[:70]))
    P('      └ 命中：%s%s' % ('、'.join('%s×%d' % (w, n) for w, n in hit), mark))
P('')
P('  词次合计 %d（与 19 号 A 段 48 对照）＝%s'
  % (n_occ, '、'.join('%s %d' % kv for kv in per_word.most_common())))

P('')
P('  ---- 按"槽名是否为色彩／外貌类"粗分（仅供人工判定的起点，不当结论）----')
c = sum(1 for nm, d, hit, t in items if any(k in nm.lower() for k in COLORISH))
P('     色彩／外貌类槽名的槽位 %d 个 ／ 其余 %d 个' % (c, len(items) - c))

P('')
P('  ---- 「留白」在 A 段的全部出现（逐条看是画论义还是排版义）----')
for nm, d, hit, t in items:
    if any(w == '留白' for w, _ in hit):
        P('     %-20s = %s' % (nm, d[:100]))

o.close()
print('写盘：%s' % OUT)
print('OK')
