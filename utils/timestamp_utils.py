from pydantic import BaseModel
from typing import Optional


class TsRangeRequest(BaseModel):
    ts_start: Optional[int] = None
    ts_end: Optional[int] = None
