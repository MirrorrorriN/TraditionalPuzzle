# -*- coding: utf-8 -*-
import scrapy
import re
from traditionalPuzzle.items import TraditionalpuzzleItem

# 解决 Python2.x版本中乱码问题，Python3.x 版本中不需要
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class RiddleSpider(scrapy.Spider):
    name = "riddle"
    allowed_domains = ["www.cmiyu.com"]
    start_urls = (
        'http://www.cmiyu.com/zmmy/926.html',
    )

    def getChineseRegexExtraction(self, content,keyword):
        pattern=keyword
        pattern= pattern.decode('utf-8')
        pattern=re.compile(pattern)
        result=re.sub(pattern,'',content,0)
        return result
    
    def parse(self, response):
        filename = "riddle.html"
        output=open(filename,'w+')
        
        
        # context = response.xpath('/html/body/div[@class="content"]/div[@class="left"]/div/div[@class="list"]/ul/li') 
        context = response.xpath('/html/body/div[@class="content"]/div[@class="left"]/div[@class="top"]') 

        #extract unicode编码？
        explanation=context.xpath('./div[@class="zy"]/p/text()').extract_first()
        #部分谜语没有解析
        if explanation:
            explanation=self.getChineseRegexExtraction(explanation,'小贴士：')
            print explanation
        else:
            explanation=''
        
        riddle = context.xpath('./div[@class="md"]')
        question=riddle.xpath('./h3[1]/text()').extract_first()
        answer=riddle.xpath('./h3[2]/text()').extract_first()
        question=self.getChineseRegexExtraction(question,'谜面：')
        strArray=question.split("（")
        #特殊情况暂不处理
        if len(strArray)==2:
            question=strArray[0]
            hint="（"+strArray[1]
            answer=self.getChineseRegexExtraction(answer,'谜底：')
            print question,hint,answer
        
            item=TraditionalpuzzleItem()
            item['question']=question
            item['hint']=hint
            item['answer']=answer
            item['explanation']=explanation
            yield item
        
        #逆序每次抓取一篇，因为网站更新从头开始，方便获取最新数据
        url = context.xpath('./div[@class="page"]/ul/li[1]/a/@href').extract_first()
        print url
        if url :
            #将信息组合成下一页的url
            baseUrl='http://www.cmiyu.com'
            page = baseUrl + url
            #返回url
            yield scrapy.Request(page, callback=self.parse)
        output.close()
        pass