import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

def run_eda():
    # 데이터 불러오기
    df = pd.read_csv('./causal-inference/data/wage.csv')

    # 결과 저장을 위한 마크다운 파일 생성
    with open('./causal-inference/EDA_Report.md', 'w', encoding='utf-8') as f:
        f.write("# Wage 데이터셋 EDA 보고서\n\n")
        f.write("이 보고서는 Wage 데이터셋에 대한 탐색적 데이터 분석(EDA) 결과를 요약합니다.\n\n")

        # 데이터 기본 정보
        f.write("## 1. 데이터 기본 정보\n\n")
        f.write("### 처음 5개 행:\n")
        f.write("```\n")
        f.write(df.head().to_string() + '\n')
        f.write("```\n\n")

        f.write("### 데이터 정보:\n")
        # df.info()는 파일에 직접 쓸 수 없으므로, 문자열로 변환하는 트릭을 사용
        import io
        buffer = io.StringIO()
        df.info(buf=buffer)
        f.write("```\n")
        f.write(buffer.getvalue() + '\n')
        f.write("```\n\n")

        f.write("### 기술 통계:\n")
        f.write("```\n")
        f.write(df.describe().to_string() + '\n')
        f.write("```\n\n")

        # 시각화 및 분석
        f.write("## 2. 데이터 시각화 및 분석\n\n")

        # Plot 1: 임금(wage) 분포 (Histogram)
        plt.figure(figsize=(10, 6))
        sns.histplot(df['wage'], kde=True, bins=30)
        plt.title('임금 분포')
        plt.xlabel('임금')
        plt.ylabel('빈도')
        img_path = './causal-inference/images/plot_1_wage_distribution.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.1. 임금 분포\n\n")
        f.write("![임금 분포](./images/plot_1_wage_distribution.png)\n\n")
        f.write("임금 데이터는 오른쪽으로 꼬리가 긴 분포를 보입니다. 대부분의 사람들은 100-150 사이에 분포하지만, 200 이상의 높은 임금을 받는 소수도 존재합니다. 이는 소득 불평등을 시사할 수 있습니다.\n\n")

        # Plot 2: 교육 수준(education) 분포 (Bar chart)
        plt.figure(figsize=(12, 7))
        education_counts = df['education'].value_counts()
        sns.barplot(x=education_counts.index, y=education_counts.values)
        plt.title('교육 수준 분포')
        plt.xlabel('교육 수준')
        plt.ylabel('인원 수')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        img_path = './causal-inference/images/plot_2_education_distribution.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.2. 교육 수준 분포\n\n")
        f.write("![교육 수준 분포](./images/plot_2_education_distribution.png)\n\n")
        f.write("가장 많은 교육 수준은 '2. High School Grad'이며, '4. College Grad'가 그 뒤를 잇습니다. 교육 수준별로 인원 수에 차이가 있으며, 이는 임금 분석에 중요한 변수가 될 수 있습니다.\n\n")
        f.write("#### 교육 수준별 교차표:\n")
        f.write("```\n")
        f.write(pd.crosstab(index=df['education'], columns='count').to_string() + '\n')
        f.write("```\n\n")


        # Plot 3: 결혼 상태(maritl) 분포 (Bar chart)
        plt.figure(figsize=(10, 6))
        maritl_counts = df['maritl'].value_counts()
        sns.barplot(x=maritl_counts.index, y=maritl_counts.values)
        plt.title('결혼 상태 분포')
        plt.xlabel('결혼 상태')
        plt.ylabel('인원 수')
        img_path = './causal-inference/images/plot_3_maritl_distribution.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.3. 결혼 상태 분포\n\n")
        f.write("![결혼 상태 분포](./images/plot_3_maritl_distribution.png)\n\n")
        f.write("'2. Married' 상태의 인원이 가장 많습니다. 결혼 여부가 임금에 영향을 미치는지 확인해볼 필요가 있습니다.\n\n")
        f.write("#### 결혼 상태별 교차표:\n")
        f.write("```\n")
        f.write(pd.crosstab(index=df['maritl'], columns='count').to_string() + '\n')
        f.write("```\n\n")

        # Plot 4: 건강 상태(health) 분포 (Bar chart)
        plt.figure(figsize=(10, 6))
        health_counts = df['health'].value_counts()
        sns.barplot(x=health_counts.index, y=health_counts.values)
        plt.title('건강 상태 분포')
        plt.xlabel('건강 상태')
        plt.ylabel('인원 수')
        img_path = './causal-inference/images/plot_4_health_distribution.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.4. 건강 상태 분포\n\n")
        f.write("![건강 상태 분포](./images/plot_4_health_distribution.png)\n\n")
        f.write("대부분의 사람들이 '1. <=Good' 또는 '2. >=Very Good'의 건강 상태를 가지고 있습니다. 건강 상태가 좋지 않은 사람은 소수입니다.\n\n")
        f.write("#### 건강 상태별 교차표:\n")
        f.write("```\n")
        f.write(pd.crosstab(index=df['health'], columns='count').to_string() + '\n')
        f.write("```\n\n")


        # Plot 5: 교육 수준별 임금 (Boxplot)
        plt.figure(figsize=(14, 8))
        sns.boxplot(x='education', y='wage', data=df)
        plt.title('교육 수준별 임금 분포')
        plt.xlabel('교육 수준')
        plt.ylabel('임금')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        img_path = './causal-inference/images/plot_5_wage_by_education.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.5. 교육 수준별 임금\n\n")
        f.write("![교육 수준별 임금](./images/plot_5_wage_by_education.png)\n\n")
        f.write("전반적으로 교육 수준이 높을수록 임금의 중앙값과 분포가 상승하는 경향을 보입니다. 특히 '5. Advanced Degree'는 다른 그룹에 비해 월등히 높은 임금을 받습니다. 이는 교육이 소득에 긍정적인 영향을 미친다는 가설을 뒷받침합니다.\n\n")


        # Plot 6: 나이(age)와 임금(wage)의 관계 (Scatter plot)
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='age', y='wage', data=df, alpha=0.5)
        sns.regplot(x='age', y='wage', data=df, scatter=False, color='red')
        plt.title('나이와 임금의 관계')
        plt.xlabel('나이')
        plt.ylabel('임금')
        img_path = './causal-inference/images/plot_6_wage_by_age.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.6. 나이와 임금의 관계\n\n")
        f.write("![나이와 임금의 관계](./images/plot_6_wage_by_age.png)\n\n")
        f.write("나이가 많아질수록 임금이 대체로 증가하는 양의 상관관계를 보입니다. 하지만 분산도 함께 커지는 경향이 있어, 나이가 들수록 개인 간의 임금 격차가 벌어질 수 있음을 시사합니다.\n\n")


        # Plot 7: 직업 분야(jobclass)별 임금 (Boxplot)
        plt.figure(figsize=(12, 7))
        sns.boxplot(x='jobclass', y='wage', data=df)
        plt.title('직업 분야별 임금 분포')
        plt.xlabel('직업 분야')
        plt.ylabel('임금')
        img_path = './causal-inference/images/plot_7_wage_by_jobclass.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.7. 직업 분야별 임금\n\n")
        f.write("![직업 분야별 임금](./images/plot_7_wage_by_jobclass.png)\n\n")
        f.write("'2. Information' 분야의 임금이 '1. Industrial' 분야보다 전반적으로 높게 나타납니다. 직업 분야가 임금 수준을 결정하는 중요한 요인 중 하나임을 알 수 있습니다.\n\n")

        # Plot 8: 인종(race)별 임금 (Violin plot)
        plt.figure(figsize=(12, 7))
        sns.violinplot(x='race', y='wage', data=df)
        plt.title('인종별 임금 분포')
        plt.xlabel('인종')
        plt.ylabel('임금')
        img_path = './causal-inference/images/plot_8_wage_by_race.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.8. 인종별 임금\n\n")
        f.write("![인종별 임금](./images/plot_8_wage_by_race.png)\n\n")
        f.write("인종별로 임금 분포에 차이가 보입니다. 특히 '3. Asian'과 '1. White' 그룹의 임금 중앙값이 다른 그룹에 비해 높은 경향이 있습니다. 바이올린 플롯은 각 그룹의 데이터 분포 형태를 보여주는데, 모든 인종 그룹에서 고임금 이상치가 존재함을 알 수 있습니다.\n\n")


        # Plot 9: 수치형 변수 간의 상관관계 (Heatmap)
        plt.figure(figsize=(10, 8))
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('수치형 변수 간의 상관관계')
        plt.tight_layout()
        img_path = './causal-inference/images/plot_9_correlation_heatmap.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.9. 수치형 변수 간의 상관관계\n\n")
        f.write("![상관관계 히트맵](./images/plot_9_correlation_heatmap.png)\n\n")
        f.write("`wage`는 `age`, `year`와 양의 상관관계를, `logwage`와는 매우 강한 양의 상관관계를 가집니다. `age`와 `year`도 약한 양의 상관관계를 보입니다. 이는 시간이 지남에 따라 나이와 임금이 함께 증가하는 경향을 반영합니다.\n\n")


        # Plot 10: 결혼 상태 및 교육 수준에 따른 임금 (Factorplot/catplot)
        g = sns.catplot(x='education', y='wage', hue='maritl', kind='bar', data=df, height=7, aspect=1.8, palette='muted')
        g.fig.suptitle('결혼 상태 및 교육 수준에 따른 임금', y=1.03)
        g.set_xticklabels(rotation=30)
        img_path = './causal-inference/images/plot_10_wage_by_education_maritl.png'
        plt.savefig(img_path)
        plt.close()
        f.write("### 2.10. 결혼 상태 및 교육 수준에 따른 임금\n\n")
        f.write("![결혼 상태 및 교육 수준별 임금](./images/plot_10_wage_by_education_maritl.png)\n\n")
        f.write("대부분의 교육 수준에서 기혼자('2. Married')의 평균 임금이 미혼자('1. Never Married')보다 높은 경향을 보입니다. 이는 결혼 여부가 임금에 긍정적인 영향을 줄 수 있다는 가능성을 제시합니다. 하지만 이는 다른 요인(예: 나이)에 의한 결과일 수도 있으므로 추가 분석이 필요합니다.\n\n")

if __name__ == '__main__':
    # 이미지 저장 디렉토리 생성
    if not os.path.exists('./causal-inference/images'):
        os.makedirs('./causal-inference/images')
    run_eda()

print("EDA 분석이 완료되었으며, 'causal-inference/EDA_Report.md' 파일에 저장되었습니다.")
