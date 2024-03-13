import boto3
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

def extract_data(html_content):
    """
    Función para extraer el precio, metraje, 
    número de habitaciones y características 
    adicionales de las páginas HTML.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    #print("HTML:     ",soup)
    properties = soup.find_all('div', class_='listing-card__information')
    #print("PROPERTIES: ",properties)
    data = []
    
    
    
    for prop in properties:
        
        price = prop.find('div', class_='price').text.strip()
        area_div = prop.find('div', class_='card-icon card-icon__area')
        area_span = None
        if area_div:
            area_span = area_div.find_next('span')
        area = area_span.text.strip() if area_span else "No disponible"
        bedrooms_element = prop.find('span', attrs={'data-test': 'bedrooms'})
         
        if bedrooms_element:
          bedrooms = bedrooms_element.text.strip()
        else:
          bedrooms = 'No disponible'
        adicional = prop.find('span', class_='facility-item__text')
        adicional_text = adicional.text.strip() if adicional else 'No disponible'
        
        data.append([price, area, bedrooms, adicional_text])
        #print(data)
    
    
    return data

def handler(event, context):
    """
    Función para procesar los datos descargados 
    y guardarlos en un archivo CSV en AWS S3.
    """
    s3 = boto3.client('s3')
    bucket_name = 'buckets-raws'

    # Obtener la fecha actual
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Obtener la lista de objetos en el bucket
    response = s3.list_objects(Bucket=bucket_name)
    all_data = []

    #for obj in response.get('Contents', []):
    if 'Contents' in response:
        for obj in response['Contents']:
        # Obtener el contenido de cada objeto
            response_obj = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
            html_content = response_obj['Body'].read()
    
            # Extraer los datos de la página HTML y agregarlos a la lista
            data = extract_data(html_content)
            all_data.extend(data)

    # Crear un DataFrame pandas con todos los datos recolectados
    df = pd.DataFrame(all_data, columns=['Price', 'Area', 'Bedrooms', 'Adicional'])
    
    df['Price'] = pd.to_numeric(df['Price'].str.replace('[$,.]', '', regex=True)
    , errors='coerce')  
    df['Price'] = df['Price'].astype('Int64')  # Convertir a tipo Int64
    
    df['Bedrooms'] = pd.to_numeric(df['Bedrooms'].str.split(' ').str[0], errors='coerce')  
    
    df['Area'] = df['Area'].str.extract(r'(\d+)').astype(float) 
    #df['Area'] = df['Area'].apply(lambda x: '{:.0f} m²'.format(x))  # Agregar el sufijo 'm²'
    
    


    # Guardar el DataFrame como archivo CSV en S3
    csv_key = f'casas/year={current_date[:4]}/month={current_date[5:7]}/day={current_date[8:]}/{current_date}.csv'
    csv_buffer = df.to_csv(index=False)
    s3.put_object(Body=csv_buffer, Bucket='buckets-final', Key=csv_key)

    return {
        'statusCode': 200,
        'body': 'Datos procesados y guardados en S3 correctamente.'
    }
    

handler(None, None)


