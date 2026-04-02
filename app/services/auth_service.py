from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
from app.repositories.user_repository import UserRepository
from app.utils.security import hash_password, verify_password, create_access_token

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def _check_user_exists(self, email: str, username: str) -> None:
        if self.user_repo.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado"
            )
        if self.user_repo.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El username ya está en uso"
            )

    def register(self, user_data: UserCreate) -> User:
        self._check_user_exists(user_data.email, user_data.username)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hash_password(user_data.password)
        )
        return self.user_repo.create(db_user)

    def login(self, email: str, password: str) -> str:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return create_access_token(data={"sub": user.email})