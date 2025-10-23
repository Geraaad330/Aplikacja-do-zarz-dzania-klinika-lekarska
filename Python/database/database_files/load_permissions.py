import sqlite3
from models.permissions import Permissions
from controllers.database_controller import DatabaseController

def load_permissions_from_file(file_to_load):
    """
    Wczytuje uprawnienia z pliku tekstowego.

    :param file_to_load: Ścieżka do pliku tekstowego z uprawnieniami.
    :return: Lista uprawnień do dodania.
    """
    loaded_permissions = []  # Zmieniono nazwę zmiennej, aby uniknąć konfliktu nazw
    with open(file_to_load, 'r', encoding='utf-8') as file:
        for line in file:
            permission_name = line.strip()
            if permission_name:  # Pomijamy puste linie
                loaded_permissions.append(permission_name)
    return loaded_permissions


def add_permissions_to_database(permissions_to_add, database_controller):
    """
    Dodaje listę uprawnień do bazy danych za pomocą klasy Permissions.

    :param permissions_to_add: Lista nazw uprawnień.
    :param database_controller: Obiekt kontrolera bazy danych.
    """
    permissions_model = Permissions(database_controller)
    permissions_model.create_table()  # Tworzy tabelę, jeśli nie istnieje

    for permission_name in permissions_to_add:
        try:
            permissions_model.add_permission(permission_name)
            print(f"Uprawnienie '{permission_name}' zostało dodane do bazy danych.")
        except ValueError as e:
            print(f"Błąd: {e}")
        except RuntimeError as e:
            print(f"Błąd: {e}")


def reset_permissions_table(database_controller):
    """
    Resetuje tabelę system_permissions, aby ID zaczynało się od 1.

    :param database_controller: Obiekt kontrolera bazy danych.
    """
    try:
        connection = database_controller.connection
        # Usuń wszystkie rekordy
        connection.execute("DELETE FROM system_permissions")
        # Zresetuj sekwencję AUTOINCREMENT
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'system_permissions'")
        connection.commit()
        print("Tabela system_permissions została zresetowana.")
    except sqlite3.Error as e:
        print(f"Błąd podczas resetowania tabeli: {e}")


if __name__ == "__main__":
    # Ścieżki do plików
    file_path = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\permission_list.txt"  # Podmień na właściwą ścieżkę, jeśli plik znajduje się w innej lokalizacji

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()  # Konstruktor bez argumentów
    db_controller.connect_to_database()  # Połączenie z bazą danych

    # Resetowanie tabeli przed dodaniem nowych rekordów
    reset_permissions_table(db_controller)

    # Wczytanie danych z pliku i dodanie do bazy danych
    permissions_list = load_permissions_from_file(file_path)
    add_permissions_to_database(permissions_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()


