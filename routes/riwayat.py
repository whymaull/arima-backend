from flask import Blueprint, request, jsonify
from database.koneksi import get_connection

riwayat_bp = Blueprint('riwayat', __name__)

@riwayat_bp.route('/riwayat/<user_id>', methods=['GET'])
def get_riwayat(user_id):

    """
    Ambil riwayat prediksi berdasarkan user_id
    ---
    tags:
      - Riwayat
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Riwayat berhasil diambil
    """


    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, user_id, symbol, start_date, period_type, periods, forecast, created_at
        FROM riwayat_prediksi
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    
    riwayat = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(riwayat)


@riwayat_bp.route('/riwayat/<int:riwayat_id>', methods=['DELETE'])
def delete_riwayat(riwayat_id):

    """
    Hapus riwayat prediksi berdasarkan ID
    ---
    tags:
      - Riwayat
    parameters:
      - name: riwayat_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Riwayat berhasil dihapus
    """


    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM riwayat_prediksi WHERE id = %s", (riwayat_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Riwayat berhasil dihapus"})
