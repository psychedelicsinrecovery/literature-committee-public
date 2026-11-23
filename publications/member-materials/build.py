from pathlib import Path
import re, html
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle
B=Path(__file__).resolve().parent; A=B/'assets'; O=B/'pdf'; O.mkdir(exist_ok=True)
for n,f in [('EB','EBG400'),('EBB','EBG700'),('EBI','EBI400')]:pdfmetrics.registerFont(TTFont(n,str(A/(f+'.ttf'))))
pdfmetrics.registerFontFamily('EB',normal='EB',bold='EBB',italic='EBI',boldItalic='EBB')
navy=HexColor('#20205c'); purple=HexColor('#593484')
W,H=612,792
_ir=ImageReader(str(A/'banner-original.png')); _iw,_ih=_ir.getSize()
BANNER_H=W*_ih/_iw            # aspect-true banner height, same on every page
COPY='© 2026 Psychedelics In Recovery™ – PIR® · All Rights Reserved, except separately licensed content.'
SKIP={'parking-lot','new-to-zoom','new-to-discord'}   # folded into staying-connected
# slug: (base font size, target pages, all-caps headings centered?, lead factor, gap factor, max scale)
SPEC={'faq':(12.2,4,False,1.24,.53,1.5),'cares-and-considerations':(12.2,4,False,1.13,.38,1.5),'netiquette':(11.4,1,False,1.10,.40,1.5),
      'staying-connected':(11.6,2,False,1.24,.53,1.25),'sponsorship-review':(11.5,None,False,1.24,.53,1.5)}
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
 story=[Paragraph(inline(title),titleStyle)]; legend=False
 for block in re.split(r'\n\s*\n',raw.strip())[1:]:
  if block.startswith('##'):
   text=block.lstrip('# ');legend=text=='Tags'
   caps=text.isupper() and len(text)>2
   story.append(Paragraph(inline(text),hc if (caps and center_caps) else h))
  elif block.startswith('> '):story.append(Paragraph(inline(block[2:]),quote))
  elif block.startswith(('- ','1. ')):
   lines=block.splitlines()
   if legend:
    cells=[Paragraph(inline(re.sub(r'^- (.*?) = ',r'**\1** = ',l)),tag) for l in lines];rows=[cells[i:i+4]+['']*max(0,4-len(cells[i:i+4])) for i in range(0,len(cells),4)];story.append(Table(rows,colWidths=[133]*4,style=TableStyle([('BACKGROUND',(0,0),(-1,-1),HexColor('#f1edf7')),('VALIGN',(0,0),(-1,-1),'TOP')])))
   else:
    for line in lines:
     s=re.sub(r'^- A sponsor','- **A sponsor**',line) if review else line
     story.append(Paragraph(inline('• '+s[2:] if s.startswith('- ') else s),bullet))
  else:story.append(Paragraph(inline(' '.join(block.splitlines())),body))
 return story,title,review
def furniture(total):
 def f(c,d):
  c.saveState()
  c.drawImage(str(A/'banner-original.png'),0,H-BANNER_H,W,BANNER_H)   # full-bleed, aspect-true, every page
  c.setFillAlpha(.065);c.drawImage(str(A/'mark-real.png'),W/2-150,H/2-90,300,180,mask='auto');c.setFillAlpha(1)
  c.setStrokeColor(HexColor('#d8d0e6'));c.line(35,39,W-35,39);c.setFillColor(navy);c.setFont('EB',8)
  if total is None:page_no=str(d.page)
  else:page_no=f'{d.page} of {total}'
  if d.page==1:c.drawCentredString(W/2,26,COPY);c.drawCentredString(W/2,15,page_no)
  else:c.drawCentredString(W/2,15,page_no)
  c.restoreState()
 return f
def render(p):
 slug=p.stem
 base,target,center_caps,lf,gf,maxs=SPEC.get(slug,(11.5,None,False,1.24,.53,1.5))
 size,lead,gap=base,base*lf,base*gf
 def emit(scale,total=None):
  s=size*scale;l=lead*scale;g=gap*scale
  story,title,review=build_story(p,s,l,g,center_caps)
  out=O/(f'{slug}-count.pdf' if total is None else f'{slug}-reformat-v3.pdf')
  d=SimpleDocTemplate(str(out),pagesize=(W,H),topMargin=BANNER_H+14,bottomMargin=48,leftMargin=34,rightMargin=34,title=title)
  d.build(story,onFirstPage=furniture(total),onLaterPages=furniture(total))
  return len(PdfReader(out).pages)
 if target:
  scale=1.0;pages=emit(scale)
  while pages>target and scale>.82:scale-=.03;pages=emit(scale)
  if pages<=target:
   while scale<maxs:
    s2=round(scale+.03,2);p2=emit(s2)
    if p2>target:pages=emit(scale);break
    scale,pages=s2,p2
 else:pages=emit(1.0)
 total=pages
 emit(scale,total)
 (O/f'{slug}-count.pdf').unlink(missing_ok=True)
 print(slug,'pages',total,'scale',round(scale,2),'bannerH',round(BANNER_H,1))
for p in sorted((B/'source').glob('*.md')):
 if p.stem not in SKIP:render(p)
