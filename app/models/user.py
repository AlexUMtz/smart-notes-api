from sqlalchemy import Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(30), nullable=False)
    create_at: Mapped[datetime]  = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    notes = relationship("Note", back_populates="owner")