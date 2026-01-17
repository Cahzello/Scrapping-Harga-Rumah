# processor.py
import pandas as pd
from config import UMP_DATA

def process_data(raw_data):
    """Mengolah data mentah menjadi data statistik yang siap ditampilkan"""
    if not raw_data:
        return pd.DataFrame(), pd.DataFrame()

    df_properti = pd.DataFrame(raw_data)
    
    # 1. Rata-rata harga per provinsi
    df_avg = df_properti.groupby('provinsi')['harga_raw'].mean().reset_index()
    
    # 2. Gabungkan dengan Data UMP
    df_ump = pd.DataFrame(list(UMP_DATA.items()), columns=['provinsi', 'ump'])
    df_final = pd.merge(df_avg, df_ump, on='provinsi')
    
    # 3. Hitung Tahun Beli (Affordability)
    df_final['tahun_beli'] = df_final['harga_raw'] / (df_final['ump'] * 12)
    
    # 4. Formatting String (Untuk keperluan Display)
    df_final['harga_display'] = df_final['harga_raw'].apply(lambda x: f"Rp {x:,.0f}")
    df_final['ump_display'] = df_final['ump'].apply(lambda x: f"Rp {x:,.0f}")
    df_final['info_beli'] = df_final['tahun_beli'].apply(lambda x: f"{x:.1f} Tahun")
    
    return df_final, df_properti