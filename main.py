# tiny-chess-01: chess engine. MIT. Alpha-beta + TT + QS + PST + null-move.
import json,os,sys,urllib.request as U
E=os.environ.get("MAKEFUN_ENV_URL")or sys.exit()
P=lambda p,b:json.load(U.urlopen(U.Request(E+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})))
def B(f):
 b={};i=0
 for r in f.split('/'):
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
  if ep in d:d.pop(ep)
 if len(m)==5:d[m[2:4]]=m[4].upper()if p.isupper()else m[4]
 else:d[m[2:4]]=p
 if p.upper()=='K'and abs(ord(m[0])-ord(m[2]))>1:
  if m[2]=='g':d['f'+m[3]]=d.pop('h'+m[3])
  elif m[2]=='c':d['d'+m[3]]=d.pop('a'+m[3])
 return d
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':20000}
# Compact PST computed from formula
def ps(p,f,r):
 """Piece-square value from file(0-7), rank(0-7 from white)"""
 cf=3.5-abs(f-3.5);cr=3.5-abs(r-3.5);pu=p.upper()
 if pu=='P':return int(50-r*8+cf*3)if r<6else 5
 if pu=='N':return int((cf+cr)*6)
 if pu=='B':return int((cf+cr)*4)
 if pu=='R':return int(r*6-18)if r<6 else 5
 if pu=='Q':return int((cf+cr)*2)
 if pu=='K':return int((cf+cr)*3-5)if r<4 else 0
 return 0
def H(b):
 s=0;bc=0;wc=0
 for sq,p in b.items():
  v=V.get(p.lower(),0);s+=v if p.isupper()else-v
  f=ord(sq[0])-97;r=8-int(sq[1]);b1=ps(p,f,r)*(1if p.isupper()else-1);s+=b1
  if p.upper()=='B':
   if p.isupper():wc+=1
   else:bc+=1
 if wc>1:s+=20
 if bc>1:s-=20
 return s
def O(b,m):
 cap=b.get(m[2:4])
 if cap:return V.get(cap.lower(),0)*10-V.get(b[m[:2]].lower(),0)//10
 if len(m)==5:return V.get(m[4],0)*5
 return 0
TT={}
def Z(b):
 h=0
 for sq,p in sorted(b.items()):h^=hash((sq,p))&0x7FFFFFFF
 return h
def Q(b,mv,wt,a,be,d=0):
 s=H(b)*(1 if wt else-1)
 if s>=be:return be
 if d>5:return s
 if s>a:a=s
 for m in sorted(mv,key=lambda m:O(b,m),reverse=True):
  if O(b,m)==0:continue
  nb=M(b,m)
  sc=-Q(nb,[],not wt,-be,-a,d+1)
  if sc>be:return be
  if sc>a:a=sc
 return a
def S(b,mv,wt,d,a,be):
 if d==0:return Q(b,mv,wt,a,be)
 hh=Z(b)
 if hh in TT:
  td,tf,ts,tm=TT[hh]
  if td>=d:
   if tf=='e':return ts
   if tf=='l'and ts<=a:return ts
   if tf=='u'and ts>=be:return ts
 if d>2 and H(b)*(1 if wt else-1)>200:
  ns=-S(b,[],not wt,d-3,-be,-be+1)
  if ns>=be:return be
 best=-99999;bm=None;oflag='l'
 om=sorted(mv,key=lambda m:O(b,m),reverse=True)
 if hh in TT:
  tm=TT[hh][3]
  if tm in om:om.insert(0,om.pop(om.index(tm)))
 for m in om:
  nb=M(b,m)
  sc=-S(nb,[],not wt,d-1,-be,-a)
  if sc>best:best=sc;bm=m
  if sc>a:a=sc;oflag='e'
  if a>=be:oflag='u';break
 TT[hh]=(d,oflag,best,bm)
 return best
def C(g):
 b=B(g["fen"]);mv=g["legal_moves"];wt=g["colour"]=="white"
 if not mv:return None
 if len(mv)==1:return mv[0]
 best=mv[0];bs=-99999
 for d in range(1,7):
  a=-99999
  om=sorted(mv,key=lambda m:O(b,m),reverse=True)
  hh=Z(b)
  if hh in TT and TT[hh][3]in om:
   tm=TT[hh][3];om.insert(0,om.pop(om.index(tm)))
  for m in om:
   nb=M(b,m)
   sc=-S(nb,[],not wt,d-1,-99999,-a)
   if sc>bs:bs=sc;best=m
   if sc>a:a=sc
 return best
while 1:
 g=P("/game",{})
 if g.get("status")=="done":print(f"{g.get('wins',0)}W {g.get('draws',0)}D {g.get('losses',0)}L",file=sys.stderr);break
 while g.get("status")=="your_move":
  mv=C(g)
  if mv is None:g=P("/resign",{"game":g["game"]});break
  g=P("/move",{"game":g["game"],"move":mv})
  print(f"g{g['game']}:{g.get('outcome','?')}",file=sys.stderr)
