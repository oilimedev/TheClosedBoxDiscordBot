# bot.py
import os
import discord
import creds
import time

intents = discord.Intents.all()

TOKEN = creds.bot_token

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if(message.channel.id == 1266239549873328211):
        await repost_message(message)

async def repost_message(message):
    channel = client.get_channel(1266276804776431737)
    await channel.send(content=f'{message.author.display_name} ({message.author}) message:')
    if(message.attachments):
        attachments_paths = await save_files(message)
        await delete_message(message)
        if(message.content):
            await channel.send(content=f'{message.content}')
        if attachments_paths:
            for path in attachments_paths:
                await channel.send(file=discord.File(path))
            delete_files(attachments_paths)
    else:
        await delete_message(message)
        await channel.send(content=f'{message.content}')

async def delete_message(message):
    if not isinstance(message.channel, discord.channel.DMChannel):
        await message.delete()

async def save_files(message):
    paths = []
    author_directory = get_author_directory(message.author)
    index = 0
    epoch_time = int(time.time())
    for attachment in message.attachments:
        saved_file_path = f'{author_directory}/{index}_{epoch_time}_{attachment.filename}'
        await attachment.save(saved_file_path)
        paths.append(saved_file_path)
        index += 1
    return paths
    
def get_author_directory(author):
    author_directory = f'./users/{author}'
    if not os.path.exists(author_directory):
        os.makedirs(author_directory)
    return author_directory

def delete_files(paths):
    for path in paths:
        os.remove(path)

client.run(TOKEN)