from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Component(BaseModel):
    id: Optional[int] = None
    key: str                      # e.g. "EmailBox"
    name: str                     # e.g. "Email Input Field"
    description: Optional[str] = None
    base_component_id: Optional[int] = None
    category: str                 # e.g. "input", "choice", "layout", "custom"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ComponentVersion(BaseModel):
    id: Optional[int] = None
    component_id: Optional[int] = None
    version_number: Optional[int] = None        # e.g. 1, 2, 3
    definition: Optional[dict] = None         # Full component definition as JSON

    # Field class allows for empty values to be empty dicts instead of None
    default_props: Optional[dict] = Field(default_factory=dict)      # Default properties as JSON
    validation_config: Optional[dict] = Field(default_factory=dict)  # Validation rules as JSON
    service_bindings: Optional[dict] = Field(default_factory=dict)   # Service endpoints as JSON
    
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None