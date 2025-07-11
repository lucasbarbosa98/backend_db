from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.dal.database import Database, User, Claim, Role, UserClaim
import typing
from datetime import datetime

class BackendService:
    def __init__(self):
        self.db = Database().get_session()

    
    def register_role_maybe_user(self, user: dict, role_id: int = None):
        if role_id:
            # Já tem role_id, cria só usuário
            created_user = self.register_user(user=user, role_id=role_id)
            return None, created_user
        else:
            # Cria role e usuário juntos
            try:
                create_role = Role(description=user["description"])
                self.db.add(create_role)
                self.db.commit()
                self.db.refresh(create_role)
            except Exception as e:
                self.db.rollback()
                raise HTTPException(status_code=500, detail=str(e))

            try:
                created_user = self.register_user(user=user, role_id=create_role.id)
                return create_role, created_user
            except Exception as e:
                self.db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
        
    def register_role(self, user:any):
        try:
            created_role = Role(
                description=user["description"],
            )
            self.db.add(created_role)
            self.db.commit()
            self.db.refresh(created_role)
            
            return created_role
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        
    def register_user(self, user: any, role_id: int = None):
        if not role_id:
            raise HTTPException(status_code=400, detail="Role ID is required to create a user.")
        try:
            create_user = User(
                name=user["name"],
                email=user["email"],
                password=user["password"] | "default_password",  # Use a default password if not provided
                role_id=role_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(create_user)
            self.db.commit()
            self.db.refresh(create_user)
            
            return create_user
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        
    def get_users_with_roles_and_claims(self):
        query = (
            self.db.query(
                User.name.label("nome"),
                User.email.label("email"),
                Role.description.label("papel"),
                func.group_concat(Claim.description, ', ').label("permissoes")
            )
            .outerjoin(Role, User.role_id == Role.id)
            .outerjoin(UserClaim, User.id == UserClaim.user_id)
            .outerjoin(Claim, UserClaim.claim_id == Claim.id)
            .group_by(User.id)
            .order_by(User.name)
        )

        return query.all()
    
    def get_role_by_role_id(self, role_id: int):
        """
        Consulta um papel (Role) pelo ID e retorna suas informações.

        Args:
            role_id (int): O ID do papel a ser consultado.

        Returns:
            Optional[Dict]: Dicionário com informações do papel e usuário,
                            ou None se não encontrado.
        """
        user_consult = self.db.query(User).filter(User.role_id == role_id).first()
        if user_consult:
            role_consult = self.db.query(Role).filter(Role.id == user_consult.role_id).first()
            if role_consult:
                return {
                    "user_id": user_consult.id,
                    "user_name": user_consult.name,
                    "user_email": user_consult.email,
                    "role_id": role_consult.id,
                    "role_description": role_consult.description,
                    "created_at": user_consult.created_at,
                    "updated_at": user_consult.updated_at,
                }
        # Se não encontrou o usuário ou o papel, retorna None
        return None

        
    # Uncomment this method if you want to use it    

    # def get_user_role_by_id(self, user_id: int) -> typing.Optional[typing.Dict]:
    #     """
    #     Consulta um usuário pelo ID e retorna suas informações junto com o papel (Role).

    #     Args:
    #         user_id (int): O ID do usuário a ser consultado.

    #     Returns:
    #         Optional[Dict]: Um dicionário contendo o ID do usuário, email,
    #                         ID do papel e descrição do papel, ou None se o usuário não for encontrado.
    #     """
    #     # Realiza a consulta ao banco de dados para buscar o usuário pelo ID
    #     # e carrega a relação 'role' para evitar consultas N+1.
    #     user = self.db.query(User).filter(User.id == user_id).first()

    #     if not user:
    #         return None # Retorna None se o usuário não for encontrado

    #     # Retorna os dados formatados conforme o exemplo original
    #     return {
    #         "user_id": user.id,
    #         "user_email": user.email, # Usando email como identificador do usuário
    #         "role_id": user.role.id,
    #         "role_description": user.role.description
    #     }