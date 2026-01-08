
import pandas as pd
import os
import numpy as np

def generate_weekly_kpi_trends():
    """
    설계된 KPI Tree의 각 노드를 실제 데이터 컬럼과 매핑하여 계산하고,
    이를 '주차(Weekly)' 단위로 집계하여 하나의 통합된 데이터프레임 파일로 저장합니다.
    """
    
    # --- 1. 환경 설정 ---
    output_dir = './kpi-tree/'
    data_path = './data/olist_merged_dataset_deduped.csv'
    output_file_path = os.path.join(output_dir, 'weekly_kpi_trend_analysis.csv')

    # 데이터 로드
    df = pd.read_csv(data_path)

    # --- 2. 시간 관련 피처 엔지니어링 ---
    # order_purchase_timestamp를 datetime으로 변환
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # 주차 시작일 계산 (주차별 집계를 위함)
    # ISO 8601 방식 (월요일을 한 주의 시작으로 간주)
    df['week_start_date'] = df['order_purchase_timestamp'].dt.to_period('W').apply(lambda r: r.start_time)

    # --- 3. 고객 분류 (신규/재구매)를 위한 데이터 준비 ---
    # 각 고객의 첫 구매일 계산
    first_purchase_date = df.groupby('customer_unique_id')['order_purchase_timestamp'].min().reset_index()
    first_purchase_date.rename(columns={'order_purchase_timestamp': 'first_purchase_date'}, inplace=True)
    df = pd.merge(df, first_purchase_date, on='customer_unique_id', how='left')

    # 각 주문이 신규 구매인지 재구매인지 판단
    # 주문의 구매일이 고객의 첫 구매일과 같으면 신규 구매, 아니면 재구매
    df['is_new_customer_order'] = (df['order_purchase_timestamp'] == df['first_purchase_date'])

    # --- 4. KPI 지표 산출 및 주차별 집계 ---
    
    # 각 주차별로 집계할 지표들을 딕셔너리에 저장
    weekly_kpis = {}

    # L0: 총 결제 금액 (Total Payment Value)
    # 정의: 일정 기간 동안 모든 고객이 결제한 총 금액.
    # 산출 로직: SUM(payment_value)
    weekly_kpis['L0_Total_Payment_Value'] = df.groupby('week_start_date')['payment_value'].sum()

    # L1: 총 주문 건수 (Total Orders)
    # 정의: 일정 기간 동안 발생한 전체 주문의 수.
    # 산출 로직: COUNT(DISTINCT order_id)
    weekly_kpis['L1_Total_Orders'] = df.groupby('week_start_date')['order_id'].nunique()

    # L1: 평균 주문 금액 (Average Order Value, AOV)
    # 정의: 단일 주문당 평균적으로 결제되는 금액.
    # 산출 로직: SUM(payment_value) / COUNT(DISTINCT order_id)
    weekly_kpis['L1_Average_Order_Value'] = weekly_kpis['L0_Total_Payment_Value'] / weekly_kpis['L1_Total_Orders']

    # L2: 신규 고객 주문 건수 (New Customer Orders)
    # 정의: 해당 기간에 처음으로 주문을 발생시킨 고객들의 총 주문 건수.
    # 산출 로직: COUNT(DISTINCT order_id) WHERE is_new_customer_order = True
    weekly_kpis['L2_New_Customer_Orders'] = df[df['is_new_customer_order']].groupby('week_start_date')['order_id'].nunique().reindex(weekly_kpis['L1_Total_Orders'].index, fill_value=0)

    # L2: 재구매 고객 주문 건수 (Repeat Customer Orders)
    # 정의: 해당 기간에 2회 이상 주문을 발생시킨 고객들의 총 주문 건수.
    # 산출 로직: COUNT(DISTINCT order_id) WHERE is_new_customer_order = False
    weekly_kpis['L2_Repeat_Customer_Orders'] = df[~df['is_new_customer_order']].groupby('week_start_date')['order_id'].nunique().reindex(weekly_kpis['L1_Total_Orders'].index, fill_value=0)

    # L3: 총 고객 수 (Total Customers) (주차별로 고유 고객 수)
    # 정의: 일정 기간 동안 서비스를 이용한 전체 고객의 수.
    # 산출 로직: COUNT(DISTINCT customer_unique_id)
    weekly_kpis['L3_Total_Customers'] = df.groupby('week_start_date')['customer_unique_id'].nunique()

    # L3: 재구매 고객 수 (Repeat Customers) (주차별 재구매 고객 수)
    # 정의: 해당 기간에 2회 이상 서비스를 이용한 고객의 수.
    # 산출 로직: COUNT(DISTINCT customer_unique_id) WHERE customer_unique_id IN (과거 주문 이력)
    # 주의: 이 지표는 '해당 주차에 재구매한 고객의 수'를 의미하며, 신규 고객으로 분류되지 않은 고객을 의미합니다.
    # 각 주차의 'is_new_customer_order'가 False인 고유 고객 ID의 수
    weekly_kpis['L3_Repeat_Customers'] = df[~df['is_new_customer_order']].groupby('week_start_date')['customer_unique_id'].nunique().reindex(weekly_kpis['L3_Total_Customers'].index, fill_value=0)

    # L3: 재구매율 (Repeat Purchase Rate)
    # 정의: 특정 기간 동안 재구매한 고객의 비율.
    # 산출 로직: (재구매 고객 수 / 총 고객 수) x 100
    weekly_kpis['L3_Repeat_Purchase_Rate'] = (weekly_kpis['L3_Repeat_Customers'] / weekly_kpis['L3_Total_Customers'] * 100).fillna(0)
    
    # L2: 평균 상품 가격 (Average Product Price)
    # 정의: 판매된 상품 하나의 평균 가격.
    # 산출 로직: SUM(price) / COUNT(order_item_id)
    weekly_kpis['L2_Average_Product_Price'] = df.groupby('week_start_date')['price'].sum() / df.groupby('week_start_date')['order_item_id'].count()
    weekly_kpis['L2_Average_Product_Price'] = weekly_kpis['L2_Average_Product_Price'].fillna(0)

    # L2: 평균 배송비 (Average Freight Value)
    # 정의: 주문당 평균 배송료.
    # 산출 로직: 주문당 고유 배송비를 주차별로 평균
    
    # 주문당 배송비는 order_id별로 고유하므로, 먼저 order_id별 배송비를 추출합니다.
    # 여러 order_item이 동일 order_id를 가질 수 있으므로, order_id별 첫 번째 freight_value를 사용합니다.
    unique_order_freight = df.drop_duplicates(subset=['order_id']).set_index('order_id')['freight_value']
    
    # 각 주문의 week_start_date를 unique_order_freight와 연결
    order_id_to_week_start_date = df.drop_duplicates(subset=['order_id']).set_index('order_id')['week_start_date']
    
    # week_start_date별 평균 배송비 계산
    weekly_kpis['L2_Average_Freight_Value'] = unique_order_freight.groupby(order_id_to_week_start_date).mean()
    weekly_kpis['L2_Average_Freight_Value'] = weekly_kpis['L2_Average_Freight_Value'].reindex(weekly_kpis['L1_Total_Orders'].index, fill_value=0)


    # L2: 평균 할인 금액 (Average Discount Value) - 데이터에 직접적인 할인 컬럼 없음.
    # 이 부분은 데이터셋에 명시적인 '할인 금액' 컬럼이 없으므로, 산출하지 않음.
    # 필요시 payment_value와 price, freight_value를 통해 역산하거나, 다른 데이터소스 필요.
    # 여기서는 지시사항에 따라 스킵.

    # 딕셔너리를 데이터프레임으로 변환
    kpi_df = pd.DataFrame(weekly_kpis)

    # --- 5. 데이터 품질 검증 (산술적 인과관계) ---
    # L0 = L1_Total_Orders * L1_Average_Order_Value 검증
    kpi_df['L0_Verification'] = kpi_df['L1_Total_Orders'] * kpi_df['L1_Average_Order_Value']
    # 부동 소수점 오차를 고려하여 근사치로 비교
    kpi_df['L0_Verified'] = np.isclose(kpi_df['L0_Total_Payment_Value'], kpi_df['L0_Verification'], rtol=1e-05, atol=1e-08)

    # L1_Total_Orders = L2_New_Customer_Orders + L2_Repeat_Customer_Orders 검증
    kpi_df['L1_Orders_Verification'] = kpi_df['L2_New_Customer_Orders'] + kpi_df['L2_Repeat_Customer_Orders']
    kpi_df['L1_Orders_Verified'] = np.isclose(kpi_df['L1_Total_Orders'], kpi_df['L1_Orders_Verification'], rtol=1e-05, atol=1e-08)

    # L3_Repeat_Purchase_Rate = (L3_Repeat_Customers / L3_Total_Customers) * 100 검증
    kpi_df['L3_Repeat_Rate_Verification'] = (kpi_df['L3_Repeat_Customers'] / kpi_df['L3_Total_Customers'] * 100).fillna(0)
    kpi_df['L3_Repeat_Rate_Verified'] = np.isclose(kpi_df['L3_Repeat_Purchase_Rate'], kpi_df['L3_Repeat_Rate_Verification'], rtol=1e-05, atol=1e-08)


    # --- 6. 결과 저장 ---
    kpi_df.index.name = 'week_start_date'
    kpi_df.to_csv(output_file_path)
    
    print(f"주차별 KPI 트렌드 분석이 완료되었습니다. 결과가 '{output_file_path}' 파일에 저장되었습니다.")
    print("\n산술적 인과관계 검증 결과:")
    print(kpi_df[['L0_Verified', 'L1_Orders_Verified', 'L3_Repeat_Rate_Verified']].all())

if __name__ == '__main__':
    generate_weekly_kpi_trends()
