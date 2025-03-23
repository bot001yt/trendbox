import discord
from discord.ext import commands
from google_sheets import add_venta
import os


TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    await tree.sync()

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
    
@bot.command()
async def addventa(ctx, fecha, categoria, producto, proveedor, compra, venta, canal, estado):
    try:
        add_venta(fecha, categoria, producto, proveedor, compra, venta, canal, estado)
        await ctx.send("✅ Venta registrada correctamente.")
    except Exception as e:
        await ctx.send(f"❌ Error al registrar la venta: {e}")

@tree.command(name="addventa", description="Registrar una venta en el Excel")
@app_commands.describe(
    fecha="Fecha de venta (dd/mm/aaaa)",
    categoria="Categoría del producto",
    producto="Producto vendido",
    proveedor="Proveedor",
    compra="Precio de compra",
    venta="Precio de venta",
    canal="Canal de venta (opcional)",
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
        await interaction.response.send_message("✅ Venta registrada correctamente.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al registrar la venta: {e}")


bot.run(TOKEN)
