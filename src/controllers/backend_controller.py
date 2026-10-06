from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from src.services.backend_service import BackendService
import json

app = FastAPI()
service = BackendService()

class BackendController:
    
    def list_users_with_permissions(self):
        ##Responsável por realizar um GET com base na query passada
        try:
            result = service.get_users_with_roles_and_claims()
            return [
                {
                    "name": r.name,
                    "email": r.email,
                    "role": r.role,
                    "permissions": r.permissions
                }
                #Responsável por iterar sobre o resultado e extrair os dados necessários    -Refatorar para avaliar necessidade-
                for r in result
            ]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        
    def get_user_role_by_roleId(self, role_id: int):
        """Função responsável por buscar um usuário e seu papel pelo ID do papel."""
        user_role = service.get_role_by_role_id(role_id)
        
        if not user_role:
            raise HTTPException(status_code=404, detail="Usuário ou papel não encontrado")
        
        return {
            "id": user_role["user_id"],
            "name": user_role["user_name"],
            "email": user_role["user_email"],
            "role_id": user_role["role_id"],
            "user_roles": user_role["role_description"],
            "created_at": str(user_role["created_at"]),
            "updated_at": str(user_role["updated_at"]),
        }
    
    def create_user(self, user: str):
        """Função responsável por criar um usuário."""
        try:
            create_user = service.register_user(user)
            
            return {
            "status_code": 201,
            "user": {
                "id": create_user.id,
                "name": create_user.name,
                "email": create_user.email,
                "role_id": create_user.role_id,
                "created_at": str(create_user.created_at),
                "updated_at": str(create_user.updated_at),
            }}
        
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        
    def create_role(self, user: str):
        """Função responsável por criar um papel."""
        try:
            create_role = service.create_role(user)
            
            return create_role
        
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)