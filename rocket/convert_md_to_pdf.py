import os
import sys
from markdown import markdown

try:
    from weasyprint import HTML
except Exception as e:
    print('Missing weasyprint or its dependencies:', e)
    sys.exit(2)

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    md_path = os.path.join(root, 'rocket', 'EDA_Report.md')
    if not os.path.exists(md_path):
        print('Markdown file not found:', md_path)
        sys.exit(1)
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()
    html_body = markdown(text, extensions=['extra', 'codehilite', 'tables'], output_format='html5')
    html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
    body {{ font-family: "Malgun Gothic", "Apple SD Gothic Neo", "Nanum Gothic", Arial, sans-serif; }}
    img {{ max-width:100%; height:auto; }}
    pre {{ white-space: pre-wrap; font-family: Consolas, monospace; }}
    </style></head><body>{html_body}</body></html>'''
    out_pdf = os.path.join(root, 'rocket', 'EDA_Report.pdf')
    try:
        HTML(string=html, base_url=root).write_pdf(out_pdf)
    except Exception as e:
        print('Failed to write PDF:', e)
        sys.exit(3)
    print('WROTE', out_pdf)

if __name__ == '__main__':
    main()
