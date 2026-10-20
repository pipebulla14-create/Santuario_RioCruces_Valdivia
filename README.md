# Visor territorial ciudadano — Santuario Río Cruces

Proyecto académico en **Python + Streamlit + Folium**. Esta versión usa las fotos proporcionadas en el chat y los logotipos remitidos por el usuario. Su inclusión es **referencial** y no significa respaldo oficial de la UACh. Confirmar permiso de uso y créditos de cada imagen antes de publicar.

## Cómo actualizar GitHub

1. Descarga y descomprime el ZIP.
2. En el repositorio, reemplaza **app.py** y **requirements.txt** en la raíz.
3. Sube la carpeta **.streamlit/config.toml** (incluido el punto inicial en el nombre de la carpeta).
4. Sube los archivos de **assets/** y **data/** conservando nombres, incluyendo `portada_humedal.jpg`, `logo_uach.png`, `logo_escuela_geografia.png`, `especies.csv` y `proyectos.csv`.
5. Confirma cambios con **Commit changes**. Streamlit Community Cloud debería redesplegar automáticamente si está conectado a la rama `main`.
6. Revisa **Manage app → Logs** si algo falla. No subas tokens ni contraseñas.

## Cuenca hidrográfica

No se inventan límites. Descargar el polígono de la **Subcuenca Río Cruces** en [SIMBIO](https://simbio.mma.gob.cl/Subcuencas/Details/1013) o la [Mapoteca DGA](https://dga.mop.gob.cl/mapoteca-digital/). Convertir en QGIS a **GeoJSON EPSG:4326**, comprobar la geometría y guardar como `data/cuenca_rio_cruces.geojson`. El visor también permite carga manual.

## Datos, imágenes y fuentes

- `data/especies.csv` contiene las fichas, roles ecológicos y fuentes.
- `data/proyectos.csv` contiene referencias documentales y registros preliminares, **no una lista de impactos confirmados**.
- Imágenes en `assets/` son ilustrativas; no constituyen prueba de presencia local de fauna.
- Fotos recibidas sin licencia/crédito confirmado: revisar atribución antes de publicar. La imagen aérea conserva su marca de agua original, que no debe eliminarse para ocultar atribución.
- Logos universitarios son elementos referenciales del prototipo; consultar autorización de uso institucional para una publicación oficial.

## Instalación local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Archivos

```
app.py
requirements.txt
.streamlit/config.toml
assets/*.jpg, assets/*.png
data/especies.csv, data/proyectos.csv
```
