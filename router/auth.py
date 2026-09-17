from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm ,OAuth2PasswordBearer
from typing import Annotated, Optional
from jose import jwt
from datetime  import timedelta , datetime ,timezone
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY ="DHSFKlihueqwdnjJJHUISDFGHWAFEYHjshffwjlweiqwpwieupcnerwiucbn"
ALGORITHM = "HS256"
OAuth2_bearer = OAuth2PasswordBearer(tokenUrl="login")
router = APIRouter()
class createUsers(BaseModel):
        email : str
        username : str
        firstname :  str
        lastname : str
        password : str
        role : str
        phone : str

class UpdateUser(BaseModel):
      email: Optional[str]=Field(default=None)
      username: Optional[str] =Field(default=None)
      firstname: Optional[str] =Field(default=None)
      lastname: Optional[str] =Field(default=None)
      phone: Optional[str] =Field(default=None)

class UpdatePassword(BaseModel):
      current_password: str
      new_password: str

      

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.post("/createuser")
def create_user(new_user: createUsers , db: Session = Depends(get_db)):
    user_model = Users( 
         email = new_user.email,
         username = new_user.username,
         firstname = new_user.firstname,
         lastname = new_user.lastname,
         hash_password = bcrypt_context.hash(new_user.password),
         is_active = True,
         role = new_user.role,
         phone = new_user.phone
    )
    db.add(user_model)
    db.commit()
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

def authenticate_user(username,password,db):
     user = db.query(Users).filter(Users.username == username).first()
     if user is None :
        return False
     if bcrypt_context.verify(password , user.hash_password):
          return user
     return False
def create_access_token(username:str , user_id:int,role:str,express_delta:timedelta):
   encode = {'sub':username,'id':user_id ,"role":role}
   expire = datetime.now(timezone.utc) + express_delta
   encode.update({"exp":expire}) 
   return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM) 

def get_current_user(token:str = Depends(OAuth2_bearer),db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username : str = payload.get("sub")
        user_id : int = payload.get("id")
        role : str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid Token")
        user = db.query(Users).filter(Users.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return {"username":username , "id":user_id , "role":role}
    except:
        raise HTTPException(status_code=401, detail="Invalid Token")
     
     
@router.post("/login")
def login_user(
    db: Session = Depends(get_db),
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()] = None,
):
   user = authenticate_user(form_data.username , form_data.password , db)
   if not user :
       raise HTTPException(status_code=401, detail="Fail Authentication")
   token = create_access_token(user.username,user.id,user.role,timedelta(minutes=30))
   return {
        "access_token": token,
        "token_type": "bearer"
    }

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.put("/edituser")
def update_user(
    user: user_dependency,
    db: Annotated[Session, Depends(get_db)],
    update_user: UpdateUser
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db_user = db.query(Users).filter(
        Users.id == user.get("id")
    ).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = update_user.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()

    return {"message": "User update successfully"}  

@router.put("/passwordChange")
def update_password(
    user: user_dependency,
    db: Annotated[Session, Depends(get_db)],
    updated_password: UpdatePassword
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(updated_password.current_password,user.hash_password):
        raise  HTTPException(status_code=401, detail="Wrong password")
    user.hash_password = bcrypt_context.hash(updated_password.new_password)
    db.add(user)
    db.commit()
    return {"message": "User password updated successfully"}  