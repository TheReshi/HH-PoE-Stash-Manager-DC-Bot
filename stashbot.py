# bot.py
import os, random, discord, math, datetime, imagehandler as imgh, config as cfg, resources as res
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=cfg.bot_prefix, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="give", brief=f"{cfg.bot_prefix}give [Account name] (Attach image of items)", description="Used for adding items to clan members.")
async def give(ctx, username = ''):
    author = ctx.message.author
    emojis = [cfg.yes_emoji, cfg.no_emoji]
    date = ctx.message.created_at.replace(second=0, microsecond=0) + datetime.timedelta(hours=1)
    #try:
    if username:
        items = imgh.upload_to_imgur(ctx.message.attachments[0].url)
        res.give_ongoing = True
        res.give_data = [-1, username, author, date, items]
        msg = res.generate_give_embed()
        sent_msg = await ctx.send(embed=msg)
        for emoji in emojis:
            await sent_msg.add_reaction(emoji)
    else:
        await ctx.send("__Wrong command format!__\n\n**The correct format is**:\n>>> !give [username]\nDo not forget to also attach the image of the items!")
    #except:
    #    await ctx.send("__Wrong command format!__\n\n**The correct format is**:\n>>> !give [username]\nDo not forget to also attach the image of the items!")
    await ctx.message.delete()

@bot.command(name="list", brief=f"{cfg.bot_prefix}list", description="Used for listing all the currently active item rentals and their IDs.")
@commands.has_role(cfg.accepted_role)
async def list(ctx):
    msg = res.get_records()
    await ctx.send(embed=msg)
    await ctx.message.delete()

@bot.command(name="take", brief=f"{cfg.bot_prefix}take [Rental ID]", description="Used for taking back items from clan members.")
@commands.has_role(cfg.accepted_role)
async def take(ctx, id):
    author = ctx.message.author
    date = ctx.message.created_at.replace(second=0, microsecond=0) + datetime.timedelta(hours=1)
    if (id):
            msg = res.delete_record(id, author, date)
            await ctx.send(embed=msg)
            await ctx.message.delete()
    else:
        await ctx.send("__Wrong command format!__\n\n**The correct format is**:\n>>> !take [id]")

@bot.command(name="test")
@commands.has_role(cfg.accepted_role)
async def test(ctx):
    print([comm.name for comm in bot.commands])

@bot.command(name="help", brief=f"{cfg.bot_prefix}help", description="Shows this command.")
async def help(ctx):
    await ctx.message.delete()
    strbuilder = "\n**AVAILABLE COMMANDS**\n"
    for comm in bot.commands:
        if comm.name != "test" and comm.name != "help":
            strbuilder += f"\n**{cfg.bot_prefix}{comm.name}**\n```\nSyntax: {comm.brief}\nDescription: {comm.description}\n```"
    await ctx.send(strbuilder)
    
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if not res.check_authority(cfg.accepted_role, user):
        return

    if res.give_ongoing:
        emoji = reaction.emoji
        if emoji == cfg.yes_emoji:
            origin_channel = reaction.message.channel
            await reaction.message.delete()
            msg = res.add_new_record()
            await origin_channel.send(embed=msg)
            res.give_ongoing = False
            res.give_data = []
        elif emoji == cfg.no_emoji:
            origin_channel = reaction.message.channel
            await reaction.message.delete()
            msg = res.generate_give_abort_embed()
            await origin_channel.send(embed=msg)
            res.give_ongoing = False
            res.give_data = []
    return

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingRole):
        await ctx.message.delete()
        await ctx.send(f"{ctx.message.author.name}, you don't have permission for this command!")

bot.run(TOKEN)