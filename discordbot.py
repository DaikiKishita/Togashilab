import discord
from discord import app_commands
import sqlite3 as sq
import os
from dotenv import load_dotenv

load_dotenv('.env')

#============Channel ID==================
To=os.getenv("ChannelId")
TOKEN=os.getenv("TOKEN")
#========設定=================
channelid=To
intents=discord.Intents.default()
intents.messages=True
intents.message_content=True
client =discord.Client(intents=intents)
bot = app_commands.CommandTree(client)
channel_sent = None

dbname = "static/Users.db"

def exesql(sql):
    with sq.connect(dbname) as conn:
        cur = conn.cursor()
        result=cur.execute(sql)
        conn.commit()
        return list(result)

@client.event
async def on_ready():
    await bot.sync()

@bot.command(name="show",description="誰が滞在してるかなぁ(＾ー＾)")
async def show(interaction:discord.Interaction):
    ctx=interaction
    names=exesql("select name from Users where color='green'")
    if list(names)==[]:
        string="現在研究室には誰もいません\nこれは富樫研の危機か？"
        await ctx.response.send_message(string)
    else:
        string="↓今現在研究室にいる人↓\n"
        for i in names:
            string+=f"・{i[0]}\n"
        await ctx.response.send_message(string)

client.run(TOKEN)