import asyncio
import logging
import yt_dlp

from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from download_manager import *


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def yt_dlp_hooks(id: int, ytdl_info: dict()):
    """Main hook function handling progress hooks returned by
    yt-dlp module.

    Args:
        id (int): ID of the download record inside DownloadManager.
        ytdl_info (dict): Info returned by yt-dlp.
    """

    async def finished(id: int, ytdl_info: dict()):
        filename = ytdl_info["filename"]
        await manager.update_download(
            id,
            status=DLStatus.POSTPROCESSING,
            progress=100,
        )
        logger.debug(f"Downloaded to file: {filename}")

    async def downloading(id: int, ytdl_info: dict()):
        try:
            title = ytdl_info["info_dict"]["title"]
            # These fields may be missing, ignore errors
            dl_bytes = ytdl_info["downloaded_bytes"]
            total_bytes = ytdl_info["total_bytes"]
            percentage = int((dl_bytes / total_bytes) * 100)

            await manager.update_download(id, progress=percentage, name=title)

            logger.debug(
                f"Downloaded {dl_bytes} out of {total_bytes}, progress: {percentage}"
            )
        except KeyError:
            logger.warning(f"Could not get status update info")

    async def error(id: int, ytdl_info: dict()):
        await manager.update_download(id, status=DLStatus.ERROR)
        logger.error(f"Failed to download from id: {id}")

    if ytdl_info["status"] == "finished":
        await finished(id, ytdl_info)
    elif ytdl_info["status"] == "downloading":
        await downloading(id, ytdl_info)
    elif ytdl_info["status"] == "error":
        await error(id, ytdl_info)
    else:
        assert False


def start_download(download_id: int, url: str):
    """Background function run whenever a download should start.

    Args:
        download_id (int): Assigned download ID used by DownloadManager.
        url (str): URL to download from.
    """
    ydl_opts = {
        "outtmpl": {"default": "%(title)s.%(ext)s"},
        "progress_hooks": [lambda d: asyncio.run(yt_dlp_hooks(download_id, d))],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)


origins = [
    "*"
]

app = FastAPI()
manager = DownloadManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/download/", status_code=status.HTTP_202_ACCEPTED)
async def download_start(start: str, background_tasks: BackgroundTasks):
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            # Just try extracting info before downloading
            ydl.extract_info(start, download=False)
    except yt_dlp.utils.DownloadError:
        raise HTTPException(status_code=400, detail="Invalid Youtube link")

    download_id = await manager.insert_download(start)
    background_tasks.add_task(start_download, download_id, start)
    return dict(id=download_id)


@app.get("/download/{id}/status")
async def download_status(id: int):
    try:
        dl = await manager.get_download(id)
        return dict(
            id=dl.id,
            status=dl.status,
            progress=dl.progress,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="ID not found")


@app.get("/download/{id}")
async def download_exec(id: int):
    try:
        dl = await manager.get_download(id)
        if dl.status != DLStatus.FINISHED or dl.path is None:
            raise HTTPException(status_code=404, detail="File not ready")

        return FileResponse(path=dl.path, filename=dl.path.name)
    except KeyError:
        raise HTTPException(status_code=404, detail="ID not found")


@app.delete("/download/{id}")
async def download_delete(id: int):
    try:
        await manager.delete_download(id)
        return "delete"
    except KeyError:
        raise HTTPException(status_code=404, detail="ID not found")
