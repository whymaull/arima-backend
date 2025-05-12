# from flask import Blueprint, request, jsonify
# from database.koneksi import get_connection
# from utils.prediksi_arima import get_stock_data, predict_arima
# import json

# predict_bp = Blueprint("predict", __name__)

# @predict_bp.route("/predict", methods=["POST"])
# def predict():
#     content = request.json
#     symbol = content.get("symbol")              # e.g. "BBCA"
#     user_id = content.get("user_id", "guest")
#     periods = content.get("periods", 7)
#     start_date = content.get("start_date")      # ← input user (tanggal prediksi dimulai)
#     period_type = content.get("period", "daily")

#     if not symbol or not start_date:
#         return jsonify({"error": "symbol dan start_date wajib diisi"}), 400

#     try:
#         # Ambil data historis sampai tanggal yang dipilih user
#         data = get_stock_data(f"{symbol}.JK", end=start_date)

#         # Prediksi dimulai dari tanggal tersebut, ke depan sesuai period
#         result = predict_arima(data, n_periods=periods, start_date=start_date, period_type=period_type)

#         # Simpan hanya nilai prediksi (tanpa tanggal)
#         forecast_only = [item['value'] for item in result]

#         # Simpan ke DB
#         conn = get_connection()
#         conn.database = "prediksi_saham"
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO riwayat_prediksi (user_id, symbol, periods, forecast) VALUES (%s, %s, %s, %s)",
#             (user_id, symbol, periods, json.dumps(forecast_only))
#         )
#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({
#             "symbol": symbol,
#             "forecast": result  # ← format [{"date": "...", "value": ...}]
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


from flask import Blueprint, request, jsonify
from database.koneksi import get_connection
from utils.prediksi_arima import get_stock_data, predict_arima
import json

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict", methods=["POST"])
def predict():
    content = request.json
    symbol = content.get("symbol")
    user_id = content.get("user_id", "guest")
    periods = content.get("periods", 7)
    start_date = content.get("start_date")
    period_type = content.get("period", "daily")

    if not symbol or not start_date:
        return jsonify({"error": "symbol dan start_date wajib diisi"}), 400

    try:
        # Ambil data historis sampai tanggal yang dipilih user
        data = get_stock_data(f"{symbol}.JK", end=start_date)
        
        if data is None:
            return jsonify({
            "error": "Data historis tidak ditemukan untuk symbol dan tanggal tersebut."
        }), 400


        # Prediksi dimulai dari tanggal tersebut
        result = predict_arima(data, n_periods=periods, start_date=start_date, period_type=period_type)

        # Simpan hanya nilai prediksi
        forecast_only = [item['value'] for item in result]

        # Simpan ke database
        conn = get_connection()
        conn.database = "prediksi_saham"
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO riwayat_prediksi (user_id, symbol, periods, forecast) VALUES (%s, %s, %s, %s)",
            (user_id, symbol, periods, json.dumps(forecast_only))
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "symbol": symbol,
            "forecast": result  # format: [{"date": "...", "value": ...}]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
