from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

FILE_PATH = r"data/Product Sales Details - Mago Coffee - All Outlets - 01 May 2026 - 31 May 2026.xls"

@app.route('/')
def home():

    try:
        df = pd.read_excel(FILE_PATH, engine='xlrd')

        total_revenue = df['Penjualan Bersih'].sum()
        total_item = df['Banyak Penjualan'].sum()
        total_trx = df['No Transaksi'].nunique()
        avg_trx = total_revenue / total_trx if total_trx > 0 else 0

        top_menu = (
            df.groupby('Detail Produk')
            .agg(
                jumlah_terjual=('Banyak Penjualan', 'sum'),
                total_revenue=('Penjualan Bersih', 'sum')
            )
            .sort_values('jumlah_terjual', ascending=False)
            .head(10)
            .reset_index()
        )

        kategori = (
    df.groupby('Kategori')
    .agg(
        jumlah_terjual=('Banyak Penjualan', 'sum'),
        total_revenue=('Penjualan Bersih', 'sum')
    )
    .reset_index()
)

    except Exception as e:
        print("ERROR:", e)

        total_revenue = 0
        total_item = 0
        total_trx = 0
        avg_trx = 0

        top_menu = pd.DataFrame()
        kategori = pd.DataFrame()

    return render_template(
    'index.html',
    total_revenue=total_revenue,
    total_item=total_item,
    total_trx=total_trx,
    avg_trx=avg_trx,
    top_menu=top_menu.to_dict('records')
)

if __name__ == '__main__':
    app.run(debug=True)