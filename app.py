import streamlit as st
import psycopg2
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image
import requests
from io import BytesIO
import base64
import requests

st.set_page_config(layout="wide")


def obtener_puntos_interes(lat, lon, radio):
    # Construir la consulta Overpass
    query = f"""
    [out:json];
    (
      node(around:{radio},{lat},{lon});
      way(around:{radio},{lat},{lon});
      relation(around:{radio},{lat},{lon});
    );
    out body;
    """
    
    # Hacer la solicitud a la Overpass API
    response = requests.get("http://overpass-api.de/api/interpreter", params={'data': query})
    
    if response.status_code == 200:
        data = response.json()
        lugares = []
        for element in data['elements']:
            if 'tags' in element:
                # Extraer solo las etiquetas highway, amenity y shop
                etiquetas = {k: v for k, v in element['tags'].items() if k in ['highway', 'amenity', 'shop']}
                
                # Verifica si hay etiquetas relevantes
                if etiquetas:  # Solo agregar si tiene alguna de estas etiquetas
                    # Verificar si el nodo es un bus_stop
                    if etiquetas.get('highway') == 'bus_stop':
                        nombre = element['tags'].get('name', 'Sin nombre')
                    elif 'amenity' in etiquetas or 'shop' in etiquetas:
                        # Obtener el nombre del lugar, si existe
                        nombre = element['tags'].get('name', 'Sin nombre')
                    else:
                        continue  # Saltar si no es bus_stop, amenity o shop
                    
                    lugar = {
                        'nombre': nombre,  # Usar el nombre que se encuentre
                        'lat': element.get('lat'),
                        'lon': element.get('lon'),
                        'tags': etiquetas
                    }
                    lugares.append(lugar)
        
        return lugares
        return data['elements']
    else:
        st.error("Error al obtener datos de la Overpass API.")
        return None

def mostrar_imagen_con_flechas(imagenes_urls, max_alto=400, max_ancho=600):
    if len(imagenes_urls) > 0:
        # Inicializar el índice de la imagen en st.session_state si no existe
        if 'imagen_index' not in st.session_state:
            st.session_state.imagen_index = 0
        
        # Contenedor para los botones de navegación
        col1, col2 = st.columns([0.1, 0.1])

        with col1:
            if st.button("←", key=f"anterior_{index}", use_container_width=True):
                # Navegar hacia la imagen anterior
                if st.session_state.imagen_index > 0:
                    st.session_state.imagen_index -= 1
                # Forzar la actualización de la imagen mostrada

        with col2:
            if st.button("→", key=f"siguiente_{index}", use_container_width=True):
                # Navegar hacia la imagen siguiente
                if st.session_state.imagen_index < len(imagenes_urls) - 1:
                    st.session_state.imagen_index += 1
                # Forzar la actualización de la imagen mostrada
        # Mostrar la imagen actual
        mostrar_imagen_ajustada(imagenes_urls[st.session_state.imagen_index], max_alto, max_ancho)
    else:
        st.write("No hay imágenes disponibles para esta propiedad.")

# Función para cargar la imagen desde URL y ajustar su tamaño si es necesario
def mostrar_imagen_ajustada(imagen_url, max_alto, max_ancho=500):
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
    img_base64 = base64.b64encode(img_bytes.read()).decode()

    # Mostrar la imagen centrada con HTML en Streamlit
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center">
            <img src="data:image/png;base64,{img_base64}" style="width: {nuevo_ancho}px; height: {nuevo_alto}px;">
        </div>
        
        <div id="modal" style="display:none; position:fixed; z-index: 200; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.9);">
            <span onclick="document.getElementById('modal').style.display='none'" 
                  style="color: white; float: right; font-size: 40px; font-weight: bold; cursor: pointer;">&times;</span>
            <img id="modal-img" style="margin: auto; display: block; width: auto; max-width: 90%; max-height: 90%; margin-top: 5%;">
        </div>
        """, 
        unsafe_allow_html=True
    )  

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

# Título de la aplicación uno
st.title("Buscar Local")

st.write("Acá podrás encontrar las mejores ofertas para arrendar local, obtener información completa, al lugar y poder mirar la zona que mas te llame la atención, ten encuenta todos los aspectos para que asi puedas poyectar tus oportunidades de crecimiento como empresa y como emprendedor, puedes filtrar por la ubicacion")

# Parámetros de conexión a la base de datos en Railway
@st.cache_resource
def init_connection():
    try:
        conn = psycopg2.connect(
            #host="autorack.proxy.rlwy.net",
            #user="postgres",  # Cambia esto según tu configuración
            #password="rJmaVfPPjUZARaPzwemDoMDvengICOrS",  # Cambia esto según tu configuración
            #dbname="railway",
            #port="33601"
            host="localhost",
            user="postgres",  # Cambia esto según tu configuración
            password="Danset01*",  # Cambia esto según tu configuración
            dbname="hackaton",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

conn = init_connection()

# Función para ejecutar consultas y obtener datos
@st.cache_data(ttl=600)  # Cachear por 10 minutos
def obtener_datos(query):
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            datos = cur.fetchall()
            columnas = [desc[0] for desc in cur.description]
            return pd.DataFrame(datos, columns=columnas)
    except psycopg2.Error as e:
        # Si ocurre un error en la transacción, se hace rollback
        conn.rollback()  # Importante: deshacer la transacción fallida
        st.error(f"Ocurrió un error al ejecutar la consulta: {e}")
        return pd.DataFrame()  # Retornar un DataFrame vacío para evitar que falle el flujo

# Consulta inicial para cargar todos los datos (incluyendo los ubicacion)
consulta_default = "SELECT * FROM propiedades LIMIT 100;"  # Cambia el límite o quítalo según tu preferencia
df = obtener_datos(consulta_default)

def obtener_imagenes(propiedad_id):
    query = f"SELECT url FROM imagenes WHERE propiedad_id={propiedad_id};"
    return obtener_datos(query)["url"].tolist()

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
    puntos_interes_lista = []
    
    # Reiniciar el índice de la imagen solo si es una nueva selección
    if 'previous_selection' not in st.session_state or st.session_state.previous_selection != barrio_seleccionado:
        st.session_state.imagen_index = 0  # Reinicia el índice al seleccionar una nueva ubicación
        
        # Reiniciar los estados de los expanders
        st.session_state.expanders = {f"expander_{index}": False for index in range(len(df_filtrado))}
        st.session_state.previous_selection = barrio_seleccionado  # Actualizar la selección anterior
    
    if 'max_image_width' not in st.session_state:
            st.session_state.max_image_width = 400
    
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

        # Iterar sobre las tres columnas simultáneamente
        for index, (area, precio, descripcion, estrato, imagen, lat, lon, 
                    admin_price, bathrooms, titulo, sector, contact, id_propiedad) in enumerate(zip(df_filtrado["area_privada"], df_filtrado["precio"], df_filtrado["descripcion"], df_filtrado["estrato"], 
                                                                                                    df_filtrado["img_src"], df_filtrado["lat"], df_filtrado["lon"], df_filtrado["admin_price"], 
                                                                                                    df_filtrado["bathrooms"], df_filtrado["sector"], df_filtrado["titulo"], df_filtrado["contact"],
                                                                                                    df_filtrado["id"]), start=1):
            imagenes_urls = obtener_imagenes(id_propiedad)
            cols = st.columns([1, 2, 0.5])
            
            with cols[0]:
                mostrar_imagen_ajustada(imagen, max_alto=300)
                
            with cols[1]:
                st.subheader(f"{titulo}")
                st.write(f"  **Precio:** {precio} COP")
                st.write(f"  **Estrato:** {estrato}")
                st.write(f"  **Area total:** {area}")
                #st.markdown(f"<p style='font-size:21px;'><b>Precio: </b>{precio}</p>", unsafe_allow_html=True)
                #st.markdown(f"<p style='font-size:21px;'><b>Estrato: </b>{estrato}</p>", unsafe_allow_html=True)
                #st.markdown(f"<p style='font-size:21px;'><b>Area Privada: </b>{area}</p>", unsafe_allow_html=True)
                if admin_price!= '[null]':
                    formateado = "${:,.0f}".format(int(admin_price)).replace(",", ".")
                    st.write(f"  **Precio Administracion:** {formateado}")
                    #st.markdown(f"<p style='font-size:21px;'><b>Precio administracion: </b>${formateado} COP</p>", unsafe_allow_html=True)
                if bathrooms!= '[null]':
                    st.write(f"  **Precio:** {bathrooms}")
                    #st.markdown(f"<p style='font-size:21px;'><b>Baños: </b>{bathrooms}</p>", unsafe_allow_html=True)
            
            with cols[2]:
                expander_key = f"expander_{index}"
        
                # Inicializar el estado del expander si no existe
                if expander_key not in st.session_state.expanders:
                    st.session_state.expanders[expander_key] = False

                # Botón para ver más detalles
                if st.button("Ver detalles", key=f"details_{index}"):
                    # Cambiar el estado del expander
                    st.session_state.expanders[expander_key] = not st.session_state.expanders[expander_key]

            # Mostrar el expander si el estado es True
            if st.session_state.expanders[expander_key]:
                with st.expander(f"Detalles de {titulo}", expanded=True):
                    st.write(f"  **Precio:** {contact} COP")
                    #st.markdown(f"<p style='font-size:21px;'><b>Contacto:</b> {contact}</p>", unsafe_allow_html=True)
                    
                    if descripcion:
                        st.write(f"  **Descripcion:** {descripcion}")
                        #st.markdown(f"<p style='font-size:18px;'><b>Descripción:</b> {descripcion}</p>", unsafe_allow_html=True)
                        
                    cols = st.columns([1, 1])
                    
                    with cols[0]:
                        mostrar_imagen_con_flechas(imagenes_urls)

                    with cols[1]:
                        # Luego en tu parte donde muestras el mapa
                        if lat != 0 and lon != 0:
                            # Definir el radio de búsqueda en metros
                            radio_busqueda = 200  # Cambia esto según tus necesidades
                            
                            amenidades = obtener_puntos_interes(lat, lon, radio=radio_busqueda)
                            
                            # Crear el mapa
                            mapa = folium.Map(location=[lat, lon], zoom_start=18)

                            # Agregar el marcador para la propiedad
                            folium.Marker([lat, lon], popup=f"Registro {index}: {titulo}", icon=folium.Icon(color='blue')).add_to(mapa)
                            
                            elementos_unicos = set()

                            # Procesar los resultados y extraer las etiquetas clave-valor solo para highway, amenity, y shop
                            for lugar in amenidades:
                                # Extraer etiquetas clave-valor solo para 'highway', 'amenity', y 'shop'
                                etiquetas = lugar.get('tags', {})
                                nombre = lugar.get('nombre').upper()
                                lat_punto = lugar.get('lat')
                                lon_punto = lugar.get('lon')
                                
                                print(etiquetas)
                                 # Definir un identificador único basado en las etiquetas que te interesan
                                identificador = (nombre, frozenset(etiquetas.items())) # Usar frozenset para poder almacenar en el set
                                
                                # Si el identificador ya está en el conjunto, saltar este elemento para evitar duplicados
                                if identificador in elementos_unicos:
                                    continue
                                
                                # Si no es un duplicado, agregar el identificador al conjunto
                                elementos_unicos.add(identificador)
                                
                                # Asignar un color basado en la etiqueta
                                if 'amenity' in etiquetas:
                                    color = 'green'  # Color para amenity
                                elif 'highway' in etiquetas:
                                    color = 'gray'  # Color para highway
                                elif 'shop' in etiquetas:
                                    color = 'orange'  # Color para shop
                                else:
                                    color = 'gray'  # Color predeterminado para otros casos
                                
                                # Agregar a la lista de puntos de interés solo las etiquetas relevantes
                                for clave, valor in etiquetas.items():
                                    if clave in ['amenity', 'highway', 'shop']:  # Solo incluir las etiquetas deseadas
                                        puntos_interes_lista.append([nombre, lat_punto, lon_punto, clave, valor])
                                    
                                    if lat_punto and lon_punto:
                                        # Agregar un marcador para cada centro comercial
                                        folium.Marker([lat_punto, lon_punto], popup=nombre, icon=folium.Icon(color=color)).add_to(mapa)

                        # Mostrar el mapa en Streamlit
                        st_folium(mapa, width=500, height=400)

                        # Convertir la lista a un DataFrame para visualización
                        df_puntos_interes = pd.DataFrame(puntos_interes_lista, columns=['Nombre', 'Latitud', 'Longitud', 'Etiqueta', 'Valor'])
                        
                        # Eliminar filas duplicadas en función de las columnas 'Nombre' y 'Valor'
                        df_puntos_interes_unicos = df_puntos_interes.drop_duplicates(subset=['Nombre', 'Valor'])
                    
                        excluir_etiquetas = ['footway', 'service', 'crossing', 'cycleway', 'tertiary', 'traffic_signals', 'turning_circle', 'trunk_link', 'steps','primary_link', 'pedestrian', 'secondary_link']
                        df_filtrado = df_puntos_interes[~df_puntos_interes['Valor'].isin(excluir_etiquetas)]
                        

                if lat != 0 and lon != 0:
                    # Mostrar la tabla en Streamlit
                    with st.expander("Ver puntos de interés cercanos"):
                        st.write("Aquí tienes la lista de puntos de interés:")
                        st.table(df_filtrado)  
            st.markdown("---")            
else:
    st.info("Selecciona un barrio para ver los datos correspondientes.")
