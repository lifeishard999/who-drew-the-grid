# -*- coding: utf-8 -*-
r"""
85e · 两件事
 ① 稿内所引《S/Z》各句，逐字回屠友祥中译本（_SZ来源\_纯文本）核一遍
    ——注[11] 只记「出版方授权的电子试读本，已通读全章」，现用户给了全文 epub，可把引文钉死
 ② 第十三封信 §1.1 引的巴特两句，在屠译本里有没有对应话头（信里那两句的译法是不是这一版的）
 ③ 「即梦模板语法」这句在我 2026-09-20 的记录里出现过——查仓库 README／站点自述，看它有没有出处
"""
import glob
import io
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SZ = pathlib.Path(r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\_SZ来源\_纯文本')
REPO = pathlib.Path(r'F:\数据集\水仙提示词库')

txt = {}
for p in sorted(SZ.glob('part*.txt')):
    with open(p, encoding='utf-8', newline='') as f:
        txt[p.stem] = f.read()
ALL = '\n'.join(txt.values())
print('S/Z 纯文本：%d 个文件，合计 %d 字符' % (len(txt), len(ALL)))
print()

# ── ① 稿内所引
QUOTES = [
    ('不可能出自科学，因为科学不作估测', 'L137／L207 引'),
    ('此实践就是写作', 'L137 引'),
    ('现今能够被写作（重新写作）的东西', 'L137／L207 引'),
    ('能够让人阅读，但无法引人写作', 'L137／L207 引'),
    ('文学工作的目的，在令读者做文的生产者，而非消费者', 'L137 引'),
    ('古典之文', 'L137 引'),
    ('能引人写作者', 'L133／L241 术语'),
    ('能引人阅读者', 'L241 术语'),
    ('就容易理解为客体，与巴特的 le scriptible 含义不吻合', 'L241 注[11] 所引译注'),
    ('评估', '第一章章题'),
]
print('① 稿内所引《S/Z》各句，逐字回屠译本：')
for q, where in QUOTES:
    hits = [n for n, v in txt.items() if q in v]
    print('  %-38s %s  %s' % (q, '✓' if hits else '✗ 未命中', hits[:4]))

print()
print('② 第十三封信 §1.1 引的巴特两句，在屠译本里有没有：')
LETTER = ['永恒的此时此刻', '无休无止的现在', '无始', '可逆', '门道纵横', '随处可入',
          '没有单一主体权', '单一主体', '主体权', '意义生产的无限性', '能引人写作者']
for q in LETTER:
    hits = [n for n, v in txt.items() if q in v]
    print('  %-24s %s  %s' % (q, '✓' if hits else '✗ 未命中', hits[:4]))

print()
print('③ 屠译本里「能引人写作」的全部落点：')
for n, v in sorted(txt.items()):
    c = v.count('能引人写作')
    if c:
        print('  %-14s ×%d' % (n, c))

print()
print('④ 「即梦」在屠译本里（应为 0）：', ALL.count('即梦'))
print()
print('=' * 78)
print('⑤ 仓库／站点自述里有没有把 {argument name=} 说成「即梦」的语法：')
for name in ('README.md', 'README.en.md', 'about.html', 'index.html'):
    for p in list(REPO.rglob(name)):
        with open(p, encoding='utf-8', errors='replace', newline='') as f:
            s = f.read()
        for kw in ('即梦', 'jimeng', 'dreamina', 'argument'):
            n = len(re.findall(kw, s, re.I))
            if n:
                print('  %-46s %-9s ×%d' % (str(p.relative_to(REPO))[:46], kw, n))
print()
print('  含「即梦」的上下文（README／about）：')
seen = set()
for name in ('README.md', 'README.en.md'):
    for p in list(REPO.rglob(name)):
        with open(p, encoding='utf-8', errors='replace', newline='') as f:
            s = f.read()
        for m in re.finditer('即梦', s):
            ctx = s[max(0, m.start() - 90):m.start() + 90].replace('\n', ' ')
            if ctx not in seen:
                seen.add(ctx)
                print('    [%s] …%s…' % (p.name, ctx))
