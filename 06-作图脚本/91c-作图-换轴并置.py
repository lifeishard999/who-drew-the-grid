# -*- coding: utf-8 -*-
r"""
91c · 生成「图 2　四份词表与基准线的并置」。

★ 图里每一个百分数都当场从代码块 §二 的注[6]（L235）里抓取并断言，不手抄——稿改了图就跟着报错。
★ 两套口径必须在图上分开写清：**基准线是汉字体积口径，四份词表是词次口径**。

★ 122·丙：同一版图另出 PDF／EPS（矢量，直接由 figure 出，**非从 PNG 转**）
与 TIFF（由 24 位 PNG 无损转，LZW）。四件同源同版，排版方点名哪种格式都无须回头改图。
"""
import io
import os
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10'
OUT = os.path.join(BASE, '图件', '图2.png')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
# ★ 122·丙：矢量件的字体按 TrueType 嵌入（42），不落 Type 3——
#   部分排版系统的 RIP 不收 Type 3 字体，中文尤甚。
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

with io.open(os.path.join(BASE, '论文-谁划的格子-投稿版.md'), encoding='utf-8', newline='') as f:
    raw = f.read()
L = raw.replace('\r\n', '\n').split('\n')
# ★ 122·丙：`[6] ` 这个行首前缀在**参考文献**里也有（`[6] 郑…`），故必须先把搜索范围
#   收在「注释」与「参考文献」两节之间——否则定位不唯一，本脚本根本跑不起来（实测 hit=[270,304]）。
i_note = next(i for i, l in enumerate(L) if l.strip() == '注释')
i_ref = next(i for i, l in enumerate(L) if l.strip() == '参考文献')
hit = [i + 1 for i, l in enumerate(L) if i_note < i < i_ref and l.startswith('[6] ')]
assert len(hit) == 1, '★ 注[6] 的定位不是唯一：%s' % hit
N6 = L[hit[0] - 1]
print('注[6] 出处：修订版 L%d' % hit[0])


def grab(pat):
    m = re.search(pat, N6)
    assert m, '★ 稿内注[6] 找不到该数：%s' % pat
    return float(m.group(1))


BASE_PCT = grab(r'占 (97\.10)%')
SIDE_PCT = grab(r'可填侧 56,851 个，占 (2\.90)%')
P_LUN = grab(r'画论词自身在两侧的分配为 (97\.15)%')
P_SE = grab(r'颜色词 35 词 (90\.10)%')
P_GAO = grab(r'二字词 (97\.60)%')
P_CAI = grab(r'材质词 24 词 (98\.32)%')
print('基准线 %.2f（可填侧 %.2f）／画论词 %.2f／颜色 %.2f／高频 %.2f／材质 %.2f'
      % (BASE_PCT, SIDE_PCT, P_LUN, P_SE, P_GAO, P_CAI))

C_BAR, C_HI, C_LINE = '#4a6fa5', '#c0392b', '#555555'
XMIN, XMAX = 88.0, 101.5

fig = plt.figure(figsize=(7.2, 3.05), dpi=300)
ax = fig.add_axes([0.275, 0.235, 0.695, 0.60])

ROWS = [(P_SE, '颜色词（35 词）'),
        (P_LUN, '画论词（37 词）'),
        (P_GAO, '语料自身最高频的\n37 个二字词'),
        (P_CAI, '材质词（24 词）')]

for y, (val, name) in enumerate(ROWS):
    hi = (name == '画论词（37 词）')
    ax.barh(y, val - XMIN, left=XMIN, height=0.52,
            color=C_HI if hi else C_BAR, edgecolor='none', zorder=3)
    ax.text(val + 0.25, y, '%.2f%%' % val, va='center', ha='left',
            fontsize=8.6, color=C_HI if hi else '#333333',
            fontweight='bold' if hi else 'normal')

ax.axvline(BASE_PCT, color=C_LINE, lw=1.3, ls=(0, (4, 2.6)), zorder=4)
ax.text(BASE_PCT, 3.62, '基准线 %.2f%%　汉字体积口径' % BASE_PCT,
        ha='center', va='bottom', fontsize=8.4, color=C_LINE)
ax.text(BASE_PCT, -0.72, '全库汉字 1,957,390 个中，预制侧 1,900,539 个',
        ha='center', va='top', fontsize=7.6, color=C_LINE)

ax.set_yticks(range(len(ROWS)))
ax.set_yticklabels([n for _, n in ROWS], fontsize=8.6)
ax.set_ylim(-1.20, 3.95)
ax.set_xlim(XMIN, XMAX)
ax.set_xticks([88, 90, 92, 94, 96, 98, 100])
ax.tick_params(axis='x', labelsize=8.4)
ax.set_xlabel('预制侧占比（%）　　横轴自 88% 起，非零点', fontsize=8.5, labelpad=6)
for s in ('top', 'right', 'left'):
    ax.spines[s].set_visible(False)
ax.spines['bottom'].set_color('#999999')
ax.grid(axis='x', color='#e2e2e2', lw=0.7, zorder=0)
ax.set_axisbelow(True)

fig.text(0.275, 0.030,
         '※ 基准线（虚线）是汉字体积口径；四份词表（横条）是词次口径。二者不可直接相减。',
         fontsize=7.6, color='#555555', ha='left', va='bottom')

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
    p = os.path.join(FIGDIR, '图2.' + ext)
    fig.savefig(p, facecolor='white')
    print('已写 %s（%.1f KB，矢量）' % (p, os.path.getsize(p) / 1024))
p = os.path.join(FIGDIR, '图2.tif')
Image.open(OUT).save(p, compression='tiff_lzw', dpi=(300, 300))
print('已写 %s（%.1f KB，LZW 无损，24 位）' % (p, os.path.getsize(p) / 1024))
