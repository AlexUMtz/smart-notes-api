from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.repositories.note_repository import NoteRepository
from app.services.ai_service import AIService
from app.exceptions import NoteNotFoundError, NotOwnerError


router = APIRouter(prefix="/ai", tags=["AI"])

def get_ai_service(db: Session = Depends(get_db)) -> AIService:
    repo = NoteRepository(db)
    return AIService(repo)


@router.post("/notes/{note_id}/summarize")
def summarize_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    try:
        return service.summarize(note_id, current_user)
    except NoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotOwnerError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/notes/{note_id}/summarize-lc")
def summarize_note_langchain(
    note_id: int,
    current_user: User = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    try:
        return service.summarize_lc(note_id, current_user)
    except NoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotOwnerError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/notes/{note_id}/improve")
def improve_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    try:
        return service.improve(note_id, current_user)
    except NoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotOwnerError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    

@router.post("/notes/{note_id}/improve-lc")
def improve_note_langchain(
    note_id: int,
    current_user: User = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    try:
        return service.improve_lc(note_id, current_user)
    except NoteNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotOwnerError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))