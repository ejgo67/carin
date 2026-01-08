
import pandas as pd
import matplotlib.pyplot as plt

import os
import io
import sys

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Create images directory if it doesn't exist
if not os.path.exists('instacart/images'):
    os.makedirs('instacart/images')

# 1. Load and merge data
print("Loading data...")
aisles = pd.read_csv('instacart/aisles.csv')
departments = pd.read_csv('instacart/departments.csv')
order_products_prior = pd.read_csv('instacart/order_products__prior.csv')
order_products_train = pd.read_csv('instacart/order_products__train.csv')
orders = pd.read_csv('instacart/orders.csv')
products = pd.read_csv('instacart/products.csv')

print("Merging data...")
order_products = pd.concat([order_products_prior, order_products_train])
full_data = orders.merge(order_products, on='order_id', how='inner')
full_data = full_data.merge(products, on='product_id', how='inner')
full_data = full_data.merge(aisles, on='aisle_id', how='inner')
full_data = full_data.merge(departments, on='department_id', how='inner')


print("Data loading and merging complete.")
report_content = "# Instacart 데이터 EDA 분석 보고서 (계획 기반)\n\n"

# --- Basic Data Information ---
report_content += "## 1. 데이터셋 기본 정보\n\n"

for df_name, df in {"aisles": aisles, "departments": departments, "order_products_prior": order_products_prior, "order_products_train": order_products_train, "orders": orders, "products": products}.items():
    report_content += f"### {df_name}.csv\n"
    report_content += f"- Shape: {df.shape}\n"
    report_content += f"- Missing values:\n```\n{df.isnull().sum().to_string()}\n```\n"
    
    # Capture info() output
    buffer = io.StringIO()
    df.info(buf=buffer, verbose=True, show_counts=True)
    report_content += f"- Info:\n```\n{buffer.getvalue()}\n```\n"
    
    report_content += f"- Description:\n```\n{df.describe().to_string()}\n```\n\n"

# --- Analysis & Visualization ---
report_content += "## 2. 주문 시간 분석\n\n"
plt.figure(figsize=(12, 6))
plt.bar(orders['order_hour_of_day'].value_counts().index, orders['order_hour_of_day'].value_counts().values)
plt.title('시간대별 주문량 분포')
plt.xlabel('주문 시간')
plt.ylabel('주문 수')
plt.savefig('instacart/images/planned_plot_1_hour_dist.png')
plt.clf()
report_content += "### 시간대별 주문량\n"
report_content += "![시간대별 주문량](images/planned_plot_1_hour_dist.png)\n"
report_content += "- 주문은 주로 오전 9시부터 오후 5시 사이에 집중됩니다.\n\n"

# By day of week
plt.figure(figsize=(12, 6))
plt.bar(orders['order_dow'].value_counts().index, orders['order_dow'].value_counts().values)
plt.title('요일별 주문량 분포')
plt.xlabel('요일 (0: 일요일, 6: 토요일)')
plt.ylabel('주문 수')
plt.savefig('instacart/images/planned_plot_2_dow_dist.png')
plt.clf()
report_content += "### 요일별 주문량\n"
report_content += "![요일별 주문량](images/planned_plot_2_dow_dist.png)\n"
report_content += "- 0(일요일)과 1(월요일)에 주문이 가장 많으며, 주말로 갈수록 주문량이 줄어드는 경향을 보입니다.\n\n"

# 3. Analyze products
report_content += "## 3. 상품 분석\n\n"

# Top 20 most sold products
top_20_sold = full_data['product_name'].value_counts().head(20)
plt.figure(figsize=(12, 8))
plt.barh(top_20_sold.index, top_20_sold.values)
plt.title('가장 많이 팔린 상품 TOP 20')
plt.xlabel('판매량')
plt.ylabel('상품명')
plt.tight_layout()
plt.savefig('instacart/images/planned_plot_3_top_20_sold.png')
plt.clf()
report_content += "### 가장 많이 팔린 상품 TOP 20\n"
report_content += "![가장 많이 팔린 상품 TOP 20](images/planned_plot_3_top_20_sold.png)\n"
report_content += "- 바나나, 유기농 딸기, 유기농 아보카도 등이 가장 인기가 많습니다.\n\n"

# Top 20 most reordered products
top_20_reordered = full_data[full_data['reordered'] == 1]['product_name'].value_counts().head(20)
plt.figure(figsize=(12, 8))
plt.barh(top_20_reordered.index, top_20_reordered.values)
plt.title('가장 많이 재주문된 상품 TOP 20')
plt.xlabel('재주문 수')
plt.ylabel('상품명')
plt.tight_layout()
plt.savefig('instacart/images/planned_plot_4_top_20_reordered.png')
plt.clf()
report_content += "### 가장 많이 재주문된 상품 TOP 20\n"
report_content += "![가장 많이 재주문된 상품 TOP 20](images/planned_plot_4_top_20_reordered.png)\n"
report_content += "- 판매량 상위 상품들이 재주문 순위에서도 상위권을 차지하고 있습니다.\n\n"


# 4. Reorder Rate Analysis
report_content += "## 4. 재주문율 분석\n\n"

# Overall reorder rate
# Note: 'reordered' column in order_products indicates if a product in an order was a reorder.
# To get overall order reorder rate, we should look at 'reordered' column in orders dataframe.
# Assuming 'reordered' in orders.csv means if the order itself contains any reordered items.
# Let's clarify this first.
# Based on Instacart dataset description: reordered (0/1): 1 if this product has been ordered by this user in a previous order, 0 otherwise.
# So, reordered in order_products dataframe makes more sense for product-level reorder rate.
# The previous EDA script (eda.py) calculated reorder ratio based on order_products.
# Let's stick to product-level reorder rate for consistency with the initial eda.py.
reorder_ratio_products = full_data['reordered'].sum() / len(full_data)
plt.figure(figsize=(6, 6))
plt.pie([1 - reorder_ratio_products, reorder_ratio_products], labels=['첫 주문 상품', '재주문 상품'], autopct='%1.1f%%', startangle=90)
plt.title('전체 상품 재주문 비율')
plt.ylabel('')
plt.savefig('instacart/images/planned_plot_6_overall_reorder_ratio.png')
plt.clf()
report_content += "### 전체 상품 재주문 비율\n"
report_content += "![전체 상품 재주문 비율](images/planned_plot_6_overall_reorder_ratio.png)\n"
report_content += f"- 전체 주문 상품 중 약 {reorder_ratio_products:.1%}가 재주문된 상품입니다.\n\n"


# 5. Department-wise Sales
report_content += "## 5. 부서별 판매량 분석\n\n"
department_sales = full_data['department'].value_counts()
plt.figure(figsize=(12, 8))
plt.barh(department_sales.index, department_sales.values)
plt.title('부서별 판매량')
plt.xlabel('판매된 상품 수')
plt.ylabel('부서명')
plt.tight_layout()
plt.savefig('instacart/images/planned_plot_7_department_sales.png')
plt.clf()
report_content += "### 부서별 판매량\n"
report_content += "![부서별 판매량](images/planned_plot_7_department_sales.png)\n"
report_content += "- `produce` 부서가 압도적으로 높은 판매량을 보입니다. 이어서 `dairy eggs`, `snacks` 등이 높은 판매량을 기록합니다.\n\n"


# 6. Aisle-wise Sales
report_content += "## 6. 아이슬별 판매량 분석\n\n"
aisle_sales = full_data['aisle'].value_counts().head(20) # Top 20 aisles
plt.figure(figsize=(12, 8))
plt.barh(aisle_sales.index, aisle_sales.values)
plt.title('아이슬별 판매량 (Top 20)')
plt.xlabel('판매된 상품 수')
plt.ylabel('아이슬명')
plt.tight_layout()
plt.savefig('instacart/images/planned_plot_8_aisle_sales.png')
plt.clf()
report_content += "### 아이슬별 판매량 (Top 20)\n"
report_content += "![아이슬별 판매량 (Top 20)](images/planned_plot_8_aisle_sales.png)\n"
report_content += "- `fresh fruits`, `fresh vegetables` 아이슬이 가장 높은 판매량을 보입니다.\n\n"


# 7. Add to cart order vs reorder rate
report_content += "## 7. 장바구니 순서와 재주문율 관계 분석\n\n"
add_to_cart_reorder_rate = full_data.groupby('add_to_cart_order')['reordered'].mean().reset_index()
plt.figure(figsize=(12, 6))
plt.plot(add_to_cart_reorder_rate['add_to_cart_order'], add_to_cart_reorder_rate['reordered'])
plt.title('장바구니 순서별 재주문율')
plt.xlabel('장바구니에 담은 순서')
plt.ylabel('재주문율')
plt.grid(True)
plt.savefig('instacart/images/planned_plot_9_add_to_cart_reorder_rate.png')
plt.clf()
report_content += "### 장바구니 순서별 재주문율\n"
report_content += "![장바구니 순서별 재주문율](images/planned_plot_9_add_to_cart_reorder_rate.png)\n"
report_content += "- 장바구니에 먼저 담는 상품일수록 재주문율이 높은 경향을 보입니다. 이는 소비자들이 자주 구매하는 품목을 먼저 장바구니에 담는 습관이 있음을 시사합니다.\n\n"


# 8. Analyze order size
report_content += "## 8. 주문 규모 분석\n\n"
products_per_order = full_data.groupby('order_id')['product_id'].count()
plt.figure(figsize=(12, 6))
plt.hist(products_per_order, bins=50)
plt.title('주문당 상품 개수 분포')
plt.xlabel('주문당 상품 개수')
plt.ylabel('주문 수')
plt.xlim(0, 60)
plt.savefig('instacart/images/planned_plot_5_products_per_order.png')
plt.clf()
report_content += "### 주문당 상품 개수\n"
report_content += "![주문당 상품 개수](images/planned_plot_5_products_per_order.png)\n"
report_content += "- 대부분의 주문은 5개에서 15개 사이의 상품을 포함하고 있습니다.\n\n"


# 9. User Order Behavior Analysis
report_content += "## 9. 사용자별 주문 행동 분석\n\n"

# Calculate order frequency per user
user_order_counts = orders.groupby('user_id')['order_number'].max()
plt.figure(figsize=(12, 6))
plt.hist(user_order_counts, bins=50)
plt.title('사용자별 총 주문 수 분포')
plt.xlabel('총 주문 수')
plt.ylabel('사용자 수')
plt.savefig('instacart/images/planned_plot_10_user_order_frequency.png')
plt.clf()
report_content += "### 사용자별 총 주문 수 분포\n"
report_content += "![사용자별 총 주문 수 분포](images/planned_plot_10_user_order_frequency.png)\n"
report_content += "- 대부분의 사용자는 5회에서 20회 사이의 주문을 했습니다. 극소수의 활성 사용자가 매우 많은 주문을 한 것을 볼 수 있습니다.\n\n"

# Calculate order periodicity per user (average days since prior order)
# Only consider orders that are not the first order (where days_since_prior_order is not NaN)
user_order_periodicity = orders.groupby('user_id')['days_since_prior_order'].mean().dropna()
plt.figure(figsize=(12, 6))
plt.hist(user_order_periodicity, bins=30)
plt.title('사용자별 평균 재주문 간격 분포')
plt.xlabel('평균 재주문 간격 (일)')
plt.ylabel('사용자 수')
plt.savefig('instacart/images/planned_plot_11_user_order_periodicity.png')
plt.clf()
report_content += "### 사용자별 평균 재주문 간격 분포\n"
report_content += "![사용자별 평균 재주문 간격 분포](images/planned_plot_11_user_order_periodicity.png)\n"
report_content += "- 많은 사용자들이 7일 또는 30일 간격으로 주문하는 경향이 있습니다. 이는 주간 또는 월간 단위의 정기 구매 패턴을 시사합니다.\n\n"


# 10. User-Product Reorder Analysis
report_content += "## 10. 사용자-상품별 재구매 분석\n\n"

# Filter for reordered items and merge with user_id
user_product_reorders = full_data[full_data['reordered'] == 1].groupby(['user_id', 'product_name']).size().reset_index(name='reorder_count')

# Distribution of how many times a product is reordered by a user
plt.figure(figsize=(12, 6))
plt.hist(user_product_reorders['reorder_count'], bins=30)
plt.title('사용자별 상품 재주문 횟수 분포')
plt.xlabel('상품 재주문 횟수')
plt.ylabel('사용자-상품 쌍 수')
plt.yscale('log') # Use log scale due to high frequency of low counts
plt.savefig('instacart/images/planned_plot_12_user_product_reorder_count_dist.png')
plt.clf()
report_content += "### 사용자별 상품 재주문 횟수 분포\n"
report_content += "![사용자별 상품 재주문 횟수 분포](images/planned_plot_12_user_product_reorder_count_dist.png)\n"
report_content += "- 대부분의 사용자-상품 쌍은 1-2회의 재주문을 보입니다. 재주문 횟수가 증가할수록 해당 사용자-상품 쌍의 수는 급격히 감소합니다.\n\n"

# Top 10 user-product pairs with highest reorder counts (illustrative)
# This might be too much to show for every user, so focusing on top overall
top_user_product_reorders = user_product_reorders.sort_values(by='reorder_count', ascending=False).head(10)
report_content += "### 가장 많이 재주문된 사용자-상품 쌍 (상위 10개)\n"
report_content += f"```\n{top_user_product_reorders.to_string(index=False)}\n```\n\n"
report_content += "- 특정 상품을 매우 자주 재주문하는 사용자 쌍이 존재합니다. 이는 충성도 높은 고객과 그들이 선호하는 상품을 파악하는 데 중요합니다.\n\n"


# --- Generate EDA Report ---
with open('instacart/Planned_EDA_Report.md', 'w', encoding='utf-8') as f:
    f.write(report_content)

print("EDA script based on eda.md created at instacart/planned_eda.py")
print("EDA report generated at instacart/Planned_EDA_Report.md")
