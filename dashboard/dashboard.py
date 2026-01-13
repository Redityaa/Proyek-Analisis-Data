import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import os

# ==============================================================================
# 1. KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ==============================================================================
# 2. MEMUAT DATA
# ==============================================================================
@st.cache_data
def load_data():
    # Menggunakan absolute path agar aman saat deploy
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "main_data.csv")
    
    data = pd.read_csv(csv_path)
    data['datetime'] = pd.to_datetime(data['datetime'])
    return data

df = load_data()

# ==============================================================================
# 3. FUNGSI TAMBAHAN (CLUSTERING)
# ==============================================================================
def categorize_air_quality(pm25):
    if pm25 <= 50:
        return 'Good'
    elif pm25 <= 100:
        return 'Moderate'
    elif pm25 <= 150:
        return 'Unhealthy'
    elif pm25 <= 250:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

# Terapkan kategorisasi ke dataframe awal
df['quality_category'] = df['PM2.5'].apply(categorize_air_quality)

# Definisi urutan kategori untuk visualisasi
cat_order = ['Good', 'Moderate', 'Unhealthy', 'Very Unhealthy', 'Hazardous']

# ==============================================================================
# 4. SIDEBAR (FILTER)
# ==============================================================================
st.sidebar.header("Filter Data")

# Filter Rentang Waktu
min_date = df['datetime'].min().date()
max_date = df['datetime'].max().date()

try:
    start_date, end_date = st.sidebar.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
except ValueError:
    st.error("Mohon pilih rentang tanggal yang valid.")
    st.stop()

# Filter Stasiun
station_list = df['station'].unique().tolist()
selected_station = st.sidebar.multiselect(
    label="Pilih Stasiun",
    options=station_list,
    default=station_list  # Default memilih semua
)

# Terapkan Filter
main_df = df[
    (df['datetime'].dt.date >= start_date) &
    (df['datetime'].dt.date <= end_date) &
    (df['station'].isin(selected_station))
]

if main_df.empty:
    st.warning("Tidak ada data yang tersedia untuk filter yang dipilih.")
    st.stop()

# ==============================================================================
# 5. DASHBOARD MAIN CONTENT
# ==============================================================================
st.title("🌍 Dashboard Analisis Kualitas Udara")
st.markdown("""
Dashboard ini menyajikan analisis mendalam mengenai kualitas udara, mencakup tren musiman, 
segmentasi kategori bahaya (Clustering), serta identifikasi stasiun paling kritis menggunakan metode RFM.
""")
st.markdown("---")

# --- BAGIAN A: KEY METRICS (KPI) ---
col1, col2, col3, col4 = st.columns(4)

avg_pm25 = main_df['PM2.5'].mean()
max_pm25 = main_df['PM2.5'].max()
dominant_category = main_df['quality_category'].mode()[0]
total_hazardous = main_df[main_df['quality_category'] == 'Hazardous'].shape[0]

with col1:
    st.metric("Rata-rata PM2.5", value=f"{avg_pm25:.2f} µg/m³")
with col2:
    st.metric("Polusi Tertinggi", value=f"{max_pm25:.0f} µg/m³")
with col3:
    st.metric("Kategori Dominan", value=f"{dominant_category}")
with col4:
    st.metric("Jam 'Hazardous'", value=f"{total_hazardous} Jam")

st.markdown("---")

# --- BAGIAN B: PERTANYAAN 1 (TREN & LOKASI) ---
st.header("1. Analisis Tren & Geospasial")
st.markdown("**Bagaimana tren tingkat polusi udara dari waktu ke waktu?**")

col_map, col_trend = st.columns([1, 1.5])

with col_map:
    st.subheader("Peta Persebaran Stasiun")
    map_data = main_df.groupby(['station', 'lat', 'lon'])['PM2.5'].mean().reset_index()
    fig_map = px.scatter_mapbox(
        map_data, lat="lat", lon="lon", hover_name="station",
        size="PM2.5", color="PM2.5",
        color_continuous_scale=px.colors.cyclical.IceFire,
        size_max=20, zoom=8, mapbox_style="carto-positron",
        title="Rata-rata PM2.5 per Lokasi"
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_trend:
    st.subheader("Tren Polusi Bulanan")
    monthly_trend = main_df.set_index('datetime').resample('M')['PM2.5'].mean().reset_index()
    fig_trend = px.line(
        monthly_trend, x='datetime', y='PM2.5', markers=True,
        title="Fluktuasi PM2.5 Sepanjang Waktu", template='plotly_white'
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# --- BAGIAN C: CLUSTERING (KATEGORI & CUACA) ---
st.header("2. Segmentasi Kualitas Udara (Clustering)")
st.markdown("**Bagaimana proporsi kategori kualitas udara dan profil cuaca saat kondisi berbahaya?**")

col_pie, col_weather = st.columns(2)

with col_pie:
    st.subheader("Proporsi Kategori Udara")
    cat_counts = main_df['quality_category'].value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']
    
    fig_pie = px.pie(
        cat_counts, names='Category', values='Count',
        color='Category',
        category_orders={'Category': cat_order},
        color_discrete_map={
            'Good': 'green', 'Moderate': 'yellow', 
            'Unhealthy': 'orange', 'Very Unhealthy': 'red', 'Hazardous': 'purple'
        },
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_weather:
    st.subheader("Profil Cuaca saat 'Hazardous'")
    haz_df = main_df[main_df['quality_category'] == 'Hazardous']
    
    if not haz_df.empty:
        # Menampilkan rata-rata cuaca saat kondisi berbahaya
        avg_haz = haz_df[['TEMP', 'WSPM', 'PRES', 'DEWP']].mean().to_frame(name='Rata-rata')
        st.dataframe(avg_haz.T)
        st.caption("Insight: Saat kategori Hazardous terjadi, perhatikan bahwa kecepatan angin (WSPM) cenderung rendah.")
    else:
        st.info("Tidak ada data kategori 'Hazardous' pada rentang waktu ini.")

st.markdown("---")

# --- BAGIAN D: RFM ANALYSIS (RANKING STASIUN) ---
st.header("3. Identifikasi Zona Merah (RFM Analysis)")
st.markdown("**Stasiun mana yang paling kritis berdasarkan frekuensi kejadian polusi ekstrem?**")

# Threshold untuk 'Bad Air' (Frequency) kita set PM2.5 > 150 (Unhealthy ke atas)
threshold_bad = 150

rfm_data = main_df.groupby('station').agg({
    'PM2.5': 'mean',              # Magnitude (Rata-rata keparahan)
    'datetime': lambda x: x.max() # Recency (Data terakhir)
}).reset_index()
rfm_data.rename(columns={'PM2.5': 'Magnitude_Avg'}, inplace=True)

# Hitung Frequency (Berapa kali PM2.5 > 150)
bad_air_freq = main_df[main_df['PM2.5'] > threshold_bad].groupby('station')['PM2.5'].count().reset_index()
bad_air_freq.columns = ['station', 'Frequency_Bad_Air']

# Merge data
rfm_final = pd.merge(rfm_data, bad_air_freq, on='station', how='left')
rfm_final['Frequency_Bad_Air'] = rfm_final['Frequency_Bad_Air'].fillna(0)

col_rfm_chart, col_rfm_table = st.columns([2, 1])

with col_rfm_chart:
    st.subheader("Peta Zona Kritis (Scatter Plot)")
    fig_rfm = px.scatter(
        rfm_final,
        x='Magnitude_Avg',
        y='Frequency_Bad_Air',
        color='station',
        size='Magnitude_Avg',
        hover_name='station',
        title="Frequency (Seringnya Polusi) vs Magnitude (Rata-rata Polusi)",
        labels={'Magnitude_Avg': 'Rata-rata PM2.5 (Magnitude)', 'Frequency_Bad_Air': 'Jumlah Kejadian > 150 (Frequency)'}
    )
    # Menambahkan garis kuadran rata-rata
    fig_rfm.add_vline(x=rfm_final['Magnitude_Avg'].mean(), line_dash="dash", line_color="gray")
    fig_rfm.add_hline(y=rfm_final['Frequency_Bad_Air'].mean(), line_dash="dash", line_color="gray")
    
    st.plotly_chart(fig_rfm, use_container_width=True)
    st.caption("Kuadran Kanan-Atas adalah 'Zona Merah' (Sering & Parah).")

with col_rfm_table:
    st.subheader("Top 5 Stasiun Kritis")
    top_stations = rfm_final.sort_values(by=['Frequency_Bad_Air', 'Magnitude_Avg'], ascending=False).head(5)
    st.table(top_stations[['station', 'Frequency_Bad_Air', 'Magnitude_Avg']])

st.markdown("---")

# --- BAGIAN E: KORELASI CUACA ---
st.header("4. Hubungan Faktor Meteorologi")
st.markdown("**Bagaimana pengaruh suhu dan angin terhadap tingkat polusi?**")

col_corr1, col_corr2 = st.columns(2)

# Sample data agar ringan saat plotting
sample_df = main_df.sample(n=min(2000, len(main_df)), random_state=42)

with col_corr1:
    fig_temp = px.scatter(
        sample_df, x='TEMP', y='PM2.5', color='quality_category',
        title="Suhu vs PM2.5", color_discrete_map={
            'Good': 'green', 'Moderate': 'yellow', 'Unhealthy': 'orange', 
            'Very Unhealthy': 'red', 'Hazardous': 'purple'
        }
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with col_corr2:
    fig_wind = px.scatter(
        sample_df, x='WSPM', y='PM2.5', color='quality_category',
        title="Kecepatan Angin vs PM2.5", color_discrete_map={
            'Good': 'green', 'Moderate': 'yellow', 'Unhealthy': 'orange', 
            'Very Unhealthy': 'red', 'Hazardous': 'purple'
        }
    )
    st.plotly_chart(fig_wind, use_container_width=True)

st.caption("Copyright © 2025 - Air Quality Analysis Project by Redityaa")