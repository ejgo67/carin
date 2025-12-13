
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 페이지 설정
st.set_page_config(layout="wide", page_title="Online Retail EDA", page_icon="🛍️")

# 한글 폰트 설정 (Streamlit에서 직접 폰트 파일 지정은 어려우므로, 시스템 폰트 사용을 가정)
# Matplotlib, Seaborn을 사용하지 않으므로 Plotly의 기본 폰트 또는 시스템 폰트에 의존합니다.

# 데이터 로딩 및 캐싱
@st.cache_data
def load_data():
    """
    엑셀 파일에서 데이터를 로드하고 기본 전처리를 수행합니다.
    - CustomerID 결측치 제거
    - 중복 행 제거
    - 데이터 타입 변환 (CustomerID, InvoiceDate)
    - TotalPrice 파생 변수 생성
    """
    df = pd.read_excel("online-retail/Online Retail.xlsx")
    
    # CustomerID가 없는 행 제거
    df.dropna(subset=['CustomerID'], inplace=True)
    
    # 중복된 행 제거
    df.drop_duplicates(inplace=True)
    
    # 데이터 타입 변환
    df['CustomerID'] = df['CustomerID'].astype(int)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # 총 구매액 파생 변수 생성
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    # 분석에 필요한 추가 파생 변수 생성
    df['InvoiceYearMonth'] = df['InvoiceDate'].dt.to_period('M')
    df['Hour'] = df['InvoiceDate'].dt.hour
    df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
    
    return df

df = load_data()

# --- 사이드바 ---
st.sidebar.title("메뉴")
st.sidebar.markdown("---")

# 연도/국가 필터
selected_year = st.sidebar.selectbox("연도 선택", options=[2010, 2011], index=1)
selected_country = st.sidebar.selectbox("국가 선택", options=['All'] + list(df['Country'].unique()))

# 필터링된 데이터
filtered_df = df[df['InvoiceDate'].dt.year == selected_year]
if selected_country != 'All':
    filtered_df = filtered_df[filtered_df['Country'] == selected_country]

# 페이지 선택
page = st.sidebar.radio("페이지 선택", ["메인", "매출 분석", "고객 및 상품 분석", "사용자 행동 분석"])
st.sidebar.markdown("---")

# 데이터 검색 기능
st.sidebar.header("데이터 검색")
search_column = st.sidebar.radio("검색할 컬럼", ["Description", "InvoiceNo"])
search_keyword = st.sidebar.text_input(f"{search_column}에서 검색할 키워드를 입력하세요.")

if search_keyword:
    search_result = df[df[search_column].astype(str).str.contains(search_keyword, case=False, na=False)]
    st.sidebar.subheader("검색 결과")
    st.sidebar.dataframe(search_result)

# --- 메인 페이지 ---
def main_page():
    st.title("🛍️ Online Retail 대시보드")
    st.markdown("---")
    st.markdown("이 대시보드는 온라인 소매 데이터를 분석하고 시각화합니다.")
    st.markdown("사이드바에서 메뉴를 선택하여 다양한 분석 결과를 확인하세요.")
    
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())
    
    st.subheader("기본 통계")
    st.write(df.describe())

# --- 매출 분석 페이지 ---
def sales_analysis_page():
    st.title("📈 매출 분석")
    st.markdown("---")
    
    tabs = st.tabs(["월별 총 매출", "상위 10개국 매출"])
    
    with tabs[0]:
        st.subheader("월별 총 매출")
        monthly_sales = filtered_df.groupby(filtered_df['InvoiceDate'].dt.to_period('M'))['TotalPrice'].sum().reset_index()
        monthly_sales['InvoiceDate'] = monthly_sales['InvoiceDate'].astype(str)
        fig = px.line(monthly_sales, x='InvoiceDate', y='TotalPrice', title="월별 총 매출", labels={'InvoiceDate': '월', 'TotalPrice': '총 매출'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(monthly_sales)

    with tabs[1]:
        st.subheader("상위 10개국 매출")
        top_countries = filtered_df.groupby('Country')['TotalPrice'].sum().nlargest(10).reset_index()
        fig = px.bar(top_countries, x='Country', y='TotalPrice', title="상위 10개국 매출", labels={'Country': '국가', 'TotalPrice': '총 매출'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(top_countries)

# --- 고객 및 상품 분석 페이지 ---
def customer_product_analysis_page():
    st.title("👥 고객 및 상품 분석")
    st.markdown("---")
    
    tabs = st.tabs(["상위 10개 상품 판매량", "상위 10명 고객 구매액"])
    
    with tabs[0]:
        st.subheader("상위 10개 상품 판매량")
        top_products = filtered_df.groupby('Description')['Quantity'].sum().nlargest(10).reset_index().sort_values('Quantity', ascending=True)
        fig = px.bar(top_products, y='Description', x='Quantity', orientation='h', title="상위 10개 상품 판매량", labels={'Description': '상품 설명', 'Quantity': '판매량'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(top_products.sort_values('Quantity', ascending=False))

    with tabs[1]:
        st.subheader("상위 10명 고객 구매액")
        top_customers = filtered_df.groupby('CustomerID')['TotalPrice'].sum().nlargest(10).reset_index()
        top_customers['CustomerID'] = top_customers['CustomerID'].astype(str)
        fig = px.bar(top_customers, x='CustomerID', y='TotalPrice', title="상위 10명 고객 구매액", labels={'CustomerID': '고객 ID', 'TotalPrice': '총 구매액'})
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("데이터 보기"):
            st.dataframe(top_customers)

# --- 사용자 행동 분석 페이지 ---
def user_behavior_analysis_page():
    st.title("🏃 사용자 행동 분석")
    st.markdown("---")
    
    tabs = st.tabs(["시간/요일별 주문", "월별 ARPU", "DAU vs MAU", "주문 히트맵", "고객 리텐션"])

    with tabs[0]:
        st.subheader("시간대별/요일별 주문 건수")
        
        # 시간대별
        hourly_orders = filtered_df.groupby('Hour')['InvoiceNo'].nunique().reset_index()
        fig_hour = px.bar(hourly_orders, x='Hour', y='InvoiceNo', title="시간대별 주문 건수", labels={'Hour': '시간', 'InvoiceNo': '주문 건수'})
        st.plotly_chart(fig_hour, use_container_width=True)
        
        # 요일별
        daily_orders = filtered_df.groupby('DayOfWeek')['InvoiceNo'].nunique().reset_index()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_orders['DayOfWeek'] = pd.Categorical(daily_orders['DayOfWeek'], categories=day_order, ordered=True)
        daily_orders = daily_orders.sort_values('DayOfWeek')
        fig_day = px.bar(daily_orders, x='DayOfWeek', y='InvoiceNo', title="요일별 주문 건수", labels={'DayOfWeek': '요일', 'InvoiceNo': '주문 건수'})
        st.plotly_chart(fig_day, use_container_width=True)

        with st.expander("데이터 보기"):
            st.dataframe(hourly_orders, column_config={"Hour": "시간", "InvoiceNo": "주문 건수"})
            st.dataframe(daily_orders, column_config={"DayOfWeek": "요일", "InvoiceNo": "주문 건수"})

    with tabs[1]:
        st.subheader("월별 ARPU (가입자당 평균 매출)")
        df_arpu = filtered_df.copy()
        df_arpu['InvoiceYearMonth'] = df_arpu['InvoiceDate'].dt.to_period('M')
        
        monthly_revenue = df_arpu.groupby('InvoiceYearMonth')['TotalPrice'].sum()
        monthly_users = df_arpu.groupby('InvoiceYearMonth')['CustomerID'].nunique()
        monthly_arpu = (monthly_revenue / monthly_users).reset_index()
        monthly_arpu.columns = ['InvoiceYearMonth', 'ARPU']
        monthly_arpu['InvoiceYearMonth'] = monthly_arpu['InvoiceYearMonth'].astype(str)
        
        fig_arpu_line = px.line(monthly_arpu, x='InvoiceYearMonth', y='ARPU', title='월별 ARPU (Line)', labels={'InvoiceYearMonth': '월', 'ARPU': 'ARPU'})
        st.plotly_chart(fig_arpu_line, use_container_width=True)
        
        fig_arpu_bar = px.bar(monthly_arpu, x='InvoiceYearMonth', y='ARPU', title='월별 ARPU (Bar)', labels={'InvoiceYearMonth': '월', 'ARPU': 'ARPU'})
        st.plotly_chart(fig_arpu_bar, use_container_width=True)

        with st.expander("데이터 보기"):
            st.dataframe(monthly_arpu)

    with tabs[2]:
        st.subheader("평균 DAU vs MAU")
        df_users = filtered_df.copy()
        df_users['InvoiceDateOnly'] = df_users['InvoiceDate'].dt.date
        df_users['InvoiceYearMonth'] = df_users['InvoiceDate'].dt.to_period('M')

        mau = df_users.groupby('InvoiceYearMonth')['CustomerID'].nunique()
        dau = df_users.groupby(['InvoiceYearMonth', 'InvoiceDateOnly'])['CustomerID'].nunique().groupby('InvoiceYearMonth').mean()
        
        user_metrics = pd.concat([dau, mau], axis=1).reset_index()
        user_metrics.columns = ['Month', 'DAU', 'MAU']
        user_metrics['Month'] = user_metrics['Month'].astype(str)

        fig = go.Figure(data=[
            go.Bar(name='DAU', x=user_metrics['Month'], y=user_metrics['DAU']),
            go.Bar(name='MAU', x=user_metrics['Month'], y=user_metrics['MAU'])
        ])
        fig.update_layout(barmode='group', title='평균 DAU vs MAU', xaxis_title='월', yaxis_title='사용자 수')
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("데이터 보기"):
            st.dataframe(user_metrics)

    with tabs[3]:
        st.subheader("시간-요일별 주문 히트맵")
        heatmap_data = filtered_df.groupby(['Hour', 'DayOfWeek'])['InvoiceNo'].nunique().reset_index()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_pivot = heatmap_data.pivot_table(index='DayOfWeek', columns='Hour', values='InvoiceNo').reindex(day_order)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale='Viridis'))
        fig.update_layout(title='시간-요일별 주문 히트맵', xaxis_title='시간', yaxis_title='요일')
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("데이터 보기"):
            st.dataframe(heatmap_pivot.fillna(0).astype(int))

    with tabs[4]:
        st.subheader("월단위 고객 리텐션")
        retention_df = filtered_df.copy()
        retention_df['InvoiceYearMonth'] = retention_df['InvoiceDate'].dt.to_period('M')
        retention_df['AcquisitionMonth'] = retention_df.groupby('CustomerID')['InvoiceYearMonth'].transform('min')
        
        def get_month_diff(row):
            return (row['InvoiceYearMonth'].year - row['AcquisitionMonth'].year) * 12 + \
                   (row['InvoiceYearMonth'].month - row['AcquisitionMonth'].month)
        
        retention_df['CohortIndex'] = retention_df.apply(get_month_diff, axis=1)
        
        cohort_data = retention_df.groupby(['AcquisitionMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
        cohort_count = cohort_data.pivot_table(index='AcquisitionMonth', columns='CohortIndex', values='CustomerID')
        
        cohort_size = cohort_count.iloc[:, 0]
        retention_matrix = cohort_count.divide(cohort_size, axis=0)
        
        retention_matrix = retention_matrix.applymap(lambda x: f'{x:.0%}' if pd.notna(x) else '')
        
        # 첫 번째 열 이름 변경
        retention_matrix.rename(columns={0: 'Acquisition'}, inplace=True)
        
        z_values = retention_matrix.replace('%', '', regex=True).replace('', np.nan).astype(float) / 100
        
        fig = go.Figure(data=go.Heatmap(
            z=z_values,
            x=retention_matrix.columns,
            y=retention_matrix.index.strftime('%Y-%m'),
            text=retention_matrix.values,
            texttemplate="%{text}",
            colorscale='Blues'
        ))
        
        fig.update_layout(
            title='월단위 고객 리텐션',
            xaxis_title='경과 월',
            yaxis_title='고객 유입 월',
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("데이터 보기"):
            st.dataframe(retention_matrix)


# --- 페이지 라우팅 ---
if page == "메인":
    main_page()
elif page == "매출 분석":
    sales_analysis_page()
elif page == "고객 및 상품 분석":
    customer_product_analysis_page()
elif page == "사용자 행동 분석":
    user_behavior_analysis_page()
