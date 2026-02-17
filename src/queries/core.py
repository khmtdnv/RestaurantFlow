from sqlalchemy import insert, select, text, update

from database import async_engine, sync_engine
from models import metadata_obj, workers_table


class SyncCore:
    @staticmethod
    def get_123_sync():
        with sync_engine.connect() as conn:
            res = conn.execute(text("SELECT VERSION()"))
            print(f"{res.all()=}")
            conn.commit()

    @staticmethod
    def create_tables():
        sync_engine.echo = False
        metadata_obj.drop_all(sync_engine)
        metadata_obj.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with sync_engine.connect() as conn:
            # stmt = """INSERT INTO workers (username) VALUES
            #     ('AO Bobr'),
            #     ('OOO Volk');"""
            stmt = insert(workers_table).values(
                [
                    {"username": "Bobr"},
                    {"username": "Volk"},
                ]
            )
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def select_workers():
        with sync_engine.connect() as conn:
            query = select(workers_table)
            result = conn.execute(query)
            workers = result.all()
            print(f"{workers=}")


class AsyncCore:
    @staticmethod
    async def get_123_async():
        async with async_engine.connect() as conn:
            res = await conn.execute(text("SELECT 1,2,3 union SELECT 4,5,6"))
            print(f"{res.all()=}")

    @staticmethod
    async def create_tables():
        sync_engine.echo = False
        metadata_obj.drop_all(sync_engine)
        metadata_obj.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    async def insert_workers():
        async with async_engine.connect() as conn:
            # stmt = """INSERT INTO workers (username) VALUES
            #     ('AO Bobr'),
            #     ('OOO Volk');"""
            stmt = insert(workers_table).values(
                [
                    {"username": "Bobr"},
                    {"username": "Volk"},
                ]
            )
            await conn.execute(stmt)
            await conn.commit()

    @staticmethod
    async def select_workers():
        async with async_engine.connect() as conn:
            query = select(workers_table)
            result = await conn.execute(query)
            workers = result.all()
            print(f"{workers=}")

    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        async with async_engine.connect() as conn:
            # # Сырой sql запрос
            # stmt = text("UPDATE workers SET username=:username WHERE id=:id")
            # stmt = stmt.bindparams(username=new_username, id=worker_id)
            # Или через функцию update из sqlalchemy
            stmt = (
                update(workers_table).values(username=new_username)
                # .where(workers_table.c.id == worker_id)
                # или вместо where использовать filter_by
                .filter_by(id=worker_id)
            )
            await conn.execute(stmt)
            await conn.commit()
