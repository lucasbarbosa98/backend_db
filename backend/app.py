from fastapi import FastAPI
import uvicorn
from sqlalchemy.orm import Session

from src.dal.database import Database
from src.routes.backend_routes import router


app = FastAPI(title="Backend Teste", debug=True, version="1.0.0")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "MVC Backend API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)