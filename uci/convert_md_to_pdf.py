from pathlib import Path
import markdown
from xhtml2pdf import pisa
try:
    from reportlab.pdfbase import ttfonts, pdfmetrics
except Exception:
    ttfonts = None
    pdfmetrics = None
import re
import base64
import mimetypes


def inline_images_in_html(html: str, base_dir: Path) -> str:
    # Find img tags and inline local images as base64
    def repl(m):
        src = m.group(1)
        if src.startswith('data:') or src.startswith('http'):
            return m.group(0)
        img_path = (base_dir / src).resolve()
        if not img_path.exists():
            return m.group(0)
        data = img_path.read_bytes()
        mime, _ = mimetypes.guess_type(str(img_path))
        if mime is None:
            mime = 'image/png'
        b64 = base64.b64encode(data).decode('ascii')
        return m.group(0).replace(src, f'data:{mime};base64,{b64}')

    return re.sub(r'<img[^>]+src="([^"]+)"', repl, html)


def md_to_pdf(md_path: Path, pdf_path: Path):
    text = md_path.read_text(encoding='utf-8')
    # Convert markdown to HTML
    html = markdown.markdown(text, extensions=['fenced_code', 'tables'])

    # Inline images as base64 so xhtml2pdf can embed them
    html_inlined = inline_images_in_html(html, md_path.parent)

    # Attempt to embed a Korean TTF (Malgun Gothic) from Windows fonts to prevent 한글 깨짐.
    font_face_css = ''
    try:
        possible_paths = [
            Path('C:/Windows/Fonts/malgun.ttf'),
            Path('C:/Windows/Fonts/Malgun.ttf'),
            Path('C:/Windows/Fonts/맑은 고딕.ttf')
        ]
        ttf_path = None
        for p in possible_paths:
            if p.exists():
                ttf_path = p
                break
        if ttf_path is not None:
            # Register TTF with reportlab directly to avoid xhtml2pdf @font-face file issues
            try:
                if pdfmetrics is not None:
                    pdfmetrics.registerFont(ttfonts.TTFont('MalgunGothicSys', str(ttf_path)))
                body_font = "'MalgunGothicSys', DejaVu Sans, Arial, sans-serif"
            except Exception:
                body_font = "DejaVu Sans, Arial, sans-serif"
        else:
            body_font = "DejaVu Sans, Arial, sans-serif"
    except Exception:
        body_font = "DejaVu Sans, Arial, sans-serif"

    head_css = font_face_css + "\n" + f"body {{ font-family: {body_font}; }}\nimg {{ max-width: 100%; height: auto; }}\npre {{ white-space: pre-wrap; }}\n"
    full_html = """<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<style>
""" + head_css + """
</style>
</head>
<body>
""" + html_inlined + """
</body>
</html>"""
    with pdf_path.open('wb') as f:
        pisa_status = pisa.CreatePDF(full_html, dest=f)
    return pisa_status.err


if __name__ == '__main__':
    base = Path(__file__).resolve().parent
    md = base / 'EDA_Report.md'
    pdf = base / 'EDA_Report.pdf'
    if not md.exists():
        print('EDA_Report.md not found')
    else:
        err = md_to_pdf(md, pdf)
        if err:
            print('PDF 생성 중 오류 발생')
        else:
            print('PDF 생성 완료:', pdf)
