# http://bbs.zhue.com.cn/gongqiu.php?mod=index&level=3&upid=1619
# http://bbs.zhue.com.cn/gongqiu.php?mod=index&level=1&upid=7
# http://bbs.zhue.com.cn/gongqiu.php?mod=index&upid=7&level=1&page=2

import re
import datetime
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from selenium import webdriver

upid_map = {'北京市': '1', '天津市': '2', '河北省': '3', '山西省': '4', '内蒙古': '5',
            '辽宁省': '6', '吉林省': '7', '黑龙江': '8', '上海市': '9', '江苏省': '10',
            '浙江省': '11', '安徽省': '12', '福建省': '13', '江西省': '14', '山东省': '15',
            '河南省': '16', '湖北省': '17', '湖南省': '18', '广东省': '19', '广西': '20',
            '海南省': '21', '重庆市': '22', '四川省': '23', '贵州省': '24', '云南省': '25',
            '西藏': '26', '陕西省': '27', '甘肃省': '28', '青海省': '29', '宁夏': '30',
            '新疆': '31', '台湾省': '32', '香港': '33', '澳门': '34', '海外': '35',
            '其他': '36'}

base_url = 'http://bbs.zhue.com.cn/gongqiu.php'  # Target website base url
query_mode = 'index'  # query type
query_level = '1'  # data level
query_upid = upid_map['吉林省']  # Province Jilin
today = datetime.date.today()  # start date
now = datetime.datetime.now()  # start datetime
file_name = str(today) + '生猪供求数据.xlsx'  # data-container file

brower = webdriver.Firefox()  # use FireFox Brower


# url constructor
def url_constructor(page_num):
    return base_url + '?mod=' + query_mode + '&level=' + query_level \
           + '&upid=' + query_upid + '&page=' + str(page_num)


# convert html to soup
def html_to_soup(url):
    r = requests.get(url)
    html = r.content
    return BeautifulSoup(html, 'xml')


# get url-list
def details_url_list_getter(url):
    brower.get(url)
    link_list = []
    span_list = brower.find_elements_by_xpath('//*[@class="gongqiu_pic tc"]')
    for span in span_list:
        link_list.append(span.find_element_by_tag_name('a').get_attribute('href'))
    return link_list


# get details
def details_info_getter(details_url):
    html = html_to_soup(details_url)
    # include `TITLE` and `PUBLIC DATE`
    top_block = html.find('div', attrs={'class', 'index_content_title'})
    title = top_block.find('h1').get_text()
    publish_date = top_block.find('div', attrs={'class', 'index_content_title_subtitle'}).get_text()
    publish_date = re.findall(r"(\d{2}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", publish_date)[0]
    # info table
    content_block = html.find('div', attrs={'class', 'index_content_extracontact'})
    info_spans = content_block.find_all('span', attrs={'class': 'val'})
    ip_location = content_block.find('span', attrs={'class': 'ip'})

    result_dic = {}
    result_dic['url'] = details_url  # 页面链接
    result_dic['title'] = title  # 标题
    result_dic['public_date'] = publish_date  # 发布日期
    result_dic['info_type'] = info_spans[0].get_text()  # 信息类型
    result_dic['region_name'] = info_spans[1].get_text()  # 区域名称
    result_dic['type_depc'] = info_spans[2].get_text()  # 类别从属
    result_dic['pay_way'] = info_spans[3].get_text()  # 付款方式
    result_dic['price'] = info_spans[4].get_text()  # 价格
    result_dic['acount'] = info_spans[5].get_text()  # 数量
    result_dic['meat_percent'] = info_spans[6].get_text()  # 出肉率
    result_dic['weight'] = info_spans[7].get_text()  # 体重
    result_dic['skin_color'] = info_spans[8].get_text()  # 毛色
    result_dic['publisher'] = info_spans[9].get_text()  # 发布人
    result_dic['contact'] = info_spans[10].get_text()  # 联系人
    result_dic['company'] = info_spans[11].get_text()  # 公司名字
    result_dic['telphone'] = info_spans[12].get_text()  # 联系电话
    result_dic['qq_number'] = info_spans[13].get_text()  # QQ咨询
    result_dic['farm_type'] = info_spans[14].get_text()  # 猪场类型
    result_dic['pub_ip'] = info_spans[15].get_text() + ip_location.get_text()  # 发布者IP
    return result_dic


# spider logic...
def spider(current_page=1):
    while True:
        print('开始获取第' + str(current_page) + '页数据...')
        url_list = details_url_list_getter(url_constructor(current_page))
        if len(url_list) > 0:
            page_info_list = []
            for url in url_list:
                page_info_list.append(details_info_getter(url))
            print('完成获取第' + str(current_page) + '页数据...')
            current_page += 1
        else:
            break


# Main method
if __name__ == '__main__':
    spider()
    print("完成本次数据爬取任务!")
    brower.close()
