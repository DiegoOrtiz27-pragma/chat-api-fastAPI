FROM python:3.13

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /code

# Copia primero el archivo de dependencias.
COPY requirements.txt requirements.txt

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación (la carpeta 'src') al contenedor
COPY ./src ./src

# Expone el puerto 8000 para que la aplicación sea accesible desde fuera del contenedor
EXPOSE 8000

# El comando para ejecutar la aplicación cuando el contenedor inicie.
# Se usa 0.0.0.0 para que sea accesible desde fuera del contenedor.
CMD ["uvicorn", "src.infrastructure.main:app", "--host", "0.0.0.0", "--port", "8000"]