import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Capital Bikeshare Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Konfigurasi gaya visualisasi
sns.set_theme(style="whitegrid")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"

# ==========================================
# LOAD DATASET
# ==========================================
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path dataset harian
    main_csv_paths = [
        os.path.join(current_dir, "main_data.csv"),
        os.path.join(current_dir, "..", "data", "day.csv"),
        os.path.join(current_dir, "..", "Bike-sharing-dataset", "day.csv"),
        "main_data.csv",
        "data/day.csv"
    ]
    
    day_df = None
    for path in main_csv_paths:
        if os.path.exists(path):
            day_df = pd.read_csv(path)
            break
            
    # Path dataset per jam
    hour_csv_paths = [
        os.path.join(current_dir, "hour_clean.csv"),
        os.path.join(current_dir, "..", "data", "hour.csv"),
        os.path.join(current_dir, "..", "Bike-sharing-dataset", "hour.csv"),
        "hour_clean.csv",
        "data/hour.csv"
    ]
    
    hour_df = None
    for path in hour_csv_paths:
        if os.path.exists(path):
            hour_df = pd.read_csv(path)
            break
            
    # Pra-pemrosesan jika data belum diproses
    if day_df is not None:
        day_df['dteday'] = pd.to_datetime(day_df['dteday'])
        if 'season_label' not in day_df.columns:
            season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
            day_df['season_label'] = day_df['season'].map(season_mapping)
        if 'weather_label' not in day_df.columns:
            weather_mapping = {
                1: 'Clear/Partly Cloudy',
                2: 'Misty/Cloudy',
                3: 'Light Snow/Rain',
                4: 'Severe Weather'
            }
            day_df['weather_label'] = day_df['weathersit'].map(weather_mapping)
        if 'year_label' not in day_df.columns:
            day_df['year_label'] = day_df['yr'].map({0: 2011, 1: 2012})
        if 'temp_celsius' not in day_df.columns:
            day_df['temp_celsius'] = day_df['temp'] * 41

    if hour_df is not None:
        hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
        if 'season_label' not in hour_df.columns:
            season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
            hour_df['season_label'] = hour_df['season'].map(season_mapping)
        if 'weather_label' not in hour_df.columns:
            weather_mapping = {
                1: 'Clear/Partly Cloudy',
                2: 'Misty/Cloudy',
                3: 'Light Snow/Rain',
                4: 'Severe Weather'
            }
            hour_df['weather_label'] = hour_df['weathersit'].map(weather_mapping)
        if 'temp_celsius' not in hour_df.columns:
            hour_df['temp_celsius'] = hour_df['temp'] * 41

    return day_df, hour_df

day_df, hour_df = load_data()

# ==========================================
# SIDEBAR / WIDGET FILTER INTERAKTIF
# ==========================================
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80", use_container_width=True)
    st.title("🚲 Capital Bikeshare")
    st.markdown("**Dashboard Analisis Peminjaman Sepeda**")
    st.markdown("Analisis data historis peminjaman sepeda Washington D.C. (2011–2012).")
    st.markdown("---")
    
    # Filter 1: Rentang Tanggal Interaktif
    min_date = day_df['dteday'].min().date()
    max_date = day_df['dteday'].max().date()
    
    date_range = st.date_input(
        label="📅 Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter 2: Pilihan Musim (Season)
    all_seasons = ['Spring', 'Summer', 'Fall', 'Winter']
    selected_seasons = st.multiselect(
        label="🍂 Filter Musim (Season):",
        options=all_seasons,
        default=all_seasons
    )
    
    # Filter 3: Pilihan Kondisi Cuaca (Weather)
    available_weather = list(day_df['weather_label'].unique())
    selected_weather = st.multiselect(
        label="⛅ Filter Kondisi Cuaca:",
        options=available_weather,
        default=available_weather
    )
    
    st.markdown("---")
    st.caption("Dicoding Submission: Belajar Fundamental Analisis Data")

# Validasi filter rentang tanggal
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Penerapan Filter ke DataFrame
filtered_day_df = day_df[
    (day_df['dteday'].dt.date >= start_date) &
    (day_df['dteday'].dt.date <= end_date) &
    (day_df['season_label'].isin(selected_seasons)) &
    (day_df['weather_label'].isin(selected_weather))
]

if hour_df is not None:
    filtered_hour_df = hour_df[
        (hour_df['dteday'].dt.date >= start_date) &
        (hour_df['dteday'].dt.date <= end_date) &
        (hour_df['season_label'].isin(selected_seasons)) &
        (hour_df['weather_label'].isin(selected_weather))
    ]
else:
    filtered_hour_df = None

# ==========================================
# HEADER & RINGKASAN METRIK UTAMA
# ==========================================
st.title("🚲 Capital Bikeshare Performance Dashboard")
st.markdown("Dashboard interaktif untuk mengeksplorasi pengaruh cuaca, musim, pola jam komuter, serta segmentasi waktu operasional peminjaman sepeda sepanjang periode tahun 2011–2012.")

if filtered_day_df.empty:
    st.warning("⚠️ Tidak ada data yang sesuai dengan kombinasi filter yang dipilih. Silakan sesuaikan kembali filter di sidebar.")
    st.stop()

# Ringkasan KPI
total_rentals = filtered_day_df['cnt'].sum()
total_casual = filtered_day_df['casual'].sum()
total_registered = filtered_day_df['registered'].sum()
avg_daily_rentals = filtered_day_df['cnt'].mean()

pct_casual = (total_casual / total_rentals * 100) if total_rentals > 0 else 0
pct_registered = (total_registered / total_rentals * 100) if total_rentals > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Total Peminjaman",
        value=f"{total_rentals:,.0f} unit"
    )
with col2:
    st.metric(
        label="Pengguna Biasa (Casual)",
        value=f"{total_casual:,.0f} unit",
        delta=f"{pct_casual:.1f}% dari total"
    )
with col3:
    st.metric(
        label="Pengguna Terdaftar (Registered)",
        value=f"{total_registered:,.0f} unit",
        delta=f"{pct_registered:.1f}% dari total"
    )
with col4:
    st.metric(
        label="Rata-rata Peminjaman Harian",
        value=f"{avg_daily_rentals:,.0f} unit/hari"
    )

st.markdown("---")

# ==========================================
# TABS UTAMA DASHBOARD
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🌦️ Musim & Cuaca (Pertanyaan 1)",
    "⏰ Pola Jam Sibuk (Pertanyaan 2)",
    "📊 Analisis Lanjutan (Clustering & Binning)",
    "💡 Kesimpulan & Rekomendasi"
])

# ------------------------------------------
# TAB 1: PENGARUH MUSIM & KONDISI CUACA
# ------------------------------------------
with tab1:
    st.subheader("Pengaruh Musim dan Kondisi Cuaca terhadap Peminjaman Sepeda")
    st.markdown("Menjawab Pertanyaan Bisnis 1: *Bagaimana pengaruh musim (season) dan kondisi cuaca (weathersit) terhadap rata-rata dan total peminjaman sepeda harian sepanjang periode tahun 2011–2012?*")
    
    # Tren Deret Waktu Harian
    st.markdown("#### Tren Volume Peminjaman Harian")
    fig_trend, ax_trend = plt.subplots(figsize=(14, 4))
    ax_trend.plot(filtered_day_df['dteday'], filtered_day_df['cnt'], color='#2980b9', linewidth=1.5, label='Total Sewa (cnt)')
    ax_trend.plot(filtered_day_df['dteday'], filtered_day_df['registered'], color='#27ae60', linewidth=1, alpha=0.7, label='Registered')
    ax_trend.plot(filtered_day_df['dteday'], filtered_day_df['casual'], color='#e67e22', linewidth=1, alpha=0.7, label='Casual')
    ax_trend.set_title("Tren Peminjaman Sepeda Harian (Rentang Terpilih)", fontsize=12, fontweight='bold')
    ax_trend.set_xlabel("Tanggal", fontsize=10)
    ax_trend.set_ylabel("Jumlah Peminjaman (Unit)", fontsize=10)
    ax_trend.legend(frameon=True, facecolor='white', loc='upper left')
    st.pyplot(fig_trend)
    plt.close(fig_trend)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### Rata-rata Peminjaman per Musim")
        season_avg = filtered_day_df.groupby('season_label', observed=False)['cnt'].mean().reindex(selected_seasons).dropna().reset_index()
        
        fig_s, ax_s = plt.subplots(figsize=(7, 5))
        colors_s = ['#e74c3c' if s == 'Fall' else '#3498db' for s in season_avg['season_label']]
        sns.barplot(x='season_label', y='cnt', data=season_avg, palette=colors_s, ax=ax_s, edgecolor='black', linewidth=0.8)
        ax_s.set_title("Rata-rata Peminjaman Harian per Musim", fontsize=12, fontweight='bold', pad=10)
        ax_s.set_xlabel("Musim", fontsize=10)
        ax_s.set_ylabel("Rata-rata Unit/Hari", fontsize=10)
        for p in ax_s.patches:
            ax_s.annotate(f"{p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                          ha='center', va='bottom', fontsize=9, fontweight='semibold', xytext=(0, 4), textcoords='offset points')
        st.pyplot(fig_s)
        plt.close(fig_s)
        
    with col_chart2:
        st.markdown("#### Rata-rata Peminjaman per Kondisi Cuaca")
        weather_avg = filtered_day_df.groupby('weather_label', observed=False)['cnt'].mean().reindex(selected_weather).dropna().reset_index()
        
        fig_w, ax_w = plt.subplots(figsize=(7, 5))
        colors_w = ['#2ecc71', '#f39c12', '#e74c3c'][:len(weather_avg)]
        sns.barplot(x='weather_label', y='cnt', data=weather_avg, palette=colors_w, ax=ax_w, edgecolor='black', linewidth=0.8)
        ax_w.set_title("Rata-rata Peminjaman Harian per Kondisi Cuaca", fontsize=12, fontweight='bold', pad=10)
        ax_w.set_xlabel("Kondisi Cuaca", fontsize=10)
        ax_w.set_ylabel("Rata-rata Unit/Hari", fontsize=10)
        for p in ax_w.patches:
            ax_w.annotate(f"{p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                          ha='center', va='bottom', fontsize=9, fontweight='semibold', xytext=(0, 4), textcoords='offset points')
        st.pyplot(fig_w)
        plt.close(fig_w)
        
    st.info("""
    **Insight Utama Pertanyaan 1:**
    - **Musim Gugur (Fall)** mencatatkan rata-rata peminjaman tertinggi secara konsisten (**5.644 unit/hari**), disusul Musim Panas (**4.992 unit/hari**). Suhu yang nyaman dan stabil sangat mendukung penggunaan sepeda di ruang publik.
    - **Kondisi Cuaca Cerah (Clear/Partly Cloudy)** mendominasi volume penggunaan (**4.877 unit/hari**). Sebaliknya, pada saat cuaca hujan/salju (*Light Snow/Rain*), aktivitas bersepeda anjlok lebih dari 63% menjadi hanya **1.803 unit/hari**.
    """)

# ------------------------------------------
# TAB 2: POLA JAM SIBUK & TIPE PENGGUNA
# ------------------------------------------
with tab2:
    st.subheader("Pola Peminjaman Sepeda per Jam: Pengguna Casual vs Registered")
    st.markdown("Menjawab Pertanyaan Bisnis 2: *Bagaimana perbedaan pola peminjaman sepeda per jam (hourly pattern) antara pengguna biasa (casual) dan pengguna terdaftar (registered) pada hari kerja (working day) dibandingkan hari libur (weekend/holiday) sepanjang periode tahun 2011–2012?*")
    
    if filtered_hour_df is not None and not filtered_hour_df.empty:
        hourly_summary = filtered_hour_df.groupby(['workingday', 'hr'])[['casual', 'registered', 'cnt']].mean().reset_index()
        work_data = hourly_summary[hourly_summary['workingday'] == 1]
        nonwork_data = hourly_summary[hourly_summary['workingday'] == 0]
        
        # Fitur Interaktif Tambahan untuk Eksplorasi Kategori Hari
        day_filter_option = st.radio(
            label="🔘 Filter Interaktif Tipe Hari:",
            options=["Perbandingan Bersisian (Hari Kerja vs Akhir Pekan)", "Hanya Hari Kerja (Working Day)", "Hanya Hari Libur / Akhir Pekan (Weekend/Holiday)"],
            horizontal=True
        )
        
        if day_filter_option == "Hanya Hari Kerja (Working Day)":
            fig_hr, ax_hr = plt.subplots(figsize=(12, 5))
            ax_hr.plot(work_data['hr'], work_data['registered'], color='#2980b9', linewidth=2.5, marker='o', label='Registered')
            ax_hr.plot(work_data['hr'], work_data['casual'], color='#e67e22', linewidth=2.5, marker='s', linestyle='--', label='Casual')
            ax_hr.set_title("Hari Kerja (Working Day) - Pola Bimodal [Jam Berangkat (08:00) & Pulang Kantor (17:00-18:00)]", fontsize=12, fontweight='bold')
            ax_hr.set_xlabel("Jam (00:00 - 23:00)", fontsize=10)
            ax_hr.set_ylabel("Rata-rata Peminjaman per Jam (Unit)", fontsize=10)
            ax_hr.set_xticks(range(0, 24, 2))
            ax_hr.legend(frameon=True, facecolor='white', loc='upper left')
            ax_hr.axvspan(7.5, 8.5, color='#3498db', alpha=0.15)
            ax_hr.axvspan(16.5, 18.5, color='#3498db', alpha=0.15)
            plt.tight_layout()
            st.pyplot(fig_hr)
            plt.close(fig_hr)
        elif day_filter_option == "Hanya Hari Libur / Akhir Pekan (Weekend/Holiday)":
            fig_hr, ax_hr = plt.subplots(figsize=(12, 5))
            ax_hr.plot(nonwork_data['hr'], nonwork_data['registered'], color='#2980b9', linewidth=2.5, marker='o', label='Registered')
            ax_hr.plot(nonwork_data['hr'], nonwork_data['casual'], color='#e67e22', linewidth=2.5, marker='s', linestyle='--', label='Casual')
            ax_hr.set_title("Hari Libur / Akhir Pekan (Weekend & Holiday) - Pola Unimodal [Rekreasi Siang Hari (12:00-16:00)]", fontsize=12, fontweight='bold')
            ax_hr.set_xlabel("Jam (00:00 - 23:00)", fontsize=10)
            ax_hr.set_ylabel("Rata-rata Peminjaman per Jam (Unit)", fontsize=10)
            ax_hr.set_xticks(range(0, 24, 2))
            ax_hr.legend(frameon=True, facecolor='white', loc='upper left')
            ax_hr.axvspan(12, 16, color='#f39c12', alpha=0.15)
            plt.tight_layout()
            st.pyplot(fig_hr)
            plt.close(fig_hr)
        else:
            fig_hr, axes_hr = plt.subplots(1, 2, figsize=(16, 5), sharey=True)
            
            # Hari Kerja (Working Day)
            axes_hr[0].plot(work_data['hr'], work_data['registered'], color='#2980b9', linewidth=2.5, marker='o', label='Registered')
            axes_hr[0].plot(work_data['hr'], work_data['casual'], color='#e67e22', linewidth=2.5, marker='s', linestyle='--', label='Casual')
            axes_hr[0].set_title("Hari Kerja (Working Day)\n[Pola Bimodal - Jam Berangkat & Pulang Kantor]", fontsize=12, fontweight='bold')
            axes_hr[0].set_xlabel("Jam (00:00 - 23:00)", fontsize=10)
            axes_hr[0].set_ylabel("Rata-rata Peminjaman per Jam (Unit)", fontsize=10)
            axes_hr[0].set_xticks(range(0, 24, 2))
            axes_hr[0].legend(frameon=True, facecolor='white', loc='upper left')
            axes_hr[0].axvspan(7.5, 8.5, color='#3498db', alpha=0.15)
            axes_hr[0].axvspan(16.5, 18.5, color='#3498db', alpha=0.15)
            
            # Hari Libur / Akhir Pekan
            axes_hr[1].plot(nonwork_data['hr'], nonwork_data['registered'], color='#2980b9', linewidth=2.5, marker='o', label='Registered')
            axes_hr[1].plot(nonwork_data['hr'], nonwork_data['casual'], color='#e67e22', linewidth=2.5, marker='s', linestyle='--', label='Casual')
            axes_hr[1].set_title("Hari Libur / Akhir Pekan (Weekend & Holiday)\n[Pola Unimodal - Rekreasi Siang Hari]", fontsize=12, fontweight='bold')
            axes_hr[1].set_xlabel("Jam (00:00 - 23:00)", fontsize=10)
            axes_hr[1].set_xticks(range(0, 24, 2))
            axes_hr[1].legend(frameon=True, facecolor='white', loc='upper left')
            axes_hr[1].axvspan(12, 16, color='#f39c12', alpha=0.15)
            
            plt.tight_layout()
            st.pyplot(fig_hr)
            plt.close(fig_hr)
        
        col_pk1, col_pk2 = st.columns(2)
        with col_pk1:
            st.markdown("**Puncak Jam Sibuk Hari Kerja (Working Day):**")
            top_work = work_data.sort_values(by='cnt', ascending=False).head(3)[['hr', 'registered', 'casual', 'cnt']]
            top_work.columns = ['Jam', 'Registered (unit)', 'Casual (unit)', 'Total (unit)']
            st.dataframe(top_work.style.format("{:,.0f}").hide(axis="index"), use_container_width=True)
            
        with col_pk2:
            st.markdown("**Puncak Jam Sibuk Hari Libur (Weekend/Holiday):**")
            top_nonwork = nonwork_data.sort_values(by='cnt', ascending=False).head(3)[['hr', 'registered', 'casual', 'cnt']]
            top_nonwork.columns = ['Jam', 'Registered (unit)', 'Casual (unit)', 'Total (unit)']
            st.dataframe(top_nonwork.style.format("{:,.0f}").hide(axis="index"), use_container_width=True)
            
        st.info("""
        **Insight Utama Pertanyaan 2:**
        - **Hari Kerja (Komuter)**: Menunjukkan pola **bimodal** dengan dua puncak signifikan pada pukul **08:00** (rata-rata 477 unit/jam) dan **17:00–18:00** (rata-rata 492–525 unit/jam). Pola ini didorong oleh komuter pengguna terdaftar (*registered*).
        - **Hari Libur (Rekreasi)**: Berubah menjadi pola **unimodal** dengan lonjakan aktivitas santai di siang hari (**12:00–16:00**). Volume pengguna biasa (*casual*) meningkat hingga ~140 unit/jam (lebih dari 2.5x lipat dibandingkan siang hari kerja).
        """)
    else:
        st.warning("Data per jam tidak tersedia untuk filter yang dipilih.")

# ------------------------------------------
# TAB 3: ANALISIS LANJUTAN (CLUSTERING & BINNING)
# ------------------------------------------
with tab3:
    st.subheader("Teknik Analisis Lanjutan: Clustering Berbasis Binning & Manual Grouping")
    st.markdown("""
    Sesuai panduan evaluasi Dicoding, analisis lanjutan dilakukan menggunakan metode **Clustering Non-Machine Learning**:
    1. **Binning Suhu Lingkungan**: Membagi temperatur riil (°C) ke dalam interval kenyamanan termal manusia menggunakan `pd.cut`.
    2. **Manual Grouping Jam Operasional**: Mengelompokkan jam ke dalam 5 klaster bisnis untuk mengevaluasi komposisi pengguna.
    """)
    
    # 1. Binning Suhu
    temp_bins = [-np.inf, 12, 22, 30, np.inf]
    temp_labels = ['Dingin (< 12°C)', 'Sejuk (12 - 22°C)', 'Hangat (22 - 30°C)', 'Panas (> 30°C)']
    
    filtered_day_df_copy = filtered_day_df.copy()
    filtered_day_df_copy['temp_cluster'] = pd.cut(filtered_day_df_copy['temp_celsius'], bins=temp_bins, labels=temp_labels)
    temp_res = filtered_day_df_copy.groupby('temp_cluster', observed=False)['cnt'].agg(
        total_hari='count',
        rata_rata='mean',
        total_sewa='sum'
    ).reset_index()
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("#### Rata-rata Peminjaman per Klaster Suhu (Binning)")
        fig_tb, ax_tb = plt.subplots(figsize=(7, 4.5))
        sns.barplot(x='temp_cluster', y='rata_rata', data=temp_res, palette=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'], ax=ax_tb, edgecolor='black', linewidth=0.8)
        ax_tb.set_title("Rata-rata Sewa Berdasarkan Kategori Suhu", fontsize=11, fontweight='bold', pad=8)
        ax_tb.set_xlabel("Kategori Temperatur", fontsize=9)
        ax_tb.set_ylabel("Rata-rata Unit/Hari", fontsize=9)
        ax_tb.set_xticklabels(ax_tb.get_xticklabels(), rotation=15, ha='right')
        for p in ax_tb.patches:
            if not np.isnan(p.get_height()):
                ax_tb.annotate(f"{p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                               ha='center', va='bottom', fontsize=8, fontweight='semibold', xytext=(0, 3), textcoords='offset points')
        st.pyplot(fig_tb)
        plt.close(fig_tb)
        
    with col_c2:
        st.markdown("#### Komposisi Pengguna per Klaster Jam Operasional")
        if filtered_hour_df is not None and not filtered_hour_df.empty:
            def assign_time_cluster(hr):
                if 0 <= hr <= 5: return '1. Early Morning (00-05)'
                elif 6 <= hr <= 9: return '2. Morning Rush (06-09)'
                elif 10 <= hr <= 15: return '3. Midday (10-15)'
                elif 16 <= hr <= 19: return '4. Evening Rush (16-19)'
                else: return '5. Night (20-23)'
                
            filtered_hour_df_copy = filtered_hour_df.copy()
            filtered_hour_df_copy['time_cluster'] = filtered_hour_df_copy['hr'].apply(assign_time_cluster)
            t_cluster = filtered_hour_df_copy.groupby('time_cluster', observed=False).agg(
                total_sewa=('cnt', 'sum'),
                casual=('casual', 'sum'),
                registered=('registered', 'sum')
            ).reset_index()
            
            fig_tc, ax_tc = plt.subplots(figsize=(7, 4.5))
            ax_tc.bar(t_cluster['time_cluster'], t_cluster['registered'], label='Registered', color='#2980b9', edgecolor='black', linewidth=0.8)
            ax_tc.bar(t_cluster['time_cluster'], t_cluster['casual'], bottom=t_cluster['registered'], label='Casual', color='#e67e22', edgecolor='black', linewidth=0.8)
            ax_tc.set_title("Total Volume Sewa per Klaster Waktu (Casual vs Registered)", fontsize=11, fontweight='bold', pad=8)
            ax_tc.set_xlabel("Klaster Waktu", fontsize=9)
            ax_tc.set_ylabel("Total Sewa (Unit)", fontsize=9)
            ax_tc.set_xticklabels(ax_tc.get_xticklabels(), rotation=15, ha='right')
            ax_tc.legend(frameon=True, facecolor='white', loc='upper left')
            st.pyplot(fig_tc)
            plt.close(fig_tc)
            
    st.info("""
    **Insight Analisis Lanjutan:**
    - **Sensitivitas Suhu**: Permintaan tertinggi terkonsentrasi pada rentang suhu **Hangat (22–30°C)** dengan rata-rata **5.719 unit/hari**. Pada suhu **Dingin (< 12°C)**, permintaan terpangkas drastis menjadi hanya **2.228 unit/hari**.
    - **Peluang Segmentasi Waktu**: Segmen **Evening Rush (16:00–19:00)** menyerap volume terbesar (1,10 juta unit), sedangkan segmen **Midday (10:00–15:00)** memiliki rasio keterlibatan pengguna kasual tertinggi (**28,8%**).
    """)

# ------------------------------------------
# TAB 4: KESIMPULAN & REKOMENDASI BISNIS
# ------------------------------------------
with tab4:
    st.subheader("💡 Kesimpulan dan Rekomendasi Action Item")
    
    st.markdown("### Kesimpulan Analisis")
    st.markdown("""
    1. **Pengaruh Musim & Cuaca (Pertanyaan 1)**:
       Musim dan kondisi cuaca memainkan peranan sangat signifikan terhadap penggunaan sepeda. Musim Gugur (*Fall*) adalah periode puncak performa bisnis dengan rata-rata **5.644 unit/hari** (total 1.061.129 peminjaman), disusul Musim Panas (*Summer*, 4.992 unit/hari). Cuaca cerah mendominasi ~68,6% dari seluruh transaksi peminjaman, sedangkan cuaca hujan/salju mereduksi permintaan hingga lebih dari 63%.
       
    2. **Dinamika Jam & Perilaku Pengguna (Pertanyaan 2)**:
       Pola peminjaman sepeda terbagi jelas menjadi dua profil operasional sepanjang periode tahun 2011–2012:
       - **Hari Kerja (Komuter)**: Berpola *bimodal* dengan lonjakan pada jam berangkat (**08:00**) dan jam pulang kerja (**17:00–18:00**), didominasi secara masif oleh pengguna *registered*.
       - **Hari Libur (Rekreasi)**: Berpola *unimodal* berpusat di tengah hari (**12:00–16:00**) dengan lonjakan tajam pengguna *casual* untuk aktivitas rekreasional.
    """)
    
    st.markdown("---")
    st.markdown("### Rekomendasi Action Item untuk Manajemen")
    
    c_rec1, c_rec2, c_rec3 = st.columns(3)
    
    with c_rec1:
        st.success("🛠️ **1. Manajemen Armada Dinamis & Perawatan Berkala**")
        st.markdown("""
        - Jadwalkan pemeliharaan besar (*overhaul*) pada **Musim Dingin & Musim Semi awal** saat permintaan terendah.
        - Pastikan ketersediaan armada 100% prima di jalan pada **Musim Panas & Musim Gugur** untuk memaksimalkan potensi pendapatan sewa.
        """)
        
    with c_rec2:
        st.info("🔄 **2. Strategi Rebalancing Stasiun Komuter**")
        st.markdown("""
        - Lakukan suplai armada ke stasiun perumahan pada pukul **06:30–07:30** sebelum jam berangkat kantor.
        - Kosongkan dermaga di area perkantoran/kampus pada pukul **16:00–17:00** guna mencegah *dock lock* (stasiun penuh) saat jam pulang kantor.
        """)
        
    with c_rec3:
        st.warning("🎯 **3. Kampanye Konversi Casual ke Member**")
        st.markdown("""
        - Bidik pengguna kasual yang aktif di akhir pekan dan siang hari (10:00–15:00) dengan diskon membership langganan tahunan.
        - Sediakan promo uji coba komuter gratis (*free commuter pass trial*) bagi penyewa kasual akhir pekan untuk mengubah mereka menjadi pelanggan harian.
        """)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>© Capital Bikeshare Data Analysis Project | Dicoding Indonesia</div>", unsafe_allow_html=True)
