import uvicorn
from fastapi import FastAPI
from strawberry.asgi import GraphQL
import strawberry
from sqlalchemy import create_engine, Column, Integer, String
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

@strawberry.type
class UserType:
    id: int
    name: str
    age: int

@strawberry.type
class Query:
    @strawberry.field
    def user(self, info, id: int) -> UserType:
        db = Session()
        user = db.query(User).filter(User.id == id).first()
        db.close()
        return UserType(id=user.id, name=user.name, age=user.age)

    @strawberry.field
    def users(self, info) -> list[UserType]:
        db = Session()
        users = db.query(User).all()
        db.close()
        return [UserType(id=user.id, name=user.name, age=user.age) for user in users]

@strawberry.type
class Mutation:
    @strawberry.mutation(name="createUser")
    def create_user(self, info, name: str, age: int) -> UserType:
        db = Session()
        user = User(name=name, age=age)
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return UserType(id=user.id, name=user.name, age=user.age)

schema = strawberry.Schema(query=Query, mutation=Mutation)
app.add_route("/", GraphQL(schema))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
