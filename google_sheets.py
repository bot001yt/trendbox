import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def add_venta(fecha, categoria, producto, proveedor, compra, venta, canal, estado):
    try:
        # Define el alcance (scopes)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        # Carga las credenciales desde la variable de entorno
        credentials_json = os.getenv("GOOGLE_CREDENTIALS")
        creds_dict = json.loads(credentials_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

        # Autoriza y abre el documento
        client = gspread.authorize(creds)
        sheet = client.open("Registro de Ventas").sheet1  # Asegúrate de que el nombre coincide

        # Calcula beneficio
        beneficio = float(venta) - float(compra)

        # Prepara y añade la fila
        row = [fecha, categoria, producto, proveedor, compra, venta, beneficio, canal, estado]
        sheet.append_row(row)

    except Exception as e:
        print(f"Error al añadir la venta: {e}")
        # No relanzamos la excepción para evitar errores molestos en Discord
