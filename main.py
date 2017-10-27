import api.crawl.yahoo as cralwer
import api.transport.csv2db as csv2db
import api.genf as genf

import os
from gevent import monkey
import gevent
import shutil
import time
from datetime import date


# get unix time
def get_unix_time(yyyy, mm, dd) :
    d = date(yyyy,mm,dd)
    unixtime = time.mktime(d.timetuple())
    return unixtime

# https://finance.yahoo.com/quote/IBM/
def crawl(tkr='') :

    yahoo = cralwer.CrawlYahooTkr()

    if tkr == '' :

        rootdir = os.path.dirname(os.path.abspath(__file__))
        fname = rootdir + '\\data\\input\\tkrlist_small.txt'
        content = []
        with open(fname) as f :
            content = [x.strip() for x in f.readlines()]

        #yahoo.download_csv('^GSPC')
        #yahoo.download_csv('AMZN')

        monkey.patch_all()
        threads = [gevent.spawn(yahoo.download_csv, tkr) for tkr in content]
        gevent.joinall(threads)
    else :
        yahoo.download_csv(tkr)

def csv_to_db(tkrhdir) :
    csv2db.copy2db(tkrhdir,'postgres://tkrapi:tkrapi@127.0.0.1/tkrapi')








#crawl()
#crawl('BAC')
#crawl('DIA')

# csv to database
# 위에서 수집한 csv 파일을 postgre database로 옮기는 함수
csv_to_db('D:\\dev\\workspace\\stock-analysis\\data\\tkrcsv')

# generate features
genf.genf('postgres://tkrapi:tkrapi@127.0.0.1/tkrapi')


# learn, predict
import api.kerastkr as kerastkr
# out_df = kerastkr.learn_predict_kerasnn('^GSPC', 6, '2017-08')
# print(out_df)

# out_df = kerastkr.load_predict_keraslinear()
# print(out_df)

'bye'

