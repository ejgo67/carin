
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib import font_manager, rc

# 한글 폰트 설정
font_path = "c:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

# 데이터가 있는 폴더 경로
data_path = 'uci/'
images_path = 'uci/images/'

# 이미지 저장 폴더 생성
if not os.path.exists(images_path):
    os.makedirs(images_path)

# 데이터 로드
try:
    events_df = pd.read_csv(os.path.join(data_path, 'events.csv'))
    category_tree_df = pd.read_csv(os.path.join(data_path, 'category_tree.csv'))
    item_props_df1 = pd.read_csv(os.path.join(data_path, 'item_properties_part1.csv'))
    item_props_df2 = pd.read_csv(os.path.join(data_path, 'item_properties_part2.csv'))
except FileNotFoundError as e:
    print(f"오류: {e}. 'uci' 폴더에 필요한 CSV 파일이 있는지 확인하세요.")
    exit()

# item_properties 데이터 합치기
item_props_df = pd.concat([item_props_df1, item_props_df2], ignore_index=True)

# 리포트 생성을 위한 리스트
report_content = ["# UCI 데이터셋 EDA 보고서"]

# --- 1. 데이터 개요 ---
report_content.append("## 1. 데이터 개요")

# Events 데이터
report_content.append("### 1.1. Events 데이터")
report_content.append(f"- 전체 레코드 수: {len(events_df)}")
report_content.append(f"- 전체 방문자 수: {events_df['visitorid'].nunique()}")
report_content.append(f"- 전체 아이템 수: {events_df['itemid'].nunique()}")
report_content.append("\n**데이터 샘플:**")
report_content.append(events_df.head().to_markdown(index=False))
report_content.append("\n**데이터 정보:**")
report_content.append("```")
events_df.info(buf=open('temp_info.txt', 'w+'))
with open('temp_info.txt', 'r') as f:
    report_content.append(f.read())
report_content.append("```")

# Item Properties 데이터
report_content.append("\n### 1.2. Item Properties 데이터")
report_content.append(f"- 전체 레코드 수: {len(item_props_df)}")
report_content.append(f"- 전체 아이템 수: {item_props_df['itemid'].nunique()}")
report_content.append("\n**데이터 샘플:**")
report_content.append(item_props_df.head().to_markdown(index=False))
report_content.append("\n**데이터 정보:**")
report_content.append("```")
item_props_df.info(buf=open('temp_info.txt', 'w+'))
with open('temp_info.txt', 'r') as f:
    report_content.append(f.read())
report_content.append("```")


# Category Tree 데이터
report_content.append("\n### 1.3. Category Tree 데이터")
report_content.append(f"- 전체 레코드 수: {len(category_tree_df)}")
report_content.append(f"- 전체 카테고리 수: {category_tree_df['categoryid'].nunique()}")
report_content.append("\n**데이터 샘플:**")
report_content.append(category_tree_df.head().to_markdown(index=False))

# --- 2. Events 데이터 분석 ---
report_content.append("\n## 2. Events 데이터 분석")

# Plot 1: 이벤트 유형별 분포
report_content.append("\n### 2.1. 이벤트 유형별 분포")
plt.figure(figsize=(10, 6))
event_counts = events_df['event'].value_counts()
event_counts.plot(kind='bar', color=['skyblue', 'salmon', 'lightgreen'])
plt.title('이벤트 유형별 발생 횟수', fontsize=16)
plt.xlabel('이벤트 유형', fontsize=12)
plt.ylabel('횟수', fontsize=12)
plt.xticks(rotation=0)
plt.tight_layout()
plot_path = os.path.join(images_path, 'plot_1_event_distribution.png')
plt.savefig(plot_path)
plt.close()
report_content.append(f"\n![이벤트 유형별 분포]({plot_path})")
report_content.append("\n**교차표:**")
report_content.append(event_counts.to_frame().to_markdown())


# Plot 2: 가장 많이 본 아이템 Top 20
report_content.append("\n### 2.2. 가장 많이 본 아이템 Top 20")
top_20_viewed_items = events_df[events_df['event'] == 'view'].groupby('itemid').size().nlargest(20)
plt.figure(figsize=(12, 8))
top_20_viewed_items.sort_values().plot(kind='barh', color='c')
plt.title('가장 많이 본 아이템 Top 20', fontsize=16)
plt.xlabel('조회수', fontsize=12)
plt.ylabel('아이템 ID', fontsize=12)
plt.tight_layout()
plot_path = os.path.join(images_path, 'plot_2_top_20_viewed_items.png')
plt.savefig(plot_path)
plt.close()
report_content.append(f"\n![가장 많이 본 아이템 Top 20]({plot_path})")
report_content.append("\n**데이터:**")
report_content.append(top_20_viewed_items.to_frame('조회수').to_markdown())

# Plot 3: 가장 많이 장바구니에 담은 아이템 Top 20
report_content.append("\n### 2.3. 가장 많이 장바구니에 담은 아이템 Top 20")
top_20_added_items = events_df[events_df['event'] == 'addtocart'].groupby('itemid').size().nlargest(20)
plt.figure(figsize=(12, 8))
top_20_added_items.sort_values().plot(kind='barh', color='b')
plt.title('가장 많이 장바구니에 담은 아이템 Top 20', fontsize=16)
plt.xlabel('장바구니에 담은 횟수', fontsize=12)
plt.ylabel('아이템 ID', fontsize=12)
plt.tight_layout()
plot_path = os.path.join(images_path, 'plot_3_top_20_added_items.png')
plt.savefig(plot_path)
plt.close()
report_content.append(f"\n![가장 많이 장바구니에 담은 아이템 Top 20]({plot_path})")
report_content.append("\n**데이터:**")
report_content.append(top_20_added_items.to_frame('장바구니에 담은 횟수').to_markdown())


# Plot 4: 가장 많이 구매한 아이템 Top 20
report_content.append("\n### 2.4. 가장 많이 구매한 아이템 Top 20")
top_20_purchased_items = events_df[events_df['event'] == 'transaction'].groupby('itemid').size().nlargest(20)
plt.figure(figsize=(12, 8))
top_20_purchased_items.sort_values().plot(kind='barh', color='g')
plt.title('가장 많이 구매한 아이템 Top 20', fontsize=16)
plt.xlabel('구매 횟수', fontsize=12)
plt.ylabel('아이템 ID', fontsize=12)
plt.tight_layout()
plot_path = os.path.join(images_path, 'plot_4_top_20_purchased_items.png')
plt.savefig(plot_path)
plt.close()
report_content.append(f"\n![가장 많이 구매한 아이템 Top 20]({plot_path})")
report_content.append("\n**데이터:**")
report_content.append(top_20_purchased_items.to_frame('구매 횟수').to_markdown())


# Plot 5: 방문자별 이벤트 수 분포
report_content.append("\n### 2.5. 방문자별 이벤트 수 분포")
visitor_event_counts = events_df.groupby('visitorid').size()
plt.figure(figsize=(10, 6))
sns.histplot(visitor_event_counts, bins=50, kde=False)
plt.title('방문자별 이벤트 수 분포', fontsize=16)
plt.xlabel('이벤트 수', fontsize=12)
plt.ylabel('방문자 수', fontsize=12)
plt.yscale('log')
plt.tight_layout()
plot_path = os.path.join(images_path, 'plot_5_events_per_visitor_distribution.png')
plt.savefig(plot_path)
plt.close()
report_content.append(f"\n![방문자별 이벤트 수 분포]({plot_path})")
report_content.append("\n**해석:** 대부분의 방문자는 적은 수의 이벤트를 발생시키며, 소수의 방문자가 매우 많은 활동을 보이는 롱테일 분포를 보입니다. Y축은 로그 스케일로 표시되어 분포를 더 명확하게 볼 수 있습니다.")


# --- 3. Item Properties 데이터 분석 ---
report_content.append("\n## 3. Item Properties 데이터 분석")

# Plot 6: 가장 많은 속성을 가진 아이템 Top 20
report_content.append("\n### 3.1. 가장 많은 속성을 가진 아이템 Top 20")
item_property_counts = item_props_df.groupby('itemid').size().nlargest(20)
plt.figure(figsize=(12, 8))
item_property_counts.sort_values().plot(kind='barh', color='purple')
plt.title('가장 많은 속성을 가진 아이템 Top 20', fontsize=16)
plt.xlabel('속성 수', fontsize=12)
plt.ylabel('아이템 ID', fontsize=12)
plt.tight_layout()
plot_path = os.path.join(images_path, 'plot_6_top_20_items_by_property_count.png')
plt.savefig(plot_path)
plt.close()
report_content.append(f"\n![가장 많은 속성을 가진 아이템 Top 20]({plot_path})")
report_content.append("\n**데이터:**")
report_content.append(item_property_counts.to_frame('속성 수').to_markdown())


# Plot 7: 가장 흔한 속성 Top 20
report_content.append("\n### 3.2. 가장 흔한 속성 Top 20")
top_20_properties = item_props_df['property'].value_counts().nlargest(20)
plt.figure(figsize=(12, 8))
top_20_properties.sort_values().plot(kind='barh', color='orange')
plt.title('가장 흔한 속성 Top 20', fontsize=16)
plt.xlabel('빈도', fontsize=12)
plt.ylabel('속성', fontsize=12)
plt.tight_layout()
plot_path = os.path.join(images_path, 'plot_7_top_20_common_properties.png')
plt.savefig(plot_path)
plt.close()
report_content.append(f"\n![가장 흔한 속성 Top 20]({plot_path})")
report_content.append("\n**데이터:**")
report_content.append(top_20_properties.to_frame('빈도').to_markdown())


# --- 4. 데이터 병합 및 추가 분석 ---
report_content.append("\n## 4. 데이터 병합 및 추가 분석")

# Events와 Item Properties 병합
merged_df = pd.merge(events_df, item_props_df, on='itemid', how='inner')
report_content.append("\n### 4.1. Events, Item Properties 데이터 병합")
report_content.append(f"- 병합 후 데이터 수: {len(merged_df)}")
report_content.append("\n**병합 데이터 샘플:**")
report_content.append(merged_df.head().to_markdown(index=False))

# Plot 8: 구매로 이어진 아이템들의 속성 분포 (Top 20)
report_content.append("\n### 4.2. 구매된 아이템의 속성 분포 Top 20")
purchased_items = events_df[events_df['event'] == 'transaction']['itemid'].unique()
purchased_item_props = item_props_df[item_props_df['itemid'].isin(purchased_items)]
top_20_purchased_props = purchased_item_props['property'].value_counts().nlargest(20)

plt.figure(figsize=(12, 8))
top_20_purchased_props.sort_values().plot(kind='barh', color='brown')
plt.title('구매된 아이템의 속성 분포 Top 20', fontsize=16)
plt.xlabel('빈도', fontsize=12)
plt.ylabel('속성', fontsize=12)
plt.tight_layout()
plot_path = os.path.join(images_path, 'plot_8_top_20_purchased_item_properties.png')
plt.savefig(plot_path)
plt.close()
report_content.append(f"\n![구매된 아이템의 속성 분포 Top 20]({plot_path})")
report_content.append("\n**데이터:**")
report_content.append(top_20_purchased_props.to_frame('빈도').to_markdown())
report_content.append("\n**해석:** 'available' 속성이 구매된 아이템에서 압도적으로 많이 나타납니다. 이는 당연한 결과일 수 있지만, 다른 속성들과의 관계를 통해 특정 속성이 구매 결정에 미치는 영향을 파악할 수 있습니다.")


# Events, Item Properties, Category Tree 병합
# 먼저, itemid와 categoryid를 연결해야 합니다.
# item_props_df에 'categoryid'라는 속성이 있는지 확인
# 'categoryid'가 속성으로 존재한다고 가정하고 진행 (데이터 명세가 없어 가정에 기반)
if 'categoryid' in item_props_df['property'].unique():
    item_category_df = item_props_df[item_props_df['property'] == 'categoryid'][['itemid', 'value']]
    item_category_df = item_category_df.rename(columns={'value': 'categoryid'})
    item_category_df['categoryid'] = pd.to_numeric(item_category_df['categoryid'])

    # events, item_category, category_tree 병합
    merged_full_df = pd.merge(events_df, item_category_df, on='itemid', how='inner')
    merged_full_df = pd.merge(merged_full_df, category_tree_df, on='categoryid', how='left') # left join으로 카테고리 정보가 없는 경우도 포함

    report_content.append("\n### 4.3. 전체 데이터 병합 (Events, Item-Category, Category Tree)")
    report_content.append(f"- 전체 병합 후 데이터 수: {len(merged_full_df)}")
    report_content.append("\n**전체 병합 데이터 샘플:**")
    report_content.append(merged_full_df.head().to_markdown(index=False))

    # Plot 9: 카테고리별 조회수 Top 20
    report_content.append("\n### 4.4. 카테고리별 조회수 Top 20")
    category_view_counts = merged_full_df[merged_full_df['event'] == 'view'].groupby('categoryid').size().nlargest(20)
    plt.figure(figsize=(12, 8))
    category_view_counts.sort_values().plot(kind='barh', color='teal')
    plt.title('카테고리별 조회수 Top 20', fontsize=16)
    plt.xlabel('조회수', fontsize=12)
    plt.ylabel('카테고리 ID', fontsize=12)
    plt.tight_layout()
    plot_path = os.path.join(images_path, 'plot_9_top_20_viewed_categories.png')
    plt.savefig(plot_path)
    plt.close()
    report_content.append(f"\n![카테고리별 조회수 Top 20]({plot_path})")
    report_content.append("\n**데이터:**")
    report_content.append(category_view_counts.to_frame('조회수').to_markdown())

    # Plot 10: 카테고리별 구매수 Top 20
    report_content.append("\n### 4.5. 카테고리별 구매수 Top 20")
    category_purchase_counts = merged_full_df[merged_full_df['event'] == 'transaction'].groupby('categoryid').size().nlargest(20)
    plt.figure(figsize=(12, 8))
    category_purchase_counts.sort_values().plot(kind='barh', color='darkviolet')
    plt.title('카테고리별 구매수 Top 20', fontsize=16)
    plt.xlabel('구매수', fontsize=12)
    plt.ylabel('카테고리 ID', fontsize=12)
    plt.tight_layout()
    plot_path = os.path.join(images_path, 'plot_10_top_20_purchased_categories.png')
    plt.savefig(plot_path)
    plt.close()
    report_content.append(f"\n![카테고리별 구매수 Top 20]({plot_path})")
    report_content.append("\n**데이터:**")
    report_content.append(category_purchase_counts.to_frame('구매수').to_markdown())
    report_content.append("\n**해석:** 특정 카테고리가 조회수와 구매수 모두에서 높게 나타나는 것을 확인할 수 있습니다. 이는 해당 카테고리가 사용자들의 주요 관심사임을 시사합니다.")

else:
    report_content.append("\n**참고:** 'item_properties' 데이터에 'categoryid' 속성이 없어 카테고리 관련 상세 분석을 생략했습니다.")


# --- 5. 결론 ---
report_content.append("\n## 5. 결론 및 요약")
report_content.append("""
1.  **이벤트 데이터**: 사용자 행동은 'view'가 대부분을 차지하며, 'addtocart'와 'transaction'으로 이어지는 비율은 상대적으로 낮습니다. 이는 일반적인 이커머스 퍼널 구조와 일치합니다.
2.  **아이템 데이터**: 특정 아이템들이 조회, 장바구니 추가, 구매에서 높은 빈도를 보입니다. 이는 인기 상품이며, 추천 시스템이나 프로모션에 활용될 수 있습니다.
3.  **사용자 행동**: 대부분의 사용자는 소수의 활동만 하고 떠나지만, 매우 활동적인 소수의 '헤비 유저' 그룹이 존재합니다. 이들의 특성을 분석하면 충성 고객 확보에 대한 인사이트를 얻을 수 있습니다.
4.  **아이템 속성**: 'available'과 같은 특정 속성이 매우 흔하게 나타나며, 특히 구매된 아이템에서 두드러집니다. 다른 속성들과의 조합을 분석하면 구매 전환에 영향을 미치는 요인을 파악할 수 있을 것입니다.
5.  **카테고리**: (데이터가 있는 경우) 특정 카테고리에 사용자들의 관심과 구매가 집중되는 경향을 보입니다. 카테고리별 마케팅 전략 수립에 중요한 단서가 될 수 있습니다.

향후 분석으로는 각 이벤트 간의 시간 간격 분석, 사용자의 구매 전환율(Conversion Rate) 분석, 혹은 아이템 속성과 사용자 행동 간의 연관 규칙 분석 등을 통해 더 깊이 있는 인사이트를 도출할 수 있을 것입니다.
""")


# --- 리포트 파일 작성 ---
with open('uci/EDA_Report.md', 'w', encoding='utf-8') as f:
    f.write("\n".join(report_content))

# 임시 파일 삭제
if os.path.exists('temp_info.txt'):
    os.remove('temp_info.txt')

print("EDA 분석이 완료되었으며, 'uci/EDA_Report.md' 파일이 생성되었습니다.")
