from playwright.async_api import async_playwright
from playwright._impl._api_types import Error, TimeoutError
from utils.clean_up_text import clean_up_text
from csv_process import update_from_dict
import asyncio
from settings.settings import get_config, logger

arr_text = []
arr_news = []


async def scroll_page(page, count, pixels, microseconds):
    for x in range(count):
        await page.mouse.wheel(0, pixels)
        await page.wait_for_timeout(microseconds)


async def get_links(selectors):
    for item in selectors:
        href = await item.get_attribute('href')
        title = await item.query_selector(".news-feed__item__title")
        title_text = await title.text_content()
        if href and title_text:
            arr_text.append({'title': title_text.strip(), 'link': href})


async def get_content(page, timeout):
    for item in arr_text:
        if await page.query_selector(".live-tv-popup") is not None:
            await page.eval_on_selector("div.live-tv-popup", "node => node.remove()")
        try:
            await page.goto(item['link'], timeout=timeout)
        except (Error, TimeoutError) as e:
            logger.info(f"Произошла ошибка при загрузке страницы {e}")
            continue
        else:
            await page.wait_for_timeout(3000)
            div = await page.query_selector(".article__text")
            if div:
                p_all = await div.query_selector_all("p")
            else:
                continue
            text = ""
            if p_all:
                for p in p_all:
                    paragraphe_text = await p.text_content()
                    if paragraphe_text:
                        text = text + paragraphe_text.strip()
            clean_texts = clean_up_text([item['title'], text])
            arr_news.append({'title': clean_texts[0], 'content': clean_texts[1]})
            await page.wait_for_timeout(2000)


async def scrape_rbc():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
        except Error as e:
            print(e)
            logger.info(e)
        else:
            page = await browser.new_page()
            print("Начат парсинг rbc.ru")
            logger.info("Начат парсинг rbc.ru")
            timeout = int(get_config('Default', 'timeout')) * 1000
            try:
                await page.goto("https://www.rbc.ru/", timeout=timeout)
            except (Error, TimeoutError) as e:
                logger.info(f"Произошла ошибка при загрузке страницы {e}")
            else:
                await page.wait_for_timeout(5000)
                if await page.query_selector(".live-tv-popup") is not None:
                    await page.eval_on_selector("div.live-tv-popup", "node => node.remove()")
                await scroll_page(page, 2, 20000, 3000)
                news_containers = await page.query_selector_all(".js-news-feed-item")
                if news_containers:
                    await get_links(news_containers)
                    await get_content(page, timeout)
                await update_from_dict(data=arr_news)
                print("Парсинг rbc.ru успешно закончен")
                logger.info("Парсинг rbc.ru успешно закончен")
            finally:
                await browser.close()
                print("Браузер закрыт")


if __name__ == "__main__":
    asyncio.run(scrape_rbc())
