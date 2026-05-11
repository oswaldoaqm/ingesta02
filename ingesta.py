import boto3
import mysql.connector
import csv
import os

# ── Configuración MySQL ──────────────────────────────────────────────────────
DB_HOST     = os.environ.get("DB_HOST",     "localhost")
DB_PORT     = int(os.environ.get("DB_PORT", "3306"))
DB_USER     = os.environ.get("DB_USER",     "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_NAME     = os.environ.get("DB_NAME",     "mi_base_de_datos")
DB_TABLE    = os.environ.get("DB_TABLE",    "mi_tabla")

# ── Configuración S3 ─────────────────────────────────────────────────────────
NOMBRE_BUCKET = os.environ.get("S3_BUCKET", "nombreBucket")   # <-- reemplaza si no usas variable de entorno
NOMBRE_ARCHIVO_CSV  = "data.csv"
S3_KEY              = NOMBRE_ARCHIVO_CSV   # ruta dentro del bucket


def leer_mysql_y_guardar_csv(archivo_csv: str) -> None:
    """Conecta a MySQL, lee todos los registros de la tabla y los guarda en CSV."""
    print(f"Conectando a MySQL en {DB_HOST}:{DB_PORT}, base: {DB_NAME}, tabla: {DB_TABLE}...")

    conexion = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    cursor = conexion.cursor()

    cursor.execute(f"SELECT * FROM {DB_TABLE};")
    columnas = [desc[0] for desc in cursor.description]
    filas    = cursor.fetchall()

    cursor.close()
    conexion.close()

    print(f"Registros leídos: {len(filas)}")

    with open(archivo_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columnas)   # cabecera
        writer.writerows(filas)

    print(f"Archivo CSV generado: {archivo_csv}")


def subir_a_s3(archivo_local: str, bucket: str, clave_s3: str) -> None:
    """Sube el archivo CSV al bucket S3 indicado."""
    print(f"Subiendo '{archivo_local}' al bucket '{bucket}' como '{clave_s3}'...")
    cliente_s3 = boto3.client("s3")
    cliente_s3.upload_file(archivo_local, bucket, clave_s3)
    print("Ingesta completada")


if __name__ == "__main__":
    leer_mysql_y_guardar_csv(NOMBRE_ARCHIVO_CSV)
    subir_a_s3(NOMBRE_ARCHIVO_CSV, NOMBRE_BUCKET, S3_KEY)
