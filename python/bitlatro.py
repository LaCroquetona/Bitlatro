# title:   Bitlatro
# author:  Croquetona
# desc:    this is a compact version of Balatro 
# license: MIT License (change this to your license of choice)
# version: 0.2.1
# script:  python

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
 "[":["110","100","100","100","110"],
 "]":["011","001","001","001","011"],
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

gs = {
    "gm":               0,
    "DS":               0,
    "Clk0":             False,
    "num1":             random.randint(0,7)+17,
    "num2":             random.randint(0,3)*16,
    "baraja":           None,
    "jokers":           [],
    "consu":            [],
    "hand":             [],
    "b":                [],
    "anim":             0,
    "up":               0,
    "pal":              "total",
    "fase_puntos":      0,
    "tot_chips":        0,
    "tot_mult":         1,
    "carta_actual_idx": 0,
    "timer_fase":       0,
    "scoring_cards":    [],
    "nombre_mano":      "",
    "chips_base_mano":  0,
    "mult_base_mano":   0,
    "vc":               None,
    "vk":               None,
    "rs":               0,
    "hd":               4,
    "ds":               4,
    "mn":               4,
    "ant":              1,
    "rd":               1,
    "ev_queue":         [],
    "ev_idx":           0,
    "ev_timer":         0,
    "active_joker_idx": -1,
    "mano_flags":       [False]*7,
    "first_match":      {},
    "particles":        [],
    "shake_chips":      0,
    "shake_mult":       0,
    "shake_nombre":     0,
}
handsize=8

DEBUG=False

# === EVENTOS ===
E_RISE=0
E_OPLAY=1
E_CSCORE=2
E_OSCORE=3
E_IND=4
E_FINAL=5
EDUR=[30,18,22,15,20,50]

# === FAMILIAS DE JOKER ===
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

# === TIPOS DE MANO ===
H_PAR=0
H_DPA=1
H_TRI=2
H_ESC=3
H_COL=4
H_FUL=5
H_POK=6

# (nombre, familia, *params)
JDEFS=[
 # Jokers clasicos (vanilla)
 ("Joker",    F_FMUL,4),
 ("Jolly",    F_HMUL,8,H_PAR),
 ("Zany",     F_HMUL,12,H_TRI),
 ("Mad",      F_HMUL,10,H_DPA),
 ("Crazy",    F_HMUL,12,H_ESC),
 ("Droll",    F_HMUL,10,H_COL),
 ("Sly",      F_HCHP,50,H_PAR),
 ("Wily",     F_HCHP,100,H_TRI),
 ("Clever",   F_HCHP,80,H_DPA),
 ("Devious",  F_HCHP,100,H_ESC),
 ("Crafty",   F_HCHP,80,H_COL),
 ("Greedy",   F_SMUL,3,3),
 ("Lusty",    F_SMUL,3,1),
 ("Wrath",    F_SMUL,3,0),
 ("Glut",     F_SMUL,3,2),
 ("Scholar",  F_RCHP,20,(1,)),
 ("Smiley",   F_RMUL,5,(11,12,13)),
 ("Even",     F_RMUL,4,(2,4,6,8,10)),
 ("Odd",      F_RCHP,31,(1,3,5,7,9)),
 ("Sock",     F_RTRG,(11,12,13)),
 ("Gross",    F_FMUL,15),
 ("Half",     F_SZMUL,20,3),
 ("Photo",    F_RXFIRST,2,(11,12,13)),
 ("Stencil",  F_STENCIL,0),
 # NUEVOS JOKERS
 ("Fibon",    F_RMUL,8,(1,2,3,5,8)), # Fibonacci: +8 Mult a A,2,3,5,8
 ("Hack",     F_RTRG,(2,3,4,5)),     # Retrigger 2..5
 ("Arrow",    F_SCHP,50,0),          # +50 chips si Picas
 ("Blood",    F_SMUL,4,1),           # +4 Mult si Corazones
 ("Banner",   F_CHIP_DISC,40),       # +40 chips por descarte restante
]

JSPR={
 # ---Base--- #
 0:(2,394),
 # ---Reskins de Jimbo--- #
 1:(3,2,394,[(3,6),(8,7)]),
 2:(3,2,394,[(3,1),(8,5)]),
 3:(3,2,394,[(3,2),(8,3),(6,3),(7,2)]),
 4:(3,2,394,[(3,2),(8,7),(6,10),(7,9)]),
 5:(3,2,394,[(8,14),(6,12),(7,13)]),
 # ---Originales--- #
 19:(0,262),
 20:(2,392),
 21:(1,356),
 22:(1,352),
 23:(2,390),
}

def onda_y(an):
 t=time()
 return math.sin((t+an)/250)*0.75+math.sin((t+an)/150)*0.3

def shake_offset(fl,du,ax,ay,fr):
 # Onda amortiguada: sin*decay. fl=frames_left, du=dur, fr=freq.
 if fl<=0:
  return (0,0)
 t=du-fl
 k=fl/du
 a=(t/du)*fr*math.pi*2
 return (math.sin(a)*ax*k, math.sin(a*1.3+1)*ay*k)

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
  spr(17,x+8, y,0,1,1)
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
   if cur>end:
    cur=end
  elif cur>end:
   cur-=inc
   if cur<end:
    cur=end
 elif rep:
  cur=st
 return cur

class Boton:
 paletas={
  0:(7,6),
  1:(2,3),
  2:(0,1),
  3:(11,13),
  4:(10,8),
  5:(13,15),
  6:(15,15),
  7:(15,13),
  8:(13,13)
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
      if h==1:
       spr(244,x,y,0)
      else:
       spr(243,x,y+(j*8),0,1,2)
      if not prs:
       line(x+1,y+(j*8)+8,x+7,y+(j*8)+8,bor)
       pix(x,y+(j*8)+7,bor)
     elif j==0:
      spr(243,x,y,0)
     else:
      spr(227,x,y+(j*8),0,1,0,3)
    elif i==w-1:
     if j==h-1:
      if h==1:
       spr(244,x+(i*8),y+(j*8),0,1,0,2)
      else:
       spr(243,x+(i*8),y+(j*8),0,1,0,2)
      if not prs:
       line(x+(i*8),y+(j*8)+8,x+(i*8)+6,y+(j*8)+8,bor)
       pix(x+(i*8)+7,y+(j*8)+7,bor)
     elif j==0:
      spr(243,x+(i*8),y,0,1,1)
     else:
      spr(227,x+(i*8),y+(j*8),0,1,0,1)
    else:
     if j==h-1:
      if h==1:
       spr(228,x+(i*8),y+(j*8),0)
      else:
       spr(227,x+(i*8),y+(j*8),0,1,2)
      if not prs:
       line(x+(i*8),y+(j*8)+8,x+(i*8)+8,y+(j*8)+8,bor)
     elif j==0:
      spr(227,x+(i*8),y,0)
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
     if h==1:
      spr(244,x,y,0)
     else:
      spr(243,x,y+(j*8),0,1,2)
    elif j==0:
     spr(243,x,y,0)
    else:
     spr(227,x,y+(j*8),0,1,0,3)
   elif i==w-1:
    if j==h-1:
     if h==1:
      spr(244,x+(i*8),y+(j*8),0,1,0,2)
     else:
      spr(243,x+(i*8),y+(j*8),0,1,0,2)
    elif j==0:
     spr(243,x+(i*8),y,0,1,1)
    else:
     spr(227,x+(i*8),y+(j*8),0,1,0,1)
   else:
    if j==h-1:
     if h==1:
      spr(228,x+(i*8),y+(j*8),0)
     else:
      spr(227,x+(i*8),y+(j*8),0,1,2)
    elif j==0:
     spr(227,x+(i*8),y,0)
    else:
     spr(227,x+(i*8),y+(j*8),0)
     line(x+(i*8),y+(j*8),x+(i*8)+8,y+(j*8),iner)
 reset_col()

class Carta:
 def __init__(self,dt,suit,value,effect,stamp,edition):
  self.dt=dt
  self.su=suit
  self.va=value
  self.ef=effect
  self.st=stamp
  self.ed=edition
  self.an=random.randint(0,1000)
  if self.ed==1:
   self.ed=random.randint(1,5)
  elif self.ed==2:
   self.ed=random.randint(49,53)
  self.x=0
  self.y=0
  self.sel=False
  self.offset_eval=0

class Joker:
 def __init__(self,type_id):
  self.id=type_id
  self.st=0
  self.an=random.randint(0,1000)

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
  x2=x+s*8
  set_col(2,2)
  if dt==0:
   spr(64,x,y,0,s,0,0,1,3)
   spr(64,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("tienes un",txx,txy,2)
    draw_text("descarte mas",txx,txy+8,2)
  elif dt==1:
   set_col(2,7)
   spr(64,x,y,0,s,0,0,1,3)
   spr(64,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("tienes una",txx,txy,7)
    draw_text("mano mas",txx,txy+8,7)
  elif dt==2:
   set_col(2,1)
   spr(64,x,y,0,s,0,0,1,3)
   spr(64,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("no genera interese,",txx,txy,1)
    draw_text("2$ por mano y 1$ por",txx,txy+8,1)
    draw_text("descarte restante",txx,txy+16,1)
  elif dt==3:
   set_col(2,8)
   spr(64,x,y,0,s,0,0,1,3)
   spr(64,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("comienzas con 10$",txx,txy,8)
  elif dt==4:
   set_col(2,15)
   spr(64,x,y,0,s,0,0,1,3)
   spr(64,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("tienes un joker",txx,txy,14)
    draw_text("mas, pero una",txx,txy+8,14)
    draw_text("mano menos",txx,txy+16,14)
  elif dt==5:
   spr(65,x,y,0,s,0,0,1,3)
   spr(65,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("una baraja que",txx,txy,2)
    draw_text("solo tiene picas",txx,txy+8,14)
    draw_text("y corazones",txx,txy+16,2)
  elif dt==6:
   spr(66,x,y,0,s,0,0,1,3)
   spr(66,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("una baraja",txx,txy,9)
    draw_text("con numeros",txx,txy+8,10)
    draw_text("del 1 al 10",txx,txy+16,9)
  elif dt==7:
   spr(67,x,y,0,s,0,0,1,3)
   spr(67,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("baraja de 52 cartas",txx,txy,8)
    draw_text("pero los numeros",txx,txy+8,3)
    draw_text("estan randomizados",txx,txy+16,7)
  reset_col()
 def muestra(self,pal):
  if pal=="total":
   return self.total
  else:
   return self.cartas
 def mezclar(self):
  random.shuffle(self.cartas)
 def ordenar(self):
  self.cartas.sort(key=lambda c:c.va)
 def repartir(self):
  hand=gs["hand"]
  while len(hand)<handsize and len(self.cartas)>0:
   hand.append(self.cartas.pop(0))
  hand.sort(key=lambda c:c.va)

def print_cards(x,y,xf,cards,permite_seleccion):
 b=gs["b"]
 hand=gs["hand"]
 if len(cards)==0:
  return
 con=0
 if len(cards)==1:
  sep=0
 else:
  sep=(xf-x-17)/(len(cards)-1)
 dec=0
 for i in cards:
  dec+=sep-int(sep)
  xc=int(x+con*int(sep)+int(dec))
  onda1=math.sin((time()+i.an)/250)*0.75
  onda2=math.sin((time()+i.an)/150)*0.3
  yc=int(y+onda1+onda2+i.y-i.offset_eval)
  if not permite_seleccion:
   i.sel=False
   i.y=0
  if permite_seleccion and mouse()[0]>xc and mouse()[0]<xc+16 and mouse()[1]>yc and mouse()[1]<yc+23:
   yc-=6
   if mouse()[2]:
    yc+=2
    if len([c for c in gs["hand"] if c.sel])<5 or i.sel:
     i.sel=True
     i.y=-4
   if i.sel and mouse()[4]:
    yc-=2
    i.sel=False
    i.y=0
  con+=1
  if i in b and cards is hand:
   continue
  cs=i.su*16
  cv=i.va
  ce=i.ef+17
  cm=i.st+59
  ced=int(i.ed)+112
  spr(ce,xc,yc,0,1,0,0,1,3)
  spr(ce,xc+8,yc,0,1,0,2,1,3)
  spr(cs,xc,yc+8,0)
  spr(cs,xc+8,yc+8,0,1,1)
  if i.su%2==1:
   set_col(14,2)
  spr(cv,xc,yc,0)
  spr(cv,xc+8,yc+16,0,1,0,2)
  set_col(14,14)
  spr(cm,xc+8,yc,0)
  if i.ed!=0:
   if i.ed<10:
    i.ed=counter(1,i.ed,5,0.125,True)
   else:
    i.ed=counter(49,i.ed,53,0.125,True)
   spr(ced,xc,yc,0,1,0,0,1,3)
   spr(ced,xc+8,yc,0,1,0,2,1,3)

def eval_hand():
 return [c for c in gs["hand"] if c.sel]

def obtener_chips_carta(card):
 if card.va==1:
  return 11
 elif card.va>=11:
  return 10
 return card.va

def detectar_mano(cartas):
 if len(cartas)==0:
  return ("",0,0,[])
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
  if not es_escalera and vals_ord==[1,2,3,4,5]:
   es_escalera=True
 if es_escalera and es_color:
  return ("ESCALERA DE COLOR",100,8,cartas[:])
 elif grupos[0]==4:
  sc=[c for c in cartas if conteo_val[c.va]==4]
  return ("POKER",60,7,sc)
 elif len(grupos)>=2 and grupos[0]==3 and grupos[1]==2:
  return ("FULL HOUSE",40,4,cartas[:])
 elif es_color:
  return ("COLOR",35,4,cartas[:])
 elif es_escalera:
  return ("ESCALERA",30,4,cartas[:])
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

# === SISTEMA DE PARTICULAS ===
# (color_rombo, prefijo). Numero en blanco (15).
PARTICLE_KINDS={
 "chip":(6,""),     # azul: +chips
 "mult":(3,"+"),    # rojo claro: +mult
 "xmult":(2,"x"),   # rojo oscuro: xmult
 "trigger":(9,""),  # naranja: retrigger activado (texto "TRIGER")
}

def draw_diamond(cx,cy,w,h,col):
 hw=w//2
 hh=h//2
 if hw<=0 or hh<=0:
  return
 tri(cx-hw,cy,cx,cy-hh,cx+hw,cy,col)
 tri(cx-hw,cy,cx,cy+hh,cx+hw,cy,col)

def card_center_xy(ci):
 c=gs["scoring_cards"][ci]
 b=gs["b"]
 if c not in b:
  return (128,53)
 idx=b.index(c)
 n=len(b)
 sep=(n*16-17)/(n-1) if n>1 else 0
 return (int(80+idx*sep)+8,53)

def joker_center_xy(ji):
 n=len(gs["jokers"])
 sep=(172-83-16)/(n-1) if n>1 else 0
 return (int(83+ji*sep)+8,20)

def spawn_particle(cx,cy,value,kind):
 gs["particles"].append({"x":cx,"y":cy,"life":45,"max_life":45,"value":value,"kind":kind})
 if kind=="chip":
  gs["shake_chips"]=15
 elif kind=="mult" or kind=="xmult":
  gs["shake_mult"]=15
 # "trigger" no activa shake: viaja junto a un chip que ya lo hace

def spawn_for_joker(ji):
 j=gs["jokers"][ji]
 d=JDEFS[j.id]
 f=d[1]
 cx,cy=joker_center_xy(ji)
 if f in (F_FMUL,F_HMUL,F_SMUL,F_RMUL,F_SZMUL):
  spawn_particle(cx,cy,d[2],"mult")
 elif f in (F_FCHP,F_HCHP,F_SCHP,F_RCHP):
  spawn_particle(cx,cy,d[2],"chip")
 elif f==F_XMUL or f==F_RXFIRST:
  spawn_particle(cx,cy,d[2],"xmult")
 elif f==F_STENCIL:
  empty=max(1,5-len(gs["jokers"]))
  spawn_particle(cx,cy,empty,"xmult")
 elif f==F_CHIP_DISC:
  spawn_particle(cx,cy,d[2]*gs["ds"],"chip")

def update_and_draw_particles():
 alive=[]
 for p in gs["particles"]:
  ml=p["max_life"]
  r=(ml-p["life"])/ml
  if r<0.2:
   s=r/0.2
  elif r<0.7:
   s=1.0
  else:
   s=1.0-(r-0.7)/0.3
  cx=int(p["x"])
  cy=int(p["y"]-r*6)
  col,prefix=PARTICLE_KINDS[p["kind"]]
  txt=prefix+str(p["value"])
  w=int(max(18,len(txt)*4+6)*s)
  h=int(10*s)
  draw_diamond(cx,cy,w,h,col)
  if s>0.5:
   draw_text(txt,cx-len(txt)*2+1,cy-2,15)
  p["life"]-=1
  if p["life"]>0:
   alive.append(p)
 gs["particles"]=alive

# === SISTEMA DE JOKERS Y COLA DE EVENTOS ===

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

def joker_fires_play(j):
 return False

def joker_fires_score(j,card):
 d=JDEFS[j.id]
 f=d[1]
 if f==F_SMUL or f==F_SCHP:
  return card.su==d[3]
 if f==F_RMUL or f==F_RCHP:
  return card.va in d[3]
 return False

def joker_fires_ind(j):
 d=JDEFS[j.id]
 f=d[1]
 if f==F_FMUL or f==F_FCHP or f==F_XMUL or f==F_STENCIL or f==F_CHIP_DISC:
  return True
 if f==F_HMUL or f==F_HCHP:
  return gs["mano_flags"][d[3]]
 if f==F_SZMUL:
  return len(gs["b"])<=d[3]
 return False

def count_retriggers(card):
 n=0
 for ji,j in enumerate(gs["jokers"]):
  d=JDEFS[j.id]
  if d[1]==F_RTRG and card.va in d[2]:
   n+=1
 return n

def apply_joker_effect(j):
 d=JDEFS[j.id]
 f=d[1]
 if f==F_FMUL or f==F_HMUL or f==F_SMUL or f==F_RMUL or f==F_SZMUL:
  gs["tot_mult"]+=d[2]
 elif f==F_FCHP or f==F_HCHP or f==F_SCHP or f==F_RCHP:
  gs["tot_chips"]+=d[2]
 elif f==F_XMUL or f==F_RXFIRST:
  gs["tot_mult"]*=d[2]
 elif f==F_STENCIL:
  empty=max(1,5-len(gs["jokers"]))
  gs["tot_mult"]*=empty
 elif f==F_CHIP_DISC:
  gs["tot_chips"]+=(d[2]*gs["ds"])

def apply_event(e):
 et=e[0]
 if et==E_CSCORE:
  ci=e[1]
  c=gs["scoring_cards"][ci]
  chips=obtener_chips_carta(c)
  gs["tot_chips"]+=chips
  cx,cy=card_center_xy(ci)
  is_rt=len(e)>2 and e[2]
  spawn_particle(cx,cy,chips,"chip")
  if is_rt:
   spawn_particle(cx,cy-12,"TRIGER","trigger")
 elif et==E_OPLAY:
  apply_joker_effect(gs["jokers"][e[1]])
  spawn_for_joker(e[1])
 elif et==E_OSCORE:
  ji,ci=e[1]
  apply_joker_effect(gs["jokers"][ji])
  spawn_for_joker(ji)
 elif et==E_IND:
  apply_joker_effect(gs["jokers"][e[1]])
  spawn_for_joker(e[1])

def build_event_queue(scoring):
 q=[[E_RISE,None]]
 fm={}
 for ji,j in enumerate(gs["jokers"]):
  d=JDEFS[j.id]
  if d[1]==F_RXFIRST:
   for ci,c in enumerate(scoring):
    if c.va in d[3]:
     fm[ji]=ci
     break
 gs["first_match"]=fm
 for ji,j in enumerate(gs["jokers"]):
  if joker_fires_play(j):
   q.append([E_OPLAY,ji])
 for ci,c in enumerate(scoring):
  rt=count_retriggers(c)
  for r in range(1+rt):
   q.append([E_CSCORE,ci,r>0])
   for ji,j in enumerate(gs["jokers"]):
    if joker_fires_score(j,c) or fm.get(ji)==ci:
     q.append([E_OSCORE,(ji,ci)])
 for ji,j in enumerate(gs["jokers"]):
  if joker_fires_ind(j):
   q.append([E_IND,ji])
 q.append([E_FINAL,None])
 return q

def finalize_score():
 gs["rs"]+=int(gs["tot_chips"]*gs["tot_mult"])
 gs["hand"]=[c for c in gs["hand"] if c not in gs["b"]]
 gs["baraja"].repartir()
 gs["b"]=[]
 gs["scoring_cards"]=[]
 gs["ev_queue"]=[]
 gs["ev_idx"]=0
 gs["ev_timer"]=0
 gs["active_joker_idx"]=-1
 gs["fase_puntos"]=0

def step_queue():
 q=gs["ev_queue"]
 if gs["ev_idx"]>=len(q):
  if DEBUG:
   if btnp(4):
    finalize_score()
  else:
   finalize_score()
  return
 e=q[gs["ev_idx"]]
 if gs["ev_timer"]==0:
  apply_event(e)
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
 for c in gs["b"]:
  c.offset_eval=0
 gs["active_joker_idx"]=-1
 q=gs["ev_queue"]
 if gs["ev_idx"]>=len(q):
  return
 e=q[gs["ev_idx"]]
 et=e[0]
 if DEBUG:
  bounce=6
 else:
  prog=min(1.0,gs["ev_timer"]/EDUR[et]) if EDUR[et]>0 else 1.0
  bounce=int(math.sin(prog*math.pi)*6)
 if et==E_CSCORE:
  ci=e[1]
  if ci<len(gs["scoring_cards"]):
   gs["scoring_cards"][ci].offset_eval=bounce
  if len(e)>2 and e[2]:
   c=gs["scoring_cards"][ci]
   for ji,j in enumerate(gs["jokers"]):
    d=JDEFS[j.id]
    if d[1]==F_RTRG and c.va in d[2]:
     gs["active_joker_idx"]=ji
     break
 elif et==E_OSCORE:
  ji,ci=e[1]
  gs["active_joker_idx"]=ji
  if ci<len(gs["scoring_cards"]):
   gs["scoring_cards"][ci].offset_eval=bounce//2
 elif et==E_OPLAY or et==E_IND:
  gs["active_joker_idx"]=e[1]

def get_event_name(e):
 RANK=["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
 SUIT=["P","C","T","R"]
 et=e[0]
 if et==E_RISE:  return "RISE"
 if et==E_FINAL: return "FINAL"
 if et==E_CSCORE:
  c=gs["scoring_cards"][e[1]]
  isrt=len(e)>2 and e[2]
  pre="RTRG " if isrt else "CARD "
  return pre+RANK[c.va-1]+SUIT[c.su]+" "+str(obtener_chips_carta(c))+"CH"
 if et==E_OPLAY:
  return "OPLAY:"+JDEFS[gs["jokers"][e[1]].id][0][:6].upper()
 if et==E_IND:
  return "IND:"+JDEFS[gs["jokers"][e[1]].id][0][:7].upper()
 if et==E_OSCORE:
  ji,ci=e[1]
  c=gs["scoring_cards"][ci]
  return "SCORE:"+JDEFS[gs["jokers"][ji].id][0][:5].upper()+"/"+RANK[c.va-1]
 return "?"

def draw_debug():
 if not DEBUG or gs["fase_puntos"]==0:
  return
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

def print_jokers():
 reset_col()
 bx=83
 by=8
 xf=172
 ai=gs["active_joker_idx"]
 n=len(gs["jokers"])
 if n==0:
  return
 if n==1:
  sep=0
 else:
  sep=(xf-bx-16)/(n-1)
 con=0
 dec=0
 for j in gs["jokers"]:
  dec+=sep-int(sep)
  xj=int(bx+con*int(sep)+int(dec))
  yj=int(by+onda_y(j.an)*1.2)-(4 if ai==con else 0)
  con+=1
  d=JDEFS[j.id]
  if dibujar_joker(xj,yj,j):
   if ai==con-1:
    rectb(xj-1,yj-1,18,26,15)
  else:
   rect(xj,yj,16,24,1)
   rectb(xj,yj,16,24,15 if ai==con-1 else 14)
   nm=d[0][:3].upper()
   draw_text(nm,xj+2,yj+3,15)
   f=d[1]
   if f in (F_FMUL,F_HMUL,F_SMUL,F_RMUL,F_SZMUL):
    draw_text("+"+str(d[2]),xj+2,yj+14,3)
   elif f in (F_FCHP,F_HCHP,F_SCHP,F_RCHP):
    draw_text("+"+str(d[2]),xj+2,yj+14,6)
   elif f==F_XMUL or f==F_RXFIRST:
    draw_text("x"+str(d[2]),xj+2,yj+14,3)
   elif f==F_STENCIL:
    draw_text("xN",xj+2,yj+14,3)
   elif f==F_RTRG:
    draw_text("RTG",xj+2,yj+14,11)
   elif f==F_CHIP_DISC:
    bono_actual=d[2]*gs["ds"]
    draw_text("+"+str(bono_actual),xj+2,yj+14,6)

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
 if gs["num2"] in (16,48):
  set_col(14,2)
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
 if btn_prev.clicado() and not gs["Clk0"]:
  gs["DS"]=(gs["DS"]+7)%8
 btn_next=Boton(" >",0,150,95,3,2,True)
 btn_next.pintar()
 if btn_next.clicado() and not gs["Clk0"]:
  gs["DS"]=(gs["DS"]+1)%8
 if gs["DS"]!=prev_DS:
  gs["baraja"]=Mazo(gs["DS"])
 play=Boton("play",4,125,95,3,2,True)
 play.pintar()
 if play.clicado() and not gs["Clk0"]:
  gs["gm"]=1
  gs["fase_puntos"]=0
  gs["rs"]=0
  gs["hd"]=4
  gs["ds"]=4
  gs["mn"]=4
  gs["ant"]=1
  gs["rd"]=1
  gs["vk"]=None
  gs["particles"]=[]
  gs["shake_chips"]=0
  gs["shake_mult"]=0
  gs["shake_nombre"]=0
  gs["baraja"].generar_mazo()
  gs["baraja"].mezclar()
  gs["baraja"].repartir()
  # === CONFIGURACIÓN DE JOKERS INICIAL EN LA PRUEBA ===
  gs["jokers"]=[Joker(0),Joker(19),Joker(22),Joker(20)]

def PantallaJuego(raton):
 cls()
 map(30,0,60,17)
 gs["up"]=counter(0,gs["up"],50,1,False)
 up=gs["up"]
 spr(189,80,140-up)
 spr(190,80,148-up)
 spr(206,80,156-up)
 for i in range(12):
  spr(190,88+i*8,140-up)
  spr(190,88+i*8,148-up)
  spr(190,88+i*8,156-up)
 spr(191,184,140-up)
 spr(190,184,148-up)
 spr(207,184,156-up)
 permitir_interaccion=(gs["fase_puntos"]==0)
 print_cards(80,140-up,193,gs["hand"],permitir_interaccion)
 draw_text(str(len(gs["hand"]))+"/8",82,162-up,11)
 draw_text(str(len(gs["jokers"]))+"/5",82,29,11)
 draw_text(str(len(gs["consu"]))+"/2",223,29,11)
 draw_text(str(len(gs["baraja"].cartas))+"/52",217,128,11)
 print_jokers()
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
 PrintBox(8,4,95,8,2)
 pix(5,96,15)
 line(4,97,4,110,15)
 pix(5,111,15)
 pix(66,96,15)
 line(67,97,67,110,15)
 pix(66,111,15)
 PrintBox(7,8,95,7,2)
 draw_text("$"+str(gs["mn"]),31,100,9)
 PrintBox(5,4,111,4,3)
 draw_text("ANTE",14,113,11)
 PrintBox(7,8,118,3,2)
 draw_text(str(gs["ant"]),21,123,7)
 PrintBox(5,36,111,4,3)
 draw_text("ROUND",45,113,11)
 PrintBox(7,40,118,3,2)
 draw_text(str(gs["rd"]),53,123,2)
 # HUD chips/mult/nombre con shake amortiguado
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
   nm=gs["nombre_mano"]
   draw_text(nm,36-int(((len(nm)/2)*4-2))+int(ox_n),44+int(oy_n),11)
 if permitir_interaccion:
  cartas_sel=[c for c in gs["hand"] if c.sel]
  if len(cartas_sel)>0:
   nm,cb,mb,_=detectar_mano(cartas_sel)
   draw_text(nm,36-int(((len(nm)/2)*4-2)),44,11)
   PrintBox(0,8,52,3,2)
   draw_text(str(cb),int(12-len(str(cb))*1.5)+8,57,6)
   PrintBox(1,41,52,3,2)
   draw_text(str(mb),int(12-len(str(mb))*1.5)+41,57,3)
 disc=Boton("discard",1,145,166-up,4,2,permitir_interaccion and gs["ds"]>0)
 disc.pintar()
 if permitir_interaccion and disc.clicado() and not gs["Clk0"] and gs["ds"]>0 and len(eval_hand())>0:
  gs["hand"]=[c for c in gs["hand"] if not c.sel]
  gs["baraja"].repartir()
  gs["ds"]-=1
 btn_play=Boton("play",0,95,166-up,4,2,permitir_interaccion and gs["hd"]>0)
 btn_play.pintar()
 if permitir_interaccion and btn_play.clicado() and not gs["Clk0"] and gs["hd"]>0:
  b=eval_hand()
  if len(b)>0:
   nm,cb,mb,sc=detectar_mano(b)
   gs["b"]=b
   gs["nombre_mano"]=nm
   gs["chips_base_mano"]=cb
   gs["mult_base_mano"]=mb
   gs["scoring_cards"]=sc
   gs["tot_chips"]=cb
   gs["tot_mult"]=mb
   gs["mano_flags"]=calcular_mano_flags(b)
   gs["ev_queue"]=build_event_queue(sc)
   gs["ev_idx"]=0
   gs["ev_timer"]=0
   gs["active_joker_idx"]=-1
   gs["fase_puntos"]=1
   gs["shake_nombre"]=22
   gs["hd"]-=1
   for c in b:
    c.offset_eval=0
 if gs["fase_puntos"]==1:
  update_event_visuals()
  q=gs["ev_queue"]
  if gs["ev_idx"]<len(q) and q[gs["ev_idx"]][0]==E_RISE:
   prog=gs["ev_timer"]/EDUR[E_RISE]
   y=int(83-prog*30)
  else:
   y=53
  print_cards(80,y,80+(len(gs["b"])*16),gs["b"],False)
  draw_debug()
  step_queue()
 gs["baraja"].mostrar(216,104,1,False,0,0)
 if raton[0]>216 and raton[0]<232 and raton[1]>104 and raton[1]<128 and raton[2] and not gs["Clk0"]:
  gs["gm"]=2
 update_and_draw_particles()

def PantallaVisor(raton):
 cls()
 map(30,18,61,35)
 total=Boton(gs["pal"],0,80,118,4,2,True)
 total.pintar()
 if total.clicado() and gs["pal"]=="actual" and not gs["Clk0"]:
  gs["pal"]="total"
 elif total.clicado() and not gs["Clk0"]:
  gs["pal"]="actual"
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
  for i in cm:
   if i.va==1:
    can[0]+=1
   elif i.va in (11,12,13):
    can[2]+=1
   else:
    can[1]+=1
   v[i.va]+=1
   if i.su==0:
    pi.append(i)
    s[0]+=1
   elif i.su==1:
    co.append(i)
    s[1]+=1
   elif i.su==2:
    tr.append(i)
    s[2]+=1
   elif i.su==3:
    ro.append(i)
    s[3]+=1
  gs["vc"]=(pi,co,tr,ro,v,s,can)
  gs["vk"]=k
 pi,co,tr,ro,v,s,can=gs["vc"]
 set_col(14,15)
 for i in range(1,14):
  spr(245,50,7+(i*7),0)
  spr(i,49,6+(i*7),0)
  draw_text(str(v[i]),46,8+(i*7),11)
 set_col(14,14)
 spr(0,11,77,0)
 spr(0,19,77,0,1,1)
 draw_text(str(s[0]),17,85,11)
 spr(16,27,77,0)
 spr(16,35,77,0,1,1)
 draw_text(str(s[1]),33,85,11)
 spr(32,11,92,0)
 spr(32,19,92,0,1,1)
 draw_text(str(s[2]),17,100,11)
 spr(48,27,92,0)
 spr(48,35,92,0,1,1)
 draw_text(str(s[3]),33,100,11)
 spr(1,11,59,0)
 draw_text(str(can[0]),16,68,11)
 spr(14,22,60,0)
 draw_text(str(can[1]),24,68,11)
 spr(15,33,60,0)
 draw_text(str(can[2]),35,68,11)
 print_cards(60,14,227,pi,False)
 print_cards(60,37,227,ro,False)
 print_cards(60,60,227,tr,False)
 print_cards(60,83,227,co,False)
 if raton[0]>12 and raton[0]<44 and raton[1]>20 and raton[1]<68 and raton[2] and not gs["Clk0"]:
  gs["gm"]=1

gs["baraja"]=Mazo(gs["DS"])

def TIC():
 raton=mouse()
 gm=gs["gm"]
 if gm==0:
  PantallaMenu(raton)
 elif gm==1:
  PantallaJuego(raton)
 elif gm==2:
  PantallaVisor(raton)
 gs["Clk0"]=raton[2]
