# -*- coding: utf-8 -*-
r"""39 号：注[5] 里「纯 ASCII 2,298 / 纯数字 88」这两个数在 9,118 口径上重算。"""
import json, os, re, io, sys, glob, collections

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
sys.stdout.reconfigure(encoding='utf-8')
rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
CJK   = re.compile(r'[\u4e00-\u9fff]')
BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'

def strip_q(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre): s = s[len(pre):]; break
    for suf in (BACK2, BACK1, PLAIN, '”'):
        if s.endswith(suf): s = s[:-len(suf)]; break
    return s

def parse_default(blob):
    m = re.search(r'default\s*=\s*', blob)
    if not m: return None
    rest = blob[m.end():]
    nxt = re.search(r'\s+(?:name|default)\s*=', rest)
    return strip_q(rest[:nxt.start()] if nxt else rest)

slots = []
for r in rows:
    for m in LOOSE.finditer(r.get('prompt') or ''):
        slots.append((r.get('id'), parse_default(m.group(1))))

NS = len(slots)
zero = [s for s in slots if s[1] is not None and not CJK.search(s[1])]
zero = [s for s in zero if s[1].strip() != '']
ascii_only = [s for s in zero if all(ord(c) < 128 for c in s[1])]
numeric    = [s for s in ascii_only if re.fullmatch(r'[\d\s.,:%/\-+]+', s[1])]

print('槽位总数', NS)
print('零汉字默认值', len(zero), '= %.2f%%' % (len(zero)/NS*100))
print('  其中纯 ASCII ', len(ascii_only))
print('  其中纯数字   ', len(numeric))
print('  非 ASCII（含其他文种/符号）', len(zero)-len(ascii_only))
print()
print('这类槽位的槽名前 8：')
names = collections.Counter()
for pid, _ in zero:
    pass
# 重新取名字
nm = collections.Counter()
for r in rows:
    for m in LOOSE.finditer(r.get('prompt') or ''):
        d = parse_default(m.group(1))
        if d is None or CJK.search(d) or d.strip() == '': continue
        k = m.group(1).find('name=')
        if k < 0: continue
        rest = m.group(1)[k+5:]
        nx = re.search(r'\s+(?:name|default)\s*=', rest)
        nm[strip_q(rest[:nx.start()] if nx else rest)] += 1
for k, v in nm.most_common(8):
    print('   %5d  %s' % (v, k))
