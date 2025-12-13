
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from load_data import load_datasets

# --- 1. 데이터 로딩 및 전처리 ---
def load_and_preprocess_data():
    """
    데이터를 로드하고 기본 전처리를 수행합니다.
    """
    # 데이터 로드
    datasets = load_datasets('e-commerce')
    orders_df = datasets['olist_orders']
    payments_df = datasets['olist_order_payments']
    reviews_df = datasets['olist_order_reviews']
    customers_df = datasets['olist_customers']

    # 데이터 병합
    df = pd.merge(orders_df, payments_df, on='order_id')
    df = pd.merge(df, reviews_df, on='order_id')
    df = pd.merge(df, customers_df, on='customer_id')

    # 시간 관련 컬럼 변환
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    return df

# --- 2. 신규/기존 고객 정의 ---
def identify_customer_cohorts(df):
    """
    고객의 첫 구매일을 기준으로 신규/기존 고객을 분류합니다.
    """
    # 각 고객의 첫 구매일 계산
    df['first_purchase_date'] = df.groupby('customer_unique_id')['order_purchase_timestamp'].transform('min')
    df['first_purchase_month'] = df['first_purchase_date'].dt.to_period('M')

    # 2017년 11월 데이터 필터링
    nov_2017_df = df[df['order_purchase_timestamp'].dt.to_period('M') == '2017-11'].copy()

    # 신규/기존 고객 분류
    nov_2017_df['customer_type'] = 'Existing'
    nov_2017_df.loc[nov_2017_df['first_purchase_month'] == '2017-11', 'customer_type'] = 'New'
    
    return nov_2017_df

# --- 3. EDA 및 시각화 함수 ---
def analyze_and_visualize(df):
    """
    신규/기존 고객 그룹에 대한 EDA를 수행하고 결과를 마크다운으로 생성합니다.
    """
    markdown_report = "# 2017년 11월 신규 vs 기존 고객 행동 분석\n\n"
    markdown_report += "이 보고서는 2017년 11월에 구매한 고객을 첫 구매 시점에 따라 '신규'와 '기존'으로 나누어 그들의 소비 패턴과 행동을 비교 분석합니다.\n\n"
    
    # 이미지 저장 디렉토리 생성
    if not os.path.exists('e-commerce/images'):
        os.makedirs('e-commerce/images')

    # --- 분석 1: 고객 및 주문 수 비교 ---
    report_part1, fig1 = analyze_customer_order_counts(df)
    markdown_report += report_part1
    fig1.write_image("e-commerce/images/nov2017_customer_order_counts.png")

    # --- 분석 2: 매출액 및 평균 주문 금액(AOV) 비교 ---
    report_part2, fig2 = analyze_sales_aov(df)
    markdown_report += report_part2
    fig2.write_image("e-commerce/images/nov2017_sales_aov.png")
    
    # --- 분석 3: 결제 유형 비교 ---
    report_part3, fig3 = analyze_payment_types(df)
    markdown_report += report_part3
    fig3.write_image("e-commerce/images/nov2017_payment_types.png")

    # --- 분석 4: 리뷰 점수 비교 ---
    report_part4, fig4 = analyze_review_scores(df)
    markdown_report += report_part4
    fig4.write_image("e-commerce/images/nov2017_review_scores.png")
    
    return markdown_report

def analyze_customer_order_counts(df):
    """분석 1: 고객 및 주문 수 비교"""
    report = "## 1. 고객 및 주문 수\n\n"
    report += "2017년 11월의 구매 활동을 신규 고객과 기존 고객 그룹으로 나누어 고객 수와 총 주문 건수를 비교합니다.\n\n"
    
    # 고객 수
    customer_counts = df.groupby('customer_type')['customer_unique_id'].nunique().reset_index()
    # 주문 수
    order_counts = df.groupby('customer_type')['order_id'].nunique().reset_index()
    
    summary_df = pd.merge(customer_counts, order_counts, on='customer_type')
    summary_df.columns = ['고객 유형', '고객 수', '주문 수']
    
    fig = go.Figure(data=[
        go.Bar(name='고객 수', x=summary_df['고객 유형'], y=summary_df['고객 수']),
        go.Bar(name='주문 수', x=summary_df['고객 유형'], y=summary_df['주문 수'])
    ])
    fig.update_layout(barmode='group', title_text='신규 vs 기존 고객 및 주문 수')
    
    report += "![고객 및 주문 수](images/nov2017_customer_order_counts.png)\n\n"
    report += "### 요약표\n\n"
    report += summary_df.to_markdown(index=False) + "\n\n"
    return report, fig

def analyze_sales_aov(df):
    """분석 2: 매출액 및 평균 주문 금액(AOV) 비교"""
    report = "## 2. 매출액 및 평균 주문 금액(AOV)\n\n"
    report += "신규 고객과 기존 고객이 발생시킨 총 매출액과 1인당 평균 주문 금액(AOV)을 비교하여 그룹별 구매력 차이를 확인합니다.\n\n"
    
    sales_summary = df.groupby('customer_type').agg(
        total_sales=('payment_value', 'sum'),
        total_orders=('order_id', 'nunique')
    ).reset_index()
    sales_summary['aov'] = sales_summary['total_sales'] / sales_summary['total_orders']
    
    fig = go.Figure(data=[
        go.Bar(name='총 매출액', x=sales_summary['customer_type'], y=sales_summary['total_sales']),
        go.Bar(name='평균 주문 금액(AOV)', x=sales_summary['customer_type'], y=sales_summary['aov'])
    ])
    fig.update_layout(barmode='group', title_text='신규 vs 기존 고객 매출액 및 AOV')

    report += "![매출액 및 AOV](images/nov2017_sales_aov.png)\n\n"
    report += "### 요약표\n\n"
    report += sales_summary.to_markdown(index=False) + "\n\n"
    return report, fig

def analyze_payment_types(df):
    """분석 3: 결제 유형 비교"""
    report = "## 3. 결제 유형 선호도\n\n"
    report += "각 고객 그룹이 선호하는 결제 수단에 차이가 있는지 확인합니다.\n\n"

    payment_counts = df.groupby(['customer_type', 'payment_type']).size().reset_index(name='count')
    
    fig = px.bar(payment_counts, x='payment_type', y='count', color='customer_type',
                 title='신규 vs 기존 고객의 결제 유형 선호도', barmode='group',
                 labels={'payment_type': '결제 유형', 'count': '사용 건수'})

    report += "![결제 유형 선호도](images/nov2017_payment_types.png)\n\n"
    report += "### 교차표\n\n"
    report += payment_counts.pivot(index='payment_type', columns='customer_type', values='count').fillna(0).to_markdown() + "\n\n"
    return report, fig

def analyze_review_scores(df):
    """분석 4: 리뷰 점수 비교"""
    report = "## 4. 리뷰 점수\n\n"
    report += "신규 고객과 기존 고객의 구매 경험 만족도에 차이가 있는지 리뷰 점수를 통해 확인합니다.\n\n"

    review_scores = df.groupby(['customer_type', 'review_score']).size().reset_index(name='count')
    
    fig = px.bar(review_scores, x='review_score', y='count', color='customer_type',
                 title='신규 vs 기존 고객의 리뷰 점수 분포', barmode='group',
                 labels={'review_score': '리뷰 점수', 'count': '리뷰 수'})
    fig.update_xaxes(type='category')

    report += "![리뷰 점수](images/nov2017_review_scores.png)\n\n"
    report += "### 교차표\n\n"
    report += review_scores.pivot(index='review_score', columns='customer_type', values='count').fillna(0).to_markdown() + "\n\n"
    return report, fig

# --- 4. 메인 실행 로직 ---
def main():
    """
    전체 EDA 프로세스를 실행하고 마크다운 보고서를 생성합니다.
    """
    # 1. 데이터 로딩 및 전처리
    full_df = load_and_preprocess_data()
    
    # 2. 2017년 11월 데이터에 대해 신규/기존 고객 분류
    nov_2017_customers_df = identify_customer_cohorts(full_df)
    
    # 3. EDA 및 시각화, 마크다운 생성
    markdown_report = analyze_and_visualize(nov_2017_customers_df)
    
    # 4. 마크다운 파일 저장
    with open('e-commerce/New_vs_Existing_Report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print("신규 vs 기존 고객 분석 보고서 생성이 완료되었습니다: e-commerce/New_vs_Existing_Report.md")

if __name__ == '__main__':
    main()
