import boto3
import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def lambda_handler(event, context):
    # Configuración de conexión a MySQL
    mysql_config = {
        'host': 'miservidor.cv8kk8aog4k1.us-east-1.rds.amazonaws.com',
        'user': 'admin',
        'password': '12345678',
        'database': 'sakila'
    }

    # Conexión a MySQL
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    try:
        # Obtener datos de clientes y películas
        cursor.execute("SELECT customer_id FROM customer")
        customers = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT film_id FROM film")
        films = [row[0] for row in cursor.fetchall()]

        # Obtener las frecuencias de renta de clientes y películas
        cursor.execute("SELECT customer_id, COUNT(*) AS rental_count FROM rental GROUP BY customer_id")
        customer_rental_counts = cursor.fetchall()
        customer_ids, customer_weights = zip(*customer_rental_counts)
        customer_weights = np.array(customer_weights) / sum(customer_weights)

        cursor.execute("SELECT film_id, COUNT(*) AS rental_count FROM rental GROUP BY film_id")
        film_rental_counts = cursor.fetchall()
        film_ids, film_weights = zip(*film_rental_counts)
        film_weights = np.array(film_weights) / sum(film_weights)

        # Simular las rentas
        new_rentals = []
        for _ in range(100):
            customer_id = np.random.choice(customer_ids, p=customer_weights)
            film_id = np.random.choice(film_ids, p=film_weights)
            rental_date = datetime.now()
            return_date = rental_date + timedelta(days=random.randint(1, 7))

            new_rentals.append((customer_id, film_id, rental_date, return_date))

        # Insertar las nuevas rentas en la base de datos
        insert_query = """
            INSERT INTO rental (customer_id, inventory_id, rental_date, return_date, staff_id, last_update)
            VALUES (%s, 
                    (SELECT inventory_id FROM inventory WHERE film_id = %s ORDER BY RAND() LIMIT 1), 
                    %s, 
                    %s, 
                    1, 
                    NOW())
        """
        cursor.executemany(insert_query, new_rentals)
        conn.commit()

        # Log de confirmación
        print(f"Inserted {len(new_rentals)} new rentals successfully.")

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Cerrar la conexión a MySQL
        cursor.close()
        conn.close()

    return {
        'statusCode': 200,
        'body': 'New rentals simulated successfully'
    }
