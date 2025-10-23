import sqlite3
from models.role_permissions import RolePermissions
from controllers.database_controller import DatabaseController


def load_role_permissions_from_file(file_to_load):
    """
    Wczytuje role i ich uprawnienia z pliku tekstowego.

    :param file_to_load: Ścieżka do pliku tekstowego z rolami i uprawnieniami.
    :return: Lista krotek (role_id, permission_ids).
    """
    loaded_role_permissions = []
    with open(file_to_load, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):  # Wiersze numerowane od 1
            line = line.strip()
            if not line:  # Pomijamy puste linie
                continue

            # Rozdzielamy wiersz na `role_id` i `permission_ids`
            columns = line.split(',', 1)  # Pierwszy przecinek rozdziela role_id i resztę
            if len(columns) < 2:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - niepoprawny format danych.")
                continue

            try:
                role_id = int(columns[0].strip())  # Pierwsza wartość to role_id
                permission_ids = [int(p.strip()) for p in columns[1].split(',') if p.strip().isdigit()]
                loaded_role_permissions.append((role_id, permission_ids))
            except ValueError as e:
                print(f"Ostrzeżenie: Pomijam wiersz {line_number} - niepoprawne wartości ({e}).")
    return loaded_role_permissions


def reset_role_permissions_table(database_controller):
    """
    Resetuje tabelę role_permissions, aby ID zaczynało się od 1.

    :param database_controller: Obiekt kontrolera bazy danych.
    """
    try:
        connection = database_controller.connection
        # Usuń wszystkie rekordy
        connection.execute("DELETE FROM role_permissions")
        # Zresetuj sekwencję AUTOINCREMENT
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'role_permissions'")
        connection.commit()
        print("Tabela role_permissions została zresetowana.")
    except sqlite3.Error as e:
        print(f"Błąd podczas resetowania tabeli: {e}")

def add_role_permissions_to_database(role_permissions_to_add, database_controller):
    """
    Dodaje role i ich uprawnienia do bazy danych za pomocą klasy RolePermissions.

    :param role_permissions_to_add: Lista krotek (role_id, permission_ids).
    :param database_controller: Obiekt kontrolera bazy danych.
    """
    role_permissions_model = RolePermissions(database_controller)
    role_permissions_model.create_table()  # Tworzy tabelę, jeśli nie istnieje

    for role_id, permission_ids in role_permissions_to_add:
        for permission_id in permission_ids:
            try:
                role_permissions_model.add_role_permission_by_ids(role_id, permission_id)
                print(f"Dodano uprawnienie {permission_id} do roli {role_id}.")
            except ValueError as e:
                print(f"Błąd: {e} (rola: {role_id}, uprawnienie: {permission_id})")
            except RuntimeError as e:
                print(f"Błąd: {e} (rola: {role_id}, uprawnienie: {permission_id})")


if __name__ == "__main__":
    # Ścieżka do pliku z listą ról i uprawnień
    file_path = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files\lists_files\role_permissions_list.txt"  # Podmień na właściwą ścieżkę, jeśli plik znajduje się w innej lokalizacji

    # Inicjalizacja kontrolera bazy danych
    db_controller = DatabaseController()  # Konstruktor bez argumentów
    db_controller.connect_to_database()  # Połączenie z bazą danych

    # Resetowanie tabeli przed dodaniem nowych rekordów
    reset_role_permissions_table(db_controller)

    # Wczytanie danych z pliku i dodanie do bazy danych
    role_permissions_list = load_role_permissions_from_file(file_path)
    add_role_permissions_to_database(role_permissions_list, db_controller)

    # Zamknięcie połączenia z bazą danych
    db_controller.connection.close()
