def get_top_menu(df):

    return (
        df.groupby('Detail Produk')
        .agg(
            jumlah_terjual=('Banyak Penjualan', 'sum'),
            total_revenue=('Penjualan Bersih', 'sum')
        )
        .sort_values('jumlah_terjual', ascending=False)
        .head(10)
        .reset_index()
    )