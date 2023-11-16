from celery import Celery
from .downloader import Downloader
import asyncio

celery = Celery(broker="pyamqp://localhost//")
loop = asyncio.get_event_loop()


@celery.task(name="download")
def download(query: str):
    d = Downloader(query)
    loop.run_until_complete(d.run())
