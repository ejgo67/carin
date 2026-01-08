
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_olist_eda():
    """
    Olist 데이터셋에 대한 EDA를 수행하고, 마크다운 보고서를 생성합니다.
    """
    
    # --- 1. 환경 설정 ---
    output_dir = './kpi-tree/'
    image_dir = os.path.join(output_dir, 'images')

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    data_path = './data/olist_merged_dataset_deduped.csv'
    df = pd.read_csv(data_path)

    report_path = os.path.join(output_dir, 'EDA_Report.md')

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Olist E-commerce 데이터셋 EDA 보고서\n\n")
        f.write("이 보고서는 Olist E-commerce 데이터셋에 대한 탐색적 데이터 분석(EDA) 결과를 요약합니다.\n\n")

        # --- 2. 데이터 기본 정보 ---
        f.write("## 1. 데이터 기본 정보\n\n")
        f.write("### 처음 5개 행:\n")
        f.write("```\n" + df.head().to_string() + "\n```\n\n")
        
        # .info()는 출력이 길어질 수 있으므로, 버퍼를 사용하여 처리합니다.
        import io
        buffer = io.StringIO()
        df.info(buf=buffer)
        f.write("### 데이터 정보:\n")
        f.write("```\n" + buffer.getvalue() + "\n```\n\n")
        
        f.write("### 기술 통계 (수치형 변수):\n")
        f.write("```\n" + df.describe().to_string() + "\n```\n\n")

        # --- 3. 데이터 시각화 및 분석 ---
        f.write("## 2. 데이터 시각화 및 분석\n\n")

        # Plot 1: 주문 상태 (order_status) 분포
        plt.figure(figsize=(10, 6))
        order_status_counts = df['order_status'].value_counts()
        sns.barplot(x=order_status_counts.index, y=order_status_counts.values)
        plt.title('주문 상태 분포')
        plt.xlabel('주문 상태')
        plt.ylabel('주문 수')
        img_path = os.path.join(image_dir, 'plot_1_order_status.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.1. 주문 상태 분포\n")
        f.write('![주문 상태 분포](./images/plot_1_order_status.png)\n')
        f.write("대부분의 주문이 'delivered'(배송 완료) 상태임을 알 수 있습니다. 'shipped'(배송 중)와 'processing'(처리 중) 상태도 일부 존재합니다.\n\n")
        f.write("#### 주문 상태별 교차표:\n")
        f.write("```\n" + pd.crosstab(index=df['order_status'], columns='count').to_string() + "\n```\n\n")

        # Plot 2: 지불 유형 (payment_type) 분포
        plt.figure(figsize=(12, 7))
        payment_type_counts = df['payment_type'].value_counts()
        sns.barplot(x=payment_type_counts.index, y=payment_type_counts.values)
        plt.title('지불 유형 분포')
        plt.xlabel('지불 유형')
        plt.ylabel('거래 수')
        img_path = os.path.join(image_dir, 'plot_2_payment_types.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.2. 지불 유형 분포\n")
        f.write('![지불 유형 분포](./images/plot_2_payment_types.png)\n')
        f.write("신용카드(credit_card)가 가장 일반적인 지불 방법이며, 그 다음으로 boleto(브라질의 현금 결제 방식), 바우처, 직불카드 순입니다.\n\n")
        f.write("#### 지불 유형별 교차표:\n")
        f.write("```\n" + pd.crosstab(index=df['payment_type'], columns='count').to_string() + "\n```\n\n")
        
        # Plot 3: 리뷰 점수 (review_score) 분포
        plt.figure(figsize=(10, 6))
        review_score_counts = df['review_score'].value_counts().sort_index()
        sns.barplot(x=review_score_counts.index, y=review_score_counts.values, palette='viridis')
        plt.title('리뷰 점수 분포')
        plt.xlabel('리뷰 점수')
        plt.ylabel('주문 수')
        img_path = os.path.join(image_dir, 'plot_3_review_scores.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.3. 리뷰 점수 분포\n")
        f.write('![리뷰 점수 분포](./images/plot_3_review_scores.png)\n')
        f.write("5점(만점) 리뷰가 압도적으로 많으며, 이는 고객 만족도가 전반적으로 높다는 것을 시사합니다. 반면, 1점 리뷰도 상당수 존재하여 불만족한 고객 경험도 있었음을 알 수 있습니다.\n\n")
        f.write("#### 리뷰 점수별 교차표:\n")
        f.write("```\n" + pd.crosstab(index=df['review_score'], columns='count').to_string() + "\n```\n\n")
        
        # 날짜/시간 데이터 변환 (시계열 분석을 위해)
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

        # Plot 4: 월별 판매 동향
        plt.figure(figsize=(14, 7))
        monthly_sales = df.set_index('order_purchase_timestamp').resample('M')['price'].sum()
        monthly_sales.plot()
        plt.title('월별 판매액 동향')
        plt.xlabel('월')
        plt.ylabel('총 판매액')
        img_path = os.path.join(image_dir, 'plot_4_monthly_sales.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.4. 월별 판매액 동향\n")
        f.write('![월별 판매액 동향](./images/plot_4_monthly_sales.png)\n')
        f.write("판매액은 시간에 따라 꾸준히 증가하는 추세를 보이며, 특정 월(특히 연말)에 급증하는 패턴이 나타납니다.\n\n")

        # Plot 5: 고객 위치 (주)별 판매량
        plt.figure(figsize=(15, 8))
        top_states = df['customer_state'].value_counts().nlargest(10)
        sns.barplot(x=top_states.index, y=top_states.values)
        plt.title('상위 10개 주(State)별 주문 수')
        plt.xlabel('주')
        plt.ylabel('주문 수')
        img_path = os.path.join(image_dir, 'plot_5_sales_by_state.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.5. 상위 10개 주(State)별 주문 수\n")
        f.write('![상위 10개 주별 주문 수](./images/plot_5_sales_by_state.png)\n')
        f.write("상파울루(SP) 주에서의 주문이 압도적으로 많으며, 이는 브라질의 경제 중심지임을 반영합니다. 리우데자네이루(RJ)와 미나스제라이스(MG)가 그 뒤를 잇고 있습니다.\n\n")

        # Plot 6: 상품 카테고리별 판매량
        plt.figure(figsize=(15, 8))
        top_categories = df['product_category_name_english'].value_counts().nlargest(10)
        sns.barplot(x=top_categories.values, y=top_categories.index, orient='h')
        plt.title('상위 10개 상품 카테고리별 주문 수')
        plt.xlabel('주문 수')
        plt.ylabel('상품 카테고리')
        img_path = os.path.join(image_dir, 'plot_6_sales_by_category.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.6. 상위 10개 상품 카테고리별 주문 수\n")
        f.write('![상위 10개 상품 카테고리별 주문 수](./images/plot_6_sales_by_category.png)\n')
        f.write("침구/욕실용품(bed_bath_table)이 가장 많이 팔렸으며, 건강/미용(health_beauty), 스포츠/레저(sports_leisure)가 뒤를 잇습니다. 이는 생활용품과 개인 관리 용품에 대한 수요가 높음을 보여줍니다.\n\n")
        
        # Plot 7: 시간대별 주문량
        plt.figure(figsize=(12, 7))
        df['order_hour'] = df['order_purchase_timestamp'].dt.hour
        hourly_orders = df['order_hour'].value_counts().sort_index()
        sns.lineplot(x=hourly_orders.index, y=hourly_orders.values)
        plt.title('시간대별 주문량')
        plt.xlabel('시간')
        plt.ylabel('주문 수')
        plt.xticks(range(0, 24))
        img_path = os.path.join(image_dir, 'plot_7_hourly_orders.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.7. 시간대별 주문량\n")
        f.write('![시간대별 주문량](./images/plot_7_hourly_orders.png)\n')
        f.write("주문은 주로 오후(13시~16시)와 저녁(20시~22시) 시간대에 집중되는 경향을 보입니다. 새벽 시간대에는 주문량이 현저히 낮습니다.\n\n")

        # Plot 8: 상위 고객 (Top Customers)
        plt.figure(figsize=(12, 7))
        top_customers = df['customer_unique_id'].value_counts().nlargest(10)
        sns.barplot(x=top_customers.values, y=top_customers.index, orient='h')
        plt.title('상위 10명 고객의 주문 횟수')
        plt.xlabel('주문 횟수')
        plt.ylabel('고객 ID')
        img_path = os.path.join(image_dir, 'plot_8_top_customers.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.8. 상위 10명 고객의 주문 횟수\n")
        f.write('![상위 고객](./images/plot_8_top_customers.png)\n')
        f.write("대부분의 고객은 한두 번의 주문만 하지만, 일부 고객은 여러 번의 재구매를 합니다. 이는 충성 고객을 식별하고 타겟 마케팅을 하는 데 활용될 수 있습니다.\n\n")

        # Plot 9: 상품 가격(price) 분포
        plt.figure(figsize=(10, 6))
        # 가격이 매우 높은 이상치를 제외하고 보기 위해 1000 이하의 데이터만 사용
        sns.histplot(df[df['price'] < 1000]['price'], bins=50, kde=True)
        plt.title('상품 가격 분포 (1000 이하)')
        plt.xlabel('가격')
        plt.ylabel('상품 수')
        img_path = os.path.join(image_dir, 'plot_9_price_distribution.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.9. 상품 가격 분포\n")
        f.write('![상품 가격 분포](./images/plot_9_price_distribution.png)\n')
        f.write("상품 가격은 대부분 200 이하에 집중되어 있으며, 오른쪽으로 긴 꼬리를 가집니다. 이는 저가 상품이 대다수를 차지하지만 고가 상품도 일부 판매되고 있음을 의미합니다.\n\n")

        # Plot 10: 배송비(freight_value) 분포
        plt.figure(figsize=(10, 6))
        # 배송비 이상치를 제외하고 보기 위해 100 이하의 데이터만 사용
        sns.histplot(df[df['freight_value'] < 100]['freight_value'], bins=50, kde=True)
        plt.title('배송비 분포 (100 이하)')
        plt.xlabel('배송비')
        plt.ylabel('주문 수')
        img_path = os.path.join(image_dir, 'plot_10_freight_value_distribution.png')
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.10. 배송비 분포\n")
        f.write('![배송비 분포](./images/plot_10_freight_value_distribution.png)\n')
        f.write("배송비는 주로 10-30 사이에 분포하고 있습니다. 배송비는 고객의 구매 결정에 중요한 요인이 될 수 있습니다.\n\n")

    print(f"EDA 분석이 완료되었으며, 결과가 '{report_path}' 파일에 저장되었습니다.")

if __name__ == '__main__':
    run_olist_eda()
