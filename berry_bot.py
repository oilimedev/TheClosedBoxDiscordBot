import discord
import asyncio
import datetime
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
reminders = {}

async def remind_leppa(member):
    await asyncio.sleep(60)
    await member.send(f'{member.mention} time to harvest your Leppa Berries!')
    if member.id in reminders:
        reminders[member.id].pop("leppa", None)

async def remind_gracidea(member):
    await asyncio.sleep(60)
    await member.send(f'{member.mention} time to harvest your Gracidea Flowers!')
    if member.id in reminders:
        reminders[member.id].pop("gracidea", None)

async def schedule_reminder(member, delay, callback, reminder_name):
    # Schedule the reminder to be sent after the specified delay
    await asyncio.sleep(delay)
    await callback(member)

    # Remove the reminder from the dictionary after it has been completed
    if member.id in reminders:
        reminders[member.id].pop(reminder_name, None)
        

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def leppa(ctx):
    delay = 20 * 60 * 60 # 20 hours in seconds
    member = ctx.author
    await ctx.send(f"Reminding {member.mention} to harvest Leppa Berry in 20 hours")
    if member.id not in reminders:
        reminders[member.id] = {}
    reminders[member.id]["leppa"] = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    await schedule_reminder(member, delay, remind_leppa, "leppa")

@bot.command()
async def gracidea(ctx):
    delay = 44 * 60 * 60 # 44 hours in seconds
    member = ctx.author
    await ctx.send(f"Reminding {member.mention} to harvest Gracidea Flower in 44 hours")
    if member.id not in reminders:
        reminders[member.id] = {}
    reminders[member.id]["gracidea"] = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    await schedule_reminder(member, delay, remind_gracidea, "gracidea")

@bot.command()
async def water(ctx, duration: int):
    delay = duration * 60 * 60 # Convert hours to seconds
    member = ctx.author
    now = datetime.datetime.now() # Get the current time on the user's computer
    due_time = now + datetime.timedelta(seconds=delay) # Calculate the due time
    await ctx.send(f"Reminding {member.mention} to water their berries at {due_time.strftime('%m/%d/%Y %I:%M %p')}")
    if member.id not in reminders:
        reminders[member.id] = {}
    reminders[member.id]["water"] = due_time # Use the due time instead of current server time
    await schedule_reminder(member, delay, lambda m: m.send(f"{m.mention} it's time to water your berries!"), "water")

@bot.command(name='reminders', help='Lists all the active reminders')
async def list_reminders(ctx):
    member = ctx.author
    if member.id in reminders:
        reminders_str = ""
        for reminder_name in reminders[member.id]:
            if reminder_name == "leppa":
                due_time = reminders[member.id][reminder_name]
                duration = int((due_time - datetime.datetime.now()).total_seconds() / 3600)
                due_str = due_time.strftime("%m/%d/%Y %I:%M %p %Z")
                reminders_str += f"Leppa Berry - Due in {duration} hours ({due_str})\n"
            elif reminder_name == "gracidea":
                due_time = reminders[member.id][reminder_name]
                duration = int((due_time - datetime.datetime.now()).total_seconds() / 3600)
                due_str = due_time.strftime("%m/%d/%Y %I:%M %p %Z")
                reminders_str += f"Gracidea Flower - Due in {duration} hours ({due_str})\n"
            elif reminder_name == "water":
                due_time = reminders[member.id][reminder_name]
                duration = int((due_time - datetime.datetime.now()).total_seconds() / 3600)
                due_str = due_time.strftime("%m/%d/%Y %I:%M %p %Z")
                reminders_str += f"Water Berries - Due in {duration} hours ({due_str})\n"
        if reminders_str:
            await ctx.send(f"{member.mention}, you have the following active reminders:\n{reminders_str}")
        else:
            await ctx.send(f"{member.mention}, you do not have any active reminders.")
    else:
        await ctx.send(f"{member.mention}, you do not have any active reminders.")

@bot.command(name='cancel', help='Cancels the specified user\'s reminder')
async def cancel(ctx, member: discord.Member):
    try:
        if member.id in reminders:
            del reminders[member.id]
            await ctx.send(f"{member.mention}, all of your reminders have been cancelled.")
        else:
            await ctx.send(f"{member.mention}, you have no active reminders.")
    except Exception as e:
        print(f"Error in cancel command: {e}")

# Run the bot
bot.run("")
