import pandas as pd

FILE_PATH = r"data/Product Sales Details - Mago Coffee - All Outlets - 01 May 2026 - 31 May 2026.xls"

def load_data():
    df = pd.read_excel(FILE_PATH, engine="xlrd")
    return df

if __name__ == "__main__":

    df = load_data()

    print(df.head())