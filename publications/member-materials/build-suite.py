from pathlib import Path
from pypdf import PdfWriter, PdfReader
b=Path(__file__).resolve().parent
pdf=b/'pdf'; old=b/'wordpress-snapshot-2026-11-22'
items=[pdf/f'{slug}-reformat-v3.pdf' for slug in ['meeting-script','safety-guidelines','twelve-steps','twelve-traditions','preamble','guiding-principles','integration-and-a-plan-of-action']]
items += [pdf/f'{slug}-reformat-v3.pdf' for slug in ['faq','netiquette','cares-and-considerations','staying-connected']]
items += [pdf/'sponsorship-and-co-travel-reformat-v3.pdf']
w=PdfWriter()
for p in items:w.append(p,outline_item={'meeting-script':'Suggested Meeting Script','twelve-steps':'Twelve Steps of Psychedelics In Recovery™','twelve-traditions':'Twelve Traditions of Psychedelics In Recovery™','faq':'Frequently Asked Questions','cares-and-considerations':'Cares & Considerations','integration-and-a-plan-of-action':'Integration and a Plan of Action','sponsorship-and-co-travel':'Sponsorship & Co-Travel'}.get(p.stem.replace('-reformat-v3',''),p.stem.replace('-reformat-v3','').replace('-',' ').title()))
p=pdf/'member-materials-suite-2026.pdf';w.write(p);print(p,len(PdfReader(p).pages),'pages')
