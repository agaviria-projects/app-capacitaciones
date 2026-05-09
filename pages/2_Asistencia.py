import streamlit as st
from sqlalchemy import text
from utils.db import engine

st.set_page_config(
    page_title="Registro Asistencia",
    page_icon="📋",
    layout="centered"
)

st.title("📋 Registro de Asistencia")

# Obtener id de formación desde la URL
params = st.query_params
id_formacion = params.get("formacion")

if not id_formacion:
    st.error("❌ No se recibió el ID de la formación.")
    st.info("Ingrese desde el enlace generado por el formador.")
    st.stop()

# Consultar formación
with engine.begin() as conn:
    formacion = conn.execute(
        text("""
            SELECT id, nombre_formacion, fecha_asistencia, formador
            FROM formaciones
            WHERE id = :id
        """),
        {"id": int(id_formacion)}
    ).fetchone()

if not formacion:
    st.error("❌ Formación no encontrada.")
    st.stop()

id_formacion = formacion[0]
nombre_formacion = formacion[1]
fecha_asistencia = formacion[2]
formador = formacion[3]

st.markdown(f"### 📚 {nombre_formacion}")
st.write(f"📅 Fecha: **{fecha_asistencia}**")
st.write(f"👨‍🏫 Formador: **{formador}**")
st.divider()

cedula = st.text_input("Digite su cédula")

empleado = None

if cedula:
    with engine.begin() as conn:
        empleado = conn.execute(
            text("""
                SELECT nombre_completo, cargo, proyecto, zona
                FROM empleados
                WHERE cedula = :cedula
                AND estado = 'ACTIVO'
            """),
            {"cedula": cedula.strip()}
        ).fetchone()

    if empleado:
        nombre_completo = empleado[0]
        cargo = empleado[1]
        proyecto = empleado[2]
        zona = empleado[3]

        st.success("✅ Empleado encontrado")

        st.text_input("Nombre completo", value=nombre_completo, disabled=True)
        st.text_input("Cargo", value=cargo, disabled=True)
        st.text_input("Proyecto", value=proyecto, disabled=True)
        st.text_input("Zona", value=zona or "", disabled=True)

    else:
        st.error("❌ Cédula no encontrada. Verifique el número ingresado.")

clasificacion = st.radio(
    "Clasificación de formación",
    ["Charla", "Capacitación"]
)

tipo_formacion = st.radio(
    "Tipo de formación",
    ["Interna", "Externa"]
)

autoriza_datos = st.radio(
    "¿Autoriza el tratamiento de datos personales?",
    ["Sí", "No"]
)

if st.button("Enviar asistencia", use_container_width=True):

    if not cedula:
        st.warning("⚠️ Debe ingresar la cédula.")

    elif not empleado:
        st.error("❌ No se puede registrar. La cédula no existe o está inactiva.")

    elif autoriza_datos == "No":
        st.error("❌ Para registrar la asistencia debe autorizar el tratamiento de datos.")

    else:
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO asistencias (
                            id_formacion,
                            cedula,
                            nombre_completo,
                            cargo,
                            proyecto,
                            zona,
                            formador,
                            clasificacion_formacion,
                            tipo_formacion,
                            autoriza_datos
                        )
                        VALUES (
                            :id_formacion,
                            :cedula,
                            :nombre_completo,
                            :cargo,
                            :proyecto,
                            :zona,
                            :formador,
                            :clasificacion_formacion,
                            :tipo_formacion,
                            :autoriza_datos
                        )
                    """),
                    {
                        "id_formacion": id_formacion,
                        "cedula": cedula.strip(),
                        "nombre_completo": nombre_completo,
                        "cargo": cargo,
                        "proyecto": proyecto,
                        "zona": zona,
                        "formador": formador,
                        "clasificacion_formacion": clasificacion,
                        "tipo_formacion": tipo_formacion,
                        "autoriza_datos": autoriza_datos
                    }
                )

            st.success("✅ Asistencia registrada correctamente.")

        except Exception as e:
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                st.warning("⚠️ Esta cédula ya registró asistencia para esta formación.")
            else:
                st.error(f"❌ Error al registrar asistencia: {e}")