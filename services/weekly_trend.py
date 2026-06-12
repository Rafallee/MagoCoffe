def get_weekly_trend(df):

    TOP5 = [
        'Es Kopi Susu',
        'Dirty Latte',
        'Americano (Ice)',
        'Matcha Latte',
        'French Fries with Truffle Oil'
    ]

    weekly_menu = (
        df[df['Detail Produk'].isin(TOP5)]
        .groupby(
            ['Minggu', 'Detail Produk']
        )['Banyak Penjualan']
        .sum()
        .unstack(fill_value=0)
    )

    return weekly_menu