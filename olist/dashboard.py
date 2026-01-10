
import streamlit as st
import os
import re

def main():
    st.set_page_config(layout="wide")
    st.title("Olist 데이터 분석 대시보드")

    report_path = 'olist/Full_EDA_Report.md'
    
    # The script runs from the root 'ICB', so the image path starts from 'olist'
    image_base_dir = 'olist'

    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Buffer to hold markdown text chunks
        buffer = []
        # Regex to find markdown image tags: ![alt text](path)
        img_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')

        # Find all image matches
        matches = list(img_pattern.finditer(md_content))
        last_index = 0

        for match in matches:
            # Add text before the image to the buffer
            buffer.append(md_content[last_index:match.start()])
            
            # Write buffered markdown content
            if buffer:
                st.markdown("".join(buffer), unsafe_allow_html=True)
                buffer = []

            # Process and display the image
            alt_text = match.group(1)
            md_path = match.group(2) # e.g., ./images/full_plot_1.png
            
            # Build the correct path from the project root
            # The path in markdown is relative, so we combine it with our base dir
            correct_image_path = os.path.normpath(os.path.join(image_base_dir, os.path.dirname(md_path), os.path.basename(md_path)))
            
            if os.path.exists(correct_image_path):
                st.image(correct_image_path, caption=alt_text)
            else:
                st.warning(f"이미지 파일을 찾을 수 없습니다: {correct_image_path}")

            last_index = match.end()

        # Add any remaining text after the last image
        buffer.append(md_content[last_index:])
        if buffer:
            st.markdown("".join(buffer), unsafe_allow_html=True)

    else:
        st.error(f"'{report_path}' 파일을 찾을 수 없습니다. 먼저 EDA 스크립트를 실행하여 보고서를 생성하세요.")

if __name__ == "__main__":
    main()
