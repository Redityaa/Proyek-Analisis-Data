import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Menggabungkan path direktori dengan nama file CSV
    csv_path = os.path.join(script_dir, "main_data.csv")
    # Membaca data dari file CSV yang sudah bersih
    data = pd.read_csv(csv_path)
    
    # Memastikan kolom datetime bertipe datetime
    data['datetime'] = pd.to_datetime(data['datetime'])
    return data

df = load_data()

# ==============================================================================
# 3. SIDEBAR (FILTER)
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
    default=station_list  # Default memilih semua stasiun
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
# 4. DASHBOARD MAIN CONTENT
# ==============================================================================
st.title("🌍 Dashboard Analisis Kualitas Udara")
st.markdown("""
Dashboard ini menyajikan hasil analisis data kualitas udara, mencakup tren polusi musiman, 
pemetaan lokasi stasiun, serta hubungan antara faktor cuaca dengan tingkat polusi.
""")

st.markdown("---")

# BAGIAN A: KEY METRICS (KPI)
col1, col2, col3, col4 = st.columns(4)

avg_pm25 = main_df['PM2.5'].mean()
avg_temp = main_df['TEMP'].mean()
max_pm25 = main_df['PM2.5'].max()
dominant_station = main_df.loc[main_df['PM2.5'].idxmax(), 'station']

with col1:
    st.metric("Rata-rata PM2.5", value=f"{avg_pm25:.2f} µg/m³")
with col2:
    st.metric("Rata-rata Suhu", value=f"{avg_temp:.1f} °C")
with col3:
    st.metric("Max PM2.5", value=f"{max_pm25:.0f} µg/m³")
with col4:
    st.metric("Lokasi Terburuk", value=f"{dominant_station}")

st.markdown("---")

# BAGIAN B: PERTANYAAN BISNIS 1 (TREN & LOKASI)
st.header("1. Tren Polusi & Sebaran Lokasi")
st.caption("Menjawab Pertanyaan: Bagaimana tren tingkat polusi udara dalam beberapa tahun terakhir dan di mana lokasi terburuknya?")

col_map, col_trend = st.columns([1, 1.5])

with col_map:
    st.subheader("Peta Persebaran Stasiun")
    # Agregasi data untuk peta (rata-rata per stasiun)
    map_data = main_df.groupby(['station', 'lat', 'lon'])['PM2.5'].mean().reset_index()
    
    fig_map = px.scatter_mapbox(
        map_data,
        lat="lat",
        lon="lon",
        hover_name="station",
        size="PM2.5",
        color="PM2.5",
        color_continuous_scale=px.colors.cyclical.IceFire,
        size_max=20,
        zoom=8,
        mapbox_style="carto-positron",
        title="Peta Tingkat Polusi Rata-rata"
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_trend:
    st.subheader("Tren Polusi PM2.5 (Per Bulan)")
    # Resample bulanan untuk grafik garis agar lebih jelas polanya
    monthly_trend = main_df.set_index('datetime').resample('M')['PM2.5'].mean().reset_index()
    
    fig_trend = px.line(
        monthly_trend,
        x='datetime',
        y='PM2.5',
        title='Tren Rata-rata PM2.5 Bulanan',
        markers=True,
        template='plotly_white'
    )
    fig_trend.update_xaxes(title="Waktu")
    fig_trend.update_yaxes(title="PM2.5 (µg/m³)")
    st.plotly_chart(fig_trend, use_container_width=True)

# Visualisasi Ranking Stasiun
st.subheader("Peringkat Stasiun Berdasarkan Tingkat Polusi")
station_rank = main_df.groupby('station')['PM2.5'].mean().sort_values(ascending=False).reset_index()

fig_bar = px.bar(
    station_rank,
    x='PM2.5',
    y='station',
    orientation='h',
    color='PM2.5',
    color_continuous_scale='Reds',
    title="Rata-rata PM2.5 per Stasiun"
)
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# BAGIAN C: PERTANYAAN BISNIS 2 (FAKTOR METEOROLOGI)
st.header("2. Korelasi Faktor Meteorologi")
st.caption("Menjawab Pertanyaan: Apakah terdapat korelasi antara kondisi cuaca (Suhu, Angin) dengan tingkat polusi?")

col_scatter1, col_scatter2 = st.columns(2)

with col_scatter1:
    st.subheader("Hubungan Suhu vs PM2.5")
    # Mengambil sample data agar scatter plot tidak terlalu berat (maks 2000 titik)
    sample_df = main_df.sample(n=min(2000, len(main_df)), random_state=42)
    
    fig_temp = px.scatter(
        sample_df,
        x='TEMP',
        y='PM2.5',
        color='PM2.5',
        title="Scatter Plot: Suhu (TEMP) vs PM2.5",
        color_continuous_scale='Bluered'
    )
    st.plotly_chart(fig_temp, use_container_width=True)
    st.write("Insight: Terlihat konsentrasi PM2.5 tinggi menumpuk saat suhu rendah (kiri grafik).")

with col_scatter2:
    st.subheader("Hubungan Angin vs PM2.5")
    
    fig_wind = px.scatter(
        sample_df,
        x='WSPM',
        y='PM2.5',
        color='PM2.5',
        title="Scatter Plot: Kecepatan Angin (WSPM) vs PM2.5",
        color_continuous_scale='Bluered'
    )
    st.plotly_chart(fig_wind, use_container_width=True)
    st.write("Insight: Angin kencang (kanan grafik) cenderung membuat level PM2.5 rendah.")

st.caption("Copyright © 2025 - Dashboard Analisis Data Air Quality by Redityaa")