from fastapi import FastAPI

from .logger import logger
from .scheduler.DownloadScheduler import DownloadSchedule
from . import task_manager as tm

app = FastAPI()

scheduler = DownloadSchedule()
scheduler.start()


@app.get("/vacancies/{query}")
async def get_vacancy(query: str):
    logger.info(f"Got GET request with query: {query}")
    logger.info(f"Queueing task to Celery")
    tm.download.delay(query)
    return 200


@app.get("/scheduler/add/{api}/{time}/{query}")
async def add_task(api: str, time: str, query: str):
    scheduler.add_task(api, query, time)
