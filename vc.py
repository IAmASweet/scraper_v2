import re
from playwright.async_api import async_playwright
from playwright._impl._api_types import Error, TimeoutError
from utils.time_process import check_time
from datetime import datetime
from csv_process import update_from_dict
from utils.clean_up_text import clean_up_text
import asyncio
from settings.settings import get_config, logger

FILENAME = "test.csv"

arr_text = []
arr_news = []


async def format_date_vc(date_news):
    news_time = re.sub(r'\(Europe/Moscow\)', "", date_news).strip()
    date_object = datetime.strptime(news_time, '%d.%m.%Y %H:%M:%S')
    return await check_time(date_object)


async def search_new_news(page):
    news_times = await page.query_selector_all(".time")
    if news_times:
        while await format_date_vc(await news_times[-1].get_attribute("title")):
            await page.mouse.wheel(0, 20000)
            await page.wait_for_timeout(3000)
            news_times = await page.query_selector_all(".time")


async def get_links(selectors):
    for item in selectors:
        item_title = await item.query_selector(".content-title")
        href_selector = await item.query_selector(".content-link")
        href = await href_selector.get_attribute('href')
        if item_title:
            text = await item_title.text_content()
            if text and href:
                match = re.sub('Статьи редакции', '', text, re.I)
                arr_text.append({'title': match.strip(), 'link': href})
        else:
            continue


async def get_content(page, timeout):
    for title in arr_text:
        try:
            await page.goto(title['link'], timeout=timeout)
        except (Error, TimeoutError) as e:
            logger.info(f"Произошла ошибка при загрузке страницы {e}")
            continue
        else:
            await page.wait_for_timeout(4000)
            content_block = await page.query_selector(".content--full")
            text = ''
            if content_block:
                text_content = await content_block.query_selector_all("p")
                if text_content:
                    for item in text_content:
                        item_text = await item.text_content()
                        if item_text:
                            text = text + item_text.strip()
            clean_texts = clean_up_text([title['title'], text])
            arr_news.append({'title': clean_texts[0], 'content': clean_texts[1]})


async def scrape_vc():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
        except Error as e:
            print(e)
            logger.info(e)
        else:
            page = await browser.new_page()
            print("Начат парсинг vc.ru")
            logger.info("Начат парсинг vc.ru")
            timeout = int(get_config('Default', 'timeout')) * 1000
            try:
                await page.goto("https://vc.ru/new/all", timeout=timeout)
            except (Error, TimeoutError) as e:
                logger.info(f"Произошла ошибка при загрузке страницы {e}")
            else:
                await page.wait_for_timeout(3000)
                await search_new_news(page)
                news_containers = await page.query_selector_all(".feed__item")
                if news_containers:
                    await get_links(news_containers)
                if arr_text:
                    await get_content(page, timeout)
                    print("update")
                    await update_from_dict(arr_news)
                print("Парсинг vc.ru успешно закончен")
                logger.info("Парсинг vc.ru успешно закончен")
            finally:
                await browser.close()
                print("Браузер закрыт")


if __name__ == '__main__':
    asyncio.run(scrape_vc())
