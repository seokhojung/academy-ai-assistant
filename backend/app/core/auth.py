from datetime import datetime, timedelta
from typing import Optional, Dict, Any
try:
    import firebase_admin
    from firebase_admin import auth, credentials
except ImportError:
    firebase_admin = None
    auth = None
    credentials = None
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.core.config import settings
from app.models.user import User
from app.core.database import get_session
import os

# Firebase 초기화
if firebase_admin:
    try:
        firebase_admin.get_app()
    except ValueError:
        # 환경 변수에서 Firebase 설정 읽기
        firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY")
        firebase_client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
        firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")
        
        if firebase_private_key and firebase_client_email and firebase_project_id and credentials:
            # 환경 변수에서 Firebase 설정 생성
            firebase_config = {
                "type": "service_account",
                "project_id": firebase_project_id,
                "private_key": firebase_private_key.replace('\\n', '\n'),
                "client_email": firebase_client_email,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{firebase_client_email}"
            }
            
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
        else:
            print("Warning: Firebase environment variables not found. Firebase auth will be disabled.")
            firebase_admin = None
else:
    print("Warning: Firebase admin not available. Firebase auth will be disabled.")

# JWT 설정
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 토큰
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials
    
    # JWT 토큰 검증
    payload = AuthService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 데이터베이스에서 사용자 조회
    statement = select(User).where(User.id == int(user_id))
    user = session.exec(statement).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    async def verify_firebase_token(id_token: str) -> Optional[Dict[str, Any]]:
        if not firebase_admin or not auth:
            return None
        
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Firebase token verification failed: {e}")
            return None
    
    @staticmethod
    async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 