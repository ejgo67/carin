
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
departments = pd.read_csv('instacart/departments.csv')
products = pd.read_csv('instacart/products.csv')

# --- Data Exploration ---
print("departments.head():")
print(departments.head())
print("\ndepartments.info():")
departments.info()
print("\ndepartaments.describe():")
print(departments.describe())


# --- Merge DataFrames ---
dept_products = products.merge(departments, on='department_id', how='left')


# --- Analysis & Visualization ---

# 1. Product count per department
plt.figure(figsize=(12, 8))
sns.countplot(y='department', data=dept_products, order = dept_products['department'].value_counts().index)
plt.title('부서별 상품 수')
plt.xlabel('상품 수')
plt.ylabel('부서')
plt.tight_layout()
plt.savefig('instacart/images/plot_dept_product_counts.png')
plt.clf()


# --- Generate EDA Report ---
with open('instacart/departments_EDA_Report.md', 'w', encoding='utf-8') as f:
    f.write('# Instacart 부서 데이터 EDA 분석 보고서\n\n')
    f.write('## 1. 개요\n')
    f.write('이 보고서는 Instacart의 `departments.csv` 데이터셋에 대한 탐색적 데이터 분석(EDA) 결과를 요약합니다.\n\n')

    f.write('## 2. 데이터 미리보기\n')
    f.write('### departments.csv\n')
    f.write(f'```\n{departments.head().to_string()}\n```\n\n')

    f.write('## 3. 분석 결과\n')
    f.write('### 3.1. 부서별 상품 수\n')
    f.write('![부서별 상품 수](images/plot_dept_product_counts.png)\n')
    f.write('- `personal care`, `snacks`, `pantry`, `beverages` 부서가 가장 많은 상품을 보유하고 있습니다.\n')
    f.write('- `bulk` 부서가 가장 적은 상품을 보유하고 있습니다.\n\n')

print("EDA script created at instacart/departments_eda.py")
print("EDA report generated at instacart/departments_EDA_Report.md")
