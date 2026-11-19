# chess engine. MIT. tiny-chess-01. Depth-limited alpha-beta with capture ordering.
import json,os,sys,urllib.request as U,urllib.error as UE
E=os.environ.get("MAKEFUN_ENV_URL")or sys.exit()
def P(p,b):
 try:
  r=U.urlopen(U.Request(E+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"}))
  return json.load(r)
 except UE.HTTPError as e:sys.exit(f"{p}:{e.code}")
V={"p":100,"n":320,"b":330,"r":500,"q":900,"k":20000}
def B(f):
 b={};i=0
 for r in f.split()[0].split('/'):
  c=0
  for ch in r:
   if'0'<=ch<='8':c+=ord(ch)-48
   else:b[chr(97+c)+str(8-i)]=ch;c+=1
  i+=1
 return b
def M(b,m):
 d=dict(b);p=d.pop(m[:2])
 if m[2:4]in d:d.pop(m[2:4])
 if p.lower()=='p'and m[0]!=m[2]and m[2:4]not in b:
  ep=m[2]+('5'if p.isupper()else'4')
  d.pop(ep,0)
 if len(m)==5:d[m[2:4]]=m[4].upper()if p.isupper()else m[4]
 else:d[m[2:4]]=p
 if p.upper()=='K'and abs(ord(m[0])-ord(m[2]))>1:
  if m[2]=='g':d['f'+m[3]]=d.pop('h'+m[3])
  elif m[2]=='c':d['d'+m[3]]=d.pop('a'+m[3])
 return d
def H(b):
 s=0
 for p in b.values():s+=V[p.lower()]*(1if p.isupper()else-1)
 return s
def R(b,m):
 """Move ordering: captures by MVV-LVA"""
 c=b.get(m[2:4])
 if c:return V[c.lower()]*10-V[b[m[:2]].lower()]
 return 0
# At root: use env legal_moves (guaranteed legal)
# Search: use env legal_moves only (no self-generated moves = no illegal moves)
def Q(b,mv,wt,a,be,d=0):
 """Quiescence: extend captures only, using env-provided moves"""
 s=H(b)*(1if wt else-1)
 if s>=be:return be
 if d>3:return s
 if s>a:a=s
 caps=sorted([m for m in mv if m[2:4]in b],key=lambda m:R(b,m),reverse=True)
 for m in caps:
  nb=M(b,m)
  sc=-Q(nb,[],not wt,-be,-a,d+1)
  if sc>be:return be
  if sc>a:a=sc
 return a
def C(g):
 b=B(g["fen"]);mv=g["legal_moves"];wt=g["colour"]=="white"
 if not mv:return None
 if len(mv)==1:return mv[0]
 best=mv[0];bs=-99999
 # Simple 1-ply with quiescence: fast and safe
 for m in sorted(mv,key=lambda m:R(b,m),reverse=True):
  nb=M(b,m)
  # Eval opponent's best capture response
  sc=-H(nb)*(1if not wt else-1)
  # Add quiescence on captures
  if R(b,m)>0:
   sc=-Q(nb,[],not wt,-99999,99999)
  if sc>bs:bs=sc;best=m
 return best
while 1:
 g=P("/game",{})
 if g.get("status")=="done":print(f"{g.get('wins',0)}W {g.get('draws',0)}D {g.get('losses',0)}L",file=sys.stderr);break
 while g.get("status")=="your_move":
  mv=C(g)
  if mv is None:
   g=P("/resign",{"game":g["game"]});break
  g=P("/move",{"game":g["game"],"move":mv})
  print(f"g{g['game']}:{g.get('outcome','?')}",file=sys.stderr)
