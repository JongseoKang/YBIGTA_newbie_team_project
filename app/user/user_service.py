from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        """
        Process user login

        Args:
            user_login (UserLogin): login request data

        Returns:
            User: user object succeeding to login

        Raises:
            ValueError: If an email is not in database or password is wrong
        """
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User not found.")  # 400 Bad Request
        if user.password != user_login.password:
            raise ValueError("Invalid ID/PW")  # 400 Bad Request
        return user

    def register_user(self, new_user: User) -> User:
        """
        Register new user

        Args:
            new_user (User): user data to be registerred

        Returns:
            User: registerred user object

        Raises:
            ValueError: If email already exist in database
        """
        existing_user = self.repo.get_user_by_email(new_user.email)
        if existing_user:
            raise ValueError("User already Exists.")  # 400 Bad Request
        new_user = self.repo.save_user(new_user)
        return new_user

    def delete_user(self, email: str) -> User:
        """
        Delete user

        Args:
            email (str): user email to be deleted

        Returns:
            User: deleted user object

        Raises:
            ValueError: If user not found
        """
        user_to_delete = self.repo.get_user_by_email(email)
        if not user_to_delete:
            raise ValueError("User not Found.")  # 404 Not Found
        deleted_user = self.repo.delete_user(user_to_delete)
        return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        """
        Update user password

        Args:
            user_update (UserUpdate): user whose password is to be updated

        Returns:
            User: user whose password is updated

        Raises:
            ValueError: If user not found
        """
        user = self.repo.get_user_by_email(user_update.email)
        if not user:
            raise ValueError("User not Found.")  # 404 Not Found
        user.password = user_update.new_password
        updated_user = self.repo.save_user(user)  # 새 비밀번호 저장
        return updated_user