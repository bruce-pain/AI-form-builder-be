from fastapi import APIRouter

from app.features.auth.routes import auth_router
from app.features.form.routes import form_router
from app.features.response.routes import response_router

main_router = APIRouter(prefix="/api/v1")
main_router.include_router(auth_router)
main_router.include_router(form_router)
main_router.include_router(response_router)
