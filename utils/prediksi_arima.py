from datetime import datetime, timedelta
import warnings
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import pandas as pd
import yfinance as yf
from statsmodels.tsa.stattools import adfuller


def get_stock_data(symbol, end, start="2023-01-01", interval="1d"):
    df = yf.download(symbol, start=start, end=end, interval=interval, progress=False, auto_adjust=False)

    if df.empty:
        print(f"❌ Data kosong untuk {symbol}")
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"][symbol]
    else:
        df = df["Close"]

    df = df.dropna()
    df.index = pd.to_datetime(df.index)

    print(f"✅ get_stock_data berhasil")
    print(f"📅 Range index: {df.index.min()} → {df.index.max()}")
    print(f"⏱️ Freq hasil infer: {pd.infer_freq(df.index)}")
    print(f"🔢 Jumlah data: {len(df)}")
    print(f"📊 Type: {type(df)}, Nulls: {df.isnull().sum()}")

    print("\n📊 Data yang dikirim ke ARIMA (preview):")
    print(df.head())

    return df 

def make_stationary(data, max_diff=3, alpha=0.05):
    print("📌 Memulai ADF Test...")
    
    d = 0
    while d <= max_diff:
        adf_result = adfuller(data)
        p_value = adf_result[1]
        print(f"📉 ADF Test (d={d}) — p-value: {p_value:.5f}")
        if p_value <= alpha:
            print(f"✅ Data stasioner pada differencing ke-{d}")
            return data, d
        data = data.diff().dropna()
        d += 1
    print("⚠️ Data tidak stasioner meskipun sudah di-difference hingga batas maksimal.")
    return data, d



def predict_arima(data, n_periods=7, start_date=None, period_type='daily'):
    warnings.filterwarnings("ignore")

    # Ambil kolom Close jika DataFrame
    if isinstance(data, pd.DataFrame):
        if "Close" in data.columns:
            data = data["Close"]
        else:
            raise ValueError("Data tidak mengandung kolom 'Close'")

    data = data.dropna().astype(float)

    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)

    if data.index.freq is None:
        data.index.freq = pd.infer_freq(data.index)

    data_stationary, d = make_stationary(data) 

    best_rmse = float("inf")
    best_model = None
    best_order = None
    best_mae = None
    best_mape = None

    print("\n🚀 Mulai tuning ARIMA...\n")

    for p in range(0, 7):
        for q in range(0, 7):
            try:
                model = ARIMA(data, order=(p, d, q))
                fitted_model = model.fit()

                in_sample_pred = fitted_model.predict(start=0, end=len(data)-1)
                in_sample_pred.index = data.index

                rmse = np.sqrt(mean_squared_error(data.values, in_sample_pred.values))
                mae = mean_absolute_error(data.values, in_sample_pred.values)
                mask = data.values != 0
                mape = np.mean(np.abs((data.values[mask] - in_sample_pred.values[mask]) / data.values[mask])) * 100

                print(f"🔍 ARIMA({p},{d},{q}) — RMSE: {rmse:.2f} | MAE: {mae:.2f} | MAPE: {mape:.2f}%")

                if rmse < best_rmse:
                    best_rmse = rmse
                    best_model = fitted_model
                    best_order = (p, d, q)
                    best_mae = mae
                    best_mape = mape

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
    print(f"MAE : {best_mae:.2f}")
    print(f"MAPE: {best_mape:.2f}%\n")

    base_date = datetime.strptime(start_date, "%Y-%m-%d")
    step = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30),
    }.get(period_type, timedelta(days=1))

    dates = [base_date + i * step for i in range(1, n_periods + 1)]

    print("\n📈 Hasil Prediksi:")
    for d, v in zip(dates, forecast):
        print(f"{d.strftime('%Y-%m-%d')} → {round(v, 2)}")

    return [{"date": d.strftime("%Y-%m-%d"), "value": round(v, 2)} for d, v in zip(dates, forecast)]


# def predict_arima(data, n_periods=7, start_date=None, period_type='daily'):
#     warnings.filterwarnings("ignore")

#     if isinstance(data, pd.DataFrame):
#         if "Close" in data.columns:
#             data = data["Close"]
#         else:
#             raise ValueError("DataFrame tidak memiliki kolom 'Close'")

#     data = data.dropna()

#     # Pastikan Series valid
#     data = data.dropna()
#     if not isinstance(data.index, pd.DatetimeIndex):
#         data.index = pd.to_datetime(data.index)

#     data = data.astype(float)

#     if data.index.freq is None:
#         data.index.freq = data.index.inferred_freq

#     d = 1
#     best_rmse = float("inf")
#     best_model = None
#     best_order = None
#     best_mae = None
#     best_mape = None

#     print("🚀 Mulai tuning ARIMA...\n")

#     for p in range(0, 6):
#         for q in range(0, 6):
#             try:
#                 model = ARIMA(data, order=(p, d, q))
#                 fitted_model = model.fit()

#                 in_sample_pred = fitted_model.predict(start=0, end=len(data)-1)
#                 in_sample_pred = pd.Series(in_sample_pred, index=data.index) 

#                 rmse = np.sqrt(mean_squared_error(data, in_sample_pred))
#                 mae = mean_absolute_error(data, in_sample_pred)
#                 mask = data != 0  # hindari pembagi 0
#                 mape = np.mean(np.abs((data[mask] - in_sample_pred[mask]) / data[mask])) * 100

#                 print(f"🔍 ARIMA({p},{d},{q}) — RMSE: {rmse:.2f} | MAE: {mae:.2f} | MAPE: {mape:.2f}%")

#                 if rmse < best_rmse:
#                     best_rmse = rmse
#                     best_model = fitted_model
#                     best_order = (p, d, q)
#                     best_mae = mae
#                     best_mape = mape

#             except Exception as e:
#                 print(f"❌ Gagal ARIMA({p},{d},{q}): {e}")
#                 continue

#     if not best_model:
#         print("⚠️ Tidak ada model yang berhasil dipakai.")
#         return []

#     print(f"\n✅ Best model: ARIMA{best_order}")
#     print(best_model.summary())

#     forecast = best_model.forecast(steps=n_periods)

#     print(f"\n📈 Evaluation Metrics:")
#     print(f"RMSE: {best_rmse:.2f}")
#     print(f"MAE : {best_mae:.2f}")
#     print(f"MAPE: {best_mape:.2f}%")
#     print(f"MAPE: {best_mape:.2f}%\n")

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

