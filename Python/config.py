# config.py

# "production" -> baza danych db_projekt_inz.db
# "test" ":memory:" -> testowa baza danych tworzona podczas testu

import os

class Config:
    @staticmethod
    def get_database_path():
        """
        Zwraca odpowiednią ścieżkę bazy danych w zależności od środowiska.
        """
        env = os.getenv("APP_ENV", "production")  # Domyślnie środowisko produkcyjne
        print("-------------------------------------------------------------")
        print(f"|UŻYWANE ŚRODOWISKO|: {env}")  # Informacja o aktualnym środowisku
        if env == "test":
            return ":memory:"  # Testowa baza danych w pamięci
        else:
            # Ścieżka do produkcyjnej bazy danych
            base_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(base_dir, "database", "db_projekt_inz.db")
        
    @staticmethod
    def get_environment_info():
        """Zwraca komunikat o aktualnym środowisku i bazie danych."""
        env = os.getenv("APP_ENV", "production")
        db_path = Config.get_database_path()
        print("-------------------------------------------------------------")
        return f"|ŚRODOWISKO|: {env} |UŻYWANA BAZA DANYCH|: {db_path}"   
    


