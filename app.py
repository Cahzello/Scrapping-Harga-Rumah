import streamlit as st
from streamlit_folium import st_folium
import data_loader
import processor
import visualizer

def main():
    st.set_page_config(page_title="Peta Affordability Indonesia", layout="wide")
    st.title("🇮🇩 Peta Keterjangkauan Rumah per Provinsi")
    st.markdown("Menggunakan **GeoJSON** otomatis dan Modular Python.")

    # 1. Load Data
    with st.spinner("Mengambil data peta..."):
        geojson_data = data_loader.load_geojson()
    
    if geojson_data:
        # 2. Scrap & Process
        raw_data = data_loader.scrape_property_data(geojson_data)
        df_summary, df_raw = processor.process_data(raw_data)

        if not df_summary.empty:
            # 3. Layout Dashboard
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Analisis Data")
                st.dataframe(df_summary[['provinsi', 'ump_display', 'info_beli']], use_container_width=True)
                
                # Panggil visualizer
                fig = visualizer.create_bar_chart(df_summary)
                st.pyplot(fig)
            
            with col2:
                st.subheader("Peta Persebaran (GeoJSON)")
                # Panggil visualizer
                map_obj = visualizer.create_geojson_map(df_summary, geojson_data)
                st_folium(map_obj, width=None, height=500)
        else:
            st.warning("Data kosong atau tidak cocok.")
    else:
        st.stop()

if __name__ == "__main__":
    main()