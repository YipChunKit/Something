import requests
from requests.exceptions import RequestException
import re
import pymysql
from multiprocessing import Pool


def get_one_page(url,headers):
    try:
        response = requests.get(url,headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_one_page(html):
    pattern = re.compile('<li>.*?em class.*?>(\d+)</em>.*?title">(.*?)</span>.*?p class.*?>'
                         + '(.*?)<br>(.*?)</p>.*?class="star">.*?property="v:average">(.*?)</span>'
                         + '.*?span>(.*?)</span>.*?class="inq">(.*?)</span>.*?<li>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'rank': item[0],
            'title': item[1],
            'director': clean_name(item[2].strip())[0],
            'actor': clean_name(item[2].strip())[1],
            'time': clean_type(item[3].strip())[0],
            'area': clean_type(item[3].strip())[1],
            'type': clean_type(item[3].strip())[2],
            'score': item[4],
            'number': item[5].strip().replace('<span>','')[:-3],
            'quote': item[6]
        }


def clean_name(data):
    txt = data.replace('/', '')
    txt = txt.replace('&nbsp', '')
    txt = txt.replace('.', '')
    txt = txt.split(';')
    director_name = txt[0][3:]
    actor_name = txt[3][3:]
    return director_name,actor_name


def clean_type(data):
    txt = data.replace('&nbsp;','')
    txt = txt.split('/')
    return txt

def main(offset):
    url = 'https://movie.douban.com/top250?start=%d&filter=' % (offset)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    html = get_one_page(url,headers = headers)
    try:
        db = pymysql.connect(host='localhost',user='root',password='123456',port=3306,db='spiders',charset='utf8')
        cursor = db.cursor()
        for item in parse_one_page(html):
            keys = ', '.join(item.keys())
            values = ','.join(['%s'] * len(item))
            try:
                sql = "INSERT INTO douban_top250({keys}) VALUES ({values})".format(keys = keys,values=values)
                cursor.execute(sql,tuple(item.values()))
            except pymysql.Error as e:
                print(e)
            print('数据保存成功')
        db.commit()
        cursor.close()
        db.close()
    except pymysql.Error as e:
        print('Mysql Error %d:%s' % (e.args[0],e.args[1]))


if __name__ == '__main__':
    db = pymysql.connect(host='localhost',user='root',password='123456',port=3306,db='spiders',charset='utf8' )
    cursor = db.cursor()
    cursor.execute("DROP TABLE IF EXISTS douban_top250")
    sqlc = """CREATE TABLE douban_top250(
        rank INT NOT NULL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        director VARCHAR(255) NOT NULL,
        actor VARCHAR(255)NOT NULL,
        time VARCHAR(255)NOT NULL,
        area VARCHAR(255) NOT NULL,
        type VARCHAR(255)NOT NULL,
        score VARCHAR(255) NOT NULL,
        number VARCHAR(255)NOT NULL,
        quote VARCHAR(255)NOT NULL
        )"""
    cursor.execute(sqlc)
    pool = Pool()
    pool.map(main,[i * 25 for i in range(10)])
