import base64
from pathlib import Path
import json

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(
    page_title="Santuario Río Cruces",
    page_icon="🦢",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"

# ============================================================
# AYUDAS GENERALES
# ============================================================
def existe_archivo(ruta):
    return Path(ruta).exists()


def leer_base64(ruta):
    ruta = Path(ruta)
    if not ruta.exists():
        return None
    return base64.b64encode(ruta.read_bytes()).decode()


def cargar_csv_seguro(ruta):
    try:
        ruta = Path(ruta)
        if not ruta.exists():
            return pd.DataFrame()
        return pd.read_csv(ruta)
    except Exception as e:
        st.error(f"Error al leer {ruta.name}: {e}")
        return pd.DataFrame()


def valor_fila(fila, posibles, default=""):
    for col in posibles:
        if col in fila and pd.notna(fila[col]):
            return str(fila[col]).strip()
    return default


def ir_a(seccion):
    st.session_state["seccion"] = seccion
    st.rerun()


# ============================================================
# ESTILO VISUAL
# ============================================================
def aplicar_estilo():
    fondo = leer_base64(ASSETS / "portada_humedal.jpg")

    css = """
    <style>
    html, body, [class*="css"] {
        font-family: "Segoe UI", sans-serif;
    }

    .stApp {
        color: #f4f7f4;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(5,58,44,0.96) 0%, rgba(3,34,27,0.97) 100%);
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    [data-testid="stSidebar"] * {
        color: #f5fbf7 !important;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        background: transparent !important;
    }

    .capa-principal {
        background: transparent !important;
        padding: 0.2rem 0.1rem 1.2rem 0.1rem;
    }

    .franja-superior {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 0.8rem 1rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
    }

    .logo-box {
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 0.5rem;
        text-align: center;
        height: 100%;
    }

    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 24px;
        min-height: 370px;
        display: flex;
        align-items: center;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 28px rgba(0,0,0,0.22);
        border: 1px solid rgba(255,255,255,0.12);
    }

    .hero-contenido {
        max-width: 780px;
        padding: 2.3rem 2.4rem;
        color: white;
    }

    .hero h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
        text-shadow: 0 4px 16px rgba(0,0,0,0.45);
    }

    .hero p {
        color: rgba(255,255,255,0.95);
        font-size: 1.08rem;
        line-height: 1.65;
        text-shadow: 0 2px 10px rgba(0,0,0,0.45);
    }

    .tarjeta {
        background: rgba(7, 49, 37, 0.60);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 1rem 1rem 1rem 1rem;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        margin-bottom: 1rem;
    }

    .tarjeta h3, .tarjeta h4 {
        color: #ffffff;
        margin-bottom: 0.35rem;
    }

    .tarjeta p, .tarjeta li, .tarjeta div {
        color: rgba(255,255,255,0.94);
    }

    .tarjeta-clara {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 18px;
        padding: 1rem;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        margin-bottom: 1rem;
    }

    .tarjeta-clara h3, .tarjeta-clara h4 {
        color: #ffffff;
    }

    .tarjeta-clara p, .tarjeta-clara li {
        color: rgba(255,255,255,0.94);
    }

    .subtitulo-suave {
        color: rgba(255,255,255,0.88);
        font-size: 0.98rem;
    }

    .stButton > button {
        background: #2d7d4d;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.6rem 1rem;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: #225f3a;
        color: white;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.10);
        padding: 0.9rem;
        border-radius: 15px;
    }

    .mini-etiqueta {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        margin-right: 0.35rem;
        font-size: 0.86rem;
    }

    .nota {
        color: rgba(255,255,255,0.80);
        font-size: 0.95rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.10);
        border-radius: 10px;
        color: white;
        padding: 10px 16px;
    }
    """

    if fondo:
        css += f"""
        .stApp {{
            background-image:
                linear-gradient(rgba(3,34,27,0.72), rgba(3,34,27,0.80)),
                url("data:image/jpeg;base64,{fondo}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .hero {{
            background-image:
                linear-gradient(90deg, rgba(5,32,25,0.85) 0%, rgba(5,32,25,0.56) 48%, rgba(5,32,25,0.18) 100%),
                url("data:image/jpeg;base64,{fondo}");
            background-size: cover;
            background-position: center;
        }}
        """
    css += "</style>"

    st.markdown(css, unsafe_allow_html=True)


# ============================================================
# DATOS
# ============================================================
def cargar_especies():
    df = cargar_csv_seguro(DATA / "especies.csv")
    if df.empty:
        return df

    # columnas mínimas flexibles
    columnas_finales = []
    for c in df.columns:
        columnas_finales.append(str(c).strip())
    df.columns = columnas_finales
    return df


def cargar_proyectos():
    df = cargar_csv_seguro(DATA / "proyectos.csv")
    if df.empty:
        return df
    columnas_finales = []
    for c in df.columns:
        columnas_finales.append(str(c).strip())
    df.columns = columnas_finales
    return df


# ============================================================
# MAPA
# ============================================================
def crear_mapa():
    centro = [-39.68, -73.19]
    m = folium.Map(location=centro, zoom_start=11, tiles="CartoDB positron")

    # límite / capas opcionales desde data
    geojsons = [
        ("cuenca_rio_cruces.geojson", "Cuenca Río Cruces", "#4ea3ff"),
        ("santuario_limite.geojson", "Límite del santuario", "#70d67f"),
        ("area_influencia.geojson", "Área de influencia", "#ffb347"),
    ]

    for archivo, nombre, color in geojsons:
        ruta = DATA / archivo
        if ruta.exists():
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    gj = json.load(f)
                folium.GeoJson(
                    gj,
                    name=nombre,
                    style_function=lambda x, color=color: {
                        "color": color,
                        "weight": 2,
                        "fillOpacity": 0.18,
                    },
                    tooltip=nombre,
                ).add_to(m)
            except Exception:
                pass

    # proyectos
    df = cargar_proyectos()
    if not df.empty:
        for _, fila in df.iterrows():
            lat = valor_fila(fila, ["lat", "latitude"], "")
            lon = valor_fila(fila, ["lon", "lng", "longitude"], "")
            if lat and lon:
                try:
                    lat = float(lat)
                    lon = float(lon)
                    nombre = valor_fila(fila, ["nombre", "proyecto"], "Proyecto")
                    descripcion = valor_fila(
                        fila,
                        ["descripcion", "detalle", "info"],
                        "Sin descripción disponible.",
                    )
                    folium.Marker(
                        [lat, lon],
                        tooltip=nombre,
                        popup=f"<b>{nombre}</b><br>{descripcion}",
                        icon=folium.Icon(color="green", icon="info-sign"),
                    ).add_to(m)
                except Exception:
                    continue

    folium.LayerControl(collapsed=True).add_to(m)
    return m


# ============================================================
# COMPONENTES
# ============================================================
def encabezado_logos():
    st.markdown('<div class="franja-superior">', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([1.1, 1.1, 1.1, 4])

    with col1:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        if existe_archivo(ASSETS / "logo_uach.png"):
            st.image(str(ASSETS / "logo_uach.png"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        if existe_archivo(ASSETS / "logo_escuela_geografia.png"):
            st.image(str(ASSETS / "logo_escuela_geografia.png"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        if existe_archivo(ASSETS / "logo_conaf.png"):
            st.image(str(ASSETS / "logo_conaf.png"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown(
            """
            <div style="padding-top:0.35rem;">
                <h3 style="margin-bottom:0.15rem; color:white;">Santuario Río Cruces</h3>
                <p class="subtitulo-suave" style="margin-top:0;">
                    Escuela de Geografía · Universidad Austral de Chile · CONAF · prototipo académico
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


def portada():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-contenido">
                <h1>Un humedal vivo, un territorio compartido</h1>
                <p>
                    Conoce el Santuario de la Naturaleza Río Cruces y Chorocamayo,
                    explora su territorio y consulta biodiversidad, proyectos,
                    conservación y fuentes públicas de información.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar():
    st.sidebar.image(str(ASSETS / "logo_escuela_geografia.png"), use_container_width=True)
    st.sidebar.markdown("## 🦢 Río Cruces")
    st.sidebar.markdown(
        "Prototipo académico · logos de referencia; no implica aval oficial"
    )
    st.sidebar.markdown("Información territorial para todas las personas")

    if "seccion" not in st.session_state:
        st.session_state["seccion"] = "Inicio"

    opciones = [
        "Inicio",
        "Visor territorial",
        "Proyectos e iniciativas",
        "Biodiversidad",
        "Conoce el humedal",
        "Fuentes y participación",
    ]

    idx = opciones.index(st.session_state["seccion"]) if st.session_state["seccion"] in opciones else 0

    seccion = st.sidebar.radio("Secciones", opciones, index=idx)
    st.session_state["seccion"] = seccion

    st.sidebar.markdown("---")
    st.sidebar.caption("Versión de trabajo · geodatos por validar")

    with st.sidebar.expander("Comprobar fotos y archivos"):
        archivos_clave = [
            ASSETS / "portada_humedal.jpg",
            ASSETS / "logo_uach.png",
            ASSETS / "logo_escuela_geografia.png",
            ASSETS / "logo_conaf.png",
            ASSETS / "cisne_cuello_negro.jpg",
            ASSETS / "huillin.jpg",
            ASSETS / "coipo.jpg",
            ASSETS / "garza_cuca.jpg",
            ASSETS / "luchecillo.jpg",
            ASSETS / "vegetacion_humedal.jpg",
            ASSETS / "ciervo_volante.jpg",
            DATA / "especies.csv",
            DATA / "proyectos.csv",
        ]
        for archivo in archivos_clave:
            icono = "✅" if archivo.exists() else "❌"
            st.write(f"{icono} {archivo.name}")


# ============================================================
# SECCIONES
# ============================================================
def seccion_inicio():
    st.markdown('<div class="capa-principal">', unsafe_allow_html=True)

    encabezado_logos()
    portada()

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="tarjeta">
                <h3>🗺️ Visor territorial</h3>
                <p>Explora las capas del santuario y comprende sus límites.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Explorar el mapa", use_container_width=True):
            ir_a("Visor territorial")

    with c2:
        st.markdown(
            """
            <div class="tarjeta">
                <h3>🏗️ Proyectos e iniciativas</h3>
                <p>Encuentra documentos, responsables y estado de los antecedentes.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Consultar proyectos", use_container_width=True):
            ir_a("Proyectos e iniciativas")

    with c3:
        st.markdown(
            """
            <div class="tarjeta">
                <h3>🌿 Conoce el humedal</h3>
                <p>Aprende sobre su biodiversidad, conservación y funcionamiento.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Aprender del humedal", use_container_width=True):
            ir_a("Conoce el humedal")

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Especies destacadas", "7")
    m2.metric("Enfoque", "Conservación")
    m3.metric("Formato", "Visor ciudadano")

    st.markdown('</div>', unsafe_allow_html=True)


def seccion_mapa():
    st.title("🗺️ Visor territorial")
    st.markdown(
        """
        <div class="tarjeta-clara">
            <p>
                Este mapa integra capas territoriales y proyectos de trabajo.
                Si agregas archivos GeoJSON en la carpeta <b>data</b>, la app los leerá automáticamente.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    mapa = crear_mapa()
    st_folium(mapa, use_container_width=True, height=650)


def seccion_proyectos():
    st.title("🏗️ Proyectos e iniciativas")

    df = cargar_proyectos()
    if df.empty:
        st.warning("No se encontró data/proyectos.csv o está vacío.")
        return

    busqueda = st.text_input("Buscar proyecto o iniciativa")
    texto_busqueda = busqueda.lower().strip()

    filtrado = df.copy()
    if texto_busqueda:
        filtrado = filtrado[
            filtrado.astype(str).apply(
                lambda col: col.str.lower().str.contains(texto_busqueda, na=False)
            ).any(axis=1)
        ]

    for _, fila in filtrado.iterrows():
        nombre = valor_fila(fila, ["nombre", "proyecto"], "Sin nombre")
        categoria = valor_fila(fila, ["categoria", "tipo"], "Sin categoría")
        descripcion = valor_fila(fila, ["descripcion", "detalle", "info"], "Sin descripción.")
        responsable = valor_fila(fila, ["responsable", "titular"], "Por definir")
        estado = valor_fila(fila, ["estado"], "Por verificar")
        fuente = valor_fila(fila, ["fuente", "url"], "")

        with st.container(border=True):
            st.subheader(nombre)
            st.caption(f"{categoria} · {estado}")
            st.write(descripcion)
            st.write(f"**Responsable:** {responsable}")
            if fuente:
                st.markdown(f"[Consultar fuente]({fuente})")


def seccion_biodiversidad():
    st.title("🌿 Biodiversidad")

    df = cargar_especies()
    if df.empty:
        st.warning("No se encontró data/especies.csv o está vacío.")
        return

    busqueda = st.text_input("Buscar por nombre común o científico")
    grupos = ["Todos"] + sorted(
        list(
            set(
                [
                    valor_fila(fila, ["tipo", "grupo"], "Sin grupo")
                    for _, fila in df.iterrows()
                ]
            )
        )
    )
    grupo_sel = st.selectbox("Filtrar por grupo", grupos)

    for _, fila in df.iterrows():
        tipo = valor_fila(fila, ["tipo", "grupo"], "Sin grupo")
        comun = valor_fila(fila, ["comun", "nombre_comun", "nombre"], "Sin nombre")
        cient = valor_fila(fila, ["cient", "cientifico", "nombre_cientifico"], "Sin nombre científico")
        descripcion = valor_fila(fila, ["descripcion", "info"], "Sin descripción.")
        habitat = valor_fila(fila, ["habitat"], "Información no disponible.")
        funcion = valor_fila(
            fila,
            ["funcion_ecologica", "funcion", "importancia_ecologica"],
            "Información no disponible.",
        )
        conservacion = valor_fila(
            fila, ["estado_conservacion", "conservacion"], "Por verificar"
        )
        cuidados = valor_fila(
            fila, ["cuidados", "proteccion", "acciones_conservacion"], "Sin detalles."
        )
        fuente = valor_fila(fila, ["fuente", "url"], "")
        imagen = valor_fila(fila, ["imagen", "foto"], "")

        if busqueda:
            objetivo = f"{comun} {cient}".lower()
            if busqueda.lower().strip() not in objetivo:
                continue

        if grupo_sel != "Todos" and tipo != grupo_sel:
            continue

        st.markdown('<div class="tarjeta">', unsafe_allow_html=True)
        col_img, col_txt = st.columns([1, 3])

        with col_img:
            if imagen and existe_archivo(ASSETS / imagen):
                st.image(str(ASSETS / imagen), width=140)
            else:
                st.info("Imagen no disponible")

        with col_txt:
            st.markdown(f"### {comun}")
            st.markdown(f"*{cient}*")
            st.markdown(f'<span class="mini-etiqueta">{tipo}</span>', unsafe_allow_html=True)
            st.write(descripcion)
            st.write(f"**Hábitat:** {habitat}")
            st.write(f"**Importancia ecológica:** {funcion}")
            st.write(f"**Estado de conservación:** {conservacion}")
            st.write(f"**Cómo cuidarla / protegerla:** {cuidados}")
            if fuente:
                st.markdown(f"[Ver fuente]({fuente})")

        st.markdown('</div>', unsafe_allow_html=True)


def seccion_conoce_humedal():
    st.title("🌱 Conoce el humedal")

    tab1, tab2, tab3 = st.tabs(["¿Qué es?", "Importancia", "Leyes y protección"])

    with tab1:
        st.markdown(
            """
            <div class="tarjeta-clara">
                <h3>¿Qué es el Santuario Río Cruces?</h3>
                <p>
                    Es un humedal de enorme valor ecológico en la Región de Los Ríos.
                    Alberga fauna, flora y procesos hidrológicos fundamentales para la biodiversidad
                    y para la vida de las comunidades vinculadas al territorio.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab2:
        st.markdown(
            """
            <div class="tarjeta-clara">
                <h3>Importancia del ecosistema</h3>
                <ul>
                    <li>Refugio y alimentación para aves acuáticas.</li>
                    <li>Hábitat para mamíferos, insectos y vegetación palustre.</li>
                    <li>Regulación hídrica y funciones ecológicas del humedal.</li>
                    <li>Valor territorial, cultural y educativo.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab3:
        st.markdown(
            """
            <div class="tarjeta-clara">
                <h3>Leyes y protección</h3>
                <p>
                    Este apartado puede complementarse con normativa ambiental,
                    áreas protegidas, instrumentos de conservación y fuentes institucionales.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def seccion_fuentes():
    st.title("📚 Fuentes y participación")

    st.markdown(
        """
        <div class="tarjeta-clara">
            <h3>Fuentes sugeridas</h3>
            <ul>
                <li>Ministerio del Medio Ambiente</li>
                <li>CONAF</li>
                <li>SEIA</li>
                <li>SNIFA / SMA</li>
                <li>Universidad Austral de Chile</li>
                <li>Centro de Humedales Río Cruces</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="tarjeta-clara">
            <h3>Participación</h3>
            <p>
                Este visor busca acercar la información a la comunidad.
                Puedes seguir ampliándolo con nuevas especies, capas geográficas,
                fuentes oficiales y contenidos educativos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# EJECUCIÓN
# ============================================================
aplicar_estilo()
sidebar()

seccion_actual = st.session_state.get("seccion", "Inicio")

if seccion_actual == "Inicio":
    seccion_inicio()
elif seccion_actual == "Visor territorial":
    seccion_mapa()
elif seccion_actual == "Proyectos e iniciativas":
    seccion_proyectos()
elif seccion_actual == "Biodiversidad":
    seccion_biodiversidad()
elif seccion_actual == "Conoce el humedal":
    seccion_conoce_humedal()
elif seccion_actual == "Fuentes y participación":
    seccion_fuentes()
else:
    seccion_inicio()
