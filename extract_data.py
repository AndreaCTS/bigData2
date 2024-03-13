import boto3
from bs4 import BeautifulSoup
from datetime import datetime
import csv
from io import StringIO

s3 = boto3.client('s3')

def handler(event, context):
    # Obtener la fecha actual
    current_date = datetime.now()
    year = current_date.strftime('%Y')
    month = current_date.strftime('%m')
    day = current_date.strftime('%d')

    # Definir la ruta del archivo CSV
    csv_key = f'casas/year={year}/month={month}/day={day}/{current_date}.csv'

    # Inicializar el CSV
    csv_data = [['Precio', 'Metraje', 'Habitaciones', 'Características']]

    # Iterar sobre los archivos en el bucket-raw
    bucket_name = 'buckets-raws'

    # Obtener el objeto que desencadenó el evento
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        obj_key = record['s3']['object']['key']

        # Descargar el archivo HTML
        obj_data = s3.get_object(Bucket=bucket_name, Key=obj_key)
        html_content = obj_data['Body'].read()

        # Procesar el HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extraer datos de la página
        precio = soup.find('span', class_='precio').text
        metraje = soup.find('span', class_='metraje').text
        habitaciones = soup.find('span', class_='habitaciones').text
        caracteristicas = soup.find('div', class_='caracteristicas').text.strip()

        # Agregar los datos al CSV
        csv_data.append([precio, metraje, habitaciones, caracteristicas])

    # Guardar el CSV en S3
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerows(csv_data)

    s3.put_object(Body=csv_buffer.getvalue(), Bucket='buckets-final', Key=csv_key)

    return {
        'statusCode': 200,
        'body': 'Datos procesados y guardados en S3 correctamente.'
    }