from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create(self, user: User) -> User:
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Email o username ya existe")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise ValueError(f"Error al crear el usuario: {str(e)}")

        