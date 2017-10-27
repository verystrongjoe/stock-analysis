import datetime, time

class Stock :

    def set_basic_info(self, startDate, endDate) :
        self.startDate = startDate
        self.endDate = endDate

    def set_basic_info_with_oneDate(self, date) :
        if self.startDate is None :
            self.startDate = date

        self.endDate = date

    def print_basic_info(self):
        print("---------------------")
        print("startDate : " , self.startDate)
        print("endDate : ", self.endDate)
        print("---------------------")

stock1 = Stock()
stock1.set_basic_info("a","b")