
import streamlit as st
import pandas as pd
import datetime

# --- 데이터 로딩 ---
@st.cache_data
def load_data():
    """
    Olist 데이터셋의 3개 핵심 파일을 로드하는 함수.
    - `st.cache_data`를 사용하여 데이터 로딩을 캐시, 성능을 최적화합니다.
    - 데이터 경로: 'olist/'
    """
    try:
        orders = pd.read_csv('olist/olist_orders_dataset.csv')
        customers = pd.read_csv('olist/olist_customers_dataset.csv')
        payments = pd.read_csv('olist/olist_order_payments_dataset.csv')
        return orders, customers, payments
    except FileNotFoundError as e:
        st.error(f"데이터 파일을 찾을 수 없습니다: {e}. 'olist' 디렉토리에 파일이 있는지 확인하세요.")
        return None, None, None

# --- 데이터 모델링 (Fact 테이블 생성) ---
def create_fact_table(orders, customers, payments):
    """
    KPI 계산을 위한 기본 Fact 테이블을 생성하는 함수.
    - Grain(행 기준): 1 order_id = 1 row
    - 중복 조인을 피하기 위해 payments 테이블을 먼저 집계 후 조인합니다.
    """
    # 1. order_id 기준으로 결제 금액 합산 (payment_value_total)
    payments_agg = payments.groupby('order_id')['payment_value'].sum().reset_index()
    payments_agg.rename(columns={'payment_value': 'payment_value_total'}, inplace=True)

    # 2. orders & customers 조인
    orders_customers = pd.merge(orders, customers, on='customer_id')

    # 3. orders_customers & payments_agg 조인
    fact_table = pd.merge(orders_customers, payments_agg, on='order_id', how='left')

    # 4. 시간 관련 컬럼 타입 변환
    fact_table['order_purchase_timestamp'] = pd.to_datetime(fact_table['order_purchase_timestamp'])

    # 5. 핵심 컬럼 선택
    fact_table = fact_table[[
        'order_id',
        'customer_unique_id',
        'order_status',
        'order_purchase_timestamp',
        'payment_value_total'
    ]]

    # payment_value가 없는 경우(결제 정보 없음) 0으로 채움
    fact_table['payment_value_total'] = fact_table['payment_value_total'].fillna(0)

    return fact_table



# --- KPI 계산 ---

def calculate_kpis(fact_table, filtered_fact_table):

    """

    AARRR 프레임워크에 따라 KPI를 계산하는 함수.

    - Acquisition 지표는 전체 기간의 데이터를 사용.

    - Activation 이후 지표는 선택된 기간의 'delivered' 데이터를 사용.

    """

    # --- 기간 필터링된 데이터 준비 ---

    delivered_orders = filtered_fact_table[filtered_fact_table['order_status'] == 'delivered'].copy()



    # --- Acquisition (획득) - 전체 기간 기준 ---

    unique_customers = fact_table['customer_unique_id'].nunique()

    total_orders = fact_table['order_id'].nunique()



    # --- Activation (활성화) - 선택 기간 기준 ---

    activated_customers_df = delivered_orders.groupby('customer_unique_id')['order_id'].count().reset_index()

    activated_customers = activated_customers_df['customer_unique_id'].nunique()

    # 활성화율의 분모는 '전체 기간'의 고유 고객을 사용하는 것이 일반적임

    activation_rate = activated_customers / unique_customers if unique_customers > 0 else 0



    # --- Retention (유지) - 선택 기간 기준 ---

    # 재구매 고객: 선택된 기간 내에 2회 이상 구매한 고객

    repeat_customers_df = activated_customers_df[activated_customers_df['order_id'] >= 2]

    repeat_customers = repeat_customers_df['customer_unique_id'].nunique()

    retention_rate = repeat_customers / activated_customers if activated_customers > 0 else 0



    # --- Revenue (매출) - 선택 기간 기준 ---

    total_revenue = delivered_orders['payment_value_total'].sum()

    paying_customers_df = delivered_orders[delivered_orders['payment_value_total'] > 0]

    paying_customers = paying_customers_df['customer_unique_id'].nunique()

    

    # ARPU와 AOV는 선택된 기간의 매출을 기준으로 계산

    arpu = total_revenue / unique_customers if unique_customers > 0 else 0

    

    delivered_order_count = delivered_orders['order_id'].nunique()

    aov = total_revenue / delivered_order_count if delivered_order_count > 0 else 0



    # --- Referral (추천, Proxy) ---

    repeat_purchase_rate = retention_rate



    kpis = {

        # Acquisition

        "Unique Customers": {"value": unique_customers, "help": "전체 기간 동안 한 번이라도 상호작용한 고유 고객 수 (날짜 필터에 영향 받지 않음)"},

        "Orders": {"value": total_orders, "help": "전체 기간 동안 발생한 총 주문 수 (날짜 필터에 영향 받지 않음)"},

        # Activation

        "Activated Customers": {"value": activated_customers, "help": "선택 기간 내 'delivered' 주문을 1회 이상 완료한 고유 고객 수"},

        "Activation Rate": {"value": f"{activation_rate:.2%}", "help": "전체 고객 중 선택 기간 내에 활성화된 고객의 비율 (Activated Customers / Unique Customers)"},

        # Retention

        "Repeat Customers": {"value": repeat_customers, "help": "선택 기간 내 'delivered' 주문을 2회 이상 완료한 고유 고객 수"},

        "Retention Rate": {"value": f"{retention_rate:.2%}", "help": "선택 기간 내 활성화 고객 중 재구매한 고객의 비율 (Repeat Customers / Activated Customers)"},

        # Revenue

        "Total Revenue": {"value": f"R$ {total_revenue:,.2f}", "help": "선택 기간 내 'delivered' 주문에서 발생한 총 매출"},

        "Paying Customers": {"value": paying_customers, "help": "선택 기간 내 'delivered' 주문에서 0 이상의 결제를 한 고유 고객 수"},

        "ARPU": {"value": f"R$ {arpu:,.2f}", "help": "선택 기간의 매출을 전체 고객으로 나눈 값 (기간 매출 / 전체 고객 수)"},

        "AOV": {"value": f"R$ {aov:,.2f}", "help": "선택 기간 내 주문 1건당 평균 매출 (기간 매출 / 기간 'delivered' 주문 수)"},

        # Referral

        "Repeat Purchase Rate": {"value": f"{repeat_purchase_rate:.2%}", "help": "선택 기간 내 활성화 고객 중 재구매한 고객의 비율 (추천 지표의 Proxy)"},

    }

    return kpis



# --- 대시보드 메인 함수 ---

def main():

    st.set_page_config(page_title="AARRR KPI 대시보드", layout="wide")

    st.title("AARRR KPI 대시보드 (Olist E-Commerce)")

    st.markdown("""

    이 대시보드는 Olist 이커머스 데이터를 AARRR 프레임워크에 맞춰 분석합니다.

    **KPI 숫자 중심**으로 비즈니스의 핵심 지표를 파악하는 것을 목적으로 합니다.

    - **데이터 모델링**: 주문(orders)을 기준으로 고객, 결제 정보를 통합한 Fact 테이블 사용.

    - **KPI 산출 기준**: `delivered` 상태의 주문을 기준으로 활성화(Activation) 및 이후 지표를 계산.

    - **주의**: 추천(Referral) 지표는 데이터 부재로 재구매율을 프록시 지표로 사용합니다.

    """)



    # 데이터 로딩 및 Fact 테이블 생성

    orders, customers, payments = load_data()



    if orders is not None:

        fact_table = create_fact_table(orders, customers, payments)



        # --- 사이드바 날짜 필터 ---

        st.sidebar.header("날짜 필터")

        min_date = fact_table['order_purchase_timestamp'].min().date()

        max_date = fact_table['order_purchase_timestamp'].max().date()



        start_date = st.sidebar.date_input("시작일", min_date, min_value=min_date, max_value=max_date)

        end_date = st.sidebar.date_input("종료일", max_date, min_value=start_date, max_value=max_date)



        # --- 선택된 기간에 따라 데이터 필터링 ---

        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)

        end_datetime = datetime.datetime.combine(end_date, datetime.time.max)



        filtered_fact_table = fact_table[

            (fact_table['order_purchase_timestamp'] >= start_datetime) &

            (fact_table['order_purchase_timestamp'] <= end_datetime)

        ]



        # --- KPI 계산 ---

        # Acquisition 지표는 전체 기간 데이터를, 그 외는 필터링된 데이터를 사용하여 계산

        kpis = calculate_kpis(fact_table, filtered_fact_table)



        # --- KPI 대시보드 ---

        st.subheader(f"AARRR KPI 요약 ({start_date} ~ {end_date})")



        # Acquisition

        st.markdown("### 획득 (Acquisition)")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(label="고유 고객 수 (Unique Customers)", value=kpis["Unique Customers"]["value"], help=kpis["Unique Customers"]["help"])

        with col2:

            st.metric(label="총 주문 수 (Orders)", value=kpis["Orders"]["value"], help=kpis["Orders"]["help"])



        # Activation

        st.markdown("### 활성화 (Activation)")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(label="활성 고객 수 (Activated Customers)", value=kpis["Activated Customers"]["value"], help=kpis["Activated Customers"]["help"])

        with col2:

            st.metric(label="활성화율 (Activation Rate)", value=kpis["Activation Rate"]["value"], help=kpis["Activation Rate"]["help"])



        # Retention

        st.markdown("### 유지 (Retention)")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(label="재구매 고객 수 (Repeat Customers)", value=kpis["Repeat Customers"]["value"], help=kpis["Repeat Customers"]["help"])

        with col2:

            st.metric(label="유지율 (Retention Rate)", value=kpis["Retention Rate"]["value"], help=kpis["Retention Rate"]["help"])

            

        # Revenue

        st.markdown("### 매출 (Revenue)")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(label="총 매출 (Total Revenue)", value=kpis["Total Revenue"]["value"], help=kpis["Total Revenue"]["help"])

        with col2:

            st.metric(label="결제 고객 수 (Paying Customers)", value=kpis["Paying Customers"]["value"], help=kpis["Paying Customers"]["help"])

        

        col1, col2 = st.columns(2)

        with col1:

            st.metric(label="고객 1인당 평균 매출 (ARPU)", value=kpis["ARPU"]["value"], help=kpis["ARPU"]["help"])

        with col2:

            st.metric(label="주문 1건당 평균 매출 (AOV)", value=kpis["AOV"]["value"], help=kpis["AOV"]["help"])

        

        # Referral

        st.markdown("### 추천 (Referral - Proxy)")

        st.metric(label="재구매율 (Repeat Purchase Rate)", value=kpis["Repeat Purchase Rate"]["value"], help=kpis["Repeat Purchase Rate"]["help"])



if __name__ == "__main__":

    main()


