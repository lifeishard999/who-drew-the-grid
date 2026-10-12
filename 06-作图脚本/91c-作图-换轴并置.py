# -*- coding: utf-8 -*-
r"""
91c · 生成「图 2　四份词表与基准线的并置」。

★ 图里每一个百分数都当场抓取并断言，不手抄——稿改了图就跟着报错。
★ 两套口径必须在图上分开写清：**基准线是汉字体积口径，四份词表是词次口径**。

★ 171：抓取源分两处，因为 `169` 动了注[6]：
  · 基准线 97.10／可填侧 2.90／画论词 97.15／高频二字词 97.60 —— 四数仍住**注[6]**，照旧从那儿抓；
  · 颜色词 90.10／材质词 98.32 —— `169` 已把这两数**从注[6] 删去**（注[6] 现只写
    「材质词 24 词与颜色词 35 词分列高低两端」），两数**仍活在图注 L141**（表图区）
    「四份词表介于 90.10% 与 98.32% 之间」⇒ 改从**全稿**抓（仍在稿面上，否则断言报错）。
  · 但图注只给**两端**、不给**归属**（谁高谁低）⇒ 归属当场读复现包里的实测输出
    `_数据与脚本包\02-中间结果\85-基准线实测-2026-10-09.txt`（L31 颜色词 90.10／L33 材质词 98.32）
    二次对表：**稿面那条管子与实测那条管子须一致**，不一致就报错。

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


def grab_any(pat, why):
    """从**全稿**抓一个数（`169` 之后注[6] 里已没有的那几个走这条）。"""
    hits = re.findall(pat, raw)
    assert len(hits) == 1, '★ 全稿里「%s」不是恰一处（%d）：%s' % (pat, len(hits), why)
    return float(hits[0])


#   注[6] 里仍在的四数
BASE_PCT = grab(r'占 (97\.10)%')
SIDE_PCT = grab(r'可填侧 56,851 个，占 (2\.90)%')
P_LUN = grab(r'画论词自身在两侧的分配为 (97\.15)%')
P_GAO = grab(r'二字词 (97\.60)%')
#   注[6] 里已无、图注 L141 仍有的两端（只给两端，不给归属）
SE_MD = grab_any(r'介于 (90\.10)%', '图注①的低端')
CAI_MD = grab_any(r'与 (98\.32)% 之间', '图注①的高端')

#   ★ 171：归属走**另一条管子**——复现包里的实测输出（`85`）。
F85 = os.path.join(BASE, '_数据与脚本包', '02-中间结果', '85-基准线实测-2026-10-09.txt')
T85 = io.open(F85, encoding='utf-8', newline='').read()


def from85(name):
    hits = re.findall(r'^\s*%s\s+\d+\s+\d+\s+\d+\s+([\d.]+)%%' % name, T85, re.M)
    assert len(hits) == 1, '★ 85 实测输出里「%s」那一行不是恰一处（%d）' % (name, len(hits))
    return float(hits[0])


P_SE, P_CAI = from85('颜色词'), from85('材质词')
assert (SE_MD, CAI_MD) == (P_SE, P_CAI), \
    '★ 两条管子不一致——稿面 (%.2f, %.2f) ／ 85 实测 (%.2f, %.2f)' % (SE_MD, CAI_MD, P_SE, P_CAI)
print('基准线 %.2f（可填侧 %.2f）／画论词 %.2f／颜色 %.2f／高频 %.2f／材质 %.2f'
      % (BASE_PCT, SIDE_PCT, P_LUN, P_SE, P_GAO, P_CAI))
print('  ★ 颜色／材质两数：图注 L141 给 (%.2f, %.2f)，85 实测给 (%.2f, %.2f) ⇒ 一致'
      % (SE_MD, CAI_MD, P_SE, P_CAI))

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

# ── ★ 157 题／171 落：截断标记「//」────────────────────────────────────
#   横轴自 88% 起，非零点。此前只在轴标签里写明，图上无记号。这里补一对短斜线，
#   压在**底脊**上、原点右侧一点（避开「88」这个刻度标注），读作「此处省略」；
#   轴标签那半句「横轴自 88% 起，非零点」保留，两处互证。
SPINE_C = '#999999'
Y0 = ax.get_ylim()[0]                      # 底脊所在的 y（数据坐标）
BRK_X, BRK_H, BRK_GAP = 88.62, 0.13, 0.30  # 位置／斜线半宽／两条间距（数据坐标）
ax.spines['bottom'].set_zorder(1.5)        # 压到抹平线之下
ax.plot([BRK_X + 0.02, BRK_X + BRK_GAP - 0.02], [Y0, Y0],
        color='white', lw=2.6, clip_on=False, zorder=6)     # 先抹平两线之间的脊
for k in (0.0, BRK_GAP):
    ax.plot([BRK_X + k - BRK_H, BRK_X + k + BRK_H], [Y0 - 0.115, Y0 + 0.115],
            color=SPINE_C, lw=1.1, clip_on=False, zorder=7, solid_capstyle='butt')

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
