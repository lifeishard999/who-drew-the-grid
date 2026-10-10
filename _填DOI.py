# -*- coding: utf-8 -*-
r"""
_填DOI · DOI 与仓库地址铸出后，一次替换 README 与 NOTICE 里的占位符

用法：
    python -I _填DOI.py 10.5281/zenodo.1234567
    python -I _填DOI.py 10.5281/zenodo.1234567 https://github.com/用户名/仓库名

会替换 README.md、NOTICE-语料来源与署名.md 里的
    10.5281/zenodo.XXXXXXX   →  DOI
    [DOI]                    →  DOI（声明正文里用的记号，也是同一个 DOI）
    [REPO]                   →  仓库地址（给了第二个参数才替换）
并删掉 README 里那行 <!-- ← 铸出后… --> 的提示注释。
替换前各留一份 .bak（不存在才写，不覆盖已有备份）。

★ 仓库地址要等你把仓库建好、名字定下来再填——先印上一个错的地址，
  比留占位符更糟（包一推上去就是公开件）。
"""
import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 2:
    print('用法：python -I _填DOI.py 10.5281/zenodo.1234567 [https://github.com/用户名/仓库名]')
    sys.exit(1)

DOI = sys.argv[1].strip().replace('https://doi.org/', '').replace('doi:', '')
if not re.match(r'^10\.\d{4,9}/\S+$', DOI):
    print('✗ 这不像一个 DOI：%r' % DOI)
    sys.exit(1)

REPO = sys.argv[2].strip() if len(sys.argv) > 2 else None
if REPO and not re.match(r'^https://github\.com/\S+/\S+$', REPO):
    print('✗ 这不像一个 GitHub 仓库地址：%r' % REPO)
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS = ['README.md', 'NOTICE-语料来源与署名.md']
OLD_DOI = '10.5281/zenodo.XXXXXXX'
# ★ 第一版漏了这个记号：README §五「数据可用性声明」的正文里用的是 [DOI]，
#   不是 10.5281/zenodo.XXXXXXX，所以填完 DOI 后声明正文里仍是空空一个 [DOI]。
#   漏的偏偏是给论文直接抄的那两段——占位符必须与正文实际写法一致。
OLD_DOI2 = '[DOI]'
OLD_REPO = '[REPO]'

n_doi = n_repo = 0
for fn in TARGETS:
    fp = os.path.join(HERE, fn)
    if not os.path.exists(fp):
        print('· 跳过（不存在）：%s' % fn)
        continue
    with open(fp, 'r', encoding='utf-8', newline='') as f:
        t = f.read()
    c_doi = t.count(OLD_DOI) + t.count(OLD_DOI2)
    c_repo = t.count(OLD_REPO)
    if not c_doi and not (REPO and c_repo):
        print('· 无待替换占位符：%s' % fn)
        continue
    bak = fp + '.bak'
    if not os.path.exists(bak):
        shutil.copy2(fp, bak)
    t = t.replace(OLD_DOI, DOI).replace(OLD_DOI2, DOI)
    if REPO:
        t = t.replace(OLD_REPO, REPO)
    t = re.sub(r'[ \t]*<!-- ← 铸出后由 `_填DOI\.py` 一次性替换 -->\r?\n', '', t)
    with open(fp, 'w', encoding='utf-8', newline='') as f:
        f.write(t)
    n_doi += c_doi
    n_repo += c_repo if REPO else 0
    print('✓ %s：DOI 替换 %d 处，仓库地址替换 %d 处' % (fn, c_doi, c_repo if REPO else 0))

print()
print('共替换 DOI %d 处 → %s' % (n_doi, DOI))
if REPO:
    print('共替换仓库地址 %d 处 → %s' % (n_repo, REPO))
else:
    left = 0
    for fn in TARGETS:
        fp = os.path.join(HERE, fn)
        if os.path.exists(fp):
            with open(fp, 'r', encoding='utf-8', newline='') as f:
                t2 = f.read()
                left += t2.count(OLD_REPO) + t2.count(OLD_DOI) + t2.count(OLD_DOI2)
    if left:
        print('⚠ 还有 %d 处占位符没填（多为 [REPO]）——把仓库地址作为第二个参数再跑一次。' % left)
