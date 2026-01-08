import os
import asyncio
from markdown import markdown

from pyppeteer import launch

async def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    md_path = os.path.join(root, 'rocket', 'EDA_Report.md')
    if not os.path.exists(md_path):
        print('Markdown not found:', md_path)
        return 1
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()
    html_body = markdown(text, extensions=['extra', 'tables'])
    html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
    body {{ font-family: "Malgun Gothic", "Apple SD Gothic Neo", "Nanum Gothic", Arial, sans-serif; padding:20px; }}
    img {{ max-width:100%; height:auto; }}
    pre {{ white-space: pre-wrap; font-family: Consolas, monospace; }}
    table {{ border-collapse: collapse; width: 100%; }}
    table, th, td {{ border: 1px solid #ddd; padding: 6px; }}
    </style></head><body>{html_body}</body></html>'''
    tmp_html = os.path.join(root, 'rocket', 'tmp_eda_report.html')
    with open(tmp_html, 'w', encoding='utf-8') as f:
        f.write(html)

    # Prefer using a local Chrome/Edge if available to avoid downloading Chromium
    possible_paths = [
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    ]
    executable = None
    for p in possible_paths:
        if os.path.exists(p):
            executable = p
            break
    if executable:
        browser = await launch(executablePath=executable, args=['--no-sandbox'])
    else:
        browser = await launch()
    page = await browser.newPage()
    await page.goto('file:///' + tmp_html.replace('\\', '/'))
    out_pdf = os.path.join(root, 'rocket', 'EDA_Report.pdf')
    await page.pdf({'path': out_pdf, 'format': 'A4', 'printBackground': True})
    await browser.close()
    print('WROTE', out_pdf)
    return 0

if __name__ == '__main__':
    asyncio.run(main())
