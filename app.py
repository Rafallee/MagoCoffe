from flask import Flask, jsonify, render_template

app = Flask(__name__)

# ── DATA SIMULASI (Sudah disinkronkan dengan penamaan properti di main.js) ──

SUMMARY = {
    "total_revenue": 487_320_500,
    "total_item": 12_847,
    "total_transaksi": 4_213,
    "avg_trx_value": 115_672,
    "periode": "Mei 2026"
}

TOP_MENU = [
    {"menu": "Es Kopi Susu", "jumlah_terjual": 1842, "total_revenue": 82_890_000, "revenue_pct": 17.0},
    {"menu": "Dirty Latte", "jumlah_terjual": 1256, "total_revenue": 62_800_000, "revenue_pct": 12.9},
    {"menu": "Americano (Ice)", "jumlah_terjual": 987, "total_revenue": 39_480_000, "revenue_pct": 8.1},
    {"menu": "Matcha Latte", "jumlah_terjual": 763, "total_revenue": 38_150_000, "revenue_pct": 7.8},
    {"menu": "French Fries with Truffle Oil", "jumlah_terjual": 621, "total_revenue": 37_260_000, "revenue_pct": 7.6},
    {"menu": "Caramel Macchiato", "jumlah_terjual": 589, "total_revenue": 29_450_000, "revenue_pct": 6.0},
    {"menu": "Cappuccino", "jumlah_terjual": 544, "total_revenue": 21_760_000, "revenue_pct": 4.5},
    {"menu": "Croissant Butter", "jumlah_terjual": 498, "total_revenue": 19_920_000, "revenue_pct": 4.1},
    {"menu": "Taro Latte", "jumlah_terjual": 431, "total_revenue": 21_550_000, "revenue_pct": 4.4},
    {"menu": "Lemonade Sparkling", "jumlah_terjual": 387, "total_revenue": 15_480_000, "revenue_pct": 3.2},
    {"menu": "Chicken Sandwich", "jumlah_terjual": 342, "total_revenue": 20_520_000, "revenue_pct": 4.2},
    {"menu": "Cold Brew", "jumlah_terjual": 298, "total_revenue": 14_900_000, "revenue_pct": 3.1},
    {"menu": "Avocado Toast", "jumlah_terjual": 267, "total_revenue": 18_690_000, "revenue_pct": 3.8},
    {"menu": "Espresso", "jumlah_terjual": 243, "total_revenue": 7_290_000, "revenue_pct": 1.5},
    {"menu": "Mango Smoothie", "jumlah_terjual": 221, "total_revenue": 11_050_000, "revenue_pct": 2.3},
]

KATEGORI = [
    {"kategori": "Kopi Susu", "jumlah": 4428, "revenue": 195_140_000, "pct": 34.5},
    {"kategori": "Non-Coffee", "jumlah": 2801, "revenue": 112_040_000, "pct": 21.8},
    {"kategori": "Makanan", "jumlah": 1728, "revenue": 96_768_000, "pct": 18.7},
    {"kategori": "Black Coffee", "jumlah": 1528, "revenue": 61_120_000, "pct": 12.6},
    {"kategori": "Minuman", "jumlah": 987, "revenue": 14_805_000, "pct": 8.1},
    {"kategori": "Lainnya", "jumlah": 375, "revenue": 7_447_500, "pct": 4.3},
]

DAILY_TREND = [
    {"tanggal": "01 Mei", "revenue": 14_200_000, "transaksi": 112},
    {"tanggal": "02 Mei", "revenue": 11_800_000, "transaksi": 98},
    {"tanggal": "03 Mei", "revenue": 10_500_000, "transaksi": 87},
    {"tanggal": "04 Mei", "revenue": 15_600_000, "transaksi": 124},
    {"tanggal": "05 Mei", "revenue": 17_800_000, "transaksi": 138},
    {"tanggal": "06 Mei", "revenue": 18_200_000, "transaksi": 142},
    {"tanggal": "07 Mei", "revenue": 19_400_000, "transaksi": 156},
    {"tanggal": "08 Mei", "revenue": 16_100_000, "transaksi": 131},
    {"tanggal": "09 Mei", "revenue": 13_700_000, "transaksi": 109},
    {"tanggal": "10 Mei", "revenue": 12_300_000, "transaksi": 103},
    {"tanggal": "11 Mei", "revenue": 15_900_000, "transaksi": 127},
    {"tanggal": "12 Mei", "revenue": 18_700_000, "transaksi": 149},
    {"tanggal": "13 Mei", "revenue": 20_100_000, "transaksi": 158},
    {"tanggal": "14 Mei", "revenue": 21_300_000, "transaksi": 167},
    {"tanggal": "15 Mei", "revenue": 17_600_000, "transaksi": 140},
    {"tanggal": "16 Mei", "revenue": 14_200_000, "transaksi": 113},
    {"tanggal": "17 Mei", "revenue": 13_400_000, "transaksi": 108},
    {"tanggal": "18 Mei", "revenue": 16_800_000, "transaksi": 133},
    {"tanggal": "19 Mei", "revenue": 19_200_000, "transaksi": 151},
    {"tanggal": "20 Mei", "revenue": 22_400_000, "transaksi": 174},
    {"tanggal": "21 Mei", "revenue": 23_600_000, "transaksi": 181},
    {"tanggal": "22 Mei", "revenue": 20_800_000, "transaksi": 163},
    {"tanggal": "23 Mei", "revenue": 17_400_000, "transaksi": 138},
    {"tanggal": "24 Mei", "revenue": 15_100_000, "transaksi": 122},
    {"tanggal": "25 Mei", "revenue": 17_900_000, "transaksi": 141},
    {"tanggal": "26 Mei", "revenue": 20_600_000, "transaksi": 160},
    {"tanggal": "27 Mei", "revenue": 24_100_000, "transaksi": 187},
    {"tanggal": "28 Mei", "revenue": 25_300_000, "transaksi": 194},
    {"tanggal": "29 Mei", "revenue": 22_700_000, "transaksi": 176},
    {"tanggal": "30 Mei", "revenue": 19_800_000, "transaksi": 155},
    {"tanggal": "31 Mei", "revenue": 16_900_000, "transaksi": 132},
]

WEEKLY_TOP5 = {
    "weeks": ["W1 (1-3 Mei)", "W2 (4-10 Mei)", "W3 (11-17 Mei)", "W4 (18-24 Mei)", "W5 (25-31 Mei)"],
    "menus": {
        "Es Kopi Susu": [310, 378, 402, 387, 365],
        "Dirty Latte": [198, 241, 278, 263, 276],
        "Americano (Ice)": [167, 189, 198, 214, 219],
        "Matcha Latte": [112, 138, 158, 172, 183],
        "French Fries with Truffle Oil": [72, 98, 138, 152, 161],
    }
}

PREDIKSI = [
    {"rank": 1, "menu": "Es Kopi Susu", "total_mei": 1842, "slope": 13.8, "growth": 17.7, "proyeksi_w6": 391, "proyeksi_w7": 405, "skor_bi": 0.921},
    {"rank": 2, "menu": "Dirty Latte", "total_mei": 1256, "slope": 19.5, "growth": 39.4, "proyeksi_w6": 295, "proyeksi_w7": 315, "skor_bi": 0.887},
    {"rank": 3, "menu": "French Fries with Truffle Oil", "total_mei": 621, "slope": 22.3, "growth": 123.6, "proyeksi_w6": 183, "proyeksi_w7": 205, "skor_bi": 0.863},
    {"rank": 4, "menu": "Matcha Latte", "total_mei": 763, "slope": 17.8, "growth": 63.4, "proyeksi_w6": 200, "proyeksi_w7": 218, "skor_bi": 0.841},
    {"rank": 5, "menu": "Americano (Ice)", "total_mei": 987, "slope": 13.0, "growth": 31.1, "proyeksi_w6": 232, "proyeksi_w7": 245, "skor_bi": 0.798},
    {"rank": 6, "menu": "Caramel Macchiato", "total_mei": 589, "slope": 11.2, "growth": 28.4, "proyeksi_w6": 152, "proyeksi_w7": 163, "skor_bi": 0.724},
    {"rank": 7, "menu": "Taro Latte", "total_mei": 431, "slope": 9.4, "growth": 41.2, "proyeksi_w6": 121, "proyeksi_w7": 131, "skor_bi": 0.698},
    {"rank": 8, "menu": "Cappuccino", "total_mei": 544, "slope": 7.1, "growth": 18.9, "proyeksi_w6": 138, "proyeksi_w7": 145, "skor_bi": 0.651},
    {"rank": 9, "menu": "Lemonade Sparkling", "total_mei": 387, "slope": 8.6, "growth": 32.7, "proyeksi_w6": 107, "proyeksi_w7": 116, "skor_bi": 0.627},
    {"rank": 10, "menu": "Avocado Toast", "total_mei": 267, "slope": 6.2, "growth": 45.1, "proyeksi_w6": 79, "proyeksi_w7": 86, "skor_bi": 0.589},
]

PEAK_HOUR = [
    {"jam": 7, "revenue": 3_200_000, "transaksi": 28},
    {"jam": 8, "revenue": 8_700_000, "transaksi": 71},
    {"jam": 9, "revenue": 14_300_000, "transaksi": 112},
    {"jam": 10, "revenue": 18_900_000, "transaksi": 148},
    {"jam": 11, "revenue": 22_400_000, "transaksi": 175},
    {"jam": 12, "revenue": 31_200_000, "transaksi": 241},
    {"jam": 13, "revenue": 28_700_000, "transaksi": 223},
    {"jam": 14, "revenue": 24_100_000, "transaksi": 189},
    {"jam": 15, "revenue": 36_800_000, "transaksi": 287},
    {"jam": 16, "revenue": 42_300_000, "transaksi": 328},
    {"jam": 17, "revenue": 38_600_000, "transaksi": 301},
    {"jam": 18, "revenue": 34_200_000, "transaksi": 268},
    {"jam": 19, "revenue": 29_400_000, "transaksi": 231},
    {"jam": 20, "revenue": 22_100_000, "transaksi": 174},
    {"jam": 21, "revenue": 14_800_000, "transaksi": 117},
    {"jam": 22, "revenue": 7_400_000, "transaksi": 58},
]

# Rekomendasi berdasarkan 3 menu teratas dari data PREDIKSI
REKOMENDASI = [
    f"Prioritaskan stok {PREDIKSI[0]['menu']} (BI Score {PREDIKSI[0]['skor_bi']})",
    f"Prioritaskan stok {PREDIKSI[1]['menu']} (BI Score {PREDIKSI[1]['skor_bi']})",
    f"Prioritaskan stok {PREDIKSI[2]['menu']} (BI Score {PREDIKSI[2]['skor_bi']})",
    "Optimalkan promo pada jam sibuk",
    "Perluas penjualan melalui delivery"
]


# ── API Endpoints ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summary')
def api_summary():
    return jsonify(SUMMARY)

@app.route('/api/top-menu')
def api_top_menu():
    return jsonify(TOP_MENU)

@app.route('/api/kategori')
def api_kategori():
    return jsonify(KATEGORI)

@app.route('/api/daily-trend')
def api_daily_trend():
    return jsonify(DAILY_TREND)

@app.route('/api/weekly-top5')
def api_weekly_top5():
    return jsonify(WEEKLY_TOP5)

@app.route('/api/prediksi')
def api_prediksi():
    return jsonify(PREDIKSI)

@app.route('/api/peak-hour')
def api_peak_hour():
    return jsonify(PEAK_HOUR)

@app.route('/api/rekomendasi')
def api_rekomendasi():
    return jsonify(REKOMENDASI)


if __name__ == '__main__':
    app.run(debug=True, port=5000)