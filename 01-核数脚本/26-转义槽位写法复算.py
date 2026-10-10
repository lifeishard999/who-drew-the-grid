# -*- coding: utf-8 -*-
"""
25 号抽出一个**口径事故**（发现于 2026-10-09，写 §二 的过程中）：

  `01` 号的 SLOT 正则要求直引号：
      \{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}
  但在 JSON 字符串**内部**，引号必须转义：
      "{argument name=\"hair color\" default=\"浅蓝色\"}"
  这种写法的槽位，`01` 一拍都没拍到 → 它统计出的「2,520 条不含具名槽位」**是高估**。
  §一 脚注 [2] 引的就是这个 2,520，须订正。

本脚本把两种写法都算上，重算：
  ① 含槽位的记录数（直引号式 ／ 转义式 ／ 二者并集）
  ② 真正"一个花括号都没有"的记录数（这一条才配写进 §二：「连一个空格都没有」）
  ③ 槽位总数与默认值汉字总数（两种式样各自计）
  ④ 两种写法是否指向同一批模板（重叠多少）
"""
import json, os, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\26-转义槽位写法复算-2026-10-09.txt'

# 直引号式（与 01 逐字相同）
SLOT_P = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
# 转义式（JSON 字符串内部）
SLOT_E = re.compile(r'\{argument\s+name=\\"([^"]*?)\\"(?:\s+default=\\"([^"]*?)\\")?\}')
ANY    = re.compile(r'\{[^}]{0,300}\}')
HAN    = re.compile(r'[\u4e00-\u9fff]')

rows = []
for nm in ('prompts.part1.json', 'prompts.part2.json', 'prompts.part3.json'):
    with io.open(os.path.join(BASE, nm), 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, list):
        rows.extend(d)

o = io.open(OUT, 'w', encoding='utf-8')
def P(*a): o.write(' '.join(str(x) for x in a) + '\n')
P('转义槽位写法复算    2026-10-09')
P('=' * 78)
P('  记录总数 %d' % len(rows))
P('')

rec_p = rec_e = rec_both = rec_either = 0
rec_any_brace = 0
n_p = n_e = 0
defhan_p = defhan_e = 0
for r in rows:
    t = r.get('prompt') or ''
    mp = list(SLOT_P.finditer(t))
    # 转义式：把 \" 还原成 " 再套同一个正则更稳，但那样会与直引号式混同；
    # 故先用转义正则单独抓，再把它从串里挖掉，避免重复计。
    me = list(SLOT_E.finditer(t))
    tt = t
    for m in reversed(me):
        tt = tt[:m.start()] + '\x00' * (m.end() - m.start()) + tt[m.end():]
    mp2 = list(SLOT_P.finditer(tt))          # 挖掉转义式后仍命中者＝纯直引号式
    has_p = len(mp2) > 0
    has_e = len(me) > 0
    if has_e: rec_e += 1
    if has_p: rec_p += 1
    if has_p and has_e: rec_both += 1
    if has_p or has_e: rec_either += 1
    if ANY.search(t): rec_any_brace += 1
    n_p += len(mp2); n_e += len(me)
    for m in mp2: defhan_p += len(HAN.findall(m.group(2) or ''))
    for m in me:  defhan_e += len(HAN.findall(m.group(2) or ''))

P('【甲】两种写法各自的覆盖面')
P('-' * 78)
P('  只按直引号式（01 的口径）含槽位的记录        %5d   ← 旧记 2,932' % rec_p)
P('  含转义式槽位的记录                          %5d' % rec_e)
P('  两种都有                                      %5d' % rec_both)
P('  ★ 并集（真正含槽位的记录）                   %5d' % rec_either)
P('  ★ 因此"不含具名槽位"的记录应为                %5d   ← 旧记 2,520，高估了 %d 条'
  % (len(rows) - rec_either, 2520 - (len(rows) - rec_either)))
P('')
P('【乙】槽位总数')
P('-' * 78)
P('  直引号式 %5d（旧记 8,145）' % n_p)
P('  转义式   %5d' % n_e)
P('  合计     %5d' % (n_p + n_e))
P('  默认值汉字：直引号式 %d ／ 转义式 %d ／ 合计 %d（旧记 50,965）'
  % (defhan_p, defhan_e, defhan_p + defhan_e))
P('')
P('【丙】真正"连花括号都没有"的记录（§二 要用的那个数）')
P('-' * 78)
P('  含任意花括号片段 %5d' % rec_any_brace)
P('  ★ 一个花括号都没有 %5d  ＝ 全库 %.1f%%'
  % (len(rows) - rec_any_brace, 100.0 * (len(rows) - rec_any_brace) / len(rows)))
o.close()
print('写盘：%s' % OUT)
print('OK')
