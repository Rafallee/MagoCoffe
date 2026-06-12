import matplotlib.pyplot as plt

def create_kategori_chart(kategori):

    plt.figure(figsize=(6,6))

    plt.pie(
        kategori['jumlah_terjual'],
        labels=kategori['Kategori'],
        autopct='%1.1f%%'
    )

    plt.title(
        'Distribusi Kategori Mago Coffee'
    )

    plt.savefig(
        'static/charts/kategori.png',
        bbox_inches='tight'
    )

    plt.close()