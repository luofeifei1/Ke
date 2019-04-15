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
        driver = webdriver.Chrome()
        driver.get(self.url)
        return driver

    def ke_scraper(self):
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
                    print ('无信息卡照片。')
                # 信息卡号：可能为空
                try:
                    duty_id = driver.find_element_by_xpath("//div[@class='content__subtitle']/ul/li/div/p").text.split('证件号码：')[1].stripe()
                    print (duty_id)
                except:
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
                # 特色标签
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
                # 发布日期


                # 最短租期


                # 最长租期


                # 所在楼层


                # 总楼层


                # 车位


                # 用电


                # 入住


                # 看房


                # 电梯


                # 用水


                # 燃气


                # 电视


                # 冰箱


                # 洗衣机


                # 空调


                # 热水器


                # 床


                # 暖气


                # 宽带


                # 衣柜


                # 天然气


                # 地址和交通


                # 小区最新成交


                # 房源描述


                # 房源链接
                house_url = url

                global df_single
                df_single = pd.DataFrame(columns=['类型','标题','上架时间','编号','信息卡照片','信息卡号','营业执照','经纪备案','房源图片列表','价格','特色标签','户型','面积','朝向'
                                              ,'经纪人姓名','经纪人联系方式','发布日期','最短租期','最长租期','所在楼层','总楼层','车位','用电','入住','看房','电梯','用水','燃气'
                                              , '电视', '冰箱', '洗衣机','空调','热水器','床','暖气','宽带','衣柜','天然气','地址和交通','小区最新成交','房源描述','房源链接'])

            return df_single

        def main(driver):
            # 获取符合当前筛选条件的所有房源链接
            list_urls = get_list_urls(driver=driver)

            # 循环获取单房源信息
            df = pd.DataFrame()
            for url in tqdm(list_urls):
                df_single = get_list_info(driver=driver, url=url)
                df = df.append(df_single)

            driver.quit()
            return df

        df = main(self.driver)
        return df
