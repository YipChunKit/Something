#本篇是跟着崔庆才老师的糗事百科段子爬虫做的
#目标是：1.抓取糗事百科热门段子   2.过滤带有图片的段子  3.实现每按一次回车显示一个段子的发布时间，发布人，段子内容，点赞数

#1.确定URL并抓取页面代码
# -*- coding:utf-8 -*-
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup


#2.提取某一页的所有段子
"""
这里和崔老师的文章不太一样，应该糗事百科又改版了，崔老师的文章是三年前的，那里的class都是同一样共用。
到现在写的时候，class 已经分成四类，应该要对四三类分别find 然后归到同一列表。有一类特别特殊，就是属性长段子，需要按查看全文
才能看到，所以这里就过滤长段子  只对 old hot recent类进行爬取"""


#3.完善交互，设计面向对象模式
#需要设计面向对象模式，引入类和方法，将代码做一下优化和封装。

__author__ = 'CQC'
#糗事百科爬虫类
class QSBK:

    #初始化方法，定义一些变量
    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        #初始化headers
        self.headers = {'User-Agent' : self.user_agent}
        #存放段子的变量，每一个元素是每一页的段子们
        self.stories =[]
        #存放程序是否继续运行的变量
        self.enable = False
    #传入某一页的索引获得页面代码
    def getPage(self,pageIndex):
        try:
            url = 'https://www.qiushibaike.com/8hr/page/' + str(pageIndex)
            #构建请求的requests,并获取代码txt
            response = requests.get(url,headers = self.headers)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException as e:
            if hasattr(e,'reaseon'):
                print("连接糗事百科失败，错误原因",e.reason)
                return None

    #传入某一页代码，返回本页不带图片的段子列表
    def getPageItems(self,pageIndex):
        html = self.getPage(pageIndex)
        if not html:
            print('页面加载失败')
            return None
        #bs解析
        soup = BeautifulSoup(html, 'lxml')
        #用来存储每页的段子们
        page_stories = []
        hot_articles = soup.find_all('div', class_="article block untagged mb15 typs_hot")
        old_articles = soup.find_all('div', class_="article block untagged mb15 typs_old")
        recent_articles = soup.find_all('div', class_="article block untagged mb15 typs_recent")
        for hot in hot_articles:
            #是否含有图片
            haveImg = hot.find('div', class_='thumb')
            #如果不含有图片，把它加入list中
            if not haveImg:
                body = hot.find('span').text
                author = hot.find('h2').text
                like_num = hot.find('span', class_='stats-vote').find('i', attrs={"class":"number"}).text
                comment_num = hot.find('span', class_='stats-comments').find('i',attrs={"class":"number"}).text
                try:
                    comment = hot.find('div', class_='main-text').text.replace('\n','   ')
                except:
                    comment = '暂时没有热评'

                joke = '作者：{}{}喜欢人数：{}\n评论人数：{}\n热评：{}'.format(author, body, like_num, comment_num, comment)
                page_stories.append(joke)

        for old in old_articles:
            haveImg = hot.find('div', class_='thumb')
            if not haveImg:
                body = old.find('span').text
                author = old.find('h2').text
                like_num = old.find('span', class_='stats-vote').find('i', attrs={"class":"number"}).text
                comment_num = old.find('span', class_='stats-comments').find('i', attrs={"class":"number"}).text
                try:
                    comment = old.find('div', class_='main-text').text.replace('\n','   ')
                except:
                    comment = '暂时没有热评'

                joke = '作者：{}{}喜欢人数：{}\n评论人数：{}\n热评：{}'.format(author, body, like_num, comment_num, comment)
                page_stories.append(joke)

        for recent in recent_articles:
            haveImg = hot.find('div', class_='thumb')
            if not haveImg:
                body = recent.find('span').text
                author = recent.find('h2').text
                like_num = recent.find('span', class_='stats-vote').find('i', attrs={"class":"number"}).text
                comment_num = recent.find('span', class_='stats-comments').find('i', attrs={"class":"number"}).text
                try:
                    comment = recent.find('div', class_='main-text').text.replace('\n','  ')
                except:
                    comment = '暂时没有热评'

                joke = '作者：{}{}喜欢人数：{}\n评论人数：{}\n热评：{}'.format(author, body, like_num, comment_num, comment)
                page_stories.append(joke)

        return page_stories


    #加载并提取页面的内容，加入到列表中
    def loadPage(self):
        #如果当前未看的页数少于2,页，则加载新一页
        if self.enable == True:
            if len(self.stories) < 2:
                #获取新一页
                page_stories = self.getPageItems(self.pageIndex)
                #将该页的段子存放到全局list中
                if page_stories:
                    self.stories.append(page_stories)
                    #获取完之后页码索引加一，表示下次读取下一页
                    self.pageIndex += 1

    #调用该方法，每次敲回车打印输出一个段子
    def getoneStory(self,page_story):
        #遍历一页的段子
        for story in page_story:
            #等待用户输出
            input1 = input()
            #每当输入回车一次，判断一下是否要加载新页面
            self.loadPage()
            #如果输入Q则程序结束
            if input1 == 'Q':
                self. enable = False
                return
            print(story)

    #开始方法
    def start(self):
        print('正在读取糗事百科，按回车查看新段子，Q退出')
        #使变量为True，程序可以正常运行
        self.enable = True
        #先加载一页内容
        self.loadPage()
        #局部变量， 控制当前读到了第几页
        while self.enable:
            if len(self.stories)>0:
                #从全局list中读取一页的段子
                page_story = self.stories[0]
                #将全局list中的第一元素删除，因为已经取出
                del self.stories[0]
                #输出该页的段子
                self.getoneStory(page_story)

spider = QSBK()
spider.start()