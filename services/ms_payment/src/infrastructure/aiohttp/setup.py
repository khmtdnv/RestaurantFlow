from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI


@asynccontextmanager
async def setup_aiohttp(app: FastAPI):
    app.state.http_session = aiohttp.ClientSession()

    try:
        yield
    finally:
        await app.state.http_session.close()
