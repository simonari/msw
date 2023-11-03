import asyncio
import time
import datetime
import re
import aiohttp
import aiohttp.web_exceptions

BASE_URL_API = "https://api.hh.ru/"
HEADERS = {"User-Agent": "Magistracy Diploma/0.1 (vsimonari@gmail.com)"}
HTML_TAG_PATTERN = re.compile("<.*?>")


class Downloader:
    def __init__(self):
        self.session: aiohttp.ClientSession = self._open_session()

    @staticmethod
    def _open_session():
        return aiohttp.ClientSession(BASE_URL_API, headers=HEADERS)

    def _close_session(self):
        self.session.close()

    async def _get_total_pages(self, params) -> int:
        response = await self.session.get("/vacancies", params=params)

        if response.status == 400:
            raise aiohttp.web_exceptions.HTTPBadRequest()

        content = await response.json()

        return content.get("pages")

    @staticmethod
    def _parse_page(content) -> list[int]:
        return [vacancy["id"] for vacancy in content["items"]]

    async def get_ids(self, params) -> list[int]:
        pages_total = await self._get_total_pages(params)

        ids = []
        for p in range(pages_total):
            params["page"] = p

            response = await self.session.get("/vacancies", params=params)

            if response.status == 400:
                raise aiohttp.web_exceptions.HTTPBadRequest()

            content = await response.json()

            ids += self._parse_page(content)

            time.sleep(0.05)

        return ids

    @staticmethod
    def _parse_vacancy(content) -> dict[str, str | list[str]]:
        salary = content.get("salary")
        salary_from = None
        salary_to = None
        currency = None

        if salary is not None:
            salary_from = salary.get("from")
            salary_to = salary.get("to")
            salary_from = float(salary_from) if salary_from is not None else None
            salary_to = float(salary_to) if salary_to is not None else None
            currency = salary.get("currency")

        return {
            "id": int(content.get("id")),
            "name": content.get("name"),
            "area": content.get("area").get("name"),
            "salary_from": salary_from,
            "salary_to": salary_to,
            "currency": currency,
            "experience": content.get("experience").get("name"),
            "schedule": content.get("schedule").get("name"),
            "employment": content.get("employment").get("name"),
            "description": re.sub(HTML_TAG_PATTERN, "", content.get("description")),
            "key_skills": [s.get("name") for s in content.get("key_skills")],
            "alternate_url": content.get("alternate_url"),
            "published_at": datetime.datetime.strptime(content.get("published_at").split("T")[0], "%Y-%m-%d"),
        }

    async def get_vacancies(self, query):
        params = {
            "per_page": "100",
            "text": f"{query}"
        }

        ids = await self.get_ids(params)
        found = []

        for _id in ids:
            response = await self.session.get(f"/vacancies/{_id}")

            if response.status == 400:
                raise aiohttp.web_exceptions.HTTPBadRequest()

            content = await response.json()

            found.append(self._parse_vacancy(content))

            time.sleep(0.5)

        return found
