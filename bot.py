import os
import discord
from discord import app_commands
from discord.ext import commands
from google_sheets import add_venta
from datetime import datetime
from openai import OpenAI
import json
import httpx

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = discord.Object(id=1350837211209138298)  # Reemplaza con el ID de tu servidor
ROL_AUTORIZADO_ID = 1350837706103722095  # ID del rol que puede usar /addventa

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


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
        system_msg = (
            "You are a professional support assistant at TrendBox. The user is here because their subscription stopped working, expired, or the password doesn't work (usually Netflix or Crunchyroll). "
            "Reassure them that the replacement process is fast and handled as soon as possible. "
            "Politely explain the process, and if more details are needed (e.g., email used, screenshot), ask for them. "
            "Keep a calm, professional tone, but if they speak Spanish, you may add friendly words like 'vale', 'no te preocupes', or 'te ayudamos enseguida'."
        )
    elif "buy" in category:
        system_msg = (
            "You are a direct and persuasive salesperson from TrendBox. If the user speaks Spanish, use friendly expressions like 'tío' or 'perfe'. Your goal is to help them complete a purchase. "
            "Clearly explain:\n"
            "- Prices for clothing and accessories do not include shipping.\n"
            "- Shipping costs are calculated at the end.\n"
            "- Buying more items gives them bigger discounts.\n"
            "Provide examples only from the following categories (with links):\n"
            "- Fashion: https://discord.com/channels/1350837211209138298/1351108289630310410\n"
            "- Accessories: https://discord.com/channels/1350837211209138298/1351108342608691200\n"
            "- Subscriptions: https://discord.com/channels/1350837211209138298/1351108198320570399\n"
            "Payment methods can be found at: https://discord.com/channels/1350837211209138298/1351140918761226272\n"
            "Always keep it short, easy to understand, and push for the sale."
        )
    elif "support" in category:
        system_msg = (
            "You are a professional support agent from TrendBox. This user needs help with something general. "
            "Try to extract information from the initial embed message in the ticket, and based on that:\n"
            "- If it's clear: proceed with solving or escalating the issue.\n"
            "- If it's unclear: ask politely for more information.\n"
            "Your goal is to respond helpfully, clearly, and always keep the conversation moving forward.\n"
            "If the user writes in Spanish, adapt your tone accordingly and be more casual with expressions like 'tío' or 'perfe'."
            "If it is something related to the product stopped working, say to them to open a replace ticket in https://discord.com/channels/1350837211209138298/1351136060415152169"
        )
    else:
        system_msg = "You are a helpful assistant from TrendBox."

    prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
    if not prompt:
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "google/gemma-3-27b-it:free",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            result = response.json()
        if "choices" in result and result["choices"]:
            reply = result["choices"][0]["message"]["content"]
            await message.channel.send(reply)
        elif "error" in result:
            error_msg = result["error"].get("message", "Unknown error")
            await message.channel.send(f"❌ AI error from API: {error_msg}")
        else:
            await message.channel.send("❌ AI error: Unexpected response format.")

    except Exception as e:
        await message.channel.send(f"❌ Error with AI response: {e}")



@bot.tree.command(name="done", description="Renombra el canal a 'done' (solo staff)", guild=GUILD_ID)
async def done(interaction: discord.Interaction):
    if not any(role.id == ROL_AUTORIZADO_ID for role in interaction.user.roles):
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return

    try:
        await interaction.channel.edit(name="done")
        await interaction.channel.send("✅ Canal renombrado a `done`", delete_after=5)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al renombrar: {e}", ephemeral=True)



@bot.tree.command(name="rename", description="Renombra el canal actual (solo staff)", guild=GUILD_ID)
@app_commands.describe(nombre="Nuevo nombre para el canal")
async def rename(interaction: discord.Interaction, nombre: str):
    if not any(role.id == ROL_AUTORIZADO_ID for role in interaction.user.roles):
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return

    try:
        await interaction.channel.edit(name=nombre)
        msg = await interaction.response.send_message(f"✅ Canal renombrado a `{nombre}`", ephemeral=False)
        await interaction.channel.send(f"✅ Canal renombrado a `{nombre}`", delete_after=5)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error al renombrar: {e}", ephemeral=True)




# === COMANDOS DE PAGO CON JSON PERSISTENTE ===

import json

WALLETS_FILE = "wallets.json"

def cargar_wallets():
    try:
        with open(WALLETS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "btc": "TU_DIRECCION_BTC",
            "ltc": "TU_DIRECCION_LTC",
            "sol": "TU_DIRECCION_SOL",
            "xmr": "TU_DIRECCION_XMR",
            "paypal": "tu@email.com"
        }

def guardar_wallets(wallets):
    with open(WALLETS_FILE, "w") as f:
        json.dump(wallets, f, indent=4)

wallets = cargar_wallets()

# --- COMANDOS DE PAGO ---

@bot.tree.command(name="btc", description="Ver dirección BTC", guild=GUILD_ID)
@app_commands.describe(cantidad="Cantidad en USD (opcional)")
async def btc(interaction: discord.Interaction, cantidad: str = None):
    msg = f"💰 Dirección de Bitcoin (BTC): `{wallets['btc']}`"
    if cantidad:
        msg += f"\n💵 Cantidad a pagar: **${cantidad}**"
    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="ltc", description="Ver dirección LTC", guild=GUILD_ID)
@app_commands.describe(cantidad="Cantidad en USD (opcional)")
async def ltc(interaction: discord.Interaction, cantidad: str = None):
    msg = f"💰 Dirección de Litecoin (LTC): `{wallets['ltc']}`"
    if cantidad:
        msg += f"\n💵 Cantidad a pagar: **${cantidad}**"
    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="sol", description="Ver dirección SOL", guild=GUILD_ID)
@app_commands.describe(cantidad="Cantidad en USD (opcional)")
async def sol(interaction: discord.Interaction, cantidad: str = None):
    msg = f"💰 Dirección de Solana (SOL): `{wallets['sol']}`"
    if cantidad:
        msg += f"\n💵 Cantidad a pagar: **${cantidad}**"
    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="xmr", description="Ver dirección XMR", guild=GUILD_ID)
@app_commands.describe(cantidad="Cantidad en USD (opcional)")
async def xmr(interaction: discord.Interaction, cantidad: str = None):
    msg = f"💰 Dirección de Monero (XMR): `{wallets['xmr']}`"
    if cantidad:
        msg += f"\n💵 Cantidad a pagar: **${cantidad}**"
    await interaction.response.send_message(msg, ephemeral=True)

@bot.tree.command(name="paypal", description="Ver dirección PayPal", guild=GUILD_ID)
@app_commands.describe(cantidad="Cantidad en USD (opcional)")
async def paypal(interaction: discord.Interaction, cantidad: str = None):
    msg = f"📩 Envíame el pago a: `{wallets['paypal']}`\n✅ Use **Friends & Family (F&F)**\n❌ No additional notes."
    if cantidad:
        msg += f"\n💵 Cantidad a pagar: **${cantidad}**"
    await interaction.response.send_message(msg, ephemeral=True)

# --- COMANDOS DE CONFIGURACIÓN ---

async def actualizar_wallet(interaction, key, valor):
    if not any(role.id == ROL_AUTORIZADO_ID for role in interaction.user.roles):
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return
    wallets[key] = valor
    guardar_wallets(wallets)
    await interaction.response.send_message(f"✅ Dirección/correo actualizado para {key.upper()}.", ephemeral=True)

@bot.tree.command(name="configbtc", description="Configurar dirección BTC", guild=GUILD_ID)
@app_commands.describe(direccion="Nueva dirección BTC")
async def configbtc(interaction: discord.Interaction, direccion: str):
    await actualizar_wallet(interaction, "btc", direccion)

@bot.tree.command(name="configltc", description="Configurar dirección LTC", guild=GUILD_ID)
@app_commands.describe(direccion="Nueva dirección LTC")
async def configltc(interaction: discord.Interaction, direccion: str):
    await actualizar_wallet(interaction, "ltc", direccion)

@bot.tree.command(name="configsol", description="Configurar dirección SOL", guild=GUILD_ID)
@app_commands.describe(direccion="Nueva dirección SOL")
async def configsol(interaction: discord.Interaction, direccion: str):
    await actualizar_wallet(interaction, "sol", direccion)

@bot.tree.command(name="configxmr", description="Configurar dirección XMR", guild=GUILD_ID)
@app_commands.describe(direccion="Nueva dirección XMR")
async def configxmr(interaction: discord.Interaction, direccion: str):
    await actualizar_wallet(interaction, "xmr", direccion)

@bot.tree.command(name="configpaypal", description="Configurar correo PayPal", guild=GUILD_ID)
@app_commands.describe(correo="Nuevo correo PayPal")
async def configpaypal(interaction: discord.Interaction, correo: str):
    await actualizar_wallet(interaction, "paypal", correo)



# Ejecuta el bot con tu token
bot.run(os.environ["TOKEN"])

