from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse
from app.exceptions import UserAlreadyExistsError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    repo = UserRepository(db)
    return AuthService(repo)

@router.post("/register", 
             response_model=UserResponse, 
             status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate, 
    service: AuthService = Depends(get_auth_service)):
    try: 
        return service.register(user_data)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
    ):
    try:
        token = service.login(form_data.username, form_data.password)
        return {"access_token": token, "token_type": "bearer"}
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )