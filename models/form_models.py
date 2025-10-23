from pydantic import BaseModel, Field
from typing import List, Optional

class Form(BaseModel):
    key: str
    name: str
    description: str | None = None


class FormVersion(BaseModel):
    form_id: int
    version_number: int
    key: str
    schema: dict
    is_active: bool = True

