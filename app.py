from flask import Flask, jsonify, render_template
import pandas as pd
import numpy as np
import os

from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# ── CONFIG JALUR DATA EXCEL ──
FOLDER_DATA = "data"
NAMA_FILE_EXCEL = "Product Sales Details - Mago Coffee - All Outlets - 01 May 2026 - 31 May 2026.xls" 
PATH_EXCEL = os.path.join(FOLDER_DATA, NAMA_FILE_EXCEL)


def clean_num(val):
    """Fungsi pembantu memastikan tidak ada NaN numerik yang dikirim ke JSON"""
    if isinstance(val, float) and np.isnan(val):
        return 0
    return val


def muat_dan_proses_data():
    """Fungsi inti membaca Excel dan menyusun struktur data 100% sesuai main.js"""
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

    # Data mingguan semua menu
    weekly_sales = (
        df.groupby(['Minggu', 'Detail Produk'])['Banyak Penjualan']
        .sum()
        .unstack(fill_value=0)
    )

    # 2. PROSES DATA KPI SUMMARY (`s` di main.js)
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

    # 3. PROSES DATA DAILY TREND (`DATA.dailyTrend` di main.js)
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

    # 4. PROSES DATA KATEGORI (`DATA.kategori` di main.js)
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

    # 5. PROSES DATA TOP 15 MENU (`DATA.topMenu` di main.js)
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

    # 6. PROSES DATA TREN MINGGUAN TOP 5 (`DATA.weeklyTop5` di main.js) - STRUKTUR PENENTU FIX ERROR!
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

    # 7. PROSES DATA PREDIKSI JUNI-JULI (`DATA.prediksi` di main.js)
    # Membuat hitungan statistik dasar otomatis (Rank, Skor BI, Proyeksi) berbasis data riil Mei
    df_all_menu = df.groupby('Detail Produk').agg({
        'Banyak Penjualan': 'sum',
        'Penjualan Bersih': 'sum'
    }).reset_index().sort_values(by='Banyak Penjualan', ascending=False)
    
    prediksi_data = []
    for idx, row in enumerate(df_all_menu.iterrows()):
        _, rdata = row
        rank = idx + 1

        menu_name = rdata['Detail Produk']

        if menu_name not in weekly_sales.columns:
            continue

        y = weekly_sales[menu_name].values.astype(float)
        

        if len(y) < 5:
            continue

        x = np.array([1,2,3,4,5]).reshape(-1,1)

        model = LinearRegression()
        model.fit(x,y)

        pred_w6  = max(0, model.predict([[6]])[0])
        pred_w7  = max(0, model.predict([[7]])[0])
        pred_w8  = max(0, model.predict([[8]])[0])
        pred_w9  = max(0, model.predict([[9]])[0])

        pred_w10 = max(0, model.predict([[10]])[0])
        pred_w11 = max(0, model.predict([[11]])[0])
        pred_w12 = max(0, model.predict([[12]])[0])
        pred_w13 = max(0, model.predict([[13]])[0])

        # Total prediksi per bulan
        proj_juni = int(round(
            pred_w6 +
            pred_w7 +
            pred_w8 +
            pred_w9
        ))

        proj_juli = int(round(
            pred_w10 +
            pred_w11 +
            pred_w12 +
            pred_w13
        ))

        # BATASI KENAIKAN MAKSIMAL 20%
        max_growth = 0.20

        max_juni = int(rdata['Banyak Penjualan'] * (1 + max_growth))
        proj_juni = min(proj_juni, max_juni)

        max_juli = int(proj_juni * (1 + max_growth))
        proj_juli = min(proj_juli, max_juli)

    

        # Simulasi skor logis & proyeksi linear aman dari volume penjualan asli
        skor_bi = max(0.1, min(0.99, 1.0 - (rank * 0.04) + (rdata['Banyak Penjualan'] * 0.002)))
        slope = round(model.coef_[0], 2)
        growth = 0

        if rdata['Banyak Penjualan'] > 0:
            growth = (
                (proj_juni - rdata['Banyak Penjualan'])
                / rdata['Banyak Penjualan']
            ) * 100

                
        prediksi_data.append({
            "rank": rank,
            "menu": str(rdata['Detail Produk']),
            "skor_bi": float(skor_bi),
            "total_mei": int(rdata['Banyak Penjualan']),
            "slope": slope,
            "growth": round(growth, 2),
            "proyeksi_juni": proj_juni,
            "proyeksi_juli": proj_juli
        })

    # 8. PROSES DATA PEAK HOUR (`DATA.peakHour` di main.js)
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


# Load data ke memori saat program dijalankan
try:
    DATABASE_DASHBOARD = muat_dan_proses_data()
    print("✅ SUKSES: Data Excel dikonversi sempurna ke format main.js!")
except Exception as e:
    print(f"❌ GAGAL MEMBACA EXCEL: {e}")
    DATABASE_DASHBOARD = {}


# ── FLASK API ENDPOINTS ───────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summary')
def api_summary():
    return jsonify(DATABASE_DASHBOARD.get("summary", {}))

@app.route('/api/top-menu')
def api_top_menu():
    return jsonify(DATABASE_DASHBOARD.get("top_menu", []))

@app.route('/api/kategori')
def api_kategori():
    return jsonify(DATABASE_DASHBOARD.get("kategori", []))

@app.route('/api/daily-trend')
def api_daily_trend():
    return jsonify(DATABASE_DASHBOARD.get("daily_trend", []))

@app.route('/api/weekly-top5')
def api_weekly_top5():
    return jsonify(DATABASE_DASHBOARD.get("weekly_top5", {"weeks": [], "menus": {}}))

@app.route('/api/prediksi')
def api_prediksi():
    return jsonify(DATABASE_DASHBOARD.get("prediksi", []))

@app.route('/api/peak-hour')
def api_peak_hour():
    return jsonify(DATABASE_DASHBOARD.get("peak_hour", []))


if __name__ == '__main__':
    app.run(debug=True, port=5000)