from models.roles import Roles
from controllers.database_controller import DatabaseController

def load_roles_from_file(file_to_load):
    """
    Wczytuje role z pliku tekstowego.

    :param file_to_load: Ścieżka do pliku tekstowego z rolami.
    :return: Lista nazw ról.
    """
    loaded_roles = []  # Unikamy konfliktu z nazwą zmiennej globalnej
    with open(file_to_load, 'r', encoding='utf-8') as file:
        for line in file:
            role_name = line.strip()
            if role_name:  # Pomijamy puste linie
                loaded_roles.append(role_name)
    return loaded_roles


def add_roles_to_database(roles_to_add, database_controller):
    """
    Dodaje listę ról do bazy danych za pomocą klasy Roles.

    :param roles_to_add: Lista nazw ról.
    :param database_controller: Obiekt kontrolera bazy danych.
    """
    roles_model = Roles(database_controller)
    roles_model.create_table()  # Tworzy tabelę, jeśli nie istnieje

    for role_name in roles_to_add:
        try:
            roles_model.create_new_record(role_name)
            print(f"Rola '{role_name}' została dodana do bazy danych.")
        except ValueError as e:
            print(f"Błąd: {e} dla roli: {role_name}")
        except RuntimeError as e:
            print(f"Błąd: {e} dla roli: {role_name}")


if __name__ == "__main__":
    # Ścieżki do plików
    file_path = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\roles_list.txt"  # Podmień na właściwą ścieżkę, jeśli plik znajduje się w innej lokalizacji

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()  # Konstruktor bez argumentów
    db_controller.connect_to_database()  # Połączenie z bazą danych

    # Wczytanie danych z pliku i dodanie do bazy danych
    roles_list = load_roles_from_file(file_path)
    add_roles_to_database(roles_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
