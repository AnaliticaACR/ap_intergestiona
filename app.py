import streamlit as st
import pandas as pd

@st.cache_data
def cargar_datos():
    return pd.read_parquet("https://raw.githubusercontent.com/williamCastro32/Coor_datos/main/app_datos/gestiones_interg-parquet")
    
# 1. Título de la aplicación
st.title("Búsqueda de Información por Cédula")

# 2. Cargar el DataFrame
df = cargar_datos()
df.set_index("CEDULA", inplace=True)

# 3. Input para buscar por ID
st.write("### Buscar información por ID:")
input_id = st.text_input("Introduce el ID:", value="")

# 4. Filtrar y mostrar resultados
if input_id:
    try:
        input_id = int(input_id)
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
            st.warning("No se encontró información para el ID proporcionado.")
    except ValueError:
        st.error("Por favor, introduce un Cedula válido (número).")

# Pie de página opcional
st.write("---")
st.write("Aplicación creada para Intergestiona.")