from pydantic import BaseModel

class Form(BaseModel):
    key: str
    name: str
    description: str | None = None
