from fastapi import FastAPI
import uvicorn
from sqlalchemy.orm import Session

from src.dal.database import Database
from src.routes.backend_routes import router

""" Instancia o FastAPI, modo debug e versão """
app = FastAPI(title="Backend Test", debug=True, version="1.0.0")

""" Registra as rotas definidas em routes """
app.include_router(router)

""" Rota base para verificar se o servidor está rodando """
@app.get("/")
def read_root():
    return {"message": "is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
    
    """ Para rodar o servidor, execute:
    uvicorn backend.app:app --reload | uvicorn app:app --host 127.0.0.1 --port 8000
    Requisições : http://127.0.0.1:8000/roles/ """