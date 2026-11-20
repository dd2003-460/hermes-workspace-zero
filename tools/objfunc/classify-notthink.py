#!/usr/bin/env python3
"""无思考模式批量分类：27b @ 8787, enable_thinking=False。
输入 d-messages-filtered.json (634条), 输出 classify-notthink-v1.json。
每批 40 条, 模型只输出 JSON 数组 [{i, type}]。"""
import json, urllib.request, time, sys

BASE = 'http://127.0.0.1:8787/v1/chat/completions'
kept = json.load(open('/Users/a1-6/Desktop/workspace/tools/objfunc/d-messages-filtered.json'))
print('total:', len(kept), flush=True)

TYPES = "反问/建议/纠正/真问/指令/状态/闲聊/噪音"
SYS = """你是消息分类器。对每条用户消息只判一个类型, 判据:
反问=断言式质疑(难道/不是应该/怎么不/为什么你), 表达"你做得不对"
建议=用户提出做法(我觉得/应该/最好/不如)
纠正=用户指出做错了(不对/错了/搞错/应该是)
真问=用户问知识/状态(吗/什么/怎么/如何, 非质疑)
指令=派活(执行/调研/你是X/请)
状态=问进度(跑完了吗/怎么样了)
闲聊=无任务内容
噪音=引用块/AI输出/系统消息/无信息
只输出JSON数组: [{"i":0,"type":"指令"}], i是行号, 不要解释。"""

def call(payload, timeout=300):
    req = urllib.request.Request(BASE, data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=timeout))
    return r['choices'][0]['message'].get('content',''), r.get('usage',{})

def classify_batch(msgs, start):
    lines = []
    for j, m in enumerate(msgs):
        c = m['content'].replace('\n', ' ')[:120]
        lines.append(f"{start+j}|{c}")
    payload = {"model": "qwen3.8-27b-mtp",
               "messages": [{"role":"system","content":SYS},{"role":"user","content":"\n".join(lines)}],
               "temperature": 0, "max_tokens": 2000,
               "chat_template_kwargs": {"enable_thinking": False}}
    for attempt in range(3):
        try:
            content, usage = call(payload)
            s = content.find('['); e = content.rfind(']')
            arr = json.loads(content[s:e+1])
            out = {}
            for item in arr:
                i = int(item['i'])
                if 0 <= i < len(msgs):
                    out[i] = item.get('type','噪音')
            return out, usage
        except Exception as ex:
            print(f'  batch@{start} attempt{attempt} fail: {str(ex)[:120]}', flush=True)
            time.sleep(5)
    return {}, {}

BATCH = 40
results = {}
t0 = time.time()
for start in range(0, len(kept), BATCH):
    msgs = kept[start:start+BATCH]
    out, usage = classify_batch(msgs, start)
    for i, t in out.items():
        results[start+i] = t
    miss = len(msgs) - len(out)
    print(f'batch {start}-{start+len(msgs)}: ok={len(out)} miss={miss} rt={usage.get("completion_tokens",0)} elapsed={int(time.time()-t0)}s', flush=True)
    if miss:
        # 缺失的标噪音
        for j in range(len(msgs)):
            if (start+j) not in results:
                results[start+j] = '噪音'

json.dump(results, open('/Users/a1-6/Desktop/workspace/tools/objfunc/classify-notthink-v1.json','w'), ensure_ascii=False)
from collections import Counter
c = Counter(results.values())
print('DONE', dict(c), 'total', len(results))
