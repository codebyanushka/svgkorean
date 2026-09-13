from fastapi import APIRouter

from app.api.v1.endpoints import auth, curation, student, teacher

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(student.router)
api_router.include_router(teacher.router)
api_router.include_router(curation.router)
