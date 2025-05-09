import pandas as pd
from database.koneksi import get_connection 

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS prediksi_saham")
    conn.database = "prediksi_saham"

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daftar_saham (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS riwayat_prediksi (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL,
            symbol VARCHAR(10) NOT NULL,
            periods INT NOT NULL,
            forecast TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )

    conn.commit()
    cursor.close()
    conn.close()

def import_symbols():
    conn = get_connection()
    conn.database = "prediksi_saham"
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM daftar_saham")
    if cursor.fetchone()[0] > 0:
        return

    df = pd.read_csv("daftar_saham_indonesia.csv")
    for _, row in df.iterrows():
        symbol = row['symbol'].strip() + ".JK"
        name = row['name'].strip()
        cursor.execute("INSERT IGNORE INTO daftar_saham (symbol, name) VALUES (%s, %s)", (symbol, name))

    conn.commit()
    cursor.close()
    conn.close()
