from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Enum
from datetime import datetime
import enum
from config.settings import settings

engine = create_async_engine(settings.DB_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class ProjectStatus(str, enum.Enum):
    CREATED = "created"
    REQUIREMENTS_ANALYSED = "requirements_analysed"
    BACKLOG_READY = "backlog_ready"
    SPRINT_PLANNING = "sprint_planning"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"

class SprintStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, default=ProjectStatus.CREATED)
    requirements_raw = Column(Text)
    backlog = Column(JSON)
    architecture = Column(Text)
    sprints = Column(JSON)
    current_sprint = Column(Integer, default=0)
    report = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentLog(Base):
    __tablename__ = "agent_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, nullable=False)
    sprint_number = Column(Integer)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    input_data = Column(Text)
    output_data = Column(Text)
    status = Column(String, default="success")
    timestamp = Column(DateTime, default=datetime.utcnow)

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, nullable=False)
    sprint_number = Column(Integer)
    test_type = Column(String)  # security, performance, uat, unit
    status = Column(String)     # passed, failed
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
