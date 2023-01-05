from pathlib import Path

import yt_dlp
from sqlalchemy.orm import Session

import crud
import models


def download_progress_hook_downloading(db: Session, ydl_info: dict):
    video_id = ydl_info["info_dict"]["id"]
    dl_bytes = ydl_info["downloaded_bytes"]
    total_bytes = ydl_info["total_bytes"]
    progress = int((dl_bytes / total_bytes) * 100)
    status = models.DownloadStatus.IN_PROGRESS

    video_info = crud.get_video_info_by_video_id(db, video_id)

    assert video_info is not None

    for i in video_info.original_jobs:
        id = i.id
        crud.update_download_job(
            db=db,
            id=id,
            status=status,
            progress=progress,
        )


def download_progress_hook_finished(db: Session, ydl_info: dict):
    video_id = ydl_info["info_dict"]["id"]
    status = models.DownloadStatus.DOWNLOADED
    progress = 100

    video_info = crud.get_video_info_by_video_id(db, video_id)

    assert video_info is not None

    for i in video_info.original_jobs:
        id = i.id
        crud.update_download_job(
            db=db,
            id=id,
            status=status,
            progress=progress,
        )


def download_progress_hook_error(db: Session, ydl_info: dict):
    video_id = ydl_info["info_dict"]["id"]
    status = models.DownloadStatus.ERROR

    video_info = crud.get_video_info_by_video_id(db, video_id)

    assert video_info is not None

    for i in video_info.original_jobs:
        id = i.id
        crud.update_download_job(
            db=db,
            id=id,
            status=status,
        )


def download_progress_hook_dispatch(db: Session, ydl_info: dict):
    if ydl_info["status"] == "downloading":
        download_progress_hook_downloading(db, ydl_info)
    elif ydl_info["status"] == "finished":
        download_progress_hook_finished(db, ydl_info)
    elif ydl_info["status"] == "error":
        download_progress_hook_error(db, ydl_info)
    else:
        assert False


def audio_postprocessor_hook_started(db: Session, ydl_info: dict):
    video_id = ydl_info["info_dict"]["id"]
    status = models.DownloadStatus.POSTPROCESSING

    video_info = crud.get_video_info_by_video_id(db, video_id)

    assert video_info is not None

    for i in video_info.original_jobs:
        id = i.id
        crud.update_download_job(
            db=db,
            id=id,
            status=status,
        )


def audio_postprocessor_hook_processing(db: Session, ydl_info: dict):
    audio_postprocessor_hook_started(db, ydl_info)


def audio_postprocessor_hook_finished(db: Session, ydl_info: dict):
    video_id = ydl_info["info_dict"]["id"]
    status = models.DownloadStatus.POSTPROCESSING_DONE

    video_info = crud.get_video_info_by_video_id(db, video_id)

    assert video_info is not None

    for i in video_info.original_jobs:
        id = i.id
        crud.update_download_job(db=db, id=id, status=status)


def move_files_postprocessor_hook_finished(db: Session, ydl_info: dict):
    info_dict = ydl_info["info_dict"]
    video_id = info_dict["id"]
    status = models.DownloadStatus.FINISHED

    video_info = crud.get_video_info_by_video_id(db, video_id)

    assert video_info is not None

    filename = info_dict["filepath"]
    file = crud.create_downloaded_file(db, Path(filename), video_info.id)

    assert file is not None

    for i in video_info.original_jobs:
        id = i.id
        crud.update_download_job(
            db=db,
            id=id,
            status=status,
            downloaded_file_id=file.id,
        )


def postprocessor_hook_dispatch(db: Session, ydl_info: dict):
    if ydl_info["postprocessor"] == "MoveFiles":
        if ydl_info["status"] == "finished":
            move_files_postprocessor_hook_finished(db, ydl_info)

    if ydl_info["postprocessor"] != "ExtractAudio":
        return

    if ydl_info["status"] == "started":
        audio_postprocessor_hook_started(db, ydl_info)
    elif ydl_info["status"] == "processing":
        audio_postprocessor_hook_processing(db, ydl_info)
    elif ydl_info["status"] == "finished":
        audio_postprocessor_hook_finished(db, ydl_info)
    else:
        assert False
