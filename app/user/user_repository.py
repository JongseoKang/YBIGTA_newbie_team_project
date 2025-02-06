import json

from typing import Dict, Optional

from app.user.user_schema import User
from app.config import USER_DATA

# class UserRepository:
#     def __init__(self) -> None:
#         self.users: Dict[str, dict] = self._load_users()

#     def _load_users(self) -> Dict[str, Dict]:
#         try:
#             with open(USER_DATA, "r") as f:
#                 return json.load(f)
#         except FileNotFoundError:
#             raise ValueError("File not found")

#     def get_user_by_email(self, email: str) -> Optional[User]:
#         user = self.users.get(email)
#         return User(**user) if user else None

#     def save_user(self, user: User) -> User: 
#         self.users[user.email] = user.model_dump()
#         with open(USER_DATA, "w") as f:
#             json.dump(self.users, f)
#         return user

#     def delete_user(self, user: User) -> User:
#         del self.users[user.email]
#         with open(USER_DATA, "w") as f:
#             json.dump(self.users, f)
#         return user
    
# app/user/user_repository.py

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from app.user.user_schema import User

from app.database.mysql_connection import engine

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)

Base.metadata.create_all(bind=engine)

class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if db_user:
            return User.from_orm(db_user)
        return None

    def save_user(self, user: User) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.email == user.email).first()
        if db_user:
            db_user.name = user.name
        else:
            db_user = UserModel(email=user.email, name=user.name)
            self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User.from_orm(db_user)

    def delete_user(self, user: User) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.email == user.email).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
        return user