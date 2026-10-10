# -*- coding: utf-8 -*-
"""
稿子里的**逐字引文**必须当场与语料比对，不能靠转抄。
本脚本校验三处：
  ① §一 的 blockquote 语料行（须完整出现在语料某条 prompt 里）
  ② §二 围栏代码块甲（47 字符）
  ③ §二 围栏代码块乙（190 字符）
——从**稿子文件本身**读出这三行，再去语料里找，找不到就报错。
"""
import json, os, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

FP   = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\论文-谁划的格子.md'
BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)
prompts = [r.get('prompt') or '' for r in rows]
blob = '\n'.join(prompts)

with io.open(FP, 'r', encoding='utf-8', newline='') as f:
    lines = f.read().split('\n')

# ① blockquote 语料行
bq = [ln for ln in lines if ln.lstrip().startswith('>') and '{argument' in ln]
# ②③ 围栏内的行
fence, in_f = [], False
for ln in lines:
    if ln.lstrip().startswith('```'):
        in_f = not in_f; continue
    if in_f: fence.append(ln)

print('=' * 70)
ok = True
def chk(tag, s):
    global ok
    hit = s in blob
    if not hit: ok = False
    print('  %-26s 长度 %4d  逐字命中：%s' % (tag, len(s), '✅' if hit else '❌ 不在语料里'))
    if not hit:
        print('      %s' % s[:120])

for i, ln in enumerate(bq, 1):
    chk('§一 blockquote 引文 %d' % i, ln.lstrip()[2:].strip())
for i, ln in enumerate(fence, 1):
    chk('§二 围栏代码块 %d' % i, ln)

print('')
print('  合计：blockquote %d 行 ／ 围栏内 %d 行' % (len(bq), len(fence)))
print('  → %s' % ('全部逐字命中 ✅' if ok else '❌ 有不命中者，须修'))
