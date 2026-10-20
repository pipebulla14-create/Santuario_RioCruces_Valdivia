# Incorporar subcuenca Río Cruces al visor

1. Descarga la subcuenca **Río Cruces**, **código BNA 1013**, desde https://simbio.mma.gob.cl/Subcuencas/Details/1013 (KMZ o Shapefile), o desde la Mapoteca DGA: https://dga.mop.gob.cl/mapoteca-digital/.
2. Si descargas un SHP, descomprime todos sus componentes (SHP, SHX, DBF, PRJ), ábrelo en QGIS y filtra por código BNA **1013**. Verifica la columna exacta del código según el archivo.
3. Exporta exclusivamente la subcuenca seleccionada como **GeoJSON**, sistema **EPSG:4326 / WGS84**.
4. Ponle el nombre `cuenca_rio_cruces.geojson` y súbelo a `data/` en GitHub, o cárgalo mediante el selector de archivos de la app.
5. Documenta fuente, año, escala, método y fecha de descarga; no confundas subcuenca con área de influencia legal.

También puedes descargar la hidrografía desde https://ide.mma.gob.cl/centro-de-descargas.
