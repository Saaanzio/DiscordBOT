import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import yt_dlp
import asyncio
from collections import deque

SONG_QUEUE = {}

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

async def search_ytdlp_async(query, ydl_opts):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))

def _extract(query, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="san", intents=intents)

modoIrritante = False

@bot.event
async def on_ready():
    print(f"{bot.user} está online!")

#WIP
@bot.event
async def on_member_join(member):
    await member.add_roles(member, discord.guild.roles, name = "Membros")

@bot.event
async def on_message(msg):
    if msg.author.id != bot.user.id and modoIrritante == True:
        await msg.channel.send(f"Que mensagem linda, {msg.author.mention}!")

@bot.event
async def on_message_edit(before,after):
    if before.author.id != bot.user.id:
        await before.channel.send(f"{before.author.mention} editou a mensagem '{before.content}' para '{after.content}'!")

@bot.tree.command(name="greet", description="Da um bom dia para o usuario")
async def greet(interaction: discord.Interaction):
    username = interaction.user.mention
    await interaction.response.send_message(f"Bom dia, {username}")

@bot.tree.command(name="modo_irritante", description="Ativa o modo irritante para todos usuários! ;)")
async def modo_irritante(interaction: discord.Interaction):
    global modoIrritante
    username = interaction.user.mention
    if modoIrritante == False:
        modoIrritante = True
        await interaction.response.send_message(f"{username} ativou o modo analisador de mensagens!")
    else:
        modoIrritante = False
        await interaction.response.send_message(f"{username} desativou o modo analisador de mensagens!")

@bot.tree.command(name="play", description="Toca música")
async def play(interaction: discord.Interaction, song_query: str):
    await interaction.response.defer()
    voice_channel = interaction.user.voice.channel

    if voice_channel is None:
        await interaction.followup.send("Amigo, você tem que estar em um canal de voz para ouvir musica.")
    voice_client = interaction.guild.voice_client
    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_channel != voice_client.channel:
        await voice_client.move_to(voice_channel)

    ydl_options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "youtube_include_dash_manifest": False,
        "youtube_include_hls_manifest": False,
    }

    query = "ytsearch1: " + song_query
    result = await search_ytdlp_async(query, ydl_options)
    tracks = result.get("entries", [])

    if tracks is None:
        await interaction.followup.send("Não encontrei nada")
        return
    first_track = tracks[0]
    audio_url = first_track["url"]
    title = first_track.get("title", "Untitled")

    guild_id = str(interaction.guild_id)
    if SONG_QUEUE.get(guild_id) is None:
        SONG_QUEUE[guild_id] = deque()
    SONG_QUEUE[guild_id].append((audio_url, title))

    if voice_client.is_playing() or voice_client.is_paused():
        await interaction.followup.send(f"Adicionada a fila: **{title}**")
    else:
        await play_next_song(voice_client, guild_id, interaction.channel)

@bot.tree.command(name="skip", description="Pular música")
async def skip(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client

    if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
        voice_client.stop()
        await interaction.response.send_message("Pulou a música atual.")
    else:
        await interaction.response.send_message("Não tá tocando nada para poder skippar.")

@bot.tree.command(name="show_queue", description="Mostra a fila de músicas.")
async def queue(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    queue_for_guild = SONG_QUEUE.get(guild_id)

    if not queue_for_guild:
        await interaction.response.send_message("Não está tocando nenhuma música no momento para eu exibir a fila.")
        return

    formatted_queue = "\n".join(
        f"{index + 1}. {title}" for index, (_, title) in enumerate(queue_for_guild)
    )

    await interaction.response.send_message(f"Fila de músicas:\n{formatted_queue}")

@bot.tree.command(name="pause", description="Pausar música")
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    
    if voice_client is None:
        return await interaction.response.send_message("Não estou em um canal de voz para pausar.")
    
    if not voice_client.is_playing():
        return await interaction.response.send_message("Tem nada tocando.")
    
    voice_client.pause()
    await interaction.response.send_message("PAUSADO!")


@bot.tree.command(name="resume", description="Resume música")
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    
    if voice_client is None:
        return await interaction.response.send_message("Não estou em um canal de voz para resumir algo.")
    
    if not voice_client.is_playing():
        return await interaction.response.send_message("Tem nada tocando.")
    
    voice_client.resume()
    await interaction.response.send_message("Resumido!")

@bot.tree.command(name="stop", description="Para música")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer()
    voice_client = interaction.guild.voice_client
    
    if not voice_client or not voice_client.is_connected():
        await interaction.followup.send("Não estou em um canal de voz para parar algo.")
        return
    
    guild_id_str = str(interaction.guild.id)
    if guild_id_str in SONG_QUEUE:
        SONG_QUEUE[guild_id_str].clear()
    
    if(voice_client.is_playing()) or voice_client.is_pause():
        voice_client.stop()

    await interaction.followup.send("Parando e desconectando!")
    await voice_client.disconnect()
    


async def play_next_song(voice_client, guild_id, channel):
    if SONG_QUEUE[guild_id]:
        audio_url, title = SONG_QUEUE[guild_id].popleft()
        ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn -c:a libopus -b:a 160k",
        }

        source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options, executable="bin\\ffmpeg\\ffmpeg.exe")

        def after_play(error):
            if error:
                print(f"Erro ao tocar {title}: {error}")
            asyncio.run_coroutine_threadsafe(play_next_song(voice_client,guild_id,channel), bot.loop)
        voice_client.play(source, after=after_play)
        asyncio.create_task(channel.send(f"Agora tocando: **{title}**"))

    else:
        await voice_client.disconnect()
        SONG_QUEUE[guild_id] = deque()

bot.run(TOKEN)