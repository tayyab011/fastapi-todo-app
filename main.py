from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import models 
from models import Todos ,Users 
from pydantic import BaseModel , Field
from database import SessionLocal, engine
from typing import Annotated, Optional
from router import auth , admin
from router.auth import get_current_user
app = FastAPI()
app.include_router(auth.router)
app.include_router(admin.router)
models.Base.metadata.create_all(bind=engine)
user_dependency = Annotated[dict, Depends(get_current_user)]
class TodoCreate(BaseModel):
    id: int
    title: str
    description: str =Field(default=None, title="The description of the todo", max_length=100)
    priority: int = Field(gt=0, lt=6, description="The priority must be between 1 and 5")
    completed: bool = False

class TodoUpdate(BaseModel):
      title: Optional[str]=Field(default=None)
      description: Optional[str] =Field(default=None, title="The description of the todo", max_length=100)
      priority: Optional[int] = Field(default=None,gt=0, lt=6, description="The priority must be between 1 and 5")
      completed: Optional[bool] = Field(default=None)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_todos(user:user_dependency,db : Annotated[Session, Depends(get_db)]):
   if user is None:
         raise HTTPException(status_code=401, detail="Unauthorized")
   return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@app.get("/todo/{todo_id}")
def read_specific_todo(user:user_dependency,todo_id: int, db : Annotated[Session, Depends(get_db)]):
    if user is None:
             raise HTTPException(status_code=401, detail="Unauthorized")
    specific_todo = db.query(Todos).filter(Todos.id == todo_id ).filter(Todos.owner_id == user.get("id")).first()
    if not specific_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return specific_todo


@app.post("/create_todo")
def create_todos(user:user_dependency,db : Annotated[Session, Depends(get_db)] ,  new_todo:TodoCreate):
   if user is None:
      raise HTTPException(status_code=401, detail="Unauthorized")
   
   todo_model = Todos(**new_todo.model_dump(),owner_id = user.get("id"))
   db.add(todo_model)
   db.commit()
   return {"message": "Todo created successfully"}


@app.put("/edit_todo/{todo_id}")
def update_todos(user:user_dependency,todo_id: int, db : Annotated[Session, Depends(get_db)],update_todo:TodoUpdate):
    if user is None:
          raise HTTPException(status_code=401, detail="Unauthorized")
    todo = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    update_data = update_todo.model_dump(exclude_unset=True) # sudhu jei field change kortesi oita niyei kaj korte help kore
    for key , value in update_data.items():
        setattr(todo,key,value) 
    db.commit() 
    return {"message": "Todo update successfully"}

@app.delete("/delete/{todo_id}")
def delete_todos(user:user_dependency,todo_id: int, db : Annotated[Session, Depends(get_db)]):
    if user is None:
          raise HTTPException(status_code=401, detail="Unauthorized")
          
    todo = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@app.get("/user")
def get_user(user:user_dependency,db : Annotated[Session, Depends(get_db)]):
   if user is None:
         raise HTTPException(status_code=401, detail="authentication failed")
   return db.query(Users).filter(Users.id == user.get("id")).first()

