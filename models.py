# models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from db import Base

class ApprovalSheet(Base):
    __tablename__ = "approval_sheets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    date = Column(Date, default=date.today)
    download_link = Column(String(500), nullable=False)

    authors = relationship("Author", back_populates="sheet", cascade="all, delete-orphan")

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sheet_id = Column(Integer, ForeignKey("approval_sheets.id"))

    sheet = relationship("ApprovalSheet", back_populates="authors")
