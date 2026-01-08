
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    order_items_df = datasets['olist_order_items']
    products_df = datasets['olist_products']

    # 데이터 병합
    df = pd.merge(orders_df, payments_df, on='order_id')
    df = pd.merge(df, reviews_df, on='order_id')
    df = pd.merge(df, customers_df, on='customer_id')
    df = pd.merge(df, order_items_df, on='order_id')
    df = pd.merge(df, products_df, on='product_id')

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
    
    # Create figure with two subplots
    fig = make_subplots(rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.1,
                        subplot_titles=('총 매출액 (Total Sales)', '평균 주문 금액 (AOV)'))

    # Add Total Sales as Bar chart in the first subplot
    fig.add_trace(
        go.Bar(x=sales_summary['customer_type'], y=sales_summary['total_sales'], name='총 매출액', marker_color='blue', showlegend=False),
        row=1, col=1
    )

    # Add AOV as Bar chart in the second subplot
    fig.add_trace(
        go.Bar(x=sales_summary['customer_type'], y=sales_summary['aov'], name='평균 주문 금액(AOV)', marker_color='red', showlegend=False),
        row=2, col=1
    )

    # Update layout and y-axis titles
    fig.update_layout(
        title_text='신규 vs 기존 고객 매출액 및 AOV',
        height=700,  # Adjust height for better visibility of two plots
        # legend=dict(x=0.1, y=1.1, orientation='h') # Not needed if showlegend=False
    )
    
    fig.update_yaxes(title_text="총 매출액 (R$)", row=1, col=1)
    fig.update_yaxes(title_text="평균 주문 금액(AOV) (R$)", row=2, col=1)
    fig.update_xaxes(title_text="고객 유형", row=2, col=1) # Only show x-axis label on the bottom plot


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

def analyze_repurchase_funnel(full_df):
    """
    고객의 재구매 퍼널을 분석하고 시각화합니다.
    """
    report = "## 5. 재구매 퍼널 분석\n\n"
    report += "2017년 11월에 구매 활동을 한 고객들을 대상으로 재구매 행동을 분석하여 퍼널을 시각화합니다.\n\n"

    # 고객별 첫 구매일 및 모든 구매 내역 정리
    customer_orders = full_df[['customer_unique_id', 'order_purchase_timestamp', 'order_id']].drop_duplicates()
    customer_orders = customer_orders.sort_values(by=['customer_unique_id', 'order_purchase_timestamp'])

    # 각 고객의 주문 순서 (1st purchase, 2nd purchase, ...)
    customer_orders['order_sequence'] = customer_orders.groupby('customer_unique_id').cumcount() + 1

    # 2017년 11월에 구매 활동을 한 고객 필터링
    nov_2017_customers = full_df[full_df['order_purchase_timestamp'].dt.to_period('M') == '2017-11']['customer_unique_id'].unique()
    
    # 2017년 11월 고객들의 전체 주문 내역 필터링
    filtered_orders = customer_orders[customer_orders['customer_unique_id'].isin(nov_2017_customers)].copy()

    # 11월에 첫 구매를 한 고객 (New)과 그 이전에 첫 구매를 한 고객 (Existing) 분류
    # identify_customer_cohorts 로직을 재사용하거나 유사하게 구현
    first_purchase_dates = full_df.groupby('customer_unique_id')['order_purchase_timestamp'].min().reset_index()
    first_purchase_dates.rename(columns={'order_purchase_timestamp': 'first_ever_purchase_date'}, inplace=True)
    
    filtered_orders = pd.merge(filtered_orders, first_purchase_dates, on='customer_unique_id', how='left')
    
    filtered_orders['customer_category'] = 'Existing'
    filtered_orders.loc[filtered_orders['first_ever_purchase_date'].dt.to_period('M') == '2017-11', 'customer_category'] = 'New'

    # 재구매 퍼널 데이터 집계
    # 신규 고객 중 재구매한 고객, 기존 고객 중 재구매한 고객 수
    repurchase_data = filtered_orders.groupby(['customer_category', 'order_sequence']).agg(
        num_customers=('customer_unique_id', 'nunique')
    ).reset_index()

    # 퍼널 시각화 (예: 막대 그래프 또는 선 그래프로 각 시퀀스별 고객 수)
    fig = px.bar(repurchase_data, 
                 x='order_sequence', 
                 y='num_customers', 
                 color='customer_category',
                 title='2017년 11월 고객의 재구매 퍼널',
                 labels={'order_sequence': '주문 순서', 'num_customers': '고객 수', 'customer_category': '고객 유형'},
                 barmode='group')
    
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1)) # X축 정수값 표시

    report += "![재구매 퍼널](images/repurchase_funnel.png)\n\n"
    report += "### 퍼널 요약표\n\n"
    report += repurchase_data.to_markdown(index=False) + "\n\n"

    return report, fig

def analyze_product_categories(df):
    """
    신규/기존 고객별 구매 카테고리 분포를 분석하고 시각화합니다.
    """
    report = "## 6. 구매 카테고리 분석\n\n"
    report += "신규 및 기존 고객 그룹이 어떤 상품 카테고리를 주로 구매하는지 분석합니다. 이번 분석에서는 각 카테고리별로 신규 및 기존 고객의 주문 건수를 비교합니다.\n\n" # 설명 추가

    # 'product_category_name'이 NaN인 경우 'unknown'으로 처리
    df['product_category_name'] = df['product_category_name'].fillna('unknown')

    # 고객 유형별, 카테고리별 주문 건수 집계
    category_counts = df.groupby(['customer_type', 'product_category_name']).size().reset_index(name='order_count')

    # 전체 카테고리 중 주문 건수 상위 N개 선별
    top_n = 10
    total_category_counts_series = category_counts.groupby('product_category_name')['order_count'].sum().nlargest(top_n)
    top_categories_ordered = total_category_counts_series.index.tolist() # 상위 카테고리를 주문 건수 합계 기준으로 정렬된 리스트로 가져옴

    filtered_category_counts = category_counts[category_counts['product_category_name'].isin(top_categories_ordered)].copy() # .copy() 추가

    # 시각화 시 카테고리 순서 지정을 위해 정렬된 순서를 Plotly에 전달
    fig = px.bar(filtered_category_counts,
                 x='product_category_name', # X축을 카테고리로 변경
                 y='order_count',
                 color='customer_type',     # color를 고객 유형으로 변경
                 title=f'신규 vs 기존 고객 구매 카테고리 분포 (상위 {top_n}개)', # 제목 변경
                 labels={'customer_type': '고객 유형', 'order_count': '주문 건수', 'product_category_name': '상품 카테고리'},
                 barmode='group', # barmode를 group으로 변경하여 나란히 비교
                 category_orders={'product_category_name': top_categories_ordered}) # 카테고리 순서 지정

    report += "![구매 카테고리 분포](images/category_distribution.png)\n\n"
    report += "### 카테고리별 주문 건수 요약표\n\n"
    # 요약표도 전체 주문 건수 기준으로 내림차순 정렬된 카테고리 순서로 표시되도록 정렬
    filtered_category_counts_sorted = filtered_category_counts.set_index('product_category_name').loc[top_categories_ordered].reset_index()
    report += filtered_category_counts_sorted.to_markdown(index=False) + "\n\n"

    return report, fig

def analyze_repurchase_rate_by_first_category(full_df):
    """
    고객의 첫 구매 카테고리별 재구매 전환율을 분석하고 시각화합니다.
    """
    report = "## 7. 첫 구매 카테고리별 재구매 전환율\n\n"
    report += "고객이 처음 구매한 상품 카테고리가 재구매에 어떤 영향을 미치는지 분석하여 카테고리별 재구매 전환율을 시각화합니다.\n\n"

    # 'product_category_name'이 NaN인 경우 'unknown'으로 처리
    full_df['product_category_name'] = full_df['product_category_name'].fillna('unknown')

    # 고객별 첫 구매 정보 (시간, 카테고리)
    first_purchases = full_df.sort_values(by=['customer_unique_id', 'order_purchase_timestamp']).groupby('customer_unique_id').first().reset_index()
    first_purchases = first_purchases[['customer_unique_id', 'order_id', 'order_purchase_timestamp', 'product_category_name']]
    first_purchases.rename(columns={'product_category_name': 'first_purchase_category'}, inplace=True)

    # 고객별 주문 횟수 계산
    customer_order_counts = full_df.groupby('customer_unique_id')['order_id'].nunique().reset_index()
    customer_order_counts.rename(columns={'order_id': 'total_orders'}, inplace=True)

    # 첫 구매 정보와 주문 횟수 병합
    customer_data = pd.merge(first_purchases, customer_order_counts, on='customer_unique_id')

    # 재구매 여부 판단 (총 주문 횟수가 1보다 크면 재구매)
    customer_data['has_repurchased'] = customer_data['total_orders'] > 1

    # 첫 구매 카테고리별 재구매율 집계
    repurchase_rate_by_category = customer_data.groupby('first_purchase_category').agg(
        total_first_time_customers=('customer_unique_id', 'nunique'),
        repurchasing_customers=('has_repurchased', lambda x: x.sum())
    ).reset_index()

    repurchase_rate_by_category['repurchase_rate'] = (repurchase_rate_by_category['repurchasing_customers'] / repurchase_rate_by_category['total_first_time_customers']) * 100

    # 재구매율이 높은 순서로 정렬 (상위 10개 카테고리)
    repurchase_rate_by_category_sorted = repurchase_rate_by_category.sort_values(by='repurchase_rate', ascending=False).head(10)
    
    fig = px.bar(repurchase_rate_by_category_sorted,
                 x='first_purchase_category',
                 y='repurchase_rate',
                 title='첫 구매 카테고리별 재구매 전환율 (상위 10개)',
                 labels={'first_purchase_category': '첫 구매 카테고리', 'repurchase_rate': '재구매 전환율 (%)'},
                 text='repurchase_rate')
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    report += "![첫 구매 카테고리별 재구매 전환율](images/repurchase_rate_by_first_category.png)\n\n"
    report += "### 첫 구매 카테고리별 재구매 전환율 요약표\n\n"
    report += repurchase_rate_by_category_sorted.to_markdown(index=False) + "\n\n"

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
    
    # 3. EDA 및 시각화, 마크다운 생성 (1~4번 분석)
    markdown_report = analyze_and_visualize(nov_2017_customers_df) # analyze_and_visualize 내부에서 1-4번 분석 수행

    # --- 분석 5: 재구매 퍼널 분석 ---
    report_part5, fig5 = analyze_repurchase_funnel(full_df)
    markdown_report += report_part5
    fig5.write_image("e-commerce/images/repurchase_funnel.png")

    # --- 분석 6: 구매 카테고리 분석 ---
    report_part6, fig6 = analyze_product_categories(nov_2017_customers_df) # nov_2017_customers_df를 넘겨야 함
    markdown_report += report_part6
    fig6.write_image("e-commerce/images/category_distribution.png")
    
    # --- 분석 7: 첫 구매 카테고리별 재구매 전환율 ---
    report_part7, fig7 = analyze_repurchase_rate_by_first_category(full_df)
    markdown_report += report_part7
    fig7.write_image("e-commerce/images/repurchase_rate_by_first_category.png")
    
    # 4. 마크다운 파일 저장
    with open('e-commerce/New_vs_Existing_Report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print("신규 vs 기존 고객 분석 보고서 생성이 완료되었습니다: e-commerce/New_vs_Existing_Report.md")

if __name__ == '__main__':
    main()
