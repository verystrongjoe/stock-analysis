import pymongo

connection = pymongo.MongoClient("mongodb://localhost")
stock = connection.stock

table = stock.tkrprices
