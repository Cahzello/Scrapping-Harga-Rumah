# data_loader.py
import requests
import pandas as pd
import random
import streamlit as st
import re
from config import GEOJSON_URL, UMP_CSV_PATH

@st.cache_data
def load_geojson():
    """Download data batas wilayah (Polygon) dari GitHub"""
    try:
        # Tambahkan headers agar tidak ditolak GitHub
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(GEOJSON_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Gagal download GeoJSON. Status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error GeoJSON: {e}")
        return None

# @st.cache_data
def load_ump_from_csv():
    """Membaca file CSV UMP"""
    try:
        df = pd.read_csv(UMP_CSV_PATH, sep=';') 

        if len(df.columns) < 3:
            st.error("Format CSV salah. Pastikan minimal ada kolom No, Provinsi, dan Upah.")
            return {}

        col_provinsi = df.columns[1] 
        col_upah = df.columns[2]

        ump_dict = {}

        for _, row in df.iterrows():
            raw_prov = str(row[col_provinsi])
            raw_upah = str(row[col_upah])
            
            if raw_prov.lower() in ['nan', 'rata-rata', 'nat'] or raw_prov.strip() == '':
                continue

            # Normalisasi: UPPERCASE & Hapus Titik (DI. YOGYAKARTA -> DI YOGYAKARTA)
            clean_prov = raw_prov.upper().strip().replace('.', '')
            
            # Fix Khusus: Jika di CSV "DKI JAKARTA" tapi di Peta "DAERAH KHUSUS IBUKOTA JAKARTA"
            # (Opsional: tambahkan mapping manual jika masih ada yang tidak match)
            
            clean_upah = re.sub(r'[^\d]', '', raw_upah)

            try:
                if clean_upah:
                    val = int(clean_upah)
                    ump_dict[clean_prov] = val
            except ValueError:
                continue

        return ump_dict

    except Exception as e:
        st.error(f"Gagal membaca CSV: {e}")
        return {}

@st.cache_data
def scrape_property_data(geojson_data, ump_data):
    data_mock = []
    
    if not geojson_data or not ump_data:
            return []

    for feature in geojson_data['features']:
        props = feature['properties']
        
        # --- UPDATE DI SINI ---
        # GeoJSON baru mungkin pakai 'Provinsi', yang lama 'Propinsi'. Kita cek semua.
        nama_prov_geojson = props.get('PROVINSI') or \
                            props.get('Provinsi') or \
                            props.get('Propinsi')
                            
        if not nama_prov_geojson:
            continue

        # Normalisasi nama dari GeoJSON
        nama_key = str(nama_prov_geojson).upper().strip()
        
        # Hapus kata-kata awalan jika perlu agar cocok dengan CSV
        # Misal: "PROVINSI JAWA BARAT" -> "JAWA BARAT"
        nama_key = nama_key.replace('PROVINSI ', '')

        # Cek apakah provinsi ini ada di data UMP
        if nama_key in ump_data:
            
            geom = feature['geometry']
            # Handle Polygon & MultiPolygon
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]
            elif geom['type'] == 'MultiPolygon':
                # Ambil polygon terbesar atau pertama
                coords = geom['coordinates'][0][0]
            else:
                continue
            
            # Cari titik tengah (centroid) sederhana
            try:
                lons = [c[0] for c in coords]
                lats = [c[1] for c in coords]
                center_lon = sum(lons) / len(lons)
                center_lat = sum(lats) / len(lats)

                # Generate 15 rumah dummy
                for i in range(15):
                    lat_rnd = center_lat + random.uniform(-0.1, 0.1)
                    lon_rnd = center_lon + random.uniform(-0.1, 0.1)
                    
                    if "JAKARTA" in nama_key:
                        harga = random.randint(800, 15000)
                    else:
                        harga = random.randint(200, 4000)
                    
                    data_mock.append({
                        "judul": f"Rumah {nama_key} #{i+1}",
                        "provinsi": nama_key,
                        "harga_raw": harga * 1000000,
                        "latitude": lat_rnd,
                        "longitude": lon_rnd
                    })
            except:
                continue
    
    return data_mock