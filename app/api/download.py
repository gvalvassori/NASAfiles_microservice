import logging

from fastapi import APIRouter, Body
from schemas.download import DownloadRequest
from services.download import Download

router = APIRouter()
logger = logging.getLogger(f"app.{__name__}")

# Ruta para descargar archivos
@router.post("/download")
def download_files(request: DownloadRequest = Body(...)):
    file_output = Download(logger, "gcrisnejo", "gcrisnejoA98")
    file_output.download(request.base_url, request.filter_list, request.filter_date)
    return {"message": "Download started successfully."}