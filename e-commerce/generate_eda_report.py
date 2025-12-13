import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import datetime as dt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from load_data import load_datasets

# 이미지 저장 디렉토리 생성
if not os.path.exists('e-commerce/images'):
    os.makedirs('e-commerce/images')

def plot_order_status(orders_df):
    """주문 상태 분포 시각화"""
    report = "## 1. 주문 상태 분포\n\n"
    report += "전체 주문의 상태별 분포를 확인하여 현재 비즈니스의 상태를 파악합니다. 'delivered'가 대부분을 차지하는 것이 이상적입니다.\n\n"

    status_counts = orders_df['order_status'].value_counts()
    
    plt.figure(figsize=(10, 6))
    status_counts.plot(kind='bar', rot=45)
    plt.title('주문 상태별 주문 수')
    plt.xlabel('주문 상태')
    plt.ylabel('주문 수')
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_1_order_status.png'
    md_img_path = 'images/plot_1_order_status.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![주문 상태 분포]({md_img_path})\n\n"
    report += "### 주문 상태 교차표\n\n"
    report += status_counts.to_frame().to_markdown() + "\n\n"
    
    return report

def plot_payment_types(payments_df):
    """결제 유형 분포 시각화"""
    report = "## 2. 결제 유형 분석\n\n"
    report += "고객들이 선호하는 결제 방식를 파악합니다. 신용카드, 현금(boleto), 바우처 등 다양한 결제 유형의 비중을 확인할 수 있습니다.\n\n"
    
    payment_counts = payments_df['payment_type'].value_counts()
    
    plt.figure(figsize=(10, 6))
    payment_counts.plot(kind='bar', rot=0)
    plt.title('결제 유형별 사용 빈도')
    plt.xlabel('결제 유형')
    plt.ylabel('빈도')
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_2_payment_types.png'
    md_img_path = 'images/plot_2_payment_types.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![결제 유형 분포]({md_img_path})\n\n"
    report += "### 결제 유형 교차표\n\n"
    report += payment_counts.to_frame().to_markdown() + "\n\n"
    
    return report

def plot_review_scores(reviews_df):
    """리뷰 점수 분포 시각화"""
    report = "## 3. 리뷰 점수 분포\n\n"
    report += "고객 만족도를 파악하기 위해 리뷰 점수 분포를 확인합니다. 1점에서 5점까지의 점수 분포를 통해 서비스의 전반적인 만족도 수준을 가늠할 수 있습니다.\n\n"
    
    score_counts = reviews_df['review_score'].value_counts().sort_index()
    
    plt.figure(figsize=(10, 6))
    score_counts.plot(kind='bar', rot=0)
    plt.title('리뷰 점수별 분포')
    plt.xlabel('리뷰 점수')
    plt.ylabel('주문 수')
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_3_review_scores.png'
    md_img_path = 'images/plot_3_review_scores.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![리뷰 점수 분포]({md_img_path})\n\n"
    report += "### 리뷰 점수 교차표\n\n"
    report += score_counts.to_frame().to_markdown() + "\n\n"
    
    return report

def plot_sales_by_month(merged_df):
    """월별 매출 추이 시각화"""
    report = "## 4. 월별 매출 추이\n\n"
    report += "시간에 따른 비즈니스 성장을 파악하기 위해 월별 총 매출 추이를 분석합니다. 특정 월에 매출이 급증하거나 급감하는 패턴을 확인할 수 있습니다.\n\n"
    
    # order_purchase_timestamp를 datetime으로 변환
    df = merged_df.copy()
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['purchase_month'] = df['order_purchase_timestamp'].dt.to_period('M')
    
    monthly_sales = df.groupby('purchase_month')['payment_value'].sum().sort_index()
    
    plt.figure(figsize=(12, 6))
    monthly_sales.plot(kind='line', marker='o')
    plt.title('월별 총 매출 추이')
    plt.xlabel('월')
    plt.ylabel('총 매출')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_4_monthly_sales.png'
    md_img_path = 'images/plot_4_monthly_sales.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![월별 매출 추이]({md_img_path})\n\n"
    report += "### 월별 매출 피봇 테이블\n\n"
    report += monthly_sales.to_frame().to_markdown() + "\n\n"
    
    return report

def plot_sales_by_state(merged_df):
    """주(State)별 매출 분석"""
    report = "## 5. 주요 고객 분포 (주별 매출)\n\n"
    report += "매출이 가장 많이 발생하는 지역을 파악하기 위해 상위 10개 주의 총 매출을 분석합니다. 이를 통해 지역별 마케팅 전략을 수립할 수 있습니다.\n\n"
    
    state_sales = merged_df.groupby('customer_state')['payment_value'].sum().sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(12, 7))
    state_sales.plot(kind='bar')
    plt.title('상위 10개 주(State)별 총 매출')
    plt.xlabel('주 (State)')
    plt.ylabel('총 매출')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_5_sales_by_state.png'
    md_img_path = 'images/plot_5_sales_by_state.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![주별 매출]({md_img_path})\n\n"
    report += "### 상위 10개 주별 매출 교차표\n\n"
    report += state_sales.to_frame().to_markdown() + "\n\n"
    
    return report

def plot_sales_by_category(merged_df):
    """상품 카테고리별 매출 분석"""
    report = "## 6. 인기 상품 카테고리 (매출 기준)\n\n"
    report += "매출 기여도가 높은 상위 10개 상품 카테고리를 분석하여 인기 상품군을 파악합니다. 이를 통해 재고 관리 및 상품 추천 전략에 활용할 수 있습니다.\n\n"

    # product_category_name이 없는 경우 제외
    df = merged_df.dropna(subset=['product_category_name_english'])
    
    category_sales = df.groupby('product_category_name_english')['payment_value'].sum().sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(12, 8))
    category_sales.plot(kind='barh')
    plt.title('상위 10개 상품 카테고리별 총 매출')
    plt.xlabel('총 매출')
    plt.ylabel('상품 카테고리')
    plt.gca().invert_yaxis() # 매출이 높은 순으로 정렬
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_6_sales_by_category.png'
    md_img_path = 'images/plot_6_sales_by_category.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![카테고리별 매출]({md_img_path})\n\n"
    report += "### 상위 10개 카테고리별 매출 교차표\n\n"
    report += category_sales.to_frame().to_markdown() + "\n\n"
    
    return report

def plot_hourly_orders(merged_df):
    """시간대별 주문 분포"""
    report = "## 7. 시간대별 주문 분포\n\n"
    report += "고객들이 주로 언제 주문하는지 파악하기 위해 시간대별 주문 분포를 분석합니다. 이를 통해 마케팅 메시지 발송 시간 등을 최적화할 수 있습니다.\n\n"
    
    df = merged_df.copy()
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
    
    hourly_orders = df['purchase_hour'].value_counts().sort_index()
    
    plt.figure(figsize=(12, 6))
    hourly_orders.plot(kind='bar')
    plt.title('시간대별 주문 수')
    plt.xlabel('시간')
    plt.ylabel('주문 수')
    plt.xticks(rotation=0)
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_7_hourly_orders.png'
    md_img_path = 'images/plot_7_hourly_orders.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![시간대별 주문]({md_img_path})\n\n"
    report += "### 시간대별 주문 교차표\n\n"
    report += hourly_orders.to_frame().to_markdown() + "\n\n"
    
    return report

def plot_top_customers(merged_df):
    """상위 고객 분석 (주문 수 기준)"""
    report = "## 8. 충성 고객 분석 (상위 10명)\n\n"
    report += "가장 많이 주문한 상위 10명의 고객을 분석하여 충성 고객의 특성을 파악합니다. 고객 ID별 주문 수를 기준으로 합니다.\n\n"
    
    top_customers = merged_df['customer_unique_id'].value_counts().head(10)
    
    plt.figure(figsize=(12, 6))
    top_customers.plot(kind='bar')
    plt.title('상위 10명 고객의 주문 수')
    plt.xlabel('고객 Unique ID')
    plt.ylabel('주문 수')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_8_top_customers.png'
    md_img_path = 'images/plot_8_top_customers.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![상위 고객]({md_img_path})\n\n"
    report += "### 상위 10명 고객 주문 수 교차표\n\n"
    report += top_customers.to_frame().to_markdown() + "\n\n"
    
    return report
    
def plot_price_distribution(items_df):
    """상품 가격 분포"""
    report = "## 9. 상품 가격 분포\n\n"
    report += "판매되는 상품들의 가격대 분포를 확인합니다. 대부분의 상품이 어느 가격대에 집중되어 있는지 파악할 수 있습니다.\n\n"
    
    plt.figure(figsize=(10, 6))
    # 가격이 매우 높은 일부 상품 때문에 분포가 치우치는 것을 방지하기 위해 상위 1% 데이터는 제외하고 시각화
    quantile_99 = items_df['price'].quantile(0.99)
    items_df[items_df['price'] < quantile_99]['price'].hist(bins=50)
    plt.title('상품 가격 분포 (상위 1% 제외)')
    plt.xlabel('가격')
    plt.ylabel('상품 수')
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_9_price_distribution.png'
    md_img_path = 'images/plot_9_price_distribution.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![가격 분포]({md_img_path})\n\n"
    report += "### 가격 기초 통계량\n\n"
    report += items_df['price'].describe().to_frame().to_markdown() + "\n\n"
    
    return report

def plot_freight_value_distribution(items_df):
    """배송비 분포"""
    report = "## 10. 배송비 분포\n\n"
    report += "배송비의 분포를 확인하여 평균적인 배송비 수준과 이상치를 파악합니다. 가격 정책 수립 시 참고할 수 있습니다.\n\n"
    
    plt.figure(figsize=(10, 6))
    # 배송비가 매우 높은 일부 경우를 제외하기 위해 상위 1% 데이터는 제외하고 시각화
    quantile_99 = items_df['freight_value'].quantile(0.99)
    items_df[items_df['freight_value'] < quantile_99]['freight_value'].hist(bins=50)
    plt.title('배송비 분포 (상위 1% 제외)')
    plt.xlabel('배송비')
    plt.ylabel('주문 수')
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_10_freight_value_distribution.png'
    md_img_path = 'images/plot_10_freight_value_distribution.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![배송비 분포]({md_img_path})\n\n"
    report += "### 배송비 기초 통계량\n\n"
    report += items_df['freight_value'].describe().to_frame().to_markdown() + "\n\n"
    
    return report

def plot_top_products_by_quantity(merged_df):
    """상위 판매 상품 (수량 기준)"""
    report = "## 11. 인기 상품 (판매 수량 기준)\n\n"
    report += "가장 많이 팔린 상위 10개 상품을 분석합니다. 상품 카테고리 이름을 기준으로 수량을 집계합니다.\n\n"
    
    df = merged_df.dropna(subset=['product_category_name_english'])
    top_products = df.groupby('product_category_name_english')['order_item_id'].count().sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(12, 8))
    top_products.plot(kind='barh')
    plt.title('상위 10개 상품 카테고리 (판매 수량 기준)')
    plt.xlabel('판매 수량')
    plt.ylabel('상품 카테고리')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_11_top_products_quantity.png'
    md_img_path = 'images/plot_11_top_products_quantity.png'
    plt.savefig(img_path)
    plt.close()

    report += f"![상위 판매 상품]({md_img_path})\n\n"
    report += "### 상위 10개 상품 판매 수량 교차표\n\n"
    report += top_products.to_frame().to_markdown() + "\n\n"
    
    return report



def plot_customer_segmentation(merged_df):
    """RFM 기반 고객 세그먼트 분석"""
    report = "## 12. 고객 세그먼트 분석 (RFM)\n\n"
    report += "고객의 최근 구매일(Recency), 구매 빈도(Frequency), 총 구매 금액(Monetary)을 기반으로 고객을 여러 세그먼트로 분류합니다. 이를 통해 각 세그먼트의 특성을 파악하고 타겟 마케팅 전략을 수립할 수 있습니다.\n\n"

    df = merged_df.copy()
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    # Recency 계산
    snapshot_date = df['order_purchase_timestamp'].max() + dt.timedelta(days=1)
    rfm = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    })
    rfm.rename(columns={'order_purchase_timestamp': 'Recency',
                        'order_id': 'Frequency',
                        'payment_value': 'Monetary'}, inplace=True)

    # 이상치 처리 (상하위 1% 제거)
    for col in ['Recency', 'Frequency', 'Monetary']:
        q1 = rfm[col].quantile(0.01)
        q99 = rfm[col].quantile(0.99)
        rfm = rfm[(rfm[col] >= q1) & (rfm[col] <= q99)]

    # RFM Scoring using quantiles
    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=False, duplicates='drop') + 1 # Recency: smaller is better, so reverse score later
    rfm['F_Score'] = pd.qcut(rfm['Frequency'], q=5, labels=False, duplicates='drop') + 1 # Frequency: larger is better
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=False, duplicates='drop') + 1 # Monetary: larger is better
    
    # Reverse Recency score: higher Recency means less recent, so lower score
    rfm['R_Score'] = rfm['R_Score'].max() - rfm['R_Score'] + 1

    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

    # User's segment_customer function
    def segment_customer(row):
        r = row["R_Score"]
        f = row["F_Score"]
        m = row["M_Score"]
        rfm_score = row["RFM_Score"]
        # 핵심 VIP 그룹
        if rfm_score in ["555", "554", "545", "544", "455"]:
            return "VIP"
        # 최근에 자주 오는 충성 고객
        elif r >= 4 and f >= 3:
            return "Loyal"
        # 횟수/금액은 높지만 최근성은 살짝 떨어지는 성장 고객
        elif f >= 4 or m >= 4:
            return "Potential"
        # 오래 안 오고, 자주/많이 사지도 않은 이탈 위험군
        elif r <= 2 and f <= 2:
            return "At Risk"
        else:
            return "Normal"

    rfm["Segment"] = rfm.apply(segment_customer, axis=1)
    
    # 세그먼트별 고객 수 시각화
    segment_counts = rfm['Segment'].value_counts()
    
    plt.figure(figsize=(10, 6))
    segment_counts.plot(kind='bar', rot=0)
    plt.title('고객 세그먼트별 고객 수')
    plt.xlabel('고객 세그먼트')
    plt.ylabel('고객 수')
    plt.tight_layout()
    
    img_path = 'e-commerce/images/plot_12_customer_segmentation.png'
    md_img_path = 'images/plot_12_customer_segmentation.png'
    plt.savefig(img_path)
    plt.close()
    
    report += f"![고객 세그먼트 분포]({md_img_path})\n\n"
    
    # 세그먼트별 특성 요약
    segment_summary = rfm.groupby('Segment').agg(
        Recency_Mean=('Recency', 'mean'),
        Frequency_Mean=('Frequency', 'mean'),
        Monetary_Mean=('Monetary', 'mean'),
        Count=('Recency', 'count')
    ).sort_values(by='Monetary_Mean', ascending=False)
    
    report += "### 고객 세그먼트별 특성\n\n"
    report += segment_summary.to_markdown() + "\n\n"
    
    return report

def main():
    """EDA 프로세스를 실행하고 마크다운 보고서를 생성합니다."""
    
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
    order_payments = pd.merge(orders_df, payments_df, on='order_id')
    order_payments_customers = pd.merge(order_payments, customers_df, on='customer_id')
    order_items_merged = pd.merge(order_payments_customers, items_df, on='order_id')
    full_df = pd.merge(order_items_merged, products_df, on='product_id')
    full_merged_df = pd.merge(full_df, translation_df, left_on='product_category_name', right_on='product_category_name', how='left')
    
    # 보고서 생성
    markdown_report = "# 브라질 이커머스(Olist) 데이터 분석 보고서\n\n"
    markdown_report += "이 보고서는 브라질 이커머스 플랫폼 Olist의 데이터를 사용하여 고객, 주문, 상품, 판매자 등 다양한 관점에서 비즈니스 현황을 분석하고 인사이트를 도출합니다.\n\n"
    
    # 각 분석 함수 호출 및 보고서에 추가
    markdown_report += plot_order_status(orders_df)
    markdown_report += plot_payment_types(payments_df)
    markdown_report += plot_review_scores(reviews_df)
    markdown_report += plot_sales_by_month(full_merged_df)
    markdown_report += plot_sales_by_state(full_merged_df)
    markdown_report += plot_sales_by_category(full_merged_df)
    markdown_report += plot_hourly_orders(full_merged_df)
    markdown_report += plot_top_customers(full_merged_df)
    markdown_report += plot_price_distribution(items_df)
    markdown_report += plot_freight_value_distribution(items_df)
    markdown_report += plot_top_products_by_quantity(full_merged_df)
    markdown_report += plot_customer_segmentation(full_merged_df)

    # 마크다운 파일 저장
    with open('e-commerce/EDA_Report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print("EDA 보고서 생성이 완료되었습니다: e-commerce/EDA_Report.md")

if __name__ == '__main__':
    main()
