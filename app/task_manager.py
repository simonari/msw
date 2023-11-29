from celery import Celery
import asyncio
import time

from .downloader import Downloader
from .logger import logger

celery = Celery(broker="pyamqp://localhost//")
loop = asyncio.get_event_loop()


@celery.task(name="download")
def download(query: str):
    logger.info(f"Task received with query: {query}")
    d = Downloader(query)
    logger.info(f"Downloader instantiated on {id(d)}")
    logger.info(f"({id(d)}): Download started")
    loop.create_task(d.run())
    # loop.run_in_executor(None, lambda: asyncio.run(d.run()))
