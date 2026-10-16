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
            after=re.sub(r'\b(?:20(?:17|18)\s+)?Replacement\s+Set\b\s*','',after,flags=re.I)\n            after=re.sub(r'\b20(?:17|18)\s+Replacement\s+Set\b\s*','',after,flags=re.I)
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
        label='NEUST - CE DEPARTMENT (COMPRE 1)'
        # One-line watermark, rotated 15 degrees counter-clockwise from the +x axis.
        bbox=font.getbbox(label)
        pad=18
        stamp=Image.new('RGBA',(bbox[2]-bbox[0]+pad*2,bbox[3]-bbox[1]+pad*2),(255,255,255,0))
        ImageDraw.Draw(stamp).text((pad-bbox[0],pad-bbox[1]),label,font=font,fill=(26,107,163,82))
        stamp=stamp.rotate(15,expand=True,resample=Image.Resampling.BICUBIC)
        # Two columns; each watermark is centered on its half-page column.
        for row in range(10):
            cy=int((row+0.5)*base.height/10)
            for col in range(2):
                cx=int((col+0.5)*base.width/2)
                layer.alpha_composite(stamp,(cx-stamp.width//2,cy-stamp.height//2))
        image=Image.alpha_composite(base,layer).convert('RGB')
        image.save(ROOT/'pages'/f'{year}-{index+1}.webp','WEBP',quality=87,method=6)
    (ROOT/f'{year}-page-count.txt').write_text(str(len(pdf)))
    print(year,edits,'edits',len(pdf),'pages')
