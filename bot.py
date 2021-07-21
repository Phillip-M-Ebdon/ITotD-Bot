import discord
from discord.ext import tasks
import sqlite3
from datetime import datetime
from decouple import config
import csv
import random

TOKEN = config("DISCORD_TOKEN")
PREFIX = config("PREFIX")


def open_connection():
    try:
        new_connection = sqlite3.connect("bot.db")
    except Exception as e:
        print(e)
        raise Exception("DB Failed")

    return new_connection


client = discord.Client()
quote = ""


@client.event
async def on_guild_join(guild):
    connection = open_connection()
    cursor = connection.execute(f"""INSERT INTO SERVER (server_id, channel_id, post_time)
    VALUES ({guild.id}, NULL, NULL);""")
    print([row for row in cursor])
    connection.commit()
    connection.close()


@client.event
async def on_guild_remove(guild):
    connection = open_connection()
    cursor = connection.execute(f"""DELETE FROM SERVER WHERE server_id = {guild.id};""")
    print([row for row in cursor])
    connection.commit()
    connection.close()


@client.event
async def on_message(message):

        if message.content.startswith(PREFIX):

            if message.guild.owner_id != message.author.id:
                return await message.reply("Only the owner can make commands")

            command, *args = message.content[1:].split()

            if command.lower() == "time":

                try:
                    hour = int(args[0])
                    minute = int(args[1])

                except IndexError:
                    return await message.reply("I require an hours and a minute value in the format XX YY where X and Y are numbers")

                except ValueError:
                    return await message.reply("I require an hours and a minute value in the format XX YY where X and Y are numbers")

                if hour < 0 or hour > 23:
                    return await message.reply("hours outside of 0 to 23 range")

                if minute < 0 or minute > 59:
                    return await message.reply("minute outside of 0 to 59 range")


                connection = open_connection()
                minute = ((minute // 5)*5)  # round minute to nearest five, going down, for simplicity
                connection.execute(f"UPDATE SERVER SET post_time = '{hour}:{minute}' WHERE server_id = {message.guild.id}")

                await message.reply(f"Set quote time to: approx {hour}:{minute} UTC")
                connection.commit()
                connection.close()
                return

            elif command.lower() == "channel":

                set_channel = args[0]
                text_channels = message.guild.text_channels

                for text_channel in text_channels:
                    if text_channel.name == set_channel:
                        connection = open_connection()
                        connection.execute(f"UPDATE SERVER "
                                           f"SET channel_id = {text_channel.id} "
                                           f"WHERE server_id = {message.guild.id};")
                        await message.reply(f"Set quote channel to {text_channel.name}")
                        connection.commit()
                        connection.close()
                        return

                return await message.reply(f"Couldn't find {set_channel}")
                pass

            elif command.lower() in ("help", "h"):

                return await message.reply("Commands are only accessible to the server owner. \n"
                                           "Commands: \n"
                                           "- **channel** - set the channel that quotes are posted in. provide the name of the channel as the argument. \n\n"
                                           "- **time** - set the time (in UTC) that the quote is published in the server. \n"
                                           "provide with two arguments, hour and minute as numbers 0-23 and 0-59. \n"
                                           "Values for minutes may be rounded to the nearest five. \n\n"
                                           "Prefix for commands is "+PREFIX)

            else:
                return await message.reply(f"I do not recognise the command {command}")


def get_quote():
    quotes = open("thoughts.csv", "r")
    quotes_reader = csv.reader(quotes)
    line_count = sum(1 for _ in quotes_reader)
    quotes.seek(0)
    random_line = random.randint(0, line_count-1)

    for i, row in enumerate(quotes_reader):
        if i == random_line:
            print(row[0])
            return row[0]

def get_channel(server_id, channel_id):
    guild = client.get_guild(server_id)
    channel = None
    if server_id is not None:
        channel = guild.get_channel(channel_id)
        if channel is None:
            # use system as backup
            channel = guild.system_channel

    # assuming no system, check all text manually and use first
    if channel is None:
        for possible_channel in guild.text_channels:
            print(possible_channel)
            if possible_channel.permissions_for(possible_channel.guild.me).send_messages:
                channel = possible_channel
                break
    return channel


@tasks.loop(minutes=5)
async def check_time():
    """ Run every five minutes, check if any servers need their Quote """
    connection = open_connection()

    time = datetime.utcnow()
    print(time)
    hour = time.hour
    minute = (time.minute // 5)*5
    print(hour, minute)
    cursor = connection.execute(f"""SELECT * FROM SERVER WHERE post_time = '{hour}:{minute}'""")
    for row in cursor:
        print(row)
        channel = get_channel(row[0], row[1])

        # try to send
        if channel is not None:
            await channel.send(get_quote())



    if (time.hour == 0 and ((time.minute // 5)*5) == 0):
        cursor = connection.execute("""SELECT server_id, channel_id, post_time FROM SERVER;""")
        # print([row for row in cursor])
        for row in cursor:
            print(row)
            channel = get_channel(row[0], row[1])

            # try to send
            if channel is not None:
                await channel.send(get_quote())
    connection.close()



@client.event
async def on_ready():
    check_time.start()
    print("Ready to spread the word of the Emperor!")


client.run(TOKEN)
