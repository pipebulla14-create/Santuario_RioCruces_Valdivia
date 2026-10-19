import json
import math
from html import escape

import folium
import requests
import streamlit as st
from folium.features import DivIcon
from shapely.geometry import LineString
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Santuario RÃ­o Cruces | Visor ciudadano",
    page_icon="ðŸ¦¢",
    layout="wide",
    initial_sidebar_state="expanded",
)

HDR = {"User-Agent": "visor-ciudadano-rio-cruces/1.1 (proyecto academico)"}
CENTRO = [-39.68, -73.19]
EJE = [
    (-39.790, -73.243), (-39.765, -73.232), (-39.742, -73.215),
    (-39.720, -73.200), (-39.695, -73.190), (-39.670, -73.182),
    (-39.645, -73.170), (-39.620, -73.160), (-39.595, -73.155),
    (-39.570, -73.150),
]

# REGISTROS PRELIMINARES: coordenadas/radios aproximados, no oficiales.
# Verificar nombre, titular, estado y geometrÃ­a en los expedientes originales.
PROYECTOS = [
    {
        "nombre": "Planta Valdivia (Celulosa Arauco)",
        "categoria": "Actividad productiva",
        "instrumento": "Por verificar",
        "estado": "Antecedente por verificar",
        "lat": -39.640, "lon": -73.010, "radio_m": 5000,
        "responsable": "Arauco (verificar titular y expediente)",
        "fuente": "https://seia.sea.gob.cl/",
        "wiki": "Celulosa Arauco y ConstituciÃ³n",
        "descripcion": (
            "InstalaciÃ³n industrial que debe analizarse con sus antecedentes ambientales. "
            "Verificar expedientes y ubicaciÃ³n. No atribuir efectos ecolÃ³gicos sin fuentes "
            "que respalden la relaciÃ³n causal."
        ),
        "verificado": False,
    },
    {
        "nombre": "Condominio Parque RÃ­o Cruces (Etapa II)",
        "categoria": "Desarrollo inmobiliario",
        "instrumento": "Por verificar",
        "estado": "Antecedente por verificar",
        "lat": -39.8044, "lon": -73.2600, "radio_m": 1500,
        "responsable": "Por verificar",
        "fuente": "https://seia.sea.gob.cl/",
        "wiki": "Isla Teja",
        "descripcion": (
            "Registro preliminar. Confirmar nombre oficial, titular, ubicaciÃ³n, instrumento "
            "ambiental y estado administrativo en fuentes oficiales. La proximidad no prueba impacto."
        ),
        "verificado": False,
    },
    {
        "nombre": "Loteo Riberas de la Dehesa (Tres Bocas)",
        "categoria": "Loteo / intervenciÃ³n territorial",
        "instrumento": "Por verificar",
        "estado": "Antecedente por verificar",
        "lat": -39.7256, "lon": -73.2381, "radio_m": 1500,
        "responsable": "Por verificar",
        "fuente": "https://snifa.sma.gob.cl/",
        "wiki": "RÃ­o Cruces",
        "descripcion": (
            "Registro preliminar para revisar antecedentes del SEIA y de la SMA, incluidos "
            "eventuales procedimientos de fiscalizaciÃ³n. No es una conclusiÃ³n de infracciÃ³n o daÃ±o."
        ),
        "verificado": False,
    },
    {
        "nombre": "Loteo / relleno Santa Rosa (Cabo Blanco)",
        "categoria": "Loteo / intervenciÃ³n territorial",
        "instrumento": "Por verificar",
        "estado": "Antecedente por verificar",
        "lat": -39.7753, "lon": -73.2311, "radio_m": 1000,
        "responsable": "Por verificar",
        "fuente": "https://snifa.sma.gob.cl/",
        "wiki": "RÃ­o Cruces",
        "descripcion": (
            "Registro preliminar pendiente de corroboraciÃ³n. Verificar localizaciÃ³n, titular, "
            "permisos y antecedentes ambientales antes de presentarlo como informaciÃ³n confirmada."
        ),
        "verificado": False,
    },
]

# Estos puntos solo ilustran cÃ³mo se verÃ­a la capa; no son observaciones georreferenciadas.
ESPECIES = [
    {"tipo": "animal", "comun": "Cisne de cuello negro", "cient": "Cygnus melanocoryphus",
     "wiki": "Cygnus melanocoryphus", "i": 4,
     "info": "Ave acuÃ¡tica emblemÃ¡tica. Punto esquemÃ¡tico, no un registro de observaciÃ³n."},
    {"tipo": "animal", "comun": "HuillÃ­n", "cient": "Lontra provocax",
     "wiki": "Lontra provocax", "i": 6,
     "info": "MamÃ­fero semiacuÃ¡tico nativo. Confirmar registros locales antes de afirmar presencia en este punto."},
    {"tipo": "animal", "comun": "Coipo", "cient": "Myocastor coypus",
     "wiki": "Myocastor coypus", "i": 2,
     "info": "MamÃ­fero semiacuÃ¡tico asociado a humedales. Punto esquemÃ¡tico."},
    {"tipo": "animal", "comun": "Garza cuca", "cient": "Ardea cocoi",
     "wiki": "Ardea cocoi", "i": 7,
     "info": "Ave de ambientes acuÃ¡ticos y ribereÃ±os. Punto esquemÃ¡tico."},
    {"tipo": "planta", "comun": "Luchecillo", "cient": "Egeria densa",
     "wiki": "Egeria densa", "i": 5,
     "info": "Planta acuÃ¡tica sumergida. Confirmar distribuciÃ³n local con fuente tÃ©cnica."},
    {"tipo": "planta", "comun": "Totora", "cient": "Schoenoplectus californicus",
     "wiki": "Schoenoplectus californicus", "i": 3,
     "info": "Planta de ambientes palustres. Punto esquemÃ¡tico."},
    {"tipo": "insecto", "comun": "Ciervo volante", "cient": "Chiasognathus granti",
     "wiki": "Chiasognathus granti", "i": 1,
     "info": "Escarabajo nativo de bosques templados. No se afirma presencia local sin registro verificable."},
]

ICONOS = {
    "animal": ("ðŸ¦¢", "#4c9be8"),
    "planta": ("ðŸŒ¿", "#5cb85c"),
    "insecto": ("ðŸª²", "#8d6e63"),
}

INICIATIVAS = [
    {
        "nombre": "Plan de Manejo del Santuario",
        "categoria": "PlanificaciÃ³n y conservaciÃ³n",
        "estado": "Consultar versiÃ³n oficial vigente",
        "responsable": "Organismos pÃºblicos competentes",
        "descripcion": "Instrumento que orienta la conservaciÃ³n y gestiÃ³n del Ã¡rea protegida. Consultar documento y fecha de vigencia.",
        "fuente": "https://www.conaf.cl/centro-documental/pm-mn-y-sn-rio-cruces-y-chorocamayo-v-extendida/",
    },
    {
        "nombre": "ActualizaciÃ³n de antecedentes para el Plan de Manejo",
        "categoria": "PlanificaciÃ³n y conservaciÃ³n",
        "estado": "Verificar contrataciÃ³n y resultados",
        "responsable": "Ministerio del Medio Ambiente (verificar ficha)",
        "descripcion": "Antecedente relacionado con amenazas, cartografÃ­a y participaciÃ³n. La licitaciÃ³n no prueba que los productos estÃ©n terminados.",
        "fuente": "https://www.mercadopublico.cl/",
    },
    {
        "nombre": "Plan Maestro del territorio del humedal",
        "categoria": "Desarrollo comunitario",
        "estado": "Consultar versiÃ³n y avances",
        "responsable": "AsociaciÃ³n Comunidad Humedal",
        "descripcion": "Antecedente de planificaciÃ³n territorial comunitaria. Revisar documento original para confirmar prioridades y avances.",
        "fuente": "https://www.comunidadhumedal.cl/",
    },
    {
        "nombre": "InvestigaciÃ³n y monitoreo del humedal",
        "categoria": "InvestigaciÃ³n y educaciÃ³n",
        "estado": "CatÃ¡logo por ampliar",
        "responsable": "Centro de Humedales RÃ­o Cruces y entidades colaboradoras",
        "descripcion": "CategorÃ­a inicial para incorporar estudios y monitoreos con tÃ­tulo, autores, aÃ±o y enlace verificable.",
        "fuente": "https://cehum.org/",
    },
]


@st.cache_data(ttl=86400, show_spinner=False)
def wiki(titulo):
    try:
        url = "https://es.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(titulo.replace(" ", "_"))
        r = requests.get(url, headers=HDR, timeout=8)
        r.raise_for_status()
        return r.json().get("thumbnail", {}).get("source")
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def limite_osm():
    for q in [
        "Santuario de la Naturaleza RÃ­o Cruces y Chorocamayo",
        "Santuario de la Naturaleza Carlos Anwandter",
    ]:
        try:
            r = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": q, "format": "jsonv2", "polygon_geojson": 1, "limit": 5},
                headers=HDR, timeout=12,
            )
            r.raise_for_status()
            for item in r.json():
                g = item.get("geojson")
                if g and g.get("type") in ("Polygon", "MultiPolygon"):
                    return {"type": "Feature", "properties": {}, "geometry": g}
        except Exception:
            pass
    return None


def limite_esquematico(metros=1000):
    lat0, lon0 = EJE[0]
    kx = 111320 * math.cos(math.radians(lat0))
    ky = 110574
    xy = [((lon - lon0) * kx, (lat - lat0) * ky) for lat, lon in EJE]
    pol = LineString(xy).buffer(metros)
    coords = [[lon0 + x / kx, lat0 + y / ky] for x, y in pol.exterior.coords]
    return {
        "type": "Feature", "properties": {"fuente": "Esquema no oficial"},
        "geometry": {"type": "Polygon", "coordinates": [coords]},
    }


def popup(titulo, img, texto):
    titulo = escape(str(titulo))
    texto = escape(str(texto))
    imagen = (
        f'<img src="{escape(img, quote=True)}" alt="" style="width:100%;max-height:145px;'
        'object-fit:cover;border-radius:6px">'
        if img else '<p style="font-size:12px;color:#667085">Imagen no disponible</p>'
    )
    html = (
        '<div style="font-family:Arial,sans-serif;width:260px">'
        f'<h4 style="margin:0 0 8px;color:#24543f">{titulo}</h4>{imagen}'
        f'<p style="font-size:12px;line-height:1.45">{texto}</p></div>'
    )
    return folium.Popup(html, max_width=320)


def marcador(grupo, lat, lon, emoji, fondo, tip, pop):
    html = (
        f'<div style="width:34px;height:34px;border-radius:50%;background:{fondo};'
        'border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,.35);display:flex;'
        f'align-items:center;justify-content:center;font-size:18px">{emoji}</div>'
    )
    folium.Marker(
        [lat, lon], tooltip=tip, popup=pop,
        icon=DivIcon(icon_size=(34, 34), icon_anchor=(17, 17), html=html),
    ).add_to(grupo)


st.markdown(
    """
    <style>
    .block-container {padding-top:1.4rem; padding-bottom:2.5rem;}
    .hero {padding:1.5rem 1.7rem; border-radius:16px; background:linear-gradient(120deg,#e4f2e9,#f5f8f5);
           border:1px solid #c9dfd1; margin-bottom:1rem;}
    .hero h1 {color:#214e3a; margin-bottom:.4rem;}
    .hero p {color:#344c40; font-size:1.05rem; max-width:900px;}
    div[data-testid="stMetric"] {background:#f6faf7; border:1px solid #e0ece4; padding:12px 14px; border-radius:12px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("ðŸ¦¢ RÃ­o Cruces")
st.sidebar.caption("Visor territorial ciudadano")
if "seccion" not in st.session_state:
    st.session_state["seccion"] = "Inicio"
secciones = ["Inicio", "Visor territorial", "Proyectos e iniciativas", "Conoce el humedal", "Fuentes y participaciÃ³n"]
seccion = st.sidebar.radio(
    "NavegaciÃ³n principal", secciones,
    index=secciones.index(st.session_state["seccion"]),
    key="nav_seccion",
)
st.session_state["seccion"] = seccion
st.sidebar.divider()
st.sidebar.caption("Las fichas preliminares se identifican expresamente. Verifica siempre las fuentes originales.")

# =============================== INICIO ===============================
if seccion == "Inicio":
    st.markdown(
        """
        <div class="hero">
          <h1>Conoce el Santuario RÃ­o Cruces</h1>
          <p>Explora informaciÃ³n territorial, ambiental y social del Santuario de la Naturaleza RÃ­o Cruces y Chorocamayo.
          Consulta el mapa, conoce iniciativas y accede a fuentes originales sin necesitar conocimientos tÃ©cnicos de cartografÃ­a.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Herramientas", "Mapa + fichas")
    c2.metric("Enfoque", "InformaciÃ³n abierta")
    c3.metric("PropÃ³sito", "Acceso ciudadano")
    st.subheader("Â¿QuÃ© quieres consultar?")
    a, b, c = st.columns(3)
    with a:
        st.markdown("### ðŸ—ºï¸ Explorar el territorio")
        st.write("Activa capas y consulta los elementos del mapa.")
        if st.button("Abrir visor", use_container_width=True):
            st.session_state["seccion"] = "Visor territorial"
            st.rerun()
    with b:
        st.markdown("### ðŸ—ï¸ Consultar proyectos")
        st.write("Busca iniciativas, estados conocidos y fuentes.")
        if st.button("Ver proyectos", use_container_width=True):
            st.session_state["seccion"] = "Proyectos e iniciativas"
            st.rerun()
    with c:
        st.markdown("### ðŸŒ¿ Conocer el humedal")
        st.write("Lee explicaciones sencillas sobre ecosistema y gestiÃ³n.")
        if st.button("Aprender", use_container_width=True):
            st.session_state["seccion"] = "Conoce el humedal"
            st.rerun()
    st.subheader("Principios de la plataforma")
    p1, p2, p3 = st.columns(3)
    p1.markdown("**Accesibilidad**\n\nInformaciÃ³n clara y alternativas al mapa.")
    p2.markdown("**Transparencia**\n\nFuentes, fechas y limitaciones visibles.")
    p3.markdown("**ParticipaciÃ³n**\n\nAcceso a instituciones y canales pÃºblicos.")
    st.info("Los puntos y radios de proyectos de esta versiÃ³n son preliminares. No deben interpretarse como ubicaciones o impactos confirmados.")

# =========================== VISOR TERRITORIAL ===========================
elif seccion == "Visor territorial":
    st.title("Visor territorial")
    st.write("Activa las capas que quieras explorar. Selecciona los elementos del mapa para consultar sus fichas.")
    with st.expander("Â¿QuÃ© significa cada tipo de Ã¡rea?"):
        st.markdown(
            "- **Ãrea protegida:** lÃ­mite legal respaldado por cartografÃ­a oficial.\n"
            "- **Ãrea de influencia de un proyecto:** delimitaciÃ³n documentada en su expediente ambiental.\n"
            "- **Ãrea de anÃ¡lisis territorial:** zona definida para estudiar relaciones hÃ­dricas, ecolÃ³gicas o sociales.\n"
            "- **Radio ilustrativo:** cÃ­rculo preliminar; no representa un impacto demostrado."
        )

    panel, mapa_col = st.columns([1, 3])
    with panel:
        tipo_mapa = st.radio("Mapa base", ["OpenStreetMap", "Satelital", "Claro"])
        ver_santuario = st.checkbox("LÃ­mite del santuario", True)
        ver_proyectos = st.checkbox("Proyectos preliminares", True)
        ver_influencia = st.checkbox("Radios ilustrativos de proyectos", False)
        ver_animales = st.checkbox("Fauna (puntos esquemÃ¡ticos)", True)
        ver_plantas = st.checkbox("Flora (puntos esquemÃ¡ticos)", True)
        ver_insectos = st.checkbox("Insectos (puntos esquemÃ¡ticos)", False)
        ver_eje = st.checkbox("Eje hidrogrÃ¡fico esquemÃ¡tico", False)
        st.caption("Los puntos de especies no son observaciones georreferenciadas.")
        archivo = st.file_uploader("Cargar lÃ­mite oficial (GeoJSON, opcional)", type=["geojson", "json"]) if ver_santuario else None

    if tipo_mapa == "Satelital":
        m = folium.Map(CENTRO, zoom_start=11, tiles=None, control_scale=True)
        folium.TileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery", name="Imagen satelital",
        ).add_to(m)
    elif tipo_mapa == "Claro":
        m = folium.Map(CENTRO, zoom_start=11, tiles="CartoDB positron", control_scale=True)
    else:
        m = folium.Map(CENTRO, zoom_start=11, tiles="OpenStreetMap", control_scale=True)

    if ver_santuario:
        limite, fuente = None, ""
        if archivo is not None:
            try:
                limite, fuente = json.load(archivo), "Archivo cargado; verificar metadatos"
            except Exception as exc:
                st.error(f"No se pudo leer el GeoJSON: {exc}")
        if limite is None:
            limite = limite_osm()
            fuente = "OpenStreetMap; no sustituye cartografÃ­a oficial"
        if limite is None:
            limite = limite_esquematico()
            fuente = "Esquema aproximado no oficial"
        folium.GeoJson(
            limite, name="LÃ­mite representado",
            style_function=lambda f: {"color": "#247445", "weight": 2.5, "fillColor": "#a8e6a1", "fillOpacity": 0.22},
            tooltip="LÃ­mite representado: revisar fuente",
        ).add_to(m)
        st.caption("**Fuente del lÃ­mite:** " + fuente)

    if ver_eje:
        folium.PolyLine(
            [[lat, lon] for lat, lon in EJE],
            color="#1976a8", weight=4, opacity=0.8,
            tooltip="Eje hidrogrÃ¡fico esquemÃ¡tico; reemplazar por red hidrogrÃ¡fica oficial",
        ).add_to(m)

    if ver_proyectos:
        gp = folium.FeatureGroup(name="Proyectos preliminares", show=True)
        for p in PROYECTOS:
            texto = (
                f"CategorÃ­a: {p['categoria']}. Estado: {p['estado']}. {p['descripcion']} "
                f"Fuente para consultar: {p['fuente']}. UbicaciÃ³n preliminar."
            )
            marcador(gp, p["lat"], p["lon"], "?", "#b97725", p["nombre"], popup(p["nombre"], wiki(p["wiki"]), texto))
        gp.add_to(m)

    if ver_influencia:
        gi = folium.FeatureGroup(name="Radios ilustrativos â€” no oficiales")
        for p in PROYECTOS:
            folium.Circle(
                [p["lat"], p["lon"]], radius=p["radio_m"], color="#d97706",
                weight=1.5, fill=True, fill_color="#fbbf24", fill_opacity=0.12,
                tooltip=f"Radio ilustrativo: {p['radio_m']:,} m â€” {p['nombre']}",
            ).add_to(gi)
        gi.add_to(m)

    visibles = {"animal": ver_animales, "planta": ver_plantas, "insecto": ver_insectos}
    for tipo, nombre in [("animal", "Fauna esquemÃ¡tica"), ("planta", "Flora esquemÃ¡tica"), ("insecto", "Insectos esquemÃ¡ticos")]:
        if not visibles[tipo]:
            continue
        grupo = folium.FeatureGroup(name=nombre)
        for e in ESPECIES:
            if e["tipo"] != tipo:
                continue
            lat, lon = EJE[e["i"]]
            emoji, color = ICONOS[tipo]
            titulo = f"{e['comun']} ({e['cient']})"
            texto = e["info"] + " UbicaciÃ³n esquemÃ¡tica; no es un registro de observaciÃ³n."
            marcador(grupo, lat + 0.004, lon - 0.006, emoji, color, e["comun"], popup(titulo, wiki(e["wiki"]), texto))
        grupo.add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)
    with mapa_col:
        st_folium(m, use_container_width=True, height=650, returned_objects=[])
    st.caption("Los radios, puntos de especies y registros preliminares no prueban ubicaciÃ³n, presencia ni impacto.")

# ======================== PROYECTOS E INICIATIVAS ========================
elif seccion == "Proyectos e iniciativas":
    st.title("Proyectos e iniciativas")
    st.write("CatÃ¡logo inicial de antecedentes. Los estados y ubicaciones pendientes se muestran de forma explÃ­cita.")
    busqueda = st.text_input("Buscar por nombre, tema o instituciÃ³n")
    registros = []
    for p in PROYECTOS:
        registros.append({**p, "tipo_registro": "Proyecto territorial"})
    for i in INICIATIVAS:
        registros.append({
            **i, "instrumento": "No aplica / revisar ficha",
            "verificado": False, "tipo_registro": "Plan, programa o iniciativa",
        })
    categorias = ["Todas"] + sorted({r["categoria"] for r in registros})
    categoria = st.selectbox("CategorÃ­a", categorias)
    pendientes = st.checkbox("Mostrar registros pendientes de verificaciÃ³n", True)
    filtrados = []
    for r in registros:
        texto = " ".join([r["nombre"], r["categoria"], r["responsable"], r["descripcion"], r["estado"]]).lower()
        if busqueda.strip().lower() not in texto:
            continue
        if categoria != "Todas" and r["categoria"] != categoria:
            continue
        if not pendientes and not r.get("verificado", False):
            continue
        filtrados.append(r)
    st.caption(f"{len(filtrados)} registros coinciden con los filtros.")
    for r in filtrados:
        with st.expander(("âš ï¸ " if not r.get("verificado", False) else "âœ“ ") + r["nombre"]):
            st.caption(r.get("tipo_registro", "Registro") + " Â· " + r["categoria"])
            st.write(r["descripcion"])
            st.write("**Estado:** " + r["estado"])
            st.write("**InstituciÃ³n / responsable:** " + r["responsable"])
            st.write("**Instrumento ambiental:** " + r.get("instrumento", "No aplica / revisar ficha"))
            st.markdown(f"[Consultar portal o fuente]({r['fuente']})")
            if not r.get("verificado", False):
                st.warning("Ficha preliminar: verificar el documento original y anotar fecha de consulta.")
    st.info("La inclusiÃ³n en el catÃ¡logo no significa que una iniciativa estÃ© aprobada, ejecutÃ¡ndose o que haya causado impactos.")

# ============================= CONOCE HUMEDAL =============================
elif seccion == "Conoce el humedal":
    st.title("Conoce el humedal")
    st.write("GuÃ­as breves para comprender el territorio sin conocimientos tÃ©cnicos previos.")
    with st.expander("Â¿QuÃ© es un humedal?", expanded=True):
        st.write("Es un ambiente donde el agua condiciona el suelo, la vegetaciÃ³n y la vida silvestre. Puede ofrecer hÃ¡bitat, almacenar agua y retener sedimentos; sus funciones varÃ­an segÃºn sus condiciones.")
    with st.expander("Â¿Por quÃ© mirar mÃ¡s allÃ¡ del lÃ­mite del santuario?"):
        st.write("Los procesos ecolÃ³gicos no siempre coinciden con lÃ­mites administrativos. El agua, los sedimentos, la conectividad de hÃ¡bitats y las actividades humanas pueden conectar el Ã¡rea protegida con sectores vecinos.")
    with st.expander("Â¿QuÃ© significa Ã¡rea de influencia?"):
        st.write("En evaluaciÃ³n ambiental se define segÃºn los elementos que podrÃ­an verse afectados y los impactos evaluados. No equivale automÃ¡ticamente a un cÃ­rculo. Los radios del visor son ilustrativos hasta ser reemplazados por geometrÃ­as documentadas.")
    with st.expander("Â¿QuÃ© diferencia hay entre DIA y EIA?"):
        st.write("Son instrumentos del Sistema de EvaluaciÃ³n de Impacto Ambiental. Tienen requisitos distintos, y el instrumento no informa por sÃ­ solo si un proyecto estÃ¡ aprobado. Hay que consultar el estado en el expediente oficial.")
    with st.expander("Â¿CÃ³mo leer las capas del mapa?"):
        st.write("Revisa fuente, fecha, escala y metodologÃ­a. Una capa puede ser un lÃ­mite legal, un dato histÃ³rico, una estimaciÃ³n o una propuesta de anÃ¡lisis; la ficha debe aclararlo.")
    st.subheader("Fuentes para profundizar")
    st.markdown(
        "- [Ministerio del Medio Ambiente](https://mma.gob.cl/)\n"
        "- [SIMBIO](https://simbio.mma.gob.cl/)\n"
        "- [Sistema de EvaluaciÃ³n de Impacto Ambiental](https://seia.sea.gob.cl/)\n"
        "- [Superintendencia del Medio Ambiente â€” SNIFA](https://snifa.sma.gob.cl/)\n"
        "- [CONAF â€” documentos del santuario](https://www.conaf.cl/centro-documental/pm-mn-y-sn-rio-cruces-y-chorocamayo-v-extendida/)\n"
        "- [Centro de Humedales RÃ­o Cruces](https://cehum.org/)\n"
        "- [AsociaciÃ³n Comunidad Humedal](https://www.comunidadhumedal.cl/)"
    )

# ======================= FUENTES Y PARTICIPACIÃ“N =======================
elif seccion == "Fuentes y participaciÃ³n":
    st.title("Fuentes, transparencia y participaciÃ³n")
    st.write("Consulta los antecedentes originales y distingue informaciÃ³n oficial, cientÃ­fica, preliminar y aportes ciudadanos.")
    fuentes = [
        ("Ministerio del Medio Ambiente", "PolÃ­ticas, planes y antecedentes ambientales.", "https://mma.gob.cl/"),
        ("SIMBIO", "Biodiversidad y Ã¡reas de conservaciÃ³n.", "https://simbio.mma.gob.cl/"),
        ("SEIA", "Expedientes y estado de proyectos evaluados ambientalmente.", "https://seia.sea.gob.cl/"),
        ("SNIFA / SMA", "FiscalizaciÃ³n y antecedentes de la Superintendencia del Medio Ambiente.", "https://snifa.sma.gob.cl/"),
        ("CONAF", "Documentos de gestiÃ³n y conservaciÃ³n.", "https://www.conaf.cl/"),
        ("Centro de Humedales RÃ­o Cruces", "InvestigaciÃ³n y educaciÃ³n.", "https://cehum.org/"),
        ("Comunidad Humedal", "Iniciativas comunitarias y territoriales.", "https://www.comunidadhumedal.cl/"),
        ("Mercado PÃºblico", "Licitaciones y contrataciones pÃºblicas.", "https://www.mercadopublico.cl/"),
    ]
    for nombre, descripcion, url in fuentes:
        with st.container(border=True):
            st.markdown(f"**{nombre}**")
            st.write(descripcion)
            st.markdown(f"[Abrir fuente]({url})")
    st.subheader("Criterios de calidad")
    st.markdown(
        "- **Oficial:** publicado por la instituciÃ³n competente.\n"
        "- **CientÃ­fica:** procedente de un estudio identificable.\n"
        "- **ElaboraciÃ³n propia:** procesada por el equipo y acompaÃ±ada de metodologÃ­a.\n"
        "- **Preliminar:** pendiente de corroboraciÃ³n.\n"
        "- **Aporte ciudadano:** entregado por una persona u organizaciÃ³n y pendiente de revisiÃ³n."
    )
    st.subheader("Sugerir una correcciÃ³n o recurso")
    st.write("Este formulario prepara un archivo local. No publica ni envÃ­a el aporte automÃ¡ticamente.")
    with st.form("formulario_aporte"):
        tipo_aporte = st.selectbox("Tipo de aporte", [
            "CorrecciÃ³n de informaciÃ³n", "Nuevo proyecto o documento",
            "Registro ambiental", "Sugerencia de accesibilidad", "Otro",
        ])
        detalle = st.text_area("Describe el aporte", placeholder="Indica quÃ© deberÃ­a revisarse y por quÃ©. No incluyas datos personales sensibles.")
        enlace = st.text_input("Enlace a una fuente (opcional)")
        enviado = st.form_submit_button("Preparar aporte")
    if enviado:
        if not detalle.strip():
            st.error("Escribe una descripciÃ³n antes de preparar el aporte.")
        else:
            aporte = {"tipo": tipo_aporte, "detalle": detalle.strip(), "fuente": enlace.strip()}
            datos = json.dumps(aporte, ensure_ascii=False, indent=2)
            st.success("Aporte preparado localmente; no se ha enviado ni publicado.")
            st.code(datos, language="json")
            st.download_button("Descargar aporte en JSON", data=datos, file_name="aporte_visor_rio_cruces.json", mime="application/json")

st.sidebar.divider()
st.sidebar.caption("Visor ciudadano Â· versiÃ³n de trabajo")
st.sidebar.caption("Verifica los datos con las fuentes originales antes de utilizarlos en informes.")
