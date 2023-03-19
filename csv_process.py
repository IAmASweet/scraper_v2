from aiocsv import AsyncDictReader, AsyncDictWriter
import aiofiles
from utils.create_csv import create_csv
from settings.settings import get_config, logger


PATH_CSV = get_config('Default', 'path_csv')


async def check_duplicate(path, value, key, encoding):
    async with aiofiles.open(path, mode="r", encoding=encoding, newline="") as afp:
        async for row in AsyncDictReader(afp, delimiter=";"):
            if row[key] == value:
                return True
        return False


async def update_from_dict(data, text=f"Данные добавлены в {PATH_CSV}"):
    encoding = get_config('Default', 'encoding')
    try:
        async with aiofiles.open(PATH_CSV, encoding=encoding) as f:
            await f.read()
    except FileNotFoundError as e:
        logger.info(e)
        await create_csv(PATH_CSV, encoding=encoding)
    finally:
        data = await check_duplicate_title(data=data, path=PATH_CSV, encoding=encoding)
        async with aiofiles.open(PATH_CSV, mode="a", encoding=encoding, newline="") as afp:
            writer = AsyncDictWriter(afp, fieldnames=['title', 'content'], delimiter=";")
            await writer.writerows(data)
            print(text)
            logger.info(text)


async def check_duplicate_title(data, path, encoding):
    for index, item in enumerate(data):
        if await check_duplicate(path=path, value=item['title'], key='title', encoding=encoding):
            data.pop(index)
    return data
