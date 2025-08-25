from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RunStatus(str, Enum):
    success = "success"
    failure = "failure"
    running = "running"

class RunIn(BaseModel):
    pipeline: str = Field(..., description="Pipeline name")
    status: RunStatus
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_sec: Optional[float] = None
    branch: Optional[str] = None
    commit: Optional[str] = None
    triggered_by: Optional[str] = None

class RunOut(BaseModel):
    id: int
    pipeline: str
    status: RunStatus
    started_at: datetime
    finished_at: Optional[datetime]
    duration_sec: Optional[float]
    branch: Optional[str] = None
    commit: Optional[str] = None
    triggered_by: Optional[str] = None

    class Config:
        from_attributes = True

class PipelineMetrics(BaseModel):
    pipeline: str
    total: int
    success: int
    failure: int
    success_rate: float
    avg_duration_sec: Optional[float]
    last_status: Optional[RunStatus]
    last_finished_at: Optional[datetime]

class SummaryMetrics(BaseModel):
    window_minutes: int
    total: int
    success: int
    failure: int
    success_rate: float
    avg_duration_sec: Optional[float]
    last_status: Optional[RunStatus]
    last_finished_at: Optional[datetime]
    per_pipeline: List[PipelineMetrics]
