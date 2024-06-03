import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import time, threading, queue


def create_driver():
    # 創建一個 Options 物件
    chrome_options = Options()

    chrome_options.add_argument("--start-maximized") # Chrome 瀏覽器在啟動時最大化視窗
    chrome_options.add_argument("--incognito") # 無痕模式
    chrome_options.add_argument("--disable-popup-blocking") # 停用 Chrome 的彈窗阻擋功能。
    chrome_options.add_argument('--headless')

    # Linux 環境啟用 ChromeDriver
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    return driver

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        print(f"{func.__name__} 執行時間: {end_time - start_time} 秒")
        return result
    return wrapper

def get_stock_price_from_openapi(stock_code):
    STOCK_DAY_AVG_ALL_URL = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_AVG_ALL'
    data = requests.get(STOCK_DAY_AVG_ALL_URL)
    for stock_info in data.json():
        if stock_info['Code'] == stock_code:
            return stock_info['ClosingPrice']

def get_stock_price_from_cnyes(q, stock_code):
    stock_code_url = f'https://www.cnyes.com/twstock/{stock_code}'
    driver = create_driver()
    driver.get(stock_code_url)
    price = driver.find_elements(By.XPATH, '//*[@id="anue-ga-wrapper"]/div[4]/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/h3')
    if q != None:
        q.put({stock_code: price[0].text})

    return price[0].text

def get_stock_price_from_yahoo(stock_code):
    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(f'https://tw.stock.yahoo.com/quote/{stock_code}.TW', headers=user_agent)

    soup = BeautifulSoup(response.text, 'lxml')

    main_element = soup.find('div', {'class': 'D(f) Ai(fe) Mb(4px)'})
    price_text = main_element.find('span').text
    
    return price_text

def get_usd_price_from_yahoo():
    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(f'https://tw.stock.yahoo.com/quote/USDTWD=X', headers=user_agent)

    soup = BeautifulSoup(response.text, 'lxml')

    main_element = soup.find('div', {'class': 'D(f) Ai(fe) Mb(4px)'})
    price_text = main_element.find('span').text
    
    return price_text

@timing_decorator
def multithread_stock_price(stock_code_list):
    q = queue.Queue()
    all_thread = []

    for code in stock_code_list:
        thread = threading.Thread(target=get_stock_price_from_cnyes, args=(q, code))
        thread.start()
        all_thread.append(thread)

    for t in all_thread:
        t.join()
    
    total_price = {}
    while not q.empty():
        price_dict = q.get()
        total_price.update(price_dict)
    return total_price

# multithread_stock_price(['00900', '00885', '6719'])

def get_asset_price_from_fubonlife(asset_name):
    driver = create_driver()

    if asset_name == '富利人生':
        url = 'https://invest.fubonlife.com.tw/w/wb/CBFubonNav1.djhtm?a=FBD15'
        element = '//*[@id="SysJustWebGraphDIV"]/div/div[2]/div[3]/div[2]/div[2]/div/span[2]'
    elif asset_name == '鑫美一生(安聯)':
        url = 'https://invest.fubonlife.com.tw/w/wr/cf02.djhtm?a=DSD1'
        element = '//*[@id="SysJustIFRAMEDIV"]/div[7]/div[1]/table/tbody/tr[1]/td[2]'
    elif asset_name == '鑫美一生(富蘭克林)':
        url = 'https://invest.fubonlife.com.tw/w/wr/cf02.djhtm?a=FRD2'
        element = '//*[@id="SysJustIFRAMEDIV"]/div[7]/div[1]/table/tbody/tr[1]/td[2]'
    else:
        return 0
    
    driver.get(url)
    time.sleep(5)
    price = driver.find_elements(By.XPATH, element)

    return price[0].text

def get_fund_price_from_yahoo(fund_name):
    user_agent = {'User-agent': 'Mozilla/5.0'}
    if fund_name == '柏瑞趨勢動態多重資產基金-B類型':
        url = 'https://tw.stock.yahoo.com/fund/summary/F00001D4E4:FO'
    elif fund_name == '摩根泰國基金':
        url = 'https://tw.stock.yahoo.com/fund/summary/F0GBR060I5:FO'
    elif fund_name == '野村特別時機非投資等級債券基金-月配類型美元計價':
        url = 'https://tw.stock.yahoo.com/fund/history/F000016ZJV:FO'
    else:
        return 0
    
    response = requests.get(url, headers=user_agent)
    soup = BeautifulSoup(response.text, 'lxml')

    main_element = soup.find('div', {'class': 'fh-price D(f) Mt(4px) Ai(fe)'})
    price_text = main_element.find('span').text

    return price_text