from flask import Flask, render_template

from services.preprocessing import load_data
from services.kpi import get_kpi
from services.top_menu import get_top_menu

app = Flask(__name__)

@app.route('/')
def home():

    df = load_data()

    kpi = get_kpi(df)

    top_menu = get_top_menu(df)

    return render_template(
        'index.html',

        total_revenue=kpi['total_revenue'],
        total_item=kpi['total_item'],
        total_trx=kpi['total_trx'],
        avg_trx=kpi['avg_trx'],

        top_menu=top_menu.to_dict('records')
    )

if __name__ == '__main__':
    app.run(debug=True)