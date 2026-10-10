# -*- coding: utf-8 -*-
r"""
92a · 取样：同一个具名槽位的**三种表面写法**，各取一个最短的真实原串。

为什么量这个：用户问「还有没有其他的图要加」。候选之一是
「同一个槽位，三种外壳」——正文 L169 的论证所依赖的证据，但目前只有
文字概括（"一种带直引号，一种……反斜杠加引号，还有一种嵌了两层"），
读者无法从文字重构出串长什么样。**能不能作图，取决于能不能取到干净的真例。**

口径：沿用 `36` 号的扫描口径（先定位 `{argument`、再按 `name=` 后接什么字符分类），
不做任何 strip，报**原始片段**的 repr 与肉眼形。
"""
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\92a-三写法取样-2026-10-09.txt'

LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

buckets = {}          # form -> list of (len, id, raw)
count = {}
recs = {}
for r in rows:
    t = r.get('prompt') or ''
    pid = r.get('id')
    for m in LOOSE.finditer(t):
        blob = m.group(1)
        k = blob.find('name=')
        if k < 0:
            form = '其他（无 name）'
        else:
            rest = blob[k + 5:]
            if rest.startswith(BACK2):
                form = 'E2 双反斜杠式'
            elif rest.startswith(BACK1):
                form = 'E1 转义式'
            elif rest.startswith(PLAIN):
                form = 'P  直引号式'
            else:
                form = '其他（引号形态不符）'
        raw = m.group(0)
        count[form] = count.get(form, 0) + 1
        recs.setdefault(form, set()).add(pid)
        buckets.setdefault(form, []).append((len(raw), pid, raw))

o = io.open(OUT, 'w', encoding='utf-8', newline='')   # ★ LF：66b 会核这一份


def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n')
    print(line)


W('同一具名槽位 · 三种表面写法 · 各取最短真例')
W('语料 = %d 条   （口径沿用脚本 `36` 的扫描法，未做任何 strip）' % len(rows))
W('')
W('%-18s %8s %8s' % ('写法', '槽位数', '记录数'))
for form in sorted(count, key=lambda f: -count[f]):
    W('%-18s %8d %8d' % (form, count[form], len(recs[form])))
W('%18s %8d %8d' % ('★ 三重并集', sum(count.values()), len(set().union(*recs.values()))))
W('')
for form in sorted(count, key=lambda f: -count[f]):
    if not count[form]:
        continue
    lst = sorted(buckets[form])
    W('=' * 78)
    W('【%s】共 %d 个；最长 %d 字符 / 最短 %d 字符'
      % (form, len(lst), lst[-1][0], lst[0][0]))
    W('  ── 最短的三个真例（原样）')
    for ln, pid, raw in lst[:3]:
        W('    len=%d  id=%s' % (ln, pid))
        W('      %s' % raw)
    W('  ── 中间长度的两个（看是否只是值更长）')
    mid = lst[len(lst) // 2:len(lst) // 2 + 2]
    for ln, pid, raw in mid:
        W('    len=%d  id=%s' % (ln, pid))
        W('      %s' % raw[:160])
    W('  ── repr（看清反斜杠层数）')
    ln, pid, raw = lst[0]
    W('    %r' % raw)
    W('')

o.close()
print()
print('写出：', OUT)
