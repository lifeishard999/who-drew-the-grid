# -*- coding: utf-8 -*-
r"""
44 号：通读（第二次）查出的三处**文本断言**，逐个当场量，不凭印象。

  ① L77「这两种空格是并排着的：**同一条提示词里**，一处是槽位，一处是版式块」
     → 须量：**同一条记录**里既有并集槽位、又有非 argument 的 JSON 版式块者，共几条。
  ② 表 1「槽名种数（仅出现一次者） 2,395（70.90%）」
     → 须量：槽名种数、只出现一次者的种数、占比。2,395 是**种数**还是**只出现一次者**？
  ③ 注[7]「出现最多的槽名是 character name（200 次）、headline text（151 次）、
     brand name（101 次）、subtitle text（53 次）」 —— **未点明分母**。
     → 须量：该榜是算在**全部 9,118 槽位**上，还是**2,515 个零汉字默认值**里？
     两套都算，对照 L95 的全局榜（hair color 638 居首）。

口径一律 **9,118 并集**（LOOSE 扫描，与 36／38 号一致）。
"""
import json, os, re, io, sys, glob, collections

BASE = r'F:\数据集\水仙提示词库\shuixian-unified\data'
OUT  = r'D:\桌面\博士立项\_会议论文-北大中文系-2026-10\44-通读三疑点核-2026-10-09.txt'
sys.stdout.reconfigure(encoding='utf-8')

rows = []
for f in sorted(glob.glob(os.path.join(BASE, 'prompts.part*.json'))):
    with io.open(f, encoding='utf-8') as fh:
        rows.extend(json.load(fh))

LOOSE = re.compile(r'\{argument\s+([^}]*?)\s*\}')
JB    = re.compile(r'\{[^{}]*?"[^"]+"\s*:[^{}]*?\}')
CJK   = re.compile(r'[\u4e00-\u9fff]')
BACK2, BACK1, PLAIN = '\\\\"', '\\"', '"'

def strip_q(s):
    s = s.strip()
    for pre in (BACK2, BACK1, PLAIN):
        if s.startswith(pre): s = s[len(pre):]; break
    for suf in (BACK2, BACK1, PLAIN, '\u201d'):
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

all_slots = []          # (name, default)
both_recs = []          # 既含槽位又含非 argument 版式块的记录
n_slot_rec = 0
for r in rows:
    t = r.get('prompt') or ''
    ms = list(LOOSE.finditer(t))
    rest = LOOSE.sub('', t)
    n_jb = 0
    for m in JB.finditer(rest):
        if 'argument' in m.group(0): continue
        n_jb += 1
    if ms: n_slot_rec += 1
    if ms and n_jb:
        both_recs.append((r.get('id'), len(ms), n_jb, t[:60]))
    for m in ms:
        n, d = parse(m.group(1))
        all_slots.append((n, d))

o = io.open(OUT, 'w', encoding='utf-8')
def W(*a):
    line = ' '.join(str(x) for x in a)
    o.write(line + '\n'); print(line)

W('通读三疑点核   语料 = %d 条   槽位 %d（并集口径）' % (len(rows), len(all_slots)))
W('=' * 78)
W('')
W('【①】L77「同一条提示词里，一处是槽位，一处是版式块」')
W('-' * 78)
W('  含并集槽位的记录           %d' % n_slot_rec)
W('  ★ 槽位 ∧ 非 argument 版式块  同现记录 **%d** 条' % len(both_recs))
for pid, ns, nj, ctx in both_recs[:20]:
    W('     id=%-7s 槽位 %-3d 版式块 %-2d  %r' % (pid, ns, nj, ctx))
if len(both_recs) > 20:
    W('     …（共 %d 条）' % len(both_recs))
W('')
W('【②】表 1「槽名种数（仅出现一次者） 2,395（70.90%）」')
W('-' * 78)
nn = collections.Counter(n for n, d in all_slots)
once = sum(1 for k, v in nn.items() if v == 1)
W('  槽位总数        %d' % len(all_slots))
W('  槽名**种数**       %d' % len(nn))
W('  只出现一次的**种数** %d   → 占种数 %.2f%%   占槽位 %.2f%%'
  % (once, 100.0 * once / len(nn), 100.0 * once / len(all_slots)))
W('  ★ 2,395 对得上的是哪一项，见上两行。')
W('  前 12 名（★ 对照正文 L95 的排序）：')
for i, (k, v) in enumerate(nn.most_common(12), 1):
    W('     %2d. %-24s %5d  %5.2f%%' % (i, k, v, 100.0 * v / len(all_slots)))
W('')
W('【③】注[7] 那份「出现最多的槽名」榜，分母是谁？')
W('-' * 78)
zero = [(n, d) for n, d in all_slots if len(CJK.findall(d or '')) == 0]
zn = collections.Counter(n for n, d in zero)
W('  零汉字默认值槽位 %d （占 %d 的 %.2f%%）' % (len(zero), len(all_slots), 100.0 * len(zero) / len(all_slots)))
W('  ★ 榜 A：算在**零汉字默认值**子集里（%d 个）：' % len(zero))
for i, (k, v) in enumerate(zn.most_common(8), 1):
    W('     %2d. %-24s %5d' % (i, k, v))
W('  ★ 榜 B：算在**全部槽位**里（%d 个）：' % len(all_slots))
for i, (k, v) in enumerate(nn.most_common(8), 1):
    W('     %2d. %-24s %5d' % (i, k, v))
W('')
W('  注[7] 原文：character name（200）、headline text（151）、brand name（101）、subtitle text（53）')
W('     榜A 中该四名：%s' % '  '.join('%s=%d' % (k, zn[k]) for k in
      ('character name', 'headline text', 'brand name', 'subtitle text')))
W('     榜B 中该四名：%s' % '  '.join('%s=%d' % (k, nn[k]) for k in
      ('character name', 'headline text', 'brand name', 'subtitle text')))
o.close()
print('\n写出：', OUT)
