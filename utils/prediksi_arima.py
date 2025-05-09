import yfinance as yf
from pmdarima import auto_arima

def get_stock_data(symbol, start="2024-01-01", end="2025-05-01"):
    data = yf.download(symbol, start=start, end=end)
    return data['Close']

def predict_arima(data, n_periods=7):
    model = auto_arima(data, seasonal=False, suppress_warnings=True)
    return model.predict(n_periods=n_periods).tolist()
