from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT=Path('compre-1')
(ROOT/'pages').mkdir(parents=True,exist_ok=True)
pdf=fitz.open('/tmp/neust-2019.pdf')
if len(pdf)!=4:
    raise RuntimeError(f'Expected 4 pages for verified 2019 questionnaire, got {len(pdf)}')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
label='NEUST - CE DEPARTMENT (COMPRE 1)'
bbox=font.getbbox(label)
pad=18
stamp=Image.new('RGBA',(bbox[2]-bbox[0]+pad*2,bbox[3]-bbox[1]+pad*2),(255,255,255,0))
ImageDraw.Draw(stamp).text((pad-bbox[0],pad-bbox[1]),label,font=font,fill=(26,107,163,82))
stamp=stamp.rotate(15,expand=True,resample=Image.Resampling.BICUBIC)
for index,page in enumerate(pdf):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False)
    base=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('RGBA')
    layer=Image.new('RGBA',base.size,(255,255,255,0))
    for row in range(10):
        cy=int((row+0.5)*base.height/10)
        for col in range(2):
            cx=int((col+0.5)*base.width/2)
            layer.alpha_composite(stamp,(cx-stamp.width//2,cy-stamp.height//2))
    Image.alpha_composite(base,layer).convert('RGB').save(ROOT/'pages'/f'2019-{index+1}.webp','WEBP',quality=87,method=6)
print('2019 verified PDF rendered:',len(pdf),'pages')
