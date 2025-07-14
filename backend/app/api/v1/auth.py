from fastapi import APIRouter, Depends, HTTPException, status, Body
from app.core.auth import AuthService
from app.models.user import User
from sqlmodel import Session
from app.core.database import get_session
from typing import Dict
import asyncio

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", summary="JWT 로그인")
def login(
    email: str = Body(...),
    password: str = Body(...),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    # 실제 구현에서는 UserService 등에서 사용자 인증
    from app.models.user import User
    from sqlmodel import select
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user or not AuthService.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = AuthService.create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/firebase", summary="Firebase 토큰 검증 및 JWT 발급")
def firebase_login(
    id_token: str = Body(...),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    firebase_user = asyncio.run(AuthService.verify_firebase_token(id_token))
    if not firebase_user or not isinstance(firebase_user, dict):
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
    # firebase_uid로 User 조회 또는 생성
    from app.models.user import User
    from sqlmodel import select
    statement = select(User).where(User.firebase_uid == firebase_user["uid"])
    user = session.exec(statement).first()
    if not user:
        # 신규 유저 생성
        user = User(
            firebase_uid=firebase_user["uid"],
            email=firebase_user.get("email", ""),
            name=firebase_user.get("name", ""),
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    access_token = AuthService.create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", summary="내 정보(JWT 인증)")
def get_me(current_user: User = Depends(AuthService.get_current_active_user)):
    return current_user 