import discord
from discord import app_commands
from discord.ext import commands
import os

from google_sheets import add_venta  # Asegúrate de tener este archivo en el proyecto

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

class VentaModal(discord.ui.Modal, title="Registrar Venta"):

    fecha = discord.ui.TextInput(label="Fecha de venta", placeholder="23/03/2025")
    categoria = discord.ui.TextInput(label="Categoría", placeholder="Ej: Accesorios")
    producto = discord.ui.TextInput(label="Producto", placeholder="Ej: Gorro blanco")
    proveedor = discord.ui.TextInput(label="Proveedor", placeholder="Ej: Zara")
    compra = discord.ui.TextInput(label="Precio compra", placeholder="Ej: 7.5")
    venta = discord.ui.TextInput(label="Precio venta", placeholder="Ej: 12.99")
    canal = discord.ui.TextInput(label="Canal de venta", placeholder="Ej: Instagram", required=False)
    estado = discord.ui.TextInput(label="Estado", placeholder="Ej: Pagado / Enviado")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            add_venta(
                self.fecha.value,
                self.categoria.value,
                self.producto.value,
                self.proveedor.value,
                self.compra.value,
                self.venta.value,
                self.canal.value,
                self.estado.value
            )
            await interaction.response.send_message("✅ Venta registrada correctamente.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error al registrar la venta: {e}", ephemeral=True)

@tree.command(name="addventa", description="Registrar una venta en el Excel")
async def open_venta_modal(interaction: discord.Interaction):
    await interaction.response.send_modal(VentaModal())

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {bot.user}")

# TOKEN para Railway (variable de entorno directa, sin dotenv)
TOKEN = os.environ["TOKEN"]

bot.run(TOKEN)



bot.run(TOKEN)
