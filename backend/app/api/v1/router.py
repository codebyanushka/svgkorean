from fastapi import APIRouter

from app.api.v1.endpoints import auth, curation, student, teacher, teacher_vocabulary, vocab_lab

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(student.router)
api_router.include_router(vocab_lab.router)
api_router.include_router(teacher.router)
api_router.include_router(teacher_vocabulary.router)
api_router.include_router(curation.router)
