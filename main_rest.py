import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

engine = create_engine("sqlite:///./users.db")
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)


class UserCreate(BaseModel):
    name: str
    age: int


class UserResponse(BaseModel):
    id: int
    name: str
    age: int


@app.get("/users", response_model=List[UserResponse])
async def get_all_users() -> List[UserResponse]:
    db = Session()
    users = db.query(User).all()
    db.close()
    return [UserResponse(id=user.id, name=user.name, age=user.age) for user in users]


@app.post("/users/")
def create_user(user: UserCreate):
    db = Session()
    db_user = User(name=user.name, age=user.age)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user


@app.get("/users/{user_id}")
def get_user(user_id: int):
    db = Session()
    db_user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return db_user


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
