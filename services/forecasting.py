import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def get_daily_trend(df):

    daily = (
        df.groupby('Tanggal')
        .agg(
            revenue=('Penjualan Bersih', 'sum'),
            transaksi=('No Transaksi', 'nunique')
        )
        .reset_index()
    )

    daily['MA7'] = (
        daily['revenue']
        .rolling(window=7, min_periods=1)
        .mean()
    )

    return daily

from sklearn.metrics import mean_absolute_percentage_error

def get_forecast(df):
    all_weekly = (
        df.groupby(['Minggu', 'Detail Produk'])['Banyak Penjualan']
        .sum()
        .unstack(fill_value=0)
    )

    hasil = []

    for menu in all_weekly.columns:
        y = all_weekly[menu].values.astype(float)

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

        slope = model.coef_[0]

        # ── AKUMULASI PREDIKSI BULANAN ──
        # Mei adalah W1-W5 (5 minggu)
        
        # Juni = W6, W7, W8, W9 (4 minggu)
        pred_juni = sum([max(0, model.predict([[i]])[0]) for i in [6, 7, 8, 9]])
        
        # Juli = W10, W11, W12, W13, W14 (5 minggu)
        pred_juli = sum([max(0, model.predict([[i]])[0]) for i in [10, 11, 12, 13, 14]])

        growth = ((y[-1] - y[0]) / max(y[0], 1)) * 100

        hasil.append({
            'Menu': menu,
            'Total Mei': int(y.sum()),
            'Slope': round(slope, 2),
            'Growth': round(growth, 2),
            'Proyeksi Juni': int(round(pred_juni)), # Mengganti W6
            'Proyeksi Juli': int(round(pred_juli))  # Mengganti W7
        })

    forecast = pd.DataFrame(hasil)
    forecast = forecast.sort_values('Slope', ascending=False)
    return forecast