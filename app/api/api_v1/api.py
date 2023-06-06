from fastapi import FastAPI

from .endpoints import user_base_url, user_router


def init_api_v1(app: FastAPI):
    app.include_router(
        router=user_router, tags=["UserAccountManagement"], prefix=user_base_url
    )
