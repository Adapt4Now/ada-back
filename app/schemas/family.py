from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


class FamilyCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    created_by: Annotated[int, Field(gt=0)]


class FamilyResponse(BaseModel):
    id: Annotated[int, Field(gt=0)]
    name: Annotated[str, Field(min_length=1, max_length=100)]
    created_by: Annotated[int, Field(gt=0)]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
