# data_loader.py
import requests
import random
import streamlit as st
from config import GEOJSON_URL, UMP_DATA

@st.cache_data
def load_geojson():
    """Download data batas wilayah (Polygon) dari GitHub"""
    try:
        response = requests.get(GEOJSON_URL)
        data = response.json()
        return data
    except Exception as e:
        st.error(f"Gagal mengambil data GeoJSON: {e}")
        return None

@st.cache_data
def scrape_property_data(geojson_data):
    """Simulasi scraping data properti berdasarkan lokasi GeoJSON"""
    data_mock = []
    
    if not geojson_data:
        return []

    for feature in geojson_data['features']:
        props = feature['properties']
        nama_prov = props.get('Propinsi') 
        
        # Hanya buat data jika provinsi ada di daftar UMP kita
        if nama_prov in UMP_DATA:
            
            # Ambil geometry untuk mencari titik tengah kasar
            geom = feature['geometry']
            if geom['type'] == 'Polygon':
                coords = geom['coordinates'][0]
            elif geom['type'] == 'MultiPolygon':
                coords = geom['coordinates'][0][0]
            else:
                continue
                
            # Hitung centroid sederhana
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            center_lon = sum(lons) / len(lons)
            center_lat = sum(lats) / len(lats)

            # Generate 15 rumah dummy
            for i in range(15):
                lat_rnd = center_lat + random.uniform(-0.3, 0.3)
                lon_rnd = center_lon + random.uniform(-0.3, 0.3)
                
                # Logika harga: Jakarta lebih mahal
                if nama_prov == "DKI JAKARTA":
                    harga = random.randint(800, 15000)
                else:
                    harga = random.randint(200, 4000)
                
                data_mock.append({
                    "judul": f"Rumah {nama_prov} #{i+1}",
                    "provinsi": nama_prov,
                    "harga_raw": harga * 1000000,
                    "latitude": lat_rnd,
                    "longitude": lon_rnd
                })
    
    return data_mock