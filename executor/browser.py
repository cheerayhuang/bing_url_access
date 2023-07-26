import asyncio
import json
import re

from lxml import html as html_parser
from lxml.html.clean import Cleaner
from pyppeteer import launch

from common.logger import get_logger

_log = get_logger('browser')

# 测试检测webdriver
"""
async def main():
    #browser = await launch(headless=False, executablePath='chrome.exe', args=['--user-data-dir=/mnt/d/work/shr_win/chrome_tmp_user_data', '--disable-infobars', '--no-sandbox', '--disable-setuid-sandbox'])
    browser = await launch(headless=True, args=['--disable-infobars', '--no-sandbox', '--disable-setuid-sandbox'])

    is_closed = False
    async def handle_closed():
        nonlocal is_closed
        is_closed = True

    browser.on(
        "disconnected",
        await asyncio.create_task(handle_closed())
    )
    page = await browser.newPage()
    await page.setUserAgent("Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5")
    await page.setViewport(viewport={'width': 1536, 'height': 768})
    await page.goto('https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html')
    await asyncio.sleep(2)
    print(await page.content())
    await page.close()
    await asyncio.sleep(3)
    await browser.close()

    print(is_closed)

#asyncio.get_event_loop().run_until_complete(main())
"""

class BrowserException(Exception):
    def __init__(self, ex, status_code):
        super().__init__()
        self.ex = ex
        self.status_code = status_code

    def __str__(self):
        return str('browser_exception: '+ str(self.ex))

class Browser(object):
    _browser = None
    _is_closed = False
    #_default_page = None
    _cleaner = Cleaner()
    _resp_collection = {}

    async def __init__(self):
        pass

    async def __new__(cls, *args, **kargs):
        obj = super().__new__(cls)

        if Browser._browser is None:
            #launch_task = asyncio.create_task(launch(headless=False, args=['--disable-infobars', '--no-sandbox', '--disable-setuid-sandbox']))
            Browser._browser = await launch(headless=False, args=['--disable-infobars', '--no-sandbox', '--disable-setuid-sandbox'])

        Browser._cleaner.javascript = True
        Browser._cleaner.style = True


        return obj

    def is_closed(self):
        return Browser._browser.process.returncode is not None

    async def close(self):
        await Browser._browser.close()

    def analyse(self, raw_html):
        html = html_parser.fromstring(raw_html)
        html_cleaned = html_parser.tostring(Browser._cleaner.clean_html(html)).decode()
        #print(html_cleaned)
        html = html_parser.fromstring(html_cleaned)
        el_body = html.xpath(r'//body')[0]

        contents = el_body.text_content().strip()
        contents = re.sub(u'\xa0+', ' ', contents)
        contents = re.sub('\t+|\n+|\r+', ' ', contents)
        contents = re.sub(' +', ' ', contents)
        contents = re.sub('<.*?>', '', contents)

        return contents

    async def intercept_response(self, response, url):
        if response.url == url:
            Browser._resp_collection[response.url] = response
            _log.info(f'response: {response.url}, {response.status}, {response.request.url}')


    async def get_page_contents(self, url):
        page = await Browser._browser.newPage()

        #TODO: capture the response
        #page.on('response', lambda response, url: asyncio.ensure_future(self.intercept_response(response, url)))

        # pass the webdriver testing
        await page.evaluateOnNewDocument('() =>{Object.defineProperties(navigator, {webdriver: {get: ()=>false}})}')

        await page.setUserAgent("Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5")
        await page.setViewport(viewport={'width': 1536, 'height': 768})

        contents = ''
        raw_html = ''
        resp = None
        try:
            await page.goto(url, {'waitUntil': 'networkidle0'})

            raw_html = await page.content()
            contents = self.analyse(raw_html)
        except Exception as e:
            _log.error(f'access url failed: {e}')
            status_code = -1
            if url in Browser._resp_collection:
                status_code = Browser._resp_collection[url].status
                del Browser._resp_collection[url]
            raise BrowserException(e, status_code)

        finally:
            if url in Browser._resp_collection:
                resp = Browser._resp_collection[url]
                del Browser._resp_collection[url]

            await page.close()

        return contents, 200

async def main():
    b = await Browser()
    print(await b.get_page_contents('https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html'))
    print(b.is_closed())
    await b.close()
    await asyncio.sleep(2)
    print(b.is_closed())

if __name__ == '__main__':
    asyncio.run(main())
    #asyncio.get_event_loop().run_until_complete(main()) # deprecated
