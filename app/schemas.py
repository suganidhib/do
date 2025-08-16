from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    roll_no: str
    department: str
    dob: str
    year: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    name: str
    roll_no: str
    department: str
    dob: str
    year: str
    email: EmailStr
