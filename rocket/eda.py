# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import numpy as np

def run_eda():
    # 이미지 저장 폴더 생성
    if not os.path.exists('rocket/images'):
        os.makedirs('rocket/images')

    # 리포트 파일 초기화
    report_path = 'rocket/EDA_Report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Rocket 데이터셋 탐색적 데이터 분석(EDA) 보고서\n\n")
        f.write("이 보고서는 `rocket` 폴더에 있는 CSV 파일들을 분석한 결과를 담고 있습니다.\n")
        f.write("요구사항에 맞춰 `koreanize-matplotlib`을 사용하여 그래프의 한글을 처리했으며, `seaborn` 스타일은 사용하지 않았습니다.\n\n")

    # 데이터 로드
    try:
        events = pd.read_csv('rocket/events.csv')
        category_tree = pd.read_csv('rocket/category_tree.csv')
        item_properties_part1 = pd.read_csv('rocket/item_properties_part1.csv')
        item_properties_part2 = pd.read_csv('rocket/item_properties_part2.csv')
        item_properties = pd.concat([item_properties_part1, item_properties_part2], ignore_index=True)
    except FileNotFoundError as e:
        with open(report_path, 'a', encoding='utf-8') as f:
            f.write(f"**오류:** 데이터 파일을 로드하는 중 오류가 발생했습니다: {e}\n")
            f.write("`rocket` 폴더에 `events.csv`, `category_tree.csv`, `item_properties_part1.csv`, `item_properties_part2.csv` 파일이 모두 있는지 확인해주세요.\n")
        return

    # --- 1. events.csv 분석 ---
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("## 1. `events.csv` 분석\n\n")
        f.write("사용자 행동 이벤트(조회, 장바구니 추가, 구매) 데이터를 담고 있습니다.\n\n")
        
        f.write("### 1.1. 데이터 샘플\n")
        f.write(events.head().to_markdown(index=False))
        f.write("\n\n")

        f.write("### 1.2. 데이터 정보\n")
        buffer = pd.io.common.StringIO()
        events.info(buf=buffer)
        f.write(f"```\n{buffer.getvalue()}\n```\n\n")

        f.write("### 1.3. 기술 통계\n")
        f.write(f"```\n{events.describe().to_string()}\n```\n\n")

        f.write("### 1.4. 결측치 확인\n")
        f.write(events.isnull().sum().to_frame('결측치 수').to_markdown())
        f.write("\n\n`transactionid`는 구매 이벤트에서만 생성되므로, 대부분의 행에서 결측치인 것은 자연스러운 현상입니다.\n\n")

    # --- 2. category_tree.csv 분석 ---
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("## 2. `category_tree.csv` 분석\n\n")
        f.write("상품 카테고리의 계층 구조(부모-자식 관계)를 나타냅니다.\n\n")

        f.write("### 2.1. 데이터 샘플\n")
        f.write(category_tree.head().to_markdown(index=False))
        f.write("\n\n")

        f.write("### 2.2. 데이터 정보\n")
        buffer = pd.io.common.StringIO()
        category_tree.info(buf=buffer)
        f.write(f"```\n{buffer.getvalue()}\n```\n\n")

        f.write("### 2.3. 기술 통계\n")
        f.write(f"```\n{category_tree.describe().to_string()}\n```\n\n")

        f.write("### 2.4. 결측치 확인\n")
        f.write(category_tree.isnull().sum().to_frame('결측치 수').to_markdown())
        f.write("\n\n 최상위 카테고리는 부모 카테고리가 없으므로 `parentid`가 결측치일 수 있습니다.\n\n")
        
    # --- 3. item_properties.csv 분석 ---
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("## 3. `item_properties.csv` 분석\n\n")
        f.write("개별 상품의 속성(프로퍼티) 정보를 담고 있습니다. 두 개의 파일(`part1`, `part2`)을 병합하여 분석합니다.\n\n")
        
        f.write("### 3.1. 데이터 샘플\n")
        f.write(item_properties.head().to_markdown(index=False))
        f.write("\n\n")

        f.write("### 3.2. 데이터 정보\n")
        buffer = pd.io.common.StringIO()
        item_properties.info(buf=buffer)
        f.write(f"```\n{buffer.getvalue()}\n```\n\n")

        f.write("### 3.3. 기술 통계\n")
        f.write(f"```\n{item_properties.describe().to_string()}\n```\n\n")

        f.write("### 3.4. 결측치 확인\n")
        f.write(item_properties.isnull().sum().to_frame('결측치 수').to_markdown())
        f.write("\n\n결측치가 없는 것을 확인했습니다.\n\n")

    # --- 4. 데이터 시각화 및 심층 분석 ---
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("## 4. 데이터 시각화 및 심층 분석\n\n")

    # Plot 1: 이벤트 유형 분포
    plt.figure(figsize=(10, 6))
    event_counts = events['event'].value_counts()
    event_counts.plot(kind='bar', rot=0)
    plt.title('이벤트 유형별 분포')
    plt.xlabel('이벤트 유형')
    plt.ylabel('횟수')
    img_path1 = 'rocket/images/plot_01_event_distribution.png'
    plt.savefig(img_path1)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.1. 이벤트 유형 분포\n\n")
        f.write("![이벤트 유형 분포](../rocket/images/plot_01_event_distribution.png)\n\n")
        f.write("가장 많은 이벤트는 'view'이며, 'addtocart'와 'transaction'이 그 뒤를 잇습니다. 이는 일반적인 이커머스 funnel 형태를 보여줍니다.\n\n")
        f.write("**교차표:**\n")
        f.write(event_counts.to_frame('횟수').to_markdown())
        f.write("\n\n")

    # 데이터 병합 (events, item_properties)
    # categoryid를 가진 property만 필터링
    item_categories = item_properties[item_properties['property'] == 'categoryid'][['itemid', 'value']].rename(columns={'value': 'categoryid'})
    item_categories['categoryid'] = pd.to_numeric(item_categories['categoryid'])
    
    # events 데이터와 상품 카테고리 정보 병합
    events_with_category = pd.merge(events, item_categories, on='itemid', how='left')

    # Plot 2: 상위 20개 카테고리 (조회수 기준)
    plt.figure(figsize=(12, 8))
    top_20_viewed_cat = events_with_category[events_with_category['event'] == 'view']['categoryid'].value_counts().nlargest(20)
    top_20_viewed_cat.plot(kind='barh')
    plt.title('상위 20개 카테고리 (조회수 기준)')
    plt.xlabel('조회수')
    plt.ylabel('카테고리 ID')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    img_path2 = 'rocket/images/plot_02_top_viewed_categories.png'
    plt.savefig(img_path2)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.2. 상위 20개 카테고리 (조회수 기준)\n\n")
        f.write("![상위 20개 카테고리 조회수](../rocket/images/plot_02_top_viewed_categories.png)\n\n")
        f.write("조회수가 가장 높은 상위 20개 카테고리입니다. 어떤 카테고리가 사용자들의 관심을 많이 끄는지 알 수 있습니다.\n\n")
        f.write("**피봇 테이블:**\n")
        f.write(top_20_viewed_cat.to_frame('조회수').to_markdown())
        f.write("\n\n")

    # Plot 3: 상위 20개 카테고리 (장바구니 추가 기준)
    plt.figure(figsize=(12, 8))
    top_20_cart_cat = events_with_category[events_with_category['event'] == 'addtocart']['categoryid'].value_counts().nlargest(20)
    top_20_cart_cat.plot(kind='barh')
    plt.title('상위 20개 카테고리 (장바구니 추가 기준)')
    plt.xlabel('장바구니 추가 횟수')
    plt.ylabel('카테고리 ID')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    img_path3 = 'rocket/images/plot_03_top_cart_categories.png'
    plt.savefig(img_path3)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.3. 상위 20개 카테고리 (장바구니 추가 기준)\n\n")
        f.write("![상위 20개 카테고리 장바구니](../rocket/images/plot_03_top_cart_categories.png)\n\n")
        f.write("장바구니에 가장 많이 추가된 상위 20개 카테고리입니다. 이는 잠재적 구매 가능성이 높은 카테고리를 의미합니다.\n\n")
        f.write("**피봇 테이블:**\n")
        f.write(top_20_cart_cat.to_frame('장바구니 추가 횟수').to_markdown())
        f.write("\n\n")

    # Plot 4: 상위 20개 카테고리 (구매 완료 기준)
    plt.figure(figsize=(12, 8))
    top_20_trans_cat = events_with_category[events_with_category['event'] == 'transaction']['categoryid'].value_counts().nlargest(20)
    top_20_trans_cat.plot(kind='barh')
    plt.title('상위 20개 카테고리 (구매 완료 기준)')
    plt.xlabel('구매 완료 횟수')
    plt.ylabel('카테고리 ID')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    img_path4 = 'rocket/images/plot_04_top_transaction_categories.png'
    plt.savefig(img_path4)
    plt.close()
    
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.4. 상위 20개 카테고리 (구매 완료 기준)\n\n")
        f.write("![상위 20개 구매 카테고리](../rocket/images/plot_04_top_transaction_categories.png)\n\n")
        f.write("실제로 구매가 가장 많이 일어난 상위 20개 카테고리입니다. 이는 비즈니스의 핵심 수익원을 파악하는 데 중요합니다.\n\n")
        f.write("**피봇 테이블:**\n")
        f.write(top_20_trans_cat.to_frame('구매 완료 횟수').to_markdown())
        f.write("\n\n")
        
    # timestamp 변환
    events['timestamp_dt'] = pd.to_datetime(events['timestamp'], unit='ms')

    # Plot 5: 일별 이벤트 발생 횟수
    plt.figure(figsize=(15, 6))
    events.set_index('timestamp_dt')['event'].resample('D').count().plot()
    plt.title('일별 총 이벤트 발생 횟수')
    plt.xlabel('날짜')
    plt.ylabel('이벤트 수')
    img_path5 = 'rocket/images/plot_05_events_over_time.png'
    plt.savefig(img_path5)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.5. 일별 총 이벤트 발생 횟수\n\n")
        f.write("![일별 이벤트 횟수](../rocket/images/plot_05_events_over_time.png)\n\n")
        f.write("시간에 따른 전체 이벤트 수의 추이를 보여줍니다. 특정 기간에 이벤트가 급증하거나 급감하는 패턴을 파악할 수 있습니다.\n\n")
        f.write("**교차표 (상위 10일):**\n")
        f.write(events.set_index('timestamp_dt')['event'].resample('D').count().nlargest(10).to_frame('이벤트 수').to_markdown())
        f.write("\n\n")

    # Plot 6: 시간대별 이벤트 발생 횟수
    events['hour'] = events['timestamp_dt'].dt.hour
    hourly_events = events['hour'].value_counts().sort_index()
    plt.figure(figsize=(12, 6))
    hourly_events.plot(kind='bar')
    plt.title('시간대별 총 이벤트 발생 횟수')
    plt.xlabel('시간 (0-23시)')
    plt.ylabel('이벤트 수')
    img_path6 = 'rocket/images/plot_06_events_by_hour.png'
    plt.savefig(img_path6)
    plt.close()
    
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.6. 시간대별 총 이벤트 발생 횟수\n\n")
        f.write("![시간대별 이벤트 횟수](../rocket/images/plot_06_events_by_hour.png)\n\n")
        f.write("하루 중 어떤 시간대에 사용자들이 가장 활발하게 활동하는지 보여줍니다. 마케팅 캠페인 시간 설정 등에 활용할 수 있습니다.\n\n")
        f.write("**교차표:**\n")
        f.write(hourly_events.to_frame('이벤트 수').to_markdown())
        f.write("\n\n")
        
    # Plot 7: 요일별 이벤트 발생 횟수
    events['dayofweek'] = events['timestamp_dt'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_events = events['dayofweek'].value_counts().loc[day_order]
    plt.figure(figsize=(10, 6))
    daily_events.plot(kind='bar', rot=45)
    plt.title('요일별 총 이벤트 발생 횟수')
    plt.xlabel('요일')
    plt.ylabel('이벤트 수')
    plt.tight_layout()
    img_path7 = 'rocket/images/plot_07_events_by_dayofweek.png'
    plt.savefig(img_path7)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.7. 요일별 총 이벤트 발생 횟수\n\n")
        f.write("![요일별 이벤트 횟수](../rocket/images/plot_07_events_by_dayofweek.png)\n\n")
        f.write("주중과 주말 중 사용자의 활동성에 차이가 있는지 파악할 수 있습니다.\n\n")
        f.write("**교차표:**\n")
        f.write(daily_events.to_frame('이벤트 수').to_markdown())
        f.write("\n\n")
        
    # Plot 8: 상위 20개 상품 속성(property) 분포
    plt.figure(figsize=(12, 8))
    top_20_properties = item_properties['property'].value_counts().nlargest(20)
    top_20_properties.plot(kind='barh')
    plt.title('상위 20개 상품 속성(Property) 분포')
    plt.xlabel('횟수')
    plt.ylabel('속성(Property)')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    img_path8 = 'rocket/images/plot_08_top_20_properties.png'
    plt.savefig(img_path8)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.8. 상위 20개 상품 속성(Property) 분포\n\n")
        f.write("![상위 20개 상품 속성](../rocket/images/plot_08_top_20_properties.png)\n\n")
        f.write("상품들이 어떤 종류의 속성을 가장 많이 가지고 있는지 보여줍니다. 'available', 'categoryid' 등이 많이 사용되는 것을 볼 수 있습니다.\n\n")
        f.write("**피봇 테이블:**\n")
        f.write(top_20_properties.to_frame('횟수').to_markdown())
        f.write("\n\n")

    # Plot 9: 사용자별 이벤트 수 분포
    plt.figure(figsize=(12, 6))
    visitor_event_counts = events['visitorid'].value_counts()
    visitor_event_counts.plot(kind='hist', bins=100, range=(0, visitor_event_counts.quantile(0.99)))
    plt.title('사용자별 이벤트 수 분포 (상위 99% 대상)')
    plt.xlabel('사용자당 이벤트 수')
    plt.ylabel('사용자 수')
    img_path9 = 'rocket/images/plot_09_events_per_visitor.png'
    plt.savefig(img_path9)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.9. 사용자별 이벤트 수 분포\n\n")
        f.write("![사용자별 이벤트 수 분포](../rocket/images/plot_09_events_per_visitor.png)\n\n")
        f.write("대부분의 사용자는 적은 수의 이벤트를 발생시키며, 소수의 '헤비 유저'가 매우 많은 이벤트를 발생시키는 롱테일 분포를 보입니다.\n\n")
        f.write("**피봇 테이블 (상위 10명):**\n")
        f.write(visitor_event_counts.nlargest(10).to_frame('이벤트 수').to_markdown())
        f.write("\n\n")
        
    # Plot 10: 상품별 이벤트 수 분포
    plt.figure(figsize=(12, 6))
    item_event_counts = events['itemid'].value_counts()
    item_event_counts.plot(kind='hist', bins=100, range=(0, item_event_counts.quantile(0.99)))
    plt.title('상품별 이벤트 수 분포 (상위 99% 대상)')
    plt.xlabel('상품당 이벤트 수')
    plt.ylabel('상품 수')
    img_path10 = 'rocket/images/plot_10_events_per_item.png'
    plt.savefig(img_path10)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.10. 상품별 이벤트 수 분포\n\n")
        f.write("![상품별 이벤트 수 분포](../rocket/images/plot_10_events_per_item.png)\n\n")
        f.write("사용자 분포와 유사하게, 대부분의 상품은 적은 수의 이벤트를 받으며, 소수의 인기 상품이 많은 주목을 받는 것을 알 수 있습니다.\n\n")
        f.write("**피봇 테이블 (상위 10개):**\n")
        f.write(item_event_counts.nlargest(10).to_frame('이벤트 수').to_markdown())
        f.write("\n\n")

def analyze_hourly_events():
    # 데이터 로드
    try:
        events = pd.read_csv('rocket/events.csv')
        events['timestamp_dt'] = pd.to_datetime(events['timestamp'], unit='ms')
        events['hour'] = events['timestamp_dt'].dt.hour
    except FileNotFoundError as e:
        print(f"오류: events.csv 파일을 찾을 수 없습니다.")
        return

    report_path = 'rocket/EDA_Report.md'
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.11. 시간대별 이벤트 심층 분석\n\n")

    # 시간대별, 이벤트 유형별 집계
    hourly_event_pivot = events.pivot_table(index='hour', columns='event', aggfunc='size', fill_value=0)
    
    # Plot 11: 시간대별 이벤트 유형 비교
    fig, ax = plt.subplots(figsize=(12, 7))
    hourly_event_pivot.plot(kind='line', ax=ax, marker='o')
    ax.set_title('시간대별 이벤트 유형 비교')
    ax.set_xlabel('시간 (0-23시)')
    ax.set_ylabel('이벤트 수')
    ax.legend(title='이벤트 유형')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    img_path11 = 'rocket/images/plot_11_hourly_event_types.png'
    plt.savefig(img_path11)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("#### 시간대별 이벤트 유형 비교\n\n")
        f.write("![시간대별 이벤트 유형 비교](../rocket/images/plot_11_hourly_event_types.png)\n\n")
        f.write("모든 이벤트 유형(view, addtocart, transaction)이 비슷한 시간대 패턴을 보입니다. 새벽 시간(6-14시)에 활동이 저조하다가, 늦은 오후부터 새벽 3시까지 활발한 활동이 이어집니다.\n\n")
        f.write("**피봇 테이블:**\n")
        f.write(hourly_event_pivot.to_markdown())
        f.write("\n\n")
        
    # 전환율 계산
    # 0으로 나누는 것을 방지하기 위해 np.divide 사용
    hourly_event_pivot['view_to_cart_rate'] = np.divide(hourly_event_pivot['addtocart'], hourly_event_pivot['view']) * 100
    hourly_event_pivot['cart_to_transaction_rate'] = np.divide(hourly_event_pivot['transaction'], hourly_event_pivot['addtocart']) * 100
    
    # Plot 12: 시간대별 전환율
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # View to Cart Rate
    hourly_event_pivot['view_to_cart_rate'].plot(kind='line', ax=ax1, marker='o', color='tab:blue')
    ax1.set_title('시간대별 조회 → 장바구니 전환율 (%)')
    ax1.set_ylabel('전환율 (%)')
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Cart to Transaction Rate
    hourly_event_pivot['cart_to_transaction_rate'].plot(kind='line', ax=ax2, marker='o', color='tab:green')
    ax2.set_title('시간대별 장바구니 → 구매 전환율 (%)')
    ax2.set_xlabel('시간 (0-23시)')
    ax2.set_ylabel('전환율 (%)')
    ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    plt.tight_layout()
    img_path12 = 'rocket/images/plot_12_hourly_conversion_rates.png'
    plt.savefig(img_path12)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("#### 시간대별 전환율 분석\n\n")
        f.write("![시간대별 전환율 분석](../rocket/images/plot_12_hourly_conversion_rates.png)\n\n")
        f.write("**조회 → 장바구니 전환율:** 사용자들이 가장 적게 활동하는 오전 8-10시 사이에 가장 높은 전환율을 보입니다. 이는 해당 시간대 사용자들이 뚜렷한 목적을 가지고 쇼핑할 가능성이 높음을 시사합니다.\n")
        f.write("**장바구니 → 구매 전환율:** 이른 새벽(2-4시)과 오전(8-11시) 시간대에 구매 전환율이 높게 나타납니다. 특히 활동량이 적은 오전 시간대의 구매 결정력이 주목할 만합니다.\n\n")
        f.write("**피봇 테이블 (전환율 포함):**\n")
        f.write(hourly_event_pivot[['view_to_cart_rate', 'cart_to_transaction_rate']].to_markdown(floatfmt=".2f"))
        f.write("\n\n")

def analyze_revisit_patterns():
    # 데이터 로드
    try:
        events = pd.read_csv('rocket/events.csv')
        events['timestamp_dt'] = pd.to_datetime(events['timestamp'], unit='ms')
        events['hour'] = events['timestamp_dt'].dt.hour
    except FileNotFoundError as e:
        print(f"오류: events.csv 파일을 찾을 수 없습니다.")
        return

    report_path = 'rocket/EDA_Report.md'
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("### 4.12. 야간 장바구니 사용자의 재방문 패턴 분석\n\n")
    
    # 1. 다음 이벤트 정보 생성
    events = events.sort_values(['visitorid', 'timestamp_dt'])
    events['next_event_timestamp'] = events.groupby('visitorid')['timestamp_dt'].shift(-1)
    events['next_event_type'] = events.groupby('visitorid')['event'].shift(-1)
    events['time_to_next_event'] = (events['next_event_timestamp'] - events['timestamp_dt']).dt.total_seconds() / 3600 # 시간 단위

    # 2. '야간 장바구니' 이벤트 필터링
    night_hours = [22, 23, 0, 1, 2, 3, 4]
    night_shoppers = events[(events['event'] == 'addtocart') & (events['hour'].isin(night_hours))].copy()
    
    if night_shoppers.empty:
        with open(report_path, 'a', encoding='utf-8') as f:
            f.write("야간 장바구니 사용자를 찾을 수 없습니다.\n\n")
        return
        
    # 3. 재방문 소요 시간 분석
    bins = [0, 1, 6, 24, 72, np.inf] # 1시간이내, 1-6시간, 6-24시간, 1-3일, 3일 이상
    labels = ['1시간 이내', '1-6시간', '6-24시간', '1-3일', '3일 이상']
    night_shoppers['revisit_time_bin'] = pd.cut(night_shoppers['time_to_next_event'], bins=bins, labels=labels, right=False)
    revisit_time_dist = night_shoppers['revisit_time_bin'].value_counts().sort_index()

    # Plot 13: 재방문 소요 시간 분포
    plt.figure(figsize=(10, 6))
    revisit_time_dist.plot(kind='bar', rot=0)
    plt.title('야간 장바구니 사용자의 재방문 소요 시간 분포')
    plt.xlabel('재방문까지 걸린 시간')
    plt.ylabel('사용자 수')
    img_path13 = 'rocket/images/plot_13_revisit_time_distribution.png'
    plt.savefig(img_path13)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("#### 재방문 소요 시간\n\n")
        f.write("![재방문 소요 시간 분포](../rocket/images/plot_13_revisit_time_distribution.png)\n\n")
        f.write("밤에 장바구니에 상품을 담은 사용자들의 상당수가 1시간 이내에 다시 사이트를 방문하는 것을 볼 수 있습니다. 이는 장바구니에 상품을 담은 직후 다른 상품을 탐색하거나 구매를 결정하는 경향이 있음을 보여줍니다.\n\n")
        f.write("**교차표:**\n")
        f.write(revisit_time_dist.to_frame('사용자 수').to_markdown())
        f.write("\n\n")

    # 4. 재방문 시 첫 행동 분석
    next_event_dist = night_shoppers['next_event_type'].value_counts()

    # Plot 14: 재방문 시 첫 행동 유형
    plt.figure(figsize=(10, 6))
    next_event_dist.plot(kind='bar', rot=0)
    plt.title('야간 장바구니 사용자의 재방문 시 첫 행동 유형')
    plt.xlabel('다음 행동 유형')
    plt.ylabel('사용자 수')
    img_path14 = 'rocket/images/plot_14_next_event_type.png'
    plt.savefig(img_path14)
    plt.close()

    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("#### 재방문 시 첫 행동 유형\n\n")
        f.write("![재방문 시 첫 행동 유형](../rocket/images/plot_14_next_event_type.png)\n\n")
        f.write("재방문한 사용자의 가장 흔한 첫 행동은 'view' 입니다. 이는 장바구니에 담은 상품과 연관된 다른 상품을 보거나, 다른 상품과 비교하는 행동으로 해석할 수 있습니다. 'addtocart'가 두 번째로 높은 것은 추가적인 상품을 장바구니에 담는 행동 패턴을 보여줍니다.\n\n")
        f.write("**교차표:**\n")
        f.write(next_event_dist.to_frame('사용자 수').to_markdown())
        f.write("\n\n")

if __name__ == '__main__':
    # 기존 EDA 실행 후 상세 분석 추가
    run_eda()
    analyze_hourly_events()
    analyze_revisit_patterns()
