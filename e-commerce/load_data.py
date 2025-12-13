
import pandas as pd
import glob
import os

def load_datasets(path):
    """
    지정된 경로에서 여러 CSV 파일을 로드하여 데이터프레임 딕셔너리를 반환합니다.
    """
    all_files = glob.glob(path + "/*.csv")
    
    data_frames = {}
    for filename in all_files:
        basename = os.path.basename(filename)
        if basename == 'product_category_name_translation.csv':
            df_name = 'product_category_name_translation'
        else:
            df_name = basename.replace('_dataset.csv', '')
        
        data_frames[df_name] = pd.read_csv(filename)
            
    return data_frames

if __name__ == '__main__':
    datasets = load_datasets('e-commerce')
    for name, df in datasets.items():
        print(f"--- {name} ---")
        print(df.head())
        print()
