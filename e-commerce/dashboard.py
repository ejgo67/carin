
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from load_data import load_datasets
import datetime as dt

# Streamlit 페이지 설정
st.set_page_config(layout="wide", page_title="이커머스 데이터 분석 대시보드")

@st.cache_data
def load_and_preprocess_data():
    """
    데이터를 로드하고 전처리합니다. 
    generate_eda_report.py의 로직을 재사용하고 결과를 캐시합니다.
    """
    # 데이터 로드
    datasets = load_datasets('e-commerce')
    orders_df = datasets['olist_orders']
    payments_df = datasets['olist_order_payments']
    reviews_df = datasets['olist_order_reviews']
    items_df = datasets['olist_order_items']
    products_df = datasets['olist_products']
    customers_df = datasets['olist_customers']
    translation_df = datasets['product_category_name_translation']

    # 데이터 병합
    df = pd.merge(orders_df, payments_df, on='order_id')
    df = pd.merge(df, reviews_df, on='order_id')
    df = pd.merge(df, items_df, on='order_id')
    df = pd.merge(df, products_df, on='product_id')
    df = pd.merge(df, customers_df, on='customer_id')
    df = pd.merge(df, translation_df, on='product_category_name', how='left')

    # 시간 관련 컬럼 변환
    time_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    for col in time_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
    df['purchase_year'] = df['order_purchase_timestamp'].dt.year

    return df

def main_page(df):
    """
    메인 페이지를 렌더링합니다.
    데이터 개요를 포함합니다.
    """
    st.title("📊 이커머스 데이터 분석 대시보드")
    st.write("이 대시보드는 브라질 이커머스(Olist) 데이터를 분석하고 시각화합니다.")

    st.header("데이터 미리보기")
    st.dataframe(df.head())


def sales_analysis_page(df):
    """
    매출 분석 페이지를 렌더링합니다.
    """
    st.title("📈 매출 분석")
    
    tabs = st.tabs(["월별 매출 추이", "주요 고객 분포 (주별 매출)", "인기 상품 카테고리 (매출 기준)"])
    
    with tabs[0]:
        st.header("월별 매출 추이")
        # 월별 매출 추이: 막대 차트
        df['purchase_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
        monthly_sales = df.groupby('purchase_month')['payment_value'].sum().reset_index()
        fig = px.bar(monthly_sales, x='purchase_month', y='payment_value', title="월별 총 매출 추이", labels={'purchase_month': '구매 월', 'payment_value': '총 매출'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(monthly_sales)
            
    with tabs[1]:
        st.header("주요 고객 분포 (주별 매출)")
        # 주요 고객 분포 (주별 매출): 막대 차트
        state_sales = df.groupby('customer_state')['payment_value'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(state_sales, x='customer_state', y='payment_value', title="상위 10개 주(State)별 총 매출", labels={'customer_state': '주(State)', 'payment_value': '총 매출'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(state_sales)
            
    with tabs[2]:
        st.header("인기 상품 카테고리 (매출 기준)")
        # 인기 상품 카테고리 (매출 기준): 막대 차트
        category_sales = df.groupby('product_category_name_english')['payment_value'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig = px.bar(category_sales, x='product_category_name_english', y='payment_value', title="상위 10개 상품 카테고리별 총 매출", labels={'product_category_name_english': '상품 카테고리', 'payment_value': '총 매출'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(category_sales)


def customer_product_analysis_page(df):
    """
    고객 및 상품 분석 페이지를 렌더링합니다.
    """
    st.title("👥 고객 및 상품 분석")
    tabs = st.tabs(["리뷰 점수 분포", "충성 고객 분석", "상품 가격 및 배송비 분포", "인기 상품"])

    with tabs[0]:
        st.header("리뷰 점수 분포")
        # 리뷰 점수 분포: 수평 막대 차트
        review_scores = df['review_score'].value_counts().sort_values().reset_index()
        fig = px.bar(review_scores, y='review_score', x='count', title="리뷰 점수 분포", orientation='h', labels={'review_score': '리뷰 점수', 'count': '주문 수'})
        fig.update_yaxes(type='category')
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(review_scores)

    with tabs[1]:
        st.header("충성 고객 분석 (상위 10명)")
        # 충성 고객 분석 (상위 10명): 막대 차트
        top_customers = df['customer_unique_id'].value_counts().head(10).reset_index()
        top_customers.columns = ['customer_unique_id', 'order_count']
        fig = px.bar(top_customers, x='customer_unique_id', y='order_count', title="상위 10명 고객의 주문 수", labels={'customer_unique_id': '고객 ID', 'order_count': '주문 수'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(top_customers)

    with tabs[2]:
        st.header("상품 가격 분포")
        # 상품 가격 분포: 히스토그램
        fig = px.histogram(df, x="price", nbins=50, title="상품 가격 분포", labels={'price': '가격', 'count': '상품 수'})
        st.plotly_chart(fig, use_container_width=True)

        st.header("배송비 분포")
        # 배송비 분포 : 히스토그램
        fig = px.histogram(df, x="freight_value", nbins=50, title="배송비 분포", labels={'freight_value': '배송비', 'count': '주문 수'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("가격 및 배송비 데이터 보기"):
            st.dataframe(df[['price', 'freight_value']].describe())

    with tabs[3]:
        st.header("인기 상품 (판매 수량 기준)")
        # 인기 상품(판매수량 기준): 막대 차트
        top_products = df['product_category_name_english'].value_counts().head(10).reset_index()
        fig = px.bar(top_products, x='product_category_name_english', y='count', title="상위 10개 인기 상품 (판매 수량 기준)", labels={'product_category_name_english': '상품 카테고리', 'count': '판매 수량'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(top_products)


def user_behavior_analysis_page(df):
    """
    사용자 행동 분석 페이지를 렌더링합니다.
    """
    st.title("🏃 사용자 행동 분석")
    tabs = st.tabs(["주문 상태 분포", "결제 유형 분석", "시간대별 주문 분포", "고객 세그먼트 분석 (RFM)"])
    
    with tabs[0]:
        st.header("주문 상태 분포")
        # 주문 상태 분포: 막대 차트
        status_counts = df['order_status'].value_counts().reset_index()
        fig = px.bar(status_counts, x='order_status', y='count', title="주문 상태별 주문 수", labels={'order_status': '주문 상태', 'count': '주문 수'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(status_counts)

    with tabs[1]:
        st.header("결제 유형 분석")
        # 결제 유형 분석: 막대 차트
        payment_counts = df['payment_type'].value_counts().reset_index()
        fig = px.bar(payment_counts, x='payment_type', y='count', title="결제 유형별 사용 빈도", labels={'payment_type': '결제 유형', 'count': '빈도'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(payment_counts)
            
    with tabs[2]:
        st.header("시간대별 주문 분포")
        # 시간대별 주문 분포: 막대 차트
        df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
        hourly_orders = df['purchase_hour'].value_counts().sort_index().reset_index()
        fig = px.bar(hourly_orders, x='purchase_hour', y='count', title="시간대별 주문 수", labels={'purchase_hour': '시간', 'count': '주문 수'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(hourly_orders)
            
    with tabs[3]:
        st.header("고객 세그먼트 분석 (RFM)")
        # 고객 세그먼트 분석 (RFM): 막대 차트
        snapshot_date = df['order_purchase_timestamp'].max() + dt.timedelta(days=1)
        # 필요한 컬럼만 추출하여 메모리 사용량 최적화
        rfm_df = df[['customer_unique_id', 'order_id', 'order_purchase_timestamp', 'payment_value']].dropna()

        rfm = rfm_df.groupby('customer_unique_id').agg({
            'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
            'order_id': 'nunique',
            'payment_value': 'sum'
        }).rename(columns={'order_purchase_timestamp': 'Recency', 'order_id': 'Frequency', 'payment_value': 'Monetary'})

        # RFM Scoring
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

        def segment_customer(row):
            if row['RFM_Score'] in ["555", "554", "545", "544", "455"]: return "VIP"
            elif row['R_Score'] >= 4 and row['F_Score'] >= 3: return "Loyal"
            elif row['F_Score'] >= 4 or row['M_Score'] >= 4: return "Potential"
            elif row['R_Score'] <= 2 and row['F_Score'] <= 2: return "At Risk"
            else: return "Normal"

        rfm['Segment'] = rfm.apply(segment_customer, axis=1)
        segment_counts = rfm['Segment'].value_counts().reset_index()

        fig = px.bar(segment_counts, x='Segment', y='count', title="고객 세그먼트별 고객 수", labels={'Segment': '세그먼트', 'count': '고객 수'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(segment_counts)

# --- Main App ---
def main():
    # 데이터 로드
    df = load_and_preprocess_data()

    # 사이드바
    st.sidebar.title("메뉴")
    page = st.sidebar.radio("페이지 선택", ["메인", "매출 분석", "고객 및 상품 분석", "사용자 행동 분석"])
    
    # 페이지 렌더링
    if page == "메인":
        main_page(df)
    elif page == "매출 분석":
        sales_analysis_page(df)
    elif page == "고객 및 상품 분석":
        customer_product_analysis_page(df)
    elif page == "사용자 행동 분석":
        user_behavior_analysis_page(df)

if __name__ == "__main__":
    main()
