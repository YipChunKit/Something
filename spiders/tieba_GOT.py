#这个是爬取最近百度贴吧---权力的游戏的帖子
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from multiprocessing import Pool
import traceback


def get_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        response = requests.get(url,headers = headers,timeout = 30)
        if response.status_code ==200:
            #这里我们知道百度贴吧的编码是utf-8，所以手动设置的。爬取其他的页面时建议使用
            #r.encoding = r.appent_encoding
            response.encoding = 'utf-8'
            return response.text
        return None
    except RequestException as e:
        return None

def parse_page(html):
    #初始化一个列表来保存所有的帖子信息：
    comments = []
    soup = BeautifulSoup(html,'lxml')
    #每个帖子都是这个li标签的class属性里
    litags = soup.find_all('li',attrs={'class':" j_thread_list clearfix"})
    for litag in litags:
        #初始化一个字典来存储文章信息
        comment = {}
        try:
            comment['rep_num']= litag.find('span',class_="threadlist_rep_num center_text").text
            comment['title'] =  litag.find('a',class_="j_th_tit ").text
            comment['author'] = litag.find('span',class_="tb_icon_author ").text
            comment['time'] = litag.find('span',class_="pull-right is_show_create_time").text
            comment['link'] = "http://tieba.baidu.com/" + litag.find('a',class_="j_th_tit")['href']
            comments.append(comment)
        except Exception as e:
            print('出了问题:',e)
            traceback.print_exc()


    return comments

def write_to_file(dict):
    with open("tieba_GOT.txt",'a+',encoding='utf-8') as f:
        for comment in dict:
            f.write('标题：{}\t 发帖人：{} \t 时间：{} \t 回复数：{} \t 链接：{}\n'.format(comment['title'],comment['author'],comment['time'],comment['rep_num'],comment['link']))
        print('当页已经爬取完成')

def main(offset):
    url = 'http://tieba.baidu.com/f?kw=%E6%9D%83%E5%8A%9B%E7%9A%84%E6%B8%B8%E6%88%8F&ie=utf-8&pn=' + str(offset)
    html = get_page(url)
    write_to_file(parse_page(html))


if __name__ == '__main__':
    pool = Pool()
    pool.map(main, [i * 50 for i in range(3)])

#问题：1.traceback回去之后看到有一些贴子因为作者没有被爬下去，回去看看网页结构，发现author的那里有些贴子文本只是...，可能text提取不了...,所以出错
#     2.但是3页多线程之后生成的txt文件只有40多个，但是原网页一页就已经有50条贴子记录，可能有一部分因为问题一的问题而缺少了，但是结果出现的只有几条的出错。问题在哪？
#针对问题2  回看了所有贴子  发现第三页一前一后的贴子都有，只有第三页被爬取到？
#然后将爬取页数改为2，看到结果和第2页的结果匹配，只有第二页被爬取到？第一页呢？
#问题所在：因为之前爬3页的时候只有第3页的内容，爬2页只有第2页的内容，证明了当爬3页的时候，第3页的内容把之前第一 第二 写好的内容给覆盖了，爬2页的时候第2页覆盖了第一页的内容。证明写txt文件的时候是删除了前面的文件又再次生成最后一次的结果
#则是文件的写入方式的错误 w是写入，会把已经在的文件删除后再创建写入，所以应该选 a，追加，将后面的内容添加到前面的内容之后。这个应该是多线程存在进行时间差的机制，最晚结束的线程运行生成该的结果，而且之前的写入数据库机制不同txt文件，数据库的机制
#应该也是追加的。下次写txt文件的时候注意写入方式。

