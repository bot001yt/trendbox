import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from google_sheets import add_venta

TOKEN = "TOKEN"  # ⚠️ Sustituye esto en Railway por la variable de entorno DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Necesario para los slash commands


class VentaModal(discord.ui.Modal, title="Registrar Venta"):

    fecha = discord.ui.TextInput(label="Fecha de venta", placeholder="Ej: 23/03/2025")
    categoria = discord.ui.TextInput(label="Categoría", placeholder="Ej: Ropa")
    producto = discord.ui.TextInput(label="Producto", placeholder="Ej: Sudadera oversize")
    proveedor = discord.ui.TextInput(label="Proveedor", placeholder="Ej: Shein")
    compra = discord.ui.TextInput(label="Precio de compra", placeholder="Ej: 10.50")
    venta = discord.ui.TextInput(label="Precio de venta", placeholder="Ej: 20.00")
    canal = discord.ui.TextInput(label="Canal de venta", required=False, placeholder="Ej: Wallapop")
    estado = discord.ui.TextInput(label="Estado", placeholder="Ej: Pagado / Pendiente")

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
async def addventa_command(interaction: discord.Interaction):
    await interaction.response.send_modal(VentaModal())


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {bot.user}")


bot.run(TOKEN)



bot.run(TOKEN)
