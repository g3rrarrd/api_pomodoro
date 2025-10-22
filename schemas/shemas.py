from pydantic import BaseModel
from datetime import datetime

class UsuarioInput(BaseModel):
    nickname: str

class UsuarioOutput(BaseModel):
    id_user: int
    nickname: str
    created_date: datetime

    class Config:
        orm_mode = True

class UsuarioResponse(BaseModel):
    message: str
    usuario: UsuarioOutput
