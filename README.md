# Ke
贝壳网爬虫API，一行代码将指定筛选条件的全量数据保存为JSON/csv。

## 安装
`pip install ke`

## 入门
请打开`test.ipynb`查看入门指南。

## 租房
```python
from ke import Ke
df = Ke(url='https://bj.zu.ke.com/zufang/dongcheng/rt200600000001rp2rp3rp4/#contentList',
            keyword='北京东城整租').ke_scraper_rent(export='json')
```
输入待爬取页面和保存文件名称，运行后将指定筛选条件下的爬取结果返回为pandas.DataFrame并保存为JSON文件（请参考`全量.json`）。也支持保存为'csv'格式或不保存（None）。

