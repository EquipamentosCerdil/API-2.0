from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import motor.motor_asyncio

# Initialize FastAPI app
app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
database = client.test_database
collection = database.test_collection

# JWT Configuration
SECRET_KEY = "sua-chave-secreta-super-segura-admin-123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

# Admin credentials (básico como solicitado)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acesso requerido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro de autenticação",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Routes
@app.get("/api/")
async def root():
    return {"message": "API de Autenticação - Sistema Admin"}

@app.post("/api/login", response_model=Token)
async def login(login_data: LoginRequest):
    # Verificação básica admin/admin
    if login_data.username != ADMIN_USERNAME or login_data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@app.get("/api/verify-token")
async def verify_user_token(current_user: str = Depends(verify_token)):
    return {"username": current_user, "authenticated": True}

@app.get("/api/dashboard")
async def dashboard(credentials: HTTPAuthorizationCredentials = Depends(security)):
    username = verify_token(credentials)
    return {
        "message": f"Bem-vindo ao dashboard, {username}!",
        "user": username,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_status():
    try:
        # Test MongoDB connection
        result = await collection.find_one({})
        return {"status": "API funcionando", "database": "conectado"}
    except Exception as e:
        return {"status": "API funcionando", "database": "erro", "error": str(e)}
