from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.models.note import Note
from app.models.user import User
from app.repositories.note_repository import NoteRepository
from app.exceptions import NoteNotFoundError, NotOwnerError
from app.utils.token_counter import count_tokens, truncate_to_token_limit
from app.config import settings

MAX_INPUT_TOKENS = 500
MAX_OUTPUT_TOKENS = 300
MODEL = "gpt-4o-mini"

# -- Cliente OpenAI --
client = OpenAI(api_key=settings.openai_api_key)

# -- Cliente LangChain --
langchain_llm = ChatOpenAI(
    model=MODEL,
    api_key=settings.openai_api_key,
    max_tokens=MAX_OUTPUT_TOKENS,
    temperature=0.7
)

# -- PromptTemplates --
summarize_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente que resume notas de forma clara y concisa."),
    ("human", "Resume la siguiente nota en máximo 2 oraciones:\n\n{content}")
])

improve_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente que mejora la redacción de textos manteniendo el contenido original."),
    ("human", "Mejora la redacción de la siguiente nota:\n\n{content}")
])

# -- Chains LCEL --

summarize_chain = (
    summarize_prompt 
    | langchain_llm
    | StrOutputParser()
)

improve_chain = (
    improve_prompt
    | langchain_llm
    | StrOutputParser()
)

class AIService:
    def __init__(self, note_repo: NoteRepository):
        self.note_repo = note_repo

    def _get_note_and_verify_owner(self, note_id: int, current_user: User) -> Note:
        note = self.note_repo.get_by_id(note_id)
        if not note:
            raise NoteNotFoundError(note_id)
        if note.owner_id != current_user.id:
            raise NotOwnerError()
        return note
    
    def _safe_content(self, content: str) -> str:
        return truncate_to_token_limit(content, MAX_INPUT_TOKENS)
    

    # -- OpenAI API --
    def _call_openai(self, system_prompt: str, user_prompt: str) -> dict:
        safe_content = truncate_to_token_limit(user_prompt, MAX_INPUT_TOKENS)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": safe_content}
            ],
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=0.7
        )
        
        return {
            "result": response.choices[0].message.content,
            "tokens_used": {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
        }
    
    # -- LangChain --
    def _call_langchain(self, chain, content: str) -> str:
        safe_content = self._safe_content(content)
        return chain.invoke({"content": safe_content})

    # -- Metodos con OpenAI API --
    def summarize(self, note_id: int, current_user: User) -> dict:
        note = self._get_note_and_verify_owner(note_id, current_user)
        response = self._call_openai(
            system_prompt="Eres un asistente que resume notas de forma clara y concisa.",
            user_prompt=f"Resume la siguiente nota en máximo 2 oraciones:\n\n{note.content}"
        )
        return {
            "note_id":     note.id,
            "title":       note.title,
            "summary":     response["result"],
            "tokens_used": response["tokens_used"],
            "engine":      "openai-sdk"
        }
        
    def improve(self, note_id: int, current_user: User) -> dict:
        note = self._get_note_and_verify_owner(note_id, current_user)
        response = self._call_openai(
            system_prompt="Eres un asistente que mejora la redacción de textos manteniendo el contenido original.",
            user_prompt=f"Mejora la redacción de la siguiente nota:\n\n{note.content}"
        )
        return {
            "note_id":          note.id,
            "title":            note.title,
            "improved_content": response["result"],
            "tokens_used":      response["tokens_used"],
            "engine":           "openai-sdk"
        }
        
    # -- Metodos con LangChain --
    def summarize_lc(self, note_id: int, current_user: User) -> dict:
        note = self._get_note_and_verify_owner(note_id, current_user)
        summary = self._call_langchain(summarize_chain, note.content)
        return {
            "note_id": note.id,
            "title":   note.title,
            "summary": summary,
            "engine":  "langchain-lcel"
        }

    def improve_lc(self, note_id: int, current_user: User) -> dict:
        note = self._get_note_and_verify_owner(note_id, current_user)
        improved = self._call_langchain(improve_chain, note.content)
        return {
            "note_id":          note.id,
            "title":            note.title,
            "improved_content": improved,
            "engine":           "langchain-lcel"
        }