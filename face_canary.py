from discord.ext.commands import Bot
import random
import asyncio
from random import sample
import datetime
import time
import discord
import mysql.connector as mysql
import sys
import re
import time
import os
import nltk.data
import nltk
from nltk.tokenize import sent_tokenize
import csv
import FACE
import random
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from discord.ext import commands, tasks
import matplotlib.pyplot as plt
from num2words import num2words

PREFIX = ['c ','C ']
token='NzcwNzY5NDk5MzA1NjcyNzU0.X5iZCA.rrqAHZ_GzKtidTYf7S5Gj9NAn6U'
intents = discord.Intents.default()
intents.members = True
client = Bot(command_prefix=PREFIX,intents=intents)
client.remove_command('help')

in_pk = []
close_pk = []
carding = []
cat_embed = discord.Embed(
    title=f'CATEGORIES:',
    colour=	0xf7f7f7,
)
for abbrev,cat in FACE.first_cat_dict.items():
    cat_embed.add_field(name=cat.capitalize(),value=abbrev)

subcat_lookup = dict()
for cat in FACE.first_cat_dict.values():
    results = []
    set_subcats = []
    for abbreviation,sub_cat in FACE.first_subcat_dict.items():
        original = sub_cat
        sub_cat = sub_cat.casefold()
        if cat in sub_cat and sub_cat.find(cat) == 0:
            results.append((abbreviation,original))
            set_subcats.append(original)
    set_subcats = list(set(set_subcats))
    embed = discord.Embed(
        title=f'SUBCATEGORIES',
        colour=	0xf7f7f7,
    )
    for subcat in set_subcats:
        all_abbrev = []
        for abbrev,subcat2 in results:
            if subcat == subcat2:
                all_abbrev.append(abbrev)
        embed.add_field(name=subcat,value=', '.join(all_abbrev))
    subcat_lookup[cat] = embed

@tasks.loop(seconds=60)
async def update_premium():
    mydb,mycursor = mysql_connect() #user_id,server_id,premium
    mycursor.execute(f'SELECT * FROM premium_servers')
    member_ids = [x.id for x in patron_role.members]
    table = mycursor.fetchall()
    for row in table:
        if row[0] not in member_ids:
            mycursor.execute(f'DELETE FROM premium_servers WHERE user_id = {row[0]}')
    mydb.commit()
    in_table_ids = list(set([x[0] for x in table]))
    for id in member_ids:
        if id not in in_table_ids:
            for i in range(3):
                mycursor.execute(f'INSERT INTO premium_servers (user_id) VALUES ({id})')
            member = bot_guild.get_member(id)
            await member.send(
'''Hi! Thank you for deciding to support us! Below is some important information:
**---**  To activate your premium membership, use the command **m activate** in your chosen server.
**---**  It could take up to 10 minutes for your benefits to become available.
**---**  You can use `m activate` up to three times in three different servers.
**---** Keep in mind that premium carding features will not be available and server members will not be able to use the bot in their DMs if the server has more than **50 people**. ''')
    mydb.commit()

@tasks.loop(minutes=30)
async def update_trial():
    mydb,mycursor = mysql_connect()
    mycursor.execute(f'SELECT * FROM trial_premium')
    rows = mycursor.fetchall()
    for row in rows:
        if row[1] - int(time.time()) < 0:
            mycursor.execute(f'UPDATE trial_premium set used = {True} WHERE server_id = {row[0]}')
    mydb.commit()

def mysql_connect():
    mydb = mysql.connect(
      host="127.0.0.1",
      user="root",
      password="TheCataclysm91$(*",
      database="face_log"
    )
    mycursor = mydb.cursor(buffered=True)
    return mydb, mycursor
def is_owner(ctx):
    return ctx.author.id == 435504471343235072 or ctx.author.id == 483405210274889728
def has_num(s):
    return any(i.isdigit() for i in s)
async def premium(id,ctx):
    def pred(m):
        return m.author == ctx.author and m.channel==ctx.channel
    if id == 0:
        await ctx.send('Please send the id of a premium server that you are in to authorize your command.\nThe id can be found by right clicking on the server icon after enabling developer mode in `User settings` --> `Appearance` --> `Advanced` -> `Developer mode`.')
        try:
            msg = await client.wait_for('message',timeout=10,check=pred)
        except asyncio.TimeoutError:
            await ctx.send('You did not respond in time!')
        else:
            try:
                id = int(msg.content)
                authorized = client.get_guild(id)
                if len(authorized.members) > 50:
                    await ctx.send('That server has more than 50 members! (DM usage is only allowed for premium servers with less than 50 members)')
                    return False
                elif ctx.author.id not in [member.id for member in authorized.members]:
                    await ctx.send('You are not in that server!')
                    return False
            except:
                await ctx.send('Server not found!')
    mydb,mycursor = mysql_connect()
    mycursor.execute(f'SELECT timeout FROM trial_premium WHERE server_id = {id}')
    row = mycursor.fetchone()
    if row and (row[0] - int(time.time()) > 0):
        return 'trial'
    mycursor.execute(f'SELECT premium FROM premium_servers WHERE server_id = {id}')
    premium = mycursor.fetchone()
    if premium and premium[0] == True:
        return True
    else:
        return False
async def get_difficulty(difficulty,ctx,in_list):
    new_numbers = []
    for x in difficulty:
        if x[0] == '[':
            if len(new_numbers) > 0:
                await ctx.channel.send('You specified difficulty twice!')
                if in_list:
                    in_list.remove(ctx.author.id)
                return
            if x[-1] != ']':
                await ctx.channel.send('Please do not use spaces when specifying difficulty!')
                if in_list:
                    in_list.remove(ctx.author.id)
                return
            else:
                numbers = x[1:-1]
                if len(numbers) == 0:
                    await ctx.channel.send('You didn\'t put anything in the brackets!')
                    if in_list:
                        in_list.remove(ctx.author.id)
                    return
                numbers = numbers.split(',')
                for entry in numbers:
                    if '-' in entry:
                        for num in list(range(int(entry[0]),int(entry[-1])+1)):
                            new_numbers.append(num)
                    else:
                        new_numbers.append(entry)
                try:
                    new_numbers = list(map(int,new_numbers))
                except:
                    await ctx.channel.send('Make sure you are using a dash when specifying difficulty!')
                    if in_list:
                        in_list.remove(ctx.author.id)
                    return
                new_numbers = list(set(new_numbers))
    return new_numbers
N_e = 0 #number of questions seen
m = 0 #number of tournaments
@client.command (name='end')
async def end(ctx):
    if ctx.author.id in in_pk:
        await ctx.channel.send('Did you mean `m pk end?`')
    else:
        await ctx.channel.send('Try sending the name of the command before end, e.g. `m practice end` or `m pk end`')

@client.command (name='guilds')
async def guilds(ctx):
    if ctx.message.author.id == 435504471343235072 or ctx.message.author.id == 483405210274889728:
        guild_names = [x.name for x in client.guilds]
        guilds = ', '.join(guild_names)
        await ctx.channel.send(guilds)
@client.command (name='shutdown')
async def shutdown(ctx):
    if is_owner(ctx):
        global is_shutdown
        await ctx.message.delete()
        await ctx.channel.send('shutting down...')
        for user_id in in_pk:
            try:
                user = client.get_user(user_id)
                await user.send('FACE is going offline for updates and bug fixes. The bot should be back up in a few minutes! Sorry for any inconveniences :slight_frown:')
            except:
                continue
        sys.exit()
@client.command (name='activate')
async def activate(ctx):
    mydb,mycursor = mysql_connect()
    try:
        guild_id = ctx.guild.id
    except:
        await ctx.channel.send('You cannot activate premium in a dm channel!')
    if await premium(ctx.guild.id,ctx) == True:
        await ctx.channel.send('This server already has access to premium features :slight_smile:!')
        return
    mycursor.execute(f'SELECT * FROM premium_servers WHERE user_id = {ctx.author.id}')
    rows = mycursor.fetchall()
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    if rows == []:
        embed = discord.Embed (
        title='FACE Bot',
        colour=	0x7dffba,
        )
        embed.add_field(name='This command is only usable by patrons. If you recently became a patron, it may take up to 15 minutes for your benefits to be available.',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
        await ctx.channel.send(embed=embed)
    else:
        slots = [row for row in rows if row[1] == None]
        if len(slots) == 0:
            await ctx.channel.send('You have already activated premium in three servers!')
        else:
            await ctx.channel.send(f'Are you sure you want to activate premium in **{ctx.guild.name}**? You cannot reverse this decision. `y` for yes, `n` for no')
            try:
                msg = await client.wait_for('message',check=pred,timeout=10)
            except asyncio.TimeoutError:
                await ctx.channel.send('You did not respond in time...')
                return
            else:
                if msg.content.lower() == 'y':
                    mycursor.execute(f'UPDATE premium_servers SET server_id = {ctx.guild.id},premium = {True} WHERE server_id IS NULL AND user_id = {ctx.author.id} LIMIT 1')
                    mydb.commit()
                    await ctx.channel.send('Premium activated! :white_check_mark:')
                elif msg.content.lower() == 'n':
                    await ctx.channel.send('Abandoning the activation process...')
                    return
                else:
                    await ctx.channel.send('Not a valid response!')
                    return
@client.command (name='trial')
async def trial(ctx):
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    mydb,mycursor = mysql_connect()
    try:
        guild_id = ctx.guild.id
    except:
        await ctx.channel.send('You cannot start a trial in a dm channel!')
    if await premium(ctx.guild.id,ctx) == True:
        await ctx.channel.send('This server already has access to premium features :slight_smile:!')
        return
    elif await premium(ctx.guild.id,ctx) == 'trial':
        await ctx.channel.send('This server is in the middle of its free trial :slight_smile:!')
        return
    mycursor.execute(f'SELECT * FROM trial_premium WHERE server_id = {ctx.guild.id}')
    rows = mycursor.fetchone()
    if rows == None:
        await ctx.channel.send(f'Are you sure you want to activate your free trial in **{ctx.guild.name}**? This is only usable once and will last for 24 hours. `y` for yes, `n` for no')
        try:
            msg = await client.wait_for('message',check=pred,timeout=10)
        except asyncio.TimeoutError:
            await ctx.channel.send('You did not respond in time...')
            return
        else:
            if msg.content.lower() == 'y':
                mycursor.execute(f'INSERT INTO trial_premium (server_id,timeout,used) VALUES ({ctx.guild.id},{int(time.time()+86400*3)},{False})') #86400
                mydb.commit()
                await ctx.channel.send('Free 24 hour trial activated! :white_check_mark:')
            elif msg.content.lower() == 'n':
                await ctx.channel.send('Abandoning the free trial activation process...')
                return
            else:
                await ctx.channel.send('Not a valid response!')
                return
    else:
        if rows[2] == True:
            await ctx.channel.send('The free trial for this server has already been used...:slight_frown:')
        else:
            await ctx.channel.send('The free trial is currently activated!')

@client.command (name='help')
async def help(ctx):
    embed= discord.Embed(
    title= 'Help',
    colour= 0x00ff00,
    timestamp=datetime.datetime.now()
    )
    embed.set_author(name='FACE Inc.')
    embed.add_field(name='m server',value='Join our support server [here](https://discord.gg/YsbhefcXpA)!')
    embed.add_field(name="m instructions `name of command`", value="In depth instructions on a specific command. e.g. `m instructions card`", inline=False)
    embed.add_field(name="m cats", value="Displays the abbreviations used for categories", inline=False)
    embed.add_field(name="m subcats",value="Displays the abbreviations used for subcategories",inline=True)
    embed.add_field(name="m invite",value="Get an invite for the bot!",inline=True)
    embed.add_field(name="m trial",value="Activate a 3 day premium trial!",inline=False)
    embed.add_field(name="m card", value="m card `category` `difficulty` `term`")
    embed.add_field(name="m pk", value = "m pk `category` `[optional] difficulty` `[optional] team` `[optional] comp` `[optional] timed`")
    embed.add_field(name="m tournament", value = "m tournament `tournament name`")
    embed.add_field(name="m practice `[optional ffa]`",value="Starts a practice session. `m practice ffa` for free for all and `m practice` for teams")
    embed.add_field(name="m lookup",value = "m lookup `category` `term`")
    await ctx.channel.send(embed=embed)
    #copy mafia embed

@client.command (name='invite')
async def invite(ctx):
    embed= discord.Embed(
    title= 'Invite FACE!',
    colour= 0xf0f0f0,
    timestamp=datetime.datetime.now()
    )
    embed.add_field(name='Link',value='[invite FACE to your server](https://discord.com/oauth2/authorize?client_id=742880812961235105&scope=bot&permissions=121920)')
    await ctx.send(embed = embed)

@client.command (name='instructions')
async def instructions(ctx,command = None):
    if command == None:
        await ctx.channel.send('Specify a command after m instructions, e.g. `m instructions card`')
    elif command == 'card':
        await ctx.channel.send('**---** Use the command `m card *category* [difficulty] *term(s)*`, e.g. `m card sci [3-5,7] proton`.\n**---** The bot will send a file that you can download and **import into Anki**!\n**---** You can substitue `all` for either the category or for the terms if you want to card entire categories or card specific terms across categories.\n**---** Use the keyword `filtered` at the end of your command to remove similar cards and make your review more efficient. (e.g. `m card sci proton filtered`)')
    elif command == 'tournament':
        await ctx.channel.send('***---*** Use `m tournament *tournament name*`\n***---*** The cards will be from the tournament with the closest name, try to be as specific as possible.')
    elif command == 'pk':
        await ctx.channel.send('***---*** Starts a pk practice session.\n**---** m pk `category` `difficulty` `game_mode` `timed?`, e.g. `m pk sci [4-6] timed` or `m pk sci[4-6]`.\n***---*** Use `team` or `comp` to make a team pk or a competitive pk, e.g. `m pk all [3] team`, `m pk sci [4-6] comp`\n**---** Use `{}` for multiple categories, e.g. `m pk {sci,myth}`\n**---** Use m subcats `category` to view subcategories, and PK with subcategories using a colon, e.g. `m pk sci:bio [4-6]`\n**---** Use `m pk end` to end the game.\n**---** Use `~` before your messages to talk during the pk. e.g. `~that was a bad question`')
@client.command (name='cats')
async def cats(ctx):
    embed = cat_embed
    embed.timestamp = datetime.datetime.now()
    await ctx.channel.send(embed=embed)
@client.command(name='subcats')
async def subcats(ctx,cat=None):
    if cat == None:
        await ctx.channel.send('Use m subcats `category` to browse subcategories. e.g. `m subcats sci`')
        return
    if cat.casefold() in FACE.first_cat_dict.values():
        cat = cat.casefold()
    elif FACE.first_cat_dict.get(cat.casefold()):
        cat = FACE.first_cat_dict.get(cat).casefold()
    else:
        await ctx.channel.send('That is not a valid category!')
        return
    embed = subcat_lookup.get(cat)
    embed.timestamp = datetime.datetime.now()
    await ctx.channel.send(embed=embed)
@client.command (name='pk')
async def pk(ctx,category=None,*difficulty):
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    def close(id):
        global close_pk
        if id not in close_pk:
            return False
        return True
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel and not m.content.startswith('~')
    # def team_pred(m):
    #     return ((m.author == ctx.author or m.author in team.members) and m.channel == ctx.channel) and not m.content.startswith('~')
    class Team():
        def __init__(self,members):
            self.members = members
            self.authors = [x.author for x in members]
            def team_pred(m):
                return ((m.author == ctx.author or m.author in self.authors) and m.channel == ctx.channel) and not m.content.startswith('~')
            self.pred = team_pred
            self.total_points = 0
            self.bonuses_heard = 0
            self.thirties = 0
            self.difficulties = []
        def update(self,points,pk_difficulty):
            self.total_points += points
            self.difficulties.append(pk_difficulty)
            self.bonuses_heard += 1
            if points == 30:
                self.thirties += 1
        def get_winner(self):
            self.members.sort(key=lambda x: x.points)
            winner = self.members[1]
            loser = self.members[0]
            return winner,loser
        def get_ppb(self):
            ppb = 0 if (self.bonuses_heard == 0) else (self.total_points/self.bonuses_heard)
            return ppb
        def get_diff(self):
            avg_diff = 0 if len(self.difficulties) == 0 else sum(self.difficulties)/len(self.difficulties)
            return avg_diff
        async def get_embed(self,category,comp_pk,is_team,guild_id):
            ppb = self.get_ppb()
            if comp_pk: #ranked_pk
                winner,loser = self.get_winner()
            embed = discord.Embed (
            title=f'PK RESULTS:',
            colour=	0x303845,
            timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            if comp_pk:
                winner,loser = team.get_winner()
                embed.add_field(name='**WINNER**',value=f'{winner.author.name}')
                embed.add_field(name=f'{winner.author.name}\'s Points',value=f'{winner.points} points, PPB: {winner.get_ppb()}')
                embed.add_field(name=f'{loser.author.name}\'s Points',value=f'{loser.points} points, PPB: {loser.get_ppb()}')
            # elif ranked_pk:
            #     winner,loesr = team.get_winner()
            #     embed.add_field(name='**WINNER**',value=f'{winner.author.name}')
            #     embed.add_field(name=f'{winner.author.name}\'s Points',value=f'{winner.points} points, PPB: {winner.get_ppb()}')
            #     embed.add_field(name=f'{loser.author.name}\'s Points',value=f'{loser.points} points, PPB: {loser.get_ppb()}')
            else:
                embed.add_field(name='**PPB**:',value=f'{ppb:.3f}')
                embed.add_field(name='30 30 30:',value=f'{self.thirties}',inline = True)
                embed.add_field(name='Total Points:',value=f'{self.total_points}',inline = True)
            embed.add_field(name='Avg diff.', value=f'{self.get_diff():.2f}')
            embed.add_field(name='Category',value=f'{category.upper()}')
            embed.add_field(name='Bonuses Seen:',value=f'{self.bonuses_heard}',inline = True)
            if not await premium(guild_id,ctx):
                embed.add_field(name='Please support us!',value=f'FACE has many more features like Team PKs or getting reviewable PK cards. Learn about our premium features [here](https://www.patreon.com/facebot)!',inline=False)
            # if await premium(guild_id,ctx):
            for player in self.members:
                await self.get_cards(player.answerlines_missed,player)
            if is_team == True:
                for player in self.members:
                    embed.add_field(name=f'{player.author.name}:',value =f'{player.points} total points',inline=False)
            return embed
        async def get_cards(self,cards,player):
            full_path = await FACE.make_bonus_cards(cards,player.author.id)
            def card_pred(m):
                return m.author == player.author and m.channel == ctx.channel
            if await premium(guild_id,ctx):
                await ctx.channel.send(f'{player.author.mention},Would you like PK review cards? Respond with `n` for no and `y` for yes.')
                try:
                    msg = await client.wait_for('message',check=card_pred,timeout=20)
                except asyncio.TimeoutError:
                    await ctx.channel.send('You did not respond in time. Deleting PK cards...')
                else:
                    if msg.content.casefold() != 'n':
                        with open(full_path, 'rb') as fp:
                            try:
                                await player.author.send(file=discord.File(fp, f'Your PK cards (click to download).csv'))
                            except:
                                await ctx.channel.send('Could not send pk cards, check that server DMs are turned on.')
                        await asyncio.sleep(5)
                        os.remove(full_path)
    class Player():
        def __init__(self,author,pred):
            self.author = author
            self.pred = pred
            self.points = 0
            self.bonuses_heard = 0
            self.thirties = 0
            self.answerlines_missed = []
            self.difficulties = []
            self.no_responses = 0
        def update(self,points,pk_difficulty):
            nonlocal team
            self.difficulties.append(pk_difficulty)
            self.bonuses_heard += 1
            team.bonuses_heard += 1
            if points == 30:
                self.thirties += 1
        def get_ppb(self):
            ppb = 0 if (self.bonuses_heard == 0) else (self.points/self.bonuses_heard)
            return ppb
    global in_pk
    global close_pk
    if ctx.author.id in in_pk: #orig_category != 'ranked'
        if category == 'end':
            if ctx.author.id not in close_pk:
                close_pk.append(ctx.author.id)
            await ctx.channel.send('Ending the pk...')
        elif category == 'end--force':
            if ctx.author.id in close_pk:
                close_pk.remove(ctx.author.id)
            in_pk.remove(ctx.author.id)
        else:
            await ctx.channel.send('You are already in a pk! Use `m pk end` to end a pk and allow a few seconds for the pk to end. If you are **not** in a pk, use `m pk end--force` after a while.')
        return
    # elif orig_category == 'ranked':
    #     if ranked_passed == ranked_questions:
    #         close_pk.append(ctx.author.id)
    #         await ctx.channel.send('Ending the pk...')
    elif category == 'end':
        await ctx.channel.send('You are not in a pk!')
        return
    in_pk.append(ctx.author.id)
    if category == None:
        await ctx.channel.send('You used the wrong format! Use the command `m pk *category* *[difficulty]*`, e.g. `m pk sci [3-7]` or `m pk sci:bio [1-9]`')
        in_pk.remove(ctx.author.id)
        return
    difficulty = list(difficulty)
    brackets = False
    numbers = False
    for arg in difficulty:
        for char in arg:
            if char == '[':
                brackets = True
            if char.isdigit() == True:
                numbers = True
    if numbers and not brackets:
        await ctx.channel.send('Please use brackets when specifying difficulty.')
        in_pk.remove(ctx.author.id)
        return
    if 'timed' in difficulty:
        difficulty.remove('timed')
        timed = True

    else:
        timed = False
    is_team = False
    comp_pk = False
    ranked_pk = False
    team = [Player(ctx.author,pred)]
    if 'team' in difficulty:
        if not await premium(guild_id,ctx):
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Team PKs are reserved for premium servers!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
            await ctx.channel.send(embed=embed)
            in_pk.remove(ctx.author.id)
            return
        # difficulty.remove('team')
        start = time.time()
        while start - time.time() < 60:
            await ctx.channel.send('Add a member to your team by mentioning them, e,g, respond with `@my_teammate`.')
            try:
                msg = await client.wait_for('message', check=pred,timeout=10)
            except asyncio.TimeoutError:
                await ctx.channel.send('You did not respond in time!')
                in_pk.remove(ctx.author.id)
                return
            else:
                if msg.content.startswith('m done'):
                    break
                teammate = None
                if len(msg.mentions)>0:
                    teammate = msg.mentions[0]
                if teammate and teammate not in team:
                    is_team = True
                    team.append(Player(teammate,pred))
                    await ctx.channel.send('Teammate added! :ballot_box_with_check:\nUse m done when you are done adding team members.')
                else:
                    await ctx.channel.send('That is not a valid Discord user!')
                    in_pk.remove(ctx.author.id)
                    return
    elif 'comp' in difficulty:
        if not await premium(guild_id,ctx):
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Competitive PKs are reserved for premium servers!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
            await ctx.channel.send(embed=embed)
            in_pk.remove(ctx.author.id)
            return
        await ctx.channel.send('Ping your opponent to add them, e.g.`@my_opponent`.')
        try:
            msg = await client.wait_for('message', check=pred,timeout=10)
        except asyncio.TimeoutError:
            await ctx.channel.send('You did not respond in time!')
            in_pk.remove(ctx.author.id)
            return
        else:
            if len(msg.mentions)>0:
                opponent = msg.mentions[0]
            if opponent:
                if 'comp' in difficulty:
                    comp_pk = True
                def pred_B(m):
                    return m.author == opponent and m.channel == ctx.channel and not m.content.startswith('~')
                team.append(Player(opponent,pred_B))
                await ctx.channel.send('Opponent added :ballot_box_with_check:')
            else:
                await ctx.channel.send('That is not a valid Discord user!')
                in_pk.remove(ctx.author.id)
                return
    elif category == 'ranked':
        # difficulty.remove('comp')
        await ctx.channel.send('Ping your opponent to add them, e.g.`@my_opponent`.')
        try:
            msg = await client.wait_for('message', check=pred,timeout=10)
        except asyncio.TimeoutError:
            await ctx.channel.send('You did not respond in time!')
            in_pk.remove(ctx.author.id)
            return
        else:
            if len(msg.mentions)>0:
                opponent = msg.mentions[0]
            if opponent:
                # if 'ranked' == category:
                #     ranked_pk = True
                def pred_B(m):
                    return m.author == opponent and m.channel == ctx.channel and not m.content.startswith('~')
                team.append(Player(opponent,pred_B))
                await ctx.channel.send('Opponent added :ballot_box_with_check:')
            else:
                await ctx.channel.send('That is not a valid Discord user!')
                in_pk.remove(ctx.author.id)
                return
    new_numbers = await get_difficulty(difficulty,ctx,in_pk)
    if new_numbers == None:
        in_pk.remove(ctx.author.id)
        return
    difficulty = new_numbers[:]
    orig_category = category
    bonuses = await FACE.get_bonus(category,difficulty)
    if bonuses == None:
        await ctx.channel.send('Please check your category spellings. Do not use spaces within the `{}` when specifying multiple categories.')
        in_pk.remove(ctx.author.id)
        return
    else:
        num_bonuses = bonuses[-1][0]
        await ctx.channel.send(f'{num_bonuses} bonuses found!')
        category = bonuses[-1][1]
        game_end = False
        id = ctx.author.id
        team = Team(team)
        first_time = True
        while True and game_end == False and close(id) == False:
            if not first_time:
                bonuses = await FACE.get_bonus(orig_category,difficulty)
            if bonuses == None:
                await ctx.channel.send('There was an error :slight_frown:. Ending the pk.')
                if id not in close_pk:
                    close_pk.append(id)
                break
            for i in range(4):
                if comp_pk == True: #or ranked_pk == True
                    if i % 2 == 0:
                        player_up = team.members[0]
                    else:
                        player_up = team.members[1]
                    avatar = player_up.author.avatar_url
                    pred_to_use = player_up.pred
                else:
                    pred_to_use = team.pred
                    player_up = team
                    avatar = ctx.author.avatar_url
                skip = False
                if game_end == True or close(id) == True:
                    break
                points = 0
                possible_points = 0
                tournament = bonuses[i][0][1]
                leadin = bonuses[i][0][0]
                color = bonuses[i][0][3]
                pk_difficulty = bonuses[i][0][2]
                for num in range(3):
                    question = bonuses[i][num+1][0]
                    formatted_answer = bonuses[i][num+1][1]
                    raw_answer = bonuses[i][num+1][2]
                    if game_end == True or close(id) == True:
                        break
                    possible_points += 10
                    embed = discord.Embed (
                    title=f'Question {team.bonuses_heard+1} ~ {tournament}',
                    colour=	0x56cef0,
                    timestamp=datetime.datetime.now()
                    )
                    if color:
                        embed.colour = color
                    embed.set_thumbnail(url=avatar)
                    if num == 0:
                        embed.add_field(name='\u200b',value = f'{leadin}')
                    embed.add_field(name='\u200b',value = f'**---**         {question}',inline=False)
                    if timed == True:
                        embed.set_footer(text='You have 16 seconds...')
                    await ctx.channel.send(embed=embed)
                    try:
                        if timed == True:
                            msg = await client.wait_for('message', check=pred_to_use,timeout=16)
                        else:
                            msg = await client.wait_for('message', check=pred_to_use,timeout=300)
                    except asyncio.TimeoutError:
                        await ctx.channel.send(formatted_answer)
                        if no_response >= 4:
                            embed = await team.get_embed(category,comp_pk,is_team,guild_id)
                            await ctx.channel.send(embed=embed)
                            close_pk.remove(id)
                            game_end = True
                            break
                        no_response += 1
                    else:
                        if msg.content == 'm skip':
                            skip = True
                            no_response = 0
                            break
                        if msg.content != 'm pk end':
                            for player in team.members:
                                if msg.author == player.author:
                                    ans_player = player
                            def find_ans(ans,key):
                                if ans.find(key)==-1:
                                    return
                                else:
                                    first = ans.find(key)+2
                                second = ans.find(key,first)
                                new_str = ans[first:second]
                                return new_str
                            underlined_portion = find_ans(formatted_answer,'__')
                            underlined_portion = find_ans(formatted_answer,'**') if underlined_portion == None else underlined_portion
                            underlined_portion = underlined_portion.casefold() if underlined_portion else underlined_portion
                            no_response = 0
                            similarity = fuzz.ratio(raw_answer.casefold(),msg.content.casefold())
                            if similarity > 75 or msg.content.casefold() == underlined_portion:
                                ans_player.points += 10
                                points += 10
                                await ctx.channel.send(f'**{points}**/{possible_points} :white_check_mark:')
                                correct = True
                            else:
                                await ctx.channel.send(f'**{points}**/{possible_points} :x:')
                                ans_player.answerlines_missed.append((question,raw_answer))
                                correct = False
                            await ctx.channel.send(f'ANSWER: {formatted_answer}')
                            if (30 <= similarity <= 75 or (msg.content.casefold() in formatted_answer.casefold()) or has_num(msg.content.casefold()) or has_num(raw_answer.casefold())) and correct == False:   #;  where should this go follow m
                                await ctx.channel.send('Were you correct? Respond with `y` or `n`')
                                try:
                                    msg = await client.wait_for('message', check=pred_to_use,timeout=10)
                                except asyncio.TimeoutError:
                                    None
                                else:
                                    if msg.content != 'm pk end':
                                        if msg.content.lower().startswith('n'):
                                                await ctx.channel.send(f'**{points}**/{possible_points} :x:')
                                        elif msg.content.lower().startswith('y'):
                                            ans_player.points += 10
                                            ans_player.answerlines_missed.remove((question,raw_answer))
                                            points += 10
                                            await ctx.channel.send(f'**{points}**/{possible_points} :white_check_mark:')
                                        else:
                                            await ctx.channel.send('Not a valid response!')
                    await asyncio.sleep(1)
                if id not in close_pk and skip == False:
                    player_up.update(points,pk_difficulty)
                    await asyncio.sleep(2)
            first_time = False
        if id in close_pk:
            embed = await team.get_embed(category,comp_pk,is_team,guild_id)
            await ctx.channel.send(embed=embed)
            close_pk.remove(id)
        if id in in_pk:
            in_pk.remove(id)
@client.command (name='practice')
async def practice(ctx,extra=None):
    if extra == 'end':
        return
    ffa = True if extra == 'ffa' else False
    def pred(m):
        return m.author == ctx.author and m.channel == ctx.channel
    def end_pred(m):
        return m.content == 'm practice end' and (m.author== moderator or m.author == ctx.author)
    def check(reaction, user):
        nonlocal msg
        return (str(reaction.emoji) == '🇧' or str(reaction.emoji) == '🅰️') and user != client.user and reaction.message.id == msg.id
    def moderator_pred(m): #used to appoint a moderator
        return m.author == ctx.author and m.channel == ctx.channel and len(m.mentions) > 0
    def buzz_pred(m):
        nonlocal directory
        nonlocal buzzes
        nonlocal ffa
        if not ffa:
            return ((m.author in players and m.content.lower().startswith('buzz')) and directory.get(m.author.id).team not in buzzes) or (m.author == moderator and m.content == 'm next') or end_pred(m)
        else:
            return ((m.author in players and m.content.lower().startswith('buzz')) and directory.get(m.author.id) not in buzzes) or (m.author == moderator and m.content == 'm next') or end_pred(m)
    def grade_pred(m): # used to grade a tossup answer
        return ((m.author == moderator) and m.content in (ten+power+neg+zero)) or end_pred(m)
    def mod_next(m): # used for advancing tossups after bonuses
        return ((m.author == moderator) and m.content.startswith('m next')) or end_pred(m)
    def grade_bonus(m):
        return ((m.author == moderator) and (m.content.isdigit() and int(m.content) in [0,10,20,30])) or end_pred(m)

    await ctx.channel.send('Do you want to practice with bonuses? (Y/N)')
    try:
        msg = await client.wait_for('message',check=pred,timeout=15)
    except asyncio.TimeoutError:
        await ctx.channel.send('Practice timed out...')
    else:
        if msg.content.casefold().startswith('y'):
            await ctx.channel.send('Bonuses enabled :white_check_mark:.')
            bonuses = True
        elif msg.content.casefold().startswith('n'):
            await ctx.channel.send('Bonuses disabled :x:.')
            bonuses = False
        else:
            await ctx.channel.send('Not a valid response. Ending practice...')
            return
    ten = ['ten','+','10']
    power = ['power','*','15']
    neg = ['neg','-','-5']
    zero = ['zero','0']
    class Team():
        def __init__(self, players, name):
            self.players = players
            self.name = name
            self.team_points = 0
        def init_directory(self):
            self.directory = dict()
            for player in self.players:
                self.directory[player.author.id] = player
    class Player():
        def __init__(self,author,team):
            self.author = author
            self.total_points = 0
            self.tossups_heard = 0
            self.powers = 0
            self.tens = 0
            self.negs = 0
            self.team=team
        def update(self,points):
            self.total_points += points
            if points == 15:
                self.team.team_points += 15
                self.powers += 1
            elif points == 10:
                self.team.team_points += 10
                self.tens += 1
            elif points == -5:
                self.team.team_points -= 5
                self.negs += 1
    start = time.time()
    Team_A = Team([],'A Team')
    Team_B = Team([],'B Team')
    players = []
    game = True
    if not ffa:
        msg = await ctx.channel.send('React to this message to join a team!')
        await msg.add_reaction('🅰️')
        await msg.add_reaction('🇧')
    else:
        msg = await ctx.channel.send('React to this message to join the practice!')
        await msg.add_reaction('🅰️')
    while time.time() - start < 15:#change to 30
        try:
            reaction,user = await client.wait_for('reaction_add', timeout=10,check=check)
        except asyncio.TimeoutError:
            None
        else:
            if user not in players:
                players.append(user)
                if str(reaction.emoji) == '🅰️':
                    Team_A.players.append(Player(user,Team_A))
                else:
                    Team_B.players.append(Player(user,Team_B))
            else:
                await msg.remove_reaction(str(reaction.emoji),user)
    if not ffa:
        A_string = '```A TEAM: '
        B_string = '```B TEAM: '
        for x in Team_A.players:
            A_string = A_string + f'\n{x.author.name}' # append to string with new line
        for x in Team_B.players:
            B_string = B_string + f'\n{x.author.name} B'
        practice_size = 2
        await ctx.channel.send(A_string+'```')
        await ctx.channel.send(B_string+'```')
    else:
        A_string = '```FFA: '
        for x in Team_A.players:
            A_string = A_string + f'\n{x.author.name}'
        practice_size = len(Team_A.players)
        await ctx.channel.send(A_string+'```')
    await ctx.channel.send('Ping the moderator within the next 30 seconds.')
    try:
        msg = await client.wait_for('message', check=moderator_pred, timeout=30)
    except asyncio.TimeoutError:
        await ctx.channel.send('No moderator added. Ending practice.')
        return
    else:
        moderator = msg.mentions[0]
        await ctx.channel.send(f'{moderator.name} is now the moderator.')
    instructions = f'''
{moderator.mention} -- **MODERATOR INSTRUCTIONS**
**---** For powers, type one of the following: `*`,`power`,`15`
**---** For tens: `+`,`ten`,`10`
**---** For negs: `-`,`neg`,`-5`
**---** For no points: `0`,`zero`
**--** Type `m next` if a tossup goes dead.
**---** On bonuses, type `m next` once the bonus is over to assign points.
**---** PLAYERS: Type `buzz` to buzz'''

    await ctx.channel.send(instructions)
    game = True
    tossup_num = 0
    next_num = 0
    Team_A.init_directory()
    Team_B.init_directory()
    directory = {**Team_A.directory, **Team_B.directory}
    while game:
        #await ctx.channel.send(f'{tossup_num}, {next_num}')
        if tossup_num >= next_num:
            buzzes = []
            await ctx.channel.send(f'\~\~\~\~\~\~\~\~\~\~\~\~**Tossup {tossup_num+1}**\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~')
            next_num = tossup_num + 1
        try:
            msg = await client.wait_for('message', check=buzz_pred,timeout=300)
        except asyncio.TimeoutError:
            await ctx.channel.send('No activity for 5 minutes, ending practice...')
            return
        else:
            if msg.content == 'm practice end':
                await ctx.channel.send('**Practice ended.**')
                break
            if msg.content == 'm next':
                tossup_num += 1
                continue
            if msg.author != moderator:
                await ctx.channel.send(f'{moderator.mention} `buzz from {msg.author.name}`')
                buzzer =  directory.get(msg.author.id)
                answering_team = buzzer.team if not ffa else buzzer
            try:
                grade = await client.wait_for('message',check=grade_pred,timeout=300)
            except asyncio.TimeoutError:
                await ctx.channel.send('No activity for 5 minutes, ending practice...')
                return
            else:
                if grade.content == 'm practice end':
                    await ctx.channel.send('**Practice ended.**')
                    break
                correct = True
                buzzes.append(answering_team)
                if grade.content in ten:
                    tossup_num += 1
                    buzzer.update(10)
                elif grade.content in power:
                    tossup_num += 1
                    buzzer.update(15)
                elif grade.content in neg:
                    correct = False
                    await ctx.channel.send('neg :x:')
                    buzzer.update(-5)
                elif grade.content in zero:
                    correct = False
                    await ctx.channel.send(':zero:')
                if bonuses == True and correct == True:
                    await ctx.channel.send(f'\~\~\~\~\~\~\~\~\~\~\~\~**Bonus {tossup_num+1}**\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~')
                    try:
                        next_msg = await client.wait_for('message',check=mod_next,timeout=300)
                    except asyncio.TimeoutError:
                        await ctx.channel.send('No activity for 5 minutes, ending practice...')
                        return
                    else:
                        if next_msg.content == 'm practice end':
                            await ctx.channel.send('**Practice ended.**')
                            break
                        await ctx.channel.send('`Points earned on bonus?: `')
                        try:
                            bonus_points = await client.wait_for('message',check=grade_bonus,timeout=300)
                        except asyncio.TimeoutError:
                            await ctx.channel.send('No activity for 5 minutes, ending practice...')
                            return
                        else:
                            if bonus_points.content == 'm practice end':
                                await ctx.channel.send('**Practice ended.**')
                                break
                            answering_team.team_points += int(bonus_points.content)
                            tossup_num += 1
                elif len(buzzes) == practice_size: #change to practice_size
                    tossup_num += 1
    embed = discord.Embed (
    title='Practice Stats',
    colour=	0x83e6d0,
    timestamp=datetime.datetime.now()
    )
    Team_A.players.sort(reverse=True,key=lambda x: x.total_points)
    Team_B.players.sort(reverse=True,key=lambda x: x.total_points)
    A_str = f'{Team_A.team_points} points\n------------------------'
    for i,player in enumerate(Team_A.players):
        stat_line = f'{player.powers}/{player.tens}/{player.negs}: {player.total_points}'
        A_str += f'\n**{i+1}**. {player.author.name} **---** {stat_line}'
    embed.add_field(name='**Team A**',value=A_str)
    B_str = f'{Team_B.team_points} points\n------------------------'
    if not ffa:
        for i,player in enumerate(Team_B.players):
            stat_line = f'{player.powers}/{player.tens}/{player.negs}: {player.total_points}'
            B_str += f'\n**{i+1}**. {player.author.name} **---** {stat_line}'
        embed.add_field(name='**Team B**',value=B_str)
    embed.set_footer(text='Close game!')
    await ctx.channel.send(embed=embed)
@client.command (name='tournament')
async def tournament(ctx,*tournament):
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    if not await premium(guild_id,ctx):
        embed = discord.Embed (
        title='FACE Bot',
        colour=	0x7dffba,
        )
        embed.add_field(name='This command is reserved for premium servers!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
        await ctx.channel.send(embed=embed)
        return
    if len(tournament) == 0:
        await ctx.channel.send('You used the wrong format! Use the command `m card *tournament*`, e.g. `m card PACE 2016`.')
        return
    tournament = ' '.join(tournament)
    result = await FACE.get_csv_tournament(tournament)
    results = result
    if results == None:
        await ctx.channel.send('No tournaments found!')
        return
    full_path,total_cards = results
    with open(full_path, 'rb') as fp:
        await ctx.channel.send(file=discord.File(fp, f'{ctx.author.name}\'s {tournament} cards (click to download).csv'))
    await ctx.channel.send(f'Around {total_cards} cards made!')
    await asyncio.sleep(7)
    os.remove(full_path)

@client.command (name='card')
async def card(ctx,category=None,*terms):
    try:
        guild_id = ctx.guild.id
    except:
        guild_id = 0
    if category == None or terms == []:
        await ctx.channel.send('You used the wrong format! Use the command `m card *category* *[difficulty]* *term*`, e.g. `m card sci [3-7] proton` or `m card sci biology all`')#i need access to the other part plz
        return
    if ctx.author.id in carding:
        await ctx.channel.send('Please wait for your previous request to finish before starting another one.')
        return
    word = str()
    separated_terms = []
    new_numbers = []
    terms = list(terms)
    if 'filtered' in terms:
        if not await premium(guild_id,ctx) or len(ctx.guild.members) > 50:
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Filtering your cards is reserved for premium servers with less than **50 members**!',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
            await ctx.channel.send(embed=embed)
            return
        raw = False
        terms.remove('filtered')
    else:
        raw = True
    new_numbers = await get_difficulty(terms,ctx,carding)
    for x in terms:
        if x[0] == '[':
            continue
        if x[-1] == ',':
            if len(word) == 0:
                word = x[:-1]
            else:
                word = word + ' ' + x[:-1]
            separated_terms.append(word)
            word = str()
        else:
            if len(word) == 0:
                word = x
            else:
                word = word + ' ' + x
    if word != '':
        separated_terms.append(word)
    if len(separated_terms) == 0:
        if not (await premium(guild_id,ctx) == True) or len(ctx.guild.members) > 50:
            embed = discord.Embed (
            title='FACE Bot',
            colour=	0x7dffba,
            )
            embed.add_field(name='Carding entire categories/subcategories is reserved for premium servers with **less than 50 members**! This feature is also restrictred from trials.',value='Access exclusive perks [here](https://www.patreon.com/facebot)!')
            await ctx.channel.send(embed=embed)
            return
        term_by_term = False
    else:
        term_by_term = True
    difficulty = new_numbers[:]
    carding.append(ctx.author.id)
    await ctx.channel.send(f'Beginning the carding process... Estimated time: `Up to five minutes...`')
    try:
        result = await FACE.get_csv(separated_terms,category,ctx.author.id,difficulty,term_by_term,raw)
    except:
        await ctx.channel.send('There was a problem! Please try again.')
        carding.remove(ctx.author.id)
        return
    if result == None:
        await ctx.channel.send('That is not a valid category!')
        carding.remove(ctx.author.id)
        return
    full_path, total_cards = result
    if full_path == None:
        await ctx.channel.send('That is not a valid category!')
        carding.remove(ctx.author.id)
        return
    with open(full_path, 'rb') as fp:
        try:
            await ctx.channel.send(file=discord.File(fp, f'{ctx.author.name}\'s {category} cards (click to download).csv'))
        except discord.errors.HTTPException:
            await ctx.channel.send('File size too large! Please try restricting your request (e.g. add difficulty parameters or use subcategories).')
    await ctx.channel.send(f'Around {total_cards} cards made!')
    await asyncio.sleep(7)
    os.remove(full_path)
    carding.remove(ctx.author.id)

@client.command (name='info',aliases=['details'])
async def info(ctx):
    embed = discord.Embed (
    title='FACE',
    colour=	0x7d99ff,
    timestamp=datetime.datetime.now()
    )
    embed.set_author(name='FACE Inc.')
    embed.set_thumbnail(url='https://media.discordapp.net/attachments/626811419815444490/631882087280017428/silhouette-3073924_960_720.png?width=300&height=600')
    embed.add_field(name='Used in:',value=f'`{len(client.guilds)} servers!`')
    embed.add_field(name='Creators of this bot:', value =f'B3nj1#7587/<@{str(435504471343235072)}> and Shozen#5061/<@{483405210274889728}>', inline=True)
    embed.add_field(name='Programming language:', value ='Python 3.6.3', inline=True)
    embed.add_field(name='Library:', value ='Discord python rewrite branch (v1.4)', inline=True)
    await ctx.channel.send(embed=embed)
@client.command (name='list')
async def freq(ctx,category,*difficulty):
    if category == None:
        await ctx.channel.send('You used the wrong format! Use the command `m lookup *category* *[difficulty]* *term*`, e.g. `m lookup sci proton`')
        return
    if category == 'all':
        await ctx.channel.send('You cannot get frequency lists for `all`!')
        return
    difficulty = list(difficulty)
    brackets = False
    numbers = False
    for arg in difficulty:
        for char in arg:
            if char == '[':
                brackets = True
            if char.isdigit() == True:
                numbers = True
    if numbers and not brackets:
        await ctx.channel.send('Please use brackets when specifying difficulty.')
        return
    difficulty = await get_difficulty(list(difficulty),ctx,None)
    result = await FACE.get_frequency(category,difficulty)
    if result == None:
        await ctx.channel.send('No results found!')
        return
    answers,coverage,color = result
    answer_embed = discord.Embed(
        title=f'Frequency List For {category.upper()}:',
        colour=	0xf7f7f7,
    )
    if color:
        answer_embed.colour = color
    for i,x in enumerate(answers[:5]):
        answer_embed.add_field(name=f'**{i+1}.**',value=x,inline=False)
    await ctx.channel.send(embed=answer_embed)
@client.command (name='lookup')
async def lookup(ctx,category,*terms):
    if category == None or terms == []:
        await ctx.channel.send('You used the wrong format! Use the command `m lookup *category* *[difficulty]* *term*`, e.g. `m lookup sci proton`')
        return
    term = ' '.join(terms)
    result = await FACE.lookup(term,category)
    if result == None:
        await ctx.channel.send('No results found!')
        return
    x,y = result
    plt.plot(x,y,markerfacecolor='red')
    plt.xlabel('Difficulty')
    plt.ylabel('Avg. appearence every 200 tossups)')
    plt.title(f'Frequency of {term.title()}')
    path = f'temp/{ctx.author.name}.png'
    plt.savefig(path,dpi=200)
    plt.clf()
    with open(path, 'rb') as fp:
        await ctx.channel.send(file=discord.File(fp))
    await asyncio.sleep(2)
    os.remove(path)

@client.command (name='review')
async def review(ctx):
    embed= discord.Embed(
    title= 'Card #1/10',
    colour= 0xf0f0f0,
    timestamp=datetime.datetime.now()
    )
    embed.add_field(name='This would be the front of the card.',value='\u200b')
    embed.set_footer(text='Add reactions based on what you would like to do.')
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('\u2B05')
    await msg.add_reaction('\u27A1')
    await msg.add_reaction('\U0001F534')
    await msg.add_reaction('\U0001F7E1')
    await msg.add_reaction('\U0001F7E2')

    #copy mafia embed
@client.command (name='kick')
async def kick(ctx, member : discord.Member, *, reason=None):
    if ctx.message.author.id == 435504471343235072 or ctx.message.author.id == 483405210274889728:
        await member.kick(reason=reason)

@client.event
async def on_message(msg):# we do not want the bot to reply to itself
    if msg.author == client.user:
        return
    # if msg.guild.id == 634580485951193089 or msg.channel.id == 742885307304902727:
    #     test1 = client.get_channel(742885307304902727)
    #     if len(msg.mentions)>0:
    #         # await msg.channel.send(f'{msg.author.mention} pinged')
    #         await test1.send(f'{msg.author.mention} pinged')
    # if msg.content == 'm':
    #     stockm = ['\U0001F1F8','\U0001F1F9','\U0001F1F4','\U0001F1E8','\U0001F1F0','\u24c2']
    #     for reaction in stockm:
    #         await msg.add_reaction(reaction)

    def pred(m):
        return m.author == msg.author and m.channel == msg.channel
    await client.process_commands(msg)

#start up
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    global bot_guild
    global patron_role
    bot_guild = client.get_guild(767772426280894474)
    patron_role = bot_guild.get_role(767776503114366978)
    update_premium.start()
    update_trial.start()
    await client.change_presence( activity=discord.Game(name='c help',type=0), afk=False)
client.run(token)