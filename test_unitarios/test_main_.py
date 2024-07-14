import pytest
import pandas as pd
from conection_rest_sqlite import Loader, DataProcessor
import sqlite3
import json


@pytest.fixture
def sample_data():
    # Carregar um exemplo de dados JSON
    with open('data.json', 'r') as file:
        data = json.load(file)
    return pd.DataFrame(data)


@pytest.fixture
def sample_database(sample_data):
    conn = sqlite3.connect(':memory:')
    sample_data.to_sql('cotacao', conn, if_exists='replace', index=False)
    return conn


def test_filter_data(sample_data):
    data_processor = DataProcessor(sample_data)
    codneg_filtrado = 'CVCB3'

    data_processor.filter_data(codneg_filtrado)

    assert not data_processor.dados_filtrados.empty
    assert (data_processor.dados_filtrados['CODNEG'] == codneg_filtrado).all()


def test_database_integration(sample_database):
    conn = sample_database
    codneg_filtrado = 'BEEF3'
    query = f"SELECT * FROM cotacao WHERE CODNEG = '{codneg_filtrado}'"

    filtered_data = pd.read_sql_query(query, conn)

    assert not filtered_data.empty
    assert (filtered_data['CODNEG'] == codneg_filtrado).all()