from fastapi import APIRouter

from app.api.v1 import projects, modules, environments, cases, executions

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(projects.router)
api_router.include_router(modules.router)
api_router.include_router(environments.router)
api_router.include_router(cases.router)
api_router.include_router(executions.router)
