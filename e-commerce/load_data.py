
import pandas as pd
import glob
import os

def load_data(path):
    """
    지정된 경로에서 여러 CSV 파일을 로드하여 단일 데이터프레임으로 병합합니다.
    """
    all_files = glob.glob(path + "/*.csv")
    
    data_frames = {}
    for filename in all_files:
        df_name = os.path.basename(filename).replace('olist_', '').replace('_dataset.csv', '')
        if df_name == 'product_category_name_translation':
            translation = pd.read_csv(filename)
            data_frames[df_name] = translation
        else:
            data_frames[df_name] = pd.read_csv(filename)
            
    # Merge dataframes
    df = data_frames['orders'].merge(data_frames['order_items'], on='order_id')
    df = df.merge(data_frames['order_payments'], on='order_id')
    df = df.merge(data_frames['order_reviews'], on='order_id')
    df = df.merge(data_frames['products'], on='product_id')
    df = df.merge(data_frames['customers'], on='customer_id')
    df = df.merge(data_frames['sellers'], on='seller_id')
    
    if 'product_category_name_translation' in data_frames:
        df = df.merge(data_frames['product_category_name_translation'], on='product_category_name')

    return df

if __name__ == '__main__':
    df = load_data('e-commerce')
    print(df.head())
    print(df.info())
