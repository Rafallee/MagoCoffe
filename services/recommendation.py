def get_recommendation(score):

    top3 = score.head(3)

    rekomendasi = []

    for _, row in top3.iterrows():

        rekomendasi.append(

            f"Prioritaskan stok {row['Menu']} "
            f"(BI Score {row['Skor BI']})"

        )

    rekomendasi.append(
        "Optimalkan promo pada jam sibuk"
    )

    rekomendasi.append(
        "Perluas penjualan melalui delivery"
    )

    return rekomendasi