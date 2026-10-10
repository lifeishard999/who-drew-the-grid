# -*- coding: utf-8 -*-
r"""
89d · 壬：重算「不含拉丁字母的槽名」全表（供注[14]入稿用）。

口径**逐字沿用 36 号**（三重并集：先定位 `{argument`，再按 `name=` 后接什么字符分类）。
判据：槽位名中**不含任何拉丁字母 A–Z / a–z** ⇒ 拾出；再分「含汉字／含假名」。

★ 为什么必须重算：记忆里那份 42 项清单（`85` 轮）按条目数只累到 37，
   **与 42 对不上**——入稿前必须当场量（通则⑧）。
★ 只读，不写语料。
"""
import io, json, glob, os, re, sys
from collections import Counter

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
sys.stdout.reconfigure(encoding='utf-8')

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
CJK = re.compile(r'[\u4e00-\u9fff]')
KANA = re.compile(r'[\u3040-\u30ff]')
LAT = re.compile(r'[A-Za-z]')
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


slots = []
for r in rows:
    for m in LOOSE.finditer(r.get('prompt') or ''):
        n, d = parse(m.group(1))
        if n is not None:
            slots.append(n)

print('语料 %d 条；具名槽位 %d 个' % (len(rows), len(slots)))

no_lat = [n for n in slots if not LAT.search(n)]
print('★ 不含拉丁字母的槽名：实例 %d 个，去重后 %d 种' % (len(no_lat), len(set(no_lat))))
cjk = [n for n in no_lat if CJK.search(n)]
kana = [n for n in no_lat if not CJK.search(n)]
print('  ├ 含汉字者 %d 个（去重 %d 种）' % (len(cjk), len(set(cjk))))
print('  └ 不含汉字者 %d 个：%s' % (len(kana), sorted(set(kana))))
print()
print('★ 全表（按实例数降序，同数按名）：')
cnt = Counter(no_lat)
for n, c in sorted(cnt.items(), key=lambda t: (-t[1], t[0])):
    print('  %-24s ×%d   %s' % (n, c, '汉字' if CJK.search(n) else '非汉字'))
print()
print('★ 一次性行文用的紧凑串（供注[14]抄）：')
print('  ' + '、'.join(n if c == 1 else '%s（%d 次）' % (n, c)
                    for n, c in sorted(cnt.items(), key=lambda t: (-t[1], t[0]))))
print()
print('★ 汉字字符数（注[14] 字数预估）：')
s = '、'.join(n if c == 1 else '%s（%d 次）' % (n, c)
              for n, c in sorted(cnt.items(), key=lambda t: (-t[1], t[0])))
print('  紧凑串 %d 字符 / 汉字 %d' % (len(s), len(CJK.findall(s))))
