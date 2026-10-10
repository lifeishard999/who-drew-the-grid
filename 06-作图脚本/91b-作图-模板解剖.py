# -*- coding: utf-8 -*-
r"""
91b · 生成「图 1　一条模板的解剖」。

底本＝稿内 §一 L37 逐字引过的那条模板（**原样，不改一字**）；标注的六项＝稿内 L39 逐字
给出的五样判断（媒介／笔触／层次／趣味／构图）＋句末的「留白」（§一 已点明它是画论词）。
★ 只读稿、只画稿内已有的东西；不引入任何新语料、新计数。

★ 122·丙：同一版图另出 PDF／EPS（矢量，直接由 figure 出，**非从 PNG 转**）
与 TIFF（由 24 位 PNG 无损转，LZW）。四件同源同版，排版方点名哪种格式都无须回头改图。
"""
import io
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10'
OUT = os.path.join(BASE, '图件', '图1.png')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
# ★ 122·丙：矢量件的字体按 TrueType 嵌入（42），不落 Type 3——
#   部分排版系统的 RIP 不收 Type 3 字体，中文尤甚。
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

# ── 稿内原文（L37 逐字）────────────────────────────────────────────────
TEMPLATE = '中国传统水墨画风格演绎 {argument name="subject" default="嫦娥奔月"}，富有表现力的黑色墨迹笔触，柔和的渐变，诗意般的简洁，极简主义构图，大面积留白'
with io.open(os.path.join(BASE, '论文-谁划的格子-投稿版.md'), encoding='utf-8', newline='') as f:
    raw = f.read()
L = raw.replace('\r\n', '\n').split('\n')
found = [i + 1 for i, l in enumerate(L) if TEMPLATE in l]
assert found, '★ 图所据的模板与稿内逐字不符——先核再画'
print('模板出处：修订版 L%s（逐字命中）' % found)

C_PRE, C_SLOT, C_WORD, C_LAB, C_GRID = '#4a6fa5', '#c0392b', '#1e7a5a', '#7a7a7a', '#cccccc'
FIG_W, FIG_H, FS = 7.2, 3.05, 11.0
PT = FIG_W * 72.0
UNIT = lambda fs: fs / PT * 100.0            # 一个全角字在数据坐标里的宽度


def w(s, fs):
    u = UNIT(fs)
    return sum(u if ('\u4e00' <= c <= '\u9fff' or '\u3000' <= c <= '\u303f'
                     or '\uff00' <= c <= '\uffef' or c in '，。、；：（）「」“”《》') else u * 0.52
               for c in s)


fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=300)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')

ROWS = [
    (86.0, [('中国传统水墨画风格演绎', 'pre', FS), (' ', 'gap', FS),
            ('{argument name="subject" default="嫦娥奔月"}', 'slot', 8.4)]),
    (62.0, [('，富有表现力的黑色墨迹笔触', 'pre', FS), ('，柔和的渐变', 'pre', FS)]),
    (38.0, [('，诗意般的简洁', 'pre', FS), ('，极简主义构图', 'pre', FS),
            ('，大面积', 'pre', FS), ('留白', 'word', FS)]),
]
LABELS = [
    (86.0, 0, '媒介（水墨画）'), (86.0, 2, '唯一可填的一格'),
    (62.0, 0, '笔触'), (62.0, 1, '层次'),
    (38.0, 0, '趣味'), (38.0, 1, '构图'), (38.0, 3, '画论词「留白」'),
]
COL = {'pre': C_PRE, 'slot': C_SLOT, 'word': C_WORD, 'gap': 'white'}

pos = {}
x0 = 4.0
for y, spans in ROWS:
    x = x0
    for k, (s, kind, fs) in enumerate(spans):
        if kind == 'slot':
            ax.text(x + w(s, fs) / 2, y, s, ha='center', va='center', fontsize=fs, color=C_SLOT,
                    bbox=dict(boxstyle='round,pad=0.35', fc='#fdecea', ec=C_SLOT, lw=1.3))
        else:
            ax.text(x, y, s, ha='left', va='center', fontsize=fs, color=COL[kind])
        pos[(y, k)] = (x, x + w(s, fs))
        x += w(s, fs)

for y, k, txt in LABELS:
    a, b = pos[(y, k)]
    xc = (a + b) / 2
    yy = y - 6.4
    ax.plot([xc, xc], [y - 3.0, yy + 1.4], color=C_LAB, lw=0.7, ls=(0, (2, 2)))
    ax.text(xc, yy - 0.6, txt, ha='center', va='top', fontsize=8.2,
            color=C_SLOT if '可填' in txt else C_LAB,
            fontweight='bold' if '可填' in txt else 'normal')

# ── 图例（★ 方块用 Rectangle 画，不用字符——▢ 在 Microsoft YaHei 里缺字形）──────
ax.plot([4.0, 96.0], [15.0, 15.0], color=C_GRID, lw=0.8)
LEG = [(C_PRE, '预制文本（写模板的人所写，用户改不动）', 4.0),
       (C_SLOT, '具名槽位（用户唯一能改的一格）', 45.0),
       (C_WORD, '画论词', 82.0)]
for col, txt, x in LEG:
    ax.add_patch(plt.Rectangle((x, 6.6), 1.5, 1.5, fc=col, ec='none'))
    ax.text(x + 2.3, 7.35, txt, ha='left', va='center', fontsize=8.0, color='#333333')
fig.savefig(OUT, dpi=300, facecolor='white')

# ★ 119：投稿图件要 24 位 RGB，不要透明通道。matplotlib 出的是 32 位 RGBA
#   （实测 alpha 全为 255，通道纯属空占）。这里落成 24 位——投稿件的常规要求。
from PIL import Image
Image.open(OUT).convert('RGB').save(OUT, dpi=(300, 300))
print('已写 %s（%.1f KB，24 位 RGB）' % (OUT, os.path.getsize(OUT) / 1024))

# ── 122·丙：另出矢量件与无损位图（供排版方按格式取用）────────────────────
#   PDF／EPS 直接由同一个 figure 出图（矢量），不是把 PNG 描一遍；
#   TIFF 由上面那件 24 位 PNG 无损转出（LZW，逐像素相同）。
FIGDIR = os.path.join(BASE, '图件')
for ext in ('pdf', 'eps'):
    p = os.path.join(FIGDIR, '图1.' + ext)
    fig.savefig(p, facecolor='white')
    print('已写 %s（%.1f KB，矢量）' % (p, os.path.getsize(p) / 1024))
p = os.path.join(FIGDIR, '图1.tif')
Image.open(OUT).save(p, compression='tiff_lzw', dpi=(300, 300))
print('已写 %s（%.1f KB，LZW 无损，24 位）' % (p, os.path.getsize(p) / 1024))
