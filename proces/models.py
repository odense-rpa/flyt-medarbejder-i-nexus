from enum import Enum
from typing import Optional
from pydantic import BaseModel, field_validator


class Opgavetype(str, Enum):
    TILFOEJELSE = "Tilføjelse"
    FJERNELSE = "Fjernelse"
    TILFOEJELSE_ROLLE = "Tilføjelse rolle"
    FJERNELSE_ROLLE = "Fjernelse rolle"


class Medarbejder(BaseModel):
    initialer: str
    organisation: Optional[str] = None
    opgavetype: Opgavetype
    rolle: Optional[str] = None