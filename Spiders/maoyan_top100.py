import pymysql
import requests
from requests.exceptions import RequestException
import re
from multiprocessing import Pool
from bs4 import BeautifulSoup


def get_one_page(url,headers):
    try:
        response = requests.get(url,headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

#正则表达式解析
def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
                         + '.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'rank': item[0],
            'picture': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }


#BeautifulSoup解析
def bs4_info(html):
    soup = BeautifulSoup(html,'html.parser')
    names = [i.string for i in soup.find_all(name = 'p',attrs = 'name')]
    stars = [i.string.strip() for i in soup.find_all(name = 'p',attrs = 'star')]
    times = [i.string for i in soup.find_all(name = 'p',attrs= ' releasetime')]
    scores_tag = [i.contents for i in soup.find_all(names = 'p',attrs = 'score')]
    scores = [item[0].string +item[1].string for item in scores_tag]

    return names,stars,times,scores


#xpath解析
def lxml_info(html):
    #这个地方注意一下，不加decode的话中文的显示有问题
    element_html = html.fromstring(html.content.decode('utf-8'))
    names = element_html.xpath("//p[@class = 'name']/a/text()")#text后面要加括号
    stars = [i.strip() for i in element_html.xpath("//p[@class = 'star']/text()")]
    times = [i for i in element_html.xpath("//p[@class = 'releasetime']/text()")]
    scores_integer = element_html.xpath("//i[@class = 'integer']/text()")
    scores_fraction = element_html.xpath("//i[@class = 'fraction']/text()")
    scores = [scores[0] + scores[1] for scores in zip(scores_integer,scores_fraction)]

    return names,stars,times,scores



def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    html = get_one_page(url,headers = headers)
    try:
        db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='spiders',
                                   charset='utf8', use_unicode=False)
        cur = db.cursor()
        for item in parse_one_page(html):
            keys = ', '.join(item.keys())
            values = ', '.join(['%s'] * len(item))
            try:
                sql = "INSERT INTO maoyan_top100 ({keys}) VALUES ({values})".format(keys=keys, values=values)
                cur.execute(sql, tuple(item.values()))
            except pymysql.Error as e:
                print(e)
            print('数据保存成功')
        db.commit()
        cur.close()
        db.close()
    except pymysql.Error as e:
        print("Mysql Error %d:%s" % (e.args[0], e.args[1]))

# 多线程
if __name__ == '__main__':
    db = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='spiders', charset='utf8')
    cur = db.cursor()
    cur.execute("DROP TABLE IF EXISTS maoyan_top100")
    sql1 = """CREATE TABLE maoyan_top100( 
           rank int not null primary key auto_increment,    
           picture VARCHAR(100) NOT NULL, 
           title VARCHAR(100) NOT NULL, 
           actor VARCHAR(200) NOT NULL, 
           time VARCHAR(100) NOT NULL, 
           score VARCHAR(50) NOT NULL   
       )"""
    cur.execute(sql1)
    db.commit()
    pool = Pool()
    pool.map(main, [i * 10 for i in range(10)])
