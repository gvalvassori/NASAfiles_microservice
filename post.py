import requests

# URL del endpoint
url = "http://127.0.0.1:8080/download/"
# si lo corremos de forma local (no a traves del contenedor docker, el puerto por default es el 8000)

# Datos que deseas enviar en el POST
data = {
    "base_url": "https://oceandata.sci.gsfc.nasa.gov/directdataaccess/Ancillary/GLOBAL",
    "filter_list": ["GMAO_MERRA2.20230628T100000.MET.nc"],
    "filter_date": "20230628"
}

# Realizar la solicitud POST
response = requests.post(url, json=data)

# Verificar la respuesta
print(response.status_code)  # Debería imprimir 200 si todo está bien
print(response.json())  # Ver la respuesta en formato JSON