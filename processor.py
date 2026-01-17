# processor.py
import pandas as pd

def process_data(raw_data, ump_dict):
    """Mengolah data dengan UMP dari CSV"""
    
    
    if not raw_data:
        return pd.DataFrame(), pd.DataFrame()

    df_properti = pd.DataFrame(raw_data)
    print('df_properti : ',df_properti)
    
    # 1. Rata-rata harga per provinsi
    df_avg = df_properti.groupby('provinsi')['harga_raw'].mean().reset_index()
    # print('df_avg : ',df_avg)
    # 2. Convert Dictionary UMP (dari CSV) ke DataFrame
    df_ump = pd.DataFrame(list(ump_dict.items()), columns=['provinsi', 'ump'])
    # 3. Merge
    df_final = pd.merge(df_avg, df_ump, on='provinsi')
    # print('df_final : ',df_final)
    
    # 4. Hitung Affordability
    df_final['tahun_beli'] = df_final['harga_raw'] / (df_final['ump'] * 12)
    
    # 5. Formatting
    df_final['harga_display'] = df_final['harga_raw'].apply(lambda x: f"Rp {x:,.0f}")
    df_final['ump_display'] = df_final['ump'].apply(lambda x: f"Rp {x:,.0f}")
    df_final['info_beli'] = df_final['tahun_beli'].apply(
    lambda x: f"{int(x*12)//12} tahun {int(x*12)%12} bulan"
    )
    
    return df_final, df_properti
