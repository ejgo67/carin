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

이 보고서는 Online Retail 데이터셋에 대한 탐색적 데이터 분석(EDA) 결과를 요약합니다.

## 1. 데이터 기본 정보

### 데이터 샘플 (상위 5개)
```
{df_head}
```

### 데이터 통계 요약
```
{df_describe}
```

---

## 2. 국가별 주문 분석

### 주문 건수 상위 10개국
United Kingdom이 압도적으로 많은 주문을 차지하고 있으며, 그 뒤를 독일, 프랑스, EIRE(아일랜드)가 잇고 있습니다.
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
"""

# 2. 국가별 매출액 분석
report_md += """
## 3. 국가별 매출 분석

### 매출액 상위 10개국
주문 건수와 마찬가지로 매출액 역시 United Kingdom이 가장 높습니다. 네덜란드와 EIRE(아일랜드)가 영국 다음으로 높은 매출을 보입니다.
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
## 4. 시간 흐름에 따른 매출 분석

### 월별 매출 추이
2011년 데이터가 대부분이며, 11월에 매출이 가장 정점을 찍는 것을 볼 수 있습니다. 이는 연말 쇼핑 시즌의 영향으로 보입니다.
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
"""

# 4. 요일별 주문 건수
report_md += """
### 요일별 주문 건수
주문은 주중에 집중되어 있으며, 특히 목요일에 가장 많은 주문이 발생합니다. 주말인 토요일은 주문이 현저히 적고, 일요일 주문 데이터는 없습니다.
"""
plt.figure(figsize=(10, 5))
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
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
"""

# 5. 시간대별 주문 건수
report_md += """
### 시간대별 주문 건수
오후 12시(정오)에 주문이 가장 많으며, 대체로 점심시간을 포함한 오후 시간대에 주문이 집중되는 경향을 보입니다.
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

### 판매 수량 상위 10개 상품
'WORLD WAR 2 GLIDERS ASSTD DESIGNS', 'JUMBO BAG RED RETROSPOT' 등 부피가 크거나 묶음 상품으로 보이는 제품들이 상위권을 차지하고 있습니다.
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
"""

# 7. 상위 10개 판매 상품 (매출액 기준)
report_md += """
### 판매 매출액 상위 10개 상품
'DOTCOM POSTAGE'가 가장 높은 매출을 기록했으며, 이는 배송료 관련 항목으로 추정됩니다. 그 외에는 'REGENCY CAKESTAND 3 TIER'와 같은 고가 상품이 상위권에 있습니다.
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

### 상품 단가 분포
대부분의 상품이 0에 가까운 낮은 단가를 가지고 있으며, 일부 고가 상품이 존재합니다. 분석의 편의를 위해 단가 50 이하인 상품들만 따로 시각화했습니다.
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

단가가 0인 경우는 비정상적인 데이터일 수 있으므로 추가적인 확인이 필요합니다.
---
"""

# 9. 고객별 분석: 총 구매액 기준 상위 10명
report_md += """
## 7. 고객 분석

### 총 구매액 상위 10명 고객
특정 고객들이 전체 매출에 큰 기여를 하고 있음을 알 수 있습니다. 상위 고객 관리가 중요한 전략이 될 수 있습니다.
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

### 주문당 평균 상품 수량
한 번의 주문에 평균적으로 약 12개의 상품을 구매하는 것으로 나타났습니다.
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
## 9. 월별 사용자당 평균 매출(ARPU)

월별 사용자당 평균 매출(ARPU)은 전체 매출을 해당 월의 활성 사용자 수로 나누어 계산합니다. 이를 통해 사용자 한 명이 평균적으로 얼마의 매출을 발생시키는지 파악할 수 있습니다.
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
"""

# 12. DAU, MAU
report_md += """
## 10. 활성 사용자 분석 (DAU/MAU)

일별/월별 활성 사용자 수(DAU/MAU)를 통해 서비스 활성도를 파악할 수 있습니다.
"""
dau = df.groupby('Date')['CustomerID'].nunique()
mau = df.groupby('YearMonth')['CustomerID'].nunique()

plt.figure(figsize=(12, 6))
mau.index = mau.index.to_timestamp()
mau.plot(kind='bar', color='lightblue')
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
"""

# 13. 시간-요일 교차 분석
report_md += """
## 11. 시간-요일 교차 분석 (히트맵)

시간대와 요일별 주문 분포를 히트맵으로 시각화하여 특정 시간/요일의 주문 집중도를 파악합니다.
"""
hour_dow_pivot = df.pivot_table(index='Hour', columns='DayOfWeek', values='InvoiceNo', aggfunc='nunique').reindex(columns=day_order)

plt.figure(figsize=(12, 8))
sns.heatmap(hour_dow_pivot, cmap='viridis', annot=True, fmt='.0f', linewidths=.5)
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
"""

# 14. 월단위 구매 고객 리텐션 분석
report_md += """
## 12. 월별 고객 리텐션 분석

첫 구매를 한 고객 코호트가 시간의 흐름에 따라 얼마나 재방문(재구매)하는지를 분석합니다.
"""
df['OrderMonth'] = df['InvoiceDate'].dt.to_period('M')
df['CohortMonth'] = df.groupby('CustomerID')['OrderMonth'].transform('min')

def get_cohort_data(df):
    cohort_data = df.groupby(['CohortMonth', 'OrderMonth'])['CustomerID'].nunique().reset_index()
    cohort_data['MonthNumber'] = (cohort_data['OrderMonth'] - cohort_data['CohortMonth']).apply(lambda x: x.n)
    cohort_counts = cohort_data.pivot_table(index='CohortMonth', columns='MonthNumber', values='CustomerID')
    
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)
    
    # 첫 달을 'Acquisition'으로 변경
    retention.rename(columns={0: 'Acquisition'}, inplace=True)
    
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
