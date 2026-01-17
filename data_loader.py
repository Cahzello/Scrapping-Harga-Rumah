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
        response = requests.get(GEOJSON_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Gagal download GeoJSON. Status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error GeoJSON: {e}")
        return None

@st.cache_data
def load_ump_from_csv():
    """Membaca file CSV UMP dengan handling khusus untuk format Anda"""
    try:
        # 1. BACA CSV DENGAN SKIPROWS
        # Kita lewati 3 baris teratas agar header tabel ("No", "Provinsi", dll) terbaca sebagai header
        df = pd.read_csv(UMP_CSV_PATH, sep=';') 
        print(df)
        print(len(df.columns))

        # 2. IDENTIFIKASI KOLOM (Berdasarkan posisi, bukan nama, agar lebih aman)
        # Asumsi struktur: Kolom ke-2 adalah PROVINSI, Kolom ke-3 adalah NILAI
        # (Indeks 0=No, 1=Provinsi, 2=Upah)
        if len(df.columns) < 3:
            st.error("Format CSV salah. Pastikan minimal ada kolom No, Provinsi, dan Upah.")
            return {}

        # Ambil kolom berdasarkan indeks posisi
        col_provinsi = df.columns[1] 
        col_upah = df.columns[2]

        ump_dict = {}

        for _, row in df.iterrows():
            # Ambil raw data
            raw_prov = str(row[col_provinsi])
            raw_upah = str(row[col_upah])

            # --- CLEANING DATA ---
            
            # A. Skip baris sampah (NaN, "Rata-Rata", atau baris kosong)
            if raw_prov.lower() in ['nan', 'rata-rata', 'nat'] or raw_prov.strip() == '':
                continue

            # B. Normalisasi Nama Provinsi
            # Ubah jadi UPPERCASE
            clean_prov = raw_prov.upper().strip()
            # Hapus titik (misal: "DI. YOGYAKARTA" jadi "DI YOGYAKARTA")
            clean_prov = clean_prov.replace('.', '')
            # Fix khusus untuk Papua Barat Daya dll jika perlu (sesuaikan dengan GeoJSON)
            # GeoJSON biasanya: "DKI JAKARTA", "DI YOGYAKARTA", "BANGKA BELITUNG"
            
            # C. Bersihkan Angka Rupiah
            # Hapus "Rp", titik ribuan, spasi
            clean_upah = re.sub(r'[^\d]', '', raw_upah) # Hanya ambil digit angka

            try:
                if clean_upah:
                    val = int(clean_upah)
                    ump_dict[clean_prov] = val
            except ValueError:
                continue

        return ump_dict

    except FileNotFoundError:
        st.error(f"File '{UMP_CSV_PATH}' tidak ditemukan.")
        return {}
    except Exception as e:
        st.error(f"Gagal membaca CSV: {e}")
        return {}

@st.cache_data
def scrape_property_data(geojson_data, ump_data):
    """
    Generate data properti dummy.
    Menerima ump_data yang sudah bersih.
    """
    data_mock = []
    
    if not geojson_data or not ump_data:
        return []

    for feature in geojson_data['features']:
        props = feature['properties']
        nama_prov_geojson = props.get('Propinsi') 
        
        if not nama_prov_geojson:
            continue

        # Normalisasi nama dari GeoJSON agar cocok dengan dictionary UMP
        nama_key = str(nama_prov_geojson).upper().strip()

        # Cek apakah provinsi ini ada di data UMP kita
        if nama_key in ump_data:
            
            # Ambil polygon & titik tengah
            geom = feature['geometry']
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]
            elif geom['type'] == 'MultiPolygon':
                coords = geom['coordinates'][0][0]
            else:
                continue
            
            # Hitung centroid
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            center_lon = sum(lons) / len(lons)
            center_lat = sum(lats) / len(lats)

            # Generate 15 rumah dummy
            for i in range(15):
                lat_rnd = center_lat + random.uniform(-0.2, 0.2)
                lon_rnd = center_lon + random.uniform(-0.2, 0.2)
                
                # Simulasi harga (Jakarta lebih mahal)
                if "JAKARTA" in nama_key:
                    harga = random.randint(9000, 15000)
                else:
                    harga = random.randint(200, 4000)
                
                data_mock.append({
                    "judul": f"Rumah {nama_prov_geojson} #{i+1}",
                    "provinsi": nama_key, # Simpan nama yang sudah dinormalisasi
                    "harga_raw": harga * 1000000,
                    "latitude": lat_rnd,
                    "longitude": lon_rnd
                })
    
    return data_mock