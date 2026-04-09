class NoteNotFoundError(Exception):
    def __init__(self, note_id: int):
        self.note_id = note_id
        super().__init__(f"Nota {note_id} no encontrada.")


class NotOwnerError(Exception):
    def __init__(self):
        super().__init__("No tienes permiso para acceder a esta nota")


class UserAlreadyExistsError(Exception):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"El {field} ya esta registrado")        


class InvalidCredentialsError(Exception):
    def __init__(self):
        super().__init__("Credenciales incorrectas")        

