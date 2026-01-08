
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

def install_libraries():
    """필요한 라이브러리가 설치되어 있는지 확인하고, 설치되지 않았다면 설치 안내 메시지를 출력합니다."""
    try:
        import sklearn
    except ImportError:
        print("scikit-learn 라이브러리가 설치되어 있지 않습니다.")
        print("터미널에서 'pip install scikit-learn' 명령어를 실행하여 설치해주세요.")
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

def calculate_similarity(df):
    """
    TF-IDF 벡터를 생성하고 상품 설명 간의 코사인 유사도를 계산합니다.
    """
    print("TF-IDF 벡터 생성 및 코사인 유사도 계산 중...")
    # Description의 유니크한 값 추출
    unique_descriptions = df['Description'].unique()
    
    # TF-IDF Vectorizer 생성 (불용어 처리)
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    
    # TF-IDF 행렬 생성
    tfidf_matrix = tfidf_vectorizer.fit_transform(unique_descriptions)
    
    # 코사인 유사도 계산
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Description과 인덱스를 매핑하는 Series 생성
    indices = pd.Series(range(len(unique_descriptions)), index=unique_descriptions).to_dict()
    
    print("유사도 계산 완료.")
    return cosine_sim, indices, unique_descriptions

def get_recommendations(description, cosine_sim, indices, unique_descriptions):
    """
    특정 상품과 가장 유사한 상품 10개를 추천합니다.
    """
    if description not in indices:
        return []
        
    idx = indices[description]
    
    # 해당 상품과의 유사도 스코어 가져오기
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # 유사도 스코어를 기준으로 내림차순 정렬
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # 자기 자신을 제외한 상위 10개 상품의 인덱스 가져오기
    sim_scores = sim_scores[1:11]
    
    # 추천된 상품의 인덱스 및 유사도 스코어
    recommended_indices = [i[0] for i in sim_scores]
    recommended_scores = [i[1] for i in sim_scores]
    
    # 추천된 상품의 Description과 유사도 스코어를 튜플 리스트로 반환
    recommendations = []
    for i, score in zip(recommended_indices, recommended_scores):
        recommendations.append((unique_descriptions[i], score))
        
    return recommendations

def main():
    """메인 실행 함수"""
    if not install_libraries():
        return

    filepath = 'online-retail/Online Retail.xlsx'
    df_valid = load_and_preprocess_data(filepath)
    
    cosine_sim, indices, unique_descriptions = calculate_similarity(df_valid)
    
    # 랜덤하게 5개 상품 선택
    random_items = random.sample(list(unique_descriptions), 5)
    
    print("\n--- 콘텐츠 기반 추천 결과 ---")
    for item in random_items:
        print(f"\n원본 상품: {item}")
        recommendations = get_recommendations(item, cosine_sim, indices, unique_descriptions)
        if recommendations:
            print("추천 상품 목록:")
            for desc, score in recommendations:
                print(f"  - {desc} (유사도: {score:.4f})")
        else:
            print("추천 상품을 찾을 수 없습니다.")

if __name__ == '__main__':
    main()
