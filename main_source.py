import json,os,sys,urllib.request as U,urllib.error as UE
E=os.environ.get("MAKEFUN_ENV_URL")or sys.exit()
def P(p,b):
 try:
  r=U.Request(E+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})
  return json.load(U.urlopen(r))
 except UE.HTTPError:sys.exit()
V={"p":100,"n":320,"b":330,"r":500,"q":900,"k":20000}
def S(s):return(ord(s[0])-97)+(int(s[1])-1)*8
def A(i):return chr(97+i%8)+str(i//8+1)
def B(f):
 b=[None]*64
 for i,r in enumerate(f.split()[0].split("/")):
  c=0
  for ch in r:
   if'0'<=ch<='8':c+=ord(ch)-48
   else:b[(7-i)*8+c]=ch;c+=1
 return b
DG=[-9,-7,7,9];OG=[-8,-1,1,8];KG=[-17,-15,-10,-6,6,10,15,17]

# Pseudo-legal moves for search
def L(b,w):
 m=[]
 for s in range(64):
  p=b[s]
  if p is None or(w^p.isupper()):continue
  pc=p.lower();f=s%8;r=s//8
  if pc=="p":
   pd=8 if w else-8;pr=7 if w else 0;sr=1 if w else 6
   t=s+pd
   if 0<=t<64 and b[t]is None:
    if r==(6 if w else 1):
     for pm in"qrbn":m.append((s,t,pm))
    else:m.append((s,t,None))
    if r==sr:
     t2=s+2*pd
     if b[t2]is None:m.append((s,t2,None))
   for df in[-1,1]:
    t=s+pd+df
    if 0<=t<64 and abs(t%8-f)==1 and b[t]and(b[t].isupper()!=w):
     if r==(6 if w else 1):
      for pm in"qrbn":m.append((s,t,pm))
     else:m.append((s,t,None))
  elif pc=="n":
   for d in KG:
    t=s+d
    if 0<=t<64 and abs(t%8-f)+abs(t//8-r)==3 and(b[t]is None or b[t].isupper()!=w):
     m.append((s,t,None))
  elif pc in"brq":
   dr=DG if pc=="b"else OG if pc=="r"else DG+OG
   for d in dr:
    t=s
    while 1:
     t+=d
     if not(0<=t<64):break
     if d in DG and abs(t%8-f)!=abs(t//8-r):break
     if d in OG and(t%8!=f and t//8!=r):break
     if b[t]:
      if b[t].isupper()!=w:m.append((s,t,None))
      break
     m.append((s,t,None))
  elif pc=="k":
   for d in DG+OG:
    t=s+d
    if 0<=t<64 and abs(t%8-f)<=1 and abs(t//8-r)<=1 and(b[t]is None or b[t].isupper()!=w):
     m.append((s,t,None))
   if w:
    if b[4]=="K"and b[7]=="R"and all(b[i]is None for i in[5,6]):m.append((4,6,None))
    if b[4]=="K"and b[0]=="R"and all(b[i]is None for i in[1,2,3]):m.append((4,2,None))
   else:
    if b[60]=="k"and b[63]=="r"and all(b[i]is None for i in[61,62]):m.append((60,62,None))
    if b[60]=="k"and b[56]=="r"and all(b[i]is None for i in[57,58,59]):m.append((60,58,None))
 return m

def M(b,m):
 nb=list(b);f=m[0];t=m[1];p=nb[f];nb[f]=None
 if p is None:return nb
 if p.lower()=="p"and f%8!=t%8 and nb[t]is None:nb[t+(-8 if p.isupper()else 8)]=None
 if m[2]:nb[t]=m[2].upper()if p.isupper()else m[2]
 else:nb[t]=p
 if p.upper()=="K"and abs(f%8-t%8)>1:
  if t%8==6:nb[t-1]=nb[t+1];nb[t+1]=None
  elif t%8==2:nb[t+1]=nb[t-2];nb[t-2]=None
 return nb

# Full PST tables (white pov, a1..h8, centipawns)
PP=[0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0]
PN=[-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50]
PB=[-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20]
PR=[0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0]
PQ=[-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20]
PK=[-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20]
PT={"p":PP,"n":PN,"b":PB,"r":PR,"q":PQ,"k":PK}

def H(b,w):
 s=0
 for i in range(64):
  p=b[i]
  if p is None:continue
  pc=p.lower();v=V[pc]
  if p.isupper():
   s+=v+PT[pc][i]
  else:
   mi=(7-(i//8))*8+(i%8)
   s-=v+PT[pc][mi]
 return s*(1 if w else-1)

K1=[None]*32;K2=[None]*32

def R(b,m,d):
 f=m[0];t=m[1]
 if b[t]:return 20000+V[b[t].lower()]*10-V[b[f].lower()]
 if m[2]:return 19000+V[m[2]]
 if m==K1[d]:return 18000
 if m==K2[d]:return 17000
 return 0

def Q(b,w,a,be,d=0):
 sc=H(b,w)
 if sc>=be:return be
 if d>3:return sc
 if sc>a:a=sc
 caps=[m for m in L(b,w)if b[m[1]]is not None]
 caps.sort(key=lambda m:R(b,m,0),reverse=1)
 for m in caps:
  nb=M(b,m)
  v=-Q(nb,not w,-be,-a,d+1)
  if v>=be:return be
  if v>a:a=v
 return a

def N(b,w,d,a,be):
 if d==0:return Q(b,w,a,be)
 # Null-move pruning: skip a move, if still good, prune
 if d>2 and be<9000:
  nb=list(b);sc=-N(nb,not w,d-3,-be,-be+1)
  if sc>=be:return be
 moves=L(b,w)
 if not moves:return-19900+(64-sum(1 for x in b if x))
 moves.sort(key=lambda m:R(b,m,d),reverse=1)
 best=-99999
 for mv in moves:
  nb=M(b,mv)
  v=-N(nb,not w,d-1,-be,-a)
  if v>=be:
   if b[mv[1]]is None and not mv[2]and mv!=K1[d]:K2[d]=K1[d];K1[d]=mv
   return be
  if v>a:a=v;best=v
 return a if best==-99999 else best

def C(g):
 fen=g["fen"];legal=g["legal_moves"];wt=g["colour"]=="white"
 if not legal:return None
 if len(legal)==1:return legal[0]
 b=B(fen)
 def rk(m):
  f=S(m[:2]);t=S(m[2:4])
  if b[t]:return 20000+V[b[t].lower()]*10
  if len(m)==5:return 19000+V[m[4]]
  return 0
 sl=sorted(legal,key=rk,reverse=1)
 bm=sl[0];bs=-99999;pb=None
 for dp in range(1,7):
  aw=25*dp
  al=bs-aw if dp>1 else-99999
  be=bs+aw if dp>1 else 99999
  if pb and pb in sl:sl.remove(pb);sl.insert(0,pb)
  for mv in sl:
   f=S(mv[:2]);t=S(mv[2:4]);pm=mv[4]if len(mv)==5 else None
   nb=M(b,(f,t,pm))
   v=-N(nb,not wt,dp-1,-be,-al)
   if v>al:
    if v>=be:v=-N(nb,not wt,dp-1,-99999,99999)
    if v>bs:bs=v;bm=mv
    al=v
  pb=bm
  if bs>9000:break
 return bm

while 1:
 g=P("/game",{})
 if g.get("status")=="done":print(f"{g.get('wins',0)}W {g.get('draws',0)}D {g.get('losses',0)}L",file=sys.stderr);break
 while g.get("status")=="your_move":
  mv=C(g)
  if mv is None:g=P("/resign",{"game":g["game"]});break
  g=P("/move",{"game":g["game"],"move":mv})
  print(f"g{g['game']}:{g.get('outcome','?')}",file=sys.stderr)