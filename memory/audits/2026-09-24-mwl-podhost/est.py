import json,os,subprocess,urllib.parse,urllib.request,collections,concurrent.futures as cf
H="https://api."+os.environ['DATADOG_SITE']
HD={'DD-API-KEY':os.environ['DD_API_KEY'],'DD-APPLICATION-KEY':os.environ['DD_APP_KEY']}
def get(p,q=None):
    u=H+p+('?'+urllib.parse.urlencode(q) if q else '')
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=HD),timeout=60))
use=json.load(open('use.json'))
RISKY={'superset.gunicorn.requests','superset.gunicorn.worker.concurrent_reqs','superset.gunicorn.worker.current_workers','superset.reports.execute'}
vol={}
for l in open('/tmp/vols.txt'):
    p=l.strip().split('|')
    if len(p)==3 and p[0].isdigit(): vol[p[2]]=int(p[0])
cands=[c for c in open('cands.txt').read().split() if c not in RISKY]
cands.sort(key=lambda c:-vol.get(c,0))
MIN={'pod_name','hostname'}
NODE=MIN|{'host','aws','kube_node','name','karpenter.sh/nodeclaim','instance-id','availability-zone','zone','instance-type','image','kernel','vcpu','security-group','iam_profile','created-by','on-host-maintenance','automatic-restart','goog-gke-node','goog-k8s-node-pool-name','goog-gke-node-pool-provisioning-model'}
def one(m):
    tags=get(f'/api/v2/metrics/{m}/all-tags')['data']['attributes']['tags']
    keys=sorted({t.split(':',1)[0] for t in tags})
    used={k.split('(')[0] for k in use.get(m,{})}
    bad=used & NODE
    def est(excl):
        g=','.join(k for k in keys if k not in excl)
        return get(f'/api/v2/metrics/{m}/estimate',{'filter[groups]':g})['data']['attributes']['estimated_output_series']
    return m,vol.get(m,0),est(MIN),est(NODE),sorted(bad),keys
out=[]
with cf.ThreadPoolExecutor(8) as ex:
    for r in ex.map(one,cands[:25]): out.append(r)
json.dump(out,open('est_sample.json','w'))
T=[sum(x[i] for x in out) for i in (1,2,3)]
print(f"{'metric':52s} {'now':>6} {'-pod/host':>9} {'-node':>6}  conflicts")
for m,v,a,b,bad,_ in out: print(f'{m[:52]:52s} {v:6d} {a:9d} {b:6d}  ', bad or '')
print(f"{'TOTAL (sample 25)':52s} {T[0]:6d} {T[1]:9d} {T[2]:6d}")
print(f'reduction: drop pod/host only = {100*(1-T[1]/T[0]):.0f}%   drop per-node set = {100*(1-T[2]/T[0]):.0f}%')
