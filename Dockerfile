# Usa una imagen base con Python 3.11
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /workdir

COPY requirements.txt /workdir/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY requirements_debug.txt /workdir/requirements_debug.txt
RUN pip install --no-cache-dir -r requirements_debug.txt

# Copia el contenido local (tu código) al contenedor 
COPY . /workdir

# Expone el puerto donde la app de FastAPI escuchará
EXPOSE 8000

# Ejecuta el servidor Uvicorn para servir la aplicación FastAPI
CMD ["uvicorn", "--app-dir", "/workdir/app","main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]