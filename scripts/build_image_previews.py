from pathlib import Path
import re, subprocess
from docx import Document
import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT=Path('compre-1')
(ROOT/'pages').mkdir(parents=True,exist_ok=True)
fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
for year in (2017,2018):
    src=Path(f'/tmp/neust-{year}.docx')
    if not src.read_bytes()[:2]==b'PK':
        raise RuntimeError(f'{year} source is not a Word file')
    doc=Document(src)
    edits=0
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            before=run.text
            after=re.sub(r'\bSIT\s*:\s*','',before,flags=re.I)
            after=re.sub(r'\(\s*(?:May|Nov(?:ember)?)\s+20(?:17|18)\s*\)\s*','',after,flags=re.I)
            if after!=before:
                run.text=after
                edits+=1
    edited=ROOT/f'COMPRE_1_{year}_EDITED.docx'
    doc.save(edited)
    subprocess.run(['libreoffice','--headless','--convert-to','pdf','--outdir',str(ROOT),str(edited)],check=True)
    pdf=fitz.open(ROOT/f'COMPRE_1_{year}_EDITED.pdf')
    font=ImageFont.truetype(fontfile,20)
    for index,page in enumerate(pdf):
        pix=page.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False)
        base=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('RGBA')
        layer=Image.new('RGBA',base.size,(255,255,255,0))
        painter=ImageDraw.Draw(layer)
        for row in range(10):
            for col in range(2):
                x=int((col+0.03)*base.width/2)
                y=42+row*int(base.height/10)
                painter.text((x,y),'NEUST - CE DEPARTMENT',font=font,fill=(26,107,163,78))
                painter.text((x,y+23),'(COMPRE 1)',font=font,fill=(26,107,163,78))
        image=Image.alpha_composite(base,layer).convert('RGB')
        image.save(ROOT/'pages'/f'{year}-{index+1}.webp','WEBP',quality=87,method=6)
    (ROOT/f'{year}-page-count.txt').write_text(str(len(pdf)))
    print(year,edits,'edits',len(pdf),'pages')
