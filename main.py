import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from keep_alive import keep_alive
from datetime import datetime, timezone
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Botun sürekli aktif olması için
keep_alive()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("TOKEN")  # .env dosyasındaki token'ı al
SEC_ROLE_NAME = "Sec"

# BOT HAZIR
@bot.event
async def on_ready():
    print(f"Bot giriş yaptı: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash komutları senkronize edildi: {len(synced)} komut")
    except Exception as e:
        print(f"Hata: {e}")

# YETKİ KONTROLÜ
def sec_rol_kontrol(interaction: discord.Interaction):
    return any(role.name == SEC_ROLE_NAME for role in interaction.user.roles)

# /sil komutu
@bot.tree.command(name="sil", description="Belirtilen kadar mesaj siler")
@app_commands.describe(amount="Silinecek mesaj sayısı")
async def sil(interaction: discord.Interaction, amount: int):
    if not sec_rol_kontrol(interaction):
        return await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
    if amount < 1 or amount > 150:
        return await interaction.response.send_message("1-150 arası olmalı.", ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"{len(deleted)} mesaj silindi.", ephemeral=True)

# /rol-ekle komutu
@bot.tree.command(name="rol-ekle", description="Bir kullanıcıya rol ekle")
@app_commands.describe(kullanici="Rol verilecek kullanıcı", rol="Verilecek rol")
async def rol_ekle(interaction: discord.Interaction, kullanici: discord.Member, rol: discord.Role):
    if not sec_rol_kontrol(interaction):
        return await interaction.response.send_message("❌ Yetkin yok.", ephemeral=True)
    try:
        await kullanici.add_roles(rol)
        await interaction.response.send_message(f"{kullanici.mention} kullanıcısına {rol.name} rolü verildi.")
    except Exception as e:
        await interaction.response.send_message(f"Hata ❌: {e}")

# /duyur komutu (sadece Sec rolü kullanabilir)
@bot.tree.command(name="duyur", description="Bir duyuru gönder.")
@app_commands.describe(mesaj="Gönderilecek duyuru mesajı")
async def duyur(interaction: discord.Interaction, mesaj: str):
    if not sec_rol_kontrol(interaction):
        return await interaction.response.send_message("❌ Bu komutu kullanmak için yetkin yok.", ephemeral=True)

    embed = discord.Embed(
        title="📢 DUYURU",
        description=mesaj,
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Duyuruyu yapan: {interaction.user.name}")
    embed.timestamp = datetime.now()

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("✅ Duyuru gönderildi.", ephemeral=True)

# /rapor komutu (Renkli embed)
@bot.tree.command(name="rapor", description="Kullanıcı hakkında rapor gönder.")
@app_commands.describe(
    isim="Kullanıcının ismi",
    icraatler="Ne yaptı?",
    rapor_sayısı="Toplam rapor sayısı",
    aktiflik="Oyundaki aktiflik süresi"
)
async def rapor(interaction: discord.Interaction, isim: str, icraatler: str, rapor_sayısı: str, aktiflik: str):
    renk = discord.Color.random()
    embed = discord.Embed(
        title="📝 Yeni Rapor",
        description=f"**İsim:** {isim}\n**İcraatler:** {icraatler}\n**Güncel rapor sayın:** {rapor_sayısı}\n**Toplam oyundaki aktiflik:** {aktiflik}\n**Tag:** <@&1324004625577152627>",
        color=renk
    )
    embed.set_footer(text=f"Raporlayan: {interaction.user.name}")
    embed.timestamp = datetime.now()

    mesaj = await interaction.channel.send(embed=embed)
    await interaction.response.send_message("📨 Rapor gönderildi.", ephemeral=True)

    for _ in range(20):  # Daha fazla geçiş olsun diye 20 yaptık
        await asyncio.sleep(0.3)  # Her 0.3 saniyede bir değişsin
        embed.color = discord.Color.random()
        await mesaj.edit(embed=embed)

# ÜYE GİRİŞ MESAJI
@bot.event
async def on_member_join(member):
    now = datetime.now(timezone.utc)
    account_age = now - member.created_at
    risk = "🔴 Riskli" if account_age.days < 7 else "🟢 Güvenli"

    embed = discord.Embed(
        title="🔔 Sunucumuza Hoş Geldin!",
        description=f"{member.mention} aramıza katıldı!",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🛡️ Risk", value=risk, inline=True)
    embed.add_field(name="👤 Kullanıcı", value=f"{member.name}#{member.discriminator}", inline=True)
    embed.add_field(name="📅 Hesap Oluşturulma", value=f"{member.created_at.strftime('%d %B %Y')} ({account_age.days} gün önce)", inline=False)
    embed.add_field(name="👥 Üye Sayısı", value=f"{member.guild.member_count}", inline=False)

    kanal = bot.get_channel(1339978357240233990)  # Hoş geldin kanal ID
    if kanal:
        await kanal.send(embed=embed)

# SA-AS MESAJI
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == "sa":
        await message.channel.send("as")
    await bot.process_commands(message)

# BOTU ÇALIŞTIR
bot.run(TOKEN)
