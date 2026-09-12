import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.init_db import initialize_database
from app.database import SessionLocal
from app.models import Usuario


def bootstrap():
    print("GymFlow bootstrap: inicializando tablas...")
    initialize_database()

    db = SessionLocal()
    try:
        existe_usuario = db.query(Usuario).first() is not None
    finally:
        db.close()

    if existe_usuario:
        print("GymFlow bootstrap: base de datos ya sembrada, omitiendo seed.")
        return

    print("GymFlow bootstrap: base de datos vacía, sembrando datos de demo...")
    from app.seed import seed_database

    seed_database()


if __name__ == "__main__":
    bootstrap()