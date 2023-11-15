from sqlalchemy import select

from . import database
from . import models

from . import custom_typings as ct


class DataBaseManger:
    def __init__(self):
        self.engine = database.engine
        self.session = database.SessionLocal()

    async def get_session(self):
        try:
            yield self.session
        finally:
            await self.session.close()

    async def add_tables(self):
        async with self.engine.begin() as conn:
            return await conn.run_sync(models.Base.metadata.create_all)

    async def add_data(self, data: ct.response) -> int:
        missing = []

        for item in data:
            query = select(models.Vacancy).where(models.Vacancy.id == item["id"])
            result = await self.session.execute(query)

            if result is not None:
                continue

            missing.append(item)

        to_add = [models.Vacancy(**item) for item in missing]

        self.session.add_all(to_add)
        await self.session.commit()
        return len(to_add)
