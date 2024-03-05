from modules.helpers import getTokenPrice
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio
import os

load_dotenv(override=False)

mongoDB = os.environ.get("DB_TOKEN")
client = AsyncIOMotorClient(mongoDB)
dbClient = client["database"]


async def getCoinPricesHandler(coins, list: bool = False):
    message = ""
    for coin in coins:
        res = await getTokenPrice(coin)
        if res == None:
            message += f"**{coin.upper()}**: `Coin not found.` \n"
        else:
            message += f"**{coin.upper()}**: ${res[0]}  `{res[1]}` \n"

    return message


async def getCoinListHandler(event):
    usersDB = dbClient.users
    discordId = event.author.id
    discordName = event.author

    userDoc = await usersDB.find_one({"discordId": discordId})
    message = "Watchlist \n"

    if userDoc:
        coins = userDoc["coins"]
        if len(coins) == 0:
            message = "No coins on watchlist. Use !t add to add some."
        else:
            res = await getCoinPricesHandler(coins)
            message += res
    else:
        defaultCoins = ["BTC", "ETH", "SOL"]
        newUser = {
            "username": str(discordName),
            "discordId": int(discordId),
            "coins": defaultCoins,
        }
        await usersDB.insert_one(newUser)
        res = await getCoinPricesHandler(defaultCoins)
        message += res
        message += "\n*Default coins returned, use !t add <coins> to add some coins.*"

    return message


async def postCoinListHandler(event, type, coins):
    usersDB = dbClient.users
    discordId = event.author.id

    userDoc = await usersDB.find_one({"discordId": discordId})
    message = ""
    if userDoc:
        currentCoins = userDoc.get("coins", [])

        if type == "add":
            updatedCoins = currentCoins.copy()
            for coin in coins:
                if coin not in currentCoins:
                    updatedCoins.append(coin)

            await usersDB.update_one(
                {"discordId": discordId}, {"$set": {"coins": updatedCoins}}
            )
            message += "Coins added successfully."

        elif type == "del":
            if len(currentCoins) == 0:
                message += "You aren't watching any coins currently, so theres nothing to delete"
            else:
                updated_coins = [coin for coin in currentCoins if coin not in coins]
                await usersDB.update_one(
                    {"discordId": discordId}, {"$set": {"coins": updated_coins}}
                )
                message += "Coins deleted successfully."
    else:
        message += "User not found. Try running !t first to create an entry in the DB."

    return message
