from werkzeug.security import generate_password_hash, check_password_hash
from fastapi import HTTPException
from backend.models import Register
from database.connection import get_db
# ------------------- REGISTER -------------------

def checking(name,email,username,password,db):
    if not all([name, email, username, password]):
        raise HTTPException(status_code=400, detail="All fields are required")
    print("hello")
    hashed_password = generate_password_hash(password)

    # Check if user already exists
    existing_user = db.query(Register).filter(
        (Register.email == email) | (Register.username == username)
    ).first()

    if existing_user:
         raise HTTPException(status_code=409, detail="Email or Username already exists")

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create new user object
    new_user = Register(
        name=name,
        email=email,
        username=username,
        password=hashed_password
    )
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }
    
# ------------------- LOGIN -------------------
def login_user(username: str, password: str, db):

    if not all([username, password]):
        raise HTTPException(status_code=400, detail="Username and password required")

    # Find user by username OR email
    user = db.query(Register).filter(
        (Register.username == username) | (Register.email == username)
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check password
    if not check_password_hash(user.password, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Login success
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username
        }
    }