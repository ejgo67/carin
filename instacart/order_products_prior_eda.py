
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Create images directory if it doesn't exist
if not os.path.exists('instacart/images'):
    os.makedirs('instacart/images')

# Load data
order_products_prior = pd.read_csv('instacart/order_products__prior.csv')

# --- Data Exploration ---
print("order_products_prior.head():")
print(order_products_prior.head())
print("\norder_products_prior.info():")
order_products_prior.info()
print("\norder_products_prior.describe():")
print(order_products_prior.describe())


# --- Analysis & Visualization ---

# 1. Reorder Rate
reorder_rate = order_products_prior['reordered'].mean()
plt.figure(figsize=(6, 6))
plt.pie([1 - reorder_rate, reorder_rate], labels=['첫 주문', '재주문'], autopct='%1.1f%%', startangle=90)
plt.title('재주문 비율')
plt.savefig('instacart/images/plot_prior_reorder_rate.png')
plt.clf()

# 2. Add to Cart Order Distribution
plt.figure(figsize=(12, 6))
sns.histplot(order_products_prior['add_to_cart_order'], bins=100)
plt.title('장바구니에 담은 순서 분포')
plt.xlabel('장바구니에 담은 순서')
plt.ylabel('빈도')
plt.xlim(0, 40)
plt.savefig('instacart/images/plot_prior_add_to_cart_order_dist.png')
plt.clf()

# 3. Reorder Rate by Add to Cart Order
reorder_rate_by_cart_order = order_products_prior.groupby('add_to_cart_order')['reordered'].mean().reset_index()
plt.figure(figsize=(12, 6))
sns.lineplot(x='add_to_cart_order', y='reordered', data=reorder_rate_by_cart_order)
plt.title('장바구니 순서별 재주문율')
plt.xlabel('장바구니에 담은 순서')
plt.ylabel('재주문율')
plt.grid(True)
plt.savefig('instacart/images/plot_prior_reorder_rate_by_cart_order.png')
plt.clf()


# --- Generate EDA Report ---
with open('instacart/order_products_prior_EDA_Report.md', 'w', encoding='utf-8') as f:
    f.write('# Instacart 이전 주문 상품 데이터 EDA 분석 보고서\n\n')
    f.write('## 1. 개요\n')
    f.write('이 보고서는 Instacart의 `order_products__prior.csv` 데이터셋에 대한 탐색적 데이터 분석(EDA) 결과를 요약합니다.\n')
    f.write('이 데이터는 고객의 이전 주문 내역을 담고 있습니다.\n\n')

    f.write('## 2. 데이터 미리보기\n')
    f.write('### order_products__prior.csv\n')
    f.write(f'```\n{order_products_prior.head().to_string()}\n```\n\n')

    f.write('## 3. 분석 결과\n')
    f.write('### 3.1. 재주문 비율\n')
    f.write('![재주문 비율](images/plot_prior_reorder_rate.png)\n')
    f.write(f'- 이전 주문 상품 중 약 {reorder_rate:.1%}가 재주문된 상품입니다.\n\n')

    f.write('### 3.2. 장바구니에 담은 순서 분포\n')
    f.write('![장바구니에 담은 순서 분포](images/plot_prior_add_to_cart_order_dist.png)\n')
    f.write('- 상품들은 대부분 장바구니 앞 순서에 담기는 경향이 있습니다.\n\n')

    f.write('### 3.3. 장바구니 순서별 재주문율\n')
    f.write('![장바구니 순서별 재주문율](images/plot_prior_reorder_rate_by_cart_order.png)\n')
    f.write('- 장바구니에 먼저 담기는 상품일수록 재주문율이 높게 나타납니다.\n')
    f.write('- 이는 고객들이 자주 구매하는 상품을 장바구니에 먼저 담는 경향이 있음을 시사합니다.\n\n')

print("EDA script created at instacart/order_products_prior_eda.py")
print("EDA report generated at instacart/order_products_prior_EDA_Report.md")

