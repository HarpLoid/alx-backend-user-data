#!/usr/bin/env python3
"""
Module - session_auth
"""
from typing import TypeVar
from api.v1.auth.auth import Auth
from models.user import User
from uuid import uuid4


class SessionAuth(Auth):
    """
    SessionAuth class
    """
    user_id_by_session_id = {}
    
    def create_session(self, user_id: str = None)-> str:
        """
        Creates a session
        """
        if user_id is None or not isinstance(user_id, str):
            return None
        
        session_id = str(uuid4())
        self.user_id_by_session_id[session_id] = user_id
        return session_id
    
    def user_id_for_session_id(self, session_id: str = None) -> str:
        """
        Return User ID based on Session ID
        """
        if session_id and isinstance(session_id, str):
            return self.user_id_by_session_id.get(session_id)  

        return None
    
    def current_user(self, request=None):
        """
        retuns User instance based on cookie value
        """
        session_id = self.session_cookie(request)
        user_id = self.user_id_for_session_id(session_id)
        
        return User.get(user_id)
