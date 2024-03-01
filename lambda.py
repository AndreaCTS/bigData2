import boto3
import urllib.request
from datetime import datetime
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    # Obtén la fecha actual
    now = datetime.now()
    date_string = now.strftime("%Y-%m-%d")
    
    url = 'https://www.eltiempo.com/'
    
    try:
        # Descargar la página del tiempo
        response = urllib.request.urlopen(url)
        data = response.read()

        # Subir el archivo a S3
        s3.put_object(Body=data, Bucket='zappa-hvwbzmvlm', Key=f'{date_string}.html')
        
        return {
            'statusCode': 200,
            'body': f'Archivo {date_string}.html subido exitosamente a S3'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error al procesar la solicitud: {str(e)}'
        }