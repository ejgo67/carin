import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from matplotlib import font_manager as fm
import datetime
import textwrap

# 한글 폰트 설정: 가능한 폰트 이름을 찾아 우선 적용합니다.
# Windows에서 일반적으로 'Malgun Gothic' 또는 '맑은 고딕'이 사용됩니다.
preferred_fonts = ["Malgun Gothic", "맑은 고딕", "NanumGothic", "AppleGothic"]
available_fonts = set(f.name for f in fm.fontManager.ttflist)
for pf in preferred_fonts:
    if pf in available_fonts:
        mpl.rcParams['font.family'] = pf
        break
mpl.rcParams['axes.unicode_minus'] = False


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def write_code_block(md_fp, title: str, content: str):
    md_fp.write(f"## {title}\n\n")
    md_fp.write("```")
    md_fp.write("\n")
    md_fp.write(content)
    if not content.endswith("\n"):
        md_fp.write("\n")
    md_fp.write("``" + "\n\n")


def save_fig(fig, out_path: Path):
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    base = Path(__file__).resolve().parent
    images_dir = base / "images"
    ensure_dir(images_dir)

    csv_files = sorted(base.glob("*.csv"))

    md_path = base / "EDA_Report.md"
    with md_path.open("w", encoding="utf-8") as md_fp:
        md_fp.write(f"# UCI 폴더 전체 EDA 리포트\n\n")
        md_fp.write(f"생성일: {datetime.datetime.now().isoformat()}\n\n")
        md_fp.write("이 리포트는 `uci` 폴더 내 모든 CSV 파일을 자동으로 읽고 요약, 통계, 시각화를 생성합니다.\n\n")

        img_counter = 0

        for csv in csv_files:
            name = csv.stem
            md_fp.write(f"---\n\n## 데이터셋: {name}\n\n")
            try:
                df = pd.read_csv(csv, low_memory=False)
            except Exception as e:
                md_fp.write(f"읽기 오류: {e}\n\n")
                continue

            md_fp.write(f"파일경로: ./uci/{csv.name}\n\n")
            md_fp.write(f"형상: {df.shape}\n\n")

            # head
            md_fp.write("### 상위 5개 행\n\n")
            write_code_block(md_fp, "head()", df.head(5).to_string())

            # info
            md_fp.write("### 데이터 정보 (info)\n\n")
            buf = []
            try:
                from io import StringIO
                bufio = StringIO()
                df.info(buf=bufio)
                info_str = bufio.getvalue()
            except Exception:
                info_str = "info 출력 실패"
            write_code_block(md_fp, "info()", info_str)

            # describe
            md_fp.write("### 기술 통계 (`describe()`)\n\n")
            try:
                desc = df.describe(include='all').to_string()
            except Exception:
                desc = "describe() 오류"
            write_code_block(md_fp, "describe()", desc)

            # Missing values
            md_fp.write("### 결측치 현황\n\n")
            miss = df.isna().sum().sort_values(ascending=False)
            write_code_block(md_fp, "missing values (count)", miss.to_string())

            # Identify numeric and categorical
            numerics = df.select_dtypes(include=["number"]).columns.tolist()
            objects = df.select_dtypes(include=["object", "category"]).columns.tolist()

            # Correlation heatmap for numeric columns
            if len(numerics) >= 2:
                fig, ax = plt.subplots(figsize=(6, 5))
                sns.heatmap(df[numerics].corr(), annot=True, fmt='.2f', ax=ax, cmap='vlag')
                img_name = f"{name}_corr.png"
                save_fig(fig, images_dir / img_name)
                md_fp.write(f"![corr](./images/{img_name})\n\n")
                img_counter += 1

            # category_tree specific hierarchy analysis
            if name == 'category_tree':
                try:
                    # build parent-child mapping
                    ct = df.copy()
                    # treat parentid NaN as root markers
                    ct['parentid'] = ct['parentid'].astype('Int64')
                    parents = ct.set_index('categoryid')['parentid'].to_dict()

                    # find roots: parentid is null or parentid not in categoryid set
                    ids = set(parents.keys())
                    roots = [nid for nid, pid in parents.items() if pd.isna(pid) or int(pid) not in ids]

                    # compute depth via BFS from each root
                    from collections import deque, defaultdict
                    depth = {}
                    children = defaultdict(list)
                    for cid, pid in parents.items():
                        if not pd.isna(pid):
                            children[int(pid)].append(int(cid))

                    q = deque()
                    for r in roots:
                        depth[int(r)] = 0
                        q.append(int(r))
                    while q:
                        node = q.popleft()
                        for ch in children.get(node, []):
                            depth[ch] = depth[node] + 1
                            q.append(ch)

                    # nodes without reachable root (isolated cycles) set to -1
                    for cid in ids:
                        if cid not in depth:
                            depth[cid] = -1

                    # depth distribution
                    depth_counts = pd.Series(list(depth.values())).value_counts().sort_index()
                    write_code_block(md_fp, 'category depth counts', depth_counts.to_string())

                    # plot depth distribution (exclude -1 if exists)
                    dc_plot = depth_counts.drop(index=-1, errors='ignore')
                    fig, ax = plt.subplots(figsize=(6, 4))
                    sns.barplot(x=dc_plot.index.astype(str), y=dc_plot.values, ax=ax)
                    ax.set_title('category_tree depth distribution')
                    ax.set_xlabel('depth')
                    ax.set_ylabel('count')
                    img_name = f"{name}_depth_dist.png"
                    save_fig(fig, images_dir / img_name)
                    md_fp.write(f"![depth](./images/{img_name})\n\n")
                    img_counter += 1

                    # top parents by number of children
                    child_counts = pd.Series({k: len(v) for k, v in children.items()}).sort_values(ascending=False).head(20)
                    write_code_block(md_fp, 'top parents by child count', child_counts.to_string())
                    fig, ax = plt.subplots(figsize=(7, 6))
                    sns.barplot(x=child_counts.values, y=child_counts.index.astype(str), ax=ax)
                    ax.set_title('Top parents by child count')
                    img_name = f"{name}_top_parents.png"
                    save_fig(fig, images_dir / img_name)
                    md_fp.write(f"![parents](./images/{img_name})\n\n")
                    img_counter += 1
                except Exception:
                    md_fp.write('category_tree 계층 분석 중 오류 발생\n\n')

            # Histograms for up to 3 numeric columns
            for col in numerics[:3]:
                try:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    sns.histplot(df[col].dropna(), bins=30, kde=False, ax=ax)
                    ax.set_title(f"{name} - {col} 분포")
                    img_name = f"{name}_hist_{col}.png"
                    save_fig(fig, images_dir / img_name)
                    md_fp.write(f"![hist](./images/{img_name})\n\n")
                    write_code_block(md_fp, f"{col} 기초통계", df[col].describe().to_string())
                    img_counter += 1
                except Exception:
                    continue

            # Barplots for up to 3 categorical columns (top categories)
            for col in objects[:3]:
                try:
                    vc = df[col].value_counts().head(20)
                    if vc.shape[0] == 0:
                        continue
                    fig, ax = plt.subplots(figsize=(7, 4))
                    sns.barplot(x=vc.values, y=vc.index, ax=ax)
                    ax.set_title(f"{name} - {col} 상위 값")
                    img_name = f"{name}_bar_{col}.png"
                    save_fig(fig, images_dir / img_name)
                    md_fp.write(f"![bar](./images/{img_name})\n\n")
                    img_counter += 1

                    # 교차표 / 피벗: value_counts와 유사한 표를 추가
                    md_fp.write("#### 해당 막대그래프에 대한 값표 (상위 20)\n\n")
                    write_code_block(md_fp, f"{col} value_counts", vc.to_string())

                    # If there is a numeric column, show pivot (mean) by this category for first numeric
                    if numerics:
                        pivot = df.groupby(col)[numerics[0]].agg(['count', 'mean']).sort_values('count', ascending=False).head(20)
                        write_code_block(md_fp, f"{col} vs {numerics[0]} (count/mean)", pivot.to_string())
                except Exception:
                    continue

            # Boxplot example: first numeric vs first categorical
            if numerics and objects:
                try:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    sns.boxplot(x=df[objects[0]].astype(str).replace('nan', pd.NA), y=df[numerics[0]], ax=ax)
                    ax.set_title(f"{name} - {numerics[0]} by {objects[0]}")
                    img_name = f"{name}_box_{objects[0]}_{numerics[0]}.png"
                    save_fig(fig, images_dir / img_name)
                    md_fp.write(f"![box](./images/{img_name})\n\n")
                    img_counter += 1
                except Exception:
                    pass

            # 간단한 해석 템플릿
            md_fp.write("### 간단한 해석\n\n")
            md_fp.write(textwrap.dedent(f"""
            - 데이터셋 `{name}` 은(는) 총 {df.shape[0]}개의 행과 {df.shape[1]}개의 열을 가집니다.
            - 결측치가 많은 열이 있다면 전처리(삭제/대체)가 필요합니다.
            - 상위 범주 및 수치 분포 이미지는 위에 포함되어 있습니다.
            """))

        # 보장: 적어도 10개 이미지가 생성되었는지 확인
        if img_counter < 10:
            md_fp.write("---\n\n# 보충 시각화\n\n")
            all_nums = []
            for csv in csv_files:
                try:
                    df = pd.read_csv(csv, low_memory=False)
                except Exception:
                    continue
                all_nums.extend(df.select_dtypes(include=["number"]).columns.tolist())
            # unique and generate histograms until >=10
            all_nums = list(dict.fromkeys(all_nums))
            i = 0
            for col in all_nums:
                if img_counter >= 10:
                    break
                try:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    # pick first dataset that has this column
                    for csv in csv_files:
                        try:
                            df = pd.read_csv(csv, low_memory=False)
                        except Exception:
                            continue
                        if col in df.columns:
                            sns.histplot(df[col].dropna(), bins=40, ax=ax)
                            img_name = f"supp_hist_{i}_{col}.png"
                            save_fig(fig, images_dir / img_name)
                            md_fp.write(f"![supp](./images/{img_name})\n\n")
                            img_counter += 1
                            i += 1
                            break
                except Exception:
                    continue

        md_fp.write("---\n\n# 총평\n\n")
        md_fp.write("자동 EDA가 완료되었습니다. 자세한 전처리 및 추가 분석은 본 리포트를 기반으로 진행하세요.\n")

        # 고객별 매출(거래수/구매수량) 기반 간단 분석 (events.csv 사용)
        events_path = base / "events.csv"
        if events_path.exists():
            try:
                md_fp.write("---\n\n# 고객별 매출(거래수/구매수량) 기반 분석\n\n")
                ev = pd.read_csv(events_path, low_memory=False)
                # transaction 이벤트가 실제 구매를 나타냄
                trans = ev[ev['event'] == 'transaction'].copy()

                # 고객별 거래수 (고유 transactionid 수) 및 구매수량 (transaction 이벤트 행 수)
                # transactionid가 NaN일 수 있으므로 처리
                def unique_count(x):
                    return x.nunique(dropna=True)

                cust = trans.groupby('visitorid').agg(
                    transactions=('transactionid', unique_count),
                    items_purchased=('itemid', 'count')
                ).reset_index()

                # 요약 통계
                md_fp.write("## 고객별 요약 통계\n\n")
                write_code_block(md_fp, 'customers describe', cust[['transactions', 'items_purchased']].describe().to_string())

                # 상위 고객 목록
                top_items = cust.sort_values('items_purchased', ascending=False).head(20)
                top_trans = cust.sort_values('transactions', ascending=False).head(20)

                write_code_block(md_fp, '구매수량 상위 20 고객 (visitorid, transactions, items_purchased)', top_items.to_string(index=False))
                write_code_block(md_fp, '거래수 상위 20 고객 (visitorid, transactions, items_purchased)', top_trans.to_string(index=False))

                # 시각화: 상위 20 고객 (items_purchased)
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.barplot(x=top_items['items_purchased'], y=top_items['visitorid'].astype(str), ax=ax)
                ax.set_title('구매수량 상위 20 고객')
                img_name = 'customers_top_items.png'
                save_fig(fig, images_dir / img_name)
                md_fp.write(f"![top_items](./images/{img_name})\n\n")

                # 시각화: 상위 20 고객 (transactions)
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.barplot(x=top_trans['transactions'], y=top_trans['visitorid'].astype(str), ax=ax)
                ax.set_title('거래수 상위 20 고객')
                img_name = 'customers_top_transactions.png'
                save_fig(fig, images_dir / img_name)
                md_fp.write(f"![top_transactions](./images/{img_name})\n\n")

                # 고객 세그먼트(예: 구매수량 기준 그룹화)
                cust['segment_items'] = pd.qcut(cust['items_purchased'].replace(0, 1), q=4, duplicates='drop')
                seg = cust.groupby('segment_items').agg(
                    customers=('visitorid', 'count'),
                    total_items=('items_purchased', 'sum'),
                    avg_items=('items_purchased', 'mean')
                )
                write_code_block(md_fp, '구매수량 기반 세그먼트 요약', seg.to_string())

                md_fp.write('### 간단 해석\n\n')
                md_fp.write(textwrap.dedent('''
                - 본 데이터셋에는 직접적인 결제 금액(amount) 컬럼이 존재하지 않습니다. 따라서 '구매수량(items_purchased)'과 '거래수(transactions)'를 매출의 대체 지표로 사용했습니다.
                - 구매수량 상위 고객은 상위 20명에 대해 시각화되어 있으며, 실제 금액 기반 분석이 필요하면 주문-상품 가격 정보를 포함한 추가 데이터(예: order_items, payments)가 필요합니다.
                - 세그먼트(사분위수 기준)는 고객군별 구매 집중도를 파악하는 데 유용합니다. 상위 세그먼트가 전체 구매량을 얼마만큼 차지하는지 추가 분석을 권장합니다.
                ''') )
            except Exception as e:
                md_fp.write(f"고객별 분석 중 오류 발생: {e}\n\n")


if __name__ == '__main__':
    main()
