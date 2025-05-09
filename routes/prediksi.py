from flask import Blueprint, request, jsonify
from database.koneksi import get_connection # type: ignore
from utils.prediksi_arima import get_stock_data, predict_arima # type: ignore
import json

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict", methods=["POST"])
def predict():
    content = request.json
    symbol = content.get("symbol")
    user_id = content.get("user_id", "guest")
    periods = content.get("periods", 7)

    try:
        data = get_stock_data(f"{symbol}.JK")
        forecast = predict_arima(data, periods)

        conn = get_connection()
        conn.database = "prediksi_saham"
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO riwayat_prediksi (user_id, symbol, periods, forecast) VALUES (%s, %s, %s, %s)",
            (user_id, symbol, periods, json.dumps(forecast))
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"symbol": symbol, "forecast": forecast})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
