from csv_process import update_from_dict
import re
from playwright.async_api import async_playwright
from playwright._impl._api_types import TimeoutError, Error
from utils.time_process import check_time
import pytz
from datetime import datetime, timedelta
from utils.clean_up_text import clean_up_text
import asyncio
from settings.settings import get_config, logger

LINK = 'https://www.change.org/ru'

arr_text = []
arr_news = []


async def get_content_change(page, timeout):
    for item in arr_text:
        await page.goto(item['link'], timeout=timeout)
        await page.wait_for_timeout(10000)
        content = await page.query_selector(".corgi-13ruqhr")
        # Подумать об ошибках сервера
        if content:
            content_text = await content.text_content()
            if content_text:
                clean_texts = clean_up_text([item['title'], content_text])
                arr_news.append({"title": clean_texts[0], "content": clean_texts[1]})


async def check_time_petition(page, link, timeout):
    try:
        await page.goto(link, timeout=timeout)
    except (Error, TimeoutError) as e:
        logger.info(f"Произошла ошибка при загрузке страницы {e}")
        return
    else:
        await page.wait_for_timeout(3000)
        await page.mouse.wheel(0, 2000)
        try:
            while not await page.locator(".corgi-1xbdly4").nth(1).is_enabled(timeout=timeout):
                while not await page.locator('.corgi-pnkuly').is_enabled(timeout=timeout):
                    await page.wait_for_timeout(2000)
        except (TimeoutError, Error) as e:
            logger.info(f"Произошла ошибка при загрузке селектора с датой, на Change org {e}")
            return True
        date_selector = await page.query_selector(".corgi-1xbdly4")
        date_created_selector = await date_selector.query_selector(".corgi-pnkuly")
        created_date = await date_created_selector.text_content()
        await page.wait_for_timeout(1000)
        await page.go_back()
        search_numbers = re.search(r"\d+", created_date)
        moscow = pytz.timezone('Europe/Moscow')
        now = datetime.now(moscow)
        delta = timedelta()
        if re.search("минут", created_date, re.I):
            delta = timedelta(minutes=int(search_numbers.group(0)))
        elif re.search("час", created_date, re.I):
            delta = timedelta(hours=int(search_numbers.group(0)))
        elif re.search("день|дней|дня", created_date, re.I):
            delta = timedelta(days=int(search_numbers.group(0)))
        time_petition = now - delta
        return await check_time(time_petition)


async def search_new_petions(page, timeout):
    titles = await page.query_selector_all(".link-block")
    if titles:
        href_last_petition = await titles[-1].get_attribute('href')
        link = 'https://www.change.org' + href_last_petition
        if link:
            while await check_time_petition(page, link, timeout):
                await page.wait_for_timeout(3000)
                try:
                    await page.wait_for_selector(".btn-big", timeout=timeout)
                    await page.get_by_role("button", name="Показать больше").click(force=True, timeout=timeout)
                except (Error, TimeoutError) as e:
                    logger.info(f"Произошла ошибка при нажатии на кнопку Показать больше, на Change org {e}")
                else:
                    await page.wait_for_timeout(4000)
                    titles = await page.query_selector_all(".link-block")
                    if titles:
                        href_last_petition = await titles[-1].get_attribute('href')
                        link = 'https://www.change.org' + href_last_petition


async def get_links(selectors):
    for item in selectors:
        text_selector = await item.query_selector(".mtn")
        href = await item.get_attribute('href')
        if text_selector and href:
            text = await text_selector.text_content()
            if text:
                arr_text.append({"title": text, "link": 'https://www.change.org' + href})


async def scrape_change_org():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False)
        except Error as e:
            print(e)
            logger.info(e)
        else:
            page = await browser.new_page()
            print("Начат парсинг change.org")
            logger.info("Начат парсинг change.org")
            timeout = int(get_config('Default', 'timeout')) * 1000
            try:
                await page.goto(LINK, timeout=timeout)
            except Error as e:
                logger.info(f"Произошла ошибка при загрузке страницы {e}")
            else:
                await page.wait_for_timeout(5000)
            try:
                await page.goto('https://www.change.org/petitions?selected=recent', timeout=timeout)
            except Error as e:
                logger.info(f"Произошла ошибка при загрузке страницы {e}")
            else:
                await page.wait_for_timeout(6000)
                await search_new_petions(page, timeout)
                await page.wait_for_timeout(4000)
                titles = await page.query_selector_all(".link-block")
                if titles:
                    await get_links(titles)
                    await get_content_change(page, timeout)
                    if arr_news:
                        await update_from_dict(arr_news)
                        print("Парсинг change.org успешно закончен")
                        logger.info("Парсинг change.org успешно закончен")
            finally:
                await browser.close()
                print("Браузер закрыт")


if __name__ == "__main__":
    asyncio.run(scrape_change_org())
