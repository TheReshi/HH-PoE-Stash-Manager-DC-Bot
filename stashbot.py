# bot.py
import imagehandler as imgh
import os
import random
import discord
import math
import datetime
import resources as res
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

give_ongoing = False
give_ongoing_details = []
yes_emoji = '\u2705'
no_emoji = '\u274C'

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='give')
async def give(ctx, username = ''):
    global give_ongoing
    global give_ongoing_details
    emojis = [yes_emoji, no_emoji]
    author = ctx.message.author.name
    date = ctx.message.created_at.replace(second=0, microsecond=0) + datetime.timedelta(hours=1)
    try:
        if (username):
            items = imgh.upload_to_imgur(ctx.message.attachments[0].url)
            give_ongoing = True
            give_ongoing_details = [username, author, date, items]
            msg = res.generate_give_embed(give_ongoing_details)
            sent_msg = await ctx.send(embed=msg)
            for emoji in emojis:
                await sent_msg.add_reaction(emoji)
        else:
            await ctx.send("__Wrong command format!__\n\n**The correct format is**:\n>>> !give [username]\nDo not forget to also attach the image of the items!")
    except:
        await ctx.send("__Wrong command format!__\n\n**The correct format is**:\n>>> !give [username]\nDo not forget to also attach the image of the items!")

    await ctx.message.delete()

@bot.command(name='list')
async def list(ctx):
    msg = res.get_records()
    await ctx.send(embed=msg)
    await ctx.message.delete()

@bot.command(name='take')
async def take(ctx, id):
    if (id):
            msg = res.delete_record(id)
            await ctx.send(embed=msg)
            await ctx.message.delete()
    else:
        await ctx.send("__Wrong command format!__\n\n**The correct format is**:\n>>> !take [id]")

@bot.command(name='test')
async def test(ctx):
    emojis = [yes_emoji, no_emoji]
    msg = await ctx.send("TEST!")

    for emoji in emojis:
        await msg.add_reaction(emoji)

    await ctx.message.delete()

@bot.event
async def on_reaction_add(reaction, user):
    global give_ongoing
    global give_ongoing_details
    emoji = reaction.emoji

    if user.bot:
        return

    if give_ongoing:
        if emoji == yes_emoji:
            origin_channel = reaction.message.channel
            await reaction.message.delete()
            msg = res.add_new_record(give_ongoing_details)
            await origin_channel.send(embed=msg)
            give_ongoing = False
            give_ongoing_details = []
        elif emoji == no_emoji:
            origin_channel = reaction.message.channel
            await reaction.message.delete()
            msg = res.generate_give_abort_embed(give_ongoing_details)
            await origin_channel.send(embed=msg)
            give_ongoing = False
            give_ongoing_details = []
    return


bot.run(TOKEN)