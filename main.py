# chess engine. MIT. tiny-chess-01. v2: PST eval + tactical search
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
  ep=m[2]+('5'if p.isupper()else'4');d.pop(ep,0)
 if len(m)==5:d[m[2:4]]=m[4].upper()if p.isupper()else m[4]
 else:d[m[2:4]]=p
 if p.upper()=='K'and abs(ord(m[0])-ord(m[2]))>1:
  if m[2]=='g':d['f'+m[3]]=d.pop('h'+m[3])
  elif m[2]=='c':d['d'+m[3]]=d.pop('a'+m[3])
 return d
# Positional eval: center control + pawn structure
def H(b):
 s=0
 for sq,p in b.items():
  f=ord(sq[0])-97;r=int(sq[1])-1;v=V[p.lower()]
  # Center distance bonus (0 at edges, 7 at e4/d4)
  c=max(0,int(7-abs(f-3.5)-abs(r-3.5)))
  # Pawn advancement
  a=0
  if p.lower()=='p':a=(r-1)*3 if p.isupper()else(6-r)*3
  s+=(v+c*2+a)*(1 if p.isupper()else-1)
 return s
def R(b,m):
 """Move ordering: captures by MVV-LVA, non-captures by center bonus."""
 c=b.get(m[2:4])
 if c:return V[c.lower()]*10-V[b[m[:2]].lower()]
 sq=m[2:4];f=ord(sq[0])-97;r=int(sq[1])-1
 return max(0,int(7-abs(f-3.5)-abs(r-3.5)))
# Capture generator for quiescence search
def G(b,w):
 """Generate all pseudo-legal captures for side w."""
 m=[];D=[-9,-7,7,9];O=[-8,-1,1,8];N=[-17,-15,-10,-6,6,10,15,17]
 for s,p in list(b.items()):
  if(w and p.isupper())or(not w and p.islower()):
   pc=p.lower();f=ord(s[0])-97;r=int(s[1])-1;i=r*8+f
   T=lambda t:chr(97+t%8)+str(t//8+1)
   E=lambda t:t in b and(b[t].isupper()!=w)
   if pc=='n':
    for d in N:
     t=i+d
     if 0<=t<64 and abs(t%8-f)+abs(t//8-r)==3:
      ts=T(t)
      if E(ts):m.append(s+ts)
   elif pc=='k':
    for d in D+O:
     t=i+d
     if 0<=t<64 and abs(t%8-f)<=1 and abs(t//8-r)<=1:
      ts=T(t)
      if E(ts):m.append(s+ts)
   else:
    dr=[]
    if pc in'bq':dr+=D
    if pc in'rq':dr+=O
    for d in dr:
     t=i
     while 1:
      t+=d
      if not(0<=t<64):break
      if d in D and abs(t%8-i%8)!=abs(t//8-i%8):break
      if d in O and t%8!=i%8 and t//8!=i%8:break
      ts=T(t)
      if ts in b:
       if E(ts):m.append(s+ts)
       break
    if pc=='p':
     pd=8 if w else-8
     for df in[-1,1]:
      t=i+pd+df
      if 0<=t<64 and abs(t%8-f)==1:
       ts=T(t)
       if E(ts):m.append(s+ts)
 return m
def Q(b,w,a,be,d=0):
 """Quiescence: extend captures only, using self-generated moves."""
 s=H(b)*(1 if w else-1)
 if s>=be:return be
 if d>3:return s
 if s>a:a=s
 caps=sorted(G(b,w),key=lambda m:R(b,m),reverse=True)
 for m in caps:
  nb=M(b,m)
  sc=-Q(nb,not w,-be,-a,d+1)
  if sc>=be:return be
  if sc>a:a=sc
 return a
def C(g):
 b=B(g["fen"]);mv=g["legal_moves"];wt=g["colour"]=="white"
 if not mv:return None
 if len(mv)==1:return mv[0]
 best=mv[0];bs=-99999
 mv.sort(key=lambda m:R(b,m),reverse=True)
 for m in mv:
  nb=M(b,m)
  sc=-Q(nb,not wt,-99999,99999)
  if sc>bs:bs=sc;best=m
 return best
while 1:
 g=P("/game",{})
 if g.get("status")=="done":print(f"{g.get('wins',0)}W {g.get('draws',0)}D {g.get('losses',0)}L",file=sys.stderr);break
 while g.get("status")=="your_move":
  mv=C(g)
  if mv is None:g=P("/resign",{"game":g["game"]});break
  g=P("/move",{"game":g["game"],"move":mv})
  print(f"g{g['game']}:{g.get('outcome','?')}",file=sys.stderr)