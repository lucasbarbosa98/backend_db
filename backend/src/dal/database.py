from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Carrega .env
load_dotenv()
DATABASE_URL = os.getenv("DB_TEST_URL")

# Base declarativa
Base = declarative_base()

# ======= MODELOS =======

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    users = relationship("User", back_populates="role")
 
 #Role[id] -> User[role_id]
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=True)

    role = relationship("Role", back_populates="users")
    claims = relationship("Claim", secondary="user_claims", back_populates="users")

class Claim(Base):
    __tablename__ = 'claims'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

    users = relationship("User", secondary="user_claims", back_populates="claims")

class UserClaim(Base):
    __tablename__ = 'user_claims'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    claim_id = Column(Integer, ForeignKey('claims.id'), primary_key=True)
    __table_args__ = (UniqueConstraint('user_id', 'claim_id', name='user_claims_un'),)

# ======= CLASSE DATABASE =======

class Database:
    def __init__(self, database_url=DATABASE_URL):
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=False  # Altere para True se quiser logar as queries
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Cria tabelas se ainda não existirem
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()
