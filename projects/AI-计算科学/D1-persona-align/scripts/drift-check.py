#!/usr/bin/env python3
# origin: ai · 成璐 voice 漂移检测（persona-align L7 重锚的量化工具）
# 基线数字来自 author-voice-mining/outputs/voice_features.md（271 条 / 26.4 万字实测）。
# 用途：python3 drift-check.py <text_file>   （或 cat file | python3 drift-check.py -）
# 无第三方依赖。输出 0-100 分 + 每项指标 vs 目标 + 漂移信号词。
import sys, re

# --- 空话/漂移信号词（出现即扣分，author-voice 反面清单 + soul-md 漂移信号） ---
EMPTY_TALK = ["值得注意的是","综上所述","显而易见","毋庸置疑","不难发现","由此可见",
              "总而言之","需要指出","一方面","另一方面","首先","其次","最后"]
# 三段套式
TRIPLE = ("首先" in ("" ) )  # placeholder, real check below

def split_sentences(text):
    # 中文句读 + 英文句点；保留分隔符用于问号率
    parts = re.split(r'([。！？!?；;])', text)
    sents = []
    i = 0
    while i < len(parts):
        chunk = parts[i]
        if i+1 < len(parts) and parts[i+1] in '。！？!?；;':
            sents.append(chunk + parts[i+1]); i += 2
        else:
            if chunk.strip(): sents.append(chunk)
            i += 1
    return [s for s in sents if s.strip()]

def count_chars(s):
    # 只数可见字符（去掉空白）
    return len(re.sub(r'\s','',s))

def analyze(text):
    sents = split_sentences(text)
    n = len(sents)
    res = {}
    # 平均句长（字）
    lens = [count_chars(s) for s in sents]
    res['avg_sent_len'] = round(sum(lens)/n, 1) if n else 0
    # 第一人称率（含「我」的句子占比）
    res['first_person'] = round(sum(1 for s in sents if '我' in s)/n, 3) if n else 0
    # 问号率
    q = sum(1 for s in sents if s.rstrip().endswith(('？','?')))
    res['question_rate'] = round(q/n, 3) if n else 0
    # 连接词
    res['所以'] = text.count('所以'); res['但是'] = text.count('但是')
    res['其实'] = text.count('其实')
    # 置信度词
    res['可能'] = text.count('可能'); res['应该'] = text.count('应该')
    res['大概率'] = text.count('大概率'); res['我猜'] = text.count('我猜')
    # "不是…而是"
    res['不是而是'] = len(re.findall(r'不是[^。！？\n]{0,30}而是', text))
    # 空话命中
    hits = {w: text.count(w) for w in EMPTY_TALK if w in text}
    res['empty_talk'] = hits
    res['empty_talk_total'] = sum(hits.values())
    # 千字字数（用于"不是而是"密度）
    total_chars = count_chars(text)
    res['total_chars'] = total_chars
    res['不是而是_per_kchar'] = round(res['不是而是']/(total_chars/1000), 3) if total_chars else 0
    return res, n

def score(res):
    s = 100.0
    flags = []
    al = res['avg_sent_len']
    if al > 70: s -= 25; flags.append(f"句长 {al} > 70（AI 长文腔）")
    elif al > 55: s -= 10; flags.append(f"句长 {al} > 55（偏 AI）")
    elif al < 20: flags.append(f"句长 {al} < 20（过碎，不像成璐陈述）")
    if res['empty_talk_total'] > 0:
        s -= 15*res['empty_talk_total']
        flags.append(f"空话/信号词 {res['empty_talk_total']} 处: {res['empty_talk']}")
    if res['但是'] >= res['所以']:
        s -= 10; flags.append(f"但是({res['但是']}) >= 所以({res['所以']})，连接词倒挂")
    if res['first_person'] < 0.2:
        s -= 10; flags.append(f"第一人称率 {res['first_person']} < 0.2（缺『我要/我觉得』）")
    if res['可能']+res['应该'] == 0:
        s -= 5; flags.append("无置信度词（可能/应该），像在断言而非成璐式判断")
    if res['不是而是_per_kchar'] > 0.7:
        s -= 5; flags.append(f"『不是…而是』密度 {res['不是而是_per_kchar']}/千字 偏高（目标 ~0.36）")
    # 三段套式（首先/其次/最后 同时出现）
    if all(w in str(res.get('empty_talk','')) for w in []):
        pass
    return max(0.0, s), flags

def main():
    if len(sys.argv) < 2:
        print("usage: drift-check.py <text_file|->", file=sys.stderr); sys.exit(2)
    path = sys.argv[1]
    text = sys.stdin.read() if path == '-' else open(path, encoding='utf-8').read()
    res, n = analyze(text)
    sc, flags = score(res)
    print(f"== 成璐 voice 漂移检测 ==")
    print(f"句子数 {n} · 总字数 {res['total_chars']}")
    print(f"平均句长 {res['avg_sent_len']}（目标 ~39，>55 警）")
    print(f"第一人称率 {res['first_person']}（目标 ~0.675，>=0.2 合格）")
    print(f"问号率 {res['question_rate']}（基线 0.413）")
    print(f"所以 {res['所以']} / 但是 {res['但是']}（应 所以 >> 但是）")
    print(f"置信度词 可能{res['可能']} 应该{res['应该']} 大概率{res['大概率']} 我猜{res['我猜']}")
    print(f"『不是…而是』 {res['不是而是']} 次 · {res['不是而是_per_kchar']}/千字（目标 ~0.36）")
    print(f"空话/信号词 {res['empty_talk_total']} 处 {res['empty_talk'] if res['empty_talk'] else ''}")
    print(f"\n>> 成璐度得分: {sc:.0f}/100")
    if flags:
        print("漂移信号:")
        for f in flags: print(f"  - {f}")
    else:
        print("无漂移信号。")

if __name__ == '__main__':
    main()
