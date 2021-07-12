from mysqlmethods import Sqlmethod
from motcapi import Auth
from requests import request
import time
# 操作mysql CRUD; cudData(query, value) return {"ok":True}成功;
# readData(query, value=None) return 查詢資料 {"error"}錯誤
mysql = Sqlmethod()
# 建立簽章
motcAPI = Auth()

# Insert data into table busvehicle
req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/Vehicle/City/Taipei?$select=PlateNumb%2C%20VehicleType&$format=JSON"
response = request("get", req_url, headers = motcAPI.authHeader())
response = response.json()
insertValue = []
# 儲存車牌以比對避免重覆
temp = []
for eachRow in response:
    if eachRow["PlateNumb"] in temp:
        continue
    tempTuple = (eachRow["PlateNumb"], eachRow["VehicleType"])
    insertValue.append(tempTuple)
    temp.append(eachRow["PlateNumb"])
insertSql = "INSERT INTO busvehicle (platenumb, vehicletype) VALUES (%s, %s)"
mysql.cudData(insertSql, insertValue)

# Insert data into table stationinfo and stopofstation
req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/Station/City/Taipei?$select=StationUID%2C%20StationName%2C%20Stops%2C%20StationAddress%2C%20StationPosition&$format=JSON"
response = request("get", req_url, headers = motcAPI.authHeader())
response = response.json()
insertStationinfo = []
insertStopofstation = []
for eachRow in response:
    tempTuple = (eachRow["StationUID"], eachRow["StationName"]["Zh_tw"], eachRow["Stops"][0]["StopName"]["En"], \
        eachRow["StationAddress"], eachRow["StationPosition"]["PositionLat"], eachRow["StationPosition"]["PositionLon"])
    insertStationinfo.append(tempTuple)
    for eachStop in eachRow["Stops"]:
        tempTuple = (eachStop["StopUID"], eachRow["StationUID"])
        insertStopofstation.append(tempTuple)
insertSqlStationinfo = "INSERT INTO stationinfo (stationUID, stopname_tw, stopname_en, address, coordinate) VALUES \
    (%s, %s, %s, %s, POINT(%s, %s))"
insertSqlStopofstation = "INSERT INTO stopofstation (stopUID, stationUID) VALUES (%s, %s)"
mysql.cudData(insertSqlStationinfo, insertStationinfo)
mysql.cudData(insertSqlStopofstation, insertStopofstation)

# Insert data into table operator
req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/Operator/City/Taipei?$select=OperatorID%2C%20OperatorName%2C%20OperatorPhone%2C%20OperatorUrl&$format=JSON"
response = request("get", req_url, headers = motcAPI.authHeader())
response = response.json()
insertValue = []
for eachRow in response:
    tempTuple = (eachRow["OperatorID"], eachRow["OperatorName"]["Zh_tw"], eachRow["OperatorName"]["En"], \
        eachRow["OperatorPhone"], eachRow["OperatorUrl"])
    insertValue.append(tempTuple)
insertSql = "INSERT INTO operator (operatorID, oname_tw, oname_en, phone, webpage) VALUES \
    (%s, %s, %s, %s, %s)"
mysql.cudData(insertSql, insertValue)

# Insert data into table busroute and operatorofroute
# data in Route API
req_url_route = "https://ptx.transportdata.tw/MOTC/v2/Bus/Route/City/Taipei?$select=RouteUID%2C%20Operators%2C%20RouteName%2C%20DepartureStopNameZh%2C%20DepartureStopNameEn%2C%20DestinationStopNameZh%2C%20DestinationStopNameEn%2C%20RouteMapImageUrl&$format=JSON"
response = request("get", req_url_route, headers = motcAPI.authHeader())
responseRoute = response.json()
insertBusroute = []
insertOperatorofroute = []
t1 = time.time()
for eachRow in responseRoute:
    for operator in eachRow["Operators"]:
        tempTuple = (eachRow["RouteUID"], operator["OperatorID"])
        insertOperatorofroute.append(tempTuple)
    tempTuple = (eachRow["RouteUID"], eachRow["RouteName"]["Zh_tw"], eachRow["RouteName"]["En"], eachRow["DepartureStopNameZh"], \
        eachRow["DepartureStopNameEn"], eachRow["DestinationStopNameZh"], eachRow["DestinationStopNameEn"], \
        eachRow["RouteMapImageUrl"])
    insertBusroute.append(tempTuple)
insertSqlBusroute = "INSERT INTO busroute (routeUID, routename_tw, routename_en, depname_tw, depname_en, \
    destname_tw, destname_en, routeimgurl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
insertSqlOperatorofroute = "INSERT INTO operatorofroute (routeUID, operatorID) VALUES (%s, %s)"
mysql.cudData(insertSqlBusroute, insertBusroute)
mysql.cudData(insertSqlOperatorofroute, insertOperatorofroute)
# data in Shape API
req_url_shape = "https://ptx.transportdata.tw/MOTC/v2/Bus/Shape/City/Taipei?$select=Geometry%2C%20RouteUID&$format=JSON"
response = request("get", req_url_shape, headers = motcAPI.authHeader())
responseShape = response.json()
insertValue = []
for eachRow in responseShape:
    tempTuple = (eachRow["Geometry"], eachRow["RouteUID"])
    insertValue.append(tempTuple)
insertSql = "UPDATE busroute SET linestrings = ST_LineStringFromText(%s) WHERE routeUID = %s"
mysql.cudData(insertSql, insertValue)
# # data in Shape API(舊的)
# req_url_shape = "https://ptx.transportdata.tw/MOTC/v2/Bus/Shape/City/Taipei?$format=JSON"
# response = request("get", req_url_shape, headers = motcAPI.authHeader())
# responseShape = response.json()
# insertValue = []
# # 預留資料供Route API及DisplayStopOfRoute判斷該RouteUID是否有路線線型資料
# routewithLine = []
# for eachRow in responseShape:
#     tempTuple = (eachRow["RouteUID"], eachRow["RouteName"]["Zh_tw"], eachRow["RouteName"]["En"], \
#         eachRow["Geometry"])
#     insertValue.append(tempTuple)
#     routewithLine.append(eachRow["RouteUID"])
# insertSql = "INSERT INTO busroute (routeUID, routename_tw, routename_en, linestrings) VALUES \
#     (%s, %s, %s, ST_LineStringFromText(%s))"
# mysql.cudData(insertSql, insertValue)
# # data in Route API
# req_url_route = "https://ptx.transportdata.tw/MOTC/v2/Bus/Route/City/Taipei?$format=JSON"
# response = request("get", req_url_route, headers = motcAPI.authHeader())
# responseRoute = response.json()
# insertBusroute = []
# insertOperatorofroute = []
# for eachRow in responseRoute:
#     for operator in eachRow["Operators"]:
#         if eachRow["RouteUID"] in routewithLine:            
#             tempTuple = (eachRow["RouteUID"], operator["OperatorID"])
#             insertOperatorofroute.append(tempTuple)
#     tempTuple = (eachRow["DepartureStopNameZh"], eachRow["DepartureStopNameEn"], eachRow["DestinationStopNameZh"], \
#         eachRow["DestinationStopNameEn"], eachRow["RouteMapImageUrl"], eachRow["RouteUID"])
#     insertBusroute.append(tempTuple)
# insertSqlBusroute = "UPDATE busroute SET depname_tw = %s, depname_en = %s, destname_tw = %s, destname_en = %s, \
#     routeimgurl = %s WHERE routeUID = %s"
# insertSqlOperatorofroute = "INSERT INTO operatorofroute (routeUID, operatorID) VALUES (%s, %s)"
# mysql.cudData(insertSqlBusroute, insertBusroute)
# mysql.cudData(insertSqlOperatorofroute, insertOperatorofroute)

# Insert data into table stopofroute
req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/DisplayStopOfRoute/City/Taipei?$select=RouteUID%2C%20Direction%2C%20Stops&$format=JSON"
response = request("get", req_url, headers = motcAPI.authHeader())
response = response.json()
insertValue = []
for eachRow in response:
    for eachStop in eachRow["Stops"]:
        tempTuple = (eachRow["RouteUID"], eachRow["Direction"], eachStop["StopUID"], eachStop["StopSequence"])
        insertValue.append(tempTuple)
insertSql = "INSERT INTO stopofroute (routeUID, direction, stopUID, stopsequence) VALUES (%s, %s, %s, %s)"
mysql.cudData(insertSql, insertValue)


t2 = time.time()
print (t2-t1)