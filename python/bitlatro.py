# title:   Bitlatro
# author:  La_Croquetona.
# desc:    this is a compact version of Balatro taking my own liberties. 
# license: MIT License (change this to your license of choice)
# version: 0.1.0
# script:  python

import random
import math

DS=0#Deck selection
handsize=8

#-mini fuente-#
mini_font = {
    "A": ["010","101","111","101","101"],
    "B": ["110","101","110","101","110"],
    "C": ["011","100","100","100","011"],
    "D": ["110","101","101","101","110"],
    "E": ["111","100","110","100","111"],
    "F": ["111","100","110","100","100"],
    "G": ["011","100","101","101","011"],
    "H": ["101","101","111","101","101"],
    "I": ["111","010","010","010","111"],
    "J": ["001","001","001","101","010"],
    "K": ["101","101","110","101","101"],
    "L": ["100","100","100","100","111"],
    "M": ["111","111","101","101","101"],
    "N": ["110","101","101","101","101"],
    "O": ["010","101","101","101","010"],
    "P": ["110","101","110","100","100"],
    "Q": ["010","101","101","111","011"],
    "R": ["110","101","111","110","101"],
    "S": ["011","100","010","001","110"],
    "T": ["111","010","010","010","010"],
    "U": ["101","101","101","101","011"],
    "V": ["101","101","101","101","010"],
    "W": ["101","101","111","111","101"],
    "X": ["101","101","010","101","101"],
    "Y": ["101","101","010","010","010"],
    "Z": ["111","001","010","100","111"],
    "0": ["011","101","101","101","110"],
    "1": ["010","110","010","010","111"],
    "2": ["110","001","010","100","111"],
    "3": ["110","001","010","001","110"],
    "4": ["101","101","111","001","001"],
    "5": ["111","100","110","001","110"],
    "6": ["011","100","111","101","111"],
    "7": ["111","001","010","100","100"],
    "8": ["111","101","111","101","111"],
    "9": ["111","101","111","001","111"],
    " ": ["000","000","000","000","000"],
    ",": ["000","000","000","010","001"],
    "$": ["011","110","011","110","010"],
    ">": ["100","010","001","010","100"],
    "<": ["001","010","100","010","001"],
    "/": ["001","010","010","010","100"],
}
 #draw_char#
def draw_char(x,y,char,col):#x=posicion x,y=posicion y,char= letra a dibujar,col= numero color de la paleta
 glyph=mini_font[char.upper()]
 for i in glyph:
  x-=3
  y+=1
  for j in i:
   x+=1
   if j=="1":
    pix(x,y,col)
 #draw_text#
def draw_text(txt,x,y,col):
 for i in txt:
  draw_char(x,y,i,col)
  x+=4

#-Escenario-#
 #counter#
def counter(st,cur,end,inc,rep):#(start,current,end,increment,repeat)
 if cur!=end:
  if cur<end:
   cur+=inc
  elif cur>end:
   cur-=inc
 elif rep:
  cur=st
  
 return cur

 #botones#
class Boton:
 def __init__(self,txt,col,x,y,w,h,active):
  self.txt = txt
  self.x = x
  self.y = y
  self.w = w
  self.h = h
  self.active=active
  self.col=col
  if col ==0:#azul
   self.iner=7
   self.bor=6
  elif col ==1:#rojo
   self.iner=2
   self.bor=3
  elif col ==2:#verde
   self.iner=0
   self.bor=1
  elif col ==3:#morado
   self.iner=11
   self.bor=13
  elif col ==4:#amarillo
   self.iner=10
   self.bor=8
  elif col ==5:#ngro
   self.iner=13
   self.bor=15
 #pintar#
 def pintar(self):
  x = self.x
  y = self.y
  w = self.w
  h = self.h 
  txt = self.txt
  
  bor = self.bor
  poke4(0x3FF0*2+6,bor)#change of palet
  
  iner = self.iner
  poke4(0x3FF0*2+7,iner)#change of palet
  
  if self.clicado()or self.active== False:
   prs=True
   y=y+1
  else:
   prs=False
  for i in range(w):
   for j in range(h):
    if i==0:
     if j==h-1:#esquina izquierda inferior
      if h==1:
       spr(244,x,y,0)
      else:
       spr(243,x,y+(j*8),0,1,2)
      if prs==False :#deepth
       line(x+1,y+(j*8)+8,x+7,y+(j*8)+8,bor)
       pix(x,y+(j*8)+7,bor)
     elif j==0:#esquina izquierda superior
       spr(243,x,y,0)
     else:#medio izquierda 
      spr(227,x,y+(j*8),0,1,0,3)
    elif i==w-1:
     if j==h-1:#esquina derecha inferior
      if h==1:
       spr(244,x+(i*8),y+(j*8),0,1,0,2)
      else:
       spr(243,x+(i*8),y+(j*8),0,1,0,2)
      if prs==False :
       line(x+(i*8),y+(j*8)+8,x+(i*8)+6,y+(j*8)+8,bor)
       pix(x+(i*8)+7,y+(j*8)+7,bor)
     elif j==0:#esquina derecha superior
      spr(243,x+(i*8),y,0,1,1)
     else:#medio derecha
      spr(227,x+(i*8),y+(j*8),0,1,0,1)
    else:
     if j==h-1:#medio inferior
      if h==1:
       spr(228,x+(i*8),y+(j*8),0)
      else:
       spr(227,x+(i*8),y+(j*8),0,1,2)
      if prs==False :
       line(x+(i*8),y+(j*8)+8,x+(i*8)+8,y+(j*8)+8,bor)
     elif j==0:#medio superior
      spr(227,x+(i*8),y,0)
     else:#medio
      spr(227,x+(i*8),y+(j*8),0)
      line(x+(i*8),y+(j*8),x+(i*8)+8,y+(j*8),iner)
  
  
  draw_text(txt,int(w*8/2-(len(txt)/2)*3)+x,int(h*8/2-4)+y,bor)
  
  poke4(0x3FF0*2+6,6)#border color reestart 
  poke4(0x3FF0*2+7,7)#interior color reestart
 #click#
 def clicado(self):
  mx=mouse()[0]
  my=mouse()[1]
  mb=mouse()[2]
  x = self.x
  y = self.y 

  if mb == 1:  
   if (mx >= x and mx < x + self.w * 8 and my >= y and my < y + self.h * 8):
    return True
 
  return False
#-Cartas-#
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
 
 
 
 


#-Mazo-#

class Mazo:
 def __init__(self, tipo_baraja):
  self.dt = tipo_baraja#Deck_type

 def generar_mazo(self):
  self.cartas=[]
  dt=self.dt
  #baraja estandar roja o azul o verde o negro o amarlla
  if dt in (0,1,2,3,4):
   for suit in range(4):
    for value in range(1, 14):
     self.cartas.append(Carta(dt,suit,value,0,0,0))
     
  elif dt == 5:
   for suit in range(2):
    for value in range(1, 14):
     for _ in range(2):
      self.cartas.append(Carta(dt,suit,value,0,0,0))
      
  elif dt == 6:
   for suit in range (4):
    for value in range (1,11):
     self.cartas.append(Carta(dt,suit,value,0,0,0))
     
  elif dt ==7:
   for i in range (52):
     suit=int(random.randint(0,3))
     value=int(random.randint(1,13))
     self.cartas.append(Carta(dt,suit,value,0,0,0))
   self.ordenar()
  self.total=self.cartas.copy()

   
   
 #mostrar#
 def mostrar(self,x,y,scale,showtxt,txx,txy):
  dt=self.dt
  s=scale
  x2=x+s*8
  
  if dt==0:
   spr(64,x,y,0,s,0,0,1,3)
   spr(64,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("tienes un",txx,txy,2)
    draw_text("descarte mas",txx,txy+8,2)
  elif dt==1:
   poke4(0x3FF0*2+2,7)
   spr(64,x,y,0,s,0,0,1,3)
   spr(64,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("tienes una",txx,txy,7)
    draw_text("mano mas",txx,txy+8,7)
  elif dt==2:
   poke4(0x3FF0*2+2,1)
   spr(64,x,y,0,s,0,0,1,3)
   spr(64,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("no genera interese,",txx,txy,1)
    draw_text("2$ por mano y 1$ por",txx,txy+8,1)
    draw_text("descarte restante",txx,txy+16,1)
  elif dt==3:
   poke4(0x3FF0*2+2,8)
   spr(64,x,y,0,s,0,0,1,3)
   spr(64,x2,y,0,s,0,2,1,3)
   if showtxt:
    draw_text("comienzas con 10$",txx,txy,8)
  elif dt==4:
   poke4(0x3FF0*2+2,15)
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
  
  poke4(0x3FF0*2+2,2)
 #muestra  
 def muestra(self,pal):
  if pal=="total":
   return self.cartas
  else :
   return self.total
 #mezclar#
 def mezclar(self):
  random.shuffle(self.cartas)
 #ordenar#
 def ordenar(self):
  x=[]
  for f in sorted(self.cartas,key=lambda x: x.va):
   x.append(f)
  self.cartas=x
 #repartir#
 def repartir(self):
  while len(hand)<handsize:
   x=random.randint(0,len(hand))
   hand.append(self.cartas[x])
   self.cartas.pop(x)
  hand.sort(key=lambda c: c.va)


#-Print Cards-#
def print_cards(x,y,xf,list,sel):
 con=0#contador cartas
 sep=(xf-x-17)/(len(list)-1)#separacion
 dec=0
 
 for i in list:
  dec+=sep-int(sep)
  xc=x+con*int(sep)+int(dec)
  onda1=math.sin((time()+i.an)/250)*0.75
  onda2=math.sin((time()+i.an)/150)*0.3
  yc=int(y+onda1+onda2)+i.y
  if not sel :
   i.sel=False
   i.y=0
  if mouse()[0]>xc and mouse()[0]<xc+16 and mouse()[1]>yc and mouse()[1]<yc+23:
   yc-=6
   if mouse()[2]:
    yc+=2
    i.sel=True
    i.y=-4
   if i.sel and mouse()[4]:
    yc-=2
    i.sel=False
    i.y=0

  con+=1
  cs=i.su*16#suit
  cv=i.va#value
  ce=i.ef+17#efecto
  cm=i.st+59#sello
  ced=int(i.ed)+112#edicion
  #print background
  spr(ce,xc,yc,0,1,0,0,1,3)
  spr(ce,xc+8,yc,0,1,0,2,1,3)
  #print suit
  spr(cs,xc,yc+8,0)
  spr(cs,xc+8,yc+8,0,1,1)
  #print value
  if i.su%2==1:
   poke4(0x3FF0*2+14,2)
  spr(cv,xc,yc,0)
  spr(cv,xc+8,yc+16,0,1,0,2)
  
  poke4(0x3FF0*2+14,14)
  #print sello
  spr(cm,xc+8,yc,0)
  #print edition
  if i.ed!=0:
   if i.ed<10:
    i.ed=counter(1,i.ed,5,0.125,True)
   elif i.ed!=0:
    i.ed=counter(49,i.ed,53,0.125,True)
   spr(ced,xc,yc,0,1,0,0,1,3)
   spr(ced,xc+8,yc,0,1,0,2,1,3)
  
#-Evaluate_hand-#

def eval_hand():
 a=[]
 
 for i in hand:
  if i.sel:
   a.append(i)
 
 rep = [[i, 0] for i in range(1, 14)]
 for i in numeros :
  for j in rep :
   if i.va == j[0]:
    j[1]+=1
 
 conteos = [j[1] for j in rep if j[1] > 1]
 conteos.sort(reverse=True)
 
  
 return a


#--== INIT ==--#
gm=0#game map
num1 = random.randint(0,7)+17
num2 = random.randint(0,3)*16
Clk0 = False
baraja=Mazo(DS)
jokers=[]
consu=[]
hand=[]
anim=0
up=0
pal="total"
b=[]
def TIC():
 global DS,Clk0,gm,baraja,jokers,consu,hand,up,anim,pal,b
 
 raton=mouse()#no se donde colocar la basura esta
 #inicio#
 if gm==0:
  cls() 
  map(0,0,30,17)
  #impresion del titulo BITL A TRO
  titx=108#title x
  tity=12# title y
  
  #TRO
  spr(77,titx+28,tity,0,2,0,0,3,2)
  #As aleatorio
  spr(num1,titx,tity-9,0,2,0,0,1,3)#random background
  spr(num1,titx+16,tity-9,0,2,0,2,1,3)
  
  spr(num2,titx,tity+7,0,2)#random suit
  spr(num2,titx+16,tity+7,0,2,1)
   
  if num2==16 or num2==48:
   poke4(0x3FF0*2+14,2)
   
  spr(1,titx,tity-9,0,2)
  spr(1,titx+16,tity+23,0,2,0,2)
  
  poke4(0x3FF0*2+14,14)
  
  #BITL
  spr(73,titx-52,tity,0,2,0,0,4,2)
  line(titx-48,tity-2,titx-41,tity-2,15)
  line(titx-48,tity-1,titx-41,tity-1,15)
  
  baraja.mostrar(64,64,2,True,102,70)
  
  prev=Boton(" <",1,100,95,3,2,True)
  prev.pintar()
  if prev.clicado()and not Clk0:
   DS-=1
  
  next=Boton(" >",0,150,95,3,2,True)
  next.pintar()
  if next.clicado()and not Clk0:
   DS+=1
  
  
  if DS>7:
   DS=0
  if DS<0:
   DS=7
  baraja=Mazo(DS)
  
  play=Boton("play",4,125,95,3,2,True)
  play.pintar()
  if play.clicado()and not Clk0:
   gm=1
   baraja.generar_mazo()
   baraja.mezclar()
   baraja.repartir()
  
  Clk0=raton[2]
 
 #play matt#  
 elif gm==1:
  cls() 
  map(30,0,60,17)
  
  up=counter(0,up,50,1,False)
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
  
  
  print_cards(80,140-up,193,hand,True)
  
  
  draw_text(str(len(hand))+"/8",82,162-up,11)
  
  draw_text(str(len(jokers))+"/5",82,29,11)
  
  draw_text(str(len(consu))+"/2",223,29,11)
  
  draw_text(str(len(baraja.cartas))+"/52",217,128,11)
  
  
  disc=Boton("discard",1,145,166-up,4,2,True)
  disc.pintar()
  if disc.clicado()and not Clk0:
   hand = [c for c in hand if not c.sel]
   baraja.repartir()
   
  play=Boton("play",0,95,166-up,4,2,True)
  play.pintar()
  if play.clicado()and not Clk0:
   b=eval_hand()
   hand = [c for c in hand if not c.sel]
   baraja.repartir()
  
 
  if b != [] and anim <30:
   anim=counter(0,anim,30,0.5,False)
   print_cards(80,90-anim,80+(len(b)*16),b,False)
  elif anim>=30 and anim <30+len(b)*40:
   anim=counter(30,anim,30+len(b)*40,0.5,False)
   print_cards(80,60,80+(len(b)*16),b,False)
  elif anim==30+len(b)*40:
   anim=0
   b=[]
   
   
  
  baraja.mostrar(216,104,1,False,0,0)

  
  if raton[0]>216 and raton[0]<232 and raton[1]>104 and raton[1]<128 and raton[2]==True:
   gm=2
   baraja.ordenar() 
  Clk0=raton[2]
 #Deck_menu#
 elif gm==2:
  cls() 
  map(30,18,60,35)
  total=Boton(pal,0,80,118,4,2,True)
  total.pintar()
  
  
  if total.clicado() and pal=="actual"and not Clk0:
   baraja.cartas
   pal="total"
  
  elif total.clicado()and not Clk0:
   baraja.total
   pal="actual"
  
  Clk0=raton[2]
  
  
  baraja.mostrar(12,12,2,False,30,65)
  
  bg1=Boton(" ",5,59,11,21,12,False)
  bg1.pintar()
  pi=[]
  co=[]
  tr=[]
  ro=[]
  v=[0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  s=[0,0,0,0]
  can=[0,0,0]
  for i in baraja.muestra(pal):
   if i.va == 1:
    can[0]+=1
   elif i.va==11 or i.va==12 or i.va==13 :
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
  poke4(0x3FF0*2+14,15)
  for i in range(1,14):
   spr(245,50,7+(i*7),0)
   spr(i,49,6+(i*7),0)
   draw_text(str(v[i]),46,8+(i*7),11)
  
  
  
  poke4(0x3FF0*2+14,14)
  
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
  
  if raton[0]>12 and raton[0]<44 and raton[1]>20 and raton[1]<68 and raton[2]==True:
   gm=1
   baraja.mezclar()