# NASAfiles_microservice
Este es un microservicio que descarga datos del sitio web de Nasa. Utilizamos FastAPI, y esta dockerizado para luego poder correrlo con Cloud Functions

## Local

Para correr el servicio de forma local usar:

uvicorn main:app --reload

y en el archivo post.py cambiar al puerto 8000

Luego hacer el post:

python3 post.py

y se descargan los archivos

## Docker

Para correrlo a través de docker, primero generar la imagen docker

docker build -t download-service .

Y luego levantar el contenedor:

docker run -d -p 8080:8080 download-service

Notemos que usamo el puerto 8080 y no el 8000.

Finalmente, hacer el post:

python3 post.py

