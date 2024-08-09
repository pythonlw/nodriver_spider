# -*- coding: utf-8 -*-
import json
from nodriver import start, cdp, loop
import nodriver as uc


async def switch_to_frame(browser, frame):
    """
    切换iframe
    let iframe = document.querySelector("YOUR_IFRAME_SELECTOR")
    let iframe_tab = iframe.contentWindow.document.body;
    """
    iframe_tab: uc.Tab = next(
            filter(
                lambda x: str(x.target.target_id) == str(frame.frame_id), browser.targets
            )
        )
    return iframe_tab


async def main():
    config = uc.Config()
    browser_args = ['--disable-web-security', f"--proxy-server=http://127.0.0.1:10809"]   # 完全禁用浏览器的同源策略
    browser = await uc.start(browser_args=browser_args)
    tab0 = browser.main_tab
    tab0.add_handler(cdp.network.RequestWillBeSent, send_handler)
    tab0.add_handler(cdp.network.ResponseReceived, receive_handler)

    tab = await browser.get("https://docs.capsolver.com/guide/recognition/FunCaptchaClassification.html")
    # tab = await browser.get("http://www.yescaptcha.cn/auth/login")

    await tab.send(cdp.page.add_script_to_evaluate_on_new_document(
         """
            Element.prototype._as = Element.prototype.attachShadow;
            Element.prototype.attachShadow = function (params) {
                return this._as({mode: "open"})
            };
        """
    ))
    for _ in range(10):
        await tab.scroll_down(50)
    await tab
    # await tab.back()
    all_urls = await tab.get_all_urls()
    # for u in all_urls:
    #     print("downloading %s" % u)
    #     await tab.download_file(u)
    await tab.sleep(15)

    cookies = browser.cookies.get_all()
    print('cookies:', cookies)

    browser.connection.mapper.clear()
    await browser.cookies.clear()

    # frame_content = await tab.select_all('div.frame-content', include_frames=True)
    # print('frame_content:', len(frame_content))
    # for frame in frame_content:
    #     print('text_all:', frame.text_all)
    #     print('get_html:', frame.get_html)

    # query_selector = await tab.select_all('button[class="widgetLabel moveFromRightLabel-enter-done"]', include_frames=True)
    # print('query_selector:', query_selector)
    # if len(query_selector) == 1:
    #     await query_selector[0].click()

    # 解决 yescaptcha.cn
    # recaptcha0 = await tab.select('iframe[title="reCAPTCHA"]')
    # print('recaptcha0:', recaptcha0.frame_id)
    # # for tar in browser.targets:
    # #     print('target_id:', tar.target.target_id)
    # iframe_tab = await switch_to_frame(browser, recaptcha0)
    # # iframe_tab: uc.Tab = next(
    # #     filter(
    # #         lambda x: str(x.target.target_id) == str(recaptcha0.frame_id), browser.targets
    # #     )
    # # )
    # print('iframe_tabwebsocket_url:', iframe_tab.websocket_url)
    # iframe_tab.websocket_url = iframe_tab.websocket_url.replace("iframe", "page")
    # button = await iframe_tab.select("span#recaptcha-anchor")
    # await button.click()


    try: # 解决普通iframe
        recaptcha0 = await tab.select('iframe[id="tidio-chat-iframe"]')
        print('recaptcha0:', recaptcha0.frame_id)
        for tar in browser.targets:
            print('target_id:', tar.target.target_id)
        iframe_tab = await switch_to_frame(browser, recaptcha0)
        print('iframe_tabwebsocket_url:', iframe_tab.websocket_url)
        iframe_tab.websocket_url = iframe_tab.websocket_url.replace("iframe", "page")
        button = await iframe_tab.select('button[class="widgetLabel moveFromRightLabel-enter-done"]')
        await button.click()
    except Exception as e:
        print('error:', e)
        query_selector = await tab.select_all('button[class="widgetLabel moveFromRightLabel-enter-done"]',
                                              include_frames=True)
        print('query_selector:', query_selector)
        if len(query_selector) == 1:
            await query_selector[0].click()

    frame_data = await tab.send(cdp.page.get_frame_tree())
    print(json.dumps(frame_data.to_json(), indent=4))

    input('stop')


async def receive_handler(event: cdp.network.ResponseReceived):
    # print('service_worker_response_source:', event.response.service_worker_response_source)
    # print('service_worker_router_info:', event.response.service_worker_router_info)
    # print('to_json:', event.response.to_json)
    # print('url:', event.response.url)
    # print('timing:', event.response.timing)
    # # print('response:', dir(event.response))
    # print('*'*100)
    pass



async def send_handler(event: cdp.network.RequestWillBeSent):
    r = event.request
    s = f"{r.method} {r.url}"
    for k, v in r.headers.items():
        s += f"\n\t{k} : {v}"


if __name__ == "__main__":
    loop().run_until_complete(main())



_node= [ 'apply', 'assigned_slot', 'attributes', 'attrs', 'backend_node_id', 'base_url', 'child_node_count', 'children',
         'clear_input', 'click', 'compatibility_mode', 'content_document', 'distributed_nodes', 'document_url', 'flash',
         'focus', 'frame_id', 'get_html', 'get_js_attributes', 'get_position', 'highlight_overlay', 'imported_document',
         'internal_subset', 'is_recording', 'is_svg', 'local_name', 'mouse_click', 'mouse_drag', 'mouse_move', 'node',
         'node_id', 'node_name', 'node_type', 'node_value', 'object_id', 'parent', 'parent_id', 'pseudo_elements',
         'pseudo_identifier', 'pseudo_type', 'public_id', 'query_selector', 'query_selector_all', 'record_video',
         'remote_object', 'remove_from_dom', 'save_screenshot', 'save_to_dom', 'scroll_into_view', 'select_option',
         'send_file', 'send_keys', 'set_text', 'set_value', 'shadow_root_type', 'shadow_roots', 'system_id', 'tab',
         'tag', 'tag_name', 'template_content', 'text', 'text_all', 'tree', 'update', 'value', 'xml_version']










