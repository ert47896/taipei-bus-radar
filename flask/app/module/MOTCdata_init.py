from mysqlmethods import mysql
from tdxapi import get_data


# Insert data into table stationinfo and stopofstation
req_url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Station/City/Taipei?$select=StationUID%2C%20StationName%2C%20Stops%2C%20StationAddress%2C%20StationPosition&$format=JSON"
response = get_data(req_url)
response = response.json()
insertStationinfo = []
insertStopofstation = []
for eachRow in response:
    if "En" not in eachRow["Stops"][0]["StopName"]:
        ename = "無資料"
    else:
        ename = eachRow["Stops"][0]["StopName"]["En"]
    tempTuple = (
        eachRow["StationUID"],
        eachRow["StationName"]["Zh_tw"],
        ename,
        eachRow["StationAddress"],
        eachRow["StationPosition"]["PositionLon"],
        eachRow["StationPosition"]["PositionLat"],
    )
    insertStationinfo.append(tempTuple)
    for eachStop in eachRow["Stops"]:
        tempTuple = (eachStop["StopUID"], eachRow["StationUID"])
        insertStopofstation.append(tempTuple)
# ST_SRID(lon, lat)
insertSqlStationinfo = "INSERT INTO stationinfo (stationUID, stopname_tw, stopname_en, address, coordinate) VALUES \
    (%s, %s, %s, %s, ST_SRID(POINT(%s, %s), 3826))"
insertSqlStopofstation = (
    "INSERT INTO stopofstation (stopUID, stationUID) VALUES (%s, %s)"
)
mysql.cudData(insertSqlStationinfo, insertStationinfo)
mysql.cudData(insertSqlStopofstation, insertStopofstation)

# Insert data into table operator
req_url = "https://tdx.transportdata.tw/api/basic/v2/Bus/Operator/City/Taipei?$select=OperatorID%2C%20OperatorName%2C%20OperatorPhone%2C%20OperatorUrl&$format=JSON"
response = get_data(req_url)
response = response.json()
insertValue = []
for eachRow in response:
    tempTuple = (
        eachRow["OperatorID"],
        eachRow["OperatorName"]["Zh_tw"],
        eachRow["OperatorName"]["En"],
        eachRow["OperatorPhone"],
        eachRow["OperatorUrl"],
    )
    insertValue.append(tempTuple)
insertSql = "INSERT INTO operator (operatorID, oname_tw, oname_en, phone, webpage) VALUES \
    (%s, %s, %s, %s, %s)"
mysql.cudData(insertSql, insertValue)

# Insert data into table busroute and operatorofroute
# data in Route API
req_url_route = "https://tdx.transportdata.tw/api/basic/v2/Bus/Route/City/Taipei?$select=RouteUID%2C%20Operators%2C%20RouteName%2C%20DepartureStopNameZh%2C%20DepartureStopNameEn%2C%20DestinationStopNameZh%2C%20DestinationStopNameEn%2C%20RouteMapImageUrl&$format=JSON"
response = get_data(req_url_route)
responseRoute = response.json()
insertBusroute = []
insertOperatorofroute = []
for eachRow in responseRoute:
    for operator in eachRow["Operators"]:
        tempTuple = (eachRow["RouteUID"], operator["OperatorID"])
        insertOperatorofroute.append(tempTuple)
    # some route didn't provide english name of departure stop / destination stop
    if "DepartureStopNameEn" not in eachRow:
        eachRow["DepartureStopNameEn"] = "未提供"
        eachRow["DestinationStopNameEn"] = "未提供"
    tempTuple = (
        eachRow["RouteUID"],
        eachRow["RouteName"]["Zh_tw"],
        eachRow["RouteName"]["En"],
        eachRow["DepartureStopNameZh"],
        eachRow["DepartureStopNameEn"],
        eachRow["DestinationStopNameZh"],
        eachRow["DestinationStopNameEn"],
        eachRow["RouteMapImageUrl"],
    )
    insertBusroute.append(tempTuple)
insertSqlBusroute = "INSERT INTO busroute (routeUID, routename_tw, routename_en, depname_tw, depname_en, \
    destname_tw, destname_en, routeimgurl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
insertSqlOperatorofroute = (
    "INSERT INTO operatorofroute (routeUID, operatorID) VALUES (%s, %s)"
)
mysql.cudData(insertSqlBusroute, insertBusroute)
mysql.cudData(insertSqlOperatorofroute, insertOperatorofroute)

# data in Shape API
req_url_shape = "https://tdx.transportdata.tw/api/basic/v2/Bus/Shape/City/Taipei?$select=Geometry%2C%20RouteUID&$format=JSON"
response = get_data(req_url_shape)
responseShape = response.json()
insertValue = []
for eachRow in responseShape:
    if "MULTILINESTRING" in eachRow["Geometry"]:
        eachRow["Geometry"] = None
    tempTuple = (eachRow["Geometry"], eachRow["RouteUID"])
    insertValue.append(tempTuple)
insertSql = "UPDATE busroute SET linestrings = ST_GeomFromText(%s) WHERE routeUID = %s"
mysql.cudData(insertSql, insertValue)

# Insert data into table stopofroute
req_url = "https://tdx.transportdata.tw/api/basic/v2/Bus/DisplayStopOfRoute/City/Taipei?$select=RouteUID%2C%20Direction%2C%20Stops&$format=JSON"
response = get_data(req_url)
response = response.json()
insertValue = []
for eachRow in response:
    for eachStop in eachRow["Stops"]:
        tempTuple = (
            eachRow["RouteUID"],
            eachRow["Direction"],
            eachStop["StopUID"],
            eachStop["StopSequence"],
        )
        insertValue.append(tempTuple)
insertSql = "INSERT INTO stopofroute (routeUID, direction, stopUID, stopsequence) VALUES (%s, %s, %s, %s)"
mysql.cudData(insertSql, insertValue)
