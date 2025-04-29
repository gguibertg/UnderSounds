# Utilizamos una imagen base de Python. Puedes elegir la versión que necesites.
FROM python:3.12-slim

# Establecemos el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copiamos nuestro código en el contenedor
COPY . .

# Instalamos las dependencias de la aplicación.
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos el puerto en el que la aplicación FastAPI escuchará (por defecto es el 8000).
EXPOSE 8000

# Comando para ejecutar la aplicación FastAPI. TODO
CMD ["uvicorn", "controller.controller:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 