
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import io

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def run_full_eda():
    # --- 1. 데이터 로드 ---
    data_path = 'olist'
    try:
        customers = pd.read_csv(os.path.join(data_path, 'olist_customers_dataset.csv'))
        geolocation = pd.read_csv(os.path.join(data_path, 'olist_geolocation_dataset.csv'))
        order_items = pd.read_csv(os.path.join(data_path, 'olist_order_items_dataset.csv'))
        payments = pd.read_csv(os.path.join(data_path, 'olist_order_payments_dataset.csv'))
        reviews = pd.read_csv(os.path.join(data_path, 'olist_order_reviews_dataset.csv'))
        orders = pd.read_csv(os.path.join(data_path, 'olist_orders_dataset.csv'))
        products = pd.read_csv(os.path.join(data_path, 'olist_products_dataset.csv'))
        sellers = pd.read_csv(os.path.join(data_path, 'olist_sellers_dataset.csv'))
        translation = pd.read_csv(os.path.join(data_path, 'product_category_name_translation.csv'))
    except FileNotFoundError as e:
        print(f"오류: 데이터 파일을 찾을 수 없습니다. {e.filename} 경로를 확인하세요.")
        return

    # --- 2. 데이터 병합 ---
    # 주문(orders)을 중심으로 데이터 병합
    df = pd.merge(orders, customers, on='customer_id')
    df = pd.merge(df, order_items, on='order_id')
    df = pd.merge(df, payments, on='order_id')
    df = pd.merge(df, reviews, on='order_id')
    df = pd.merge(df, products, on='product_id')
    df = pd.merge(df, sellers, on='seller_id')
    df = pd.merge(df, translation, on='product_category_name')

    # --- 3. 데이터 전처리 및 기본 설정 ---
    # 날짜 데이터 변환
    for col in ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    # 결과물 저장 경로
    output_folder = 'olist'
    images_folder = os.path.join(output_folder, 'images')
    report_path = os.path.join(output_folder, 'Full_EDA_Report.md')

    # 이미지 폴더 생성
    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    # 마크다운 보고서 내용
    md_content = []
    md_content.append("# Olist 전체 데이터셋 EDA 보고서")
    md_content.append("이 보고서는 Olist E-commerce 데이터셋의 9개 파일을 통합하여 심층 분석한 결과를 담고 있습니다.")

    # --- 4. 기본 정보 출력 ---
    md_content.append("## 1. 통합 데이터 개요")
    md_content.append("### 1.1. 데이터 크기")
    md_content.append(f"- 행: {df.shape[0]}, 열: {df.shape[1]}")
    md_content.append("### 1.2. 데이터 미리보기 (상위 3개)")
    md_content.append("```\n" + df.head(3).to_string() + "\n```")
    md_content.append("\n### 1.3. 데이터 구조")
    buffer = io.StringIO()
    df.info(buf=buffer)
    md_content.append("```\n" + buffer.getvalue() + "\n```")
    md_content.append("\n### 1.4. 기술 통계")
    md_content.append("```\n" + df.describe().to_string() + "\n```")
    md_content.append("\n### 1.5. 결측치 확인")
    md_content.append("```\n" + df.isnull().sum().to_string() + "\n```")
    md_content.append("\n- `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date` 등 배송 관련 열에 결측치가 존재합니다. 이는 주문 상태(예: 'canceled')와 관련이 있을 수 있습니다.")
    md_content.append("- `product` 관련 일부 열에도 소수의 결측치가 존재합니다.")

    # --- 5. 시각화 및 분석 ---
    md_content.append("\n## 2. 데이터 시각화 및 분석")

    # 시각화 1: 월별 매출 추이
    df['order_purchase_month'] = df['order_purchase_timestamp'].dt.to_period('M')
    monthly_sales = df.groupby('order_purchase_month')['payment_value'].sum().to_frame().reset_index()
    monthly_sales['order_purchase_month'] = monthly_sales['order_purchase_month'].astype(str)
    
    plt.figure(figsize=(15, 7))
    sns.lineplot(x='order_purchase_month', y='payment_value', data=monthly_sales, marker='o')
    plt.title('월별 총 매출 추이', fontsize=16)
    plt.xlabel('연-월')
    plt.ylabel('총 매출액')
    plt.xticks(rotation=45)
    plt.grid(True)
    img_path_1 = os.path.join(images_folder, 'full_plot_1_monthly_sales.png')
    plt.savefig(img_path_1)
    plt.close()

    md_content.append("### 2.1. 월별 총 매출 추이")
    md_content.append(f"![월별 총 매출 추이](./images/full_plot_1_monthly_sales.png)")
    md_content.append("#### 해석:")
    md_content.append("- 2017년 초부터 2017년 11월까지 매출이 꾸준히 성장하다가, 2017년 11월에 급증하는 패턴을 보입니다. 이는 블랙프라이데이 등 연말 쇼핑 시즌의 영향으로 보입니다.")
    md_content.append("- 2018년에도 전반적인 성장세를 유지하지만, 특정 월에 매출 변동이 있습니다.")
    md_content.append("\n")

    # 시각화 2: 상위 15개 상품 카테고리 (판매량 기준)
    plt.figure(figsize=(12, 8))
    top_15_cat = df['product_category_name_english'].value_counts().nlargest(15)
    sns.barplot(x=top_15_cat.values, y=top_15_cat.index, palette='plasma')
    plt.title('상위 15개 상품 카테고리 (판매량 기준)', fontsize=16)
    plt.xlabel('판매량')
    plt.ylabel('상품 카테고리 (영문)')
    img_path_2 = os.path.join(images_folder, 'full_plot_2_top_categories.png')
    plt.savefig(img_path_2)
    plt.close()
    
    md_content.append("### 2.2. 상위 15개 상품 카테고리 (판매량 기준)")
    md_content.append(f"![상위 15개 상품 카테고리](./images/full_plot_2_top_categories.png)")
    md_content.append("#### 교차표:")
    md_content.append("```\n" + top_15_cat.to_frame().to_string() + "\n```")
    md_content.append("#### 해석:")
    md_content.append("- 'bed_bath_table'(침실/욕실/테이블용품) 카테고리가 압도적인 판매량을 보입니다.")
    md_content.append("- 그 뒤를 이어 'health_beauty'(건강/미용), 'sports_leisure'(스포츠/레저), 'furniture_decor'(가구/인테리어), 'computers_accessories'(컴퓨터/액세서리) 등이 인기 있는 카테고리임을 알 수 있습니다.")
    md_content.append("\n")

    # 시각화 3: 결제 수단 분포
    plt.figure(figsize=(10, 7))
    payment_counts = df['payment_type'].value_counts()
    plt.pie(payment_counts, labels=payment_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('결제 수단 분포', fontsize=16)
    plt.ylabel('')
    img_path_3 = os.path.join(images_folder, 'full_plot_3_payment_types.png')
    plt.savefig(img_path_3)
    plt.close()

    md_content.append("### 2.3. 결제 수단 분포")
    md_content.append(f"![결제 수단 분포](./images/full_plot_3_payment_types.png)")
    md_content.append("#### 교차표:")
    md_content.append("```\n" + payment_counts.to_frame().to_string() + "\n```")
    md_content.append("#### 해석:")
    md_content.append("- 'credit_card'(신용카드)가 전체 결제의 약 73.9%를 차지하며 가장 보편적인 결제 수단입니다.")
    md_content.append("- 'boleto'(브라질의 현금 결제 방식)가 그 뒤를 잇고, 'voucher'와 'debit_card'의 사용률은 상대적으로 낮습니다.")
    md_content.append("\n")

    # 시각화 4: 리뷰 점수 분포
    plt.figure(figsize=(10, 6))
    review_scores = df['review_score'].value_counts().sort_index()
    sns.barplot(x=review_scores.index, y=review_scores.values, palette='coolwarm')
    plt.title('리뷰 점수 분포', fontsize=16)
    plt.xlabel('리뷰 점수')
    plt.ylabel('주문 건수')
    img_path_4 = os.path.join(images_folder, 'full_plot_4_review_scores.png')
    plt.savefig(img_path_4)
    plt.close()

    md_content.append("### 2.4. 리뷰 점수 분포")
    md_content.append(f"![리뷰 점수 분포](./images/full_plot_4_review_scores.png)")
    md_content.append("#### 교차표:")
    md_content.append("```\n" + review_scores.to_frame().to_string() + "\n```")
    md_content.append("#### 해석:")
    md_content.append("- 5점(매우 만족)을 준 고객이 압도적으로 많아, 전반적인 고객 만족도가 높다는 것을 알 수 있습니다.")
    md_content.append("- 1점(매우 불만족)을 준 고객도 상당수 존재하여, 불만족 원인에 대한 추가 분석이 필요해 보입니다.")
    md_content.append("\n")
    
    # 시각화 5: 요일별 주문량
    df['order_dow'] = df['order_purchase_timestamp'].dt.day_name()
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    plt.figure(figsize=(10, 6))
    sns.countplot(x='order_dow', data=df, order=dow_order, palette='spring')
    plt.title('요일별 주문량', fontsize=16)
    plt.xlabel('요일')
    plt.ylabel('주문 건수')
    img_path_5 = os.path.join(images_folder, 'full_plot_5_orders_by_dow.png')
    plt.savefig(img_path_5)
    plt.close()

    md_content.append("### 2.5. 요일별 주문량")
    md_content.append(f"![요일별 주문량](./images/full_plot_5_orders_by_dow.png)")
    md_content.append("#### 교차표:")
    md_content.append("```\n" + df['order_dow'].value_counts().reindex(dow_order).to_frame().to_string() + "\n```")
    md_content.append("#### 해석:")
    md_content.append("- 주 초반인 월요일에 주문량이 가장 많고, 주말로 갈수록 점차 감소하는 경향을 보입니다.")
    md_content.append("- 특히 일요일에 주문량이 가장 적습니다. 이는 주말 동안 쇼핑을 마친 후 주중에 주문하는 패턴을 시사합니다.")
    md_content.append("\n")

    # 시각화 6: 시간대별 주문량
    df['order_hour'] = df['order_purchase_timestamp'].dt.hour
    plt.figure(figsize=(12, 6))
    sns.countplot(x='order_hour', data=df, palette='twilight_shifted')
    plt.title('시간대별 주문량', fontsize=16)
    plt.xlabel('시간 (0-23시)')
    plt.ylabel('주문 건수')
    img_path_6 = os.path.join(images_folder, 'full_plot_6_orders_by_hour.png')
    plt.savefig(img_path_6)
    plt.close()

    md_content.append("### 2.6. 시간대별 주문량")
    md_content.append(f"![시간대별 주문량](./images/full_plot_6_orders_by_hour.png)")
    md_content.append("#### 교차표:")
    md_content.append("```\n" + df['order_hour'].value_counts().sort_index().to_frame().to_string() + "\n```")
    md_content.append("#### 해석:")
    md_content.append("- 점심시간 이후인 오후 1시부터 4시 사이에 주문이 가장 활발하게 일어납니다.")
    md_content.append("- 저녁 시간인 8시에서 9시 사이에도 작은 피크가 나타납니다. 새벽 시간에는 주문량이 급격히 감소합니다.")
    md_content.append("\n")

    # 시각화 7: 고객 거주 주(State) 분포 (상위 10개)
    plt.figure(figsize=(12, 7))
    top_10_states = df['customer_state'].value_counts().nlargest(10)
    sns.barplot(x=top_10_states.index, y=top_10_states.values, palette='viridis')
    plt.title('상위 10개 주(State)의 주문 건수', fontsize=16)
    plt.xlabel('주(State)')
    plt.ylabel('주문 건수')
    img_path_7 = os.path.join(images_folder, 'full_plot_7_top_states.png')
    plt.savefig(img_path_7)
    plt.close()

    md_content.append("### 2.7. 상위 10개 주의 주문 건수")
    md_content.append(f"![상위 10개 주](./images/full_plot_7_top_states.png)")
    md_content.append("#### 교차표:")
    md_content.append("```\n" + top_10_states.to_frame().to_string() + "\n```")
    md_content.append("#### 해석:")
    md_content.append("- 상파울루(SP) 주가 다른 주에 비해 압도적으로 많은 주문 건수를 기록하며, Olist의 가장 큰 시장임을 보여줍니다.")
    md_content.append("- 리우데자네이루(RJ)와 미나스제라이스(MG)가 그 뒤를 잇고 있습니다. 이는 브라질의 인구 및 경제 중심지와 일치하는 결과입니다.")
    md_content.append("\n")

    # 시각화 8: 배송 시간과 리뷰 점수의 관계
    df['delivery_duration'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
    plt.figure(figsize=(12, 7))
    sns.boxplot(x='review_score', y='delivery_duration', data=df, palette='bone')
    plt.title('리뷰 점수별 배송 소요 기간', fontsize=16)
    plt.xlabel('리뷰 점수')
    plt.ylabel('배송 소요 기간 (일)')
    plt.ylim(0, 60) # 이상치로 인해 y축 범위가 너무 넓어지는 것을 방지
    img_path_8 = os.path.join(images_folder, 'full_plot_8_delivery_duration_vs_review.png')
    plt.savefig(img_path_8)
    plt.close()
    
    md_content.append("### 2.8. 리뷰 점수별 배송 소요 기간")
    md_content.append(f"![배송 기간과 리뷰 점수](./images/full_plot_8_delivery_duration_vs_review.png)")
    md_content.append("#### 해석:")
    md_content.append("- 리뷰 점수가 낮을수록(1, 2점) 평균 배송 소요 기간이 길어지는 뚜렷한 경향을 보입니다.")
    md_content.append("- 반면, 5점 만점을 준 고객들은 평균적으로 훨씬 빠른 배송을 경험했습니다.")
    md_content.append("- 이는 **빠르고 정확한 배송이 고객 만족도에 매우 중요한 요소**임을 강력하게 시사합니다.")
    md_content.append("\n")

    # 시각화 9: 가격과 배송비의 관계
    plt.figure(figsize=(10, 8))
    sns.scatterplot(x='price', y='freight_value', data=df.sample(n=5000, random_state=42), alpha=0.5)
    plt.title('상품 가격과 배송비의 관계 (5000개 샘플)', fontsize=16)
    plt.xlabel('상품 가격')
    plt.ylabel('배송비')
    plt.xscale('log')
    plt.yscale('log')
    img_path_9 = os.path.join(images_folder, 'full_plot_9_price_vs_freight.png')
    plt.savefig(img_path_9)
    plt.close()

    md_content.append("### 2.9. 상품 가격과 배송비의 관계")
    md_content.append(f"![가격과 배송비](./images/full_plot_9_price_vs_freight.png)")
    md_content.append("#### 해석:")
    md_content.append("- 상품 가격과 배송비 사이에는 양의 상관관계가 희미하게 보이지만, 전반적으로 뚜렷한 패턴은 없습니다.")
    md_content.append("- 가격이 낮은 상품이라도 배송비가 높을 수 있고, 그 반대의 경우도 많습니다. 이는 배송비가 가격보다는 상품의 무게, 부피, 그리고 배송 거리에 더 큰 영향을 받기 때문일 것으로 추정됩니다.")
    md_content.append("- (x, y축 모두 로그 스케일로 변환하여 분포를 더 명확하게 확인)")
    md_content.append("\n")

    # 시각화 10: 결제 할부 개월 수 분포
    plt.figure(figsize=(12, 6))
    sns.countplot(x='payment_installments', data=df[df['payment_type'] == 'credit_card'], palette='magma')
    plt.title('신용카드 결제 시 할부 개월 수 분포', fontsize=16)
    plt.xlabel('할부 개월 수')
    plt.ylabel('주문 건수')
    img_path_10 = os.path.join(images_folder, 'full_plot_10_payment_installments.png')
    plt.savefig(img_path_10)
    plt.close()

    md_content.append("### 2.10. 신용카드 할부 개월 수 분포")
    md_content.append(f"![할부 개월 수 분포](./images/full_plot_10_payment_installments.png)")
    md_content.append("#### 교차표:")
    md_content.append("```\n" + df[df['payment_type'] == 'credit_card']['payment_installments'].value_counts().sort_index().to_frame().to_string() + "\n```")
    md_content.append("#### 해석:")
    md_content.append("- 일시불(1개월) 결제가 가장 많지만, 2~3개월과 8, 10개월 할부 결제도 많이 사용됩니다.")
    md_content.append("- 고객들은 비교적 다양한 할부 옵션을 활용하고 있으며, 특히 고가의 상품 구매 시 장기 할부를 선호할 가능성이 있습니다.")
    md_content.append("\n")

    # --- 추가 분석: 가격대별 분석 ---
    # 시각화 11 & 12: 가격대별 주문 및 매출 분석
    price_bins = [0, 50, 100, 200, 500, df['price'].max()]
    price_labels = ['0-50', '50-100', '100-200', '200-500', '500+']
    df['price_range'] = pd.cut(df['price'], bins=price_bins, labels=price_labels, right=False)

    price_analysis = df.groupby('price_range').agg(
        order_count=('order_id', 'nunique'),
        total_sales=('payment_value', 'sum')
    ).reset_index()

    # 시각화 11: 가격대별 주문 건수
    plt.figure(figsize=(10, 6))
    sns.barplot(x='price_range', y='order_count', data=price_analysis, palette='rocket')
    plt.title('가격대별 주문 건수', fontsize=16)
    plt.xlabel('상품 가격대 (헤알)')
    plt.ylabel('총 주문 건수')
    img_path_11 = os.path.join(images_folder, 'full_plot_11_orders_by_price.png')
    plt.savefig(img_path_11)
    plt.close()

    # 시각화 12: 가격대별 총 매출액
    plt.figure(figsize=(10, 6))
    sns.barplot(x='price_range', y='total_sales', data=price_analysis, palette='rocket')
    plt.title('가격대별 총 매출액', fontsize=16)
    plt.xlabel('상품 가격대 (헤알)')
    plt.ylabel('총 매출액 (백만 헤알)')
    img_path_12 = os.path.join(images_folder, 'full_plot_12_sales_by_price.png')
    plt.savefig(img_path_12)
    plt.close()
    
    md_content.append("### 2.11. 가격대별 주문 및 매출 분석")
    md_content.append("상품 가격을 여러 구간으로 나누어 각 구간의 주문 건수와 매출액 규모를 분석합니다.")
    md_content.append(f"![가격대별 주문 건수](./images/full_plot_11_orders_by_price.png)")
    md_content.append(f"![가격대별 총 매출액](./images/full_plot_12_sales_by_price.png)")
    md_content.append("#### 교차표:")
    md_content.append("```\n" + price_analysis.to_string() + "\n```")
    md_content.append("#### 해석:")
    md_content.append("- **주문 건수**: 0~50 헤알 사이의 저가 상품에서 가장 많은 주문이 발생했습니다. 상품 가격이 상승할수록 주문 건수는 감소하는 경향을 보입니다.")
    md_content.append("- **매출액**: 주문 건수와 달리, 총 매출액은 50-100 헤알 구간에서 가장 높게 나타났습니다. 100-200 헤알 구간도 상당한 매출 비중을 차지합니다.")
    md_content.append("- 이는 저가 상품이 판매량은 높지만(박리다매), 실제 매출을 견인하는 주력 상품군은 50-200 헤알 사이의 중가 상품임을 의미합니다. 500헤알 이상의 고가 상품은 판매량은 적지만, 매출 기여도는 무시할 수 없는 수준입니다.")
    md_content.append("\n")


    # --- 6. 결론 ---
    md_content.append("## 3. 결론 및 요약")
    md_content.append("- **주요 시장**: 브라질 남동부 지역, 특히 상파울루(SP) 주가 Olist의 핵심 시장입니다.")
    md_content.append("- **고객 만족**: 전반적인 리뷰 점수는 높지만, **배송 지연이 낮은 리뷰 점수의 주요 원인**으로 강력하게 작용하고 있습니다. 배송 시스템 최적화가 고객 만족도 향상의 핵심 과제입니다.")
    md_content.append("- **인기 상품**: '침실/욕실/테이블용품', '건강/미용', '스포츠/레저' 등이 높은 판매량을 보이는 주요 카테고리입니다.")
    md_content.append("- **구매 패턴**: 주문은 주중에 집중되며, 특히 오후 시간대에 가장 활발합니다. 결제는 신용카드가 압도적이며, 고객들은 다양한 할부 옵션을 사용합니다.")
    md_content.append("- **향후 분석**: 이 통합 데이터를 바탕으로 RFM 분석을 통한 고객 세분화, 카테고리별 수익성 분석, 배송 지연 예측 모델링 등 더 구체적인 비즈니스 문제 해결을 위한 분석을 진행할 수 있습니다.")

    # 마크다운 파일 작성
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))

    print(f"Full EDA 보고서가 '{report_path}'에 성공적으로 생성되었습니다.")


if __name__ == '__main__':
    run_full_eda()
