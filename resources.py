import imagehandler as imgh
import datetime
import discord

logfile = "log.txt"

def read_log():
    with open(logfile) as log:
        data = [x for x in log]
        return data

def add_new_record(new_element):
    data = read_log()
    if data[0] == '0':
        data[0] = f"{str(int(data[0]) + 1)}"
    else:
        data[0] = f"{str(int(data[0]) + 1)}\n"
    data.append(f"\n{data[0].strip()},{strify(new_element)}")
    with open(logfile, 'w') as log:
        log.writelines(data)
    return generate_give_confirm_embed(new_element, data[0].strip())

def delete_record(id):
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
            embed.add_field(name=f"**Log ID: {row[0]}**", value=f"Username: {row[1]}\nGiven by: {row[2]}\nGiven on: {row[3].strftime('%Y-%m-%d %H:%M')}\nItems: {row[4]}", inline=False)
    with open(logfile, 'w') as log:
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

def generate_give_embed(data):
    embed = discord.Embed(color=0x555555)
    embed.set_thumbnail(url = data[3])
    embed.add_field(name="**Are the following details correct? Use a reaction!**", value=f"Username: {data[0]}\nGiven by: {data[1]}\nGiven on: {data[2].strftime('%Y-%m-%d %H:%M')}\nItems: {data[3]}", inline=False)
    return embed

def generate_give_confirm_embed(data, id):
    embed = discord.Embed(title="**RENTAL SUCCESS!**", color=0x1EBA02)
    embed.set_thumbnail(url = data[3])
    embed.add_field(name=f"**ID: {id}**", value=f"Username: {data[0]}\nGiven by: {data[1]}\nGiven on: {data[2].strftime('%Y-%m-%d %H:%M')}\nItems: {data[3]}", inline=False)
    return embed

def generate_give_abort_embed(data):
    data[2] = data[2].strftime('%Y-%m-%d %H:%M')
    embed = discord.Embed(title="**RENTAL ABORTED!**", color=0xFF0000)
    embed.set_thumbnail(url = data[3])
    embed.add_field(name=f"**The following process is aborted**", value=f"Username: {data[0]}\nGiven by: {data[1]}\nGiven on: {data[2]}\nItems: {data[3]}", inline=False)
    return embed

def strify(element, char = ','):
    element_copy = element.copy()
    element_copy[2] = date_to_str(element_copy[2])
    return char.join(element_copy)

def date_to_str(dt):
    return dt.strftime('%Y-%m-%d-%H-%M')

def str_to_date(str_dt):
    str_dt = str_dt.split("-")
    return datetime.datetime(int(str_dt[0]), int(str_dt[1]), int(str_dt[2]), int(str_dt[3]), int(str_dt[4]))