import json,re,glob,collections
cands=set(open('cands.txt').read().split())
TERM=re.compile(r'(?:\b(?:avg|sum|min|max|count|p\d+|pct\d+):)?([A-Za-z_][\w\.]*)\{([^}]*)\}(?:\s*by\s*\{([^}]*)\})?')
def strings(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,str) and k in('q','query','numerator','denominator'): yield v
            else: yield from strings(v)
    elif isinstance(o,list):
        for x in o: yield from strings(x)
use=collections.defaultdict(lambda: collections.defaultdict(set))  # metric -> tagkey -> set(assets)
touch=collections.defaultdict(set) # metric -> assets
def parse(q,asset,tvmap):
    for m,scope,by in TERM.findall(q):
        if m not in cands: continue
        touch[m].add(asset)
        keys=set()
        for tok in re.split(r'[,\s]+|\bAND\b|\bOR\b',scope):
            tok=tok.strip().lstrip('!(').rstrip(')')
            if not tok or tok=='*': continue
            if tok.startswith('$'):
                v=tok[1:].split('.')[0]
                keys.add(tvmap.get(v,v)+'(tv)')
            elif ':' in tok: keys.add(tok.split(':',1)[0])
        for g in (by or '').split(','):
            g=g.strip()
            if g: keys.add(g+'(by)')
        for k in keys: use[m][k].add(asset)
for f in glob.glob('dash/*.json'):
    d=json.load(open(f)); t=d.get('title','?')
    tv={x['name']:(x.get('prefix') or x['name']) for x in (d.get('template_variables') or [])}
    for q in strings(d.get('widgets') or []): parse(q,'dash:'+t,tv)
for l in open('monitors.jsonl'):
    m=json.loads(l); parse(m['q'] or '','mon:%s %s'%(m['id'],m['name']),{})
for s in json.load(open('slo.json')).get('data') or []:
    for q in strings(s.get('query') or {}): parse(q,'slo:'+s.get('name',''),{})
INFRA={'pod_name','hostname','host','kube_pod_name','container_id','container_name'}
json.dump({m:{k:sorted(v) for k,v in ks.items()} for m,ks in use.items()},open('use.json','w'),indent=1)
json.dump({m:sorted(v) for m,v in touch.items()},open('touch.json','w'),indent=1)
unused=[m for m in cands if m not in touch]
risky={m:{k:v for k,v in use[m].items() if k.split('(')[0] in INFRA} for m in touch}
risky={m:v for m,v in risky.items() if v}
print('candidates:',len(cands))
print('  not referenced by ANY monitor/dashboard/SLO:',len(unused))
print('  referenced:',len(touch))
print('  referenced AND grouped/filtered by an infra tag (pod_name/hostname/host/...):',len(risky))
for m,v in sorted(risky.items()):
    for k,a in v.items(): print('   !!',m,'|',k,'|',sorted(a)[:4])
