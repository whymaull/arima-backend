from flask import Blueprint, jsonify
from database.koneksi import get_connection 

symbol_bp = Blueprint("symbols", __name__)

@symbol_bp.route("/symbols", methods=["GET"])
def get_symbols():

    """
    Ambil daftar kode saham dari database
    ---
    tags:
      - Saham
    responses:
      200:
        description: Daftar simbol saham
    """

    conn = get_connection()
    conn.database = "prediksi_saham"
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT symbol, name FROM daftar_saham ORDER BY symbol")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)
