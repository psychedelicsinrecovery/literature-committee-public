from pathlib import Path
from pypdf import PdfWriter, PdfReader
b=Path(__file__).resolve().parent
pdf=b/'pdf'; old=b/'wordpress-snapshot-2026-11-22'
items=[old/f'member-material-{slug}-source.pdf' for slug in ['meeting-script','safety-guidelines','twelve-steps','twelve-traditions','preamble','guiding-principles','integration-and-a-plan-of-action']]
items += [pdf/f'{slug}-reformat-v3.pdf' for slug in ['faq','netiquette','cares-and-considerations','staying-connected']]
items += [old/'member-material-sponsorship-source.pdf']
w=PdfWriter()
for p in items:w.append(p,outline_item=p.stem.replace('-reformat-v3','').replace('member-material-','').replace('-source','').replace('-',' ').title())
p=pdf/'member-materials-suite-2026.pdf';w.write(p);print(p,len(PdfReader(p).pages),'pages')
