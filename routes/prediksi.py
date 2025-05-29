from flask import Blueprint, request, jsonify
from database.koneksi import get_connection
from utils.prediksi_arima import get_stock_data, predict_arima
import json

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/predict", methods=["POST"])
def predict():

    """
    Prediksi harga saham menggunakan ARIMA
    ---
    tags:
      - Prediksi
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              symbol:
                type: string
                example: KAEF
              user_id:
                type: string
                example: 1
              periods:
                type: integer
                example: 7
              start_date:
                type: string
                format: date
                example: 2024-12-01
              period:
                type: string
                enum: [daily, weekly, monthly]
                example: daily
    responses:
      200:
        description: Berhasil memprediksi
        content:
          application/json:
            schema:
              type: object
              properties:
                symbol:
                  type: string
                forecast:
                  type: array
                  items:
                    type: object
                    properties:
                      date:
                        type: string
                      value:
                        type: number
    """

    content = request.json
    symbol = content.get("symbol")
    user_id = content.get("user_id", "guest")
    periods = content.get("periods", 7)
    start_date = content.get("start_date")
    period_type = content.get("period", "daily")

    if not symbol or not start_date:
        return jsonify({"error": "symbol dan start_date wajib diisi"}), 400

    try:
        # Tentukan interval berdasarkan periode
        interval_map = {
            "daily": "1d",
            "weekly": "1wk",
            "monthly": "1mo"
        }
        interval = interval_map.get(period_type, "1d")

        # Ambil data historis saham dengan interval sesuai
        data = get_stock_data(f"{symbol}.JK", end=start_date, interval=interval)

        if data is None:
            return jsonify({
                "error": "Data historis tidak ditemukan untuk symbol dan tanggal tersebut."
            }), 400

        # Lakukan prediksi
        result = predict_arima(
            data,
            n_periods=periods,
            start_date=start_date,
            period_type=period_type
        )

        # Simpan ke database
        conn = get_connection()
        conn.database = "prediksi_saham"
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO riwayat_prediksi (user_id, symbol, start_date, period_type, periods, forecast)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            symbol,
            start_date,
            period_type,
            periods,
            json.dumps(result)
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "symbol": symbol,
            "forecast": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
