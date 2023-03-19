from datetime import datetime

import pytz

from utils.work_file import read_file, write_file


async def check_time(date_object):
    moscow = pytz.timezone('Europe/Moscow')
    prev_date = await read_time("settings/time.txt")
    prev_date = prev_date.replace(tzinfo=moscow)
    date_object = date_object.replace(tzinfo=moscow)
    if date_object > prev_date:
        return True
    return False


async def write_time(file_path: str,
                     timezone: str = 'Europe/Moscow',
                     format_time: str = "%m/%d/%Y %H:%M:%S") -> None:
    geo = pytz.timezone(timezone)
    now = datetime.now(geo)
    strf_time = now.strftime(format_time)
    await write_file(file_path, strf_time)


async def read_time(file_path: str,
                    format_time: str = "%m/%d/%Y %H:%M:%S") \
        -> datetime:
    line = await read_file(file_path)
    previously_time = datetime.strptime(line.strip(), format_time)
    return previously_time
