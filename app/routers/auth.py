from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", 
             response_model=UserResponse, 
             status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    service = AuthService(repo)
    return service.register(user_data)

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    repo = UserRepository(db)
    service = AuthService(repo)
    token = service.login(form_data.username, form_data.password)
    return {"access_token": token, "token_type": "bearer"}