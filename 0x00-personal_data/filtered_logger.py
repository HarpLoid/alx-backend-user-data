#!/usr/bin/env python3
"""
Module - filtered_logger
"""
from typing import List
import re
import logging
import os
import mysql.connector


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        org = super().format(record)
        return filter_datum(self.fields, self.REDACTION,
                            org, self.SEPARATOR)

def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """
    Returns the log massage obfuscated

    Args:
        fields (List[str]): a list of strings representing
            all fields to obfuscate
        redaction (str): a string representing
            by what the field will be obfuscated
        message (str): a string representing the log line
        separator (str): a string representing
            by which character is separating all
            fields in the log line (message)

    Returns:
        str: log message obfuscated
    """
    for field in fields:
        pattern = f"{field}=[^{separator}]*"
        message = re.sub(pattern, f"{field}={redaction}", message)
    return message


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def get_logger()->logging.Logger:
    """
    gets the logger
    """
    log = logging.getLogger("user_data")
    log.setLevel(logging.INFO)
    log.propagate = False
    sh = logging.StreamHandler()
    sh.setFormatter(RedactingFormatter(PII_FIELDS))
    log.addHandler(sh)
    return log


def get_db()->mysql.connector.connection.MySQLConnection:
    """
    returns MySQLConnection object
    """
    username = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    password = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.getenv("PERSONAL_DATA_DB_NAME")
    
    return mysql.connector.connect(
        user=username, password=password,
        host=host, database=db_name
    )


def main():
    """
    Entry point
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    log = get_logger()
    for row in cursor:
        data = []
        for desc, value in zip(cursor.description, row):
            pair = f"{desc[0]}={str(value)}"
            data.append(pair)
        row_str = "; ".join(data)
        log.info(row_str)
    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
