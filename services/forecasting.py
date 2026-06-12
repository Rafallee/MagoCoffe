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

        X = np.arange(1, len(y) + 1).reshape(-1, 1)

        model = LinearRegression()

        model.fit(X, y)

        slope = model.coef_[0]

        pred_w6 = max(0, model.predict([[6]])[0])

        pred_w7 = max(0, model.predict([[7]])[0])

        growth = (
            (y[-1] - y[0])
            /
            max(y[0], 1)
        ) * 100

        hasil.append({

            'Menu': menu,

            'Total Mei': int(y.sum()),

            'Slope': round(slope, 2),

            'Growth': round(growth, 2),

            'Proyeksi W6': int(round(pred_w6)),

            'Proyeksi W7': int(round(pred_w7))
        })

    forecast = pd.DataFrame(hasil)

    forecast = forecast.sort_values(
        'Slope',
        ascending=False
    )

    return forecast