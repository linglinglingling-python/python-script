import json,time
import uvicorn
from pydantic import BaseModel

from browsermobproxy import Server
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from fastapi import FastAPI, Response, Request,status
from fastapi.responses import JSONResponse
 
def get_pic(url):
    # 开启Proxy
    server = Server(r'你的browsermob-proxy所在目录\bin\browsermob-proxy.bat',{"port":7988})
    server.start()
    proxy = server.create_proxy()
 
    # 配置Proxy启动WebDriver
    chrome_options = Options()
    chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
    # 解决 您的连接不是私密连接问题
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-urlfetcher-cert-requests')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    #无头浏览器
    chrome_options.add_argument("--headless")
    # 通过设置user-agent，用来模拟移动设备
    user_ag='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    chrome_options.add_argument('user-agent=%s'%user_ag)
    #chromedriver放在chrome浏览器目录下
    service = Service('你的chromedriver所在目录\chromedriver.exe')
    driver = webdriver.Chrome(service=service,options=chrome_options)
    driver.implicitly_wait(20)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                            Object.defineProperty(navigator, 'webdriver', {
                              get: () => undefined
                            })
                          """
        })
    proxy.new_har("kuaishou", options={'captureHeaders': True, 'captureContent': True})
 
    driver.get(url)#
    time.sleep(3)

    result = proxy.har
 
 
    for entry in result['log']['entries']:
        _url = entry['request']['url']
        if "photos?__NS_sig3=" in _url:
            _response = entry['response']
            _content = _response["content"]
            # 获取接口返回内容
            if _content["size"]!=0:
                _data=json.loads(_content["text"])

                _data=_data["data"]["finishPlayingRecommend"]["feeds"][0]["ext_params"]["atlas"]
                #print(_data)
                server.stop()
                return {
                    "status":"ok",
                    "data":_data
                }


            # 读取信息
    
 
    server.stop()
    return {"status":"no",}

#get_pic()

class Item(BaseModel):
    url: str

app = FastAPI(
    title="My first blog FastAPI",
    description="Author - DJWOMS",
    version="0.5",
)

@app.post("/yzm/")
async def read_item(item: Item):
    item_dict = item.dict()
    jd = get_pic(item_dict["url"])
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jd
    )  
uvicorn.run(app, port=7862)
