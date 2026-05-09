import os
from io import BytesIO

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import text
from utils.db import engine

from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter


# =========================
# CONFIGURACIÓN INICIAL
# =========================
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

st.set_page_config(page_title="Panel Admin", layout="wide")
st.title("🔐 Panel Administrador")

password = st.text_input("Ingrese contraseña admin", type="password")

if password != ADMIN_PASSWORD:
    st.warning("⚠️ Ingrese contraseña admin")
    st.stop()

st.success("✅ Acceso autorizado")

tab_formacion, tab_empleados, tab_asistencias = st.tabs(
    [
        "📚 Crear Formación",
        "👥 Gestión Empleados",
        "📋 Asistencias y Reportes"
    ]
)


# =========================
# TAB 1: CREAR FORMACIÓN
# =========================
with tab_formacion:
    st.subheader("📚 Crear Formación")

    col1, col2 = st.columns(2)

    with col1:
        nombre_formacion = st.text_input("Nombre de la capacitación")

    with col2:
        fecha = st.date_input("Fecha asistencia")

    formador = st.text_input("Formador", value="Eduardo Florez")

    if st.button("Crear formación", use_container_width=True):
        if not nombre_formacion:
            st.warning("⚠️ Debe ingresar el nombre de la capacitación")
        else:
            try:
                with engine.begin() as conn:
                    resultado = conn.execute(
                        text("""
                            INSERT INTO formaciones (
                                nombre_formacion,
                                fecha_asistencia,
                                formador
                            )
                            VALUES (
                                :nombre_formacion,
                                :fecha_asistencia,
                                :formador
                            )
                            RETURNING id
                        """),
                        {
                            "nombre_formacion": nombre_formacion.strip(),
                            "fecha_asistencia": fecha,
                            "formador": formador.strip()
                        }
                    )
                    id_formacion = resultado.fetchone()[0]

                url = f"http://localhost:8501/Asistencia?formacion={id_formacion}"

                st.success("✅ Formación creada correctamente")
                st.info(f"🔗 URL formación:\n\n{url}")

            except Exception as e:
                st.error(f"❌ Error al crear formación: {e}")


# =========================
# TAB 2: GESTIÓN EMPLEADOS
# =========================
with tab_empleados:
    st.subheader("👥 Gestión de Empleados")

    subtab_agregar, subtab_consultar = st.tabs(
        [
            "➕ Agregar empleado",
            "🔎 Consultar empleados"
        ]
    )

    with subtab_agregar:
        st.markdown("### ➕ Agregar empleado")

        col1, col2 = st.columns(2)

        with col1:
            cedula_emp = st.text_input("Cédula empleado")
            nombre_emp = st.text_input("Nombre completo")

        with col2:
            cargo_emp = st.text_input("Cargo")
            zona_emp = st.text_input("Zona", value="Metropolitano")

        proyecto_emp = st.text_input(
            "Proyecto",
            value="CONEXIÓN Y VINCULACIÓN METROPOLITANO"
        )

        if st.button("Guardar empleado", use_container_width=True):
            if not cedula_emp or not nombre_emp or not cargo_emp:
                st.warning("⚠️ Cédula, nombre y cargo son obligatorios.")
            else:
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO empleados (
                                    cedula,
                                    nombre_completo,
                                    cargo,
                                    proyecto,
                                    zona,
                                    estado
                                )
                                VALUES (
                                    :cedula,
                                    :nombre_completo,
                                    :cargo,
                                    :proyecto,
                                    :zona,
                                    'ACTIVO'
                                )
                            """),
                            {
                                "cedula": cedula_emp.strip(),
                                "nombre_completo": nombre_emp.strip(),
                                "cargo": cargo_emp.strip(),
                                "proyecto": proyecto_emp.strip(),
                                "zona": zona_emp.strip()
                            }
                        )

                    st.success("✅ Empleado guardado correctamente.")

                except Exception as e:
                    if "duplicate" in str(e).lower() or "unique" in str(e).lower():
                        st.warning("⚠️ Esta cédula ya existe.")
                    else:
                        st.error(f"❌ Error al guardar empleado: {e}")

    with subtab_consultar:
        st.markdown("### 🔎 Consultar empleados")

        buscar = st.text_input("Buscar por cédula, nombre, cargo, proyecto o zona")

        with engine.begin() as conn:
            df_empleados = pd.read_sql(
                text("""
                    SELECT
                        cedula,
                        nombre_completo,
                        cargo,
                        proyecto,
                        zona,
                        estado,
                        fecha_creacion
                    FROM empleados
                    WHERE
                        :buscar = ''
                        OR cedula ILIKE :patron
                        OR nombre_completo ILIKE :patron
                        OR cargo ILIKE :patron
                        OR proyecto ILIKE :patron
                        OR zona ILIKE :patron
                    ORDER BY nombre_completo
                """),
                conn,
                params={
                    "buscar": buscar.strip(),
                    "patron": f"%{buscar.strip()}%"
                }
            )

        if df_empleados.empty:
            st.info("ℹ️ No hay empleados para mostrar.")
        else:
            st.success(f"✅ Total empleados encontrados: {len(df_empleados)}")
            st.dataframe(df_empleados, use_container_width=True)


# =========================
# TAB 3: ASISTENCIAS Y REPORTES
# =========================
with tab_asistencias:
    st.subheader("📋 Consultar Asistencias y Descargar Reporte")

    with engine.begin() as conn:
        df_formaciones = pd.read_sql(
            text("""
                SELECT id, nombre_formacion, fecha_asistencia, formador
                FROM formaciones
                ORDER BY id DESC
            """),
            conn
        )

    if df_formaciones.empty:
        st.info("ℹ️ No hay formaciones creadas todavía")
        st.stop()

    opciones = {
        f"{row.id} - {row.nombre_formacion} - {row.fecha_asistencia}": row.id
        for row in df_formaciones.itertuples()
    }

    seleccion = st.selectbox("Seleccione una formación", list(opciones.keys()))
    id_seleccionado = opciones[seleccion]

    with engine.begin() as conn:
        df_asistencias = pd.read_sql(
            text("""
                SELECT
                    f.nombre_formacion,
                    f.fecha_asistencia,
                    a.cedula,
                    a.nombre_completo,
                    a.cargo,
                    a.proyecto,
                    a.zona,
                    a.formador,
                    a.clasificacion_formacion,
                    a.tipo_formacion,
                    a.autoriza_datos,
                    a.fecha_registro
                FROM asistencias a
                INNER JOIN formaciones f
                    ON a.id_formacion = f.id
                WHERE a.id_formacion = :id_formacion
                ORDER BY a.fecha_registro DESC
            """),
            conn,
            params={"id_formacion": id_seleccionado}
        )

    if df_asistencias.empty:
        st.info("ℹ️ Esta formación aún no tiene asistencias registradas")
    else:
        st.success(f"✅ Total asistentes: {len(df_asistencias)}")

        st.dataframe(
            df_asistencias,
            use_container_width=True
        )

        buffer = BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_asistencias.to_excel(
                writer,
                index=False,
                sheet_name="Asistencias"
            )

        buffer.seek(0)

        wb = load_workbook(buffer)
        ws = wb["Asistencias"]

        # Congelar fila de encabezados
        ws.freeze_panes = "A2"

        # Crear tabla estructurada
        ultima_fila = ws.max_row
        ultima_columna = ws.max_column
        rango_tabla = f"A1:{get_column_letter(ultima_columna)}{ultima_fila}"

        tabla = Table(
            displayName="TablaAsistencias",
            ref=rango_tabla
        )

        estilo = TableStyleInfo(
            name="TableStyleMedium2",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False
        )

        tabla.tableStyleInfo = estilo
        ws.add_table(tabla)

        # Formato encabezados
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Alinear celdas
        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(vertical="center")

        # Autoajustar columnas
        for columna in ws.columns:
            max_length = 0
            letra_columna = get_column_letter(columna[0].column)

            for cell in columna:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            ws.column_dimensions[letra_columna].width = max_length + 3

        # Alto encabezado
        ws.row_dimensions[1].height = 24

        salida = BytesIO()
        wb.save(salida)
        salida.seek(0)

        st.download_button(
            label="📥 Descargar Excel",
            data=salida,
            file_name=f"asistencia_formacion_{id_seleccionado}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )