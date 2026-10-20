# Visor territorial ciudadano — Santuario Río Cruces

Prototipo académico desarrollado con Streamlit y Folium. Los datos están en revisión.

## Estructura
- `app.py`: aplicación Streamlit.
- `requirements.txt`: bibliotecas que instala Streamlit Cloud.
- `assets/portada_humedal.jpg`: ilustración de portada (reemplazar por foto autorizada y atribuir autoría).
- `data/proyectos.csv`: proyectos y antecedentes; se pueden ampliar en una hoja de cálculo.
- `data/especies.csv`: fichas educativas.

## Publicación en GitHub + Streamlit Cloud
1. Subir los archivos y las carpetas conservando la estructura.
2. En Streamlit Cloud elegir repositorio y `app.py` como archivo principal.
3. Dejar que Streamlit instale las dependencias de `requirements.txt`.
4. Agregar un GeoJSON oficial del santuario y un GeoJSON justificado del área de análisis.
5. Corroborar coordenadas y expedientes antes de usar información como oficial.

## Agregar datos
Agregar filas en los CSV sin cambiar nombres de columnas. `mostrar_mapa=si` requiere `lat`, `lon`, `radio_m` numéricos. El radio es **solo ilustrativo** y está desactivado por defecto.

## Estado de los datos
Las iniciativas documentales tienen enlace a su fuente. El estado de ejecución actual requiere revisión. Los cuatro puntos del código original son **no verificados**. No son evidencia de impacto ambiental.

## Mejoras futuras
Incorporar geometrías oficiales de cuenca/subcuencas, secciones de descarga SIG, fechas automáticas de verificación de fuentes y backend moderado para participación.


## Fotografías y responsabilidad editorial
Las fotos recibidas se incluyen como **material de trabajo**. Antes de difundir públicamente, verifica autor, procedencia, licencia o permiso y crédito de cada imagen. Las fotos no prueban presencia georreferenciada. La foto de vegetación emergente no se identifica taxonómicamente como totora sin verificación adicional.

## Función ecológica de especies
Las columnas `funcion_ecologica`, `como_cuidarla` y `evidencia_local` permiten contar por qué importa cada especie y cómo se relaciona con la protección del santuario. Los textos son divulgativos y requieren apoyo bibliográfico específico antes de publicación académica.
