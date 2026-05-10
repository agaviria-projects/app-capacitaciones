import streamlit as st
from sqlalchemy import text
from utils.db import get_connection

st.set_page_config(
    page_title="Registro Asistencia",
    page_icon="📋",
    layout="centered"
)

st.markdown("""
<style>

html, body, [class*="css"] {
    overflow-x: hidden !important;
}
            
/* =========================================================
   OCULTAR ELEMENTOS NATIVOS STREAMLIT
========================================================= */

#MainMenu,
footer,
header,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

/* =========================================================
   SIDEBAR
========================================================= */

section[data-testid="stSidebar"] {
    display: none !important;
}

/* =========================================================
   BADGES STREAMLIT CLOUD
========================================================= */

a[href*="streamlit.io"],
a[href*="github.com"],
div[class*="viewerBadge"],
div[class*="statusWidget"],
div[class*="deployButton"],
div[class*="stToolbar"],
div[class*="stDecoration"] {

    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;

    pointer-events: none !important;

    height: 0 !important;
    width: 0 !important;
}

/* =========================================================
   CONTENEDOR PRINCIPAL
========================================================= */

.block-container {

    max-width: 680px !important;

    padding-top: 2rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;

    /* 🔥 ESPACIO INFERIOR */
    padding-bottom: 170px !important;

    margin: auto !important;
}

/* =========================================================
   TÍTULOS
========================================================= */

.titulo-principal {

    text-align: center;

    font-size: 27px;
    font-weight: 800;

    line-height: 1.15;

    margin-bottom: 24px;

    color: #1e293b !important;
}

.titulo-formacion {

    text-align: center;

    font-size: 22px;
    font-weight: 800;

    line-height: 1.2;

    margin-bottom: 8px;

    color: #1e293b !important;
}

.info-formacion {

    text-align: center;

    font-size: 14px;

    margin-bottom: 8px;

    color: #1e293b !important;
}

/* =========================================================
   MÁS ESPACIO PARA BOTÓN
========================================================= */

.stButton {

    margin-top: 20px !important;
    margin-bottom: 40px !important;

    position: relative !important;

    z-index: 99999999 !important;
}

/* =========================================================
   TRAMPA VISUAL BADGE
========================================================= */

.badge-cover {

    position: fixed !important;

    left: 0 !important;
    bottom: 0 !important;

    width: 100vw !important;
    height: 90px !important;

    background: #0e1117 !important;

    z-index: 999999999 !important;

    pointer-events: none !important;

    border-top: 1px solid #111827;
}

/* =========================================================
   MODO MÓVIL
========================================================= */

@media (max-width: 600px) {

    .block-container {

        max-width: 100% !important;

        padding-top: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;

        /* 🔥 MÁS ESPACIO EN CELULAR */
        padding-bottom: 220px !important;
    }

    .titulo-principal {

        font-size: 27px !important;
        color: #ffffff !important;
    }

    .titulo-formacion {

        font-size: 22px !important;
        color: #ffffff !important;
    }

    .info-formacion {

        font-size: 14px !important;
        color: #ffffff !important;
    }

    .badge-cover {

        width: 100vw !important;

        height: 110px !important;

        background: #0e1117 !important;
    }

    .stButton {

        margin-bottom: 60px !important;
    }
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="badge-cover"></div>', unsafe_allow_html=True) 
# =========================================
# 🔗 OBTENER ID FORMACIÓN DESDE URL
# =========================================

params = st.query_params
id_formacion = params.get("formacion")

if not id_formacion:
    st.error("❌ No se recibió el ID de la formación.")
    st.info("Ingrese desde el enlace generado por el formador.")
    st.stop()

# =========================================
# 📚 CONSULTAR FORMACIÓN
# =========================================

try:

    with get_connection() as conn:

        formacion = conn.execute(
            text("""
                SELECT id, nombre_formacion, fecha_asistencia, formador
                FROM formaciones
                WHERE id = :id
            """),
            {"id": int(id_formacion)}
        ).fetchone()

except Exception:

    st.error("""
    ⚠️ No fue posible conectar con el sistema.

    Contacte al administrador.
    """)

    st.stop()

if not formacion:
    st.error("❌ Formación no encontrada.")
    st.stop()

id_formacion = formacion[0]
nombre_formacion = formacion[1]
fecha_asistencia = formacion[2]
formador = formacion[3]

st.markdown(
    '<div class="titulo-principal">📋 Registro de Asistencia</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="titulo-formacion">📚 {nombre_formacion}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="info-formacion">📅 Fecha: <b>{fecha_asistencia}</b></div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="info-formacion">👨‍🏫 Formador: <b>{formador}</b></div>',
    unsafe_allow_html=True
)

st.divider()

# =========================================
# 👤 CONSULTA EMPLEADO
# =========================================

cedula = st.text_input("Digite su cédula")

empleado = None

if cedula:

    try:

        with get_connection() as conn:

            empleado = conn.execute(
                text("""
                    SELECT nombre_completo, cargo, proyecto, zona
                    FROM empleados
                    WHERE cedula = :cedula
                    AND estado = 'ACTIVO'
                """),
                {"cedula": cedula.strip()}
            ).fetchone()

    except Exception:

        st.error("""
        ⚠️ No fue posible consultar la información.

        Contacte al administrador.
        """)

        st.stop()

    if empleado:

        nombre_completo = empleado[0]
        cargo = empleado[1]
        proyecto = empleado[2]
        zona = empleado[3]

        st.success("✅ Empleado encontrado")

        st.text_input(
            "Nombre completo",
            value=nombre_completo,
            disabled=True
        )

        st.text_input(
            "Cargo",
            value=cargo,
            disabled=True
        )

        st.text_input(
            "Proyecto",
            value=proyecto,
            disabled=True
        )

        st.text_input(
            "Zona",
            value=zona or "",
            disabled=True
        )

    else:

        st.error(
            "❌ Cédula no encontrada. Verifique el número ingresado."
        )

# =========================================
# 📋 FORMULARIO
# =========================================

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

# =========================================
# 💾 REGISTRAR ASISTENCIA
# =========================================

if st.button("Enviar asistencia", use_container_width=True):

    if not cedula:

        st.warning("⚠️ Debe ingresar la cédula.")

    elif not empleado:

        st.error("""
        ❌ No se puede registrar.

        La cédula no existe o está inactiva.
        """)

    elif autoriza_datos == "No":

        st.error("""
        ❌ Para registrar la asistencia debe autorizar
        el tratamiento de datos.
        """)

    else:

        try:

            with get_connection() as conn:

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

            st.success(
                "✅ Asistencia registrada correctamente."
            )

        except Exception as e:

            if (
                "unique" in str(e).lower()
                or
                "duplicate" in str(e).lower()
            ):

                st.warning("""
                ⚠️ Esta cédula ya registró asistencia
                para esta formación.
                """)

            else:

                st.error("""
                ⚠️ No fue posible registrar la asistencia.

                Contacte al administrador.
                """)

        st.markdown("<br><br><br><br>", unsafe_allow_html=True)