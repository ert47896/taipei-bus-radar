from flask import Blueprint, jsonify
from module.mysqlmethods import Sqlmethod
from module.motcapi import Auth
from module.cache import cache
from requests import request
import time

buslocationApi = Blueprint("buslocationApi", __name__)

# 操作mysql CRUD; cudData(query, value) return {"ok":True}成功;
# readData(query, value=None) return 查詢資料 {"error"}錯誤
mysql = Sqlmethod()
# 建立簽章
motcAPI = Auth()


@buslocationApi.route("/buslocation", methods=["GET"])
@cache.cached(timeout=15)
def get_bus_location():
    # Access data from MOTC ptx
    t1 = time.time()
    req_url = "https://ptx.transportdata.tw/MOTC/v2/Bus/RealTimeByFrequency/City/Taipei?$select=PlateNumb%2C%20RouteUID%2C%20BusPosition%2C%20Speed%2C%20Direction&$filter=DutyStatus%20eq%201%20or%20DutyStatus%20eq%200&$format=JSON"
    response = request("get", req_url, headers=motcAPI.authHeader())
    response = response.json()
    busRouteUID = []
    returnData = dict()
    returnData["data"] = dict()
    for eachBusData in response:
        if eachBusData["RouteUID"] not in busRouteUID:
            busRouteUID.append(eachBusData["RouteUID"])
            returnData["data"][eachBusData["RouteUID"]] = dict()
            returnData["data"][eachBusData["RouteUID"]]["OperateBus"] = []
        returnData["data"][eachBusData["RouteUID"]]["OperateBus"].append(
            {
                "platenumb": eachBusData["PlateNumb"],
                "direction": eachBusData["Direction"],
                "longitude": eachBusData["BusPosition"]["PositionLon"],
                "latitude": eachBusData["BusPosition"]["PositionLat"],
                "speed": eachBusData["Speed"],
            }
        )
    routeUID_strings = "','".join(busRouteUID)
    selectSql = f"SELECT routeUID, routename_tw, routename_en, depname_tw, depname_en, destname_tw, destname_en FROM busroute WHERE routeUID IN ('{routeUID_strings}')"
    result = mysql.readData(selectSql)
    for routeData in result:
        returnData["data"][routeData[0]]["routename"] = {
            "tw": routeData[1],
            "en": routeData[2],
        }
        returnData["data"][routeData[0]]["depdestname"] = {
            "depname_tw": routeData[3],
            "depname_en": routeData[4],
            "destname_tw": routeData[5],
            "destname_en": routeData[6],
        }
    t2 = time.time()
    print(t2 - t1)
    return jsonify(returnData), 200
