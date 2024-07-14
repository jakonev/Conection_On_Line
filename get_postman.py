from flask import Flask, request, jsonify
import requests
import pandas as pd
import sqlite3

app = Flask(__name__)


class Loader:
    def __init__(self, url, headers, params):
        self.url = url
        self.headers = headers
        self.params = params
        self.data = None

    def fetch_data(self):
        response = requests.get(self.url, headers=self.headers, params=self.params)
        if response.status_code == 200:
            self.data = response.json()
        else:
            response.raise_for_status()


class DataProcessor:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotacao (
                _id TEXT,
                CODNEG TEXT,
                PRE_ABE REAL,
                PRE_ULT REAL,
                PRE_OFV REAL,
                PREMED REAL,
                VOLT_TOT REAL,
                DATA_PREGAO TEXT
            )
        ''')

    def insert_data(self, df):
        df.to_sql('cotacao', self.conn, if_exists='replace', index=False)

    def filter_data(self, codneg):
        query = f"SELECT * FROM cotacao WHERE CODNEG = '{codneg}'"
        filtered_data = pd.read_sql_query(query, self.conn)
        return filtered_data

    def close_connection(self):
        self.conn.close()


@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    codneg_filtrado = request.args.get('codneg')

    if not codneg_filtrado:
        return jsonify({"error": "codneg is required"}), 400

    # Parâmetros da API
    url = "https://cotahist-2f8e.restdb.io/rest/cota-hist"
    headers = {
        'content-type': "application/json",
        'x-apikey': "a78a2fe211a7547f5fc7f323bf8ed3a99651a",
        'cache-control': "no-cache"
    }
    params = {'_id': '', 'CODNEG': '', 'PRE-ABE': '', 'PRE-ULT': '', 'PRE-OFV': '', 'PREMED': '', 'VOLT-TOT': '',
              'DATA_PREGAO': ''}

    # Carregar dados
    data_loader = Loader(url, headers, params)
    data_loader.fetch_data()
    df = pd.DataFrame(data_loader.data)
    db_name = 'cotacao.db'
    data_processor = DataProcessor(db_name)
    data_processor.insert_data(df)
    filtered_data = data_processor.filter_data(codneg_filtrado)
    data_processor.close_connection()

    return filtered_data.to_json(orient='records')


if __name__ == "__main__":
    app.run(debug=True)
