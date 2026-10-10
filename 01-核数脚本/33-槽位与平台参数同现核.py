# -*- coding: utf-8 -*-
"""
复核一条承重推论：`{argument}` 槽位与 MJ `--参数` 是否**同现**在同一记录里。

为什么要复核：若 `{argument}` 是某一座生图平台（即梦）的语法，
它就不该与 MJ 专属参数（--ar 等）出现在同一条 prompt 里。
—— 这条推论是 `16-界面与平台证据-2026-10-09.md` §二 第三条的全部依据，
   落稿前必须能重算。

口径：报【记录数】与【出现次数】两个数，分开报；并打印同现实例的 id 供抽查。
"""
import json, os, re, io, sys, glob

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\33-槽位与平台参数同现核-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

prompts = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        prompts.extend(json.load(fh))

# 三类装置
RE_ARG_DIRECT = re.compile(r'\{argument[^}]*\}')          # 直引号式槽位
RE_ARG_ESC    = re.compile(r'\{\\?"?argument')            # 转义式（宽口径，只用于定位）
RE_MJ_PARAM   = re.compile(r'(?<![\w-])--[a-z]{1,10}\b', re.I)
RE_SD_WEIGHT  = re.compile(r'\([^()]{0,60}:\s*[\d.]+\s*\)')
RE_LORA       = re.compile(r'<lora:', re.I)

n = len(prompts)
def scan(pred):
    return [p for p in prompts if pred(p.get('prompt') or '')]

has_arg  = scan(lambda s: RE_ARG_DIRECT.search(s) or '\\"argument' in s or '{argument' in s)
has_mj   = scan(lambda s: RE_MJ_PARAM.search(s))
has_sd   = scan(lambda s: RE_SD_WEIGHT.search(s) or RE_LORA.search(s))

both_mj  = [p for p in has_arg if RE_MJ_PARAM.search(p.get('prompt') or '')]
both_sd  = [p for p in has_arg if RE_SD_WEIGHT.search(p.get('prompt') or '') or RE_LORA.search(p.get('prompt') or '')]

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

P('槽位 × 平台参数 同现核   语料 =', n, '条')
P('')
P('含槽位的记录          :', len(has_arg))
P('含 MJ --参数的记录    :', len(has_mj))
P('含 SD 权重/lora 的记录:', len(has_sd))
P('')
P('★ 同时含 槽位 与 MJ --参数 :', len(both_mj))
P('★ 同时含 槽位 与 SD 权重/lora:', len(both_sd))
P('')
P('【同现实例（至多 12 条，供抽查）】')
P('-' * 74)
for p in both_mj[:12]:
    s = p.get('prompt') or ''
    args = RE_ARG_DIRECT.findall(s)[:4]
    mjs  = RE_MJ_PARAM.findall(s)[:6]
    P('id=' + str(p.get('id')) + '  MJ参数=' + repr(mjs))
    P('    槽位=' + repr(args))
    P('    原文前 200 字: ' + s[:200].replace('\n', ' '))
    P('')

if not both_mj:
    P('（无同现）')
o.close()
print('\n写出：', OUT)
