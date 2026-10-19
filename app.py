"""Visor ciudadano del Santuario Río Cruces. Proyecto académico, datos geográficos en revisión."""
import base64
import json
import math
from html import escape
from pathlib import Path

import folium
import pandas as pd
import requests
import streamlit as st
from folium.features import DivIcon
from shapely.geometry import LineString, shape, mapping
from shapely.ops import transform
from streamlit_folium import st_folium

ROOT = Path(__file__).parent
st.set_page_config(page_title='Santuario Río Cruces | Visor ciudadano', page_icon='🦢', layout='wide')
CENTER = [-39.68, -73.19]
HEADERS = {'User-Agent': 'VisorRioCrucesAcademico/1.0 (consulta cartografica)'}
DATA = ROOT / 'data'
ASSETS = ROOT / 'assets'

@st.cache_data
def cargar_csv(archivo):
    return pd.read_csv(DATA / archivo).fillna('')

proyectos = cargar_csv('proyectos.csv')
especies = cargar_csv('especies.csv')

@st.cache_data(ttl=86400)
def osm_limite():
    for term in ['Santuario de la Naturaleza Río Cruces y Chorocamayo', 'Santuario de la Naturaleza Carlos Anwandter']:
        try:
            r = requests.get('https://nominatim.openstreetmap.org/search',
                             params={'q':term, 'format':'jsonv2', 'polygon_geojson':1, 'limit':5},
                             headers=HEADERS, timeout=12)
            r.raise_for_status()
            for item in r.json():
                g = item.get('geojson', {})
                if g.get('type') in ['Polygon', 'MultiPolygon']:
                    return {'type':'Feature','properties':{'fuente':'OpenStreetMap: referencia no oficial'}, 'geometry':g}
        except (requests.RequestException, ValueError):
            pass
    return None

# El eje es referencia esquemática original; NO es una geometría oficial.
EJE = [(-39.790,-73.243),(-39.765,-73.232),(-39.742,-73.215),(-39.720,-73.200),
       (-39.695,-73.190),(-39.670,-73.182),(-39.645,-73.170),(-39.620,-73.160),
       (-39.595,-73.155),(-39.570,-73.150)]

def esquema(metros=1000):
    lat0, lon0=EJE[0]
    kx=111320*math.cos(math.radians(lat0)); ky=110574
    pts=[((lon-lon0)*kx,(lat-lat0)*ky) for lat,lon in EJE]
    geom=LineString(pts).buffer(metros)
    xy=[[lon0+x/kx, lat0+y/ky] for x,y in geom.exterior.coords]
    return {'type':'Feature','properties':{},'geometry':{'type':'Polygon','coordinates':[xy]}}

def leer_geojson(archivo):
    if archivo is None: return None
    try:
        d=json.load(archivo)
        if d.get('type') not in ['Feature','FeatureCollection','Polygon','MultiPolygon']:
            raise ValueError('El tipo de geometría no es compatible.')
        # Folium acepta objetos FeatureCollection, Feature y geometrías GeoJSON.
        return d
    except (ValueError, json.JSONDecodeError) as exc:
        st.error(f'No se pudo cargar el GeoJSON: {exc}')
        return None

def imagen_encabezado():
    path=ASSETS/'portada_humedal.jpg'
    if path.exists():
        b64=base64.b64encode(path.read_bytes()).decode()
        return f'url("data:image/jpeg;base64,{b64}")'
    return 'linear-gradient(120deg,#173b38,#37795a)'

st.markdown('''<style>
.block-container{padding-top:1rem;padding-bottom:2rem;max-width:1450px}
.hero{border-radius:22px;padding:3rem 2.5rem;min-height:340px;display:flex;flex-direction:column;justify-content:center;color:white;
background:linear-gradient(90deg,rgba(5,31,33,.91),rgba(5,31,33,.37)),var(--hero-image);background-position:center;background-size:cover}
.hero h1{font-size:clamp(2rem,4vw,3.25rem);color:white;max-width:780px}
.hero p{max-width:660px;font-size:1.12rem;line-height:1.65}
.note{border-left:4px solid #347f6a;padding:.7rem 1rem;background:#edf5f1;border-radius:6px}
div[data-testid="stMetric"]{border:1px solid #dce8e1;border-radius:12px;padding:12px;background:#f6faf8}
@media(max-width:700px){.hero{padding:2rem 1.2rem;min-height:270px}}
</style>''',unsafe_allow_html=True)

if 'navegacion' not in st.session_state: st.session_state.navegacion='Inicio'
paginas=['Inicio','Visor territorial','Proyectos e iniciativas','Conoce el humedal','Fuentes y participación']
st.sidebar.markdown('## 🦢 Río Cruces')
st.sidebar.caption('Información territorial para todas las personas')
pagina=st.sidebar.radio('Secciones', paginas, key='navegacion')
st.sidebar.divider()
st.sidebar.caption('Versión de trabajo · geodatos por validar')

if pagina=='Inicio':
    background=imagen_encabezado()
    st.markdown(f'<div class="hero" style="--hero-image:{background}"><h1>Un humedal vivo, un territorio compartido</h1><p>Conoce el Santuario de la Naturaleza Río Cruces y Chorocamayo, explora su territorio y consulta iniciativas, biodiversidad y fuentes de información pública.</p></div>',unsafe_allow_html=True)
    st.write('')
    a,b,c=st.columns(3)
    with a:
        st.subheader('🗺️ Visor territorial'); st.write('Explora las capas y comprende sus límites.')
        if st.button('Explorar el mapa',use_container_width=True): st.session_state.navegacion='Visor territorial';st.rerun()
    with b:
        st.subheader('🏗️ Proyectos e iniciativas');st.write('Encuentra documentos, responsables y estado de los antecedentes.')
        if st.button('Consultar proyectos',use_container_width=True): st.session_state.navegacion='Proyectos e iniciativas';st.rerun()
    with c:
        st.subheader('🌿 Conoce el humedal');st.write('Aprende sobre su biodiversidad, conservación y funcionamiento.')
        if st.button('Aprender del humedal',use_container_width=True):st.session_state.navegacion='Conoce el humedal';st.rerun()
    st.divider();st.subheader('El territorio en contexto')
    c1,c2,c3=st.columns(3)
    c1.metric('Iniciativas documentales',len(proyectos),'No implica ejecución vigente',delta_color='off')
    c2.metric('Temas de biodiversidad',len(especies),'Fichas de divulgación',delta_color='off')
    c3.metric('Criterio del visor','Fuentes abiertas')
    st.info('Los proyectos institucionales son referencias documentales; los proyectos de impacto territorial originales están separados como registros de trabajo sin verificar. No se deducen impactos a partir de cercanía geográfica.')
    st.markdown('**Nuestro propósito:** que la información se pueda consultar mediante mapas, fichas y enlaces directos, sin conocimientos previos de SIG.')

elif pagina=='Visor territorial':
    st.title('🗺️ Visor territorial')
    st.write('Utiliza las capas para explorar el territorio. En la leyenda se distingue entre límites verificados, datos de referencia y dibujos ilustrativos.')
    panel,main=st.columns([1,3],gap='large')
    with panel:
        base=st.selectbox('Mapa base',['OpenStreetMap','Satelital','Claro'])
        st.subheader('Capas')
        ver_limite=st.checkbox('Límite del santuario',True)
        ver_esquema=st.checkbox('Franja esquemática',False,help='No es área de influencia oficial')
        ver_eje=st.checkbox('Eje hidrográfico de referencia',False)
        ver_proyectos=st.checkbox('Proyectos con ubicación preliminar',True)
        ver_radios=st.checkbox('Radios ilustrativos de proyectos',False)
        ver_especies=st.checkbox('Ejemplos de especies (no son observaciones)',False)
        st.divider();st.caption('Límites / área de influencia')
        limite_cargado=leer_geojson(st.file_uploader('GeoJSON oficial del santuario',type=['json','geojson'],key='limite'))
        influencia_cargada=leer_geojson(st.file_uploader('GeoJSON del área de análisis',type=['json','geojson'],key='influencia'))
        st.caption('Subir archivos no demuestra que sean oficiales: consigna fuente, escala y metodología.')
    if base=='Satelital':
        mapa=folium.Map(CENTER,zoom_start=11,tiles=None,control_scale=True)
        folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',attr='Esri World Imagery',name='Satelital').add_to(mapa)
    else:
        mapa=folium.Map(CENTER,zoom_start=11,tiles='OpenStreetMap' if base=='OpenStreetMap' else 'CartoDB positron',control_scale=True)
    if ver_limite:
        limite=limite_cargado or osm_limite()
        if limite:
            folium.GeoJson(limite,name='Santuario (revisar fuente)',style_function=lambda f:{'color':'#21824d','weight':3,'fillColor':'#71d7a2','fillOpacity':.18},tooltip='Límite representado; confirmar fuente').add_to(mapa)
        else:st.warning('No se obtuvo el polígono. Carga el límite oficial GeoJSON. No se dibujó uno ficticio como límite legal.')
    if influencia_cargada:
        folium.GeoJson(influencia_cargada,name='Área de análisis aportada',style_function=lambda f:{'color':'#f39c12','weight':3,'dashArray':'7,6','fillOpacity':.08},tooltip='Área de análisis cargada: revisar metodología').add_to(mapa)
    if ver_esquema:
        folium.GeoJson(esquema(1200),name='Franja esquemática NO OFICIAL',style_function=lambda f:{'color':'#e9a23b','weight':2,'dashArray':'6,6','fillOpacity':.04},tooltip='Franja ilustrativa, no es área de influencia').add_to(mapa)
    if ver_eje:folium.PolyLine(EJE,color='#1a78a3',weight=3,tooltip='Eje aproximado').add_to(mapa)
    if ver_proyectos:
        grupo=folium.FeatureGroup(name='Proyectos de ubicación preliminar')
        for _,p in proyectos[proyectos['mostrar_mapa'].astype(str)=='si'].iterrows():
            if str(p['lat'])=='' or str(p['lon'])=='':continue
            contenido=f"<b>{escape(str(p['nombre']))}</b><br>{escape(str(p['categoria']))}<br>Ubicación aproximada; revisar expediente.<br><a target='_blank' href='{escape(str(p['fuente']),quote=True)}'>Ver fuente</a>"
            folium.Marker([float(p['lat']),float(p['lon'])],tooltip=p['nombre'],popup=folium.Popup(contenido,max_width=290),icon=folium.Icon(color='orange',icon='info-sign')).add_to(grupo)
        grupo.add_to(mapa)
    if ver_radios:
        grupo=folium.FeatureGroup(name='Radios ilustrativos NO OFICIALES')
        for _,p in proyectos[proyectos['mostrar_mapa'].astype(str)=='si'].iterrows():
            if str(p['lat'])=='' or str(p['lon'])=='':continue
            folium.Circle([float(p['lat']),float(p['lon'])],radius=int(p['radio_m']),color='#de8e29',fill=True,fill_opacity=.07,tooltip='Radio ilustrativo; no equivale a área de influencia').add_to(grupo)
        grupo.add_to(mapa)
    if ver_especies:
        grupo=folium.FeatureGroup(name='Puntos DEMOSTRATIVOS de especies')
        for ix,(_,e) in enumerate(especies.iterrows()):
            lat,lon=EJE[ix%len(EJE)]
            folium.CircleMarker([lat,lon],radius=7,color='#218f76',fill=True,fill_opacity=.85,tooltip=e['nombre']+' (punto demostrativo)').add_to(grupo)
        grupo.add_to(mapa)
    folium.LayerControl(collapsed=True).add_to(mapa)
    with main: st_folium(mapa,height=610,use_container_width=True,returned_objects=[])
    st.warning('IMPORTANTE: aún no se ha incorporado una capa oficial de influencia hidroecológica. Carga una geometría GeoJSON fundamentada o trabaja la delimitación en QGIS. Los círculos no representan impactos ambientales.')
    with st.expander('Cómo elaborar el área de influencia en QGIS'):
        st.markdown('1. Obtener el polígono oficial del santuario y la red hidrográfica/subcuencas.\n2. Definir conexiones hídricas y ecosistemas asociados con criterios justificables.\n3. Incorporar localidades e infraestructura como capa socio-territorial diferenciada.\n4. Exportar **GeoJSON EPSG:4326** y cargarlo en el visor.\n5. Documentar método, escala, fecha y fuentes.\n\nUn buffer uniforme solo sirve para una aproximación exploratoria, no equivale a un área de influencia ecológica oficial.')

elif pagina=='Proyectos e iniciativas':
    st.title('🏗️ Proyectos e iniciativas')
    st.write('Consulta instrumentos de manejo, proyectos comunitarios y registros preliminares de actividades territoriales. Cada ficha enlaza su fuente de consulta.')
    col1,col2,col3=st.columns([2,1,1])
    with col1:consulta=st.text_input('Buscar por nombre, descripción o responsable',placeholder='Ej.: gobernanza, restauración, Cau Cau')
    with col2:categoria=st.selectbox('Categoría',['Todas']+sorted(proyectos.categoria.unique().tolist()))
    with col3:solo_documentados=st.checkbox('Solo referencias documentales',False)
    seleccion=proyectos.copy()
    if consulta:
        cols=['nombre','categoria','descripcion','responsable']
        filtro=seleccion[cols].astype(str).apply(lambda col:col.str.contains(consulta,case=False,regex=False)).any(axis=1)
        seleccion=seleccion[filtro]
    if categoria!='Todas':seleccion=seleccion[seleccion.categoria==categoria]
    if solo_documentados:seleccion=seleccion[seleccion['nivel']=='Referencia documental']
    st.caption(f'{len(seleccion)} resultados · registro documental ≠ proyecto vigente ni impacto constatado')
    for _,p in seleccion.iterrows():
        with st.expander(('📖 ' if p['nivel']=='Referencia documental' else '⚠️ ')+str(p['nombre'])):
            st.markdown(f"**Categoría:** {p['categoria']}  ")
            st.markdown(f"**Tipo de registro:** {p['nivel']}  ")
            st.markdown(f"**Estado:** {p['estado']}  ")
            st.markdown(f"**Responsable:** {p['responsable']}  ")
            st.write(p['descripcion'])
            st.markdown(f"[Consultar documento o portal de origen]({p['fuente']})")
            st.caption('Ubicación cartográfica disponible solo cuando exista coordenada; las marcadas son aproximadas. Fuente consultada: ' + str(p['fecha_consulta']))
    st.download_button('Descargar catálogo CSV (incluye nivel de certeza)',proyectos.to_csv(index=False).encode('utf-8-sig'),file_name='proyectos_rio_cruces.csv',mime='text/csv')

elif pagina=='Conoce el humedal':
    st.title('🌿 Conoce el humedal')
    st.write('Un recorrido por los conceptos esenciales, con explicaciones sencillas y fuentes para profundizar.')
    tabs=st.tabs(['El humedal','Biodiversidad','El territorio','Preguntas frecuentes'])
    with tabs[0]:
        st.subheader('¿Por qué es importante?')
        st.write('Los humedales son ecosistemas donde el agua influye en los suelos, las plantas y los animales. Pueden albergar biodiversidad, retener sedimentos y aportar a la regulación del agua. Sus funciones varían según cada sitio.')
        st.markdown('**Santuario Río Cruces y Chorocamayo:** conoce su gestión en el [Plan de Manejo de CONAF](https://www.conaf.cl/centro-documental/pm-mn-y-sn-rio-cruces-y-chorocamayo-v-extendida/).')
    with tabs[1]:
        texto=st.text_input('Buscar una especie')
        resultados=especies[especies['nombre'].str.contains(texto,case=False,regex=False)]
        for _,e in resultados.iterrows():
            with st.expander(f"{e['emoji']} {e['nombre']} — {e['cientifico']}"):
                st.write(e['descripcion'])
                st.caption('Ficha educativa: no implica registro georreferenciado en el lugar dibujado en el mapa.')
                st.markdown(f"[Más información sobre la especie]({e['fuente']})")
    with tabs[2]:
        st.markdown('**Cuenca hidrográfica:** territorio cuyas aguas drenan hacia un mismo sistema.\n\n**Área protegida:** límite legal definido en su instrumento de creación.\n\n**Área de análisis territorial:** delimitación definida por un estudio; necesita objetivos y metodología.\n\n**Área de influencia de proyecto:** debe justificarse de acuerdo con el sistema ambiental y sus posibles efectos.')
    with tabs[3]:
        for pregunta,respuesta in [
            ('¿Un proyecto cercano daña necesariamente al santuario?','No. La proximidad es un antecedente espacial, pero no demuestra impactos ni relaciones causales.'),
            ('¿Qué diferencia hay entre DIA y EIA?','Ambas son vías de evaluación del SEIA con requisitos distintos. El instrumento no señala por sí solo si el proyecto fue aprobado.'),
            ('¿El mapa muestra áreas oficiales?','Solo cuando se cuenta con un archivo oficial y se verifica su origen. Las capas de referencia se etiquetan explícitamente.')]:
            with st.expander(pregunta):st.write(respuesta)

else:
    st.title('👥 Fuentes y participación')
    st.write('Transparencia para consultar los datos, revisar su calidad y aportar observaciones.')
    sitios=[('Plan de Manejo CONAF','https://www.conaf.cl/centro-documental/pm-mn-y-sn-rio-cruces-y-chorocamayo-v-extendida/'),('SIMBIO','https://simbio.mma.gob.cl/'),('SEIA','https://seia.sea.gob.cl/'),('SNIFA — SMA','https://snifa.sma.gob.cl/'),('Comunidad Humedal','https://www.comunidadhumedal.cl/biblioteca/'),('Centro de Humedales Río Cruces','https://cehum.org/'),('Mercado Público','https://www.mercadopublico.cl/')]
    for name,url in sitios:st.markdown(f'- [{name}]({url})')
    st.subheader('Qué significa cada nivel de información')
    st.markdown('**Referencia documental:** existe una fuente específica sobre la iniciativa, pero su estado actual puede requerir confirmación.\n\n**Pendiente de verificación:** ficha de trabajo sin suficientes documentos para comprobar su contenido.\n\n**Ilustrativo:** elemento visual que no representa coordenadas ni delimitaciones oficiales.')
    st.subheader('Prepara un aporte ciudadano')
    st.caption('Este formulario no envía información a un servidor ni publica datos. Genera un archivo para compartir con el equipo que administra el visor.')
    with st.form('aporte'):
        tipo=st.selectbox('¿Qué deseas aportar?',['Corrección de un dato','Documento o iniciativa','Sugerencia de accesibilidad','Otro'])
        descripcion=st.text_area('Cuéntanos tu sugerencia (sin datos personales sensibles)')
        url=st.text_input('Enlace a la fuente, si existe')
        enviar=st.form_submit_button('Preparar archivo de aporte')
    if enviar:
        if not descripcion.strip():st.error('Completa la descripción.')
        else:
            archivo=json.dumps({'tipo':tipo,'descripcion':descripcion,'fuente':url},ensure_ascii=False,indent=2)
            st.success('Archivo preparado. No se ha enviado automáticamente.')
            st.download_button('Descargar sugerencia',archivo,file_name='aporte_visor.json',mime='application/json')

st.divider()
st.caption('Visor territorial ciudadano · Prototipo académico · Verifica fechas, geometrías y estados en las fuentes originales. No sustituye información ambiental oficial.')
