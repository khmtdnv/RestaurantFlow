import asyncio
import os
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from queries.core import AsyncCore, SyncCore
from queries.orm import AsyncORM, SyncORM

sys.path.insert(1, os.path.join(sys.path[0], ".."))


async def main():
    await AsyncORM.create_tables()

    await AsyncORM.insert_workers()

    await AsyncORM.insert_resumes()
    await AsyncORM.insert_additional_resumes()

    # await AsyncORM.select_resumes_avg_compensation()
    await AsyncORM.add_vacancies_and_replies()
    await AsyncORM.select_resumes_with_all_relationship()


def create_fastapi_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
    )

    @app.get("/workers")
    async def get_workers():
        workers = AsyncORM.select_workers_dto()
        return workers

    return app


app = create_fastapi_app()

if __name__ == "__main__":
    asyncio.run(main())
    # uvicorn.run(
    #     app="src.main:app",
    #     reload=True,
    # )
