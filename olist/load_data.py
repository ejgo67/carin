import pandas as pd
import os

def load_datasets(base_path='./olist'):
    """
    Olist 데이터셋을 로드하는 함수.
    
    Args:
        base_path (str): 데이터셋 파일들이 위치한 기본 경로.
        
    Returns:
        dict: 데이터프레임들을 담고 있는 딕셔너리.
    """
    datasets = {}
    
    # 데이터셋 파일 경로
    file_paths = {
        'customers': os.path.join(base_path, 'olist_customers_dataset.csv'),
        'geolocation': os.path.join(base_path, 'olist_geolocation_dataset.csv'),
        'order_items': os.path.join(base_path, 'olist_order_items_dataset.csv'),
        'order_payments': os.path.join(base_path, 'olist_order_payments_dataset.csv'),
        'order_reviews': os.path.join(base_path, 'olist_order_reviews_dataset.csv'),
        'orders': os.path.join(base_path, 'olist_orders_dataset.csv'),
        'products': os.path.join(base_path, 'olist_products_dataset.csv'),
        'sellers': os.path.join(base_path, 'olist_sellers_dataset.csv'),
        'category_translation': os.path.join(base_path, 'product_category_name_translation.csv')
    }
    
    for name, path in file_paths.items():
        if os.path.exists(path):
            datasets[name] = pd.read_csv(path)
            print(f"Loaded {name}_dataset.csv")
        else:
            print(f"Warning: {name}_dataset.csv not found at {path}")
            
    return datasets

if __name__ == '__main__':
    # 테스트를 위해 데이터 로드 함수 실행
    olist_datasets = load_datasets()
    for name, df in olist_datasets.items():
        print(f"\nDataset: {name}, Shape: {df.shape}")
        print(df.head())
