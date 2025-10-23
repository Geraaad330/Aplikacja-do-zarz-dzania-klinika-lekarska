import bcrypt
from datetime import datetime
from models.users_accounts import UsersAccounts


class LoginController:
    """
    Kontroler odpowiedzialny za uwierzytelnianie użytkowników.
    """

    def __init__(self, db_controller):
        self.db_controller = db_controller

    def authenticate_user(self, username, password):
        """
        Uwierzytelnia użytkownika na podstawie username i hasła.
        Pobiera dane użytkownika, jego rolę i uprawnienia.

        Args:
            username (str): Nazwa użytkownika.
            password (str): Hasło użytkownika.

        Returns:
            dict: Dane użytkownika z rolą i uprawnieniami.
        """
        # Pobierz użytkownika na podstawie username
        query = """
        SELECT u.user_id, u.username, u.password_hash, u.role_id, r.role_name
        FROM users_accounts u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.username = ?
        """
        cursor = self.db_controller.connection.execute(query, (username,))
        user = cursor.fetchone()

        if user:
            user_id, username, password_hash, role_id, role_name = user
            # Weryfikacja hasła

            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):

                # Aktualizuj czas logowania
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                users_accounts_controller = UsersAccounts(self.db_controller)
                users_accounts_controller.update_last_login(user_id, current_time)

                # Pobierz uprawnienia użytkownika
                permissions = self._get_permissions(role_id)
                return {
                    "user_id": user_id,
                    "username": username,
                    "role_id": role_id,
                    "role_name": role_name,
                    "permissions": permissions,
                }
        return None





    def _get_permissions(self, role_id):
        """
        Pobiera listę uprawnień przypisanych do roli.

        Args:
            role_id (int): ID roli użytkownika.

        Returns:
            list: Lista uprawnień.
        """
        query = """
        SELECT sp.permission_name
        FROM role_permissions rp
        JOIN system_permissions sp ON rp.permission_id = sp.permission_id
        WHERE rp.role_id = ?
        """
        cursor = self.db_controller.connection.execute(query, (role_id,))
        permissions = [row[0] for row in cursor.fetchall()]
        return permissions
