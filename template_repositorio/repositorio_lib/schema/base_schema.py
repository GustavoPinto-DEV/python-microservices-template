# dates
from datetime import datetime, time, date

# other
from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TblBaseSchema(BaseSchema):
    bas_id: int
    bas_nombre: str
    bas_activo: Optional[bool] = None

