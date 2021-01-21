import phoenixdb
import os

class Db:
    def __init__(self):
        opts = {}
        opts['authentication'] = 'BASIC'
        opts['avatica_user'] = os.environ["WORKLOAD_USER"]
        opts['avatica_password'] = os.environ["WORKLOAD_PASSWORD"]
        database_url = os.environ["OPDB_ENDPOINT"]
        self.TABLENAME = "stocks_feed"
        self.conn = phoenixdb.connect(database_url, autocommit=True,**opts)
        self.curs = self.conn.cursor()

    def create_stock_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS """+self.TABLENAME+""" (
        symbol VARCHAR NOT NULL,
        datet VARCHAR NOT NULL,
        open_val FLOAT,
        high_val FLOAT,
        low_val  FLOAT,
        close_val FLOAT,
        volume FLOAT CONSTRAINT my_pk PRIMARY KEY (symbol,datet))
        """
        
        #print(query)
        self.curs.execute(query)
    
    def upsert(self, data):

        sql = "upsert into " + self.TABLENAME + \
            " (symbol ,datet,open_val,high_val,low_val,close_val,volume) \
             values (?,?,?,?,?,?,?)"
        #print(data)
        self.curs.executemany(sql,data)
        self.conn.commit()
    
    def get_data(self, symbol):
      query = f"SELECT open_val,high_val,low_val,close_val,volume " \
            f"from (select * from {self.TABLENAME} where symbol  = ? order by datet desc) as t"
      #print(query)
      self.curs.execute(query,[symbol])
      rows = self.curs.fetchall()
      return rows
    
    def get_data_stat(self, symbol):
      query = f"select count(*) total_records from {self.TABLENAME} where symbol  = ?"
      self.curs.execute(query,[symbol])
      count = self.curs.fetchone()[0]
      print (f"Total records for {symbol} is {count}")
      
    def delete_data(self, symbol):
      sql = "delete from " + self.TABLENAME + \
            " where symbol = ?"
      self.curs.execute(sql,[symbol])
      self.conn.commit()
      
    def drop_stocks_table(self):
        query = "DROP TABLE IF EXISTS "+self.TABLENAME
        self.curs.execute(query)