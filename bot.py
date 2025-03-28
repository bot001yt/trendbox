import os
import discord
from discord import app_commands
from discord.ext import commands
from google_sheets import add_venta
from datetime import datetime
from openai import OpenAI
import json

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = discord.Object(id=1350837211209138298)  # Reemplaza con el ID de tu servidor
ROL_AUTORIZADO_ID = 1350837706103722095  # ID del rol que puede usar /addventa

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.content.startswith(f"<@{bot.user.id}>") and not message.content.startswith(f"<@!{bot.user.id}>"):
        return

    category = message.channel.category.name.lower()

    if "replace" in category:
        system_msg = "You are a professional support assistant at TrendBox. The user is here because their subscription stopped working, expired, or the password doesn't work (usually Netflix or Crunchyroll). Reassure them that the replacement process is fast and handled as soon as possible. Politely explain the process, and if more details are needed (e.g., email used, screenshot), ask for them. Keep a calm, professional tone, but if they speak Spanish, you may add friendly words like 'vale', 'no te preocupes', or 'te ayudamos enseguida'."
    elif "buy" in category:
        system_msg = "You are a direct and persuasive salesperson from TrendBox. If the user speaks Spanish, use friendly expressions like 'tío' or 'perfe'. Your goal is to help them complete a purchase. Clearly explain: Prices for clothing and accessories do not include shipping. Shipping costs are calculated at the end. Buying more items gives them bigger discounts. Provide examples only from the following categories (with links): Fashion: https://discord.com/channels/1350837211209138298/1351108289630310410 Accessories: https://discord.com/channels/1350837211209138298/1351108342608691200 Subscriptions: https://discord.com/channels/1350837211209138298/1351108198320570399 Payment methods can be found at: https://discord.com/channels/1350837211209138298/1351140918761226272 Always keep it short, easy to understand, and push for the sale."
    elif "support" in category:
        system_msg = "You are a professional support agent from TrendBox. This user needs help with something general. Try to extract information from the initial embed message in the ticket, and based on that: If it's clear: proceed with solving or escalating the issue. If it's unclear: ask politely for more information. Your goal is to respond helpfully, clearly, and always keep the conversation moving forward. If the user writes in Spanish, adapt your tone accordingly and be more casual with expressions like 'tío' or 'perfe'."
    else:
        system_msg = "You are a general assistant for TrendBox. Help the user as best as possible in a polite and concise way."

    prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
    if not prompt:
        return

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        reply = response.choices[0].message.content
        await message.channel.send(reply)

    except Exception as e:
        await message.channel.send(f"❌ Error with AI response:\n```{e}```")

# Ejecuta el bot con tu token
bot.run(os.environ["TOKEN"])

