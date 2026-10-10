# -*- coding: utf-8 -*-
r"""
85d · 第十三封信 §2.1 的实测：画论词「97.96% 落在预制侧」有没有基准线？

机器逐字照搬 `43-三段切分在9118口径上.py` 的 **pass 2（并集口径）**：
    A = 具名槽位默认值（SLOT 并集：直引号式／转义式／双反斜杠式，统一用 LOOSE 认）
    J = JSON 版式块（先挖掉槽位，再在余文里找 {…"key": value…}，含 argument 的块不算）
    R = 其余正文
★ 通则「复算前先读被检脚本作用在哪段文本上」：本脚本的作用域与 43 号同，未改正则。

本脚本新加三件 43 号没有的事：
  ① 三个段的**汉字数**（43 号只算了 A 段的）
  ② **体积基准线**：(han_R+han_J) / (han_R+han_J+han_A) —— 任何词若按篇幅均匀分布，应得的预制侧占比
  ③ **语料自产基准线**：从语料自身取最高频的 37 个二字词（不与画论词表重叠），
     过同一台机器，看它们的预制侧占比 —— 信所要求的「任意词类」的对照，且不由我挑词
另附 ④：42 个「不含拉丁字母」的槽名全部列出（看 §2.2 那个对比的分母有多大）
"""
import collections
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\85-基准线实测-2026-10-09.txt'

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

CN_PAINT = ['水墨', '工笔', '写意', '山水', '画意', '意境', '宣纸', '留白', '皴', '泼墨',
            '白描', '气韵', '丹青', '没骨', '界画', '青绿', '卷轴', '立轴', '手卷', '斗方',
            '题跋', '章法', '笔法', '墨色', '淡彩', '重彩', '院体', '文人画', '国画',
            '花鸟', '人物画', '工笔画', '水墨画', '毛笔', '砚', '印章', '题款']
HAN = re.compile(r'[\u4e00-\u9fff]')
LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
JB = re.compile(r'\{[^{}]*?"[^"]+"\s*:[^{}]*?\}')
NOTARG = re.compile(r'(?s)^(?!.*argument).*$')

BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'


def strip_q(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre):
            s = s[len(pre):]
            break
    for suf in (BACK2, BACK1, PLAIN, '\u201d'):
        if s.endswith(suf):
            s = s[:-len(suf)]
            break
    return s


def parse_default(blob):
    m = re.search(r'default\s*=\s*', blob)
    if not m:
        return ''
    rest = blob[m.end():]
    nxt = re.search(r'\s+(?:name|default)\s*=', rest)
    return strip_q(rest[:nxt.start()] if nxt else rest)


def split_records():
    """返回 [(R, J, A, names, full)]；names = 该条全部槽名。"""
    out = []
    for r in rows:
        t = r.get('prompt') or ''
        defs, names = [], []
        for m in LOOSE.finditer(t):
            blob = m.group(1)
            names.append(strip_q(re.search(r'name\s*=\s*(.*?)(?=\s+default\s*=|$)', blob).group(1))
                         if re.search(r'name\s*=\s*', blob) else '')
            defs.append(parse_default(blob))
        rest = LOOSE.sub('', t)
        j_parts = [m.group(0) for m in JB.finditer(rest) if 'argument' not in m.group(0)]
        j_txt = ' '.join(j_parts)
        r_txt = JB.sub(lambda m: '' if 'argument' not in m.group(0) else m.group(0), rest)
        out.append((r_txt, j_txt, ' '.join(defs), names, t))
    return out


RECS = split_records()


def count_words(words, s):
    """长词优先、命中后挖掉（19 号口径）。"""
    s = s or ''
    hit = collections.Counter()
    for w in sorted(set(words), key=len, reverse=True):
        n = s.count(w)
        if n:
            hit[w] += n
            s = s.replace(w, '\x00' * len(w))
    return hit


def zone_report(words):
    """某一词表在 R/J/A 三段上的词次。"""
    c = {'R': collections.Counter(), 'J': collections.Counter(), 'A': collections.Counter()}
    for r_txt, j_txt, a_txt, _, _ in RECS:
        for k, s in (('R', r_txt), ('J', j_txt), ('A', a_txt)):
            c[k].update(count_words(words, s))
    return c


# ── ① 三段汉字数 + 画论词 ④
han = {'R': 0, 'J': 0, 'A': 0}
for r_txt, j_txt, a_txt, _, _ in RECS:
    for k, s in (('R', r_txt), ('J', j_txt), ('A', a_txt)):
        han[k] += len(HAN.findall(s))

O = io.open(OUT, 'w', encoding='utf-8', newline='')


def W(*a):
    line = ' '.join(str(x) for x in a)
    O.write(line + '\n')
    print(line)


W('85 · 第十三封信 §2.1「基准线」实测   语料 = %d 条' % len(RECS))
W('=' * 84)
W('')
W('【① 三段汉字数（并集机器）】')
tot_han = sum(han.values())
W('  R 其余正文（散文）  %10d  (%6.2f%%)' % (han['R'], 100.0 * han['R'] / tot_han))
W('  J JSON 版式块       %10d  (%6.2f%%)' % (han['J'], 100.0 * han['J'] / tot_han))
W('  A 槽位默认值        %10d  (%6.2f%%)' % (han['A'], 100.0 * han['A'] / tot_han))
W('  ─────────────────────────────────────────')
W('  预制侧 J＋R          %10d  (%6.2f%%)   ← 体积基准线' % (
    han['J'] + han['R'], 100.0 * (han['J'] + han['R']) / tot_han))
W('  可填侧 A             %10d  (%6.2f%%)' % (han['A'], 100.0 * han['A'] / tot_han))
W('  ★ 预制 : 可填 = %.1f : 1' % ((han['J'] + han['R']) / han['A']))

# ── ④ 画论词
pc = zone_report(CN_PAINT)
tp = {k: sum(pc[k].values()) for k in 'RJA'}
totp = sum(tp.values())
pre_p = tp['R'] + tp['J']
W('')
W('【② 画论词（37 词表）在三段的分布】')
for k, lab in (('R', 'R 散文'), ('J', 'JSON'), ('A', '槽位默认值')):
    W('  %-12s %6d  (%6.2f%%)' % (lab, tp[k], 100.0 * tp[k] / totp))
W('  剔前合计 %d ；预制侧 %d ＝ %.2f%% ；可填侧 %d ＝ %.2f%%'
  % (totp, pre_p, 100.0 * pre_p / totp, tp['A'], 100.0 * tp['A'] / totp))
W('  （注[6]／表 1 的剔后口径：预制 1,876 ＝ 1,720＋156，可填 39，97.96% ／ 2.04%）')
W('  ★ 画论词的 预制:可填 = %.1f : 1' % (pre_p / tp['A'] if tp['A'] else float('inf')))

# ── ③ 语料自产基准线：高频二字词
gram = collections.Counter()
for _, _, _, _, full in RECS:
    for run in re.findall(r'[\u4e00-\u9fff]{2,}', full):
        for i in range(len(run) - 1):
            gram[run[i:i + 2]] += 1
PAINT_CHARS = set(''.join(CN_PAINT))
cand = []
for w, n in gram.most_common(4000):
    if any(w in p or p in w for p in CN_PAINT):
        continue
    cand.append(w)
    if len(cand) == 37:
        break
gc = zone_report(cand)
tg = {k: sum(gc[k].values()) for k in 'RJA'}
totg = sum(tg.values())
pre_g = tg['R'] + tg['J']
W('')
W('【③ 语料自产基准线：语料自身最高频的 37 个二字词（不与画论词表重叠，我不挑词）】')
W('  词表：' + '、'.join(cand))
for k, lab in (('R', 'R 散文'), ('J', 'JSON'), ('A', '槽位默认值')):
    W('  %-12s %6d  (%6.2f%%)' % (lab, tg[k], 100.0 * tg[k] / totg))
W('  合计 %d ；预制侧 %d ＝ %.2f%% ；可填侧 %d ＝ %.2f%%'
  % (totg, pre_g, 100.0 * pre_g / totg, tg['A'], 100.0 * tg['A'] / totg))
W('  ★ 该基准组的 预制:可填 = %.1f : 1' % (pre_g / tg['A'] if tg['A'] else float('inf')))

# ── ⑤ 手挑对照词表（信举的「颜色词」等）
LISTS = {
    '颜色词': ['红色', '蓝色', '绿色', '黄色', '紫色', '橙色', '黑色', '白色', '灰色', '粉色',
               '金色', '银色', '棕色', '褐色', '深蓝', '浅蓝', '天蓝', '湖蓝', '宝蓝', '墨绿',
               '深绿', '浅绿', '翠绿', '玫红', '酒红', '粉红', '桃红', '紫红', '朱红', '米白',
               '暖色', '冷色', '暖色调', '冷色调', '渐变色'],
    '构图词': ['构图', '对称', '三分法', '对角线', '水平线', '垂直线', '俯视', '仰视', '平视',
               '特写', '远景', '中景', '近景', '全景', '视角', '透视', '焦点', '前景', '背景',
               '居中', '竖版', '横版', '方形', '圆形', '横构图', '竖构图'],
    '材质词': ['油画', '水彩', '丙烯', '版画', '素描', '炭笔', '颜料', '画布', '笔刷', '材质',
               '质感', '光泽', '哑光', '高光', '反光', '透明', '半透明', '陶瓷', '玻璃', '金属',
               '皮革', '织物', '木质', '纸质'],
}
W('')
W('【④ 信所举的对照词表（手挑，仅供同尺度比照）】')
W('  %-10s %8s %8s %8s %10s' % ('词表', '预制侧', '可填侧', '合计', '预制占比'))
for name, wl in LISTS.items():
    c = zone_report(wl)
    t = {k: sum(c[k].values()) for k in 'RJA'}
    tt = sum(t.values())
    pr = t['R'] + t['J']
    W('  %-10s %8d %8d %8d %9.2f%%' % (name, pr, t['A'], tt, 100.0 * pr / tt if tt else 0))

# ── ⑥ 槽名的语言：列出全部「不含拉丁字母」的槽名
allnames = []
for _, _, _, names, _ in RECS:
    allnames.extend(n for n in names if n)
LAT = re.compile(r'[A-Za-z]')
nocn = [n for n in allnames if not LAT.search(n)]
has_han = [n for n in nocn if HAN.search(n)]
W('')
W('【⑤ §2.2 那个对比的分母】')
W('  槽位总数 %d ；槽名含拉丁字母者 %d ；不含拉丁字母者 %d ；其中含汉字者 %d'
  % (len(allnames), len(allnames) - len(nocn), len(nocn), len(has_han)))
W('  全部「不含拉丁字母」的槽名（%d 个，按出现次数）：' % len(nocn))
for n, k in collections.Counter(nocn).most_common():
    W('     %-24s ×%d' % (n, k))
O.close()
print('\n写出：', OUT)
