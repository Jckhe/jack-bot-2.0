import httpx
import os
from datetime import datetime, timedelta, timezone
from requests.exceptions import RequestException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import BulkWriteError
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

from utils.constants import CoinAPIRateEndpoint

load_dotenv(override=False)
coinAPIKeys = [
    os.environ.get("COINAPI_TOKEN"),
    os.environ.get("COINAPI_TOKEN2"),
    # os.environ.get('COINAPI_TOKEN3')
]


async def getTokenPrice(coin: str):
    times = await generateTimesInISOFormat()
    url = CoinAPIRateEndpoint.format(
        coin.upper(), times[0], times[1]
    )  # Parameters: (coin, timestart, timeend)

    for coinAPIKey in coinAPIKeys:
        headers = {"X-CoinAPI-Key": coinAPIKey}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 429 or response.status_code >= 400:
                    print(
                        f"Rate limit hit with current key: {coinAPIKey} rotating key..."
                    )
                    continue
                data = response.json()
                # If the coin is NOT found on the API. Return None.
                if len(data) < 1:
                    return None
                oldPrice = data[0]["rate_close"]
                currentPrice = data[1]["rate_close"]
                percentage = await percentageChange(oldPrice, currentPrice)
                currentPrice = float(currentPrice)
                if currentPrice < 0.1:
                    return ("{:,.8f}".format(round(currentPrice, 8)), percentage)
                elif currentPrice < 1:
                    return (round(currentPrice, 5), percentage)
                else:
                    return (round(currentPrice, 2), percentage)
        except Exception as e:
            print("Request Error with current key: ", e)
    return None


async def generateTimesInISOFormat():
    """
    Purpose of this function is to return two ISO strings that will represent the time 24 hours from right now and the current time.
    We need these strings to pass into the coinAPI endpoint.
    Returns a tuple
    """
    current_time = datetime.now(timezone.utc)
    timeStarts = (current_time - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%f0Z")
    timeEnds = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f0Z")
    return (timeStarts, timeEnds)


async def percentageChange(oldPrice, currentPrice):
    change = ((currentPrice - oldPrice) / abs(oldPrice)) * 100
    change_symbol = "+" if change >= 0 else "-"
    return f"{change_symbol}{abs(change):.2f}%"


# async def getTokenIDsAndUpdateCollection(apiKey: str):
#   """
#   Main purpose of this function is to grab all the token ID's from CoinGecko and insert them into
#   the "tokens" collection on MongoDB. That way we don't need to constantly query the CoinGecko API
#   for the list of tokens
#   """
#   url = CoinGeckoCoinsListEndpoint
#   headers = {"x-cg-demo-api-key": apiKey}
#   tokensCollection = dbClient.tokens
#   try:
#       async with httpx.AsyncClient() as client:
#           response = await client.get(url, headers=headers)
#           tokens = response.json()
#           try:
#               tokensCollection.insert_many(tokens)
#               return "Updated tokens in DB."
#           except BulkWriteError as bwe:
#               return (f"Error inserting documents into MongoDB: {bwe.details}")
#           except Exception as e:
#               return (f"An unexpected error occurred with MongoDB: {e}")

#   except httpx.RequestError as re:
#       return (f"Request to CoinGecko API failed: {re}")
#   except httpx.HTTPStatusError as status_error:
#       return (f"Error response {status_error.response.status_code} while requesting {status_error.request.url!r}.")
#   except ValueError:
#       return ("Failed to decode JSON response from CoinGecko API.")
#   except Exception as e:
#       return (f"An unexpected error occurred: {e}")
