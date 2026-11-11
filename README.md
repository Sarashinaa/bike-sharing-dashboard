# Capital Bikeshare Data Analysis Dashboard ✨

Dashboard interaktif untuk menganalisis data historis penyewaan sepeda pada Capital Bikeshare (Washington D.C.) periode 2011–2012. Proyek ini dibangun untuk memenuhi kriteria proyek akhir kelas **"Belajar Fundamental Analisis Data" - Dicoding Indonesia**.

---

## 📁 Struktur Direktori
```
submission
├─── dashboard
│    ├─── main_data.csv
│    ├─── hour_clean.csv
│    └─── dashboard.py
├─── data
│    ├─── day.csv
│    └─── hour.csv
├─── notebook.ipynb
├─── README.md
├─── requirements.txt
└─── url.txt
```

---

## ⚙️ Setup Environment

### Opsi 1: Menggunakan Anaconda / Conda
```bash
conda create --name bike-sharing python=3.9
conda activate bike-sharing
pip install -r requirements.txt
```

### Opsi 2: Menggunakan Terminal / Virtualenv (pip)
```bash
# Buat dan aktifkan virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate

# Install dependensi
pip install -r requirements.txt
```

---

## 🚀 Cara Menjalankan Dashboard

Masuk ke direktori `submission/dashboard` atau direktori utama, lalu jalankan perintah:

```bash
cd dashboard
streamlit run dashboard.py
```
atau dari root:
```bash
streamlit run dashboard/dashboard.py
```

Setelah perintah dijalankan, dashboard akan otomatis terbuka di peramban web pada alamat `http://localhost:8501`.

---

## 📊 Fitur Dashboard
1. **Ringkasan Metrik Utama (KPI)**: Total penyewaan, proporsi pengguna biasa (*casual*), proporsi pengguna terdaftar (*registered*), serta rata-rata sewa harian.
2. **Filter Interaktif**: Pemilihan rentang tanggal, filter musim (*season*), dan filter kondisi cuaca (*weather condition*).
3. **Tab 1 - Musim & Cuaca**: Menjawab Pertanyaan Bisnis 1 terkait dinamika sewa sepeda terhadap musim dan cuaca ekstrem.
4. **Tab 2 - Pola Jam Sibuk**: Menjawab Pertanyaan Bisnis 2 terkait perbedaan pola jam komuter (*working day*) vs pola rekreasi (*weekend/holiday*).
5. **Tab 3 - Analisis Lanjutan**: Eksplorasi teknik *Clustering* tanpa machine learning (*Binning* suhu kenyamanan termal dan *Manual Grouping* klaster jam operasional).
6. **Tab 4 - Kesimpulan & Rekomendasi**: Rangkuman temuan bisnis serta 3 rekomendasi taktis berorientasi aksi untuk manajemen.
