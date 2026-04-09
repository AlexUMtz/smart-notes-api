from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.note_repository import NoteRepository
from app.services.notes_service import NotesService
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.exceptions import NoteNotFoundError, NotOwnerError

router = APIRouter(prefix="/notes", tags=["Notes"])

def get_notes_service(db: Session = Depends(get_db)) -> NotesService:
    repo = NoteRepository(db)
    return NotesService(repo)

@router.get("/", 
            response_model=list[NoteResponse], 
            status_code=status.HTTP_200_OK,
            response_description="Lista de notas del usuario autenticado")
def get_all_notes(
    current_user: User = Depends(get_current_user),
    service: NotesService = Depends(get_notes_service)
):
    return service.get_all(current_user)

@router.get("/{note_id}",
            response_model=NoteResponse,
            status_code=status.HTTP_200_OK,
            response_description="Nota encontrada")
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    service: NotesService = Depends(get_notes_service)
):
    try:
        return service.get_one(note_id, current_user)
    except NoteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except NotOwnerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.post("/",
             response_model=NoteResponse,
             status_code=status.HTTP_201_CREATED,
             response_description="Nota creada exitosamente")
def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    service: NotesService = Depends(get_notes_service)
):
    return service.create(note_data, current_user)

@router.put("/{note_id}", 
            response_model=NoteResponse,
            status_code=status.HTTP_200_OK,
            response_description="Nota actualizada exitosamente")
def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    service: NotesService = Depends(get_notes_service)
):
    try:
        return service.update(note_id, note_data, current_user)
    except NoteNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except NotOwnerError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

@router.delete("/{note_id}", 
               status_code=status.HTTP_204_NO_CONTENT,
               response_description="Nota eliminada exitosamente")
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    service: NotesService = Depends(get_notes_service)
):
    try:
        service.delete(note_id, current_user)
    except NoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotOwnerError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
