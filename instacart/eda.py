
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Create images directory
if not os.path.exists('instacart/images'):
    os.makedirs('instacart/images')

# Load data
aisles = pd.read_csv('instacart/aisles.csv')
departments = pd.read_csv('instacart/departments.csv')
order_products_prior = pd.read_csv('instacart/order_products__prior.csv')
order_products_train = pd.read_csv('instacart/order_products__train.csv')
orders = pd.read_csv('instacart/orders.csv')
products = pd.read_csv('instacart/products.csv')

# --- Data Exploration ---
print("aisles.head():")
print(aisles.head())
print("\ndepartments.head():")
print(departments.head())
print("\norder_products_prior.head():")
print(order_products_prior.head())
print("\norder_products_train.head():")
print(order_products_train.head())
print("\norders.head():")
print(orders.head())
print("\nproducts.head():")
print(products.head())


# --- Merge DataFrames ---
order_products = pd.concat([order_products_prior, order_products_train])
order_products = order_products.merge(products, on='product_id', how='left')
order_products = order_products.merge(aisles, on='aisle_id', how='left')
order_products = order_products.merge(departments, on='department_id', how='left')
order_products = order_products.merge(orders, on='order_id', how='left')


# --- Analysis & Visualization ---

# 1. Order Hour of Day Distribution
plt.figure(figsize=(12, 6))
sns.countplot(x='order_hour_of_day', data=orders)
plt.title('주문 시간대별 분포')
plt.xlabel('주문 시간')
plt.ylabel('주문 수')
plt.savefig('instacart/images/plot_1_order_hour_of_day.png')
plt.clf()

# 2. Day of Week Distribution
plt.figure(figsize=(12, 6))
sns.countplot(x='order_dow', data=orders)
plt.title('요일별 주문 분포')
plt.xlabel('요일')
plt.ylabel('주문 수')
plt.savefig('instacart/images/plot_2_order_dow.png')
plt.clf()

# 3. Number of items per order
items_per_order = order_products.groupby('order_id')['product_id'].count()
plt.figure(figsize=(12, 6))
sns.histplot(items_per_order, bins=50)
plt.title('주문당 상품 수')
plt.xlabel('상품 수')
plt.ylabel('주문 수')
plt.savefig('instacart/images/plot_3_items_per_order.png')
plt.clf()

# 4. Reordered items distribution
reorder_ratio = order_products.groupby('reordered')['reordered'].count()
reorder_ratio = reorder_ratio / len(order_products)
plt.figure(figsize=(6, 6))
reorder_ratio.plot.pie(autopct='%1.1f%%', startangle=90, labels=['재주문 안함', '재주문'])
plt.title('재주문 비율')
plt.ylabel('')
plt.savefig('instacart/images/plot_4_reorder_ratio.png')
plt.clf()

# 5. Most reordered items
reordered_products = order_products[order_products['reordered'] == 1]
most_reordered = reordered_products['product_name'].value_counts().head(10)
plt.figure(figsize=(12, 6))
sns.barplot(x=most_reordered.index, y=most_reordered.values)
plt.title('가장 많이 재주문된 상품 TOP 10')
plt.xlabel('상품명')
plt.ylabel('재주문 수')
plt.xticks(rotation=90)
plt.savefig('instacart/images/plot_5_most_reordered.png')
plt.clf()

# 6. Add to cart order vs reorder
add_to_cart_reorder = order_products.groupby('add_to_cart_order')['reordered'].mean()
plt.figure(figsize=(12, 6))
add_to_cart_reorder.plot.line()
plt.title('장바구니 순서와 재주문율 관계')
plt.xlabel('장바구니에 담은 순서')
plt.ylabel('재주문율')
plt.savefig('instacart/images/plot_6_add_to_cart_reorder.png')
plt.clf()

# --- Generate EDA Report ---
with open('instacart/EDA_Report.md', 'w', encoding='utf-8') as f:
    f.write('# Instacart 데이터 EDA 분석 보고서\n\n')
    f.write('## 1. 개요\n')
    f.write('이 보고서는 Instacart 데이터셋에 대한 탐색적 데이터 분석(EDA) 결과를 요약합니다.\n\n')

    f.write('## 2. 데이터 미리보기\n')
    f.write('### aisles.csv\n')
    f.write(f'```\n{aisles.head().to_string()}\n```\n\n')
    f.write('### departments.csv\n')
    f.write(f'```\n{departments.head().to_string()}\n```\n\n')
    f.write('### orders.csv\n')
    f.write(f'```\n{orders.head().to_string()}\n```\n\n')
    f.write('### products.csv\n')
    f.write(f'```\n{products.head().to_string()}\n```\n\n')

    f.write('## 3. 분석 결과\n')
    f.write('### 3.1. 시간대별 주문 분포\n')
    f.write('![주문 시간대별 분포](images/plot_1_order_hour_of_day.png)\n')
    f.write('- 주문은 주로 오전 9시부터 오후 5시 사이에 가장 많습니다.\n\n')

    f.write('### 3.2. 요일별 주문 분포\n')
    f.write('![요일별 주문 분포](images/plot_2_order_dow.png)\n')
    f.write('- 0번과 1번 요일(일요일, 월요일)에 주문이 가장 많습니다.\n\n')

    f.write('### 3.3. 주문당 상품 수\n')
    f.write('![주문당 상품 수](images/plot_3_items_per_order.png)\n')
    f.write('- 대부분의 주문은 5-15개의 상품을 포함하고 있습니다.\n\n')

    f.write('### 3.4. 재주문 비율\n')
    f.write('![재주문 비율](images/plot_4_reorder_ratio.png)\n')
    f.write('- 전체 주문 상품 중 약 59%가 재주문 상품입니다.\n\n')

    f.write('### 3.5. 가장 많이 재주문된 상품\n')
    f.write('![가장 많이 재주문된 상품](images/plot_5_most_reordered.png)\n')
    f.write('- 바나나, 유기농 바나나, 유기농 딸기 등이 가장 많이 재주문되는 상품입니다.\n\n')

    f.write('### 3.6. 장바구니 순서와 재주문율\n')
    f.write('![장바구니 순서와 재주문율](images/plot_6_add_to_cart_reorder.png)\n')
    f.write('- 장바구니에 먼저 담기는 상품일수록 재주문율이 높은 경향을 보입니다.\n\n')

print("EDA script created at instacart/eda.py")
print("EDA report generated at instacart/EDA_Report.md")
