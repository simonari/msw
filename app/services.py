import sqlalchemy as orm

from . import database
from . import models

from . import custom_typings as ct


class DataBaseManger:
    def __init__(self):
        self.engine = database.engine
        self.session = database.SessionLocal

    async def get_session(self):
        try:
            yield self.session
        finally:
            await self.session.close()

    async def add_tables(self):
        async with self.engine.begin() as conn:
            return await conn.run_sync(models.Base.metadata.create_all)

    async def add_data(self, data: ct.response):
        # TODO: do it with async context manager
        session = self.session()
        # getting ids that we want to add
        missing = set([i["id"] for i in data])

        # getting ids that presented in database
        query = orm.select(models.Vacancy.id)
        existing = set(item[0] for item in await session.execute(query))

        # leaving only unique for database ids
        missing -= existing

        # creating a list of items that we want to add
        to_add = [models.Vacancy(**item) for item in data if item["id"] in missing]

        # adding items and saving state of database
        session.add_all(to_add)
        await session.commit()
        # closing session
        await session.close()
