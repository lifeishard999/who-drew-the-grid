# -*- coding: utf-8 -*-
r"""
88a · 「丁」所需的实测：命名**语言**与命名**权**之间，有没有一条可量的中介？

第十四封信 §2.3 说：L165「预先截除」那一跳（命名用另一种语言 ⇒ 命名权不在用户手里）缺支撑。
要补这一跳，得在两者之间找一条**可量的中介**。候选三条：

  ① 默认值与槽名**分别由谁写下** —— 注意：这是**规范层**语料，看不到填的那一步；
     能看到的只有「谁把这一格写进模板」，看不到「谁往格里填」。故这条只能在作者面上做。
  ② **槽名的复用**：同一个槽名被多少位**不同作者**使用。
     - 若绝大多数名字是各人自造（一人一名），则命名权确在写者手上 → 该跳不成立，稿子该退；
     - 若被大量启动的少数名字是**跨作者共用**的，则那部分名字不属于任何一个人，
       谁也无权单独改动 → 该跳可以补，但要改写成一个**弱**断言。
  ③ 用户能否新增槽名 —— 注[4] 已测「站点无任何输入控件、唯一动作是原样复制」，属站点层，本轮不重复。

方法：把现役精选版逐条回接旧版的 author（键＝prompt 全串，辅以前 30 字，与 `52b` 同）。
      槽位抽法与 `36` 号**三重并集**口径逐字相同。

★ 口径纪律：槽名与作者都只在**回接得上**的那批记录里量；回接率随报告一并报出，
  不得把「回接得上的作者数」说成「全库的作者数」。

★★★ 首跑即发现本脚本自身的分母缺陷（保留此版，不移除；订正见 `88b`）：
  【二】那张分档表的**分子全部取自"回接得上"的 3,437 条，分母却写成了全库**——
    · `tot_names` 是 `len(name_authors[n]) >= 1`，实际只数到 **2,378 种**（不是 2,395，
      有 17 种槽名只出现在回接不上的记录里），标题却印着「2,395 种」；
    · 实例占比用 `len(nm)`＝**9,118**（全库）作分母，而分子只有 **9,008**（回接得上的那批）。
  → **分档合计 2,378 ≠ 2,395、9,008 ≠ 9,118，正是"分子分母各取一套"**。
  故【二】表里的 76.24% 与五个实例占比**一律不得引用**，须用 `88b` 的重算值。
"""
import io, json, os, re, sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'F:\数据集\水仙提示词库'

# ── 与 36 号逐字相同的抽取口径 ──────────────────────────────
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
        val = rest[:nxt.start()] if nxt else rest
        out[key] = strip_quotes(val)
    return out['name'], out['default']

def slots_of(text):
    """返回 [(name, default), …]，只取有 name 属性的槽位（与 36 号同）"""
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

print('精选版 %d 条 ／ 旧版 %d 条' % (len(uni), len(old)))
print()

by_full, by_head = {}, {}
for r in old:
    pr = str(r.get('prompt', ''))
    by_full.setdefault(pr, r)
    by_head.setdefault(pr[:30], r)

# ── 全库先复算一遍语言归属（与 36 号对账）──────────────────
CJK, LAT = re.compile(r'[\u4e00-\u9fff]'), re.compile(r'[A-Za-z]')
allslots = []
for r in uni:
    allslots += slots_of(str(r.get('prompt', '')))
nm = [s[0] for s in allslots]
cnt_all = Counter(nm)
lat = sum(1 for n in nm if LAT.search(n) and not CJK.search(n))
print('【对账 · 36 号口径】槽位 %d 个 ／ 槽名 %d 种 ／ 只一次 %d（%.2f%%）'
      % (len(nm), len(cnt_all), sum(1 for v in cnt_all.values() if v == 1),
         100.0 * sum(1 for v in cnt_all.values() if v == 1) / len(cnt_all)))
print('   槽名含拉丁且不含汉字 %d（%.2f%%）' % (lat, 100.0 * lat / len(nm)))
print('   前 10 种占比 %.2f%% ／ 首位 %r %d（%.2f%%）'
      % (100.0 * sum(v for _, v in cnt_all.most_common(10)) / len(nm),
         cnt_all.most_common(1)[0][0], cnt_all.most_common(1)[0][1],
         100.0 * cnt_all.most_common(1)[0][1] / len(nm)))
print()

# ── 回接作者 ────────────────────────────────────────────────
matched, miss = 0, 0
name_authors = defaultdict(set)      # 槽名 → {作者}
inst_by_name = Counter()             # 槽名 → 实例数（只在回接得上的记录里）
per_author = defaultdict(list)       # 作者 → [该记录用到的槽名列表]
for r in uni:
    pr = str(r.get('prompt', ''))
    o = by_full.get(pr) or by_head.get(pr[:30])
    if o is None:
        miss += 1; continue
    matched += 1
    a = str(o.get('author', '')) or '（空）'
    ss = slots_of(pr)
    per_author[a].append([n for n, _ in ss])
    for n, _ in ss:
        name_authors[n].add(a)
        inst_by_name[n] += 1

print('【回接】%d / %d = %.1f%%（未匹配 %d）  作者取值 %d 个'
      % (matched, len(uni), 100.0 * matched / len(uni), miss, len(per_author)))
print()

# ── 一、前 15 名：次数 vs 作者数 ───────────────────────────
print('【一】被启动最多的 15 个槽名 —— 出现次数 vs 出自多少位不同作者')
print('   %-22s %8s %9s %10s' % ('槽名', '出现次数', '作者数', '次数/作者数'))
top = inst_by_name.most_common(15)
for n, c in top:
    k = len(name_authors[n])
    print('   %-22s %8d %9d %10.2f' % (n[:22], c, k, c / k))
print()

# ── 二、槽名按"作者数"分档 ─────────────────────────────────
print('【二】2,395 种槽名按「被多少位不同作者用过」分档')
buckets = [(1, 1), (2, 4), (5, 9), (10, 49), (50, 10 ** 9)]
lbl = ['1 位（个人自造）', '2–4 位', '5–9 位', '10–49 位', '≥50 位（跨作者公共词）']
tot_names = sum(len(name_authors[n]) >= 1 for n in cnt_all)
for (lo, hi), L in zip(buckets, lbl):
    ns = [n for n in cnt_all if lo <= len(name_authors.get(n, ())) <= hi]
    ins = sum(inst_by_name.get(n, 0) for n in ns)
    print('   %-20s 名字 %5d 种 %6.2f%%   实例 %5d 个 %6.2f%%'
          % (L, len(ns), 100.0 * len(ns) / tot_names, ins, 100.0 * ins / len(nm)))
print()

# ── 三、作者内复用：一人写多条时，他自己换不换名字 ─────────
print('【三】同一位作者写多条时，槽名的自用复用率（只在写 ≥5 条、且槽位实例 ≥10 的作者上算）')
ratios = []
for a, recs in per_author.items():
    flat = [n for r in recs for n in r]
    if len(recs) >= 5 and len(flat) >= 10:
        ratios.append((a, len(recs), len(flat), len(set(flat))))
ratios.sort(key=lambda x: -x[2])
if ratios:
    import statistics
    k_over_n = [u / f for _, _, f, u in ratios]
    print('   入算作者 %d 位；槽名种数/槽位实例数：中位 %.3f  均 %.3f  最低 %.3f'
          % (len(ratios), statistics.median(k_over_n), sum(k_over_n) / len(k_over_n), min(k_over_n)))
    print('   写得多、名字也换得勤的前 8 位（条数 / 实例 / 不同名 / 比值）：')
    for a, rc, f, u in ratios[:8]:
        print('     %-24s %4d 条 %5d 实例 %5d 名 %.3f' % (str(a)[:24], rc, f, u, u / f))
else:
    print('   （无满足条件者）')
print()

# ── 四、关键几句：可以写进稿的判断标准 ─────────────────────
print('【四】可落笔的判据')
hc = 'hair color'
print('   ① 首位 %r：%d 次实例，出自 %d 位不同作者 → %s'
      % (hc, inst_by_name.get(hc, 0), len(name_authors.get(hc, ())),
         '跨作者共享' if len(name_authors.get(hc, ())) > 20 else '作者数不足，不宜称共享'))
ten = [n for n, _ in inst_by_name.most_common(10)]
print('   ② 前十名的作者数中位 %d，最少 %d，最多 %d'
      % (sorted(len(name_authors[n]) for n in ten)[5],
         min(len(name_authors[n]) for n in ten), max(len(name_authors[n]) for n in ten)))
tot_auth = len(per_author)
print('   ③ 回接得上的作者共 %d 位；前十名里有 %d 个名字被 ≥ %d%% 的作者用过'
      % (tot_auth, sum(1 for n in ten if len(name_authors[n]) >= 0.1 * tot_auth),
         int(10)))
print('   ★ 请判读：这些数是支持「命名权在写者手上」（分档里 1 位占比高），')
print('     还是支持「被大量启动的少数名字无人专有」（≥50 位那档的实例占比高）——')
print('     两者可同时成立，稿子应当写成哪一层，看的是**实例占比**而非名字种数占比。')
