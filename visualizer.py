# visualizer.py
import matplotlib.pyplot as plt
import folium

def create_bar_chart(df_summary):
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.RdYlGn_r(df_summary['tahun_beli'] / df_summary['tahun_beli'].max())
    
    bars = ax.bar(df_summary['provinsi'], df_summary['tahun_beli'], color=colors)
    ax.set_title("Lama Kerja untuk Beli Rumah (Tahun)")
    ax.set_ylabel("Tahun")
    ax.set_xticklabels(df_summary['provinsi'], rotation=90) # Rotasi 90 biar muat
    ax.bar_label(bars, fmt='%.1f th')
    
    plt.tight_layout()
    return fig

def create_geojson_map(df_summary, geojson_data):
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5)

    style_dict = {}
    for _, row in df_summary.iterrows():
        warna = "red" if row['tahun_beli'] > 20 else "orange" if row['tahun_beli'] > 10 else "green"
        style_dict[row['provinsi']] = {
            "color": warna,
            "info": row['info_beli'],
        }

    def style_function(feature):
        # --- PERBAIKAN 1: Ambil key 'PROVINSI' ---
        props = feature['properties']
        # Prioritaskan 'PROVINSI' (huruf besar) sesuai error log Anda
        nama_raw = props.get('PROVINSI') or props.get('Provinsi') or props.get('Propinsi')
        
        # Normalisasi nama agar cocok dengan CSV
        nama_prov = str(nama_raw).upper().strip().replace('PROVINSI ', '') if nama_raw else ""
        
        default_style = {'fillColor': 'gray', 'color': 'gray', 'fillOpacity': 0.1, 'weight': 1}
        
        if nama_prov in style_dict:
            return {
                'fillColor': style_dict[nama_prov]['color'],
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            }
        return default_style

    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            # --- PERBAIKAN 2: Ganti 'Propinsi' jadi 'PROVINSI' ---
            # Harus sama persis dengan yang ada di pesan error: ('KODE_PROV', 'PROVINSI')
            fields=['PROVINSI'],
            aliases=['Provinsi: '],
            localize=True
        )
    ).add_to(m)

    return m