# import yfinance as yf
# from pmdarima import auto_arima
# from datetime import datetime, timedelta

# def get_stock_data(symbol, end, start="2024-01-01"):
#     df = yf.download(symbol, start=start, end=end)
#     return df['Close'].dropna()

# def predict_arima(data, n_periods=7, start_date=None, period_type='daily'):
#     model = auto_arima(data, seasonal=False, suppress_warnings=True)
#     forecast = model.predict(n_periods=n_periods).tolist()

#     base_date = datetime.strptime(start_date, "%Y-%m-%d")

#     step = {
#         'daily': timedelta(days=1),
#         'weekly': timedelta(weeks=1),
#         'monthly': timedelta(days=30), 
#     }.get(period_type, timedelta(days=1))

#     dates = [(base_date + step * i).strftime("%Y-%m-%d") for i in range(1, n_periods + 1)]

#     return [{"date": d, "value": v} for d, v in zip(dates, forecast)]


import yfinance as yf
from pmdarima import auto_arima
from datetime import datetime, timedelta

def get_stock_data(symbol, end, start="2024-01-01"):
    df = yf.download(symbol, start=start, end=end, progress=False)

    if df is None or df.empty:
        return None

    try:
        close = df["Close"]
        if close.empty:
            return None
        return close  # Series
    except Exception:
        return None

def predict_arima(data, n_periods=7, start_date=None, period_type='daily'):
    model = auto_arima(
        data,
        seasonal=False,
        stepwise=True,
        max_p=3,
        max_q=3,
        max_order=5,
        suppress_warnings=True,
        error_action="ignore"
    )

    forecast = model.predict(n_periods=n_periods).tolist()

    base_date = datetime.strptime(start_date, "%Y-%m-%d")
    step = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30),
    }.get(period_type, timedelta(days=1))

    dates = [base_date + i * step for i in range(1, n_periods + 1)]

    return [{"date": d.strftime("%Y-%m-%d"), "value": round(v, 2)} for d, v in zip(dates, forecast)]
