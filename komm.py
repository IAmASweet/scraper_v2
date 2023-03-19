from playwright.async_api import async_playwright
from datetime import datetime
from playwright._impl._api_types import Error, TimeoutError
from utils.time_process import check_time
from csv_process import update_from_dict
import asyncio
from utils.clean_up_text import clean_up_text
from settings.settings import get_config, logger

arr_text = []
KOMMERSANT = 'https://www.kommersant.ru/'
arr_news = []


async def format_date_kommersant(date_news):
    date_news = date_news.strip()
    date_object = datetime.strptime(date_news, '%d.%m.%Y, %H:%M')
    return await check_time(date_object)


async def get_content(page, timeout):
    for item in arr_text:
        try:
            await page.goto(item['link'], timeout=timeout)
        except (Error, TimeoutError) as e:
            logger.info(f"Произошла ошибка при загрузке страницы {e}")
            continue
        else:
            await page.wait_for_timeout(2000)
            first_news = await page.query_selector(".js-article")
            content = ''
            if first_news:
                contents = await first_news.query_selector_all(".doc__text")
                for text in contents:
                    content = content + await text.text_content()
                thoughts = await page.query_selector_all("doc__thought")
                for thought in thoughts:
                    content = content + await thought.text_content()
                if content:
                    clean_texts = clean_up_text([item['title'], content.strip()])
                    arr_news.append({'title': clean_texts[0], 'content': clean_texts[1]})
                await page.wait_for_timeout(3000)


async def search_new_news(page, timeout):
    articles = await page.query_selector_all('.uho__text')
    if articles:
        date_news = await articles[-1].query_selector(".uho__tag")
        while await format_date_kommersant(await date_news.text_content()):
            try:
                await page.wait_for_selector(".doc_button--rubric", timeout=timeout)
                await page.get_by_role("button", name="Показать еще").click(force=True, timeout=timeout)
            except (Error, TimeoutError) as e:
                logger.info(f"Произошла ошибка при нажатии на кнопку Показать ещё {e}")
                break
            else:
                await page.wait_for_timeout(2000)
                articles = await page.query_selector_all('.uho__text')
                if articles:
                    date_news = await articles[-1].query_selector(".uho__tag")
    return articles


async def get_links(selectors):
    for item in selectors:
        title = await item.query_selector(".uho__link")
        if title:
            href = await title.get_attribute('href')
            title_text = await title.text_content()
            if title_text and href:
                arr_text.append({'title': title_text.strip(), 'link': KOMMERSANT + href})


async def scrape_kommersant():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False)
        except Error as e:
            print(e)
            logger.info(e)
        else:
            page = await browser.new_page()
            print("Начат парсинг kommersant.ru")
            logger.info("Начат парсинг kommersant.ru")
            timeout = int(get_config('Default', 'timeout')) * 1000
            try:
                await page.goto("https://www.kommersant.ru/lenta?from=all_lenta", timeout=timeout)
            except (Error, TimeoutError) as e:
                logger.info(f"Произошла ошибка при загрузке страницы {e}")
            else:
                await page.wait_for_timeout(5000)
                articles = await search_new_news(page, timeout)
                if articles:
                    await page.wait_for_timeout(5000)
                    await get_links(articles)
                    await get_content(page, timeout)
                    await update_from_dict(data=arr_news)
                    print("Парсинг kommersant.ru успешно закончен")
                    logger.info("Парсинг kommersant.ru успешно закончен")
            finally:
                await browser.close()
                print("Браузер закрыт")


if __name__ == "__main__":
    asyncio.run(scrape_kommersant())
