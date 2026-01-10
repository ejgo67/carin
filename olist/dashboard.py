
import streamlit as st
import os

def main():
    st.set_page_config(layout="wide")
    st.title("Olist 데이터 분석 대시보드")

    report_path = 'olist/Full_EDA_Report.md'

    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        st.markdown(md_content, unsafe_allow_html=True)
    else:
        st.error(f"'{report_path}' 파일을 찾을 수 없습니다. 먼저 EDA 스크립트를 실행하여 보고서를 생성하세요.")

if __name__ == "__main__":
    main()
