#本篇按照书本实战项目爬取去哪儿网酒店信息
import time

import datetime

import pymongo
from bs4 import BeautifulSoup
from datashape import unicode
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class QunarSpider(object):

    def __init__(self):
        self.client = pymongo.MongoClient('localhost')
        self.db = self.client['qunar']

    def get_hotel(self,browser,tocity,fromdate,todate):
        wait = WebDriverWait(browser, 30)
        ele_tocity = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#toCity')))
        ele_fromdate = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#fromDate'))
        )
        ele_todate = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#toDate'))
        )
        ele_tosearch  = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainlandForm > div.search-btn-list.clrfix > div.search-btn > a'))
        )
        ele_tocity.clear()
        ele_tocity.send_keys(tocity)
        ele_fromdate.clear()
        ele_fromdate.send_keys(fromdate)
        ele_todate.clear()
        ele_todate.send_keys(todate)
        ele_tosearch.click()
        while True:
            try:
                wait.until(
                    EC.title_contains(tocity
                ))
            except Exception as e:
                print(e)
                break
            time.sleep(5)

            js = "window.scrollTo(0,document.body.scrollHeight)"
            browser.execute_script(js)
            time.sleep(5)

            html = browser.page_source
            soup  = BeautifulSoup(html,'lxml')
            infos = soup.find_all('div',class_ = 'item_hotel_info')
            for i in infos:
                hotel_info = {
                    'name' : i.find('a',class_ = 'e_title js_list_name').text,
                    'address' : i.find('p',class_ = 'adress').text,
                    'star' : i.find(class_='level_score js_list_score').text[:-3],
                    'comm_nums' : i.find(class_='level_comment level_commentbd js_list_usercomcount').text[:-3],
                    'price' : i .find(class_='item_price js_hasprice').find('b').text
                }
                print(hotel_info)
                self.save_to_mongo(hotel_info)
            #翻页 读取下一页内容进行爬取
            try:
                next_page = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,'#searchHotelPanel > div.b_tool.clr_after > div.pager.js_pager > div > ul > li.item.next'))
                )
                next_page.click()
                time.sleep(10)
            except Exception as e:
                print(e)
                break


    def save_to_mongo(self,hotel_info):
        try:
            if self.db['hotel'].insert(hotel_info):
                print('存储到MONGODB成功',hotel_info)
        except Exception:
            print('存储到MONGO失败',hotel_info)

    def crawl(self,root_url,tocity):
        fromdate= datetime.date.today().strftime('%Y-%m-%d')
        todate = datetime.date.today() + datetime.timedelta(days=1)
        todate = todate.strftime('%Y-%m-%d')
        browser = webdriver.Chrome()
        browser.get(root_url)
        browser.implicitly_wait(30)#控制间隔时间，等待浏览器反应
        self.get_hotel(browser,tocity,fromdate,todate)


if __name__ == '__main__':
    spider = QunarSpider()
    spider.crawl('http://hotel.qunar.com/',"广州")