import hikari
import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from modules.messageHandlers import (
    getCoinPricesHandler,
    getCoinListHandler,
    postCoinListHandler,
)

load_dotenv(override=False)

discord_token = os.environ.get("DISCORD_TOKEN")
admin_discord_id = int(os.environ.get("DISCORD_ADMIN_ID"))
db_token = os.environ.get("DB_TOKEN")

bot = hikari.GatewayBot(
    discord_token,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT,
)

# PREFIXES for message commands/creation
WATCHLIST_PREFIX = "!t"
CRYPTO_PREFIX = "t "
UPDATE_TOKENS_PREFIX = "!update"


@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    content = event.content
    if content and content.startswith(CRYPTO_PREFIX):
        coins = event.content[2:].split(" ")
        message = await getCoinPricesHandler(coins)
        await event.message.respond(message)
    if content and content.startswith(WATCHLIST_PREFIX):
        if len(content) > 2:
            type = content[3:6]
            if type == "add" or type == "del":
                coins = content[7 : len(content)].upper().split(" ")
                message = await postCoinListHandler(event, type, coins)
                await event.message.respond(message)
            else:
                await event.message.respond(
                    "Invalid list action. Use either 'add' or 'del'."
                )
        else:
            message = await getCoinListHandler(event)
            await event.message.respond(message)


@bot.listen()
async def admin(event: hikari.GuildMessageCreateEvent) -> None:
    if event.author.id != admin_discord_id:
        return
    ## ADD ADMIN COMMANDS HERE


bot.run()
