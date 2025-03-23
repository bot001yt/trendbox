import discord
from discord import app_commands
from discord.ext import commands
import os
from google_sheets import add_venta

# Define el ID de tu servidor y el ID del rol permitido
GUILD_ID = discord.Object(id=123456789012345678)  # Reemplaza por el ID de tu servidor
OWNER_ROLE_ID = 1350837706103722095  # ID del rol que puede usar el comando

intents = discord.Intents.default()
intents.message_content = False  # No es necesario para slash commands
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=GUILD_ID)
    print(f"✅ Bot conectado como {bot.user}")

@bot.tree.command(name="addventa", description="Registrar una venta en el Excel", guild=GUILD_ID)
@app_commands.describe(
    fecha="Fecha de la venta",
    categoria="Categoría del producto",
    producto="Nombre del producto",
    proveedor="Proveedor del producto",
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
    # Verifica si el usuario tiene el rol correcto
    if not any(role.id == OWNER_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return

    try:
        add_venta(fecha, categoria, producto, proveedor, compra, venta, canal, estado)
        await interaction.response.send_message("✅ Venta registrada correctamente.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al registrar la venta: {e}")

# Ejecuta el bot con tu token
bot.run(os.environ["TOKEN"])

