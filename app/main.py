from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from . import schemas, database, auth, dependencies

database.init_db()

app = FastAPI()

# Allow frontend to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def redirect_to_register():
    return {"message": "Please visit /register to create an account"}

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = auth.hash_password(user.password)
    try:
        cursor.execute("""
            INSERT INTO users (name, roll_no, department, dob, year, email, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user.name, user.roll_no, user.department, user.dob, user.year, user.email, hashed_password))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    conn.close()
    return schemas.UserOut(**user.dict())

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = database.get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (form_data.username,)).fetchone()
    conn.close()
    
    if not user or not auth.verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = auth.create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/home")
def home(current_user: dict = Depends(dependencies.get_current_user)):
    return {"message": f"Welcome {current_user['name']}!"}

@app.get("/profile", response_model=schemas.UserOut)
def profile(current_user: dict = Depends(dependencies.get_current_user)):
    return schemas.UserOut(
        name=current_user["name"],
        roll_no=current_user["roll_no"],
        department=current_user["department"],
        dob=current_user["dob"],
        year=current_user["year"],
        email=current_user["email"]
    )
