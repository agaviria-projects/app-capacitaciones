import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ No se encontró DATABASE_URL en el archivo .env")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)


def get_connection():
    """
    Retorna una conexión activa a Supabase/PostgreSQL.
    """
    return engine.connect()


def probar_conexion():
    """
    Prueba rápida para validar conexión con la base de datos.
    """
    try:
        with get_connection() as conn:
            resultado = conn.execute(text("SELECT 1 AS prueba"))
            return resultado.fetchone()[0] == 1
    except SQLAlchemyError as e:
        print(f"Error de conexión: {e}")
        return False