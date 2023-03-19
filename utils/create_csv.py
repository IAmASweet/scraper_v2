import aiofiles
from aiocsv import AsyncDictWriter


async def create_csv(file_csv, encoding):
    async with aiofiles.open(file_csv, mode="w",
                             encoding=encoding, newline="") as afp:
        writer = AsyncDictWriter(afp, ["title", "content"],
                                 delimiter=";")
        await writer.writeheader()
