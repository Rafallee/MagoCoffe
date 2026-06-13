import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error

def get_forecast(df):
    # 1. Proteksi Data Asli
    df_copy = df.copy()
    
    # 2. Standarisasi Format Tanggal
    df_copy['Tanggal'] = pd.to_datetime(df_copy['Tanggal'], errors='coerce')
    
    # 3. Klasifikasi Minggu (Baseline Mei)
    def kelompokkan_minggu(row):
        if pd.isna(row['Tanggal']):
            return 'W1' # Fallback
        day = row['Tanggal'].day
        if day <= 3: return 'W1'
        elif day <= 10: return 'W2'
        elif day <= 17: return 'W3'
        elif day <= 24: return 'W4'
        else: return 'W5'
        
    df_copy['Minggu'] = df_copy.apply(kelompokkan_minggu, axis=1)

    # 4. Agregasi Data Penjualan per Minggu dan Menu
    all_weekly = (
        df_copy.groupby(['Minggu', 'Detail Produk'])['Banyak Penjualan']
        .sum()
        .unstack(fill_value=0)
    )

    hasil = []

    for menu in all_weekly.columns:
        y = all_weekly[menu].values.astype(float)
        
        print(menu, y)

        # Lewati menu musiman/baru yang datanya kurang dari 3 minggu
        if np.sum(y > 0) < 3:
            continue

        # 5. Kalkulasi Tren Terkini (EMA)
        # Menggunakan span=3 agar model sensitif terhadap perubahan mendadak di W4-W5
        # series_y = pd.Series(y)
        # ema = series_y.ewm(span=3, adjust=False).mean().values
        
        # 6. Proyeksi Jangka Pendek (Pangkas horizon hanya untuk W6 & W7)
        # pred_w6 = max(0, ema[-1])
        # W7 diberi penalti 5% sebagai buffer keamanan stok (hindari overstock)
        # pred_w7 = max(0, ema[-1] * 0.95) 

        # ===== LINEAR REGRESSION =====

        x = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)

        model = LinearRegression()
        model.fit(x, y)

        pred_w6 = model.predict([[6]])[0]
        pred_w7 = model.predict([[7]])[0]

        pred_w6 = max(0, pred_w6)
        pred_w7 = max(0, pred_w7)
        # 7. Evaluasi Metrik Historis
        avg_recent_volume = np.mean(y[-3:]) 
        
        # Hitung momentum murni dari 2 minggu terakhir
        growth_recent = 0
        if y[-2] > 0:
            growth_recent = ((y[-1] - y[-2]) / y[-2]) * 100

        # 8. Skor BI Berbasis Stabilitas (Mencegah Bias Menu Viral Sesaat)
        skor_bi = (avg_recent_volume * 0.7) + (max(0, growth_recent) * 0.3)

        hasil.append({
            'menu': menu,
            'total_mei': int(y.sum()),
            'history_w1_w5': y.tolist(), # <- PENTING: Dikirim untuk dirender di grafik
            'rata_rata_terkini': round(avg_recent_volume, 2),
            'growth_terkini': round(growth_recent, 2),
            'proyeksi_w6': int(round(pred_w6)),
            'proyeksi_w7': int(round(pred_w7)),
            'skor_bi': round(skor_bi, 3)
        })

    # 9. Sortir Objektif berdasarkan Skor BI tertinggi
    hasil_sorted = sorted(hasil, key=lambda x: x['skor_bi'], reverse=True)
    
    # Ambil Top 10
    top_10 = hasil_sorted[:10]
    
    return top_10