import streamlit as st
import psycopg2
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image
import requests
from io import BytesIO

import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Función para cargar la imagen desde URL y ajustar su tamaño si es necesario
def mostrar_imagen_ajustada(imagen_url, max_alto, max_ancho=400):
    # Cargar la imagen desde la URL
    response = requests.get(imagen_url)
    img = Image.open(BytesIO(response.content))

    # Obtener las dimensiones de la imagen
    ancho_original, alto_original = img.size

    # Verificar si es necesario redimensionar
    if ancho_original > max_ancho or alto_original > max_alto:
        # Calcular la proporción para mantener el aspecto
        proporción_ancho = max_ancho / float(ancho_original)
        proporción_alto = max_alto / float(alto_original)
        
        # Elegir la proporción que mantenga la imagen dentro de los límites
        proporción = min(proporción_ancho, proporción_alto)
        
        # Calcular el nuevo tamaño basado en la proporción elegida
        nuevo_ancho = int(ancho_original * proporción)
        nuevo_alto = int(alto_original * proporción)
        
        # Redimensionar la imagen
        img = img.resize((nuevo_ancho, nuevo_alto))

    # Guardar la imagen en un archivo temporal
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Mostrar la imagen centrada con HTML en Streamlit
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center;">
            <img src="{imagen_url}" style="width: {nuevo_ancho}px; height: {nuevo_alto}px;">
        </div>
        """, 
        unsafe_allow_html=True
    )

    
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .banner {
        background-color: #337aff;
        color: white;
        padding: 10px;
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;    
    }
    </style>
    <div class="banner">
        Proyectatech
    </div>
    """, unsafe_allow_html=True)

# Título de la aplicación
st.title("Buscar Local")

st.write("Acá podrás encontrar las mejores ofertas para arrendar local, obtener información completa, al lugar y poder mirar la zona que mas te llame la atención, ten encuenta todos los aspectos para que asi puedas poyectar tus oportunidades de crecimiento como empresa y como emprendedor, puedes filtrar por la ubicacion")

# Parámetros de conexión a la base de datos en Railway
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host="autorack.proxy.rlwy.net",
        user="postgres",  # Cambia esto según tu configuración
        password="rJmaVfPPjUZARaPzwemDoMDvengICOrS",  # Cambia esto según tu configuración
        dbname="railway",
        port="33601"
    )

conn = init_connection()

# Función para ejecutar consultas y obtener datos
@st.cache_data(ttl=600)  # Cachear por 10 minutos
def obtener_datos(query):
    with conn.cursor() as cur:
        cur.execute(query)
        datos = cur.fetchall()
        columnas = [desc[0] for desc in cur.description]
        return pd.DataFrame(datos, columns=columnas)

# Consulta inicial para cargar todos los datos (incluyendo los ubicacion)
consulta_default = "SELECT * FROM propiedades LIMIT 100;"  # Cambia el límite o quítalo según tu preferencia
df = obtener_datos(consulta_default)

df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

logo_path = "logo.png"

st.sidebar.image(logo_path, width=250)  # Ajusta el ancho según lo necesites

# Sidebar para filtrar por ubicacion
st.sidebar.header("Empieza Seleccionando")

# Crear un selector de ubicacion basado en los valores únicos de la columna "ubicacion"
barrios = df["barrio"].unique().tolist()  # Obtener las ubicaciones únicas
barrios.sort()
barrios.insert(0, "Seleccionar Ubicacion")  # Agregar opción "Seleccionar ubicacion"
barrio_seleccionado = st.sidebar.selectbox("Selecciona una Ubicacion:", barrios)

# Mostrar los datos solo si se ha seleccionado un ubicacion diferente a "Seleccionar ubicacion"
if barrio_seleccionado != "Seleccionar Ubicacion":
    # Filtrar los datos por el ubicacion seleccionado
    df_filtrado = df[df["barrio"] == barrio_seleccionado]
    
    if 'expanders' not in st.session_state:
        st.session_state.expanders = {}
    
    if 'previous_selection' not in st.session_state or st.session_state.previous_selection != barrio_seleccionado:
        st.session_state.expanders = {f"expander_{index}": False for index in range(len(df_filtrado))}

    st.session_state.previous_selection = barrio_seleccionado
    
    # Mostrar solo los datos relevantes del ubicacion
    st.write(f"Se han encontrado {len(df_filtrado)} registros en la Ubicacion seleccionada.")

    # Verifica que las columnas existan en el DataFrame
    if "area_privada" in df_filtrado.columns and "precio" in df_filtrado.columns and "descripcion" in df_filtrado.columns and "estrato" in df_filtrado.columns and "img_src" in df_filtrado.columns and "admin_price" in df_filtrado.columns and "bathrooms" in df_filtrado.columns and "lat" in df_filtrado.columns and "lon" in df_filtrado.columns and "titulo" in df_filtrado.columns and "sector" in df_filtrado.columns and "contact" in df_filtrado.columns:
        #st.subheader(f"Datos del Inmueble: {barrio_seleccionado}")
            
        if 'max_image_width' not in st.session_state:
            st.session_state.max_image_width = 400
            
            # Reiniciar el estado de los expanders
        if 'previous_selection' not in st.session_state or st.session_state.previous_selection != barrio_seleccionado:
            for index in range(len(df_filtrado)):
                expander_key = f"expander_{index}"
                st.session_state.expanders[expander_key] = False
        st.session_state.previous_selection = barrio_seleccionado

        # Iterar sobre las tres columnas simultáneamente
        for index, (area, precio, descripcion, estrato, imagen, lat, lon, admin_price, bathrooms, titulo, sector, contact) in enumerate(zip(df_filtrado["area_privada"], df_filtrado["precio"], df_filtrado["descripcion"], df_filtrado["estrato"], df_filtrado["img_src"], df_filtrado["lat"], df_filtrado["lon"], df_filtrado["admin_price"], df_filtrado["bathrooms"], df_filtrado["sector"], df_filtrado["titulo"], df_filtrado["contact"]), start=1):
            #st.subheader(f"{titulo}")
            #st.write(f"{sector}")
            #st.write(f"  Área privada: {area}")
            #st.write(f"  Precio: {precio} COP")
            #st.write(f"  Estrato: {estrato}")
            #if admin_price != '[null]':
                #st.write(f"  Admin precio: {admin_price}")
            #if bathrooms != '[null]':
            #    st.write(f"  Baños: {bathrooms}")
            
            cols = st.columns([1, 2, 1])
            
            with cols[0]:
                mostrar_imagen_ajustada(imagen, max_alto=300)
                
            with cols[1]:
                st.subheader(f"{titulo}")
                st.write(f"  Precio: {precio} COP")
                st.write(f"  Estrato: {estrato}")
                st.write(f"  Área privada: {area}")
                if admin_price!= '[null]':
                    st.write(f"  Admin precio: {admin_price}")
                if bathrooms!= '[null]':
                    st.write(f"  Baños: {bathrooms}")
            
            with cols[2]:
                expander_key = f"expander_{index}"
                expander_key = f"expander_{index}"
        
                # Inicializar el estado del expander si no existe
                if expander_key not in st.session_state.expanders:
                    st.session_state.expanders[expander_key] = False

                # Botón para ver más detalles
                if st.button(f"Ver detalles {index}"):
                    # Cambiar el estado del expander
                    st.session_state.expanders[expander_key] = not st.session_state.expanders[expander_key]

            # Mostrar el expander si el estado es True
            if st.session_state.expanders[expander_key]:
                with st.expander(f"Detalles de {titulo}", expanded=True):
                    st.write(f"**Contacto:** {contact}")
                    if descripcion:
                        st.write(f"**Descripción:** {descripcion}")
                    
                    cols = st.columns([1, 2])
                    with cols[0]:
                        mostrar_imagen_ajustada(imagen, st.session_state.max_image_width)

                    with cols[1]:
                        if lat != 0 and lon != 0:
                            mapa = folium.Map(location=[lat, lon], zoom_start=16)
                            folium.Marker([lat, lon], popup=f"Registro {index}: {descripcion}").add_to(mapa)
                            st_folium(mapa, width=500, height=400)
                        
            st.markdown("---")                 

else:
    st.info("Selecciona un barrio para ver los datos correspondientes.")
