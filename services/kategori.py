def get_kategori(df):

    return (
        df.groupby('Kategori')
        .agg(
            jumlah_terjual=('Banyak Penjualan', 'sum'),
            total_revenue=('Penjualan Bersih', 'sum')
        )
        .reset_index()
    )