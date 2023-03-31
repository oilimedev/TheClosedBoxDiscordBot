import discord
import asyncio
import datetime
import pickle
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALERTS_FILE = 'alerts.pickle'

try:
    with open(ALERTS_FILE, 'rb') as f:
        alerts = pickle.load(f)
except FileNotFoundError:
    alerts = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.loop.create_task(send_alerts())

@bot.event
async def on_message(message):
    if message.content.startswith('!leppa'):
        author_id = message.author.id
        alerts[author_id] = {
            'harvest': datetime.datetime.utcnow() + datetime.timedelta(hours=20)
        }
        await message.author.send('A reminder has been set to harvest your Leppa berries in 20 hours.')
        with open(ALERTS_FILE, 'wb') as f:
            pickle.dump(alerts, f)
    elif message.content.startswith('!water'):
        try:
            hours = int(message.content.split()[1])
            author_id = message.author.id
            if author_id not in alerts:
                alerts[author_id] = {}
            alerts[author_id]['water'] = datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
            await message.author.send(f'A reminder has been set to water your berries in {hours} hours.')
            with open(ALERTS_FILE, 'wb') as f:
                pickle.dump(alerts, f)
        except (IndexError, ValueError):
            await message.author.send('Invalid syntax. Use !water (hours).')
    elif message.content.startswith('!myalerts'):
        author_id = message.author.id
        if author_id in alerts:
            harvest_time = alerts[author_id].get('harvest')
            water_time = alerts[author_id].get('water')
            if harvest_time:
                await message.author.send(f'Harvest reminder in {(harvest_time - datetime.datetime.utcnow()).seconds // 60} minutes.')
            if water_time:
                await message.author.send(f'Water reminder in {(water_time - datetime.datetime.utcnow()).seconds // 60} minutes.')
        else:
            await message.author.send('You have no active reminders.')
    elif message.content.startswith('!cancelalerts'):
        author_id = message.author.id
        if author_id in alerts:
            del alerts[author_id]
            await message.author.send('All reminders cancelled.')
            with open(ALERTS_FILE, 'wb') as f:
                pickle.dump(alerts, f)
        else:
            await message.author.send('You have no active reminders to cancel.')

async def send_alerts():
    while True:
        now = datetime.datetime.utcnow()
        for author_id, reminder_times in alerts.copy().items():
            user = bot.get_user(author_id)
            if user is not None:
                for reminder_type, reminder_time in reminder_times.copy().items():
                    if now >= reminder_time:
                        await user.send(f'It is time to {reminder_type} your berries.')
                        if reminder_type == 'harvest':
                            del alerts[author_id]['harvest']
                        elif reminder_type == 'water':
                            del alerts[author_id]['water']

                        # Check if the alerts[author_id] dictionary is empty and remove it
                        if not alerts[author_id]:
                            del alerts[author_id]

                        with open(ALERTS_FILE, 'wb') as f:
                            pickle.dump(alerts, f)
        await asyncio.sleep(60)

bot.run('TOKEN')


