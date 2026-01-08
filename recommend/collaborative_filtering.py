
import pandas as pd
import numpy as np
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
    """
    print("데이터를 로드하고 전처리하는 중...")
    df = pd.read_excel(filepath)
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df.dropna(subset=['CustomerID', 'Description'], inplace=True)
    df['CustomerID'] = df['CustomerID'].astype(int)
    print("데이터 전처리 완료.")
    return df

def create_user_item_matrix(df):
    """
    사용자-아이템 행렬을 생성합니다.
    구매 여부를 1로 표시합니다 (메모리 효율성을 위해).
    """
    print("사용자-아이템 행렬 생성 중...")
    # 간단한 협업 필터링을 위해 수량이 아닌 구매 여부(1)로 처리
    user_item_df = df.groupby(['CustomerID', 'Description'])['InvoiceNo'].count().unstack().fillna(0).applymap(lambda x: 1 if x > 0 else 0)
    print("사용자-아이템 행렬 생성 완료.")
    return user_item_df

def get_recommendations_for_user(user_id, user_item_matrix, user_similarity_df, num_similar_users=5, num_recommendations=10):
    """
    특정 사용자를 위한 상품을 추천합니다.
    """
    # 해당 사용자와 다른 모든 사용자 간의 유사도 가져오기
    similar_scores = user_similarity_df[user_id].sort_values(ascending=False)
    
    # 자기 자신을 제외한 가장 유사한 사용자 N명 선택
    similar_users = similar_scores.iloc[1:num_similar_users+1].index
    
    # 대상 사용자가 이미 구매한 상품 목록
    user_purchased_items = user_item_matrix.loc[user_id]
    user_purchased_items = user_purchased_items[user_purchased_items > 0].index
    
    # 유사한 사용자들이 구매한 모든 상품 집계
    recommendations = {}
    for sim_user in similar_users:
        # 유사한 사용자가 구매한 상품 목록 (아직 대상 사용자가 구매하지 않은 것)
        sim_user_purchased = user_item_matrix.loc[sim_user]
        sim_user_purchased = sim_user_purchased[sim_user_purchased > 0].index
        
        for item in sim_user_purchased:
            if item not in user_purchased_items:
                if item in recommendations:
                    recommendations[item] += 1
                else:
                    recommendations[item] = 1
    
    # 가장 많이 추천된 순서(등장 빈도)로 정렬
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    
    # 상위 N개 상품 추천
    return sorted_recommendations[:num_recommendations]


def main():
    """메인 실행 함수"""
    if not install_libraries():
        return
        
    filepath = 'online-retail/Online Retail.xlsx'
    df_valid = load_and_preprocess_data(filepath)
    
    # 데이터가 너무 크면 메모리 오류가 발생할 수 있으므로, 일부 데이터만 사용
    # 여기서는 시간 관계상 CustomerID 상위 1000명만 사용
    top_customers = df_valid['CustomerID'].value_counts().nlargest(1000).index
    df_sample = df_valid[df_valid['CustomerID'].isin(top_customers)]

    user_item_matrix = create_user_item_matrix(df_sample)
    
    # 사용자 간 코사인 유사도 계산
    print("사용자 간 유사도 계산 중...")
    user_similarity = cosine_similarity(user_item_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)
    print("유사도 계산 완료.")

    # 랜덤하게 5명 사용자 선택
    random_users = random.sample(list(user_item_matrix.index), 5)
    
    print("\n--- 협업 필터링 추천 결과 ---")
    for user in random_users:
        print(f"\n사용자 ID: {user} 님을 위한 추천")
        # 유사도 높은 사용자 찾기
        top_similar_user = user_similarity_df[user].sort_values(ascending=False).index[1]
        similarity_score = user_similarity_df[user].sort_values(ascending=False).iloc[1]
        print(f"(가장 유사한 사용자: {top_similar_user}, 유사도: {similarity_score:.4f})")

        # 추천 상품 목록 가져오기
        recommendations = get_recommendations_for_user(user, user_item_matrix, user_similarity_df)
        
        if recommendations:
            print("추천 상품 목록:")
            for item, score in recommendations:
                print(f"  - {item} (추천 점수: {score})")
        else:
            print("추천할 상품이 없습니다.")


if __name__ == '__main__':
    main()
