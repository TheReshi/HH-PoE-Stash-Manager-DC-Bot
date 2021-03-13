import datetime, discord, json, re
import imagehandler as imgh
import config as cfg

class StashRecord:
    def __init__(self, id, receiver, giver, given_date, img_url):
        self.id = id
        self.receiver = receiver
        self.giver = giver.name
        self.given_date = given_date.strftime('%Y-%m-%d %H:%M')
        self.deadline = (given_date + datetime.timedelta(days=5)).strftime('%Y-%m-%d %H:%M')
        self.img_url = imgh.upload_to_imgur(img_url)
        self.extended = 0
        self.warned = 0

def read_log():
    with open(cfg.log_path) as json_file:
        return json.load(json_file)

def write_log(data):
    with open(cfg.log_path, 'w') as outfile:
        json.dump(data, outfile)

def generate_give_embed(new_record):
    embed = discord.Embed(color=0x555555)
    embed.set_thumbnail(url = new_record.img_url)
    embed.add_field(name="**Are the following details correct? Use a reaction!**",
                    value=f"""Account name: {new_record.receiver}
                              Given by: {new_record.giver}
                              Given on: {new_record.given_date}
                              Items: {new_record.img_url}""",
                    inline=False)
    return embed

def check_authority(role, author):
    return role in [role.id for role in author.roles]

def add_new_record(new_record):
    data = read_log()
    data["counter"] = int(data["counter"]) + 1
    new_record.id = data["counter"]
    data["rentals"].append(new_record.__dict__)
    write_log(data)
    return generate_give_confirm_embed(new_record)

def generate_give_confirm_embed(new_record):
    embed = discord.Embed(title="**RENTAL SUCCESSFUL**", color=0x1EBA02)
    embed.set_thumbnail(url = new_record.img_url)
    embed.add_field(name=f"**ID: {new_record.id}**",
                    value=f"""Account name: {new_record.receiver}
                              Given by: {new_record.giver}
                              Given on: {new_record.given_date}
                              Deadline: {new_record.deadline}
                              Items: {new_record.img_url}""",
                    inline=False)
    return embed

def generate_give_abort_embed(new_record):
    embed = discord.Embed(title="**RENTAL ABORTED**", color=0xFF0000)
    embed.set_thumbnail(url = new_record.img_url)
    embed.add_field(name=f"**The following process is aborted**",
                    value=f"""Account name: {new_record.receiver}
                              Given by: {new_record.giver}
                              Given on: {new_record.given_date}
                              Items: {new_record.img_url}""",
                    inline=False)
    return embed

def get_records():
    data = read_log()
    if len(data["rentals"]) < 1:
        embed = discord.Embed(title="**NO ACTIVE RENTALS**", color=0x555555)
    else:
        embed = discord.Embed(title="**CURRENTLY ACTIVE RENTALS**", color=0x555555)
    for record in data["rentals"]:
        deadline_str = get_deadline_str(record)
        embed.add_field(name=f"**ID: {record['id']}**",
                        value=f"""> Account name: {record['receiver']}
                                  > Given by: {record['giver']}
                                  > Given on: {record['given_date']}
                                  > {deadline_str}{record['deadline']}
                                  > Items: <{record['img_url']}>""",
                        inline=False)
    return embed

def delete_record(id, author, date):
    data = read_log()
    embed = False
    for i, record in enumerate(data["rentals"]):
        if int(id) == int(record["id"]):
            deadline_str = get_deadline_str(record)
            embed = discord.Embed(title="**RENTAL ENDED**", color=0xFF0000)
            embed.set_thumbnail(url = record['img_url'])
            embed.add_field(name=f"**ID: {record['id']}**",
                            value=f"""Account name: {record['receiver']}
                                      Given by: {record['giver']}
                                      Given on: {record['given_date']}
                                      {deadline_str}{record['deadline']}
                                      Taken by: {author.name}
                                      Taken on: {date.strftime('%Y-%m-%d %H:%M')}
                                      Items: {record['img_url']}""",
                            inline=False)
            del data["rentals"][i]
            break
    write_log(data)
    if not embed:
        embed = discord.Embed(title=f"**Couldn't find stash record!**", color=0xFF0000)
        embed.add_field(name=f"ID: {id}", value=f"For available stash log record, see !get_list", inline=False)
    return embed

def get_expired_list():
    data = read_log()
    expired_rentals = get_expired(data)
    if len(expired_rentals) > 0:
        embed = discord.Embed(title=f"**EXPIRED RENTALS: {len(expired_rentals)}**", color=0xFF0000)
        for expired_rental in expired_rentals:
            deadline_str = get_deadline_str(expired_rental)
            if int(expired_rental["extended"]) == 0:
                embed.add_field(name=f"**ID: {expired_rental['id']}**",
                                value=f"""Account name: {expired_rental['receiver']}
                                        Given by: {expired_rental['giver']}
                                        Given on: {expired_rental['given_date']}
                                        {deadline_str}{expired_rental['deadline']}
                                        Items: {expired_rental['img_url']}
                                        
                                        **CAN BE EXTENDED 1 MORE TIME!**""",
                                inline=False)
            else:
                embed.add_field(name=f"**ID: {expired_rental['id']}**",
                                value=f"""Account name: {expired_rental['receiver']}
                                        Given by: {expired_rental['giver']}
                                        Given on: {expired_rental['given_date']}
                                        {deadline_str}{expired_rental['deadline']}
                                        Items: {expired_rental['img_url']}
                                        
                                        **CANNOT BE EXTENDED ANYMORE!**""",
                                inline=False)
    else:
        embed = discord.Embed(title=f"**NO EXPIRED RENTALS**", color=0x1EBA02)
    return embed

def extend_rental(id, author):
    data = read_log()
    embed = ""
    for i, record in enumerate(data["rentals"]):
        if int(id) == int(record["id"]):
            deadline_str = get_deadline_str(record)
            if int(record["extended"]) == 1:
                embed = discord.Embed(title="**RENTAL ALREADY EXTENDED**", color=0xFF0000)
                embed.set_thumbnail(url = record['img_url'])
                embed.add_field(name=f"**ID: {record['id']}**",
                                value=f"""Account name: {record['receiver']}
                                        Given by: {record['giver']}
                                        Given on: {record['given_date']}
                                        {deadline_str}{record['deadline']}
                                        Items: {record['img_url']}""",
                                inline=False)
            else:
                record["deadline"] = (into_datetime(record["deadline"]) + datetime.timedelta(days=5)).strftime('%Y-%m-%d %H:%M')
                record["extended"] = 1
                record["warned"] = 0
                data["rentals"][i] = record
                embed = discord.Embed(title="**RENTAL SUCCESSFULLY EXTENDED**", color=0x1EBA02)
                embed.set_thumbnail(url = record['img_url'])
                embed.add_field(name=f"**ID: {record['id']}**",
                                value=f"""Account name: {record['receiver']}
                                        Given by: {record['giver']}
                                        Given on: {record['given_date']}
                                        {deadline_str}{record['deadline']}
                                        Extended by: {author.name}
                                        Items: {record['img_url']}""",
                                inline=False)
            break
    if not embed:
        embed = discord.Embed(title="**Couldn't find the specified rental ID**", color=0xFF0000)
    write_log(data)
    return embed


def into_datetime(strtime):
    times = re.split(r"-|:|\s", strtime)
    times = [int(time) for time in times]
    return datetime.datetime(times[0], times[1], times[2], times[3], times[4])

def get_deadline_str(record):
    if int(record["extended"]) > 0:
        return "Extended Deadline: "
    else:
        return "Deadline: "

def get_expired(data):
    expired_rentals = []
    for record in data["rentals"]:
        current_time = datetime.datetime.now()
        expiry_time = into_datetime(record["deadline"])
        if current_time > expiry_time:
            expired_rentals.append(record)
    return expired_rentals

def warn_expired():
    data = read_log()
    counter = 0
    for i, record in enumerate(data["rentals"]):
        current_time = datetime.datetime.now()
        expiry_time = into_datetime(record["deadline"])
        if current_time > expiry_time:
            embed = discord.Embed(title=f"**RENTALS EXPIRED TODAY**", color=0xFF0000)
            if int(record["warned"]) == 0:
                counter = counter + 1
                record["warned"] = 1
                data["rentals"][i] = record
                write_log(data)
                deadline_str = get_deadline_str(record)
                embed.add_field(name=f"**ID: {record['id']}**",
                                    value=f"""Account name: {record['receiver']}
                                            Given by: {record['giver']}
                                            Given on: {record['given_date']}
                                            {deadline_str}{record['deadline']}
                                            Items: {record['img_url']}""",
                                    inline=False)
    if counter > 0:
        return embed
    return False
