import re,sys,json
p='revival-frontier-research.md'
L=open(p,encoding='utf-8').read().split('\n')
# split by top-level sections
secs={}; cur=None
for i,l in enumerate(L):
    if l.startswith('## '):
        cur=l[3:].strip(); secs[cur]=[]
    if cur: secs[cur].append((i+1,l))
req=['Q1 记忆/人格持久化','Q2 思维操作可执行编码','Q3 外部锚点网络','横向结论（≤10 行：三方向的最小系统形态）']
res={'checks':{}, 'counts':{}}
def ok(k,v,detail=''):
    res['checks'][k]={'pass':bool(v),'detail':detail}
for r in req: ok('section:'+r, r in secs)
ok('appendix present', any(k.startswith('附录') for k in secs) or '## 附录（过程论证，不计入核心篇幅）' in secs)
# the '---' separator and appendix: appendix header is '## 附录...'
for d in ['Q1 记忆/人格持久化','Q2 思维操作可执行编码','Q3 外部锚点网络']:
    body=secs[d]
    text='\n'.join(l for _,l in body)
    # core length: lines in section excluding trailing blank/--- lines
    core=[l for _,l in body if l.strip() not in ('','---')]
    ok(f'{d}: core lines <=50', len(core)<=50, f'{len(core)} non-empty lines')
    ok(f'{d}: has SOTA heading', '### SOTA 方法' in text)
    ok(f'{d}: has 推荐组合 heading', '### 推荐组合（≤5 行）' in text)
    # table header columns
    hdr=[l for l in body if l[1].startswith('| 方法')]
    cols=[c.strip() for c in hdr[0][1].strip('|').split('|')] if hdr else []
    ok(f'{d}: table header', cols==['方法','链接','一句话原理','对我们适配度','conf'], str(cols))
    rows=[l for _,l in body if l.startswith('| ') and not l.startswith('| 方法') and not l.startswith('|---') and not l.startswith('|------')]
    rows=[r for r in rows if r.count('|')>=6]
    # recommendation list lines
    rec_start=[i for i,(n,l) in enumerate(body) if l.startswith('### 推荐组合')][0]
    rec=[l for _,l in body[rec_start+1:] if re.match(r'^\d+\. ',l)]
    ok(f'{d}: 推荐组合 <=5 lines', len(rec)<=5 and len(rec)>0, f'{len(rec)} lines')
    urls=set(re.findall(r'https?://[^\s\)；;）（()]+', text))
    ok(f'{d}: conf present in every row', all(re.search(r'\| 0\.\d+ \|$', r) or 'conf' in r for r in rows), '')
    res['counts'][d]={'sota_rows':len(rows),'recommend_items':len(rec),'conclusions_total':len(rows)+len(rec),'distinct_urls':len(urls),'urls':sorted(urls)}
hz=secs['横向结论（≤10 行：三方向的最小系统形态）']
hz_items=[l for _,l in hz if re.match(r'^\d+\. ',l)]
ok('横向结论 <=10 lines', len(hz_items)<=10, f'{len(hz_items)} items')
print(json.dumps(res,ensure_ascii=False,indent=1))
