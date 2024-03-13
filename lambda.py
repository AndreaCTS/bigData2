import requests
import boto3
from datetime import datetime


def f(event, context):
    s3 = boto3.client('s3')
    bucket_name = 'buckets-raws'

    for page_number in range(1, 6):
        if page_number == 1:
            url = (
                'https://casas.mitula.com.co/searchRE/'
                'nivel1-Cundinamarca/nivel2-Bogot%C3%A1/'
                'orden-0/q-bogot%C3%A1?req_sgmt=REVTS1RPUDtVU0VSX1NFQVJDSDtTRVJQOw==')
        else:
            url = ('https://casas.mitula.com.co/searchRE/'
                   'nivel1-Cundinamarca/nivel2-Bogot%C3%A1/'
                   f'orden-0/q-bogot%C3%A1/pag-{page_number}?'
                   'req_sgmt=REVTS1RPUDtVU0VSX1NFQVJDSDtTRVJQOw==')
        response = requests.get(url)

        if response.status_code == 200:
            current_date = datetime.now().strftime('%Y-%m-%d')
            file_key = f'casas/contenido-pag-{page_number}-{current_date}.html'
            s3.put_object(
                Body=response.content,
                Bucket=bucket_name,
                Key=file_key)

    return {
        'statusCode': 200,
        'body': 'Páginas descargadas y guardadas en S3 correctamente.'
    }
