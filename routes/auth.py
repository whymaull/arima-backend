from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.schema import get_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
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
