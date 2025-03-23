import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Columnas: Fecha, Categoría, Producto, Proveedor, Precio Compra, Precio Venta, Beneficio, Canal, Estado
def add_sale_row(fecha, categoria, producto, proveedor, compra, venta, canal, estado):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
    client = gspread.authorize(creds)

    # Reemplaza con el nombre o URL de tu hoja
    sheet = client.open("Registro de Ventas").sheet1

    beneficio = float(venta) - float(compra)

    # Nueva fila
    row = [fecha, categoria, producto, proveedor, compra, venta, beneficio, canal, estado]
    sheet.append_row(row)
