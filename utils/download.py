import logging
from aiofile import async_open
import aiohttp
import re
import json
import os
import brotli

HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
}


async def rank() -> dict:
    async with async_open("db/RecommendedRank.json", "r") as f:
        data = json.loads(await f.read())
    return data


async def GSheet(key: str, gid: str, sql: str = "select%20*"):
    """
    Download google sheet and convert to a dict.

    Args:
        key (str): Between the slashes after spreadsheets/d.
        gid (str): The gid value at query.
        sql (str, optional): Query sql. Defaults to "select%20*".

    Raises:
        e: Exceptions caused by ClientSession.

    Returns:
        A converted dict.
    """
    url = f"https://docs.google.com/spreadsheets/u/0/d/{key}/gviz/tq?gid={gid}&tqx=out:json&tq={sql}"
    async with aiohttp.ClientSession() as session:
        try:
            fetchData = await session.get(url, headers=HEADER, timeout=aiohttp.ClientTimeout(total=10.0))
            data = re.search(r"(\{.*\})", await fetchData.text())
            data = json.loads(data.group(1))

            rows = data["table"]["rows"]
            cols = [i["label"].strip() for i in data["table"]["cols"]]
            result = {}
            for row in rows:
                temp = {}
                for i in range(1, len(cols)):
                    if isinstance(row["c"][i]["v"], float):
                        temp[cols[i]] = int(row["c"][i]["v"])
                    else:
                        temp[cols[i]] = row["c"][i]["v"]
                result[int(row["c"][0]["v"])] = temp
            return result

        except Exception as e:
            logging.error(f"Download Google Sheets failed. {key}({gid})")
            raise e


async def gameDB(url: str, filename: str, isBrotli: bool = True):
    """
    Download game database from url.

    Args:
        url (str): Url of the file.
        filename (str): The name that should be saved as.
        isBrotli (bool, optional): Should it be decompressed by brotli. Defaults to True.

    Raises:
        e: Exceptions caused by ClientSession.
    """
    async with aiohttp.ClientSession() as session:
        try:
            fetch = await session.get(url, headers=HEADER, timeout=aiohttp.ClientTimeout(total=10.0))
            async with async_open(os.path.join("./gameDB", filename), "wb+") as f:
                if isBrotli:
                    await f.write(brotli.decompress(await fetch.content.read()))
                else:
                    await f.write(await fetch.content.read())

        except Exception as e:
            logging.error(f"Download gameDB failed. ({filename}, {url})")
            raise e


async def json_(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            f = await session.get(url, headers=HEADER, timeout=aiohttp.ClientTimeout(total=10.0))
            return await f.json()
        except Exception as e:
            logging.error(f"Download json failed. ({url})")
            raise e
