# -*- coding: utf-8 -*-
r"""
52 号：核查「策展人」这一称谓在语料侧的依据，并核 注[6]「策展人自撰的散文」/ L27「写作者身份明确」
是否有据。

背景：用户问「文章里"策展人"是什么？」。先在稿件里定位，再回站点自述与数据字段找依据。

要核三件：
  ① 站点自述（about.html / submit.html / README）用的是自称还是"作者"？
  ② 现役 5,452 精选版（shuixian-unified）的记录里有没有著者/来源字段？
  ③ 旧版 17,427（old/shuixian-deploy）有 author 字段——它的取值分布如何？
     （若旧版作者多元，则"这批散文出自一人之手"就不是站点层面的通例）
"""
import io, json, os, sys, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
ROOT = r'F:\数据集\水仙提示词库'

def p(*a):
    print(*a)

# ── ① 站点自述用词 ───────────────────────────────
p('══ ① 站点自述里与"作者/来源"有关的句子')
for f in ('about.html', 'submit.html'):
    fp = os.path.join(ROOT, 'shuixian-unified', f)
    if not os.path.exists(fp):
        p(f'  （缺 {f}）'); continue
    t = io.open(fp, encoding='utf-8').read()
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', '\n', t)
    for line in t.split('\n'):
        s = line.strip()
        if not s:
            continue
        if re.search(r'作者|版权|原创|投稿|收集|整理|筛选|收录|散落|花园|我们', s):
            p(f'  [{f}] {s}')

# 关键词计数
p()
p('  ── 关键词在站点页面里的出现次数')
KW = ['策展', '作者', '版权', '原创', '投稿', '收集', '整理', '筛选', '收录', '花园', '散落']
alltext = ''
for f in ('about.html', 'submit.html', 'index.html'):
    fp = os.path.join(ROOT, 'shuixian-unified', f)
    if os.path.exists(fp):
        alltext += io.open(fp, encoding='utf-8').read()
for k in KW:
    p(f'     {k:<6} ×{alltext.count(k)}')

# ── ② 现役精选版字段 ─────────────────────────────
p()
p('══ ② 现役精选版 shuixian-unified/data/prompts.part*.json 的字段')
ddir = os.path.join(ROOT, 'shuixian-unified', 'data')
files = sorted(f for f in os.listdir(ddir) if f.startswith('prompts.part') and f.endswith('.json'))
p('  文件：', files)
recs = []
for f in files:
    fp = os.path.join(ddir, f)
    with io.open(fp, encoding='utf-8') as fh:
        d = json.load(fh)
    if isinstance(d, dict):
        p(f'  [{f}] 顶层是 dict，键：{list(d.keys())[:12]}')
        d = d.get('prompts') or d.get('data') or d.get('items') or []
    p(f'  [{f}] 记录数 {len(d)}')
    recs += d
p(f'  ★ 合计 {len(recs)} 条')
keys = Counter()
for r in recs:
    keys.update(r.keys())
p('  ★ 字段出现次数：')
for k, n in keys.most_common():
    p(f'     {k:<16} {n}')
p('  ★ 样张（第 1 条）：')
if recs:
    for k, v in recs[0].items():
        s = str(v)
        p(f'     {k:<16} {s[:80]!r}')

# ── ③ 旧版 author 字段分布 ───────────────────────
p()
p('══ ③ 旧版 17,427（old/shuixian-deploy）的 author 字段分布')
odir = os.path.join(ROOT, 'old', 'shuixian-deploy')
cands = []
for dp, dn, fn in os.walk(odir):
    for f in fn:
        if f.endswith('.json'):
            cands.append(os.path.join(dp, f))
p('  候选 json：', [os.path.relpath(c, ROOT) for c in cands][:20])
old = []
for c in cands:
    try:
        with io.open(c, encoding='utf-8') as fh:
            d = json.load(fh)
    except Exception as e:
        p(f'  （{os.path.basename(c)} 读不了：{e}）'); continue
    if isinstance(d, dict):
        d = d.get('prompts') or d.get('data') or d.get('items') or []
    if d and isinstance(d[0], dict) and 'author' in d[0]:
        p(f'  ★ {os.path.relpath(c, ROOT)}：{len(d)} 条，含 author 字段')
        old += d
if old:
    au = Counter(str(r.get('author', '')) for r in old)
    p(f'  ★ 旧版合计 {len(old)} 条，author 取值 {len(au)} 种；前 20：')
    for a, n in au.most_common(20):
        p(f'     {a[:40]!r:<44} {n}')
else:
    p('  （未找到含 author 字段的旧版 json）')

# ── ④ 现役精选版与旧版的重合（可选：看精选版是否取自旧版）──
p()
p('══ ④ 现役精选版是否从中挑出：按 prompt 前 30 字比对')
if recs and old:
    oset = {str(r.get('prompt', ''))[:30] for r in old}
    hit = sum(1 for r in recs if str(r.get('prompt', ''))[:30] in oset)
    p(f'  ★ 精选 {len(recs)} 条中，{hit} 条能在旧版里找到同前 30 字的条目（{hit/len(recs):.1%}）')
    if hit:
        ex = [r for r in recs if str(r.get('prompt', ''))[:30] in oset][:5]
        oidx = {}
        for r in old:
            oidx.setdefault(str(r.get('prompt', ''))[:30], r)
        for r in ex:
            o = oidx[str(r.get('prompt', ''))[:30]]
            p(f"     精选「{r.get('title','')[:20]}」 ← 旧版 author={o.get('author','')!r}")
