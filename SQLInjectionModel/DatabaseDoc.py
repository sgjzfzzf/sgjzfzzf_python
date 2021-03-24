import sqlite3


class MyDB:
    def __init__(self):
        self.conPath = "mydb.db"
        self.tableName = "INFO"
        self.conn = sqlite3.connect(self.conPath)
        self.create_table()

    def __del__(self):
        self.close()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS {}(
                ID INT PRIMARY KEY,
                NAME VARCHAR(45) NOT NULL,
                PRI_KEY INT NOT NULL
            ) ;
        '''.format(self.tableName))

    def search(self, id=None, name=None):
        if id == None or name == None:
            return []
        else:
            sql = "SELECT ID,NAME,PRI_KEY FROM {} WHERE ID={} AND NAME='{}';".format(
                self.tableName, id, name)
            print(sql)
            return self.conn.execute(sql)
