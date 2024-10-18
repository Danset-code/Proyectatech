import streamlit as st
import psycopg2
import pandas as pd
import folium
from streamlit_folium import st_folium


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
    
    # Mostrar solo los datos relevantes del ubicacion
    st.write(f"Se han encontrado {len(df_filtrado)} registros en la Ubicacion seleccionada.")

    # Verifica que las columnas existan en el DataFrame
    if "area_privada" in df_filtrado.columns and "precio" in df_filtrado.columns and "descripcion" in df_filtrado.columns and "estrato" in df_filtrado.columns and "img_src" in df_filtrado.columns and "admin_price" in df_filtrado.columns and "bathrooms" in df_filtrado.columns and "lat" in df_filtrado.columns and "lon" in df_filtrado.columns and "titulo" in df_filtrado.columns and "sector" in df_filtrado.columns and "contact" in df_filtrado.columns:
        #st.subheader(f"Datos del Inmueble: {barrio_seleccionado}")

        # Iterar sobre las tres columnas simultáneamente
        for index, (area, precio, descripcion, estrato, imagen, lat, lon, admin_price, bathrooms, titulo, sector, contact) in enumerate(zip(df_filtrado["area_privada"], df_filtrado["precio"], df_filtrado["descripcion"], df_filtrado["estrato"], df_filtrado["img_src"], df_filtrado["lat"], df_filtrado["lon"], df_filtrado["admin_price"], df_filtrado["bathrooms"], df_filtrado["sector"], df_filtrado["titulo"], df_filtrado["contact"]), start=1):
            st.subheader(f"{titulo}")
            st.write(f"{sector}")
            st.write(f"  Área privada: {area}")
            st.write(f"  Precio: {precio} COP")
            st.write(f"  Estrato: {estrato}")

            if admin_price != '[null]':
                st.write(f"  Admin precio: {admin_price}")
            if bathrooms != '[null]':
                st.write(f"  Baños: {bathrooms}")
            
            st.write(f"  Contacto: {contact}")

            if descripcion != None:
                st.write(f"  Descripción: {descripcion}")

            st.image(imagen, caption=f"Imagen del Registro {index}", use_column_width=True)

            if lat != 0 and lon != 0:
    
                mapa = folium.Map(location=[lat, lon], zoom_start=16)
                
                # Agregar un marcador en la ubicación
                folium.Marker([lat, lon], popup=f"Registro {index}: {descripcion}").add_to(mapa)
                
                # Mostrar el mapa con folium en Streamlit
                st_folium(mapa, width=700, height=400)

else:
    st.info("Selecciona un barrio para ver los datos correspondientes.")
