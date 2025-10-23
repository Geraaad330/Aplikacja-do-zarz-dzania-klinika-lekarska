# test_database_add.py

"""
Testowanie powinno odbywać się w środowisku testowym. Wskazuje na to fakt, że baza danych 
testowa używa konfiguracji :memory:, co jest typowe dla testów jednostkowych, 
aby uniknąć wpływu na produkcyjne dane.
W testach należy unikać korzystania z oryginalnej bazy danych produkcyjnej.
Testy powinny być izolowane od środowiska produkcyjnego i nie powinny operować 
na rzeczywistych danych. Bazę danych testową można przygotować dynamicznie, np. 
w pamięci lub jako oddzielny plik tymczasowy.
"""


import sqlite3
import pytest
from config import Config  # Poprawiony import

@pytest.fixture
def database_connection():
    """
    Tworzy połączenie z bazą danych na potrzeby testów i zamyka je po zakończeniu.
    """
    connection = sqlite3.connect(Config.get_database_path())
    yield connection
    connection.close()

@pytest.fixture(autouse=True)
def setup_database(database_connection):
    """
    Tworzy tabelę testową w bazie danych.
    """
    cursor = database_connection.cursor()
    # Tworzy przykładową tabelę
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    """)
    database_connection.commit()

def test_list_tables(database_connection):
    """
    Testuje połączenie z bazą danych i weryfikuje, czy tabela istnieje.
    """
    cursor = database_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Nazwy tabel w bazie danych:", [table[0] for table in tables])
    assert len(tables) > 0, "Brak tabel w bazie danych."