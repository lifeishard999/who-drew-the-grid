# -*- coding: utf-8 -*-
r"""
88b · 88a 的分母订正版。

88a 的【二】把「回接得上那批」的分子配了「全库」的分母（2,378 vs 2,395；9,008 vs 9,118）。
本脚本把两个尺度**分列**，每一列自带分母，且**层级合计必须等于该尺度下的总数**
（否则当场判红——这是本轮给这条通则加的一个守卫）。

两个尺度：
  · 全库 5,452 条        —— 只有槽位，没有作者
  · 回接得上 3,437 条    —— 有作者，可以问"这个名字被几位不同作者用过"

★ 报数纪律：凡引出【作者数】的数，必须连"回接得上"这个限定一起报。
"""
import io, json, os, re, sys, statistics
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'F:\数据集\水仙提示词库'

LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'


def strip_quotes(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre):
            s = s[len(pre):]; break
    for suf in (BACK2, BACK1, PLAIN, '”'):
        if s.endswith(suf):
            s = s[:-len(suf)]; break
    return s


def parse(blob):
    out = {}
    for key in ('name', 'default'):
        m = re.search(key + r'\s*=\s*', blob)
        if not m:
            out[key] = None; continue
        rest = blob[m.end():]
        nxt = re.search(r'\s+(?:name|default)\s*=', rest)
        out[key] = strip_quotes(rest[:nxt.start()] if nxt else rest)
    return out['name'], out['default']


def slots_of(text):
    out = []
    for m in LOOSE.finditer(text or ''):
        blob = m.group(1)
        if blob.find('name=') < 0:
            continue
        n, d = parse(blob)
        if n:
            out.append((n, d))
    return out


def load(fp):
    with io.open(fp, encoding='utf-8') as fh:
        d = json.load(fh)
    if isinstance(d, dict):
        d = d.get('prompts') or d.get('data') or d.get('items') or []
    return d


uni = []
for f in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    uni += load(os.path.join(ROOT, 'shuixian-unified', 'data', f))
old = []
for f in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    old += load(os.path.join(ROOT, 'old', 'shuixian-deploy', 'data', f))

by_full, by_head = {}, {}
for r in old:
    pr = str(r.get('prompt', ''))
    by_full.setdefault(pr, r)
    by_head.setdefault(pr[:30], r)

# ── 尺度 A：全库 ───────────────────────────────────────────
A_names, A_inst = [], Counter()
# ── 尺度 B：回接得上 ───────────────────────────────────────
B_names, B_inst, B_authors = [], Counter(), defaultdict(set)
B_per_author = defaultdict(list)
n_match = 0

for r in uni:
    pr = str(r.get('prompt', ''))
    ss = slots_of(pr)
    A_names += [n for n, _ in ss]
    for n, _ in ss:
        A_inst[n] += 1
    o = by_full.get(pr) or by_head.get(pr[:30])
    if o is None:
        continue
    n_match += 1
    a = str(o.get('author', '')) or '（空）'
    B_per_author[a].append([n for n, _ in ss])
    for n, _ in ss:
        B_names.append(n)
        B_inst[n] += 1
        B_authors[n].add(a)

print('══ 两个尺度各自的总数（先验层级合计）')
print('  A 全库      记录 %d   槽位实例 %d   槽名 %d 种' % (len(uni), len(A_names), len(A_inst)))
print('  B 回接得上  记录 %d   槽位实例 %d   槽名 %d 种   作者 %d 位'
      % (n_match, len(B_names), len(B_inst), len(B_per_author)))
print('  回接率 %.1f%%   未匹配 %d 条' % (100.0 * n_match / len(uni), len(uni) - n_match))
print()

# ── 尺度 B 的分档：分子分母同源，且合计须等于 B 的总数 ─────
BUCKETS = [(1, 1, '1 位（个人自造）'), (2, 4, '2–4 位'), (5, 9, '5–9 位'),
           (10, 49, '10–49 位'), (50, 10 ** 9, '≥50 位（跨作者共用）')]
print('══ 尺度 B：【%d 种槽名】按被多少位不同作者用过分档（分母自洽）' % len(B_inst))
ns_tot = ins_tot = 0
for lo, hi, L in BUCKETS:
    ns = [n for n in B_inst if lo <= len(B_authors.get(n, ())) <= hi]
    ins = sum(B_inst[n] for n in ns)
    ns_tot += len(ns); ins_tot += ins
    print('   %-22s 名字 %5d 种 %6.2f%%   实例 %5d 个 %6.2f%%'
          % (L, len(ns), 100.0 * len(ns) / len(B_inst), ins, 100.0 * ins / len(B_names)))
ok1 = (ns_tot == len(B_inst)) and (ins_tot == len(B_names))
print('   ── 合计 %d 种 / %d 实例  …… %s' % (ns_tot, ins_tot,
      '✓ 与总数相符' if ok1 else '★★★ 与总数不符，本表作废'))
print()

# ── 尺度 A 的同名对照（只有槽位，没有作者）────────────────
once_A = sum(1 for v in A_inst.values() if v == 1)
print('══ 尺度 A：全库槽名 %d 种，只出现 1 次的 %d 种（%.2f%%）'
      % (len(A_inst), once_A, 100.0 * once_A / len(A_inst)))
print('   前 10 种占 %.2f%%   首位 %r %d 次（%.2f%%）'
      % (100.0 * sum(v for _, v in A_inst.most_common(10)) / len(A_names),
         A_inst.most_common(1)[0][0], A_inst.most_common(1)[0][1],
         100.0 * A_inst.most_common(1)[0][1] / len(A_names)))
print()

# ── 前 15 名：两个尺度并列，禁止混引 ───────────────────────
print('══ 前 15 名（A 列＝全库次数；B 列＝回接得上的次数与作者数）')
print('   %-20s %8s %8s %8s' % ('槽名', 'A 全库', 'B 次数', 'B 作者数'))
for n, cA in A_inst.most_common(15):
    print('   %-20s %8d %8d %8d' % (n[:20], cA, B_inst.get(n, 0), len(B_authors.get(n, ()))))
print()

# ── 作者内复用 ─────────────────────────────────────────────
ratios = []
for a, recs in B_per_author.items():
    flat = [n for r in recs for n in r]
    if len(recs) >= 5 and len(flat) >= 10:
        ratios.append((a, len(recs), len(flat), len(set(flat))))
k_over_n = [u / f for _, _, f, u in ratios]
print('══ 作者内复用（写 ≥5 条且槽位实例 ≥10 的作者 %d 位）' % len(ratios))
print('   不同槽名数 ÷ 槽位实例数：中位 %.3f  均 %.3f  最低 %.3f（越低＝越爱复用少数名）'
      % (statistics.median(k_over_n), sum(k_over_n) / len(k_over_n), min(k_over_n)))
print()

# ── 可落笔的判据（全部限定在尺度 B）────────────────────────
print('══ 可落笔的判据（★ 全部是尺度 B，即"回接得上的 %d 条 / %d 位作者"）'
      % (n_match, len(B_per_author)))
n1 = sum(1 for n in B_inst if len(B_authors[n]) == 1)
i1 = sum(B_inst[n] for n in B_inst if len(B_authors[n]) == 1)
hi = [n for n in B_inst if len(B_authors[n]) >= 50]
ihi = sum(B_inst[n] for n in hi)
print('   ① 只被 1 位作者用过的槽名 %d / %d = %.2f%%；其实例 %d / %d = %.2f%%'
      % (n1, len(B_inst), 100.0 * n1 / len(B_inst), i1, len(B_names), 100.0 * i1 / len(B_names)))
print('   ② 被 ≥50 位作者用过的槽名 %d 种，却占实例 %d / %d = %.2f%%'
      % (len(hi), ihi, len(B_names), 100.0 * ihi / len(B_names)))
top1 = B_inst.most_common(1)[0]
print('   ③ 首位 %r：回接得上的记录里 %d 次，出自 %d 位不同作者（作者面的 %.1f%%）'
      % (top1[0], top1[1], len(B_authors[top1[0]]),
         100.0 * len(B_authors[top1[0]]) / len(B_per_author)))
print()
print('   ★ 两条同时成立：**名目层**个人的名字多（①），**实例层**共用名多（②）。')
print('     故「命名权在不在用户手里」不能一句话答；能答的是：')
print('     能自己起名的格子一直在（①那七成六），被反复填的那几格无主（②那三成四）。')
sys.exit(0 if ok1 else 1)
