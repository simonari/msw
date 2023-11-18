import aiohttp.web_response
from fastapi import FastAPI, Depends, Response
import json

from .scheduler import DownloadSchedule
from .downloader import Downloader
from . import task_manager as tm

app = FastAPI()

scheduler = DownloadSchedule()
scheduler.start()


@app.get("/vacancies/{query}")
async def get_vacancy(query: str):
    tm.download.delay(query)
    return 200


@app.get("/scheduler/add/{time}/{query}")
async def add_task(time: str, query: str):
    scheduler.add_task(query, time)
