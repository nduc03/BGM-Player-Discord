import discord
import os

from discord.ext import commands
from bgm_stream import BGMStreamManager, BGMPlayer

try:
    import dotenv
    dotenv.load_dotenv()
except ModuleNotFoundError:
    print('Running on production mode. Make sure to set the environment variables')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

async def join(ctx):
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(ctx.author.voice.channel)

    await ctx.author.voice.channel.connect()

@client.command()
async def play(ctx):
    """Joins a voice channel then play the bgm"""
    await join(ctx)

    stream_manager = BGMStreamManager()

    def cleanup(error):
        nonlocal stream_manager
        if error:
            print(f'Player error: {error}')
        stream_manager.close()

    stream_manager.open_files('intro_converted.wav', 'loop_converted.wav')
    source = BGMPlayer(stream_manager.get_intro_stream(), stream_manager.get_loop_stream())
    ctx.voice_client.play(source, after=cleanup)
    await ctx.send('Now playing')

@client.command(aliases=['leave'])
async def stop(ctx):
    """Stops and disconnects the bot from voice"""
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

try:
    client.run(os.getenv('TOKEN'))
except Exception: # wait for 10 seconds before restart container when crash
    import time, sys
    time.sleep(10)
    sys.exit(1)