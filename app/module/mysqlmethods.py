from mysql.connector import pooling
from dotenv import load_dotenv
import os, time

load_dotenv()


class Sqlmethod:
    def __init__(self):
        self.host = os.getenv("db_host")
        self.user = os.getenv("db_user")
        self.password = os.getenv("db_password")
        self.database = os.getenv("db_database")
        self.pool_name = "mypool"
        self.pool_size = 10
        self.connection_pool = pooling.MySQLConnectionPool(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            pool_name=self.pool_name,
            pool_size=self.pool_size,
        )

    # For CREATE, UPDATE, DELETE
    def cudData(self, query, value):
        try:
            connection_object = self.connection_pool.get_connection()
            cursor = connection_object.cursor()
            if type(value) == list:
                cursor.executemany(query, value)
            else:
                cursor.execute(query, value)
            connection_object.commit()
            # return {"ok": True}
        except Exception as error:
            self.recordError(str(error))
            # return {"error": str(error)}
        finally:
            if connection_object.is_connected():
                cursor.close()
                connection_object.close()

    # For SELECT
    def readData(self, query, value=None):
        try:
            connection_object = self.connection_pool.get_connection()
            cursor = connection_object.cursor()
            cursor.execute(query, value)
            sqlresult = cursor.fetchall()
            return sqlresult
        except Exception as error:
            self.recordError(str(error))
            return {"error": str(error)}
        finally:
            if connection_object.is_connected():
                cursor.close()
                connection_object.close()

    # For Table and Database
    def tableDBControl(self, query):
        try:
            connection_object = self.connection_pool.get_connection()
            cursor = connection_object.cursor()
            cursor.execute(query)
            # return {"ok": True}
        except Exception as error:
            self.recordError(str(error))
            # return {"error": str(error)}
        finally:
            if connection_object.is_connected():
                cursor.close()
                connection_object.close()

    def recordError(self, error):
        with open("errorinsql.txt", "a") as outfile:
            nowStruct = time.localtime(time.time())
            nowString = time.strftime("%a, %d %b %Y %H:%M:%S", nowStruct)
            errorStr = nowString + "\n" + error + "\n"
            outfile.writelines(errorStr)


# 操作mysql CRUD
mysql = Sqlmethod()
