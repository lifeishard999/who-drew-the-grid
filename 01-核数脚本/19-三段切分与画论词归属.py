# -*- coding: utf-8 -*-
"""
§二 要以「画论词汉字 97.40% 在预制侧」立论。写之前先堵一个漏洞：

  01 号的「固定文本」＝ SLOT.sub('', t)，**只拿掉 {argument} 槽位**，
  而 **JSON 版式块（J 类）留在"固定文本"里面**。
  可 J 块本身也是一种"留给人改"的装置（改的是值）。
  → 若画论词出现在 J 块里，就被 01/02 误记成了"预制"。**必须先量。**

本脚本把每条记录切成**三段**（互斥、无重叠）：
  A 段＝具名槽位及其默认值 {argument name=… default=…}
  J 段＝JSON 版式块
  R 段＝其余正文（真正的"策展人预制散文"）
再让画论词（与 01/02 逐字相同的 37 词表）在三段里各点一次数。

另附：短 J 块样本（逐字，供 §二 原样贴出）、默认值含画论词的槽位全表（44 个）。
"""
import json, os, io, re, sys, collections

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\19-三段切分与画论词归属-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

SLOT = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')   # 与 01 逐字相同
JB   = re.compile(r'\{[^{}]*?"[^"]+"\s*:[^{}]*?\}')                            # JSON 版式块（无嵌套花括号）
HAN  = re.compile(r'[\u4e00-\u9fff]')

CN_PAINT = ['水墨', '工笔', '写意', '山水', '画意', '意境', '宣纸', '留白', '皴', '泼墨',
            '白描', '气韵', '丹青', '没骨', '界画', '青绿', '卷轴', '立轴', '手卷', '斗方',
            '题跋', '章法', '笔法', '墨色', '淡彩', '重彩', '院体', '文人画', '国画',
            '花鸟', '人物画', '工笔画', '水墨画', '毛笔', '砚', '印章', '题款']
CN_SET = sorted(set(CN_PAINT), key=len, reverse=True)

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')

P('三段切分与画论词归属    2026-10-09    记录 %d' % len(rows))
P('=' * 78)

def count_words(s):
    """返回 {词: 词次}，长词优先、命中后从串里挖掉，避免「水墨」与「水墨画」重复计。"""
    s = s or ''
    hit = collections.Counter()
    for w in CN_SET:
        n = s.count(w)
        if n:
            hit[w] += n
            s = s.replace(w, '\x00' * len(w))
    return hit

tot_han = {'A': 0, 'J': 0, 'R': 0}
tot_words = {'A': 0, 'J': 0, 'R': 0}
cnt = {'A': 0, 'J': 0, 'R': 0}
words_in = {'A': collections.Counter(), 'J': collections.Counter(), 'R': collections.Counter()}
a_slot_han = 0        # 槽位默认值汉字（A 段的"可填"部分）
a_name_ch = 0
slots_with_paint = []
short_J = []
j_samples_seen = set()
n_jb = 0

for r in rows:
    t = r.get('prompt') or ''
    # 先抠 A（slot）——连同默认值一起，整段归 A
    a_txt_parts = []
    for m in SLOT.finditer(t):
        a_txt_parts.append(m.group(2) or '')
        a_slot_han += len(HAN.findall(m.group(2) or ''))
        d = m.group(2) or ''
        if any(w in d for w in CN_SET):
            slots_with_paint.append((m.group(1), d, t[:70]))
    a_txt = ' '.join(a_txt_parts)
    rest = SLOT.sub('', t)
    # 再从 rest 里抠 J
    j_txt_parts = []
    for m in JB.finditer(rest):
        b = m.group(0)
        if 'argument' in b:          # 转义引号变体等，不当作 JSON
            continue
        n_jb += 1
        j_txt_parts.append(b)
        key = re.sub(r'"[^"]*"', '"…"', b)[:60]
        if len(b) <= 150 and key not in j_samples_seen:
            j_samples_seen.add(key)
            short_J.append(b)
    j_txt = ' '.join(j_txt_parts)
    r_txt = JB.sub(lambda m: '' if 'argument' not in m.group(0) else m.group(0), rest)

    for k, s in (('A', a_txt), ('J', j_txt), ('R', r_txt)):
        cnt[k] += 1 if s.strip() else 0
        tot_han[k] += len(HAN.findall(s))
        w = count_words(s)
        tot_words[k] += sum(w.values())
        words_in[k].update(w)

P('')
P('【0】三段各有多大（汉字/字符口径与 01 号一致：汉字数）')
P('-' * 78)
P('  %-6s %10s %10s' % ('段', '汉字数', '占比'))
for k, lab in (('R', 'R 其余正文（策展人散文）'), ('J', 'J JSON 版式块'),
               ('A', 'A 槽位默认值（可填）')):
    P('  %-6s %10d %9.2f%%   ← %s' % (k, tot_han[k],
      100.0 * tot_han[k] / sum(tot_han.values()), lab))
P('  合计 %d 汉字' % sum(tot_han.values()))
P('  ★ 其中 A 段＝**槽位默认值里的汉字总数**，应等于旧记 50,965：%s' % a_slot_han)

P('')
P('【1】★★ 画论词在三段里的分布（词次）——这是 §二的立论根据')
P('-' * 78)
tw = sum(tot_words.values())
P('  %-26s %8s %8s' % ('段', '词次', '占比'))
for k, lab in (('R', '其余正文'), ('J', 'JSON 版式块'), ('A', '槽位默认值')):
    P('  %-26s %8d %7.2f%%' % (lab, tot_words[k], 100.0 * tot_words[k] / tw))
P('  %-26s %8d' % ('合计', tw))
P('')
P('  ★ 旧口径「预制侧」＝ J ＋ R ＝ %d 词次，占 %.2f%%'
  % (tot_words['J'] + tot_words['R'],
     100.0 * (tot_words['J'] + tot_words['R']) / tw))
P('  ★ 若「可写」只算 A（具名槽位）＝ %d 词次，占 %.2f%%'
  % (tot_words['A'], 100.0 * tot_words['A'] / tw))
P('  ★ ★ 但 J 段里画论词 %d 词次 —— **必须判读这 %d 次是不是"用户可改的值"**'
  % (tot_words['J'], tot_words['J']))
P('')
P('  逐词（R / J / A）：')
keys = set()
for k in words_in: keys |= set(words_in[k])
for w in sorted(keys, key=lambda x: -(words_in['R'][x] + words_in['J'][x] + words_in['A'][x])):
    P('    %-8s R=%-6d J=%-6d A=%-6d' % (w, words_in['R'][w], words_in['J'][w], words_in['A'][w]))

P('')
P('【2】J 段里出现的画论词，逐条看（上限 40 条，判"值"还是"键"）')
P('-' * 78)
n = 0
for r in rows:
    t = r.get('prompt') or ''
    rest = SLOT.sub('', t)
    for m in JB.finditer(rest):
        b = m.group(0)
        if 'argument' in b: continue
        if any(w in b for w in CN_SET):
            n += 1
            if n <= 40:
                P('   %s' % b[:220])
P('  含画论词的 J 块共 %d 个' % n)

P('')
P('【3】短 J 块样本（逐字，≤150 字符，去重后前 24 条）——供 §二 原样贴出')
P('-' * 78)
for b in short_J[:24]:
    P('   %s' % b)
P('  （去重后短样本共 %d 条）' % len(short_J))

P('')
P('【4】默认值含画论词的槽位全表（%d 个）——「哪一种画法可以被商量」的正面清单' % len(slots_with_paint))
P('-' * 78)
for i, (nm, d, ctx) in enumerate(slots_with_paint, 1):
    P('   %2d. %-22s = %s' % (i, nm, d))

P('')
P('【5】J 块总数（本脚本正则）＝ %d   （旧记 2,250，02 号正则）' % n_jb)
o.close()
print('写盘：%s' % OUT)
print('OK')
