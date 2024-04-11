#!/usr/bin/env python3
"""
Module - encrypt_password
"""
from bcrypt import hashpw, gensalt, checkpw


def hash_password(password: str) -> bytes:
    """
    Generates password hash
    """
    return hashpw(password.encode("utf-8"),
                  gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    check if password id valid
    """
    return checkpw(password.encode("utf-8"), hashed_password)
