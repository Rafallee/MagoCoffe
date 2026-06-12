def get_kpi(df):

    total_revenue = df['Penjualan Bersih'].sum()
    total_item = df['Banyak Penjualan'].sum()
    total_trx = df['No Transaksi'].nunique()
    avg_trx = total_revenue / total_trx if total_trx > 0 else 0

    return {
        "total_revenue": total_revenue,
        "total_item": total_item,
        "total_trx": total_trx,
        "avg_trx": avg_trx
    }