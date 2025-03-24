from flask import Flask 
from pymongo import MongoClient

app = Flask(__name__)

# Configurar la conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["market-health"]

@app.route("/")
def home():
    return "Conectado a MongoDB en Flask"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context=('certs/certificate.crt', 'certs/private.key'))
