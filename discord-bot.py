# bot.py
import os
from pathlib import Path

import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

import speech_recognition as sr
import soundfile as sf
import audioread

class Client(commands.Bot):
    # @client.event
    async def on_ready(self):
        for guild in client.guilds:
            # guild_ids.append(guild.id)
            try:
                synced = await self.tree.sync(guild=discord.Object(id=guild.id))
                print(f'Synced {len(synced)} commands to guild {guild.id}')
            except Exception as e:
                print(f'error {e}')
        print(f'{self.user} has connected to Discord!')

load_dotenv()
TOKEN = os.getenv('TOKEN')
print(TOKEN)

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)
r = sr.Recognizer()

guild_id = 1000986856122503278

# @client.event
@client.tree.command(name="transcribe", description="Transcribes the linked message if sent in the same server.", guild=discord.Object(id=guild_id))
async def slash_command(interaction: discord.Interaction, message: str):    
    try:
        msg = await interaction.channel.fetch_message(message.split('/')[-1])
        if msg.guild.id != interaction.guild.id:
            await interaction.response.send_message('The provided link is not from this server.')
            return

        if msg.attachments and msg.attachments[0].filename.endswith('.ogg'):
            await interaction.response.send_message('Voice message detected. Starting transcription...')
            voice_file_path = os.getcwd()+f'\\tmp\\{msg.attachments[0].filename}'
            await msg.attachments[0].save(voice_file_path)
            data, samplerate = sf.read(voice_file_path)
            sf.write(voice_file_path.replace('ogg', 'wav'), data, samplerate)
            os.remove(voice_file_path)
            voice_file_path = voice_file_path.replace('ogg', 'wav')
            with sr.AudioFile(voice_file_path) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data)
                await interaction.followup.send(f'Recognized text: {text}')
            os.remove(voice_file_path)
        else:
            await interaction.response.send_message('The provided link does not contain a voice message.')
    except Exception as e:
        await interaction.response.send_message(f'Error fetching message: {e}')

client.run(TOKEN)