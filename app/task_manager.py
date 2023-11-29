from celery import Celery
import asyncio

from .downloader import Downloader
from .logger import logger

celery = Celery(broker="pyamqp://localhost//")
loop = asyncio.get_event_loop()


@celery.task(name="download")
def download(api: str, query: str):
    logger.info(f"Task received with query: {query} to {api} API")
    d = Downloader(api, query)
    logger.info(f"Downloader instantiated on {id(d)}")
    logger.info(f"({id(d)}): Download started")
    loop.create_task(d.run())
    # loop.run_in_executor(None, lambda: asyncio.run(d.run()))
