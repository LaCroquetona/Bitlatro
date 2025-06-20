-- title:   Balaro
-- author:  menestra de croquetas
-- desc:    short description
-- site:    website link
-- license: MIT License 
-- version: 0.0.0
-- script:  lua

--== VARIABLES ==--
hand=8
values={1,13,12,11,10,9,8,7,6,5,4,3,2}
cardsinhand={}
cursor={79,120,0,0}
play={}
hands={{1,5,1,"High"},{1,10,2,"Pair"},{1,20,2,"Two Pair"},{1,30,3,"Three"},{1,30,4,"Straight"},{1,35,4,"Flush"},{1,40,4,"Full House"},{1,60,7,"Four"},{1,100,8,"Straight Flush"},{1,120,12,"Royal Flush"},{0,0,0,""}}

--== UTILS ==--
function add(t,v) t[#t+1]=v end
function deli(t,i) return table.remove(t,i or #t) end
function insert(t,o,v) table.insert(t,o,v) end
function rnd(x) return math.random()*(x or 1) end
function flr(x) return math.floor(x) end
function pop(t,o)for i=1,#t do if t[i]==o then table.remove(t,i)break end end end -- .pop(list,a)
function find(t,o) for i=1,#t do if t[i]==o then return i end end end


--== MINI-FONT ==--
mini_font = {
 A = {"010","101","111","101","101"},
 B = {"110","101","110","101","110"},
 C = {"011","100","100","100","011"},
 D = {"110","101","101","101","110"},
 E = {"111","100","110","100","111"},
 F = {"111","100","110","100","100"},
 G = {"011","100","101","101","011"},
 H = {"101","101","111","101","101"},
 I = {"111","010","010","010","111"},
 J = {"001","001","001","101","010"},
 K = {"101","101","110","101","101"},
 L = {"100","100","100","100","111"},
 M = {"111","111","101","101","101"},
 N = {"110","101","101","101","101"},
 O = {"010","101","101","101","010"},
 P = {"110","101","110","100","100"},
 Q = {"010","101","101","111","011"},
 R = {"110","101","111","110","101"},
 S = {"011","100","010","001","110"},
 T = {"111","010","010","010","010"},
 U = {"101","101","101","101","011"},
 V = {"101","101","101","101","010"},
 W = {"101","101","111","111","101"},
 X = {"101","101","010","101","101"},
 Y = {"101","101","010","010","010"},
 Z = {"111","001","010","100","111"},
 ["0"] = {"011","101","101","101","110"},
 ["1"] = {"010","110","010","010","111"},
 ["2"] = {"110","001","010","100","111"},
 ["3"] = {"110","001","010","001","110"},
 ["4"] = {"101","101","111","001","001"},
 ["5"] = {"111","100","110","001","110"},
 ["6"] = {"011","100","111","101","111"},
 ["7"] = {"111","001","010","100","100"},
 ["8"] = {"111","101","111","101","111"},
 ["9"] = {"111","101","111","001","111"},
 [" "] = {"000","000","000","000","000"}
}

function draw_char(x,y,c,col)
 local glyph = mini_font[string.upper(c)]
 if not glyph then return end
 for j=1,#glyph do
  for i=1,#glyph[j] do
   if glyph[j]:sub(i,i)=="1" then
    pix(x+i-1, y+j-1, col)
   end
  end
 end
end

function draw_text(txt,x,y,col)
 for i=1,#txt do
  draw_char(x+(i-1)*4, y, txt:sub(i,i), col)
 end
end

--== ESCENARIO ==--

function print_Box(x,y,px,py,c)
	s=243
	if x==1 or y==1 then s=245 end
	if c==1 then s=s+1 end
	for iy=0,y-1 do
		for ix=0,x-1 do
			local sx=px+ix*8 sy=py+iy*8
			if iy==0 and ix==0 then spr(s,sx,sy,1,1,0,0)
			elseif iy==0 and ix==x-1 then spr(s,sx,sy,1,1,1,0)
			elseif iy==y-1 and ix==0 then spr(s,sx,sy,1,1,0,3)
			elseif iy==y-1 and ix==x-1 then spr(s,sx,sy,1,1,1,3)
			elseif iy==0 or iy==y-1 or ix==0 or ix==x-1 then spr(s-16,sx,sy,0,1)
end end end end

--== MAZO ==--
function make_deck()
 local d={}
 for s=0,3 do for i=1,#values do add(d,{values[i],s,0,0,0,0,0}) end end
 return d
end

function shuffle(t)
 for i=#t,2,-1 do local j=flr(rnd(i))+1 t[i],t[j]=t[j],t[i] end
end

--== CARTAS ==--
function print_cards(x,y,list)
 for i=1,#list do
  local c=list[i]
  local cx=x+(i-1)*15
  c[5]=cx
  c[6]=y
  local y_offset=(c[7]==1) and (c[6]-4) or c[6]
  spr(c[3]+64,cx,y_offset,1,1,0,0,1,3)
  spr(c[3]+64,cx+8,y_offset,1,1,0,2,1,3)
  spr(c[4]+144,cx+8,y_offset,1,1)
  local nb=(c[2]%2==0) and (c[1]+16) or c[1]
  spr(nb,cx,y_offset,1,1)
  spr(nb,cx+8,y_offset+16,1,1,0,2)
  spr(c[2]*16,cx,y_offset+8,1,1)
  spr(c[2]*16,cx+8,y_offset+8,1,1,1)
 end
end

--== MANO ==--
function eval_hand()
 local v,s={},{},{}
 for i=1,#play do
  add(v,play[i][1])
  add(s,play[i][2])
 end
 table.sort(v)

 local counts={}
 local max=0
 for i=1,#v do counts[v[i]]=1+(counts[v[i]] or 0) end

 local pair,three,four=0,0,0
 for _,c in pairs(counts) do
  if c==2 then pair=pair+1 end
  if c==3 then three=three+1 end
  if c==4 then four=four+1 end
  if c>max then max=c end
 end

 local flush=false
 if #s>0 then
  flush=true
  for i=2,#s do
   if s[i]~=s[1] then flush=false break end
  end
 end

 local straight=false
 if #v>=5 then
  local unique_vals={} for _,val in ipairs(v) do unique_vals[val]=true end
  local uniq_sorted={} for k in pairs(unique_vals) do add(uniq_sorted,k) end
  table.sort(uniq_sorted)
  for i=1,#uniq_sorted-4 do
   if uniq_sorted[i+4]-uniq_sorted[i]==4 then straight=true break end
  end
  if unique_vals[1] and unique_vals[10] and unique_vals[11] and unique_vals[12] and unique_vals[13] then
   straight=true
  end
 end

 if straight and flush and v[1]==1then return 10
 elseif straight and flush then return 9
 elseif four==1then return 8
 elseif three==1 and pair>=1then return 7
 elseif flush and#s>=5then return 6
 elseif straight then return 5
 elseif three==1then return 4
 elseif pair>=2then return 3
 elseif pair==1then return 2
 elseif #play>=1then return 1
 else return 11 end
end

--== INIT ==--
deck=make_deck()
shuffle(deck)

--== TIC ==--
function TIC()
 --mapa--
 cls()
 map(0,0,30,17)
 print_Box(3,1,10,32,0)
 print_Box(4,1,38,32,1)
 --Cursor--
 spr(240,cursor[1],cursor[2],1)
 if btnp(3) and cursor[3]<hand-1 then cursor[1]=cursor[1]+15 cursor[3]=cursor[3]+1
 elseif btnp(2) and cursor[3]>0 then cursor[1]=cursor[1]-15 cursor[3]=cursor[3]-1 end
 if #cardsinhand>cursor[3] then
  local c=cardsinhand[cursor[3]+1]
  if btnp(4) then
   if c[7]==0 and #play<5 then c[7]=1 add(play,c)
   elseif c[7]~=0 then c[7]=0 for i=#play,1,-1 do if play[i]==c then deli(play,i) break end end
   end
  end
 end
 while #cardsinhand<hand do add(cardsinhand,deli(deck,1)) end

 -- ordenar todos los ases al frente
 table.sort(cardsinhand,function(a,b)
  if a[1]==1 and b[1]~=1 then return true
  elseif a[1]~=1 and b[1]==1 then return false
  elseif a[1]==b[1] then return a[2]<b[2]
  else return a[1]>b[1] end
 end)

 print_cards(75,96,cardsinhand)
 local hand_type = eval_hand()
 draw_text(hands[hand_type][4],10,25,12)
 if hand_type<11 and btn(5)then
 	for i = 1, #play do
  	p=find(cardsinhand,play[i])
  	pop(cardsinhand,play[i])
   -- insertar carta en blanco en posicion p
  end
 	print_cards(75,70,play)
 	draw_text(tostring(hands[hand_type][2]),12,34,12)
  draw_text(tostring(hands[hand_type][3]),40,34,12)
 end

end
