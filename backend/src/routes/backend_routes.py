from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.controllers.backend_controller import BackendController

router = APIRouter(prefix="/roles", tags=["Roles"])
controller = BackendController()


@router.post("/create")
def create_role_and_user(user: dict):
    """Payload : {
        "name": "string",
        "email": "string",
        "password": "string",
        "description": "string",}"""
    try:
        result = controller.register_role_and_user(user)
        return JSONResponse(status_code=result["status_code"], content=result)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
@router.get("/users")
def get_users_with_roles_and_permissions():
    """GET /users, não é necessário parametros"""
    return controller.list_users_with_permissions()

@router.get("/users/{role_id}")
def get_users_by_role(role_id: int):
    """Payload : {
        "role_id": "int"}"""
    try:
        result = controller.get_user_role_by_roleId(role_id)
        if not result:
            raise HTTPException(status_code=404, detail="Nenhum usuário encontrado para este papel")
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# @router.get("/users/{user_id}")
# def get_user_role(user_id: int):
#     result = controller.get_user_role(user_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Usuário não encontrado")
#     return JSONResponse(status_code=200, content=result)
    