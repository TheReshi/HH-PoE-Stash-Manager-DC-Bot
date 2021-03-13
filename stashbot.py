# bot.py
import os, random, discord, math, datetime, time, imagehandler as imgh, config as cfg, resources as res
from discord.ext import commands, tasks

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=cfg.bot_prefix, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="give", brief=f"{cfg.bot_prefix}give [account name] (attach image of items)", description="Used for adding items to clan members.")
@commands.has_role(cfg.accepted_role)
async def give(ctx, account_name = ''):
    emojis = [cfg.yes_emoji, cfg.no_emoji]
    author = ctx.message.author
    date = ctx.message.created_at.replace(second=0, microsecond=0) + datetime.timedelta(hours=1)
    #try:
    if account_name:
        bot.give_ongoing = True
        bot.current_record = res.StashRecord(-1, account_name, author, date, ctx.message.attachments[0].url)
        msg = res.generate_give_embed(bot.current_record)
        sent_msg = await ctx.send(embed=msg)
        for emoji in emojis:
            await sent_msg.add_reaction(emoji)
    else:
        await ctx.send("__Wrong command format!__\n\n**The correct format is**:\n>>> !give [account name]\nDo not forget to also attach the image of the items!")
    #except:
    #    await ctx.send("__Wrong command format!__\n\n**The correct format is**:\n>>> !give [account name]\nDo not forget to also attach the image of the items!")
    await ctx.message.delete()

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot or not res.check_authority(cfg.accepted_role, user):
        return

    if bot.give_ongoing:
        emoji = reaction.emoji
        if emoji == cfg.yes_emoji:
            origin_channel = reaction.message.channel
            await reaction.message.delete()
            msg = res.add_new_record(bot.current_record)
            await origin_channel.send(embed=msg)
            bot.give_ongoing = False
            del bot.current_record
        elif emoji == cfg.no_emoji:
            origin_channel = reaction.message.channel
            await reaction.message.delete()
            msg = res.generate_give_abort_embed(bot.current_record)
            await origin_channel.send(embed=msg)
            bot.give_ongoing = False
            del bot.current_record
    return

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

@bot.command(name="help", brief=f"{cfg.bot_prefix}help", description="Shows this command.")
async def help(ctx):
    await ctx.message.delete()
    strbuilder = "\n**AVAILABLE COMMANDS**\n"
    for comm in bot.commands:
        if comm.name != "test" and comm.name != "help":
            strbuilder += f"\n**{cfg.bot_prefix}{comm.name}**\n```\nSyntax: {comm.brief}\nDescription: {comm.description}\n```"
    await ctx.send(strbuilder)

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingRole):
        await ctx.message.delete()
        await ctx.send(f"{ctx.message.author.name}, you don't have permission for this command!")

@bot.command(name="expired", brief=f"{cfg.bot_prefix}expired", description="Used for checking expired rentals.")
@commands.has_role(cfg.accepted_role)
async def expired(ctx):
    msg = res.get_expired_list()
    await ctx.send(embed=msg)
    await ctx.message.delete()

@bot.command(name="extend", brief=f"{cfg.bot_prefix}extend [id]", description="Used for extending rentals by 5 days.")
@commands.has_role(cfg.accepted_role)
async def extend(ctx, id):
    author = ctx.message.author
    msg = res.extend_rental(id, author)
    await ctx.send(embed=msg)
    await ctx.message.delete()

@bot.command(name="test")
@commands.has_role(cfg.accepted_role)
async def test(ctx):
    msg = res.warn_expired()
    if msg:
        await ctx.send("Asd!", embed=msg)

@tasks.loop(hours=24)
async def warn_expired():
    msg_channel = bot.get_channel(cfg.bot_channel)
    msg = res.warn_expired()
    mention_msg = ' '.join([f"<@&{role}>" for role in cfg.roles_to_mention])
    if msg:
        await msg_channel.send(mention_msg, embed=msg)

@warn_expired.before_loop
async def before():
    await bot.wait_until_ready()

warn_expired.start()

bot.run(TOKEN)