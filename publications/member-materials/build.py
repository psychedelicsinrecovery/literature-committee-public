from pathlib import Path
import re, html, json
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,PageBreak,Spacer
B=Path(__file__).resolve().parent; A=B/'assets'; O=B/'pdf'; O.mkdir(exist_ok=True)
for n,f in [('EB','EBG400'),('EBB','EBG700'),('EBI','EBI400')]:pdfmetrics.registerFont(TTFont(n,str(A/(f+'.ttf'))))
pdfmetrics.registerFontFamily('EB',normal='EB',bold='EBB',italic='EBI',boldItalic='EBB')
navy=HexColor('#20205c'); purple=HexColor('#593484')
W,H=612,792
_ir=ImageReader(str(A/'banner-original.png')); _iw,_ih=_ir.getSize()
BANNER_H=W*_ih/_iw            # aspect-true banner height, same on every page
COPY='© 2026 Psychedelics In Recovery™ – PIR® · All Rights Reserved, except separately licensed content.'
SKIP={'parking-lot','new-to-zoom','new-to-discord'}   # folded into staying-connected
# slug: (base font size, target pages, all-caps headings centered?)
SPEC={'faq':(12.2,4,False,1.24,.53,1.5),'cares-and-considerations':(12.25,4,True,1.12,.33,1.5),'netiquette':(11.4,1,False,1.10,.40,1.5),
      'twelve-steps':(11.5,1,False,1.18,.39,1.35),'twelve-traditions':(11.5,1,False,1.18,.39,1.35),
      'meeting-script':(11.5,2,False,1.16,.42,1.4),'safety-guidelines':(12.4,1,False,1.23,.55,1.37),'sponsorship-and-co-travel':(12.4,1,False,1.23,.55,1.25),
      'preamble':(14,1,False,1.30,.85,1.65),'guiding-principles':(14,1,False,1.30,.85,1.65),
      'integration-and-a-plan-of-action':(13,1,False,1.30,.75,1.6),
      'staying-connected':(11.6,2,False,1.22,.47,1.25),'sponsorship-review':(11.5,None,False,1.24,.53,1.5)}
def inline(s):
 s=html.escape(s,quote=False)
 def link(m):return '<link href="'+m[2].replace('"','&quot;')+'" color="#2576ac">'+m[1]+'</link>'
 s=re.sub(r'\[([^\]]+)\]\((https?://[^ )]+(?:\([^)]*\)[^ )]*)?)\)',link,s)
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
 return s.replace(r'\*','*')
def build_story(p,size,lead,gap,center_caps):
 slug=p.stem; raw=p.read_text(); title=raw.splitlines()[0][2:]; review=slug=='sponsorship-review'
 def style(n,**kw):return ParagraphStyle(n,fontName=kw.pop('fontName','EB'),fontSize=kw.pop('fontSize',size),leading=kw.pop('leading',lead),textColor=kw.pop('textColor',navy),**kw)
 body=style('body',spaceAfter=gap); h=style('heading',fontName='EBB',keepWithNext=True,spaceBefore=5,spaceAfter=3,textColor=purple)
 hc=style('heading-center',fontName='EBB',keepWithNext=True,spaceBefore=6,spaceAfter=4,textColor=purple,alignment=TA_CENTER)
 titleStyle=style('title',fontName='EBB',fontSize=20,leading=23,alignment=1,spaceAfter=12)
 quote=style('quote',leftIndent=12,rightIndent=10,borderColor=HexColor('#ded4ef'),borderWidth=.6,borderPadding=6,backColor=HexColor('#f5effa'),spaceBefore=3,spaceAfter=10)
 tag=style('tag',fontSize=size*.86,leading=lead*.87); bullet=style('bullet',leftIndent=12,firstLineIndent=-10,spaceAfter=gap)
 story=[]; legend=False; toc=False; optional=False
 title_main, sep, sub=title.partition(' of Psychedelics In Recovery™')
 if sep and slug in {'twelve-steps','twelve-traditions'}:
  story.append(Paragraph(inline(title_main),style('main-title',fontName='EBB',fontSize=21,leading=23,alignment=TA_CENTER)))
  story.append(Paragraph('of Psychedelics In Recovery™',style('sub-title',fontSize=12,leading=15,alignment=TA_CENTER,spaceAfter=12)))
 else: story.append(Paragraph(inline(title),titleStyle))
 toc_line=style('toc-line',alignment=TA_CENTER,spaceAfter=.4)
 compact=style('compact',fontSize=size*.91,leading=lead*.91,spaceAfter=gap*.76)
 compact_head=style('compact-head',fontName='EBB',fontSize=size*.93,leading=lead,spaceBefore=4,spaceAfter=2,keepWithNext=True,textColor=purple)
 for block in re.split(r'\n\s*\n',raw.strip())[1:]:
  if block == '<!-- pagebreak -->':
   story.append(PageBreak())
  elif block.startswith('##'):
   text=block.lstrip('# ');legend=text=='Tags'; toc=text=='Table of Contents'
   if slug=='meeting-script' and text=='OPTIONAL ADDITIONS': optional=True
   if text in {'RESOURCES','Tags'}: story.append(Spacer(1,5))
   if text.startswith('Meeting Ending: '):
    beat,cue=text.split(': ',1); story.append(Paragraph(inline('**'+beat+':**')+' <font name="EB" size="'+str(size*.83)+'">'+inline(cue)+'</font>',h)); continue
   story.append(Paragraph(inline(text.upper() if toc else text),hc if (text in {'CARES','CONSIDERATIONS','RESOURCES','Table of Contents'} and center_caps) else (compact_head if optional and text!='OPTIONAL ADDITIONS' else h)))
  elif block.startswith('> '):
   if slug=='sponsorship-and-co-travel': story.append(Spacer(1,4))
   story.append(Paragraph(inline(block[2:]),quote))
   if slug=='sponsorship-and-co-travel': story.append(Spacer(1,4))
  elif block.startswith('- ') or re.match(r'^\d+\. ',block):
   lines=block.splitlines()
   if toc:
    for line in lines:
     item=line.removeprefix('- ')
     story.append(Paragraph(('<b>'+item[0]+'<font size="'+str(size*.79)+'">'+item[1:]+'</font></b>') if item in {'CARES','CONSIDERATIONS'} else inline(item),toc_line))
   elif legend:
    cells=[Paragraph(inline(re.sub(r'^- (.*?) = ',r'**\1** = ',l)),tag) for l in lines];rows=[cells[i:i+4]+['']*max(0,4-len(cells[i:i+4])) for i in range(0,len(cells),4)];story.append(Table(rows,colWidths=[133]*4,style=TableStyle([('BACKGROUND',(0,0),(-1,-1),HexColor('#f1edf7')),('VALIGN',(0,0),(-1,-1),'TOP')])))
   else:
    for line in lines:
     s=re.sub(r'^- A sponsor','- **A sponsor**',line) if review else line
     story.append(Paragraph(inline('• '+s[2:] if s.startswith('- ') else s),bullet))
  else:story.append(Paragraph(inline(' '.join(block.splitlines())),compact if optional else body))
 return story,title,review
WATERMARK=json.loads((A/'watermark-paths.json').read_text())
def furniture(total,title,continued):
 def f(c,d):
  c.saveState()
  c.drawImage(str(A/'banner-original.png'),0,H-BANNER_H,W,BANNER_H)   # full-bleed, aspect-true, every page
  c.setFillColor(HexColor('#f4f0f8')); p=c.beginPath(); k=.44
  for ring in WATERMARK:
   coords=[(W/2+(x-296)*k,H/2+(184-y)*k) for x,y in ring]; p.moveTo(*coords[0]);
   for xy in coords[1:]:p.lineTo(*xy)
   p.close()
  c.drawPath(p,fill=1,stroke=0,fillMode=0)
  if continued and d.page>1:
   c.setFillColor(purple);c.setFont('EBB',11)
   c.drawCentredString(W/2,H-BANNER_H-17,title+' (continued)')
  c.setStrokeColor(HexColor('#d8d0e6'));c.line(35,39,W-35,39);c.setFillColor(navy);c.setFont('EB',8)
  if total is None:page_no=str(d.page)
  else:page_no=f'{d.page} of {total}'
  c.drawCentredString(W/2,26,COPY)
  c.drawCentredString(W/2,15,page_no)
  c.restoreState()
 return f
def render(p):
 slug=p.stem
 base,target,center_caps,lf,gf,maxs=SPEC.get(slug,(11.5,None,False,1.24,.53,1.5))
 size,lead,gap=base,base*lf,base*gf
 continued=bool(target and target>1)
 def emit(scale,total=None):
  s=size*scale;l=lead*scale;g=gap*scale
  story,title,review=build_story(p,s,l,g,center_caps)
  out=O/(f'{slug}-count.pdf' if total is None else f'{slug}-reformat-v3.pdf')
  d=SimpleDocTemplate(str(out),pagesize=(W,H),topMargin=BANNER_H+14,bottomMargin=48,leftMargin=27 if center_caps else 34,rightMargin=27 if center_caps else 34,title=title)
  if continued:
   d.topMargin=BANNER_H+34; d._calc()
  d.build(story,onFirstPage=furniture(total,title,False),onLaterPages=furniture(total,title,continued))
  return len(PdfReader(out).pages)
 if target:
  scale=1.0;pages=emit(scale)
  while pages>target and scale>.82:scale-=.03;pages=emit(scale)
  if pages<=target:
   while scale<maxs:
    s2=round(scale+.03,2);p2=emit(s2)
    if p2>target:pages=emit(scale);break
    scale,pages=s2,p2
 else:scale=1.0;pages=emit(scale)
 total=pages
 if total>1 and not continued:
  continued=True; total=emit(scale)
 assert emit(scale,total)==total
 (O/f'{slug}-count.pdf').unlink(missing_ok=True)
 print(slug,'pages',total,'scale',round(scale,2),'bannerH',round(BANNER_H,1))
for p in sorted((B/'source').glob('*.md')):
 if p.stem not in SKIP:render(p)
