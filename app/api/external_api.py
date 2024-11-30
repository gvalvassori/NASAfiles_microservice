from api import download
from fastapi import APIRouter

api_router = APIRouter()

# External API
api_router.include_router(download.router, tags=["NASA Ocean Data API"], prefix="/oceandata")