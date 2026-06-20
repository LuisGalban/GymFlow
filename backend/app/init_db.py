import sys
import os

# Aseguramos que la raíz del backend esté en el sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.database import engine, Base
from app import models  # Cargar los modelos dentro del namespace 'app'

def initialize_database():
    try:
        print("Conectando a PostgreSQL y creando tablas...")
        Base.metadata.create_all(bind=engine)
        print(">>> ¡Base de datos e infraestructura de tablas inicializadas con éxito en PostgreSQL! <<<")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    initialize_database()
