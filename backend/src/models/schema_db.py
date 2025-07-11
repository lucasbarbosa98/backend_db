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