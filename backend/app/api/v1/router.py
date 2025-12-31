from fastapi import APIRouter

from app.api.v1 import projects, modules, environments, cases, executions, suites, schedules, stats

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(projects.router)
api_router.include_router(modules.router)
api_router.include_router(environments.router)
api_router.include_router(cases.router)
api_router.include_router(executions.router)
api_router.include_router(suites.router)
api_router.include_router(schedules.router)
api_router.include_router(stats.router)
