from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.dal.database import Database, User, Claim, Role, UserClaim
import typing
from datetime import datetime


""" CLASSE SERVIÇO, RESPONSÁVEL POR REALIZAR AS INTERAÇÕES COM O BANCO DE DADOS """
class BackendService:
    def __init__(self):
        self.db = Database().get_session()

    
    """FUNÇÃO PARA CRIAR O REGISTRO DOS PAPEIS NA TABELA ROLES"""
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
            return { "error": str(e) }
        
    """FUNÇÃO PARA CRIAR O REGISTRO DOS USUÁRIOS NA TABELA USERS"""
    def register_user(self, user: any):
        try:
            create_user = User(
                name=user["name"],
                email=user["email"],
                password=user["password"] or  "default_password",  # se possível, utilizar algum token para senha
                role_id=user["role_id"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.db.add(create_user)
            self.db.commit()
            self.db.refresh(create_user)
            
            return create_user
        
        except Exception as e:
            self.db.rollback()
            return { "error": str(e) }
        
    """GET QUERY_SQL NAS TABELAS USERS, ROLES, CLAIMS E USER_CLAIMS"""
    def get_users_with_roles_and_claims(self):
        try:
            query = (
                self.db.query(
                    User.name.label("name"),
                    User.email.label("email"),
                    Role.description.label("role"),
                    func.group_concat(Claim.description, ', ').label("permissions")
                )
                .outerjoin(Role, User.role_id == Role.id)
                .outerjoin(UserClaim, User.id == UserClaim.user_id)
                .outerjoin(Claim, UserClaim.claim_id == Claim.id)
                .group_by(User.id)
                .order_by(User.name)
            )

            return query.all()
        except Exception as e:
            return { "error": str(e) }
    
    """GET PARA LISTAR O USUÁRIO POR ID"""
    def get_role_by_role_id(self, role_id: int):
        """ Consulta um papel (Role) pelo ID e retorna suas informações."""
        if role_id > 0:
            user_consult = self.db.query(User).filter(User.role_id == role_id).first()
            if not user_consult:
                raise HTTPException(status_code=404, detail="Usuário não encontrado para este papel.")
                
            role_consult = self.db.query(Role).filter(Role.id == user_consult.role_id).first()
            if not role_consult:
                raise HTTPException(status_code=404, detail="Papel não encontrado para este usuário.")
            return {
                "user_id": user_consult.id,
                "user_name": user_consult.name,
                "user_email": user_consult.email,
                "role_id": role_consult.id,
                "role_description": role_consult.description,
                "created_at": user_consult.created_at,
                "updated_at": user_consult.updated_at,
            } # Se não encontrou o usuário ou o papel, retorna None
            


    # def register_role_maybe_user(self, user: dict, role_id: int = None):
    #     if role_id:
    #         # Já tem role_id, cria só usuário
    #         created_user = self.register_user(user=user, role_id=role_id)
    #         return None, created_user
    #     else:
    #         # Cria role e usuário juntos
    #         try:
    #             create_role = Role(description=user["description"])
    #             self.db.add(create_role)
    #             self.db.commit()
    #             self.db.refresh(create_role)
    #         except Exception as e:
    #             self.db.rollback()
    #             return { "error": str(e) }

    #         try:
    #             created_user = self.register_user(user=user, role_id=create_role.id)
    #             return create_role, created_user
    #         except Exception as e:
    #             self.db.rollback()
    #             return { "error": str(e) }