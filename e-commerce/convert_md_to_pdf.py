#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마크다운 파일을 PDF로 변환하는 스크립트 (ReportLab 사용)
EDA_Report.md -> EDA_Report.pdf
"""

import os
import sys
from pathlib import Path
import re

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    print('✓ reportlab 모듈 로드 완료')
except ImportError as e:
    print(f'❌ reportlab 로드 오류: {e}')
    sys.exit(1)

# 한글 폰트 등록 시도
try:
    # Windows 시스템 폰트 경로
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('MalgunGothic', font_path))
        title_style = ParagraphStyle(
            'TitleStyle',
            fontName='MalgunGothic',
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # center
        )
        heading_style = ParagraphStyle(
            'HeadingStyle',
            fontName='MalgunGothic',
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        )
        normal_style = ParagraphStyle(
            'NormalStyle',
            fontName='MalgunGothic',
            fontSize=11,
            leading=14,
            alignment=4  # justify
        )
    else:
        print('⚠ 한글 폰트를 찾을 수 없습니다. 기본 영문 폰트를 사용합니다.')
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        heading_style = styles['Heading2']
        normal_style = styles['BodyText']
except Exception as e:
    print(f'⚠ 폰트 등록 오류: {e}. 기본 폰트를 사용합니다.')
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['BodyText']

# 파일 경로 설정
md_file = 'e-commerce/EDA_Report.md'
pdf_file = 'e-commerce/EDA_Report.pdf'

print('\n' + '='*60)
print('마크다운 → PDF 변환 (ReportLab)')
print('='*60)

# 1. 마크다운 파일 확인
if not os.path.exists(md_file):
    print(f'❌ 파일을 찾을 수 없습니다: {md_file}')
    sys.exit(1)

print(f'✓ 입력 파일 확인: {md_file}')

# 2. 마크다운 읽기
try:
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    print(f'✓ 마크다운 파일 읽기 완료 ({len(md_content)} bytes)')
except Exception as e:
    print(f'❌ 파일 읽기 오류: {e}')
    sys.exit(1)

# 3. 마크다운 파싱 및 PDF 콘텐츠 생성
story = []

# 제목 추가
story.append(Paragraph('브라질 이커머스 데이터 분석 보고서', title_style))
story.append(Spacer(1, 0.3 * inch))

# 마크다운 줄 단위로 파싱
lines = md_content.split('\n')
current_section = []

for i, line in enumerate(lines):
    # H1 제목
    if line.startswith('# ') and not line.startswith('## '):
        if current_section:
            story.append(Paragraph('\n'.join(current_section), normal_style))
            current_section = []
        title = line.replace('# ', '').strip()
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(title, title_style))
    
    # H2 제목
    elif line.startswith('## '):
        if current_section:
            story.append(Paragraph('\n'.join(current_section), normal_style))
            current_section = []
        subtitle = line.replace('## ', '').strip()
        story.append(Paragraph(subtitle, heading_style))
    
    # 이미지 (마크다운 형식: ![alt](path))
    elif line.startswith('!['):
        if current_section:
            story.append(Paragraph('\n'.join(current_section), normal_style))
            current_section = []
        try:
            match = re.search(r'!\[.*?\]\((.*?)\)', line)
            if match:
                img_path = match.group(1)
                # 상대 경로를 절대 경로로 변환
                abs_img_path = os.path.join(os.getcwd(), img_path)
                if os.path.exists(abs_img_path):
                    img = Image(abs_img_path, width=6*inch, height=3.5*inch)
                    story.append(img)
                    story.append(Spacer(1, 0.2 * inch))
                else:
                    story.append(Paragraph(f'[이미지: {img_path} (찾을 수 없음)]', normal_style))
        except Exception as e:
            print(f'⚠ 이미지 처리 오류: {line} ({e})')
    
    # 표 (마크다운 표 형식)
    elif line.startswith('|'):
        if current_section:
            story.append(Paragraph('\n'.join(current_section), normal_style))
            current_section = []
        
        # 표 데이터 수집
        table_lines = []
        for j in range(i, min(i+10, len(lines))):
            if lines[j].startswith('|'):
                table_lines.append(lines[j])
            else:
                break
        
        if len(table_lines) >= 2:
            # 표 파싱
            rows = []
            for tline in table_lines:
                cells = [cell.strip() for cell in tline.split('|')[1:-1]]
                rows.append(cells)
            
            # 헤더와 데이터 분리
            if len(rows) > 2:
                table_data = [rows[0]] + rows[2:]  # 헤더 + 데이터 (구분선 제외)
                
                if table_data:
                    tbl = Table(table_data, colWidths=[2*inch]*len(table_data[0]))
                    tbl.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(tbl)
                    story.append(Spacer(1, 0.3 * inch))
    
    # 일반 텍스트
    elif line.strip() and not line.startswith('#'):
        current_section.append(line.strip())

# 남은 콘텐츠 처리
if current_section:
    story.append(Paragraph('\n'.join(current_section), normal_style))

# 4. PDF 생성
try:
    print(f'\n변환 중...')
    doc = SimpleDocTemplate(pdf_file, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    doc.build(story)
    print(f'✓ PDF 파일 생성: {pdf_file}')
except Exception as e:
    print(f'❌ PDF 생성 오류: {e}')
    sys.exit(1)

# 5. 결과 확인
if os.path.exists(pdf_file):
    pdf_size = os.path.getsize(pdf_file)
    print(f'\n✓ PDF 생성 완료!')
    print(f'  파일 크기: {pdf_size:,} bytes')
    print(f'  경로: {os.path.abspath(pdf_file)}')
else:
    print(f'❌ PDF 파일이 생성되지 않았습니다.')
    sys.exit(1)

print('\n' + '='*60)
print('완료: 마크다운 → PDF 변환 성공')
print('='*60)
