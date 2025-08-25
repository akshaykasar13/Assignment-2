from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from database import Base
import enum

class RunStatus(str, enum.Enum):
    success = "success"
    failure = "failure"
    running = "running"

class Pipeline(Base):
    __tablename__ = "pipelines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    runs = relationship("Run", back_populates="pipeline", cascade="all, delete-orphan")

class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False, index=True)
    status = Column(Enum(RunStatus), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_sec = Column(Float, nullable=True)
    branch = Column(String, nullable=True)
    commit = Column(String, nullable=True)
    triggered_by = Column(String, nullable=True)

    pipeline = relationship("Pipeline", back_populates="runs")
