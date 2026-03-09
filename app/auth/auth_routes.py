from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.database import get_connection
from app.auth.auth_service import hash_password, verify_password, create_access_token

router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(user: RegisterRequest):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (user.username,)
    )

    existing = cursor.fetchone()

    if existing:
        return {"error": "User already exists"}

    hashed_password = hash_password(user.password)

    cursor.execute(
        """
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
        """,
        (
            user.username,
            user.email,
            hashed_password,
            user.role
        )
    )

    conn.commit()
    conn.close()

    return {"message": "User registered successfully"}
    
@router.post("/login")
def login_user(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (data.username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(
        {
            "user_id": user["id"],
            "username": user["username"],
            "role": user["role"],
        }
    )

    return {"access_token": token, "token_type": "bearer"}

@router.post("/reset-password")
def reset_password(username: str, new_password: str):

    conn = get_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(new_password)

    cursor.execute(
        """
        UPDATE users
        SET password = ?
        WHERE username = ?
        """,
        (hashed_password, username)
    )

    conn.commit()
    conn.close()

    return {"message": "Password reset successfull"}