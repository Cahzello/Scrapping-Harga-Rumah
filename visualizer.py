# visualizer.py
import matplotlib.pyplot as plt
import folium

def create_bar_chart(df_summary):
    """Membuat grafik batang Matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Warna dinamis: Merah jika lama, Hijau jika cepat
    colors = plt.cm.RdYlGn_r(df_summary['tahun_beli'] / df_summary['tahun_beli'].max())
    
    bars = ax.bar(df_summary['provinsi'], df_summary['tahun_beli'], color=colors)
    ax.set_title("Lama Kerja untuk Beli Rumah (Tahun)")
    ax.set_ylabel("Tahun")
    ax.set_xticklabels(df_summary['provinsi'], rotation=45)
    ax.bar_label(bars, fmt='%.1f th')
    
    plt.tight_layout()
    return fig

def create_geojson_map(df_summary, geojson_data):
    """Membuat peta Folium dengan layer GeoJSON"""
    m = folium.Map(location=[-2.5, 118.0], zoom_start=5)

    # Dictionary untuk lookup warna agar cepat
    style_dict = {}
    for _, row in df_summary.iterrows():
        warna = "red" if row['tahun_beli'] > 20 else "orange" if row['tahun_beli'] > 10 else "green"
        style_dict[row['provinsi']] = {
            "color": warna,
            "info": row['info_beli'],
        }

    def style_function(feature):
        nama_prov = feature['properties']['Propinsi']
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
            fields=['Propinsi'],
            aliases=['Provinsi: '],
            localize=True
        )
    ).add_to(m)

    return m