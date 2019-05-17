#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Ke: A scraper of Beike, the best Chinese Real Estate Listing Website."""

__author__ = 'Qiao Zhang'

import time
import json
import codecs
import pandas as pd
import pyautogui
from selenium import webdriver
from bs4 import BeautifulSoup
from collections import OrderedDict
from tqdm import tqdm



class WriterJson:
    def __init__(self):
        pass

    # 将单个DataFrame保存为JSON，确保中文显示正确
    def df_to_json(self, df, orient:str = 'table'):
        return json.loads(df.to_json(orient, force_ascii=False))

    # 将多个DataFrames组成的字典批量保存为JSON，确保中文显示正确:服务于类似`金融产品信息表`这样的包含多
    def dfs_to_json(self, dic_dfs, orient:str = 'table'):
        pass

    # 将单个OrderedDict保存为JSON List
    def odict_to_json(self, odict):
        items = list(odict.items())
        list_JSONed = []

        # 把列表中的每个dict通过list append变成json
        for i in range(len(items)):
            try:
                # 当内容为dict
                try:
                    list_JSONed.append([items[i][0],json.dumps(items[i][1], ensure_ascii=False)])
                # 当内容为df
                except:
                    list_JSONed.append([items[i][0], json.loads(items[i][1].to_json(orient='table', force_ascii=False))])
            except:
                print(items[i][0] + '表为空，请检查。')
        # 记录版本信息
        list_JSONed.append({'version_date': time.strftime("%Y/%m/%d")})

        return list_JSONed

    # 从list_JSONed获取公司名称，用于设置JSON文件名称
    def get_company_name_from_JSON(self, items_JSONed):
        pass

    # 将一个json list或者json dict存入文件
    def write_json(self, json_list, file_name, indent=4, encoding='utf-8'):
        f_out = codecs.open(file_name, 'w', encoding=encoding)
        json_str = json.dumps(json_list, indent=indent, ensure_ascii=False)
        f_out.write(json_str)
        f_out.close()


class Ke:

    def __init__(self, username=None, password=None):
        self.username, self.password = username, password
        self.driver = self.login()

    def login(self):
        """
        登录程序，暂时不需要输入用户密码就可以登录。
        :return:
        """
        #TODO：登录程序debug，登录按钮无法点击
        driver = webdriver.Chrome()

        # driver.get('https://bj.zu.ke.com/zufang/')
        # driver.find_element_by_xpath("//*[@id='top']/li[12]/span/span[1]").click()
        # driver.find_element_by_xpath("//*[@id='con_login_user_tel']/form/ul/li[8]/a").click()
        # driver.find_element_by_xpath("//*[@id='con_login_user']/form/ul/li[1]/input").send_keys(self.username)
        # driver.find_element_by_xpath("//*[@id='con_login_user']/form/ul/li[2]/input").send_keys(self.password)
        # time.sleep(1)
        # driver.find_element_by_xpath("//*[@id='con_login_user']/form/ul/li[7]/a").click()
        return driver

    def ke_scraper_rent(self, url, keyword=None, export='csv'):
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
                pages_number = int(driver.find_element_by_xpath("//div[@class='content__pg']").get_attribute('data-totalpage'))
                return pages_number

            def change_page():
                """
                实现多房源列表页的翻页功能。
                :param driver:
                :return:
                """
                try:
                    driver.find_element_by_link_text('下一页').click()
                except:
                    page_number_current = int(driver.find_element_by_xpath("//div[@class='content__pg']").get_attribute('data-curpage'))
                    driver.find_element_by_xpath("//div[@class='content__pg']/a[@data-page='{}']".format(page_number_current+1)).click()

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
            print('开始获取当前筛选条件下的所有房源页链接。Windows平台下，请勿最小化浏览器。')
            for _ in tqdm(range(pages_number - 1)): # 默认-1/97
                change_page()
                list_urls_single = get_list_urls_single()
                list_urls += list_urls_single

            # 去除重复链接
            list_urls = list(set(list_urls))
            return list_urls

        def get_list_info(driver, url):
            """
            获取单房源信息。针对公寓和整租/合租的两种情况分别爬取,并分别存入数据库。
            :param driver:
            :param url:
            :return: df
            """
            driver.get(url)
            ##TODO：支持对公寓房源的爬取。
            if 'apartment' in url:
                pass
            else:
                # 类型/标题：可能为空，导致标题的爬取报错
                # try:
                #     rent_type = driver.find_element_by_xpath("//p[@class='content__title']").text.split(' · ')[0]
                #     title = driver.find_element_by_xpath("//p[@class='content__title']").text.split(' · ')[1]
                # except:
                #     rent_type = '未知'
                #     title = driver.find_element_by_xpath("//p[@class='content__title']").text
                rent_type = driver.find_elements_by_xpath("//p[@class='content__article__table']/span")[0].text
                title = driver.find_element_by_xpath("//p[@class='content__title']").text
                if '未知' in rent_type:
                    rent_type = '未知'

                # 上架时间
                time_listed = driver.find_element_by_xpath("//div[@class='content__subtitle']").text[7:17]

                # 编号
                house_code = driver.find_element_by_xpath("//div[@class='content__subtitle']/i[@class='house_code']").text[5:]

                # 信息卡照片：可能为空
                ##TODO:是否有多个？有bug无法打开
                try:
                    duty_img = driver.find_element_by_xpath("//div[@class='content__subtitle']/ul/li/div/img").get_attribute('src').split('!')[0]
                except:
                    duty_img = ''

                # 信息卡号：可能为空
                try:
                    duty_id = driver.find_element_by_xpath("//div[@class='content__subtitle']/ul/li/div/p").text.split('证件号码：')[1].stripe()
                except:
                    duty_id = ''

                # 营业执照
                ##TODO

                # 经纪备案：可能为空
                ##TODO
                try:
                    pass
                except:
                    pass

                # 房源照片列表
                json_house_imgs = []
                for i in driver.find_elements_by_xpath("//div[@class='content__article__slide__item']/img"):
                    json_house_imgs.append(i.get_attribute('src'))
                json_house_imgs = json.dumps(json_house_imgs, ensure_ascii=False)

                # 价格
                house_price = int(driver.find_element_by_xpath("//p[@class='content__aside--title']/span").text)

                # 特色标签列表
                json_house_tags = []
                for i in driver.find_elements_by_xpath("//p[@class='content__aside--tags']/i"):
                    json_house_tags.append(i.text)
                json_house_tags = json.dumps(json_house_tags, ensure_ascii=False)

                # 户型、面积、朝向
                house_type = driver.find_elements_by_xpath("//p[@class='content__article__table']/span")[1].text
                house_area = int(driver.find_elements_by_xpath("//p[@class='content__article__table']/span")[2].text.split('㎡')[0])
                house_orient = driver.find_elements_by_xpath("//p[@class='content__article__table']/span")[3].text.split('朝')[1]

                # 经纪人姓名：可能为空
                ##TODO

                # 经纪人联系方式
                try:
                    broker_contact = driver.find_element_by_xpath("//p[@class='content__aside__list--bottom oneline']").text
                except:
                    broker_contact = ''

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
                        print ("请手工检查租期：", rent_peroid, url)
                        rent_peroid_lower = rent_peroid
                        rent_peroid_upper = rent_peroid
                else:
                    rent_peroid_lower = rent_peroid
                    rent_peroid_upper = rent_peroid

                # 所在楼层
                house_floor = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[8]").text[3:].split('/')[0]

                # 总楼层
                house_total_floor = int(driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[8]").text[3:].split('/')[1].replace('层',''))

                # 车位
                parking = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[11]").text[3:]

                # 用电
                electricity_type = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[14]").text[3:]

                # 入住
                check_in = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[3]").text[3:]

                # 看房
                reservation = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[6]").text[3:]

                # 电梯
                lift = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[9]").text[3:]

                # 用水
                water = driver.find_element_by_xpath("//div[@class='content__article__info']/ul/li[12]").text[3:]

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

                # 地址和交通，地铁便利性
                ##TODO:地铁便利性的筛选标准，距任一地铁站的距离有小于1000m的
                accessibility_subway = 0
                try:
                    list_subways = []
                    for i in driver.find_elements_by_xpath("//div[@class='content__article__info4']/ul/li"):
                        subway_line = i.text[3:].split(' - ')[0]
                        subway_station = i.text.split(' - ')[1].split(' ')[0]
                        subway_station_distance = int(i.text.split(' - ')[1].split(' ')[1].split('m')[0])
                        list_subways.append([subway_line,subway_station,subway_station_distance])

                        if subway_station_distance < 1000:
                            accessibility_subway = 1
                    json_subways = json.dumps(list_subways, ensure_ascii=False)
                except:
                    print("地址和交通有未知错误：", url)
                    json_subways = ''

                # 小区最新成交
                try:
                    complex_deals = driver.find_element_by_xpath("//div[@class='table']").get_attribute('innerHTML')
                    table = BeautifulSoup(complex_deals, 'lxml')
                    record = []
                    # 表格内容
                    for tr in table.find_all("div", class_='tr')[1:]:
                        cols = tr.find_all("div", class_='td')
                        cols = [ele.text.strip() for ele in cols]
                        record.append([ele for ele in cols if ele])  # Get rid of empty values
                    complex_deals = pd.DataFrame(data=record, columns=['成交日期','居室','面积','租赁方式','出租价格']).to_json(orient='records', force_ascii=False)
                except:
                    print ("无小区最新成交信息：", url)
                    complex_deals = ''

                # 房源描述
                if len(driver.find_elements_by_xpath("//div[@class='content__article__info3 ']/ul/li/p")) > 2:
                    house_description = ''
                    print ("请调整子函数get_list_info的房源描述部分，有超过一条评论的情况需要全部考虑。（做成列表而不再是文本）", url)
                else:
                    try:
                        house_description = driver.find_element_by_xpath("//div[@class='content__article__info3 ']/ul/li/p[1]").text
                    except:
                        house_description = ''

                # 房源链接
                house_url = url

                # 城市
                city = driver.find_element_by_xpath("//div[@class='bread__nav w1150 bread__nav--empty']/p/a[1]").text[:-3]

                # 城区
                district = driver.find_element_by_xpath("//div[@class='bread__nav w1150 bread__nav--empty']/p/a[2]").text[:-2]

                # 商圈
                bizcircle = driver.find_element_by_xpath("//div[@class='bread__nav w1150 bread__nav--empty']/p/a[3]").text[:-2]

                # 小区名称
                complex = driver.find_element_by_xpath("//div[@class='bread__nav w1150 bread__nav--empty']/h1/a").text[:-2]

                # 小区链接
                complex_url = driver.find_element_by_xpath("//div[@class='bread__nav w1150 bread__nav--empty']/h1/a").get_attribute('href')

                # 每平米房价
                try:
                    house_price_unit = round(house_price/house_area, 2)
                except:
                    print('无法计算每平米房价：', url)
                    house_price_unit = ''

                # 经纪人品牌
                broker_brand = driver.find_element_by_xpath("//div[@class='content__aside fr']/ul[@class='content__aside__list']/li/p").text
                if ' 经纪人' in broker_brand:
                    broker_brand = broker_brand[:-4]
                if '管家' in broker_brand:
                    broker_brand = broker_brand[:-3]

                # 上下楼便利性：无障碍性，楼层与电梯的合成项
                accessibility_floor = 0
                if lift == '有':
                    accessibility_floor = 1
                elif lift == '无' and house_floor <= '3':
                    accessibility_floor = 1
                elif lift == 0 and house_floor == '低楼层':
                    accessibility_floor = 1
                else:
                    pass

                # 导出所有信息
                dict_single = {'类型':rent_type,'标题':title,'上架时间':time_listed,'编号':house_code,'信息卡照片':duty_img,'信息卡号':duty_id,
                              '营业执照':'','经纪备案':'','房源图片列表':json_house_imgs,'价格':house_price,'特色标签列表':json_house_tags,
                              '户型':house_type,'面积':house_area,'朝向':house_orient,'经纪人姓名':'','经纪人联系方式':broker_contact,
                              '最短租期':rent_peroid_lower,'最长租期':rent_peroid_upper,'所在楼层':house_floor,'总楼层':house_total_floor,
                              '车位':parking,'用电':electricity_type,'入住':check_in,'看房':reservation,'电梯':lift,'用水':water,'燃气':gas,
                              '电视':television, '冰箱':refrigerator,'洗衣机':washing_machine,'空调':air_conditioner,'热水器':water_heater,
                              '床':bed,'暖气':heating,'宽带':wifi,'衣柜':wardrobe,'天然气':natural_gas,'地址和交通':json_subways,
                              '小区最新成交':complex_deals,'房源描述':house_description,'房源链接':house_url,
                              '城市':city,'城区':district,'商圈':bizcircle,'小区名称':complex,'小区链接':complex_url,
                              '每平米房价':house_price_unit, '经纪人品牌':broker_brand, '上下楼便利性':accessibility_floor,
                              '地铁便利性':accessibility_subway}
                return dict_single

        def gen_json(table_dict, keyword):
            """
            保存字典为JSON文件，用于数据存储。
            :param table_dict: dict_all
            :param keyword: 筛选条件
            :return:
            """
            list_dic = []
            for i in list(table_dict.keys()):
                list_dic.append((i, table_dict[i]))
            dic = OrderedDict(list_dic)
            list_json = WriterJson().odict_to_json(dic)
            WriterJson().write_json(json_list=list_json, file_name=keyword+'.json')

        def main(driver, keyword):
            """
            主运行函数。
            :param driver:
            :param keyword: 筛选条件，用于命名JSON文件。
            :return: df
            """
            # 获取符合当前筛选条件的所有房源链接
            list_urls = get_list_urls(driver=driver)

            # 循环获取单房源信息并保存为df
            print("开始获取房源具体信息。")
            dict_all = {}
            list_sequence = 0
            df = pd.DataFrame()
            for url in tqdm(list_urls):
                if 'apartment' not in url:
                    try:
                        dict_single = get_list_info(driver=driver, url=url)
                        dict_all[list_sequence] = dict_single
                        df = df.append(pd.DataFrame(list(dict_all[list_sequence].items())).transpose(), ignore_index=True)
                        list_sequence += 1
                    except:
                        print("有未知报错，请检查:", url)
                        pass

            # 去除多余的表头
            ##TODO:加快表头的处理速度。
            df.drop_duplicates(inplace=True)
            df = df.reset_index()
            header = df.iloc[0]
            df = df[1:]
            df.columns = header

            # 保存列表为JSON或csv（默认）
            if export == 'csv':
                df.to_csv(keyword+'.csv', encoding='gb18030')
            elif export == 'json':
                gen_json(table_dict=dict_all, keyword=keyword)
            elif export is None:
                pass
            else:
                print("请选择正确的输出格式，支持'xlsx'和'json'。")
                pass

            driver.quit()
            return df

        self.driver.get(url)
        df = main(self.driver, keyword)
        return df

    def ke_scraper_bizcircles(self, url, keyword=None, export='csv'):
        """
        输入获取指定城市的商圈信息。贝壳网的租房和买房（新房/二手房）使用同一商圈信息。默认下爬取北京市。
        :return: 一个包含商圈信息的pandas.DataFrame
        """
        self.driver.get(url)

        df_bizcircles = pd.DataFrame(columns=['bizcircle_name', 'bizcircle_url', 'district'])

        for i in tqdm(range(len(self.driver.find_elements_by_xpath("//li[@data-type='district']")[1:]))):
            self.driver.find_element_by_xpath("//li[@data-type='district'][{}]".format(i+1)).click()

            # 获取指定城区的所有商圈
            df_bizcircle = pd.DataFrame(columns=['bizcircle_name', 'bizcircle_url', 'district'])

            for bizcircle in self.driver.find_elements_by_xpath("//li[@data-type='bizcircle']")[1:]:
                bizcircle_url = bizcircle.find_element_by_xpath(".//a").get_attribute('href')
                bizcircle_name = bizcircle.text.strip()
                df_bizcircle = df_bizcircle.append(
                    {'bizcircle_name': bizcircle_name, 'bizcircle_url': bizcircle_url}, ignore_index=True)

            df_bizcircle['district'] = self.driver.find_element_by_xpath("//li[@data-type='district'][{}+1]/a".format(i)).text
            df_bizcircles = df_bizcircles.append(df_bizcircle, ignore_index=True)

        # 保存列表为JSON或csv（默认）
        if export == 'csv':
            df_bizcircles.to_csv(keyword + '.csv', encoding='gb18030')
        elif export == 'json':
            df_bizcircles.to_json(keyword + '.json', force_ascii=False)
        elif export is None:
            pass
        else:
            print("请选择正确的输出格式，支持'xlsx'和'json'。")
            pass

        self.driver.quit()
        return df_bizcircles

    def ke_messenger(self, url, content):
        """
        输入指定房源信息页，输出指定文本内容到关于该房源的联系对话框。

        1, 锁定“在线咨询”按钮，并点击
        2. 跳转点击到对话框
        3. 输入指定文本内容
        :return:
        """
        #TODO:登录问题未解决，无法使用messenger。
        self.driver.get(url)
        time.sleep(5)
        print('开始1')
        self.driver.find_element_by_xpath("//*[@id='aside']/ul[2]/li/div[2]/span").click()
        # buttonx, buttony = pyautogui.locateCenterOnScreen('在线咨询.png')
        # pyautogui.click(buttonx, buttony)
        time.sleep(5)
        print('开始2')
        self.driver.find_element_by_xpath("/html/body/div[5]/div[1]/div[2]/div[2]/div[3]/div[1]/textarea").send_keys(content)


if __name__ == "__main__":
    # df_bizcircles = Ke(username='17810375258', password='abcd1234').ke_scraper_bizcircles(url='https://bj.zu.ke.com/zufang/', keyword='北京商圈', export='csv')
    df = Ke(username='17810375258', password='abcd1234').ke_scraper_rent(url='https://bj.zu.ke.com/zufang/sanlitun/l0', keyword='北京三里屯', export='csv')
    # driver = Ke(username='17810375258', password='abcd1234').ke_messenger(url='https://bj.zu.ke.com/zufang/BJ2221643218612142080.html?h=BJ2221643218612142080&t=default&click_position=0&unique_id=dd54f946-724f-49c2-8a0a-dff8f8844c8ezufangsanlitunrt200600000001l0l1l21558063862371', content='Hi')