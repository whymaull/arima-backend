from flask import Flask
from flask_cors import CORS # type: ignore
from flasgger import Swagger
from models.schema import init_db, import_symbols
from routes.kode_saham import symbol_bp # type: ignore
from routes.prediksi import predict_bp # type: ignore
from routes.auth import auth_bp 
from routes.riwayat import riwayat_bp 

app = Flask(__name__)
CORS(app)

swagger = Swagger(app)

app.register_blueprint(symbol_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(riwayat_bp)

init_db()
import_symbols()

@app.route("/")
def index():
    return "<h1>API Prediksi Saham - Buka /apidocs untuk dokumentasi Swagger</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
