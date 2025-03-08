from typing import Optional
from enum import Enum
from pydantic import BaseModel


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AIQueueData(BaseModel):
    unique_id: str
    loan_id: int
    loan_no: int
    vendor: str
    transaction_id: str
    org_name: str
    priority: Priority
    image_base_url: str
    pdf_base_url: str
    user_id: Optional[int] = None
