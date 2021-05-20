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
    embed.add_field(name="**Helyesek az alábbi adatok? Használd az alsó hangulatjeleket!**",
                    value=f"""Account név: {new_record.receiver}
                              Kiadó neve: {new_record.giver}
                              Kiadás dátuma: {new_record.given_date}
                              Itemek: {new_record.img_url}""",
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
    embed = discord.Embed(title="**SIKERESEN KIADVA**", color=0x1EBA02)
    embed.set_thumbnail(url = new_record.img_url)
    embed.add_field(name=f"**SORSZÁM: {new_record.id}**",
                    value=f"""Account név: {new_record.receiver}
                              Kiadó neve: {new_record.giver}
                              Kiadás dátuma: {new_record.given_date}
                              Határidő: {new_record.deadline}
                              Itemek: {new_record.img_url}""",
                    inline=False)
    return embed

def generate_give_abort_embed(new_record):
    embed = discord.Embed(title="**KIADÁS MEGSZAKÍTVA**", color=0xFF0000)
    embed.set_thumbnail(url = new_record.img_url)
    embed.add_field(name=f"**Az alábbi kiadás meg lett szakítva, így nem került mentésre**",
                    value=f"""Account név: {new_record.receiver}
                              Kiadó neve: {new_record.giver}
                              Kiadás dátuma: {new_record.given_date}
                              Itemek: {new_record.img_url}""",
                    inline=False)
    return embed

def get_records():
    data = read_log()
    if len(data["rentals"]) < 1:
        embed = discord.Embed(title="**NINCS AKTÍV KINTLÉVŐSÉG**", color=0x555555)
    else:
        embed = discord.Embed(title="**AKTÍV KINTLÉVŐSÉGEK**", color=0x555555)
    for record in data["rentals"]:
        deadline_str = get_deadline_str(record)
        embed.add_field(name=f"**SORSZÁM: {record['id']}**",
                        value=f"""> Account név: {record['receiver']}
                                  > Kiadó neve: {record['giver']}
                                  > Kiadás dátuma: {record['given_date']}
                                  > {deadline_str}{record['deadline']}
                                  > Itemek: <{record['img_url']}>""",
                        inline=False)
    return embed

def delete_record(id, author, date):
    data = read_log()
    embed = False
    for i, record in enumerate(data["rentals"]):
        if int(id) == int(record["id"]):
            deadline_str = get_deadline_str(record)
            embed = discord.Embed(title="**VISSZAVÉTEL**", color=0xFF0000)
            embed.set_thumbnail(url = record['img_url'])
            embed.add_field(name=f"**SORSZÁM: {record['id']}**",
                            value=f"""Account név: {record['receiver']}
                                      Kiadó neve: {record['giver']}
                                      Kiadás dátuma: {record['given_date']}
                                      {deadline_str}{record['deadline']}
                                      Visszavevő neve: {author.name}
                                      Visszaadás dátuma: {date.strftime('%Y-%m-%d %H:%M')}
                                      Itemek: {record['img_url']}""",
                            inline=False)
            del data["rentals"][i]
            break
    write_log(data)
    if not embed:
        embed = discord.Embed(title=f"**Nincs ilyen kintlévőség!**", color=0xFF0000)
        embed.add_field(name=f"ID: {id}", value=f"A kintlévőségek listájáért használd a \"!list\" parancsot!", inline=False)
    return embed

def get_expired_list():
    data = read_log()
    expired_rentals = get_expired(data)
    if len(expired_rentals) > 0:
        embed = discord.Embed(title=f"**LEJÁRT KINTLÉVŐSÉGEK: {len(expired_rentals)}**", color=0xFF0000)
        for expired_rental in expired_rentals:
            deadline_str = get_deadline_str(expired_rental)
            if int(expired_rental["extended"]) == 0:
                embed.add_field(name=f"**SORSZÁM: {expired_rental['id']}**",
                                value=f"""Account név: {expired_rental['receiver']}
                                        Kiadó neve: {expired_rental['giver']}
                                        Kiadás dátuma: {expired_rental['given_date']}
                                        {deadline_str}{expired_rental['deadline']}
                                        Itemek: {expired_rental['img_url']}
                                        
                                        **HOSSZABBÍTÁS LEHETSÉGES!**""",
                                inline=False)
            else:
                embed.add_field(name=f"**SORSZÁM: {expired_rental['id']}**",
                                value=f"""Account név: {expired_rental['receiver']}
                                        Kiadó neve: {expired_rental['giver']}
                                        Kiadás dátuma: {expired_rental['given_date']}
                                        {deadline_str}{expired_rental['deadline']}
                                        Itemek: {expired_rental['img_url']}
                                        
                                        **HOSSZABBÍTÁS NEM LEHETSÉGES!**""",
                                inline=False)
    else:
        embed = discord.Embed(title=f"**NINCS LEJÁRT KINTLÉVŐSÉG**", color=0x1EBA02)
    return embed

def extend_rental(id, author):
    data = read_log()
    embed = ""
    for i, record in enumerate(data["rentals"]):
        if int(id) == int(record["id"]):
            deadline_str = get_deadline_str(record)
            if int(record["extended"]) == 1:
                embed = discord.Embed(title="**HOSSZABBÍTÁS NEM LEHETSÉGES**", color=0xFF0000)
                embed.set_thumbnail(url = record['img_url'])
                embed.add_field(name=f"**SORSZÁM: {record['id']}**",
                                value=f"""Account név: {record['receiver']}
                                        Kiadó neve: {record['giver']}
                                        Kiadás dátuma: {record['given_date']}
                                        {deadline_str}{record['deadline']}
                                        Itemek: {record['img_url']}""",
                                inline=False)
            else:
                record["deadline"] = (into_datetime(record["deadline"]) + datetime.timedelta(days=5)).strftime('%Y-%m-%d %H:%M')
                record["extended"] = 1
                record["warned"] = 0
                data["rentals"][i] = record
                embed = discord.Embed(title="**HOSSZABBÍTÁS SIKERES**", color=0x1EBA02)
                embed.set_thumbnail(url = record['img_url'])
                embed.add_field(name=f"**SORSZÁM: {record['id']}**",
                                value=f"""Account név: {record['receiver']}
                                        Kiadó neve: {record['giver']}
                                        Kiadás dátuma: {record['given_date']}
                                        {deadline_str}{record['deadline']}
                                        Hosszabbította: {author.name}
                                        Itemek: {record['img_url']}""",
                                inline=False)
            break
    if not embed:
        embed = discord.Embed(title="**Ilyen sorszám nem létezik, kérlek használd a \"!list\" parancsot a lehetséges sorszámokért!**", color=0xFF0000)
    write_log(data)
    return embed


def into_datetime(strtime):
    times = re.split(r"-|:|\s", strtime)
    times = [int(time) for time in times]
    return datetime.datetime(times[0], times[1], times[2], times[3], times[4])

def get_deadline_str(record):
    if int(record["extended"]) > 0:
        return "Hosszabbított határidő: "
    else:
        return "Határidő: "

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
            embed = discord.Embed(title=f"**MA LEJÁRT KINTLÉVŐSÉGEK**", color=0xFF0000)
            if int(record["warned"]) == 0:
                counter = counter + 1
                record["warned"] = 1
                data["rentals"][i] = record
                write_log(data)
                deadline_str = get_deadline_str(record)
                embed.add_field(name=f"**SORSZÁM: {record['id']}**",
                                    value=f"""Account név: {record['receiver']}
                                            Kiadó neve: {record['giver']}
                                            Kiadás dátuma: {record['given_date']}
                                            {deadline_str}{record['deadline']}
                                            Itemek: {record['img_url']}""",
                                    inline=False)
    if counter > 0:
        return embed
    return False
