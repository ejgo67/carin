
import pandas as pd
import os

def merge_and_deduplicate_olist_data():
    """
    Olist 데이터셋의 여러 CSV 파일들을 병합하고 중복을 제거하여
    하나의 CSV 파일로 저장합니다.
    """
    
    # 데이터 파일이 있는 디렉토리
    data_dir = './data'

    # 각 CSV 파일 불러오기
    try:
        customers = pd.read_csv(os.path.join(data_dir, 'olist_customers_dataset.csv'))
        geolocation = pd.read_csv(os.path.join(data_dir, 'olist_geolocation_dataset.csv'))
        order_items = pd.read_csv(os.path.join(data_dir, 'olist_order_items_dataset.csv'))
        order_payments = pd.read_csv(os.path.join(data_dir, 'olist_order_payments_dataset.csv'))
        order_reviews = pd.read_csv(os.path.join(data_dir, 'olist_order_reviews_dataset.csv'))
        orders = pd.read_csv(os.path.join(data_dir, 'olist_orders_dataset.csv'))
        products = pd.read_csv(os.path.join(data_dir, 'olist_products_dataset.csv'))
        sellers = pd.read_csv(os.path.join(data_dir, 'olist_sellers_dataset.csv'))
        category_translation = pd.read_csv(os.path.join(data_dir, 'product_category_name_translation.csv'))
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure all Olist CSV files are in the 'data' directory.")
        return

    # --- 데이터 병합 (Merge) ---
    # 1. orders & customers
    merged_df = pd.merge(orders, customers, on='customer_id', how='left')

    # 2. merged_df & order_items
    merged_df = pd.merge(merged_df, order_items, on='order_id', how='left')

    # 3. merged_df & products
    merged_df = pd.merge(merged_df, products, on='product_id', how='left')

    # 4. merged_df & product_category_name_translation
    merged_df = pd.merge(merged_df, category_translation, on='product_category_name', how='left')
    
    # 5. merged_df & order_payments
    merged_df = pd.merge(merged_df, order_payments, on='order_id', how='left')

    # 6. merged_df & order_reviews
    merged_df = pd.merge(merged_df, order_reviews, on='order_id', how='left')
    
    # 7. merged_df & sellers
    merged_df = pd.merge(merged_df, sellers, on='seller_id', how='left')

    # --- 중복 제거 (Deduplication) ---
    # order_id와 order_item_id를 기준으로 중복을 확인합니다.
    # 여러 지불 수단이나 리뷰 때문에 중복이 발생할 수 있으므로, 대표적인 값만 남깁니다.
    # 여기서는 간단하게 첫 번째 행을 기준으로 중복을 제거합니다.
    merged_df.drop_duplicates(subset=['order_id', 'order_item_id'], inplace=True)
    
    # --- 결과 저장 ---
    output_path = os.path.join(data_dir, 'olist_merged_dataset_deduped.csv')
    merged_df.to_csv(output_path, index=False)
    
    print(f"데이터 병합 및 중복 제거가 완료되었습니다. 결과가 '{output_path}' 파일에 저장되었습니다.")

if __name__ == '__main__':
    merge_and_deduplicate_olist_data()
