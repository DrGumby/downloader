from pathlib import Path
from typing import List, Union

from sqlalchemy.orm import Session

import models


def create_video_info(
    db: Session,
    video_id: str,
    url: str,
    title: str,
):
    db_record = models.VideoInfo(
        video_id=video_id,
        url=url,
        title=title,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_video_info(
    db: Session,
    id: int,
):
    return db.query(models.VideoInfo).filter(models.VideoInfo.id == id).first()


def get_video_info_by_video_id(
    db: Session,
    video_id: str,
):
    return (
        db.query(models.VideoInfo).filter(models.VideoInfo.video_id == video_id).first()
    )


def create_download_job_started(
    db: Session,
):
    db_record = models.DownloadJob()
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_download_job(
    db: Session,
    id: int,
):
    return db.query(models.DownloadJob).filter(models.DownloadJob.id == id).first()


def get_download_job_all(
    db: Session,
):
    return db.query(models.DownloadJob).all()


def update_download_job(
    db: Session,
    id: int,
    status: Union[models.DownloadStatus, None] = None,
    progress: Union[int, None] = None,
    video_info_id: Union[int, None] = None,
    downloaded_file_id: Union[int, None] = None,
):
    db_record = db.query(models.DownloadJob).filter(models.DownloadJob.id == id)

    if status is not None:
        db_record.update(dict(status=status))
    if progress is not None:
        db_record.update(dict(progress=progress))
    if video_info_id is not None:
        db_record.update(dict(video_info_id=video_info_id))
    if downloaded_file_id is not None:
        db_record.update(dict(downloaded_file_id=downloaded_file_id))

    db.commit()
    return db_record


def create_downloaded_file(
    db: Session,
    path: Path,
    video_info_id: int,
):
    db_record = models.DownloadedFile(
        path=str(path),
        video_info_id=video_info_id,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_downloaded_file(
    db: Session,
    id: int,
):
    return (
        db.query(models.DownloadedFile).filter(models.DownloadedFile.id == id).first()
    )


def get_downloaded_file_all(
    db: Session,
):
    return db.query(models.DownloadedFile).all()


"""
def get_downloaded_file(db: Session, id: int):
    return (
        db.query(models.DownloadedFile).filter(models.DownloadedFile.id == id).first()
    )


def create_downloaded_file(db: Session, path: Path):
    db_record = models.DownloadedFile(
        path=str(path),
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_download_job(db: Session, id: int):
    return db.query(models.DownloadJob).filter(models.DownloadJob.id == id).first()


def get_download_job_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DownloadJob).offset(skip).limit(limit).all()


def create_download_job_base(db: Session, url: str, title: str):
    db_record = models.DownloadJob(
        url=url,
        title=title,
        downloaded_file_id=None,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def create_download_job_full(
    db: Session,
    url: str,
    title: str,
    status: models.DownloadStatus,
    progress: int,
    downloaded_file_id: int,
):
    db_record = models.DownloadJob(
        url=url,
        title=title,
        status=status,
        progress=progress,
        downloaded_file_id=downloaded_file_id,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def update_download_job(
    db: Session,
    job_id: int,
    status: Union[models.DownloadStatus, None] = None,
    progress: Union[int, None] = None,
    downloaded_file_id: Union[int, None] = None,
):
    db_record = db.query(models.DownloadJob).filter(models.DownloadJob.id == job_id)
    if status is not None:
        db_record.update(dict(status=status))
    if progress is not None:
        db_record.update(dict(progress=progress))
    if downloaded_file_id is not None:
        db_record.update(dict(downloaded_file_id=downloaded_file_id))

    db.commit()
    db.refresh(db_record)
    return db_record.first()

"""
