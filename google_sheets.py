import gspread
import json
import os
from google.oauth2.service_account import Credentials

# Columnas: Fecha, Categoría, Producto, Proveedor, Precio Compra, Precio Venta, Beneficio, Canal, Estado
def add_venta(fecha, categoria, producto, proveedor, compra, venta, canal, estado):
    # Leer la variable GOOGLE_CREDENTIALS desde Railway
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict)

    # Autorizar cliente
    client = gspread.authorize(creds)

    # Abrir la hoja de cálculo (ajusta el nombre si es distinto)
    sheet = client.open("Registro de Ventas").sheet1

    # Calcular beneficio
    beneficio = float(venta) - float(compra)

    # Crear fila y añadirla
    fila = [fecha, categoria, producto, proveedor, compra, venta, beneficio, canal, estado]
    sheet.append_row(fila, value_input_option="USER_ENTERED")
