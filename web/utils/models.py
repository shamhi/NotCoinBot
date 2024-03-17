from typing import Literal

from pydantic import BaseModel


class ClickStatus(BaseModel):
    status: Literal['on', 'off']
