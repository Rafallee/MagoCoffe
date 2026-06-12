from flask import Flask, render_template

from services.preprocessing import load_data
from services.kpi import get_kpi
from services.top_menu import get_top_menu
from services.charts import create_kategori_chart
from services.kategori import get_kategori
from services.forecasting import get_daily_trend
from services.forecasting import get_daily_trend
from services.forecasting import get_forecast
from services.scoring import get_bi_score
from services.recommendation import get_recommendation
from services.peak_hour import get_peak_hour
from services.weekly_trend import get_weekly_trend


app = Flask(__name__)

@app.route('/')
def home():

    df = load_data()

    kpi = get_kpi(df)

    top_menu = get_top_menu(df)

    kategori = get_kategori(df)

    create_kategori_chart(kategori)

    daily = get_daily_trend(df)

    forecast = get_forecast(df)

    score = get_bi_score(forecast)

    recommendation = get_recommendation(score)

    hourly, peak_hour = get_peak_hour(df)

    weekly_menu = get_weekly_trend(df)

    return render_template(

    'index.html',

    total_revenue=kpi['total_revenue'],
    total_item=kpi['total_item'],
    total_trx=kpi['total_trx'],
    avg_trx=kpi['avg_trx'],

    top_menu=top_menu.to_dict('records'),

    kategori=kategori.to_dict('records'),

    daily=daily.tail(10).to_dict('records'),

    forecast=forecast.head(10).to_dict('records'),

    score=score.head(10).to_dict('records'),

    recommendation=recommendation,

    hourly=hourly.to_dict('records'),

    peak_hour=peak_hour,

    weekly_menu=weekly_menu.reset_index().to_dict('records')
)

if __name__ == '__main__':
    app.run(debug=True)