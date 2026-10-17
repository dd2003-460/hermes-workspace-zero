#!/usr/bin/env python3
# origin: ai · m00552 条款①:场景化复刻检验 — 语言层量化
# 用途: python3 scenario-score.py <workspace>
# 输入: tasks/scenario-raw/S{1,2,3}_*_{persona|generic}-*.txt + /tmp/scen/*_gt.txt
# 输出: voice特征表 + A vs GT / B vs GT 余弦近似度 + drift-check 成璐度
# 无第三方依赖。GT=成璐真实消息(锚), A=persona盲生成, B=generic盲生成。
import sys, os, re, json

def load_raw(path):
    # 去掉 # 头行和 > 元数据行; --- 处理: axiom 的 body 在 --- 后, S2 generic msg1 在 --- 前
    lines = open(path, encoding='utf-8').read().splitlines()
    body = [l for l in lines if not l.startswith('#') and not l.startswith('>')]
    text = '\n'.join(body)
    if '---' in text:
        parts = text.split('---', 1)
        before = re.sub(r'\s', '', parts[0])
        after = re.sub(r'\s', '', parts[1])
        # axiom: --- 前(去元数据后)很短 → body 在 --- 后; S2 generic: --- 前是 msg1 → 取 --- 前
        text = parts[1] if len(before) < len(after) else parts[0]
    return text.strip()

def load_gt(path):
    t = open(path, encoding='utf-8').read().strip()
    # 去掉尾部日期 artifact(3月19日 等)
    t = re.sub(r'\s*\d{1,2}月\d{1,2}日\s*$', '', t)
    return t.strip()

def split_sentences(text):
    # 列表感知: 成璐 GT 编号项用空格或换行分隔且无句号; 小数(4.6opus)不拆
    t = text.replace('；', '。').replace(';', '。')
    segments = re.split(r'(?:(?<=\n)\s*|\s+)(?=\d+(?:\.\d+)?[\.\、])', t)
    sents = []
    for seg in segments:
        parts = re.split(r'([。！？!?])', seg)
        i = 0
        while i < len(parts):
            chunk = parts[i]
            if i+1 < len(parts) and parts[i+1] in '。！？!?':
                sents.append(chunk + parts[i+1]); i += 2
            else:
                if chunk.strip(): sents.append(chunk)
                i += 1
    return [s for s in sents if chars(s) > 0]

def chars(s):
    return len(re.sub(r'\s', '', s))

def features(text):
    sents = split_sentences(text)
    n = len(sents)
    total = chars(text)
    f = {
        'chars': total,
        'n_sents': n,
        'avg_sent_len': round(sum(chars(s) for s in sents)/n, 1) if n else 0,
        'first_person': round(sum(1 for s in sents if '我' in s)/n, 3) if n else 0,
        'question_rate': round(sum(1 for s in sents if s.rstrip().endswith(('？','?')))/n, 3) if n else 0,
        '所以': text.count('所以'),
        '但是': text.count('但是'),
        '所以_k': round(text.count('所以')/(total/1000), 1) if total else 0,
        '但是_k': round(text.count('但是')/(total/1000), 1) if total else 0,
        'suoyi_ratio': round(text.count('所以')/(text.count('但是')+1), 2),
        'conf_words': sum(text.count(w) for w in ['可能','应该','大概率','我觉得','我猜']),
        'conf_k': round(sum(text.count(w) for w in ['可能','应该','大概率','我觉得','我猜'])/(total/1000), 1) if total else 0,
        '可能': text.count('可能'),
        '应该': text.count('应该'),
        'bushi_ershi_kchar': round(len(re.findall(r'不是[^。！？\n]{0,30}而是', text))/(total/1000), 2) if total else 0,
        'empty_talk': sum(text.count(w) for w in ["值得注意的是","综上所述","显而易见","毋庸置疑","不难发现","由此可见","总而言之","需要指出","一方面","另一方面","首先","其次","最后"]),
        'empty_k': round(sum(text.count(w) for w in ["值得注意的是","综上所述","显而易见","毋庸置疑","不难发现","由此可见","总而言之","需要指出","一方面","另一方面","首先","其次","最后"])/(total/1000), 1) if total else 0,
        'numbered': len(re.findall(r'(?:^|\n)\s*\d+[\.\、]', text)) + len(re.findall(r'\d+\.\d+', text)),
        'numbered_k': round((len(re.findall(r'(?:^|\n)\s*\d+[\.\、]', text)) + len(re.findall(r'\d+\.\d+', text)))/(total/1000), 1) if total else 0,
        'cut': sum(text.count(w) for w in ['砍','不用讨论','先不']),
        'cut_k': round(sum(text.count(w) for w in ['砍','不用讨论','先不'])/(total/1000), 1) if total else 0,
    }
    return f

def drift_score(f):
    # 与 drift-check.py 同规则的独立实现(避免子进程), 便于同表输出
    s = 100.0
    if f['avg_sent_len'] > 70: s -= 25
    elif f['avg_sent_len'] > 55: s -= 10
    s -= 15 * f['empty_talk']
    if f['但是'] >= f['所以']: s -= 10
    if f['first_person'] < 0.2: s -= 10
    if f['可能'] + f['应该'] == 0: s -= 5   # 与 drift-check.py 同规则
    elif f['conf_words'] == 0: s -= 5
    if f['bushi_ershi_kchar'] > 0.7: s -= 5
    return max(0.0, s)

def cosine(a, b, dims):
    va = [a[d] for d in dims]; vb = [b[d] for d in dims]
    na = sum(x*x for x in va) ** 0.5; nb = sum(x*x for x in vb) ** 0.5
    if na == 0 or nb == 0: return 0.0
    return sum(x*y for x, y in zip(va, vb)) / (na*nb)

def main():
    ws = sys.argv[1] if len(sys.argv) > 1 else '.'
    raw = os.path.join(ws, 'projects/AI-计算科学/D1-persona-align/tasks/scenario-raw')
    scenes = {
        'S1-消费决策-硬件': '/tmp/scen/S1-消费决策-硬件_gt.txt',
        'S2-量化估算-元评估': '/tmp/scen/S2-量化估算-元评估_gt.txt',
        'S3-ML训练机制-CoT': '/tmp/scen/S3-ML训练机制-CoT_gt.txt',
    }
    DIMS = ['avg_sent_len','first_person','question_rate','suoyi_ratio','conf_k','bushi_ershi_kchar','empty_k','numbered_k','cut_k']
    results = {}
    for scene, gt_path in scenes.items():
        gt = load_gt(gt_path)
        gtf = features(gt)
        outs = {}
        for fn in sorted(os.listdir(raw)):
            if fn.startswith(scene) and '_persona-' in fn:
                outs['A'] = features(load_raw(os.path.join(raw, fn)))
            elif fn.startswith(scene) and '_axiom-' in fn:
                outs['AX'] = features(load_raw(os.path.join(raw, fn)))
            elif fn.startswith(scene) and '_generic-' in fn:
                outs['B'] = features(load_raw(os.path.join(raw, fn)))
        # 归一化: 以本场景 GT 为参照尺度做 cosine 前先整体 max 归一化(9文本)
        results[scene] = {'GT': gtf, **outs,
                          'cos_A_GT': None, 'cos_AX_GT': None, 'cos_B_GT': None,
                          'drift_A': drift_score(outs['A']), 'drift_AX': drift_score(outs['AX']),
                          'drift_B': drift_score(outs['B']),
                          'drift_GT': drift_score(gtf)}
    # 全部9文本 max 归一化后算 cosine
    allf = [results[s][k] for s in results for k in ('GT','A','AX','B')]
    norm = {}
    for d in DIMS:
        m = max(abs(x[d]) for x in allf) or 1
        norm[d] = m
    for s in results:
        g = results[s]['GT']; a = results[s]['A']; ax = results[s]['AX']; b = results[s]['B']
        gn = {d: g[d]/norm[d] for d in DIMS}
        an = {d: a[d]/norm[d] for d in DIMS}
        axn = {d: ax[d]/norm[d] for d in DIMS}
        bn = {d: b[d]/norm[d] for d in DIMS}
        results[s]['cos_A_GT'] = round(cosine(an, gn, DIMS), 3)
        results[s]['cos_AX_GT'] = round(cosine(axn, gn, DIMS), 3)
        results[s]['cos_B_GT'] = round(cosine(bn, gn, DIMS), 3)
    # 输出
    for s, r in results.items():
        print(f"\n===== {s} =====")
        print(f"{'指标':<18}{'GT':>10}{'A persona':>12}{'AX 公理':>12}{'B generic':>12}")
        for d in ['chars','n_sents','avg_sent_len','first_person','question_rate','所以_k','但是_k','suoyi_ratio','conf_words','conf_k','bushi_ershi_kchar','empty_talk','numbered','numbered_k','cut','cut_k']:
            print(f"{d:<18}{r['GT'][d]:>10}{r['A'][d]:>12}{r['AX'][d]:>12}{r['B'][d]:>12}")
        print(f"{'余弦 vs GT':<18}{'':>10}{r['cos_A_GT']:>12}{r['cos_AX_GT']:>12}{r['cos_B_GT']:>12}")
        print(f"{'drift 成璐度':<18}{'':>10}{r['drift_A']:>12.0f}{r['drift_AX']:>12.0f}{r['drift_B']:>12.0f}  (GT参照 {r['drift_GT']:.0f})")
    ca = sum(results[s]['cos_A_GT'] for s in results)/3
    cax = sum(results[s]['cos_AX_GT'] for s in results)/3
    cb = sum(results[s]['cos_B_GT'] for s in results)/3
    da = sum(results[s]['drift_A'] for s in results)/3
    dax = sum(results[s]['drift_AX'] for s in results)/3
    db = sum(results[s]['drift_B'] for s in results)/3
    print(f"\n===== 汇总(3场景均值) =====")
    print(f"余弦近似度: A persona = {ca:.3f} | AX 公理 = {cax:.3f} | B generic = {cb:.3f}")
    print(f"  Δ: A-B = {ca-cb:+.3f} | AX-B = {cax-cb:+.3f} | A-AX = {ca-cax:+.3f}")
    print(f"drift 成璐度: A = {da:.0f} | AX = {dax:.0f} | B = {db:.0f}  (Δ: A-B = {da-db:+.0f}, AX-B = {dax-db:+.0f})")

if __name__ == '__main__':
    main()
