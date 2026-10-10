# -*- coding: utf-8 -*-
r"""
43 号：三段切分（R 散文 / J JSON / A 槽位默认值）在 9,118 并集口径上重算画论词。

★★ 动因（2026-10-09 通读查出）：38 号把分母 **1,931 写死**（那是 19 号 P-only 口径的量），
   而它报出的分子 55 是**并集口径**的量 —— 一分子一分母两套口径 → 注[6] 与表 1 内部对不上：

       1,721 ＋ 156 ＋ 55 ＝ **1,932**  ≠ 注[6] 的 1,931
       1,931 － 16 ＝ **1,915**         ≠ 注[6] 的 1,916（＝ 1,877 ＋ 39，表 1 自洽）

   ★ 本脚本用**同一套机器**跑两遍：
       pass 1（对照）A 段只认直引号式 `{argument name="…"}`  —— 应复现 19 号的 1,721 / 156 / 54
       pass 2（待定）A 段认并集（含转义式、双反斜杠式）        —— 看剔前总数究竟是 1,931 还是 1,932
   ★ 判据：pass 1 若能逐字复现 19 号，则机器可信，pass 2 的数即为答案。
"""
import json, os, re, io, sys, glob, collections

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\43-三段切分在9118口径上-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

# ── 19 号：词表与计数法，逐字照搬 ──────────────────────────
CN_PAINT = ['水墨', '工笔', '写意', '山水', '画意', '意境', '宣纸', '留白', '皴', '泼墨',
            '白描', '气韵', '丹青', '没骨', '界画', '青绿', '卷轴', '立轴', '手卷', '斗方',
            '题跋', '章法', '笔法', '墨色', '淡彩', '重彩', '院体', '文人画', '国画',
            '花鸟', '人物画', '工笔画', '水墨画', '毛笔', '砚', '印章', '题款']
CN_SET = sorted(set(CN_PAINT), key=len, reverse=True)
HAN = re.compile(r'[\u4e00-\u9fff]')

def count_words(s):
    """长词优先、命中后从串里挖掉。（19 号逐字）"""
    s = s or ''
    hit = collections.Counter()
    for w in CN_SET:
        n = s.count(w)
        if n:
            hit[w] += n
            s = s.replace(w, '\x00' * len(w))
    return hit

# ── 两套 A 段识别 ────────────────────────────────────────
SLOT_P = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')   # 19 号逐字
LOOSE  = re.compile(r'\{argument\s+([^}]*?)\s*\}')                              # 38 号并集
JB     = re.compile(r'\{[^{}]*?"[^"]+"\s*:[^{}]*?\}')                           # 19 号逐字

BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'
def strip_q(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre): s = s[len(pre):]; break
    for suf in (BACK2, BACK1, PLAIN, '\u201d'):
        if s.endswith(suf): s = s[:-len(suf)]; break
    return s
def parse_default(blob):
    m = re.search(r'default\s*=\s*', blob)
    if not m: return ''
    rest = blob[m.end():]
    nxt = re.search(r'\s+(?:name|default)\s*=', rest)
    return strip_q(rest[:nxt.start()] if nxt else rest)

def run(mode):
    """mode='P' 只认直引号式；mode='U' 认并集。返回 (tot_words, words_in, a_han, n_slots, n_records)"""
    tot_words = {'A': 0, 'J': 0, 'R': 0}
    words_in  = {'A': collections.Counter(), 'J': collections.Counter(), 'R': collections.Counter()}
    a_han = 0; n_slots = 0; nrec = 0
    for r in rows:
        t = r.get('prompt') or ''
        if mode == 'P':
            defs = [(m.group(2) or '') for m in SLOT_P.finditer(t)]
            rest = SLOT_P.sub('', t)
        else:
            defs = []
            for m in LOOSE.finditer(t):
                defs.append(parse_default(m.group(1)))
            rest = LOOSE.sub('', t)
        n_slots += len(defs)
        a_txt = ' '.join(defs)
        a_han += len(HAN.findall(a_txt))
        j_parts = []
        for m in JB.finditer(rest):
            b = m.group(0)
            if 'argument' in b:        # 19 号逐字：含槽位装置的块不算 JSON
                continue
            j_parts.append(b)
        j_txt = ' '.join(j_parts)
        r_txt = JB.sub(lambda m: '' if 'argument' not in m.group(0) else m.group(0), rest)
        if defs or j_txt.strip() or r_txt.strip():
            nrec += 1
        for k, s in (('A', a_txt), ('J', j_txt), ('R', r_txt)):
            w = count_words(s)
            tot_words[k] += sum(w.values())
            words_in[k].update(w)
    return tot_words, words_in, a_han, n_slots, nrec

RES = {}
for mode, lab in (('P', 'pass 1 对照：A 段只认直引号式（19 号口径）'),
                  ('U', 'pass 2 待定：A 段认并集（9,118 口径）')):
    RES[mode] = run(mode)

o = io.open(OUT, 'w', encoding='utf-8')
def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

W('三段切分 · 同一机器两遍   语料 = %d 条' % len(rows))
W('=' * 78)
for mode in ('P', 'U'):
    tw, wi, a_han, ns, nrec = RES[mode]
    tot = sum(tw.values())
    W('')
    W('【%s】' % ('pass 1 · P-only（应复现 19 号）' if mode == 'P' else 'pass 2 · 并集（9,118）'))
    W('-' * 78)
    W('  槽位 %d    A 段（槽位默认值）汉字 %d' % (ns, a_han))
    W('  %-24s %8s %9s' % ('段', '词次', '占比'))
    for k, lab in (('R', 'R 其余正文（散文）'), ('J', 'J JSON 版式块'), ('A', 'A 槽位默认值')):
        W('  %-24s %8d %8.2f%%' % (lab, tw[k], 100.0 * tw[k] / tot))
    W('  %-24s %8d' % ('★ 剔前合计', tot))
    W('  %-24s %8d   （＝ %.2f%%）' % ('★ 剔后合计（−16）', tot - 16, 100.0 * (tot - 16) / tot))
    W('  %-24s %8d' % ('预制侧 J＋R', tw['J'] + tw['R']))
    W('  逐词 R/J/A：')
    keys = set()
    for k in wi: keys |= set(wi[k])
    for w in sorted(keys, key=lambda x: -(wi['R'][x] + wi['J'][x] + wi['A'][x])):
        W('    %-8s R=%-6d J=%-6d A=%-6d' % (w, wi['R'][w], wi['J'][w], wi['A'][w]))

W('')
W('=' * 78)
twP, _, _, _, _ = RES['P']
twU, wiU, _, _, _ = RES['U']
W('★★ 结论')
W('  19 号原报：  R=1721  J=156  A=54   合计 1931')
W('  本脚本 P ：  R=%d  J=%d  A=%d   合计 %d   ← 与 19 号%s'
  % (twP['R'], twP['J'], twP['A'], sum(twP.values()),
     '逐字相符 ✓' if (twP['R'], twP['J'], twP['A']) == (1721, 156, 54) else '★ 不符，机器须重对 ✗'))
W('  本脚本 U ：  R=%d  J=%d  A=%d   合计 %d   ← 注[6]／表 1 应改用此组'
  % (twU['R'], twU['J'], twU['A'], sum(twU.values())))
W('  注[6] 现在写的： R=1721（89.12%） J=156（8.08%） A=55（2.85%） 合计 1931')
totU = sum(twU.values())
W('  按 U 重算占比： R=%.2f%%  J=%.2f%%  A=%.2f%%'
  % (100.0 * twU['R'] / totU, 100.0 * twU['J'] / totU, 100.0 * twU['A'] / totU))
o.close()
print('\n写出：', OUT)
