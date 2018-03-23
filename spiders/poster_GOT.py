#本篇是模仿崔老师的爬取百度贴吧贴子内容的项目实战--目标对象是两个贴子
#1.权力的游戏一至六季海报图片 http://tieba.baidu.com/p/4662159543?pn=1
#2.同一样的楼主发布出来第七季的海报图片 http://tieba.baidu.com/p/5180609302?pn=1
#本篇目标：1.对百度贴吧任意贴子进行抓取 2.指定是否只爬取楼主发帖内容  3.将抓取的内容分析并保存文件
#因为代码是保存图片在文件夹中，运行前先创建相应路径的文件夹或者改文件路径
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from multiprocessing import Pool

#百度贴吧爬虫类：
class BDTB:

    #初始化，传入基地址，是否只看楼主的参数
    def __init__(self,seelz):
        self.see_lz = '?see_lz=' + str(seelz)
        self.link_list = []
        self.link_list_other = []
    #传入页码，获取该页贴子的代码
    def get_page(self,url):
        headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
        try:
            response = requests.get(url,headers = headers,timeout = 60)
            if response.status_code == 200:
                return response.text
            return None
        except RequestException as e:
            return None

    def get_link(self,html):
        soup = BeautifulSoup(html,'lxml')
        img_tags = soup.find_all('img',class_="BDE_Image")
        for img in img_tags:
            link = img['src']
            self.link_list.append(link)
        print('已得到链接列表')
        return self.link_list

    def get_image(self,page_num):
        index = 1
        for link in self.link_list:
            r = requests.get(link, timeout = 30)
            file_name = 'C:/Users/hasee/Desktop/GOT_IMG' + '/' + str(page_num)+ '-' + str(index) + '.jpg'
            with open(file_name,'wb') as f:
                f.write(r.content)
            index += 1
        print('一页的图片保存成功')

    def main(self,offset):
        base_url = 'http://tieba.baidu.com/p/4662159543'
        url = base_url + self.see_lz + '&pn=' + str(offset)
        html = self.get_page(url)
        self.get_link(html)
        self.get_image(offset)

    def get_other(self,html):
        soup = BeautifulSoup(html, 'lxml')
        img_tags = soup.find_all('img', class_="BDE_Image")
        for img in img_tags:
            link = img['src']
            self.link_list_other.append(link)
        index = 1
        for link in self.link_list_other:
            r = requests.get(link, timeout = 30)
            file_name = 'C:/Users/hasee/Desktop/GOT_IMG' + '/' + '第七季-' + str(index) + '.jpg'
            with open(file_name,'wb') as f:
                f.write(r.content)
            index += 1
        print('一页的图片保存成功')

    def other_main(self):
        url = 'http://tieba.baidu.com/p/5180609302?see_lz=1'
        html = self.get_page(url)
        self.get_other(html)

if __name__ == '__main__':
    # see_lz=1  是只看楼主，输入参数1 然后对其实例化
    pool = Pool()
    bdtb = BDTB(1)
    pool.map(bdtb.main,[i for i in range(1,30)])
    bdtb.other_main()
    print('所有图片保存成功')

#问题:想使用多线程进行快速爬取，发现存在超时或者文件丢失或文件被叠加重名，可能这是多线程的弊端，而且一边读写文件，一边请求页面
#     请求页面的速度快于读写的速度 导致list的内存混乱，试试放弃多线程进行爬取
#之后又对多线程进行取消，用for循环代替多线程发现情况一样，然后以为是类的问题 又取消了类  结果甚至提前就已经取消
#猜测 是网站的反爬虫机制，对机器不回应