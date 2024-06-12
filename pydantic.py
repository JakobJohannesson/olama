from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

user = User(name="John Doe", email="johndoe@example.com", age=30)
print(user)