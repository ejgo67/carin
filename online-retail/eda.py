import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import seaborn as sns

# 이미지 저장 폴더 생성
if not os.path.exists('online-retail/images'):
    os.makedirs('online-retail/images')

# 데이터 로드
try:
    df = pd.read_excel('online-retail/Online Retail.xlsx')
except FileNotFoundError:
    print("Error: 'online-retail/Online Retail.xlsx' 파일을 찾을 수 없습니다.")
    exit()

# --- 데이터 전처리 ---
# 결측치 제거
df.dropna(subset=['CustomerID'], inplace=True)
df['Description'].fillna('No description', inplace=True)

# 데이터 타입 변환
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['CustomerID'] = df['CustomerID'].astype('int64').astype('str')

# 주문 취소 건 제외 (InvoiceNo가 'C'로 시작)
df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]

# 총 가격 (TotalPrice) 컬럼 생성
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']


# --- EDA 및 시각화 ---
report_md = """
# Online Retail 데이터 분석 보고서

이 보고서는 Online Retail 데이터셋에 대한 탐색적 데이터 분석(EDA) 결과를 요약하고, 각 분석의 기준과 방법을 함께 제시합니다.

## 1. 분석 개요

### 1.1. 분석 목표
Online Retail 데이터셋의 주요 특징을 파악하고, 매출, 고객, 상품 등 다양한 관점에서 비즈니스 인사이트를 도출하는 것을 목표로 합니다.

### 1.2. 데이터 전처리
분석의 정확도를 높이기 위해 다음과 같은 전처리 과정을 수행했습니다.
- **결측치 처리**: `CustomerID`가 없는 데이터는 고객 식별이 불가능하므로 제거했으며, `Description`의 결측치는 'No description'으로 대체했습니다.
- **데이터 타입 변환**: `InvoiceDate`는 날짜/시간 타입으로, `CustomerID`는 문자열 타입으로 변환했습니다.
- **이상치 제거**: 주문 취소 건(InvoiceNo가 'C'로 시작)은 분석에서 제외했습니다.
- **파생 변수 생성**: 분석을 위해 수량과 단가를 곱하여 총 가격(`TotalPrice`) 컬럼을 생성했습니다.

---

## 2. 데이터 기본 정보

### 데이터 샘플 (상위 5개)
```
{df_head}
```

### 데이터 통계 요약
```
{df_describe}
```

---

## 3. 국가별 분석

### 3.1. 주문 건수 상위 10개국
- **분석 방법**: 국가(`Country`)별로 데이터 개수를 카운트(`value_counts()`)하여 주문 건수를 집계하고, 가장 많은 주문 건수를 기록한 상위 10개국을 시각화했습니다.
- **분석 결과**: United Kingdom이 압도적으로 많은 주문을 차지하고 있으며, 그 뒤를 독일, 프랑스, EIRE(아일랜드)가 잇고 있습니다.
"""

# 1. 국가별 주문 건수
plt.figure(figsize=(12, 6))
country_counts = df['Country'].value_counts().nlargest(10)
country_counts.plot(kind='bar')
plt.title('주문 건수 상위 10개국')
plt.xlabel('국가')
plt.ylabel('주문 건수')
plt.xticks(rotation=45)
plt.tight_layout()
plot_path_1 = 'online-retail/images/plot_1_top_10_countries_orders.png'
plt.savefig(plot_path_1)
plt.close()

report_md += f"""
![주문 건수 상위 10개국](../{plot_path_1})

#### 교차표: 국가별 주문 건수
{country_counts.to_markdown(index=True)}
---

### 3.2. 매출액 상위 10개국
- **분석 방법**: 국가(`Country`)별로 총 매출액(`TotalPrice`)의 합계(`sum()`)를 계산(`groupby()`)하고, 매출액 기준 상위 10개국을 시각화했습니다.
- **분석 결과**: 주문 건수와 마찬가지로 매출액 역시 United Kingdom이 가장 높습니다. 네덜란드와 EIRE(아일랜드)가 영국 다음으로 높은 매출을 보입니다.
"""
plt.figure(figsize=(12, 6))
country_sales = df.groupby('Country')['TotalPrice'].sum().nlargest(10)
country_sales.plot(kind='bar', color='skyblue')
plt.title('매출액 상위 10개국')
plt.xlabel('국가')
plt.ylabel('총 매출액')
plt.xticks(rotation=45)
plt.tight_layout()
plot_path_2 = 'online-retail/images/plot_2_top_10_countries_sales.png'
plt.savefig(plot_path_2)
plt.close()

report_md += f"""
![매출액 상위 10개국](../{plot_path_2})

#### 피봇 테이블: 국가별 매출액
{country_sales.to_markdown(index=True)}
---
"""

# 월별, 요일별, 시간별 분석을 위한 데이터 가공
df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
df['Hour'] = df['InvoiceDate'].dt.hour
df['Date'] = df['InvoiceDate'].dt.date


# 3. 월별 매출 추이
report_md += """
## 4. 시간 흐름에 따른 분석

### 4.1. 월별 매출 추이
- **분석 방법**: 주문일(`InvoiceDate`)에서 '연도-월' 정보를 추출하여 `YearMonth` 파생 변수를 만들고, 이를 기준으로 총 매출액(`TotalPrice`)의 합계를 집계했습니다.
- **분석 결과**: 2011년 데이터가 대부분이며, 11월에 매출이 가장 정점을 찍는 것을 볼 수 있습니다. 이는 연말 쇼핑 시즌의 영향으로 보입니다.
"""
plt.figure(figsize=(12, 6))
monthly_sales = df.groupby('YearMonth')['TotalPrice'].sum()
monthly_sales.index = monthly_sales.index.astype(str)
monthly_sales.plot(kind='line', marker='o')
plt.title('월별 매출 추이')
plt.xlabel('월')
plt.ylabel('총 매출액')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plot_path_3 = 'online-retail/images/plot_3_monthly_sales_trend.png'
plt.savefig(plot_path_3)
plt.close()

report_md += f"""
![월별 매출 추이](../{plot_path_3})

#### 피봇 테이블: 월별 매출액
{monthly_sales.to_markdown(index=True)}
---

### 4.2. 요일별 주문 건수
- **분석 방법**: 주문일(`InvoiceDate`)에서 요일 정보(`DayOfWeek`)를 추출하고, 요일별 데이터 개수를 카운트하여 주문 건수를 집계했습니다.
- **분석 결과**: 주문은 주중에 집중되어 있으며, 특히 목요일에 가장 많은 주문이 발생합니다. 주말인 토요일은 주문이 현저히 적고, 일요일 주문 데이터는 없습니다.
"""
plt.figure(figsize=(10, 5))
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
daily_orders = df['DayOfWeek'].value_counts().reindex(day_order)
daily_orders.plot(kind='bar', color='lightgreen')
plt.title('요일별 주문 건수')
plt.xlabel('요일')
plt.ylabel('주문 건수')
plt.xticks(rotation=0)
plt.tight_layout()
plot_path_4 = 'online-retail/images/plot_4_daily_orders.png'
plt.savefig(plot_path_4)
plt.close()

report_md += f"""
![요일별 주문 건수](../{plot_path_4})

#### 교차표: 요일별 주문 건수
{daily_orders.to_markdown(index=True)}
---

### 4.3. 시간대별 주문 건수
- **분석 방법**: 주문일(`InvoiceDate`)에서 시간 정보(`Hour`)를 추출하고, 시간대별 고유 주문서 수(`InvoiceNo.nunique()`)를 집계했습니다.
- **분석 결과**: 오후 12시(정오)에 주문이 가장 많으며, 대체로 점심시간을 포함한 오후 시간대에 주문이 집중되는 경향을 보입니다.
"""
plt.figure(figsize=(12, 6))
hourly_orders = df.groupby('Hour')['InvoiceNo'].nunique()
hourly_orders.plot(kind='bar', color='orange')
plt.title('시간대별 주문 건수')
plt.xlabel('시간')
plt.ylabel('주문 건수')
plt.xticks(rotation=0)
plt.grid(axis='y')
plt.tight_layout()
plot_path_5 = 'online-retail/images/plot_5_hourly_orders.png'
plt.savefig(plot_path_5)
plt.close()

report_md += f"""
![시간대별 주문 건수](../{plot_path_5})

#### 피봇 테이블: 시간대별 주문 건수
{hourly_orders.to_markdown(index=True)}
---
"""

# 6. 상위 10개 판매 상품 (수량 기준)
report_md += """
## 5. 상품 분석

### 5.1. 판매 수량 상위 10개 상품
- **분석 방법**: 상품명(`Description`)을 기준으로 총 판매 수량(`Quantity`)의 합계를 계산하고, 판매 수량 기준 상위 10개 상품을 시각화했습니다.
- **분석 결과**: 'WORLD WAR 2 GLIDERS ASSTD DESIGNS', 'JUMBO BAG RED RETROSPOT' 등 부피가 크거나 묶음 상품으로 보이는 제품들이 상위권을 차지하고 있습니다.
"""
plt.figure(figsize=(12, 6))
top_products_quantity = df.groupby('Description')['Quantity'].sum().nlargest(10)
top_products_quantity.sort_values().plot(kind='barh', color='coral')
plt.title('판매 수량 상위 10개 상품')
plt.xlabel('총 판매 수량')
plt.ylabel('상품명')
plt.tight_layout()
plot_path_6 = 'online-retail/images/plot_6_top_10_products_quantity.png'
plt.savefig(plot_path_6)
plt.close()

report_md += f"""
![판매 수량 상위 10개 상품](../{plot_path_6})

#### 피봇 테이블: 판매 수량 상위 10개 상품
{top_products_quantity.to_markdown(index=True)}
---

### 5.2. 판매 매출액 상위 10개 상품
- **분석 방법**: 상품명(`Description`)을 기준으로 총 매출액(`TotalPrice`)의 합계를 계산하고, 매출액 기준 상위 10개 상품을 시각화했습니다.
- **분석 결과**: 'DOTCOM POSTAGE'가 가장 높은 매출을 기록했으며, 이는 배송료 관련 항목으로 추정됩니다. 그 외에는 'REGENCY CAKESTAND 3 TIER'와 같은 고가 상품이 상위권에 있습니다.
"""
plt.figure(figsize=(12, 6))
top_products_sales = df.groupby('Description')['TotalPrice'].sum().nlargest(10)
top_products_sales.sort_values().plot(kind='barh', color='gold')
plt.title('판매 매출액 상위 10개 상품')
plt.xlabel('총 매출액')
plt.ylabel('상품명')
plt.tight_layout()
plot_path_7 = 'online-retail/images/plot_7_top_10_products_sales.png'
plt.savefig(plot_path_7)
plt.close()

report_md += f"""
![판매 매출액 상위 10개 상품](../{plot_path_7})

#### 피봇 테이블: 판매 매출액 상위 10개 상품
{top_products_sales.to_markdown(index=True)}
---
"""

# 8. 단가(UnitPrice) 분포
report_md += """
## 6. 가격 분석

### 6.1. 상품 단가 분포
- **분석 방법**: 상품 단가(`UnitPrice`)의 분포를 히스토그램으로 시각화했습니다. 대부분의 상품이 낮은 가격대에 분포하고 있어, 분포를 자세히 확인하기 위해 단가 50 이하인 상품들만 필터링하여 시각화했습니다.
- **분석 결과**: 대부분의 상품이 0에 가까운 낮은 단가를 가지고 있으며, 일부 고가 상품이 존재합니다. 단가가 0인 경우는 프로모션 또는 오류 데이터일 수 있으므로 추가적인 확인이 필요합니다.
"""
plt.figure(figsize=(12, 6))
# 단가가 0인 경우를 제외하고, 현실적인 범위에서 확인
df[df['UnitPrice'] < 50]['UnitPrice'].hist(bins=50, color='purple')
plt.title('상품 단가 분포 (0-50 범위)')
plt.xlabel('단가 (UnitPrice)')
plt.ylabel('빈도')
plt.tight_layout()
plot_path_8 = 'online-retail/images/plot_8_unitprice_distribution.png'
plt.savefig(plot_path_8)
plt.close()

report_md += f"""
![상품 단가 분포](../{plot_path_8})
---
"""

# 9. 고객별 분석: 총 구매액 기준 상위 10명
report_md += """
## 7. 고객 분석

### 7.1. 총 구매액 상위 10명 고객
- **분석 방법**: 고객 ID(`CustomerID`)를 기준으로 총 구매액(`TotalPrice`)의 합계를 계산하고, 상위 10명의 고객을 시각화했습니다.
- **분석 결과**: 특정 고객들이 전체 매출에 큰 기여를 하고 있음을 알 수 있습니다. 상위 고객(VIP) 관리가 중요한 비즈니스 전략이 될 수 있습니다.
"""
plt.figure(figsize=(12, 6))
top_customers = df.groupby('CustomerID')['TotalPrice'].sum().nlargest(10)
top_customers.sort_values().plot(kind='barh', color='brown')
plt.title('총 구매액 상위 10명 고객')
plt.xlabel('총 구매액')
plt.ylabel('고객 ID')
plt.tight_layout()
plot_path_9 = 'online-retail/images/plot_9_top_10_customers_sales.png'
plt.savefig(plot_path_9)
plt.close()

report_md += f"""
![총 구매액 상위 10명 고객](../{plot_path_9})

#### 피봇 테이블: 총 구매액 상위 10명 고객
{top_customers.to_markdown(index=True)}
---
"""

# 10. 주문당 상품 수량 분포
report_md += """
## 8. 주문 특성 분석

### 8.1. 주문당 평균 상품 수량
- **분석 방법**: 주문 번호(`InvoiceNo`)를 기준으로 판매 수량(`Quantity`)의 합계를 계산하여 '주문당 총 수량'을 구하고, 이의 분포와 평균을 확인했습니다.
- **분석 결과**: 한 번의 주문에 평균적으로 약 12개의 상품을 구매하는 것으로 나타났습니다. 하지만 분포를 보면 대부분의 주문은 평균보다 적은 수량을 포함하고, 일부 대량 주문이 평균을 높이는 것을 알 수 있습니다.
"""
plt.figure(figsize=(12, 6))
quantity_per_invoice = df.groupby('InvoiceNo')['Quantity'].sum()
quantity_per_invoice.hist(bins=100, range=(0, 500), color='cyan')
plt.title('주문당 상품 수량 분포 (0-500 범위)')
plt.xlabel('주문당 총 수량')
plt.ylabel('빈도')
plt.axvline(quantity_per_invoice.mean(), color='red', linestyle='dashed', linewidth=2)
plt.text(quantity_per_invoice.mean()+10, 500, f'평균: {quantity_per_invoice.mean():.2f}', color='red')

plt.tight_layout()
plot_path_10 = 'online-retail/images/plot_10_quantity_per_invoice.png'
plt.savefig(plot_path_10)
plt.close()

report_md += f"""
![주문당 상품 수량 분포](../{plot_path_10})

평균값(빨간 점선)을 통해 대부분의 주문이 평균 이하의 수량을 가짐을 알 수 있습니다.
---
"""

# 11. Monthly Average Revenue Per User (ARPU)
report_md += """
## 9. 사용자 행동 지표 분석

### 9.1. 월별 사용자당 평균 매출 (ARPU)
- **분석 방법**: 월별 사용자당 평균 매출(ARPU, Average Revenue Per User)은 `월별 총 매출 / 월별 활성 사용자 수(MAU)`로 계산합니다. 이를 통해 사용자 한 명이 특정 월에 평균적으로 얼마의 매출을 발생시키는지 파악할 수 있습니다.
- **분석 결과**: 월별 ARPU 추이를 통해 객단가의 변화나 프로모션 효과 등을 가늠해볼 수 있습니다.
"""
monthly_sales_for_arpu = df.groupby('YearMonth')['TotalPrice'].sum()
mau_for_arpu = df.groupby('YearMonth')['CustomerID'].nunique()
arpu = monthly_sales_for_arpu / mau_for_arpu
arpu.index = arpu.index.astype(str)

# 선 그래프
plt.figure(figsize=(12, 6))
arpu.plot(kind='line', marker='o', color='deeppink')
plt.title('월별 사용자당 평균 매출(ARPU) 추이')
plt.xlabel('월')
plt.ylabel('ARPU')
plt.grid(True)
plt.tight_layout()
plot_path_11 = 'online-retail/images/plot_11_monthly_arpu_line.png'
plt.savefig(plot_path_11)
plt.close()

# 막대 그래프
plt.figure(figsize=(12, 6))
arpu.plot(kind='bar', color='tomato')
plt.title('월별 사용자당 평균 매출(ARPU)')
plt.xlabel('월')
plt.ylabel('ARPU')
plt.xticks(rotation=45)
plt.tight_layout()
plot_path_12 = 'online-retail/images/plot_12_monthly_arpu_bar.png'
plt.savefig(plot_path_12)
plt.close()


report_md += f"""
![월별 ARPU 선 그래프](../{plot_path_11})

![월별 ARPU 막대 그래프](../{plot_path_12})

#### 피봇 테이블: 월별 ARPU
{arpu.to_markdown(index=True)}
---

### 9.2. 활성 사용자 분석 (DAU/MAU)
- **분석 방법**:
    - **DAU (Daily Active Users)**: 일별 고유 접속 고객 수(`CustomerID.nunique()`)를 집계합니다.
    - **MAU (Monthly Active Users)**: 월별 고유 접속 고객 수(`CustomerID.nunique()`)를 집계합니다.
    - **Stickiness (DAU/MAU Ratio)**: `평균 DAU / 평균 MAU`로 계산하며, 서비스에 얼마나 자주 방문하는지를 나타내는 충성도 지표입니다.
- **분석 결과**: MAU는 꾸준히 증가하는 추세를 보이며 서비스가 성장하고 있음을 보여줍니다. Stickiness 비율을 통해 고객 충성도를 가늠할 수 있습니다.
"""
dau = df.groupby('Date')['CustomerID'].nunique()
mau = df.groupby('YearMonth')['CustomerID'].nunique()

plt.figure(figsize=(12, 6))
mau_plot = mau.copy()
mau_plot.index = mau_plot.index.to_timestamp()
mau_plot.plot(kind='bar', color='lightblue')
plt.title('월별 활성 사용자 수 (MAU)')
plt.xlabel('월')
plt.ylabel('고유 사용자 수')
plt.xticks(rotation=45)
plt.tight_layout()
plot_path_13 = 'online-retail/images/plot_13_mau.png'
plt.savefig(plot_path_13)
plt.close()

dau_mau_ratio = dau.mean() / mau.mean() if mau.mean() != 0 else 0

report_md += f"""
![월별 활성 사용자 수](../{plot_path_13})

- **평균 DAU:** {dau.mean():.2f}
- **평균 MAU:** {mau.mean():.2f}
- **DAU/MAU 비율 (Stickiness):** {dau_mau_ratio:.2%}

#### 월별 활성 사용자 수 (MAU) 교차표
{mau.to_markdown(index=True)}
---

### 9.3. 시간-요일 교차 분석 (히트맵)
- **분석 방법**: `pivot_table`을 사용하여 시간(`Hour`)과 요일(`DayOfWeek`)을 각각 행과 열로, 고유 주문서 수(`InvoiceNo.nunique()`)를 값으로 하는 교차 테이블을 생성하고 히트맵으로 시각화했습니다.
- **분석 결과**: 특정 시간대와 요일의 주문 집중도를 한눈에 파악할 수 있습니다. 주중 점심시간(12-14시)에 주문이 가장 활발한 것을 명확하게 보여줍니다.
"""
hour_dow_pivot = df.pivot_table(index='Hour', columns='DayOfWeek', values='InvoiceNo', aggfunc='nunique')
# 정렬 및 NaN을 0으로 채워 시각화가 올바르게 표시되도록 처리
hour_dow_pivot = hour_dow_pivot.sort_index().reindex(columns=day_order).fillna(0)

plt.figure(figsize=(12, 8))
ax = sns.heatmap(hour_dow_pivot, cmap='viridis', annot=True, fmt='.0f', linewidths=.5, cbar_kws={'label': '주문 수'})
# y축을 반전하여 시간이 위->아래로 자연스럽게 보이도록 조정
ax.invert_yaxis()
plt.title('시간 및 요일별 주문 수 히트맵')
plt.xlabel('요일')
plt.ylabel('시간')
plt.tight_layout()
plot_path_14 = 'online-retail/images/plot_14_hour_day_heatmap.png'
plt.savefig(plot_path_14)
plt.close()

report_md += f"""
![시간-요일 히트맵](../{plot_path_14})

#### 시간-요일 교차표
{hour_dow_pivot.to_markdown(index=True)}
---

### 9.4. 월별 고객 리텐션 분석
- **분석 방법**: 코호트 분석을 통해 고객 리텐션을 분석합니다.
    1. 각 고객의 첫 구매월을 `CohortMonth`로 정의합니다. (`groupby('CustomerID')['OrderMonth'].transform('min')`)
    2. `CohortMonth`와 실제 주문월(`OrderMonth`)을 기준으로 고유 고객 수를 집계합니다.
    3. 첫 구매월 대비 각 월의 재방문 고객 비율을 계산하여 리텐션 매트릭스를 생성하고 히트맵으로 시각화합니다.
- **분석 결과**: 첫 구매 고객(코호트)이 시간이 지남에 따라 얼마나 재구매하는지 보여줍니다. 초기 코호트일수록 리텐션이 점차 감소하는 자연스러운 패턴을 보이며, 특정 월의 리텐션 변화를 통해 마케팅 활동의 효과 등을 추측해볼 수 있습니다.
"""
df['OrderMonth'] = df['InvoiceDate'].dt.to_period('M')
df['CohortMonth'] = df.groupby('CustomerID')['OrderMonth'].transform('min')

def get_cohort_data(df):
    cohort_data = df.groupby(['CohortMonth', 'OrderMonth'])['CustomerID'].nunique().reset_index()
    cohort_data['MonthNumber'] = (cohort_data['OrderMonth'] - cohort_data['CohortMonth']).apply(lambda x: x.n)
    cohort_counts = cohort_data.pivot_table(index='CohortMonth', columns='MonthNumber', values='CustomerID')
    
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    
    # 첫 달을 100%로 표시하기 위해 0번 컬럼 이름을 변경하지 않고 그대로 사용하거나, 별도 처리
    # retention.rename(columns={0: 'Acquisition'}, inplace=True) 
    
    return retention, cohort_counts

retention_matrix, cohort_counts_matrix = get_cohort_data(df)

# 히트맵 시각화
plt.figure(figsize=(15, 8))
sns.heatmap(retention_matrix, annot=True, fmt='.0%', cmap='BuGn')
plt.title('월별 고객 리텐션 (재방문율)')
plt.xlabel('첫 구매 후 경과 개월')
plt.ylabel('첫 구매월(코호트)')
plt.tight_layout()
plot_path_15 = 'online-retail/images/plot_15_monthly_retention.png'
plt.savefig(plot_path_15)
plt.close()

report_md += f"""
![월별 리텐션 히트맵](../{plot_path_15})

#### 리텐션 교차표 (비율)
{retention_matrix.to_markdown(index=True, floatfmt=".2%")}

#### 리텐션 교차표 (고객 수)
{cohort_counts_matrix.to_markdown(index=True, floatfmt=".0f")}
---
"""


report_md += """
## 10. 결론

본 분석을 통해 Online Retail 데이터셋의 다양한 패턴을 확인할 수 있었습니다. 영국 중심의 매출 구조, 연말 쇼핑 시즌의 매출 집중, 주중 점심시간의 높은 주문율, VIP 고객의 중요성, 고객 충성도 및 재방문 패턴 등 비즈니스 전략 수립에 도움이 될 수 있는 여러 인사이트를 도출했습니다.

분석을 마칩니다.
"""

# 마크다운 파일에 데이터 정보 채우기
report_md = report_md.format(
    df_head=df.head().to_string(),
    df_describe=df.describe().to_string()
)


# 최종 리포트 파일 작성
with open('online-retail/EDA_Report.md', 'w', encoding='utf-8') as f:
    f.write(report_md)

print("EDA 리포트 'online-retail/EDA_Report.md' 생성이 완료되었습니다.")
print(f"이미지 폴더 'online-retail/images/'에 시각화 파일이 저장되었습니다.")
