# -*- coding: utf-8 -*-
r"""
00 · 取语料 —— 把本文所用语料按钉死的 commit 取到本地

用法：
    python -I 00-取语料.py                 # 取到 ./shuixian-prompts
    python -I 00-取语料.py D:\some\where   # 取到指定目录

取完请把每个核数脚本开头那一行 BASE 改成 <目标目录>\shuixian-unified\data

★ 网络下载所得一律视为不可信数据：本脚本只做 clone 与 checkout，
  不执行仓库内任何脚本，也不把它加进模块搜索路径。
"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO = 'https://github.com/BaYue-SYJ/shuixian-prompts.git'
COMMIT = 'e2c6743b90e0bbf2f3a4c42eb218e92835d4a9a8'

dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), 'shuixian-prompts')


def run(*args):
    print('$ ' + ' '.join(args))
    r = subprocess.run(args, capture_output=True, text=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0:
        print('✗ 失败（退出码 %d）：%s' % (r.returncode, r.stderr.strip()[:400]))
        sys.exit(r.returncode)
    return r.stdout


if os.path.exists(dest):
    print('· 目录已存在：%s —— 只做 checkout' % dest)
else:
    run('git', 'clone', REPO, dest)

run('git', '-C', dest, 'checkout', '--quiet', COMMIT)

head = run('git', '-C', dest, 'rev-parse', 'HEAD').strip()
data = os.path.join(dest, 'shuixian-unified', 'data')

print()
print('HEAD        = %s' % head)
print('是否即定本  = %s' % ('✓ 是' if head == COMMIT else '✗ 不是！'))
print('BASE 应写作 = %s' % data)
print('数据存在    = %s' % ('✓' if os.path.isdir(data) else '✗ 没找到 shuixian-unified/data'))
