import psycopg2
import csv
import os
import logging
from contextlib import contextmanager
from src.config import DB_CONFIG

logger = logging.getLogger(__name__)


def ensure_database_exists():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG['database'],)
        )
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            logger.info(f"Database '{DB_CONFIG['database']}' has been created!")
        
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        logger.error(f"Error creating database: {e}")
        raise


def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


@contextmanager
def get_cursor(commit=True):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def initialize_database():
    ensure_database_exists()
    
    with get_cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                brand VARCHAR(100) NOT NULL,
                processor VARCHAR(255) NOT NULL,
                ram_gb INTEGER NOT NULL,
                storage_gb INTEGER NOT NULL,
                storage_type VARCHAR(50) NOT NULL,
                gpu VARCHAR(255) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock_quantity INTEGER NOT NULL,
                customer_rating DECIMAL(3, 2) NOT NULL,
                category VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        
        if count == 0:
            _load_products_from_csv(cursor)
        
        logger.info(f"Database initialized. {count} products in database")


def _load_products_from_csv(cursor):
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'products.csv')
    
    if not os.path.exists(csv_path):
        logger.warning(f"CSV file not found at {csv_path}")
        return
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products = []
        
        for row in reader:
            products.append((
                row['name'], row['brand'], row['processor'],
                int(row['ram_gb']), int(row['storage_gb']), row['storage_type'],
                row['gpu'], float(row['price']), int(row['stock_quantity']),
                float(row['customer_rating']), row['category']
            ))
    
    cursor.executemany('''
        INSERT INTO products (name, brand, processor, ram_gb, storage_gb, storage_type, 
                            gpu, price, stock_quantity, customer_rating, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', products)
    
    logger.info(f"Inserted {len(products)} products from CSV")
