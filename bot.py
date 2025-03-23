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


bot.run(TOKEN)
