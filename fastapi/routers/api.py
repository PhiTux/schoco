from fastapi import APIRouter
from routers import auth

router = APIRouter()
router.include_router(auth)
