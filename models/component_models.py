from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class Component(BaseModel):
    id: Optional[int] = None
    key: str                      # e.g. "EmailBox"
    name: str                     # e.g. "Email Input Field"
    schema: Optional[Any] = None
    base_component_id: Optional[int] = None
    category: str                 # e.g. "input", "choice", "layout", "custom"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ComponentVersion(BaseModel):
    id: Optional[int] = None
    component_id: int
    version_number: int
    definition: dict              # Full component definition as JSON
    default_props: Optional[dict] = None      # Default properties as JSON
    validation_config: Optional[dict] = None  # Validation rules as JSON
    service_bindings: Optional[dict] = None   # Service endpoints as JSON
    is_active: bool = True
    created_at: Optional[datetime] = None