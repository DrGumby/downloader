import enum

from sqlalchemy import (
    DateTime,
    Enum,
    Column,
    ForeignKey,
    Integer,
    String,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class DownloadStatus(str, enum.Enum):
    """Represents the status of a single download"""

    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    DOWNLOADED = "DOWNLOADED"
    POSTPROCESSING = "POSTPROCESSING"
    POSTPROCESSING_DONE = "POSTPROCESSING_DONE"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


class VideoInfo(Base):
    """Video information helper table."""

    __tablename__ = "video_info"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)

    original_jobs = relationship("DownloadJob", back_populates="video_info")

    downloaded_file = relationship(
        "DownloadedFile", back_populates="video_info", uselist=False
    )


class DownloadedFile(Base):
    """Table type used to store downloaded file records
    with their paths.
    """

    __tablename__ = "downloaded_file"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True)
    created_at = Column(DateTime, server_default=func.now())

    video_info_id = Column(Integer, ForeignKey("video_info.id"), unique=True)
    video_info = relationship("VideoInfo", back_populates="downloaded_file")

    original_jobs = relationship("DownloadJob", back_populates="downloaded_file")


class DownloadJob(Base):
    """Table type used to store job statuses for
    individual downloads.
    """

    __tablename__ = "download_job"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(
        Enum(DownloadStatus), nullable=False, default=DownloadStatus.STARTED
    )
    progress = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, server_default=func.now())

    downloaded_file_id = Column(Integer, ForeignKey("downloaded_file.id"))
    downloaded_file = relationship("DownloadedFile", back_populates="original_jobs")

    video_info_id = Column(Integer, ForeignKey("video_info.id"))
    video_info = relationship("VideoInfo", back_populates="original_jobs")

    CheckConstraint(
        "progress >= 0 AND progress <= 100", name="download_job_progress_percent_check"
    )
