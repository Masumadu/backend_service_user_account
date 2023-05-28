from fastapi import FastAPI

from .endpoints import sample_base_url, sample_router


def init_api_v1(app: FastAPI):
    app.include_router(
        router=sample_router, tags=["SampleRoute"], prefix=sample_base_url
    )
