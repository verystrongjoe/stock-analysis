from bs4 import BeautifulSoup

import requests
import urllib
import datetime, time
from prettytable import PrettyTable
import logging

from Domain import Stock

## resilience 주식의 회복 탄력성을 계산해주는 로직
class Resilience :

    # 1~ 513 페이지를 네비게이션하면서 1996년도에서 오늘까지의 일일 종가 데이터를 가져온다.
    domainUrl = 'http://finance.naver.com/item/sise_day.nhn?'
    pageUrl = '&page='
    codeUrl = "&code="

    threshold_DroppedPersent = 5
    threshold_MaxDayToCountupRecoveryTime = 1000

    stock = Stock.Stock()

    def main(self, code):
        prices = Resilience.getPricesFromWeb(self, code)
        dropPrices = Resilience.getDropBadlyList(self,prices)
        dropPrices = Resilience.calculateDaysToBeRecovered(self,prices,dropPrices)
        Resilience.printRecoveryReport(self,dropPrices)

        newsList = Resilience.getNewsList(self,code)
        dropPrices = Resilience.appendRelatedNewsOnDroppedDay(self,dropPrices,newsList)
        Resilience.printResultWithNews(self,dropPrices)


    def getLastPageIdx(self, url, code):
        source_code = requests.get(url, timeout=None)
        soup = BeautifulSoup(source_code.text, 'lxml')
        tableSoup = soup.find('table', attrs={'class', 'Nnavi'})
        lastPageSoup = tableSoup.find('td', attrs={'class', 'pgRR'})

        lastpageUrl = lastPageSoup.a['href'][lastPageSoup.a['href'].find("page=")+5:]
        logging.debug('lastpageUrl is %s', lastpageUrl)
        #print('lastpageUrl is %s', lastpageUrl)

        return int(lastpageUrl)



    def getFirstDateinPage(self, code, domainUrl, page):
        domainUrl = Resilience.domainUrl + str(Resilience.codeUrl) + "code=" + code + str(Resilience.pageUrl) + page
        source_code = requests.get(domainUrl, timeout=None)
        soup = BeautifulSoup(source_code.text, 'lxml')
        tableSoup = soup.find('table', attrs={'class', 'type2'})
        trSoup = tableSoup.find_all('tr')

        for tr in trSoup:
            i = i + 1
            if i > 2 and i < 16 and i <= len(tr):
                if i == 8 or i == 9 or i == 10:
                    continue
                j = 0


                for td in tr:

                    j = j + 1
                    if j == 2:
                        date_str = str(td.span.text)
                        date_str = date_str.replace(".", "")
                        resultDate = datetime.date(int(date_str[0:4]), int(date_str[4:6]), int(date_str[6:8]))
                        break
            break
        return resultDate


    def getPricesFromWeb(self, code):

        # last page 구하는 로직
        url = Resilience.domainUrl + Resilience.codeUrl + code + str(Resilience.pageUrl) + "1"
        last_page_index = Resilience.getLastPageIdx(self, url, code)

        list = []

        for page in range(1, last_page_index):
            url = Resilience.domainUrl + Resilience.codeUrl +  code + str(Resilience.pageUrl) + str(page)
            source_code = requests.get(url, timeout=None)
            soup = BeautifulSoup(source_code.text, 'lxml')
            tableSoup = soup.find('table', attrs={'class', 'type2'})
            trSoup = tableSoup.find_all('tr')

            i = 0
            rowcount = 0;

            for tr in trSoup:
                i = i + 1
                if i > 2 and i < 16 and i <= len(tr):
                    if i == 8 or i == 9 or i == 10:
                        continue
                    j = 0
                    dic = {}

                    for td in tr:

                        j = j + 1
                        if j == 2:
                            date_str = str(td.span.text)
                            date_str = date_str.replace(".", "")
                            dic['date'] = datetime.date(int(date_str[0:4]), int(date_str[4:6]), int(date_str[6:8]))

                            Resilience.stock.set_basic_info_with_oneDate((dic['date']))

                        if j == 4:
                            price = str(td.span.text)
                            dic['price'] = int(price.replace(',', ''))
                        if j == 6:
                            change = str(td.span.text).strip()
                            if change != '0':
                                if td.img['src'].endswith('ico_up.gif') or td.img['src'].endswith('ico_up2.gif'):
                                    dic['change'] = int(change.replace(',', ''))
                                else:
                                    dic['change'] = -1 * int(change.replace(',', ''))
                            else:
                                dic['change'] = 0
                    list.append(dic)
        return list


    def getDropBadlyList(self, list):
        # 하루 등락률이 10프로 하락하는 지점을 찾는다. 하락을 했다면 그날의 시가를 가지고 향후 언제 그 가격을 넘어서는지를 찾을 것이다.
        # 전날 종가를 기준으로 등락률을 매기는게 맞는데 그냥 당일 종가와 등락 가격을 가지고 퍼센티지를 계산함.

        drop_badly_list = []
        for day in list :
            #print(day['date'] +  " : " + str(day['price']) + " : " + str(day['change']))
            percent = ( day['price'] + day['change'] ) / day['price']  * 100 - 100
            #print(day['date'] + " : " + str(percent))
            if percent < -1 * Resilience.threshold_DroppedPersent :
                drop_badly_list.append(day)

        # 그래서 우선 list를 filter해서 가지고 있고 그 시가를 가지고 있는 list를 만들 것이다. 그리고 이 filtered_list를 가지고 다시 원래의 list
        return drop_badly_list

    # 우선 특정 % 이상 떨어진 일자들을 얻고 각각 일자에 대해 전날 종가 가격으로의 회복 기간이 얼마 소요되었는지 하고 그것에 대한 평균도 구하도록 한다.
    # threshold 한계값 정해서 이 값을 넘을 경우는 실제 계산에서 배제를 하도록 한다. : 추가 기능
    def calculateDaysToBeRecovered(self, list, drop_badly_list):

        # 날짜 오름차순으로 변경
        list.reverse()

        recovery = []

        for drop_day in drop_badly_list:
            change = drop_day['change']
            yesterdayPrice = drop_day['price']
            d = drop_day['date']

            counting = 0
            isCounting = False
            element = {}

            for day in list:

                if day['date'] == d:
                    isCounting = True
                    yesterdayPrice -= change
                    theDay = d

                if isCounting:
                    if yesterdayPrice < day['price']:
                        break
                    else:
                        counting = counting + 1
                        # print(day['date'],day['price'])∂

            element['theDay'] = theDay
            element['counting'] = counting
            element['yesterdayPrice'] = yesterdayPrice

            recovery.append(element)
        return recovery

    def printRecoveryReport(self, recovery):

        t = PrettyTable(['5% 이상 떨어진 일자','회복하는데 걸린 일수', '회복해야하는 주가'])

        for ele in recovery:
            t.add_row([ele['theDay'], ele['counting'], ele['yesterdayPrice']])

        print(t)

        # for ele in recovery :
        #     print('----------------------------')
        #     print('5% 이상 떨어진 일자 : ',  ele['theDay'])
        #     print('회복하는데 걸린 일수 : ', ele['counting'])
        #     print('회복해야하는 주가 : ', ele['yesterdayPrice'])

        sum = 0
        for ele in recovery :
            sum = sum + ele['counting']
        print('The average of days to recover is ' , sum/len(recovery))

    def getNewsList(self, code):

        # 그다음 이시기에 어떤 뉴스가 있었는지를 찾기 위해서 네이버 증권의 뉴스데이터를 이용한다.
        news_domain_url = 'http://finance.naver.com/item/news_news.nhn?'

        source_code = requests.get(news_domain_url+Resilience.codeUrl+code, timeout=None)
        soup = BeautifulSoup(source_code.text,  'lxml')

        tableSoup = soup.find('table', attrs={'class', 'Nnavi'} )
        td = tableSoup.find('td', attrs={'class','pgRR'}).a['href']
        last_page_index = int(td[td.index('page=') + 5:])

        #last_page_index = 300

        # TODO : 여기에 이분탐색을 하는 로직이 들어가야함 왼쪽과 오른쪽 끝을 가르키는 포인터를 두고 계속 찾아갈수 있게 로직 필요. 왜냐. 너무 오래 걸림 ㅠㅠ
        """
        1. get a total page number substracting the index of first page from index of last page
        2. get a start date and a last date
        3. get the period between the start date and the last date
        4. divide a total page into the period
        5. using the result of 4, we can estimate of the page Index having the news of the date


        1. start = 1,  mid = pages / 2 , end = lastPageId
        2. start ~ mid / mid ~ end
        3.
        """

        news_list = []

        firstIdx = 1
        midIdx = last_page_index / 2
        endIdx = last_page_index

        while True :
            firstDate = Resilience.getFirstDateinPage(code, news_domain_url, firstIdx)
            midDate = Resilience.getFirstDateinPage(code, news_domain_url, midIdx)
            firstDate = Resilience.getFirstDateinPage(code, news_domain_url, endIdx)
            break

        for page in range(1,last_page_index) :
        # for page in range(600, 900):
            url = news_domain_url + Resilience.pageUrl + str(page)
            source_code = requests.get(url, timeout=None)
            soup = BeautifulSoup(source_code.text, 'lxml')

            newsTabelSoup = soup.find('table', attrs={'class', 'type2'})
            trSoup = newsTabelSoup.find_all('tr')

            i = 0
            rowcount = 0;

            for tr in trSoup:
                i = i + 1
                if i > 2 and i < 16:
                    if i == 8 or i == 9:
                        continue
                    j = 0
                    dic = {}

                    for td in tr:
                        j = j + 1
                        if j == 2:
                            strDate = str(td.span.text)
                            # print(strDate)
                            yyyy = int(strDate[0:4])
                            mm = int(strDate[5:7])
                            dd = int(strDate[8:10])

                            # 나중에 시간이 오후 3시 30분 이후에 있는건 제외를 하자. 다음날 영향 변수
                            hh = int(strDate[11:13])
                            minutes = int(strDate[14:16])

                            # dic['date'] = str(td.span.text)
                            dic['date'] = datetime.date(int(yyyy), int(mm), int(dd))

                        if j == 4:
                            dic['title'] = td.a.text
                        if j == 6:
                            dic['publish'] = td.text
                    news_list.append(dic)
        return news_list

    def appendRelatedNewsOnDroppedDay(self, recovery, news_list):

        for recv in recovery:
            d = recv['theDay']
            news_list2 = []

            for news in news_list:
                if news.get('date') == d:
                    #            print(news['title'])
                    news_list2.append(news['title'])

            recv['news_list'] = news_list2
        return recovery

    def printResultWithNews(self, recovery):

        import pprint
        pprint.pprint(recovery)

        #print(recovery)
        # t = PrettyTable(['Date','Original Price', 'DaysToBeRecovered', 'NewsList'])
        #
        # for recv in recovery:
        #     t.add_row([recv['theDay'], recv['yesterdayPrice'], recv['counting'], recv['news_list']])
        #
        # print(t)