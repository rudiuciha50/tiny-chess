# chess engine. MIT. ab+TT+QS. tiny-chess-01.
import json,os,sys,urllib.request as U
E=os.environ.get("MAKEFUN_ENV_URL")or sys.exit()
P=lambda p,b:json.load(U.urlopen(U.Request(E+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})))
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
 if p.lower()=='p'and m[0]!=m[2]and m[2:4]not in b:d.pop(m[2]+('5'if p.isupper()else'4'),0)
 if len(m)==5:d[m[2:4]]=m[4].upper()if p.isupper()else m[4]
 else:d[m[2:4]]=p
 if p.upper()=='K'and abs(ord(m[0])-ord(m[2]))>1:
  if m[2]=='g':d['f'+m[3]]=d.pop('h'+m[3])
  elif m[2]=='c':d['d'+m[3]]=d.pop('a'+m[3])
 return d
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':20000}
D=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
W=[(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]
def G(b,w):
 m=[]
 for s,p in b.items():
  if p.isupper()!=w:continue
  f=ord(s[0])-97;r=int(s[1])
  if p.lower()=='p':
   d=1if w else-1;v=r+d;t=chr(97+f)+str(v)
   if 1<=v<=8and t not in b:m.append(s+t)
   for x in[-1,1]:
    u=f+x;t=chr(97+u)+str(v)
    if 0<=u<8and 1<=v<=8and t in b and b[t].isupper()!=w:m.append(s+t)
  elif p.lower()=='n':
   for x,y in W:
    u=f+x;v=r+y;t=chr(97+u)+str(v)
    if 0<=u<8and 1<=v<=8and(not t in b or b[t].isupper()!=w):m.append(s+t)
  elif p.lower()in'bqr':
   for x,y in D:
    q=p.lower()=='q'or(p.lower()=='b'and x*y)or(p.lower()=='r'and not x*y)
    if not q:continue
    u=f+x;v=r+y
    while 0<=u<8and 1<=v<=8:
     t=chr(97+u)+str(v)
     if t in b:
      if b[t].isupper()!=w:m.append(s+t)
      break
     m.append(s+t);u+=x;v+=y
  elif p.lower()=='k':
   for x,y in D:
    u=f+x;v=r+y;t=chr(97+u)+str(v)
    if 0<=u<8and 1<=v<=8and(not t in b or b[t].isupper()!=w):m.append(s+t)
 return m
def H(b):
 s=0
 for p in b.values():s+=V[p.lower()]*(1if p.isupper()else-1)
 return s
def O(b,m):
 c=b.get(m[2:4])
 return V[c.lower()]*10-V[b[m[:2]].lower()]//10 if c else 0
T={}
def Z(b):
 h=0
 for s,p in sorted(b.items()):h^=hash((s,p))&0x7FFFFFFF
 return h
def Q(b,w,a,be,d=0):
 s=H(b)*(1if w else-1)
 if s>=be:return be
 if d>4:return s
 if s>a:a=s
 for m in sorted([x for x in G(b,w)if x[2:4]in b],key=lambda m:V.get(b[m[2:4]].lower(),0),reverse=True):
  sc=-Q(M(b,m),not w,-be,-a,d+1)
  if sc>be:return be
  if sc>a:a=sc
 return a
def S(b,w,d,a,be):
 if d==0:return Q(b,w,a,be)
 h=Z(b)
 if h in T:
  t=T[h]
  if t[0]>=d and(t[1]=='e'or(t[1]=='l'and t[2]<=a)or(t[1]=='u'and t[2]>=be)):return t[2]
 mv=G(b,w)
 if not mv:return-99999
 if d>2and H(b)*(1if w else-1)>200:
  if-S(b,not w,d-3,-be,-be+1)>=be:return be
 bm=sorted(mv,key=lambda m:O(b,m),reverse=True)
 if h in T and T.get(h,(0,'',0,0))[3]in bm:bm.insert(0,bm.pop(bm.index(T[h][3])))
 bs=-99999;bf=bm[0];fl='l'
 for m in bm:
  sc=-S(M(b,m),not w,d-1,-be,-a)
  if sc>bs:bs=sc;bf=m
  if sc>a:a=sc;fl='e'
  if a>=be:fl='u';break
 T[h]=(d,fl,bs,bf)
 return bs
def C(g):
 b=B(g["fen"]);w=g["colour"]=="white";mv=g["legal_moves"]
 if not mv:return None
 if len(mv)==1:return mv[0]
 bt=mv[0];bs=-99999
 for d in range(1,6):
  a=-99999
  om=sorted(mv,key=lambda m:O(b,m),reverse=True)
  h=Z(b)
  if h in T and T.get(h,(0,'',0,0))[3]in om:om.insert(0,om.pop(om.index(T[h][3])))
  for m in om:
   sc=-S(M(b,m),not w,d-1,-99999,-a)
   if sc>bs:bs=sc;bt=m
   if sc>a:a=sc
 return bt
while 1:
 g=P("/game",{})
 if g.get("status")=="done":print(f"{g.get('wins',0)}W {g.get('draws',0)}D {g.get('losses',0)}L",file=sys.stderr);break
 while g.get("status")=="your_move":
  mv=C(g)
  if mv is None:g=P("/resign",{"game":g["game"]});break
  g=P("/move",{"game":g["game"],"move":mv})
  print(f"g{g['game']}:{g.get('outcome','?')}",file=sys.stderr)
