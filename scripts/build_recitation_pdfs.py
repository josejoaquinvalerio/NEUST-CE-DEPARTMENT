from pathlib import Path
import re, html
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT=Path("compre-1")
W,H=A4
for year in (2017,2018):
    out=ROOT/f"COMPRE_1_{year}_WATERMARKED.pdf"
    pdf=canvas.Canvas(str(out),pagesize=A4)
    for page in (1,2,3):
        source=(ROOT/"pages"/f"{year}-{page}.html").read_text(encoding="utf-8")
        block=re.search(r'<div class="content">(.*?)</div>',source,re.S).group(1)
        text=html.unescape(re.sub(r'<[^>]+>','',block))
        pdf.setFillColorRGB(1,1,1);pdf.rect(0,0,W,H,fill=1,stroke=0)
        pdf.saveState()
        pdf.setFillColorRGB(.79,.88,.94)
        for y in range(95,800,85):
            pdf.saveState()
            pdf.translate(95,y);pdf.rotate(27)
            pdf.setFont("Helvetica-Bold",11)
            pdf.drawString(0,0,"NEUST - CE DEPARTMENT (COMPRE 1)")
            pdf.restoreState()
        pdf.restoreState()
        pdf.setFillColorRGB(.10,.19,.27)
        pdf.setFont("Helvetica-Bold",12)
        pdf.drawString(42,H-37,f"NEUST CE | COMPRE 1 | {year} SET")
        y=H-62
        pdf.setFont("Helvetica",8.4)
        for line in text.splitlines():
            words=line.split()
            if not words:
                y-=8
                continue
            buf=""
            for word in words:
                candidate=(buf+" "+word).strip()
                if stringWidth(candidate,"Helvetica",8.4)>W-84 and buf:
                    pdf.drawString(42,y,buf);y-=11
                    buf=word
                else:buf=candidate
            if buf:
                pdf.drawString(42,y,buf);y-=11
            if y<48:
                pdf.showPage();y=H-55
        pdf.setFont("Helvetica-Bold",8)
        pdf.drawCentredString(W/2,24,"PREPARED BY COMPRE 1 INSTRUCTORS")
        pdf.showPage()
    pdf.save()
    print(out)
