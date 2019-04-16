#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ke: A scraper of Beike, the best Chinese Real Estate Listing Website."""

__author__ = 'Qiao Zhang'

import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from collections import deque, OrderedDict
from tqdm import tqdm


class Ke:
    def __init__(self):
        self.url = self.generator_url()
        self.driver = self.login()

    def generator_url(self):
        """
        根据指定的爬取类型，获得正确的URL。贝壳网采用POST方式显示页面变化。

        要考虑整租/合租/公寓，省份，对话框关键字和依次的各项筛选条件。
        :return:
        """
        # 目前爬取北京的全量租房
        url = 'https://bj.zu.ke.com/zufang'

        return url

    def login(self):
        """
        登录程序，暂时不需要输入用户密码就可以登录。
        :return:
        """
        driver = webdriver.Chrome()
        driver.get(self.url)
        return driver

    def ke_scraper_rent(self):
        def get_list_urls(driver):
            """
            获取当前筛选条件下的所有房源链接。
            :param driver:
            :return:
            """
            def read_pages_number():
                """
                返回当前筛选条件下的多房源列表页码数，用于翻页。
                :param driver:
                :return: pages_number
                """
                pages_number = int(driver.find_elements_by_xpath("//div[@class='content__pg']/a")[-2].text)
                return pages_number

            def change_page():
                """
                实现多房源列表页的翻页功能。
                :param driver:
                :return:
                """
                driver.find_element_by_link_text('下一页').click()

            def get_list_urls_single():
                """
                获取单页所有的房源链接。
                :param driver:
                :return: list_urls_single
                """
                list_urls_single = []
                for i in driver.find_elements_by_xpath("//a[@class='content__list--item--aside']"):
                    list_urls_single.append(i.get_attribute('href'))
                return list_urls_single

            pages_number = read_pages_number()
            list_urls = []
            list_urls_single = get_list_urls_single()
            list_urls += list_urls_single
            print('开始获取当前筛选条件下的所有房源页链接。')
            for _ in tqdm(range(pages_number - 1)):
                change_page()
                list_urls_single = get_list_urls_single()
                list_urls += list_urls_single
            return list_urls

        def get_list_info(driver, url):
            """
            获取单房源信息。针对公寓和整租/合租的两种情况分别爬取,并分别存入数据库。
            :param driver:
            :param url:
            :return: df
            """
            driver.get(url)
            if 'apartment' in url:
                pass
            else:
                # 类型/标题：可能为空，导致标题的爬取报错
                try:
                    rent_type = driver.find_element_by_xpath("//p[@class='content__title']").text.split(' · ')[0]
                    title = driver.find_element_by_xpath("//p[@class='content__title']").text.split(' · ')[1]
                    print (rent_type, title)
                except:
                    rent_type = '未知'
                    title = driver.find_element_by_xpath("//p[@class='content__title']").text
                    print (url,'租赁方式未知', title)

                # 上架时间
                time_listed = driver.find_element_by_xpath("//div[@class='content__subtitle']").text[7:17]
                print (url, time_listed)

                # 编号
                house_code = driver.find_element_by_xpath("//div[@class='content__subtitle']/i[@class='house_code']").text[5:]
                print (house_code)

                # 信息卡照片：可能为空
                ##TODO:是否有多个？有bug无法打开
                try:
                    duty_img = driver.find_element_by_xpath("//div[@class='content__subtitle']/ul/li/div/img").get_attribute('src').split('!')[0]
                    print (duty_img)
                except:
                    duty_img = ''
                    print ('无信息卡照片。')

                # 信息卡号：可能为空
                try:
                    duty_id = driver.find_element_by_xpath("//div[@class='content__subtitle']/ul/li/div/p").text.split('证件号码：')[1].stripe()
                    print (duty_id)
                except:
                    duty_id = ''
                    print ('无信息卡号。')

                # 营业执照
                ##TODO

                # 经纪备案：可能为空
                ##TODO
                try:
                    pass
                except:
                    pass

                # 房源照片列表
                list_house_imgs = []
                for i in driver.find_elements_by_xpath("//div[@class='content__article__slide__item']/img"):
                    list_house_imgs.append(i.get_attribute('src'))
                print (list_house_imgs)

                # 价格
                house_price = int(driver.find_element_by_xpath("//p[@class='content__aside--title']/span").text)
                print(house_price)

                # 特色标签列表
                list_house_tags = []
                for i in driver.find_elements_by_xpath("//p[@class='content__aside--tags']/i"):
                    list_house_tags.append(i.text)
                print (list_house_tags)
                # 户型、面积、朝向
                house_type = driver.find_elements_by_xpath("//p[@class='content__article__table']/span")[1].text
                house_area = int(driver.find_elements_by_xpath("//p[@class='content__article__table']/span")[2].text.split('㎡')[0])
                house_orient = driver.find_elements_by_xpath("//p[@class='content__article__table']/span")[3].text.split('朝')[1]
                print (house_type, house_area, house_orient)

                # 经纪人姓名：可能为空
                ##TODO

                # 经纪人联系方式
                broker_contact = driver.find_element_by_xpath("//p[@class='content__aside__list--bottom oneline']").text
                print (broker_contact)

                # 最短租期/最长租期:统一显示为天数，一年360天(防止12个月和365天天数不相等的情况)，一个月30天
                rent_peroid = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[5]").text[3:]
                if '~' in rent_peroid:
                    if '月' in rent_peroid:
                        rent_peroid_lower = int(rent_peroid.split('~')[0])*30
                        rent_peroid_upper = int(rent_peroid.split('~')[1].split('个月')[0])*30
                    elif '年' in rent_peroid:
                        rent_peroid_lower = int(rent_peroid.split('~')[0])*360
                        rent_peroid_upper = int(rent_peroid.split('~')[1].split('年')[0])*360
                    else:
                        print (rent_peroid)
                        rent_peroid_lower = rent_peroid
                        rent_peroid_upper = rent_peroid
                else:
                    rent_peroid_lower = rent_peroid
                    rent_peroid_upper = rent_peroid
                print (rent_peroid_lower, rent_peroid_upper)

                # 所在楼层
                house_floor = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[8]").text[3:].split('/')[0]
                print(house_floor)

                # 总楼层
                house_total_floor = int(driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[8]").text[3:].split('/')[1].replace('层',''))
                print(house_total_floor)

                # 车位
                parking = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[11]").text[3:]
                print(parking)

                # 用电
                electricity_type = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[14]").text[3:]
                print(electricity_type)

                # 入住
                check_in = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[3]").text[3:]

                # 看房
                reservation = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[6]").text[3:]

                # 电梯
                lift= driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[9]").text[3:]

                # 用水
                water= driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[12]").text[3:]

                # 燃气
                ##TODO:和下面的天然气有什么区别？
                gas= driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[15]").text[3:]

                # 电视
                television = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[2]").get_attribute('class')
                if '_no' in television:
                    television = 0
                else:
                    television = 1

                # 冰箱
                refrigerator = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[3]").get_attribute('class')
                if '_no' in refrigerator:
                    refrigerator = 0
                else:
                    refrigerator = 1

                # 洗衣机
                washing_machine = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[4]").get_attribute('class')
                if '_no' in washing_machine:
                    washing_machine = 0
                else:
                    washing_machine = 1

                # 空调
                air_conditioner = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[5]").get_attribute('class')
                if '_no' in air_conditioner:
                    air_conditioner = 0
                else:
                    air_conditioner = 1

                # 热水器
                water_heater = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[6]").get_attribute('class')
                if '_no' in water_heater:
                    water_heater = 0
                else:
                    water_heater = 1

                # 床
                bed = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[7]").get_attribute('class')
                if '_no' in bed:
                    bed = 0
                else:
                    bed = 1

                # 暖气
                heating = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[8]").get_attribute('class')
                if '_no' in heating:
                    heating = 0
                else:
                    heating = 1

                # 宽带
                wifi = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[9]").get_attribute('class')
                if '_no' in wifi:
                    wifi = 0
                else:
                    wifi = 1

                # 衣柜
                wardrobe = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[10]").get_attribute('class')
                if '_no' in wardrobe:
                    wardrobe = 0
                else:
                    wardrobe = 1

                # 天然气
                natural_gas = driver.find_element_by_xpath("//ul[@class='content__article__info2']/li[11]").get_attribute('class')
                if '_no' in natural_gas:
                    natural_gas = 0
                else:
                    natural_gas = 1

                # 地址和交通
                ##TODO:subway_line结构化优化：10号线 - 亮马桥，1号线,八通线 - 四惠，4号线大兴线 - 生物医药基地，s1线 - 上岸
                list_subways = []
                for i in driver.find_elements_by_xpath("//div[@class='content__article__info4']/ul/li"):
                    print(i.text)
                    subway_line = i.find_element_by_xpath("//span[1]").text.split(' - ')[0]
                    print(subway_line)
                    subway_station = i.find_element_by_xpath("//span[1]").text.split(' - ')[1]
                    subway_station_distance = int(i.find_element_by_xpath("//span[2]").text.split('m')[0])
                    list_subways.append([subway_line, subway_station, subway_station_distance])

                # 小区最新成交
                complex_deals = driver.find_element_by_xpath("//div[@class='table']")
                complex_deals = pd.read_html('<table>' + complex_deals.get_attribute('innerHTML') + '</table>')
                complex_deals = complex_deals.to_dict()
                print (complex_deals)

                # 房源描述
                ##TODO:检查有无超过一条描述的情况
                if len(driver.find_elements_by_xpath("//div[@class='content__article__info3 ']/ul/li/p")) > 2:
                    house_description = ''
                    print ("请调整子函数get_list_info的房源描述部分，有超过一条评论的情况需要全部考虑。（做成列表而不再是文本）")
                else:
                    try:
                        house_description = driver.find_element_by_xpath("//div[@class='content__article__info3 ']/ul/li/p[1]").text
                    except:
                        house_description = ''

                # 房源链接
                house_url = url

                # 导入所有信息
                global df_single
                df_single = pd.DataFrame({'类型':rent_type,'标题':title,'上架时间':time_listed,'编号':house_code,'信息卡照片':duty_img,'信息卡号':duty_id,
                                          '营业执照':'','经纪备案':'','房源图片列表':list_house_imgs,'价格':house_price,'特色标签列表':list_house_tags,
                                          '户型':house_type,'面积':house_area,'朝向':house_orient,'经纪人姓名':'','经纪人联系方式':broker_contact,
                                          '最短租期':rent_peroid_lower,'最长租期':rent_peroid_upper,'所在楼层':house_floor,'总楼层':house_total_floor,
                                          '车位':parking,'用电':electricity_type,'入住':check_in,'看房':reservation,'电梯':lift,'用水':water,'燃气':gas,
                                          '电视':television, '冰箱':refrigerator,'洗衣机':washing_machine,'空调':air_conditioner,'热水器':water_heater,
                                          '床':bed,'暖气':heating,'宽带':wifi,'衣柜':wardrobe,'天然气':natural_gas,'地址和交通':list_subways,
                                          '小区最新成交':complex_deals,'房源描述':house_description,'房源链接':house_url})

            return df_single

        def main(driver):
            # 获取符合当前筛选条件的所有房源链接
            list_urls = get_list_urls(driver=driver)

            # 循环获取单房源信息
            df = pd.DataFrame()
            for url in tqdm(list_urls):
                df_single = get_list_info(driver=driver, url=url)
                df = df.append(df_single)

            # 保存列表
            df.to_csv('rent.csv', encoding='gb18030')

            driver.quit()
            return df

        df = main(self.driver)
        return df
