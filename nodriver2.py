# -*- coding: utf-8 -*-
import mss
import subprocess
import time
from pyppeteer import launch
import os
import requests
import json
import asyncio
import random
from undetected_chromedriver import find_chrome_executable
import nodriver as uc
from nodriver import cdp, loop

"""
https://stabler.tech/blog/nodriver-a-new-webscraping-tool
https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1832 拦截请求
https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1816
https://ultrafunkamsterdam.github.io/nodriver/index.html # 文档
https://github.com/ultrafunkamsterdam/nodriver/blob/main/docs/_build/markdown/index.md
https://ultrafunkamsterdam.github.io/nodriver/_modules/nodriver/cdp/browser.html
https://ultrafunkamsterdam.github.io/nodriver/nodriver/cdp/fetch.html # 文档
https://chromedevtools.github.io/devtools-protocol/tot/Page/
"""




def cmd_start_brower(chrome_path, port, user_data_dir=None):
    # 命令行启动浏览器
    # chrome_path_temp = self.chrome_path.replace('\chrome.exe', '')
    # start_params = r'cd {} && chrome.exe --remote-debugging-port={} --no-first-run --disable-infobars --allow-file-access-from-files --no-default-browser-check --profile-directory=Profile1'
    # os.popen(start_params.format(chrome_path_temp, self.port))

    # --disable-popup-blocking
    start_params = r'{} --remote-debugging-port={} --no-first-run --no_sandbox --disable-infobars --allow-file-access-from-files --no-default-browser-check --profile-directory=Profile1 --disable-features=PrivacySandboxSettings4'
    subprocess.Popen(start_params.format(chrome_path, port), encoding="gbk", shell=True)


def get_session_url(chrome_path, port, user_data_dir):
    url = f'http://127.0.0.1:{port}/json/version'
    try:
        res = requests.get(url)
        print(res.text)
        webSocketDebuggerUrl = json.loads(res.text)['webSocketDebuggerUrl']
    except Exception as e:
        print('error:', e)
        cmd_start_brower(chrome_path, port, user_data_dir)
        time.sleep(random.randint(4, 6))


async def judge_element_exist(page, js_path, type=1, params=None):
    # 判断标签是否存在
    if type == 1:
        # 元素路径需要双引号包裹
        js_path = js_path.replace('"', "'")
        if params:
            result = await page.evaluate(
                '''var temp = arguments[0].querySelector("%s");if(temp){true}else{"false"}''' % js_path,
                params)
        else:
            result = await page.evaluate(
                '''var temp = document.querySelector("%s");if(temp){true}else{"false"}''' % js_path)
    else:
        # 元素路径需要单引号包裹 模糊匹配
        js_path = js_path.replace("'", '"')
        if params:
            result = await page.evaluate(
                '''var temp = arguments[0].querySelector('%s'); if(temp){true}else{"false"}''' % js_path,
                params)
        else:
            result = await page.evaluate(
                '''var temp = document.querySelector('%s');if(temp){true}else{"false"}''' % js_path)
    return result


async def js_element_click(page, js_path=None, type=1, params=None):
    # js 元素点击
    if type == 1:
        # 元素路径需要双引号包裹
        if params:
            params_js = '''var temp = arguments[0];if(temp){temp.click()}'''
            await page.evaluate(params_js, params)
        else:
            js_path = js_path.replace('"', "'")
            await page.evaluate('''var temp=document.querySelector("%s");if(temp){temp.click()}''' % js_path)
    else:
        # 元素路径需要单引号包裹(模糊匹配)
        if params:
            params_js = '''var temp = arguments[0]; if(temp){temp.click()}'''
            await page.evaluate(params_js, params)
        else:
            js_path = js_path.replace("'", '"')
            await page.evaluate('''var temp=document.querySelector('%s');if(temp){temp.click()}''' % js_path)


async def judge_element_text(page, tag_path, text):
    # js 根据文本定位
    js0 = '''
    var temp = Array.from(document.querySelectorAll('%s')).find(el => el.textContent.includes('%s'));
    if(temp){true}else{"false"};
    '''% (tag_path, text)
    result = await page.evaluate(js0)
    return result


async def judge_element_text_click(page, text, tag_path=None, params=None):
    # js 根据文本定位
    if params:
        params_js = '''var temp = arguments[0];if(temp){temp.click()}'''
        await page.evaluate(params_js, params)
    else:
        js0 = """
            var temp = Array.from(document.querySelectorAll('%s')).find(el => el.textContent.includes('%s'));
            if(temp){temp.click()};
        """ % (tag_path, text)
        await page.evaluate(js0)



async def operate_setup(driver, page):
    # is_invalid = await page.select('form#sb_form')
    # print('is_invalid:', dir(is_invalid))
    # print('attr:', is_invalid.attr)

    # get_content = await page.get_content()
    get_content = await asyncio.wait_for(page.get_content(), timeout=60)
    # print(get_content)
    # await page.save_screenshot()

    frame_data = await page.send(uc.cdp.page.get_frame_tree())
    print('child_frames:', frame_data.child_frames)
    print('to_json:', frame_data.to_json())

    current_url = frame_data.frame.url
    current_url1 = page.url
    my_url = await page.evaluate("window.location.href")
    print('current_url1:', current_url1)
    print('current_url:', current_url)
    print('current_url:', my_url)
    # await page.scroll_down(150)
    await page.sleep(6)

    locationhref = await page.evaluate('''window.location.href''')
    print('locationhref:', locationhref)

    await page.evaluate('''document.querySelector("#kw").value="python"''')
    result = await page.evaluate(
        '''{var temp = document.querySelector("input[id*='kw12']");if(temp){temp.value}else{"0000"}}''',
        await_promise=True)
    print('result:', result)

    result1 = await judge_element_exist(page, "input[id*='kw']")
    print('result1:', result1)
    await js_element_click(page, 'input[id="su"]')

    await page.sleep(3.5)

    dynamic_content = await page.evaluate('document.querySelector("#kw").innerText')
    print(f'Dynamic Content: {dynamic_content}')

    # result2 = await judge_element_text(page, 'a', '百度首页')
    # print('result2:', result2)
    # await judge_element_text_click(page, '百度首页', 'a')

    tabs = driver.tabs
    print('tabs:', tabs)
    targets = driver.targets
    print('targets:', targets)
    main_tab = driver.main_tab
    print('main_tab:', main_tab)
    print('handlers:', page.handlers)


async def change_handle(driver, url_params='blog.csdn.net'):
    # 多个tab页面切换
    """
    :param url_params: url包含的内容
    :return: page对象
    """
    for page in driver.tabs:
        title = page.target.title
        url = page.target.url
        print('title:', title)
        print('url:', url)
        if url_params in url:
            await page.bring_to_front()  # 将页面前置,激活此页面
            await page
            return page
        else:
            await page.close()
        print('target_id:', page.target.target_id)


async def flash_spans(tab, i):
    await tab.activate()
    title = tab.target.title
    print('title:', title)


async def demo_drag_to_relative_position_in_steps(browser):
    # 将元素拖到指定位置
    tab = await browser.get('https://nowsecure.nl/mouse.html', new_tab=True)
    boxes = await tab.select_all('.box')
    for box in boxes:
        await box.mouse_drag((500, 500), relative=True, steps=50)


async def receive_handler(event: cdp.network.ResponseReceived):
    print('request_id:', event.request_id)
    print('response:', event.response)


async def send_handler(event: cdp.network.RequestWillBeSent):
    # print('request_id:', event.request_id)
    r = event.request
    s = f"{r.method} {r.url}"
    for k, v in r.headers.items():
        s += f"\n\t{k} : {v}"
    # print('request:', s)


async def receive_handler1(event: cdp.fetch.RequestPaused, main_tab):
    print('resource_type:', event.resource_type)
    return await main_tab.send(cdp.fetch.continue_request(request_id=event.request_id))


async def main1():
    config = uc.Config()
    config.host = "127.0.0.1"
    config.port = 62805
    # config.user_data_dir = user_data_dir
    browser_args = ['--no-first-run', '--no-sandbox', '--window-size=1020,1080', '--disable-infobars',
                    '--disable-web-security', '--disable-site-isolation-trials',
                    # f"--proxy-server=http://127.0.0.1:10809"
                    ]
    driver = await uc.start(
        config=config,
        browser_args=browser_args
                            )

    main_tab = driver.main_tab
    main_tab.add_handler(cdp.network.RequestWillBeSent, send_handler)
    # main_tab.add_handler(cdp.fetch.RequestPaused, lambda e: receive_handler1(e, main_tab))
    main_tab.add_handler(cdp.network.ResponseReceived, receive_handler)

    page = await asyncio.wait_for(driver.get('https://www.baidu.com'), timeout=120)
    print('page:', dir(page))
    print('driver:', dir(driver))

    # page2 = await driver.get('https://twitter.com', new_tab=True)
    # page3 = await driver.get('https://github.com/ultrafunkamsterdam/nodriver', new_window=True)
    await page.reload()    # 刷新页面
    await page.bring_to_front()

    tabs = driver.tabs
    print('tabs:', tabs)
    targets = driver.targets
    print('targets:', targets)
    main_tab = driver.main_tab
    print('main_tab:', main_tab)
    print('to_json:', page.to_json())
    input_text = await page.select('input[id="kw"]')
    await input_text.clear_input()
    await input_text.send_keys('python')
    await page.sleep(2)

    create_account = await page.find("百度一下", best_match=True)
    print('create_account:', create_account)
    # await create_account.click()
    await page.sleep(3.5)
    su = await page.select('input#su')
    await su.click()
    await page.sleep(3.5)

    input_thing = await page.select("a[href^='http://trust.baidu.com']")
    attrs = input_thing.attrs
    print('attrs:', attrs)

    # 异步执行多个操作
    # await asyncio.gather(*[flash_spans(tab, i) for (i, tab) in enumerate(driver.tabs)])
    await page.sleep(2)
    # await demo_drag_to_relative_position_in_steps(driver)

    content_left = await page.select('div#content_left>div a[href^="http://www.baidu.com/link"]')
    print('content_left:', dir(content_left))
    print('text_all:', content_left.text_all)
    
    # 获取cookie
    frame_data = await page.send(cdp.page.get_frame_tree())
    print('frame_data00:', frame_data.frame.url)
    cookies1 = await page.send(cdp.network.get_cookies([frame_data.frame.url]))
    print('cookies1', cookies1)
    cookies2 = [{i.name: i.value for i in cookies1}]
    cookies3 = [i.to_json() for i in cookies1]
    with open('cookies.json', 'w') as f:
        f.write(json.dumps(cookies2))
    # await page.set_cookies(cookies)
    await operate_setup(driver, page)


port = 62805
# 查找谷歌浏览器路径
chrome_path = find_chrome_executable()
print('chrome_path:', chrome_path)
user_data_dir = './pyppeteer_chrome'
# 检测浏览器是否已打开
get_session_url(chrome_path, port, user_data_dir)

uc.loop().run_until_complete(main1())








