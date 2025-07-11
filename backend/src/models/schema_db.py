# from sqlalchemy import Column, Integer, String, Boolean, Date, BigInteger, ForeignKey, UniqueConstraint
# from sqlalchemy.orm import relationship, declarative_base
# from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, BigInteger, ForeignKey, UniqueConstraint
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship, sessionmaker
# from datetime import date
# from dotenv import load_dotenv
# import os

# load_dotenv()
# DATABASE_URL = os.getenv("DB_TEST_URL")

# # Configuração do engine
# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False}
# )


# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# class Role(Base):
#     __tablename__ = 'roles'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     description = Column(String, nullable=False)
#     users = relationship("User", back_populates="role")

# class User(Base):
#     __tablename__ = 'users'
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     name = Column(String, nullable=False)
#     email = Column(String, nullable=False)
#     password = Column(String, nullable=False)
#     role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
#     created_at = Column(Date, nullable=False)
#     updated_at = Column(Date, nullable=True)

#     role = relationship("Role", back_populates="users")
#     claims = relationship("Claim", secondary="user_claims", back_populates="users")

# class Claim(Base):
#     __tablename__ = 'claims'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     description = Column(String, nullable=False)
#     active = Column(Boolean, nullable=False, default=True)

#     users = relationship("User", secondary="user_claims", back_populates="claims")

# class UserClaim(Base):
#     __tablename__ = 'user_claims'
#     user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
#     claim_id = Column(BigInteger, ForeignKey('claims.id'), primary_key=True)
#     __table_args__ = (UniqueConstraint('user_id', 'claim_id', name='user_claims_un'),)

# class Database:
#     def __init__(self, database_url="sqlite:///homolog.test.db"):
#         self.engine = create_engine(database_url, echo=True)
#         Base.metadata.create_all(self.engine)
#         self.SessionLocal = sessionmaker(bind=self.engine)
    
#     def get_session(self):
#         return self.SessionLocal()