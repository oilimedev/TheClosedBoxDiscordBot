import discord
import config
import creds  # File with bot token
import asyncio
import datetime
import os
import json
from discord.ext import commands
from enum import Enum

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix=config.bot_command_prefix, intents=intents)

if not os.path.exists(config.users_folder_name):
    os.makedirs(config.users_folder_name)

@bot.event
async def on_ready():
    print(f'{bot.user} is ready!')
    bot.loop.create_task(check_alerts())

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_input = message.content.lower().split(" ")[0]
    if not user_input.startswith(config.bot_command_prefix):
        return

    command = user_input.split(config.bot_command_prefix)[1]
    command_exists = False
    
    if command in CommandsEnum.__members__: # Check if command is an existing command
        command_exists = True
    
    if command in BerriesCommandsEnum.__members__: # Check if command is a berry command
        command_exists = True

    if not command_exists:
        return
    
    if command in CommandsEnum.__members__:
        await run_generic_command(message)

    if command in BerriesCommandsEnum.__members__:
        await run_berry_command(message)

async def run_berry_command(message):
    user_file = await get_user_file_by_author(message.author)
    berry_command = message.content.split(config.bot_command_prefix)[1]
    with open('berries_data.json', 'r') as berries_file:
        berries = json.load(berries_file)
        user_data = await get_user_data_by_userfile(user_file)
        if berry_command not in berries:
            return
        berry_data = berries[berry_command]
        berry_name = berry_data['name']
        current_time = get_utc_now()
        alert_time_datetime = current_time + datetime.timedelta(hours = berry_data['hours'])
        beautified_time = beautify_remaining_time(alert_time_datetime - current_time)
        await add_alert(user_data, berry_name, alert_time_datetime.timestamp(), AlertType.harvest.value)
        await write_json(user_data, user_file)
        await send_message(message, f'A reminder has been set to harvest your {berry_name} berries in **{beautified_time}**.')

async def run_generic_command(message):
    user_file = await get_user_file_by_author(message.author)
    user_command = message.content.split(config.bot_command_prefix)[1]

    # Test commands
    if user_command == CommandsEnum.ping:
        await send_message(message, "Pong!")
        return
    
    if user_command == CommandsEnum.myalerts:
        user_data = await get_user_data_by_userfile(user_file)
        if "alerts" in user_data:
            if len(user_data["alerts"]) == 0:
                await send_message(message, "You have no reminders.")
                return
            all_alerts_message = "**Active Reminders**:\n"
            alerts = sorted(user_data["alerts"], key=lambda k: k['time'])
            for alert in alerts:
                alert_time = alert['time']
                alert_time_datetime = datetime.datetime.fromtimestamp(alert_time)
                remaining_time = alert_time_datetime - get_utc_now()
                remaining_time_formatting_text = beautify_remaining_time(remaining_time)
                all_alerts_message += beautify_alert_message(alert['type'], alert['name'], remaining_time_formatting_text)
            await send_message(message, all_alerts_message)
        else:
            await send_message(message, "You have no reminders.")
        return
    
    if user_command == CommandsEnum.clearalerts:
        user_data = await get_user_data_by_userfile(user_file)
        if "alerts" in user_data:
            if len(user_data["alerts"]) == 0:
                await send_message(message, "You have no reminders.")
                return
            user_data["alerts"] = []
            await write_json(user_data, user_file)
            await send_message(message, "All reminders have been cleared.")
        return

    if user_command == CommandsEnum.help:
        await send_message(message, help_message)
        return
    
    if user_command.startswith(CommandsEnum.water):
        try:
            hours = int(message.content.split(" ")[1])
        except (IndexError, ValueError):
            await send_message(message, "Please enter a valid number of hours.")
            raise
        user_data = await get_user_data_by_userfile(user_file)
        current_time = get_utc_now()
        alert_time_datetime = current_time + datetime.timedelta(hours = hours)
        beautified_time = beautify_remaining_time(alert_time_datetime - current_time)
        await add_alert(user_data, "", alert_time_datetime.timestamp(), AlertType.water.value)
        await write_json(user_data, user_file)
        await send_message(message, f'A reminder has been set to water your berries in **{beautified_time}**.')

# Get user file and data
async def get_user_file_by_author(author):
    user_file = f"{config.users_folder_name}/{author.id}.json"
    return user_file

async def get_user_data_by_userfile(user_file):
    if not check_file_exists(user_file):
        await write_json({}, user_file)

    with open(user_file, 'r') as user_file:
        try:
            user_data = json.load(user_file)
            return user_data
        except json.JSONDecodeError:
            return

async def get_user_data_by_author(author):
    user_file = f"{config.users_folder_name}/{author.id}.json"
    if not check_file_exists(user_file):
        await write_json({}, user_file)

    with open(user_file, 'r') as user_file:
        try:
            user_data = json.load(user_file)
            return user_data
        except json.JSONDecodeError:
            return

async def get_user_file_by_filename(file_name):
    user_file = f"{config.users_folder_name}/{file_name}"
    return user_file

# Add or remove alerts
async def add_alert(user_data, berry_name, action_time, action_name):
    if "alerts" not in user_data:
        user_data["alerts"] = []
    user_data["alerts"].append(
        {"name": berry_name, "time": action_time, "type": action_name})

# JSON File Functions
async def add_json_key(json, key, value):
    json[key] = value

async def remove_json_key(json, key):
    try:
        del json[key]
    except KeyError:
        pass

async def write_json(user_data, user_file):
    with open(user_file, 'w') as user_file:
        json.dump(user_data, user_file)

async def send_message(message, text_to_send):
    recipient = message.author
    if not isinstance(message.channel, discord.channel.DMChannel):
        await message.delete()
    await recipient.send(text_to_send)

async def send_message_to_user(recipient, text_to_send):
    await recipient.send(text_to_send)

# Alert Functions
async def check_alerts():
    while True:
        total_alerts = 0
        total_users = 0
        for user_filename in os.listdir(config.users_folder_name):
            total_users += 1
            user_id = int(user_filename.split(".")[0])
            user_file = await get_user_file_by_filename(user_filename)
            user_data = await get_user_data_by_userfile(user_file)
            if "alerts" in user_data:
                alerts = user_data["alerts"]
                for alert in alerts:
                    alert_time = alert['time']
                    if alert_time <= get_utc_now().timestamp():
                        total_alerts += 1
                        alert_message = beautify_ready_alert_message(alert)
                        await send_message_to_user(bot.get_user(user_id), alert_message)
                        user_data["alerts"].remove(alert)
                        await write_json(user_data, user_file)
        print(f"Sent {total_alerts} alerts and checked {total_users} users.")
        await asyncio.sleep(10)

# Static Functions
def check_file_exists(file):
    if os.path.exists(file):
        return True
    else:
        return False

def get_timestamp_from_datetime(datetime):
    return datetime.timestamp()

def get_utc_now():
    return datetime.datetime.utcnow()

def beautify_remaining_time(remaining_time):
    remaining_minutes = int(remaining_time.total_seconds() / 60)
    if remaining_minutes < 60:
        return f"{remaining_minutes} minutes"
    else:
        remaining_hours = int(remaining_minutes / 60)
        remaining_minutes = remaining_minutes % 60
        beautified_text = f"{remaining_hours} hours"
        if remaining_minutes > 0:
            beautified_text += f" and {remaining_minutes} minutes"
        return beautified_text
    
def beautify_alert_message(alert_type, berry_name, remaining_time):
    if alert_type == AlertType.harvest.value:
        return f"- {berry_name} berries harvest reminder in **{remaining_time}**.\n"
    elif alert_type == AlertType.water.value:
        return f"- Water reminder in **{remaining_time}**.\n"
    
def beautify_ready_alert_message(alert):
    if alert['type'] == AlertType.harvest.value:
        return f"This is your {alert['name']} berries harvest reminder."
    elif alert['type'] == AlertType.water.value:
        return f"This is your water reminder."
    
# Custom Classes
    # Command Classes
class CommandsEnum(str, Enum):
    help = "help"
    ping = "ping"
    myalerts = "myalerts"
    clearalerts = "clearalerts"
    water = "water"

class BerriesCommandsEnum(Enum):
    leppa = 0

class AlertType(str, Enum):
    harvest = 'harvest'
    water = 'watering'

#TODO: Refactor code to add berries dinamically from berries_data.json and commands from a commands_data.json

# Help Message
help_message = '''\
**Alert Commands**
`{prefix}myalerts` - Shows all your reminders.
`{prefix}clearalerts` - Clears all your reminders.
`{prefix}water (hours)` - Sets a reminder in X hours to water

**Berry Commands**
`{prefix}leppa` - Sets a reminder in 20 hours to harvest your Leppa Berries

**General Commands**
`{prefix}ping` - Pong!
`{prefix}help` - Shows this message
'''.format(prefix = config.bot_command_prefix)

bot.run(creds.bot_token)