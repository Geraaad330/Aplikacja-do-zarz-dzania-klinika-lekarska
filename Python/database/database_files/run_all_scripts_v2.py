import subprocess
import os

def run_script(path_to_script):
    """
    Uruchamia pojedynczy plik Python (.py).
    
    :param path_to_script: Ścieżka do pliku Python.
    """
    try:
        print(f"Uruchamiam: {path_to_script}")
        subprocess.run(["python", path_to_script], check=True)
        print(f"Zakończono pomyślnie: {path_to_script}\n")
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas uruchamiania {path_to_script}: {e}\n")
    except FileNotFoundError as e:
        print(f"Plik {path_to_script} nie został znaleziony: {e}\n")
    except Exception as e: # pylint: disable=broad-exception-caught  # Jeśli musisz obsłużyć wszystkie inne błędy
        print(f"Nieoczekiwany błąd podczas uruchamiania {path_to_script}: {e}\n")


if __name__ == "__main__":
    # Lista plików do uruchomienia
    scripts = [
        "reset_database_v2.py",
        "load_patients.py",
        "load_employees.py",
        "load_roles.py",
        "load_services.py",
        "load_specialties.py",
        "load_meeting_types.py",
        "load_room_types.py",
        "load_form_types.py",
        "load_employee_specialties.py",
        "load_employee_services.py",
        "load_users.py",
        "load_assigned_patients.py",
        "load_rooms.py",
        "load_room_reservations.py",
        "load_appointments_v3.py",
        "load_diagnoses.py",
        "load_prescriptions.py",
        "load_internal_meetings_v2.py",
        "load_meeting_participants.py",
    ]

    # Ścieżka główna do skryptów
    base_path = r"C:\gry-programy\Qt\Qt_projekty\Projekt_inz\Python\database\database_files"  # Zmień na odpowiednią ścieżkę

    for script in scripts:
        script_path = os.path.join(base_path, script)
        run_script(script_path)


