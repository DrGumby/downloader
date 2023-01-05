import hooks

from sqlalchemy.orm import Session


def get_ydl_opts(db: Session):
    return dict(
        outtmpl="%(title)s.%(ext)s",
        progress_hooks=[lambda d: hooks.download_progress_hook_dispatch(db, d)],
        postprocessor_hooks=[lambda d: hooks.postprocessor_hook_dispatch(db, d)],
        postprocessors=[dict(key="FFmpegExtractAudio", preferredcodec="mp3")],
    )
