from sqlalchemy.orm import Session
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

class NoteRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_by_id(self, note_id: int) -> Note | None:
        return self.db.query(Note).filter(Note.id == note_id).first()
    
    def get_all_by_owner(self, owner_id: int) -> list[Note]:
        return self.db.query(Note).filter(Note.owner_id == owner_id).all()
    
    def create(self, note_data: NoteCreate, owner_id: int) -> Note:
        try:
            db_note = Note(**note_data.model_dump(), owner_id=owner_id)
            self.db.add(db_note)
            self.db.commit()
            self.db.refresh(db_note)
            return db_note
        except Exception as e:
            self.db.rollback()
            raise e
        
    def update(self, note: Note, note_data: NoteUpdate) -> Note:
        try:
            for field, value in note_data.model_dump(exclude_unset=True).items():
                setattr(note, field, value)
            self.db.commit()
            self.db.refresh(note)
            return note
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete(self, note: Note) -> None:
        try:
            self.db.delete(note)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        