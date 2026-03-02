# app/schemas.py

"""
Módulo de esquemas Pydantic para la validación de datos.
Define las estructuras de entrada y salida para la API.
"""
from __future__ import annotations
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

# --- USER ---
class UserBase(BaseModel):
    """Estructura base para usuarios."""
    email: EmailStr

class UserCreate(UserBase):
    """Esquema para creación de usuarios."""
    password: str

class User(UserBase):
    """Esquema de respuesta de usuario."""
    id: int
    is_active: bool
    
    model_config = {"from_attributes": True}

# --- BOARD ---
class BoardBase(BaseModel):
    """Estructura base para tableros."""
    title: str

class BoardCreate(BoardBase):
    """Esquema para creación de tableros."""

class BoardGet(BoardBase):
    """Esquema de respuesta de tableros."""
    id: int
    owner_id: int
    
    model_config = {"from_attributes": True}

# --- TOKEN ---
class Token(BaseModel):
    """Esquema para tokens de acceso."""
    access_token: str
    token_type: str

# --- CARD ---
class CardBase(BaseModel):
    """Estructura base para tarjetas."""
    title: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = None
    due_date: Optional[date] = None

class CardCreate(CardBase):
    """Esquema para creación de tarjetas."""
    list_id: int
    board_id: int

class CardMove(BaseModel):
    """Esquema para mover tarjetas entre listas."""
    list_id: int
    order: int

class CardUpdate(BaseModel):
    """Esquema para actualización parcial de tarjetas."""
    title: Optional[str] = Field(None, min_length=1, max_length=80)
    description: Optional[str] = None
    due_date: Optional[date] = None
    list_id: Optional[int] = None

class Card(CardBase):
    """Esquema de respuesta completa de tarjeta."""
    id: int
    list_id: int
    order: int
    board_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    labels: list[Label] = []
    subtasks: list['Subtask'] = []

    model_config = {"from_attributes": True}

# --- LIST (Renombrado para evitar conflicto con typing.List) ---
class CardInList(BaseModel):
    """Esquema simplificado de tarjeta para incluir en ListSchema."""
    id: int
    title: str
    description: Optional[str] = None
    order: int
    due_date: Optional[date] = None
    
    model_config = {"from_attributes": True}


class ListSchema(BaseModel):
    """Esquema para listas de tarjetas."""
    id: int
    title: str
    position: int
    board_id: int
    cards: List[CardInList] = []
    
    model_config = {"from_attributes": True}

# --- WORKLOG ---
class WorklogBase(BaseModel):
    """Estructura base para registros de horas."""
    date: date
    hours: float = Field(..., gt=0)
    note: Optional[str] = Field(None, max_length=200)

class WorklogCreate(WorklogBase):
    """Esquema para creación de registros de horas."""
    card_id: int

class WorklogUpdate(BaseModel):
    """Esquema para actualizar registros de horas - todos los campos opcionales."""
    model_config = {"extra": "forbid"}
    
    date: Optional[str] = None  # Aceptar string de fecha ISO y parsear luego
    hours: Optional[float] = None
    note: Optional[str] = None

class Worklog(WorklogBase):
    """Esquema de respuesta de registros de horas."""
    id: int
    card_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class WorklogResponse(BaseModel):
    """Esquema de respuesta para worklogs con card_title enriquecido."""
    id: int
    card_id: int
    card_title: str
    date: date
    hours: float
    note: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

# --- LABELS ---

class LabelBase(BaseModel):
    """Base para etiquetas."""
    name: str = Field(..., max_length=30)
    color: str = Field(..., max_length=20)


class LabelCreate(LabelBase):
    """Esquema para crear etiquetas."""
    


class Label(LabelBase):
    """Esquema de respuesta de etiquetas."""
    id: int
    card_id: int

    model_config = {"from_attributes": True}


class LabelTemplateBase(BaseModel):
    """Base para plantillas de etiquetas."""
    name: str
    color: str


class LabelTemplate(LabelTemplateBase):
    """Esquema de respuesta de plantillas."""
    id: int

    model_config = {"from_attributes": True}


# --- SUBTASKS ---
class SubtaskBase(BaseModel):
    """Base para subtasks."""
    title: str = Field(..., max_length=100)
    completed: bool = False


class SubtaskCreate(SubtaskBase):
    """Esquema para crear subtasks."""
    


class SubtaskUpdate(BaseModel):
    """Esquema para actualizar subtasks."""
    title: Optional[str] = Field(None, max_length=100)
    completed: Optional[bool] = None


class Subtask(SubtaskBase):
    """Esquema de respuesta de subtask."""
    id: int
    card_id: int

    model_config = {"from_attributes": True}
