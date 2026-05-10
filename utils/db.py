import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# =========================================
# 🔥 LEER DATABASE_URL DESDE STREAMLIT SECRETS
# =========================================

DATABASE_URL = st.secrets["DATABASE_URL"]

# =========================================
# 🔥 ENGINE SQLALCHEMY
# =========================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)


# =========================================
# 🔌 OBTENER CONEXIÓN
# =========================================

def get_connection():
    """
    Retorna una conexión activa PostgreSQL/Supabase.
    """
    return engine.connect()


# =========================================
# 🧪 PRUEBA DE CONEXIÓN
# =========================================

def probar_conexion():

    try:

        with get_connection() as conn:

            resultado = conn.execute(
                text("SELECT 1 AS prueba")
            )

            return resultado.fetchone()[0] == 1

    except SQLAlchemyError:

        return False