from mysqlmethods import Sqlmethod
from motcapi import Auth
from requests import request
import time
from datetime import datetime
from math import floor

# 操作mysql CRUD; cudData(query, value) return {"ok":True}成功;
# readData(query, value=None) return 查詢資料 {"error"}錯誤
mysql = Sqlmethod()
# 建立簽章
motcAPI = Auth()

# 儲存本次公車服務起始時間、該車次buspass_id
busStartTime = dict()

req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeNearStop/City/Taipei?$select=PlateNumb%2C%20DutyStatus%2C%20RouteUID%2C%20Direction%2C%20StopUID%2C%20StopSequence%2C%20DutyStatus%2C%20A2EventType&$format=JSON"
response = request("get", req_url, headers = motcAPI.authHeader())
response = response.json()

# Insert data into table busonroute & buspassstop
insertBusonroute = []
insertBuspassstop = []
t1 = time.time()
for eachRow in response:
    # 當公車未在busStartTime dictionary內，且dutystatus != 2，以車牌當key新增當下時間；
    # 當dutystatus = 2，且公車在busStartTime dictionary內，將公車由dictionary移除
    if eachRow["DutyStatus"] != 2 and eachRow["PlateNumb"] not in busStartTime:
        busStartTime[eachRow["PlateNumb"]] = []
        busStartTime[eachRow["PlateNumb"]].append(floor(time.time()))
    elif eachRow["DutyStatus"] == 2 and eachRow["PlateNumb"] in busStartTime:
        busStartTime.pop(eachRow["PlateNumb"])
    # 整理要放進busonroute table的值
    tempTuple = (eachRow["PlateNumb"], eachRow["RouteUID"], eachRow["Direction"], eachRow["StopUID"], \
        eachRow["StopSequence"], eachRow["DutyStatus"], eachRow["A2EventType"])
    insertBusonroute.append(tempTuple)
    # 整理要放進buspassstop的值
    # 針對營運中公車(有在busStartTime dictionary內)，確認該公車在這次營運下，現在的buspass_id與dictionary內是否相同，
    # 相同 更新passtime；不同 相關資料INSERT INTO busspassstop
    if eachRow["PlateNumb"] in busStartTime:
        selectSql = "SELECT buspass_id FROM buspassstop WHERE starttime = %s AND platenumb = %s AND stopUID = %s"
        selectValue = (busStartTime[eachRow["PlateNumb"]], eachRow["PlateNumb"], eachRow["StopUID"])
        checkresult = mysql.readData(selectSql, selectValue)
        if len(checkresult) == 0:
            useSql = "INSERT INTO buspassstop (buspass_id, platenumb, routeUID, direction, stopUID, passtime, hour, \
                starttime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            useValue = (eachRow["PlateNumb"] + str(busStartTime[eachRow["PlateNumb"]]) + eachRow["StopUID"], \
                eachRow["PlateNumb"], eachRow["RouteUID"], eachRow["Direction"], eachRow["StopUID"], floor(time.time()), \
                datetime.now().hour, busStartTime[eachRow["PlateNumb"]])
        else:
            useSql = "UPDATE buspassstop SET passtime = %s, hour = %s WHERE starttime = %s AND platenumb = %s AND stopUID = %s"
            useValue = (floor(time.time()), datetime.now().hour, busStartTime[eachRow["PlateNumb"]], eachRow["PlateNumb"], eachRow["StopUID"])
        mysql.cudData(useSql, useValue)
insertSqlonroute = "INSERT INTO busonroute (platenumb, routeUID, direction, stopUID, sequence, dutystatus, eventtype) \
    VALUES (%s, %s, %s, %s, %s, %s, %s)"
# 將上次表格資料清空後新增資料
mysql.tableDBControl("TRUNCATE busonroute")
t3 = time.time()
mysql.cudData(insertSqlonroute, insertBusonroute)


t2 = time.time()
print (t2-t1)
print (t2-t3)
