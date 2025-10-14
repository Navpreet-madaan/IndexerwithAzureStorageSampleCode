"""
Document SQL table for super search
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# declarative base class
Base = declarative_base()


class Document(Base):
    """
    Represents a document.
    """

    __tablename__ = "SuperSearch"
    __table_args__ = {"schema": "knowledgebase"}

    id = Column(Integer, name="ID", primary_key=True, autoincrement=False)
    name = Column(String, name="Name")
    version = Column(String, name="Version")
    checksum = Column(Integer, name="CheckSum")
    last_modified = Column(DateTime, name="LastModified")
    status = Column(String, name="Status")
    updated_at = Column(DateTime, name="UpdatedAt")
    created_at = Column(DateTime, name="CreatedAt")
