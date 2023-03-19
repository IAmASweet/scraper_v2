import aiofiles

'''async def write_time():
    async with aiofiles.open('time.txt', 'w') as f:
        moscow = pytz.timezone('Europe/Moscow')
        now = datetime.now(moscow)
        strf_time = now.strftime("%m/%d/%Y %H:%M:%S")
        await f.writelines(strf_time)'''


async def write_file(file_path, data):
    async with aiofiles.open(file_path, 'w') as f:
        await f.writelines(data)


async def read_file(file_path):
    async with aiofiles.open(file_path, 'r') as f:
        data = await f.read()
        return data


'''async def read_time(file_path):
    async with aiofiles.open(file_path, 'r') as f:
        line = await f.read()
        previously_time = datetime.strptime(line.strip(), "%m/%d/%Y %H:%M:%S")
        return previously_time'''



