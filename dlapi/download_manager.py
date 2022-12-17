import asyncio
import logging

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Union

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DLStatus(str, Enum):
    """Download status enumeration"""

    IN_PROGRESS = "IN_PROGRESS"
    POSTPROCESSING = "POSTPROCESSING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


@dataclass
class Download:
    """Single download entry"""

    id: int
    url: str
    status: DLStatus
    progress: int
    path: Union[Path, None]


class DownloadManager:
    """Main download manager. Used to store the download information."""

    def __init__(self) -> None:
        self.access_lock = asyncio.Lock()
        self.current_id = 0
        self.downloads = dict()

    async def insert_download(self, url: str) -> int:
        """Initialize a single download from given URL.

        Args:
            url (str): URL string from which to download

        Returns:
            int: ID of inserted entry
        """
        async with self.access_lock:
            id = self.current_id

            # Should never happen, but check anyways
            assert id not in self.downloads

            dl = Download(
                id=id,
                url=url,
                status=DLStatus.IN_PROGRESS,
                progress=0,
                path=None,
            )

            self.downloads[id] = dl
            self.current_id += 1

        logger.debug(f"Inserted new download with id {id}")
        return id

    async def get_download(self, id: int) -> Download:
        """Get the download info for given id.

        Args:
            id (int): ID of download info to return.

        Returns:
            Download: Returned download info object.
        """
        async with self.access_lock:
            dl = self.downloads[id]

        return dl

    async def update_download(
        self,
        id: int,
        status: Union[DLStatus, None] = None,
        progress: Union[int, None] = None,
        path: Union[Path, None] = None,
    ):
        """Update a specified download record.

        Args:
            id (int): ID of record to be updated.
            status (Union[DLStatus, None]): Status to be set (or None for no change).
            progress (Union[int, None]): Progress to be set (or None for no change).
            path (Union[Path, None]): Path to be set (or None for no change).
        """
        async with self.access_lock:
            dl: Download = self.downloads[id]

            if status is not None:
                dl.status = status
            if progress is not None:
                dl.progress = progress
            if path is not None:
                dl.path = path

            # Not sure if this is necessary
            self.downloads[dl.id] = dl

        logger.debug(
            f"Updated download id: {id} with status: {status}, progress: {progress}, path: {path}"
        )

    async def delete_download(self, id: int):
        """Remove given record from the download dict.

        Args:
            id (int): ID to be removed.
        """
        async with self.access_lock:
            dl = self.downloads[id]
            if dl.path is not None:
                dl.path.unlink()

            del self.downloads[id]

        logger.debug(f"Removed download with id: {id}")
