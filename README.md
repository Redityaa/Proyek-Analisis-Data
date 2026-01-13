# **🌍 Air Quality Analysis Dashboard**

Dashboard ini dibuat untuk menganalisis data kualitas udara (Air Quality Dataset). Proyek ini berfokus pada analisis tren polusi udara dari waktu ke waktu, perbandingan tingkat polusi antar stasiun, serta korelasi antara kualitas udara dengan faktor meteorologi seperti suhu dan kecepatan angin.

## **📂 Struktur Direktori**

```text
Proyek Analisis Data
├── dashboard/
│   ├── dashboard.py        # File utama dashboard
│   └── main_data.csv       # Data bersih yang digunakan 
├── data/
│   ├── PRSA_Data_Aotizhongxin_20130301-20170228.csv
│   ├── PRSA_Data_Changping_20130301-20170228.csv
│   └── ... (file data kota lainnya sesuai dataset)
├── notebook.ipynb          # File Jupyter Notebook (Analisis Data)
├── requirements.txt        # Daftar library yang dibutuhkan
├── url.txt                 # Tautan streamlit
└── README.md               # Dokumentasi Proyek
```

## **🔧 Cara Menjalankan Proyek**
Ikuti langkah-langkah berikut untuk menjalankan dashboard di komputer lokal Anda:

1. **Persiapan Lingkungan (Environment)** <br>
Pastikan Anda telah menginstal Python. Disarankan menggunakan Virtual Environment agar instalasi library tidak mengganggu sistem global.

    **Windows:**

    ```Bash
    python -m venv venv
    venv\Scripts\activate
    ```
    **macOS/Linux:**
    ```Bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Instalasi Library** <br>
Instal semua dependensi yang diperlukan yang terdaftar di requirements.txt. Pastikan Anda berada di direktori root proyek (sejajar dengan file requirements.txt).

    ```Bash
    pip install -r requirements.txt
    ```
3. **Menjalankan Dashboard**
Masuk ke folder `dashboard`, lalu jalankan perintah streamlit:

    ```Bash
    cd dashboard
    streamlit run dashboard.py
    ```
    Setelah dijalankan, dashboard akan otomatis terbuka di browser Anda pada alamat `http://localhost:8501`.

## **📊 Temuan & Insight Utama**
Berdasarkan hasil analisis data menggunakan Jupyter Notebook dan visualisasi Dashboard, diperoleh kesimpulan sebagai berikut:

1. **Tren Musiman yang Signifikan:**

    - Terdapat pola musiman yang kuat di mana tingkat polusi udara (PM2.5) meningkat drastis pada **musim dingin** (Desember - Februari). Hal ini kemungkinan disebabkan oleh fenomena inversi suhu dan peningkatan aktivitas pembakaran untuk pemanas ruangan.

    - Sebaliknya, kualitas udara cenderung membaik/menurun polusinya pada musim panas.

2. **Analisis Lokasi (Geospatial):**

    - Stasiun **Dongsi** teridentifikasi sebagai wilayah dengan rata-rata tingkat polusi tertinggi ("Zona Merah"), yang mengindikasikan perlunya fokus penanggulangan di area urban padat tersebut.

    - Stasiun **Dingling** dan area pinggiran lainnya mencatat kualitas udara yang relatif lebih baik.

3. **Korelasi Faktor Meteorologi:**

    - **Suhu (TEMP):** Memiliki korelasi negatif dengan PM2.5. Saat suhu rendah (dingin), polutan cenderung terperangkap di dekat tanah (akumulasi tinggi).

    - **Kecepatan Angin (WSPM):** Memiliki korelasi negatif yang cukup kuat. Angin kencang berperan efektif dalam menyebarkan dan mengurangi konsentrasi polutan di udara.

## **🛠️ Teknologi yang Digunakan**
- **Python:** Bahasa pemrograman utama.

- **Pandas:** Untuk pembersihan (cleaning) dan manipulasi data.

- **Matplotlib & Seaborn:** Untuk visualisasi data statis di Notebook.

- **Plotly Express:** Untuk visualisasi interaktif dan pemetaan geospasial di Dashboard.

- **Streamlit:** Framework untuk membangun dashboard web interaktif.

**Copyright © 2025 - Analisis Data Air Quality by Redityaa**