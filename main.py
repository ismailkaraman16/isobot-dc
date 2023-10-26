import discord
from discord.ext import commands
from gtts import gTTS
from pydub import AudioSegment
from pytube import YouTube, Search
import requests
import re
import json
import random
import asyncio
import os

token = os.environ.get("BOT_TOKEN")
giphyApiKey = "your_giphy_api_key"

if token:
    print("token found successfully")
else:
    print("token couldnt found")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

activity = discord.Game(name="i!help")

current_directory = os.getcwd()

bot = commands.Bot(command_prefix = 'i!', activity=activity, status=discord.Status.online, intents = intents)
discord.opus.load_opus(current_directory+"/opus/lib/libopus.so") #

queues = {}

@bot.event
async def on_ready():
    print(f'{bot.user} aktif!')

async def play(ctx):
    if (ctx.message.guild.id in queues and queues[ctx.message.guild.id]) == False:
        return await ctx.send("Bu hatayı aldıysan tebrik ederim dost nası başardın?")

    server = ctx.message.guild
    voice_channel = server.voice_client

    if(len(queues[ctx.message.guild.id])>0):
        try:
            voice_channel.play(discord.FFmpegPCMAudio(source="yt-downloaded/"+queues[ctx.message.guild.id][0]["name"]), after=lambda e: asyncio.run_coroutine_threadsafe(play(ctx), bot.loop))
            await ctx.send(queues[ctx.message.guild.id][0]["user"] + " isteği üzerine **" + queues[ctx.message.guild.id][0]["name"][:-4] + "** sıradan çalıyorrrr ")
        except Exception as err:
            print(err)

        queues[ctx.message.guild.id].pop(0)
        return

@bot.command(help="Sıradaki şarkıları gösterir")
async def sira(ctx, *args):
    if (ctx.message.guild.id in queues and queues[ctx.message.guild.id]) == False:
        return await ctx.send("Bu hatayı aldıysan tebrik ederim dost nası başardın?")

    if(len(queues[ctx.message.guild.id])<1):
        return await ctx.send("Sırada şarkı yok")

    content = ""
    for i in range(0, len(queues[ctx.message.guild.id])):
        content += str(i + 1) + " - " + queues[ctx.message.guild.id][i]["name"][:-4] + "\n"

    await ctx.send(content)


@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        filename = "dibinekadar.mp3"
        voice_channel.play(discord.FFmpegPCMAudio(source=filename))
    await ctx.send("**" + filename + "** çalıyorrrr")

@bot.command(help="Youtube'dan şarkı aratır")
async def ara(ctx, *args):
    query = ' '.join(args)
    try:
        try:
            channel = ctx.author.voice.channel
        except Exception as err:
            print(err)
            return await ctx.send("Seste değilsin dostum.")

        if channel:
            await channel.connect()
        else:
            return await ctx.send("Seste değilsin dostum.")
    except Exception as err:
        print(err)
        pass

    loadingMessage = await ctx.send("Arıyorum...", file=discord.File("loading.gif"))

    s = Search(query)
    if(len(s.results)<=0):
        return await ctx.send("Ne arattıysan bulamadım dost düzgün bir şey arat")

    yt = YouTube(str("https://www.youtube.com/watch?v=" + s.results[0].video_id))
    audio = yt.streams.filter(only_audio = True).first()
    audio.download(output_path="yt-downloaded")
    path = audio.default_filename

    server = ctx.message.guild
    voice_channel = server.voice_client

    await loadingMessage.delete()

    try:
        voice_channel.play(discord.FFmpegPCMAudio(source="yt-downloaded/"+path), after=lambda e: asyncio.run_coroutine_threadsafe(play(ctx), bot.loop))
        await ctx.send("**" + path[:-4] + "** çalıyorrrr")
    except Exception as err:
        print(err)
        if ctx.message.guild.id in queues:
            queues[ctx.message.guild.id].append({"name": path, "user": "<@"+str(ctx.author.id)+">"})
        else:
            queues[ctx.message.guild.id] = [{"name": path, "user": "<@"+str(ctx.author.id)+">"}]

        await ctx.send("**" + path[:-4] + "** sıraya eklendi")

@bot.command()
async def azbidur(ctx):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        if(voice_channel.is_playing() == True):
            voice_channel.pause()
        else:
            await ctx.send("Şarkı çalmıyo zaten?")
    except Exception as err:
        print(err)
        await ctx.send("Şarkı çalmıyo zaten?")

@bot.command()
async def devam(ctx):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        if(voice_channel.is_playing() == False):
            voice_channel.resume()
        else:
            await ctx.send("Çalıyo ya zaten?")
    except Exception as err:
        print(err)
        await ctx.send("Neyi devam ettireyim bro?")

@bot.command(help="Youtube'dan link ile şarkı oynatır")
async def oynat(ctx, url):
    try:
        try:
            channel = ctx.author.voice.channel
        except Exception as err:
            print(err)
            await ctx.send("Seste değilsin dostum.")

        if channel:
            await channel.connect()
        else:
            await ctx.send("Seste değilsin dostum.")
    except Exception as err:
        print(err)
        pass

    loadingMessage = await ctx.send("Bi saniye canım...", file=discord.File("loading.gif"))

    yt = YouTube(str(url))
    audio = yt.streams.filter(only_audio = True).first()
    audio.download(output_path="yt-downloaded")
    path = audio.default_filename

    server = ctx.message.guild
    voice_channel = server.voice_client

    await loadingMessage.delete()

    try:
        voice_channel.play(discord.FFmpegPCMAudio(source="yt-downloaded/"+path), after=lambda e: asyncio.run_coroutine_threadsafe(play(ctx), bot.loop))
        await ctx.send("**" + path[:-4] + "** çalıyorrrr")
    except Exception as err:
        print(err)
        if ctx.message.guild.id in queues:
            queues[ctx.message.guild.id].append({"name": path, "user": "<@"+str(ctx.author.id)+">"})
        else:
            queues[ctx.message.guild.id] = [{"name": path, "user": "<@"+str(ctx.author.id)+">"}]

        await ctx.send("**" + path + "** sıraya eklendi")

@bot.command(help="Oynayan sesi durdurur")
async def hamidimiz(ctx):
    server = ctx.message.guild
    queues[server] = []

    voice_channel = server.voice_client
    voice_channel.stop()

    await ctx.send(content="Ne dedi ne dedi??", file=discord.File("hamidimiz.gif"))

@bot.command(help="Botu ses kanalından çıkartır.")
async def sg(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send(content="Hadi ben kaçar :raised_hand:", file=discord.File("bb.gif"))
    else:
        await ctx.send("Seste değilim zaten.")

@bot.command(help="Selamlaşma!")
async def selam(ctx):
    print(ctx.author)
    await ctx.send("Selam " + ctx.author.name)

@bot.command(help="Yazılan yazıyı sesli bir şekilde okur")
async def oku(ctx, text, lang="tr"):
    try:
        try:
            channel = ctx.author.voice.channel
        except Exception as err:
            print(err)
            return await ctx.send("Seste değilsin dostum.")

        if channel:
            await channel.connect()
        else:
            return await ctx.send("Seste değilsin dostum.")
    except Exception as err:
        print(err)
        pass

    obj = gTTS(text=text, lang=lang, slow=False)
    obj.save("read.mp3")

    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.play(discord.FFmpegPCMAudio(source="read.mp3"))


@bot.command(help="YOOOOOOK (GHOST RIDER)")
async def yok(ctx):
    try:
        try:
            channel = ctx.author.voice.channel
        except Exception as err:
            print(err)
            await ctx.send("Seste değilsin dostum.")

        if channel:
            await channel.connect()
        else:
            await ctx.send("Seste değilsin dostum.")
    except Exception as err:
        print(err)
        pass

    server = ctx.message.guild
    voice_channel = server.voice_client

    filename = "yok.mp3"
    voice_channel.play(discord.FFmpegPCMAudio(source=filename))

@bot.command(help="Youtube'dan şarkı aratır")
async def vid(ctx, *args):
    query = ' '.join(args)

    loadingMessage = await ctx.send("Arıyorum...", file=discord.File("loading.gif"))

    s = Search(query)
    if(len(s.results)<=0):
        return await ctx.send("Ne arattıysan bulamadım dostum düzgün bir şey arat")

    yt = YouTube(str("https://www.youtube.com/watch?v=" + s.results[0].video_id))
    video = yt.streams.filter(file_extension='mp4', progressive=True, res='360p')

    if not video:
        video = yt.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').desc().first()
    else:
        video = video.first()

    if(video.filesize > 50000000):
        await loadingMessage.delete()
        return await ctx.send("Bu video çok büyük dost")

    video.download(output_path="yt-downloaded")
    path = video.default_filename

    await loadingMessage.delete()
    await ctx.send(file=discord.File("yt-downloaded/"+path))

@bot.command(help="İyi geceler :)")
async def gn(ctx):
    await ctx.send(content="İyi geceler bebeimmm :heart: <@"+str(ctx.author.id)+">")


@bot.command()
async def gif(ctx, *args): #user
    query = ' '.join(args)
    params = {
      "q": query,
      "api_key": giphyApiKey,
      "limit": "100"
    }
    r = requests.get("http://api.giphy.com/v1/gifs/search", params=params)
    r = r.json()

    await ctx.send(r["data"][random.randint(0,len(r["data"]) - 1)]['images']['fixed_height']['url'])

bot.run(token)