import os
import discord
from discord import app_commands
from discord.ext import commands
from google_sheets import add_venta
from datetime import datetime


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
@bot.tree.command(name="vouch", description="Leave a vouch for a product", guild=GUILD_ID)
@app_commands.describe(
    product="Name of the product",
    stars="Rating (stars)",
    payment_method="Payment method used",
    comment="Additional comment or review"
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
async def vouch(
    interaction: discord.Interaction,
    product: str,
    stars: app_commands.Choice[str],
    payment_method: str,
    comment: str
):
    user = interaction.user
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    embed = discord.Embed(
        title="✅ New vouch created!",
        color=discord.Color.green()
    )
    embed.add_field(name="⭐ Rating", value=stars.value, inline=False)
    embed.add_field(name="💬 Vouch", value=comment, inline=False)
    embed.add_field(name="🛍️ Product", value=product, inline=True)
    embed.add_field(name="💳 Payment Method", value=payment_method, inline=True)
    embed.add_field(name="👤 Vouched by", value=f"{user.mention}", inline=True)
    embed.add_field(name="📅 Vouched at", value=now, inline=True)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="Service provided by myvouch.es")

    await interaction.response.send_message(embed=embed)



# Ejecuta el bot con tu token
bot.run(os.environ["TOKEN"])

