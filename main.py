import discord
from discord.ext import commands
from pymongo import MongoClient
from random import randint

from cred import get_cred
from constants import *


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=DEFAULT_PREFIX, intents=intents)
bot.remove_command("help")

cred = get_cred()

mongo_client = MongoClient(cred["mongodb-url"])
db = mongo_client["odmozdzacze-bot"]
modmail_reports_col = db["modmail-reports"]


def generate_id(ids):
    while True:
        number = randint(10000000, 99999999)
        if number in ids:
            continue
        else:
            return number


def cursor_to_list(cursor, _filter=None):
    if _filter is None:
        a = []
        for i in cursor:
            a.append(i)
        return a
    else:
        a = []
        for i in cursor:
            a.append(i[_filter])
        return a


@bot.command(aliases=["help", "h", "?"])
async def _help(ctx):
    await ctx.send(embed=discord.Embed(
        title="Pomoc bota",
        description=":white_check_mark: Zobacz [listę poleceń](https://github.com/odmozdzacze/odmozdzacze-bot/wiki)\n\n:question: Jeśli masz wątpliwości, napisz do tego bota `!modmail <wiadomość-do-moderatora>`",
        color=COLORS["info"]
    ))


@bot.command(aliases=["modmail", "mmnew", "mmn"])
async def _modmail(ctx, *, message):
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.send(embed=discord.Embed(
            title="Nie można wysłać zgłoszenia Modmail",
            description=f"Zgłoszenie nie może być wysłane na kanale grupowym. Wyślij zgłoszenie na prywatną wiadomość do {bot.user.mention} .",
            color=COLORS["error"]
        ))
    else:

        modmail_channel = bot.get_channel(CHANNEL_IDS["modmail"])

        ids = cursor_to_list(modmail_reports_col.find(), "id")
        report_id = generate_id(ids)

        modmail_reports_col.insert_one({
            "id": report_id,
            "author": ctx.author.id,
            "message": message
        })

        embed = discord.Embed(
            title=f"Nowe zgłoszenie Modmail!",
            color=COLORS["info"]
        )
        embed.add_field(name="ID:", value=str(report_id), inline=False)
        embed.add_field(name="Autor:", value=ctx.author.mention, inline=False)
        embed.add_field(name="Wiadomość:", value=message, inline=False)
        await modmail_channel.send(embed=embed)

        embed = discord.Embed(
            title=f"Zgłoszenie Modmail wysłane.",
            color=COLORS["info"]
        )
        embed.add_field(name="ID:", value=str(report_id), inline=False)
        embed.add_field(name="Autor:", value=ctx.author.mention, inline=False)
        embed.add_field(name="Wiadomość:", value=message, inline=False)
        await ctx.send(embed=embed)


@bot.command(aliases=["modmailclose", "mmclose", "mmc"])
async def _modmail_close(ctx, report_id: int):
    if (ROLE_IDS["Moderator"] in [y.id for y in ctx.author.roles]) or (ROLE_IDS["Admin"] in [y.id for y in ctx.author.roles]):

        report_ids = cursor_to_list(modmail_reports_col.find({"id": report_id}), "id")
        if report_id in report_ids:
            modmail_reports_col.delete_one({"id": report_id})
            await ctx.send(embed=discord.Embed(
                title="Zgłoszenie Modmail zostało zamknięte i usunięte",
                color=COLORS["info"]
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="Nieprawidłowe ID zgłoszenia Modmail",
                description="Upewnij się, że wpisałeś prawidłowe ID zgłoszenia. Możesz też wyświetlić listę zgłoszeń za pomocą polecenia `!mmlist`.",
                color=COLORS["error"]
            ))


@bot.command(aliases=["modmaillist", "mmlist", "mml"])
async def _modmail_list(ctx):
    if (ROLE_IDS["Moderator"] in [y.id for y in ctx.author.roles]) or (ROLE_IDS["Admin"] in [y.id for y in ctx.author.roles]):

        reports = cursor_to_list(modmail_reports_col.find({}))

        if not len(reports) == 0:

            embed = discord.Embed(
                title="Lista zgłoszeń modmail",
                color=COLORS["info"]
            )

            for i in reports:
                embed.add_field(name=str(i["id"]), value=i["message"])

        else:
            embed = discord.Embed(
                title="Nie ma żadnych zgłoszeń Modmail"
            )

        await ctx.send(embed=embed)


@bot.command(aliases=["verifymod", "vmod", "vm"])
async def _verifymod(ctx):
    if (not isinstance(ctx.channel, discord.channel.DMChannel)) and (ctx.channel.id == CHANNEL_IDS["verify-role"]):
        await ctx.message.delete()

        if ROLE_IDS["Moderator"] not in [y.id for y in ctx.author.roles]:

            if ROLE_IDS["VIP"] not in [y.id for y in ctx.author.roles]:
                await ctx.author.send("Nie możesz awansować na @Moderator. Musisz najpierw zostać @VIP.")
            else:
                await ctx.author.send(f"Wypełnij formularz: http://tiny.cc/odmozdzacze-discord-mod i czekaj na wiadomość.")

        elif ROLE_IDS["Moderator"] in [y.id for y in ctx.author.roles]:

            await ctx.author.send(f"Już jesteś @Moderator .")


@bot.command(aliases=["verifydev", "vdev", "vd"])
async def _verifydev(ctx):
    if (not isinstance(ctx.channel, discord.channel.DMChannel)) and (ctx.channel.id == CHANNEL_IDS["verify-role"]):
        await ctx.message.delete()

        if ROLE_IDS["Developer"] not in [y.id for y in ctx.author.roles]:

            await ctx.author.send(f"*Funkcja w budowie...*")

        elif ROLE_IDS["Developer"] in [y.id for y in ctx.author.roles]:

            await ctx.author.send(f"Już jesteś @Developer.")


@bot.command(aliases=["verifyvip", "vvip", "vv"])
async def _verifyvip(ctx):

    if (not isinstance(ctx.channel, discord.channel.DMChannel)) and (ctx.channel.id == CHANNEL_IDS["verify-role"]):
        await ctx.message.delete()

        if ROLE_IDS["VIP"] not in [y.id for y in ctx.author.roles]:

            await ctx.author.send(embed=discord.Embed(
                title="Czekaj...",
                description="Twoje wiadomości i zgłoszenia na Odmóżdżaczach są skanowane.",
                color=COLORS["info"]
            ))

            messages_number = 0
            for channel_id in [788341540438933557, 816372606248026142, 816372641099153408, 788343045027528714, 788343078447874069, 788343156323385344]:
                channel = bot.get_channel(channel_id)
                async for message in channel.history():
                    if message.author == ctx.author:
                        messages_number += 1

            if messages_number >= VIP_GATE_MIN_MESSAGES_NUMBER:
                # role = ctx.author.guild.get_role(ROLE_IDS["VIP"])
                # await ctx.author.add_roles(role)

                await ctx.author.send(embed=discord.Embed(
                    title="Bramka VIP'a otwarta! Jesteś @VIP! :tada:",
                    description=f"Masz więcej niż {VIP_GATE_MIN_MESSAGES_NUMBER} wiadomości na uwzględnianych kanałach. Jeśli jeszcze nie dostałeś roli, napisz DM do {bot.user.mention} o treści `!modmail <wiadomość-do-moderatora>`",
                    color=COLORS["info"]
                ))
            else:
                embed = discord.Embed(
                    title="Nie przeszedłeś bramki VIP'a",
                    description=f"Nie możesz zostać @VIP, nie spełniłeś wszystkich kryteriów. Więcej informacji na #verify-role.",
                    color=COLORS["error"]
                )
                await ctx.author.send(embed=embed)

        elif ROLE_IDS["VIP"] in [y.id for y in ctx.author.roles]:

            await ctx.author.send(embed=discord.Embed(
                title="Już jesteś @VIP",
                description="Nie możesz zostać @VIP, bo już nim jesteś :upside_down:",
                color=COLORS["error"]
            ))


@bot.event
async def on_member_join(member):
    if not member.bot:
        # role = member.guild.get_role(ROLE_IDS["Member"])
        # await member.add_roles(role)

        await member.send("Witaj na serwerze! Cieszymy się, że dołączyłeś! Zobacz kanał ogłoszeń!")
    else:
        role = member.guild.get_role(ROLE_IDS["Bot"])
        await member.add_roles(role)


@_modmail.error
async def _modmail_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=discord.Embed(
            title="Brakująca wiadomość do moderatora",
            description=f"Składnia polecenia: `{DEFAULT_PREFIX}modmail <wiadomość-do-moderatora>`",
            color=COLORS["error"]
        ))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


if __name__ == "__main__":
    bot.run(cred["discord-token"])
