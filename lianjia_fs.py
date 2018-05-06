import json
from multiprocessing.pool import Pool

import pymysql
import time
from lxml import etree

import requests
from bs4 import BeautifulSoup


class spider(object):
    def start_quest(self,url):
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
        response = requests.get(url, headers=self.headers)
        try:
            if response.status_code == 200:
                html = response.text
        except Exception as e:
            print(e)
            return None
        return html

    def parse_index(self,html):
        soup = BeautifulSoup(html,'lxml')
        url_list = []
        list1 = soup.find_all('div',class_='info-panel')
        for i in list1:
            url = i.find('h2').find('a')['href']
            url_list.append(url)
        return(url_list)

    def getlocation(self,name):
        url = 'http://api.map.baidu.com/geocoder/v2/'
        output = 'json'
        ak = 'V4jViWqvBdGgS3yM1B5VNOhfqRqwMZx6'
        address = name
        uri = url + '?' + 'address=' + address + '&output=' + output + '&ak=' + ak
        resp = requests.get(uri)
        text = json.loads(resp.text)
        if 'result' in text:
            lat = text['result']['location']['lat']
            lng = text['result']['location']['lng']
        else:
            return None
        return lat,lng

    def parse_detail(self,lists):
        for i in lists:
            html = self.start_quest(i)
            soup = BeautifulSoup(html,'lxml')
            name= soup.find('div', class_='content zf-content').find_all('p')[5].find('a').text
            yield {
                'id': soup.find('span',class_='houseNum').text[5:],
                'price' : soup.find('div',class_='price').text,
                'square':soup.find('div',class_='content zf-content').find_all('p')[0].text,
                'size':soup.find('div',class_='content zf-content').find_all('p')[1].text,
                'floor':soup.find('div',class_='content zf-content').find_all('p')[2].text,
                'face':soup.find('div',class_='content zf-content').find_all('p')[3].text,
                'dstnce_sub':soup.find('div',class_='content zf-content').find_all('p')[4].text,
                'name':soup.find('div',class_='content zf-content').find_all('p')[5].find('a').text,
                'county':soup.find('div', class_='content zf-content').find_all('p')[6].find_all('a')[0].text,
                'town':soup.find('div', class_='content zf-content').find_all('p')[6].find_all('a')[1].text,
                'lat' : self.getlocation(name)[0] if self.getlocation(name)  else None,
                'lng' : self.getlocation(name)[1] if self.getlocation(name)  else None
            }



    def main(self,offset):
        url = 'https://fs.lianjia.com/zufang/'+ 'pg' + str(offset)
        print(offset)
        html = self.start_quest(url)
        url_list = self.parse_index(html)
        try:
            db = pymysql.connect(host='localhost',user='root',password='123456',port=3306,db='spiders',charset='utf8')
            cursor = db.cursor()
            for item in self.parse_detail(url_list):
                keys = ', '.join(item.keys())
                values = ','.join(['%s'] * len(item))
                try:
                    sql = 'INSERT INTO lianjia({keys}) VALUES ({values})'.format(keys = keys,values=values)
                    cursor.execute(sql,tuple(item.values()))
                except pymysql.Error as e:
                    print(e)
                print('数据保存成功')
            db.commit()
            db.close()
        except pymysql.Error as e:
            print('Mysql Error %d:%s' % (e.args[0],e.args[1]))

if __name__=='__main__':
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='spiders', charset='utf8')
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS lianjia")
    sqlc = """CREATE TABLE lianjia(
            id VARCHAR(255) NOT NULL PRIMARY KEY,
            price VARCHAR(255) NOT NULL,
            square VARCHAR(255) NOT NULL,
            size VARCHAR(255)NOT NULL,
            floor VARCHAR(255)NOT NULL,
            face VARCHAR(255) NOT NULL,
            dstnce_sub VARCHAR(255)NOT NULL,
            name VARCHAR(255) NOT NULL,
            county VARCHAR(255)NOT NULL,
            town VARCHAR(255)NOT NULL,
            lat VARCHAR(255) ,
            lng VARCHAR(255) 
            )"""
    cursor.execute(sqlc)
    fs = spider()
    pool = Pool()
    pool.map(fs.main,[i for i in range(0,88)])
    time.sleep(3)
