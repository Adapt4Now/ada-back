from pydantic import BaseModel
from typing import Annotated
from pydantic import Field, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginSchema(BaseModel):
    username: Annotated[str | None, Field(default=None)] = None
    email: Annotated[EmailStr | None, Field(default=None)] = None
    password: str

    model_config = dict(str_strip_whitespace=True)
