import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import pymysql # Necesario para que SQLAlchemy sepa cómo conectarse a MySQL

# --- Constantes (reemplaza si es necesario) ---
# El nombre de la tabla en tu base de datos MySQL
MYSQL_TABLE_NAME = st.secrets["connections"]["mysql"].get("table_name", "gestiones_interg") # Usa el nombre de la tabla de secrets o por defecto

# 1. Título de la aplicación
st.title("Búsqueda de Información por Cédula")

# ----------------------------------------------------------------------
# Modificaciones para leer desde MySQL
# ----------------------------------------------------------------------

# @st.cache_resource para la conexión de la base de datos
# Esto es importante porque los objetos de conexión no son directamente serializables
# y queremos reutilizar la misma conexión a través de las ejecuciones de la aplicación.
# ttl=3600 (1 hora) significa que la conexión se reestablecerá cada hora,
# asegurando que cualquier cambio en la configuración de la BD se refleje
@st.cache_resource(ttl=3600)
def get_db_connection():
    try:
        # Recupera las credenciales de st.secrets
        db_config = st.secrets["connections"]["mysql"]
        
        # Crea la cadena de conexión para SQLAlchemy
        # Asegúrate de que el driver pymysql esté instalado
        connection_string = (
            f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        
        engine = create_engine(connection_string)
        st.success("Conexión a MySQL establecida.")
        return engine
    except Exception as e:
        st.error(f"Error al conectar a la base de datos MySQL: {e}")
        st.warning("Asegúrate de que las credenciales en `.streamlit/secrets.toml` sean correctas y que la base de datos sea accesible.")
        return None

# @st.cache_data para cargar los datos
# ttl=3600 (1 hora) significa que los datos se recargarán desde la BD como máximo cada hora.
# Esto sincroniza con tu pipeline de actualización horaria.
@st.cache_data(ttl=3600)
def cargar_datos_desde_mysql():
    engine = get_db_connection()
    if engine is None:
        return pd.DataFrame() # No se pudo conectar a la BD
    
    try:
        # Carga todos los datos de la tabla
        # Asegúrate de que 'gestiones_interg' es el nombre correcto de tu tabla
        query = f"SELECT * FROM {MYSQL_TABLE_NAME}"
        df = pd.read_sql(query, engine)
        st.info(f"Datos cargados de MySQL. Filas: {len(df)}")
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos desde MySQL: {e}")
        return pd.DataFrame() # Devuelve un DataFrame vacío en caso de error


# 2. Cargar el DataFrame
df = cargar_datos_desde_mysql()

# Manejar el caso de DataFrame vacío después de la carga
if df.empty:
    st.warning("No se pudieron cargar los datos o el DataFrame está vacío. Por favor, revisa la conexión y el nombre de la tabla.")
    st.stop() # Detiene la ejecución para evitar errores si df está vacío

# Asegúrate de que "CEDULA" existe antes de establecer el índice
if "CEDULA" in df.columns:
    df.set_index("CEDULA", inplace=True)
else:
    st.error("La columna 'CEDULA' no se encontró en los datos. Por favor, verifica el esquema de tu tabla MySQL.")
    st.stop()


# 3. Input para buscar por ID
st.write("### Buscar información por ID:")
input_id = st.text_input("Introduce el ID:", value="")

# 4. Filtrar y mostrar resultados
if input_id:
    try:
        input_id = int(input_id)
        # Buscar directamente en el DataFrame en memoria (ya cargado)
        result = df.loc[[input_id]] if input_id in df.index else pd.DataFrame()
        
        if not result.empty:
            st.write("### Información encontrada:")
            
            # Tabla que ocupa todo el ancho con formato de números enteros
            st.dataframe(
                result, 
                use_container_width=True,  # Ocupa todo el ancho disponible
                column_config={
                    col: st.column_config.NumberColumn(format="%d") 
                    for col in result.select_dtypes(include=['float64', 'float32', 'int64']).columns
                }
            )
        else:
            st.warning(f"No se encontró información para el ID: {input_id}.")
    except ValueError:
        st.error("Por favor, introduce un ID válido (número entero).")
    except KeyError:
        st.error(f"El ID {input_id} no se encontró en el índice del DataFrame.")

# Pie de página opcional
st.write("---")
st.write("Aplicación creada para Intergestiona.")