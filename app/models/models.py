from datetime import datetime
from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from uuid import uuid4
from sqlalchemy import Enum as PyEnum

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"

    class AgentStatus(PyEnum):
        ACTIVE = "active"
        INACTIVE = "inactive"
        SUSPENDED = "suspended"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uid = Column(UUID, unique=True, default=uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def model_dump(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "password": self.password,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class AgentAssignment(Base):
    __tablename__ = "agent_assignments"

    class AssignmentStatus(PyEnum):
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"

    class AssignmentType(PyEnum):
        VERIFICATION = "verification"
        PAYMENT_REMINDER = "payment_reminder"
        DOCUMENT_COLLECTION = "document_collection"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uid = Column(UUID, unique=True, default=uuid4)
    agent_id = Column(UUID, ForeignKey("agents.uid"), nullable=True)
    assignment_id = Column(UUID, nullable=False)
    action = Column(String, nullable=False)
    property_id = Column(UUID, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def model_dump(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "agent_id": self.agent_id,
            "assignment_id": self.assignment_id,
            "action": self.action,
            "property_id": self.property_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

class AgentLocationActivity(Base):
    __tablename__ = "agent_location_activities"

    id = Column(UUID, primary_key=True, default=uuid4)
    agent_id = Column(UUID, ForeignKey("agents.uid"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    accuracy = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def model_dump(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp,
            "accuracy": self.accuracy,
            "speed": self.speed,
            "heading": self.heading,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
