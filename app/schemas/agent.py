from pydantic import BaseModel
from uuid import UUID

class AgentSchema(BaseModel):
    id: int
    Uid: UUID
    first_name: str
    last_name:str
    email: str
    phone: str
    password:str
    status: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True


class AgentAssignmentSchema(BaseModel):
    id: int
    uid: UUID
    agent_id: UUID
    assignment_id: UUID
    action: str
    property_id: UUID
    status: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
    