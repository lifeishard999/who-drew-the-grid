# -*- coding: utf-8 -*-
"""
平台归属探针：语料到底是"只收一座平台（即梦）的用法"，还是平台中立？

动因：README.md L9 明写「兼容模型：ChatGPT·Grok·Gemini·Midjourney·Stable Diffusion·Flux·
即梦·可灵·豆包·海螺·文心一格等等」，与论文 §一「只收一座平台（即梦）的用法」直接冲突。
而 `_可行性评估-2026-09-20.md` §六 问题 3「平台绑定即梦模板语法」**未给证据**，meta.json 也无平台字段。

做法：在 5,452 条 prompt 里找**各平台的特征串**。命中近零 = 语料是平台中立的；
命中成规模 = 有平台烙印，须改论文口径。

口径：一律报【记录数】与【出现次数】两个数，分开报。
"""
import json, os, re, io, sys, glob

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\32-平台归属探针-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

# 读全部 prompts.part*.json
prompts = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        prompts.extend(json.load(fh))
print('记录数 =', len(prompts))

# 各平台特征串
PATTERNS = [
    # Midjourney
    ('MJ: --ar',        re.compile(r'--ar\b', re.I)),
    ('MJ: --v / --niji / --style / --stylize / --chaos / --q',
                        re.compile(r'--(?:v|niji|style|stylize|chaos|q|s|iw|no)\b', re.I)),
    ('MJ: 任意 --参数',  re.compile(r'(?<![\w-])--[a-z]{1,10}\b', re.I)),
    # Stable Diffusion / A1111
    ('SD: 权重括号 (x:1.2)', re.compile(r'\([^()]{0,60}:\s*[\d.]+\s*\)')),
    ('SD: <lora:...>',   re.compile(r'<lora:', re.I)),
    ('SD: 采样参数块 (Steps/CFG/Sampler/Seed)', re.compile(r'\b(?:Steps|CFG ?scale|Sampler|Seed|Negative prompt)\s*:', re.I)),
    # 通用负面词写法
    ('负向: 负面提示/negative prompt（中文）', re.compile(r'负面提示|负向提示词|反向提示词')),
    # 平台中文名直呼
    ('直呼 即梦',        re.compile(r'即梦')),
    ('直呼 MJ/midjourney', re.compile(r'midjourney|mj\b', re.I)),
    ('直呼 stable diffusion/sd', re.compile(r'stable\s*diffusion|\bsd\b', re.I)),
    ('直呼 可灵/豆包/海螺/文心', re.compile(r'可灵|豆包|海螺|文心一格')),
    # 画幅/分辨率写法
    ('画幅 16:9 等比例串', re.compile(r'\b\d{1,2}\s*[:：]\s*\d{1,2}\b')),
    ('画幅 --ar 之外的「横屏/竖屏/方图」', re.compile(r'竖屏|横屏|方图|竖版|横版')),
]

rows = []
for label, pat in PATTERNS:
    rec = 0; tot = 0
    for p in prompts:
        s = p.get('prompt') or ''
        n = len(pat.findall(s))
        if n:
            rec += 1; tot += n
    rows.append((label, rec, tot))

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

P('平台归属探针  语料 =', len(prompts), '条')
P('')
P(f"{'特征串':<44}{'记录数':>8}{'占比':>9}{'出现次数':>10}")
P('-' * 74)
for label, rec, tot in rows:
    P(f"{label:<44}{rec:>8}{rec/len(prompts)*100:>8.2f}%{tot:>10}")

P('')
P('【判读用：各串的实例（每种最多 3 条）】')
for label, pat in PATTERNS:
    hits = [(p.get('id'), (p.get('prompt') or '')) for p in prompts if pat.search(p.get('prompt') or '')]
    if hits:
        P('')
        P('## ' + label + f'  （共 {len(hits)} 条）')
        for i, s in hits[:3]:
            P('   id=' + str(i) + ' | ' + s[:160])
o.close()
print('\n写出：', OUT)
