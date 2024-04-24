#!/usr/bin/env python3
"""
Module - Auth module
"""
from uuid import uuid4
import bcrypt
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound

def _hash_password(password: str) -> bytes:
    """
    Generates password hash
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def _generate_uuid()-> str:
    """
    generates a uuid str
    """
    return str(uuid4())
    


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()
    
    def register_user(self, email: str, password: str) -> User:
        """
        registers the user to the db
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            hashedpwd = _hash_password(password)
            return self._db.add_user(email, hashedpwd)
    
    def valid_login(self, email: str, password: str)-> bool:
        """
        determines if user is valid
        """
        try:
            return bcrypt.checkpw(password.encode("utf-8"),
                                  self._db.find_user_by(email=email).hashed_password)
        except NoResultFound:
            return False
    
    def create_session(self, email: str) -> str:
        """
        creates a session
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except NoResultFound:
            return None
    
    def get_user_from_session_id(self, session_id: str) -> User|None:
        """
        gets user from session_id
        """
        if session_id:
            try:
                return self._db.find_user_by(session_id=session_id)
            except NoResultFound:
                return None
        return None
    
    def destroy_session(self, user_id: str)-> None:
        """
        destroys a users session
        """
        self._db.update_user(user_id, session_id=None)
    
    def get_reset_password_token(self, email: str) -> str:
        """
        generates reset password token
        """
        try:
            user = self._db.find_user_by(email=email)
            reset_token = _generate_uuid()
            self._db.update_user(user.id, reset_token=reset_token)
            return reset_token
        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str, password: str)-> None:
        """
        updates the user's password
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed_pwd = _hash_password(password)
            self._db.update_user(user.id, hashed_password=hashed_pwd, reset_token=None)
        except NoResultFound:
            raise ValueError
