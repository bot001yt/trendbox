import discord
from discord.ext import commands
from discord import app_commands
import os
from google_sheets import add_venta  # Asegúrate de tenerlo correcto

# Configura el bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Ya viene incluido en discord.Bot

# Evento al iniciar el bot
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {bot.user}")

# Slash command con campos + restricción de rol
@app_commands.checks.has_role("1350837706103722095")
@tree.command(name="addventa", description="Registrar una venta en el Excel")
@app_commands.describe(
    fecha="Fecha de la venta (DD/MM/AAAA)",
    categoria="Categoría del producto",
    producto="Nombre del producto",
    proveedor="Proveedor",
    compra="Precio de compra",
    venta="Precio de venta",
    canal="Canal de venta",
    estado="Estado de la venta"
)
async def addventa(
    interaction: discord.Interaction,
    fecha: str,
    categoria: str,
    producto: str,
    proveedor: str,
    compra: float,
    venta: float,
    canal: str,
    estado: str
):
    try:
        add_venta(fecha, categoria, producto, proveedor, compra, venta, canal, estado)
        await interaction.response.send_message("✅ Venta registrada correctamente.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al registrar la venta: {e}", ephemeral=True)

# Gestión de errores por permisos
@addventa.error
async def on_addventa_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Ocurrió un error: {error}", ephemeral=True)


bot.run(os.environ["TOKEN"])

