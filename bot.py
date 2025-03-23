import os
import discord
from discord import app_commands
from discord.ext import commands
from google_sheets import add_venta

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = discord.Object(id=1350837211209138298)  # Reemplaza con el ID de tu servidor
ROL_AUTORIZADO_ID = 1350837706103722095  # ID del rol que puede usar /addventa

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        await bot.tree.sync(guild=GUILD_ID)
        print("🌐 Comandos sincronizados.")
    except Exception as e:
        print(f"⚠️ Error al sincronizar comandos: {e}")


# --- COMANDO ADDVENTA ---
@bot.tree.command(name="addventa", description="Registrar una venta en el Excel", guild=GUILD_ID)
@app_commands.describe(
    fecha="Fecha de la venta (DD/MM/AAAA)",
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
    compra: str,
    venta: str,
    canal: str,
    estado: str
):
    if not any(role.id == ROL_AUTORIZADO_ID for role in interaction.user.roles):
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return

    try:
        add_venta(fecha, categoria, producto, proveedor, compra, venta, canal, estado)
        await interaction.response.send_message("✅ Venta registrada correctamente.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al registrar la venta: {e}", ephemeral=True)


# --- COMANDO VOUCH ---
@bot.tree.command(name="vouch", description="Leave a vouch", guild=GUILD_ID)
@app_commands.describe(
    product="Product's name",
    stars="Stars",
    payment_method="Payment method"
)
@app_commands.choices(
    stars=[
        app_commands.Choice(name="⭐", value="⭐"),
        app_commands.Choice(name="⭐⭐", value="⭐⭐"),
        app_commands.Choice(name="⭐⭐⭐", value="⭐⭐⭐"),
        app_commands.Choice(name="⭐⭐⭐⭐", value="⭐⭐⭐⭐"),
        app_commands.Choice(name="⭐⭐⭐⭐⭐", value="⭐⭐⭐⭐⭐"),
    ]
)
async def vouch(interaction: discord.Interaction, product: str, stars: app_commands.Choice[str], payment_method: str):
    embed = discord.Embed(
        title="📝 Nuevo Vouch",
        description=(
            f"**Product:** {product}\n"
            f"**Stars:** {stars.value}\n"
            f"**Payment Method:** {payment_method}"
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Leaved by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)


# Ejecuta el bot con tu token
bot.run(os.environ["TOKEN"])

