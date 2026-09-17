from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm ,OAuth2PasswordBearer
from typing import Annotated
from jose import jwt
from datetime  import timedelta , datetime ,timezone
from router.auth import get_current_user
from models import Todos
router = APIRouter()
user_dependency = Annotated[dict, Depends(get_current_user)]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session,Depends(get_db)]



@router.get("/admin/todo")
def read_all(user:user_dependency,db : Annotated[Session, Depends(get_db)]):
   if user is None or user.get("role") != 'admin':
         raise HTTPException(status_code=401, detail="Unauthorized")
   return db.query(Todos).all()

@router.delete("/admin/delete/{todo_id}")
def delete_todos_by_Admin(user:user_dependency,todo_id: int, db : Annotated[Session, Depends(get_db)]):
    if user is None or user.get("role") != 'admin':
          raise HTTPException(status_code=401, detail="Unauthorized")
          
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}