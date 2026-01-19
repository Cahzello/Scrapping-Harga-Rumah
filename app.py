# app.py
import streamlit as st
from streamlit_folium import st_folium

# Import modul
import data_loader
import processor
import visualizer

def main():
    st.set_page_config(page_title="Peta Affordability Indonesia", layout="wide")
    st.title("🇮🇩 Peta Keterjangkauan Rumah per Provinsi")
    st.markdown("Menggunakan data **UMP Official (CSV)** dan GeoJSON.")

    # 1. Load Data
    with st.spinner("Menyiapkan data..."):
        # Load Peta
        geojson_data = data_loader.load_geojson()
        
        # Load UMP dari CSV
        ump_dict = data_loader.load_ump_from_csv()
        
        # Tampilkan info jika berhasil load CSV
        if not ump_dict:
            st.warning("Data UMP kosong. Pastikan file CSV ada dan formatnya benar.")
            

    if geojson_data and ump_dict:
        # 2. Scrap & Process
        # Kirim ump_dict ke fungsi scraping untuk filter provinsi
        raw_data = data_loader.scrape_property_data(geojson_data, ump_dict)
        
        # Kirim ump_dict ke processor untuk perhitungan
        df_summary, df_raw = processor.process_data(raw_data, ump_dict)
        
        if not df_summary.empty:
            # 3. Layout Dashboard
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Analisis Data")
                st.dataframe(df_summary[['provinsi', 'ump_display', 'info_beli']], width='stretch')
                
                fig = visualizer.create_bar_chart(df_summary)
                st.pyplot(fig)
            
            with col2:
                st.subheader("Peta Persebaran")
                map_obj = visualizer.create_geojson_map(df_summary, geojson_data)
                st_folium(map_obj, width=None, height=500)
        else:
            st.error("Tidak ada data provinsi yang cocok antara CSV dan GeoJSON. Cek ejaan nama provinsi.")
            
        # debugging(geojson_data, ump_dict)
    else:
        st.stop()

def debugging(geojson_data, ump_dict):
    
    with st.expander("🕵️ DIAGNOSA: Cek Data Provinsi yang Hilang"):
        # 1. Ambil semua nama provinsi dari Peta (GeoJSON)
        nama_di_peta = set()
        for f in geojson_data['features']:
            # Cek berbagai kemungkinan key nama properti
            props = f['properties']
            nama = props.get('Propinsi') or props.get('PROVINSI') or props.get('NAME_1')
            if nama:
                nama_di_peta.add(str(nama).upper())
        
        # 2. Ambil semua nama dari CSV UMP
        nama_di_csv = set(ump_dict.keys())
        
        # 3. Cari yang Hilang
        hilang_karena_nama_beda = nama_di_csv - nama_di_peta
        
        st.write(f"Total Provinsi di CSV: **{len(nama_di_csv)}**")
        st.write(f"Total Provinsi di Peta: **{len(nama_di_peta)}**")
        st.write(f"Data yang Match: **{len(nama_di_csv.intersection(nama_di_peta))}**")
        
        if hilang_karena_nama_beda:
            st.error(f"❌ {len(hilang_karena_nama_beda)} Provinsi ada di CSV tapi TIDAK DITEMUKAN di Peta:")
            st.write(list(hilang_karena_nama_beda))
            st.info("💡 Solusi: Samakan penulisan di CSV dengan nama yang ada di Peta, atau ganti URL GeoJSON yang lebih lengkap.")
    

if __name__ == "__main__":
    main()