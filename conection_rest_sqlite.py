import requests
import pandas as pd
import sqlite3
from datetime import datetime

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

class SqlBase:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = '''
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
        '''
        self.conn.cursor().execute(query)
        self.conn.commit()

    def insert_data(self, df):
        df.to_sql('cotacao', self.conn, if_exists='replace', index=False)

    def query_data(self, query):
        return pd.read_sql_query(query, self.conn)

    def close_connection(self):
        self.conn.close()

class DataProcessor(SqlBase):
    def __init__(self, db_name):
        super().__init__(db_name)

    def filter_data(self, codneg_filtrado):
        query = f"SELECT * FROM cotacao WHERE CODNEG = '{codneg_filtrado}'"
        return self.query_data(query)

def main():
    # Parâmetros da API
    url = "https://cotahist-2f8e.restdb.io/rest/cota-hist"
    headers = {
        'content-type': "application/json",
        'x-apikey': "a78a2fe211a7547f5fc7f323bf8ed3a99651a",
        'cache-control': "no-cache"
    }
    params = {'_id': '', 'CODNEG': '', 'PRE-ABE': '', 'PRE-ULT': '', 'PRE-OFV': '', 'PREMED': '', 'VOLT-TOT': '', 'DATA_PREGAO': ''}

    # Carregar dados
    data_loader = Loader(url, headers, params)
    data_loader.fetch_data()
    df = pd.DataFrame(data_loader.data)
    db_name = 'cotacao.db'
    data_processor = DataProcessor(db_name)
    data_processor.insert_data(df)
    codneg_filtrado = 'BEEF3'
    filtered_data = data_processor.filter_data(codneg_filtrado)
    print(filtered_data)

    data_processor.close_connection()

if __name__ == "__main__":
    main()


