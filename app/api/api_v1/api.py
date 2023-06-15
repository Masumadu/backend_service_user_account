from fastapi import FastAPI

from .endpoints import (
    resource_base_url,
    resource_router,
    role_base_url,
    role_router,
    user_base_url,
    user_router,
)


def init_api_v1(app: FastAPI):
    app.include_router(
        router=user_router, tags=["UserAccountManagement"], prefix=user_base_url
    )
    app.include_router(
        router=resource_router, tags=["ResourceManagement"], prefix=resource_base_url
    )
    app.include_router(router=role_router, tags=["RoleManagement"], prefix=role_base_url)
