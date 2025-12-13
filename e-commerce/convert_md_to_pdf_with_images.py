#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
마크다운 파일을 PDF로 변환하는 스크립트 (이미지 포함)
EDA_Report.md -> EDA_Report.pdf
"""

import os
import sys
import re
from pathlib import Path

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
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('MalgunGothic', font_path))
        title_style = ParagraphStyle(
            'TitleStyle',
            fontName='MalgunGothic',
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1
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
            leading=14
        )
        print('✓ Malgun Gothic 폰트 등록 완료')
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

# 파일 경로 설정 (e-commerce 폴더 기준)
md_file = 'EDA_Report.md'
pdf_file = 'EDA_Report.pdf'
images_dir = 'images'

print('\n' + '='*60)
print('마크다운 → PDF 변환 (이미지 포함)')
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
skip_until = -1  # 표 처리 후 스킵할 줄 인덱스

for i, line in enumerate(lines):
    # 이미 처리된 줄 스킵 (표의 경우)
    if i < skip_until:
        continue
    
    # H1 제목 (## 제외)
    if line.startswith('# ') and not line.startswith('## '):
        if current_section:
            text = ' '.join(current_section).strip()
            if text:
                story.append(Paragraph(text, normal_style))
            current_section = []
        title = line.replace('# ', '').strip()
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(title, title_style))
    
    # H2 제목
    elif line.startswith('## '):
        if current_section:
            text = ' '.join(current_section).strip()
            if text:
                story.append(Paragraph(text, normal_style))
            current_section = []
        subtitle = line.replace('## ', '').strip()
        story.append(Paragraph(subtitle, heading_style))
    
    # 이미지 (마크다운 형식: ![alt](path))
    elif line.startswith('!['):
        if current_section:
            text = ' '.join(current_section).strip()
            if text:
                story.append(Paragraph(text, normal_style))
            current_section = []
        
        try:
            match = re.search(r'!\[.*?\]\((.*?)\)', line)
            if match:
                img_path = match.group(1)
                print(f'  이미지 처리: {img_path}')
                
                # 상대 경로 정규화 (../ 제거)
                img_path_normalized = img_path.replace('../e-commerce/', '').replace('../', '')
                abs_img_path = os.path.join(os.getcwd(), img_path_normalized)
                
                if os.path.exists(abs_img_path):
                    try:
                        img = Image(abs_img_path, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 0.2 * inch))
                        print(f'    ✓ 이미지 추가됨: {abs_img_path}')
                    except Exception as e:
                        print(f'    ❌ 이미지 로드 오류: {e}')
                        story.append(Paragraph(f'[이미지 로드 실패: {img_path}]', normal_style))
                else:
                    print(f'    ⚠ 이미지 파일 없음: {abs_img_path}')
                    # 파일명만으로도 찾기 시도
                    filename = os.path.basename(img_path)
                    alt_path = os.path.join(os.getcwd(), images_dir, filename)
                    if os.path.exists(alt_path):
                        try:
                            img = Image(alt_path, width=6*inch, height=4*inch)
                            story.append(img)
                            story.append(Spacer(1, 0.2 * inch))
                            print(f'    ✓ 이미지 추가됨 (대체 경로): {alt_path}')
                        except Exception as e:
                            print(f'    ❌ 이미지 로드 오류: {e}')
                    else:
                        story.append(Paragraph(f'[이미지를 찾을 수 없음: {img_path}]', normal_style))
        except Exception as e:
            print(f'⚠ 이미지 처리 오류: {line} ({e})')
    
    # 표 (마크다운 표 형식: | 로 시작)
    elif line.startswith('|'):
        if current_section:
            text = ' '.join(current_section).strip()
            if text:
                story.append(Paragraph(text, normal_style))
            current_section = []
        
        # 표 데이터 수집
        table_lines = []
        for j in range(i, min(i+20, len(lines))):
            if lines[j].startswith('|'):
                table_lines.append(lines[j])
            elif table_lines:  # 표가 이미 시작했는데 | 가 없으면 종료
                break
        
        if len(table_lines) >= 2:
            # 표 파싱
            rows = []
            for tline in table_lines:
                cells = [cell.strip() for cell in tline.split('|')[1:-1]]
                rows.append(cells)
            
            # 헤더와 데이터 분리 (마크다운: 헤더, 구분선, 데이터)
            if len(rows) > 2:
                table_data = [rows[0]] + rows[2:]  # 헤더 + 데이터
                
                if table_data:
                    try:
                        # 컬럼 너비 자동 계산
                        col_count = len(table_data[0])
                        col_width = 7.5 * inch / col_count
                        tbl = Table(table_data, colWidths=[col_width]*col_count)
                        
                        tbl.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ]))
                        
                        story.append(tbl)
                        story.append(Spacer(1, 0.3 * inch))
                    except Exception as e:
                        print(f'⚠ 표 생성 오류: {e}')
        
        skip_until = i + len(table_lines)
    
    # 일반 텍스트
    elif line.strip() and not line.startswith('#'):
        current_section.append(line.strip())

# 남은 콘텐츠 처리
if current_section:
    text = ' '.join(current_section).strip()
    if text:
        story.append(Paragraph(text, normal_style))

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
print('완료: 마크다운 → PDF 변환 성공 (이미지 포함)')
print('='*60)
