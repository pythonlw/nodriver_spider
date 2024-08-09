# -*- coding: utf-8 -*-
import asyncio
import nodriver as uc
from nodriver import cdp
import time

xhr_requests = []

class RequestMonitor:
    def __init__(self):
        self.requests = []
        self.last_request = None
        self.lock = asyncio.Lock()

    async def listen(self, page):
        async def handler(evt):
            async with self.lock:
                if evt.response.encoded_data_length > 0 and evt.type_ is cdp.network.ResourceType.XHR:
                    # print(f"EVENT PERCEIVED BY BROWSER IS:- {evt.type_}") # If unsure about event or to check behaviour of browser
                    self.requests.append([evt.response.url, evt.request_id])
                    self.last_request = time.time()
        page.add_handler(cdp.network.ResponseReceived, handler)

    async def receive(self, page):
        responses = []
        retries = 0
        max_retries = 5

        # Wait at least 2 seconds after the last XHR request to get some more
        while True:
            print('max_retries:', max_retries)
            print('self.last_request:', self.last_request)
            if self.last_request is None or retries >= max_retries:
                break
            if time.time() - self.last_request <= 2:
                retries += 1
                await asyncio.sleep(2)
                continue
            else:
                break
        await page  # Waiting for page operation to complete.
        # Loop through gathered requests and get its response body
        print('0000')
        async with self.lock:
            for request in self.requests:
                try:
                    print('url:', request[1])
                    res = await page.send(cdp.network.get_response_body(request[1]))
                    if res is None:
                        continue
                    responses.append({
                        'url': request[0],
                        'body': res[0],  # Assuming res[0] is the response body
                        'is_base64': res[1]  # Assuming res[1] indicates if response is base64 encoded
                    })
                except Exception as e:
                    print("Error getting body", e)
        print('1111')
        return responses


async def crawl():
    browser = await uc.start(headless=False)
    monitor = RequestMonitor()
    tab = browser.main_tab

    await monitor.listen(tab)

    tab = await asyncio.wait_for(browser.get("https://www.bing.com"), timeout=60)
    await asyncio.sleep(6)

    xhr_responses = await monitor.receive(tab)
    for response in xhr_responses:
        print(f"URL: {response['url']}")
        # print("Response Body:")
        # print(response['body'] if not response['is_base64'] else "Base64 encoded data")

    frame_data = await tab.send(uc.cdp.page.get_frame_tree())
    current_url = frame_data.frame.url
    current_url2 = await tab.evaluate("window.location.href")
    print('current_url:', current_url)
    print('current_url2:', current_url2)

    cookies = await tab.send(cdp.storage.get_cookies())
    print('cookies2:', cookies)

    res = await tab.send(cdp.network.get_cookies([current_url]))
    for i in res:
        name = i.name
        value = i.value
        to_json = i.to_json()
        print('name:', name)
        print('value:', value)
        print('to_json:', to_json)
        break


if __name__ == '__main__':
    uc.loop().run_until_complete(crawl())












