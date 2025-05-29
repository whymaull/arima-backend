from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.schema import get_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():

    """
    Register pengguna baru
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              username:
                type: string
                example: johndoe
              email:
                type: string
                example: johndoe@gmail.com
              password:
                type: string
                example: secret123
    responses:
      200:
        description: Berhasil register
    """

    data = request.get_json()
    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                   (username, email, password))
    conn.commit()
    return jsonify({'message': 'Daftar Berhasil'})

@auth_bp.route('/login', methods=['POST'])
def login():

    """
    Login ke sistem
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                example: johndoe@example.com
              password:
                type: string
                example: secret123
    responses:
      200:
        description: Login berhasil
      401:
        description: Email atau password salah
    """

    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user[3], password):
        return jsonify({'message': 'Login Berhasil', 'user': {
            'id': user[0], 'username': user[1], 'email': user[2]
        }})
    else:
        return jsonify({'message': 'Email atau password salah'}), 401

@auth_bp.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):

    """
    Ambil profil pengguna berdasarkan user_id
    ---
    tags:
      - Auth
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Data profil ditemukan
      404:
        description: User tidak ditemukan
    """

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500