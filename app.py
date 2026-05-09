import streamlit as st
from utils.db import probar_conexion

st.set_page_config(
    page_title="App Capacitaciones",
    page_icon="📋",
    layout="centered"
)

st.title("📋 Sistema de Capacitaciones")

st.markdown("""
Bienvenido al sistema de gestión de capacitaciones.

Utiliza el menú lateral para navegar.
""")