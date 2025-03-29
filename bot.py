import os
import discord
from discord import app_commands
from discord.ext import commands
from google_sheets import add_venta
from datetime import datetime
import openai
import json

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
    embed.set_footer(text="Service provided by Trendbox")


    openai.api_key = os.getenv("OPENAI_API_KEY")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith(f"<@{bot.user.id}>") and not message.content.startswith(f"<@!{bot.user.id}>"):
        return

    if not message.channel.name.startswith("ticket-"):
        return

    category = message.channel.category.name.lower()

    # Define el contexto según la categoría del ticket
    if "replace" in category:
        system_msg = (
            "Eres un asistente de soporte profesional especializado en reemplazos. "
            "Ayuda al usuario si su suscripción (normalmente Netflix o Crunchyroll) ha dejado de funcionar, ha caducado, o la contraseña no va. "
            "Explica que debe solicitar el reemplazo por este canal y que será atendido lo antes posible."
        )
    elif "buying" in category:
        system_msg = (
            "Eres un vendedor persuasivo y directo. Si detectas que el usuario escribe en español, usa expresiones como 'tío' o 'perfe' en lugar de 'perfecto'. "
            "Informa que los precios de ropa y accesorios no incluyen envío, que se calcula al final de la compra. "
            "Indica que cuantos más productos compre, mayor será el descuento.
"
            "Métodos de pago: disponibles en https://discord.com/channels/1350837211209138298/1351140918761226272

"
            "Ofrece ejemplos reales de productos:
"
            "- Fashion: https://discord.com/channels/1350837211209138298/1351108289630310410
"
            "- Accessories: https://discord.com/channels/1350837211209138298/1351108342608691200
"
            "- Subscriptions: https://discord.com/channels/1350837211209138298/1351108198320570399"
        )
    elif "support" in category:
        system_msg = (
            "Eres un asistente técnico profesional. Si puedes leer el primer mensaje del ticket (embed), usa esa información para responder. "
            "Si no, pide más detalles al usuario sobre su problema para poder ayudarle mejor. Sé claro y eficiente."
        )
    else:
        system_msg = "Eres un asistente general para una tienda de Discord. Ayuda al usuario con lo que necesite."

    prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()

    if not prompt:
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        reply = response["choices"][0]["message"]["content"]
        await message.channel.send(reply)

    except Exception as e:
        await message.channel.send(f"❌ Error with AI response: {e}")


    await interaction.response.send_message(embed=embed)



# Ejecuta el bot con tu token
bot.run(os.environ["TOKEN"])

