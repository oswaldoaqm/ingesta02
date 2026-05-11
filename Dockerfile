FROM python:3-slim

WORKDIR /programas/ingesta

# Instalar dependencias
RUN pip3 install boto3 mysql-connector-python

# Copiar código fuente
COPY . .

# Ejecutar el script al iniciar el contenedor
CMD ["python3", "./ingesta.py"]
