import pandas as pd

def minmax_norm(series):

    rng = series.max() - series.min()

    if rng == 0:
        return series * 0

    return (series - series.min()) / rng


def get_bi_score(forecast):

    df_score = forecast.copy()

    df_score['norm_volume'] = minmax_norm(
        df_score['Total Mei']
    )

    df_score['norm_slope'] = minmax_norm(
        df_score['Slope']
    )

    df_score['norm_growth'] = minmax_norm(
        df_score['Growth']
    )

    df_score['Skor BI'] = (

        0.40 * df_score['norm_volume']

        +

        0.35 * df_score['norm_slope']

        +

        0.25 * df_score['norm_growth']

    ).round(3)

    df_score = df_score.sort_values(
        'Skor BI',
        ascending=False
    )

    return df_score