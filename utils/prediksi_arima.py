from datetime import datetime, timedelta
import warnings
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import yfinance as yf

def get_stock_data(symbol, end, start="2023-01-01", interval="1d"):
    df = yf.download(symbol, start=start, end=end, interval=interval, progress=False, auto_adjust=False, threads=False, timeout=20)

    if df is None or df.empty:
        print(f"❌ Data kosong untuk {symbol} dengan interval {interval}")
        return None

    try:
        close = df["Close"]
        if close.empty:
            print("❌ Kolom 'Close' kosong.")
            return None

        print(f"\n📊 Data harga penutupan saham '{symbol}' dari {start} sampai {end} (interval: {interval}):\n")
        print(close.to_string())

        return close  
    except Exception as e:
        print(f"❌ Gagal parsing data: {e}")
        return None

# def predict_arima(data, n_periods=7, start_date=None, period_type='daily'):
    
#     if period_type == 'weekly':
#         seasonal = True
#         m = 52
#     elif period_type == 'monthly':
#         seasonal = True
#         m = 12
#     else:  
#         seasonal = False
#         m = 1

#     model = auto_arima(
#         data,
#         seasonal=seasonal,
#         m=m,
#         stepwise=True,
#         max_p=6,
#         max_q=6,
#         max_order=5,
#         suppress_warnings=True,
#         error_action="ignore"
#     )

#     # Cetak model dan summary
#     print(f"\n✅ Best model: {model.order}")
#     print(model.summary())

#     forecast = model.predict(n_periods=n_periods).tolist()

#     in_sample_pred = model.predict_in_sample()
#     rmse = np.sqrt(mean_squared_error(data, in_sample_pred))
#     mae = mean_absolute_error(data, in_sample_pred)

#     print(f"\n📈 Evaluation Metrics:")
#     print(f"RMSE: {rmse:.2f}")
#     print(f"MAE : {mae:.2f}\n")

#     base_date = datetime.strptime(start_date, "%Y-%m-%d")

#     step = {
#         'daily': timedelta(days=1),
#         'weekly': timedelta(weeks=1),
#         'monthly': timedelta(days=30),
#     }.get(period_type, timedelta(days=1))

#     dates = [base_date + i * step for i in range(1, n_periods + 1)]
#     print("\n📈 Hasil Prediksi:")
#     for d, v in zip(dates, forecast):
#         print(f"{d.strftime('%Y-%m-%d')}  →  {round(v, 2)}")

#     return [{"date": d.strftime("%Y-%m-%d"), "value": round(v, 2)} for d, v in zip(dates, forecast)]


def predict_arima(data, n_periods=7, start_date=None, period_type='daily'):
    warnings.filterwarnings("ignore")

    if data.index.freq is None:
        data.index.freq = data.index.inferred_freq

    d = 1
    best_rmse = float("inf")
    best_model = None
    best_order = None
    best_mae = None

    print("🚀 Mulai tuning ARIMA...\n")

    for p in range(0, 6):
        for q in range(0, 6):
            try:
                model = ARIMA(data, order=(p, d, q))
                fitted_model = model.fit()

                in_sample_pred = fitted_model.predict(start=0, end=len(data)-1)
                rmse = np.sqrt(mean_squared_error(data, in_sample_pred))
                mae = mean_absolute_error(data, in_sample_pred)

                print(f"🔍 ARIMA({p},{d},{q}) — RMSE: {rmse:.2f} | MAE: {mae:.2f}")

                if rmse < best_rmse:
                    best_rmse = rmse
                    best_model = fitted_model
                    best_order = (p, d, q)
                    best_mae = mae

            except Exception as e:
                print(f"❌ Gagal ARIMA({p},{d},{q}): {e}")
                continue

    if not best_model:
        print("⚠️ Tidak ada model yang berhasil dipakai.")
        return []

    print(f"\n✅ Best model: ARIMA{best_order}")
    print(best_model.summary())

    forecast = best_model.forecast(steps=n_periods)

    print(f"\n📈 Evaluation Metrics:")
    print(f"RMSE: {best_rmse:.2f}")
    print(f"MAE : {best_mae:.2f}\n")

    base_date = datetime.strptime(start_date, "%Y-%m-%d")
    step = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30),
    }.get(period_type, timedelta(days=1))

    dates = [base_date + i * step for i in range(1, n_periods + 1)]

    print("\n📈 Hasil Prediksi:")
    for d, v in zip(dates, forecast):
        print(f"{d.strftime('%Y-%m-%d')}  →  {round(v, 2)}")

    return [{"date": d.strftime("%Y-%m-%d"), "value": round(v, 2)} for d, v in zip(dates, forecast)]