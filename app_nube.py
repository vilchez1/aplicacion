import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Control de Repuestos", page_icon="🚗")
st.title("🚗 Sistema de Gestión (Nube)")

# PEGA AQUÍ EL ENLACE DE TU GOOGLE SHEET (Debe estar público como Editor)
url_google_sheet = "https://docs.google.com/spreadsheets/d/1at2vT2V6wY9AE2syGKj777CMqom7NlUdoMsYQi8z_aY/edit?usp=sharing"

# --- CONEXIÓN CON GOOGLE SHEETS ---
# Establecemos la conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para leer los datos
def cargar_datos():
    # ttl=0 significa que no guarde caché, que lea siempre los datos frescos
    return conn.read(spreadsheet=url_google_sheet, usecols=[0, 1, 2, 3, 4, 5], ttl=0)

# Función para guardar datos
def guardar_datos(nuevo_df):
    conn.update(spreadsheet=url_google_sheet, data=nuevo_df)

# --- INTERFAZ ---

menu = ["Ver Inventario", "Registrar Nuevo"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# Cargamos los datos actuales de la nube
try:
    df = cargar_datos()
    # Aseguramos que los números sean números y no texto
    df['precio'] = pd.to_numeric(df['precio'], errors='coerce').fillna(0)
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0).astype(int)
except Exception as e:
    st.error(f"Error al conectar con la hoja. Asegúrate de que el enlace sea correcto y esté público como Editor. Detalle: {e}")
    df = pd.DataFrame(columns=["codigo", "nombre", "modelo_auto", "marca", "precio", "cantidad"])

# 1. VER INVENTARIO
if choice == "Ver Inventario":
    st.subheader("Inventario en la Nube")
    
    if df.empty:
        st.info("La hoja está vacía.")
    else:
        st.dataframe(df, use_container_width=True)
        
        # Buscador simple
        busqueda = st.text_input("Buscar por nombre o marca:")
        if busqueda:
            filtro = df[df['nombre'].str.contains(busqueda, case=False, na=False) | 
                        df['marca'].str.contains(busqueda, case=False, na=False)]
            st.write("Resultados:")
            st.dataframe(filtro)

# 2. REGISTRAR NUEVO
elif choice == "Registrar Nuevo":
    st.subheader("Ingresar Nuevo Repuesto")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código (SKU)")
            nombre = st.text_input("Nombre del Repuesto")
            modelo = st.text_input("Modelo de Auto")
        with col2:
            marca = st.text_input("Marca") 
            precio = st.number_input("Precio", min_value=0.0, format="%.2f")
            cantidad = st.number_input("Cantidad", min_value=1, step=1)
        
        submitted = st.form_submit_button("Guardar en la Nube")

        if submitted:
            if codigo and nombre:
                # Verificamos si el código ya existe
                if codigo in df['codigo'].values:
                    st.error("¡Ese código ya existe!")
                else:
                    # Creamos una nueva fila
                    nueva_fila = pd.DataFrame([{
                        "codigo": codigo,
                        "nombre": nombre,
                        "modelo_auto": modelo,
                        "marca": marca,
                        "precio": precio,
                        "cantidad": cantidad
                    }])
                    
                    # Unimos la fila nueva con los datos viejos
                    df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                    
                    # Enviamos todo a Google Sheets
                    guardar_datos(df_actualizado)
                    st.success("¡Guardado exitosamente en Google Sheets!")
                    # Recargamos la página para ver los cambios
                    st.rerun()
            else:
                st.warning("Falta el código o el nombre.")