from flask import Flask, jsonify, render_template
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# ── CONFIG JALUR DATA EXCEL & WEATHER ──
FOLDER_DATA = "data"
NAMA_FILE_EXCEL = "Product Sales Details - Mago Coffee - All Outlets - 01 May 2026 - 31 May 2026.xls" 
PATH_EXCEL = os.path.join(FOLDER_DATA, NAMA_FILE_EXCEL)

# Gunakan read_excel karena format asli file cuaca Anda adalah XLSX murni
NAMA_FILE_WEATHER = "Bandung2.xlsx"
PATH_WEATHER = os.path.join(FOLDER_DATA, NAMA_FILE_WEATHER)


def clean_num(val):
    if isinstance(val, float) and np.isnan(val):
        return 0
    return val


def muat_dan_proses_data():
    """KEMBALI KE AWAL: Murni menghitung tren waktu tanpa merge cuaca"""
    if not os.path.exists(PATH_EXCEL):
        raise FileNotFoundError(f"File Excel tidak ditemukan di: {PATH_EXCEL}")
        
    df = pd.read_excel(PATH_EXCEL)
    
    # 1. STANDARISASI WAKTU & TANGGAL
    df['Tanggal_Clean'] = pd.to_datetime(df['Tanggal'], errors='coerce')
    df['Waktu_Clean'] = pd.to_datetime(df['Waktu'], format='%H:%M', errors='coerce')
    df['Jam'] = df['Waktu_Clean'].dt.hour
    if df['Jam'].isna().all():
        df['Jam'] = df['Waktu'].astype(str).str.split(':').str[0].str.extract(r'(\d+)').astype(float)
    df['Jam'] = df['Jam'].fillna(12).astype(int)
    
    # Kelompokkan Minggu (W1 - W5)
    def dapatkan_minggu(row):
        if pd.isna(row['Tanggal_Clean']): return 'W1'
        day = row['Tanggal_Clean'].day
        if day <= 3: return 'W1'
        elif day <= 10: return 'W2'
        elif day <= 17: return 'W3'
        elif day <= 24: return 'W4'
        else: return 'W5'
    df['Minggu'] = df.apply(dapatkan_minggu, axis=1)

    # 2. PROSES DATA KPI SUMMARY
    total_rev = float(df['Penjualan Bersih'].sum())
    total_item = int(df['Banyak Penjualan'].sum())
    total_trx = int(df['No Transaksi'].nunique())
    avg_trx = float(total_rev / total_trx) if total_trx > 0 else 0
    
    summary_data = {
        "total_revenue": total_rev,
        "total_item": total_item,
        "total_transaksi": total_trx,
        "avg_trx_value": avg_trx
    }

    # 3. PROSES DATA DAILY TREND
    df_daily = df.groupby(df['Tanggal_Clean'].dt.strftime('%Y-%m-%d')).agg({
        'Penjualan Bersih': 'sum'
    }).reset_index()
    
    daily_trend_data = []
    for _, row in df_daily.iterrows():
        daily_trend_data.append({
            "tanggal": row['Tanggal_Clean'],
            "revenue": float(row['Penjualan Bersih'])
        })
    daily_trend_data.sort(key=lambda x: x['tanggal'])

    # 4. PROSES DATA KATEGORI
    df_kat = df.groupby('Kategori').agg({
        'Banyak Penjualan': 'sum'
    }).reset_index()
    total_kat_item = df_kat['Banyak Penjualan'].sum() if df_kat['Banyak Penjualan'].sum() > 0 else 1
    
    kategori_data = []
    for _, row in df_kat.iterrows():
        pct = round((row['Banyak Penjualan'] / total_kat_item) * 100, 1)
        kategori_data.append({
            "kategori": str(row['Kategori']),
            "jumlah": int(row['Banyak Penjualan']),
            "pct": pct
        })

    # 5. PROSES DATA TOP 15 MENU
    df_menu = df.groupby('Detail Produk').agg({
        'Banyak Penjualan': 'sum',
        'Penjualan Bersih': 'sum'
    }).reset_index().sort_values(by='Banyak Penjualan', ascending=False).head(15)
    
    top_menu_data = []
    for _, row in df_menu.iterrows():
        rev_pct = round((row['Penjualan Bersih'] / total_rev) * 100, 1) if total_rev > 0 else 0
        top_menu_data.append({
            "menu": str(row['Detail Produk']),
            "jumlah_terjual": int(row['Banyak Penjualan']),
            "total_revenue": float(row['Penjualan Bersih']),
            "revenue_pct": rev_pct
        })

    # 6. PROSES DATA TREN MINGGUAN TOP 5
    top5_names = df.groupby('Detail Produk')['Banyak Penjualan'].sum().nlargest(5).index.tolist()
    weeks_list = ['W1', 'W2', 'W3', 'W4', 'W5']
    
    menus_weekly_dict = {}
    for name in top5_names:
        menus_weekly_dict[name] = [0, 0, 0, 0, 0]
        
    df_weekly_agg = df[df['Detail Produk'].isin(top5_names)].groupby(['Detail Produk', 'Minggu'])['Banyak Penjualan'].sum().reset_index()
    for _, row in df_weekly_agg.iterrows():
        m_name = row['Detail Produk']
        m_week = row['Minggu']
        if m_week in weeks_list:
            idx = weeks_list.index(m_week)
            menus_weekly_dict[m_name][idx] = int(row['Banyak Penjualan'])
            
    weekly_top5_data = {
        "weeks": weeks_list,
        "menus": menus_weekly_dict
    }

    # 7. KEMBALI KE PREDIKSI AWAL (Berdasarkan volume murni)
    df_all_menu = df.groupby('Detail Produk').agg({
        'Banyak Penjualan': 'sum',
        'Penjualan Bersih': 'sum'
    }).reset_index().sort_values(by='Banyak Penjualan', ascending=False)
    
    prediksi_data = []
    for idx, row in enumerate(df_all_menu.iterrows()):
        _, rdata = row
        rank = idx + 1
        skor_bi = max(0.1, min(0.99, 1.0 - (rank * 0.04) + (rdata['Banyak Penjualan'] * 0.002)))
        slope = int(rdata['Banyak Penjualan'] * 0.05) if rank <= 5 else int(-1 * (rank % 3))
        growth = int(skor_bi * 25)
        proj_juni = int(rdata['Banyak Penjualan'] * (1 + (growth/100)))
        proj_juli = int(proj_juni * 1.05)
        
        prediksi_data.append({
            "rank": rank,
            "menu": str(rdata['Detail Produk']),
            "skor_bi": float(skor_bi),
            "total_mei": int(rdata['Banyak Penjualan']),
            "slope": slope,
            "growth": growth,
            "proyeksi_juni": proj_juni,
            "proyeksi_juli": proj_juli
        })

    # 8. PROSES DATA PEAK HOUR
    peak_hour_data = []
    for jam_id in range(24):
        df_jam = df[df['Jam'] == jam_id]
        rev_jam = float(df_jam['Penjualan Bersih'].sum())
        trx_jam = int(df_jam['No Transaksi'].nunique())
        peak_hour_data.append({
            "jam": jam_id,
            "revenue": rev_jam,
            "transaksi": trx_jam
        })

    return {
        "summary": summary_data,
        "daily_trend": daily_trend_data,
        "kategori": kategori_data,
        "top_menu": top_menu_data,
        "weekly_top5": weekly_top5_data,
        "prediksi": prediksi_data,
        "peak_hour": peak_hour_data
    }


# Load data utama ke memori
try:
    DATABASE_DASHBOARD = muat_dan_proses_data()
    print("✅ SUKSES: Data Excel dikonversi sempurna!")
except Exception as e:
    print(f"❌ GAGAL MEMBACA EXCEL: {e}")
    DATABASE_DASHBOARD = {}


# ── FLASK API ENDPOINTS ───────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summary')
def api_summary(): return jsonify(DATABASE_DASHBOARD.get("summary", {}))

@app.route('/api/top-menu')
def api_top_menu(): return jsonify(DATABASE_DASHBOARD.get("top_menu", []))

@app.route('/api/kategori')
def api_kategori(): return jsonify(DATABASE_DASHBOARD.get("kategori", []))

@app.route('/api/daily-trend')
def api_daily_trend(): return jsonify(DATABASE_DASHBOARD.get("daily_trend", []))

@app.route('/api/weekly-top5')
def api_weekly_top5(): return jsonify(DATABASE_DASHBOARD.get("weekly_top5", {}))

@app.route('/api/prediksi')
def api_prediksi(): return jsonify(DATABASE_DASHBOARD.get("prediksi", []))

@app.route('/api/peak-hour')
def api_peak_hour(): return jsonify(DATABASE_DASHBOARD.get("peak_hour", []))


# API BARU: Menghitung Pendapatan Hujan vs Cerah per Minggu
# API BARU: Komparasi Realisasi Omzet Hujan vs Prediksi Target Omzet Cerah
@app.route('/api/weather-revenue')
def get_weather_revenue():
    try:
        # 1. Muat data transaksi penjualan dan data cuaca
        df_sales = pd.read_excel(PATH_EXCEL)
        df_sales['Tanggal_Clean'] = pd.to_datetime(df_sales['Tanggal'], errors='coerce')
        
        df_weather = pd.read_excel(PATH_WEATHER)
        df_weather['Tanggal_Clean'] = pd.to_datetime(df_weather['datetime'], errors='coerce')
        df_weather_clean = df_weather[['Tanggal_Clean', 'precip', 'conditions']].copy().rename(columns={'precip': 'Curah_Hujan', 'conditions': 'Kondisi'})
        
        # 2. Tentukan titik hari ini (Anchor Date berdasarkan scope data Mei 2026)
        hari_ini = pd.to_datetime("2026-05-15")
        
        # 3. Ambil 7 Hari ke Belakang (Historis: 8 Mei s/d 14 Mei)
        tanggal_lalu = [ (hari_ini - pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7, 0, -1) ]
        
        labels_lalu = []
        omzet_lalu = []
        cuaca_lalu = []
        
        for tgl in tanggal_lalu:
            # Hitung total pendapatan di hari tersebut
            sub_sales = df_sales[df_sales['Tanggal_Clean'] == tgl]
            total_rev = sub_sales['Penjualan Bersih'].sum()
            
            # Ambil info cuaca asli di hari tersebut
            sub_weat = df_weather_clean[df_weather_clean['Tanggal_Clean'] == tgl]
            info_cuaca = sub_weat['Kondisi'].values[0] if not sub_weat.empty else "N/A"
            precip_val = sub_weat['Curah_Hujan'].values[0] if not sub_weat.empty else 0
            
            labels_lalu.append(pd.to_datetime(tgl).strftime('%d %b'))
            omzet_lalu.append(float(total_rev))
            cuaca_lalu.append(f"{info_cuaca} ({precip_val}mm)")

        # 4. Ambil 7 Hari ke Depan (Prediksi Cuaca: 15 Mei s/d 21 Mei)
        tanggal_depan = [ (hari_ini + pd.Timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 7) ]
        
        labels_depan = []
        cuaca_depan = []
        
        for tgl in tanggal_depan:
            sub_weat = df_weather_clean[df_weather_clean['Tanggal_Clean'] == tgl]
            info_cuaca = sub_weat['Kondisi'].values[0] if not sub_weat.empty else "Rain Forecast"
            precip_val = sub_weat['Curah_Hujan'].values[0] if not sub_weat.empty else 0
            
            labels_depan.append(pd.to_datetime(tgl).strftime('%d %b'))
            cuaca_depan.append(f"{info_cuaca} ({precip_val}mm)")

        return jsonify({
            "historis": {
                "labels": labels_lalu,
                "revenue": omzet_lalu,
                "cuaca": cuaca_lalu
            },
            "prediksi_cuaca": {
                "labels": labels_depan,
                "cuaca": cuaca_depan
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)