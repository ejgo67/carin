
import pandas as pd
import glob
import os

def load_datasets(path):
    """
    지정된 경로에서 여러 CSV 파일을 로드하여 데이터프레임 딕셔너리를 반환합니다.
    파일 이름 대신 컬럼 내용으로 파일을 식별하여 안정성을 높입니다.
    """
    all_files = glob.glob(path + "/*.csv")
    data_frames = {}

    for filename in all_files:
        df = pd.read_csv(filename)
        cols = set(df.columns)
        
        # 컬럼 내용으로 데이터프레임 식별
        if 'order_status' in cols and 'customer_id' in cols:
            df_name = 'olist_orders'
        elif 'payment_sequential' in cols and 'payment_type' in cols:
            df_name = 'olist_order_payments'
        elif 'review_id' in cols and 'review_score' in cols:
            df_name = 'olist_order_reviews'
        elif 'order_item_id' in cols and 'seller_id' in cols:
            df_name = 'olist_order_items'
        elif 'product_name_lenght' in cols and 'product_description_lenght' in cols: # 오타가 있는 컬럼명 사용
            df_name = 'olist_products'
        elif 'customer_unique_id' in cols and 'customer_zip_code_prefix' in cols:
            df_name = 'olist_customers'
        elif 'seller_zip_code_prefix' in cols and 'seller_city' in cols:
            df_name = 'olist_sellers'
        elif 'geolocation_zip_code_prefix' in cols and 'geolocation_lat' in cols:
            df_name = 'olist_geolocation'
        elif 'product_category_name_english' in cols:
            df_name = 'product_category_name_translation'
        else:
            # 식별되지 않은 파일은 건너뛰거나 기본 이름을 사용
            df_name = os.path.basename(filename)

        data_frames[df_name] = df
            
    return data_frames

if __name__ == '__main__':
    datasets = load_datasets('e-commerce')
    for name, df in datasets.items():
        print(f"--- {name} ---")
        print(df.head())
        print()
