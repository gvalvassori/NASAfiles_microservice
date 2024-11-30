import logging

from fastapi import APIRouter, Body, HTTPException
from schemas.download import DownloadRequest
from services.download import Download

router = APIRouter()
logger = logging.getLogger(f"app.{__name__}")

# Ruta para descargar archivos
@router.post("/download")
async def download_files(request: DownloadRequest = Body(...)):
    try:
        # Llamamos a la clase Download para ejecutar la descarga
        file_output = Download(logger, "gcrisnejo", "gcrisnejoA98")
        file_output.download(request.base_url, request.filter_list, request.filter_date)
        return {"message": "Download started successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))