from sqlalchemy import Column, Integer, String, Enum as SAEnum
from .database import Base
import enum

class Role(str, enum.Enum):
    Admin = "Admin"
    User = "User"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(Role), default=Role.User, nullable=False)
