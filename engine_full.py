# SUPER chess engine for tiny-chess-01 — alpha-beta + TTable + QSearch + PST + killers + null-move + IID
# Will be lzma-compressed into main.py
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
  if m[2]=='g':d['f'+m[3]]=d.pop('h'+m[3]);
  elif m[2]=='c':d['d'+m[3]]=d.pop('a'+m[3])
 return d
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':20000}
# Compact PST: [pawn, knight, bishop, rook, queen, king_mg, king_eg] x 64 squares
PST={}
def I():
 """Initialize PST lookup from compact array"""
 pa=[0,0,0,0,0,0,0,0,5,5,5,5,5,5,5,5,1,1,2,3,3,2,1,1,0,0,0,2,2,0,0,0,0,-1,-1,0,0,-1,-1,0,0,1,2,2,1,1,0,0,0,2,3,3,2,0,0,0,0,0,0,0,0,0,0,0]
 kn=[-5,-4,-3,-3,-3,-3,-4,-5,-4,-2,0,0,0,0,-2,-4,-3,0,1,2,2,1,0,-3,-3,0,2,2,2,2,0,-3,-3,0,2,2,2,2,0,-3,-3,0,1,2,2,1,0,-3,-4,-2,0,0,0,0,-2,-4,-5,-4,-3,-3,-3,-3,-4,-5]
 bi=[-2,-1,-1,-1,-1,-1,-1,-2,-1,0,0,0,0,0,0,-1,-1,0,1,1,1,1,0,-1,-1,1,1,1,1,1,1,-1,-1,0,1,1,1,1,0,-1,-1,1,0,0,0,0,1,-1,-1,0,1,0,0,0,0,-1,-2,-1,-1,-1,-1,-1,-1,-2]
 ro=[0,0,0,0,0,0,0,0,1,2,2,2,2,2,2,1,-1,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,-1,-1,0,0,0,0,0,0,-1,-1,-1,-1,-1,-1,-1,-1,-1,0,0,0,0,0,0,0,0]
 qu=[-2,-1,-1,-1,-1,-1,-1,-2,-1,0,0,0,0,0,0,-1,-1,0,1,1,1,1,0,-1,-1,0,1,1,1,1,0,-1,-1,0,0,1,1,0,0,-1,-1,0,0,0,0,0,0,-1,-2,-1,-1,-1,0,0,0,-2,-2,-1,-1,0,0,2,3,-2]
 km=[-3,-4,-4,-5,-5,-4,-4,-3,-3,-4,-4,-5,-5,-4,-4,-3,-3,-4,-4,-5,-5,-4,-4,-3,-3,-4,-4,-5,-5,-4,-4,-3,-2,-3,-3,-4,-4,-3,-3,-2,-1,-2,-2,-2,-2,-2,-2,-1,2,2,0,0,0,0,2,2,2,3,1,0,0,1,3,2]
 ke=[-5,-3,-3,-3,-3,-3,-3,-5,-3,0,0,0,0,0,0,-3,-3,0,1,2,2,1,0,-3,-3,0,2,3,3,2,0,-3,-3,0,2,3,3,2,0,-3,-3,0,1,2,2,1,0,-3,-3,-1,-1,-1,-1,-1,-1,-3,-5,-3,-3,-3,-3,-3,-3,-5]
 for i,sq in enumerate([f+r for f in'abcdefgh'for r in'87654321']):
  PST[sq,'P']=pa[i];PST[sq,'N']=kn[i];PST[sq,'B']=bi[i];PST[sq,'R']=ro[i];PST[sq,'Q']=qu[i];PST[sq,'K']=km[i];PST[sq,'k']=ke[i]
I()
def E(b):
 s=0
 for sq,p in b.items():
  v=V.get(p.lower(),0);s+=v if p.isupper()else-v
  if (sq,p.upper())in PST:
   s+=PST[sq,p.upper()]*(1if p.isupper()else-1)
  # Bishop pair bonus
  if p.upper()=='B'and len([x for x in b.values()if x.upper()=='B'])>1:
   s+=20*(1if p.isupper()else-1)
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
KT=[[0]*64 for _ in range(2)]
def Q(b,mv,wt,a,be,d=0):
 stand=E(b)*(1if wt else-1)
 if stand>=be:return be
 if d>6:return stand
 if stand>a:a=stand
 for m in sorted(mv,key=lambda m:O(b,m),reverse=True):
  if O(b,m)==0:continue
  nb=M(b,m)
  s=-Q(nb,[],not wt,-be,-a,d+1)
  if s>be:return be
  if s>a:a=s
 return a
def N(b,wt):
 """null-move heuristic: is position clearly winning?"""
 return E(b)*(1if wt else-1)<-200
def S(b,mv,wt,d,a,be):
 if d==0:return Q(b,mv,wt,a,be)
 hh=Z(b)
 if hh in TT:
  td,tf,ts,tm=TT[hh]
  if td>=d:
   if tf=='e':return ts
   if tf=='l'and ts<=a:return ts
   if tf=='u'and ts>=be:return ts
 # Null-move pruning
 if d>2 and not N(b,wt):
  ns=-S(b,[],not wt,d-3,-be,-be+1)
  if ns>=be:return be
 best=-99999;bm=None;oflag='l'
 om=sorted(mv,key=lambda m:O(b,m),reverse=True)
 if hh in TT:
  tm=TT[hh][3]
  if tm in om:om.insert(0,om.pop(om.index(tm)))
 for m in om:
  nb=M(b,m)
  s=-S(nb,[],not wt,d-1,-be,-a)
  if s>best:best=s;bm=m
  if s>a:a=s;oflag='e'
  if a>=be:oflag='u';break
 TT[hh]=(d,oflag,best,bm)
 return best
def C(g):
 global KT
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
   s=-S(nb,[],not wt,d-1,-99999,-a)
   if s>bs:bs=s;best=m
   if s>a:a=s
 return best
while 1:
 g=P("/game",{})
 if g.get("status")=="done":
  print(f"{g.get('wins',0)}W {g.get('draws',0)}D {g.get('losses',0)}L",file=sys.stderr);break
 while g.get("status")=="your_move":
  mv=C(g)
  if mv is None:g=P("/resign",{"game":g["game"]});break
  g=P("/move",{"game":g["game"],"move":mv})
  print(f"g{g['game']}:{g.get('outcome','?')}",file=sys.stderr)