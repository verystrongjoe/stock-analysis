import os
from sqlalchemy import create_engine

class Postgre :

    db_url = 'postgres://tkrapi:tkrapi@127.0.0.1/tkrapi'
    conn = None

    def __init__(self, dburl):
        self.db_url = dburl
        self.conn = create_engine(self.db_url).connect()

    def execute_select_sql(self, sql, param=[]):
        return self.conn.execute(sql, param)

    # def execute_and_check_result(self, sql):
    #     result = self.conn.execute(sql)
    #
    #     print("#todo : debug and check how to generalize the output with same source code")

        # for row in result:
        #     print(row['tkr'], row['csvh'].split(',')[-2:])