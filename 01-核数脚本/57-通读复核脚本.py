# -*- coding: utf-8 -*-
r"""
57：第四次通读（2026-10-09）的复核脚本。
只核「稿里写了、但此前没有脚本逐条钉过」的数。不改稿。

待核清单：
  A 摘要/L43「只留一处默认可填的位置」——每条记录到底有几个具名槽位（中位数）
  B L81「两千二百多条……连一个花括号都不出现」——是「无具名槽位」还是「无任何花括号」
  C L161「默认值则有百分之六十八点五三为纯汉字」
  D 表 1 槽名种数 2,395 ／ 仅出现一次 1,698 ／ 70.90% ／ 拉丁字母 9,076 ／ 99.54%
  E 注[7] 2,515 ／ 2,305 ／ 161 三者是否自洽
  F L29 的 61 ／ 12 ／ 16 与 L173 的 36
  G 注[3] 305 条 ／ 5.6% ／ 两种正则 2,313 与 2,250
  H 注[5]／[6] 51 槽位 55 词次 → 剔 16 → 39 词次 35 槽位
"""
import io, json, os, re, sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'F:\数据集\水仙提示词库'
HAN = re.compile(r'[\u4e00-\u9fff]')

def load(fp):
    with io.open(fp, encoding='utf-8') as fh:
        d = json.load(fh)
    if isinstance(d, dict):
        d = d.get('prompts') or d.get('data') or d.get('items') or []
    return d

uni = []
for f in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    uni += load(os.path.join(ROOT, 'shuixian-unified', 'data', f))
print(f'★ 精选版记录数 = {len(uni):,}')
print()

# ---- 槽位提取（三式并集） ----
BLOCK = re.compile(r'\{\s*\\{0,2}"?\s*argument\b([^}]*)\}', re.I)
def attr(a, s):
    m = re.search(r'\b' + a + r'\s*=\s*\\{0,2}"(.*?)\\{0,2}"', s, re.S | re.I)
    return m.group(1) if m else None

slots = []   # (record_index, name, default)
rec_slotn = []
rec_anybrace = []
for i, r in enumerate(uni):
    p = str(r.get('prompt', ''))
    bs = BLOCK.findall(p)
    rec_slotn.append(len(bs))
    rec_anybrace.append(('{' in p) or ('}' in p))
    for b in bs:
        slots.append((i, attr('name', b) or '', attr('default', b) or ''))

print('=' * 60)
print('A ★ 「只留一处」核：每条记录的具名槽位数')
print(f'   槽位总数 = {len(slots):,}')
slotted = [n for n in rec_slotn if n > 0]
print(f'   含槽位记录 = {len(slotted):,}   平均 {sum(slotted)/len(slotted):.2f} 个/条')
import statistics as st
print(f'   ★ 含槽位记录的槽位数中位 = {st.median(slotted)}')
print(f'   ★ 全库记录（含 0）的槽位数中位 = {st.median(rec_slotn)}')
d = Counter(slotted)
print('   槽位数分布（前 12）：', sorted(d.items())[:12])
print(f'   ★ 只有 1 个槽位的记录 = {d[1]:,} / {len(slotted):,} = {d[1]/len(slotted):.2%}')

print()
print('=' * 60)
print('B ★ 「连一个花括号都不出现」核')
n_slot0 = sum(1 for n in rec_slotn if n == 0)
n_brace0 = sum(1 for x in rec_anybrace if not x)
print(f'   无具名槽位的记录 = {n_slot0:,} = {n_slot0/len(uni):.2%}')
print(f'   无任何花括号的记录 = {n_brace0:,} = {n_brace0/len(uni):.2%}')
print(f'   ★ 有花括号但无具名槽位 = {n_slot0 - n_brace0:,}')

print()
print('=' * 60)
print('C ★ 「纯汉字」默认值占比核')
defs = [d for (_, _, d) in slots]
def is_han_only(s):
    return bool(s) and all(('\u4e00' <= c <= '\u9fff') or c.isspace() for c in s)
def is_han_only_strict(s):
    return bool(s) and all('\u4e00' <= c <= '\u9fff' for c in s)
a1 = sum(1 for s in defs if is_han_only(s))
a2 = sum(1 for s in defs if is_han_only_strict(s))
a3 = sum(1 for s in defs if HAN.search(s))
print(f'   槽位总数 = {len(defs):,}')
print(f'   纯汉字（容许空白） = {a1:,} = {a1/len(defs):.2%}')
print(f'   纯汉字（严格）     = {a2:,} = {a2/len(defs):.2%}')
print(f'   含至少一个汉字     = {a3:,} = {a3/len(defs):.2%}   （其补 = 无汉字 {len(defs)-a3:,}）')
print(f'   ★ 稿中 68.53% ↔ 9,118×0.6853 = {9118*0.6853:.0f}')

print()
print('=' * 60)
print('D ★ 槽名种数与拉丁字母占比')
names = [n for (_, n, _) in slots]
c = Counter(names)
print(f'   槽名种数 = {len(c):,}')
once = sum(1 for k, v in c.items() if v == 1)
print(f'   仅出现一次 = {once:,} = {once/len(c):.2%}')
lat = sum(1 for n in names if n and all(ord(ch) < 128 for ch in n))
print(f'   槽名全为拉丁/ASCII = {lat:,} = {lat/len(names):.2%}')
lat2 = sum(1 for n in names if n and not HAN.search(n))
print(f'   槽名不含汉字 = {lat2:,} = {lat2/len(names):.2%}')
print('   前 7 名：', c.most_common(7))

print()
print('=' * 60)
print('E ★ 注[7] 三个数是否自洽')
noh = [s for s in defs if not HAN.search(s)]
print(f'   默认值不含任何汉字的槽位 = {len(noh):,} = {len(noh)/len(defs):.2%}')
ascii_only = [s for s in noh if all(ord(ch) < 128 for ch in s)]
num_punct = [s for s in noh if re.fullmatch(r'[0-9.,:%/+\-\s]*', s)]
print(f'     其中全 ASCII = {len(ascii_only):,}')
print(f'     其中仅数字与 .,:%/+- 及空格 = {len(num_punct):,}')
print(f'   ★ 2,305 + 161 = {2305+161:,}，与 2,515 差 {2515-2305-161}')
print(f'     实测：包含关系？ num_punct ⊆ ascii_only : {set(map(id,num_punct)) <= set(map(id,ascii_only))}')
print(f'     非 ASCII 但无汉字者 = {len(noh)-len(ascii_only):,}')
cn = Counter(n for (_, n, dv) in slots if not HAN.search(dv))
print('     无汉字槽位里前几名：', cn.most_common(4))

print()
print('=' * 60)
print('F ★ 平台参数与槽位同现')
mj = re.compile(r'--(ar|v|stylize|chaos|niji|style|q)\b')
sd = re.compile(r'\([^()]{1,40}:\s*\d+(\.\d+)?\)')
plat = re.compile(r'midjourney|stable\s*diffusion|即梦|dall[\s-]?e|niji|novelai|flux', re.I)
n_mj = sum(1 for r in uni if mj.search(str(r.get('prompt', ''))))
n_sd = sum(1 for r in uni if sd.search(str(r.get('prompt', ''))))
n_pl = sum(1 for r in uni if plat.search(str(r.get('prompt', ''))))
n_both = sum(1 for r in uni if mj.search(str(r.get('prompt', ''))) and BLOCK.search(str(r.get('prompt', ''))))
L = len(uni)
print(f'   含 MJ 参数 = {n_mj:,} = {n_mj/L:.2%}   （稿：61 / 1.12%）')
print(f'   含 SD 权重写法 = {n_sd:,} = {n_sd/L:.2%}   （稿：12 / 0.22%）')
print(f'   直呼平台名 = {n_pl:,}   （稿：16）')
print(f'   ★ 同含 MJ 参数与具名槽位 = {n_both:,}   （稿：36）')

print()
print('=' * 60)
print('G ★ JSON 版式块')
j1 = re.compile(r'\{\s*"type"\s*:')          # 窄式
j2 = re.compile(r'\{\s*\\{0,2}"[A-Za-z_]+\s*\\{0,2}"\s*:')  # 宽式
n_j1 = sum(1 for r in uni if j1.search(str(r.get('prompt', ''))))
n_j2 = sum(1 for r in uni if j2.search(str(r.get('prompt', ''))))
print(f'   窄式（"type":）命中记录 = {n_j1:,}')
print(f'   宽式（"key":）命中记录 = {n_j2:,}')
allj1 = sum(len(j1.findall(str(r.get('prompt', '')))) for r in uni)
allj2 = sum(len(j2.findall(str(r.get('prompt', '')))) for r in uni)
print(f'   ★ 片段数：窄式 {allj1:,} ／ 宽式 {allj2:,}   （稿：2,313 与 2,250）')
print(f'   （稿中 305 条 / 5.6% = {305/L:.2%}）')

print()
print('=' * 60)
print('H ★ 画论词分布（复算「1,931 ／ 1,720 ／ 156 ／ 55」）')
WORDS = ('水墨 工笔 写意 山水 画意 意境 宣纸 留白 皴 泼墨 白描 气韵 丹青 没骨 界画 青绿 卷轴 立轴 手卷 斗方 '
         '题跋 章法 笔法 墨色 淡彩 重彩 院体 文人画 国画 花鸟 人物画 工笔画 水墨画 毛笔 砚 印章 题款').split()
WORDS.sort(key=len, reverse=True)
PAT = re.compile('|'.join(map(re.escape, WORDS)))

def cut(p):
    """三段切分：J = 版式块（{...} 且以 " 开头）；A = 具名槽位默认值；R = 其余"""
    marks = []
    for m in BLOCK.finditer(p):
        marks.append(('A', m.start(), m.end()))
    for m in j2.finditer(p):
        # 找到配对的右花括号（无嵌套时即下一个 }）
        e = p.find('}', m.start())
        if e > 0:
            marks.append(('J', m.start(), e + 1))
    marks.sort(key=lambda x: x[1])
    R, J, A = [], [], []
    cur = 0
    for kind, s, e in marks:
        if s < cur:
            continue
        R.append(p[cur:s])
        (A if kind == 'A' else J).append(p[s:e])
        cur = e
    R.append(p[cur:])
    return ''.join(R), ''.join(J), ''.join(A)

tot = {'R': 0, 'J': 0, 'A': 0}
for r in uni:
    R, J, A = cut(str(r.get('prompt', '')))
    for k, v in (('R', R), ('J', J), ('A', A)):
        tot[k] += len(PAT.findall(v))
s = sum(tot.values())
print(f'   R 其余正文 {tot["R"]:,} = {tot["R"]/s:.2%}   （稿：1,720 / 89.07%）')
print(f'   J 版式块   {tot["J"]:,} = {tot["J"]/s:.2%}   （稿：156 / 8.08%）')
print(f'   A 槽位默认 {tot["A"]:,} = {tot["A"]/s:.2%}   （稿：55 / 2.85%）')
print(f'   合计 {s:,}   （稿：1,931）')
nA = sum(1 for (_, _, dv) in slots if PAT.search(dv))
print(f'   ★ 含画论词的槽位 = {nA:,}   （稿：51 个槽位 / 55 词次）')
