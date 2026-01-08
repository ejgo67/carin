import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

st.set_page_config(layout="wide")

@st.cache_data
def load_data(filepath='../online-retail/Online Retail.xlsx'):
    """
    데이터를 로드하고 기본 전처리를 수행합니다.
    """
    df = pd.read_excel(filepath)
    df.dropna(subset=['CustomerID', 'Description'], inplace=True)
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df['CustomerID'] = df['CustomerID'].astype(int)
    return df

def get_top_customers(df, n=1000):
    """
    주문 건수 기준 상위 고객을 선택합니다.
    """
    top_customers = df['CustomerID'].value_counts().nlargest(n).index
    return df[df['CustomerID'].isin(top_customers)]

# --- Content-Based Filtering Functions ---
@st.cache_data
def get_tfidf_matrix(_df):
    """
    상품 설명에 대한 TF-IDF 행렬을 계산합니다.
    """
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(_df['Description'])
    return tfidf_matrix, tfidf

@st.cache_data
def get_item_similarity(_tfidf_matrix):
    """
    아이템 간 코사인 유사도를 계산합니다.
    """
    return cosine_similarity(_tfidf_matrix, _tfidf_matrix)

def content_based_recommendations(user_id, df, item_similarity, items, num_recommendations=10):
    """
    콘텐츠 기반 추천을 생성합니다.
    """
    if user_id not in df['CustomerID'].unique():
        return pd.DataFrame()

    user_purchases = df[df['CustomerID'] == user_id]['Description'].unique()
    
    # 사용자가 구매한 상품들의 인덱스 찾기
    purchased_indices = [list(items).index(item) for item in user_purchases if item in items]
    
    if not purchased_indices:
        return pd.DataFrame()

    # 사용자가 구매한 상품들과 다른 모든 상품들의 유사도 합산
    total_similarity_scores = item_similarity[purchased_indices].sum(axis=0)
    
    # 추천 점수를 시리즈로 변환
    recommendation_scores = pd.Series(total_similarity_scores, index=items)
    
    # 이미 구매한 상품 제외
    recommendation_scores = recommendation_scores.drop(user_purchases, errors='ignore')
    
    # 점수가 높은 순으로 정렬하여 상위 N개 추천
    recommended_items = recommendation_scores.nlargest(num_recommendations)
    
    return recommended_items

# --- Collaborative Filtering Functions ---
@st.cache_data
def create_user_item_matrix(_df):
    """
    사용자-아이템 행렬을 생성합니다.
    """
    user_item_matrix = _df.groupby(['CustomerID', 'Description'])['InvoiceNo'].count().unstack().fillna(0).applymap(lambda x: 1 if x > 0 else 0)
    return user_item_matrix

@st.cache_data
def get_user_similarity(_user_item_matrix):
    """
    사용자 간 코사인 유사도를 계산합니다.
    """
    user_similarity = cosine_similarity(_user_item_matrix)
    return pd.DataFrame(user_similarity, index=_user_item_matrix.index, columns=_user_item_matrix.index)

def collaborative_filtering_recommendations(user_id, user_item_matrix, user_similarity_df, num_similar_users=5, num_recommendations=10):
    """
    협업 필터링 추천을 생성합니다.
    """
    if user_id not in user_item_matrix.index:
        return []

    similar_scores = user_similarity_df[user_id].sort_values(ascending=False)
    similar_users = similar_scores.iloc[1:num_similar_users+1].index
    
    user_purchased_items = user_item_matrix.loc[user_id]
    user_purchased_items = user_purchased_items[user_purchased_items > 0].index
    
    recommendations = {}
    for sim_user in similar_users:
        sim_user_purchased = user_item_matrix.loc[sim_user]
        sim_user_purchased = sim_user_purchased[sim_user_purchased > 0].index
        
        for item in sim_user_purchased:
            if item not in user_purchased_items:
                if item in recommendations:
                    recommendations[item] += 1
                else:
                    recommendations[item] = 1
    
    sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    return sorted_recommendations[:num_recommendations]

# --- Streamlit App ---
st.title("상품 추천 시스템")

# 데이터 로드
df_raw = load_data()
df_sample = get_top_customers(df_raw, n=500) # 성능을 위해 샘플링
customer_list = sorted(df_sample['CustomerID'].unique())

# --- UI ---
selected_customer = st.selectbox("추천을 받을 고객 ID를 선택하세요:", customer_list)

col1, col2 = st.columns(2)

with col1:
    st.header("사용자 정보")
    if selected_customer:
        st.write(f"**선택된 고객 ID:** {selected_customer}")
        
        customer_purchases = df_sample[df_sample['CustomerID'] == selected_customer]['Description'].value_counts().reset_index()
        customer_purchases.columns = ['상품명', '구매 횟수']
        
        st.write("**최근 구매 내역 (상위 10개):**")
        st.dataframe(customer_purchases.head(10))

with col2:
    st.header("추천 결과")
    recommendation_type = st.radio(
        "추천 방식을 선택하세요:",
        ('콘텐츠 기반 필터링', '협업 필터링')
    )

    if st.button("추천 받기"):
        if recommendation_type == '콘텐츠 기반 필터링':
            with st.spinner('콘텐츠 기반 추천을 생성하는 중...'):
                # 콘텐츠 기반 필터링 준비
                product_descriptions = df_sample[['Description']].drop_duplicates().sort_values('Description').reset_index(drop=True)
                item_list = product_descriptions['Description'].tolist()
                
                tfidf_matrix, _ = get_tfidf_matrix(product_descriptions)
                item_similarity_matrix = get_item_similarity(tfidf_matrix)

                recommendations = content_based_recommendations(selected_customer, df_sample, item_similarity_matrix, item_list)
                
                if not recommendations.empty:
                    st.success(f"**'{selected_customer}'** 님을 위한 **콘텐츠 기반** 추천 상품 목록입니다.")
                    st.table(recommendations.reset_index().rename(columns={'index': '상품명', 0: '추천 점수'}))
                else:
                    st.warning("이 고객에게 추천할 상품을 찾지 못했습니다.")

        elif recommendation_type == '협업 필터링':
            with st.spinner('협업 필터링 추천을 생성하는 중...'):
                # 협업 필터링 준비
                user_item_matrix = create_user_item_matrix(df_sample)
                user_similarity_df = get_user_similarity(user_item_matrix)
                
                recommendations = collaborative_filtering_recommendations(selected_customer, user_item_matrix, user_similarity_df)
                
                if recommendations:
                    st.success(f"**'{selected_customer}'** 님을 위한 **협업 필터링** 추천 상품 목록입니다.")
                    recs_df = pd.DataFrame(recommendations, columns=['상품명', '추천 점수'])
                    st.table(recs_df)
                else:
                    st.warning("이 고객에게 추천할 상품을 찾지 못했습니다.")

st.sidebar.title("About")
st.sidebar.info(
    """
    이 대시보드는 온라인 소매 데이터를 사용하여 고객에게 상품을 추천합니다.
    - **콘텐츠 기반 필터링**: 사용자가 과거에 구매한 상품과 유사한 상품을 추천합니다.
    - **협업 필터링**: 사용자와 유사한 취향을 가진 다른 사용자들이 구매한 상품을 추천합니다.
    
    데이터는 상위 500명의 고객 데이터만 샘플링하여 사용합니다.
    """
)
