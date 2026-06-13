def get_peak_hour_data(df):

    hourly = (
        df.groupby('Jam')
        .agg(
            revenue=('Penjualan Bersih', 'sum'),
            transaksi=('No Transaksi', 'nunique')
        )
        .reset_index()
    )

    peak_hour = hourly.loc[
        hourly['revenue'].idxmax(),
        'Jam'
    ]

    return hourly, peak_hour