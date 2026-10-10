# -*- coding: utf-8 -*-
r"""
38 号：在 9,118 口径上重算画论词（★ 用 19 号的长词优先算法），并修正中位数口径。

37 号犯了两个错，本脚本逐一改掉：
  ① **画论词用朴素 count** → 「水墨画」里的「水墨」被重复计，得 61/51；
     19 号的 count_words 是**长词优先、命中后从串里挖掉**，才是既有口径。已逐字照搬。
  ② **中位数口径错**：注[2] 的「370 : 13」是**按记录**算的
     （一条记录里 预制文本的汉字数 / 全部槽位默认值合计的汉字数），
     我 37 号却按**槽位**算了槽位侧，得 4.0。
     ★ 「每槽中位 4 汉字」是**另一个分母**的数，两者不可混说。

自检：必须复现 注[2] 370 / 13、注[6] 槽位侧 54 词次 / 50 槽位（在 9,090 口径上）。
"""
import json, os, re, io, sys, glob, collections

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\38-画论词在9118口径上-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

# ── 19 号：词表与计数法，逐字照搬 ──────────────────────────
CN_PAINT = ['水墨', '工笔', '写意', '山水', '画意', '意境', '宣纸', '留白', '皴', '泼墨',
            '白描', '气韵', '丹青', '没骨', '界画', '青绿', '卷轴', '立轴', '手卷', '斗方',
            '题跋', '章法', '笔法', '墨色', '淡彩', '重彩', '院体', '文人画', '国画',
            '花鸟', '人物画', '工笔画', '水墨画', '毛笔', '砚', '印章', '题款']
CN_SET = sorted(set(CN_PAINT), key=len, reverse=True)

def count_words(s):
    """长词优先、命中后从串里挖掉，避免「水墨」与「水墨画」重复计。（19 号逐字）"""
    s = s or ''
    hit = collections.Counter()
    for w in CN_SET:
        n = s.count(w)
        if n:
            hit[w] += n
            s = s.replace(w, '\x00' * len(w))
    return hit

# ── 26 号精确口径 与 36 号扫描口径，两套都建，用于标出"新认的槽位" ──
SLOT_P = re.compile(r'\{argument\s+name="([^"]*)"(?:\s+default="([^"]*)")?\}')
SLOT_E = re.compile(r'\{argument\s+name=\\"([^"]*?)\\"(?:\s+default=\\"([^"]*?)\\")?\}')
LOOSE  = re.compile(r'\{argument\s+([^}]*?)\s*\}')
CJK    = re.compile(r'[\u4e00-\u9fff]')
BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'

def strip_q(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre): s = s[len(pre):]; break
    for suf in (BACK2, BACK1, PLAIN, '”'):
        if s.endswith(suf): s = s[:-len(suf)]; break
    return s

def parse(blob):
    out = {}
    for key in ('name', 'default'):
        m = re.search(key + r'\s*=\s*', blob)
        if not m: out[key] = None; continue
        rest = blob[m.end():]
        nxt = re.search(r'\s+(?:name|default)\s*=', rest)
        out[key] = strip_q(rest[:nxt.start()] if nxt else rest)
    return out['name'], out['default']

def han(s): return len(CJK.findall(s or ''))
def median(xs):
    xs = sorted(xs); n = len(xs)
    return 0 if n == 0 else (xs[n//2] if n % 2 else (xs[n//2-1]+xs[n//2])/2)

slots = []                 # (id, name, default, is_new)
per_rec_pred, per_rec_slot, per_slot = [], [], []
for r in rows:
    t = r.get('prompt') or ''
    ms = list(LOOSE.finditer(t))
    if not ms: continue
    # 26 号精确口径覆盖到的位置
    covered = [False]*len(t)
    for m in list(SLOT_P.finditer(t)) + list(SLOT_E.finditer(t)):
        for i in range(m.start(), m.end()): covered[i] = True
    tot_def_han = 0
    for m in ms:
        n, d = parse(m.group(1))
        new = not any(covered[m.start():m.end()])
        slots.append((r.get('id'), n, d, new))
        tot_def_han += han(d)
        per_slot.append(han(d))
    per_rec_pred.append(han(LOOSE.sub('', t)))
    per_rec_slot.append(tot_def_han)

NS, NR = len(slots), len(per_rec_pred)
o = io.open(OUT, 'w', encoding='utf-8')
def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

W('画论词 · 9,118 口径（19 号算法）   记录', len(rows))
W('')
W('【零】自检')
W(f"  含槽位记录 {NR}   槽位 {NS}   ★ 新认（E2 双反斜杠 / 值含引号）槽位 {sum(1 for s in slots if s[3])}")
W(f"  预制中位汉字（按记录）        {median(per_rec_pred):>7}   注[2]：370")
W(f"  槽位默认值中位汉字（按记录）  {median(per_rec_slot):>7}   注[2]：13")
W(f"  槽位默认值中位汉字（按槽位）  {median(per_slot):>7}   记忆另记：每槽中位 4")
W('')

W('【一】★ 画论词落在槽位默认值里（19 号算法，剔前）')
tot = collections.Counter(); hits = []
for pid, nm, d, new in slots:
    h = count_words(d)
    if h:
        hits.append((pid, nm, d, new, h)); tot += h
W(f"  含画论词的槽位 {len(hits)}   词次 {sum(tot.values())}")
W(f"  （注[6] 在 9,090 口径上：50 槽位 / 54 词次）")
W(f"  分母＝全库画论词次 1,931  →  {sum(tot.values())/1931*100:.2f}%")
W('')
W('  逐词：' + '  '.join(f'{w}×{c}' for w, c in tot.most_common()))
W('')
newhits = [h for h in hits if h[3]]
W(f"  ★ 其中来自「新认槽位」的命中：{len(newhits)} 条")
for pid, nm, d, _, h in newhits:
    W(f"     id={pid} name={nm!r} default={d[:70]!r}  {dict(h)}")
W('')
W('  ---- 全部逐条（★ 供人工重判同形异义，不得静默丢弃）----')
for pid, nm, d, new, h in hits:
    W(f"    {'★新' if new else '   '} id={pid:<7} {nm!r:<26} {d[:56]!r}  {dict(h)}")

o.close()
print('\n写出：', OUT)
