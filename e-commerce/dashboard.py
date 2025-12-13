
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
        df[col] = pd.to_datetime(df[col])
        
    df['purchase_year'] = df['order_purchase_timestamp'].dt.year

    return df

def main_page(df):
    """
    메인 페이지를 렌더링합니다.
    데이터 개요와 검색 기능을 포함합니다.
    """
    st.title("📊 이커머스 데이터 분석 대시보드")
    st.write("이 대시보드는 브라질 이커머스(Olist) 데이터를 분석하고 시각화합니다.")

    st.header("데이터 미리보기")
    st.dataframe(df.head())

    st.header("데이터 검색")
    search_col = st.radio("검색할 컬럼 선택", ('상품 카테고리 (영문)', '주문 ID'))
    
    if search_col == '상품 카테고리 (영문)':
        search_term = st.text_input("검색할 상품 카테고리(영문)를 입력하세요:")
        if search_term:
            results = df[df['product_category_name_english'].str.contains(search_term, case=False, na=False)]
            st.dataframe(results)
    else: # 주문 ID
        search_term = st.text_input("검색할 주문 ID를 입력하세요:")
        if search_term:
            results = df[df['order_id'].str.contains(search_term, case=False, na=False)]
            st.dataframe(results)


def sales_analysis_page(df):
    """
    매출 분석 페이지를 렌더링합니다.
    """
    st.title("📈 매출 분석")
    
    tabs = st.tabs(["월별 매출 추이", "주요 고객 분포 (주별 매출)", "인기 상품 카테고리 (매출 기준)"])
    
    with tabs[0]:
        st.header("월별 매출 추이")
        # 4. 월별 매출 추이: 막대 차트
        df['purchase_month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
        monthly_sales = df.groupby('purchase_month')['payment_value'].sum().reset_index()
        fig = px.bar(monthly_sales, x='purchase_month', y='payment_value', title="월별 총 매출 추이", labels={'purchase_month': '구매 월', 'payment_value': '총 매출'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(monthly_sales)
            
    with tabs[1]:
        st.header("주요 고객 분포 (주별 매출)")
        # 5. 주요 고객 분포 (주별 매출): 막대 차트
        state_sales = df.groupby('customer_state')['payment_value'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(state_sales, x='customer_state', y='payment_value', title="상위 10개 주(State)별 총 매출", labels={'customer_state': '주(State)', 'payment_value': '총 매출'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(state_sales)
            
    with tabs[2]:
        st.header("인기 상품 카테고리 (매출 기준)")
        # 6. 인기 상품 카테고리 (매출 기준): 라인 차트와 막대 차트
        category_sales = df.groupby('product_category_name_english')['payment_value'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=category_sales['product_category_name_english'], y=category_sales['payment_value'], name='매출액 (막대)'))
        fig.add_trace(go.Scatter(x=category_sales['product_category_name_english'], y=category_sales['payment_value'], name='매출액 (라인)', mode='lines+markers'))
        
        fig.update_layout(
            title="상위 10개 상품 카테고리별 총 매출",
            xaxis_title="상품 카테고리",
            yaxis_title="총 매출"
        )
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
        # 3. 리뷰 점수 분포: 수평 막대 차트
        review_scores = df['review_score'].value_counts().sort_values().reset_index()
        fig = px.bar(review_scores, y='review_score', x='count', title="리뷰 점수 분포", orientation='h', labels={'review_score': '리뷰 점수', 'count': '주문 수'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(review_scores)

    with tabs[1]:
        st.header("충성 고객 분석 (상위 10명)")
        # 8. 충성 고객 분석 (상위 10명): plotly.graph_objects.Heatmap 사용
        top_customers = df['customer_unique_id'].value_counts().head(10).reset_index()
        top_customers.columns = ['customer_unique_id', 'order_count']
        fig = go.Figure(data=go.Heatmap(
                   z=[top_customers['order_count']],
                   x=top_customers['customer_unique_id'],
                   y=['주문 수'],
                   hoverongaps=False,
                   colorscale='Viridis'))
        fig.update_layout(title='상위 10명 고객의 주문 수')
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(top_customers)

    with tabs[2]:
        st.header("상품 가격 분포")
        # 9. 상품 가격 분포: plotly.graph_objects.Heatmap 사용. 첫 번째 열의 이름은 'Acquisition'으로 지정합니다.
        price_bins = pd.cut(df['price'], bins=10)
        price_dist = df.groupby(price_bins, observed=False)['price'].count().reset_index()
        price_dist.columns = ['가격 범위', '상품 수']

        fig = go.Figure(data=go.Heatmap(
                   z=[price_dist['상품 수']],
                   x=price_dist['가격 범위'].astype(str),
                   y=['상품 수'],
                   hoverongaps=False,
                   colorscale='Blues'))
        fig.update_layout(title='상품 가격 분포')
        fig.update_yaxes(autorange="reversed", ticktext=["Acquisition"], tickvals=[0]) # 첫 번째 열 이름 지정
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("가격대별 상품 수 데이터 보기"):
            st.dataframe(price_dist)

        st.header("배송비 분포")
        # 10. 배송비 분포 : 라인 차트
        freight_dist = df['freight_value'].value_counts().sort_index().reset_index()
        fig = px.line(freight_dist, x='freight_value', y='count', title="배송비 분포", labels={'freight_value': '배송비', 'count': '주문 수'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(freight_dist)

    with tabs[3]:
        st.header("인기 상품 (판매 수량 기준)")
        # 11. 인기 상품(판매수량 기준): 막대 차트
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
        # 1. 주문 상태 분포: 라인 차트
        status_counts = df['order_status'].value_counts().reset_index()
        fig = px.line(status_counts, x='order_status', y='count', title="주문 상태별 주문 수", markers=True, labels={'order_status': '주문 상태', 'count': '주문 수'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(status_counts)

    with tabs[1]:
        st.header("결제 유형 분석")
        # 2. 결제 유형 분석: 막대 차트
        payment_counts = df['payment_type'].value_counts().reset_index()
        fig = px.bar(payment_counts, x='payment_type', y='count', title="결제 유형별 사용 빈도", labels={'payment_type': '결제 유형', 'count': '빈도'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(payment_counts)
            
    with tabs[2]:
        st.header("시간대별 주문 분포")
        # 7. 시간대별 주문 분포: 막대 차트
        df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
        hourly_orders = df['purchase_hour'].value_counts().sort_index().reset_index()
        fig = px.bar(hourly_orders, x='purchase_hour', y='count', title="시간대별 주문 수", labels={'purchase_hour': '시간', 'count': '주문 수'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(hourly_orders)
            
    with tabs[3]:
        st.header("고객 세그먼트 분석 (RFM)")
        # 12. 고객 세그먼트 분석 (RFM): 라인 차트
        snapshot_date = df['order_purchase_timestamp'].max() + dt.timedelta(days=1)
        rfm = df.groupby('customer_unique_id').agg({
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

        fig = px.line(segment_counts, x='Segment', y='count', title="고객 세그먼트별 고객 수", markers=True, labels={'Segment': '세그먼트', 'count': '고객 수'})
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
    
    st.sidebar.title("필터")
    
    # 연도 필터
    all_years = sorted(df['purchase_year'].unique())
    selected_year = st.sidebar.selectbox("연도 선택", ["전체"] + all_years)
    
    # 국가 필터
    all_states = sorted(df['customer_state'].unique())
    selected_state = st.sidebar.selectbox("주(State) 선택", ["전체"] + all_states)

    # 필터링된 데이터
    filtered_df = df.copy()
    if selected_year != "전체":
        filtered_df = filtered_df[filtered_df['purchase_year'] == selected_year]
    if selected_state != "전체":
        filtered_df = filtered_df[filtered_df['customer_state'] == selected_state]

    # 페이지 렌더링
    if page == "메인":
        main_page(filtered_df)
    elif page == "매출 분석":
        sales_analysis_page(filtered_df)
    elif page == "고객 및 상품 분석":
        customer_product_analysis_page(filtered_df)
    elif page == "사용자 행동 분석":
        user_behavior_analysis_page(filtered_df)

if __name__ == "__main__":
    main()
