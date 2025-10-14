"SQL PY class for SQL operations"
import struct
import urllib
import pyodbc

from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SqlConnector:
    "SQL Connector class for SQL operations"

    def __init__(
        self,
        sql_server,
        sql_database,
    ):
        _connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};SERVER="
            + sql_server
            + ".database.windows.net;DATABASE="
            + sql_database
        )
        self.connection_string = _connection_string

    def _get_access_token(self):
        _scope = "https://database.windows.net/.default"
        _credential = DefaultAzureCredential()
        _access_token = _credential.get_token(_scope)
        return _access_token

    def _get_token_struct(self):
        _access_token = self._get_access_token()
        _tokenb = bytes(_access_token.token, "UTF-8")
        _exptoken = b""
        for i in _tokenb:
            _exptoken += bytes({i})
            _exptoken += bytes(1)
        _tokenstruct = struct.pack("=i", len(_exptoken)) + _exptoken
        return _tokenstruct

    def get_sql_connection(self):
        "getting SQL connection"
        _tokenstruct = self._get_token_struct()
        access_token = 1256
        _connection = pyodbc.connect(
            self.connection_string,
            attrs_before={access_token: _tokenstruct},
        )
        return _connection

    def get_engine(self):
        "getting SQL engine"
        tokenstruct = self._get_token_struct()
        params = urllib.parse.quote_plus(self.connection_string)
        access_token = 1256
        engine = create_engine(
            "mssql+pyodbc:///?odbc_connect=%s" % params,
            connect_args={
                "attrs_before": {access_token: tokenstruct},
                "timeout": 120,
            },
            pool_timeout=120,
            pool_pre_ping=True,
        )
        return engine

    def get_session(self):
        "getting SQL session"
        engine = self.get_engine()
        session_maker = sessionmaker(engine)
        session = session_maker()
        return session
