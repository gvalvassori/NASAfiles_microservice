import logging

from fastapi import FastAPI
from api.external_api import api_router

# Crear la app FastAPI
app = FastAPI(
    title="NASA Ocean Data API",
    description="API para descargar archivos de la NASA",
    version="0.1"
)

app.include_router(api_router)

# Logger para el servicio
logger = logging.getLogger(__name__)


