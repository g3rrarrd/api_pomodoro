import re
from fastapi import HTTPException

VALID_STRING_PATTERN = re.compile(r'^[\w\s\.\-\@]+$')

def validar_string(texto: str, campo: str):
    if texto is None:
        return
    if not isinstance(texto, str):
        raise HTTPException(status_code=400, detail=f"El campo '{campo}' debe ser una cadena de texto.")
    if not VALID_STRING_PATTERN.match(texto):
        raise HTTPException(
            status_code=400,
            detail=f"El campo '{campo}' contiene caracteres no permitidos. "
                   "Solo se permiten letras, números, espacios, puntos, guiones y @."
        )