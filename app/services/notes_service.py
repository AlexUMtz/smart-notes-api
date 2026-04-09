from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate
from app.repositories.note_repository import NoteRepository
from app.exceptions import NoteNotFoundError, NotOwnerError

class NotesService:
    def __init__(self, note_repo: NoteRepository):
        self.note_repo = note_repo
        
    def _get_note_and_verify_owner(self, note_id: int, current_user: User) -> Note:
        note = self.note_repo.get_by_id(note_id)
        if not note:
            raise NoteNotFoundError(note_id)
        if note.owner_id != current_user.id:
            raise NotOwnerError()
        return note
    
    def get_all(self, current_user: User) -> list[Note]:
        return self.note_repo.get_all_by_owner(current_user.id)
    
    def get_one(self, note_id: int, current_user: User) -> Note:
        return self._get_note_and_verify_owner(note_id, current_user)
    
    def create(self, note_data: NoteCreate, current_user: User) -> Note:
        return self.note_repo.create(note_data, current_user.id)
    
    def update(self, note_id: int, note_data: NoteUpdate, current_user: User) -> Note:
        note = self._get_note_and_verify_owner(note_id, current_user)
        return self.note_repo.update(note, note_data)
    
    def delete(self, note_id: int, current_user: User) -> None:
        note = self._get_note_and_verify_owner(note_id, current_user)
        self.note_repo.delete(note)
    