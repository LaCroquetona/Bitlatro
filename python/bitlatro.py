# title:   Bitlatro
# author:  Croquetona
# desc:    this is a compact version of Balatro
# license: MIT License (change this to your license of choice)
# version: 0.3.0
# script:  python

# TO DO: para reducir espacio cogeremos la logica usada para dibujar sokers sin prite (unicamente la parte numerica / que define que hacer) y crearemos una funcion que sustituya a joker_value_text

import random
import math

mini_font={
 "A":["010","101","111","101","101"],
 "B":["110","101","110","101","110"],
 "C":["011","100","100","100","011"],
 "D":["110","101","101","101","110"],
 "E":["111","100","110","100","111"],
 "F":["111","100","110","100","100"],
 "G":["011","100","101","101","011"],
 "H":["101","101","111","101","101"],
 "I":["111","010","010","010","111"],
 "J":["001","001","001","101","010"],
 "K":["101","101","110","101","101"],
 "L":["100","100","100","100","111"],
 "M":["111","111","101","101","101"],
 "N":["110","101","101","101","101"],
 "O":["010","101","101","101","010"],
 "P":["110","101","110","100","100"],
 "Q":["010","101","101","111","011"],
 "R":["110","101","111","110","101"],
 "S":["011","100","010","001","110"],
 "T":["111","010","010","010","010"],
 "U":["101","101","101","101","011"],
 "V":["101","101","101","101","010"],
 "W":["101","101","111","111","101"],
 "X":["101","101","010","101","101"],
 "Y":["101","101","010","010","010"],
 "Z":["111","001","010","100","111"],
 "0":["011","101","101","101","110"],
 "1":["010","110","010","010","111"],
 "2":["110","001","010","100","111"],
 "3":["110","001","010","001","110"],
 "4":["101","101","111","001","001"],
 "5":["111","100","110","001","110"],
 "6":["011","100","111","101","111"],
 "7":["111","001","010","100","100"],
 "8":["111","101","111","101","111"],
 "9":["111","101","111","001","111"],
 " ":["000","000","000","000","000"],
 ",":["000","000","000","010","001"],
 "$":["011","110","011","110","010"],
 "/":["001","010","010","010","100"],
 "<":["001","010","100","010","001"],
 ">":["100","010","001","010","100"],
 ":":["000","010","000","010","000"],
 "+":["000","010","111","010","000"],
 "-":["000","000","111","000","000"],
 ".":["000","000","000","000","010"],
 "[":["011","010","010","010","011"],
 "]":["110","010","010","010","110"],
 "?":["111","001","010","000","010"],
 "=":["000","111","000","111","000"],
 "(":["001","010","010","010","001"],
 ")":["100","010","010","010","100"],
}

def draw_char(x,y,char,col):
 glyph=mini_font[char.upper()]
 for i in glyph:
  x-=3
  y+=1
  for j in i:
   x+=1
   if j=="1":
    pix(x,y,col)

def draw_text(txt,x,y,col):
 for i in txt:
  draw_char(x,y,i,col)
  x+=4

def set_col(slot,col):
 poke4(0x3FF0*2+slot,col)

def reset_col():
 set_col(6,6)
 set_col(7,7)
 set_col(14,14)
 set_col(2,2)

SUITS=("PICAS","CORAZONES","TREBOLES","DIAMANTES")

gs={
 "gm":0,"DS":0,"Clk0":False,
 "num1":random.randint(0,7)+17,"num2":random.randint(0,3)*16,
 "baraja":None,"jokers":[],"consu":[],"hand":[],"b":[],
 "anim":0,"up":0,"pal":"total",
 "fase_puntos":0,"tot_chips":0,"tot_mult":1,
 "carta_actual_idx":0,"timer_fase":0,
 "scoring_cards":[],"nombre_mano":"","chips_base_mano":0,"mult_base_mano":0,
 "vc":None,"vk":None,
 "rs":0,"hd":4,"ds":4,"mn":4,"ant":1,"rd":1,"hs":8,
 "ev_queue":[],"ev_idx":0,"ev_timer":0,"active_joker_idx":-1,
 "mano_flags":[False]*7,"first_match":{},"particles":[],
 "shake_chips":0,"shake_mult":0,"shake_nombre":0,"shake_money":0,
 "blind":0,"voff":0,"co_wait":0,
 "co_reward":0,"co_hands":0,"co_interest":0,"co_total":0,"co_req":0,
 "tt_target":None,
 "sort_mode":0,
 "drag_card":None,"drag_active":False,"drag_px":0,"drag_py":0,
 "drag_joker":None,
 "shop_j":[],"shop_p":[],"reroll":5,"free_rr":0,"pack":None,
 "jslots":5,"co_disc":0,"co_extra":0,
}

DEBUG=False

E_RISE=0
E_OPLAY=1
E_CSCORE=2
E_OSCORE=3
E_IND=4
E_FINAL=5
E_HELD=6
EDUR=[35,45,50,42,45,80,42]

F_FMUL=0
F_FCHP=1
F_XMUL=2
F_HMUL=3
F_HCHP=4
F_SMUL=5
F_RMUL=6
F_SCHP=7
F_RCHP=8
F_RTRG=9
F_SZMUL=10
F_RXFIRST=11
F_STENCIL=12
F_CHIP_DISC=13
F_NJOK_M=14
F_NODISC_M=15
F_HD_LAST_X=16
F_BULL=17
F_STICKY_M=18
F_STICKY_C=19
F_HELD_R=20
F_HXMUL=21
F_HIKER=22
F_RAND_M=23
F_BOOTS=24
F_DUSK=25
F_RAMEN=26
F_RCM=27
F_FCHP_DEC=28
F_SXPROB=29
F_HS_MOD=30
F_SMONEY=31
F_DECK_C=32
F_FMUL_DEC=33
F_EOR_MONEY=34
F_EOR_DISC=35
F_EOR_INT=36
F_EOR_DECK_RANK=37
F_SPLASH=38
F_FIRST_RTRG=39
F_HAND_SIZE=40
F_BONES=41
F_FREE_REROLL=42

J_GROS=20
J_CAVE=30
JCOST=(4,6,8)
PACK_DEF=((2,1,4),(4,1,6),(4,2,8))
PACK_NAME=("BUF","JMB","MEG")
SHOP_BASE_REROLL=5

SC_NO_FACE=0
SC_PLAYED=1
SC_HAND_FLAG=2
SC_SIZE_EQ=3
SC_RANK_SCORED=4
H_PAR=0
H_DPA=1
H_TRI=2
H_ESC=3
H_COL=4
H_FUL=5
H_POK=6

SCREEN_H=136
ANTE_BASE=(300,800,2800,6000,11000,20000,35000,50000)
BLIND_MULT=(1.0,1.5,2.0)
BLIND_REWARD=(3,4,5)
BLIND_NAME=("SMALL","BIG","BOSS")
INTEREST_CAP=5
CASH_SPEED=2
CASH_WAIT=20

JDEFS=[
 ("Joker",F_FMUL,4), #F S 0
 ("Jolly Joker",F_HMUL,8,H_PAR), #F S
 ("Zany Joker",F_HMUL,12,H_TRI), #F S
 ("Mad Joker",F_HMUL,10,H_DPA), #F S
 ("Crazy Joker",F_HMUL,12,H_ESC), #F S
 ("Droll Joker",F_HMUL,10,H_COL), #F S 5
 ("Sly Joker",F_HCHP,50,H_PAR), #F S
 ("Wily Joker",F_HCHP,100,H_TRI), #F S
 ("Clever Joker",F_HCHP,80,H_DPA), #F S
 ("Devious Joker",F_HCHP,100,H_ESC), #F S
 ("Crafty Joker",F_HCHP,80,H_COL), #F S 10
 ("Greedy Joker",F_SMUL,3,3), #F
 ("Lusty Joker",F_SMUL,3,1), #F
 ("Wrathful Joker",F_SMUL,3,0), #F
 ("Gluttonous Joker",F_SMUL,3,2), #F
 ("Scholar",F_RCM,20,4,(1,)), #F S 15
 ("Smiley Face",F_RMUL,5,(11,12,13)), #F S
 ("Even Steven",F_RMUL,4,(2,4,6,8,10)), #F S
 ("Odd Todd",F_RCHP,31,(1,3,5,7,9)), #F S
 ("Sock and Buskin",F_RTRG,(11,12,13)), #F S
 ("Gros Michel",F_FMUL,15),#TODO: 1/6 prob de autodestruirse al final de ronda y desbloquear Cavendish
 ("Half Joker",F_SZMUL,20,3), #F S 21
 ("Photograph",F_RXFIRST,2,(11,12,13)), #F S
 ("Joker Stencil",F_STENCIL,0), #F S
 ("Fibonacci",F_RMUL,8,(1,2,3,5,8)), #F S
 ("Hack",F_RTRG,(2,3,4,5)), #F S 25
 ("Arrowhead",F_SCHP,50,0), #F
 ("Bloodstone",F_SXPROB,1.5,2,1), #F
 ("Banner",F_CHIP_DISC,30), #F S
 ("Scary Face",F_RCHP,30,(11,12,13)), #F S
 ("Cavendish",F_XMUL,3),#30 TODO: 1/1000 prob de autodestruirse al final de ronda
 ("Wee Joker",F_STICKY_C,8,SC_RANK_SCORED,(2,)), #F S
 ("Onyx Agate",F_SMUL,7,2), #F
 ("The Duo",F_HXMUL,2,H_PAR), #F
 ("The Tribe",F_HXMUL,2,H_COL), #F
 ("The Order",F_HXMUL,3,H_ESC), #F 35
 ("The Trio",F_HXMUL,3,H_TRI), #F
 ("The Family",F_HXMUL,4,H_POK), #F
 ("Rough Gem",F_SMONEY,1,3), #F
 ("Misprint",F_RAND_M,23), #F
 ("Dusk",F_DUSK), #F 40
 ("Bootstraps",F_BOOTS,2,5), #F
 ("Stuntman",F_HS_MOD,250,-2), #F
 ("Ice Cream",F_FCHP_DEC,100,5,0), #F
 ("Abstract Joker",F_NJOK_M,3), #F
 ("Mystic Summit",F_NODISC_M,15), #F 45
 ("Acrobat",F_HD_LAST_X,3), #F
 ("Bull",F_BULL,2), #F
 ("Ride the Bus",F_STICKY_M,1,SC_NO_FACE,0), #F
 ("Green Joker",F_STICKY_M,1,SC_PLAYED,0), #F
 ("Hiker",F_HIKER,5), #F 50
 ("Ramen",F_RAMEN,2), #F
 ("Runner",F_STICKY_C,15,SC_HAND_FLAG,H_ESC), #F
 ("Square Joker",F_STICKY_C,4,SC_SIZE_EQ,4), #F
 ("Spare Trousers",F_STICKY_M,2,SC_HAND_FLAG,H_PAR), #F
 ("Shoot the Moon",F_HELD_R,13,(12,),0), #F 55
 ("Baron",F_HELD_R,1.5,(13,),1), #F
 ("The Duo",F_HXMUL,20,H_PAR),
 ("Walkie Talkie",F_RCM,10,4,(10,4)), # 58
 ("Blue Joker",F_DECK_C,2),
 ("Juggler",F_HAND_SIZE,1), # 60
 ("Popcorn",F_FMUL_DEC,20,4),
 ("Golden Joker",F_EOR_MONEY,4),
 ("Delayed Gratification",F_EOR_DISC,2),
 ("To the Moon",F_EOR_INT),
 ("Splash",F_SPLASH), # 65
 ("Hanging Chad",F_FIRST_RTRG,2),
 ("Cloud 9",F_EOR_DECK_RANK,1,9),
 ("Mr Bones",F_BONES),
 ("Chaos Clown",F_FREE_REROLL),
]

JRAR={
 0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,
 10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,
 19:1,20:1,21:0,22:0,23:1,24:1,25:1,26:1,27:1,28:0,29:0,
 30:1,31:0,32:1,33:2,34:2,35:2,36:2,37:2,38:1,39:1,
 40:1,41:1,42:2,43:0,44:0,45:0,46:1,47:1,48:0,49:0,
 50:1,51:1,52:0,53:0,54:1,55:1,56:2,
 58:0,59:0,60:0,61:0,62:0,63:0,64:1,65:0,66:0,67:0,68:1,69:1,
}

JPOOL=[[],[],[]]
for _jid,_rar in JRAR.items():
 JPOOL[_rar].append(_jid)

JSPR={
 0:(2,394),
 1:(3,2,394,[(3,6),(8,7)]),
 2:(3,2,394,[(3,1),(8,5),(7,1),(6,5)]),
 3:(3,2,394,[(3,2),(8,3),(6,3),(7,2)]),
 4:(3,2,394,[(3,2),(8,7),(6,10),(7,9)]),
 5:(3,2,394,[(8,14),(6,12),(7,13)]),
 6:(3,2,420,[(4,6),(3,6),(2,7),(8,7),(10,6)]),
 7:(3,2,420,[(4,5),(8,6),(3,1),(2,5),(10,7)]),
 8:(3,2,420,[(7,9),(8,9),(4,2),(2,4),(3,2)]),
 9:(3,2,420,[(7,2),(3,10),(2,9),(4,7),(8,3),(10,2)]),
 10:(3,2,420,[(7,2),(4,14),(3,14),(2,13),(8,3),(10,2)]),
 15:(2,418),
 16:(3,2,416,[(11,8)]),
 17:(2,398),
 18:(2,396),
 19:(0,262),
 20:(2,392),
 21:(1,356),
 22:(1,352),
 23:(2,390),
 24:(0,258),
 25:(3,2,422,[(11,2)]),
 28:(2,424),
 29:(3,2,426,[(11,15)]),
 30:(3,2,392,[(11,0)]),
 31:(1,354),
 49:(3,2,394,[(8,5),(3,1),(2,1),(7,1),(6,5)]),
}

def onda_y(an):
 t=time()
 return math.sin((t+an)/250)*0.75+math.sin((t+an)/150)*0.3

def shake_offset(fl,du,ax,ay,fr):
 if fl<=0:
  return (0,0)
 t=du-fl
 k=fl/du
 a=(t/du)*fr*math.pi*2
 return (math.sin(a)*ax*k, math.sin(a*1.3+1)*ay*k)

def tt_card(c,xc,yc):
 v=c.va
 a=str(c.va)
 if v==1:a="A"
 if v==11:a="J"
 if v==12:a="Q"
 if v==13:a="K"
 nm=a+" de "+SUITS[c.su]
 ls=[("+"+str(chips_c(c))+" CHIPS",7)]
 if c.ef:
  ls.append(("EFECTO",9))
 if c.st:
  ls.append(("SELLO",4))
 if c.ed:
  ls.append(("FOIL" if c.ed<10 else "HOLO",12))
 ml=len(nm)
 for l in ls:
  if len(l[0])>ml: ml=len(l[0])
 ws=(ml*4+6)//8+1
 hb=len(ls)
 tx=xc+8-ws*4
 ty=yc+27
 if tx+ws*8>240: tx=240-ws*8
 PrintBox(7,tx,ty,ws,2+len(ls))
 draw_text(nm,tx+(ws*8-len(nm)*4)//2+3,ty+2,11)
 PrintBox(5,tx+4,ty+7,ws-1,hb+1)
 for j in range(hb):
  draw_text(ls[j][0],tx+9,ty+11+j*9,ls[j][1])

JVT={
 F_FMUL:("+",1," MULT","",0),F_FCHP:("+",1," CHIP","",0),
 F_XMUL:("X",1," MULT","",0),F_HMUL:("+",1," MULT","",0),
 F_HCHP:("+",1," CHIP","",0),F_HXMUL:("X",1," MULT","",0),
 F_SMUL:("+",1," MULT/PALO","",0),F_RMUL:("+",1," M/RANGO","",0),
 F_SCHP:("+",1," F/PALO","",0),F_RCHP:("+",1," F/RANGO","",0),
 F_RCM:("+",1,"F +",2,"M"),F_SMONEY:("+$",1,"/PALO","",0),
 F_SXPROB:("X",1," MULT","",0),F_RTRG:("RETRIGGER",0,"","",0),
 F_DUSK:("RETRIGGER FIN",0,"","",0),F_RXFIRST:("X",1," 1A CARTA","",0),
 F_SZMUL:("+",1," M SI<=",2,""),F_STENCIL:("X(5-JOKERS)",0,"","",0),
 F_CHIP_DISC:("+",1," F/DESC","",0),F_NJOK_M:("+",1," M/JOKER","",0),
 F_NODISC_M:("+",1," SI 0 DESC","",0),F_HD_LAST_X:("X",1," U.MANO","",0),
 F_BULL:("+",1," F/$","",0),F_BOOTS:("+",1,"M/",2,"$"),
 F_RAND_M:("+0-",1," MULT","",0),F_HIKER:("+",1,"F PERM","",0),
 F_STICKY_M:("+",3," MULT","",0),F_STICKY_C:("+",3," FICHAS","",0),
 F_RAMEN:("X",4," MULT","",0),F_FCHP_DEC:("+",3," FICHAS","",0),
 F_HS_MOD:("+",1,"F ",2,"MANO"),F_DECK_C:("+",1," F/CARTA MAZO","",0),
 F_FMUL_DEC:("+",3," MULT","",0),F_EOR_MONEY:("+$",1," FIN RD","",0),
 F_EOR_DISC:("+$",1,"/DESC NO USA","",0),F_EOR_INT:("INTERES X2",0,"","",0),
 F_EOR_DECK_RANK:("+$",1,"/CARTA ",2,""),F_SPLASH:("TODAS PUNTUAN",0,"","",0),
 F_FIRST_RTRG:("+",1," RTRG 1A","",0),F_HAND_SIZE:("+",1," MANO","",0),
 F_BONES:("EVITA DERROTA",0,"","",0),F_FREE_REROLL:("1 REROLL GRATIS",0,"","",0),
}

def _jvt_v(j,d,m):
 if m==1: return str(d[2])
 if m==2: return str(d[3])
 if m==3: return str(j.st)
 if m==4: return str(round(j.xm,2))
 return ""

def joker_value_text(j):
 d=JDEFS[j.id]
 f=d[1]
 if f==F_HELD_R:
  p="+" if d[4]==0 else "X"
  return p+str(d[2])+" M/RETEN"
 e=JVT.get(f)
 if not e: return ""
 p1,m1,p2,m2,p3=e
 r=p1+_jvt_v(j,d,m1)+p2+_jvt_v(j,d,m2)
 if p3: r+=p3
 return r

def tt_joker(j,xj,yj):
 nm=JDEFS[j.id][0].upper()
 dsc=joker_value_text(j)
 lns=[nm]
 if dsc: lns.append(dsc)
 ml=0
 for ln in lns:
  if len(ln)>ml: ml=len(ln)
 ws=(ml*4+6)//8+1
 tx=xj+8-ws*4
 ty=yj+28
 if tx<0: tx=0
 if tx+ws*8>240: tx=240-ws*8
 PrintBox(7,tx,ty,ws,len(lns)+1)
 PrintBox(5,tx+4,ty+7,ws-1,len(lns))
 for k in range(len(lns)):
  ln=lns[k]
  draw_text(ln,tx+(ws*8-len(ln)*4)//2+2,ty+2+k*9,11)

def dibujar_joker(x,y,j):
 if j.id not in JSPR:
  return False
 cfg=JSPR[j.id]
 modo=cfg[0]
 if modo==3:
  for slot,col in cfg[3]:
   set_col(slot,col)
  bm=cfg[1]
  sid=cfg[2]
 else:
  bm=modo
  sid=cfg[1]
 if bm==2:
  spr(17,x,y,0)
  spr(17,x+8,y,0,1,1)
  spr(17,x,y+16,0,1,2)
  spr(17,x+8,y+16,0,1,3)
  spr(sid,x,y+4,0,1,0,0,2,2)
 elif bm==1:
  spr(sid,x,y+4,0,1,0,0,2,2)
 else:
  spr(sid,x,y,0,1,0,0,2,3)
 if modo==3:
  for slot,_ in cfg[3]:
   set_col(slot,slot)
 return True

def counter(st,cur,end,inc,rep):
 if cur!=end:
  if cur<end:
   cur+=inc
   if cur>end: cur=end
  elif cur>end:
   cur-=inc
   if cur<end: cur=end
 elif rep:
  cur=st
 return cur

class Boton:
 paletas={
  0:(7,6),1:(2,3),2:(0,1),3:(11,13),4:(10,8),
  5:(13,15),6:(15,15),7:(15,13),8:(13,13)
 }
 def __init__(self,txt,col,x,y,w,h,active):
  self.txt=txt
  self.x=x
  self.y=y
  self.w=w
  self.h=h
  self.active=active
  self.iner,self.bor=Boton.paletas.get(col,(7,6))
 def pintar(self):
  x=self.x
  y=self.y
  w=self.w
  h=self.h
  txt=self.txt
  bor=self.bor
  iner=self.iner
  set_col(6,bor)
  set_col(7,iner)
  clk=self.clicado()
  if clk or not self.active:
   prs=True
   y+=1
  else:
   prs=False
  for i in range(w):
   for j in range(h):
    if i==0:
     if j==h-1:
      if h==1: spr(244,x,y,0)
      else: spr(243,x,y+(j*8),0,1,2)
      if not prs:
       line(x+1,y+(j*8)+8,x+7,y+(j*8)+8,bor)
       pix(x,y+(j*8)+7,bor)
     elif j==0: spr(243,x,y,0)
     else: spr(227,x,y+(j*8),0,1,0,3)
    elif i==w-1:
     if j==h-1:
      if h==1: spr(244,x+(i*8),y+(j*8),0,1,0,2)
      else: spr(243,x+(i*8),y+(j*8),0,1,0,2)
      if not prs:
       line(x+(i*8),y+(j*8)+8,x+(i*8)+6,y+(j*8)+8,bor)
       pix(x+(i*8)+7,y+(j*8)+7,bor)
     elif j==0: spr(243,x+(i*8),y,0,1,1)
     else: spr(227,x+(i*8),y+(j*8),0,1,0,1)
    else:
     if j==h-1:
      if h==1: spr(228,x+(i*8),y+(j*8),0)
      else: spr(227,x+(i*8),y+(j*8),0,1,2)
      if not prs: line(x+(i*8),y+(j*8)+8,x+(i*8)+8,y+(j*8)+8,bor)
     elif j==0: spr(227,x+(i*8),y,0)
     else:
      spr(227,x+(i*8),y+(j*8),0)
      line(x+(i*8),y+(j*8),x+(i*8)+8,y+(j*8),iner)
  draw_text(txt,int(w*8/2-(len(txt)/2)*3)+x,int(h*8/2-4)+y,bor)
  reset_col()
  return clk
 def clicado(self):
  mx=mouse()[0]
  my=mouse()[1]
  mb=mouse()[2]
  if mb:
   if mx>=self.x and mx<self.x+self.w*8 and my>=self.y and my<self.y+self.h*8:
    return True
  return False

def PrintBox(col,x,y,w,h):
 iner,bor=Boton.paletas.get(col,(7,6))
 set_col(6,bor)
 set_col(7,iner)
 y+=1
 for i in range(w):
  for j in range(h):
   if i==0:
    if j==h-1:
     if h==1: spr(244,x,y,0)
     else: spr(243,x,y+(j*8),0,1,2)
    elif j==0: spr(243,x,y,0)
    else: spr(227,x,y+(j*8),0,1,0,3)
   elif i==w-1:
    if j==h-1:
     if h==1: spr(244,x+(i*8),y+(j*8),0,1,0,2)
     else: spr(243,x+(i*8),y+(j*8),0,1,0,2)
    elif j==0: spr(243,x+(i*8),y,0,1,1)
    else: spr(227,x+(i*8),y+(j*8),0,1,0,1)
   else:
    if j==h-1:
     if h==1: spr(228,x+(i*8),y+(j*8),0)
     else: spr(227,x+(i*8),y+(j*8),0,1,2)
    elif j==0: spr(227,x+(i*8),y,0)
    else:
     spr(227,x+(i*8),y+(j*8),0)
     line(x+(i*8),y+(j*8),x+(i*8)+8,y+(j*8),iner)
 reset_col()

def sort_hand():
 h=gs["hand"]
 if gs["sort_mode"]==0:
  h.sort(key=lambda c:14 if c.va==1 else c.va,reverse=True)
 else:
  h.sort(key=lambda c:(c.su,-(14 if c.va==1 else c.va)))

class Carta:
 def __init__(self,dt,suit,value,effect,stamp,edition):
  self.dt=dt
  self.su=suit
  self.va=value
  self.ef=effect
  self.st=stamp
  self.ed=edition
  self.an=random.randint(0,1000)
  if self.ed==1: self.ed=random.randint(1,5)
  elif self.ed==2: self.ed=random.randint(49,53)
  self.sel=False
  self.offset_eval=0
  self.bc=0

class Joker:
 def __init__(self,type_id):
  self.id=type_id
  self.st=0
  self.xm=0.0
  d=JDEFS[type_id]
  if d[1]==F_RAMEN: self.xm=float(d[2])
  elif d[1]==F_FCHP_DEC: self.st=d[2]
  elif d[1]==F_FMUL_DEC: self.st=d[2]
  self.an=random.randint(0,1000)
  self.ht=0

DECK_INFO=(
 (64,2,(("tienes un",2),("descarte mas",2))),
 (64,7,(("tienes una",7),("mano mas",7))),
 (64,1,(("no genera interese,",1),("2$ por mano y 1$ por",1),("descarte restante",1))),
 (64,8,(("comienzas con 10$",8),)),
 (64,15,(("tienes un joker",14),("mas, pero una",14),("mano menos",14))),
 (65,2,(("una baraja que",2),("solo tiene picas",14),("y corazones",2))),
 (66,2,(("una baraja",9),("con numeros",10),("del 1 al 10",9))),
 (67,2,(("baraja de 52 cartas",8),("pero los numeros",3),("estan randomizados",7))),
)

class Mazo:
 def __init__(self,tipo_baraja):
  self.dt=tipo_baraja
  self.cartas=[]
  self.total=[]
 def generar_mazo(self):
  self.cartas=[]
  dt=self.dt
  if dt in (0,1,2,3,4):
   for suit in range(4):
    for value in range(1,14):
     self.cartas.append(Carta(dt,suit,value,0,0,0))
  elif dt==5:
   for suit in range(2):
    for value in range(1,14):
     for _ in range(2):
      self.cartas.append(Carta(dt,suit,value,0,0,0))
  elif dt==6:
   for suit in range(4):
    for value in range(1,11):
     self.cartas.append(Carta(dt,suit,value,0,0,0))
  elif dt==7:
   for i in range(52):
    suit=int(random.randint(0,3))
    value=int(random.randint(1,13))
    self.cartas.append(Carta(dt,suit,value,0,0,0))
   self.ordenar()
  self.total=self.cartas.copy()
 def mostrar(self,x,y,scale,showtxt,txx,txy):
  dt=self.dt
  s=scale
  sp,c2,lns=DECK_INFO[dt]
  set_col(2,c2)
  spr(sp,x,y,0,s,0,0,1,3)
  spr(sp,x+s*8,y,0,s,0,2,1,3)
  if showtxt:
   for k in range(len(lns)):
    t,c=lns[k]
    draw_text(t,txx,txy+k*8,c)
  reset_col()
 def muestra(self,pal):
  return self.total if pal=="total" else self.cartas
 def mezclar(self): random.shuffle(self.cartas)
 def ordenar(self): self.cartas.sort(key=lambda c:c.va)
 def repartir(self):
  hand=gs["hand"]
  while len(hand)<gs["hs"] and len(self.cartas)>0:
   hand.append(self.cartas.pop(0))
  sort_hand()

def draw_card_at(i,xc,yc_base):
 cs=i.su*16
 cv=i.va
 ce=i.ef+17
 cm=i.st+59
 ced=int(i.ed)+112
 spr(ce,xc,yc_base,0,1,0,0,1,3)
 spr(ce,xc+8,yc_base,0,1,0,2,1,3)
 spr(cs,xc,yc_base+8,0)
 spr(cs,xc+8,yc_base+8,0,1,1)
 if i.su%2==1: set_col(14,2)
 spr(cv,xc,yc_base,0)
 spr(cv,xc+8,yc_base+16,0,1,0,2)
 set_col(14,14)
 spr(cm,xc+8,yc_base,0)
 if i.ed!=0:
  if i.ed<10: i.ed=counter(1,i.ed,5,0.125,True)
  else: i.ed=counter(49,i.ed,53,0.125,True)
  spr(ced,xc,yc_base,0,1,0,0,1,3)
  spr(ced,xc+8,yc_base,0,1,0,2,1,3)

def print_cards(x,y,xf,cards,permite_seleccion):
 b=gs["b"]
 hand=gs["hand"]
 if len(cards)==0: return
 tt=gs["gm"]==2
 mx=mouse()[0]
 my=mouse()[1]
 mb=mouse()[2]
 draggable=permite_seleccion and (cards is hand)
 if draggable and mb and gs["drag_card"] is not None and not gs["drag_active"]:
  if abs(mx-gs["drag_px"])>3: gs["drag_active"]=True
 if draggable and not mb and gs["Clk0"]:
  dc=gs["drag_card"]
  if dc is not None:
   if gs["drag_active"]:
    n=len(hand)
    sp=0 if n<=1 else (xf-x-17)/(n-1)
    if sp>0: ni=int(round((mx-x-8)/sp))
    else: ni=0
    if ni<0: ni=0
    if ni>=n: ni=n-1
    if dc in hand:
     oi=hand.index(dc)
     if ni!=oi:
      hand.pop(oi)
      hand.insert(ni,dc)
   else:
    if dc.sel or len([cc for cc in hand if cc.sel])<5:
     dc.sel=not dc.sel
  gs["drag_card"]=None
  gs["drag_active"]=False
 con=0
 sep=0 if len(cards)==1 else (xf-x-17)/(len(cards)-1)
 dec=0
 for i in cards:
  dec+=sep-int(sep)
  xc=int(x+con*int(sep)+int(dec))
  yc_base=int(y+onda_y(i.an)-i.offset_eval+(-4 if (i.sel and permite_seleccion) else 0))
  con+=1
  if i in b and cards is hand: continue
  hv=(permite_seleccion or tt) and mx>=xc and mx<xc+16 and my>=yc_base and my<yc_base+23
  if draggable and hv and mb and not gs["Clk0"]:
   gs["drag_card"]=i
   gs["drag_active"]=False
   gs["drag_px"]=mx
   gs["drag_py"]=my
  if gs["drag_active"] and gs["drag_card"] is i: continue
  draw_card_at(i,xc,yc_base)
  if tt and hv: gs["tt_target"]=("card",i,xc,yc_base)
 if draggable and gs["drag_active"] and gs["drag_card"] is not None:
  draw_card_at(gs["drag_card"],mx-8,my-12)


def eval_hand():
 return [c for c in gs["hand"] if c.sel]

def chips_c(card):
 if card.va==1: return 11+card.bc
 elif card.va>=11: return 10+card.bc
 return card.va+card.bc

def detectar_mano(cartas):
 if len(cartas)==0: return ("",0,0,[])
 conteo_val={}
 conteo_su={}
 for c in cartas:
  conteo_val[c.va]=conteo_val.get(c.va,0)+1
  conteo_su[c.su]=conteo_su.get(c.su,0)+1
 grupos=sorted(conteo_val.values(),reverse=True)
 vals_ord=sorted(conteo_val.keys())
 es_color=(len(conteo_su)==1 and len(cartas)==5)
 es_escalera=False
 if len(cartas)==5 and len(conteo_val)==5:
  rng=vals_ord[-1]-vals_ord[0]
  es_escalera=(rng==4)
  if not es_escalera and vals_ord==[1,2,3,4,5]: es_escalera=True
 if es_escalera and es_color: return ("ESCALERA DE COLOR",100,8,cartas[:])
 elif grupos[0]==4:
  sc=[c for c in cartas if conteo_val[c.va]==4]
  return ("POKER",60,7,sc)
 elif len(grupos)>=2 and grupos[0]==3 and grupos[1]==2: return ("FULL HOUSE",40,4,cartas[:])
 elif es_color: return ("COLOR",35,4,cartas[:])
 elif es_escalera: return ("ESCALERA",30,4,cartas[:])
 elif grupos[0]==3:
  sc=[c for c in cartas if conteo_val[c.va]==3]
  return ("TRIO",30,3,sc)
 elif len(grupos)>=2 and grupos[0]==2 and grupos[1]==2:
  sc=[c for c in cartas if conteo_val[c.va]==2]
  return ("DOBLE PAREJA",20,2,sc)
 elif grupos[0]==2:
  sc=[c for c in cartas if conteo_val[c.va]==2]
  return ("PAREJA",10,2,sc)
 else:
  mejor=max(cartas,key=lambda c:c.va if c.va!=1 else 14)
  return ("CARTA ALTA",5,1,[mejor])

PARTICLE_KINDS={
 "chip":(6,""),"mult":(3,"+"),"xmult":(2,"x"),
 "trigger":(9,""),"money":(9,"$"),"loss_m":(2,"-"),
}

def draw_diamond(cx,cy,w,h,col):
 hw=w//2
 hh=h//2
 if hw<=0 or hh<=0: return
 tri(cx-hw,cy,cx,cy-hh,cx+hw,cy,col)
 tri(cx-hw,cy,cx,cy+hh,cx+hw,cy,col)

def card_center_xy(ci):
 c=gs["scoring_cards"][ci]
 b=gs["b"]
 if c not in b: return (128,53)
 idx=b.index(c)
 n=len(b)
 sep=(n*16-17)/(n-1) if n>1 else 0
 return (int(80+idx*sep)+8,53)

def joker_center_xy(ji):
 n=len(gs["jokers"])
 sep=(172-83-16)/(n-1) if n>1 else 0
 return (int(83+ji*sep)+8,20)

def hand_card_center(hi):
 cards=gs["hand"]
 if len(cards)==0 or hi>=len(cards): return (128,140-gs["up"])
 x=80
 y=140-gs["up"]
 xf=193
 sep=0 if len(cards)==1 else (xf-x-17)/(len(cards)-1)
 xc=int(x+hi*sep)
 return (xc+8,y+10)

def spawn_particle(cx,cy,value,kind):
 gs["particles"].append({"x":cx,"y":cy,"life":45,"max_life":45,"value":value,"kind":kind})
 if kind=="chip": gs["shake_chips"]=15
 elif kind in ("mult","xmult"): gs["shake_mult"]=15
 elif kind=="money": gs["shake_money"]=15
 elif kind=="loss_m": gs["shake_mult"]=15

def spawn_for_joker(ji):
 j=gs["jokers"][ji]
 d=JDEFS[j.id]
 f=d[1]
 cx,cy=joker_center_xy(ji)
 if f in (F_FMUL,F_HMUL,F_SMUL,F_RMUL,F_SZMUL,F_NODISC_M): spawn_particle(cx,cy,d[2],"mult")
 elif f in (F_FCHP,F_HCHP,F_SCHP,F_RCHP): spawn_particle(cx,cy,d[2],"chip")
 elif f in (F_XMUL,F_RXFIRST,F_HD_LAST_X,F_HXMUL): spawn_particle(cx,cy,d[2],"xmult")
 elif f==F_RAMEN: spawn_particle(cx,cy,round(j.xm,2),"xmult")
 elif f==F_STENCIL: spawn_particle(cx,cy,max(1,5-len(gs["jokers"])),"xmult")
 elif f==F_CHIP_DISC: spawn_particle(cx,cy,d[2]*gs["ds"],"chip")
 elif f==F_NJOK_M: spawn_particle(cx,cy,d[2]*len(gs["jokers"]),"mult")
 elif f==F_BULL: spawn_particle(cx,cy,d[2]*gs["mn"],"chip")
 elif f==F_STICKY_M: spawn_particle(cx,cy,j.st,"mult")
 elif f==F_STICKY_C: spawn_particle(cx,cy,j.st,"chip")
 elif f==F_RAND_M: spawn_particle(cx,cy,"?","mult")
 elif f==F_BOOTS: spawn_particle(cx,cy,d[2]*(gs["mn"]//d[3]),"mult")
 elif f==F_RCM:
  spawn_particle(cx,cy,d[2],"chip")
  spawn_particle(cx,cy-6,d[3],"mult")
 elif f==F_SXPROB: spawn_particle(cx,cy,d[2],"xmult")
 elif f==F_SMONEY: spawn_particle(cx,cy,d[2],"money")
 elif f==F_HS_MOD: spawn_particle(cx,cy,d[2],"chip")
 elif f==F_FCHP_DEC: spawn_particle(cx,cy,j.st,"chip")
 elif f==F_DECK_C: spawn_particle(cx,cy,d[2]*len(gs["baraja"].total),"chip")
 elif f==F_FMUL_DEC: spawn_particle(cx,cy,j.st,"mult")

def update_and_draw_particles():
 alive=[]
 for p in gs["particles"]:
  ml=p["max_life"]
  r=(ml-p["life"])/ml
  if r<0.2: s=r/0.2
  elif r<0.7: s=1.0
  else: s=1.0-(r-0.7)/0.3
  cx=int(p["x"])
  cy=int(p["y"]-r*6)
  col,prefix=PARTICLE_KINDS[p["kind"]]
  txt=prefix+str(p["value"])
  w=int(max(18,len(txt)*4+6)*s)
  h=int(10*s)
  draw_diamond(cx,cy,w,h,col)
  if s>0.5: draw_text(txt,cx-len(txt)*2+1,cy-2,15)
  p["life"]-=1
  if p["life"]>0: alive.append(p)
 gs["particles"]=alive

def calcular_mano_flags(cartas):
 cv={}
 cs={}
 for c in cartas:
  cv[c.va]=cv.get(c.va,0)+1
  cs[c.su]=cs.get(c.su,0)+1
 grupos=sorted(cv.values(),reverse=True)
 vals=sorted(cv.keys())
 escolor=(len(cs)==1 and len(cartas)==5)
 esesc=False
 if len(cartas)==5 and len(cv)==5:
  rng=vals[-1]-vals[0]
  esesc=(rng==4) or (vals==[1,2,3,4,5])
 f=[False]*7
 f[H_PAR]=grupos[0]>=2
 f[H_DPA]=len(grupos)>=2 and grupos[0]>=2 and grupos[1]>=2
 f[H_TRI]=grupos[0]>=3
 f[H_ESC]=esesc
 f[H_COL]=escolor
 f[H_FUL]=grupos[0]>=3 and len(grupos)>=2 and grupos[1]>=2
 f[H_POK]=grupos[0]>=4
 return f

def joker_fires_play(j): return False

def joker_fires_score(j,card):
 d=JDEFS[j.id]
 f=d[1]
 if f==F_SMUL or f==F_SCHP: return card.su==d[3]
 if f==F_RMUL or f==F_RCHP: return card.va in d[3]
 if f==F_RCM: return card.va in d[4]
 if f==F_SMONEY: return card.su==d[3]
 if f==F_SXPROB:
  if card.su!=d[4]: return False
  return random.randint(1,d[3])==1
 return False

def joker_fires_ind(j):
 d=JDEFS[j.id]
 f=d[1]
 if f in (F_FMUL,F_FCHP,F_XMUL,F_STENCIL,F_CHIP_DISC,F_RAMEN): return True
 if f in (F_NJOK_M,F_BULL,F_RAND_M): return True
 if f in (F_HMUL,F_HCHP,F_HXMUL): return gs["mano_flags"][d[3]]
 if f==F_SZMUL: return len(gs["b"])<=d[3]
 if f==F_NODISC_M: return gs["ds"]==0
 if f==F_HD_LAST_X: return gs["hd"]==1
 if f in (F_STICKY_M,F_STICKY_C): return j.st>0
 if f==F_BOOTS: return gs["mn"]>=d[3]
 if f==F_HS_MOD: return True
 if f==F_FCHP_DEC: return j.st>0
 if f==F_DECK_C: return True
 if f==F_FMUL_DEC: return j.st>0
 return False

def count_retriggers(card):
 n=0
 for ji,j in enumerate(gs["jokers"]):
  d=JDEFS[j.id]
  if d[1]==F_RTRG and card.va in d[2]: n+=1
  if d[1]==F_DUSK and gs["hd"]==1: n+=1
 return n

def apply_joker_effect(j):
 d=JDEFS[j.id]
 f=d[1]
 if f in (F_FMUL,F_HMUL,F_SMUL,F_RMUL,F_SZMUL,F_NODISC_M): gs["tot_mult"]+=d[2]
 elif f in (F_FCHP,F_HCHP,F_SCHP,F_RCHP): gs["tot_chips"]+=d[2]
 elif f in (F_XMUL,F_RXFIRST,F_HD_LAST_X,F_HXMUL): gs["tot_mult"]*=d[2]
 elif f==F_RAMEN: gs["tot_mult"]*=j.xm
 elif f==F_STENCIL: gs["tot_mult"]*=max(1,5-len(gs["jokers"]))
 elif f==F_CHIP_DISC: gs["tot_chips"]+=d[2]*gs["ds"]
 elif f==F_NJOK_M: gs["tot_mult"]+=d[2]*len(gs["jokers"])
 elif f==F_BULL: gs["tot_chips"]+=d[2]*gs["mn"]
 elif f==F_STICKY_M: gs["tot_mult"]+=j.st
 elif f==F_STICKY_C: gs["tot_chips"]+=j.st
 elif f==F_RAND_M: gs["tot_mult"]+=random.randint(0,d[2])
 elif f==F_BOOTS: gs["tot_mult"]+=d[2]*(gs["mn"]//d[3])
 elif f==F_RCM:
  gs["tot_chips"]+=d[2]
  gs["tot_mult"]+=d[3]
 elif f==F_SXPROB: gs["tot_mult"]*=d[2]
 elif f==F_SMONEY: gs["mn"]+=d[2]
 elif f==F_HS_MOD: gs["tot_chips"]+=d[2]
 elif f==F_FCHP_DEC: gs["tot_chips"]+=j.st
 elif f==F_DECK_C: gs["tot_chips"]+=d[2]*len(gs["baraja"].total)
 elif f==F_FMUL_DEC: gs["tot_mult"]+=j.st

def apply_event(e):
 et=e[0]
 if et==E_CSCORE:
  ci=e[1]
  c=gs["scoring_cards"][ci]
  for jh in gs["jokers"]:
   if JDEFS[jh.id][1]==F_HIKER: c.bc+=JDEFS[jh.id][2]
  chips=chips_c(c)
  gs["tot_chips"]+=chips
  cx,cy=card_center_xy(ci)
  is_rt=len(e)>2 and e[2]
  spawn_particle(cx,cy,chips,"chip")
  if is_rt: spawn_particle(cx,cy-12,"TRIGER","trigger")
 elif et==E_OPLAY:
  apply_joker_effect(gs["jokers"][e[1]])
  spawn_for_joker(e[1])
 elif et==E_OSCORE:
  ji,ci=e[1]
  apply_joker_effect(gs["jokers"][ji])
  spawn_for_joker(ji)
 elif et==E_IND:
  ji=e[1]
  apply_joker_effect(gs["jokers"][ji])
  spawn_for_joker(ji)
 elif et==E_HELD:
  ji,hi=e[1]
  j=gs["jokers"][ji]
  d=JDEFS[j.id]
  if hi<len(gs["hand"]): cx,cy=hand_card_center(hi)
  else: cx,cy=joker_center_xy(ji)
  if d[4]==0:
   gs["tot_mult"]+=d[2]
   spawn_particle(cx,cy,d[2],"mult")
  else:
   gs["tot_mult"]*=d[2]
   spawn_particle(cx,cy,d[2],"xmult")

def update_sticky(b,sc,flags):
 face=(11,12,13)
 has_face=False
 for c in sc:
  if c.va in face:
   has_face=True
   break
 for j in gs["jokers"]:
  d=JDEFS[j.id]
  f=d[1]
  if f!=F_STICKY_M and f!=F_STICKY_C: continue
  cond=d[3]
  param=d[4]
  inc=d[2]
  if cond==SC_NO_FACE:
   if has_face: j.st=0
   else: j.st+=inc
  elif cond==SC_PLAYED: j.st+=inc
  elif cond==SC_HAND_FLAG:
   if flags[param]: j.st+=inc
  elif cond==SC_SIZE_EQ:
   if len(b)==param: j.st+=inc
  elif cond==SC_RANK_SCORED:
   for c in sc:
    if c.va in param: j.st+=inc

def build_event_queue(scoring):
 q=[[E_RISE,None]]
 fm={}
 first_rt=0
 for ji,j in enumerate(gs["jokers"]):
  d=JDEFS[j.id]
  if d[1]==F_RXFIRST:
   for ci,c in enumerate(scoring):
    if c.va in d[3]:
     fm[ji]=ci
     break
  elif d[1]==F_FIRST_RTRG:
   first_rt+=d[2]
 gs["first_match"]=fm
 for ji,j in enumerate(gs["jokers"]):
  if joker_fires_play(j): q.append([E_OPLAY,ji])
 for ci,c in enumerate(scoring):
  rt=count_retriggers(c)
  if ci==0: rt+=first_rt
  for r in range(1+rt):
   q.append([E_CSCORE,ci,r>0])
   for ji,j in enumerate(gs["jokers"]):
    if joker_fires_score(j,c) or fm.get(ji)==ci:
     q.append([E_OSCORE,(ji,ci)])
 for ji,j in enumerate(gs["jokers"]):
  d=JDEFS[j.id]
  if d[1]==F_HELD_R:
   for hi,c in enumerate(gs["hand"]):
    if c not in gs["b"] and c.va in d[3]:
     q.append([E_HELD,(ji,hi)])
  elif joker_fires_ind(j): q.append([E_IND,ji])
 q.append([E_FINAL,None])
 return q

def recalc_hs():
 hs=8
 for j in gs["jokers"]:
  d=JDEFS[j.id]
  if d[1]==F_HS_MOD: hs+=d[3]
  elif d[1]==F_HAND_SIZE: hs+=d[2]
 if hs<1: hs=1
 gs["hs"]=hs

def base_hands():
 dt=gs["baraja"].dt
 v=4
 if dt==1: v+=1
 elif dt==4: v-=1
 return v

def base_discards():
 dt=gs["baraja"].dt
 v=4
 if dt==0: v+=1
 return v

def start_money():
 if gs["baraja"].dt==3: return 10
 return 4

def joker_slots():
 if gs["baraja"].dt==4: return 6
 return 5

def ante_base(a):
 if a<=8: return ANTE_BASE[a-1]
 v=ANTE_BASE[7]
 for _ in range(a-8): v=int(v*1.6)
 return v

def splash_active():
 for j in gs["jokers"]:
  if JDEFS[j.id][1]==F_SPLASH: return True
 return False

def joker_round_money():
 m=0
 for j in gs["jokers"]:
  d=JDEFS[j.id]
  f=d[1]
  if f==F_EOR_MONEY: m+=d[2]
  elif f==F_EOR_DISC:
   if gs["ds"]==base_discards(): m+=d[2]*gs["ds"]
  elif f==F_EOR_DECK_RANK:
   c=0
   for ca in gs["baraja"].total:
    if ca.va==d[3]: c+=1
   m+=d[2]*c
 return m

def has_free_reroll():
 for j in gs["jokers"]:
  if JDEFS[j.id][1]==F_FREE_REROLL: return True
 return False

def roll_rarity():
 r=random.randint(1,100)
 if r<=70: return 0
 if r<=95: return 1
 return 2

def roll_joker():
 rar=roll_rarity()
 pool=JPOOL[rar]
 if len(pool)==0: pool=JPOOL[0]
 return pool[random.randint(0,len(pool)-1)]

def joker_price(jid):
 return JCOST[JRAR.get(jid,0)]

def clicked_rect(r,x,y,w,h):
 return r[0]>=x and r[0]<x+w and r[1]>=y and r[1]<y+h and r[2] and not gs["Clk0"]

def blind_req():
 a=gs["ant"]
 return int(ante_base(a)*BLIND_MULT[gs["blind"]])

def cash_out_money():
 dt=gs["baraja"].dt
 reward=BLIND_REWARD[gs["blind"]]
 if dt==2:
  hands=gs["hd"]*2
  interest=0
  disc=gs["ds"]
 else:
  hands=gs["hd"]
  itc=INTEREST_CAP
  for j in gs["jokers"]:
   if JDEFS[j.id][1]==F_EOR_INT: itc*=2
  interest=min(itc,gs["mn"]//5)
  disc=0
 extra=joker_round_money()
 return reward,hands,interest,disc,extra

def try_mr_bones():
 for ji,j in enumerate(gs["jokers"]):
  if JDEFS[j.id][1]==F_BONES:
   if gs["rs"]>=blind_req()//4:
    gs["jokers"].pop(ji)
    recalc_hs()
    gs["rs"]=blind_req()
    return True
   return False
 return False

def start_round_win():
 new_j=[]
 for j in gs["jokers"]:
  d=JDEFS[j.id]
  if j.id==J_GROS:
   if random.randint(1,6)==1: continue
  elif j.id==J_CAVE:
   if random.randint(1,1000)==1: continue
  elif d[1]==F_FMUL_DEC:
   j.st-=d[3]
   if j.st<=0: continue
  new_j.append(j)
 gs["jokers"]=new_j
 recalc_hs()
 r,h,it,dc,ex=cash_out_money()
 gs["co_reward"]=r
 gs["co_hands"]=h
 gs["co_interest"]=it
 gs["co_disc"]=dc
 gs["co_extra"]=ex
 gs["co_total"]=r+h+it+dc+ex
 gs["co_req"]=blind_req()
 gs["voff"]=0
 gs["co_wait"]=CASH_WAIT
 gs["fase_puntos"]=2

def finalize_score():
 new_j=[]
 for j in gs["jokers"]:
  d=JDEFS[j.id]
  if d[1]==F_FCHP_DEC:
   j.st-=d[3]
   if j.st<=d[4]: continue
  new_j.append(j)
 gs["jokers"]=new_j
 recalc_hs()
 gs["rs"]+=int(gs["tot_chips"]*gs["tot_mult"])
 gs["hand"]=[c for c in gs["hand"] if c not in gs["b"]]
 gs["b"]=[]
 gs["scoring_cards"]=[]
 gs["ev_queue"]=[]
 gs["ev_idx"]=0
 gs["ev_timer"]=0
 gs["active_joker_idx"]=-1
 if gs["rs"]>=blind_req():
  start_round_win()
 elif gs["hd"]<=0:
  if try_mr_bones(): start_round_win()
  else: gs["gm"]=5
 else:
  gs["baraja"].repartir()
  gs["fase_puntos"]=0

def step_queue():
 q=gs["ev_queue"]
 if gs["ev_idx"]>=len(q):
  if DEBUG:
   if btnp(4): finalize_score()
  else: finalize_score()
  return
 e=q[gs["ev_idx"]]
 if gs["ev_timer"]==0: apply_event(e)
 gs["ev_timer"]+=1
 if DEBUG:
  if btnp(4):
   gs["ev_idx"]+=1
   gs["ev_timer"]=0
 else:
  if gs["ev_timer"]>=EDUR[e[0]]:
   gs["ev_idx"]+=1
   gs["ev_timer"]=0

def update_event_visuals():
 for c in gs["b"]: c.offset_eval=0
 for c in gs["hand"]:
  if c not in gs["b"]: c.offset_eval=0
 gs["active_joker_idx"]=-1
 q=gs["ev_queue"]
 if gs["ev_idx"]>=len(q): return
 e=q[gs["ev_idx"]]
 et=e[0]
 if DEBUG: bounce=6
 else:
  prog=min(1.0,gs["ev_timer"]/EDUR[et]) if EDUR[et]>0 else 1.0
  bounce=int(math.sin(prog*math.pi)*6)
 if et==E_CSCORE:
  ci=e[1]
  if ci<len(gs["scoring_cards"]): gs["scoring_cards"][ci].offset_eval=bounce
  if len(e)>2 and e[2]:
   c=gs["scoring_cards"][ci]
   for ji,j in enumerate(gs["jokers"]):
    d=JDEFS[j.id]
    if d[1]==F_RTRG and c.va in d[2]:
     gs["active_joker_idx"]=ji
     break
    elif d[1]==F_DUSK and gs["hd"]==0:
     gs["active_joker_idx"]=ji
     break
 elif et==E_OSCORE:
  ji,ci=e[1]
  gs["active_joker_idx"]=ji
  if ci<len(gs["scoring_cards"]): gs["scoring_cards"][ci].offset_eval=bounce//2
 elif et==E_OPLAY or et==E_IND: gs["active_joker_idx"]=e[1]
 elif et==E_HELD:
  ji,hi=e[1]
  gs["active_joker_idx"]=ji
  if hi<len(gs["hand"]): gs["hand"][hi].offset_eval=bounce

def get_event_name(e):
 RANK=["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
 SUIT=["P","C","T","R"]
 et=e[0]
 if et==E_RISE: return "RISE"
 if et==E_FINAL: return "FINAL"
 if et==E_CSCORE:
  c=gs["scoring_cards"][e[1]]
  isrt=len(e)>2 and e[2]
  return ("RTRG " if isrt else "CARD ")+RANK[c.va-1]+SUIT[c.su]+" "+str(chips_c(c))+"CH"
 if et==E_OPLAY: return "OPLAY:"+JDEFS[gs["jokers"][e[1]].id][0][:6].upper()
 if et==E_IND: return "IND:"+JDEFS[gs["jokers"][e[1]].id][0][:7].upper()
 if et==E_OSCORE:
  ji,ci=e[1]
  c=gs["scoring_cards"][ci]
  return "SCORE:"+JDEFS[gs["jokers"][ji].id][0][:5].upper()+"/"+RANK[c.va-1]
 if et==E_HELD:
  ji,hi=e[1]
  if hi<len(gs["hand"]):
   c=gs["hand"][hi]
   return "HELD:"+JDEFS[gs["jokers"][ji].id][0][:4].upper()+"/"+RANK[c.va-1]
  return "HELD:?"
 return "?"

def draw_debug():
 if not DEBUG or gs["fase_puntos"]==0: return
 q=gs["ev_queue"]
 idx=gs["ev_idx"]
 rect(4,77,172,20,0)
 rectb(4,77,172,20,6)
 if idx>=len(q):
  draw_text("DONE   Z>FIN",6,80,15)
  draw_text("CH:"+str(int(gs["tot_chips"])),6,88,6)
  draw_text("ML:"+str(int(gs["tot_mult"])),70,88,3)
  return
 e=q[idx]
 nm=get_event_name(e)
 draw_text(nm,6,80,15)
 draw_text("CH:"+str(int(gs["tot_chips"])),6,88,6)
 draw_text("ML:"+str(int(gs["tot_mult"])),70,88,3)
 draw_text("Z>NEXT",126,88,14)

def print_jokers(oy=0):
 reset_col()
 bx=83
 by=8+oy
 xf=172
 ai=gs["active_joker_idx"]
 n=len(gs["jokers"])
 if n==0:
  if not mouse()[2] and gs["Clk0"]:
   gs["drag_joker"]=None
   gs["drag_active"]=False
  return
 sep=0 if n==1 else (xf-bx-16)/(n-1)
 mx=mouse()[0]
 my=mouse()[1]
 mb=mouse()[2]
 draggable=(gs["gm"] in (1,3)) and gs["fase_puntos"]==0 and oy==0
 if draggable and mb and gs["drag_joker"] is not None and not gs["drag_active"]:
  if abs(mx-gs["drag_px"])>3 or abs(my-gs["drag_py"])>3: gs["drag_active"]=True
 if draggable and not mb and gs["Clk0"]:
  dj=gs["drag_joker"]
  if dj is not None and gs["drag_active"] and dj in gs["jokers"]:
   nj=len(gs["jokers"])
   sp=0 if nj<=1 else (xf-bx-16)/(nj-1)
   if sp>0: ni=int(round((mx-bx-8)/sp))
   else: ni=0
   if ni<0: ni=0
   if ni>=nj: ni=nj-1
   oi=gs["jokers"].index(dj)
   if ni!=oi:
    gs["jokers"].pop(oi)
    gs["jokers"].insert(ni,dj)
  gs["drag_joker"]=None
  gs["drag_active"]=False
 con=0
 dec=0
 tt_target=None
 for j in gs["jokers"]:
  dec+=sep-int(sep)
  xj=int(bx+con*int(sep)+int(dec))
  yj_base=int(by+onda_y(j.an)*1.2)-(4 if ai==con else 0)
  hv=mx>=xj and mx<xj+16 and my>=yj_base and my<yj_base+24
  if hv and not gs["drag_active"]:
   if j.ht<30: j.ht+=1
  else: j.ht=0
  if draggable and hv and mb and not gs["Clk0"] and gs["drag_joker"] is None:
   gs["drag_joker"]=j
   gs["drag_active"]=False
   gs["drag_px"]=mx
   gs["drag_py"]=my
  con+=1
  d=JDEFS[j.id]
  if gs["drag_active"] and gs["drag_joker"] is j: continue
  if not dibujar_joker(xj,yj_base,j):
   draw_joker_box(xj,yj_base,j)
   f=d[1]
   if f==F_DECK_C or f==F_HELD_R:
    rect(xj+1,yj_base+13,14,7,1)
    if f==F_DECK_C: draw_text("+"+str(d[2]*len(gs["baraja"].total)),xj+2,yj_base+14,6)
    else:
     held=0
     for c in gs["hand"]:
      if c not in gs["b"] and c.va in d[3]: held+=1
     if d[4]==0: draw_text("+"+str(d[2]*held),xj+2,yj_base+14,3)
     else: draw_text("x"+str(d[2]),xj+2,yj_base+14,3)
  if hv and j.ht>=15 and gs["fase_puntos"]<2 and not gs["drag_active"]: tt_target=(j,xj,yj_base)
 if tt_target: gs["tt_target"]=("joker",tt_target[0],tt_target[1],tt_target[2])
 if draggable and gs["drag_active"] and gs["drag_joker"] is not None:
  dj=gs["drag_joker"]
  dx=mx-8
  dy=my-12
  if not dibujar_joker(dx,dy,dj):
   draw_joker_box(dx,dy,dj)

def PantallaMenu(raton):
 cls()
 map(0,0,31,18)
 titx=108
 tity=12
 spr(77,titx+28,tity,0,2,0,0,3,2)
 spr(gs["num1"],titx,tity-9,0,2,0,0,1,3)
 spr(gs["num1"],titx+16,tity-9,0,2,0,2,1,3)
 spr(gs["num2"],titx,tity+7,0,2)
 spr(gs["num2"],titx+16,tity+7,0,2,1)
 if gs["num2"] in (16,48): set_col(14,2)
 spr(1,titx,tity-9,0,2)
 spr(1,titx+16,tity+23,0,2,0,2)
 set_col(14,14)
 spr(73,titx-52,tity,0,2,0,0,4,2)
 line(titx-48,tity-2,titx-41,tity-2,15)
 line(titx-48,tity-1,titx-41,tity-1,15)
 gs["baraja"].mostrar(64,64,2,True,102,70)
 prev_DS=gs["DS"]
 btn_prev=Boton(" <",1,100,95,3,2,True)
 btn_prev.pintar()
 if btn_prev.clicado() and not gs["Clk0"]: gs["DS"]=(gs["DS"]+7)%8
 btn_next=Boton(" >",0,150,95,3,2,True)
 btn_next.pintar()
 if btn_next.clicado() and not gs["Clk0"]: gs["DS"]=(gs["DS"]+1)%8
 if gs["DS"]!=prev_DS: gs["baraja"]=Mazo(gs["DS"])
 play=Boton("play",4,125,95,3,2,True)
 play.pintar()
 if play.clicado() and not gs["Clk0"]:
  gs["fase_puntos"]=0
  gs["rs"]=0
  gs["ant"]=1
  gs["rd"]=1
  gs["vk"]=None
  gs["particles"]=[]
  gs["shake_chips"]=0
  gs["shake_mult"]=0
  gs["shake_nombre"]=0
  gs["shake_money"]=0
  gs["hs"]=8
  gs["blind"]=0
  gs["voff"]=0
  gs["co_wait"]=0
  gs["pack"]=None
  gs["baraja"].generar_mazo()
  gs["baraja"].mezclar()
  gs["mn"]=start_money()
  gs["jslots"]=joker_slots()
  gs["hd"]=base_hands()
  gs["ds"]=base_discards()
  gs["jokers"]=[Joker(57)]
  #gs["jokers"]=[Joker(28),Joker(29),Joker(30),Joker(31),Joker(32),Joker(33),Joker(34)] # descomentar para test
  gs["hand"]=[]
  gs["b"]=[]
  gs["consu"]=[]
  recalc_hs()
  gs["gm"]=4

def draw_money_box():
 voff=gs["voff"]
 ox,oy=shake_offset(gs["shake_money"],15,2,1,4)
 if gs["shake_money"]>0: gs["shake_money"]-=1
 PrintBox(8,4,95,8,2)
 pix(5,96,15)
 line(4,97,4,110,15)
 pix(5,111,15)
 pix(66,96,15)
 line(67,97,67,110,15)
 pix(66,111,15)
 PrintBox(7,8+int(ox),95+int(oy),7,2)
 draw_text("$"+str(gs["mn"]),31+int(ox),100+int(oy),9)

def draw_score_hud(permitir):
 voff=gs["voff"]
 ox_c,oy_c=shake_offset(gs["shake_chips"],15,2,1,4)
 ox_m,oy_m=shake_offset(gs["shake_mult"],15,2,1,4)
 ox_n,oy_n=shake_offset(gs["shake_nombre"],22,3,2,3)
 if gs["shake_chips"]>0: gs["shake_chips"]-=1
 if gs["shake_mult"]>0: gs["shake_mult"]-=1
 if gs["shake_nombre"]>0: gs["shake_nombre"]-=1
 PrintBox(5,4,40,8,4)
 PrintBox(0,8+int(ox_c),52+int(oy_c),3,2)
 PrintBox(1,41+int(ox_m),52+int(oy_m),3,2)
 spr(242,32,57,0)
 if gs["fase_puntos"]>0:
  tc=int(gs["tot_chips"])
  tm=int(gs["tot_mult"])
  PrintBox(0,8+int(ox_c),52+int(oy_c),3,2)
  draw_text(str(tc),int(12-len(str(tc))*1.5)+8+int(ox_c),57+int(oy_c),6)
  PrintBox(1,41+int(ox_m),52+int(oy_m),3,2)
  draw_text(str(tm),int(12-len(str(tm))*1.5)+41+int(ox_m),57+int(oy_m),3)
  if gs["nombre_mano"]!="":
   draw_text(gs["nombre_mano"],36-int(((len(gs["nombre_mano"])/2)*4-2))+int(ox_n),44+int(oy_n),11)
 if permitir:
  sel=[c for c in gs["hand"] if c.sel]
  if len(sel)>0:
   nm,cb,mb,_=detectar_mano(sel)
   draw_text(nm,36-int(((len(nm)/2)*4-2)),44,11)
   PrintBox(0,8,52,3,2)
   draw_text(str(cb),int(12-len(str(cb))*1.5)+8,57,6)
   PrintBox(1,41,52,3,2)
   draw_text(str(mb),int(12-len(str(mb))*1.5)+41,57,3)

def handle_discard(up):
 voff=gs["voff"]
 disc=Boton("discard",1,145,166-up-voff,4,2,gs["fase_puntos"]==0 and gs["ds"]>0)
 disc.pintar()
 if gs["fase_puntos"]==0 and disc.clicado() and not gs["Clk0"] and gs["ds"]>0 and len(eval_hand())>0:
  n_disc=len([c for c in gs["hand"] if c.sel])
  gs["hand"]=[c for c in gs["hand"] if not c.sel]
  gs["baraja"].repartir()
  gs["ds"]-=1
  positions=[joker_center_xy(ji) for ji in range(len(gs["jokers"]))]
  new_j=[]
  for ji,j in enumerate(gs["jokers"]):
   d=JDEFS[j.id]
   f=d[1]
   if f==F_RAMEN:
    j.xm-=0.01*n_disc
    if j.xm<=1.0: continue
   if f==F_STICKY_M and d[3]==SC_PLAYED:
    if j.st>0:
     j.st-=1
     if ji<len(positions): spawn_particle(positions[ji][0],positions[ji][1],1,"loss_m")
   new_j.append(j)
  gs["jokers"]=new_j
  recalc_hs()

def handle_play(up):
 voff=gs["voff"]
 btn_play=Boton("play",0,95,166-up-voff,4,2,gs["fase_puntos"]==0 and gs["hd"]>0)
 btn_play.pintar()
 if gs["fase_puntos"]==0 and btn_play.clicado() and not gs["Clk0"] and gs["hd"]>0:
  b=eval_hand()
  if len(b)>0:
   nm,cb,mb,sc=detectar_mano(b)
   if splash_active(): sc=b[:]
   gs["b"]=b
   gs["nombre_mano"]=nm
   gs["chips_base_mano"]=cb
   gs["mult_base_mano"]=mb
   gs["scoring_cards"]=sc
   gs["tot_chips"]=cb
   gs["tot_mult"]=mb
   gs["mano_flags"]=calcular_mano_flags(b)
   update_sticky(b,sc,gs["mano_flags"])
   gs["ev_queue"]=build_event_queue(sc)
   gs["ev_idx"]=0
   gs["ev_timer"]=0
   gs["active_joker_idx"]=-1
   gs["fase_puntos"]=1
   gs["shake_nombre"]=22
   gs["hd"]-=1
   for c in b: c.offset_eval=0

def handle_sort(up):
 voff=gs["voff"]
 lbl="Rango" if gs["sort_mode"]==0 else "Palo"
 act=gs["fase_puntos"]==0
 btn=Boton(lbl,3,180,166-up-voff,3,2,act)
 btn.pintar()
 if act and btn.clicado() and not gs["Clk0"]:
  gs["sort_mode"]=1-gs["sort_mode"]
  sort_hand()

def reset_round():
 b=gs["baraja"]
 b.cartas=b.total.copy()
 for c in b.cartas:
  c.sel=False
  c.offset_eval=0
 b.mezclar()
 gs["hand"]=[]
 b.repartir()

def enter_shop():
 gs["voff"]=0
 gs["fase_puntos"]=0
 gs["pack"]=None
 gs["reroll"]=SHOP_BASE_REROLL
 gs["free_rr"]=1 if has_free_reroll() else 0
 roll_shop()
 gs["gm"]=3

def collect_cash_out():
 gs["mn"]+=gs["co_total"]
 gs["rs"]=0
 enter_shop()

def shop_next_round():
 gs["blind"]+=1
 if gs["blind"]>2:
  gs["blind"]=0
  gs["ant"]+=1
 gs["rd"]+=1
 gs["gm"]=4

def start_blind():
 gs["rs"]=0
 gs["hd"]=base_hands()
 gs["ds"]=base_discards()
 gs["voff"]=0
 gs["fase_puntos"]=0
 reset_round()
 gs["gm"]=1

def roll_shop():
 gs["shop_j"]=[]
 for _ in range(2):
  jid=roll_joker()
  gs["shop_j"].append([Joker(jid),joker_price(jid),False])
 gs["shop_p"]=[]
 for _ in range(2):
  r=random.randint(1,100)
  if r<=60: k=0
  elif r<=90: k=1
  else: k=2
  gs["shop_p"].append([k,PACK_DEF[k][2],False])

def do_reroll():
 if gs["free_rr"]>0:
  gs["free_rr"]-=1
 elif gs["mn"]>=gs["reroll"]:
  gs["mn"]-=gs["reroll"]
  gs["reroll"]+=1
 else:
  return
 gs["shop_j"]=[]
 for _ in range(2):
  jid=roll_joker()
  gs["shop_j"].append([Joker(jid),joker_price(jid),False])

def buy_joker(slot):
 if slot>=len(gs["shop_j"]): return
 e=gs["shop_j"][slot]
 if e[2]: return
 if len(gs["jokers"])>=gs["jslots"]: return
 if gs["mn"]<e[1]: return
 gs["mn"]-=e[1]
 gs["jokers"].append(e[0])
 e[2]=True
 recalc_hs()

def open_pack(slot):
 if slot>=len(gs["shop_p"]): return
 e=gs["shop_p"][slot]
 if e[2]: return
 if gs["mn"]<e[1]: return
 k=e[0]
 gs["mn"]-=e[1]
 e[2]=True
 ch=[]
 for _ in range(PACK_DEF[k][0]):
  ch.append(Joker(roll_joker()))
 gs["pack"]={"k":k,"choices":ch,"picks":PACK_DEF[k][1]}

def pack_pick(idx):
 p=gs["pack"]
 if p is None: return
 if idx>=len(p["choices"]): return
 if len(gs["jokers"])>=gs["jslots"]:
  gs["pack"]=None
  return
 gs["jokers"].append(p["choices"].pop(idx))
 recalc_hs()
 p["picks"]-=1
 if p["picks"]<=0 or len(p["choices"])==0: gs["pack"]=None

def pack_skip():
 gs["pack"]=None

def draw_cash_out(oy):
 bx=97
 bw=96
 by=53+oy
 PrintBox(4,bx,by,int(bw/8),2)
 t="CASH OUT: $"+str(gs["co_total"])
 draw_text(t,bx+(bw-len(t)*4)//2,by+6,11)
 px=bx-8
 py=by+20
 pw=112
 circ(px+10,py+12,11,(6,8,3)[gs["blind"]])
 nb=BLIND_NAME[gs["blind"]]
 draw_text(nb,px+13-len(nb)*2,py+9,11)
 draw_text("PUNTUA AL MENOS",px+28,py+5,11)
 draw_text(str(gs["co_req"]),px+28,py+14,2)
 draw_text("$"*gs["co_reward"],px+pw-gs["co_reward"]*4-3,py+10,9)
 draw_text("."*29,px-1,py+21,11)
 draw_text(str(gs["co_hands"]),px,py+30,6)
 draw_text("MANOS RESTANTES",px+6,py+30,11)
 nh=gs["co_hands"]
 if nh>10: nh=10
 draw_text("$"*nh,px+pw-nh*4-3,py+30,9)
 yl=py+40
 if gs["co_disc"]>0:
  draw_text(str(gs["co_disc"]),px,yl,2)
  draw_text("DESCARTES REST.",px+6,yl,11)
  nd=gs["co_disc"]
  if nd>10: nd=10
  draw_text("$"*nd,px+pw-nd*4-3,yl,9)
 else:
  draw_text(str(gs["co_interest"]),px,yl,8)
  draw_text("INTERES 1 POR 5",px+6,yl,11)
  draw_text("$"*gs["co_interest"],px+pw-gs["co_interest"]*4-3,yl,9)
 if gs["co_extra"]>0:
  yl2=py+50
  draw_text("JOKER/BARAJA",px+6,yl2,11)
  ne=gs["co_extra"]
  if ne>10: ne=10
  draw_text("$"*ne,px+pw-ne*4-3,yl2,9)

def draw_side_hud(permitir):
 PrintBox(5,4,25,8,2)
 PrintBox(6,32,29,4,1)
 spr(241,32,30,0)
 draw_text(str(gs["rs"]),42,30,11)
 draw_text("ROUND",10,28,11)
 draw_text("SCORE",10,34,11)
 PrintBox(5,4,71,4,3)
 draw_text("HANDS",13,73,11)
 PrintBox(7,8,78,3,2)
 draw_text(str(gs["hd"]),21,83,7)
 PrintBox(5,36,71,4,3)
 draw_text("Discard",41,73,11)
 PrintBox(7,40,78,3,2)
 draw_text(str(gs["ds"]),53,83,2)
 draw_money_box()
 PrintBox(5,4,111,4,3)
 draw_text("ANTE",14,113,11)
 PrintBox(7,8,118,3,2)
 draw_text(str(gs["ant"]),21,123,7)
 PrintBox(5,36,111,4,3)
 draw_text("ROUND",45,113,11)
 PrintBox(7,40,118,3,2)
 draw_text(str(gs["rd"]),53,123,2)
 draw_score_hud(permitir)

JBOX={
 F_FMUL:("+",1,3),F_HMUL:("+",1,3),F_SMUL:("+",1,3),F_RMUL:("+",1,3),F_SZMUL:("+",1,3),
 F_FCHP:("+",1,6),F_HCHP:("+",1,6),F_SCHP:("+",1,6),F_RCHP:("+",1,6),
 F_XMUL:("x",1,3),F_RXFIRST:("x",1,3),F_HD_LAST_X:("x",1,3),F_HXMUL:("x",1,3),
 F_RAMEN:("x",2,3),F_STENCIL:("xN",None,3),
 F_RTRG:("RTG",None,11),F_DUSK:("RTG",None,11),
 F_CHIP_DISC:("+",3,6),F_NJOK_M:("+",4,3),F_NODISC_M:("+",1,3),F_BULL:("+",5,6),
 F_STICKY_M:("+",6,3),F_STICKY_C:("+",6,6),
 F_RAND_M:("+?",None,3),F_BOOTS:("+",7,3),F_HIKER:("+",1,6),
 F_RCM:("+",8,6),F_SXPROB:("x",1,3),F_SMONEY:("+$",1,9),F_HS_MOD:("+",1,6),
 F_FCHP_DEC:("+",6,6),F_DECK_C:("+",1,6),F_FMUL_DEC:("+",6,3),
 F_EOR_MONEY:("$",1,9),F_EOR_DISC:("$/D",None,9),F_EOR_INT:("INTx2",None,9),
 F_EOR_DECK_RANK:("$/",9,9),F_SPLASH:("ALL",None,11),F_FIRST_RTRG:("RT1",None,11),
 F_HAND_SIZE:("+",10,15),F_BONES:("REV",None,11),F_FREE_REROLL:("RR0",None,9),
}

def _jbox_val(j,d,m):
 if m==1: return str(d[2])
 if m==2: return str(round(j.xm,2))
 if m==3: return str(d[2]*gs["ds"])
 if m==4: return str(d[2]*len(gs["jokers"]))
 if m==5: return str(d[2]*gs["mn"])
 if m==6: return str(j.st)
 if m==7: return str(d[2]*(gs["mn"]//d[3]))
 if m==8: return str(d[2])+"c"
 if m==9: return str(d[3])
 if m==10: return str(d[2])+"H"
 return ""

def draw_joker_box(xj,yj_base,j):
 d=JDEFS[j.id]
 rect(xj,yj_base,16,24,1)
 rectb(xj,yj_base,16,24,14)
 draw_text(d[0][:3].upper(),xj+2,yj_base+3,15)
 f=d[1]
 e=JBOX.get(f)
 if e:
  prefix,m,col=e
  txt=prefix+_jbox_val(j,d,m) if m is not None else prefix
  draw_text(txt,xj+2,yj_base+14,col)
 elif f==F_HELD_R:
  pre="+" if d[4]==0 else "x"
  draw_text(pre+str(d[2]),xj+2,yj_base+14,3)

def PantallaJuego(raton):
 cls()
 voff=gs["voff"]
 fp=gs["fase_puntos"]
 map(60,17,30,17,0,-voff)
 if fp>=2: map(60,0,30,17,0,SCREEN_H-voff)
 gs["up"]=counter(0,gs["up"],50,1,False)
 up=gs["up"]
 spr(189,80,140-up-voff)
 spr(190,80,148-up-voff)
 spr(206,80,156-up-voff)
 for i in range(12):
  spr(190,88+i*8,140-up-voff)
  spr(190,88+i*8,148-up-voff)
  spr(190,88+i*8,156-up-voff)
 spr(191,184,140-up-voff)
 spr(190,184,148-up-voff)
 spr(207,184,156-up-voff)
 permitir_interaccion=(fp==0)
 print_cards(80,140-up-voff,193,gs["hand"],permitir_interaccion)
 draw_text(str(len(gs["hand"]))+"/"+str(gs["hs"]),82,162-up-voff,11)
 draw_text(str(len(gs["jokers"]))+"/"+str(gs["jslots"]),82,29-voff,11)
 draw_text(str(len(gs["consu"]))+"/2",223,29-voff,11)
 draw_text(str(len(gs["baraja"].cartas))+"/52",217,128-voff,11)
 if fp>=2:
  draw_text(str(len(gs["jokers"]))+"/"+str(gs["jslots"]),82,29+SCREEN_H-voff,11)
  draw_text(str(len(gs["consu"]))+"/2",223,29+SCREEN_H-voff,11)
  draw_text(str(len(gs["baraja"].cartas))+"/52",217,128+SCREEN_H-voff,11)
 print_jokers(-voff)
 if fp>=2: print_jokers(SCREEN_H-voff)
 draw_side_hud(permitir_interaccion)
 handle_discard(up)
 handle_play(up)
 handle_sort(up)
 if fp==1:
  update_event_visuals()
  q=gs["ev_queue"]
  if gs["ev_idx"]<len(q) and q[gs["ev_idx"]][0]==E_RISE:
   prog=gs["ev_timer"]/EDUR[E_RISE]
   y=int(83-prog*30)
  else: y=53
  print_cards(80,y,80+(len(gs["b"])*16),gs["b"],False)
  draw_debug()
  step_queue()
 gs["baraja"].mostrar(216,104-voff,1,False,0,0)
 if fp>=2: gs["baraja"].mostrar(216,104+SCREEN_H-voff,1,False,0,0)
 if fp==0 and raton[0]>216 and raton[0]<232 and raton[1]>104 and raton[1]<128 and raton[2] and not gs["Clk0"]:
  gs["gm"]=2
 update_and_draw_particles()
 if fp>=2:
  if fp==2:
   if gs["co_wait"]>0: gs["co_wait"]-=1  # pausa: jokers de fin de ronda
   else:
    gs["voff"]+=CASH_SPEED
    if gs["voff"]>=SCREEN_H:
     gs["voff"]=SCREEN_H
     gs["fase_puntos"]=3
  draw_cash_out(SCREEN_H-gs["voff"])
  if gs["fase_puntos"]==3 and raton[2] and not gs["Clk0"]:
   if raton[0]>=97 and raton[0]<193 and raton[1]>=53 and raton[1]<69:
    collect_cash_out()

def PantallaVisor(raton):
 cls()
 map(30,18,61,35)
 total=Boton(gs["pal"],0,80,118,4,2,True)
 total.pintar()
 if total.clicado() and gs["pal"]=="actual" and not gs["Clk0"]: gs["pal"]="total"
 elif total.clicado() and not gs["Clk0"]: gs["pal"]="actual"
 gs["baraja"].mostrar(12,12,2,False,30,65)
 bg1=Boton(" ",5,59,11,21,12,False)
 bg1.pintar()
 cm=gs["baraja"].muestra(gs["pal"])
 k=(gs["pal"],len(cm))
 if gs["vk"]!=k:
  pi=[]
  co=[]
  tr=[]
  ro=[]
  v=[0]*14
  s=[0,0,0,0]
  can=[0,0,0]
  bys=[pi,co,tr,ro]
  for i in cm:
   if i.va==1: can[0]+=1
   elif i.va in (11,12,13): can[2]+=1
   else: can[1]+=1
   v[i.va]+=1
   bys[i.su].append(i)
   s[i.su]+=1
  for ly in bys: ly.sort(key=lambda c:c.va)
  gs["vc"]=(pi,co,tr,ro,v,s,can)
  gs["vk"]=k
 pi,co,tr,ro,v,s,can=gs["vc"]
 set_col(14,15)
 for i in range(1,14):
  spr(245,50,7+(i*7),0)
  spr(i,49,6+(i*7),0)
  draw_text(str(v[i]),46,8+(i*7),11)
 set_col(14,14)
 for k in range(4):
  sx,sy,tx=(11,77,17) if k<2 else (11,92,17)
  if k%2: sx+=16; tx+=16
  sid=k*16
  spr(sid,sx,sy,0)
  spr(sid,sx+8,sy,0,1,1)
  draw_text(str(s[k]),tx,sy+8,11)
 for k in range(3):
  sids=(1,14,15)
  sxs=(11,22,33)
  txs=(16,24,35)
  spr(sids[k],sxs[k],59 if k==0 else 60,0)
  draw_text(str(can[k]),txs[k],68,11)
 print_cards(60,14,227,pi,False)
 print_cards(60,37,227,ro,False)
 print_cards(60,60,227,tr,False)
 print_cards(60,83,227,co,False)
 if raton[0]>12 and raton[0]<44 and raton[1]>20 and raton[1]<68 and raton[2] and not gs["Clk0"]:
  gs["gm"]=1

def draw_shop_jslot(slot,x,y,raton):
 if slot>=len(gs["shop_j"]): return
 e=gs["shop_j"][slot]
 j=e[0]
 pr=e[1]
 sold=e[2]
 if not sold:
  PrintBox(6,x,y-9,2,1)
  draw_text("$"+str(pr),x+4,y-7,9)
 yj=int(y+onda_y(j.an)*1.2)
 if not dibujar_joker(x,yj,j):
  draw_joker_box(x,yj,j)
 mx=raton[0]
 my=raton[1]
 hv=mx>=x and mx<x+16 and my>=yj and my<yj+24
 if sold:
  draw_text("SOLD",x-1,yj+9,2)
 elif hv:
  gs["tt_target"]=("joker",j,x,yj)
  if raton[2] and not gs["Clk0"]:
   buy_joker(slot)

def draw_shop_pslot(slot,x,y,raton):
 if slot>=len(gs["shop_p"]): return
 e=gs["shop_p"][slot]
 k=e[0]
 pr=e[1]
 sold=e[2]
 if not sold:
  PrintBox(6,x,y-9,2,1)
  draw_text("$"+str(pr),x+4,y-7,9)
 PrintBox(3,x,y,2,3)
 nm=PACK_NAME[k]
 draw_text(nm,x+8-len(nm)*2,y+4,11)
 draw_text("PACK",x+8-8,y+12,15)
 if sold:
  draw_text("OPEN",x-1,y+10,2)
  return
 mx=raton[0]
 my=raton[1]
 hv=mx>=x and mx<x+16 and my>=y and my<y+24
 if hv and raton[2] and not gs["Clk0"]:
  open_pack(slot)

def draw_pack_picker(raton):
 PrintBox(7,72,40,21,9)
 p=gs["pack"]
 if p is None: return
 nm=PACK_NAME[p["k"]]+" PACK"
 draw_text(nm,120-len(nm)*2,45,11)
 et="ELIGE "+str(p["picks"])
 draw_text(et,120-len(et)*2,53,15)
 ch=p["choices"]
 n=len(ch)
 if n>0:
  bx=120-(n*20)//2+2
  mx=raton[0]
  my=raton[1]
  for i in range(n):
   j=ch[i]
   xj=bx+i*20
   yj=int(70+onda_y(j.an)*1.2)
   if not dibujar_joker(xj,yj,j):
    draw_joker_box(xj,yj,j)
   hv=mx>=xj and mx<xj+16 and my>=yj and my<yj+24
   if hv:
    gs["tt_target"]=("joker",j,xj,yj)
    if raton[2] and not gs["Clk0"]:
     pack_pick(i)
     return
 sk=Boton("skip",1,156,108,4,2,True)
 sk.pintar()
 if sk.clicado() and not gs["Clk0"]: pack_skip()

def PantallaTienda(raton):
 cls()
 map(90,0,30,17)
 draw_side_hud(False)
 draw_text(str(len(gs["jokers"]))+"/"+str(gs["jslots"]),82,29,11)
 draw_text(str(len(gs["consu"]))+"/2",223,29,11)
 draw_text(str(len(gs["baraja"].cartas))+"/52",217,128,11)
 print_jokers(0)
 gs["baraja"].mostrar(216,104,1,False,0,0)
 PrintBox(5,130,46,9,5)
 PrintBox(5,146,88,7,5)
 PrintBox(5,86,88,7,5)
 PrintBox(5,90,92,6,4)
 if gs["pack"] is not None:
  draw_pack_picker(raton)
  return
 nr=Boton("next",1,87,48,5,2,True)
 nr.pintar()
 if nr.clicado() and not gs["Clk0"]: shop_next_round()
 if gs["free_rr"]>0: rlbl="rr free"
 else: rlbl="rr $"+str(gs["reroll"])
 act=gs["free_rr"]>0 or gs["mn"]>=gs["reroll"]
 rr=Boton(rlbl,0,87,69,5,2,act)
 rr.pintar()
 if act and rr.clicado() and not gs["Clk0"]: do_reroll()
 draw_shop_jslot(0,142,59,raton)
 draw_shop_jslot(1,173,59,raton)
 draw_shop_pslot(0,155,101,raton)
 draw_shop_pslot(1,178,101,raton)

def blind_panel(bi,x,y,raton):
 sel=(bi==gs["blind"])
 circ(x+24,y+18,11,(6,8,2)[bi])
 nb=BLIND_NAME[bi]
 draw_text(nb,x+27-len(nb)*2,y+15,11)
 req=int(ante_base(gs["ant"])*BLIND_MULT[bi])
 draw_text("PUNTUA",x+15,y+40,11)
 draw_text(str(req),x+27-len(str(req))*2,y+48,2)
 rw=BLIND_REWARD[bi]
 if sel:
  bt=Boton("jugar",4,x+9,y+58,4,2,True)
  bt.pintar()
  if bt.clicado() and not gs["Clk0"]: start_blind()
 else:
  draw_text("$"*rw,x+27-rw*2,y+62,8)

def PantallaBlind(raton):
 cls()
 map(90,17,30,17)
 draw_side_hud(False)
 draw_text(str(len(gs["jokers"]))+"/"+str(gs["jslots"]),82,29,11)
 draw_text(str(len(gs["consu"]))+"/2",223,29,11)
 print_jokers(0)
 blind_panel(0,79,52,raton)
 blind_panel(1,136,52,raton)
 blind_panel(2,192,52,raton)

def PantallaGameOver(raton):
 cls(0)
 draw_text("GAME OVER",106,40,2)
 draw_text("ANTE "+str(gs["ant"])+" RONDA "+str(gs["rd"]),100,56,11)
 draw_text("$"+str(gs["mn"]),114,68,9)
 bt=Boton("menu",4,102,90,4,2,True)
 bt.pintar()
 if bt.clicado() and not gs["Clk0"]:
  gs["gm"]=0
  gs["hand"]=[]
  gs["b"]=[]
  gs["jokers"]=[]
  gs["consu"]=[]
  gs["pack"]=None
  gs["baraja"]=Mazo(gs["DS"])

gs["baraja"]=Mazo(gs["DS"])

def TIC():
 gs["tt_target"]=None
 raton=mouse()
 gm=gs["gm"]
 if gm==0: PantallaMenu(raton)
 elif gm==1: PantallaJuego(raton)
 elif gm==2: PantallaVisor(raton)
 elif gm==3: PantallaTienda(raton)
 elif gm==4: PantallaBlind(raton)
 elif gm==5: PantallaGameOver(raton)
 tt=gs["tt_target"]
 if tt:
  if tt[0]=="card": tt_card(tt[1],tt[2],tt[3])
  elif tt[0]=="joker": tt_joker(tt[1],tt[2],tt[3])
 gs["Clk0"]=raton[2]
