from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from database import Base

class RoleEnum(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    user = "user"

class StatusEnum(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)
    assigned_to = Column(UUID, ForeignKey("users.id"))
    created_by = Column(UUID, ForeignKey("users.id"))
    due_date = Column(DateTime)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium)