from pathlib import Path

import yt_dlp
from fastapi import BackgroundTasks, Body, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import crud
import hooks
import models
import ydl_config

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["content-disposition"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def start_download(db: Session, url: str):
    with yt_dlp.YoutubeDL(ydl_config.get_ydl_opts(db)) as ydl:
        ydl.download(url)


def skip_download(db: Session, video_info_id: int):
    video_info = crud.get_video_info(db, video_info_id)
    assert video_info is not None

    file = video_info.downloaded_file

    assert file is not None

    for i in video_info.original_jobs:
        id = i.id
        crud.update_download_job(
            db=db,
            id=id,
            status=models.DownloadStatus.FINISHED,
            progress=100,
            downloaded_file_id=file.id,
        )


def init_download_checked(db: Session, job_id: int, url: str) -> None:
    with yt_dlp.YoutubeDL({}) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            assert type(info_dict) is dict
        except yt_dlp.utils.DownloadError as e:
            crud.update_download_job(db, job_id, status=models.DownloadStatus.ERROR)
            return

    video_id = info_dict["id"]
    title = info_dict["title"]

    stored_info = crud.get_video_info_by_video_id(db, video_id)
    if stored_info is None:
        stored_info = crud.create_video_info(db, video_id, url, title)

    assert stored_info is not None

    crud.update_download_job(db, job_id, video_info_id=stored_info.id)

    if stored_info.downloaded_file is not None:
        skip_download(db, stored_info.id)
    else:
        start_download(db, url)


@app.post("/api/download_job")
async def create_download_job(
    background_tasks: BackgroundTasks,
    url: str = Body(),
    db: Session = Depends(get_db),
):
    record = crud.create_download_job_started(db)
    if record is None:
        raise HTTPException(status_code=500, detail="DB failed to create object")

    background_tasks.add_task(init_download_checked, db, record.id, url)
    return {"id": record.id}


@app.get("/api/download_job")
async def get_download_job_all(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_download_job_all(db)


@app.get("/api/download_job/{id}")
async def get_download_job(id: int, db: Session = Depends(get_db)):
    return crud.get_download_job(db, id)


@app.get("/api/downloaded_file")
async def get_downloaded_file_all(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_downloaded_file_all(db)


@app.get("/api/downloaded_file/{id}")
async def get_downloaded_file(id: int, db: Session = Depends(get_db)):
    file = crud.get_downloaded_file(db, id)
    if file is None:
        raise HTTPException(status_code=404, detail="No such 'id' in database")

    path = file.path
    return FileResponse(path, filename=Path(path).name)
