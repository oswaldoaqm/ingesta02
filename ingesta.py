import os
import csv
import mysql.connector
import boto3
from botocore.exceptions import NoCredentialsError

# ── 1. Configuración mediante Variables de Entorno ────────────────────────────
# Esto evita tener contraseñas "quemadas" (hardcodeadas) en el código.
DB_HOST    = os.getenv('DB_HOST',    'localhost')
DB_USER    = os.getenv('DB_USER',    'root')
DB_PASS    = os.getenv('DB_PASS',    'password')
DB_NAME    = os.getenv('DB_NAME',    'mi_base_de_datos')
TABLE_NAME = os.getenv('TABLE_NAME', 'mi_tabla')

# Credenciales de AWS
AWS_ACCESS_KEY    = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY    = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')   # Necesario en AWS Academy
S3_BUCKET         = os.getenv('S3_BUCKET', 'nombre-de-tu-bucket')

CSV_FILENAME = 'datos_exportados.csv'


def extraer_mysql_a_csv():
    print(f"Conectando a MySQL en {DB_HOST}...")
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        cursor = conexion.cursor()

        # Ejecutar la consulta
        print(f"Extrayendo registros de la tabla '{TABLE_NAME}'...")
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        resultados = cursor.fetchall()

        # Obtener los nombres de las columnas para la cabecera del CSV
        nombres_columnas = [i[0] for i in cursor.description]

        # Guardar en CSV
        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as archivo_csv:
            writer = csv.writer(archivo_csv)
            writer.writerow(nombres_columnas)   # Escribimos la cabecera
            writer.writerows(resultados)        # Escribimos las filas

        print(f"Datos guardados exitosamente en {CSV_FILENAME}")

        cursor.close()
        conexion.close()

    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        raise


def subir_a_s3():
    print(f"Subiendo {CSV_FILENAME} a S3 (Bucket: {S3_BUCKET})...")
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        aws_session_token=AWS_SESSION_TOKEN
    )

    try:
        s3.upload_file(CSV_FILENAME, S3_BUCKET, CSV_FILENAME)
        print("¡Subida a S3 completada con éxito!")
    except FileNotFoundError:
        print("El archivo CSV no se encontró localmente.")
    except NoCredentialsError:
        print("Error: Credenciales de AWS no disponibles o inválidas.")


if __name__ == "__main__":
    extraer_mysql_a_csv()
    subir_a_s3()
