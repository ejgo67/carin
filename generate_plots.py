# generate_plots.py
# 간단 실행 스크립트: seaborn 내장 penguins 데이터로 3개 플롯 생성
import matplotlib
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

print('Loading penguins dataset...')
df = sns.load_dataset('penguins')
print('Loaded shape:', df.shape)

# Plot 1: histograms (body_mass_g, flipper_length_mm)
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
df['body_mass_g'].dropna().hist(bins=25, color='steelblue', edgecolor='black')
plt.xlabel('체질량 (g)')
plt.ylabel('빈도')
plt.title('펭귄 체질량 분포')

plt.subplot(1, 2, 2)
df['flipper_length_mm'].dropna().hist(bins=25, color='coral', edgecolor='black')
plt.xlabel('지느러미 길이 (mm)')
plt.ylabel('빈도')
plt.title('펭귄 지느러미 길이 분포')

plt.tight_layout()
plt.savefig('plot_1_histogram.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved plot_1_histogram.png')

# Plot 2: scatter (bill_length_mm vs bill_depth_mm)
plt.figure(figsize=(10, 6))
species_colors = {'Adelie': 'C0', 'Chinstrap': 'C1', 'Gentoo': 'C2'}
for species in df['species'].dropna().unique():
    mask = df['species'] == species
    plt.scatter(df[mask]['bill_length_mm'], df[mask]['bill_depth_mm'], label=species, alpha=0.7, s=60, color=species_colors.get(species))
plt.xlabel('부리 길이 (mm)')
plt.ylabel('부리 깊이 (mm)')
plt.title('부리 길이 vs 깊이 (종별)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('plot_2_scatter.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved plot_2_scatter.png')

# Plot 3: boxplots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
species_list = df['species'].dropna().unique()
flipper_by_species = [df[df['species'] == sp]['flipper_length_mm'].dropna() for sp in species_list]
axes[0].boxplot(flipper_by_species, labels=species_list)
axes[0].set_xlabel('펭귄 종')
axes[0].set_ylabel('지느러미 길이 (mm)')
axes[0].set_title('종별 지느러미 길이 분포')
axes[0].grid(True, alpha=0.3)

sex_list = df['sex'].dropna().unique()
mass_by_sex = [df[df['sex'] == s]['body_mass_g'].dropna() for s in sex_list]
axes[1].boxplot(mass_by_sex, labels=sex_list)
axes[1].set_xlabel('성별')
axes[1].set_ylabel('체질량 (g)')
axes[1].set_title('성별 체질량 분포')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plot_3_boxplot.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved plot_3_boxplot.png')

print('All plots generated.')
