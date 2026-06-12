import pandas as pd

FILE_PATH = r"data/Product Sales Details - Mago Coffee - All Outlets - 01 May 2026 - 31 May 2026.xls"

def load_data():

    df = pd.read_excel(FILE_PATH, engine="xlrd")

    # Konversi tanggal
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])

    # Jam
    df['Jam'] = df['Waktu'].astype(str).str[:2].astype(int)

    # Minggu
    df['Minggu'] = df['Tanggal'].dt.isocalendar().week.astype(int)

    # Hari
    df['Hari'] = df['Tanggal'].dt.day_name()

    return df