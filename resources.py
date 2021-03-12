import imagehandler as imgh
import config as cfg
import datetime
import discord

give_ongoing = False
give_data = []
log_path = "log.db"

def read_log():
    with open(log_path) as log:
        data = [x for x in log]
        return data

def add_new_record():
    data = read_log()
    if len(data) == 1:
        data[0] = f"{str(int(data[0]) + 1)}"
    else:
        data[0] = f"{str(int(data[0]) + 1)}\n"
    data.append(f"\n{data[0].strip()},{strify(give_data[1:])}")
    with open(log_path, 'w') as log:
        log.writelines(data)
    return generate_give_confirm_embed(data[0].strip())

def delete_record(id, author, date):
    data = read_log()
    strbuilder = [data[0]]
    embed = ''
    for row in data[1:]:
        if str(id) != row.split(",")[0]:
            strbuilder.append(f"{row}")
        else:
            if row[0] == data[-1][0]:
                strbuilder[-1] = strbuilder[-1][:-1]
            row = row.split(',')
            row[3] = str_to_date(row[3])
            embed = discord.Embed(title="**RENTAL ENDED!**", color=0xFF0000)
            embed.set_thumbnail(url = row[4])
            embed.add_field(name=f"**Log ID: {row[0]}**", value=f"Username: {row[1]}\nGiven by: {row[2]}\nGiven on: {row[3].strftime('%Y-%m-%d %H:%M')}\nTaken by: {author.name}\nTaken on: {date.strftime('%Y-%m-%d %H:%M')}\nItems: {row[4]}", inline=False)
    with open(log_path, 'w') as log:
        log.writelines(strbuilder)
    if not embed:
        embed = discord.Embed(title=f"**Cannot find stash record!**", color=0xFF0000)
        embed.add_field(name=f"ID: {id}", value=f"For available stash log record, see !get_list", inline=False)
    return embed

def get_records():
    embed = discord.Embed(title="**CURRENTLY ACTIVE RENTALS**", color=0x555555)
    data = read_log()
    for row in data[1:]:
        datas = row.strip().split(',')
        datas[3] = str_to_date(datas[3])
        embed.add_field(name=f"**ID: {datas[0]}**", value=f"> Username: {datas[1]}\n> Given by: {datas[2]}\n> Given on: {datas[3].strftime('%Y-%m-%d %H:%M')}\n> Items: <{datas[4]}>", inline=False)
    return embed

def generate_give_embed():
    embed = discord.Embed(color=0x555555)
    embed.set_thumbnail(url = give_data[cfg.log_url])
    embed.add_field(name="**Are the following details correct? Use a reaction!**", value=f"Username: {give_data[cfg.log_receiver]}\nGiven by: {give_data[cfg.log_giver].name}\nGiven on: {give_data[cfg.log_date].strftime('%Y-%m-%d %H:%M')}\nItems: {give_data[cfg.log_url]}", inline=False)
    return embed

def generate_give_confirm_embed(id):
    embed = discord.Embed(title="**RENTAL SUCCESS!**", color=0x1EBA02)
    embed.set_thumbnail(url = give_data[cfg.log_url])
    embed.add_field(name=f"**ID: {id}**", value=f"Username: {give_data[cfg.log_receiver]}\nGiven by: {give_data[cfg.log_giver].name}\nGiven on: {give_data[cfg.log_date].strftime('%Y-%m-%d %H:%M')}\nItems: {give_data[cfg.log_url]}", inline=False)
    return embed

def generate_give_abort_embed():
    embed = discord.Embed(title="**RENTAL ABORTED!**", color=0xFF0000)
    embed.set_thumbnail(url = give_data[cfg.log_url])
    embed.add_field(name=f"**The following process is aborted**", value=f"Username: {give_data[cfg.log_receiver]}\nGiven by: {give_data[cfg.log_giver].name}\nGiven on: {give_data[cfg.log_date].strftime('%Y-%m-%d %H:%M')}\nItems: {give_data[cfg.log_url]}", inline=False)
    return embed

def strify(element, char = ','):
    element_copy = element.copy()
    element_copy[2] = date_to_str(element_copy[2])
    element_copy[1] = element_copy[1].name
    return char.join(element_copy)

def date_to_str(dt):
    return dt.strftime('%Y-%m-%d-%H-%M')

def str_to_date(str_dt):
    str_dt = str_dt.split("-")
    return datetime.datetime(int(str_dt[0]), int(str_dt[1]), int(str_dt[2]), int(str_dt[3]), int(str_dt[4]))

def check_authority(role, author):
    return role in [role.id for role in author.roles]
