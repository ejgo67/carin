
import pandas as pd
import numpy as np
import csv

def install_libraries():
    """필요한 라이브러리가 설치되어 있는지 확인하고, 설치되지 않았다면 설치 안내 메시지를 출력합니다."""
    try:
        import torch
        import sentence_transformers
    except ImportError:
        print("PyTorch 또는 sentence-transformers 라이브러리가 설치되어 있지 않습니다.")
        print("터미널에서 'pip install torch sentence-transformers' 명령어를 실행하여 설치해주세요.")
        return False
    return True

def load_and_preprocess_data(filepath):
    """
    데이터를 로드하고 전처리합니다.
    - 'C'로 시작하는 InvoiceNo (반품) 제거
    - CustomerID가 없는 데이터 제거
    - Description이 없는 데이터 제거
    """
    print("데이터를 로드하고 전처리하는 중...")
    df = pd.read_excel(filepath)
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df.dropna(subset=['CustomerID', 'Description'], inplace=True)
    df['CustomerID'] = df['CustomerID'].astype(int)
    print("데이터 전처리 완료.")
    return df

def main():
    """메인 실행 함수"""
    if not install_libraries():
        return

    from sentence_transformers import SentenceTransformer

    filepath = 'online-retail/Online Retail.xlsx'
    df_valid = load_and_preprocess_data(filepath)
    
    unique_descriptions = df_valid['Description'].unique()
    
    print("임베딩 모델을 로드하는 중... (시간이 걸릴 수 있습니다)")
    # 허깅페이스의 경량 모델 로드
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("상품 설명을 임베딩하는 중...")
    # 설명 임베딩 생성
    embeddings = model.encode(unique_descriptions, show_progress_bar=True)
    
    # 벡터 파일 (vectors.tsv) 저장
    print("'recommend/vectors.tsv' 파일 저장 중...")
    with open('recommend/vectors.tsv', 'w', newline='', encoding='utf-8') as f_vectors:
        writer = csv.writer(f_vectors, delimiter='\t')
        writer.writerows(embeddings)
        
    # 메타데이터 파일 (metadata.tsv) 저장
    print("'recommend/metadata.tsv' 파일 저장 중...")
    with open('recommend/metadata.tsv', 'w', newline='', encoding='utf-8') as f_metadata:
        writer = csv.writer(f_metadata, delimiter='\t')
        for desc in unique_descriptions:
            writer.writerow([desc])
            
    print("\nTSV 파일 생성이 완료되었습니다.")
    print("TensorFlow Embedding Projector (https://projector.tensorflow.org/) 에 다음 파일들을 업로드하여 시각화할 수 있습니다:")
    print("- Vectors: recommend/vectors.tsv")
    print("- Metadata: recommend/metadata.tsv")

if __name__ == '__main__':
    main()
