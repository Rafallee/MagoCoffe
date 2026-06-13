import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def get_forecast(df):
    # Buat salinan dataframe agar tidak merusak data asli
    df_copy = df.copy()
    
    # 1. Pastikan kolom Tanggal terbaca sebagai tipe data tanggal (Datetime)
    # Kebanyakan format data Indonesia/POS menggunakan format tanggal-bulan-tahun
    df_copy['Tanggal'] = pd.to_datetime(df_copy['Tanggal'], errors='coerce')
    
    # 2. Membuat kolom 'Minggu' otomatis berdasarkan tanggal di bulan Mei
    # Kita bagi menjadi W1 (tgl 1-3), W2 (tgl 4-10), W3 (tgl 11-17), W4 (tgl 18-24), W5 (tgl 25-31)
    def kelompokkan_minggu(row):
        if pd.isna(row['Tanggal']):
            return 'W1' # Fallback jika ada tanggal kosong
        day = row['Tanggal'].day
        if day <= 3: return 'W1'
        elif day <= 10: return 'W2'
        elif day <= 17: return 'W3'
        elif day <= 24: return 'W4'
        else: return 'W5'
        
    df_copy['Minggu'] = df_copy.apply(kelompokkan_minggu, axis=1)

    # 3. Kelompokkan data berdasarkan Minggu dan Detail Produk
    all_weekly = (
        df_copy.groupby(['Minggu', 'Detail Produk'])['Banyak Penjualan']
        .sum()
        .unstack(fill_value=0)
    )

    hasil = []

    for menu in all_weekly.columns:
        y = all_weekly[menu].values.astype(float)

        # Jika menu terjual kurang dari 3 minggu berbeda, lewati (biar tidak error linear regression)
        if np.sum(y > 0) < 3:
            continue

        X = np.arange(1, len(y) + 1).reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, y)

        slope = model.coef_[0]

        # Prediksi bulan Juni (Minggu ke 6, 7, 8, 9) dan Juli (Minggu 10, 11, 12, 13, 14)
        pred_juni = sum([max(0, model.predict(np.array([[i]]))[0]) for i in [6, 7, 8, 9]])
        pred_juli = sum([max(0, model.predict(np.array([[i]]))[0]) for i in [10, 11, 12, 13, 14]])

        # Hitung pertumbuhan penjualan historis (growth)
        growth = ((y[-1] - y[0]) / max(y[0], 1)) * 100

        # Rumus BI Score sederhana untuk menentukan ranking menu prioritas
        total_volume = y.sum()
        skor_bi = (total_volume * 0.5) + (slope * 0.3) + (growth * 0.2)

        hasil.append({
            'menu': menu,
            'total_mei': int(total_volume),
            'slope': round(slope, 2),
            'growth': round(growth, 2),
            'proyeksi_juni': int(round(pred_juni)),
            'proyeksi_juli': int(round(pred_juli)),
            'skor_bi': round(skor_bi, 3)
        })

    # Urutkan berdasarkan Skor BI tertinggi (Menu terlaris & paling tren)
    hasil_sorted = sorted(hasil, key=lambda x: x['skor_bi'], reverse=True)
    
    # Ambil 10 teratas untuk dikirim ke dashboard
    return hasil_sorted[:10]