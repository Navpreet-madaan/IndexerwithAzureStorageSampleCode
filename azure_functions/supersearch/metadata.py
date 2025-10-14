"""
Document metadata handling
"""

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

from common import KeyVault
from common.handlers import KeyVaultHandler
from common.sql import SqlConnector
from supersearch.document import Document

# declarative base class
Base = declarative_base()


class DocumentManager:
    """Document manager class for handling document metadata"""

    def __init__(
        self,
    ):
        _key_vault_handler = KeyVaultHandler()
        _sql_server = _key_vault_handler.get_secret(
            secret_name=KeyVault.sql_server_name_secret
        )
        _sql_database = _key_vault_handler.get_secret(
            secret_name=KeyVault.sql_db_name_secret
        )

        _sql_connector = SqlConnector(
            sql_server=_sql_server,
            sql_database=_sql_database,
        )
        self._sql_connector = _sql_connector

    def get(
        self,
        doc_id,
    ):
        """
        Get a document by its id
        """
        session = self._sql_connector.get_session()
        try:
            result = (
                session.query(
                    Document,
                )
                .filter_by(
                    id=doc_id,
                )
                .first()
            )
            return result
        finally:
            session.close()

    def list(
        self,
    ):
        """
        Get a list of all documents
        """
        session = self._sql_connector.get_session()
        try:
            result = session.query(
                Document,
            ).all()
            return result
        finally:
            session.close()

    def save(
        self,
        document,
    ):
        """
        Create or Update a document
        """
        _document: Document = document
        session = self._sql_connector.get_session()
        try:

            if not self.get(
                doc_id=_document.id,
            ):
                _document.updated_at = datetime.utcnow()
                _document.created_at = datetime.utcnow()
                session.add(_document)
            else:
                session.query(
                    Document,
                ).filter(
                    Document.id == _document.id,
                ).update(
                    {
                        "name": _document.name,
                        "version": _document.version,
                        "checksum": _document.checksum,
                        "last_modified": _document.last_modified,
                        "status": _document.status,
                        "updated_at": datetime.utcnow(),
                    },
                    synchronize_session=False,
                )
            session.commit()
        finally:
            session.flush()
            session.close()

    def retire(
        self,
        document,
    ):
        """
        Create or Update a document
        """
        _document: Document = document
        session = self._sql_connector.get_session()
        try:

            if self.get(
                doc_id=_document.id,
            ):
                session.query(
                    Document,
                ).filter(
                    Document.id == _document.id,
                ).update(
                    {
                        "status": _document.status,
                        "updated_at": datetime.utcnow(),
                    },
                    synchronize_session=False,
                )
                session.commit()
        finally:
            session.flush()
            session.close()

    def delete(
        self,
        document,
    ):
        """
        Delete a document
        """
        _document: Document = document
        session = self._sql_connector.get_session()
        try:
            session.query(
                Document,
            ).filter(
                Document.id == _document.id,
            ).delete(
                synchronize_session="fetch",
            )
            session.commit()
        finally:
            session.close()
